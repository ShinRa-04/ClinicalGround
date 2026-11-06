"""Protocol boundary audit: malformed batches, code-owned IDs, usage and recovery."""
import copy
import json
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from health_harness_codex.codex_provider import CodexSessionModel, _reply_schema
from health_harness_codex.engine import Harness
from health_harness_codex.evaluation import RecordingModel, RunRecorder, classify_result
from health_harness_codex.models import Limits, ModelReply, Scope, ToolCall, ToolSpec, UnknownOutcomeError
from health_harness_codex.providers import ModelResponseFormatError, ProviderError
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


SCOPE=Scope('synthetic','protocol-audit','org','worker','patient','case')
SPEC=ToolSpec('records.apply','Write one synthetic result.',{'type':'object','properties':{'value':{'type':'string'}},
    'required':['value'],'additionalProperties':False},effect='write')
USAGE={'input_tokens':11,'output_tokens':3,'total_tokens':14}


def decode(calls, request_key='a'*64):
    return CodexSessionModel._parse_reply(json.dumps({'content':'','tool_calls':calls}),[SPEC],USAGE,request_key=request_key)


class WriteTools:
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def list_tools(self):return [SPEC]
    def call(self,name,args):
        self.calls.append((name,copy.deepcopy(args)))
        if self.fail:raise UnknownOutcomeError('Synthetic write outcome uncertain.')
        return {'saved':True}


def contract():
    return operator_observation_contract(SCOPE,'UM',SPEC.name,[{'id':'saved','path':'saved','op':'eq','value':True}],
                                        phase='terminal_write_response')


