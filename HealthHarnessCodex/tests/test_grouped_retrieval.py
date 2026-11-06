import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing

from health_harness_codex.retrieval import retrieve_evidence,field_overview
from health_harness_codex.working_set import packed,pointer,project_working_context
from health_harness_codex.context import project_context
from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope,IsolationError,ToolCall,ToolSpec,ModelReply,Limits
from health_harness_codex.store import CaseStore
from health_harness_codex.docker_bridge import DockerWorkspaceTools,_WORKSPACE_SCRIPT
from health_harness_codex.policy_grounding import record_decision,check_decision


class GroupedRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.scope=Scope('world','task','org','actor','patient','case')
        self.value={'patient':{'id':'patient'},'coverage':{'active':True},'service_request':{'code':'SYN-1'},
            'notes':'Eligibility — αβγ requires documented evidence. An exception may apply.',
            'a/b':{'~key':'Another eligibility passage.'}}
        self.source={'id':'original','scope':self.scope.to_dict(),'outcome':'success','tool':'cases.get_case',
                     'observed_result':{'structuredContent':self.value,'content':[{'type':'text','text':'Do not duplicate JSON envelope'}]}}
        self.state={'scope':self.scope.to_dict(),'evidence':[self.source]}

    def test_related_fields_and_phrases_return_together_with_exact_original_coordinates(self):
        before=copy.deepcopy(self.state)
        d=retrieve_evidence(self.state,[{'id':'original','paths':['/patient','/coverage','/service_request'],
            'queries':['eligibility','exception']}])
        entry=d['results'][0]
        self.assertEqual(3,len(entry['fields']));self.assertEqual('original',entry['id'])
        self.assertIs(entry['fields'][1]['value']['active'],True)
        self.assertFalse(d['creates_evidence'])
        self.assertTrue(entry['passages'])
        for p in entry['passages']:
            text=pointer(self.value,p['text_pointer'])
            self.assertEqual(text[p['start']:p['end']],p['text'])
        self.assertTrue(any(p['text_pointer']=='/a~1b/~0key' for p in entry['passages']))
        self.assertNotIn('JSON envelope',packed(d));self.assertEqual(before,self.state)

    def test_foreign_failed_and_fabricated_ids_reject_entire_batch_before_returning_data(self):
        for kind in ('foreign','failed','missing'):
            s=copy.deepcopy(self.state);other=copy.deepcopy(self.source);other['id']='other'
            if kind=='foreign':other['scope']={'patient':'another'}
            if kind=='failed':other['outcome']='failure'
            if kind!='missing':s['evidence'].append(other)
            with self.subTest(kind=kind),self.assertRaises(IsolationError):
                retrieve_evidence(s,[{'id':'original'},{'id':'other'}])

    def test_partial_results_and_missing_fields_are_explicit_and_output_is_bounded(self):
        self.value['notes']='eligibility '*10000
        d=retrieve_evidence(self.state,[{'id':'original','paths':['/unknown'],'queries':['eligibility'],
            'max_passages':1}],max_chars=4000)
        self.assertLessEqual(len(packed(d)),4000)
        entry=d['results'][0]
        self.assertIn('error',entry['fields'][0]);self.assertTrue(entry['search_partial'])
        self.assertIn('eligibility',entry['unprocessed_queries'])
        # Each oversized request remains bounded and source-addressed.
        requests=[{'id':'original','paths':['/notes'],'limit':4000} for _ in range(12)]
        d=retrieve_evidence(self.state,requests,max_chars=4000)
        self.assertLessEqual(len(packed(d)),4000)
        self.assertIsNotNone(d['next_request'])
        follow=retrieve_evidence(self.state,requests,max_chars=4000,request_offset=d['next_request'])
        self.assertEqual(d['next_request'],follow['results'][0]['request_index'])

    def test_overview_exposes_multiple_large_root_fields_with_continuation(self):
        value={'coverage':{'active':True},'summaries':['FIRST_NOTE '+('x'*4000),'NEXT_NOTE'],
               'forms':[{'field':'required'}]*100,'other':'x'*20000}
        d=field_overview(value)
        self.assertIn('FIRST_NOTE',packed(d));self.assertIn('/coverage',packed(d))
        self.assertIn('/forms',packed(d));self.assertIn('omitted_fields',d)
        self.assertLessEqual(len(packed(d)),4500)
        giant={('field'+'x'*900+str(i)):'y'*10000 for i in range(30)}
        self.assertLessEqual(len(packed(field_overview(giant,1800))),1800)

    def test_search_continuation_reaches_later_passages_without_repeating_first_hit(self):
        self.value['notes']='First eligibility '+('x'*1000)+' Later eligibility '+('y'*1000)+' Final eligibility'
        req={'id':'original','queries':['eligibility'],'max_passages':1}
        first=retrieve_evidence(self.state,[req])['results'][0]
        self.assertIsNotNone(first['next_match'])
        second=retrieve_evidence(self.state,[{**req,'search_offset':first['next_match']}])['results'][0]
        self.assertNotEqual(first['passages'][0]['start'],second['passages'][0]['start'])
        self.assertIn('Later eligibility',second['passages'][0]['text'])

    def test_grouped_passages_survive_context_projection_without_becoming_new_evidence(self):
        d=retrieve_evidence(self.state,[{'id':'original','paths':['/coverage'],'queries':['eligibility']}])
        state={**self.state,'completion_contract':{'domain':'pa_provider'},'obligations':[],'domain':'PA'}
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'task'},
            {'role':'tool','name':'case.retrieve_evidence','content':packed(d)}]
        messages.extend({'role':'user','content':str(i)} for i in range(15))
        before=copy.deepcopy(state)
        output=project_context(messages,state,[],100000)
        self.assertIn('retained_source_readouts',output[0]['content'])
        self.assertIn('Eligibility',output[0]['content']);self.assertEqual(before,state)

    def test_engine_can_retrieve_three_fields_in_one_local_operation_without_helper_model(self):
        parent=self
        class Tools:
            def list_tools(self):return [ToolSpec('records.read','Read record',{'type':'object'},effect='read')]
            def call(self,*args):return parent.source['observed_result']
        replies=[ModelReply(tool_calls=(ToolCall('source','records.read',{}),)),
            ModelReply(tool_calls=(ToolCall('batch','case.retrieve_evidence',{'requests':[
                {'id':'ev:m1:source','paths':['/patient','/coverage','/service_request']}]}),)),
            ModelReply(content='{"status":"incomplete","claim":"Software test only","evidence_ids":[]}')]
        captured=[]
        class Model:
            def complete(self,messages,*args,**kwargs):captured.append(copy.deepcopy(messages));return replies.pop(0)
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(),Tools(),limits=Limits(max_model_calls=3)).run(self.scope,'Synthetic task','PA')
            self.assertEqual(3,result['model_calls']);self.assertEqual(1,len(result['evidence']))
            self.assertEqual(2,result['tool_calls'])
            batch=next(m for m in captured[-1] if m.get('name')=='case.retrieve_evidence')
            self.assertEqual(3,len(json.loads(batch['content'])['results'][0]['fields']))


