"""CM outreach worker in a clean context, using the owner's normal dispatcher."""
from .models import ToolCall
from .working_set import business, canonical, packed

QUESTION_CAP = 3000


def outreach_question(instruction, source_id, session_id):
    """Cap the rendered question, including JSON escaping, by trimming only the excerpt."""
    context = (
        "Own this patient-facing outreach stage; the owner's proposed first message was NOT sent. "
        "Before speaking, use case.record_authorized_statements to prepare source-backed answers and decide policy conditions from observed records. "
        "Read the current transcript and governing outreach protocol, including entry and exit duties. "
        "Plan required choice and closing information while contact remains open: another closing turn "
        "may be unavailable. An actual stop ends contact immediately; do not reopen it to repair omissions. "
        "The handoff supplies downstream capabilities and a chart index; retrieve relevant original passages. "
        "Reviewing existing information when permitted differs from formal assessment; useful help need not "
        "all depend on enrollment. Explain what collaborative planning adds to independent action. "
        "Contact is turn-capped (the send tool's max_turns; replies report turn_number) and a closing offer can "
        "end it, so every message spends a shared limit. Before speaking, also retrieve the assessment standards "
        "and record their required counterparty items as information_needs; "
        "keep the decision portion brief and, after clear enrollment consent, if willing, gather information_needs "
        "in their order in grouped questions, asking named instruments' items; acknowledge problems raised and note them for the plan stage "
        "instead of solving them during the interview. On ended contact or a completed interview, retrieve the final transcript and "
        "return original source IDs, participation decision, priorities, findings and unresolved duties. "
        "Only the owner saves and verifies outreach summaries, structured assessments, plans and closure "
        "records. Shared budgets apply; there is no separate fixed dialogue-turn quota.\n"
    )
    def render(n):
        return context + packed({'public_assignment_excerpt':instruction[:n],
            'assignment_excerpted':n<len(instruction), 'observed_session_source_id':source_id,
            'session_id':session_id})
    if len(render(0))>QUESTION_CAP:
        raise ValueError('Outreach session metadata exceeds question cap')
    low,high=0,len(instruction)
    while low<high:
        middle=(low+high+1)//2
        if len(render(middle))<=QUESTION_CAP:low=middle
        else:high=middle-1
    return render(low)


def stage_handoff(state, specs):
    """Small capability/receipt map, not permission or clinical evidence."""
    owner_tools=[]
    for spec in specs:
        name=canonical(spec.name)
        if name.startswith(('cm_assessment.','cm_care_plan.')):
            owner_tools.append({'tool':name,'description':' '.join(spec.description.split())[:160]})
    receipts=[]
    for name in ('cm_intake.open_case','cm_chart.submit_chart_review'):
        item=next((e for e in reversed(state.get('evidence',[]))
            if e.get('scope')==state.get('scope') and e.get('outcome')=='success'
            and canonical(e.get('tool',''))==name),None)
        if item:receipts.append({'tool':name,'evidence_id':item['id']})
    chart=next((e for e in reversed(state.get('evidence',[]))
        if e.get('scope')==state.get('scope') and e.get('outcome')=='success'
        and canonical(e.get('tool',''))=='cm_chart.get_chart_data'),None)
    chart_index=None
    if chart:
        from .retrieval import field_overview
        value=business(chart['observed_result'])
        if isinstance(value,dict):
            chart_index={'evidence_id':chart['id'],'metadata_only':True,
                'available_top_level_fields':list(value)[:24],'field_index_partial':len(value)>24,
                'document_index':field_overview(value,4500).get('document_index'),
                'instruction':'Use this original source ID and document/field pointers with case.retrieve_evidence. '
                    'Metadata is not clinical evidence; retrieve the actual text, check applicability and patient permission.'}
    return {'kind':'team_capability_metadata','grants_permissions':False,
        'requested_work':state.get('completion_contract',{}).get('public_instruction','')[:500],
        'owner_only_tools':sorted(owner_tools,key=lambda x:x['tool'])[:6],
        'observed_operation_receipts':receipts,
        'chart_source_index':chart_index,
        'capability_rule':'Use the system capability rule; these owner-only tools are not delegated speaking tools.',
        'interpretation':'These are the case owner\'s actual tool contracts and original receipt references. '
            'They establish neither patient consent nor clinical eligibility or promised delivery. '
            'Retrieve applicable policy and original records before explaining the program. '
            'Your callable tools and write permissions remain those separately delegated.'}


def session_ended(state, scope, session_id):
    """True when this scope observed that session as ended (its transcript, or a send result after its start)."""
    started=False
    for e in state.get('evidence',[]):
        if e.get('scope')!=scope.to_dict() or e.get('outcome')!='success':continue
        value=business(e.get('observed_result'))
        if isinstance(value,dict) and isinstance(value.get('content'),list) and value['content'] \
                and isinstance(value['content'][0],dict):
            value=value['content'][0].get('parsed_json',value)
        if not isinstance(value,dict):continue
        name=canonical(e.get('tool',''))
        if name=='cm_outreach.start_outreach_call':
            started=value.get('session_id')==session_id
        elif name=='cm_outreach.get_transcript' and value.get('session_id')==session_id and value.get('status')=='ended':
            return True
        elif name=='cm_outreach.send_message' and started and (value.get('session_status')=='ended' or value.get('stopped') is True):
            return True
    return False


