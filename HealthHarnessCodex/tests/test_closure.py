"""Exercise composition of task evidence, deferred work, final reply and reporting."""
import copy
import json
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from closure_fixtures import stop_record
from test_assignment_stages import SCOPE, TASK, evidence, state
from health_harness_codex.assignment import completion_audit
from health_harness_codex.closure import assess_closure, derive_stop_metadata, assess_stop_record
from health_harness_codex.completion_contracts import contract_hash
from health_harness_codex.engine import Harness
from health_harness_codex.evaluation import RunRecorder
from health_harness_codex.models import Limits, ModelReply, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.workflow import recovery_prompt


class Tools:
    def list_tools(self):
        return []


def pending_state(branch_name=None):
    s = state(evidence())
    if branch_name:
        branch = next(b for b in s['completion_contract']['branches'] if b.get('allows_external_wait'))
        branch['id'] = branch_name
        s['completion_contract_sha256'] = contract_hash(s['completion_contract'])
    branch = next(b['id'] for b in s['completion_contract']['branches'] if b.get('allows_external_wait'))
    s.update(model_calls=1, status='running')
    s['obligations'] = [{'id': 'external', 'status': 'deferred', 'handoff_branch': branch,
                        'evidence_ids': ['ev:determination.get_summary'], 'next_action': 'Obtain the requested report.'}]
    return s