class WorkspaceBatchTests(unittest.TestCase):
    def setUp(self):self.scope=Scope('world','task','org','actor','patient','case')

    def test_actual_workspace_program_still_enforces_reference_and_hidden_boundaries_in_batch(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);owned=base/'owned';refs=base/'refs';foreign=base/'foreign'
            for p in (owned,refs,foreign):p.mkdir()
            for p,text in [(refs/'policy.md','Approved policy text '*300),(refs/'expectations.json','HIDDEN_SENTINEL'),
                           (foreign/'chart.txt','FOREIGN_SENTINEL')]:p.write_text(text,encoding='utf-8')
            class Executor:
                def python_json(self,script,data,**kwargs):
                    data={**data,'case_root':str(owned),'read_roots':[str(refs)]}
                    p=subprocess.run([sys.executable,'-X','utf8','-c',script],input=json.dumps(data),
                        text=True,capture_output=True,timeout=10)
                    if p.returncode:raise RuntimeError('reader boundary rejection')
                    return json.loads(p.stdout)
            tools=DockerWorkspaceTools('owned','/logs/workspaces',self.scope,executor=Executor())
            result=tools.call('workspace.read_many',{'requests':[
                {'operation':'read_file','arguments':{'path':str(refs/'policy.md')}},
                {'operation':'read_file','arguments':{'path':str(refs/'expectations.json')}},
                {'operation':'read_file','arguments':{'path':str(foreign/'chart.txt')}}],'max_chars':4000})
            self.assertLessEqual(len(packed(result)),4000)
            self.assertIn('Approved policy',result['items'][0]['result']['text'])
            self.assertTrue(result['items'][0]['result']['has_more'])
            self.assertNotIn('HIDDEN_SENTINEL',packed(result));self.assertNotIn('FOREIGN_SENTINEL',packed(result))
            for i in (1,2):self.assertIn('error',result['items'][i]['result'])
            with self.assertRaises(ValueError):tools.call('workspace.read_many',{'requests':[
                {'operation':'write_file','arguments':{'path':'x','content':'forbidden'}}]})

    def test_policy_citation_uses_original_batch_id_and_child_text_pointer(self):
        source={'id':'batch','scope':self.scope.to_dict(),'outcome':'success','tool':'workspace.read_many',
            'observed_result':{'items':[{'operation':'read_file','result':{
                'path':'/workspace/skills/managed-care-operations-handbook/references/medical-library/medical-policies/synthetic.md',
                'text':'Synthetic criteria and their qualifying exception.'}}]}}
        case={'id':'case','scope':self.scope.to_dict(),'outcome':'success','tool':'cases.get_case','observed_result':{}}
        state={'scope':self.scope.to_dict(),'policy_grounding_required':True,'evidence':[source,case]}
        args={'policy_name':'Synthetic','applicability':'Synthetic scope','policy_sources':[
            {'evidence_id':'batch','text_pointer':'/items/0/result/text'}],'case_evidence_ids':['case'],
            'assessment':'Compare facts','unresolved_questions':[],'decision':'Model decision',
            'applies_to':['auth.submit_authorization']}
        record_decision(state,args,{'auth.submit_authorization'},self.scope.to_dict())
        self.assertIsNone(check_decision(state,'auth.submit_authorization',{},self.scope.to_dict()))
        for op in ('search_files','write_file'):
            other=copy.deepcopy(state);other['evidence'][0]['observed_result']['items'][0]['operation']=op
            with self.subTest(op=op),self.assertRaises(ValueError):record_decision(other,args,{'auth.submit_authorization'},self.scope.to_dict())


if __name__=='__main__':unittest.main()
