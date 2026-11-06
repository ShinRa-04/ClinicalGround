from __future__ import annotations

import json
import unittest

from health_harness_codex.engine import Harness
from health_harness_codex.models import Limits, ModelReply, Scope, ToolCall, ToolSpec, UnknownOutcomeError
from health_harness_codex.providers import ModelResponseFormatError, ProviderError
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


def make_scope(patient="patient-a", case="case-a"):
    return Scope("env", "task", "org", "principal", patient, case)


class SequenceModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def complete(self, messages, tools, *, max_output_tokens):
        self.calls.append(json.loads(json.dumps(messages)))
        if not self.responses:
            raise AssertionError("unexpected model request")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class WriteTool:
    def __init__(self, fail=None):
        self.fail = fail
        self.calls = []
        self.spec = ToolSpec("records.apply", "Apply one authorized update", {
            "type": "object", "required": ["value"],
            "properties": {"value": {"type": "string"}}, "additionalProperties": False,
        }, effect="write")

    def list_tools(self):
        return [self.spec]

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if self.fail:
            raise self.fail
        return {"status": "applied"}


class FormattingRetryTests(unittest.TestCase):
    def setUp(self):
        self.store = CaseStore(":memory:")

    def tearDown(self):
        self.store.close()

    @staticmethod
    def completed_reply(evidence_id):
        return ModelReply(content=json.dumps({"status": "complete", "claim": "Observed update completed.",
                                             "evidence_ids": [evidence_id]}),
                          usage={"input_tokens": 4, "output_tokens": 2})

    def test_format_retry_then_write_executes_once_and_keeps_failed_usage(self):
        model = SequenceModel([
            ModelResponseFormatError("outer_json", {"input_tokens": 3, "output_tokens": 1}),
            ModelReply(tool_calls=(ToolCall("write-1", "records.apply", {"value": "approved"}),),
                       usage={"input_tokens": 4}),
            self.completed_reply("ev:m2:write-1"),
        ])
        tools = WriteTool()
        scope = make_scope()
        completion_contract = operator_observation_contract(
            scope, "UM", "records.apply", [
                {"id": "write_applied", "path": "status", "op": "eq", "value": "applied"},
            ], phase="terminal_write_response")
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=5, max_tool_calls=5)).run(
            scope, "Perform the requested scoped update.", "UM",
            completion_contract=completion_contract)

        self.assertEqual("complete", result["status"])
        self.assertEqual(3, result["model_calls"])  # failed request, one retry, then post-write completion
        self.assertEqual(1, result["tool_calls"])
        self.assertEqual(1, len(tools.calls))
        self.assertEqual(1, result["model_response_format_retry_count"])
        self.assertEqual("outer_json", result["model_response_format_retries"][0]["stage"])
        self.assertEqual({"input_tokens": 11, "output_tokens": 3}, result["usage"])
        self.assertIn("Formatting correction only", model.calls[1][-1]["content"])
        self.assertEqual("Perform the requested scoped update.", model.calls[1][-2]["content"])

    def test_second_format_failure_stops_without_tools_or_second_retry(self):
        model = SequenceModel([
            ModelResponseFormatError("outer_json", {"input_tokens": 2}),
            ModelResponseFormatError("arguments_json", {"input_tokens": 5}),
        ])
        tools = WriteTool()
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=5, max_tool_calls=5)).run(
            make_scope(), "Do the scoped work.", "UM")

        self.assertEqual("error", result["status"])
        self.assertEqual(2, result["model_calls"])
        self.assertEqual(1, result["model_response_format_retry_count"])
        self.assertEqual(1, len(result["model_response_format_retries"]))
        self.assertEqual([], tools.calls)
        self.assertEqual({"input_tokens": 7}, result["usage"])

    def test_native_incomplete_output_can_correct_then_execute_one_write(self):
        model=SequenceModel([ModelResponseFormatError('output_token_limit',{'input_tokens':3}),
            ModelReply(tool_calls=(ToolCall('write-1','records.apply',{'value':'authorized'}),)),
            self.completed_reply('ev:m2:write-1')])
        tools=WriteTool();scope=make_scope()
        contract=operator_observation_contract(scope,'UM','records.apply',[
            {'id':'applied','path':'status','op':'eq','value':'applied'}],phase='terminal_write_response')
        result=Harness(self.store,model,tools,limits=Limits(max_model_calls=4)).run(
            scope,'Perform one authorized update.','UM',completion_contract=contract)
        self.assertEqual('complete',result['status'])
        self.assertEqual(1,len(tools.calls))
        self.assertEqual('authorized',tools.calls[0][1]['value'])
        self.assertEqual(1,result['model_response_format_retry_count'])
        self.assertIn('output-token limit',model.calls[1][-1]['content'])
        self.assertEqual('output_token_limit',result['model_response_format_retries'][0]['stage'])

    def test_output_limit_repeated_generations_are_counted_and_do_not_replay_actions(self):
        model=SequenceModel([ModelResponseFormatError('output_token_limit',{'input_tokens':2}) for _ in range(3)]+[
            ModelReply(tool_calls=(ToolCall('write-1','records.apply',{'value':'authorized'}),)),
            self.completed_reply('ev:m4:write-1')])
        tools=WriteTool();scope=make_scope()
        contract=operator_observation_contract(scope,'UM','records.apply',[
            {'id':'applied','path':'status','op':'eq','value':'applied'}],phase='terminal_write_response')
        result=Harness(self.store,model,tools,limits=Limits(max_model_calls=6)).run(
            scope,'Perform one update.','UM',completion_contract=contract)
        self.assertEqual('complete',result['status'])
        self.assertEqual(5,result['model_calls'])
        self.assertEqual(3,result['model_response_format_retry_count'])
        self.assertEqual(1,len(tools.calls))
        self.assertEqual(10,result['usage']['input_tokens'])

    def test_output_limit_recovery_is_bounded_and_respects_the_global_model_budget(self):
        for budget,expected_calls in [(10,4),(2,2)]:
            scope=make_scope(case='case-'+str(budget))
            model=SequenceModel([ModelResponseFormatError('output_token_limit') for _ in range(expected_calls)])
            tools=WriteTool()
            result=Harness(self.store,model,tools,limits=Limits(max_model_calls=budget)).run(scope,'One update.','UM')
            self.assertEqual('error',result['status'])
            self.assertEqual(expected_calls,result['model_calls'])
            self.assertEqual([],tools.calls)

    def test_oversized_response_uses_the_same_bounded_correction_without_dispatch(self):
        model = SequenceModel([
            ModelResponseFormatError('response_size', {'input_tokens': 2}),
            ModelResponseFormatError('response_size', {'input_tokens': 5}),
        ])
        tools = WriteTool()
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=5)).run(
            make_scope(), 'Do the scoped work.', 'UM')
        self.assertEqual('error', result['status'])
        self.assertEqual(2, result['model_calls'])
        self.assertEqual(1, result['model_response_format_retry_count'])
        self.assertEqual([], tools.calls)
        self.assertEqual({'input_tokens': 7}, result['usage'])
        self.assertIn('60000-character', model.calls[1][-1]['content'])
        self.assertIn('No proposal from it was executed', model.calls[1][-1]['content'])

    def test_later_format_failure_recovers_after_success_without_replaying_write(self):
        model = SequenceModel([
            ModelResponseFormatError("outer_json", {"input_tokens": 2}),
            ModelReply(tool_calls=(ToolCall("write-1", "records.apply", {"value": "approved"}),)),
            ModelResponseFormatError("outer_json", {"input_tokens": 5}),
            self.completed_reply("ev:m2:write-1"),
        ])
        tools = WriteTool()
        scope = make_scope()
        contract = operator_observation_contract(scope, "UM", "records.apply", [
            {"id": "write_applied", "path": "status", "op": "eq", "value": "applied"},
        ], phase="terminal_write_response")
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=5)).run(
            scope, "Perform one update.", "UM", completion_contract=contract)
        self.assertEqual("complete", result["status"])
        self.assertEqual(4, result["model_calls"])
        self.assertEqual(2, result["model_response_format_retry_count"])
        self.assertEqual([2, 4], [x["retry_model_call"] for x in result["model_response_format_retries"]])
        self.assertEqual([("records.apply", {"value": "approved"})], tools.calls)
        self.assertEqual(11, result["usage"]["input_tokens"])

    def test_failed_tool_observation_does_not_replenish_format_correction(self):
        class RejectedTool(WriteTool):
            def call(self, name, arguments):
                self.calls.append((name, arguments))
                return {"error": "rejected", "isError": True}
        tools = RejectedTool()
        model = SequenceModel([
            ModelResponseFormatError("outer_json"),
            ModelReply(tool_calls=(ToolCall("write-1", "records.apply", {"value": "approved"}),)),
            ModelResponseFormatError("outer_json"),
        ])
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=6)).run(
            make_scope(), "Do one update.", "UM")
        self.assertEqual("error", result["status"])
        self.assertEqual(3, result["model_calls"])
        self.assertEqual(1, result["model_response_format_retry_count"])
        self.assertEqual(1, len(tools.calls))

    def test_renewed_correction_still_stops_at_model_budget(self):
        tools = WriteTool()
        model = SequenceModel([
            ModelResponseFormatError("outer_json"),
            ModelReply(tool_calls=(ToolCall("write-1", "records.apply", {"value": "approved"}),)),
            ModelResponseFormatError("outer_json", {"input_tokens": 7}),
        ])
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=3)).run(
            make_scope(), "Do one update.", "UM")
        self.assertEqual("error", result["status"])
        self.assertEqual(3, len(model.calls))
        self.assertEqual(1, result["model_response_format_retry_count"])
        self.assertEqual(1, len(tools.calls))
        self.assertEqual(7, result["usage"]["input_tokens"])

    def test_model_budget_prevents_retry_but_retains_parse_usage(self):
        model = SequenceModel([ModelResponseFormatError("outer_json", {"input_tokens": 6})])
        result = Harness(self.store, model, WriteTool(), limits=Limits(max_model_calls=1, max_tool_calls=5)).run(
            make_scope(), "Do the scoped work.", "UM")

        self.assertEqual("error", result["status"])
        self.assertEqual(1, len(model.calls))
        self.assertEqual(1, result["model_calls"])
        self.assertEqual(0, result["model_response_format_retry_count"])
        self.assertEqual({"input_tokens": 6}, result["usage"])

    def test_other_provider_errors_do_not_retry(self):
        model = SequenceModel([ProviderError("authentication failed")])
        result = Harness(self.store, model, WriteTool(), limits=Limits(max_model_calls=5, max_tool_calls=5)).run(
            make_scope(), "Do the scoped work.", "UM")

        self.assertEqual("error", result["status"])
        self.assertEqual(1, len(model.calls))
        self.assertEqual(0, result["model_response_format_retry_count"])

    def test_unknown_write_after_retry_is_not_replayed_or_retried(self):
        model = SequenceModel([
            ModelResponseFormatError("outer_json"),
            ModelReply(tool_calls=(ToolCall("write-1", "records.apply", {"value": "approved"}),)),
        ])
        tools = WriteTool(UnknownOutcomeError("write outcome uncertain"))
        result = Harness(self.store, model, tools, limits=Limits(max_model_calls=5, max_tool_calls=5)).run(
            make_scope(), "Perform the scoped update.", "UM")

        self.assertEqual("blocked", result["status"])
        self.assertEqual(2, len(model.calls))
        self.assertEqual(1, len(tools.calls))
        self.assertEqual(1, result["model_response_format_retry_count"])

    def test_retry_counter_and_correction_are_case_local(self):
        model = SequenceModel([
            ModelResponseFormatError("outer_json"),
            ModelReply(content="No supported completion is claimed."),
            ModelReply(content="No supported completion is claimed."),
        ])
        harness = Harness(self.store, model, WriteTool(), limits=Limits(max_model_calls=5, max_tool_calls=5))
        first = harness.run(make_scope("patient-a", "case-a"), "First case task.", "UM")
        second = harness.run(make_scope("patient-b", "case-b"), "Second case task.", "UM")

        self.assertEqual(1, first["model_response_format_retry_count"])
        self.assertEqual(0, second["model_response_format_retry_count"])
        self.assertEqual("Second case task.", model.calls[2][-1]["content"])
        self.assertNotIn("Formatting correction only", model.calls[2][-1]["content"])


if __name__ == "__main__":
    unittest.main()
