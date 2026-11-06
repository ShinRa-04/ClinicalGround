import json
import unittest
from contextlib import closing

from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope,Limits,ToolSpec,ToolCall,ModelReply
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


SCOPE=Scope('synthetic','recovery-job','payer','actor','patient','case')
READ='review.get_md_review_data'


def blocked():
    return ModelReply(content=json.dumps({'status':'incomplete','claim':'Cannot continue without a supplied registry.',
        'evidence_ids':[],'blocker':{'blocked_action':'Read the assigned source','missing_information':'Registry',
        'why_required':'Assumed prerequisite','next_required_action':'Wait for the registry'}}))


class Model:
    def __init__(self,callback):self.callback=callback;self.seen=[];self.specs=[]
    def complete(self,messages,tools,**kw):
        self.seen.append(messages);self.specs.append(tools)
        return self.callback(len(self.seen),messages,tools)


class Tools:
    def __init__(self):self.calls=[]
    def list_tools(self):return [ToolSpec(READ,'Read current synthetic source',{'type':'object','properties':{}},effect='read'),
        ToolSpec('review.save_md_review','Write synthetic source',{'type':'object','properties':{}},effect='write')]
    def call(self,name,args):self.calls.append(name);return {'case_id':'case','status':'observed'}


def contract():
    c=operator_observation_contract(SCOPE,'UM',READ,[{'id':'source_observed','path':'status','op':'eq','value':'observed'}])
    c['domain']='pa_um';return c


class RecoveryAuditTests(unittest.TestCase):
    def test_repeated_blocker_runs_one_read_only_review_then_owner_can_act(self):
        def callback(n,m,specs):
            if n in (1,2):return blocked()
            if n==3:
                self.assertIn('Challenge the owner blocker',m[1]['content'])
                from health_harness_codex.cm_guidance import CAPABILITY_LIMITS, STOP_REVIEW
                self.assertIn(CAPABILITY_LIMITS,m[0]['content'])
                self.assertNotIn(CAPABILITY_LIMITS,m[1]['content'])
                self.assertIn(STOP_REVIEW,m[1]['content'])
                self.assertTrue(all(s.effect=='read' for s in specs))
                return ModelReply(tool_calls=(ToolCall('contract','case.get_tool_contract',{'tool_name':READ}),))
            if n==4:return ModelReply(content=json.dumps({'status':'complete','conclusion':'No registry input is required; read the source.',
                'evidence_ids':[],'open_questions':[]}))
            if n==5:
                self.assertIn('read-only recovery reviewer',json.dumps(m))
                return ModelReply(tool_calls=(ToolCall('read',READ,{}),))
            return ModelReply(content=json.dumps({'status':'complete','claim':'Source observed.','evidence_ids':['ev:m5:read']}))
        model=Model(callback);tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto').run(SCOPE,'Read assigned source.','UM',completion_contract=contract())
        self.assertEqual('complete',result['status'],result['message'])
        self.assertEqual(6,result['model_calls'])
        self.assertEqual([READ],tools.calls)
        self.assertEqual(1,len(result['helper_jobs']))
        self.assertEqual('recovery_audit',result['helper_jobs'][0]['invocation'])
        self.assertFalse(result['recovery_audit']['write_authority'])

    def test_still_unresolved_after_review_does_not_spawn_an_endless_helper_chain(self):
        def callback(n,m,specs):
            if n==3:return ModelReply(content=json.dumps({'status':'complete','conclusion':'Inspect the source before claiming a blocker.',
                'evidence_ids':[],'open_questions':[]}))
            return blocked()
        model=Model(callback)
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,Tools(),composition='helpers',recovery_helper_policy='auto').run(SCOPE,'Read source.','UM',completion_contract=contract())
        self.assertEqual('unresolved',result['status'])
        self.assertEqual(1,len(result['helper_jobs']))
        self.assertLessEqual(result['model_calls'],6)

    def test_automatic_reviewer_cannot_dispatch_a_write(self):
        def callback(n,m,specs):
            if n in (3,4):return ModelReply(tool_calls=(ToolCall('bad','review.save_md_review',{}),))
            return blocked()
        tools=Tools();model=Model(callback)
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,composition='helpers',recovery_helper_policy='auto').run(SCOPE,'Read source.','UM',completion_contract=contract())
        self.assertEqual([],tools.calls)
        self.assertEqual(1,len(result['helper_jobs']))
        self.assertEqual('incomplete',result['helper_jobs'][0]['status'])

    def test_off_and_combined_modes_do_not_silently_start_a_helper(self):
        for composition,policy in (('helpers','off'),('combined','auto')):
            model=Model(lambda *a:blocked())
            with closing(CaseStore(':memory:')) as store:
                result=Harness(store,model,Tools(),composition=composition,recovery_helper_policy=policy).run(SCOPE,'Read source.','UM',completion_contract=contract())
            self.assertEqual([],result['helper_jobs'])

    def test_review_does_not_spend_the_owner_last_calls_or_raise_case_budget(self):
        model=Model(lambda *a:blocked())
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,Tools(),limits=Limits(max_model_calls=4),composition='helpers',recovery_helper_policy='auto').run(SCOPE,'Read source.','UM',completion_contract=contract())
        self.assertEqual([],result['helper_jobs'])
        self.assertLessEqual(result['model_calls'],4)


if __name__=='__main__':unittest.main()