class BoundaryAuditTests(unittest.TestCase):
    def test_model_schema_has_no_request_id_but_preserves_domain_id_arguments(self):
        spec=ToolSpec('read','Read a domain ID.',{'type':'object','properties':{'id':{'type':'string'}},'required':['id']})
        schema=_reply_schema([spec]);variant=schema['properties']['tool_calls']['items']['anyOf'][0]
        self.assertEqual(['name','arguments'],variant['required'])
        self.assertNotIn('id',variant['properties'])
        self.assertIn('id',schema['$defs']['tool_0']['properties'])

    def test_code_assigns_unique_stable_labels_and_ignores_invalid_legacy_labels(self):
        for label in ('same','',None,[],1,'x'*300):
            with self.subTest(label_type=type(label).__name__):
                calls=[{'id':label,'name':SPEC.name,'arguments':{'value':'first'}},
                       {'id':label,'name':SPEC.name,'arguments':{'value':'second'}}]
                reply=decode(calls);again=decode(calls)
                self.assertEqual(2,len({c.id for c in reply.tool_calls}))
                self.assertEqual([c.id for c in reply.tool_calls],[c.id for c in again.tool_calls])
                self.assertEqual(['first','second'],[c.arguments['value'] for c in reply.tool_calls])
                self.assertEqual('req_'+'a'*64+'_1',reply.tool_calls[0].id)

    def test_request_keys_separate_requests_without_changing_clinical_arguments(self):
        calls=[{'name':SPEC.name,'arguments':{'value':'unchanged'}}]
        self.assertNotEqual(decode(calls,'a'*64).tool_calls[0].id,decode(calls,'b'*64).tool_calls[0].id)
        self.assertEqual(calls[0]['arguments'],decode(calls).tool_calls[0].arguments)
        with self.assertRaises(ValueError):decode(calls,'invalid-code-key')

    def test_response_contract_failure_matrix_preserves_usage_and_no_raw_payload(self):
        examples=[
            ('not json','outer_json'),('[]','reply_shape'),
            ('{"content":"x"}','reply_shape'),('{"content":null,"tool_calls":[]}','content_shape'),
            ('{"content":"","tool_calls":{}}','tool_calls_shape'),
            (json.dumps({'content':'','tool_calls':[None]}),'tool_call_shape'),
            (json.dumps({'content':'','tool_calls':[{'name':SPEC.name,'arguments_json':'{}'}]}),'tool_call_shape'),
            (json.dumps({'content':'','tool_calls':[{'name':'private-unknown-name','arguments':{}}]}),'tool_name'),
            (json.dumps({'content':'','tool_calls':[{'name':SPEC.name,'arguments':[]}]}),'arguments_shape'),
            ('{"content":"","content":"private-secret","tool_calls":[]}','duplicate_json_key'),
            ('{"content":"","tool_calls":[{"name":"records.apply","arguments":{"value":NaN}}]}','nonfinite_json'),
            (json.dumps({'content':'','tool_calls':[{'name':SPEC.name,'arguments':{}}]*33}),'tool_calls_shape'),
        ]
        for text,stage in examples:
            with self.subTest(stage=stage):
                with self.assertRaises(ModelResponseFormatError) as raised:
                    CodexSessionModel._parse_reply(text,[SPEC],USAGE)
                error=raised.exception
                self.assertEqual(stage,error.stage)
                self.assertEqual(USAGE,error.usage)
                self.assertTrue(error.proposal_dispatch_safe)
                self.assertNotIn('private-',str(error)+json.dumps(error.diagnostics))
                self.assertEqual('response_format:'+stage,error.failure_category)

    def test_resource_rejection_is_not_an_unbounded_retry_and_retains_known_usage(self):
        text=json.dumps({'content':'','tool_calls':[{'name':SPEC.name,'arguments':{'value':'x'*33000}}]})
        with self.assertRaises(ProviderError) as raised:CodexSessionModel._parse_reply(text,[SPEC],USAGE)
        self.assertNotIsInstance(raised.exception,ModelResponseFormatError)
        self.assertEqual('response_limit:arguments',raised.exception.failure_category)
        self.assertEqual(USAGE,raised.exception.usage)

    def test_bad_sibling_rejects_entire_batch_then_corrected_write_executes_once(self):
        class Model:
            calls=0
            def complete(self,messages,tools,**kwargs):
                self.calls+=1
                if self.calls==1:
                    return decode([{'name':SPEC.name,'arguments':{'value':'never-execute'}},
                                   {'name':SPEC.name,'arguments':'invalid'}])
                if self.calls==2:
                    self.reply=decode([{'name':SPEC.name,'arguments':{'value':'execute-once'}}],request_key='b'*64)
                    return self.reply
                return ModelReply(content=json.dumps({'status':'complete','claim':'Saved observed result.',
                    'evidence_ids':['ev:m2:'+self.reply.tool_calls[0].id]}),usage=USAGE)
        model=Model();tools=WriteTools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,limits=Limits(max_model_calls=4)).run(SCOPE,'Apply a synthetic update.','UM',completion_contract=contract())
        self.assertEqual('complete',result['status'],result['message'])
        self.assertEqual([(SPEC.name,{'value':'execute-once'})],tools.calls)
        self.assertEqual(1,result['model_response_format_retry_count'])
        self.assertEqual(33,result['usage']['input_tokens'])
        self.assertEqual('arguments_shape',result['model_response_format_retries'][0]['stage'])

    def test_non_codex_backend_duplicate_ids_are_rejected_before_any_dispatch(self):
        class Model:
            calls=0
            def complete(self,messages,tools,**kwargs):
                self.calls+=1
                if self.calls==1:return ModelReply(tool_calls=(ToolCall('same',SPEC.name,{'value':'one'}),
                    ToolCall('same',SPEC.name,{'value':'two'})),usage=USAGE)
                if self.calls==2:return ModelReply(tool_calls=(ToolCall('corrected',SPEC.name,{'value':'one'}),),usage=USAGE)
                return ModelReply(content=json.dumps({'status':'complete','claim':'Saved result.',
                    'evidence_ids':['ev:m2:corrected']}),usage=USAGE)
        tools=WriteTools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(),tools).run(SCOPE,'Apply one result.','UM',completion_contract=contract())
        self.assertEqual('complete',result['status'])
        self.assertEqual([(SPEC.name,{'value':'one'})],tools.calls)
        self.assertEqual('tool_call_id',result['model_response_format_retries'][0]['stage'])

    def test_repeated_malformed_response_stops_after_one_correction_without_dispatch(self):
        class Model:
            def complete(self,*args,**kwargs):return decode([{'name':SPEC.name,'arguments':[]}])
        tools=WriteTools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(),tools,limits=Limits(max_model_calls=8)).run(SCOPE,'Apply one result.','UM')
        self.assertEqual('error',result['status'])
        self.assertEqual(2,result['model_calls'])
        self.assertEqual([],tools.calls)
        self.assertEqual(22,result['usage']['input_tokens'])
        self.assertEqual('response_contract_failure',classify_result(result))

    def test_failed_provider_response_usage_is_recorded_without_claiming_missing_usage(self):
        class Model:
            def complete(self,*args,**kwargs):
                raise ProviderError('Response too large.',failure_category='response_limit:arguments',usage=USAGE)
        with tempfile.TemporaryDirectory() as temp:
            rec=RunRecorder(Path(temp)/'runs'/'synthetic',{})
            with closing(CaseStore(':memory:')) as store:
                result=Harness(store,RecordingModel(Model(),rec),WriteTools()).run(SCOPE,'Apply one result.','UM')
            events=[json.loads(line) for line in rec.events_path.read_text(encoding='utf-8').splitlines()]
        failed=next(e for e in events if e['kind']=='model_call_failed')
        self.assertEqual(USAGE,failed['usage'])
        self.assertEqual(USAGE,result['usage'])
        self.assertEqual('response_contract_failure',classify_result(result))

    def test_code_owned_ids_do_not_bypass_unknown_write_fencing(self):
        class Model:
            calls=0
            def complete(self,*args,**kwargs):
                self.calls+=1
                return decode([{'name':SPEC.name,'arguments':{'value':'uncertain'}}],request_key='c'*64)
        model=Model();tools=WriteTools(fail=True)
        with closing(CaseStore(':memory:')) as store:
            harness=Harness(store,model,tools)
            first=harness.run(SCOPE,'Apply one result.','UM')
            second=harness.run(SCOPE,'Apply one result.','UM',resume=True)
        self.assertEqual('blocked',first['status'])
        self.assertEqual('blocked',second['status'])
        self.assertEqual(1,model.calls)
        self.assertEqual(1,len(tools.calls))

    def test_failed_input_and_public_reply_are_private_replay_artifacts_not_console_events(self):
        class Model:
            def complete(self,*args,**kwargs):raise ProviderError('Synthetic timeout.')
            def failure_response(self):return {'text':'PRIVATE-REPLY','generation_completed':False,'text_truncated':False}
        with tempfile.TemporaryDirectory() as temp:
            rec=RunRecorder(Path(temp)/'runs'/'synthetic',{})
            with self.assertRaises(ProviderError):
                RecordingModel(Model(),rec).complete([{'role':'user','content':'PRIVATE-CASE-INPUT'}],[SPEC],max_output_tokens=10)
            capture=json.loads((rec.run_dir/'model-failures'/'call-0001.private.json').read_text(encoding='utf-8'))
            self.assertEqual('PRIVATE-CASE-INPUT',capture['request']['messages'][0]['content'])
            self.assertEqual('PRIVATE-REPLY',capture['assistant_response']['text'])
            self.assertFalse(capture['assistant_response']['generation_completed'])
            public=rec.events_path.read_text(encoding='utf-8')+rec.live_path.read_text(encoding='utf-8')
            self.assertNotIn('PRIVATE-REPLY',public)
            self.assertNotIn('PRIVATE-CASE-INPUT',public)

    def test_capture_io_failure_does_not_replace_the_original_provider_failure(self):
        class Model:
            def complete(self,*args,**kwargs):raise ProviderError('original failure')
        with tempfile.TemporaryDirectory() as temp:
            rec=RunRecorder(Path(temp)/'runs'/'synthetic',{})
            (rec.run_dir/'model-failures').write_text('not a directory',encoding='utf-8')
            with self.assertRaisesRegex(ProviderError,'original failure'):
                RecordingModel(Model(),rec).complete([],[],max_output_tokens=10)


if __name__=='__main__':unittest.main()
