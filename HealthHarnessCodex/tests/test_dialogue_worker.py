import json
from contextlib import closing
from unittest import TestCase

from health_harness_codex.engine import Harness
from health_harness_codex.models import ModelReply,ToolCall,ToolSpec,UnknownOutcomeError
from health_harness_codex.store import CaseStore
from health_harness_codex.dialogue_worker import before_send, stage_handoff
from test_goal_planning import base,ev,SCOPE,INSTRUCTION

SEND='cm_outreach.send_message'
TRANSCRIPT='cm_outreach.get_transcript'


class Tools:
    def __init__(self,unknown=False):self.calls=[];self.unknown=unknown
    def list_tools(self):return [ToolSpec(n,'Synthetic',{'type':'object'},effect=effect) for n,effect in
        [(SEND,'write'),(TRANSCRIPT,'read'),('records.save','write')]]
    def call(self,name,args):
        self.calls.append((name,args))
        if name==SEND:
            if self.unknown:raise UnknownOutcomeError('Synthetic uncertain dialogue')
            return {'patient_response':'No thank you. Goodbye.','session_status':'ended','case_id':'case'}
        return {'case_id':'case','session_id':'s','status':'ended' if len(self.calls)>1 else 'active','messages':[]}


class Model:
    def __init__(self):self.calls=0;self.allowed=[]
    def complete(self,messages,tools,**kwargs):
        self.allowed.append([t.name for t in tools])
        if len(tools)==1 and tools[0].name=='case.record_authorized_statements':
            return ModelReply(tool_calls=[ToolCall('prepare',tools[0].name,{'statements':[]})])
        self.calls+=1
        if self.calls==1:return ModelReply(tool_calls=[ToolCall('read',TRANSCRIPT,{'session_id':'s'})])
        if self.calls==2:return ModelReply(tool_calls=[ToolCall('send',SEND,{'session_id':'s','message':'What support would matter to you?',
                                                                         'conversation_move':'ask_priority'})])
        if self.calls==3:return ModelReply(tool_calls=[ToolCall('read-final',TRANSCRIPT,{'session_id':'s'})])
        observed=json.loads(next(m['content'] for m in reversed(messages) if m.get('role')=='tool'))
        return ModelReply(content=json.dumps({'status':'complete','conclusion':'Observed conversation ended; no enrollment claimed.',
            'evidence_ids':[observed['evidence_id']],'open_questions':[]}))


def seed(store):
    s=store.open_case(SCOPE,INSTRUCTION,'CM');s.update({k:v for k,v in base().items() if k!='version'})
    ev(s,'cm_outreach.start_outreach_call',{'session_id':'s','case_id':'case','status':'active'})
    return s


