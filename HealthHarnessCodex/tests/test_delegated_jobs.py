import copy
import json
import unittest
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from contextlib import closing

from health_harness_codex.engine import Harness
from health_harness_codex.models import Scope, ToolSpec, ToolCall, ModelReply, Limits, UnknownOutcomeError
from health_harness_codex.providers import ModelResponseFormatError, ProviderError
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract
from health_harness_codex.context import project_context


SCOPE = Scope("synthetic", "job-test", "org", "principal", "patient", "case")
RAW = "PRIVATE_HELPER_DOCUMENT " + "long source text " * 1800


class Tools:
    def __init__(self, unknown=False): self.calls = []; self.unknown = unknown
    def list_tools(self):
        return [ToolSpec("records.read", "Read synthetic current-case data", {"type": "object", "properties": {}}, effect="read"),
                ToolSpec("records.write", "Write synthetic current-case data", {"type": "object", "properties": {}}, effect="write")]
    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if self.unknown and name == "records.write": raise UnknownOutcomeError("synthetic unknown write")
        return {"status": "observed", "text": RAW}


class Model:
    def __init__(self, callback): self.callback = callback; self.seen = []; self.tools = []
    def complete(self, messages, tools, **kwargs):
        self.seen.append(copy.deepcopy(messages)); self.tools.append([t.name for t in tools])
        result = self.callback(len(self.seen), messages, tools)
        if isinstance(result, Exception): raise result
        return result


def delegated(**overrides):
    args = {"role_id": "PA-01", "question": "Find the synthetic status and cite its source.",
            "tool_names": ["records.read"], "max_model_calls": 3, "max_tool_calls": 3}
    args.update(overrides)
    return ModelReply(tool_calls=(ToolCall("job", "case.request_helper", args),))


def source_ids(messages):
    return [m["evidence_id"] for m in messages if m.get("role") == "tool" and m.get("evidence_id")]


def helper_result(messages):
    return next(json.loads(m["content"]) for m in reversed(messages)
                if m.get("role") == "tool" and m.get("name") == "case.request_helper")


def incomplete():
    return ModelReply(content=json.dumps({"status": "incomplete", "claim": "Synthetic check only.", "evidence_ids": []}))


