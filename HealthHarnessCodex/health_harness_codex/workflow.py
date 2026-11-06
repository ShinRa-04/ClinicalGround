"""Case-local planning and bounded recovery from unsupported early stops.

This module describes execution capabilities, not clinical truth. A reported
blocker is not a verified diagnosis, and recovery never changes case identity.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from .models import ToolSpec
from .working_set import business, canonical, packed

MAX_STOP_RECOVERIES = 4


def execution_capabilities(specs: Iterable[ToolSpec]) -> dict[str, Any]:
    creation = []
    for spec in specs:
        # Match the actual tool or its deterministic MCP alias, not model prose.
        if spec.name != "cases.create_from_order" and not spec.name.startswith("mcp_cases_create_from_order_"):
            continue
        schema = spec.input_schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if isinstance(properties, dict) and "source_order_id" in properties and "source_order_id" not in required:
            creation.append({"tool": spec.name, "existing_order_required": False,
                             "required_fields": list(required)})
    return {"new_request_creation": creation}


def evidence_fingerprint(state: dict[str, Any]) -> str:
    # Local notes and merely opening/closing obligations are not new source data.
    scope = state.get('scope')
    sources = [{"outcome": item.get("outcome"),
                "tool": item.get("tool"), "result": item.get("observed_result")}
               for item in state.get("evidence", []) if isinstance(item, dict)
               and (scope is None or item.get('scope') == scope)]
    # Retrieving an unread field is awareness progress, not new clinical truth.
    known = {e.get('id') for e in state.get('evidence',[]) if e.get('outcome') == 'success'
             and (scope is None or e.get('scope') == scope)}
    for message in state.get('messages',[]):
        if message.get('role') != 'tool' or message.get('name') not in {'case.inspect_evidence','case.get_tool_contract','case.audit_assignment'}: continue
        try: value = json.loads(message.get('content',''))
        except (ValueError,TypeError): continue
        if isinstance(value,dict) and 'error' not in value:
            if message.get('name') in {'case.get_tool_contract','case.audit_assignment'}:
                sources.append({'observed_procedural_contract':value})
            elif value.get('id') in known:sources.append({'inspected_source':value})
    audit=state.get('recovery_audit')
    if audit and audit.get('status')=='completed':
        sources.append({'procedural_recovery_review':{'status':'completed','helper_id':audit.get('helper_id')}})
    distinct = sorted({json.dumps(item, sort_keys=True, ensure_ascii=False, default=str) for item in sources})
    return hashlib.sha256(json.dumps(distinct).encode()).hexdigest()


def recovery_diagnostics(state: dict[str, Any]) -> dict[str, Any]:
    """Build actionable, attributed next checks; never fabricate an answer."""
    sources = [e for e in state.get('evidence',[]) if e.get('scope') == state.get('scope')]
    latest = {}; references = []; failed = []
    for e in sources:
        name = canonical(e.get('tool',''))
        if e.get('outcome') != 'success':
            failed.append({'id':e['id'],'tool':name,'outcome':e.get('outcome')})
            continue
        value = business(e.get('observed_result'))
        latest[name] = (e['id'],value)
        if name in {'workspace.read_file','workspace.read_pdf'} and isinstance(value,dict):
            references.append({'id':e['id'],'tool':name,'text_was_returned':bool(value.get('text') or value.get('pages')),
                'has_more':value.get('has_more'),'read_action':{'tool':'case.inspect_evidence','arguments':{
                    'id':e['id'],'path':'/text' if 'text' in value else '/pages','offset':0,'limit':4000 if 'text' in value else 1}}})
    gaps = []
    def collect(node,path,source):
        if isinstance(node,dict):
            for key,value in node.items():
                child=path+'/'+key.replace('~','~0').replace('/','~1')
                if key in {'missing_required_fields','missing_fields','missing_information'} and value:
                    gaps.append({'id':source,'path':child,'reported_gap':value})
                elif isinstance(value,(dict,list)): collect(value,child,source)
        elif isinstance(node,list):
            for i,item in enumerate(node): collect(item,path+'/'+str(i),source)
    for name in ('cases.get_case','forms.list_required_forms','forms.validate_form','determination.get_summary','cm_chart.get_chart_data'):
        if name in latest:
            source,value=latest[name];collect(value,'',source)
    return {'reference_retrieval':references[-4:],'observed_gaps':gaps[:12],
            'failed_operations':failed[-4:],
            'identity_rule':'An uncertain identity is not repairable by switching patients inside this bound case. Stop before new writes and report rebootstrap required if public evidence contradicts it.',
            'next_step_rule':'Resolve each reported gap against its source and schema. Retrieve returned reference text before reporting documentation unavailable. Interpret field applicability using its real form contract; never invent an access reason or clinical fact. Choose and execute a specific permitted next check, not a repeated generic blocker.'}


def recovery_prompt(state: dict[str, Any]) -> str:
    from .closure import STOP_RECORD_GUIDANCE
    gate=state.get('completion_gate') or {}
    if gate.get('accepted') is True:
        return ('Recorded effects satisfy a supported structural endpoint. Your final assessment still needs '
            'to establish whether any useful permitted action remains. This is a scope/actionability question, '
            'not an instruction to approve treatment or finalize a pending case. Do not repeat completed writes. '
            'Identify and perform a remaining investigation, cite evidence that the structural mapping misses '
            'a responsibility, or give a source-backed stop_assessment explaining why current work must wait. '
            + STOP_RECORD_GUIDANCE)
    capabilities = state.get("workflow_capabilities", {})
    creation = capabilities.get("new_request_creation", [])
    guidance = (
        "The recorded effects do not yet establish a supported endpoint. Reconcile the remaining responsibilities and your blocker before ending the attempt. "
        "Own the replanning decision. Distinguish a failed tool call, a successful empty result, an assumed "
        "prerequisite and genuinely missing information. For the blocked action, identify its exact required "
        "field/authority and source basis; assess whether the discrepancy affects that action or a later decision. "
        "Consult the relevant tool contract and role guidance when that question remains unanswered; repeated reads "
        "alone are not progress. Use case-local evidence and perform only permitted actions. Revise the remaining "
        "obligations and their dependencies. Do not repeat completed writes, invent patient facts, change "
        "patient/case identity, or bypass an unknown write. "
    )
    if (state.get('completion_contract') or {}).get('domain')=='pa_provider':
        guidance += (
        "A ready_to_submit case is an intermediate state unless the public task explicitly assigns "
        "preparation only. If the supported provider decision is to submit, finish the declared "
        "authorization submission and verify the packet/readback instead of ending at readiness. "
        "If the provider stage has a verified gather-more-evidence disposition, forms are completed, and "
        "only an external document remains unavailable, case.defer_obligation can record that verified "
        "handoff without falsely closing the outstanding work. Cite the fresh case readback and state "
        "the next action. Local deferral does not notify anyone and must never be described as delivery. "
        )
    else:
        from .assignment import stage_guidance
        guidance += stage_guidance(state)['guidance'] + ' Inspect case.audit_assignment for the remaining structural records; it is not an official grade. '
    if creation:
        guidance += (
            "The observed case-creation schema makes source_order_id OPTIONAL. No existing ServiceRequest "
            "is therefore not, by itself, a blocker: that tool can record a NEW request and draft case from "
            "the supported intake fields. A new authorized record is different from claiming a historical "
            "order existed. Resolve provider identity using the public contacts tools, use the actual intake "
            "and approved coding/policy references for clinical fields, and omit optional fields rather than "
            "inventing values. If a required field truly cannot be established, say precisely which field "
            "and which consulted sources leave it unknown. "
        )
    return guidance + '\n' + STOP_RECORD_GUIDANCE + '\nTargeted recovery checks:\n' + packed(recovery_diagnostics(state)) + '\n' + (
        "Continue useful work within the original budgets. If no permitted action remains, return an "
        "incomplete final with a blocker object containing category, blocked_action, why_required, evidence_ids, "
        "attempted_checks, missing_information, other_work_considered and next_required_action. "
        "Explain why the remaining actions depend on the missing fact; preserve supported progress. A blocker is a reported limitation, not proof "
        "that the tool, dataset, or patient selection is wrong."
    )


def request_stop_recovery(state: dict[str, Any], *, max_model_calls: int) -> bool:
    """Give an incomplete final a bounded chance to investigate/replan.

    New completions still pass the independent task contract. No effect is
    replayed here: only another ordinary, budget-charged model turn is requested.
    """
    contract = state.get("completion_contract")
    if not isinstance(contract, dict) or contract.get("domain") not in {"pa_provider", "pa_um", "cm"}:
        return False
    history = state.setdefault("workflow_recoveries", [])
    if len(history) >= MAX_STOP_RECOVERIES or state.get("model_calls", 0) >= max_model_calls:
        state["workflow_stop_reason"] = ("model_budget_exhausted" if state.get("model_calls", 0) >= max_model_calls
                                         else "stop_recovery_limit_reached")
        return False
    fingerprint = evidence_fingerprint(state)
    if history and history[-1].get("evidence_fingerprint") == fingerprint:
        state["workflow_stop_reason"] = "no_new_source_evidence_after_recovery"
        return False
    final = state.get("final")
    blocker = final.get("blocker") if isinstance(final, dict) else None
    history.append({"recovery_number": len(history) + 1,
                    "after_model_call": state.get("model_calls", 0),
                    "evidence_fingerprint": fingerprint,
                    "reported_blocker_present": isinstance(blocker, dict),
                    "diagnostics": recovery_diagnostics(state)})
    state["messages"].append({"role": "user", "content": recovery_prompt(state)})
    state["status"] = "running"
    state["message"] = "Investigating an early stop and replanning within the original case budget."
    state["workflow_stop_reason"] = None
    return True


def validate_dependencies(obligations: list[dict[str, Any]], proposed: dict[str, Any]) -> None:
    graph = {item["id"]: item.get("depends_on", []) for item in obligations}
    graph[proposed["id"]] = proposed.get("depends_on", [])
    if any(dependency not in graph for dependency in graph[proposed["id"]]):
        raise ValueError("obligation dependencies must reference existing obligations")
    visiting, visited = set(), set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError("obligation dependencies must not contain a cycle")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
