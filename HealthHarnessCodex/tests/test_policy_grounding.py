import copy
import hashlib
import json
import unittest
from contextlib import closing

from health_harness_codex.policy_grounding import record_decision,check_decision,operation_name,PolicyGroundingError
from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope,ToolSpec,ToolCall,ModelReply,Limits
from health_harness_codex.store import CaseStore


class PolicyGroundingTests(unittest.TestCase):
    def _cm_decision(self, engagement='tentative', basis='patient_refusal'):
        state=copy.deepcopy(self.state)
        state['evidence'][0]['observed_result']['path']='/workspace/skills/managed-care-operations-handbook/references/roles/care-management.md'
        outreach={'id':'outreach','scope':self.scope.to_dict(),'outcome':'success',
                  'tool':'cm_outreach.end_outreach_call','observed_result':{
                      'case_id':'case','engagement_status':engagement,'consent_obtained':False}}
        state['evidence'].append(outreach)
        args=copy.deepcopy(self.args)
        args['applies_to']=['cm_intake.disenroll_case']
        args['case_evidence_ids'].append('outreach')
        args['closure_basis']=basis
        args['bound_arguments']={'cm_intake.disenroll_case':{'case_id':'case','reason':'Synthetic supported exit'}}
        return state,args

    def test_tentative_outreach_cannot_support_refusal_based_terminal_closure(self):
        state,args=self._cm_decision()
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(state,args,{'cm_intake.disenroll_case'},self.scope.to_dict())
        self.assertEqual('refusal_not_recorded',caught.exception.feedback['reason'])
        self.assertFalse(state.get('policy_decisions'))

    def test_refusal_and_other_policy_bases_remain_available_without_forcing_consent(self):
        for engagement,basis in [('refused','patient_refusal'),('tentative','other_policy_basis')]:
            with self.subTest(engagement=engagement,basis=basis):
                state,args=self._cm_decision(engagement,basis)
                record_decision(state,args,{'cm_intake.disenroll_case'},self.scope.to_dict())
                bound=args['bound_arguments']['cm_intake.disenroll_case']
                self.assertIsNone(check_decision(state,'cm_intake.disenroll_case',bound,self.scope.to_dict()))
                self.assertEqual('policy_decision_action_changed',check_decision(state,'cm_intake.disenroll_case',
                    {**bound,'reason':'Changed outcome'},self.scope.to_dict()))
                new=copy.deepcopy(state['evidence'][-1]);new['id']='new-outreach';state['evidence'].append(new)
                self.assertEqual('policy_decision_source_changed',check_decision(state,'cm_intake.disenroll_case',bound,self.scope.to_dict()))

    def test_cm_closure_needs_exact_arguments_and_current_outreach_sources(self):
        for defect in ['missing_case','missing_reason','missing_basis','missing_outreach']:
            state,args=self._cm_decision('refused')
            if defect=='missing_case':args['bound_arguments']['cm_intake.disenroll_case'].pop('case_id')
            if defect=='missing_reason':args['bound_arguments']['cm_intake.disenroll_case'].pop('reason')
            if defect=='missing_basis':args.pop('closure_basis')
            if defect=='missing_outreach':args['case_evidence_ids'].remove('outreach')
            with self.subTest(defect=defect),self.assertRaises(ValueError):
                record_decision(state,args,{'cm_intake.disenroll_case'},self.scope.to_dict())

    def test_cm_workflow_reference_does_not_expand_provider_policy_sources(self):
        state,args=self._cm_decision('refused')
        args['applies_to']=['auth.submit_authorization']
        args['bound_arguments']={}
        with self.assertRaises(ValueError):
            record_decision(state,args,self.operations,self.scope.to_dict())

    def test_cm_intake_accepts_approved_workflow_policy_in_direct_and_batched_reads(self):
        for batched in (False,True):
            state=copy.deepcopy(self.state);args=copy.deepcopy(self.args)
            source=state['evidence'][0]
            source['observed_result']['path']='/workspace/skills/managed-care-operations-handbook/references/care-manager/operational/program-eligibility.md'
            path='/text'
            if batched:
                source['tool']='workspace.read_many'
                source['observed_result']={'items':[{'operation':'read_file','result':source['observed_result']}]}
                path='/items/0/result/text'
            args['policy_sources']=[{'evidence_id':source['id'],'text_pointer':path}]
            args['applies_to']=['cm_intake.open_case']
            args['bound_arguments']={'cm_intake.open_case':{'referral_id':'synthetic-referral'}}
            with self.subTest(batched=batched):
                decision=record_decision(state,args,{'cm_intake.open_case'},self.scope.to_dict())
                self.assertTrue(decision['provenance_verified'])
                self.assertEqual(path,decision['policy_sources'][0]['path'])

    def _routing_state(self):
        # Shapes reproduce the Nov 3 UM triage failure: one batched read of the
        # operational routing procedure and a clinical medical policy.
        state=copy.deepcopy(self.state)
        state['evidence'][0]={'id':'batch','scope':self.scope.to_dict(),'outcome':'success','tool':'workspace.read_many',
            'observed_result':{'items':[
                {'operation':'read_file','result':{'path':'/workspace/skills/managed-care-operations-handbook/references/payer-um/operational/02-triage-routing.md',
                                                   'text':'Synthetic routing step. Default: route to nurse review.'}},
                {'operation':'read_file','result':{'path':'/workspace/skills/managed-care-operations-handbook/references/medical-library/medical-policies/synthetic.md',
                                                   'text':'Synthetic criteria apply to the requested service.'}}]}}
        return state

    def test_operational_decision_may_cite_its_governing_procedure_in_any_domain(self):
        state=self._routing_state();args=copy.deepcopy(self.args)
        args['policy_sources']=[{'evidence_id':'batch','text_pointer':'/items/0/result/text'}]
        args['applies_to']=['triage.route_case']
        args['bound_arguments']={'triage.route_case':{'case_id':'case'}}
        decision=record_decision(state,args,{'triage.route_case'},self.scope.to_dict())
        self.assertTrue(decision['provenance_verified'])

    def test_determination_needs_clinical_source_but_may_also_cite_procedure(self):
        state=self._routing_state();args=copy.deepcopy(self.args)
        args['applies_to']=['auth.submit_authorization'];args['bound_arguments']={}
        args['policy_sources']=[{'evidence_id':'batch','text_pointer':'/items/0/result/text'}]
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(state,args,self.operations,self.scope.to_dict())
        self.assertEqual('clinical_source_required_for_determination',caught.exception.feedback['reason'])
        args['policy_sources'].append({'evidence_id':'batch','text_pointer':'/items/1/result/text'})
        self.assertTrue(record_decision(state,args,self.operations,self.scope.to_dict())['provenance_verified'])

    def test_rejected_citation_reports_index_source_and_reason(self):
        state=self._routing_state();args=copy.deepcopy(self.args)
        args['applies_to']=['triage.route_case'];args['bound_arguments']={}
        args['policy_sources']=[{'evidence_id':'batch','text_pointer':'/items/1/result/text'},
                                {'evidence_id':'batch','text_pointer':'/items/0/result/path'}]
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(state,args,{'triage.route_case'},self.scope.to_dict())
        feedback=caught.exception.feedback
        self.assertEqual(('not_retrieved_policy_text',1),(feedback['reason'],feedback['citation_index']))
        self.assertTrue(feedback['source_path'].endswith('02-triage-routing.md'))

    def test_engine_refuses_terminal_cm_write_before_any_dispatch(self):
        class Tools:
            calls=[]
            def list_tools(self):
                return [ToolSpec('cm_intake.disenroll_case','Terminal closure',{'type':'object'},effect='write')]
            def call(self,name,args):
                self.calls.append(name)
                return {'case_id':'case','status':'disenrolled'}
        replies=[ModelReply(tool_calls=(ToolCall('exit','cm_intake.disenroll_case',
                     {'case_id':'case','reason':'Missing consent'}),)),
                 ModelReply(content='{"status":"incomplete","claim":"Synthetic guard test","evidence_ids":[]}')]
        class Model:
            def complete(self,*a,**k):
                return replies.pop(0) if replies else ModelReply(content='{"status":"incomplete","claim":"Synthetic guard test","evidence_ids":[]}')
        tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(),tools,limits=Limits(max_model_calls=3),require_policy_grounding=True).run(
                self.scope,'Synthetic task','CM')
            self.assertEqual([],tools.calls)
            self.assertEqual('no_source_backed_policy_decision',result['policy_decision_refusals'][0]['reason'])
            self.assertEqual([],store.actions(self.scope))

    def setUp(self):
        self.scope=Scope('world','task','org','actor','patient','case')
        self.operations={'docs.create_submission_bundle','auth.finalize_provider_determination','auth.submit_authorization'}
        self.policy={'id':'policy-source','scope':self.scope.to_dict(),'outcome':'success','tool':'workspace.read_file',
            'observed_result':{'path':'/workspace/skills/managed-care-operations-handbook/references/medical-library/medical-policies/synthetic.md',
                               'text':'Synthetic eligibility depends on documented facts. Exceptions require their stated evidence.'}}
        self.case={'id':'case-source','scope':self.scope.to_dict(),'outcome':'success','tool':'cases.get_case',
                   'observed_result':{'case':{'id':'case','status':'ready_to_submit'},'form_validation':{'complete':True}}}
        self.state={'scope':self.scope.to_dict(),'policy_grounding_required':True,'evidence':[self.policy,self.case]}
        self.args={'policy_name':'Synthetic policy','applicability':'Assigned service and plan match this source.',
            'policy_sources':[{'evidence_id':'policy-source','path':'/text','quote':'Synthetic eligibility depends on documented facts.'}],
            'case_evidence_ids':['case-source'],'assessment':'Compare the documented facts and any exceptions; semantic correctness is not a software verdict.',
            'unresolved_questions':[],'decision':'Worker chooses the supported action.',
            'applies_to':sorted(self.operations),'bound_arguments':{'auth.finalize_provider_determination':{'final_action':'submit_pa'}}}

    def test_complete_forms_and_ready_state_do_not_substitute_for_policy_sources(self):
        self.assertEqual('no_source_backed_policy_decision',check_decision(self.state,'auth.submit_authorization',{},self.scope.to_dict()))
        record_decision(self.state,self.args,self.operations,self.scope.to_dict())
        self.assertIsNone(check_decision(self.state,'auth.submit_authorization',{},self.scope.to_dict()))
        self.assertIsNone(check_decision(self.state,'auth.finalize_provider_determination',{'final_action':'submit_pa'},self.scope.to_dict()))

    def test_worker_can_choose_non_submission_with_unresolved_facts(self):
        args=copy.deepcopy(self.args);args['applies_to']=['auth.finalize_provider_determination']
        args['bound_arguments']['auth.finalize_provider_determination']['final_action']='gather_more_evidence'
        args['unresolved_questions']=['A required fact is not yet established.']
        record_decision(self.state,args,self.operations,self.scope.to_dict())
        self.assertIsNone(check_decision(self.state,'auth.finalize_provider_determination',{'final_action':'gather_more_evidence'},self.scope.to_dict()))
        self.assertEqual('policy_decision_action_changed',check_decision(self.state,'auth.finalize_provider_determination',{'final_action':'submit_pa'},self.scope.to_dict()))

    def test_fabricated_foreign_metadata_and_authored_sources_are_rejected(self):
        for kind in ['foreign','fabricated','metadata','chart_opinion','authored']:
            state=copy.deepcopy(self.state);args=copy.deepcopy(self.args)
            if kind=='foreign':state['evidence'][0]['scope']={'patient':'other'}
            elif kind=='fabricated':args['policy_sources'][0]['quote']='An invented policy instruction.'
            elif kind=='metadata':
                state['evidence'][0]['observed_result']['title']='Synthetic policy document'
                args['policy_sources'][0].update(path='/title',quote='Synthetic policy document')
            elif kind=='chart_opinion':state['evidence'][0]['tool']='chart.get_patient_chart_by_patient'
            elif kind=='authored':state['evidence'][0]['tool']='workspace.write_file'
            with self.subTest(kind=kind),self.assertRaises(ValueError):record_decision(state,args,self.operations,self.scope.to_dict())

    def test_tool_returned_policy_text_is_accepted_without_forcing_file_reads(self):
        state=copy.deepcopy(self.state);state['evidence'][0].update(tool='policies.get_policy',
            observed_result={'structuredContent':{'id':'policy-id','text':self.policy['observed_result']['text']}})
        record_decision(state,self.args,self.operations,self.scope.to_dict())
        self.assertIsNone(check_decision(state,'auth.submit_authorization',{},self.scope.to_dict()))

    def test_file_citation_accepts_exact_retrieved_path_or_infers_text_without_new_file_access(self):
        for location in ('exact_file','implicit','typed_pointer','unobserved_file'):
            state=copy.deepcopy(self.state);args=copy.deepcopy(self.args);citation=args['policy_sources'][0]
            citation.pop('path')
            if location=='exact_file':citation['path']=self.policy['observed_result']['path']
            elif location=='typed_pointer':citation['text_pointer']='/text'
            elif location=='unobserved_file':citation['path']='/some/other/unread-policy.md'
            if location=='unobserved_file':
                with self.assertRaisesRegex(ValueError,'EXACT|exactly match'):record_decision(state,args,self.operations,self.scope.to_dict())
            else:
                record=record_decision(state,args,self.operations,self.scope.to_dict())
                self.assertEqual('/text',record['policy_sources'][0]['path'])
                self.assertIsNone(check_decision(state,'auth.submit_authorization',{},self.scope.to_dict()))

    def test_changed_scope_or_changed_source_invalidates_record(self):
        record_decision(self.state,self.args,self.operations,self.scope.to_dict())
        other=dict(self.scope.to_dict(),patient='other')
        self.assertEqual('policy_decision_scope_changed',check_decision(self.state,'auth.submit_authorization',{},other))
        self.state['evidence'][0]['observed_result']['text']+=' Changed.'
        self.assertEqual('policy_decision_source_changed',check_decision(self.state,'auth.submit_authorization',{},self.scope.to_dict()))

    def test_source_only_citation_captures_returned_text_and_not_unread_file_content(self):
        args=copy.deepcopy(self.args)
        args['policy_sources']=[{'evidence_id':'policy-source'}]
        self.policy['observed_result'].update(offset_chars=500,total_chars=5000)
        record=record_decision(self.state,args,self.operations,self.scope.to_dict())
        source=record['policy_sources'][0]
        self.assertEqual(self.policy['observed_result']['text'],source['quote'])
        self.assertEqual(0,source['start'])
        self.assertEqual(len(source['quote']),source['end'])
        self.assertIsNone(check_decision(self.state,'auth.submit_authorization',{},self.scope.to_dict()))

    def test_passage_range_captures_unicode_exactly_and_detects_receipt_tampering(self):
        self.policy['observed_result']['text']='Header\nEligibility — αβγ.\nUnrelated clause.'
        args=copy.deepcopy(self.args)
        args['policy_sources']=[{'evidence_id':'policy-source','start':7,'end':25}]
        source=record_decision(self.state,args,self.operations,self.scope.to_dict())['policy_sources'][0]
        self.assertEqual(self.policy['observed_result']['text'][7:25],source['quote'])
        self.assertIsNone(check_decision(self.state,'auth.submit_authorization',{},self.scope.to_dict()))
        source['start']=8
        self.assertEqual('policy_decision_source_changed',check_decision(self.state,'auth.submit_authorization',{},self.scope.to_dict()))

    def test_invalid_passage_ranges_do_not_create_records(self):
        for start,end in [(-1,30),(10,5),(5,5),(0,10000),(True,30),(0,2.5)]:
            args=copy.deepcopy(self.args)
            args['policy_sources']=[{'evidence_id':'policy-source','start':start,'end':end}]
            with self.subTest(start=start,end=end),self.assertRaises(PolicyGroundingError) as raised:
                record_decision(self.state,args,self.operations,self.scope.to_dict())
            self.assertEqual('invalid_passage_range',raised.exception.feedback['reason'])
            self.assertFalse(self.state.get('policy_decisions'))

    def test_source_references_still_reject_foreign_metadata_authored_and_conflicting_selectors(self):
        for kind in ('foreign','metadata','authored','quote_and_range'):
            state=copy.deepcopy(self.state);args=copy.deepcopy(self.args)
            args['policy_sources']=[{'evidence_id':'policy-source'}]
            if kind=='foreign':state['evidence'][0]['scope']={'patient':'other'}
            elif kind=='metadata':
                state['evidence'][0]['observed_result']['title']='Synthetic policy document'
                args['policy_sources'][0]['text_pointer']='/title'
            elif kind=='authored':state['evidence'][0]['tool']='workspace.write_file'
            else:args['policy_sources'][0].update(start=0,end=30,quote='Synthetic eligibility depends on documented facts.')
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                record_decision(state,args,self.operations,self.scope.to_dict())

    def test_invalid_quote_feedback_identifies_source_and_inspection_coordinates(self):
        args=copy.deepcopy(self.args);args['policy_sources'][0]['quote']='A paraphrased policy statement.'
        with self.assertRaises(PolicyGroundingError) as raised:
            record_decision(self.state,args,self.operations,self.scope.to_dict())
        feedback=raised.exception.feedback
        self.assertEqual('quotation_not_verbatim',feedback['reason'])
        self.assertEqual('policy-source',feedback['evidence_id'])
        self.assertEqual('/text',feedback['inspect_source']['arguments']['path'])
        self.assertEqual(0,feedback['citation_index'])

    def test_truncated_mcp_alias_cannot_bypass_policy_action_matching(self):
        name='review.submit_nurse_case_recommendation'
        slug=name.replace('.','_')[:36]
        alias='mcp_'+slug+'_'+hashlib.sha256(('chi-bench-real-case\0'+name).encode()).hexdigest()[:12]
        self.assertEqual(name,operation_name(alias))
        self.assertEqual('no_source_backed_policy_decision',check_decision(self.state,alias,{},self.scope.to_dict()))

    def test_actual_engine_blocks_bundle_then_reuses_one_record_for_supported_operations(self):
        parent=self
        class Tools:
            def __init__(self):self.calls=[]
            def list_tools(self):return [ToolSpec(n,'Synthetic operation',{'type':'object'},effect='read' if n in {'workspace.read_file','cases.get_case'} else 'write')
                for n in ['workspace.read_file','cases.get_case',*sorted(parent.operations)]]
            def call(self,name,args):
                self.calls.append(name)
                if name=='workspace.read_file':return parent.policy['observed_result']
                if name=='cases.get_case':return parent.case['observed_result']
                return {'ok':True}
        args=copy.deepcopy(self.args);args['policy_sources']=[{'evidence_id':'ev:m1:policy'}];args['case_evidence_ids']=['ev:m1:case']
        replies=[ModelReply(tool_calls=(ToolCall('policy','workspace.read_file',{}),ToolCall('case','cases.get_case',{}))),
            ModelReply(tool_calls=(ToolCall('unsupported-bundle','docs.create_submission_bundle',{}),)),
            ModelReply(tool_calls=(ToolCall('record','case.record_policy_decision',args),)),
            ModelReply(tool_calls=(ToolCall('bundle','docs.create_submission_bundle',{}),
                ToolCall('disposition','auth.finalize_provider_determination',{'final_action':'submit_pa'}),
                ToolCall('submit','auth.submit_authorization',{}))),
            ModelReply(content='{"status":"incomplete","claim":"Mechanical test only","evidence_ids":[]}')]
        class Model:
            def complete(self,*a,**k):return replies.pop(0)
        tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(),tools,limits=Limits(max_model_calls=8),require_policy_grounding=True).run(self.scope,'Synthetic task','PA')
            self.assertEqual(1,tools.calls.count('docs.create_submission_bundle'))
            self.assertEqual(1,tools.calls.count('auth.submit_authorization'))
            self.assertEqual(1,len(result['policy_decision_refusals']))
            self.assertEqual(1,len(result['policy_decisions']))
            self.assertFalse(any(a['id']=='m2:unsupported-bundle' for a in store.actions(self.scope)))


