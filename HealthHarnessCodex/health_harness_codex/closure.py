"""One evidence/obligation assessment for audit, finalization and recovery.

Code verifies provenance/effects. The model must assess whether further useful
permitted work exists; a boolean assertion never proves clinical correctness.
"""
from .completion_contracts import contract_hash, validate_completion_contract


STOP_RECORD_GUIDANCE = (
    'Testcase completion means no further useful permitted action remains within the assignment. '
    'Ambiguity alone is not completion: perform available investigations first. '
    'For a pending-information endpoint or an alternative terminal endpoint leaving the primary task goal unmet, return stop_assessment with '
    'no_further_permitted_action (boolean), reason (string), evidence_ids (successful original same-case IDs), '
    'and other_work_considered (nonempty string list). You may omit investigations_performed: '
    'code fills this factual list of completed read/dialogue operations from the current case journal, '
    'not their clinical adequacy. If supplied explicitly, it must cite original read/dialogue observations. '
    'You must still acknowledge existing work: '
    'Put waiting_on_obligation_ids and blocked_obligation_ids INSIDE stop_assessment: '
    'stop_assessment.waiting_on_obligation_ids must match deferred work, and '
    'stop_assessment.blocked_obligation_ids must match source-linked open work. '
    'Unfinished work remains unfinished and never counts as achieved. '
    'Explain why the outstanding work cannot be performed now, including available retrieval, '
    'communication and remaining assigned stages. A pending case status alone is insufficient. '
    'Local assignment audits and notes create no original ev: evidence IDs; cite external observations. '
    'If an action is still available, perform it rather than claiming no further action. '
    'A valid no-further-action record may accompany complete or incomplete: it describes current '
    'execution, while the patient case can remain pending. Never use it to conceal missing internal work, '
    'a tool failure, an unknown write or budget exhaustion. The judge separately evaluates correctness.'
)


def _rejected(reason, **fields):
    return {'accepted': False, 'structural_accepted': False, 'branch_id': None,
            'missing_milestones': [], 'reason_code': reason, **fields}


def investigation_source_ids(state):
    from .working_set import canonical
    # Mutation safety and information gathering are separate dimensions. A
    # dialogue writes a turn AND observes a counterparty response. A summary
    # authored by the owner or a terminal mutation is not that observation.
    return {e['id'] for e in state.get('evidence',[]) if e.get('scope')==state.get('scope')
        and e.get('outcome')=='success' and (e.get('effect')=='read' or
        canonical(e.get('tool','')) in {'cm_outreach.send_message','p2p_session.send_turn'})}


def derive_stop_metadata(state, payload, gate):
    """Derive journal facts or relocate explicit worker lists; never invent acknowledgment."""
    record=payload.get('stop_assessment')
    if not isinstance(record,dict):return payload,None
    derived={};relocated={}
    values={'investigations_performed':sorted(investigation_source_ids(state))}
    for key,value in values.items():
        if key not in record:derived[key]=value
    for key in ('waiting_on_obligation_ids','blocked_obligation_ids'):
        if key not in record and key in payload:relocated[key]=payload[key]
    if not derived and not relocated:return payload,None
    return {**payload,'stop_assessment':{**record,**derived,**relocated}}, {
        'source':'successful same-case read/dialogue journal and explicit worker field placement',
        'derived_fields':list(derived),'relocated_fields':list(relocated),
        'clinical_reason_or_patient_choice_changed':False,
        'semantic_actionability_verified':False}


