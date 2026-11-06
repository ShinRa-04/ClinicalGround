"""Assignment -> editable plan -> observed evidence. No clinical outcome choice."""
from __future__ import annotations

from .completion_contracts import _tool_matches
from .closure import assess_closure
from .working_set import business, stage, canonical


def completion_audit(state, actual_scope=None):
    contract=state.get('completion_contract')
    if not isinstance(contract,dict):
        return {'mapping_status':'unverified','branches':[],'accepted':False,
                'warning':'No structural assignment contract is available; do not invent an endpoint.'}
    checked=assess_closure(state,actual_scope)
    branches=[]
    for branch in contract.get('branches',[]):
        result=assess_closure(state,actual_scope,branch_id=branch['id'])
        missing=result.get('missing_milestones',[])
        branches.append({'id':branch['id'],'accepted':result['accepted'],
            'structural_accepted':result['structural_accepted'],
            'reason_code':result['reason_code'],
            'open_obligation_ids':result.get('open_obligation_ids',[]),
            'allows_external_wait':branch.get('allows_external_wait',False),
            'missing_milestones':missing,
            'satisfied_milestones':[r['id'] for r in branch['requirements'] if r['id'] not in missing],
            'requirements':[{'id':r['id'],'tools':r['tools'],'phase':r['phase']} for r in branch['requirements']]})
    return {**checked,'branches':branches,'assignment_source':{
        'kind':'public_instruction_and_documented_workflow','instruction_sha256':contract.get('instruction_sha256'),
        'mapping_basis':contract.get('mapping_basis')},
        'clinical_correctness_verified':False,'is_official_grade':False,
        'creates_evidence':False,
        'evidence_rule':'This local audit creates no ev: source ID. Cite the original successful external tool observations for case facts; do not invent an audit evidence ID.',
        'rule':'This checks scoped records/effects against an explicit structural interpretation. '
               'The assignment is fixed; your plan and clinical branch are yours to revise. '
               'A missing record is not an instruction to manufacture a decision. '
               'A pending case alone is not completion. Stop only after supported effects and a source-backed '
               'assessment that no further useful permitted action remains; ambiguity requires investigation.'}


def _latest(state,tool):
    for e in reversed(state.get('evidence',[])):
        if (e.get('scope')==state.get('scope') and e.get('outcome')=='success'
                and _tool_matches(e.get('tool',''),[tool])):
            value=business(e['observed_result'])
            return value if isinstance(value,dict) else {}
    return {}


