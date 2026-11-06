import copy
import json
import unittest
from contextlib import closing

from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope,ToolCall,ToolSpec,ModelReply,IsolationError
from health_harness_codex.store import CaseStore
from health_harness_codex.prepared_actions import resolve
from health_harness_codex.tools import _tool_alias
from health_harness_codex.helper_jobs import observed_resource_handles,run_helper

SCOPE=Scope('synthetic','prepared','org','actor','patient','case')
OP='cm_intake.disenroll_case'
ALIAS=_tool_alias('synthetic-server',OP)


class Tools:
    def __init__(self):self.calls=[]
    def list_tools(self):return [ToolSpec(ALIAS,'Synthetic terminal write',
        {'type':'object','required':['case_id','reason'],'additionalProperties':False,
         'properties':{'case_id':{'type':'string'},'reason':{'type':'string'}}},effect='write')]
    def call(self,name,args):self.calls.append((name,copy.deepcopy(args)));return {'case_id':'case','status':'disenrolled'}


def prepared_state(store):
    s=store.open_case(SCOPE,'Synthetic prepared-action task.','CM')
    s.update(status='running',composition='helpers',model_calls=1)
    s['policy_decisions']=[{'id':'policy-decision:1','scope':SCOPE.to_dict(),'actual_scope':SCOPE.to_dict(),
        'provenance_verified':True,'applies_to':[OP],
        'bound_arguments':{OP:{'case_id':'case','reason':'Exact owner-authored prepared reason.'}}}]
    return s


class PreparedActionTests(unittest.TestCase):
    def test_actual_mcp_alias_receives_exact_bound_payload_and_repeat_is_not_dispatched(self):
        with closing(CaseStore(':memory:')) as store:
            s=prepared_state(store);tools=Tools();h=Harness(store,None,tools)
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,s,owner,fence)
            refs={'record_id':'policy-decision:1','operation':OP}
            for n in (1,2):
                s['model_calls']=n;h._save(SCOPE,s,owner,fence)
                request={'id':f'commit-{n}','journal_id':f'm{n}:commit-{n}',
                    'name':'case.execute_recorded_action','arguments':refs}
                s,fence=h._execute_calls(SCOPE,s,[request],h._tool_map(),owner,fence)
            self.assertEqual([(ALIAS,s['policy_decisions'][0]['bound_arguments'][OP])],tools.calls)
            self.assertEqual(1,len(store.actions(SCOPE)))
            self.assertTrue(store.actions(SCOPE)[0]['id'].startswith('prepared:'))
            self.assertEqual(1,len(s['evidence']))
            self.assertEqual(ALIAS,s['evidence'][0]['tool'])
            self.assertTrue(all(m['tool_call_id'].startswith('commit-') for m in s['messages'] if m.get('role')=='tool'))

    def test_wrong_scope_invalid_payload_and_helper_permission_cannot_be_bypassed(self):
        for defect in ('scope','payload','permission'):
            with self.subTest(defect=defect),closing(CaseStore(':memory:')) as store:
                s=prepared_state(store);h=Harness(store,None,Tools())
                if defect=='scope':s['policy_decisions'][0]['scope']={**SCOPE.to_dict(),'patient':'foreign'}
                if defect=='payload':s['policy_decisions'][0]['bound_arguments'][OP]['case_id']='foreign'
                if defect=='permission':
                    h._helper_channel={'id':'helper'}
                    s['helper_jobs']=[{'id':'helper','allow_writes':True,'tool_names':['case.execute_recorded_action']}]
                with self.assertRaises((ValueError,IsolationError)):
                    resolve(h,SCOPE,s,{'record_id':'policy-decision:1','operation':OP},h._tool_map())
                self.assertEqual([],store.actions(SCOPE))

    def test_resource_handles_are_exact_same_case_actor_outputs_not_draft_or_foreign_data(self):
        spec=ToolSpec('cm_outreach.get_transcript','Read transcript',{'type':'object','required':['session_id'],
                      'properties':{'session_id':{'type':'string'}}},effect='read')
        s={'scope':SCOPE.to_dict(),'evidence':[
            {'id':'ev:start','scope':SCOPE.to_dict(),'outcome':'success','tool':'cm_outreach.start_outreach_call',
             'observed_result':{'structuredContent':{'session_id':'SESSION-OBSERVED','case_id':'case'}}},
            {'id':'ev:draft','scope':SCOPE.to_dict(),'outcome':'success','tool':'workspace.write_file',
             'observed_result':{'session_id':'DRAFT-ID'}},
            {'id':'ev:foreign','scope':{**SCOPE.to_dict(),'patient':'foreign'},'outcome':'success','tool':'cm_outreach.start_outreach_call',
             'observed_result':{'session_id':'FOREIGN-ID'}}]}
        handles=observed_resource_handles(s,[spec])
        self.assertEqual(['SESSION-OBSERVED'],[i['value'] for i in handles])
        self.assertEqual('ev:start',handles[0]['evidence_id'])
        self.assertFalse(handles[0]['grants_additional_permissions'])

    def test_helper_sees_deduplicated_facts_and_session_handle_without_mutating_originals(self):
        class HelperTools:
            def list_tools(self):return [ToolSpec('cm_outreach.get_transcript','Read',
                {'type':'object','required':['session_id'],'properties':{'session_id':{'type':'string'}}},effect='read')]
        seen=[]
        class Model:
            def complete(self,messages,tools,**kw):
                seen.extend(messages)
                return ModelReply(content=json.dumps({'status':'complete','conclusion':'Source inspection only.',
                    'evidence_ids':['ev:start'],'open_questions':[]}))
        with closing(CaseStore(':memory:')) as store:
            s=store.open_case(SCOPE,'Synthetic helper input task.','CM');s.update(status='running',composition='helpers')
            body={'session_id':'SESSION-1','case_id':'case','status':'active'}
            raw={'structuredContent':body,'content':[{'type':'text','text':json.dumps(body),'parsed_json':body}],'isError':False}
            s['evidence']=[{'id':'ev:start','scope':SCOPE.to_dict(),'outcome':'success','effect':'write',
                'tool':'cm_outreach.start_outreach_call','observed_result':raw}]
            original=copy.deepcopy(raw);h=Harness(store,Model(),HelperTools(),composition='helpers')
            owner='owner';fence=store.claim(SCOPE,owner);h._save(SCOPE,s,owner,fence)
            result=run_helper(h,SCOPE,s,ToolCall('delegate','case.request_helper',{'role_id':'SH-10','question':'Inspect transcript.',
                'evidence_ids':['ev:start'],'tool_names':['cm_outreach.get_transcript'],'allow_writes':False}),owner,fence)
            prompt=json.loads(seen[1]['content'])
            self.assertNotIn('content',prompt['observations'][0]['observed_result'])
            self.assertEqual('SESSION-1',prompt['observed_resource_handles'][0]['value'])
            self.assertEqual(original,store.load_case(SCOPE)['evidence'][0]['observed_result'])
            self.assertEqual('complete',result['status'])


if __name__=='__main__':unittest.main()
