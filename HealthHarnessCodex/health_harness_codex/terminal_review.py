"""Selective precommit challenge when a supported action leaves a goal unmet."""
from __future__ import annotations

import hashlib
import json

from .goal_state import action_impact, view
from .models import ToolCall
from .working_set import canonical, business


def before_action(h, scope, state, call, owner, fence):
    """Return updated state and optional not-dispatched feedback.

    No reviewer decides the clinical outcome and no terminal write is reserved
    here. A reviewer result must return to a NEW owner turn before execution.
    """
    impact = action_impact(state, call.name, h._identity_scope(scope,state).to_dict())
    if impact is None:
        return state, None
    decision = next((d for d in reversed(state.get('policy_decisions',[]))
                     if impact['operation'] in d.get('applies_to',[])),None)
    feedback = {'error':'terminal_goal_impact_requires_review','known_not_dispatched':True,
        'goal_impact':impact,'required_tool':'case.record_policy_decision',
        'instruction':'The requested outcome remains unmet. Record current sources, exact bound arguments, '
            'remaining_actions_considered and why_act_now before this terminal action. '
            'A source-backed stop is allowed; neither the goal nor this review authorizes fabricated consent or facts.'}
    if (not decision or not decision.get('provenance_verified') or
            decision.get('bound_arguments',{}).get(impact['operation']) != call.arguments or
            not decision.get('remaining_actions_considered') or not str(decision.get('why_act_now','')).strip()):
        return state, feedback
    if h._helper_channel:
        return state, {**feedback,'error':'terminal_goal_impact_requires_owner',
                       'instruction':'Return this consequential decision to the owner; do not delegate recursively.'}
    ids = list(dict.fromkeys(decision.get('case_evidence_ids',[]) +
        [s['evidence_id'] for s in decision.get('policy_sources',[])]))
    observations = {e['id']:e for e in state.get('evidence',[]) if e.get('scope')==scope.to_dict() and e.get('outcome')=='success'}
    if any(i not in observations for i in ids):
        return state, feedback
    effect_arguments = dict(call.arguments)
    if impact['operation']=='cm_intake.disenroll_case':
        # Public service contract: reason is audit text, not a different case
        # transition. Exact current reason is still bound/validated above.
        effect_arguments.pop('reason',None)
    source_hashes = sorted({hashlib.sha256(json.dumps(business(observations[i]['observed_result']),
        sort_keys=True,ensure_ascii=False).encode()).hexdigest() for i in ids})
    material = {'effect_arguments':effect_arguments,'operation':impact['operation'],
        'contract_sha256':state.get('completion_contract_sha256'),
        'source_content_sha256':source_hashes}
    fingerprint = hashlib.sha256(json.dumps(material,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    reviews = state.setdefault('terminal_reviews',{})
    prior = reviews.get(fingerprint)
    if prior and prior.get('status') in {'completed','owner_only'}:
        prior['latest_owner_decision_record_id']=decision['id']
        prior['current_wording_independently_reviewed']=decision['id']==prior['decision_record_id']
        h._save(scope,state,owner,fence)
        return state, None
    if prior:
        return state, {**feedback,'error':'terminal_review_unfinished','review_id':fingerprint,
                       'instruction':'This review was already started; reconcile it rather than starting a duplicate.'}
    review = {'status':'owner_only','operation':impact['operation'],'decision_record_id':decision['id'],
              'goal_id':'primary','write_authority':False,'semantic_correctness_verified':False}
    reviews[fingerprint] = review
    # Honor the existing frozen composition, policy and shared budgets. Do not
    # invent a second model in combined mode or falsely claim a review occurred.
    remaining = h.limits.max_model_calls-state['model_calls']
    if h.composition=='combined' or h.recovery_helper_policy!='auto' or remaining<4:
        review['reason'] = 'helpers_disabled' if h.composition=='combined' or h.recovery_helper_policy!='auto' else 'helper_budget_unavailable'
        h._save(scope,state,owner,fence)
        return state, None
    preferred = {'case.get_goal_state','case.find_evidence','case.audit_assignment','case.get_tool_contract','case.get_working_record',
        'case.inspect_evidence','case.retrieve_evidence','workspace.read_file','workspace.read_many',
        'workspace.hybrid_search','cases.get_case','determination.get_summary',
        'review.get_md_review_data','cm_chart.get_chart_data','cm_outreach.get_transcript'}
    names = [s.name for s in h._available_specs(h._tool_map(),state) if s.effect=='read' and canonical(s.name) in preferred]
    if not names or h.limits.max_tool_calls-state['tool_calls']<1:
        review['reason']='helper_tool_budget_unavailable'
        h._save(scope,state,owner,fence)
        return state,None
    policy_ids = list(dict.fromkeys(s['evidence_id'] for s in decision.get('policy_sources',[])))
    selected = list(dict.fromkeys(decision.get('case_evidence_ids',[])[-2:] + policy_ids[:2]))
    question = ('Challenge this proposed terminal decision BEFORE execution. It leaves an explicit requested outcome unmet. '
        'Check the source-backed justification, what work this action prevents, and whether useful permitted investigation '
        'or communication remains. You may retrieve new permitted sources; do not simply agree with the owner. '
        'Check whether the claimed barrier concerns performing an activity, recording its refusal/non-performance, '
        'or finalizing a source-grounded document; establish the actual policy and tool scope instead of equating these. '
        'Distinguish tool requirements, observed state, policy interpretation and assumptions. Respect patient choices and '
        'actual stopping rules; never force a clinical outcome. Return evidence IDs, conclusion and unresolved questions.\n'
        + json.dumps({'goal':view(state)['primary_goal'],
            'impact':{'operation':impact['operation'],'alternative_branches':impact['alternative_branches'],
                      'requested_outcome_status':impact['requested_outcome']['status']},
            'proposed_argument_keys':sorted(call.arguments),
            'decision_policy_source_ids':policy_ids[:2],
            'proposed_reason_excerpt':str(call.arguments.get('reason',''))[:200],
            'owner_justification':{'assessment_excerpt':str(decision.get('assessment',''))[:300],
                'why_act_now_excerpt':str(decision.get('why_act_now',''))[:300],
                'remaining_actions_excerpt':[str(x)[:160] for x in decision.get('remaining_actions_considered',[])[:3]]},
            'excerpted':True},ensure_ascii=False))
    review.update(status='started',source_ids=selected,after_model_call=state['model_calls'])
    h._save(scope,state,owner,fence)
    if h.progress:
        h.progress('terminal_review_started',tool_name=impact['operation'],after_model_call=state['model_calls'])
    from .helper_jobs import run_helper
    result = run_helper(h,scope,state,ToolCall('terminal-review-'+fingerprint[:12],'case.request_helper',{
        'role_id':'SH-10','question':question,'evidence_ids':selected,'tool_names':names,
        'allow_writes':False,'max_model_calls':min(3,remaining-1),'max_tool_calls':8}),owner,fence,invocation='terminal_review')
    state = h.store.load_case(scope)
    state['terminal_reviews'][fingerprint].update(status='completed',helper_id=result.get('helper_id'),
        result=result,after_model_call=state['model_calls'])
    h._save(scope,state,owner,fence)
    if h.progress:
        h.progress('terminal_review_finished',status='completed')
    return state, {**feedback,'error':'terminal_review_returned_to_owner','review_id':fingerprint,
        'helper_result':result,
        'instruction':'No terminal write was dispatched. Reassess the reviewer conclusion against its sources. '
            'Revise your plan or explicitly re-propose the justified action in the next owner turn. '
            'The helper is advisory and has no clinical decision or write authority.'}
