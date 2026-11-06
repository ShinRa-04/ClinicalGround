import copy
import json
import unittest
from contextlib import closing

from health_harness_codex.assignment import completion_audit,stage_guidance,resolve_tool
from health_harness_codex.completion_contracts import build_completion_contract,validate_completion_contract
from health_harness_codex.engine import Harness,_completion_contract_hash
from health_harness_codex.models import Scope,ToolSpec,ToolCall,ModelReply,IsolationError
from health_harness_codex.store import CaseStore
from health_harness_codex.workflow import recovery_prompt
from closure_fixtures import stop_record


SCOPE=Scope('synthetic','assignment-test','payer','actor','patient','case')
TASK='Triage Routing. Pick the review lane, then work clinical review, MD decision and any P2P to final determination yourself.'


def ev(tool,value,effect='write'):
    return {'id':'ev:'+tool,'scope':SCOPE.to_dict(),'tool':tool,'effect':effect,'outcome':'success','observed_result':value}


def evidence(md=True,notice_after=True):
    events=[ev('triage.route_case',{'route_record':{'case_id':'case'}}),
        ev('review.submit_nurse_case_recommendation',{'case_recommendation':{'case_id':'case','recommendation':'request_info'}})]
    physician=ev('review.submit_md_case_decision',{'case_decision':{'id':'md-record','case_id':'case',
        'decision':'request_info','determination_rationale':'Source-supported missing information.',
        'info_requested':'Documented missing measurements','info_deadline':'seven days','signed_off':True}})
    notice=ev('payer_letter_center.deliver',{'letter':{'case_id':'case','letter_type':'pend','delivered_at':'2026-01-01'}})
    if not notice_after:events.append(notice)
    if md:events.append(physician)
    if notice_after:events.append(notice)
    events.append(ev('determination.get_summary',{'case_id':'case','case_status':'pended_action_required',
        'md_decision':{'id':'md-record','case_id':'case','decision':'request_info'} if md else None},'read'))
    return events


def state(events=None):
    contract=build_completion_contract(SCOPE.task,'pa_um',TASK,SCOPE.to_dict())
    return {'scope':SCOPE.to_dict(),'domain':'UM','composition':'helpers','instruction':TASK,
        'completion_contract':contract,'completion_contract_sha256':_completion_contract_hash(contract),
        'evidence':events or [],'obligations':[],'messages':[],'workflow_capabilities':{}}


