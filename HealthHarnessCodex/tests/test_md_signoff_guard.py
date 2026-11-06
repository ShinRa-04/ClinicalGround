import unittest
from contextlib import closing

from health_harness_codex.workflow_guard import PayerRoutingGuard
from health_harness_codex.models import Scope, ToolSpec, ToolCall, ModelReply, Limits
from health_harness_codex.engine import Harness
from health_harness_codex.store import CaseStore


SCOPE = Scope('synthetic', 'task', 'payer', 'actor', 'patient', 'case')
NAME = 'review.submit_md_case_decision'
SPEC = ToolSpec(NAME, 'Public contract: signed_off may be false only for p2p_review.', {
    'type': 'object', 'required': ['case_id', 'decision'], 'properties': {
        'case_id': {'type': 'string'}, 'decision': {'type': 'string'}, 'signed_off': {'type': 'boolean'}}}, effect='write')


class Actor:
    def __init__(self): self.calls = []
    def list_tools(self): return [SPEC]
    def call(self, name, arguments):
        self.calls.append((name, arguments.copy()))
        return {'case_decision': {**arguments, 'id': 'synthetic-md'}}


def guarded():
    actor = Actor(); guard = PayerRoutingGuard(actor, {NAME: NAME}); guard.bind_scope(SCOPE)
    return actor, guard


class MDSignoffGuardTests(unittest.TestCase):
    def test_unsigned_non_reserved_decisions_are_rejected_before_immutable_write(self):
        for decision in ['request_info', 'approve', 'deny', 'partial_approve']:
            for value in ['omitted', False, 1]:
                actor, guard = guarded()
                args = {'case_id': SCOPE.case, 'decision': decision}
                if value != 'omitted': args['signed_off'] = value
                result = guard.call(NAME, args)
                self.assertEqual('md_signoff_contract_violation', result['error'])
                self.assertTrue(result['known_not_dispatched'])
                self.assertEqual([], actor.calls)

    def test_explicit_signoff_preserves_the_models_decision_and_reserved_p2p_remains_allowed(self):
        for decision, signed in [('request_info', True), ('approve', True), ('deny', True),
                                 ('partial_approve', True), ('p2p_review', False)]:
            actor, guard = guarded()
            args = {'case_id': SCOPE.case, 'decision': decision, 'signed_off': signed}
            result = guard.call(NAME, args)
            self.assertEqual(decision, result['case_decision']['decision'])
            self.assertEqual([(NAME, args)], actor.calls)

    def test_foreign_case_is_rejected_even_without_triage_capabilities(self):
        actor, guard = guarded()
        result = guard.call(NAME, {'case_id': 'other', 'decision': 'request_info', 'signed_off': True})
        self.assertEqual('md_decision_scope_mismatch', result['error'])
        self.assertEqual([], actor.calls)

    def test_engine_allows_model_correction_but_never_executes_unsigned_proposal(self):
        actor, guard = guarded()
        class Model:
            calls = 0
            def complete(model, messages, tools, **kwargs):
                model.calls += 1
                if model.calls == 2:
                    self.assertIn('md_signoff_contract_violation', messages[-1]['content'])
                return ModelReply(tool_calls=(ToolCall('proposal-' + str(model.calls), NAME,
                    {'case_id': SCOPE.case, 'decision': 'request_info', 'signed_off': model.calls == 2}),))
        with closing(CaseStore(':memory:')) as store:
            Harness(store, Model(), guard, limits=Limits(max_model_calls=2)).run(SCOPE, 'Perform synthetic review.', 'UM')
        self.assertEqual(1, len(actor.calls))
        self.assertIs(actor.calls[0][1]['signed_off'], True)


if __name__ == '__main__': unittest.main()