if __name__=='__main__':unittest.main()


class RequestSpecificationGroundingTests(unittest.TestCase):
    """55 of 56 saved provider runs created the case from the chart alone, before any policy read."""

    def setUp(self):
        self.scope=Scope('world','task','org','actor','patient','namespace')
        chart={'id':'chart','scope':self.scope.to_dict(),'outcome':'success','tool':'chart.get_patient_chart_by_patient',
               'observed_result':{'notes':'Synthetic ordering note recommends the requested service.'}}
        workflow={'id':'workflow','scope':self.scope.to_dict(),'outcome':'success','tool':'workspace.read_file',
                  'observed_result':{'path':'/workspace/skills/managed-care-operations-handbook/references/provider/operational/intake.md',
                                     'text':'Synthetic provider intake procedure step.'}}
        policy={'id':'policy','scope':self.scope.to_dict(),'outcome':'success','tool':'workspace.read_file',
                'observed_result':{'path':'/workspace/skills/managed-care-operations-handbook/references/pa-requirements/synthetic.md',
                                   'text':'Synthetic requirement names the covered codes and the permitted site of service.'}}
        self.state={'scope':self.scope.to_dict(),'policy_grounding_required':True,'evidence':[chart,workflow,policy]}
        self.call={'patient_id':'patient','procedure_code':'00000','diagnosis_codes':['Z00.0'],
                   'site_of_service':'office','service_type':'medical'}
        self.args={'policy_name':'Synthetic requirement','applicability':'Requested service and plan match.',
                   'policy_sources':[{'evidence_id':'policy','text_pointer':'/text'}],'case_evidence_ids':['chart'],
                   'assessment':'Actor chooses the request from documentation and requirements.','unresolved_questions':[],
                   'decision':'Create the request.','applies_to':['cases.create_from_order'],
                   'bound_arguments':{'cases.create_from_order':{k:self.call[k] for k in
                       ('procedure_code','diagnosis_codes','site_of_service','service_type')}},
                   'field_basis':[{'field':k,'basis_kind':'documented','basis':'Synthetic source states it.',
                                   'source_evidence_ids':['chart']}
                                  for k in ('procedure_code','diagnosis_codes','site_of_service','service_type')]}
        self.ops={'cases.create_from_order'}

    def check(self,call=None):
        return check_decision(self.state,'mcp_cases_create_from_order_3b90b0d81dae',call or self.call,self.scope.to_dict())

    def test_chart_only_creation_is_held_until_a_grounded_request_decision(self):
        self.assertEqual('cases.create_from_order',operation_name('mcp_cases_create_from_order_3b90b0d81dae'))
        self.assertEqual('no_source_backed_policy_decision',self.check())
        record_decision(self.state,copy.deepcopy(self.args),self.ops,self.scope.to_dict())
        self.assertIsNone(self.check())

    def test_request_needs_clinical_requirement_text_not_only_workflow_procedure(self):
        args=copy.deepcopy(self.args);args['policy_sources']=[{'evidence_id':'workflow','text_pointer':'/text'}]
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual('clinical_source_required_for_determination',caught.exception.feedback['reason'])

    def test_request_fields_must_be_bound_and_unchanged(self):
        args=copy.deepcopy(self.args);args['bound_arguments']={'cases.create_from_order':{}}
        with self.assertRaisesRegex(ValueError,'requested service fields'):
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        args['bound_arguments']={'cases.create_from_order':{'procedure_code':'00000'}}
        record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual('request_fields_not_bound',self.check())
        record_decision(self.state,copy.deepcopy(self.args),self.ops,self.scope.to_dict())
        self.assertEqual('policy_decision_action_changed',self.check({**self.call,'site_of_service':'inpatient_hospital'}))

    def test_engine_never_dispatches_an_ungrounded_case_creation(self):
        name='mcp_cases_create_from_order_3b90b0d81dae';call=self.call
        class Tools:
            calls=[]
            def list_tools(self):
                return [ToolSpec(name,'Create a provider case',{'type':'object'},effect='write')]
            def call(self,tool,args):
                self.calls.append(tool);return {'case':{'id':'case','status':'draft'}}
        replies=[ModelReply(tool_calls=(ToolCall('create',name,dict(call)),))]
        final=ModelReply(content='{"status":"incomplete","claim":"Synthetic guard test","evidence_ids":[]}')
        class Model:
            def complete(self,*a,**k):return replies.pop(0) if replies else final
        tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(),tools,limits=Limits(max_model_calls=3),require_policy_grounding=True).run(
                self.scope,'Synthetic task','PA')
            self.assertEqual([],tools.calls)
            self.assertEqual('cases.create_from_order',result['policy_decision_refusals'][0]['tool'])
            refusal=next(m['content'] for m in store.load_case(self.scope)['messages'] if m.get('tool_call_id')=='create')
            self.assertIn('site of service',refusal);self.assertIn('known_not_dispatched',refusal)