def stage_guidance(state):
    domain=(state.get('completion_contract') or {}).get('domain')
    if (state.get('completion_contract') or {}).get('mapping_status')!='mapped':
        return {'domain':domain,'current_responsibility':'assignment_unverified',
            'guidance':'The structural goal is not mapped. Establish assignment scope from public instructions; do not invent required stages or a terminal outcome.',
            'clinical_outcome_selected_by_code':False}
    if domain=='pa_um':
        requirements=[r for b in state['completion_contract'].get('branches',[]) for r in b['requirements']]
        needs=lambda name:any(name in r['tools'] for r in requirements)
        nurse=_latest(state,'review.submit_nurse_case_recommendation').get('case_recommendation')
        md=_latest(state,'review.submit_md_case_decision').get('case_decision')
        if md:
            decision=md.get('decision')
            if decision=='request_info':
                phase='information_handoff'
                guidance=('Verify the physician request, rationale, deadline, sign-off, delivered pend notice and fresh case/MD readback. '
                    'Do not force approval or denial while evidence is genuinely unresolved. '
                    'Use case.audit_assignment to check whether the assigned review-round handoff is structurally supported. '
                    'Only a verified external handoff can defer an external obligation; it cannot conceal an unperformed MD stage.')
            elif decision=='p2p_review':
                phase='peer_to_peer'
                guidance='Own the applicable peer-to-peer work and subsequent assigned decision/notice. A recorded referral does not start an unrequested worker.'
            else:
                phase='determination_and_notice'
                guidance='Complete applicable determination/notice actions using the observed physician decision and policy. Verify actual delivery and fresh state; never change the clinical outcome just to satisfy a checker.'
        elif needs('review.submit_md_case_decision') and (nurse or not needs('review.submit_nurse_case_recommendation')):
            phase='physician_review'
            guidance=('The assignment still includes the MD decision. A nurse recommendation finishes the nurse subtask, not this owner assignment. '
                'Pending provider documents alone do not establish that MD work is forbidden: the public MD contract supports request_info as well as other decisions. '
                'Inspect current MD state, applicable policy and reviewer authority; perform or explicitly delegate the supported MD work. '
                'A newly authored reviewer decision/sign-off is distinct from evidence of a treating physician historical order. '
                'Do not invent facts, sign-offs or prerequisites. No other worker picks up this stage unless a job is actually started.')
        elif needs('triage.route_case') and not _latest(state,'triage.route_case'):
            phase='triage'
            guidance=('Complete the assigned routing and observed triage requirements; preserve immutable records. '
                'A lookup or SLA calculation can return inputs without saving a triage decision. Inspect the permitted disposition/persistence contract '
                'and actual triage readback; follow the API-supported ordering and distinguish already-recorded values from values you merely calculated. '
                'Do not invent prerequisites or overwrite a valid existing decision. A chosen lane is a stage transition, not the whole review.')
        else:
            phase='nurse_review'
            guidance=('Assess source-backed clinical criteria and the supported nurse recommendation. Uncertainty can be recorded as unclear where permitted. '
                'A request for documents does not waive an MD decision explicitly required by the assignment. '
                'You remain responsible for later assigned stages; delegate explicitly if a specialist should do them.')
    else:
        phase=stage(state)
        guidance=({'pa_provider':'Own the provider-stage preparation/disposition/submission or documented information handoff. Provider completion does not imply a separate payer case has run.',
                   'cm':'Own the assigned outreach/assessment/plan or supported care-management handoff. A proposed handoff is not delivered care.'}.get(domain,
                    'Use the public assignment, observed effects and actual authority to determine the current responsibility.'))
    packet={}
    if domain=='cm':
        from .roles import roles_for
        ids={'intake':{'CM-01','CM-02'},'outreach':{'CM-03','CM-04','CM-05','CM-09'},
             'assessment':{'CM-06','CM-07'},'plan':{'CM-12','CM-13'},'closure':{'CM-20'}}.get(phase,set())
        packet={'responsibility_packet':[{'role_id':r['id'],**{k:r[k] for k in
            ('name','inputs','output','boundary','completion_check','decision_scope','authority','approach')}}
            for r in roles_for('CM') if r['id'] in ids and r['model_visible']],
            'responsibility_packet_source':'packaged design contracts, not policy or independent clinical authority'}
        if phase=='outreach':
            guidance+=' Observe each reply before authoring its summary.'
            guidance+=' The end_outreach_call operation closes the conversation as well as saving its summary. Before that close, retrieve the governing assessment/plan standards and ask, within the given consent, for remaining patient-interview needs while contact is open. Gather information only after the actual required consent/permissions; a persistence-stage transition is not a substitute for those permissions.'
            if state.get('cm_dialogue_worker'):
                guidance+=' A scoped CM-04 conversation worker has run. Verify its ORIGINAL transcript, not its completion label, before recording consent or clinical findings. You retain responsibility for structured records, assessment and care plan.'
            guidance+=' Make the next message responsive to the patient\'s latest question, priorities and permissions. Required topics guide the work; they do not justify a checklist monologue or disregarding a concern. Revisit the plan when the reply changes what the patient is willing to discuss.'
        elif phase=='closure':
            guidance+=' An actual terminal state is observed. Verify its effects and remaining obligations; this does not establish that the original requested outcome was achieved or authorize reopening the case.'
    return {'domain':domain,'current_responsibility':phase,'guidance':guidance,**packet,
            'source':'public assignment requirements and successful same-case operation records',
            'clinical_outcome_selected_by_code':False}


def local_tool_allowed(domain,name):
    if name=='case.record_external_handoff':return domain in {'UM','pa_um'}
    return name!='case.defer_obligation' or domain in {'PA','pa_provider'}


def resolve_tool(specs,name):
    exact=next((s for s in specs if s.name==name),None)
    if exact:return exact
    matches=[s for s in specs if canonical(s.name).casefold()==name.casefold() or _tool_matches(s.name,[name])]
    if len(matches)!=1:
        raise ValueError('tool name must resolve uniquely to a permitted alias or public operation')
    return matches[0]