class AssignmentStageTests(unittest.TestCase):
    def test_nurse_pending_does_not_complete_md_assignment_and_guidance_changes(self):
        s=state(evidence(md=False));audit=completion_audit(s)
        self.assertFalse(audit['accepted'])
        self.assertEqual('physician_review',stage_guidance(s)['current_responsibility'])
        self.assertIn('MD decision',stage_guidance(s)['guidance'])
        self.assertFalse(stage_guidance(s)['clinical_outcome_selected_by_code'])
        self.assertFalse(audit['is_official_grade'])

    def test_md_information_handoff_is_supported_without_manufactured_coverage_decision(self):
        s=state(evidence());checked=completion_audit(s)
        self.assertTrue(checked['accepted'],checked)
        self.assertEqual('um_md_information_handoff',checked['branch_id'])
        self.assertEqual('information_handoff',stage_guidance(s)['current_responsibility'])
        self.assertFalse(checked['clinical_correctness_verified'])

    def test_notice_before_md_or_stale_readback_cannot_complete_handoff(self):
        s=state(evidence(notice_after=False));self.assertFalse(completion_audit(s)['accepted'])
        s=state(evidence());s['evidence']=s['evidence'][:-1];self.assertFalse(completion_audit(s)['accepted'])
        s=state(evidence());s['evidence'][-1]['observed_result']['md_decision']['id']='different'
        self.assertFalse(completion_audit(s)['accepted'])

    def test_missing_md_rationale_signature_deadline_or_case_identity_is_not_waived(self):
        for field in ('determination_rationale','signed_off','info_deadline','case_id'):
            s=state(evidence());decision=s['evidence'][2]['observed_result']['case_decision'];decision.pop(field)
            self.assertFalse(completion_audit(s)['accepted'],field)

    def test_explicit_task_restriction_and_required_p2p_are_respected(self):
        for instruction in (TASK+' Do not pend.',TASK+' Run the peer-to-peer session and record the outcome.'):
            c=build_completion_contract('different-task','pa_um',instruction,SCOPE.to_dict())
            self.assertNotIn('um_md_information_handoff',[b['id'] for b in c['branches']])

    def test_conditional_intake_keeps_intake_scope_on_pending_path(self):
        text=('New intake. If a failed check requires rejection, finalize the denial and issue the required letter. '
              'Otherwise, route the case and complete clinical review, the physician decision, and any required peer-to-peer review.')
        c=build_completion_contract('intake','pa_um',text,SCOPE.to_dict())
        branch=next(b for b in c['branches'] if b['id']=='um_md_information_handoff')
        self.assertIn('intake_completed',[r['id'] for r in branch['requirements']])
        self.assertFalse(validate_completion_contract(c,evidence(),SCOPE.to_dict())['accepted'])

    def test_provider_only_deferral_hidden_and_refused_for_um(self):
        class Tools:
            def list_tools(self):return []
        with closing(CaseStore(':memory:')) as store:
            store.open_case(SCOPE,TASK,'UM');s=store.load_case(SCOPE)
            h=Harness(store,None,Tools(),composition='helpers')
            names=[spec.name for spec in h._available_specs({},s)]
            self.assertNotIn('case.defer_obligation',names)
            self.assertIn('case.record_external_handoff',names)
            with self.assertRaises(IsolationError):h._local_call(SCOPE,s,ToolCall('bad','case.defer_obligation',{}),'owner',1)
        self.assertNotIn('case.defer_obligation',recovery_prompt(state(evidence(md=False))))

    def test_canonical_contract_resolution_is_unique_and_permission_preserving(self):
        s=ToolSpec('mcp_review_get_md_review_data_123456abcdef','Read MD',{'type':'object'})
        self.assertEqual(s,resolve_tool([s],'review.get_md_review_data'))
        with self.assertRaises(ValueError):resolve_tool([s],'review.unknown')
        other=ToolSpec('mcp_review_get_md_review_data_abcdef123456','Other',{'type':'object'})
        with self.assertRaises(ValueError):resolve_tool([s,other],'review.get_md_review_data')

    def test_um_external_obligation_deferred_only_after_real_md_handoff(self):
        class Tools:
            def list_tools(self):return []
        with closing(CaseStore(':memory:')) as store:
            store.open_case(SCOPE,TASK,'UM');s=store.load_case(SCOPE);s.update(state(evidence(md=False)))
            s['obligations']=[{'id':'external','status':'open','owner':'provider'}]
            store.save_case(SCOPE,s,s['version']);fence=store.claim(SCOPE,'owner');s=store.load_case(SCOPE)
            h=Harness(store,None,Tools(),composition='helpers')
            call=ToolCall('handoff','case.record_external_handoff',{'id':'external','evidence_ids':['ev:determination.get_summary'],'next_action':'Obtain the requested record.'})
            with self.assertRaises(ValueError):h._local_call(SCOPE,s,call,'owner',fence)
            s['evidence']=evidence();store.save_case(SCOPE,s,s['version'],owner='owner',fence=fence);s=store.load_case(SCOPE)
            result=h._local_call(SCOPE,s,call,'owner',fence)
            self.assertTrue(result['deferred']);self.assertFalse(result['obligation_completed'])
            self.assertFalse(result['notification_sent_by_this_tool'])
            self.assertEqual('deferred',store.load_case(SCOPE)['obligations'][0]['status'])

    def test_actual_owner_context_moves_nurse_to_md_to_handoff(self):
        class Model:
            def __init__(self):self.calls=0;self.phases=[]
            def complete(self,messages,tools,**kwargs):
                self.calls+=1
                ledger=json.loads(messages[0]['content'].rsplit('Current case working set:\n',1)[1])
                self.phases.append(ledger['stage_guidance']['current_responsibility'])
                if self.calls==1:return ModelReply(tool_calls=(ToolCall('route','triage.route_case',{}),))
                if self.calls==2:return ModelReply(tool_calls=(ToolCall('nurse','review.submit_nurse_case_recommendation',{}),))
                if self.calls==3:return ModelReply(tool_calls=(ToolCall('md','review.submit_md_case_decision',{}),))
                if self.calls==4:return ModelReply(tool_calls=(ToolCall('notice','payer_letter_center.deliver',{}),ToolCall('summary','determination.get_summary',{})))
                return ModelReply(content=json.dumps({'status':'complete','claim':'Observed assigned information handoff.',
                    'stop_assessment':stop_record(['ev:m3:md','ev:m4:notice','ev:m4:summary']),
                    'evidence_ids':['ev:m3:md','ev:m4:notice','ev:m4:summary']}))
        class Tools:
            def list_tools(self):return [ToolSpec(e['tool'],'Synthetic stage operation',{'type':'object','properties':{}},effect=e['effect']) for e in evidence()]
            def call(self,name,args):return next(e['observed_result'] for e in evidence() if e['tool']==name)
        model=Model()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,Tools(),composition='helpers').run(SCOPE,TASK,'UM',completion_contract=state()['completion_contract'])
        self.assertEqual('complete',result['status'],result['message'])
        self.assertEqual(['triage','nurse_review','physician_review','information_handoff','information_handoff'],model.phases)


if __name__=='__main__':unittest.main()
