"""Case-local links over existing work records, not a hospital graph in a prompt.

Code checks recorded effects and source integrity. Actionability and policy
necessity remain model judgments. No function here chooses a clinical outcome.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .completion_contracts import contract_hash, validate_completion_contract, _tool_matches


def public_task_text(state):
    contract = state.get('completion_contract')
    if isinstance(contract,dict) and isinstance(contract.get('public_instruction'),str):
        return contract['public_instruction']
    # Legacy/synthetic callers may pass the raw task directly. The hash check
    # below still refuses an unmatched wrapped prompt; never guess a substring.
    return state.get('instruction','')


def requested_outcome(state, actual_scope=None):
    contract = state.get('completion_contract')
    unknown = {'status':'unverified', 'is_official_grade':False,
               'semantic_correctness_verified':False, 'requested_branch_ids':[]}
    if state.get('goal_scope_invalid'):
        return unknown
    if not isinstance(contract, dict) or contract_hash(contract) != state.get('completion_contract_sha256'):
        return unknown
    ids = contract.get('requested_branch_ids')
    if not isinstance(ids, list) or not ids or not all(isinstance(i,str) for i in ids):
        return unknown
    branches = [b for b in contract.get('branches',[]) if b.get('id') in ids]
    if len(branches) != len(set(ids)):
        return unknown
    instruction = public_task_text(state)
    if (contract.get('instruction_sha256') and (not isinstance(instruction,str) or
            hashlib.sha256(instruction.encode('utf-8')).hexdigest() != contract['instruction_sha256'])):
        return unknown
    checked = validate_completion_contract({**contract,'branches':branches}, state.get('evidence',[]),
        state.get('scope'), actual_scope or state.get('goal_actual_scope') or state.get('scope'))
    return {**unknown, 'status':('achieved' if checked.get('accepted') else
             'unmet' if checked.get('mapping_status')=='mapped' else 'unverified'),
            'requested_branch_ids':list(ids), 'matched_branch_id':checked.get('branch_id'),
            'missing_milestones':checked.get('missing_milestones',[]),
            'basis':'public_instruction_structural_mapping'}


def view(state, *, blocker_id=None, offset=0, work_offset=0, limit=4, max_chars=3200):
    """Small working slice; full records stay in the case store and are paged.

    'Other work' means not covered by these blocker claims, not code-certified
    permission to execute it. Narrative labels are deliberately not gate logic.
    """
    blockers = [r for r in reversed(state.get('prerequisite_records',[])) if r.get('status')!='resolved'
                and not r.get('helper_job_id')]
    if blocker_id is not None:
        blockers = [r for r in blockers if r.get('id')==blocker_id]
    work = [o for o in state.get('obligations',[]) if o.get('status')!='closed']
    affected = {i for b in blockers for i in b.get('affected_obligation_ids',[])}
    instruction = str(public_task_text(state))
    result = {
        'primary_goal':{'id':'primary','marker':'PRIMARY TASK GOAL — KEEP VISIBLE',
            'source':'original_public_instruction','instruction_sha256':hashlib.sha256(instruction.encode()).hexdigest(),
            'excerpt':instruction[:600], 'excerpt_partial':len(instruction)>600,
            'full_instruction_retained':bool(instruction)},
        'requested_outcome':requested_outcome(state),
        'blockers':[], 'other_open_work':[], 'total_active_blockers':len(blockers),
        'total_open_work':len(work), 'offset':offset, 'next_offset':None,
        'work_offset':work_offset,'next_work_offset':None,
        'projection_partial':False,
        'creates_evidence':False,
        'rule':'A blocker applies to its named action and linked work only. Other work is not automatically permitted. '
               'Necessity, relevance and next investigations are model judgments; source links are not clinical proof. '
               'Use case.get_goal_state or case.get_working_record for omitted records.'}
    if result['requested_outcome'].get('status') == 'achieved' and work:
        result['completion_note'] = ('The requested outcome is verified as achieved. Open work does not undo it: '
            'finish open work that permitted tools can still do; work you have source-linked as blocked is reported '
            'as an outstanding duty in stop_assessment.blocked_obligation_ids, not as an unmet primary goal.')
    # The projection never repeats long source passages or grows with history.
    result['requested_outcome']['missing_milestones'] = result['requested_outcome'].get('missing_milestones',[])[:8]
    consumed = 0
    for b in blockers[offset:offset+limit]:
        item = {k:deepcopy(b[k]) for k in ('id','basis_kind','support','affected_obligation_ids') if k in b}
        item.update(goal_id='primary',blocked_action=str(b.get('blocked_action',''))[:180],
            claim=str(b.get('claim',''))[:220],next_investigation=str(b.get('next_investigation',''))[:220],
            source_ids=[r.get('evidence_id') for r in b.get('facts',{}).get('source_references',[])][:6],
            scope_of_claim='named_action_only',semantic_necessity_verified=False)
        if len(json.dumps({**result,'blockers':result['blockers']+[item]},ensure_ascii=False)) > max_chars:
            break
        result['blockers'].append(item)
        consumed += 1
    if offset+consumed < len(blockers):
        result['next_offset'] = offset+consumed
    other_work = [o for o in work if o['id'] not in affected]
    for o in other_work[work_offset:work_offset+limit]:
        item = {'id':o['id'],'status':o.get('status'),'description':str(o.get('description',''))[:160],
                'depends_on':o.get('depends_on',[])[:8], 'dependencies_partial':len(o.get('depends_on',[]))>8,
                'permission_to_execute_verified':False}
        if len(result['other_open_work'])>=limit or len(json.dumps(
                {**result,'other_open_work':result['other_open_work']+[item]},ensure_ascii=False)) > max_chars:
            break
        result['other_open_work'].append(item)
    if work_offset+len(result['other_open_work']) < len(other_work):
        result['next_work_offset'] = work_offset+len(result['other_open_work'])
    result['projection_partial'] = (offset+consumed < len(blockers) or
        work_offset+len(result['other_open_work']) < len(other_work))
    return result


def action_impact(state, tool, actual_scope=None):
    """Recognize a contract-declared alternative terminal write, never guess it.

    Also honor owner-declared goal impact in source-backed decision records for
    other domains. The declaration is an interpretation, not observed effect.
    """
    if not state.get('goal_planning_enabled'):
        return None
    outcome = requested_outcome(state, actual_scope)
    if outcome['status']!='unmet':
        return None
    contract = state.get('completion_contract') or {}
    requested = set(outcome['requested_branch_ids'])
    alternatives = [b['id'] for b in contract.get('branches',[]) if b['id'] not in requested and any(
        r.get('phase')=='terminal_write_response' and _tool_matches(tool,r.get('tools',[]))
        for r in b.get('requirements',[]))]
    from .policy_grounding import operation_name
    op = operation_name(tool)
    decision = next((d for d in reversed(state.get('policy_decisions',[])) if op in d.get('applies_to',[])),None)
    declared = bool(decision and 'primary' in decision.get('unmet_goal_ids',[]))
    if not alternatives and not declared:
        return None
    return {'goal_id':'primary','requested_outcome':outcome,'alternative_branches':alternatives,
            'owner_declared_goal_impact':declared,'operation':op,
            'decision_record_id':decision.get('id') if decision else None}


def execution_summary(state):
    status = state.get('status','unresolved')
    return {'execution_state':('finished' if status=='complete' else
                'running' if status=='running' else 'stopped'),
            'stop_reason':('no_further_useful_permitted_action_reported' if status=='complete' else status),
            'requested_outcome':requested_outcome(state),
            'observed_endpoint':(state.get('completion_gate') or {}).get('branch_id'),
            'benchmark_evaluation':'not_assessed_by_harness'}


def sourced_blocked_work(state, obligation_ids):
    """Verify explicit blocker links, not that the model's necessity is correct."""
    successful = {e['id'] for e in state.get('evidence',[]) if e.get('scope')==state.get('scope')
                  and e.get('outcome')=='success'}
    covered = set()
    for b in state.get('prerequisite_records',[]):
        if b.get('status')=='resolved' or b.get('helper_job_id'):
            continue
        if b.get('support') not in {'policy_passage_provenance_verified','schema_required_field','observation_referenced_necessity_unverified'}:
            continue
        refs = b.get('facts',{}).get('source_references',[])
        if not refs or not all(r.get('evidence_id') in successful for r in refs):
            continue
        covered.update(b.get('affected_obligation_ids',[]))
    return set(obligation_ids) <= covered