def before_send(h, scope, state, call, owner, fence, proposal_round):
    if (canonical(call.name)=='cm_outreach.send_message' and not h._helper_channel
            and session_ended(state,scope,call.arguments.get('session_id'))):
        # Sending to an ended session errors on a write, which would become an unknown outcome.
        return state,{'error':'message_not_sent','reason':'contact_ended','owner_proposal_not_dispatched':True,
            'known_not_dispatched':True,'creates_evidence':False,
            'instruction':'This session was observed as ended and cannot be reopened. Continue with the next '
                          'permitted work using what the transcript shows.'}
    if (canonical(call.name)!='cm_outreach.send_message' or h._helper_channel
            or h.composition=='combined' or h.recovery_helper_policy!='auto'
            or state.get('completion_contract',{}).get('domain')!='cm'):
        return state,None
    prior=state.get('cm_dialogue_worker')
    if prior:
        if prior['status']=='started':
            return state,{'error':'delegated_dialogue_requires_reconciliation',
                'owner_proposal_not_dispatched':True,'delegated_effects_may_exist':True,
                'instruction':'An earlier dialogue worker did not settle. Reconcile its journal before further contact; do not restart it.'}
        return state,None
    # Never take over an already-running conversation or infer session handles.
    sources=[e for e in state.get('evidence',[]) if e.get('scope')==scope.to_dict() and e.get('outcome')=='success']
    if any(canonical(e.get('tool',''))=='cm_outreach.send_message' for e in sources):return state,None
    start=next((e for e in reversed(sources) if canonical(e.get('tool',''))=='cm_outreach.start_outreach_call'
        and isinstance(business(e['observed_result']),dict)
        and business(e['observed_result']).get('session_id')==call.arguments.get('session_id')
        and business(e['observed_result']).get('status')=='active'),None)
    if not start:return state,None
    remaining=h.limits.max_model_calls-state['model_calls']-2
    available_tools=h.limits.max_tool_calls-state['tool_calls']
    if remaining<3 or available_tools<2:return state,None
    allowed_reads={'cm_outreach.get_transcript','case.find_evidence','case.inspect_evidence','case.retrieve_evidence',
        'case.search_evidence','case.search_narrative','case.get_tool_contract','workspace.read_file',
        'workspace.read_many','workspace.hybrid_search'}
    specs=[s for s in h._available_specs(h._tool_map(),state)
        if (s.effect=='read' and canonical(s.name) in allowed_reads)
        or canonical(s.name) in {'cm_outreach.send_message','case.record_authorized_statements'}]
    selected=[start['id']]
    # Already-retrieved same-case records/policy only; preserve original source IDs.
    for e in sources:
        if canonical(e.get('tool','')) in {'cm_intake.get_referral', 'workspace.read_file',
                'workspace.read_many', 'cm_chart.get_chart_data', 'case.retrieve_evidence'}:
            selected.append(e['id'])
    selected=list(dict.fromkeys(selected))
    handoff=stage_handoff(state,h._tool_map().values())
    state['cm_dialogue_worker']={'status':'started','role_id':'CM-04','session_id':call.arguments['session_id'],
        'owner_proposal_not_dispatched':True,'source_ids':selected,'after_model_call':state['model_calls'],
        'allowed_write':'cm_outreach.send_message','allowed_local_writes':['case.record_authorized_statements'],'stage_handoff':handoff}
    h._save(scope,state,owner,fence)
    if h.progress:h.progress('cm_dialogue_worker_started',role_id='CM-04')
    question=outreach_question(state.get('completion_contract',{}).get('public_instruction',''),
        start['id'],call.arguments['session_id'])
    from .helper_jobs import run_helper
    result=run_helper(h,scope,state,ToolCall('cm-dialogue-stage','case.request_helper',{
        'role_id':'CM-04','question':question,'evidence_ids':selected,'tool_names':[s.name for s in specs],
        'allow_writes':True,'max_model_calls':remaining,'max_tool_calls':available_tools}),owner,fence,
        invocation='cm_dialogue_worker',stage_handoff=handoff,preparation=True,
        conversation_tools=('cm_outreach.send_message',))
    state=h.store.load_case(scope)
    state['cm_dialogue_worker'].update(status='settled',helper_id=result.get('helper_id'),result=result,
        after_model_call=state['model_calls'])
    # Owner siblings were authored before all these dialogue effects. Require
    # a new owner turn before ANY further write from that old proposal batch.
    state['conversation_observation_fence']={'tool':'CM-04 delegated outreach',
        'proposal_round':proposal_round,'delegation_only':True,'helper_id':result.get('helper_id')}
    h._save(scope,state,owner,fence)
    if h.progress:h.progress('cm_dialogue_worker_finished',role_id='CM-04',status=result['status'])
    return state,{'owner_proposal_not_dispatched':True,'creates_evidence':False,'delegated_dialogue':result,
        'instruction':'The original proposed message was not sent. The CM-04 worker conducted the delegated stage '
        'through the ordinary guarded tools. Read its ORIGINAL transcript/effect sources and take a new owner turn. '
        'Verify actual consent and remaining assigned work; do not infer consent from the helper status, '
        'replay its messages, or treat its conclusion as new clinical evidence.'}
