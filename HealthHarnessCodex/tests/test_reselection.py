import json
from pathlib import Path
import tempfile
import unittest
from contextlib import closing

from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope, Limits, ModelReply, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.reselection import run_identity_episodes, write_requires_reconciliation


class Tools:
    def __init__(self,marker):self.marker=marker;self.calls=[]
    def list_tools(self):
        return [ToolSpec('records.read','Read chart',{'type':'object'},effect='read'),
                ToolSpec('records.write','Change clinical record',{'type':'object'},effect='write')]
    def call(self,name,args):self.calls.append(name);return {'fact':self.marker}


class Model:
    def __init__(self,replies,forbidden=()):self.replies=list(replies);self.forbidden=forbidden
    def complete(self,messages,tools,**kwargs):
        text=json.dumps(messages)
        for value in self.forbidden:
            if value in text:raise AssertionError('quarantined information leaked into new model context')
        if not self.replies:raise AssertionError('unexpected model call')
        return self.replies.pop(0)


class ReselectionTests(unittest.TestCase):
    def test_explicit_pre_dispatch_rejection_is_safe_but_generic_write_error_is_not(self):
        self.assertFalse(write_requires_reconciliation('records.write','write','completed',
                         {'isError':True,'known_not_dispatched':True}))
        self.assertTrue(write_requires_reconciliation('records.write','write','completed',
                        {'isError':True,'error':'timeout'}))
        self.assertTrue(write_requires_reconciliation('records.write','write','pending',
                        {'isError':True,'known_not_dispatched':True}))

    def test_reset_stops_sibling_writes_and_clean_episode_keeps_audit_and_spent_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);seen=[];backends=[]
            def episode(**kwargs):
                rejected=kwargs.get('_excluded_patient_ids',())
                second=bool(rejected);patient='patient-B' if second else 'patient-A'
                if second:
                    self.assertEqual(('patient-A',),rejected)
                    self.assertEqual(8,kwargs['max_model_calls'])
                    self.assertEqual(17,kwargs['max_tool_calls'])
                    self.assertFalse((root/'state.sqlite').exists())
                    self.assertEqual(1,len(list((root/'quarantine').iterdir())))
                scope=Scope('world','task','org','actor',patient,'case-'+patient)
                backend=Tools('NEW_FACT_B' if second else 'OLD_SECRET_A');backends.append(backend)
                replies=([
                    ModelReply(tool_calls=(ToolCall('read','records.read',{}),)),
                    ModelReply(content=json.dumps({'status':'complete','claim':'Observed current record',
                                                  'evidence_ids':['ev:m1:read']}))] if second else [
                    ModelReply(tool_calls=(ToolCall('read','records.read',{}),
                        ToolCall('plan','case.add_obligation',{'id':'OLD_PLAN_A','description':'OLD_SECRET_A'}),
                        ToolCall('reset','case.request_identity_reselection',{'reason':'OLD_SECRET_A makes identity unjustified',
                                                                            'evidence_ids':['ev:m1:read']}),
                        ToolCall('must-not-run','records.write',{})))])
                store=CaseStore(root/'state.sqlite')
                try:
                    local=Harness(store,Model(replies,('OLD_SECRET_A','OLD_PLAN_A') if second else ()),backend,
                        limits=Limits(max_model_calls=kwargs['max_model_calls'],max_tool_calls=kwargs['max_tool_calls'])).run(
                            scope,'Investigate the intended subject','PA')
                finally:store.close()
                report={'scope':scope.to_dict(),'local_harness':local,'bootstrap_model_calls':1,
                        'model_calls_total_observed':local['model_calls']+1}
                (root/'run.result.json').write_text(json.dumps(report))
                (root/'evaluation.json').write_text(json.dumps({'harness_status':local['status'],'metrics':{}}))
                (root/'result.private.json').write_text(json.dumps(local))
                seen.append(kwargs);return report
            result=run_identity_episodes(episode,{'run_dir':root,'max_model_calls':10,'max_tool_calls':20,
                                                   'max_context_chars':100000})
            self.assertEqual(2,len(seen));self.assertEqual('unresolved',result['local_harness']['status'])
            self.assertEqual('completion_contract_missing',result['local_harness']['completion_gate']['reason_code'])
            self.assertEqual(5,result['model_calls_total_observed'])
            self.assertEqual(3,result['local_harness']['model_calls'])
            self.assertEqual(4,result['local_harness']['tool_calls'])
            self.assertEqual([],result['local_harness']['obligations'])
            self.assertNotIn('OLD_SECRET_A',json.dumps(result['local_harness']['evidence']))
            self.assertNotIn('records.write',backends[0].calls)
            self.assertTrue((root/'quarantine/episode-001/state.sqlite').is_file())
            self.assertIn('OLD_SECRET_A',(root/'quarantine/episode-001/result.private.json').read_text())
            self.assertTrue((root/'quarantine/episode-001/integrity.json').is_file())

    def test_external_write_blocks_reset_without_erasing_its_effect_or_audit(self):
        with closing(CaseStore(':memory:')) as store:
            scope=Scope('w','t','o','a','p','c');tools=Tools('fact')
            model=Model([ModelReply(tool_calls=(ToolCall('write','records.write',{}),
                        ToolCall('reset','case.request_identity_reselection',{'reason':'Identity concern'}),
                        ToolCall('later','records.write',{})))])
            result=Harness(store,model,tools).run(scope,'task','PA')
            self.assertEqual('blocked',result['status'])
            self.assertTrue(result['identity_reselection']['requires_reconciliation'])
            self.assertFalse(result['identity_reselection']['reset_allowed'])
            self.assertEqual(['records.write'],tools.calls)
            self.assertEqual('completed',store.actions(scope)[0]['status'])

    def test_controller_rechecks_journal_and_blocks_a_forged_safe_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def episode(**kwargs):
                scope=Scope('w','t','o','a','p','c')
                with closing(CaseStore(root/'state.sqlite')) as store:
                    store.open_case(scope,'task','PA')
                    store.reserve_action(scope,'unknown-write','records.write',{},'write')
                return {'scope':scope.to_dict(),'local_harness':{'status':'reselection_requested','model_calls':1,
                        'tool_calls':1,'identity_reselection':{'requested':True,'reset_allowed':True}}}
            result=run_identity_episodes(episode,{'run_dir':root,'max_model_calls':10,'max_tool_calls':20,'max_context_chars':100000})
            self.assertEqual('blocked',result['local_harness']['status'])
            self.assertFalse((root/'quarantine').exists())
            self.assertTrue((root/'state.sqlite').is_file())

    def test_reset_does_not_replenish_budget_or_loop_when_identity_pool_is_exhausted(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);calls=[]
            def episode(**kwargs):
                calls.append(kwargs)
                scope=Scope('w','t','o','a','p','c')
                with closing(CaseStore(root/'state.sqlite')) as store:store.open_case(scope,'task','PA')
                return {'scope':scope.to_dict(),'model_calls_total_observed':2,'local_harness':{
                    'status':'reselection_requested','model_calls':2,'tool_calls':1,
                    'identity_reselection':{'requested':True,'reset_allowed':True}}}
            result=run_identity_episodes(episode,{'run_dir':root,'max_model_calls':2,'max_tool_calls':20,'max_context_chars':100000})
            self.assertEqual(1,len(calls));self.assertEqual('unresolved',result['local_harness']['status'])
            self.assertFalse((root/'quarantine').exists())


if __name__=='__main__':unittest.main()
