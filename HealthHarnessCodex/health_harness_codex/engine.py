"""Bounded, stateless-request execution over case-scoped SQLite state."""

from __future__ import annotations

import json
import hashlib
import re
from dataclasses import replace
import threading
import time
import uuid
from typing import Any, Callable, Mapping, Protocol

from .models import (CompletionContract, ConflictError, IsolationError, Limits, ModelReply,
                     Scope, ToolCall, ToolSpec, UnknownOutcomeError, WorldUnavailableError, BudgetError, budget_is_reduction)
from .context import project_context
from .roles import roles_for, system_prompt, helper_prompt
from .schema import validate_arguments, UnexpectedParameterError
from .store import CaseStore
from .identity import (resolve_actual_case_id, resolve_patient_identity,
                       resolve_patient_identity_at_path, IdentityResolutionError)
from .providers import ModelResponseFormatError, format_correction, response_retry_limit, safe_request_diagnostics, validate_reply_structure, can_retry_disconnected_generation
from .workflow import execution_capabilities, request_stop_recovery, validate_dependencies


class Model(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[ToolSpec], *, max_output_tokens: int) -> ModelReply: ...


class Tools(Protocol):
    def list_tools(self) -> list[ToolSpec]: ...
    def call(self, name: str, arguments: dict[str, Any]) -> Any: ...


from .authorized_statements import SPEC as AUTHORIZED_STATEMENTS_SPEC

_LOCAL_SPECS = [
    AUTHORIZED_STATEMENTS_SPEC,
    ToolSpec('case.execute_recorded_action','Explicitly execute one remote write using the exact bound arguments already stored in a source-backed policy decision. You choose whether/when to commit. Avoid retyping long reasons or clinical payloads. All actual tool schemas, policy/identity checks, reviews, budgets and unknown-write fencing remain in force; repeated commits of the same record/operation do not repeat the remote write.',{
        'type':'object','additionalProperties':False,'required':['record_id','operation'],
        'properties':{'record_id':{'type':'string','minLength':1,'maxLength':100},
                      'operation':{'type':'string','minLength':1,'maxLength':256}}},effect='write'),
    ToolSpec('case.get_goal_state','Inspect the pinned primary task goal and a paged slice of active blockers and other open work. Links scope a blocker to named actions only; they do not authorize actions or create evidence. Full source records stay in the case store.',{
        'type':'object','additionalProperties':False,'properties':{
            'blocker_id':{'type':'string','minLength':1},'offset':{'type':'integer','minimum':0},
            'work_offset':{'type':'integer','minimum':0},
            'limit':{'type':'integer','minimum':1,'maximum':10},
            'instruction_offset':{'type':'integer','minimum':0},
            'instruction_limit':{'type':'integer','minimum':1,'maximum':4000}}},effect='read'),
    ToolSpec('case.audit_assignment','Read assignment obligations and evidence-supported missing milestones. Structural interpretation only, not clinical correctness or an official grade.',{
        'type':'object','properties':{},'additionalProperties':False},effect='read'),
    ToolSpec('case.record_external_handoff','Record an external dependency after a verified UM MD information-request handoff and delivered notice. Does not waive MD work, obtain documents or send a notification.',{
        'type':'object','required':['id','evidence_ids','next_action'],'additionalProperties':False,
        'properties':{'id':{'type':'string','minLength':1},'evidence_ids':{'type':'array','minItems':1,'items':{'type':'string'}},
            'next_action':{'type':'string','minLength':1,'maxLength':1200}}},effect='write'),
    ToolSpec('case.get_working_record','Read paged case notes, prerequisite records or helper job summaries. Original source pointers recover captured passages. Does not return full helper transcripts or create clinical evidence.',{
        'type':'object','required':['kind'],'additionalProperties':False,'properties':{
            'kind':{'type':'string','enum':['notes','blockers','jobs','work','decisions']},'id':{'type':'string'},
            'offset':{'type':'integer','minimum':0},'limit':{'type':'integer','minimum':1,'maximum':10}}},effect='read'),
    ToolSpec('case.get_tool_contract', 'Inspect the actual permitted input contract and description. Required input fields, optional fields and defaults are API facts, not proof of clinical prerequisites. An optional output/catalog must not be assumed mandatory.', {
        'type':'object','required':['tool_name'],'additionalProperties':False,
        'properties':{'tool_name':{'type':'string','minLength':1}}},effect='read'),
    ToolSpec('case.record_working_note', 'Maintain a concise case-local finding, open question, decision interpretation or next step. Upsert by id. Findings need original source IDs. Notes are interpretations, never new evidence or permission.', {
        'type':'object','required':['id','kind','summary'],'additionalProperties':False,
        'properties':{'id':{'type':'string','minLength':1,'maxLength':100},
            'kind':{'type':'string','enum':['finding','question','decision','next_step']},
            'summary':{'type':'string','minLength':1,'maxLength':1200},
            'status':{'type':'string','enum':['active','resolved']},
            'evidence_ids':{'type':'array','maxItems':12,'items':{'type':'string'}}}},effect='write'),
    ToolSpec('case.record_blocker', 'Record and investigate a claimed prerequisite. Cite actual tool fields or original policy/case passages; use hypothesis when necessity is unverified. Code verifies schema facts/provenance, not clinical interpretation. Optional fields and absent output fields do not prove a mandatory requirement.', {
        'type':'object','required':['id','blocked_action','claim','basis_kind'],'additionalProperties':False,
        'properties':{'id':{'type':'string','minLength':1,'maxLength':100},
            'blocked_action':{'type':'string','minLength':1,'maxLength':1000},
            'claim':{'type':'string','minLength':1,'maxLength':1200},
            'affected_obligation_ids':{'type':'array','maxItems':12,'items':{'type':'string','minLength':1},
                'description':'Existing current-case work affected by this prerequisite; leave other work visible. This does not disable tools.'},
            'next_investigation':{'type':'string','maxLength':600,
                'description':'Specific question/action that could resolve or change this blocker. Unverified necessity remains a hypothesis.'},
            'basis_kind':{'type':'string','enum':['tool_field','policy','observed_gap','hypothesis']},
            'tool_name':{'type':'string'},'field_name':{'type':'string'},'schema_path':{'type':'string'},
            'status':{'type':'string','enum':['open','resolved']},
            'sources':{'type':'array','maxItems':6,'items':{'type':'object','required':['evidence_id','path'],'additionalProperties':False,
                'properties':{'evidence_id':{'type':'string'},'path':{'type':'string'},
                    'start':{'type':'integer','minimum':0},'end':{'type':'integer','minimum':1}}}}}},effect='write'),
    ToolSpec('case.search_narrative', 'Find conceptually relevant narrative passages in specified original current-case observations using BM25 plus local GPU embeddings. A calibrated cosine floor screens basic relevance; empty matches mean none cleared the screen, not proof of absence. Refine the query or inspect original evidence if needed. Not for identity selection, code equality or fresh state; use exact typed fields for those. Preserves original evidence IDs/text pointers and surrounding context. No provider API or helper model. Missing local embedding runtime is an explicit error.',{
        'type':'object','required':['ids','query'],'additionalProperties':False,'properties':{
            'ids':{'type':'array','minItems':1,'maxItems':12,'items':{'type':'string','minLength':1}},
            'query':{'type':'string','minLength':1,'maxLength':1000},
            'max_results':{'type':'integer','minimum':1,'maximum':8},
            'max_chars':{'type':'integer','minimum':4000,'maximum':24000}}},effect='read'),
    ToolSpec('case.retrieve_evidence', 'Retrieve several typed fields and literal search passages from already-stored current-case observations in ONE operation. Group related questions by original source ID. Code searches all supplied phrases together; no model/helper call, new clinical evidence or external fetch. Results retain original IDs, text pointers, exact text offsets and partial/continuation markers. Prefer this to serial inspect/search calls. Omitted paths and queries are unknown, not absent.', {
        'type':'object','required':['requests'],'additionalProperties':False,'properties':{
            'requests':{'type':'array','minItems':1,'maxItems':12,'items':{'type':'object','required':['id'],
                'additionalProperties':False,'properties':{
                    'id':{'type':'string','minLength':1},
                    'paths':{'type':'array','maxItems':8,'items':{'type':'string','maxLength':1000}},
                    'queries':{'type':'array','maxItems':8,'items':{'type':'string','minLength':1,'maxLength':200}},
                    'offset':{'type':'integer','minimum':0},
                    'search_offset':{'type':'integer','minimum':0,'description':'Resume with the previous result next_match and the same source/queries.'},
                    'limit':{'type':'integer','minimum':1,'maximum':4000},
                    'max_passages':{'type':'integer','minimum':1,'maximum':12}}}},
            'max_chars':{'type':'integer','minimum':4000,'maximum':24000},
            'request_offset':{'type':'integer','minimum':0}}},effect='read'),
    ToolSpec('case.record_policy_decision', 'Record your policy-grounded decision before policy-dependent writes. Cite original retrieved policy source IDs and text fields/passages from approved files or policy tools; code captures exact text. Explain applicability, successful case evidence, your criterion/exception analysis, unresolved questions and intended operations. This verifies provenance, not clinical correctness; you choose the decision. Reuse the record for unchanged decisions. Bind provider final_action, and the requested service fields for case creation, in bound_arguments; for case creation give each bound field its own field_basis. No new clinical evidence is created.', {
        'type':'object','additionalProperties':False,
        'required':['policy_name','applicability','policy_sources','case_evidence_ids','assessment','unresolved_questions','decision','applies_to'],
        'properties':{
            'policy_name':{'type':'string','minLength':1,'maxLength':500},
            'applicability':{'type':'string','minLength':1,'maxLength':1500},
            'policy_sources':{'type':'array','minItems':1,'maxItems':8,'items':{'type':'object','additionalProperties':False,
                'required':['evidence_id'],'properties':{'evidence_id':{'type':'string','minLength':1,
                    'description':'Original successful source evidence ID, not the local inspection call ID.'},
                    'text_pointer':{'type':'string','maxLength':1000,'description':'JSON field pointer relative to business result (structuredContent when present), e.g. /text for files, /policy_text or /policy/text for tools. This is NOT a filesystem path. File reads may omit this: /text is inferred.'},
                    'path':{'type':'string','maxLength':1000,'description':'Optional source location: JSON field pointer or the EXACT already-retrieved file path. No new file is read from this value. Prefer text_pointer for tool results.'},
                    'start':{'type':'integer','minimum':0,'description':'Optional zero-based character start within the referenced stored text field (not original file offsets). Omit start/end to cite the entire returned passage.'},
                    'end':{'type':'integer','minimum':1,'description':'Optional exclusive character end within that field. Code captures exact text; use coordinates from source inspection/search, do not guess.'},
                    'quote':{'type':'string','minLength':8,'maxLength':1500,'description':'Legacy exact quotation; prefer source/passage references without copying. Cannot combine with start/end.'}}}},
            'case_evidence_ids':{'type':'array','minItems':1,'maxItems':20,'items':{'type':'string','minLength':1},
                'description':'Original actor case records or retrieved clinical attachments verified against same-case actor document metadata. For attachments read the exact actor-listed relative_path; filename aliases and generated drafts do not qualify.'},
            'assessment':{'type':'string','minLength':1,'maxLength':4000},
            'unresolved_questions':{'type':'array','maxItems':12,'items':{'type':'string','maxLength':500}},
            'decision':{'type':'string','minLength':1,'maxLength':1000},
            'unmet_goal_ids':{'type':'array','maxItems':12,'items':{'type':'string'},
                'description':'Declare primary when this decision would leave the requested outcome unmet. Does not waive that outcome.'},
            'remaining_actions_considered':{'type':'array','maxItems':8,'items':{'type':'string','minLength':1,'maxLength':600}},
            'why_act_now':{'type':'string','maxLength':1600,
                'description':'For a terminal action leaving the primary goal unmet, explain why acting now is justified despite the remaining work.'},
            'closure_basis':{'type':'string','enum':['patient_refusal','other_policy_basis'],
                'description':'Required only for cm_intake.disenroll_case. Refusal must agree with the latest outreach record; other supported policy reasons remain your judgment. Bind exact case_id and reason in bound_arguments.'},
            'applies_to':{'type':'array','minItems':1,'maxItems':12,'items':{'type':'string','minLength':1}},
            'bound_arguments':{'type':'object','additionalProperties':{'type':'object'}},
            'field_basis':{'type':'array','maxItems':8,'items':{'type':'object','additionalProperties':False,
                'required':['field','basis_kind','basis','source_evidence_ids'],'properties':{
                    'field':{'type':'string','enum':['procedure_code','diagnosis_codes','site_of_service','service_type']},
                    'basis_kind':{'type':'string','enum':['documented','inferred'],
                        'description':'documented: a cited source states this value; inferred: you derived it, so also cite the retrieved policy, requirement or handbook passage whose rule you applied. When no source states a required value, choose the best-supported one and record the uncertainty; do not block creation.'},
                    'basis':{'type':'string','minLength':1,'maxLength':600},
                    'source_evidence_ids':{'type':'array','minItems':1,'maxItems':6,'items':{'type':'string','minLength':1}}}},
                'description':'Required for case creation: one entry per requested service field you bind, citing the retrieved records or policy it comes from.'}}},effect='write'),
    ToolSpec('case.request_identity_reselection', 'Reject the current patient/case selection and request a clean identity investigation. Previous patient facts, drafts, obligations and caches will not enter the new context. Audit and cumulative budgets remain. External or uncertain writes require reconciliation instead of automatic reset. Use when evidence makes the current binding unjustified, not to evade a difficult clinical decision.', {
        'type':'object','required':['reason'],'additionalProperties':False,
        'properties':{'reason':{'type':'string','minLength':1,'maxLength':2000},
                      'evidence_ids':{'type':'array','uniqueItems':True,'items':{'type':'string'}}}},effect='write'),
    ToolSpec("case.inspect_evidence", "Read typed fields from an original successful case observation using a JSON pointer relative to its business result (structuredContent when present). No new evidence is created. Empty path inspects top-level fields; strings/lists support exact offset/limit slices. Omitted fields remain unknown.", {
        "type": "object", "required": ["id"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "path": {"type": "string", "maxLength": 1000},
            "offset": {"type": "integer", "minimum": 0}, "limit": {"type": "integer", "minimum": 1, "maximum": 4000},
            "representation": {"type":"string","enum":["business","raw"]}}}, effect="read"),
    ToolSpec("case.find_evidence", "Find original current-case source IDs by tool name or ID. Does not read medical text or create evidence; use search/inspect on the returned IDs. Supports paging.", {
        "type": "object", "properties": {"query": {"type": "string", "maxLength": 200},
            "offset": {"type": "integer", "minimum": 0}}, "additionalProperties": False}, effect="read"),
    ToolSpec("case.discover_tools", "Find and activate other already-permitted tools by name, namespace or description. Returned aliases and schemas become available on the next model call. This changes presentation only, never case permissions. Page through matches with offset.", {
        "type": "object", "required": ["query"], "additionalProperties": False,
        "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 200},
            "offset": {"type": "integer", "minimum": 0}}}, effect="read"),
    ToolSpec("case.get_role", "Read one complete general responsibility definition from this domain/shared catalog. Does not execute a helper or grant authority.", {
        "type": "object", "required": ["role_id"], "additionalProperties": False,
        "properties": {"role_id": {"type": "string", "minLength": 1}}}, effect="read"),
    ToolSpec("case.defer_obligation", "Record an outstanding external-document obligation at a verified provider information-gathering handoff. Does not close the obligation or send a notification. Requires completed forms, the actual gather-more disposition and fresh case readback.", {
        "type": "object", "required": ["id", "evidence_ids", "next_action"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1},
                       "evidence_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                       "next_action": {"type": "string", "minLength": 1, "maxLength": 1000}},
    }, effect="write"),
    ToolSpec("case.add_obligation", "Record a case-local task obligation.", {
        "type": "object", "required": ["id", "description"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "description": {"type": "string", "minLength": 1}, "owner": {"type": "string"},
                       "depends_on": {"type": "array", "uniqueItems": True, "items": {"type": "string", "minLength": 1}}},
    }, effect="write"),
    ToolSpec("case.close_obligation", "Close an obligation only with case-local observed evidence.", {
        "type": "object", "required": ["id", "evidence_ids"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "evidence_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}}},
    }, effect="write"),
    ToolSpec("case.read_evidence", "Read a bounded character range from one current-case observed result. "
             "Rehydration creates no new evidence: cite the original source ID returned in id, "
             "never an ev: ID constructed from this local tool call.", {
        "type": "object", "required": ["id", "offset", "length"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "offset": {"type": "integer", "minimum": 0},
                       "length": {"type": "integer", "minimum": 1, "maximum": 8000}},
    }, effect="read"),
    ToolSpec("case.search_evidence", "Search one successful current-case observation using a literal case-insensitive phrase. Returns bounded source snippets with original character offsets; use case.read_evidence with the same original id, offset, and length to inspect more context. Search creates no evidence ID.", {
        "type": "object", "required": ["id", "query"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1},
                       "query": {"type": "string", "minLength": 1, "maxLength": 500},
                       "max_results": {"type": "integer", "minimum": 1, "maximum": 5}},
    }, effect="read"),
    ToolSpec("case.request_helper", "Delegate a bounded investigation to a separate-context role worker. Select original case evidence and explicitly delegate tool_names; without tools it gives read-only analysis. allow_writes grants only the selected permitted writes. Shared case budgets and guards apply; no recursive delegation or identity reset. Returns a concise attributed result, not its full transcript.", {
        "type": "object", "required": ["role_id", "question"], "additionalProperties": False,
        "properties": {"role_id": {"type": "string", "minLength": 1}, "question": {"type": "string", "minLength": 1, "maxLength":4000},
            "evidence_ids": {"type": "array", "maxItems":12,"items": {"type": "string"}},
            "tool_names":{"type":"array","maxItems":32,"items":{"type":"string"}},
            "allow_writes":{"type":"boolean"},
            "max_model_calls":{"type":"integer","minimum":1},
            "max_tool_calls":{"type":"integer","minimum":1}},
    }, effect="read"),
]