class DialogueWorkerTests(TestCase):
    def test_team_handoff_is_small_scoped_metadata_not_a_full_chart(self):
        s=base()
        ev(s,'cm_intake.open_case',{'private_long_record':'x'*12000})
        original=ev(s,'cm_chart.submit_chart_review',{'private_long_record':'x'*12000})
        foreign=ev(s,'cm_chart.submit_chart_review',{'foreign_private_record':'not this patient'})
        foreign['scope']={**SCOPE.to_dict(),'patient':'other-patient'}
        specs=[ToolSpec('cm_care_plan.finalize','Finalize observed plan.',{'type':'object'},effect='write'),
            ToolSpec('cm_assessment.start_assessment','Start after required consent.',{'type':'object'},effect='write'),
            ToolSpec('unrelated.send','Unrelated',{'type':'object'},effect='write')]
        brief=stage_handoff(s,specs);text=json.dumps(brief)
        self.assertFalse(brief['grants_permissions'])
        self.assertEqual({'cm_care_plan.finalize','cm_assessment.start_assessment'},
            {x['tool'] for x in brief['owner_only_tools']})
        self.assertIn(original['id'],[x['evidence_id'] for x in brief['observed_operation_receipts']])
        self.assertNotIn(foreign['id'],[x['evidence_id'] for x in brief['observed_operation_receipts']])
        self.assertNotIn('private_long_record',text);self.assertNotIn('foreign_private_record',text)
        self.assertLess(len(text),4000)

    def test_visible_owner_capability_does_not_grant_helper_execution_authority(self):
        class OwnerTools(Tools):
            def list_tools(self):
                return super().list_tools()+[ToolSpec('cm_care_plan.finalize','Finalize plan.',{'type':'object'},effect='write')]
        class Attempt:
            calls=0
            def complete(inner,messages,tools,**kwargs):
                inner.calls+=1
                brief=json.loads(messages[1]['content'])['stage_handoff']
                from health_harness_codex.cm_guidance import PROGRAM_DESCRIPTION, CAPABILITY_LIMITS
                self.assertIn(PROGRAM_DESCRIPTION,messages[0]['content'])
                self.assertIn(CAPABILITY_LIMITS,messages[0]['content'])
                self.assertNotIn(PROGRAM_DESCRIPTION,messages[1]['content'])
                self.assertNotIn(CAPABILITY_LIMITS,messages[1]['content'])
                self.assertEqual('cm_care_plan.finalize',brief['owner_only_tools'][0]['tool'])
                self.assertNotIn('cm_care_plan.finalize',[t.name for t in tools])
                if inner.calls==1:return ModelReply(tool_calls=[ToolCall('forbidden','cm_care_plan.finalize',{})])
                return ModelReply(content=json.dumps({'status':'incomplete','conclusion':'Owner retains planning.',
                    'evidence_ids':[],'open_questions':['Conversation not performed.']}))
        with closing(CaseStore(':memory:')) as store:
            state=seed(store);tools=OwnerTools();model=Attempt()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            state,result=before_send(h,SCOPE,state,ToolCall('draft',SEND,{'session_id':'s','message':'Original'}),owner,fence,'m1')
            self.assertEqual([],tools.calls)
            self.assertEqual(3,model.calls)
            self.assertEqual('incomplete',result['delegated_dialogue']['status'])

    def test_chart_handoff_exposes_original_index_without_copying_document_bodies(self):
        s=base()
        docs=[{'title':'Recorded follow-up '+str(i),'date':'2026-01-01','content':'PRIVATE_BODY_'+str(i)*1000}
            for i in range(4)]
        original=ev(s,'cm_chart.get_chart_data',{'documents':docs,'medications':[{'name':'PRIVATE_MEDICATION'}]},'read')
        foreign=ev(s,'cm_chart.get_chart_data',{'documents':[{'title':'FOREIGN_CHART','content':'FOREIGN_BODY'}]},'read')
        foreign['scope']={**SCOPE.to_dict(),'patient':'other'}
        brief=stage_handoff(s,[]);chart=brief['chart_source_index'];text=json.dumps(brief)
        self.assertEqual(original['id'],chart['evidence_id'])
        self.assertTrue(chart['metadata_only'])
        self.assertFalse(chart['document_index']['partial'])
        self.assertEqual(4,len(chart['document_index']['items']))
        self.assertEqual('/documents/3/content',chart['document_index']['items'][3]['content_path'])
        self.assertNotIn('PRIVATE_BODY',text);self.assertNotIn('PRIVATE_MEDICATION',text)
        self.assertNotIn('FOREIGN_CHART',text)
        self.assertLess(len(text),4000)

    def test_chart_index_marks_omitted_metadata_instead_of_claiming_complete_coverage(self):
        s=base()
        ev(s,'cm_chart.get_chart_data',{'documents':[{'title':'Document '+str(i),'content':'PRIVATE'} for i in range(100)]},'read')
        chart=stage_handoff(s,[])['chart_source_index']
        self.assertEqual(100,chart['document_index']['total_items'])
        self.assertTrue(chart['document_index']['partial'])
        self.assertLess(len(chart['document_index']['items']),100)

    def test_real_helper_dispatch_is_scoped_and_old_owner_sibling_cannot_write(self):
        with closing(CaseStore(':memory:')) as store:
            state=seed(store);model=Model();tools=Tools()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            calls=[{'id':'draft','journal_id':'m1:draft','name':SEND,'arguments':{'session_id':'s','message':'Original owner draft'}},
                {'id':'stale','journal_id':'m1:stale','name':'records.save','arguments':{'consent_obtained':True}}]
            state,fence=h._execute_calls(SCOPE,state,calls,h._tool_map(),owner,fence)
            self.assertEqual([TRANSCRIPT,SEND,TRANSCRIPT],[n for n,a in tools.calls])
            self.assertNotIn('Original owner draft',[a.get('message') for n,a in tools.calls])
            self.assertTrue(all('records.save' not in names for names in model.allowed))
            self.assertTrue(all('case.request_helper' not in names for names in model.allowed))
            self.assertEqual('settled',state['cm_dialogue_worker']['status'])
            self.assertEqual(1,len(state['helper_jobs']))
            self.assertLessEqual(len(state['helper_jobs'][0]['question']),3000)
            self.assertEqual(4,model.calls)
            self.assertEqual([],state['authorized_statements'])
            self.assertEqual(5,state['helper_jobs'][0]['model_calls'])
            self.assertEqual(['case.record_authorized_statements'],model.allowed[0])
            self.assertIn('owner_proposal_not_dispatched',next(m['content'] for m in state['messages'] if m.get('tool_call_id')=='draft'))
            self.assertTrue(any('conversation_response_must_be_observed_first' in m.get('content','') for m in state['messages']))
            self.assertFalse(state.get('completion'))
            state['model_calls']+=1;h._save(SCOPE,state,owner,fence)
            state,fence=h._execute_calls(SCOPE,state,[{'id':'new-owner','name':'records.save','arguments':{'note':'Actual observed outcome'}}],h._tool_map(),owner,fence)
            self.assertEqual('records.save',tools.calls[-1][0])

    def test_preparation_receives_earlier_policy_reads_and_chart_not_foreign_sources(self):
        from health_harness_codex.authorized_statements import NAME
        class Inspect:
            calls=0
            def complete(inner,messages,tools,**kwargs):
                inner.calls+=1
                packet=json.loads(messages[1]['content'])
                if inner.calls==1:
                    self.assertEqual([NAME],[s.name for s in tools])
                    observed={e['id'] for e in packet['observations']}
                    self.assertTrue(required.issubset(observed))
                    self.assertNotIn(foreign['id'],observed)
                    return ModelReply(tool_calls=[ToolCall('prepare',NAME,{'statements':[]})])
                self.assertIn('actor_source_linked_preparation_not_policy',messages[0]['content'])
                return ModelReply(content=json.dumps({'status':'incomplete','conclusion':'Synthetic stop.',
                    'evidence_ids':[],'open_questions':[]}))
        with closing(CaseStore(':memory:')) as store:
            state=seed(store)
            required={ev(state,name,{'text':'Synthetic source'},'read')['id'] for name in (
                'workspace.read_file','workspace.read_file','workspace.read_many','cm_chart.get_chart_data')}
            foreign=ev(state,'workspace.read_file',{'text':'Foreign source'},'read')
            foreign['scope']={**SCOPE.to_dict(),'patient':'other'}
            model=Inspect(); tools=Tools()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner'; fence=store.claim(SCOPE,owner); h._save(SCOPE,state,owner,fence)
            state,result=before_send(h,SCOPE,state,ToolCall('draft',SEND,{'session_id':'s','message':'Synthetic draft'}),owner,fence,'m1')
            self.assertTrue(state['helper_jobs'][0]['preparation'])
            self.assertLessEqual(len(state['helper_jobs'][0]['question']),3000)
            self.assertEqual([],tools.calls)

    def test_uncertain_delegated_write_is_not_restarted(self):
        with closing(CaseStore(':memory:')) as store:
            state=seed(store);tools=Tools(unknown=True);model=Model()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            call=ToolCall('draft',SEND,{'session_id':'s','message':'Original'})
            with self.assertRaises(UnknownOutcomeError):before_send(h,SCOPE,state,call,owner,fence,'m1')
            resumed=store.load_case(SCOPE)
            resumed,result=before_send(h,SCOPE,resumed,call,owner,fence,'m2')
            self.assertTrue(result['delegated_effects_may_exist'])
            self.assertEqual(2,model.calls)
            self.assertEqual(1,len(resumed['helper_jobs']))

    def test_combined_mode_and_other_domains_keep_original_owner_path(self):
        for composition,domain in [('combined','cm'),('helpers','pa_um')]:
            with self.subTest(composition=composition,domain=domain),closing(CaseStore(':memory:')) as store:
                state=seed(store);state['completion_contract']['domain']=domain
                h=Harness(store,None,Tools(),composition=composition,recovery_helper_policy='auto')
                original=ToolCall('draft',SEND,{'session_id':'s','message':'Original'})
                state,result=before_send(h,SCOPE,state,original,'unused',1,'m1')
                self.assertIsNone(result);self.assertNotIn('cm_dialogue_worker',state)