class RequestFieldBasisTests(RequestSpecificationGroundingTests):
    """t008 grounded-02: the decision analysed coverage but bound site_of_service with no stated basis."""

    def setUp(self):
        super().setUp()
        self.args['field_basis']=[{'field':k,'basis_kind':'documented','basis':'Synthetic source states it.',
                                   'source_evidence_ids':['chart']}
                                  for k in ('procedure_code','diagnosis_codes','site_of_service','service_type')]

    def test_every_bound_field_needs_its_own_cited_basis(self):
        args=copy.deepcopy(self.args);args['field_basis']=args['field_basis'][:3]
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual('request_field_basis_missing',caught.exception.feedback['reason'])
        self.assertEqual(['service_type'],caught.exception.feedback['missing_fields'])
        args.pop('field_basis')
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual(4,len(caught.exception.feedback['missing_fields']))

    def test_inferred_basis_is_recorded_and_unbound_fields_need_none(self):
        args=copy.deepcopy(self.args)
        args['bound_arguments']={'cases.create_from_order':{'procedure_code':'00000','site_of_service':'office'}}
        args['field_basis']=[args['field_basis'][0],{**args['field_basis'][2],'basis_kind':'inferred',
                                                     'source_evidence_ids':['chart','policy']}]
        record=record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual(['procedure_code','site_of_service'],[f['field'] for f in record['field_basis']])
        self.assertEqual('inferred',record['field_basis'][1]['basis_kind'])

    def test_mistyped_basis_source_names_the_id_and_duplicates_are_rejected(self):
        args=copy.deepcopy(self.args);args['field_basis'][2]['source_evidence_ids']=['chartt']
        with self.assertRaisesRegex(ValueError,"'chartt'.*closest returned ids: \['chart'\]"):
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        args=copy.deepcopy(self.args);args['field_basis'].append(copy.deepcopy(args['field_basis'][0]))
        with self.assertRaisesRegex(ValueError,'one field_basis entry per'):
            record_decision(self.state,args,self.ops,self.scope.to_dict())