def _format_retry_count(state: dict[str, Any]) -> int:
    total = 0
    for key in ("model_response_format_retry_count", "final_format_retry_count",
                "pre_dispatch_validation_retry_count"):
        value = state.get(key, 0)
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            total += value
    # One correction between successful new external observations. Lifetime
    # counters remain intact for audit; a successful parse alone is not progress.
    checkpoint = state.get("format_retry_progress_checkpoint", 0)
    if type(checkpoint) is not int or checkpoint < 0 or checkpoint > total:
        checkpoint = 0
    return total - checkpoint


def _record_format_progress(state: dict[str, Any]) -> None:
    state["format_retry_progress_checkpoint"] = sum(
        state.get(key, 0) for key in ("model_response_format_retry_count",
        "final_format_retry_count", "pre_dispatch_validation_retry_count")
        if type(state.get(key, 0)) is int and state.get(key, 0) > 0)


def _normalize_completion_contract(value: CompletionContract | Mapping[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise TypeError("completion contract must be a JSON object")
    try:
        encoded = json.dumps(dict(value), ensure_ascii=False, allow_nan=False, sort_keys=True)
        normalized = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError("completion contract must contain JSON-safe values") from exc
    if not isinstance(normalized, dict):
        raise ValueError("completion contract must be a JSON object")
    return normalized


def _completion_contract_hash(contract: dict[str, Any] | None) -> str | None:
    from .completion_contracts import contract_hash
    return contract_hash(contract)


def _safe_validation_feedback(exc: Exception, spec: ToolSpec) -> dict[str, Any]:
    """Keep only a stable category and schema-backed path; never include arguments."""
    if isinstance(exc, UnexpectedParameterError):
        return {"category": "schema_unexpected_field", "path": "$",
                "allowed_fields": list(exc.allowed_fields)}
    detail = str(exc)
    category = "arguments_rejected"
    patterns = (
        (r"array length at (\$[A-Za-z0-9_.$\[\]]*) is out of bounds", "schema_array_bounds"),
        (r"string length at (\$[A-Za-z0-9_.$\[\]]*) is out of bounds", "schema_string_bounds"),
        (r"number at (\$[A-Za-z0-9_.$\[\]]*) (?:is below minimum|exceeds maximum|does not exceed exclusiveMinimum|does not satisfy exclusiveMaximum)", "schema_number_bounds"),
        (r"value at (\$[A-Za-z0-9_.$\[\]]*) does not satisfy anyOf", "schema_any_of"),
        (r"value at (\$[A-Za-z0-9_.$\[\]]*) is not an allowed enum value", "schema_enum"),
        (r"string at (\$[A-Za-z0-9_.$\[\]]*) must be a timezone-qualified RFC 3339 date-time", "schema_datetime"),
        (r"expected [A-Za-z]+ at (\$[A-Za-z0-9_.$\[\]]*), got [A-Za-z]+", "schema_type"),
        (r"missing required field\(s\) at (\$[A-Za-z0-9_.$\[\]]*)", "schema_required"),
        (r"unexpected field at (\$[A-Za-z0-9_.$\[\]]*): [A-Za-z_][A-Za-z0-9_]*", "schema_unexpected_field"),
        (r"tool identity field '([A-Za-z_][A-Za-z0-9_]*)' does not match current case scope", "identity_scope"),
        (r"argument identity at (\$[A-Za-z0-9_.$\[\]]*) does not match current case scope", "identity_scope"),
    )
    path = None
    for pattern, matched_category in patterns:
        match = re.fullmatch(pattern, detail)
        if match:
            category = matched_category
            candidate = match.group(1)
            if matched_category == "identity_scope" and not candidate.startswith("$"):
                candidate = f"$.{candidate}"
            # Only expose paths composed of declared schema properties. A model
            # supplied unknown key is never copied into the correction prompt.
            if _path_uses_declared_properties(candidate, spec.input_schema):
                path = candidate
            break
    if "internal case-subject namespace" in detail:
        category = "identity_internal_namespace"
    feedback = {"category": category}
    if path:
        feedback["path"] = path
        node=_declared_schema_at_path(path,spec.input_schema)
        if category in {"schema_array_bounds","schema_string_bounds","schema_number_bounds"}:
            constraints={k:node[k] for k in ("minItems","maxItems","minLength","maxLength",
                "minimum","maximum","exclusiveMinimum","exclusiveMaximum") if k in node}
            feedback["constraints"]=constraints
    return feedback


def _declared_schema_at_path(path: str, schema: Any):
    """Traverse declared object properties and array items, never argument values."""
    if not re.fullmatch(r'\$(?:\.[A-Za-z_][A-Za-z0-9_]*|\[\d+\])*',path):return None
    node=schema
    for field,index in re.findall(r'\.([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]',path):
        if not isinstance(node,dict):return None
        if field:node=node.get('properties',{}).get(field)
        else:node=node.get('items')
    return node if isinstance(node,dict) else None


def _path_uses_declared_properties(path: str, schema: Any) -> bool:
    return _declared_schema_at_path(path,schema) is not None


def _has_observed_identity_for_rejection(feedback: dict[str, str], scope: Scope,
                                         state: dict[str, Any]) -> bool:
    if not feedback.get("category", "").startswith("identity_"):
        return True
    path = feedback.get("path", "")
    field = path.rsplit(".", 1)[-1] if path else ""
    if field in {"patient", "patient_id", "patientId"}:
        return bool(state.get("identity_bindings", {}).get("patient_id")
                    or not scope.patient.startswith("case-subject:"))
    if field in {"case", "case_id", "caseId"}:
        return bool(state.get("case_bindings") or not scope.case.startswith("case-subject:"))
    if field in {"actor", "principal_id", "user_id"}:
        return bool(state.get("principal_bindings"))
    return False


def _can_omit_optional_audit_actor(spec: ToolSpec, arguments: dict[str, Any],
                                  scope: Scope, feedback: dict[str, Any]) -> bool:
    """Prove omission is valid without accepting a new principal or dispatching.

    Optional audit attribution is not necessarily the harness principal. Keep
    the original identity rejection, but allow the model to remove that field
    when the ENTIRE remaining proposal passes schema and isolation checks.
    Explicit identity_fields and conditional required constraints still apply.
    """
    if feedback.get('category') != 'identity_scope' or feedback.get('path') not in (None, '', '$.actor') \
            and not str(feedback.get('path')).endswith('.actor'):
        return False
    candidate = {key: value for key, value in arguments.items() if key != 'actor'}
    # Bound arguments of a recorded decision may carry the same optional
    # attribution one level down; strip only that key, nothing else.
    if isinstance(candidate.get('bound_arguments'), dict):
        candidate['bound_arguments'] = {op: ({k: v for k, v in values.items() if k != 'actor'}
                                             if isinstance(values, dict) else values)
                                        for op, values in candidate['bound_arguments'].items()}
    if candidate == arguments:
        return False
    try:
        validate_arguments(spec, candidate, scope)
    except (ValueError, IsolationError):
        return False
    return True


def _completed_tool_call_duplicate(state: dict[str, Any], store: CaseStore, scope: Scope,
                                   tool_name: str, arguments: dict[str, Any]) -> bool:
    args_key = json.dumps(arguments, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    for action in store.actions(scope):
        if action.get("status") == "completed" and action.get("tool") == tool_name:
            prior_key = json.dumps(action.get("arguments"), sort_keys=True, ensure_ascii=False,
                                   separators=(",", ":"))
            if prior_key == args_key:
                return True
    tool_results = {message.get("tool_call_id"): message for message in state.get("messages", [])
                    if isinstance(message, dict) and message.get("role") == "tool"}
    for message in state.get("messages", []):
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls", []):
            if (not isinstance(call, dict) or call.get("name") != tool_name
                    or not isinstance(call.get("arguments"), dict)):
                continue
            if json.dumps(call["arguments"], sort_keys=True, ensure_ascii=False,
                          separators=(",", ":")) != args_key:
                continue
            tool_result = tool_results.get(call.get("id"))
            if not isinstance(tool_result, dict):
                continue
            try:
                result = json.loads(tool_result.get("content", "{}"))
            except (TypeError, json.JSONDecodeError):
                continue
            if isinstance(result, dict) and not ("error" in result or result.get("isError") is True):
                return True
    return False


def _resolve_principal_identity_at_path(result: Any, scope: Scope, path: tuple[str, ...],
                                        existing_principal: str | None = None) -> str | None:
    """Resolve one principal only from its explicitly trusted, same-case record."""
    if not isinstance(path, tuple) or not path or any(not isinstance(part, str) or not part for part in path):
        raise IdentityResolutionError("trusted principal path is invalid")
    node = result
    for part in path:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    if not isinstance(node, dict):
        return None
    case_id = node.get("case_id")
    actor = node.get("actor")
    if case_id is not None and (not isinstance(case_id, str) or case_id != scope.case):
        raise IdentityResolutionError("trusted principal source record does not match the active case")
    if case_id is None or actor is None:
        return None
    if not isinstance(actor, str) or not actor.strip() or actor.startswith("case-subject:"):
        raise IdentityResolutionError("trusted principal source contains an invalid actor identity")
    if existing_principal is not None and actor != existing_principal:
        raise IdentityResolutionError("trusted principal source conflicts with the existing case binding")
    return actor


class Harness:
    def __init__(self, store: CaseStore, model: Model, tools: Tools, limits: Limits | None = None,
                 composition: str = "combined", patient_identity_tools: tuple[str, ...] = (),
                 case_identity_tools: tuple[str, ...] = (),
                 case_binding_callback: Callable[[dict[str, Any]], None] | None = None,
                 patient_identity_result_paths: Mapping[str, tuple[str, ...]] | None = None,
                 principal_identity_result_paths: Mapping[str, tuple[str, ...]] | None = None,
                 require_policy_grounding: bool = False, progress=None, recovery_helper_policy='off', runtime_guard=None):
        self.store = store
        self.model = model
        self.tools = tools
        self._narrative_index = None
        self._helper_channel = None
        self.progress=progress
        if runtime_guard is not None and not callable(runtime_guard):raise TypeError('runtime guard must be callable')
        self.runtime_guard=runtime_guard
        self.limits = limits or Limits()
        if not isinstance(require_policy_grounding,bool):raise TypeError('require_policy_grounding must be boolean')
        self.require_policy_grounding=require_policy_grounding
        if recovery_helper_policy not in {'off','auto'}:raise ValueError('recovery_helper_policy must be off or auto')
        self.recovery_helper_policy=recovery_helper_policy
        if composition not in {"combined", "helpers", "team"}:
            raise ValueError("composition must be combined, helpers, or team")
        self.composition = composition
        if any(not isinstance(name, str) or not name for name in patient_identity_tools):
            raise ValueError("patient identity sources must be explicit tool names")
        if any(not isinstance(name, str) or not name for name in case_identity_tools):
            raise ValueError("case identity sources must be explicit tool names")
        if case_binding_callback is not None and not callable(case_binding_callback):
            raise TypeError("case binding callback must be callable")
        self.patient_identity_tools = frozenset(patient_identity_tools)
        self.case_identity_tools = frozenset(case_identity_tools)
        self.case_binding_callback = case_binding_callback
        paths = dict(patient_identity_result_paths or {})
        if (any(not isinstance(name, str) or not name for name in paths)
                or any(not isinstance(path, tuple) or not path
                       or any(not isinstance(part, str) or not part for part in path)
                       for path in paths.values())
                or not set(paths).issubset(self.patient_identity_tools)):
            raise ValueError("patient identity result paths must be explicit paths for whitelisted source tools")
        self.patient_identity_result_paths = paths
        principal_paths = dict(principal_identity_result_paths or {})
        if (any(not isinstance(name, str) or not name for name in principal_paths)
                or any(not isinstance(path, tuple) or not path
                       or any(not isinstance(part, str) or not part for part in path)
                       for path in principal_paths.values())):
            raise ValueError("principal identity result paths must be explicit paths for trusted source tools")
        self.principal_identity_result_paths = principal_paths
        self._run_lock = threading.Lock()

    def run(self, scope: Scope, instruction: str, domain: str, resume: bool = False,
            continuation_note: str | None = None, continuation_limits: Limits | None = None,
            completion_contract: CompletionContract | Mapping[str, Any] | None = None) -> dict[str, Any]:
        if continuation_note is not None and (not resume or not isinstance(continuation_note, str)
                                               or not continuation_note.strip()):
            raise ValueError("an explicit non-empty continuation note requires resume=True")
        if continuation_limits is not None and (continuation_note is None or not isinstance(continuation_limits, Limits)):
            raise ValueError("continuation limits require an explicit continuation note")
        if not self._run_lock.acquire(blocking=False):
            raise ConflictError("this Harness instance already has a run in progress")
        try:
            return self._run_owned(scope, instruction, domain, resume, continuation_note,
                                   continuation_limits, completion_contract)
        finally:
            self._run_lock.release()

    def _run_owned(self, scope: Scope, instruction: str, domain: str, resume: bool = False,
                   continuation_note: str | None = None, continuation_limits: Limits | None = None,
                   completion_contract: CompletionContract | Mapping[str, Any] | None = None) -> dict[str, Any]:
        binder = getattr(self.tools, "bind_scope", None)
        if callable(binder):
            binder(scope)
        state = self.store.open_case(scope, instruction, domain)
        requested_contract = _normalize_completion_contract(completion_contract)
        requested_contract_hash = _completion_contract_hash(requested_contract)
        configured_limits = self.limits
        owner = f"run-{uuid.uuid4().hex}"
        fence = self.store.claim(scope, owner, ttl_seconds=120)
        try:
            state = self.store.load_case(scope)
            if state["version"] == 0 and not state["messages"]:
                state["budgets"] = {key: getattr(self.limits, key) for key in
                                    ("max_model_calls", "max_tool_calls", "max_context_chars", "max_output_tokens")}
                state["composition"] = self.composition
                state["completion_contract"] = requested_contract
                state["completion_contract_sha256"] = requested_contract_hash
                state['policy_grounding_required']=self.require_policy_grounding
                state['goal_planning_enabled']=True
            else:
                self.limits = Limits(**state.get("budgets", {}))
                if state.get("composition", self.composition) != self.composition:
                    raise ConflictError("composition cannot change while resuming a case")
                persisted_contract_hash = state.get("completion_contract_sha256")
                if persisted_contract_hash != requested_contract_hash and completion_contract is not None:
                    raise ConflictError("completion contract cannot change while resuming a case")
                if persisted_contract_hash != _completion_contract_hash(state.get("completion_contract")):
                    raise ConflictError("persisted completion contract failed integrity validation")
                if not state.get("completion_contract_sha256"):
                    # Old state without a pinned contract remains unverified.
                    state["completion_contract"] = None
                    state["completion_contract_sha256"] = None
            state.setdefault("processed_tool_calls", [])
            if state.get('recovery_helper_policy',self.recovery_helper_policy)!=self.recovery_helper_policy:
                raise ConflictError('recovery helper policy cannot change while resuming a case')
            state['recovery_helper_policy']=self.recovery_helper_policy
            state.setdefault("usage", {})
            state.setdefault("model_response_format_retry_count", 0)
            state.setdefault("model_response_format_retries", [])
            state.setdefault("model_transport_retries", [])
            state.setdefault("model_transport_retry_streak", 0)
            state.setdefault("final_format_retry_count", 0)
            state.setdefault("final_format_retries", [])
            state.setdefault("pre_dispatch_validation_retry_count", 0)
            state.setdefault("pre_dispatch_validation_retries", [])
            if state["messages"] and not resume:
                raise ConflictError("case already has a conversation; pass resume=True to continue it")
            if continuation_note is not None:
                if not state["messages"] or state.get("status") not in {"complete", "unresolved", "exhausted", "error"}:
                    raise ConflictError("only a settled case may be explicitly continued")
                if any(a["status"] == "unknown" or (a["status"] == "pending" and a["effect"] == "write")
                       for a in self.store.actions(scope)):
                    raise UnknownOutcomeError("unknown or pending writes need actual reconciliation before continuation")
                new_limits = continuation_limits or self.limits
                budget_names = ("max_model_calls", "max_tool_calls", "max_context_chars", "max_output_tokens")
                if any(budget_is_reduction(name,getattr(new_limits,name),getattr(self.limits,name)) for name in budget_names):
                    raise ValueError("continuation cannot reduce persisted limits")
                state.setdefault("continuations", []).append({
                    "previous_status": state.get("status"), "previous_final": state.get("final"),
                    "previous_completion": state.get("completion"), "previous_budgets": dict(state["budgets"]),
                    "previous_completion_gate": state.get("completion_gate"),
                    "model_calls_at_start": state["model_calls"], "tool_calls_at_start": state["tool_calls"],
                    "note": continuation_note,
                })
                self.limits = new_limits
                state["budgets"] = {name: getattr(new_limits, name) for name in budget_names}
                state.update(status="running", message="", final=None, completion=None,
                             completion_gate=None, completion_gate_corrections=0)
                state["messages"].append({"role": "user", "content": continuation_note})
                self._save(scope, state, owner, fence)
            if resume and state.get("status") == "error":
                # A transient model/schema error may be retried. Any already
                # requested effects still pass through the journal below.
                state["status"] = "running"
                self._save(scope, state, owner, fence)
            if state.get("status") == "complete":
                pinned = state.get("completion_contract")
                gate = state.get("completion_gate")
                if (not isinstance(pinned, dict) or pinned.get("mapping_status") != "mapped"
                        or pinned.get("verified_task_goal") is not True
                        or pinned.get("task_id") != scope.task
                        or _completion_contract_hash(pinned) != state.get("completion_contract_sha256")
                        or not isinstance(gate, dict) or gate.get("accepted") is not True):
                    state.update(status="unresolved", completion=None,
                                 message="A prior complete status has no matching trusted terminal-condition verification.")
                    self._save(scope, state, owner, fence)
                else:
                    return self._result(state)
            if not state["messages"]:
                state["messages"] = [
                    {"role": "system", "content": system_prompt(domain, scope, self.composition)},
                    {"role": "user", "content": instruction},
                ]
                state["status"] = "running"
                self._save(scope, state, owner, fence)
            remote = self._tool_map()
            if state.get('helper_active'):
                state.update(status='blocked',message='A delegated job was interrupted. Reconcile its recorded actions before continuation; no helper or write will be replayed automatically.')
                self._save(scope,state,owner,fence)
                return self._result(state)
            from .working_set import canonical
            state['tool_name_index'] = sorted(canonical(s.name) for s in remote.values())
            state["workflow_capabilities"] = execution_capabilities(remote.values())
            # Finish any response already persisted before a process interruption.
            while state["messages"]:
                pending_round = self._pending_tool_calls(state)
                if pending_round:
                    state, fence = self._execute_calls(scope, state, pending_round, remote, owner, fence)
                    if state.get("status") != "running":
                        return self._result(state)
                if self._should_request_model(state):
                    self._check_runtime()
                    from .assignment import completion_audit,stage_guidance
                    if state.get('completion_contract_sha256')!=_completion_contract_hash(state.get('completion_contract')):
                        raise IsolationError('assignment contract integrity check failed')
                    state['assignment_audit']=completion_audit(state,self._identity_scope(scope,state).to_dict())
                    state['stage_guidance']=stage_guidance(state)
                    from .planning import progress_recovery
                    if progress_recovery(state):
                        self._save(scope,state,owner,fence)
                        if self.progress:self.progress('progress_recovery',after_model_call=state['model_calls'])
                    from .recovery_audit import run_recovery_audit
                    if run_recovery_audit(self,scope,state,owner,fence,'stagnant_blocker'):
                        state=self.store.load_case(scope)
                        if state.get('status')!='running':return self._result(state)
                        state['assignment_audit']=completion_audit(state,self._identity_scope(scope,state).to_dict())
                        state['stage_guidance']=stage_guidance(state)
                    self._save(scope,state,owner,fence)
                    if state["model_calls"] >= self.limits.max_model_calls:
                        state["status"] = "exhausted"
                        state["message"] = "Model-call budget exhausted with the case unresolved."
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    final_format_retry_pending = state.get("final_format_retry_pending") is True
                    validation_retry = state.get("pre_dispatch_validation_retry")
                    validation_retry_pending = (isinstance(validation_retry, dict)
                                                and validation_retry.get("pending") is True)
                    if final_format_retry_pending:
                        available_specs = []
                    elif validation_retry_pending:
                        retry_name = validation_retry.get("tool_name")
                        retry_spec = next((spec for spec in self._available_specs(remote,state)
                                           if spec.name == retry_name), None)
                        if retry_spec is None:
                            state["pre_dispatch_validation_retry"]["pending"] = False
                            state["status"] = "error"
                            state["message"] = "The rejected tool is no longer available for its bounded correction."
                            self._save(scope, state, owner, fence)
                            return self._result(state)
                        available_specs = [retry_spec]
                    else:
                        from .working_set import select_tools
                        available_specs = select_tools(self._available_specs(remote,state), state)
                    context_messages = project_context(state["messages"], state, available_specs,
                                                       self.limits.max_context_chars)
                    if context_messages is None:
                        state["status"] = "exhausted"
                        state["message"] = "Context budget exhausted; unresolved obligations and source records were preserved."
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    state.pop("model_failure", None)
                    fence = self.store.claim(scope, owner, ttl_seconds=120)
                    state["model_calls"] += 1
                    self._save(scope, state, owner, fence)
                    try:
                        with self.store.maintained_claim(scope,owner,fence):
                            reply = self.model.complete(context_messages, available_specs,
                                                        max_output_tokens=self.limits.max_output_tokens)
                        if not isinstance(reply, ModelReply):
                            raise TypeError("model.complete must return ModelReply")
                        validate_reply_structure(reply,{s.name for s in self._available_specs(remote,state)})
                    except Exception as exc:
                        state = self.store.load_case(scope)
                        self._merge_usage(state,getattr(exc,'usage',{}))
                        if self._request_disconnection_retry(state,exc):
                            self._save(scope,state,owner,fence)
                            continue
                        if isinstance(exc, ModelResponseFormatError):
                            retry_count = state.get("model_response_format_retry_count", 0)
                            final_format_retry_count = state.get("final_format_retry_count", 0)
                            validation_retry_count = state.get("pre_dispatch_validation_retry_count", 0)
                            if (isinstance(retry_count, int) and not isinstance(retry_count, bool)
                                    and isinstance(final_format_retry_count, int)
                                    and not isinstance(final_format_retry_count, bool)
                                    and isinstance(validation_retry_count, int)
                                    and not isinstance(validation_retry_count, bool)
                                    and _format_retry_count(state) < response_retry_limit(exc)
                                    and state["model_calls"] < self.limits.max_model_calls):
                                retry_call = state["model_calls"] + 1
                                state["model_response_format_retry_count"] = retry_count + 1
                                state.setdefault("model_response_format_retries", []).append({
                                    "retry_number": retry_count + 1,
                                    "failed_model_call": state["model_calls"],
                                    "retry_model_call": retry_call,
                                    "error_type": type(exc).__name__,
                                    "stage": exc.stage,
                                })
                                state["messages"].append({"role":"user","content":format_correction(exc)})
                                if self.progress:self.progress('response_correction',response_failure_stage=exc.stage,
                                    after_model_call=state['model_calls'])
                                state["status"] = "running"
                                state["message"] = "Requesting a bounded response correction since the last successful tool observation."
                                self._save(scope, state, owner, fence)
                                continue
                        failure_category = getattr(exc, "failure_category", None)
                        if not isinstance(failure_category, str) or not failure_category.isascii() \
                                or any(not (char.isalnum() or char in "_:-") for char in failure_category) \
                                or len(failure_category) > 96:
                            failure_category = None
                        state["model_failure"] = {
                            "error_type": type(exc).__name__,
                            "failure_category": failure_category,
                            "proposal_dispatch_safe": bool(getattr(exc, "proposal_dispatch_safe", False)),
                            "transient_retry_eligible": bool(getattr(exc, "transient_retry_eligible", False)),
                        }
                        diagnostics=safe_request_diagnostics(getattr(exc,'diagnostics',{}))
                        if diagnostics:state['model_failure']['request_diagnostics']=diagnostics
                        if validation_retry_pending:
                            state["pre_dispatch_validation_retry"]["pending"] = False
                        state["status"] = "error"
                        state["message"] = f"Model request failed: {type(exc).__name__}: {exc}"
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    if final_format_retry_pending and reply.tool_calls:
                        state = self.store.load_case(scope)
                        self._merge_usage(state, reply.usage)
                        state["final_format_retry_pending"] = False
                        state["status"] = "error"
                        state["message"] = "Format-only correction proposed a tool call; it was not dispatched."
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    if validation_retry_pending:
                        retry_name = validation_retry.get("tool_name")
                        if reply.tool_calls:
                            if len(reply.tool_calls) != 1 or reply.tool_calls[0].name != retry_name:
                                state = self.store.load_case(scope)
                                self._merge_usage(state, reply.usage)
                                state["pre_dispatch_validation_retry"]["pending"] = False
                                state["status"] = "error"
                                state["message"] = "Schema correction did not return exactly the rejected tool; no proposal was dispatched."
                                self._save(scope, state, owner, fence)
                                return self._result(state)
                            corrected = reply.tool_calls[0]
                            prior_tool_call_ids = {
                                call.get("id") for message in state.get("messages", [])
                                if isinstance(message, dict) and message.get("role") == "assistant"
                                for call in message.get("tool_calls", []) if isinstance(call, dict)
                            }
                            completed_duplicate = _completed_tool_call_duplicate(
                                state, self.store, scope, retry_name, corrected.arguments)
                            if corrected.id in prior_tool_call_ids or completed_duplicate:
                                state = self.store.load_case(scope)
                                self._merge_usage(state, reply.usage)
                                state["pre_dispatch_validation_retry"]["pending"] = False
                                state["status"] = "error"
                                state["message"] = "Schema correction would repeat a completed write; no proposal was dispatched."
                                self._save(scope, state, owner, fence)
                                return self._result(state)
                    from .planning import capture_public_plan
                    state = self.store.load_case(scope)
                    state['model_transport_retry_streak']=0
                    capture_public_plan(state,reply.content)
                    self._save(scope,state,owner,fence)
                    if reply.tool_calls:
                        state = self.store.load_case(scope)
                        self._merge_usage(state, reply.usage)
                        call_ids = [call.id for call in reply.tool_calls]
                        if len(set(call_ids)) != len(call_ids) or any(not isinstance(cid, str) or not cid for cid in call_ids):
                            state["status"] = "error"
                            state["message"] = "Model returned missing or duplicate tool-call IDs."
                            self._save(scope, state, owner, fence)
                            return self._result(state)
                        if self.composition == "helpers" and sum(call.name == "case.request_helper" for call in reply.tool_calls) > 1:
                            state["status"] = "error"
                            state["message"] = "helpers composition permits one bounded role analysis per model turn; use team for selected multiple analyses."
                            self._save(scope, state, owner, fence)
                            return self._result(state)
                        model_round = state["model_calls"]
                        retry_journal_id = (validation_retry.get("journal_id")
                                            if validation_retry_pending and isinstance(validation_retry, dict)
                                            else None)
                        if validation_retry_pending:
                            state["pre_dispatch_validation_retry"]["pending"] = False
                        state["messages"].append({"role": "assistant", "content": reply.content,
                                                  "tool_calls": [dict(self._call_dict(call),
                                                                       journal_id=(retry_journal_id if index == 0 and retry_journal_id
                                                                                   else f"m{model_round}:{call.id}"))
                                                                 for index, call in enumerate(reply.tool_calls)]})
                        self._save(scope, state, owner, fence)
                        # The persisted assistant request is replayable for reads only;
                        # journaled writes stop on a pre-existing pending reservation.
                        state, fence = self._execute_calls(scope, state, state["messages"][-1]["tool_calls"], remote, owner, fence)
                        if state.get("status") != "running":
                            return self._result(state)
                        continue
                    state = self.store.load_case(scope)
                    self._merge_usage(state, reply.usage)
                    state["messages"].append({"role": "assistant", "content": reply.content})
                    if final_format_retry_pending:
                        state["final_format_retry_pending"] = False
                    if validation_retry_pending:
                        state["pre_dispatch_validation_retry"]["pending"] = False
                    try:
                        proposed_final=json.loads(reply.content)
                    except (ValueError,TypeError):
                        proposed_final=None
                    if isinstance(proposed_final,dict) and proposed_final.get('status') in {'complete','incomplete'}:
                        self._save(scope,state,owner,fence)
                        if run_recovery_audit(self,scope,state,owner,fence,'proposed_stop'):
                            state=self.store.load_case(scope)
                            continue
                    state = self._accept_final(state, reply.content)
                    if (state.get("status") == "unresolved" and isinstance(state.get("final"), dict)
                            and not (state['final'].get('status')=='incomplete' and state.get('stop_assessment_validation',{}).get('accepted'))
                            and state.get('workflow_stop_reason')!='stop_report_reference_repair_exhausted'
                            and (state["final"].get("status") != "complete"
                                 or state.get('stop_review_required')
                                 or state.get("message", "").startswith("Completion is blocked by open obligations:"))):
                        if state.get('stop_review_required') or not run_recovery_audit(self,scope,state,owner,fence,'repeated_final'):
                            request_stop_recovery(state, max_model_calls=self.limits.max_model_calls)
                        else:state=self.store.load_case(scope)
                    if state.get("status") == "running":
                        self._save(scope, state, owner, fence)
                        continue
                    retry_budget_used = _format_retry_count(state)
                    if (state.get("status") == "unresolved"
                            and state.get("message") == "The model returned prose without the required structured completion record."
                            and retry_budget_used < 1
                            and state["model_calls"] < self.limits.max_model_calls):
                        failed_call = state["model_calls"]
                        retry_call = failed_call + 1
                        state["final_format_retry_count"] = state.get("final_format_retry_count", 0) + 1
                        state["final_format_retries"].append({
                            "retry_number": state["final_format_retry_count"],
                            "failed_model_call": failed_call,
                            "retry_model_call": retry_call,
                            "error_type": "FinalCompletionFormatError",
                        })
                        state["messages"].append({"role": "user", "content":
                            "Formatting correction only: return exactly one valid JSON object with keys "
                            "status, claim, and evidence_ids. Use status=complete only if the original task "
                            "is fully supported by this case's successful observed evidence and all obligations "
                            "are closed; otherwise use a non-complete status and explain what remains. Do not "
                            "propose tools or new actions. Preserve the original task scope and do not add facts."})
                        state["final_format_retry_pending"] = True
                        state["status"] = "running"
                        state["message"] = "Retrying once after a final completion format error."
                        self._save(scope, state, owner, fence)
                        continue
                    self._save(scope, state, owner, fence)
                    return self._result(state)
                # A no-tool assistant message is terminal; this guard avoids a
                # malformed conversation spinning without progress.
                if state["messages"][-1].get("role") == "assistant":
                    return self._result(state)
            state["status"] = "unresolved"
            state["message"] = "No model response was recorded."
            self._save(scope, state, owner, fence)
            return self._result(state)
        except WorldUnavailableError as exc:
            state=self.store.load_case(scope)
            uncertain=any(a['status']=='unknown' or (a['status']=='pending' and a['effect']=='write')
                for a in self.store.actions(scope))
            state.update(status='blocked' if uncertain else 'error',message=str(exc),
                runtime_failure={'component':'task_world','reason':exc.reason,
                    'further_inference_stopped':True,'requires_reconciliation':uncertain})
            if self.progress:self.progress('world_unavailable',runtime_status=exc.reason)
            self._save(scope,state,owner,fence)
            return self._result(state)
        except UnknownOutcomeError as exc:
            state = self.store.load_case(scope)
            state["status"] = "blocked"
            state["message"] = str(exc)
            self._save(scope, state, owner, fence)
            return self._result(state)
        except BudgetError as exc:
            state = self.store.load_case(scope)
            state["status"] = "exhausted"
            state["message"] = str(exc)
            self._save(scope, state, owner, fence)
            return self._result(state)
        finally:
            try:
                self.store.release(scope, owner, fence)
            except ConflictError:
                # Lease expired or was taken over; stale code cannot write after
                # that point, and the new owner remains responsible for recovery.
                pass
            self.limits = configured_limits

    def _execute_calls(self, scope: Scope, state: dict[str, Any], calls: list[dict[str, Any]],
                       remote: dict[str, ToolSpec], owner: str, fence: int) -> tuple[dict[str, Any], int]:
        from .working_set import canonical
        for call_index, raw in enumerate(calls):
            call = ToolCall(raw["id"], raw["name"], raw["arguments"])
            prepared_reference=None
            processing_id = raw.get("journal_id", f"m{state['model_calls']}:{call.id}")
            round_match=re.match(r'^((?:[^:]+:)?m\d+):',processing_id)
            proposal_round=round_match.group(1) if round_match else f"m{state['model_calls']}"
            processed = set(state.get("processed_tool_calls", []))
            if processing_id not in processed and state["tool_calls"] >= self.limits.max_tool_calls:
                state["status"] = "exhausted"
                state["message"] = "Tool-call budget exhausted with pending work preserved."
                self._save(scope, state, owner, fence)
                return state, fence
            if processing_id not in processed:
                state.setdefault("processed_tool_calls", []).append(processing_id)
                state["tool_calls"] += 1
                self._save(scope, state, owner, fence)
            spec = next((s for s in _LOCAL_SPECS if s.name == call.name), remote.get(call.name))
            if spec is None:
                state["status"] = "error"
                state["message"] = f"Unknown tool requested: {call.name}"
                self._save(scope, state, owner, fence)
                return state, fence
            conversation_observation=state.get('conversation_observation_fence')
            if (conversation_observation is not None and spec.effect=='write'
                    and conversation_observation.get('proposal_round')==proposal_round):
                if self.progress:self.progress('conversation_write_deferred',tool_name=canonical(call.name))
                state['messages'].append({'role':'tool','tool_call_id':call.id,'name':call.name,
                    'content':json.dumps({'error':'conversation_response_must_be_observed_first',
                        'known_not_dispatched':True,'observation':conversation_observation,
                        'instruction':'This write was drafted before the preceding conversation response was known. '
                            'Read the actual returned response, then choose and re-propose any appropriate write in a new turn. '
                            'Do not assume consent, refusal, agreement or a conversation outcome.'})})
                self._save(scope,state,owner,fence)
                continue
            try:
                validate_arguments(spec, call.arguments, self._identity_scope(scope, state))
            except (ValueError, IsolationError) as exc:
                feedback = _safe_validation_feedback(exc, spec)
                can_omit_actor = _can_omit_optional_audit_actor(
                    spec, call.arguments, self._identity_scope(scope, state), feedback)
                if can_omit_actor:
                    feedback['correction'] = {'omit_optional_parameter': 'actor',
                        'reason': 'Omission passes the tool schema and identity checks; it does not assert or bind a new principal.'}
                state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                          "content": json.dumps({"error": "arguments_rejected_before_dispatch",
                                                                 **feedback})})
                # A model turn can contain siblings after this rejected call.
                # They are explicitly answered as not dispatched; none may run
                # after a correction is requested.
                for skipped in calls[call_index + 1:]:
                    state["messages"].append({
                        "role": "tool", "tool_call_id": skipped["id"], "name": skipped["name"],
                        "content": json.dumps({"error": "not_dispatched_after_validation_rejection",
                                               "category": feedback["category"]}),
                    })
                retry_allowed = (
                    _format_retry_count(state) < 1
                    and state["model_calls"] < self.limits.max_model_calls
                    and (_has_observed_identity_for_rejection(feedback, scope, state) or can_omit_actor)
                )
                if retry_allowed:
                    retry_count = state.get("pre_dispatch_validation_retry_count", 0) + 1
                    retry_call = state["model_calls"] + 1
                    state["pre_dispatch_validation_retry_count"] = retry_count
                    state.setdefault("pre_dispatch_validation_retries", []).append({
                        "retry_number": retry_count,
                        "failed_model_call": state["model_calls"],
                        "retry_model_call": retry_call,
                        "tool_name": call.name,
                        "category": feedback["category"],
                        "path": feedback.get("path"),
                    })
                    state["pre_dispatch_validation_retry"] = {
                        "pending": True,
                        "tool_name": call.name,
                        "journal_id": processing_id,
                        "category": feedback["category"],
                        "path": feedback.get("path"),
                    }
                    note = ("Schema-only correction: the previous proposal was rejected before dispatch. "
                            "No rejected or skipped proposal was executed. Return at most one corrected call "
                            f"to the same tool, `{call.name}`, using its declared schema and only evidence or "
                            "same-case identities already observed in this conversation. Do not repeat any "
                            "completed tool call, invent dates or identifiers, or propose other tools. "
                            "Use the supplied validation category, field path and schema constraints to correct the violation. "
                            "For list limits, preserve the intended investigation by grouping items within valid entries "
                            "of the same tool request when its schema permits. "
                            "If the values cannot be corrected from available evidence, return a structured "
                            "non-complete final with no tool calls.")
                    if (not can_omit_actor and feedback.get('category','').startswith('identity_')
                            and str(feedback.get('path','')).rsplit('.',1)[-1] in {'actor','principal_id','user_id'}):
                        note += (' The rejected value is actor/principal attribution, possibly nested in bound arguments. '
                                 'Use an identity already bound in this case if one exists; otherwise omit that field where '
                                 'the schema allows. Never substitute a different or guessed identity.')
                    if can_omit_actor:
                        note += (' The rejected actor is optional audit attribution: omit the actor parameter entirely, '
                                 'including inside bound_arguments. '
                                 'Do not replace it with another identity or null. Let the tool apply its own declared default; '
                                 'all other schema and identity checks remain in force.')
                    state["messages"].append({"role": "user", "content": note})
                    state["status"] = "running"
                    state["message"] = "Requesting one bounded correction after pre-dispatch tool validation rejection."
                else:
                    state["status"] = "error"
                    state["message"] = (
                        "The bounded tool-argument correction still failed validation; inspect its category, path and constraints."
                        if _format_retry_count(state)>=1 else
                        "Tool arguments were rejected before dispatch; no safe correction was available within identity and model-call limits.")
                self._save(scope, state, owner, fence)
                return state, fence
            if call.name=='case.execute_recorded_action':
                try:
                    from .prepared_actions import resolve
                    spec,payload,processing_id,prepared_reference=resolve(self,scope,state,call.arguments,remote)
                    call=ToolCall(call.id,spec.name,payload)
                except (ValueError,IsolationError) as exc:
                    state['messages'].append({'role':'tool','tool_call_id':call.id,'name':call.name,
                        'content':json.dumps({'error':'prepared_action_rejected','known_not_dispatched':True,
                            'detail':str(exc),'instruction':'Inspect the decision and actual tool contract; create a corrected source-backed bound record. No remote action was dispatched.'})})
                    self._save(scope,state,owner,fence)
                    continue
            from .dialogue_guard import blocked as dialogue_blocked
            dialogue_feedback = dialogue_blocked(state, call.name)
            if dialogue_feedback:
                state['messages'].append({'role':'tool','tool_call_id':call.id,'name':call.name,
                    'content':json.dumps(dialogue_feedback)})
                if self.progress:self.progress('conversation_repetition_stopped', tool_name=canonical(call.name))
                self._save(scope,state,owner,fence)
                continue
            if call.name.startswith("case."):
                try:
                    result = self._observed_local_call(scope, state, call, owner, fence)
                except (ValueError, KeyError, ConflictError, IsolationError) as exc:
                    if isinstance(exc,ConflictError):raise
                    result = {"error": type(exc).__name__, "detail": str(exc)}
                    from .policy_grounding import PolicyGroundingError
                    if isinstance(exc,PolicyGroundingError):result['feedback']=exc.feedback
                    state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                              "content": json.dumps(result, ensure_ascii=False)})
                    self._save(scope, state, owner, fence)
                    continue
                state = self.store.load_case(scope)
                fence = self.store.claim(scope,owner,ttl_seconds=120)
                investigative={'case.inspect_evidence','case.retrieve_evidence','case.find_evidence','case.read_evidence',
                    'case.search_evidence','case.search_narrative','case.get_tool_contract','case.get_role','case.discover_tools','case.get_working_record','case.get_goal_state'}
                if call.name in investigative:
                    from .planning import observe_progress
                    outcome='failure' if isinstance(result,dict) and result.get('error') not in (None,'source_path_absent') else 'success'
                    feedback=observe_progress(state,call.name,call.arguments,result,
                        result.get('id',f'local:{processing_id}') if isinstance(result,dict) else f'local:{processing_id}',outcome)
                    if feedback and isinstance(result,dict):result={**result,'progress_feedback':feedback}
                state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                          "content": json.dumps(result, ensure_ascii=False, default=str)})
                self._save(scope, state, owner, fence)
                if state.get('status') != 'running':
                    for skipped in calls[call_index+1:]:
                        state['messages'].append({'role':'tool','tool_call_id':skipped['id'],'name':skipped['name'],
                            'content':json.dumps({'error':'not_dispatched_after_identity_reselection','creates_evidence':False})})
                    self._save(scope,state,owner,fence)
                    return state,fence
                continue

            action_id = processing_id
            prior = next((a for a in self.store.actions(scope) if a["id"] == action_id), None)
            if prior is None:
                from .dialogue_worker import before_send
                state,delegated=before_send(self,scope,state,call,owner,fence,proposal_round)
                if delegated:
                    state['messages'].append({'role':'tool','tool_call_id':call.id,'name':call.name,
                        'content':json.dumps(delegated,ensure_ascii=False)})
                    self._save(scope,state,owner,fence)
                    continue
            if spec.effect == "write" and prior is None:
                from .policy_grounding import check_decision, operation_name
                grounding_error=check_decision(state,call.name,call.arguments,self._identity_scope(scope,state).to_dict())
                if grounding_error:
                    state.setdefault('policy_decision_refusals',[]).append({'tool':operation_name(call.name),
                        'model_call':state['model_calls'],'reason':grounding_error})
                    state['messages'].append({'role':'tool','tool_call_id':call.id,'name':call.name,
                        'content':json.dumps({'error':grounding_error,'status':'not_dispatched','known_not_dispatched':True,
                            'operation':operation_name(call.name),'required_tool':'case.record_policy_decision',
                            'instruction':'No operation was dispatched. Retrieve the governing policy text, including relevant conditions, exclusions and definitions; compare it with current case evidence and record your supported decision. Filled forms and readiness flags do not establish policy eligibility. You choose the applicable decision; this guard does not choose an outcome.'
                                + (' Case creation commits the requested service: ground the procedure code, diagnoses, service type and site of service in the ordering clinical documentation and the governing policy or requirement text, bind each field you send, and give each its own field_basis with the retrieved sources it comes from.'
                                   if operation_name(call.name)=='cases.create_from_order' else '')})})
                    self._save(scope,state,owner,fence)
                    continue
                from .terminal_review import before_action
                state, terminal_feedback = before_action(self,scope,state,call,owner,fence)
                if terminal_feedback is not None:
                    state['messages'].append({'role':'tool','tool_call_id':call.id,'name':call.name,
                        'content':json.dumps(terminal_feedback,ensure_ascii=False)})
                    # No sibling from the stale owner proposal may commit
                    # after the reviewer supplied potentially new evidence.
                    for skipped in calls[call_index+1:]:
                        state['messages'].append({'role':'tool','tool_call_id':skipped['id'],'name':skipped['name'],
                            'content':json.dumps({'error':'not_dispatched_after_terminal_review',
                                                 'known_not_dispatched':True})})
                    self._save(scope,state,owner,fence)
                    return state,fence
                from .completion_contracts import unmet_tool_prerequisites
                prerequisites = unmet_tool_prerequisites(
                    state.get("completion_contract"), state.get("evidence", []), call.name,
                    scope.to_dict(), self._identity_scope(scope, state).to_dict())
                if prerequisites:
                    state.setdefault("workflow_guard_refusals", []).append({
                        "tool": call.name, "model_call": state["model_calls"],
                        "missing": [item["id"] for item in prerequisites]})
                    state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                        "content": json.dumps({"error": "workflow_prerequisite_missing",
                                               "status": "not_dispatched", "required_reads": prerequisites,
                                               "instruction": "Read the created case's current requirements before recording a disposition or submission. Then reconsider the action using that evidence."})})
                    self._save(scope, state, owner, fence)
                    continue

            try:
                fence = self.store.claim(scope, owner, ttl_seconds=120)
                record = self.store.reserve_action(scope, action_id, call.name, call.arguments, spec.effect,
                                                   owner=owner, fence=fence)
            except UnknownOutcomeError:
                raise
            if prior and prior["status"] == "pending" and spec.effect == "write":
                self.store.unknown_action(scope, action_id, "process stopped after write reservation; reconcile from the actual tool state",
                                          owner=owner, fence=fence)
                raise UnknownOutcomeError(f"write action {action_id!r} was left pending; automatic replay is blocked")
            identity_mismatch = False
            resolved_patient = None
            resolved_case = None
            resolved_principal = None
            if record["status"] == "completed":
                result = record["result"]
                result, resolved_patient, identity_mismatch, resolved_case, resolved_principal = self._check_result_identity(
                    result, scope, state, call.name)
            else:
                try:
                    if call.name in self.case_identity_tools and state.get("case_bindings"):
                        result = {"error": "case_already_bound", "isError": True,
                                  "known_not_dispatched": True,
                                  "detail": "This patient scope already has a trusted provider case binding."}
                    else:
                        result = self.tools.call(call.name, call.arguments)
                    # Verify JSON safety before committing the observed result.
                    encoded_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
                    result = json.loads(encoded_result)
                    result, resolved_patient, identity_mismatch, resolved_case, resolved_principal = self._check_result_identity(
                        result, scope, state, call.name)
                    fence = self.store.claim(scope, owner, ttl_seconds=120)
                    self.store.finish_action(scope, action_id, result, owner=owner, fence=fence)
                except Exception as exc:
                    if isinstance(exc,WorldUnavailableError):
                        if spec.effect=='write':
                            self.store.unknown_action(scope,action_id,'Task runtime unavailable after write reservation; reconcile before replay.',owner=owner,fence=fence)
                        else:
                            self.store.finish_action(scope,action_id,{'error':'WorldUnavailableError','runtime_status':exc.reason},owner=owner,fence=fence)
                        raise
                    if spec.effect == "write":
                        # If the fence was lost, preserve the pending record for
                        # the replacement worker instead of writing stale state.
                        self.store.unknown_action(scope, action_id, f"tool call outcome uncertain: {type(exc).__name__}: {exc}",
                                                  owner=owner, fence=fence)
                        raise UnknownOutcomeError(f"write action {action_id!r} may have executed; reconcile before continuing") from exc
                    result = {"error": type(exc).__name__, "detail": str(exc)}
                    fence = self.store.claim(scope, owner, ttl_seconds=120)
                    self.store.finish_action(scope, action_id, result, owner=owner, fence=fence)
            state = self.store.load_case(scope)
            evidence_id = f"ev:{action_id}"
            if resolved_case and not identity_mismatch and not state.get("case_bindings"):
                binding = {
                    "case_namespace": scope.case,
                    "case_id": resolved_case,
                    "patient_id": scope.patient,
                    "source_tool": call.name,
                    "source_evidence_id": evidence_id,
                    "method": "same_case_provider_creation_result",
                }
                state["case_bindings"] = binding
                if self.case_binding_callback is not None:
                    try:
                        self.case_binding_callback(dict(binding))
                    except Exception as exc:
                        state["status"] = "blocked"
                        state["message"] = ("The provider case was created and its identity was validated, "
                                             f"but scoped workspace binding failed ({type(exc).__name__}).")
            if resolved_patient and not identity_mismatch and not state.get("identity_bindings"):
                state["identity_bindings"] = {"patient_id": resolved_patient, "case_id": scope.case,
                                               "source_tool": call.name, "source_evidence_id": evidence_id,
                                               "method": "same_case_actor_result"}
            if resolved_principal and not identity_mismatch and not state.get("principal_bindings"):
                state["principal_bindings"] = {
                    "principal_namespace": scope.principal,
                    "principal_id": resolved_principal,
                    "case_id": scope.case,
                    "source_tool": call.name,
                    "source_evidence_id": evidence_id,
                    "method": "same_case_trusted_review_actor_result",
                }
            evidence = next((item for item in state["evidence"] if item.get("id") == evidence_id), None)
            newly_recorded=evidence is None
            if evidence is None:
                outcome = "failure" if isinstance(result, dict) and ("error" in result or result.get("isError") is True) else "success"
                evidence = {"id": evidence_id, "scope": scope.to_dict(), "action_id": action_id,
                            "tool": call.name, "effect": spec.effect, "outcome": outcome,
                            "observed_result": result}
                state["evidence"].append(evidence)
            from .write_feedback import assess_write_payload
            try:payload_feedback = assess_write_payload(spec,call.arguments,result,evidence_id)
            except (TypeError,ValueError,KeyError,RecursionError):payload_feedback = None
            if payload_feedback:
                evidence['execution_feedback'] = payload_feedback
                if self.progress:self.progress('write_payload_warning',tool_name=call.name)
            from .planning import observe_progress
            feedback = observe_progress(state,call.name,call.arguments,result,evidence_id,evidence['outcome'])
            if newly_recorded and evidence['outcome']=='success' and feedback is None and record['status']!='completed':
                _record_format_progress(state)
            state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                      "evidence_id": evidence_id,
                                      "content": json.dumps({"evidence_id": evidence_id, "outcome": evidence["outcome"],
                                                             "observed_result": result,
                                                             **({'execution_feedback':payload_feedback} if payload_feedback else {}),
                                                             **({'execution_reference':prepared_reference} if prepared_reference else {}),
                                                             **({'progress_feedback':feedback} if feedback else {})}, ensure_ascii=False, default=str)})
            if identity_mismatch:
                state["status"] = "blocked"
                state["message"] = "A tool returned an explicit patient or case identity outside the active scope; content was quarantined."
            if canonical(call.name) in {'cm_outreach.send_message','p2p_session.send_turn'}:
                state['conversation_observation_fence']={'tool':canonical(call.name),'evidence_id':evidence_id,
                    'outcome':evidence['outcome'],'proposal_round':proposal_round}
            if newly_recorded:
                from .dialogue_guard import observe as observe_dialogue
                if observe_dialogue(state,call.name,call.arguments,result,evidence_id,evidence['outcome']):
                    if self.progress:self.progress('conversation_repetition_stopped',tool_name=canonical(call.name))
                    state['messages'].append({'role':'user','content':json.dumps(dialogue_blocked(state,call.name))})
            self._save(scope, state, owner, fence)
            if state.get("status") == "blocked":
                return state, fence
        return self.store.load_case(scope), fence

    def _identity_scope(self, scope: Scope, state: dict[str, Any]) -> Scope:
        view = scope
        case_binding = state.get("case_bindings")
        if case_binding is not None:
            if (not isinstance(case_binding, dict)
                    or scope.case != f"case-subject:{scope.patient}"
                    or case_binding.get("case_namespace") != scope.case
                    or case_binding.get("patient_id") != scope.patient
                    or not isinstance(case_binding.get("case_id"), str)
                    or not case_binding["case_id"].strip()
                    or case_binding["case_id"].startswith("case-subject:")
                    or case_binding.get("source_tool") not in self.case_identity_tools
                    or not isinstance(case_binding.get("source_evidence_id"), str)
                    or not case_binding["source_evidence_id"].startswith("ev:")):
                raise IsolationError("invalid persisted provider case binding")
            view = replace(view, case=case_binding["case_id"])
        binding = state.get("identity_bindings")
        if binding:
            if (scope.patient != f"case-subject:{scope.case}" or binding.get("case_id") != scope.case
                    or not isinstance(binding.get("patient_id"), str)
                    or not binding["patient_id"] or binding["patient_id"].startswith("case-subject:")):
                raise IsolationError("invalid persisted case patient binding")
            # This validation view never changes the durable case namespace/key.
            view = replace(view, patient=binding["patient_id"])
        principal_binding = state.get("principal_bindings")
        if principal_binding:
            if (not isinstance(principal_binding, dict)
                    or principal_binding.get("principal_namespace") != scope.principal
                    or not isinstance(principal_binding.get("principal_id"), str)
                    or not principal_binding["principal_id"].strip()
                    or principal_binding["principal_id"].startswith("case-subject:")
                    or principal_binding.get("case_id") != scope.case
                    or principal_binding.get("source_tool") not in self.principal_identity_result_paths
                    or not isinstance(principal_binding.get("source_evidence_id"), str)
                    or not principal_binding["source_evidence_id"].startswith("ev:")
                    or principal_binding.get("method") != "same_case_trusted_review_actor_result"):
                raise IsolationError("invalid persisted case principal binding")
            source_evidence = next((item for item in state.get("evidence", [])
                                    if isinstance(item, dict)
                                    and item.get("id") == principal_binding["source_evidence_id"]), None)
            evidence_scope = source_evidence.get("scope") if isinstance(source_evidence, dict) else None
            if (source_evidence is None
                    or source_evidence.get("outcome") != "success"
                    or source_evidence.get("tool") != principal_binding["source_tool"]
                    or not isinstance(evidence_scope, dict)
                    or evidence_scope.get("case") != scope.case):
                raise IsolationError("principal binding lacks matching same-case successful evidence")
            view = replace(view, principal=principal_binding["principal_id"])
        return view

    def _check_result_identity(self, result: Any, scope: Scope, state: dict[str, Any],
                               tool_name: str) -> tuple[Any, str | None, bool, str | None, str | None]:
        expected = self._identity_scope(scope, state)
        candidate = None
        candidate_case = None
        candidate_principal = None
        try:
            is_error = isinstance(result, dict) and ("error" in result or result.get("isError") is True)
            if (scope.case == f"case-subject:{scope.patient}" and tool_name in self.case_identity_tools
                    and not state.get("case_bindings") and not is_error):
                candidate_case = resolve_actual_case_id(result, scope)
                expected = replace(scope, case=candidate_case)
            if (scope.patient == f"case-subject:{scope.case}" and tool_name in self.patient_identity_tools
                    and not is_error):
                existing = state.get("identity_bindings", {}).get("patient_id")
                trusted_path = self.patient_identity_result_paths.get(tool_name)
                candidate = (resolve_patient_identity_at_path(result, scope, trusted_path, existing)
                             if trusted_path is not None
                             else resolve_patient_identity(result, scope, existing))
                if candidate:
                    expected = replace(expected, patient=candidate)
            principal_path = self.principal_identity_result_paths.get(tool_name)
            if principal_path is not None and not is_error:
                principal_bindings = state.get("principal_bindings", {})
                existing_principal = principal_bindings.get("principal_id") if isinstance(principal_bindings, dict) else None
                candidate_principal = _resolve_principal_identity_at_path(
                    result, scope, principal_path, existing_principal)
                if candidate_principal:
                    expected = replace(expected, principal=candidate_principal)
            mismatches = self._result_identity_mismatches(result, expected)
        except IdentityResolutionError:
            mismatches = ["actor_identity_binding_conflict"]
        if mismatches:
            return ({"error": "result_identity_mismatch", "mismatched_fields": mismatches,
                     "detail": "Returned content was quarantined before it entered case context."}, None, True, None, None)
        return result, candidate, False, candidate_case, candidate_principal

    def _observed_local_call(self, scope, state, call, owner, fence):
        # Separate event kinds preserve external dispatch accounting.
        started=time.monotonic()
        if self.progress:self.progress('local_tool_started',tool_name=call.name)
        status='error'
        try:
            result=self._local_call(scope,state,call,owner,fence)
            status=('error' if isinstance(result,dict) and result.get('error')
                    and result.get('field_status')!='absent_in_original_observation' else 'success')
            return result
        finally:
            if self.progress:self.progress('local_tool_finished',tool_name=call.name,
                result_status=status,elapsed_seconds=time.monotonic()-started)

    def _narrative_progress(self,event,**fields):
        if self.progress:self.progress(event,tool_name='case.search_narrative',**fields)

    def _local_call(self, scope: Scope, state: dict[str, Any], call: ToolCall, owner: str, fence: int) -> Any:
        args = call.arguments
        if call.name == 'case.get_goal_state':
            from .goal_state import view, public_task_text
            result=view(state,blocker_id=args.get('blocker_id'),offset=args.get('offset',0),
                        work_offset=args.get('work_offset',0),limit=args.get('limit',4),max_chars=10000)
            if 'instruction_offset' in args or 'instruction_limit' in args:
                instruction=public_task_text(state);start=min(args.get('instruction_offset',0),len(instruction))
                end=min(len(instruction),start+args.get('instruction_limit',4000))
                result['original_instruction']={'text':instruction[start:end],'offset':start,'next_offset':end,
                    'has_more':end<len(instruction),'total_chars':len(instruction),'kind':'public_task_instruction',
                    'instruction_sha256':hashlib.sha256(instruction.encode()).hexdigest()}
            return result
        from .assignment import local_tool_allowed
        if not local_tool_allowed(state.get('domain'),call.name):
            raise IsolationError('local operation is not permitted in this task domain; do not retry an incompatible handoff')
        if call.name == 'case.record_authorized_statements':
            from .authorized_statements import record
            result = record(state, args)
            self._save(scope, state, owner, fence)
            return result
        if call.name=='case.audit_assignment':
            from .assignment import completion_audit
            if state.get('completion_contract_sha256')!=_completion_contract_hash(state.get('completion_contract')):
                raise IsolationError('assignment contract integrity check failed')
            return completion_audit(state,self._identity_scope(scope,state).to_dict())
        if call.name=='case.record_external_handoff':
            from .assignment import completion_audit
            if state.get('domain')!='UM':raise IsolationError('this handoff requires the UM information-request contract')
            if state.get('completion_contract_sha256')!=_completion_contract_hash(state.get('completion_contract')):
                raise IsolationError('assignment contract integrity check failed')
            audit=completion_audit(state,self._identity_scope(scope,state).to_dict())
            if not audit.get('structural_accepted') or audit.get('allows_external_wait') is not True:
                raise ValueError('required MD decision, information notice and fresh scoped handoff evidence must be observed first')
            from .planning import source
            for source_id in args['evidence_ids']:source(state,source_id)
            obligation=next((o for o in state['obligations'] if o['id']==args['id']),None)
            if obligation is None or obligation.get('status') not in {'open','deferred'}:
                raise ValueError('handoff must refer to an existing outstanding obligation')
            obligation.update(status='deferred',evidence_ids=list(dict.fromkeys(args['evidence_ids'])),
                next_action=args['next_action'],handoff_branch=audit['branch_id'])
            self._save(scope,state,owner,fence)
            return {'id':args['id'],'deferred':True,'obligation_completed':False,'handoff_branch':audit['branch_id'],
                'delivery_previously_observed':True,'notification_sent_by_this_tool':False,'creates_evidence':False}
        if call.name=='case.search_narrative':
            from .hybrid_search import HybridIndex,DockerEmbedder,CorpusCoverageError,relevance_settings
            from .retrieval import _strings
            from .working_set import business,packed
            namespace=packed(scope.to_dict());documents=[];traversal_partial=False
            sources={e['id']:e for e in state['evidence']}
            for source_id in args['ids']:
                source=sources.get(source_id)
                if source is None or source.get('scope')!=scope.to_dict() or source.get('outcome')!='success':
                    raise IsolationError('narrative search requires successful evidence from this exact case')
            for source_id in args['ids']:
                source=sources.get(source_id)
                traversal={'visited':0,'partial':False}
                for path,text in _strings(business(source['observed_result']),work=traversal):
                    if len(text)<80:continue
                    leaf=path.rsplit('/',1)[-1].casefold()
                    if leaf in {'id','path','sha256','status','code','npi','dob','member_number'} or leaf.endswith(('_id','_code')):continue
                    documents.append({'id':source_id+':'+path,'title':path,'text':text,
                        'source':{'evidence_id':source_id,'text_pointer':path,'source_text_sha256':hashlib.sha256(text.encode()).hexdigest()}})
                traversal_partial=traversal_partial or traversal['partial']
            if traversal_partial:
                return {'error':'corpus_coverage_incomplete','semantic_executed':False,
                    'instruction':'Source traversal was incomplete. No partial-corpus ranking was returned; use exact source inspection.'}
            if self._narrative_index is None or self._narrative_index.namespace!=namespace:
                self._narrative_index=HybridIndex(namespace,DockerEmbedder(),
                    relevance_floor=relevance_settings('narrative')['minimum_cosine'],progress=self._narrative_progress,query_cache=True)
            try:
                result=self._narrative_index.search(documents,args['query'],namespace=namespace,
                    limit=args.get('max_results',5),max_chars=args.get('max_chars',16000))
            except CorpusCoverageError:
                return {'error':'corpus_coverage_incomplete','semantic_executed':False}
            except RuntimeError:
                return {'error':'semantic_backend_unavailable','semantic_executed':False,
                    'instruction':'No semantic result was produced. Exact structured reads and literal search remain available; do not infer that no relevant narrative exists.'}
            return result
        if call.name == 'case.retrieve_evidence':
            from .retrieval import retrieve_evidence
            return retrieve_evidence(state,args['requests'],max_chars=args.get('max_chars',16000),
                                     request_offset=args.get('request_offset',0))
        if call.name == 'case.record_policy_decision':
            from .policy_grounding import record_decision, operation_name
            record=record_decision(state,args,{operation_name(s.name) for s in self._tool_map().values()},
                                   self._identity_scope(scope,state).to_dict())
            self._save(scope,state,owner,fence)
            return {'record_id':record['id'],'provenance_verified':True,'semantic_correctness':'not_assessed',
                    'creates_evidence':False,'applies_to':record['applies_to'],
                    'prepared_actions':[{'operation':op,'commit':{'tool':'case.execute_recorded_action',
                        'arguments':{'record_id':record['id'],'operation':op}}} for op in record['bound_arguments']],
                    'instruction':'Prepared commands are optional execution references, not approvals. You choose whether to execute; code rechecks sources, scope, arguments and consequential review before dispatch.'}
        if call.name == 'case.request_identity_reselection':
            from .reselection import write_requires_reconciliation
            ids=set(args.get('evidence_ids',[]))
            known={e['id'] for e in state['evidence'] if e.get('scope')==scope.to_dict() and e.get('outcome')=='success'}
            if not ids.issubset(known):raise IsolationError('reselection citations must belong to this case')
            actions=self.store.actions(scope)
            writes=[a for a in actions if write_requires_reconciliation(
                a.get('tool'),a.get('effect'),a.get('status'),a.get('result'))]
            # A failed response may follow a committed effect. No blanket
            # assumption that an error/timeout undid a clinical mutation.
            blocked=bool(writes)
            state['identity_reselection']={'requested':True,'reason':args['reason'],'evidence_ids':sorted(ids),
                'reset_allowed':not blocked,'requires_reconciliation':blocked,
                'external_write_action_ids':[a['id'] for a in writes]}
            state['status']='blocked' if blocked else 'reselection_requested'
            state['message']=('Identity reconsideration requires reconciliation of existing external writes.' if blocked
                              else 'Identity reconsideration requested; quarantine this context before rediscovery.')
            self._save(scope,state,owner,fence)
            return {'status':state['status'],'reset_allowed':not blocked,'creates_evidence':False}
        if call.name == 'case.inspect_evidence':
            from .working_set import inspect_source, missing_path_feedback
            source = next((e for e in state['evidence'] if e['id'] == args['id']), None)
            if source is None or source.get('outcome') != 'success' or source.get('scope') != scope.to_dict():
                raise IsolationError('inspection requires successful evidence from this exact case')
            try:
                view=inspect_source(source['observed_result'], args.get('path',''), args.get('offset',0), args.get('limit',2000),
                                    representation=args.get('representation','business'))
            except (KeyError,TypeError):
                view=missing_path_feedback(source['observed_result'],args.get('path',''),args.get('representation','business'))
            return {'id':source['id'],'creates_evidence':False,**view}
        if call.name == 'case.get_tool_contract':
            from .schema import tool_parameter_schema
            from .assignment import resolve_tool
            spec=resolve_tool(self._available_specs(self._tool_map(),state),args['tool_name'])
            schema=tool_parameter_schema(spec.input_schema)
            return {'name':spec.name,'description':spec.description,'input_schema':schema,
                'required_input_fields':schema.get('required',[]),
                'optional_input_fields':[k for k in schema.get('properties',{}) if k not in schema.get('required',[])],
                'effect':spec.effect,'creates_evidence':False,
                'warning':'This is the declared API contract. Required input fields, optional defaults, and clinical policy requirements are different. Output-field absence does not establish a mandatory prerequisite.'}
        if call.name == 'case.get_working_record':
            from .planning import working_record_view
            return working_record_view(state,args)
        if call.name == 'case.record_working_note':
            from .planning import record_note
            result=record_note(state,args)
            if self._helper_channel:
                state['working_notes'][-1]['helper_job_id']=self._helper_channel['id']
            self._save(scope,state,owner,fence)
            return result
        if call.name == 'case.record_blocker':
            from .planning import record_blocker
            result=record_blocker(state,args,self._available_specs(self._tool_map(),state))
            if self._helper_channel:
                state['prerequisite_records'][-1]['helper_job_id']=self._helper_channel['id']
            self._save(scope,state,owner,fence)
            return result
        if call.name == 'case.find_evidence':
            from .working_set import canonical
            query = args.get('query','').casefold(); offset = args.get('offset',0)
            items = [{'id':e['id'],'tool':canonical(e['tool']),'outcome':e['outcome']} for e in state['evidence']
                     if query in (canonical(e['tool']) + ' ' + e['id']).casefold()]
            return {'items': items[offset:offset+20], 'total':len(items),
                    'next_offset':offset+20 if offset+20<len(items) else None}
        if call.name == 'case.discover_tools':
            from .working_set import canonical,rank_tools
            query = args['query'].casefold(); offset = args.get('offset',0)
            registry = list(self._tool_map().values())
            matches = rank_tools(registry,query)
            selected = matches[offset:offset+8]
            state['activated_tools'] = list(dict.fromkeys([*state.get('activated_tools',[]), *[s.name for s in selected]]))[-16:]
            self._save(scope,state,owner,fence)
            return {'tools':[{'name':s.name,'operation':canonical(s.name),'description':s.description[:160]} for s in selected],
                    'total':len(matches),'next_offset':offset+8 if offset+8<len(matches) else None,
                    'exact_operation_present':any(query == canonical(s.name).casefold() for s in registry),
                    'instruction':'Ranked available operations, not proof a requested API exists. Selected aliases are available next turn; use their supplied schemas. The complete operation index is in the working set.'}
        if call.name == 'case.get_role':
            role = next((r for r in roles_for(state['domain']) if r['id'] == args['role_id']),None)
            if role is None: raise IsolationError('role is outside this domain/shared catalog')
            return role
        if call.name == "case.defer_obligation":
            from .completion_contracts import _payload_path, _tool_matches
            from .closure import assess_closure
            contract = state.get("completion_contract")
            if (not isinstance(contract, dict)
                    or _completion_contract_hash(contract) != state.get("completion_contract_sha256")):
                raise IsolationError("a pinned workflow contract is required for deferral")
            gate = assess_closure(state,self._identity_scope(scope,state).to_dict())
            if not gate.get("structural_accepted") or gate.get('allows_external_wait') is not True:
                raise ValueError("deferral requires a verified provider information-gathering handoff")
            selected = [item for item in state["evidence"] if item.get("id") in args["evidence_ids"]]
            if (len({item["id"] for item in selected}) != len(set(args["evidence_ids"]))
                    or any(item.get("outcome") != "success" or item.get("scope") != scope.to_dict() for item in selected)):
                raise IsolationError("deferral references must be successful same-case observations")
            # Do not defer form preparation as though it were an external document.
            last_write = max((i for i, item in enumerate(state["evidence"])
                              if item.get("effect") == "write" and item.get("outcome") == "success"), default=-1)
            if not any(item in selected and i > last_write and item.get("effect") == "read"
                       and _tool_matches(item.get("tool", ""), ["cases.get_case"])
                       and _payload_path(item.get("observed_result"), "form_validation.complete") is True
                       for i, item in enumerate(state["evidence"])):
                raise ValueError("deferral needs a fresh case readback confirming completed form preparation")
            obligation = next((item for item in state["obligations"] if item["id"] == args["id"]), None)
            if obligation is None or obligation.get("status") not in {"open", "deferred"}:
                raise ValueError("only an outstanding obligation can be deferred")
            obligation.update(status="deferred", evidence_ids=list(dict.fromkeys(args["evidence_ids"])),
                              next_action=args["next_action"], handoff_branch=gate["branch_id"])
            self._save(scope, state, owner, fence)
            return {"deferred": True, "id": args["id"], "handoff_branch": gate["branch_id"],
                    "obligation_completed": False, "notification_sent": False}
        if call.name == "case.add_obligation":
            existing = next((item for item in state["obligations"] if item.get("id") == args["id"]), None)
            proposed = {"id": args["id"], "description": args["description"], "owner": args.get("owner"),
                        "status": "open", "evidence_ids": []}
            if "depends_on" in args:
                proposed["depends_on"] = list(args["depends_on"])
            validate_dependencies(state["obligations"], proposed)
            if existing and existing != proposed:
                raise ConflictError("obligation ID already exists with different content")
            if not existing:
                state["obligations"].append(proposed)
                self._save(scope, state, owner, fence)
            return {"recorded": True, "obligation": proposed}
        if call.name == "case.close_obligation":
            item = next((item for item in state["obligations"] if item.get("id") == args["id"]), None)
            if item is None:
                raise KeyError("obligation does not exist")
            dependencies = set(item.get("depends_on", []))
            if any(other["id"] in dependencies and other.get("status") != "closed"
                   for other in state["obligations"]):
                raise ValueError("obligation prerequisites must be closed first")
            evidence_by_id = {e["id"]: e for e in state["evidence"]}
            if any(eid not in evidence_by_id or evidence_by_id[eid].get("outcome") != "success" for eid in args["evidence_ids"]):
                raise IsolationError("closure must cite evidence recorded from this case's completed tool actions")
            item["status"] = "closed"
            item["evidence_ids"] = list(dict.fromkeys(args["evidence_ids"]))
            self._save(scope, state, owner, fence)
            return {"closed": True, "id": item["id"], "evidence_ids": item["evidence_ids"]}
        if call.name == "case.read_evidence":
            item = next((item for item in state["evidence"] if item.get("id") == args["id"]), None)
            if item is None:
                raise KeyError("evidence ID is not present in this case")
            serialized = json.dumps(item.get("observed_result"), ensure_ascii=False, sort_keys=True, default=str)
            start = args["offset"]
            end = min(len(serialized), start + args["length"])
            return {"id": item["id"], "offset": start, "total_chars": len(serialized),
                    "text": serialized[start:end], "has_more": end < len(serialized), "outcome": item.get("outcome")}
        if call.name == "case.search_evidence":
            item = next((item for item in state["evidence"] if item.get("id") == args["id"]), None)
            if item is None:
                raise KeyError("evidence ID is not present in this case")
            if item.get("scope") != scope.to_dict() or item.get("outcome") != "success":
                raise IsolationError("only successful evidence from this exact case can be searched")
            serialized = json.dumps(item.get("observed_result"), ensure_ascii=False, sort_keys=True, default=str)
            query = args["query"]
            limit = min(args.get("max_results", 3), 5)
            matches = []
            has_more = False
            for match in re.finditer(re.escape(query), serialized, flags=re.IGNORECASE):
                if len(matches) >= limit:
                    has_more = True
                    break
                match_start, match_end = match.span()
                start = max(0, match_start - 150)
                end = min(len(serialized), start + 400)
                if match_end > end:
                    start = max(0, match_end - 400)
                    end = min(len(serialized), start + 400)
                matches.append({"offset": start, "length": end - start,
                                "text": serialized[start:end], "match_offset": match_start})
            return {"id": item["id"], "total_chars": len(serialized),
                    "matches": matches, "has_more": has_more}
        if call.name == "case.request_helper":
            from .helper_jobs import run_helper
            return run_helper(self,scope,state,call,owner,fence)
        raise ValueError("unsupported local case operation")

    def _check_runtime(self):
        if self.runtime_guard is not None:self.runtime_guard()

    def _request_disconnection_retry(self,state,error,*,helper_id=None):
        if (not can_retry_disconnected_generation(error)
                or state.get('model_transport_retry_streak',0)>=1
                or state['model_calls']>=self.limits.max_model_calls):
            return False
        state['model_transport_retry_streak']=state.get('model_transport_retry_streak',0)+1
        record={'failed_model_call':state['model_calls'],'retry_model_call':state['model_calls']+1,
                'failure_category':error.failure_category,'proposal_dispatched':False}
        if helper_id is not None:record['helper_id']=helper_id
        state.setdefault('model_transport_retries',[]).append(record)
        state.update(status='running',message='Retrying a disconnected model generation once; no proposal was dispatched.')
        if self.progress:self.progress('model_transport_retry',after_model_call=state['model_calls'])
        return True

    def _request_final_reference_correction(self,state,payload):
        if state.get('final_format_retry_count',0)>=1 or state.get('model_calls',0)>=self.limits.max_model_calls:
            return False
        from .working_set import canonical
        successful=[e for e in state.get('evidence',[]) if e.get('scope')==state.get('scope') and e.get('outcome')=='success']
        requested=[]
        record=payload.get('stop_assessment')
        if not isinstance(record,dict):record={}
        for value in (payload.get('evidence_ids'),record.get('evidence_ids'),record.get('investigations_performed')):
            if isinstance(value,list):requested.extend(x for x in value if isinstance(x,str))
        selected=[e for e in successful if e['id'] in requested]
        selected.extend(e for e in successful[-12:] if e not in selected)
        if not selected:return False
        from .closure import investigation_source_ids
        investigative=investigation_source_ids(state)
        sources=[{'id':e['id'],'tool':canonical(e['tool']),'read':e.get('effect')=='read',
                  'investigation_eligible':e['id'] in investigative} for e in selected]
        state['final_format_retry_count']=state.get('final_format_retry_count',0)+1
        failure_stage=state.get('stop_assessment_validation',{}).get('reason_code')
        accounting=failure_stage in {'stop_dependencies_not_accounted_for','stop_blocked_work_not_accounted_for','stop_work_accounting_conflict'}
        state.setdefault('final_format_retries',[]).append({'retry_number':state['final_format_retry_count'],
            'failed_model_call':state['model_calls'],'retry_model_call':state['model_calls']+1,
            'error_type':'FinalWorkAccountingError' if accounting else 'FinalEvidenceReferenceError'})
        state['final_format_retry_pending']=True
        state['messages'].append({'role':'user','content':
            'Reference-only correction: the final JSON source references or saved-work accounting did not validate. '
            'No new tool action is needed or permitted for this correction. Local assignment audits, notes and '
            'deferral operations do not create clinical evidence IDs. Do not manufacture an ev: ID for them. '
            'Use successful original case observations; investigations_performed must cite investigation_eligible sources '
            '(original reads or observed counterparty replies, not authored summaries or terminal writes). '
            'Preserve the clinical decision and supported facts. Return corrected final JSON only, with honest '
            'uncertainty if the original claim cannot be supported. Put both work lists INSIDE stop_assessment, '
            'not only at the top level: stop_assessment.waiting_on_obligation_ids must equal '
            'the saved deferred-obligation IDs; stop_assessment.blocked_obligation_ids must equal the saved source-linked blocked IDs. '
            'These lists describe existing work; they do not close it or establish clinical completion. '
            'Required work accounting: '+json.dumps({k:state.get('completion_gate',{}).get(k,[]) for k in
                ('deferred_obligation_ids','blocked_obligation_ids')})+
            '. Available original sources: '+json.dumps(sources)})
        state.update(status='running',message='Requesting one tool-free correction of the final evidence/work-accounting record.')
        return True

    def _accept_final(self, state: dict[str, Any], content: str) -> dict[str, Any]:
        from .closure import assess_closure, assess_stop_record, derive_stop_metadata
        state['stop_review_required'] = False
        # Always assess the actual state, including when the worker says incomplete.
        # Identity/contract errors fail closed and cannot be hidden by deferrals.
        try:
            actual = self._identity_scope(Scope(**state['scope']),state).to_dict()
            gate = assess_closure(state,actual)
        except IsolationError:
            gate = {'accepted':False,'structural_accepted':False,'branch_id':None,
                    'missing_milestones':[],'reason_code':'completion_identity_binding_invalid'}
        except Exception as exc:
            gate = {'accepted':False,'structural_accepted':False,'branch_id':None,
                    'missing_milestones':[],'reason_code':'completion_validator_unavailable',
                    'validator_error_type':type(exc).__name__}
        state['completion_gate'] = gate
        if gate.get('reason_code') in {'completion_contract_integrity_error','completion_contract_task_mismatch',
                'completion_identity_binding_invalid','completion_validator_unavailable'}:
            state.update(status='unresolved',completion=None,final=content,
                message='Finalization rejected because the pinned contract or identity assessment is invalid; no source correction or workflow success is authorized.')
            return state
        try:
            payload = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            state["status"] = "unresolved"
            state["message"] = "The model returned prose without the required structured completion record."
            state["final"] = content
            return state
        state["final"] = payload
        if (not isinstance(payload, dict) or not isinstance(payload.get('status'),str)
                or payload['status'] not in {'complete','incomplete'}):
            state["status"] = "unresolved"
            state["message"] = "The structured response did not claim scoped completion."
            return state
        normalized,derivation=derive_stop_metadata(state,payload,gate)
        state.pop('stop_metadata_derivation',None)
        state.pop('final_submitted',None)
        if derivation:
            state['final_submitted']=payload
            state['stop_metadata_derivation']=derivation
            payload=normalized;state['final']=payload
        stop = assess_stop_record(state,payload,gate)
        state['stop_assessment_validation'] = stop
        if (isinstance(payload.get('stop_assessment'),dict) and not stop['accepted']
                and stop.get('reason_code') in {'stop_evidence_unverified','stop_investigation_evidence_unverified',
                    'stop_dependencies_not_accounted_for','stop_blocked_work_not_accounted_for','stop_work_accounting_conflict'}
                and self._request_final_reference_correction(state,payload)):
            return state
        if (not stop['accepted'] and stop.get('reason_code') in {
                'stop_dependencies_not_accounted_for','stop_blocked_work_not_accounted_for','stop_work_accounting_conflict'}
                and state.get('final_format_retry_count',0)>=1):
            state.update(status='unresolved',stop_review_required=False,
                workflow_stop_reason='stop_report_accounting_repair_exhausted',
                message='Final stop work accounting did not validate after its bounded correction ('+stop['reason_code']+'); unfinished work remains.')
            return state
        if payload['status'] != 'complete' and not stop['accepted']:
            state['stop_review_required'] = gate.get('accepted') is True
            state['status'] = 'unresolved'
            state['message'] = 'The structured response did not claim scoped completion.'
            if (stop.get('reason_code') in {'stop_evidence_unverified','stop_investigation_evidence_unverified',
                    'stop_dependencies_not_accounted_for','stop_blocked_work_not_accounted_for','stop_work_accounting_conflict'}
                    and state.get('final_format_retry_count',0)>=1):
                state['workflow_stop_reason']='stop_report_reference_repair_exhausted'
                state['stop_review_required']=False
                state['message']='The incomplete stop report still has invalid source references after its bounded correction; no workflow success is claimed.'
            return state
        claim = payload.get("claim")
        evidence_ids = payload.get("evidence_ids")
        if not isinstance(claim, str) or not claim.strip() or not isinstance(evidence_ids, list) or not evidence_ids:
            state["status"] = "unresolved"
            state["message"] = "Completion requires a claim and supporting observed evidence IDs."
            return state
        if any(not isinstance(evidence_id, str) or not evidence_id for evidence_id in evidence_ids):
            state["status"] = "unresolved"
            state["message"] = "Completion evidence IDs must be non-empty strings."
            return state
        successful = {e["id"] for e in state["evidence"] if e.get("outcome") == "success"}
        if not set(evidence_ids) <= successful:
            if self._request_final_reference_correction(state,payload):
                return state
            state["status"] = "unresolved"
            state["message"] = "Completion cited evidence outside this case's observed action journal."
            return state
        if payload['status']=='incomplete' and stop['accepted'] and gate.get('accepted') is not True:
            # A valid report of an unsuccessful stop is not clinical completion.
            # The independent gate and all unmet obligations remain untouched.
            state.update(status='unresolved',completion=None,
                workflow_stop_reason='source_backed_incomplete_stop',
                message='Execution stopped with an evidence-linked incomplete report; requested workflow completion remains unverified.')
            return state
        open_items = gate.get('open_obligation_ids',[])
        if open_items and gate.get('accepted') is not True:
            state["status"] = "unresolved"
            state["message"] = "Completion is blocked by open obligations: " + ", ".join(open_items)
            return state
        contract = state.get("completion_contract")
        if gate.get('reason_code')=='completion_contract_integrity_error':
            state["status"] = "unresolved"
            state["completion"] = None
            state["message"] = "The pinned completion contract failed its integrity check."
            return state
        deferred = [item for item in state["obligations"] if item.get("status") == "deferred"]
        if gate.get("accepted") is not True:
            corrections = state.get("completion_gate_corrections", 0)
            contract_mapped = isinstance(contract, dict) and contract.get("mapping_status") == "mapped"
            if (contract_mapped and isinstance(corrections, int) and not isinstance(corrections, bool)
                    and corrections < 2 and state.get("model_calls", 0) < self.limits.max_model_calls):
                corrections += 1
                state["completion_gate_corrections"] = corrections
                missing = gate.get("missing_milestones")
                if not isinstance(missing, list):
                    missing = []
                safe_missing = [item[:120] for item in missing
                                if isinstance(item, str) and item][:20]
                state["messages"].append({"role": "user", "content":
                    "The harness could not verify the requested workflow's terminal condition from trusted, "
                    "case-local tool readbacks. Continue the original task using the declared tools and the "
                    "fixed completion contract in the case ledger. Resolve only the listed missing milestones "
                    f"if they apply: {json.dumps(safe_missing, ensure_ascii=False)}. Obtain a successful readback "
                    "after the latest write when the contract requires it. Do not claim a result that is not "
                    "present in observed tool output, and do not repeat a write whose outcome is unknown."})
                state["status"] = "running"
                state["message"] = "A completion claim lacked trusted terminal evidence; continuing within the configured workflow budget."
                return state
            state["status"] = "unresolved"
            state["message"] = "The task-specific terminal condition was not verified by trusted same-case readback evidence."
            return state
        if gate.get('requires_stop_assessment') and not stop['accepted']:
            if stop['reason_code'] in {'stop_evidence_unverified','stop_investigation_evidence_unverified'}:
                if self._request_final_reference_correction(state,payload):return state
            state.update(status='unresolved',stop_review_required=True,
                message='Supported endpoint effects are recorded; assess remaining useful permitted actions and acknowledge unfinished work before stopping.')
            return state
        if isinstance(payload.get('stop_assessment'),dict) and not stop['accepted']:
            state.update(status='unresolved',stop_review_required=True,
                message='The worker reports remaining actions or an unsupported no-further-action record.')
            return state
        state["status"] = "complete"
        state["workflow_stop_reason"] = None
        state["completion"] = {"claim": claim, "evidence_ids": list(dict.fromkeys(evidence_ids)),
                               "scope": state["scope"], "kind": (
                                   "task-contract verified handoff; external work remains; not official benchmark success"
                                   if deferred else
                                   "task-contract verified local workflow; acknowledged blocked duties remain open; not official benchmark success"
                                   if gate.get('outstanding_obligation_ids') else
                                   "task-contract verified local workflow; not official benchmark success"),
                               "outstanding_obligations": list(gate.get('outstanding_obligation_ids', [])),
                               "branch_id": gate.get("branch_id"), "proof_kind": gate.get("proof_kind"),
                               "has_deferred_work": bool(deferred),
                                "execution_endpoint":'no_further_permitted_action',
                                "model_reported_status":payload['status'],
                                "stop_assessment":payload.get('stop_assessment'),
                                "stop_assessment_validation":stop,
                               "deferred_obligations": [item["id"] for item in deferred]}
        state["message"] = "The harness verified the task-specific terminal condition with case-local tool evidence."
        if gate.get('outstanding_obligation_ids'):
            state['message'] += (' Acknowledged blocked duties remain open: '
                                 + ', '.join(gate['outstanding_obligation_ids']) + '.')
        if gate.get('requested_outcome',{}).get('status') == 'unmet':
            state['message'] = 'Execution finished at a supported stopping endpoint; the original requested outcome remains unmet. This is not benchmark success.'
        return state

    def _tool_map(self) -> dict[str, ToolSpec]:
        specs = self.tools.list_tools()
        names = [spec.name for spec in specs]
        if len(set(names)) != len(names):
            raise ValueError("tool names must be unique before harness execution")
        if set(names) & {spec.name for spec in _LOCAL_SPECS}:
            raise ValueError("remote tools cannot shadow local case operations")
        return {spec.name: spec for spec in specs}

    def _available_specs(self, remote: dict[str, ToolSpec], state=None) -> list[ToolSpec]:
        from .assignment import local_tool_allowed
        locals_allowed = [spec for spec in _LOCAL_SPECS if (spec.name != "case.request_helper" or self.composition != "combined")
            and (state is None or local_tool_allowed(state.get('domain'),spec.name))
            and (state is None or spec.name!='case.record_external_handoff' or state.get('domain')=='UM')]
        return [*remote.values(), *locals_allowed]

    @staticmethod
    def _call_dict(call: ToolCall) -> dict[str, Any]:
        return {"id": call.id, "name": call.name, "arguments": call.arguments}

    @staticmethod
    def _should_request_model(state: dict[str, Any]) -> bool:
        if not state["messages"]:
            return True
        last = state["messages"][-1]
        return last.get("role") != "assistant" or bool(last.get("tool_calls"))

    @staticmethod
    def _pending_tool_calls(state: dict[str, Any]) -> list[dict[str, Any]]:
        for index in range(len(state["messages"]) - 1, -1, -1):
            message = state["messages"][index]
            if message.get("role") == "assistant" and message.get("tool_calls"):
                answered = {m.get("tool_call_id") for m in state["messages"][index + 1:] if m.get("role") == "tool"}
                return [call for call in message["tool_calls"] if call.get("id") not in answered]
        return []

    @staticmethod
    def _result_identity_mismatches(value: Any, scope: Scope) -> list[str]:
        expected = scope.to_dict()
        mismatches: list[str] = []

        def visit(node: Any, path: str = "$") -> None:
            if isinstance(node, dict):
                for key, item in node.items():
                    if key in {"patient_id", "case_id", "patientId", "caseId"}:
                        kind = "patient" if "patient" in key.lower() else "case"
                        if isinstance(item, str) and item != expected[kind]:
                            mismatches.append(f"{path}.{key}")
                    elif key in {"patient", "case"} and isinstance(item, dict) and isinstance(item.get("id"), str):
                        if item["id"] != expected[key]:
                            mismatches.append(f"{path}.{key}.id")
                    visit(item, f"{path}.{key}")
            elif isinstance(node, list):
                for index, item in enumerate(node):
                    visit(item, f"{path}[{index}]")
            elif isinstance(node, str) and node.lstrip().startswith(("{", "[")):
                try:
                    decoded = json.loads(node)
                except json.JSONDecodeError:
                    return
                visit(decoded, f"{path}<json>")

        visit(value)
        return list(dict.fromkeys(mismatches))

    def _save(self, scope: Scope, state: dict[str, Any], owner: str, fence: int) -> None:
        if state.get('goal_planning_enabled'):
            # Display/assessment uses the same validated binding view as actual
            # dispatch. This cached view never grants tool permissions.
            try:
                state['goal_actual_scope'] = self._identity_scope(scope,state).to_dict()
                state.pop('goal_scope_invalid',None)
            except (IsolationError,AttributeError,TypeError):
                # Persist the failure safely. Display calculation must not
                # prevent the existing dispatcher from recording its error.
                state.pop('goal_actual_scope',None)
                state['goal_scope_invalid']=True
        if self._helper_channel:
            channel=self._helper_channel
            for message in state['messages'][channel['message_start']:]:
                message['helper_job_id']=channel['id']
            for evidence in state.get('evidence',[])[channel['evidence_start']:]:
                evidence['helper_job_id']=channel['id']
        self.store.save_case(scope, state, state["version"], owner=owner, fence=fence)
        state["version"] += 1

    @staticmethod
    def _result(state: dict[str, Any]) -> dict[str, Any]:
        from .goal_state import execution_summary
        return {"status": state.get("status", "unresolved"), "message": state.get("message", ""),
                'execution_assessment':execution_summary(state),
                'goal_planning_enabled':state.get('goal_planning_enabled',False),
                'terminal_reviews':state.get('terminal_reviews',{}),
                'conversation_observation_fence':state.get('conversation_observation_fence'),
                'working_notes':state.get('working_notes',[]),
                'prerequisite_records':state.get('prerequisite_records',[]),
                'current_plan':state.get('current_plan'),
                'progress_recoveries':state.get('progress_recoveries',[]),
                'assignment_audit':state.get('assignment_audit'),
                'stop_assessment_validation':state.get('stop_assessment_validation'),
                'stage_guidance':state.get('stage_guidance'),
                'recovery_audit':state.get('recovery_audit'),
                'helper_jobs':[{k:j[k] for k in ('id','role_id','status','invocation','model_calls','tool_proposals','source_ids','result') if k in j}
                               for j in state.get('helper_jobs',[])],
                'policy_decisions':state.get('policy_decisions',[]),
                'policy_grounding_required':state.get('policy_grounding_required',False),
                'policy_decision_refusals':state.get('policy_decision_refusals',[]),
                'identity_reselection':state.get('identity_reselection'),
                "final": state.get("final"), "completion": state.get("completion"),
                "completion_gate": state.get("completion_gate"),
                "workflow_recoveries": state.get("workflow_recoveries", []),
                "workflow_stop_reason": state.get("workflow_stop_reason"),
                "workflow_guard_refusals": state.get("workflow_guard_refusals", []),
                "completion_gate_corrections": state.get("completion_gate_corrections", 0),
                "completion_contract_sha256": state.get("completion_contract_sha256"),
                "obligations": state.get("obligations", []), "evidence": state.get("evidence", []),
                "model_calls": state.get("model_calls", 0), "tool_calls": state.get("tool_calls", 0),
                "usage": state.get("usage", {}), "version": state.get("version", 0),
                "identity_bindings": state.get("identity_bindings", {}),
                "principal_bindings": state.get("principal_bindings", {}),
                "case_bindings": state.get("case_bindings", {}),
                "model_response_format_retry_count": state.get("model_response_format_retry_count", 0),
                "model_response_format_retries": state.get("model_response_format_retries", []),
                "model_transport_retries": state.get("model_transport_retries", []),
                "final_format_retry_count": state.get("final_format_retry_count", 0),
                "final_format_retries": state.get("final_format_retries", []),
                "pre_dispatch_validation_retry_count": state.get("pre_dispatch_validation_retry_count", 0),
                "pre_dispatch_validation_retries": state.get("pre_dispatch_validation_retries", []),
                "model_failure": state.get("model_failure"),
                "runtime_failure": state.get("runtime_failure")}

    @staticmethod
    def _merge_usage(state: dict[str, Any], usage: dict[str, Any]) -> None:
        totals = state.setdefault("usage", {})
        if not isinstance(usage, dict):
            return
        for name, value in usage.items():
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                totals[name] = totals.get(name, 0) + value