class CloseFirstModel:
    """Tries to end contact before inviting a decision, then complies."""
    def __init__(self):self.calls=0;self.feedback=[]
    def complete(self,messages,tools,**kwargs):
        if len(tools)==1 and tools[0].name=='case.record_authorized_statements':
            return ModelReply(tool_calls=[ToolCall('prepare',tools[0].name,{'statements':[]})])
        send=next(t for t in tools if t.name==SEND)
        assert 'conversation_move' in send.input_schema['required']
        self.calls+=1
        self.feedback=[m['content'] for m in messages if 'close_before_decision_invitation' in str(m.get('content',''))]
        if self.calls==1:return ModelReply(tool_calls=[ToolCall('close',SEND,{'session_id':'s','message':'Anything else, or stop here?',
                                                                              'conversation_move':'close'})])
        if self.calls==2:return ModelReply(tool_calls=[ToolCall('invite',SEND,{'session_id':'s','message':'Would you like to enroll?',
                                                                               'conversation_move':'invite_decision'})])
        return ModelReply(content=json.dumps({'status':'complete','conclusion':'Invitation made; reply observed.',
            'evidence_ids':[],'open_questions':[]}))


class ConversationMoveTests(TestCase):
    def test_close_before_invitation_is_deferred_once_and_field_never_dispatches(self):
        with closing(CaseStore(':memory:')) as store:
            state=seed(store);tools=Tools();model=CloseFirstModel()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            state,result=before_send(h,SCOPE,state,ToolCall('draft',SEND,{'session_id':'s','message':'Original'}),owner,fence,'m1')
            sent=[a for n,a in tools.calls if n==SEND]
            self.assertEqual(['Would you like to enroll?'],[a['message'] for a in sent])
            self.assertTrue(all('conversation_move' not in a for a in sent))
            self.assertEqual(1,len(model.feedback))
            job=state['helper_jobs'][0]
            self.assertEqual(['invite_decision'],job['conversation_moves'])
            self.assertTrue(job['close_feedback_given'])

    def test_gate_never_blocks_twice_or_after_a_declared_decline(self):
        from health_harness_codex.helper_jobs import _conversation_gate
        job={}
        self.assertIsNotNone(_conversation_gate(job,ToolCall('a',SEND,{'conversation_move':'close'})))
        self.assertIsNone(_conversation_gate(job,ToolCall('b',SEND,{'conversation_move':'close'})))
        job={}
        self.assertIsNone(_conversation_gate(job,ToolCall('c',SEND,{'conversation_move':'respect_decline'})))
        self.assertIsNone(_conversation_gate(job,ToolCall('d',SEND,{'conversation_move':'close'})))

    def test_return_with_open_contact_is_held_once_after_an_invitation_never_after_decline(self):
        from health_harness_codex.helper_jobs import _return_gate
        self.assertIsNone(_return_gate({'conversation_moves':['ask_priority']}))
        self.assertIsNone(_return_gate({'conversation_moves':['invite_decision','respect_decline']}))
        job={'conversation_moves':['invite_decision','confirm_consent','close']}
        self.assertEqual('contact_still_open',_return_gate(job)['reason'])
        self.assertIsNone(_return_gate(job))

    def test_closing_offer_after_consent_is_held_once_by_the_same_reminder(self):
        from health_harness_codex.helper_jobs import _conversation_gate
        job={'conversation_moves':['invite_decision','confirm_consent']}
        held=_conversation_gate(job,ToolCall('a',SEND,{'conversation_move':'close'}))
        self.assertEqual(('message_not_sent','contact_still_open'),(held['error'],held['reason']))
        self.assertIsNone(_conversation_gate(job,ToolCall('b',SEND,{'conversation_move':'close'})))
        self.assertIsNone(_conversation_gate({'conversation_moves':['invite_decision','respect_decline']},
                                             ToolCall('c',SEND,{'conversation_move':'close'})))

    def test_open_contact_return_hold_reaches_the_worker_once(self):
        class OpenTools(Tools):
            def call(inner,name,args):
                result=super().call(name,args)
                return {**result,'session_status':'active'} if name==SEND else result
        with closing(CaseStore(':memory:')) as store:
            state=seed(store);tools=OpenTools();model=CloseFirstModel()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            state,result=before_send(h,SCOPE,state,ToolCall('draft',SEND,{'session_id':'s','message':'Original'}),owner,fence,'m1')
            job=state['helper_jobs'][0]
            self.assertTrue(job['return_feedback_given'])
            self.assertEqual(4,model.calls)
            self.assertEqual('complete',result['delegated_dialogue']['status'])
            self.assertEqual(1,len([a for n,a in tools.calls if n==SEND]))