class DelegatedJobTests(unittest.TestCase):
    def test_helper_disconnection_retry_consumes_shared_and_job_budget_without_tool_replay(self):
        def callback(n,messages,tools):
            if n==1:return delegated(max_model_calls=3)
            if n==2:return ProviderError('disconnected',failure_category='error:unknown:responseStreamDisconnected',
                proposal_dispatch_safe=True,transient_retry_eligible=True,
                diagnostics={'cleanup_confirmed':True,'request_timed_out':False})
            if n==3:return ModelReply(tool_calls=(ToolCall('read','records.read',{}),))
            if n==4:return ModelReply(content=json.dumps({'status':'complete','conclusion':'Observed.',
                'evidence_ids':source_ids(messages),'open_questions':[]}))
            receipt=helper_result(messages)
            return ModelReply(content=json.dumps({'status':'complete','claim':'Observed.',
                'evidence_ids':receipt['evidence_ids']}))
        contract=operator_observation_contract(SCOPE,'PA','records.read',[
            {'id':'read','path':'status','op':'eq','value':'observed'}])
        tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,Model(callback),tools,composition='helpers',limits=Limits(max_model_calls=5)).run(
                SCOPE,'Observe synthetic status.','PA',completion_contract=contract)
        self.assertEqual('complete',result['status'],result.get('message'))
        self.assertEqual(5,result['model_calls'])
        self.assertEqual(3,result['helper_jobs'][0]['model_calls'])
        self.assertEqual([('records.read',{})],tools.calls)
        self.assertEqual(1,len(result['model_transport_retries']))
        self.assertEqual(result['helper_jobs'][0]['id'],result['model_transport_retries'][0]['helper_id'])

    def test_tool_using_helper_has_private_context_and_owner_completes_from_real_receipt(self):
        def callback(n, messages, tools):
            if n == 1: return delegated()
            if n == 2:
                self.assertNotIn("OWNER_UNRELATED_HISTORY", json.dumps(messages))
                self.assertNotIn('No trusted task contract',json.dumps(messages))
                self.assertNotIn('Current case ledger',json.dumps(messages))
                self.assertIn('not the whole patient case',messages[0]['content'])
                self.assertEqual(["records.read"], [t.name for t in tools])
                return ModelReply(tool_calls=(ToolCall("read", "records.read", {}),), usage={"input_tokens": 5})
            if n == 3:
                self.assertIn(RAW, json.dumps(messages))
                return ModelReply(content=json.dumps({"status": "complete", "conclusion": "Status observed.",
                    "evidence_ids": source_ids(messages), "open_questions": []}), usage={"input_tokens": 7})
            self.assertNotIn("PRIVATE_HELPER_DOCUMENT", json.dumps(messages))
            receipt = helper_result(messages)
            self.assertEqual("complete", receipt["status"])
            return ModelReply(content=json.dumps({"status": "complete", "claim": "Observed status.",
                                                  "evidence_ids": receipt["evidence_ids"]}))
        tools = Tools(); model = Model(callback)
        contract = operator_observation_contract(SCOPE, "PA", "records.read", [{"id": "read", "path": "status", "op": "eq", "value": "observed"}])
        # Exercise the actual clinical projection branch as well as dispatch.
        contract["domain"] = "pa_provider"
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, tools, composition="helpers").run(
                SCOPE, "OWNER_UNRELATED_HISTORY. Obtain observed status.", "PA", completion_contract=contract)
            state = store.load_case(SCOPE)
            self.assertNotIn("helper_active", state)
            self.assertTrue(state["evidence"][0].get("helper_job_id"))
            self.assertIn("PRIVATE_HELPER_DOCUMENT", json.dumps(state["helper_jobs"][0]["messages"]))
        self.assertEqual("complete", result["status"], result.get("message"))
        self.assertEqual(4, result["model_calls"])
        self.assertEqual(2, result["tool_calls"])  # owner request + actual helper read
        self.assertEqual(12, result["usage"]["input_tokens"])
        self.assertEqual([("records.read", {})], tools.calls)

    def test_undelegated_tool_is_not_dispatched(self):
        def callback(n, messages, specs):
            if n == 1: return delegated(max_model_calls=2)
            if n in (2, 3): return ModelReply(tool_calls=(ToolCall("bad", "records.write", {}),))
            return incomplete()
        tools = Tools(); model = Model(callback)
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, tools, composition="helpers").run(SCOPE, "Read only.", "PA")
        self.assertEqual([], tools.calls)
        self.assertEqual("incomplete", result["helper_jobs"][0]["status"])
        self.assertEqual(4, result["model_calls"])

    def test_selected_writes_require_explicit_authority_and_recursive_tools_are_denied(self):
        for args in ({"tool_names": ["records.write"]}, {"tool_names": ["case.request_helper"]},
                     {"tool_names": ["case.request_identity_reselection"], "allow_writes": True}):
            tools = Tools()
            model = Model(lambda n, m, t: delegated(**args) if n == 1 else incomplete())
            with closing(CaseStore(":memory:")) as store:
                result = Harness(store, model, tools, composition="helpers").run(SCOPE, "Scoped work.", "PA")
            self.assertEqual([], tools.calls)
            self.assertEqual([], result["helper_jobs"])
            self.assertEqual(2, result["model_calls"])

    def test_delegated_unknown_write_blocks_without_replay(self):
        def callback(n, m, t):
            if n == 1: return delegated(tool_names=["records.write"], allow_writes=True)
            return ModelReply(tool_calls=(ToolCall("write", "records.write", {}),))
        tools = Tools(unknown=True); model = Model(callback)
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, tools, composition="helpers").run(SCOPE, "Scoped write.", "PA")
            self.assertTrue(store.load_case(SCOPE).get("helper_active"))
            self.assertEqual("unknown", store.actions(SCOPE)[0]["status"])
        self.assertEqual("blocked", result["status"])
        self.assertEqual(1, len(tools.calls))
        self.assertEqual(2, len(model.seen))
        self.assertEqual(1,result['helper_jobs'][0]['tool_proposals'])

    def test_helper_write_authority_is_explicit_and_can_execute_once(self):
        def callback(n,m,t):
            if n==1:return delegated(tool_names=['records.write'],allow_writes=True)
            if n==2:
                self.assertIn('delegated reads and writes',m[0]['content'])
                self.assertNotIn('This is read-only advice',m[0]['content'])
                return ModelReply(tool_calls=(ToolCall('write','records.write',{}),))
            if n==3:return ModelReply(content=json.dumps({'status':'complete','conclusion':'Observed update.',
                'evidence_ids':source_ids(m),'open_questions':[]}))
            return incomplete()
        model=Model(callback);tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,composition='helpers').run(SCOPE,'Write the authorized update.','PA')
        self.assertEqual([('records.write',{})],tools.calls)
        self.assertEqual('complete',result['helper_jobs'][0]['status'])

    def test_foreign_patient_result_is_quarantined_through_normal_dispatcher(self):
        class ForeignTools(Tools):
            def call(self,name,args):self.calls.append((name,args));return {'patient_id':'other-patient','text':'FOREIGN_SECRET'}
        model=Model(lambda n,m,t:delegated() if n==1 else ModelReply(tool_calls=(ToolCall('read','records.read',{}),)))
        tools=ForeignTools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,composition='helpers').run(SCOPE,'Read current case.','PA')
        self.assertEqual('blocked',result['status'])
        self.assertNotIn('FOREIGN_SECRET',json.dumps(result['evidence']))
        self.assertEqual(2,len(model.seen))

    def test_helper_job_budget_does_not_consume_reserved_owner_call(self):
        def callback(n, m, t):
            if n == 1: return delegated(max_model_calls=100)
            if n == 2: return ModelReply(tool_calls=(ToolCall("read", "records.read", {}),))
            return incomplete()
        tools = Tools(); model = Model(callback)
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, tools, composition="helpers", limits=Limits(max_model_calls=3)).run(SCOPE, "Read.", "PA")
        self.assertEqual(3, len(model.seen))
        self.assertEqual(1, result["helper_jobs"][0]["model_calls"])
        self.assertEqual("incomplete", result["helper_jobs"][0]["status"])
        self.assertEqual(1, len(tools.calls))

    def test_shared_tool_budget_prevents_excess_helper_group(self):
        def callback(n, m, t):
            if n == 1: return delegated(max_model_calls=2)
            if n == 2: return ModelReply(tool_calls=(ToolCall("a", "records.read", {}), ToolCall("b", "records.read", {})))
            return incomplete()
        tools = Tools(); model = Model(callback)
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, tools, composition="helpers", limits=Limits(max_tool_calls=2)).run(SCOPE, "Read.", "PA")
        self.assertEqual([], tools.calls)
        self.assertEqual(1, result["tool_calls"])
        self.assertEqual("incomplete", result["helper_jobs"][0]["status"])

    def test_failed_helper_parse_usage_is_counted_and_correction_is_bounded(self):
        def callback(n, m, t):
            if n == 1: return delegated(max_model_calls=2)
            if n in (2, 3): return ModelResponseFormatError("outer_json", {"input_tokens": 7})
            return incomplete()
        model = Model(callback)
        with closing(CaseStore(":memory:")) as store:
            result = Harness(store, model, Tools(), composition="helpers").run(SCOPE, "Read.", "PA")
        self.assertEqual(14, result["usage"]["input_tokens"])
        self.assertEqual(4, result["model_calls"])
        self.assertEqual("incomplete", result["helper_jobs"][0]["status"])

    def test_interrupted_helper_cannot_be_automatically_restarted(self):
        model = Model(lambda *args: self.fail("no model request permitted during reconciliation"))
        with closing(CaseStore(":memory:")) as store:
            store.open_case(SCOPE, "Task", "PA")
            state = store.load_case(SCOPE)
            state.update(status="running", composition="helpers", helper_active="interrupted-job")
            store.save_case(SCOPE, state, state["version"])
            result = Harness(store, model, Tools(), composition="helpers").run(SCOPE, "Task", "PA", resume=True)
        self.assertEqual("blocked", result["status"])
        self.assertEqual([], model.seen)

    def test_generic_projection_also_excludes_helper_transcript(self):
        messages = [{"role": "system", "content": "Owner"}, {"role": "user", "content": "Task"},
                    {"role": "assistant", "content": "PRIVATE_HELPER_TRANSCRIPT", "helper_job_id": "job"},
                    {"role": "tool", "content": "Concise summary"}]
        result = project_context(messages, {"scope": SCOPE.to_dict(), "evidence": [], "obligations": []}, [], 0)
        self.assertNotIn("PRIVATE_HELPER_TRANSCRIPT", json.dumps(result))

    def test_helper_cannot_consume_the_only_remaining_owner_call(self):
        model=Model(lambda n,m,t:delegated() if n==1 else incomplete());tools=Tools()
        with closing(CaseStore(':memory:')) as store:
            result=Harness(store,model,tools,composition='helpers',limits=Limits(max_model_calls=2)).run(SCOPE,'Inspect.','PA')
        self.assertEqual(2,len(model.seen))
        self.assertEqual([],result['helper_jobs'])
        self.assertEqual([],tools.calls)
        self.assertIn('helper_budget_unavailable',json.dumps(model.seen[-1]))

    def test_recorded_model_calls_distinguish_helper_and_owner_and_restore_role(self):
        from health_harness_codex.evaluation import RunRecorder,RecordingModel
        def callback(n,m,t):
            if n==1:return delegated()
            if n==2:return ModelReply(tool_calls=(ToolCall('read','records.read',{}),))
            if n==3:return ModelReply(content=json.dumps({'status':'complete','conclusion':'Read.',
                'evidence_ids':source_ids(m),'open_questions':[]}))
            return incomplete()
        with tempfile.TemporaryDirectory() as temp:
            recorder=RunRecorder(Path(temp)/'runs'/'job',{'task_id':'synthetic','model':'synthetic-model'})
            model=RecordingModel(Model(callback),recorder)
            with closing(CaseStore(':memory:')) as store:
                Harness(store,model,Tools(),composition='helpers',progress=recorder.emit).run(SCOPE,'Inspect.','PA')
            events=[json.loads(x) for x in recorder.events_path.read_text(encoding='utf-8').splitlines()]
        self.assertEqual(['workflow','helper','helper','workflow'],[e['model_role'] for e in events if e['kind']=='model_call_started'])
        self.assertEqual('workflow',recorder.metadata['model_role'])
        self.assertEqual('completed',next(e for e in events if e['kind']=='helper_finished')['status'])

    def test_long_helper_tool_retains_the_same_live_fence(self):
        class ShortLeaseStore(CaseStore):
            def __init__(self):super().__init__(':memory:');self.fences=[]
            def claim(self,scope,owner,ttl_seconds=120):
                fence=super().claim(scope,owner,ttl_seconds=.15);self.fences.append(fence);return fence
            @contextmanager
            def maintained_claim(self,scope,owner,fence,**kwargs):
                with super().maintained_claim(scope,owner,fence,ttl_seconds=.15,interval_seconds=.02):yield
        class SlowTools(Tools):
            def call(self,name,args):time.sleep(.3);return super().call(name,args)
        def callback(n,m,t):
            if n==1:return delegated()
            if n==2:return ModelReply(tool_calls=(ToolCall('read','records.read',{}),))
            if n==3:return ModelReply(content=json.dumps({'status':'complete','conclusion':'Observed.',
                'evidence_ids':source_ids(m),'open_questions':[]}))
            return incomplete()
        with closing(ShortLeaseStore()) as store:
            result=Harness(store,Model(callback),SlowTools(),composition='helpers').run(SCOPE,'Read.','PA')
            self.assertEqual(1,len(set(store.fences)))
        self.assertEqual('complete',result['helper_jobs'][0]['status'])
        self.assertEqual(4,result['model_calls'])


if __name__ == "__main__": unittest.main()
