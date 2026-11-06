import json
from contextlib import closing
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch

from health_harness_codex.authorized_statements import NAME
from health_harness_codex.engine import Harness
from health_harness_codex.helper_jobs import run_helper
from health_harness_codex.models import ModelReply, ToolCall, Limits
from health_harness_codex.store import CaseStore
from health_harness_codex.worker_preparation import INSTRUCTION, prepare
from test_dialogue_worker import seed, Tools
from test_goal_planning import SCOPE, ev


class WorkerPreparationTests(TestCase):
    def run_job(self, replies, *, preparation=True, budget=5, tool_budget=8, context_cap=0, role_id="CM-04"):
        class Fake:
            def __init__(self): self.contexts=[]; self.tools=[]
            def complete(inner, messages, tools, **kwargs):
                inner.contexts.append(deepcopy(messages)); inner.tools.append([s.name for s in tools])
                return replies.pop(0) if replies else ModelReply(content=json.dumps({
                    'status':'complete','conclusion':'Synthetic result','evidence_ids':[],'open_questions':[]}))
        with closing(CaseStore(':memory:')) as store:
            state=seed(store); e=ev(state,'workspace.read_file',{'text':'Synthetic policy record'},'read')
            state['model_calls']=0
            model=Fake(); tools=Tools(); events=[]
            h=Harness(store,model,tools,Limits(max_model_calls=10,max_tool_calls=10,max_context_chars=context_cap),
                composition='helpers',progress=lambda name,**kw:events.append((name,kw)))
            owner='owner'; fence=store.claim(SCOPE,owner); h._save(SCOPE,state,owner,fence)
            result=run_helper(h,SCOPE,state,ToolCall('job','case.request_helper',{
                'role_id':role_id,'question':'Explain supported options.', 'evidence_ids':[e['id']],
                'tool_names':[NAME], 'allow_writes':True,'max_model_calls':budget,'max_tool_calls':tool_budget}),
                owner,fence,preparation=preparation)
            return store.load_case(SCOPE), model, tools, events, result

    def test_first_call_local_only_budgeted_and_later_pin(self):
        state,model,tools,events,result=self.run_job([ModelReply(tool_calls=[ToolCall('p',NAME,{'statements':[]})])])
        self.assertEqual([NAME],model.tools[0]); self.assertIn(INSTRUCTION,model.contexts[0][-1]['content'])
        self.assertIn('actor_source_linked_preparation_not_policy',model.contexts[1][0]['content'])
        self.assertEqual(2,state['model_calls']); self.assertEqual(1,state['tool_calls'])
        self.assertEqual(2,result['model_calls']); self.assertEqual(1,result['tool_proposals'])
        self.assertEqual([],tools.calls)
        self.assertEqual(0,next(data for name,data in events if name=='worker_preparation')['recorded'])
        self.assertTrue(any(m.get('helper_job_id') and m.get('name')==NAME for m in state['messages']))

    def test_invalid_one_retry_then_conversation_no_dispatch(self):
        bad=ModelReply(tool_calls=[ToolCall('x','records.save',{})])
        state,model,tools,events,result=self.run_job([bad,bad])
        self.assertEqual(3,state['model_calls']); self.assertEqual(2,state['tool_calls'])
        self.assertEqual([[NAME],[NAME],[NAME]],model.tools)
        feedback=json.loads(model.contexts[1][-1]['content'])
        self.assertIn('error',feedback); self.assertIn('detail',feedback)
        self.assertNotIn(INSTRUCTION,model.contexts[2][-1]['content'])
        self.assertNotIn('authorized_statements',state); self.assertEqual([],tools.calls)
        self.assertEqual('complete',result['status'])

    def test_invalid_citation_corrected(self):
        item={'text':'Synthetic supported statement','source_evidence_id':'missing',
            'policy_condition':None,'condition_status':'not_applicable','condition_evidence_ids':[]}
        bad=ModelReply(tool_calls=[ToolCall('p',NAME,{'statements':[item]})])
        good=ModelReply(tool_calls=[ToolCall('q',NAME,{'statements':[]})])
        state,model,tools,events,result=self.run_job([bad,good])
        self.assertEqual([],state['authorized_statements']); self.assertEqual(3,result['model_calls'])
        self.assertEqual([],tools.calls)

    def test_budget_retains_conversation_and_owner_turn(self):
        bad=ModelReply(tool_calls=[ToolCall('x','records.save',{})])
        state,model,tools,events,result=self.run_job([bad],budget=2,tool_budget=1)
        self.assertEqual(2,state['model_calls']); self.assertEqual(1,state['tool_calls'])
        self.assertEqual(1,state['helper_jobs'][0]['preparation_result']['model_calls'])
        self.assertEqual('complete',result['status']); self.assertEqual([],tools.calls)

    def test_default_worker_has_no_preparation_phase(self):
        state,model,tools,events,result=self.run_job([],preparation=False,role_id="SH-10")
        self.assertEqual(1,state['model_calls']); self.assertEqual(0,state['tool_calls'])
        self.assertFalse(any(name=='worker_preparation' for name,data in events))
        self.assertNotIn(INSTRUCTION,json.dumps(model.contexts))

    def test_probe_prepare_calls_shared_routine(self):
        import health_harness_codex.conversation_probe as cp
        from test_conversation_probe import fixture, FakeModel
        saved,job,tools=fixture()
        messages,specs,patient=cp.prepare_probe(saved,job,1,'current',tools)
        with patch.object(cp,'prepare_worker',wraps=prepare) as shared:
            cp.repeated_probe(saved,job,1,'current',FakeModel(),messages,specs,patient,prepare=True)
        self.assertEqual(1,shared.call_count)