class SendAfterEndModel:
    """Invites a decision (the synthetic contact ends), tries to keep talking, then returns."""
    def __init__(self):self.calls=0;self.feedback=[]
    def complete(self,messages,tools,**kwargs):
        if len(tools)==1 and tools[0].name=='case.record_authorized_statements':
            return ModelReply(tool_calls=[ToolCall('prepare',tools[0].name,{'statements':[]})])
        self.calls+=1
        self.feedback=[m['content'] for m in messages if 'contact_ended' in str(m.get('content',''))
                       or 'contact_still_open' in str(m.get('content',''))]
        if self.calls==1:return ModelReply(tool_calls=[ToolCall('invite',SEND,{'session_id':'s','message':'Would you like to enroll?',
                                                                              'conversation_move':'invite_decision'})])
        if self.calls==2:return ModelReply(tool_calls=[ToolCall('more',SEND,{'session_id':'s','message':'One more question.',
                                                                            'conversation_move':'answer'})])
        return ModelReply(content=json.dumps({'status':'complete','conclusion':'Contact ended after the invitation.',
            'evidence_ids':[],'open_questions':[]}))


class EndedContactTests(TestCase):
    def test_no_send_and_no_open_contact_hold_after_observed_end(self):
        with closing(CaseStore(':memory:')) as store:
            state=seed(store);tools=Tools();model=SendAfterEndModel()
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            state,result=before_send(h,SCOPE,state,ToolCall('draft',SEND,{'session_id':'s','message':'Original'}),owner,fence,'m1')
            self.assertEqual(['Would you like to enroll?'],[a['message'] for n,a in tools.calls if n==SEND])
            job=state['helper_jobs'][0]
            self.assertTrue(job['contact_ended'])
            self.assertFalse(job.get('return_feedback_given'))
            self.assertEqual(1,len(model.feedback));self.assertIn('contact_ended',model.feedback[0])
            self.assertEqual('complete',result['delegated_dialogue']['status'])
            self.assertEqual('running',state['status'])


