"""Rejected optional audit attribution must not terminate an otherwise safe write."""
import json
import unittest
from contextlib import closing

from health_harness_codex.engine import Harness, _can_omit_optional_audit_actor
from health_harness_codex.models import Limits, ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


SCOPE = Scope('env', 'task', 'org', 'principal', 'patient-a', 'case-a')
FEEDBACK = {'category': 'identity_scope', 'path': '$.actor'}


class LetterTools:
    def __init__(self):
        self.calls = []
        self.spec = ToolSpec('letters.generate', 'Generate a synthetic notice; actor is optional audit attribution.', {
            'type': 'object', 'required': ['case_id'], 'properties': {
                'case_id': {'type': 'string'},
                'actor': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None},
            }, 'additionalProperties': False}, effect='write', identity_fields=('case_id',))

    def list_tools(self):
        return [self.spec]

    def call(self, name, arguments):
        self.calls.append((name, dict(arguments)))
        return {'case_id': arguments['case_id'], 'generated': True}


class Model:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.seen = []

    def complete(self, messages, tools, *, max_output_tokens):
        self.seen.append(json.loads(json.dumps(messages)))
        return next(self.replies)


class OptionalActorRecoveryTests(unittest.TestCase):
    def test_optional_actor_rejection_corrects_by_omission_and_dispatches_once(self):
        tools = LetterTools()
        model = Model([
            ModelReply(tool_calls=(ToolCall('bad', 'letters.generate', {'case_id': SCOPE.case, 'actor': 'SYSTEM'}),)),
            ModelReply(tool_calls=(ToolCall('fixed', 'letters.generate', {'case_id': SCOPE.case}),)),
            ModelReply(content=json.dumps({'status': 'complete', 'claim': 'Notice generated.',
                                          'evidence_ids': ['ev:m1:bad']})),
        ])
        contract = operator_observation_contract(SCOPE, 'UM', 'letters.generate', [
            {'id': 'generated', 'path': 'generated', 'op': 'eq', 'value': True},
        ], phase='terminal_write_response')
        with closing(CaseStore(':memory:')) as store:
            result = Harness(store, model, tools, limits=Limits(max_model_calls=4)).run(
                SCOPE, 'Generate the synthetic notice.', 'UM', completion_contract=contract)
        self.assertEqual('complete', result['status'], result.get('message'))
        self.assertEqual(1, result['pre_dispatch_validation_retry_count'])
        self.assertEqual({}, result['principal_bindings'])
        self.assertEqual([('letters.generate', {'case_id': SCOPE.case})], tools.calls)
        self.assertIn('omit the actor parameter entirely', model.seen[1][-1]['content'])
        feedback = [json.loads(m['content']) for m in model.seen[1]
                    if m.get('role') == 'tool' and m.get('tool_call_id') == 'bad'][0]
        self.assertEqual('actor', feedback['correction']['omit_optional_parameter'])
        self.assertNotIn('SYSTEM', json.dumps(feedback))

    def test_required_explicit_and_conditional_identity_requirements_are_not_omittable(self):
        base = LetterTools().spec
        args = {'case_id': SCOPE.case, 'actor': 'SYSTEM'}
        variants = [
            ToolSpec(base.name, '', {**base.input_schema, 'required': ['case_id', 'actor']}),
            ToolSpec(base.name, '', base.input_schema, identity_fields=('actor',)),
            ToolSpec(base.name, '', {**base.input_schema, 'allOf': [{'required': ['actor']}]}),
        ]
        for spec in variants:
            with self.subTest(spec=spec):
                self.assertFalse(_can_omit_optional_audit_actor(spec, args, SCOPE, FEEDBACK))

    def test_omission_does_not_mask_other_scope_or_schema_violations(self):
        spec = LetterTools().spec
        for args in ({'case_id': 'other-case', 'actor': 'SYSTEM'},
                     {'case_id': SCOPE.case, 'actor': 'SYSTEM', 'unknown': 1}):
            self.assertFalse(_can_omit_optional_audit_actor(spec, args, SCOPE, FEEDBACK))
        self.assertFalse(_can_omit_optional_audit_actor(spec, {'case_id': SCOPE.case}, SCOPE,
                                                      {**FEEDBACK, 'path': '$.case_id'}))

    def test_repeated_bad_actor_stops_without_dispatch_or_unbounded_retry(self):
        tools = LetterTools()
        model = Model([ModelReply(tool_calls=(ToolCall(str(i), 'letters.generate',
            {'case_id': SCOPE.case, 'actor': 'SYSTEM'}),)) for i in range(2)])
        with closing(CaseStore(':memory:')) as store:
            result = Harness(store, model, tools, limits=Limits(max_model_calls=5)).run(
                SCOPE, 'Generate a synthetic notice.', 'UM')
        self.assertEqual('error', result['status'])
        self.assertEqual(2, result['model_calls'])
        self.assertEqual(1, result['pre_dispatch_validation_retry_count'])
        self.assertEqual([], tools.calls)


if __name__ == '__main__':
    unittest.main()
