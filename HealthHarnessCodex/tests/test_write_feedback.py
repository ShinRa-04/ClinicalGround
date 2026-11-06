import json
import unittest
from contextlib import closing

from health_harness_codex.models import ToolSpec, ToolCall, ModelReply, Scope, Limits
from health_harness_codex.write_feedback import assess_write_payload
from health_harness_codex.engine import Harness
from health_harness_codex.store import CaseStore


SPEC = ToolSpec('review.save', 'Save a synthetic review.', {'type': 'object', 'properties': {
    'line': {'type': 'integer'}, 'evaluations': {'anyOf': [{'type': 'array', 'items': {'type': 'string'}}, {'type': 'null'}]}},
    'required': ['line']}, effect='write')


class WriteFeedbackTests(unittest.TestCase):
    def test_omitted_payload_and_empty_result_are_reported_without_changing_result(self):
        result = {'review': {'criteria': []}}
        feedback = assess_write_payload(SPEC, {'line': 1}, result, 'ev:test')
        self.assertEqual(['evaluations'], feedback['omitted_collection_inputs'])
        self.assertEqual(['/review/criteria'], feedback['observed_empty_collections'])
        self.assertFalse(feedback['creates_evidence'])
        self.assertEqual({'review': {'criteria': []}}, result)

    def test_intentional_empty_payload_nonempty_result_and_reads_are_not_misclassified(self):
        self.assertIsNone(assess_write_payload(SPEC, {'line': 1, 'evaluations': []}, {'criteria': []}, 'ev:test'))
        self.assertIsNone(assess_write_payload(SPEC, {'line': 1}, {'criteria': ['present']}, 'ev:test'))
        read = ToolSpec('review.get', 'Read.', SPEC.input_schema, effect='write')
        self.assertIsNone(assess_write_payload(read, {}, {'criteria': []}, 'ev:test'))

    def test_engine_keeps_original_evidence_and_allows_model_to_correct_payload(self):
        class Tools:
            calls = []
            def list_tools(self): return [SPEC]
            def call(self, name, arguments):
                self.calls.append(arguments)
                return {'review': {'criteria': arguments.get('evaluations', [])}}

        class Model:
            calls = 0
            saw_feedback = False
            def complete(model, messages, tools, **kwargs):
                model.calls += 1
                if model.calls == 1: return ModelReply(tool_calls=(ToolCall('empty', SPEC.name, {'line': 1}),))
                if model.calls == 2:
                    observed = json.loads(messages[-1]['content'])
                    self.assertEqual([], observed['observed_result']['review']['criteria'])
                    self.assertEqual(['evaluations'], observed['execution_feedback']['omitted_collection_inputs'])
                    model.saw_feedback = True
                    return ModelReply(tool_calls=(ToolCall('content', SPEC.name, {'line': 1, 'evaluations': ['synthetic finding']}),))
                return ModelReply(content='No additional synthetic operation.')

        tools = Tools(); model = Model()
        with closing(CaseStore(':memory:')) as store:
            harness = Harness(store, model, tools, limits=Limits(max_model_calls=3))
            result = harness.run(Scope('env', 'task', 'org', 'principal', 'patient', 'case'), 'Save synthetic content.', 'UM')
            state = store.load_case(Scope('env', 'task', 'org', 'principal', 'patient', 'case'))
            self.assertTrue(model.saw_feedback)
            self.assertEqual(2, len(tools.calls))
            self.assertEqual([], state['evidence'][0]['observed_result']['review']['criteria'])
            self.assertEqual(['synthetic finding'], state['evidence'][1]['observed_result']['review']['criteria'])
            self.assertNotEqual('complete', result['status'])  # No trusted completion contract was supplied.


if __name__ == '__main__': unittest.main()