NEEDS=[{'need':'Synthetic instrument A items','source_evidence_id':'ev:0'},
       {'need':'Synthetic instrument B items','source_evidence_id':'ev:0'},
       {'need':'Synthetic detail C','source_evidence_id':'ev:0'}]


def _send(move,covers=None,updates=None):
    args={'session_id':'s','message':'Synthetic','conversation_move':move}
    if covers is not None:args['covers_needs']=covers
    if updates is not None:args['need_status_updates']=updates
    return ToolCall('x',SEND,args)


class InformationNeedOrderTests(TestCase):
    def test_lower_ranked_need_is_held_once_while_higher_ranked_need_is_open(self):
        from health_harness_codex.helper_jobs import _conversation_gate
        job={'conversation_moves':['invite_decision','confirm_consent']}
        call=_send('gather_information',[3])
        held=_conversation_gate(job,call,NEEDS)
        self.assertEqual('higher_ranked_needs_unasked',held['reason'])
        self.assertEqual([1,2],[n['number'] for n in held['open_information_needs']])
        self.assertNotIn('covers_needs',call.arguments);self.assertNotIn('conversation_move',call.arguments)
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[3]),NEEDS))

    def test_settled_higher_needs_and_exempt_moves_pass(self):
        from health_harness_codex.helper_jobs import _conversation_gate
        job={'conversation_moves':['confirm_consent']}
        updates=[{'need':1,'status':'declined'},{'need':2,'status':'answered'}]
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[3],updates),NEEDS))
        job={'conversation_moves':['confirm_consent']}
        self.assertIsNone(_conversation_gate(job,_send('answer',[3]),NEEDS))
        self.assertIsNone(_conversation_gate({'conversation_moves':['ask_priority']},_send('ask_priority',[3]),NEEDS))
        self.assertIsNone(_conversation_gate({'conversation_moves':['confirm_consent']},_send('gather_information',[1,2]),NEEDS))

    def test_missing_covers_is_asked_once_and_partial_stays_open(self):
        from health_harness_codex.helper_jobs import _conversation_gate,_open_needs
        job={'conversation_moves':['confirm_consent']}
        self.assertEqual('covers_needs_missing',_conversation_gate(job,_send('gather_information'),NEEDS)['reason'])
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[]),NEEDS))
        _conversation_gate(job,_send('gather_information',[1],[{'need':1,'status':'partial'},{'need':9,'status':'answered'}]),NEEDS)
        self.assertEqual([1,2,3],[i for i,_ in _open_needs(job,NEEDS)])

    def test_open_contact_hold_lists_open_needs_and_contact_note_reports_turns(self):
        from health_harness_codex.helper_jobs import _return_gate,_contact_note
        job={'id':'h','conversation_moves':['confirm_consent'],'need_status':{NEEDS[0]['need']:'answered'}}
        held=_return_gate(job,NEEDS)
        self.assertEqual([2,3],[n['number'] for n in held['open_information_needs']])
        state={'evidence':[{'helper_job_id':'h','outcome':'success','observed_result':{'turn_number':6,'session_status':'active'}}]}
        note=_contact_note(state,job,NEEDS)
        self.assertIn('turn_number 6',note);self.assertIn('undisclosed',note);self.assertIn('2. [not yet asked] Synthetic instrument B',note)
        self.assertNotIn('1. Synthetic instrument A',note)
        self.assertEqual('',_contact_note({'evidence':[]},{'id':'h'},[]))


