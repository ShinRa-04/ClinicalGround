"""One bounded read-only challenge to a recurring case-owner blocker."""
from __future__ import annotations

from .models import ToolCall
from .working_set import canonical,packed
from .cm_guidance import STOP_REVIEW


def review_due(h,state,trigger):
    if (h.recovery_helper_policy!='auto' or h.composition=='combined' or h._helper_channel
            or state.get('helper_active') or state.get('recovery_audit')):
        return False
    contract=state.get('completion_contract') or {}
    if contract.get('mapping_status')!='mapped' or contract.get('domain') not in {'pa_provider','pa_um','cm'}:
        return False
    if state.get('status') not in {'running','unresolved'}:
        return False
    if trigger=='proposed_stop':
        from .goal_state import requested_outcome
        return bool(state.get('goal_planning_enabled') and requested_outcome(state)['status']=='unmet'
            and not any(r.get('status')=='completed' for r in state.get('terminal_reviews',{}).values()))
    if trigger=='repeated_final':return bool(state.get('workflow_recoveries'))
    history=state.get('progress_recoveries',[])
    return bool(history and state.get('current_plan',{}).get('reported_blocker')
        and state['model_calls']>=history[-1]['after_model_call']+3
        and state.get('last_information_progress_call',0)<=history[-1]['after_model_call'])


def run_recovery_audit(h,scope,state,owner,fence,trigger):
    if not review_due(h,state,trigger):return False
    remaining=h.limits.max_model_calls-state['model_calls']
    if remaining<4 or h.limits.max_tool_calls-state['tool_calls']<1:
        return False
    from .helper_jobs import run_helper
    from .assignment import completion_audit,stage_guidance
    specs=h._available_specs(h._tool_map(),state)
    preferred={'case.get_goal_state','case.find_evidence','case.audit_assignment','case.get_tool_contract','case.get_working_record','case.inspect_evidence',
        'case.retrieve_evidence','case.find_evidence','workspace.read_many','workspace.hybrid_search',
        'review.get_md_review_data','review.get_nurse_review_data','determination.get_summary',
        'cases.get_case','cm_chart.get_chart_data','cm_outreach.get_transcript','payer_intake_hub.get_intake_case'}
    names=[s.name for s in specs if s.effect=='read' and canonical(s.name) in preferred]
    if not names:return False
    selected=[];seen=set()
    for e in reversed(state.get('evidence',[])):
        name=canonical(e.get('tool',''))
        if (e.get('scope')!=scope.to_dict() or e.get('outcome')!='success'
                or name.startswith('workspace.') or name in seen):continue
        selected.append(e['id']);seen.add(name)
        if len(selected)==3:break
    audit=completion_audit(state,h._identity_scope(scope,state).to_dict())
    brief=[{'id':b['id'],'missing':b['missing_milestones'][:5]} for b in audit.get('branches',[])[:3]]
    plan=state.get('current_plan',{});blocker=plan.get('reported_blocker',{})
    question=('Challenge the owner blocker rather than agreeing with it. Also test whether the proposed stop is premature. Determine which assigned role work remains, '
        'whether the cited missing information actually prevents that next action, and which public API/policy supports '
        'that necessity. Inspect current records and tool contracts or new permitted references as needed. '
        'Distinguish clinical uncertainty, role handoff, supported information request, and an assumed prerequisite. '
        'Return source-backed conclusions, limitations and a supported next investigation; do not choose a clinical outcome '
        'to satisfy a checklist, perform writes, invent facts, or treat this helper job as whole-case completion.\n'
        + STOP_REVIEW + '\n'
        +packed({'assignment_excerpt':state.get('instruction','')[:350],
            'owner_claim':str(plan.get('claim',''))[:400],
            'reported_blocker':{k:str(v)[:200] for k,v in blocker.items()},
            'remaining_structural_work':brief,'phase':{k:v for k,v in stage_guidance(state).items()
                if k in {'domain','current_responsibility'}}}))
    # Keep the delegated question bounded; the full audit is also a read tool.
    question=question[:4000]
    state['recovery_audit']={'status':'started','trigger':trigger,'after_model_call':state['model_calls'],
                             'write_authority':False,'source_ids':selected}
    state['status']='running';h._save(scope,state,owner,fence)
    if h.progress:h.progress('stop_review_started' if trigger=='proposed_stop' else 'blocker_audit_started',after_model_call=state['model_calls'])
    result=run_helper(h,scope,state,ToolCall('controller-blocker-audit','case.request_helper',{
        'role_id':'SH-10','question':question,'evidence_ids':selected,'tool_names':names,
        'allow_writes':False,'max_model_calls':min(3,remaining-2),'max_tool_calls':10}),owner,fence,invocation='recovery_audit')
    state=h.store.load_case(scope)
    state['recovery_audit'].update(status='completed',result=result,helper_id=result.get('helper_id'))
    if state.get('status')=='running':
        state['messages'].append({'role':'user','content':
            'A bounded read-only recovery reviewer examined the blocker. This is advice, not new clinical evidence or '
            'permission to write. Reassess your plan against its cited observations and the assignment. '
            'You retain the decision and must justify a remaining blocker. No other staff member is automatically '
            'performing your remaining work.\n'+STOP_REVIEW+'\n'+packed(result)})
    h._save(scope,state,owner,fence)
    if h.progress:h.progress('stop_review_finished' if trigger=='proposed_stop' else 'blocker_audit_finished',status='completed' if result.get('status')=='complete' else 'incomplete')
    return True