class InferredFieldReferenceTests(RequestFieldBasisTests):
    """t008 grounded-03: site of service marked 'inferred, provisional' while citing only the chart."""

    def test_inferred_field_citing_only_case_records_is_refused(self):
        args=copy.deepcopy(self.args)
        args['field_basis'][2]={**args['field_basis'][2],'basis_kind':'inferred','source_evidence_ids':['chart']}
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual('inferred_field_needs_reference_source',caught.exception.feedback['reason'])
        self.assertEqual(['site_of_service'],caught.exception.feedback['fields'])

    def test_documented_field_may_rest_on_the_case_record_and_inferred_on_a_reference(self):
        args=copy.deepcopy(self.args)
        args['field_basis'][2]={**args['field_basis'][2],'basis_kind':'inferred','source_evidence_ids':['chart','workflow']}
        record=record_decision(self.state,args,self.ops,self.scope.to_dict())
        self.assertEqual(['chart'],record['field_basis'][0]['source_evidence_ids'])
        self.assertEqual('inferred',record['field_basis'][2]['basis_kind'])


class InferredFieldProceedTests(RequestFieldBasisTests):
    """t008 grounded-05: after the refusal the actor found setting rules but treated an undocumented required field as a blocker."""

    def test_refusal_asks_for_the_applied_rule_and_to_proceed_with_the_best_supported_value(self):
        args=copy.deepcopy(self.args)
        args['field_basis'][2]={**args['field_basis'][2],'basis_kind':'inferred','source_evidence_ids':['chart']}
        with self.assertRaises(PolicyGroundingError) as caught:
            record_decision(self.state,args,self.ops,self.scope.to_dict())
        text=caught.exception.feedback['instruction']
        self.assertIn('whose rule your inference applies',text)
        self.assertIn('best-supported value',text)
        self.assertIn('Do not leave a required request field blocking creation',text)
