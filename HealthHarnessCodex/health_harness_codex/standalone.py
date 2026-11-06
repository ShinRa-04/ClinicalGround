"""Run one explicit public χ-Bench case through the Codex-backed harness."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time
import traceback
from typing import Any
import unicodedata

from .codex_provider import CodexSessionModel, validate_active_timeout
from .completion_contracts import build_completion_contract
from .domain_profiles import (DOMAIN_PROFILES, DomainSpec, discover_domain_case, domain_for_task,
                              readback_domain_case)
from .docker_bridge import DockerExecutor, DockerMCPClient, DockerWorkspaceTools
from .engine import Harness
from .evaluation import RecordingModel, RecordingTools, RunRecorder
from .models import Limits, Scope, ToolSpec
from .providers import ModelResponseFormatError, format_correction, response_retry_limit, MAX_OUTPUT_LIMIT_CORRECTIONS
from .store import CaseStore
from .tools import ToolRegistry
from .workflow_guard import PayerRoutingGuard


DEFAULT_LIMITS = {"max_model_calls": 12, "max_tool_calls": 50,
                  "max_context_chars": 0, "max_output_tokens": 4000}
_MAX_INSTRUCTION_BYTES = 250_000
class StandaloneError(RuntimeError):
    pass


class _CaseSubjectNamespaceTools:
    """Guard against presenting an internal case namespace as a real patient ID."""

    def __init__(self, tools: Any, namespace: str, enabled: bool,
                 actual_names: dict[str, str] | None = None,
                 discovery_only_names: tuple[str, ...] | set[str] = (),
                 allowed_actor_namespaces: tuple[str, ...] | None = None,
                 case_namespace: str | None = None,
                 case_identity_names: tuple[str, ...] | set[str] = (),
                 case_scoped_names: tuple[str, ...] | set[str] = (),
                 patient_scoped_names: tuple[str, ...] | set[str] = (),
                 require_actual_case_for_writes: bool = False):
        self.tools = tools
        self.namespace = namespace
        self.enabled = enabled
        self.actual_names = dict(actual_names or {})
        self.discovery_only_names = frozenset(discovery_only_names)
        self.allowed_actor_namespaces = (frozenset(allowed_actor_namespaces)
                                          if allowed_actor_namespaces else None)
        self.case_namespace = case_namespace
        self.case_identity_names = frozenset(case_identity_names)
        self.case_scoped_names = frozenset(case_scoped_names)
        self.patient_scoped_names = frozenset(patient_scoped_names)
        self.case_identity_aliases = {alias for alias, actual in self.actual_names.items()
                                      if actual in self.case_identity_names}
        self.require_actual_case_for_writes = require_actual_case_for_writes
        self.actual_case_id: str | None = None
        self.discovery_aliases = {alias for alias, actual in self.actual_names.items()
                                  if actual in self.discovery_only_names}
        self.restricted_aliases = {
            alias for alias, actual in self.actual_names.items()
            if self.allowed_actor_namespaces is not None and actual.partition(".")[0] not in self.allowed_actor_namespaces
        }

    def bind_scope(self, scope: Scope) -> None:
        self.tools.bind_scope(scope)

    def bind_actual_case(self, binding: dict[str, Any]) -> None:
        case_id = binding.get("case_id")
        patient_id = binding.get("patient_id")
        source_tool = binding.get("source_tool")
        if (not isinstance(case_id, str) or not case_id or case_id.startswith("case-subject:")
                or not isinstance(patient_id, str) or not patient_id
                or source_tool not in self.case_identity_aliases):
            raise StandaloneError("workspace case binding did not match the trusted provider creation source")
        if self.actual_case_id is not None and self.actual_case_id != case_id:
            raise StandaloneError("workspace cannot be rebound to a different actual case")
        self.actual_case_id = case_id

    def list_tools(self):
        hidden = self.discovery_aliases | self.restricted_aliases
        visible = []
        for spec in self.tools.list_tools():
            if spec.name in hidden:
                continue
            actual = self.actual_names.get(spec.name)
            if actual == "cases.create_from_order":
                spec = ToolSpec(spec.name, spec.description + (
                    " Workflow clarification: source_order_id is optional. This operation may create a NEW "
                    "ServiceRequest from supported intake fields and a draft case; an empty existing-order list "
                    "does not itself prevent its use. Distinguish authorized creation of a new record from "
                    "inventing a historical order. Resolve actual provider IDs with people tools and ground "
                    "clinical/coding fields in the intake, chart, and approved references."
                ), spec.input_schema, spec.effect, spec.identity_fields)
            if actual in self.case_scoped_names:
                schema = deepcopy(spec.input_schema)
                properties = schema.setdefault("properties", {})
                properties.setdefault("case_id", {"type": "string", "minLength": 1})
                required = schema.setdefault("required", [])
                if "case_id" not in required:
                    required.append("case_id")
                identities = tuple(dict.fromkeys((*spec.identity_fields, "case_id")))
                dependency = (
                    " Provider workflow prerequisite: call this only after cases.create_from_order has returned "
                    "a real actor case ID and that case is bound to the selected patient. Before that binding, "
                    "do not call this tool or invent a case ID; complete the required pre-case work first. "
                    "Never use the internal case-subject namespace as case_id."
                )
                spec = ToolSpec(spec.name, spec.description + dependency, schema, spec.effect, identities)
            visible.append(spec)
        return visible

    def call(self, name: str, arguments: dict[str, Any]):
        actual = self.actual_names.get(name, name)
        if actual in self.discovery_only_names:
            return {"error": "discovery_tool_unavailable_after_case_binding",
                    "isError": True, "known_not_dispatched": True,
                    "instruction": "Use the already bound case scope; bootstrap discovery tools are unavailable to the case worker."}
        if name in self.restricted_aliases:
            return {"error": "actor_namespace_unavailable_for_domain",
                    "isError": True, "known_not_dispatched": True,
                    "instruction": "Use only tools in the selected domain's declared actor namespaces."}
        if self.case_namespace and _contains_case_id_value(arguments, self.case_namespace):
            return {"error": "internal_case_namespace_not_actor_case_id",
                    "isError": True, "known_not_dispatched": True,
                    "instruction": "Use only a real case ID returned by the trusted provider case-creation tool."}
        if actual in self.case_scoped_names:
            if self.actual_case_id is None:
                return {"error": "provider_case_not_bound", "isError": True,
                        "known_not_dispatched": True,
                        "instruction": "Read inbox messages only after the trusted provider case-creation result binds the active case."}
            if arguments.get("case_id") != self.actual_case_id:
                return {"error": "provider_case_scope_mismatch", "isError": True,
                        "known_not_dispatched": True,
                        "instruction": "Use the actual case ID bound to this provider workflow."}
        if (actual in self.patient_scoped_names
                and arguments.get("patient_id") != self.namespace):
            return {"error": "patient_scope_mismatch", "isError": True,
                    "known_not_dispatched": True,
                    "instruction": "Use only the patient ID selected from the public actor roster for this workflow."}
        if self.actual_case_id is not None and name in self.case_identity_aliases:
            return {"error": "provider_case_already_bound",
                    "isError": True, "known_not_dispatched": True,
                    "instruction": "This patient scope is already bound to its provider case; do not create another case."}
        if (self.require_actual_case_for_writes and name == "workspace.write_file"
                and self.actual_case_id is None):
            return {"error": "provider_case_workspace_not_bound",
                    "isError": True, "known_not_dispatched": True,
                    "instruction": "Create and verify the actual provider case before writing workspace files; keep preliminary notes and obligations in the case-local ledger."}
        if self.enabled and _contains_patient_id_value(arguments, self.namespace):
            raise StandaloneError("case-subject namespace cannot be sent as an actor patient_id")
        return self.tools.call(name, arguments)


def _contains_patient_id_value(value: Any, namespace: str, in_patient_field: bool = False) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            patient_field = in_patient_field or key.lower() in {"patient_id", "patientid", "patient"}
            if patient_field and item == namespace:
                return True
            if _contains_patient_id_value(item, namespace, patient_field):
                return True
    elif isinstance(value, list):
        return any(_contains_patient_id_value(item, namespace, in_patient_field) for item in value)
    elif in_patient_field and value == namespace:
        return True
    return False


def _contains_case_id_value(value: Any, namespace: str) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"case_id", "caseId"} and item == namespace:
                return True
            if key == "case" and isinstance(item, dict) and item.get("id") == namespace:
                return True
            if _contains_case_id_value(item, namespace):
                return True
    elif isinstance(value, list):
        return any(_contains_case_id_value(item, namespace) for item in value)
    return False


def _parse_semantic_identity_match_response(content: Any, task_instruction: str,
                                           context_json: str, *, require_clinical_evidence: bool = False) -> bool:
    if not isinstance(content, str):
        raise StandaloneError("patient matcher did not return text JSON")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    try:
        decoded = json.loads(content, object_pairs_hook=unique_object)
    except (TypeError, json.JSONDecodeError, ValueError):
        raise StandaloneError("patient matcher did not return a unique-key JSON comparison") from None
    if require_clinical_evidence:
        if (not isinstance(decoded, dict) or set(decoded) != {"matches", "evidence_pairs", "identity_conflicts", "clinical_discrepancies", "missing_support"}
                or not isinstance(decoded.get("matches"), bool)
                or not isinstance(decoded.get("evidence_pairs"), list)
                or any(not isinstance(decoded.get(key),list) or any(not isinstance(x,str) for x in decoded[key])
                       for key in ('identity_conflicts','clinical_discrepancies','missing_support'))):
            raise StandaloneError("patient matcher requires a structured clinical identity comparison")
        categories = set(); task_quotes = set(); chart_quotes = set()
        paragraphs = re.split(r"\n\s*\n", task_instruction.strip())
        narrative = paragraphs[1] if len(paragraphs) > 1 else task_instruction
        for pair_index,pair in enumerate(decoded["evidence_pairs"]):
            if not isinstance(pair, dict) or set(pair) != {"category", "task_quote", "context_quote"}:
                raise StandaloneError("patient matcher evidence pair has invalid fields")
            category, tq, cq = pair["category"], pair["task_quote"], pair["context_quote"]
            if (not isinstance(category,str) or category not in {"clinician", "presentation", "imaging", "treatment_history", "timeline", "requested_action"}
                    or not isinstance(tq, str) or not isinstance(cq, str)
                    or len(tq.strip()) < 8 or len(cq.strip()) < 8):
                raise StandaloneError("patient matcher evidence must quote the clinical narrative and candidate exactly")
            invalid_fields=[]
            if tq not in narrative:invalid_fields.append('task_quote')
            if cq not in context_json:invalid_fields.append('context_quote')
            if invalid_fields:
                fields=', '.join(f'evidence_pairs[{pair_index}].{field}' for field in invalid_fields)
                raise StandaloneError('patient matcher evidence must quote the clinical narrative and candidate exactly: '
                    +fields+' is not an exact source substring (case and punctuation sensitive). '
                    'Copy a passage from its own supplied source; do not capitalize, paraphrase or reconstruct it.')
            categories.add(category); task_quotes.add(tq); chart_quotes.add(cq)
        if decoded["matches"] and (decoded["identity_conflicts"] or len(categories) < 2
                or len(task_quotes) < 2 or len(chart_quotes) < 2
                or not categories.intersection({"clinician", "imaging", "treatment_history", "timeline"})):
            raise StandaloneError("patient match lacks distinct clinical evidence or reports contradictions")
        return decoded["matches"]
    if (not isinstance(decoded, dict) or set(decoded) != {"matches", "task_quote", "context_quote"}
            or not isinstance(decoded.get("matches"), bool)
            or not isinstance(decoded.get("task_quote"), str)
            or not isinstance(decoded.get("context_quote"), str)):
        raise StandaloneError("patient matcher returned an invalid comparison object")
    if decoded["matches"]:
        task_quote, context_quote = decoded["task_quote"], decoded["context_quote"]
        if (len(task_quote.strip()) < 8 or len(context_quote.strip()) < 8
                or task_quote not in task_instruction or context_quote not in context_json):
            raise StandaloneError("patient matcher returned quotes that do not exactly match its two sources")
    return decoded["matches"]


def _parse_semantic_patient_match_response(content: Any, task_instruction: str,
                                           chart_json: str) -> bool:
    """Compatibility wrapper for the original provider-chart matcher tests."""
    return _parse_semantic_identity_match_response(content, task_instruction, chart_json)


def _record_identity_comparison(run_dir: Path, number: int, task: str, context: str,
                                content: Any, *, matched: bool | None, error: str | None = None) -> None:
    """Keep the declared decision and quotes, never hidden model reasoning."""
    try:
        decision = json.loads(content) if isinstance(content,str) else None
    except ValueError:
        decision = None
    payload = {'comparison_number':number,'task_sha256':hashlib.sha256(task.encode()).hexdigest(),
               'candidate_context_sha256':hashlib.sha256(context.encode()).hexdigest(),
               'validation_passed':error is None,'matched':matched,'decision':decision,
               'validation_error':error}
    # Fresh attempts own their run directory. Refuse overwriting an earlier
    # receipt, and never feed other candidates' assessments into the worker.
    with (run_dir/f'identity-comparison-{number:03d}.private.json').open('x',encoding='utf-8') as handle:
        json.dump(payload,handle,ensure_ascii=False,indent=2)


def _workspace_read_roots(case_workspace_root: str, case_role_root: str,
                          profile: DomainSpec, case_bound: bool) -> tuple[str, ...]:
    reference_roots = ("/workspace/skills/managed-care-operations-handbook",
                       "/opt/healthverse-task-assets/tool_reference.md")
    if profile.name == "pa_um":
        return reference_roots + (
            f"{case_role_root}/incoming_request", f"{case_workspace_root}/shared/handoff",
            f"{case_workspace_root}/shared/intake")
    if not case_bound:
        return reference_roots
    return reference_roots + (case_role_root, f"{case_workspace_root}/shared")


def _rebind_provider_workspace(workspace: Any, profile: DomainSpec, scope: Scope,
                               binding: dict[str, Any], case_tools: _CaseSubjectNamespaceTools) -> None:
    if profile.name != "pa_provider" or binding.get("case_namespace") != scope.case:
        raise StandaloneError("case binding does not match this provider workspace scope")
    if (binding.get("patient_id") != scope.patient
            or binding.get("source_tool") not in case_tools.case_identity_aliases):
        raise StandaloneError("case binding source does not match the selected provider patient and creation tool")
    case_id_actual = binding.get("case_id")
    if not isinstance(case_id_actual, str) or not case_id_actual or case_id_actual.startswith("case-subject:"):
        raise StandaloneError("case binding did not supply a real provider case ID")
    workspace_base = PurePosixPath("/logs/artifacts/workspaces")
    actual_case_workspace = workspace_base / _path_component(case_id_actual)
    actual_role_root = actual_case_workspace / profile.workspace_role
    if not actual_role_root.is_relative_to(workspace_base) or actual_role_root == workspace_base:
        raise StandaloneError("actual provider workspace path escaped the case workspace root")
    workspace.root = actual_role_root
    workspace.case_root = actual_role_root / scope.key
    workspace.read_roots = tuple(PurePosixPath(path) for path in _workspace_read_roots(
        str(actual_case_workspace), str(actual_role_root), profile, case_bound=True))
    case_tools.bind_actual_case(binding)


def _write_private_setup_exception(run_dir: Path, stage: str, exc: Exception) -> bool:
    """Preserve setup failure details locally without exposing traceback locals."""
    receipt = {
        "schema_version": 1,
        "stage": stage,
        "exception_type": type(exc).__name__,
        "message": str(exc),
        "traceback": [
            {"filename": frame.filename, "line": frame.lineno, "function": frame.name}
            for frame in traceback.extract_tb(exc.__traceback__)
        ],
    }
    target = run_dir / ".setup-exception.private.json"
    try:
        with target.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
    except OSError:
        # Do not replace the original setup error or overwrite a prior receipt.
        return False
    return True


_SETUP_ERROR_CODES = {
    "provider patient name and chart cue did not identify the same roster entry":
        "patient_identity_conflict",
    "provider chart readback patient identity disagreed with the actor-visible roster":
        "patient_identity_conflict",
    "provider public patient roster is not complete within the bounded discovery limit":
        "incomplete_public_roster",
    "provider public patient search did not return a bounded, non-empty roster":
        "incomplete_public_roster",
    "Codex executable does not exist or is not a file": "native_executable_missing",
}


def _setup_error_code(exc: Exception) -> str:
    """Classify only exact stable errors; never echo dynamic/private exception text."""
    return _SETUP_ERROR_CODES.get(str(exc), "setup_error")


def run_case(container: str, task_dir: Path, run_dir: Path, executable: str,
             allowed_instruction_sources: dict[str, str], max_model_calls: int = 12,
             max_tool_calls: int = 50, max_context_chars: int = 0,
             timeout: float = 180, composition: str = 'combined', case_id: str | None = None,
             allow_case_subject_namespace: bool = False, domain: str | None = None,
             attempt_number: int = 1, max_identity_resets: int = 2,recovery_helper_policy: str = 'off',
             active_timeout: float | None = None, model_name: str = 'gpt-6-luna') -> dict[str, Any]:
    from .reselection import run_identity_episodes
    parameters=locals().copy();parameters.pop('max_identity_resets');parameters.pop('run_identity_episodes')
    return run_identity_episodes(_run_case_episode,parameters,max_identity_resets)


def _run_case_episode(container: str, task_dir: Path, run_dir: Path, executable: str,
             allowed_instruction_sources: dict[str, str], max_model_calls: int = 12,
             max_tool_calls: int = 50, max_context_chars: int = 0,
             timeout: float = 180, composition: str = "combined",
             case_id: str | None = None,
             allow_case_subject_namespace: bool = False,
             domain: str | None = None,
             attempt_number: int = 1, _excluded_patient_ids: tuple[str,...] = (),
             _excluded_case_ids: tuple[str,...] = (),recovery_helper_policy: str = 'off',
             active_timeout: float | None = None, model_name: str = 'gpt-6-luna') -> dict[str, Any]:
    """Run an unscored case in an already-started, root-owned container.

    This function never starts/stops containers. It reads only the case's public
    instruction.md and derives the patient/case scope from observed actor MCP
    queue and case responses. No task filename is used as a patient identifier.
    """
    if composition not in {"combined", "helpers", "team"}:
        raise ValueError("composition must be combined, helpers, or team")
    if recovery_helper_policy not in {'off','auto'}:raise ValueError('recovery_helper_policy must be off or auto')
    if isinstance(attempt_number, bool) or not isinstance(attempt_number, int) or attempt_number < 1:
        raise ValueError("attempt_number must be a positive integer")
    limits = Limits(max_model_calls=max_model_calls, max_tool_calls=max_tool_calls,
                    max_context_chars=max_context_chars, max_output_tokens=DEFAULT_LIMITS["max_output_tokens"])
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 1 <= timeout <= 1800:
        raise ValueError("timeout must be between 1 and 1800 seconds")
    validate_active_timeout(timeout, active_timeout)
    task_dir = Path(task_dir).resolve(strict=True)
    profile = domain_for_task(task_dir, override=domain)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,100}", task_dir.name):
        raise StandaloneError("task directory name is not a valid public χ-Bench task identifier")
    instruction_path = task_dir / "instruction.md"
    if not task_dir.is_dir() or not instruction_path.is_file() or instruction_path.is_symlink():
        raise StandaloneError("task directory must contain a regular public instruction.md")
    instruction_bytes = instruction_path.read_bytes()
    if len(instruction_bytes) > _MAX_INSTRUCTION_BYTES:
        raise StandaloneError("public instruction exceeds the configured size bound")
    try:
        public_instruction = instruction_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise StandaloneError("public instruction is not valid UTF-8") from None
    task_hash = hashlib.sha256(instruction_bytes).hexdigest()

    run_dir = Path(run_dir).resolve()
    package_root = Path(__file__).resolve().parents[1]
    runs_root = package_root / "runs"
    if not run_dir.is_relative_to(runs_root):
        raise StandaloneError("run_dir must be inside HealthHarnessCodex/runs/ (ignored local run data)")
    if any((run_dir / name).exists() for name in
           ("events.jsonl", "state.sqlite", "evaluation.json", "run.result.json", "result.private.json")):
        raise StandaloneError("run_dir already contains an attempt; use a fresh directory to preserve its evidence")
    run_dir.mkdir(parents=True, exist_ok=True)
    executor = DockerExecutor(container, timeout=min(40, float(timeout)))
    metadata = _run_metadata(task_dir.name, task_hash, allowed_instruction_sources, limits, timeout, composition, container, model_name=model_name)
    metadata['recovery_helper_policy']=recovery_helper_policy
    metadata['limits']['active_timeout_seconds']=active_timeout
    metadata["domain"] = profile.name
    metadata["engine_domain"] = profile.engine_domain
    metadata["attempt"] = attempt_number
    metadata["model_role"] = "workflow"
    recorder = RunRecorder(run_dir, metadata)
    recording_model: Any | None = None
    bootstrap_model_calls = 0
    identity_decisions: dict[str, Any] = {}
    run_started = time.monotonic()

    def semantic_patient_matcher(task_instruction: str, candidate_identity_context: Any) -> bool:
        nonlocal bootstrap_model_calls
        if bootstrap_model_calls >= limits.max_model_calls:
            raise StandaloneError("bootstrap identity matching exhausted the aggregate model-call budget")
        context_json = json.dumps(candidate_identity_context, ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":"))
        if limits.max_context_chars and len(context_json) > limits.max_context_chars:
            raise StandaloneError("one candidate identity context exceeded the bounded matching context")
        messages = [
            {"role": "system", "content": (
                "Compare the assigned public task with only the single candidate identity context supplied in this request. "
                "Decide only whether this context identifies the same case described in the task; do not make a clinical "
                "decision or propose an action. Return exactly one JSON object with keys matches (boolean), "
                "task_quote (string), and context_quote (string). For matches=true, quote an exact identifying phrase "
                "of at least eight characters from each source. For matches=false, the quote strings may be empty. "
                "Do not use outside knowledge or infer from task IDs or filenames."
            )},
            {"role": "user", "content": (
                "PUBLIC_TASK_TEXT\n" + task_instruction + "\n\nONE_CANDIDATE_IDENTITY_CONTEXT_JSON\n" + context_json
            )},
        ]
        clinical_identity = profile.name == "pa_provider"
        if clinical_identity:
            messages[0]["content"] = (
                "Identify whether this ONE candidate chart is the person in the public clinical intake. "
                "A matching diagnosis, surname, age, sex or repeated wording alone is NOT identity. "
                "Assess IDENTITY separately from clinical consistency. Compare multiple independent anchors: "
                "clinician, anatomy/laterality, distinctive imaging, chronology, and prior treatment/response. "
                "The task is an intake description, not a verbatim chart copy. Minor measurement variation, "
                "clinical discrepancies, missing details, and later workflow stages do not automatically mean "
                "a different patient. Record them without resolving or hiding them. Clear demographic or "
                "explicit patient-identity conflicts still prevent a match. A diagnosis alone is insufficient. "
                "Ignore task filenames/IDs and do not invent missing facts. Return exactly JSON keys matches "
                "(boolean), evidence_pairs (list), identity_conflicts, clinical_discrepancies, missing_support "
                "(each a list of strings). Explain nonmatching or uncertain decisions through these fields. "
                "Each evidence pair has exactly category, task_quote, context_quote. Category is clinician, presentation, "
                "imaging, treatment_history, timeline or requested_action. Quotes must be exact source substrings "
                "of at least 8 characters: task_quote from the clinical narrative paragraph, not its diagnosis "
                "heading; context_quote from this candidate JSON. A positive match requires at least TWO "
                "distinct identity anchors in different categories, including clinician, imaging, treatment_history "
                "or timeline, and no unresolved identity conflict. Clinical discrepancies must be retained for "
                "the case worker; do not reject solely because they exist. Do not relabel one fact as two categories. If only a generic "
                "diagnosis agrees or the story cannot be established, return matches=false. For nonmatches, "
                "evidence_pairs may be empty. No actions or clinical decisions."
            )
        if (recording_model is None
                or (limits.max_context_chars and sum(len(str(message.get("content", ""))) for message in messages) > limits.max_context_chars)):
            raise StandaloneError("identity-matching request exceeded the configured context limit")
        for correction_attempt in range(MAX_OUTPUT_LIMIT_CORRECTIONS+1):
            if bootstrap_model_calls >= limits.max_model_calls:
                raise StandaloneError("bootstrap identity matching exhausted the aggregate model-call budget")
            bootstrap_model_calls += 1
            recorder.metadata["bootstrap_model_calls"] = bootstrap_model_calls
            recorder.metadata["model_role"] = "identity_comparison"
            try:
                try:
                    reply = recording_model.complete(messages, [],
                                                     max_output_tokens=min(limits.max_output_tokens, 1024 if clinical_identity else 256))
                except ModelResponseFormatError as exc:
                    recorder.emit('bootstrap_format_correction',stage=exc.stage,comparison_number=bootstrap_model_calls)
                    if correction_attempt>=response_retry_limit(exc):raise
                    messages.append({'role':'user','content':format_correction(exc)})
                    continue
            finally:
                recorder.metadata["bootstrap_model_calls"] = bootstrap_model_calls
                recorder.metadata["bootstrap_model_role"] = "isolated_candidate_identity_comparison"
                recorder.metadata["model_role"] = "workflow"
            if getattr(reply, "tool_calls", ()):
                raise StandaloneError(
                    "patient matcher attempted a tool call; bootstrap matching requires a structured comparison only"
                )
            try:
                matched = _parse_semantic_identity_match_response(reply.content, task_instruction, context_json,
                                                                 require_clinical_evidence=clinical_identity)
                _record_identity_comparison(run_dir,bootstrap_model_calls,task_instruction,context_json,
                                             reply.content,matched=matched)
                identity_decisions[hashlib.sha256(context_json.encode()).hexdigest()] = json.loads(reply.content)
                recorder.emit('identity_comparison_result',comparison_number=bootstrap_model_calls,
                              matched=matched,validation_passed=True)
                return matched
            except StandaloneError as exc:
                _record_identity_comparison(run_dir,bootstrap_model_calls,task_instruction,context_json,
                                             reply.content,matched=None,error=str(exc))
                if correction_attempt:
                    raise
                # Retry only this candidate, before any clinical tool dispatch.
                # The feedback identifies the validation rule but provides no
                # answer, quote, or information from another candidate.
                messages.extend((
                    {"role": "assistant", "content": reply.content if isinstance(reply.content, str) else ""},
                    {"role": "user", "content": (
                        "The previous response failed exact source validation. Return one JSON object with exactly "
                        "the required keys. Any non-empty quote must be copied exactly from its own supplied source. "
                        "Re-evaluate only this candidate and do not invent or infer a quote. "
                        "Validation detail: " + str(exc)
                    )},
                ))

    def investigate_competing_patients(task_instruction,charts):
        from .identity_investigation import investigate_identity
        assessments=[identity_decisions[hashlib.sha256(json.dumps(c,ensure_ascii=False,sort_keys=True,
            separators=(',',':')).encode()).hexdigest()] for c in charts]
        remaining=max(0,limits.max_model_calls-bootstrap_model_calls-8)
        if not remaining:
            raise StandaloneError('identity investigation has no remaining budget after reserving workflow calls')
        recorder.emit('identity_investigation_started',candidate_count=len(charts))
        audit_path=run_dir/'identity-investigation.private.json'
        if audit_path.exists():raise StandaloneError('identity investigation receipt already exists')
        def save_audit(value):
            temporary=audit_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
            temporary.replace(audit_path)
        def complete_investigation(messages,tools):
            nonlocal bootstrap_model_calls
            if bootstrap_model_calls>=limits.max_model_calls-8:
                raise StandaloneError('identity investigation reached aggregate budget with workflow calls reserved')
            bootstrap_model_calls+=1
            recorder.metadata['bootstrap_model_calls']=bootstrap_model_calls
            recorder.metadata['model_role']='identity_investigation'
            try:
                return recording_model.complete(messages,tools,max_output_tokens=limits.max_output_tokens)
            finally:
                recorder.metadata['model_role']='workflow'
        choice=investigate_identity(task_instruction,charts,assessments,complete_investigation,
            max_calls=min(6,remaining),max_context_chars=limits.max_context_chars,audit=save_audit)
        recorder.emit('identity_investigation_finished',candidate_count=len(charts),resolved=choice is not None)
        # Never forward the cross-candidate discussion to a patient worker.
        # Its existing independent assessment alone remains eligible for handoff.
        return choice

    semantic_patient_matcher.resolve_ambiguity=investigate_competing_patients
    # Leave room for workflow execution instead of discovering at call 48 that
    # an unbounded roster consumed the entire actor budget.
    semantic_patient_matcher.max_candidate_calls = max(0, limits.max_model_calls - 8)
    setup_stage = "provider_initialization"
    recorder.emit("setup_stage_started", stage=setup_stage)
    try:
        model = CodexSessionModel(executable, model=model_name, reasoning_effort="high", timeout=timeout,
                                  active_timeout=active_timeout,
                                  allowed_instruction_sources=allowed_instruction_sources)
        recording_model = RecordingModel(model, recorder)
        setup_stage = "ownership_validation"
        recorder.emit("setup_stage_started", stage=setup_stage)
        executor.validate_owned_trial(task_dir.name)
        setup_stage = "actor_discovery"
        recorder.emit("setup_stage_started", stage=setup_stage)
        actor = DockerMCPClient(container, port=profile.port, timeout=min(30, float(timeout)), executor=executor)
        intake_context_reader = None
        if profile.name == "pa_um":
            from .intake_sources import IntakeSourceReader
            reader_holder: dict[str, Any] = {}

            def read_intake_context(selected_case_id: str, document_metadata: Any) -> dict[str, Any]:
                if "reader" not in reader_holder:
                    reader_holder["reader"] = IntakeSourceReader(executor)
                return reader_holder["reader"](selected_case_id, document_metadata)

            intake_context_reader = read_intake_context

        observed = discover_domain_case(
            actor, profile, public_instruction, case_id=case_id,
            allow_case_subject_namespace=allow_case_subject_namespace,
            legacy_um_discover=_discover_current_case if profile.name == "pa_um" else None,
            semantic_patient_matcher=(semantic_patient_matcher
                                      if profile.name in {"pa_provider", "pa_um"} else None),
            intake_context_reader=intake_context_reader,
            progress=recorder.emit,excluded_patient_ids=_excluded_patient_ids,excluded_case_ids=_excluded_case_ids)
        observed_ids = {key: value for key, value in observed.items() if key.endswith("_id")}
        if (observed_ids.get('patient_id') in _excluded_patient_ids
                or observed_ids.get('case_id') in _excluded_case_ids):
            raise StandaloneError('rediscovery selected a model-rejected identity; no worker started')
        if isinstance(observed.get("case_namespace_kind"), str):
            observed_ids["case_namespace_kind"] = observed["case_namespace_kind"]
        if bootstrap_model_calls >= limits.max_model_calls:
            raise StandaloneError("bootstrap patient matching left no model-call budget for the assigned workflow")
        execution_limits = Limits(
            max_model_calls=limits.max_model_calls - bootstrap_model_calls,
            max_tool_calls=limits.max_tool_calls,
            max_context_chars=limits.max_context_chars,
            max_output_tokens=limits.max_output_tokens)
        metadata["case_selection_method"] = observed.get("selection_method", "unknown")
        metadata["semantic_matcher_invocations"] = observed.get("semantic_matcher_invocations", 0)
        metadata["actor_tool_names"] = dict(actor._actual_names)
        metadata.update({"bootstrap_model_calls": bootstrap_model_calls,
                         "agent_model_calls_budget": execution_limits.max_model_calls})
        recorder.metadata.update(metadata)
    except Exception as exc:
        diagnostic_written = _write_private_setup_exception(run_dir, setup_stage, exc)
        error_code = _setup_error_code(exc)
        recorder.emit("setup_failed", stage=setup_stage, error_type=type(exc).__name__,
                      error_code=error_code)
        recorder.finish({"status": "setup_failure", "message": f"Setup failed: {type(exc).__name__}"}, 0,
                        environment_observations={"setup_error_type": type(exc).__name__,
                                                  "setup_error_code": error_code,
                                                  "setup_stage": setup_stage,
                                                  "private_diagnostic_written": diagnostic_written})
        raise
    actual_patient_id = observed_ids.get("patient_id")
    selection_method = observed.get("selection_method", "unknown")
    scope_patient = actual_patient_id or f"case-subject:{observed_ids['case_id']}"
    fallback_role = "payer" if profile.name == "pa_um" else profile.workspace_role
    scope = Scope(environment=f"docker:{container}", task=task_dir.name,
                  organization=observed_ids.get("organization_id", f"{fallback_role}-organization"),
                  principal=observed_ids.get("principal_id", f"{fallback_role}-actor"),
                  patient=scope_patient, case=observed_ids["case_id"])
    case_workspace_root = f"/logs/artifacts/workspaces/{_path_component(scope.case)}"
    case_role_root = f"{case_workspace_root}/{profile.workspace_role}"
    base_read_roots = _workspace_read_roots(
        case_workspace_root, case_role_root, profile,
        case_bound=profile.name != "pa_provider")
    workspace = DockerWorkspaceTools(
        container, case_role_root, scope,
        read_roots=base_read_roots,
        progress=recorder.emit,
        executor=executor,
    )
    actor_tools = PayerRoutingGuard(actor, actor._actual_names) if profile.name == "pa_um" else actor
    tools = ToolRegistry(actor_tools, workspace)
    full_instruction = _profile_instruction(profile, task_dir.name, observed_ids, scope, actual_patient_id,
                                             workspace.case_root, public_instruction)
    full_instruction += ('\n\nIf observed evidence makes this patient/case selection unjustified, you may call '
        'case.request_identity_reselection with your reason and current-scope citations. The controller can '
        'discard this working context and rediscover without carrying this patient information forward. '
        'Do not send tool calls for another patient inside this scope. Existing external or uncertain writes '
        'require reconciliation; a context reset cannot undo them or replenish budgets. Clinical uncertainty '
        'alone does not establish that the patient identity is wrong.')
    selected_identity_hash = observed.get('identity_comparison_context_sha256')
    if selected_identity_hash:
        assessment = identity_decisions.get(selected_identity_hash)
        if not isinstance(assessment,dict) or assessment.get('matches') is not True:
            raise StandaloneError('selected patient has no matching validated identity assessment')
        metadata['selected_identity_assessment'] = {'source_context_sha256':selected_identity_hash,'assessment':assessment}
        full_instruction += ('\n\nSelected-patient identity assessment (bootstrap analysis, not a new clinical fact or '
            'completion proof). Its quotes come from the assigned task and this patient chart. Read the chart '
            'through your tools before using clinical claims. Retain listed discrepancies and assess their relevance '
            'to each proposed action; they are not blanket prerequisites to resolve before all work. Investigate '
            'when the next action actually depends on the uncertain fact. Do not invent agreement or change patients.\n' +
            json.dumps(assessment,ensure_ascii=False,sort_keys=True))
    completion_contract = build_completion_contract(task_dir.name, profile.name, public_instruction,
                                                    scope=scope.to_dict())

    metadata.update({"scope": scope.to_dict(), "case_selection_method": selection_method,
        "completion_contract": completion_contract,
        "identity_scope": {
        "patient_namespace": scope.patient,
        "patient_namespace_kind": "observed_patient_id" if actual_patient_id else "case_subject_namespace",
        "case_namespace": scope.case,
        "case_namespace_kind": observed.get("case_namespace_kind", "actor_observed_case_id"),
        "actual_observed_patient_id": actual_patient_id,
        "case_id": observed_ids["case_id"],
    }, "identity_fingerprint": hashlib.sha256(
        json.dumps(observed_ids, sort_keys=True).encode()).hexdigest(),
        "initial_state_fingerprint": observed["case_payload_sha256"]})
    recorder.metadata.update(metadata)
    recorder.emit("environment_case_bound", identifiers=observed_ids,
                  selection_method=selection_method,
                  patient_namespace_kind="observed_patient_id" if actual_patient_id else "case_subject_namespace",
                  initial_state_fingerprint=observed["case_payload_sha256"])
    case_tools = _CaseSubjectNamespaceTools(
        tools, scope.patient, actual_patient_id is None, actor._actual_names,
        discovery_only_names=profile.discovery_only_tools,
        allowed_actor_namespaces=profile.namespaces or None,
        case_namespace=(scope.case if observed_ids.get("case_namespace_kind") == "patient_subject_namespace" else None),
        case_identity_names=profile.case_identity_tools,
        case_scoped_names=profile.case_scoped_tools,
        patient_scoped_names=profile.patient_scoped_tools,
        require_actual_case_for_writes=profile.name == "pa_provider")

    def bind_provider_workspace(binding: dict[str, Any]) -> None:
        _rebind_provider_workspace(workspace, profile, scope, binding, case_tools)

    recording_tools = RecordingTools(case_tools, recorder)
    store = CaseStore(run_dir / "state.sqlite")
    run_exception: Exception | None = None
    try:
        identity_sources = tuple(alias for alias, actual in actor._actual_names.items()
                                 if actual in profile.identity_source_tools)
        case_identity_sources = tuple(alias for alias, actual in actor._actual_names.items()
                                      if actual in profile.case_identity_tools)
        patient_identity_result_paths = {
            alias: ("structuredContent", "missing_information", "case")
            for alias, actual in actor._actual_names.items()
            if profile.name == "pa_um" and actual == "review.submit_md_case_decision"
        }
        principal_identity_result_paths = {
            alias: ("structuredContent", "triage")
            for alias, actual in actor._actual_names.items()
            if profile.name == "pa_um" and actual in {
                "review.get_md_review_data", "review.get_nurse_review_data"
            }
        }
        identity_sources = tuple(dict.fromkeys((*identity_sources, *patient_identity_result_paths)))
        harness = Harness(store, recording_model, recording_tools, limits=execution_limits, composition=composition,
                          recovery_helper_policy=recovery_helper_policy,
                          runtime_guard=getattr(executor,'assert_running',None),
                          require_policy_grounding=True, progress=recorder.emit,
                          patient_identity_tools=identity_sources,
                          case_identity_tools=case_identity_sources,
                          case_binding_callback=bind_provider_workspace if profile.name == "pa_provider" else None,
                          patient_identity_result_paths=patient_identity_result_paths,
                          principal_identity_result_paths=principal_identity_result_paths)
        recorder.emit("workflow_started", role="workflow")
        result = harness.run(scope, full_instruction, profile.engine_domain,
                             completion_contract=completion_contract)
    except Exception as exc:
        run_exception = exc
        # Exception reporting must not erase already-accounted calls or a case
        # binding. Read durable state without attempting an unfenced mutation.
        result={}
        try:
            saved=store.load_case(scope)
            for field in ('model_calls','tool_calls','usage','evidence','obligations',
                          'case_bindings','identity_bindings','principal_bindings'):
                if field in saved:result[field]=saved[field]
            result['persisted_status']=saved.get('status')
        except Exception as read_error:
            result['state_read_error_type']=type(read_error).__name__
        result.update(status='runtime_failure',error_type=type(exc).__name__,
                      message=f'Run failed with {type(exc).__name__}; see the private run record.')
    try:
        statuses: dict[str, int] = {}
        try:
            for action in store.actions(scope):
                key = str(action.get("status", "unknown"))
                statuses[key] = statuses.get(key, 0) + 1
        except Exception as exc:
            statuses = {"journal_read_error": 1}
            result["journal_read_error_type"] = type(exc).__name__
        result["journal_statuses"] = statuses
    finally:
        store.close()
    elapsed = time.monotonic() - run_started
    agent_model_calls = result.get("model_calls", 0) if isinstance(result.get("model_calls", 0), int) else 0
    result["bootstrap_model_calls"] = bootstrap_model_calls
    result["model_calls_total_observed"] = bootstrap_model_calls + agent_model_calls
    result["agent_model_calls_budget"] = execution_limits.max_model_calls

    readback_ids = dict(observed_ids)
    provider_case_binding = result.get("case_bindings") if isinstance(result, dict) else None
    if (profile.name == "pa_provider" and isinstance(provider_case_binding, dict)
            and isinstance(provider_case_binding.get("case_id"), str)):
        readback_ids["case_id"] = provider_case_binding["case_id"]
        readback_ids["case_namespace_kind"] = "actual_case_id"
    readback = ({"status": "skipped_after_run_exception", "reason_type": type(run_exception).__name__}
                if run_exception else readback_domain_case(actor, profile, readback_ids))
    if profile.name == "pa_um":
        terminal = _terminal_value(readback)
    else:
        terminal = None
    report = {
        "mode": "real-case-unscored", "task": task_dir.name, "domain": profile.name,
        "scope": scope.to_dict(),
        "local_harness": result, "official_score": "unknown; no judge invoked",
        "actual_workflow_readback": readback,
        "bootstrap_model_calls": bootstrap_model_calls,
        "model_calls_total_observed": bootstrap_model_calls + agent_model_calls,
        "model_call_budget_total": limits.max_model_calls,
        "model": model_name, "reasoning_effort": "high",
        "task_instruction_sha256": task_hash, "elapsed_seconds": elapsed,
        "container_identity": container,
    }
    if profile.name == "pa_um":
        report["actual_determination_readback"] = readback
    p2p_failures = [e.get("tool") for e in result.get("evidence", []) if isinstance(e, dict)
                    and e.get("outcome") == "failure" and "p2p" in str(e.get("tool", "")).lower()]
    if p2p_failures:
        report["environment_blockers"] = [{"type": "peer_to_peer_tool_failure",
                                           "tools": list(dict.fromkeys(p2p_failures)),
                                           "detail": "The actor P2P operation failed; no P2P outcome was simulated."}]
    env_observations = {"case_identity": observed_ids, "workflow_readback": readback}
    if profile.name == "pa_um":
        env_observations["determination_readback"] = readback
    if terminal is not None:
        env_observations["public_determination_terminal"] = terminal
    recorder.emit("workflow_readback", domain=profile.name, status=readback.get("status"), terminal=terminal)
    recorder.finish(result, elapsed, environment_observations=env_observations)
    _write_report(run_dir / "run.result.json", report)
    return report


def _standalone_instruction(task_id: str, observed_ids: dict[str, str], scope: Scope,
                            actual_patient_id: str | None, artifact_directory: str,
                            public_instruction: str) -> str:
    """Wrap the exact public task in isolated benchmark authority boundaries."""
    patient_identity_label = "observed patient ID" if actual_patient_id else "case-subject namespace; not a patient ID"
    prefix = (
        f"Public χ-Bench task: {task_id}\n"
        f"Actual identifiers observed in actor responses: "
        f"{json.dumps(observed_ids, ensure_ascii=False, sort_keys=True)}\n"
        f"Scope patient namespace: {scope.patient!r} ({patient_identity_label}).\n"
        "Never use a case-subject namespace as a patient_id argument to an actor tool. "
        "When the actual patient ID is unavailable, use case-bound tool arguments only.\n\n"
        "If a trusted case response later binds an actual patient ID, the current ledger records the "
        "observed_identity_binding; that ID may be used in patient_id arguments. The internal case "
        "namespace stays unchanged.\n\n"
        "Execution and simulated authority: this is an authorized, isolated simulation of the assigned "
        "χ-Bench payer workflow, not a real hospital or clinical deployment. Staff-role functions required "
        "by the public task may be performed by this same scoped actor using the exposed actor tools. The "
        "public task and actor tool contracts together define simulated action authority; an exposed tool "
        "alone does not authorize an action outside the assigned task. Treat staff and reviewer roles as "
        "workflow modes, not distinct real people. Do not invent real staff, licenses, credentials, "
        "independent humans, reviewer IDs, or claims that a real person performed a review. Use only IDs "
        "observed from the actor or defaults explicitly declared by a tool contract.\n\n"
        "Determine which conditional stages apply from the applicable observed policy and current case "
        "records. A list of downstream stages in the public task describes workflow scope; it does not by "
        "itself prove that every conditional stage is required for this case. The existence of a clinical "
        "policy or an exposed tool alone does not establish that a particular review branch applies. Before "
        "a routing or bypass choice, record a brief evidence-linked eligibility checkpoint: cite the relevant "
        "policy and case evidence, state the actual exception/exclusion trigger if observed, name remaining "
        "unknowns, and explain the branch basis. Resolve facts needed to choose a branch; never infer an "
        "exception or absence of exclusions from missing or uncertain evidence. Bypass a conditional stage "
        "only when the applicable policy or actor record supports that case-specific branch, and verify the "
        "resulting actor state. Never select a branch for convenience.\n\n"
        "A writable triage disposition is not an input to the default route_case operation. Its default derives "
        "the route from case policy, so route the active case using that policy-derived operation while the "
        "intake remains complete. An explicit route override is a bypass and requires case-specific policy and "
        "evidence support, not just a task list of stages. After actual route readback, read the triage record; only "
        "an explicit triage=null response establishes that no record exists. The first disposition is a one-time "
        "immutable commit and must follow the observed route. Build that first administrative record from the actual "
        "route result and current case SLA and gold-card observations, using only values returned by those tools. "
        "Calculate SLA from the observed intake level_of_urgency, and recompute it from a newly observed urgency "
        "if the case urgency changes; "
        "do not commit a provisional lane guess. If a record already exists, do not attempt to amend it. If the "
        "existing record conflicts with the route, preserve the evidence and leave dependent letter work unresolved. "
        "Do not repeat a successfully completed route or alter a valid completed clinical action to force agreement. "
        "Unknown disposition-to-route mappings remain unknown; do not force a classification. A gold-card assessment "
        "establishes only its declared scope and does not imply that every service exception was checked.\n\n"
        "Treat each assessment according to its tool-declared scope: it establishes only the fields it says it "
        "checked. Do not narrow it to one factor or expand it into certification of unmentioned flags. Before "
        "a branch choice, check the policy-required inputs, observed eligibility, any explicit exception trigger, "
        "remaining unknowns, and the evidence basis for the choice. Resolve required facts and explicit "
        "contradictions. Distinguish observed contrary evidence from hypothetical or unmentioned exceptions. "
        "Uncertainty alone does not prove an exception; missing fields do not prove that no exception exists, "
        "but do not create mandatory negative-certification steps for possibilities the policy and tool contract "
        "do not require.\n\n"
        f"Your owned writable artifact directory is {artifact_directory}. Use paths relative to that directory.\n\n"
        "Complete the entire assigned task at its stated stage, including any required clinical review, "
        "MD review, peer-to-peer when available, final determination, notices, and status readback. "
        "Do not stop at initial intake or triage. Use only the available actor tools and approved references. "
        "A terminal status alone does not prove every assigned requirement was met: reconcile each "
        "required review, decision and communication against observed records, including any actor-"
        "documented exemption or automatic disposition. Never invent a review or waive a requirement "
        "merely to close an obligation. Preserve substantive clinical, policy, and stage prerequisites. "
        "Do not invent facts or claim effects without tool readback.\n\n"
        "--- Public task instruction ---\n" + public_instruction
    )
    return prefix


def _profile_instruction(profile: DomainSpec, task_id: str, observed_ids: dict[str, str], scope: Scope,
                         actual_patient_id: str | None, artifact_directory: str,
                         public_instruction: str) -> str:
    if profile.name == "pa_um":
        return _standalone_instruction(task_id, observed_ids, scope, actual_patient_id,
                                       artifact_directory, public_instruction)
    identity_label = "observed patient ID" if actual_patient_id else "case-subject namespace; not a patient ID"
    provider_binding_guidance = ""
    if profile.name == "pa_provider":
        provider_binding_guidance = (
            "The assigned provider workflow begins with an observed patient and an internal case-subject namespace; "
            "no actor case exists yet. Never send that internal namespace as case_id. Use the patient-bound public "
            "chart and the assigned task to determine the requested clinical choices, then create the actual case "
            "only through the declared cases.create_from_order tool. That tool can mint a NEW ServiceRequest; source_order_id is optional. "
            "Do not require an existing order when the authorized clinical intake supplies the new request. "
            "Select required clinical/coding fields using the intake, chart and approved role references, and "
            "read the procedure's governing policy before choosing them. Site of service is the place of service "
            "where the procedure is performed: inpatient_hospital means the patient is admitted for a stay; "
            "outpatient_hospital means hospital care without admission; ambulatory_surgical_center means a "
            "same-day surgical centre. Decide it from coding and policy rules, not the facility name: whether the "
            "procedure code is designated inpatient-only (as on the CMS Inpatient Only list), and whether a payer "
            "site-of-service policy lists the procedure as eligible for outpatient or ASC care; such a policy "
            "that does not list the procedure does not support an outpatient setting. An undocumented admission "
            "is unknown, not evidence of outpatient care. Record the rule you applied in field_basis, and "
            "look up the actual ordering provider. Do not invent missing patient facts or pretend a historical "
            "order existed. Trust the resulting case ID only after its result "
            "binds that case to this patient. Before that binding, keep preliminary notes and obligations in the "
            "case-local ledger and do not write workspace files. After binding, use only that actual case ID for "
            "case-scoped messages and workspace work.\n\n"
            "After creating the case, read cases.get_case to inspect its actual requirements before recording "
            "a provider disposition or submitting. Resolve what can be established from the existing chart, "
            "forms and approved references before treating a missing field as an external information blocker. "
            "Use gather_more_evidence for genuinely unresolved requirements, not as a substitute for preparing "
            "the record. Re-read current case state after changes.\n\n"
            "For a referral workflow, a submit_pa disposition and ready_to_submit status are intermediate: "
            "after preparing the supported bundle, checking the current case requirements and resolving "
            "required fields, continue with the declared authorization-submission tool and verify the "
            "resulting packet and case readback. Stop at readiness only if the public task explicitly "
            "assigns preparation alone. This does not authorize submitting an inappropriate request or "
            "bypassing a genuine missing-evidence or no-authorization decision.\n\n"
        )
    prefix = (
        f"Public χ-Bench task: {task_id}\n"
        f"Selected domain: {profile.name} ({profile.engine_domain}).\n"
        f"Actual identifiers observed in actor responses: {json.dumps(observed_ids, ensure_ascii=False, sort_keys=True)}\n"
        f"Scope patient namespace: {scope.patient!r} ({identity_label}).\n"
        "Never use a case-subject namespace as a patient_id argument to an actor tool. Keep all actor and workspace "
        "operations within the bound case.\n\n"
        "This is an authorized, isolated simulation of the assigned χ-Bench workflow, not a real healthcare deployment. "
        "Staff functions required by the public task may be performed by this same scoped actor; do not invent real "
        "people, credentials, reviews, approvals, clinical facts, or workflow steps. Use only actor tools in the "
        f"selected domain namespaces ({', '.join(profile.namespaces)}) and approved public references. Follow the "
        "public task, observed case records, applicable policy, and declared tool contracts to decide what is required. "
        "Use only IDs returned by trusted actor reads or defaults expressly declared by a tool contract; never derive "
        "patient or case IDs from task names or file paths. "
        "Preserve uncertainty and resolve explicit contradictions from their sources; do not add certifications or "
        "exceptions that the task, policy, or tool contracts do not require. Verify effects with the domain's available "
        "actor readbacks and never claim an action without observed confirmation.\n\n"
    )
    return prefix + provider_binding_guidance + (
        f"Your owned writable artifact directory is {artifact_directory}. Use paths relative to that directory.\n\n"
        "Complete the assigned task at its stated stage, including its required communications and status readback. "
        "Keep patient-specific information within this case's scope.\n\n"
        "--- Public task instruction ---\n" + public_instruction
    )


def _discover_current_case(client: DockerMCPClient, case_id: str | None = None,
                          allow_case_subject_namespace: bool = False,
                          task_instruction: str | None = None) -> dict[str, str]:
    specs = client.list_tools()
    names = client._actual_names
    queue_alias = _find_alias(names, "list_intake_queue")
    case_alias = _find_alias(names, "get_intake_case")
    if not queue_alias or not case_alias:
        raise StandaloneError("payer actor lacks required list_intake_queue/get_intake_case identity tools")
    queue_spec = next(spec for spec in specs if spec.name == queue_alias)
    queue_result = client.call(queue_alias, _required_arguments(queue_spec, {}))
    records = _records(queue_result)
    candidates = [record for record in records if _find_identifier(record, "case") or _find_identifier(record, "intake")]
    candidates = _unique_candidates(candidates)
    selection_method = "single_actor_queue_case"
    if case_id is not None:
        if not isinstance(case_id, str) or not case_id:
            raise StandaloneError("explicit case_id must be a non-empty actor-observed identifier")
        candidates = [record for record in candidates if _find_identifier(record, "case") == case_id]
        selection_method = "explicit_case_id"
    elif len(candidates) > 1:
        if not isinstance(task_instruction, str) or not task_instruction.strip():
            raise StandaloneError("actor-visible queue has multiple cases; public task provider/procedure matching is required")
        candidates = _select_cases_by_public_instruction(candidates, task_instruction)
        selection_method = "public_instruction_provider_procedure"
    if len(candidates) != 1:
        qualifier = "explicit case_id was not present exactly once in" if case_id else "payer intake queue did not identify exactly one case in"
        raise StandaloneError(f"{qualifier} actor-visible queue ({len(candidates)} candidates after selection)")
    candidate = candidates[0]
    case_spec = next(spec for spec in specs if spec.name == case_alias)
    case_args = _arguments_from_observation(case_spec, candidate, default_kind="intake")
    case_result = client.call(case_alias, case_args)
    observed = _first_record(case_result)
    for kind in ("patient", "case", "intake"):
        before, after = _find_identifier(candidate, kind), _find_identifier(observed, kind)
        if before and after and before != after:
            raise StandaloneError(f"actor case readback disagreed with queue {kind} identity")
    combined = {**candidate, **observed}
    patient_id = _find_identifier(combined, "patient")
    case_id = _find_identifier(combined, "case")
    intake_id = _find_identifier(combined, "intake")
    if not case_id:
        raise StandaloneError("actor-visible intake case did not provide a case identifier")
    review_payload_hash = None
    if not patient_id:
        patient_id, review_payload_hash = _discover_patient_identity(client, specs, names, case_id, intake_id)
    if not patient_id and not allow_case_subject_namespace:
        raise StandaloneError("actor review data did not provide a patient identity for the selected case")
    out = {"case_id": case_id}
    if patient_id:
        out["patient_id"] = patient_id
    if intake_id:
        out["intake_id"] = intake_id
    for kind in ("organization", "principal"):
        value = _find_identifier(combined, kind)
        if value:
            out[f"{kind}_id"] = value
    payload_fingerprints = {"queue_record": _fingerprint(candidate), "intake_case": _fingerprint(case_result)}
    if review_payload_hash:
        payload_fingerprints["review_identity"] = review_payload_hash
    out["case_payload_sha256"] = _fingerprint(payload_fingerprints)
    out["selection_method"] = selection_method
    return out


def _select_cases_by_public_instruction(candidates: list[dict[str, Any]], instruction: str) -> list[dict[str, Any]]:
    instruction_tokens = _normalized_word_tokens(instruction)
    matches = []
    for candidate in candidates:
        provider_name = _requesting_provider_name(candidate)
        provider_tokens = _normalized_word_tokens(provider_name) if provider_name else []
        if len(provider_tokens) < 2 or not _contains_token_phrase(instruction_tokens, provider_tokens):
            continue
        procedure_tokens = [_normalized_word_tokens(name) for name in _procedure_names(candidate)]
        if any(_procedure_matches_instruction(tokens, instruction_tokens) for tokens in procedure_tokens):
            matches.append(candidate)
    return matches


def _requesting_provider_name(record: dict[str, Any]) -> str | None:
    provider = record.get("requesting_provider")
    if isinstance(provider, dict):
        name = provider.get("provider_name")
        return name if isinstance(name, str) and name.strip() else None
    if isinstance(provider, str) and provider.strip():
        return provider
    return None


def _procedure_names(record: dict[str, Any]) -> list[str]:
    items = record.get("line_items")
    if not isinstance(items, list):
        return []
    names = []
    for line_item in items:
        if not isinstance(line_item, dict):
            continue
        procedures = line_item.get("procedures")
        if not isinstance(procedures, list):
            continue
        for procedure in procedures:
            if isinstance(procedure, dict):
                name = procedure.get("name")
                if isinstance(name, str) and name.strip():
                    names.append(name)
    return names


def _normalized_word_tokens(value: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)


def _contains_token_phrase(haystack: list[str], phrase: list[str]) -> bool:
    if not phrase or len(phrase) > len(haystack):
        return False
    width = len(phrase)
    return any(haystack[index:index + width] == phrase for index in range(len(haystack) - width + 1))


def _procedure_matches_instruction(procedure_tokens: list[str], instruction_tokens: list[str]) -> bool:
    if len(procedure_tokens) < 3:
        return False
    if _contains_token_phrase(instruction_tokens, procedure_tokens):
        return True
    leading_phrase = procedure_tokens[:6]
    return len(leading_phrase) >= 3 and _contains_token_phrase(instruction_tokens, leading_phrase)


def _discover_patient_identity(client: DockerMCPClient, specs: list[Any], names: dict[str, str],
                               case_id: str, intake_id: str | None) -> tuple[str | None, str | None]:
    candidates = []
    for alias, actual in names.items():
        if "review" in actual and (actual.endswith("get_nurse_review_data") or actual.endswith("get_md_review_data")):
            candidates.append((0 if actual.endswith("get_nurse_review_data") else 1, alias))
    identity = {"case_id": case_id}
    if intake_id:
        identity["intake_id"] = intake_id
    for _, alias in sorted(candidates):
        spec = next((item for item in specs if item.name == alias), None)
        if spec is None:
            continue
        try:
            args = _arguments_from_observation(spec, identity, default_kind="case")
            observed = _first_record(client.call(alias, args))
        except StandaloneError:
            raise
        except Exception:
            continue
        review_case = _find_identifier(observed, "case")
        if review_case and review_case != case_id:
            raise StandaloneError("actor review payload identity disagreed with the selected case")
        review_intake = _find_identifier(observed, "intake")
        if intake_id and review_intake and review_intake != intake_id:
            raise StandaloneError("actor review payload identity disagreed with the selected intake")
        patient = _find_identifier(observed, "patient")
        if patient:
            if review_case != case_id:
                raise StandaloneError("actor review payload patient identity was not bound to the selected case")
            return patient, _fingerprint(observed)
    return None, None


def _fingerprint(value: Any) -> str:
    packed = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(packed.encode("utf-8")).hexdigest()


def _read_determination_summary(client: DockerMCPClient, ids: dict[str, str]) -> dict[str, Any]:
    alias = _find_alias(client._actual_names, "get_summary")
    if not alias or "determination" not in client._actual_names[alias]:
        return {"status": "unavailable", "reason": "determination.get_summary is not exposed by this actor"}
    spec = next((s for s in (client._specs or []) if s.name == alias), None)
    if spec is None:
        return {"status": "unavailable", "reason": "determination summary schema is unavailable"}
    args = _arguments_from_observation(spec, ids, allow_defaults=True, default_kind="case")
    try:
        return {"status": "observed", "tool": client._actual_names[alias], "result": client.call(alias, args)}
    except Exception as exc:
        return {"status": "error", "tool": client._actual_names[alias], "error_type": type(exc).__name__}


def _terminal_value(readback: dict[str, Any]) -> bool | None:
    result = readback.get("result")
    if not isinstance(result, dict):
        return None
    current = result.get("structuredContent", result)
    if not isinstance(current, dict):
        return None
    for key in ("terminal", "is_terminal", "isTerminal", "finalized", "is_final"):
        if isinstance(current.get(key), bool):
            return current[key]
    # This is a report of the current actor's explicit workflow fields, not a grade.
    workflow = current.get("workflow_state")
    if (isinstance(workflow, dict) and workflow.get("workflow_stage") == "determination"
            and workflow.get("stage_detail") == "finalized" and workflow.get("action_owner") == "none"):
        return True
    return None


def _run_metadata(task_id: str, task_hash: str, allowed_sources: dict[str, str], limits: Limits,
                  timeout: float, composition: str, container: str, *, model_name: str = 'gpt-6-luna') -> dict[str, Any]:
    from .hybrid_search import runtime_config
    return {
        'retrieval_runtime':runtime_config(),
        "mode": "real-case-unscored", "task": task_id, "task_id": task_id,
        "task_instruction_sha256": task_hash, "container_identity": container,
        "model": model_name, "reasoning_effort": "high", "effort": "high",
        "limits": {"max_model_calls": limits.max_model_calls, "max_tool_calls": limits.max_tool_calls,
                   "max_context_chars": limits.max_context_chars, "max_output_tokens": limits.max_output_tokens,
                   "timeout_seconds": float(timeout)},
        "budgets": {"model_calls": limits.max_model_calls, "tool_calls": limits.max_tool_calls,
                    "context_chars": limits.max_context_chars},
        "source_commit": _source_commit(), "source_fingerprint": _source_fingerprint(),
        "allowed_instruction_source_sha256": dict(allowed_sources), "composition": composition,
        "started_unix": time.time(),
    }


def _find_alias(mapping: dict[str, str], suffix: str) -> str | None:
    matches = [alias for alias, actual in mapping.items()
               if actual == suffix or actual.endswith("." + suffix) or actual.endswith("_" + suffix)]
    return matches[0] if len(matches) == 1 else None


def _records(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if _find_identifier(node, "case") or _find_identifier(node, "intake"):
                found.append(node)
            for item in node.values():
                visit(item)
        elif isinstance(node, list):
            for item in node:
                visit(item)
    visit(value)
    return _unique_candidates(found)


def _unique_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    seen: set[tuple[str | None, str | None, str | None]] = set()
    for item in items:
        key = (_find_identifier(item, "patient"), _find_identifier(item, "case"), _find_identifier(item, "intake"))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _first_record(value: Any) -> dict[str, Any]:
    records = _records(value)
    if records:
        return records[0]
    if isinstance(value, dict):
        structured = value.get("structuredContent")
        return structured if isinstance(structured, dict) else value
    return {}


def _find_identifier(record: dict[str, Any], kind: str) -> str | None:
    names = {
        "patient": ("patient_id", "patientId", "patient"),
        "case": ("case_id", "caseId", "case"),
        "intake": ("intake_id", "intakeId", "referral_id", "referralId"),
        "organization": ("organization_id", "organizationId", "payer_id", "payerId"),
        "principal": ("principal_id", "principalId", "actor_id", "actorId", "reviewer_id", "reviewerId"),
    }[kind]
    for name in names:
        value = record.get(name)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, dict):
            ident = value.get("id")
            if isinstance(ident, str) and ident:
                return ident
    return None


def _arguments_from_observation(spec: Any, observed: dict[str, str], allow_defaults: bool = False,
                                default_kind: str | None = None) -> dict[str, Any]:
    schema = spec.input_schema
    properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
    required = schema.get("required", []) if isinstance(schema, dict) else []
    result: dict[str, Any] = {}
    source_keys = {
        "patient": ("patient_id", "patientId"), "case": ("case_id", "caseId"),
        "intake": ("intake_id", "intakeId", "referral_id", "referralId"),
        "organization": ("organization_id", "organizationId", "payer_id", "payerId"),
        "principal": ("principal_id", "principalId", "actor_id", "actorId", "reviewer_id", "reviewerId"),
    }
    for name in required:
        if name in properties:
            normalized = name.replace("Id", "_id").lower()
            value = None
            for kind, keys in source_keys.items():
                if name in keys or normalized in keys or kind in normalized:
                    value = _find_identifier(observed, kind)
                    if value:
                        break
            if value:
                result[name] = value
            elif not allow_defaults:
                if name.lower() in {"id", "resource_id"} and default_kind:
                    value = _find_identifier(observed, default_kind)
                    if value:
                        result[name] = value
                        continue
                raise StandaloneError(f"identity argument {name!r} was not present in actor observations")
            elif properties[name].get("type") == "string":
                case_id = _find_identifier(observed, "case")
                if case_id:
                    result[name] = case_id
    return result


def _required_arguments(spec: Any, observed: dict[str, str]) -> dict[str, Any]:
    required = spec.input_schema.get("required", [])
    if required:
        raise StandaloneError("intake queue tool requires filters; refusing to guess an identity selection")
    return {}


def _path_component(value: str) -> str:
    return value if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value) else "case-" + hashlib.sha256(value.encode()).hexdigest()[:16]


def _write_report(path: Path, value: dict[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    temp.replace(path)


def _source_fingerprint() -> str:
    root = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    files = sorted(root.rglob("*.py")) + sorted((root / 'data').glob('*.json'))
    for path in files:
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(root).as_posix().encode("utf-8")
            digest.update(len(relative).to_bytes(4, "big"))
            digest.update(relative)
            data = path.read_bytes()
            digest.update(len(data).to_bytes(8, "big"))
            digest.update(data)
    return digest.hexdigest()


def _source_commit() -> str | None:
    repo = Path(__file__).resolve().parents[2]
    try:
        result = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                                text=True, timeout=3, check=False,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and re.fullmatch(r"[0-9a-fA-F]{40,64}", value) else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="health-harness-codex-real-case")
    parser.add_argument("--container", required=True, help="already-running root-owned chi-bench runtime container")
    parser.add_argument("--task-dir", type=Path, required=True, help="one public PA, UM, or CM task directory")
    parser.add_argument("--domain", choices=tuple(DOMAIN_PROFILES),
                        help="explicit domain override for synthetic or legacy task paths")
    parser.add_argument("--case-id", help="explicit case ID observed in the live actor queue")
    parser.add_argument("--allow-case-subject-namespace", action="store_true",
                        help="allow isolated case scope when actor responses expose no patient ID")
    parser.add_argument("--run-dir", type=Path, required=True, help="ignored local directory for run state and trace")
    parser.add_argument("--codex-executable", required=True, help="absolute path to the native Codex executable")
    parser.add_argument('--model',default='gpt-6-luna',help='case-worker Codex model')
    parser.add_argument("--codex-instruction-source", type=Path, action="append", default=[])
    parser.add_argument("--max-model-calls", type=int, default=12)
    parser.add_argument("--max-tool-calls", type=int, default=50)
    parser.add_argument("--max-context-chars", type=int, default=0, help="Working-context character cap; 0 disables the harness cap.")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument('--active-timeout', type=float, help='total model request cap while generation is active; --timeout remains the silence/setup cap')
    parser.add_argument("--composition", choices=("combined", "helpers", "team"), default="combined")
    parser.add_argument('--recovery-helper-policy',choices=('off','auto'),default='auto')
    args = parser.parse_args(argv)
    if not Path(args.codex_executable).is_absolute():
        parser.error("--codex-executable must be an absolute path")
    try:
        approved = {}
        for source in args.codex_instruction_source:
            canonical = source.resolve(strict=True)
            if not canonical.is_file():
                raise StandaloneError("instruction source must be a regular file")
            approved[str(canonical)] = hashlib.sha256(canonical.read_bytes()).hexdigest()
        result = run_case(args.container, args.task_dir, args.run_dir, args.codex_executable, approved,
                          max_model_calls=args.max_model_calls, max_tool_calls=args.max_tool_calls,
                          max_context_chars=args.max_context_chars, timeout=args.timeout, composition=args.composition,
                          active_timeout=args.active_timeout,
                          model_name=args.model,
                          recovery_helper_policy=args.recovery_helper_policy,
                          case_id=args.case_id,
                          allow_case_subject_namespace=args.allow_case_subject_namespace,
                          domain=args.domain)
        print(json.dumps({
            "status": result["local_harness"].get("status", "unknown"),
            "model_calls": result["local_harness"].get("model_calls"),
            "tool_calls": result["local_harness"].get("tool_calls"),
            "result_path": str(args.run_dir / "run.result.json"),
            "trace_path": str(args.run_dir / "run.live.md"),
        }, ensure_ascii=False))
        return 0 if result["local_harness"].get("status") == "complete" else 2
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__,
                          "run_dir": str(args.run_dir)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