class SkipAheadModel:
    """After consent asks a lower-ranked need first, is held, then asks the ranked needs."""
    def __init__(self,source_id):self.calls=0;self.notes=[];self.source_id=source_id
    def complete(self,messages,tools,**kwargs):
        if len(tools)==1 and tools[0].name=='case.record_authorized_statements':
            needs=[{**n,'source_evidence_id':self.source_id} for n in NEEDS]
            return ModelReply(tool_calls=[ToolCall('prepare',tools[0].name,{'statements':[],'information_needs':needs})])
        self.calls+=1
        self.notes.append(messages[-1]['content'])
        plan={1:('Would you like to enroll?','invite_decision',None),2:('Do you consent?','confirm_consent',None),
              3:('Detail C?','gather_information',[3]),4:('Instrument A and B items?','gather_information',[1,2])}
        if self.calls in plan:
            text,move,covers=plan[self.calls]
            args={'session_id':'s','message':text,'conversation_move':move}
            if covers:args['covers_needs']=covers
            return ModelReply(tool_calls=[ToolCall(f'c{self.calls}',SEND,args)])
        return ModelReply(content=json.dumps({'status':'complete','conclusion':'Synthetic.','evidence_ids':[],'open_questions':[]}))


class NeedOrderIntegrationTests(TestCase):
    def test_held_message_never_dispatches_and_worker_fields_are_stripped(self):
        class OpenTools(Tools):
            def call(inner,name,args):
                result=super().call(name,args)
                return {**result,'session_status':'active','turn_number':2*len([n for n,_ in inner.calls if n==SEND])} if name==SEND else result
        with closing(CaseStore(':memory:')) as store:
            state=seed(store)
            tools=OpenTools();model=SkipAheadModel(state['evidence'][-1]['id'])
            h=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,state,owner,fence)
            before_send(h,SCOPE,state,ToolCall('draft',SEND,{'session_id':'s','message':'Original'}),owner,fence,'m1')
            sent=[a for n,a in tools.calls if n==SEND]
            self.assertEqual(['Would you like to enroll?','Do you consent?','Instrument A and B items?'],[a['message'] for a in sent])
            self.assertTrue(all(set(a)=={'session_id','message'} for a in sent))
            self.assertTrue(any('turn_number 4' in n for n in model.notes))


class BreadthFirstNeedTests(TestCase):
    def test_partly_answered_higher_need_does_not_block_moving_on(self):
        from health_harness_codex.helper_jobs import _conversation_gate
        job={'conversation_moves':['confirm_consent']}
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[1]),NEEDS))
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[2],[{'need':1,'status':'partial'}]),NEEDS))
        self.assertEqual([NEEDS[0]['need'],NEEDS[1]['need']],job['needs_asked'])

    def test_follow_up_detail_is_held_once_while_a_need_was_never_asked(self):
        from health_harness_codex.helper_jobs import _conversation_gate,_contact_note
        job={'id':'h','conversation_moves':['confirm_consent']}
        _conversation_gate(job,_send('gather_information',[1,2]),NEEDS)
        held=_conversation_gate(job,_send('gather_information',[1],[{'need':1,'status':'partial'}]),NEEDS)
        self.assertEqual('unasked_needs_remain',held['reason'])
        self.assertEqual([3],[n['number'] for n in held['open_information_needs']])
        self.assertIn('[not yet asked] Synthetic detail C',_contact_note({'evidence':[]},job,NEEDS))
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[1]),NEEDS))
        self.assertIsNone(_conversation_gate(job,_send('gather_information',[3]),NEEDS))