def assess_closure(state, actual_scope=None, *, branch_id=None):
    contract = state.get('completion_contract')
    if not isinstance(contract, dict):
        return _rejected('completion_contract_missing')
    if state.get('completion_contract_sha256') != contract_hash(contract):
        return _rejected('completion_contract_integrity_error')
    scope = state.get('scope')
    if contract.get('task_id') != (scope or {}).get('task'):
        return _rejected('completion_contract_task_mismatch')
    selected = contract
    if branch_id is not None:
        selected = {**contract, 'branches': [b for b in contract.get('branches', []) if b['id'] == branch_id]}
    gate = dict(validate_completion_contract(selected, state.get('evidence', []), scope, actual_scope or scope))
    gate['structural_accepted'] = gate.get('accepted') is True
    gate['clinical_correctness_verified'] = False
    gate['is_official_grade'] = False
    from .goal_state import requested_outcome
    gate['requested_outcome'] = requested_outcome(state, actual_scope)
    deferred = [o for o in state.get('obligations', []) if o.get('status') == 'deferred']
    opened = [o['id'] for o in state.get('obligations', []) if o.get('status') not in {'closed', 'deferred'}]
    gate.update(open_obligation_ids=opened, deferred_obligation_ids=[o['id'] for o in deferred],
                requires_stop_assessment=(gate.get('allows_external_wait') is True or
                    (state.get('goal_planning_enabled') is True and gate['requested_outcome']['status']=='unmet')))
    # Work-accounting metadata is needed for a truthful FAILED stop too; it
    # must not disappear merely because endpoint verification failed first.
    from .goal_state import sourced_blocked_work
    if opened and state.get('goal_planning_enabled') and sourced_blocked_work(state,opened):
        gate.update(blocked_obligation_ids=opened,blocked_work_necessity_verified=False)
    if not gate['structural_accepted']:
        return gate
    if opened:
        from .goal_state import sourced_blocked_work
        if (state.get('goal_planning_enabled') and gate['requested_outcome']['status']=='unmet'
                and gate.get('allows_external_wait') is not True and sourced_blocked_work(state,opened)):
            gate.update(requires_stop_assessment=True,blocked_obligation_ids=opened,
                        blocked_work_necessity_verified=False)
        elif (state.get('goal_planning_enabled') and gate['requested_outcome']['status']=='achieved'
                and sourced_blocked_work(state,opened)):
            # The requested outcome itself is verified. Remaining actor-recorded duties with
            # source-linked blockers stay open and must be acknowledged; they are not hidden.
            gate.update(requires_stop_assessment=True,blocked_obligation_ids=opened,
                        blocked_work_necessity_verified=False,outstanding_obligation_ids=opened)
        else:
            gate.update(accepted=False, reason_code='open_obligations')
            return gate
    if deferred:
        successful = {e['id'] for e in state.get('evidence', [])
                      if e.get('scope') == scope and e.get('outcome') == 'success'}
        if (gate.get('allows_external_wait') is not True or any(
                o.get('handoff_branch') != gate['branch_id'] or not o.get('evidence_ids')
                or not set(o['evidence_ids']) <= successful
                or not isinstance(o.get('next_action'), str) or not o['next_action'].strip()
                for o in deferred)):
            gate.update(accepted=False, reason_code='deferred_work_requires_matching_handoff')
            # Select a supported alternative with matching obligations, rather
            # than letting the first structural match dictate closure policy.
            if branch_id is None:
                for branch in contract.get('branches',[]):
                    if branch['id']==gate['branch_id']:continue
                    alternative=assess_closure(state,actual_scope,branch_id=branch['id'])
                    if alternative.get('accepted') is True:return alternative
    return gate


def assess_stop_record(state, payload, gate):
    record = payload.get('stop_assessment')
    if not isinstance(record, dict):
        return {'accepted': False, 'reason_code': 'stop_assessment_missing'}
    for key in ('waiting_on_obligation_ids','blocked_obligation_ids'):
        if key not in record or key not in payload:continue
        nested,outer=record[key],payload[key]
        same=(nested==outer or (isinstance(nested,list) and isinstance(outer,list)
            and all(isinstance(x,str) for x in nested+outer) and set(nested)==set(outer)))
        if not same:
            return {'accepted':False,'reason_code':'stop_work_accounting_conflict',
                    'field':'stop_assessment.'+key,
                    'instruction':'Top-level and nested work lists conflict. Return one consistent explicit acknowledgment; no values were overwritten.'}
    if record.get('no_further_permitted_action') is not True:
        return {'accepted': False, 'reason_code': 'worker_reports_actions_remaining'}
    if not isinstance(record.get('reason'), str) or not record['reason'].strip():
        return {'accepted': False, 'reason_code': 'stop_reason_missing'}
    for key in ('investigations_performed', 'other_work_considered'):
        value = record.get(key)
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
            return {'accepted': False, 'reason_code': key + '_missing'}
    sources = record.get('evidence_ids')
    known = {e['id'] for e in state.get('evidence', [])
             if e.get('scope') == state.get('scope') and e.get('outcome') == 'success'}
    read_sources = investigation_source_ids(state)
    if not set(record['investigations_performed']) <= read_sources:
        return {'accepted':False,'reason_code':'stop_investigation_evidence_unverified',
                'unsupported_investigation_ids':sorted(set(record['investigations_performed'])-read_sources),
                'instruction':'Cite original reads or counterparty dialogue responses as investigations. '
                    'Authored summaries and terminal writes may support observed effects, but are not investigations.'}
    if (not isinstance(sources, list) or not sources or any(not isinstance(x, str) for x in sources)
            or not set(sources) <= known):
        return {'accepted': False, 'reason_code': 'stop_evidence_unverified'}
    waiting = record.get('waiting_on_obligation_ids')
    if (not isinstance(waiting, list) or any(not isinstance(x, str) for x in waiting)
            or set(waiting) != set(gate.get('deferred_obligation_ids', []))):
        return {'accepted': False, 'reason_code': 'stop_dependencies_not_accounted_for'}
    blocked = record.get('blocked_obligation_ids',[])
    if (not isinstance(blocked,list) or any(not isinstance(i,str) for i in blocked)
            or set(blocked)!=set(gate.get('blocked_obligation_ids',[]))):
        return {'accepted':False,'reason_code':'stop_blocked_work_not_accounted_for'}
    return {'accepted': True, 'reason_code': 'source_backed_no_further_action_reported',
            'semantic_actionability_verified': False, 'evidence_ids': list(dict.fromkeys(sources))}
