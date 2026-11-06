import copy
import json
from contextlib import closing
from unittest import TestCase

from health_harness_codex.engine import Harness
from health_harness_codex.planning import capture_public_plan
from health_harness_codex.retrieval import field_overview
from health_harness_codex.store import CaseStore
from test_goal_planning import base, ev, Tools, SCOPE, INSTRUCTION
from health_harness_codex.models import ModelReply


class CMRepairTests(TestCase):
    def stop_fixture(self):
        s=base()
        observed=ev(s,'cm_outreach.send_message',{'patient_response':'I need to end this call.','session_status':'ended'})
        authored=ev(s,'cm_outreach.end_outreach_call',{'consent_obtained':False,'notes':'A worker-authored summary.'})
        record={'no_further_permitted_action':True,'reason':'The conversation ended; the requested goal is unmet.',
            'evidence_ids':[observed['id']],'investigations_performed':[observed['id']],
            'other_work_considered':['Read available records and assess remaining permitted work.'],
            'waiting_on_obligation_ids':[]}
        payload={'status':'incomplete','claim':'Care plan not achieved; truthful unsuccessful stop.',
            'evidence_ids':[observed['id']],'stop_assessment':record}
        return s,payload,authored

    def test_incomplete_stop_needs_no_success_endpoint_and_cannot_create_one(self):
        s,payload,_=self.stop_fixture();before=copy.deepcopy(s['completion_contract'])
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,None,Tools())._accept_final(s,json.dumps(payload))
        self.assertEqual('unresolved',result['status'])
        self.assertEqual('source_backed_incomplete_stop',result['workflow_stop_reason'])
        self.assertIsNone(result['completion'])
        self.assertFalse(result['completion_gate']['accepted'])
        self.assertEqual('unmet',result['completion_gate']['requested_outcome']['status'])
        self.assertEqual(before,result['completion_contract'])

    def test_bad_investigation_gets_precise_correction_even_without_endpoint(self):
        s,payload,authored=self.stop_fixture()
        payload['stop_assessment']['investigations_performed'].append(authored['id'])
        with closing(CaseStore(':memory:')) as store:
            h=Harness(store,None,Tools());result=h._accept_final(s,json.dumps(payload))
            self.assertEqual('running',result['status'])
            self.assertIn('Reference-only correction',result['messages'][-1]['content'])
            self.assertFalse(result['completion_gate']['accepted'])
            result=h._accept_final(result,json.dumps(payload))
        self.assertEqual('unresolved',result['status'])
        self.assertEqual('stop_report_reference_repair_exhausted',result['workflow_stop_reason'])
        self.assertFalse(result['stop_assessment_validation']['accepted'])

    def test_chart_index_finds_later_document_without_claiming_its_contents(self):
        chart={'documents':[{'title':f'Observed note {i}','content':'Clinical record '*1000} for i in range(6)]}
        original=copy.deepcopy(chart);view=field_overview(chart)
        item=view['document_index']['items'][5]
        self.assertEqual('/documents/5/content',item['content_path'])
        self.assertEqual('Observed note 5',item['title'])
        self.assertLessEqual(len(json.dumps(view,ensure_ascii=False,separators=(',',':'))),4500)
        self.assertEqual(original,chart)

    def test_public_plan_keeps_next_step_and_only_original_case_source_links(self):
        s=base();observed=ev(s,'records.read',{'value':'Original data'},'read')
        capture_public_plan(s,json.dumps({'claim':'A question remains.','next_step':'Read the recorded plan before answering.',
            'patient_priority':'Understand available support.','unresolved_question':'Does the record still apply?',
            'evidence_ids':[observed['id'],'invented']}))
        self.assertIn('Read the recorded plan',s['current_plan']['next_step'])
        self.assertEqual([observed['id']],s['current_plan']['evidence_ids'])
        self.assertFalse(s['current_plan']['is_observed_fact'])
        before=copy.deepcopy(s['current_plan']);capture_public_plan(s,'{}')
        self.assertEqual(before,s['current_plan'])

    def test_failed_endpoint_retains_blocked_work_without_verifying_its_necessity(self):
        from health_harness_codex.closure import assess_closure
        s,payload,_=self.stop_fixture();source_id=payload['evidence_ids'][0]
        s['obligations']=[{'id':'unfinished','status':'open'}]
        s['prerequisite_records']=[{'support':'observation_referenced_necessity_unverified',
            'affected_obligation_ids':['unfinished'],'facts':{'source_references':[{'evidence_id':source_id}]}}]
        gate=assess_closure(s)
        self.assertFalse(gate['accepted']);self.assertEqual(['unfinished'],gate['blocked_obligation_ids'])
        self.assertFalse(gate['blocked_work_necessity_verified'])
        payload['stop_assessment']['blocked_obligation_ids']=['unfinished']
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,None,Tools())._accept_final(s,json.dumps(payload))
        self.assertEqual('source_backed_incomplete_stop',result['workflow_stop_reason'])
        self.assertEqual('open',result['obligations'][0]['status'])

    def test_full_owner_loop_corrects_failed_stop_once_without_workflow_replanning(self):
        s,good,authored=self.stop_fixture();bad=copy.deepcopy(good)
        bad['stop_assessment']['investigations_performed'].append(authored['id'])
        class Model:
            calls=0
            def complete(self,messages,tools,**kwargs):
                self.calls+=1
                if self.calls>2:raise AssertionError('Unnecessary workflow restart')
                return ModelReply(content=json.dumps(bad if self.calls==1 else good))
        with closing(CaseStore(':memory:')) as store:
            initial=store.open_case(SCOPE,INSTRUCTION,'CM')
            initial.update({k:v for k,v in s.items() if k!='version'})
            store.save_case(SCOPE,initial,initial['version'])
            model=Model();h=Harness(store,model,Tools(),composition='helpers')
            result=h.run(SCOPE,INSTRUCTION,'CM',resume=True)
            saved=store.load_case(SCOPE)
        self.assertEqual(2,model.calls)
        self.assertEqual('unresolved',result['status'])
        self.assertEqual('source_backed_incomplete_stop',saved['workflow_stop_reason'])
        self.assertFalse(saved.get('workflow_recoveries'))

    def test_omitted_journal_lists_are_derived_without_rewriting_model_reason(self):
        s,payload,authored=self.stop_fixture();original=copy.deepcopy(payload)
        for field in ('investigations_performed',):
            payload['stop_assessment'].pop(field,None)
        submitted=copy.deepcopy(payload)
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,None,Tools())._accept_final(s,json.dumps(payload))
        self.assertEqual(submitted,payload)
        self.assertEqual(submitted,result['final_submitted'])
        record=result['final']['stop_assessment']
        self.assertEqual(original['stop_assessment']['reason'],record['reason'])
        self.assertNotIn(authored['id'],record['investigations_performed'])
        self.assertEqual(original['stop_assessment']['investigations_performed'],record['investigations_performed'])
        self.assertEqual('unresolved',result['status'])
        self.assertFalse(result['completion_gate']['accepted'])
        self.assertFalse(result['stop_metadata_derivation']['clinical_reason_or_patient_choice_changed'])

    def test_explicit_incorrect_journal_lists_are_not_silently_replaced(self):
        from health_harness_codex.closure import derive_stop_metadata,assess_closure,assess_stop_record
        s,payload,authored=self.stop_fixture()
        payload['stop_assessment']['investigations_performed']=[authored['id']]
        normalized,_=derive_stop_metadata(s,payload,assess_closure(s))
        self.assertEqual([authored['id']],normalized['stop_assessment']['investigations_performed'])
        self.assertEqual('stop_investigation_evidence_unverified',assess_stop_record(s,normalized,assess_closure(s))['reason_code'])