class ReplayDerivedTests(TestCase):
    """Cases taken from saved runs sonnetpatient-02..12 (synthetic text, real shapes)."""

    def test_real_length_needs_are_accepted(self):
        # Real preparations used needs of 230-300 characters; a 200 cap rejected most of them.
        from health_harness_codex.authorized_statements import record
        from test_authorized_statements import state, arguments
        for size, ok in ((300, True), (400, True), (401, False)):
            s = state(); a = arguments(); a['information_needs'] = [{'need': 'x' * size, 'source_evidence_id': 'ev:0'}]
            if ok: self.assertEqual(1, record(s, a)['information_needs'])
            else:
                with self.assertRaises(ValueError): record(s, a)

    def test_invitation_alone_does_not_start_need_checks_but_gathering_does(self):
        # -12 went from invite_decision straight to gather_information without confirm_consent.
        from health_harness_codex.helper_jobs import _conversation_gate
        self.assertIsNone(_conversation_gate({'conversation_moves': ['invite_decision']}, _send('ask_priority'), NEEDS))
        job = {'conversation_moves': ['invite_decision', 'invite_decision']}
        self.assertEqual('higher_ranked_needs_unasked', _conversation_gate(job, _send('gather_information', [3]), NEEDS)['reason'])
        self.assertEqual([{'move': 'gather_information', 'covers_needs': [3], 'held': 'higher_ranked_needs_unasked'}],
                         job['conversation_log'])

    def test_mistyped_final_citation_keeps_the_worker_result(self):
        # -02/-07/-09/-10: a mistyped ID in the final answer discarded everything the worker learned.
        class TypoFinal(Model):
            def complete(inner, messages, tools, **kwargs):
                reply = super().complete(messages, tools, **kwargs)
                if reply.content and not reply.tool_calls:
                    final = json.loads(reply.content); final['evidence_ids'] = [*final['evidence_ids'], 'ev:m9:req_typo_1']
                    return ModelReply(content=json.dumps(final))
                return reply
        with closing(CaseStore(':memory:')) as store:
            state = seed(store); model = TypoFinal(); tools = Tools()
            h = Harness(store, model, tools, composition='helpers', recovery_helper_policy='auto')
            owner = 'owner'; fence = store.claim(SCOPE, owner); h._save(SCOPE, state, owner, fence)
            state, result = before_send(h, SCOPE, state, ToolCall('draft', SEND, {'session_id': 's', 'message': 'Original'}), owner, fence, 'm1')
            dialogue = result['delegated_dialogue']
            self.assertEqual('complete', dialogue['status'])
            self.assertIn('no enrollment claimed', dialogue['conclusion'])
            self.assertEqual(['ev:m9:req_typo_1'], dialogue['dropped_unreturned_evidence_ids'])
            self.assertNotIn('ev:m9:req_typo_1', dialogue['evidence_ids'])

    def test_owner_send_to_an_observed_ended_session_is_refused_before_dispatch(self):
        # -04/-07: a write error on an ended session became an unknown outcome and blocked the run.
        with closing(CaseStore(':memory:')) as store:
            state = seed(store)
            ev(state, TRANSCRIPT, {'session_id': 's', 'case_id': 'case', 'status': 'ended', 'messages': []}, 'read')
            tools = Tools(); h = Harness(store, None, tools, composition='combined', recovery_helper_policy='auto')
            state, result = before_send(h, SCOPE, state, ToolCall('late', SEND, {'session_id': 's', 'message': 'One more'}), 'o', 1, 'm9')
            self.assertEqual('contact_ended', result['reason']); self.assertTrue(result['known_not_dispatched'])
            self.assertEqual([], tools.calls)
            state, result = before_send(h, SCOPE, state, ToolCall('other', SEND, {'session_id': 'other', 'message': 'Hi'}), 'o', 1, 'm9')
            self.assertIsNone(result)
