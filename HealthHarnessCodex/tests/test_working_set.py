import copy
import json
from pathlib import Path
import tempfile
import unittest

from health_harness_codex.context import project_context
from health_harness_codex.completion_contracts import build_completion_contract
from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope, ToolCall, ToolSpec, IsolationError
from health_harness_codex.roles import system_prompt
from health_harness_codex.store import CaseStore
from health_harness_codex.working_set import normalize_mcp, inspect_source, select_tools, rank_tools


class WorkingSetTests(unittest.TestCase):
    def test_disabled_context_cap_preserves_large_explicit_read_that_exhausts_finite_budget(self):
        text='Synthetic policy source text. '*5000
        result={'path':'/approved/policy.md','text':text,'has_more':False}
        messages=[{'role':'system','content':system_prompt('PA',self.scope)},
                  {'role':'user','content':'Clinical intake. Work from observed evidence.'},
                  {'role':'assistant','content':'','tool_calls':[{'id':'read','name':'workspace.read_file','arguments':{}}]},
                  {'role':'tool','tool_call_id':'read','name':'workspace.read_file','evidence_id':'ev:read',
                   'content':json.dumps({'evidence_id':'ev:read','observed_result':result})}]
        state=copy.deepcopy(self.state);state['evidence']=[{'id':'ev:read','tool':'workspace.read_file',
            'scope':self.scope.to_dict(),'outcome':'success','observed_result':result}]
        tools=[ToolSpec('synthetic.read','x'*70000,{'type':'object'},effect='read')]
        self.assertIsNone(project_context(messages,state,tools,180000))
        unlimited=project_context(messages,state,tools,0)
        self.assertIsNotNone(unlimited)
        self.assertIn(text,json.loads(unlimited[-1]['content'])['observed_result']['text'])
        self.assertEqual(result,state['evidence'][0]['observed_result'])

    def setUp(self):
        self.scope=Scope('environment','task','org','actor','patient','subject')
        self.contract=build_completion_contract('task','pa_provider','Clinical intake. Prepare the supported referral.',self.scope.to_dict())
        self.state={'scope':self.scope.to_dict(),'domain':'PA','composition':'combined',
            'completion_contract':self.contract,'evidence':[],'obligations':[]}

    def test_only_exact_mcp_duplicate_text_is_removed_without_mutating_source(self):
        value={'structuredContent':{'consent':True},'content':[{'type':'text','text':'{"consent":true}'}]}
        saved=copy.deepcopy(value)
        self.assertNotIn('content',normalize_mcp(value));self.assertEqual(saved,value)
        value['content'][0]['text']='{"consent":1}'
        self.assertEqual(value,normalize_mcp(value))
        value['content']=[{'type':'image','data':'separate-image'}]
        self.assertEqual(value,normalize_mcp(value))
        self.assertEqual('separate-image',inspect_source(value,'/content/0/data',representation='raw')['value'])

    def test_large_source_is_retrievable_without_filling_context_or_losing_provenance(self):
        messages=[{'role':'system','content':system_prompt('PA',self.scope)},
                  {'role':'user','content':'Clinical intake. Prepare the supported referral.'}]
        for i in range(30):
            result={'structuredContent':{'case':{'id':'actual','status':'draft'},'detail':'PRIVATE_SOURCE_FACT '+('x'*100_000)}}
            eid=f'ev:{i}';self.state['evidence'].append({'id':eid,'scope':self.scope.to_dict(),
                'tool':'cases.get_case','outcome':'success','observed_result':result})
            messages.extend([{'role':'assistant','content':'','tool_calls':[{'id':str(i),'name':'cases.get_case','arguments':{}}]},
                {'role':'tool','name':'cases.get_case','tool_call_id':str(i),'evidence_id':eid,
                 'content':json.dumps({'observed_result':result})}])
        original=copy.deepcopy(self.state)
        projected=project_context(messages,self.state,[],180000)
        self.assertLess(len(json.dumps(projected)),60_000)
        self.assertNotIn('x'*10_000,json.dumps(projected));self.assertIn('ev:29',json.dumps(projected))
        self.assertIn('omitted_fields',json.dumps(projected))
        self.assertEqual('PRIVATE_SOURCE_FACT',inspect_source(self.state['evidence'][-1]['observed_result'],'/detail',0,19)['value'])
        self.assertEqual(original,self.state)
        calls={x['id'] for m in projected for x in m.get('tool_calls',[])}
        results={m['tool_call_id'] for m in projected if m['role']=='tool'}
        self.assertEqual(calls,results)

    def test_typed_pointer_preserves_scalar_types_and_array_continuation(self):
        source={'structuredContent':{'a/b':{'~key':[False,1,2,3]}}}
        result=inspect_source(source,'/a~1b/~0key',1,2)
        self.assertEqual([1,2],result['value']);self.assertEqual(3,result['next_offset'])
        self.assertIs(False,inspect_source(source,'/a~1b/~0key/0')['value'])
        with self.assertRaises(KeyError):inspect_source(source,'/a~1b/~0key/100')

    def test_confirmed_field_absence_survives_history_compaction_with_source_scope(self):
        state=copy.deepcopy(self.state)
        state['evidence']=[{'id':'ev:original','scope':self.scope.to_dict(),'outcome':'success',
            'tool':'records.read','observed_result':{'documents':[]}}]
        messages=[{'role':'system','content':'Rules'},{'role':'user','content':'Task'},
            {'role':'assistant','content':'','tool_calls':[{'id':'inspect','name':'case.inspect_evidence','arguments':{}}]},
            {'role':'tool','name':'case.inspect_evidence','tool_call_id':'inspect','content':json.dumps({
                'id':'ev:original','path':'/catalog','representation':'business','error':'source_path_absent',
                'field_status':'absent_in_original_observation','available_fields':['documents']})}]
        for i in range(15):messages.append({'role':'user','content':f'Next action {i}'})
        projected=project_context(messages,state,[],0)
        self.assertIn('absent_in_original_observation',projected[0]['content'])
        self.assertIn('historical_observation_only',projected[0]['content'])
        self.assertIn('/catalog',projected[0]['content'])

    def test_explicit_source_readout_survives_many_later_turns_without_new_evidence(self):
        source={'id':'ev:original','scope':self.scope.to_dict(),'tool':'records.read','outcome':'success',
                'observed_result':{'clinical_fact':'READ_AND_RETAIN_ME'}}
        self.state['evidence']=[source]
        messages=[{'role':'system','content':'safety rules'},{'role':'user','content':'task'},
            {'role':'assistant','content':'','tool_calls':[{'id':'inspect','name':'case.inspect_evidence','arguments':{}}]},
            {'role':'tool','name':'case.inspect_evidence','tool_call_id':'inspect',
             'content':json.dumps({'id':'ev:original','path':'/clinical_fact','value':'READ_AND_RETAIN_ME','creates_evidence':False})}]
        for i in range(15):messages.append({'role':'user','content':f'Later task step {i}'})
        before=copy.deepcopy(self.state)
        projected=project_context(messages,self.state,[],100000)
        self.assertIn('READ_AND_RETAIN_ME',projected[0]['content'])
        self.assertIn('historical source fields',projected[0]['content'])
        self.assertEqual(before,self.state)

    def test_stage_presentation_can_activate_only_existing_tools(self):
        specs=[ToolSpec(n,'',{'type':'object'}) for n in ['cases.create_from_order','cases.get_case',
            'auth.submit_authorization','auth.file_appeal','case.discover_tools','workspace.read_file']]
        self.assertNotIn('auth.submit_authorization',[s.name for s in select_tools(specs,self.state)])
        self.state['case_bindings']={'case_id':'actual'}
        selected=[s.name for s in select_tools(specs,self.state)]
        self.assertIn('auth.submit_authorization',selected);self.assertNotIn('auth.file_appeal',selected)
        self.state['activated_tools']=['auth.file_appeal','nonexistent.tool']
        selected=[s.name for s in select_tools(specs,self.state)]
        self.assertIn('auth.file_appeal',selected);self.assertNotIn('nonexistent.tool',selected)

    def test_bounded_reference_text_survives_compaction_and_later_turns(self):
        text='REFERENCE_TEXT_MUST_REMAIN_READABLE '+('source text '*700)
        raw={'path':'/approved/reference.md','text':text,'offset_chars':0,'has_more':False}
        self.state['evidence']=[{'id':'ev:reference','scope':self.scope.to_dict(),'tool':'workspace.read_file',
            'outcome':'success','observed_result':raw}]
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'task'},
            {'role':'assistant','content':'','tool_calls':[{'id':'read','name':'workspace.read_file','arguments':{}}]},
            {'role':'tool','name':'workspace.read_file','tool_call_id':'read','evidence_id':'ev:reference',
             'content':json.dumps({'observed_result':raw})}]
        original=copy.deepcopy(self.state)
        projected=project_context(messages,self.state,[],100000)
        result=next(m for m in projected if m.get('tool_call_id')=='read')
        self.assertIn(text,projected[0]['content'])
        self.assertEqual('Current case working set.retained_reference_excerpts',json.loads(result['content'])['original_body_in'])
        self.assertEqual(1,json.dumps(projected,ensure_ascii=False).count(text))
        for i in range(15):messages.append({'role':'user','content':f'later turn {i}'})
        projected=project_context(messages,self.state,[],100000)
        self.assertIn(text,projected[0]['content'])
        self.assertIn('retained_reference_excerpts',projected[0]['content'])
        self.assertEqual(original,self.state)

    def test_natural_language_tool_queries_find_real_tools_without_inventing_requested_names(self):
        specs=[ToolSpec('people.list_ordering_providers','Directory of requesting practitioners with NPI.',{'type':'object'}),
               ToolSpec('cases.get_case','Read an authorization case.',{'type':'object'})]
        found=rank_tools(specs,'people get practitioner provider by id NPI')
        self.assertEqual('people.list_ordering_providers',found[0].name)
        self.assertNotIn('people.get_practitioner',[s.name for s in found])

    def test_foreign_evidence_does_not_enter_clinical_working_view(self):
        self.state['evidence']=[{'id':'foreign','scope':{'patient':'another'},'tool':'cases.get_case',
            'outcome':'success','observed_result':{'secret':'FOREIGN_CASE_MARKER'}}]
        text=json.dumps(project_context([{'role':'system','content':'rules'}, {'role':'user','content':'task'}],self.state,[],10000))
        self.assertNotIn('FOREIGN_CASE_MARKER',text);self.assertNotIn('foreign',text)

    def test_engine_inspection_rejects_other_case_and_discovery_is_not_dispatch(self):
        class Tools:
            def list_tools(self):return [ToolSpec('auth.file_appeal','appeal',{'type':'object'},effect='write')]
            def call(self,*a):raise AssertionError('discovery must not dispatch')
        with tempfile.TemporaryDirectory() as folder:
            store=CaseStore(Path(folder)/'state.sqlite')
            try:
                state=store.open_case(self.scope,'task','PA');fence=store.claim(self.scope,'worker',120)
                harness=Harness(store,None,Tools())
                result=harness._local_call(self.scope,state,ToolCall('d','case.discover_tools',{'query':'appeal'}),'worker',fence)
                self.assertEqual('auth.file_appeal',result['tools'][0]['name'])
                self.assertIn('auth.file_appeal',store.load_case(self.scope)['activated_tools'])
                with self.assertRaises(IsolationError):
                    harness._local_call(self.scope,state,ToolCall('i','case.inspect_evidence',{'id':'foreign'}),'worker',fence)
            finally:store.close()


if __name__=='__main__':unittest.main()
