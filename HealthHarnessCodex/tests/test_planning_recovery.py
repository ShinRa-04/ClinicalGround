import copy
import json
import unittest
from contextlib import closing

from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope,ToolSpec,ToolCall,ModelReply,Limits,IsolationError
from health_harness_codex.planning import record_blocker,record_note,observe_progress,progress_recovery,working_record_view
from health_harness_codex.working_set import inspect_source,missing_path_feedback
from health_harness_codex.retrieval import retrieve_evidence
from health_harness_codex.store import CaseStore


SCOPE=Scope('synthetic','task','org','principal','patient','case')


def state():
    return {'scope':SCOPE.to_dict(),'messages':[{'role':'system','content':'Source rules'},
            {'role':'user','content':'Task'}],'evidence':[],'status':'running','model_calls':1,'obligations':[]}


def evidence(s,key,value,tool='records.read'):
    e={'id':key,'scope':SCOPE.to_dict(),'outcome':'success','tool':tool,'observed_result':value}
    s['evidence'].append(e);return e


class PlanningRecoveryTests(unittest.TestCase):
    def test_absence_is_in_original_not_a_partial_preview_and_root_slash_is_explained(self):
        data={'documents':['long data'*1000],'triage':{'status':'review'}}
        result=missing_path_feedback(data,'/catalog')
        self.assertEqual('absent_in_original_observation',result['field_status'])
        self.assertEqual(['documents','triage'],result['available_fields'])
        self.assertFalse(result['partial'])
        self.assertIn('empty string',missing_path_feedback(data,'/')['instruction'])
        self.assertTrue(inspect_source(data,'',max_chars=100)['partial'])
        self.assertEqual('review',inspect_source(data,'/triage/status')['value'])
        self.assertEqual(1,missing_path_feedback({'items':[1]},'/items/9')['array_length'])

    def test_batch_retrieval_preserves_absence_feedback_and_successful_siblings(self):
        s=state();evidence(s,'ev:one',{'documents':[{'name':'synthetic'}]})
        result=retrieve_evidence(s,[{'id':'ev:one','paths':['/catalog','/documents']}])
        fields=result['results'][0]['fields']
        self.assertEqual('source_path_absent',fields[0]['error'])
        self.assertEqual([{'name':'synthetic'}],fields[1]['value'])

    def test_optional_catalog_is_not_promoted_to_a_mandatory_requirement(self):
        s=state();spec=ToolSpec('review.save','Save supported criteria',{'type':'object','required':['id'],
            'properties':{'id':{'type':'string'},'catalog':{'type':'string'}}})
        base={'id':'b','blocked_action':'save review','claim':'Need the catalog','basis_kind':'tool_field','tool_name':spec.name}
        for field,support in [('id','schema_required_field'),('catalog','schema_optional_field'),
                              ('other','field_not_declared_in_input_contract')]:
            result=record_blocker(s,{**base,'field_name':field},[spec])
            self.assertEqual(support,result['support'])
            self.assertFalse(result['facts']['clinical_interpretation_verified'])

    def test_nested_criterion_contract_uses_its_own_required_list(self):
        s=state();spec=ToolSpec('review.save','Save',{'type':'object','$defs':{'Criterion':{
            'type':'object','required':['label'],'properties':{'label':{'type':'string'},'version':{'type':'string'}}}},
            'properties':{'items':{'type':'array','items':{'$ref':'#/$defs/Criterion'}}}})
        result=record_blocker(s,{'id':'b','blocked_action':'review','claim':'Version required','basis_kind':'tool_field',
            'tool_name':spec.name,'schema_path':'/$defs/Criterion','field_name':'version'},[spec])
        self.assertEqual('schema_optional_field',result['support'])
        self.assertEqual(['label'],result['facts']['required_input_fields'])

    def test_policy_claim_captures_original_slice_but_does_not_certify_interpretation(self):
        s=state();text='Synthetic requirement: documented consent must precede this action.'
        evidence(s,'ev:policy',{'path':'/workspace/skills/managed-care-operations-handbook/references/medical-library/synthetic.md',
                             'text':text},'workspace.read_file')
        args={'id':'b','blocked_action':'synthetic action','claim':'Consent is required','basis_kind':'policy',
              'sources':[{'evidence_id':'ev:policy','path':'/text','start':0,'end':len(text)}]}
        result=record_blocker(s,args,[])
        self.assertEqual(text,result['facts']['source_references'][0]['text'])
        self.assertEqual('policy_passage_provenance_verified',result['support'])
        self.assertFalse(result['facts']['clinical_interpretation_verified'])
        args['sources'][0]['evidence_id']='ev:not-observed'
        with self.assertRaises(IsolationError):record_blocker(s,args,[])

    def test_observed_absence_is_not_a_verified_necessity_and_hypotheses_remain_hypotheses(self):
        s=state();evidence(s,'ev:read',{'status':'draft'})
        result=record_blocker(s,{'id':'b','blocked_action':'save','claim':'Missing catalog','basis_kind':'observed_gap',
            'sources':[{'evidence_id':'ev:read','path':'/catalog'}]},[])
        self.assertEqual('observation_referenced_necessity_unverified',result['support'])
        self.assertEqual('source_path_absent',result['facts']['source_references'][0]['error'])
        result=record_blocker(s,{'id':'b','blocked_action':'save','claim':'Maybe needed','basis_kind':'hypothesis'},[])
        self.assertEqual('unverified_hypothesis',result['support'])
        self.assertEqual(1,len(s['prerequisite_records']))

    def test_blank_observed_text_is_citable_as_a_gap_but_not_as_policy_authority(self):
        s=state();evidence(s,'ev:one',{'detail':''})
        args={'id':'b','blocked_action':'review','claim':'Detail missing','basis_kind':'observed_gap',
              'sources':[{'evidence_id':'ev:one','path':'/detail'}]}
        result=record_blocker(s,args,[])
        self.assertTrue(result['facts']['source_references'][0]['empty'])
        self.assertEqual('present',result['facts']['source_references'][0]['field_status'])
        with self.assertRaises(ValueError):record_blocker(s,{**args,'basis_kind':'policy'},[])

    def test_case_notes_upsert_with_source_provenance_and_do_not_create_evidence(self):
        s=state();evidence(s,'ev:one',{'status':'review'})
        record_note(s,{'id':'n','kind':'finding','summary':'Observed review state','evidence_ids':['ev:one']})
        record_note(s,{'id':'n','kind':'question','summary':'What remains?','status':'resolved'})
        self.assertEqual(1,len(s['working_notes']))
        self.assertEqual(1,len(s['evidence']))
        with self.assertRaises(ValueError):record_note(s,{'id':'x','kind':'finding','summary':'Unsupported'})
        s['evidence'][0]['scope']={**SCOPE.to_dict(),'patient':'other'}
        with self.assertRaises(IsolationError):record_note(s,{'id':'x','kind':'finding','summary':'Cross case','evidence_ids':['ev:one']})

    def test_older_notes_are_paged_and_helper_transcripts_are_not_returned(self):
        s=state()
        for i in range(12):record_note(s,{'id':f'n{i}','kind':'question','summary':f'Question {i}'})
        first=working_record_view(s,{'kind':'notes','limit':5})
        self.assertEqual(5,first['next_offset'])
        self.assertEqual('n5',working_record_view(s,{'kind':'notes','offset':5})['items'][0]['id'])
        s['helper_jobs']=[{'id':'h','status':'complete','messages':[{'content':'PRIVATE_TRANSCRIPT'}],'result':{'conclusion':'Short result'}}]
        result=working_record_view(s,{'kind':'jobs'})
        self.assertNotIn('PRIVATE_TRANSCRIPT',json.dumps(result))
        self.assertEqual('Short result',result['items'][0]['result']['conclusion'])

    def test_local_read_of_same_data_under_new_source_ids_does_not_fake_progress(self):
        s=state();evidence(s,'ev:one',{'v':1});evidence(s,'ev:two',{'v':1})
        observe_progress(s,'case.inspect_evidence',{'id':'ev:one'},{'id':'ev:one','value':1},'ev:one','success')
        s['model_calls']=2
        result=observe_progress(s,'case.inspect_evidence',{'id':'ev:two'},{'id':'ev:two','value':1},'ev:two','success')
        self.assertFalse(result['new_source_information'])
        self.assertEqual(1,s['last_information_progress_call'])

    def test_alternating_unchanged_queries_do_not_reset_information_progress(self):
        s=state()
        for call,kind in enumerate(('work','blockers','work','blockers','work','blockers'),1):
            s['model_calls']=call
            result={'kind':kind,'items':[{'id':kind,'status':'open'}]}
            feedback=observe_progress(s,'case.get_working_record',{'kind':kind},result,f'local:{call}','success')
            if call>2:self.assertFalse(feedback['new_source_information'])
        self.assertEqual(2,s['last_information_progress_call'])
        self.assertEqual(2,len(s['operation_query_progress']))
        self.assertTrue(progress_recovery(s))
        self.assertFalse(progress_recovery(s))
        s['model_calls']=7
        self.assertIsNone(observe_progress(s,'case.get_working_record',{'kind':'work'},
            {'kind':'work','items':[{'id':'work','status':'closed'}]},'local:changed','success'))
        self.assertEqual(7,s['last_information_progress_call'])
        self.assertEqual('running',s['status'])

    def test_authored_labels_are_allowed_only_where_contract_allows_and_case_identity_stays_checked(self):
        from health_harness_codex.schema import validate_arguments
        props={'case_id':{'type':'string'},'criterion_id':{'type':'string'}}
        free=ToolSpec('review.save','Save a new sourced review label',{'type':'object','properties':props,'required':['case_id','criterion_id']})
        validate_arguments(free,{'case_id':'case','criterion_id':'source-section-label'},SCOPE)
        with self.assertRaises(IsolationError):validate_arguments(free,{'case_id':'other','criterion_id':'source-section-label'},SCOPE)
        supplied=ToolSpec('review.save','Use supplied public catalog labels',{'type':'object','properties':{
            **props,'criterion_id':{'type':'string','enum':['supplied-label']}},'required':['case_id','criterion_id']})
        with self.assertRaises(ValueError):validate_arguments(supplied,{'case_id':'case','criterion_id':'source-section-label'},SCOPE)

    def test_unchanged_data_gets_one_replan_per_information_state_without_forced_action(self):
        s=state()
        self.assertIsNone(observe_progress(s,'records.read',{}, {'value':1},'ev:one','success'))
        for call in (2,3,4):
            s['model_calls']=call
            feedback=observe_progress(s,'records.read',{}, {'value':1},f'ev:{call}','success')
            self.assertFalse(feedback['new_source_information'])
        self.assertTrue(progress_recovery(s))
        self.assertEqual('running',s['status'])
        self.assertIn('reassess',s['messages'][-1]['content'].lower())
        self.assertFalse(progress_recovery(s))
        s['model_calls']=5
        self.assertIsNone(observe_progress(s,'records.read',{}, {'value':2},'ev:new','success'))
        self.assertEqual(5,s['last_information_progress_call'])
        self.assertFalse(progress_recovery(s))

    def test_different_arguments_with_same_business_result_do_not_fake_progress(self):
        s=state();observe_progress(s,'records.save',{'value':1},{'saved':[]},'ev:one','success')
        s['model_calls']=2
        result=observe_progress(s,'records.save',{'value':2},{'saved':[]},'ev:two','success')
        self.assertFalse(result['new_source_information'])
        self.assertEqual(1,s['last_information_progress_call'])

    def test_controller_exposes_absent_path_without_generic_keyerror(self):
        class Model:
            def __init__(self):self.calls=0;self.seen=[]
            def complete(self,messages,tools,**kw):
                self.calls+=1;self.seen.append(copy.deepcopy(messages))
                if self.calls==1:return ModelReply(tool_calls=(ToolCall('read','records.read',{}),))
                if self.calls==2:return ModelReply(tool_calls=(ToolCall('inspect','case.inspect_evidence',{'id':'ev:m1:read','path':'/missing'}),))
                return ModelReply(content=json.dumps({'status':'incomplete','claim':'Synthetic only','evidence_ids':['ev:m1:read']}))
        class Tools:
            def list_tools(self):return [ToolSpec('records.read','read',{'type':'object'},effect='read')]
            def call(self,*a):return {'documents':[]}
        model=Model()
        with closing(CaseStore(':memory:')) as store:
            Harness(store,model,Tools(),limits=Limits(max_model_calls=3)).run(SCOPE,'Inspect a source.','PA')
        result=json.loads(model.seen[-1][-1]['content'])
        self.assertEqual('source_path_absent',result['error'])
        self.assertEqual(['documents'],result['available_fields'])

    def test_controller_requests_replan_after_unchanged_reads_without_terminating(self):
        class Model:
            def __init__(self):self.calls=0;self.last=None
            def complete(self,messages,tools,**kw):
                self.calls+=1;self.last=copy.deepcopy(messages)
                if self.calls<=4:return ModelReply(tool_calls=(ToolCall(f'read{self.calls}','records.read',{}),))
                return ModelReply(content=json.dumps({'status':'complete','claim':'Observed result.','evidence_ids':['ev:m4:read4']}))
        class Tools:
            def list_tools(self):return [ToolSpec('records.read','read',{'type':'object'},effect='read')]
            def call(self,*a):return {'status':'observed'}
        from health_harness_codex.synthetic_contracts import operator_observation_contract
        contract=operator_observation_contract(SCOPE,'PA','records.read',[{'id':'s','path':'status','op':'eq','value':'observed'}])
        model=Model()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,Tools(),limits=Limits(max_model_calls=5)).run(SCOPE,'Read current status.','PA',completion_contract=contract)
        self.assertEqual('complete',result['status'])
        self.assertEqual(1,len(result['progress_recoveries']))
        self.assertIn('Progress review:',json.dumps(model.last))


if __name__=='__main__':unittest.main()