def final_reply(s, status='complete'):
    ids = [s['evidence'][-1]['id']]
    return {'status': status, 'claim': 'Supported request delivered; current work must await its response.',
            'evidence_ids': ids, 'stop_assessment': stop_record(ids, ['external'])}


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.store = CaseStore(':memory:')
        self.h = Harness(self.store, None, Tools(), limits=Limits(max_model_calls=10))

    def tearDown(self):
        self.store.close()

    def test_explicit_top_level_work_lists_relocate_losslessly_without_closing_work(self):
        s=pending_state();payload=final_reply(s)
        original=copy.deepcopy(payload)
        payload['waiting_on_obligation_ids']=payload['stop_assessment'].pop('waiting_on_obligation_ids')
        payload['blocked_obligation_ids']=[]
        submitted=copy.deepcopy(payload)
        normalized,receipt=derive_stop_metadata(s,payload,assess_closure(s))
        self.assertEqual(submitted,payload)
        self.assertEqual(original['stop_assessment'],{k:v for k,v in normalized['stop_assessment'].items() if k!='blocked_obligation_ids'})
        self.assertEqual({'waiting_on_obligation_ids','blocked_obligation_ids'},set(receipt['relocated_fields']))
        self.assertTrue(assess_stop_record(s,normalized,assess_closure(s))['accepted'])
        result=self.h._accept_final(s,json.dumps(payload))
        self.assertEqual('complete',result['status'])
        self.assertEqual('deferred',result['obligations'][0]['status'])
        self.assertEqual(submitted,result['final_submitted'])

    def test_missing_wrong_and_conflicting_work_lists_still_reject(self):
        for invalid in ('missing','wrong','conflicting'):
            with self.subTest(invalid=invalid):
                s=pending_state();payload=final_reply(s)
                if invalid=='missing':payload['stop_assessment'].pop('waiting_on_obligation_ids')
                elif invalid=='wrong':
                    payload['stop_assessment'].pop('waiting_on_obligation_ids')
                    payload['waiting_on_obligation_ids']=['invented']
                else:payload['waiting_on_obligation_ids']=[]
                result=self.h._accept_final(s,json.dumps(payload))
                self.assertFalse(result['stop_assessment_validation']['accepted'])
                self.assertTrue(result['final_format_retry_pending'])
                self.assertIn('INSIDE stop_assessment',result['messages'][-1]['content'])
                self.assertEqual('FinalWorkAccountingError',result['final_format_retries'][-1]['error_type'])
                result=self.h._accept_final(result,json.dumps(payload))
                self.assertEqual('unresolved',result['status'])
                self.assertEqual('stop_report_accounting_repair_exhausted',result['workflow_stop_reason'])
                self.assertIn('work accounting',result['message'])

    def test_same_work_ids_in_different_order_do_not_create_a_conflict(self):
        s=pending_state()
        s['obligations'].append({**s['obligations'][0],'id':'external-two'})
        payload=final_reply(s)
        payload['stop_assessment']['waiting_on_obligation_ids']=['external','external-two']
        payload['waiting_on_obligation_ids']=['external-two','external']
        result=self.h._accept_final(s,json.dumps(payload))
        self.assertEqual('complete',result['status'])
        self.assertTrue(result['stop_assessment_validation']['accepted'])
        self.assertEqual(0,result.get('final_format_retry_count',0))

    def test_generic_wait_branch_audit_and_final_agree_and_preserve_deferred_work(self):
        s = pending_state('operator_declared_external_wait')
        audit = completion_audit(s)
        result = self.h._accept_final(s, json.dumps(final_reply(s)))
        self.assertEqual('complete', result['status'])
        self.assertEqual(audit, completion_audit(s))
        self.assertEqual(audit['branch_id'], result['completion_gate']['branch_id'])
        self.assertTrue(result['completion_gate']['accepted'])
        self.assertEqual('deferred', s['obligations'][0]['status'])
        self.assertFalse(result['completion']['stop_assessment_validation']['semantic_actionability_verified'])

    def test_incomplete_reply_is_assessed_and_explicit_no_action_can_end_pending_work(self):
        s = pending_state()
        result = self.h._accept_final(s, json.dumps(final_reply(s, 'incomplete')))
        self.assertEqual('complete', result['status'])
        self.assertEqual('incomplete', result['final']['status'])
        self.assertEqual('incomplete', result['completion']['model_reported_status'])
        self.assertTrue(result['completion']['has_deferred_work'])

    def test_pending_status_or_ambiguity_without_actionability_record_cannot_end(self):
        for status in ('complete', 'incomplete'):
            s = pending_state(); reply = final_reply(s, status); reply.pop('stop_assessment')
            result = self.h._accept_final(s, json.dumps(reply))
            self.assertEqual('unresolved', result['status'])
            self.assertTrue(result['completion_gate']['accepted'])
            self.assertTrue(result['stop_review_required'])
            prompt = recovery_prompt(result)
            self.assertIn('available investigations first', prompt)
            self.assertNotIn('You returned before completing', prompt)

    def test_remaining_actions_are_not_overridden_by_structural_success(self):
        s = pending_state(); reply = final_reply(s)
        reply['stop_assessment']['no_further_permitted_action'] = False
        result = self.h._accept_final(s, json.dumps(reply))
        self.assertEqual('unresolved', result['status'])
        self.assertEqual('worker_reports_actions_remaining', result['stop_assessment_validation']['reason_code'])

    def test_no_action_claim_cannot_waive_missing_notice_or_open_internal_work(self):
        for missing in ('notice', 'internal_work'):
            s = pending_state()
            if missing == 'notice':s['evidence'] = [e for e in s['evidence'] if e['tool'] != 'payer_letter_center.deliver']
            else:s['obligations'].append({'id': 'internal_review', 'status': 'open'})
            result = self.h._accept_final(s, json.dumps(final_reply(s)))
            self.assertNotEqual('complete', result['status'])
            self.assertFalse(result['completion_gate']['accepted'])
            self.assertFalse(completion_audit(s)['accepted'])

    def test_deferral_metadata_reference_and_scope_cannot_be_bypassed(self):
        for invalid in ('permission', 'branch', 'reference', 'next_action', 'cross_scope'):
            s = pending_state()
            if invalid == 'permission':
                for b in s['completion_contract']['branches']:b.pop('allows_external_wait', None)
                s['completion_contract_sha256'] = contract_hash(s['completion_contract'])
            elif invalid == 'branch':s['obligations'][0]['handoff_branch'] = 'unrelated'
            elif invalid == 'reference':s['obligations'][0]['evidence_ids'] = ['ev:invented']
            elif invalid == 'next_action':s['obligations'][0]['next_action'] = ''
            else:s['evidence'][-1]['scope'] = {**SCOPE.to_dict(), 'patient': 'other'}
            result = self.h._accept_final(s, json.dumps(final_reply(s)))
            self.assertNotEqual('complete', result['status'], invalid)
            self.assertFalse(completion_audit(s)['accepted'], invalid)

    def test_stop_record_requires_sources_investigations_and_all_waiting_obligations(self):
        for missing in ('evidence_ids', 'investigations_performed', 'other_work_considered', 'waiting_on_obligation_ids'):
            s = pending_state(); reply = final_reply(s); reply['stop_assessment'][missing] = []
            result = self.h._accept_final(s, json.dumps(reply))
            self.assertNotEqual('complete', result['status'], missing)
        s = pending_state();reply = final_reply(s);reply['stop_assessment']['evidence_ids'] = ['ev:invented']
        self.assertNotEqual('complete', self.h._accept_final(s,json.dumps(reply))['status'])

    def test_contract_integrity_rejection_is_shared_by_audit_and_final(self):
        s = pending_state();s['completion_contract']['branches'][0]['id'] = 'tampered'
        self.assertEqual('completion_contract_integrity_error',completion_audit(s)['reason_code'])
        result = self.h._accept_final(s,json.dumps(final_reply(s)))
        self.assertEqual('completion_contract_integrity_error',result['completion_gate']['reason_code'])
        self.assertEqual('unresolved',result['status'])

    def test_asserted_investigations_require_actual_successful_read_sources(self):
        for sources in (['ev:invented'],['ev:review.submit_md_case_decision']):
            s=pending_state();reply=final_reply(s);reply['stop_assessment']['investigations_performed']=sources
            result=self.h._accept_final(s,json.dumps(reply))
            self.assertNotEqual('complete',result['status'])
            self.assertEqual('stop_investigation_evidence_unverified',result['stop_assessment_validation']['reason_code'])

    def test_malformed_status_cannot_bypass_assessment_or_raise_type_error(self):
        s=pending_state();reply=final_reply(s);reply['status']=[]
        result=self.h._accept_final(s,json.dumps(reply))
        self.assertEqual('unresolved',result['status'])
        self.assertTrue(result['completion_gate']['accepted'])

    def test_alternative_selection_accounts_for_deferred_work_not_branch_order(self):
        s=pending_state()
        alternate=next(b for b in s['completion_contract']['branches'] if b.get('allows_external_wait'))
        first=copy.deepcopy(alternate);first['id']='also_structurally_satisfied';first.pop('allows_external_wait')
        s['completion_contract']['branches'].insert(0,first)
        s['completion_contract_sha256']=contract_hash(s['completion_contract'])
        audit=completion_audit(s)
        self.assertTrue(audit['accepted'])
        self.assertEqual('um_md_information_handoff',audit['branch_id'])
        self.assertEqual('complete',self.h._accept_final(s,json.dumps(final_reply(s)))['status'])

    def test_invented_local_audit_citation_gets_one_tool_free_reference_correction(self):
        s=pending_state();reply=final_reply(s);reply['evidence_ids'].append('ev:invented-local-audit')
        result=self.h._accept_final(s,json.dumps(reply))
        self.assertEqual('running',result['status'])
        self.assertTrue(result['final_format_retry_pending'])
        self.assertIn('No new tool action',result['messages'][-1]['content'])
        self.assertNotIn('ev:invented-local-audit',result['messages'][-1]['content'])
        fixed=self.h._accept_final(s,json.dumps(final_reply(s)))
        self.assertEqual('complete',fixed['status'])
        self.assertFalse(completion_audit(s)['creates_evidence'])

    def test_final_reference_correction_is_bounded_and_never_accepts_bad_ids(self):
        s=pending_state();reply=final_reply(s);reply['stop_assessment']['investigations_performed']=['ev:fake']
        self.h._accept_final(s,json.dumps(reply))
        self.assertEqual(1,s['final_format_retry_count'])
        result=self.h._accept_final(s,json.dumps(reply))
        self.assertEqual('unresolved',result['status'])
        self.assertEqual(1,s['final_format_retry_count'])

    def test_end_to_end_um_deferral_finalization_and_report_share_the_assessment(self):
        class ActorTools:
            def list_tools(self):
                return [ToolSpec(e['tool'],'Synthetic operation',{'type':'object','properties':{}},effect=e['effect'])
                        for e in evidence()]
            def call(self,name,args):return next(e['observed_result'] for e in evidence() if e['tool']==name)
        class Worker:
            calls = 0
            def complete(self,messages,tools,**kwargs):
                self.calls += 1
                actions = {
                    1: (ToolCall('route','triage.route_case',{}),),
                    2: (ToolCall('nurse','review.submit_nurse_case_recommendation',{}),),
                    3: (ToolCall('md','review.submit_md_case_decision',{}),),
                    4: (ToolCall('notice','payer_letter_center.deliver',{}),ToolCall('summary','determination.get_summary',{})),
                    5: (ToolCall('obligation','case.add_obligation',{'id':'external','description':'Obtain a requested external report.'}),),
                    6: (ToolCall('defer','case.record_external_handoff',{'id':'external','evidence_ids':['ev:m4:summary'],'next_action':'Await provider response.'}),),
                }
                if self.calls in actions:return ModelReply(tool_calls=actions[self.calls])
                return ModelReply(content=json.dumps({'status':'incomplete','claim':'Request sent; no current action remains.',
                    'evidence_ids':['ev:m4:summary'], 'stop_assessment':stop_record(['ev:m4:summary'],['external'])}))
        worker = Worker()
        result = Harness(self.store,worker,ActorTools(),composition='helpers').run(SCOPE,TASK,'UM',
            completion_contract=state()['completion_contract'])
        self.assertEqual('complete',result['status'],result['message'])
        self.assertEqual(7,worker.calls)
        self.assertEqual('deferred',result['obligations'][0]['status'])
        with tempfile.TemporaryDirectory() as temp:
            recorder = RunRecorder(Path(temp)/'runs'/'synthetic',{})
            report = recorder.finish(result,1.0,{'public_determination_terminal':False})
        self.assertEqual('locally_complete_ungraded',report['classification'])
        self.assertTrue(report['harness_accepted_completion'])
        self.assertFalse(report['model_claimed_complete'])
        self.assertIsNone(report['official_score'])


if __name__ == '__main__':unittest.main()
