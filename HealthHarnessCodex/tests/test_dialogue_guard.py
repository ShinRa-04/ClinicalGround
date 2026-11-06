import json
from contextlib import closing
from unittest import TestCase

from health_harness_codex.dialogue_guard import observe, blocked
from health_harness_codex.engine import Harness
from health_harness_codex.models import ToolSpec
from health_harness_codex.store import CaseStore
from test_goal_planning import base, SCOPE, INSTRUCTION

SEND = 'cm_outreach.send_message'


class DialogueGuardTests(TestCase):
    def exchange(self, state, index, message='What would you like to discuss?', reply='Please explain.', session='s'):
        return observe(state, SEND, {'session_id':session,'message':message},
                       {'structuredContent':{'patient_response':reply}}, f'ev:{index}', 'success')

    def test_three_pairs_stop_without_turning_it_into_a_patient_choice(self):
        state={}
        self.assertFalse(self.exchange(state,1))
        self.assertFalse(self.exchange(state,1))  # Cached journal response.
        self.assertFalse(self.exchange(state,2,message=' What   would you like to discuss? '))
        self.assertTrue(self.exchange(state,3,reply=' PLEASE explain. '))
        self.assertEqual(['ev:1','ev:2','ev:3'],state['dialogue_repetition_stop']['evidence_ids'])
        self.assertFalse(state['dialogue_repetition_stop']['patient_refusal_inferred'])
        self.assertFalse(state['dialogue_repetition_stop']['patient_stop_signal_inferred'])
        self.assertIsNotNone(blocked(state,'cm_outreach.start_outreach_call'))
        self.assertIsNone(blocked(state,'cm_outreach.end_outreach_call'))
        self.assertIsNone(blocked(state,'cm_chart.get_chart_data'))
        self.assertIsNone(blocked({},SEND))

    def test_same_reply_to_different_questions_or_sessions_is_not_a_loop(self):
        state={}
        for index in range(8):
            self.assertFalse(self.exchange(state,index,message=f'Question {index}?',reply='No.'))
        for index in range(3):
            self.assertFalse(self.exchange(state,20+index,session=f'session-{index}'))
        self.assertNotIn('dialogue_repetition_stop',state)

    def test_resume_blocks_actual_send_and_replacement_session_but_allows_record_work(self):
        class Tools:
            def __init__(self):self.calls=[]
            def list_tools(self):return [ToolSpec(n,'Synthetic',{'type':'object'},effect='write' if n!= 'records.read' else 'read')
                for n in (SEND,'cm_outreach.start_outreach_call','records.read')]
            def call(self,name,args):
                self.calls.append(name)
                return {'patient_response':'Please explain.'} if name==SEND else {'ok':True}
        with closing(CaseStore(':memory:')) as store:
            state=store.open_case(SCOPE,INSTRUCTION,'CM');state.update({k:v for k,v in base().items() if k!='version'})
            tools=Tools();h=Harness(store,None,tools);owner='owner';fence=store.claim(SCOPE,owner)
            for index in range(1,4):
                state['model_calls']=index;h._save(SCOPE,state,owner,fence)
                state,fence=h._execute_calls(SCOPE,state,[{'id':str(index),'name':SEND,
                    'arguments':{'session_id':'s','message':'What would you like to discuss?'}}],h._tool_map(),owner,fence)
            self.assertEqual(3,len(tools.calls))
            state=store.load_case(SCOPE);state['model_calls']=4;h._save(SCOPE,state,owner,fence)
            calls=[{'id':n,'name':n,'arguments':{'session_id':'s','message':'Again'}}
                for n in (SEND,'cm_outreach.start_outreach_call','records.read')]
            state,fence=h._execute_calls(SCOPE,state,calls,h._tool_map(),owner,fence)
            self.assertEqual([SEND,SEND,SEND,'records.read'],tools.calls)
            self.assertEqual(4,len(store.actions(SCOPE)))
            self.assertTrue(any('conversation_stopped_for_repetition' in m.get('content','') for m in state['messages']))
            self.assertEqual('running',state['status'])
