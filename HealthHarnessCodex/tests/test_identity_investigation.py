import copy
import json
import unittest

from health_harness_codex.identity_investigation import investigate_identity, _decision
from health_harness_codex.domain_profiles import _select_provider_patient
from health_harness_codex.models import ModelReply, ToolCall
from health_harness_codex.providers import ModelResponseFormatError, ProviderError


class IdentityInvestigationTests(unittest.TestCase):
    def test_zero_context_cap_does_not_stop_identity_investigation(self):
        replies=[self.reads(),ModelReply(content=json.dumps(self.decision))]
        self.assertEqual(1,investigate_identity('task',self.charts,self.assessments,
            lambda *args:replies.pop(0),max_context_chars=0))

    def test_format_recovery_preserves_completed_reads_and_counts_failed_attempt(self):
        calls=[];audit=[]
        replies=[self.reads(),ModelResponseFormatError('arguments_json'),ModelReply(content=json.dumps(self.decision))]
        def complete(messages,tools):
            calls.append(copy.deepcopy(messages));reply=replies.pop(0)
            if isinstance(reply,Exception):raise reply
            return reply
        self.assertEqual(1,investigate_identity('task',self.charts,self.assessments,complete,max_calls=3,audit=audit.append))
        self.assertEqual(3,len(calls));self.assertEqual(2,len(audit[-1]['reads']))
        self.assertEqual([{'call':2,'stage':'arguments_json'}],audit[-1]['format_errors'])
        self.assertIn('No proposal from that response was executed',calls[2][-1]['content'])
        self.assertEqual(2,sum(m['role']=='tool' for m in calls[2]))

    def test_format_failure_first_last_repeated_and_nonformat_error(self):
        unresolved=ModelReply(content=json.dumps({'status':'unresolved','candidate_index':None,
            'candidate_assessments':[],'uncertainties':['Insufficient source support']}))
        for replies,budget,status in ([ModelResponseFormatError('outer_json'),unresolved],2,'unresolved'), \
            ([self.reads(),ModelResponseFormatError('arguments_json')],2,'model_budget_exhausted'), \
            ([ModelResponseFormatError('outer_json'),ModelResponseFormatError('arguments_json')],6,'response_format_failed'):
            calls=[];audit=[]
            def complete(*args):
                calls.append(1);value=replies.pop(0)
                if isinstance(value,Exception):raise value
                return value
            self.assertIsNone(investigate_identity('task',self.charts,self.assessments,complete,max_calls=budget,audit=audit.append))
            self.assertEqual(2,len(calls));self.assertEqual(status,audit[-1]['status'])
        with self.assertRaises(ProviderError):
            investigate_identity('task',self.charts,self.assessments,
                lambda *args:(_ for _ in ()).throw(ProviderError('quota')))

    def setUp(self):
        self.charts=[{'notes':'Shared symptoms; unrelated clinician; OTHER_PATIENT_MARKER'},
                     {'notes':'Specific referring clinician and imaging; SELECTED_PATIENT_MARKER'}]
        self.assessments=[{'matches':True,'clinical_discrepancies':['Unexplained clinician difference']},
                          {'matches':True,'clinical_discrepancies':['Minor imaging discrepancy']}]
        self.decision={'status':'selected','candidate_index':1,'uncertainties':['Retain the imaging discrepancy'],
            'candidate_assessments':[
                {'candidate_index':0,'supports_selection':False,'reason':'Only generic similarities, not identifying support.',
                 'source_ids':['identity-read:1']},
                {'candidate_index':1,'supports_selection':True,'reason':'Distinctive clinician and imaging align.',
                 'source_ids':['identity-read:2']}]}

    def reads(self):
        return ModelReply(tool_calls=tuple(ToolCall(str(i),'identity.inspect_candidate',
            {'candidate_index':i,'path':'/notes','limit':4000}) for i in range(2)))

    def test_model_investigates_original_records_before_selecting_no_external_effects(self):
        original=copy.deepcopy(self.charts);calls=[];audit=[]
        replies=[self.reads(),ModelReply(content=json.dumps(self.decision))]
        def complete(messages,tools):
            calls.append(copy.deepcopy(messages))
            self.assertEqual(['identity.inspect_candidate'],[t.name for t in tools])
            return replies.pop(0)
        selected=investigate_identity('Synthetic public intake',self.charts,self.assessments,complete,audit=audit.append)
        self.assertEqual(1,selected)
        self.assertEqual(original,self.charts)
        self.assertNotIn('OTHER_PATIENT_MARKER',json.dumps(calls[0]))
        self.assertIn('OTHER_PATIENT_MARKER',json.dumps(calls[1]))
        self.assertEqual('selected',audit[-1]['status'])
        self.assertEqual(self.charts[1]['notes'],audit[-1]['reads']['identity-read:2']['view']['value'])

    def test_fabricated_cross_candidate_or_unread_references_do_not_select(self):
        for kind in ('fabricated','foreign','unread'):
            replies=[self.reads()];d=copy.deepcopy(self.decision)
            d['candidate_assessments'][0]['source_ids']=[
                'made-up' if kind=='fabricated' else 'identity-read:2' if kind=='foreign' else 'identity-read:3']
            replies.append(ModelReply(content=json.dumps(d)));audit=[]
            with self.subTest(kind=kind):
                self.assertIsNone(investigate_identity('task',self.charts,self.assessments,
                    lambda *args:replies.pop(0),max_calls=2,audit=audit.append))
                self.assertEqual('model_budget_exhausted',audit[-1]['status'])

    def test_genuine_unresolved_identity_is_preserved_not_forced(self):
        d={'status':'unresolved','candidate_index':None,'candidate_assessments':[],
           'uncertainties':['No unique identifying information is present.']}
        self.assertIsNone(investigate_identity('task',self.charts,self.assessments,
            lambda *args:ModelReply(content=json.dumps(d))))

    def test_invalid_tools_cannot_mutate_or_read_outside_candidate_set(self):
        replies=[ModelReply(tool_calls=(ToolCall('write','auth.submit_authorization',{}),
            ToolCall('foreign','identity.inspect_candidate',{'candidate_index':2}))),
            ModelReply(content=json.dumps({'status':'unresolved','candidate_index':None,
                'candidate_assessments':[],'uncertainties':['No supported selection.']}))]
        audit=[]
        self.assertIsNone(investigate_identity('task',self.charts,self.assessments,
            lambda *args:replies.pop(0),audit=audit.append))
        self.assertEqual({},audit[-1]['reads'])

    def test_context_and_read_limits_stop_before_unbounded_investigation(self):
        calls=[]
        self.assertIsNone(investigate_identity('task',self.charts,self.assessments,
            lambda *args:calls.append(args),max_context_chars=1))
        self.assertEqual([],calls)
        audit=[]
        self.assertIsNone(investigate_identity('task',self.charts,self.assessments,
            lambda *args:self.reads(),max_reads=1,audit=audit.append))
        self.assertEqual('read_budget_exhausted',audit[-1]['status'])
        self.assertEqual(1,len(audit[-1]['reads']))

    def test_selection_requires_assessment_of_every_competitor_and_unique_support(self):
        reads={'identity-read:1':{'candidate_index':0},'identity-read:2':{'candidate_index':1}}
        for kind in ('missing','both_positive','wrong_index','duplicate_key'):
            d=copy.deepcopy(self.decision)
            if kind=='missing':d['candidate_assessments'].pop()
            if kind=='both_positive':d['candidate_assessments'][0]['supports_selection']=True
            if kind=='wrong_index':d['candidate_index']=True
            text=json.dumps(d)
            if kind=='duplicate_key':text=text.replace('"status": "selected"','"status":"selected","status":"selected"')
            with self.subTest(kind=kind),self.assertRaises(ValueError):_decision(text,2,reads)

    def test_selector_uses_investigated_choice_without_automatic_order_or_score(self):
        records=[{'id':'first'},{'id':'second'}];charts=dict(zip(('first','second'),self.charts))
        def matcher(*args):return True
        seen=[]
        matcher.resolve_ambiguity=lambda task,contexts:seen.append(contexts) or 1
        result,method,count=_select_provider_patient(records,charts,'Synthetic intake',matcher)
        self.assertEqual('second',result['id']);self.assertEqual('public_instruction_investigated_match',method)
        self.assertEqual(2,count);self.assertEqual([self.charts],seen)
        matcher.resolve_ambiguity=lambda *args:None
        with self.assertRaisesRegex(ValueError,'2 positive candidates'):
            _select_provider_patient(records,charts,'Synthetic intake',matcher)
        matcher.resolve_ambiguity=lambda *args:True
        with self.assertRaisesRegex(ValueError,'unavailable candidate'):
            _select_provider_patient(records,charts,'Synthetic intake',matcher)


if __name__=='__main__':unittest.main()
