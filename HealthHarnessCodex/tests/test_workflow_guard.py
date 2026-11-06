from __future__ import annotations

from copy import deepcopy
import json
import unittest

from health_harness_codex.engine import Harness
from health_harness_codex.models import ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.tools import ToolRegistry
from health_harness_codex.workflow_guard import PayerRoutingGuard


CASE = "case-17"
NAMES = {
    "get_alias": "triage.get",
    "set_alias": "triage.set_disposition",
    "route_alias": "triage.route_case",
    "sla_alias": "triage.calculate_sla",
    "gold_alias": "triage.check_gold_card",
    "letter_generate": "payer_letter_center.generate_letter",
    "letter_deliver": "payer_letter_center.deliver_letter",
}
SCOPE = Scope(environment="test", task="task", organization="payer", principal="actor",
              patient="patient-17", case=CASE)
SLA = {"case_id": CASE, "urgency": "standard", "deadline": "2026-10-21",
       "hours": 24, "rule_source": "observed-sla-policy"}
GOLD = {"case_id": CASE, "gold_card_eligible": True}


class Actor:
    def __init__(self, actual_names=NAMES):
        self.actual_names = dict(actual_names)
        self.calls = []
        self.results = {}
        self.failures = {}

    def bind_scope(self, scope):
        self.scope = scope

    def list_tools(self):
        return ["unchanged specs"]

    def call(self, name, arguments):
        self.calls.append((name, deepcopy(arguments)))
        if name in self.failures:
            raise self.failures[name]
        return deepcopy(self.results.get(name, {"structuredContent": None, "isError": False}))


def envelope(key, value, case_id=CASE):
    payload = {key: value}
    return {"structuredContent": payload, "isError": False}


def route_result(case_id=CASE, target="gold_card_lane"):
    return envelope("route_record", {"case_id": case_id, "recommended_target": target,
                                     "reason": "Observed actor route."})


def triage_record(disposition="auto_approval", case_id=CASE, **overrides):
    record = {"case_id": case_id, "disposition": disposition, "urgency_level": "standard",
              "sla_deadline": "2026-10-21", "sla_hours": 24,
              "sla_rule_source": "observed-sla-policy", "gold_card_eligible": True}
    record.update(overrides)
    return record


def set_arguments(disposition="auto_approval", **overrides):
    result = {"case_id": CASE, "disposition": disposition, "urgency_level": "standard",
              "sla_deadline": "2026-10-21", "sla_hours": 24,
              "sla_rule_source": "observed-sla-policy", "gold_card_eligible": True}
    result.update(overrides)
    return result


def guarded(actor=None):
    actor = actor or Actor()
    wrapped = PayerRoutingGuard(actor, actor.actual_names)
    wrapped.bind_scope(SCOPE)
    return actor, wrapped


def observe_route(actor, wrapped, target="gold_card_lane", case_id=CASE):
    actor.results["route_alias"] = route_result(case_id, target)
    return wrapped.call("route_alias", {"case_id": CASE})


def observe_absent(actor, wrapped, result_value=None):
    actor.results["get_alias"] = result_value or envelope("triage", None)
    return wrapped.call("get_alias", {"case_id": CASE})


def observe_sla_and_gold(actor, wrapped, sla=SLA, gold=GOLD):
    actor.results["sla_alias"] = envelope("sla", sla)
    actor.results["gold_alias"] = envelope("gold_card", gold)
    wrapped.call("sla_alias", {"case_id": CASE})
    wrapped.call("gold_alias", {"case_id": CASE})


def prepare_first_commit(actor, wrapped):
    observe_route(actor, wrapped)
    observe_absent(actor, wrapped)
    observe_sla_and_gold(actor, wrapped)
    actor.results["set_alias"] = envelope("triage", triage_record())


class _Model:
    def __init__(self, replies):
        self.replies = list(replies)

    def complete(self, messages, tools, *, max_output_tokens):
        return self.replies.pop(0)


class WorkflowGuardTests(unittest.TestCase):
    def test_premature_first_commit_is_refused_without_remote_write(self):
        actor, wrapped = guarded()
        refusal = wrapped.call("set_alias", set_arguments())
        self.assertEqual("route_readback_required", refusal["error"])
        self.assertTrue(refusal["known_not_dispatched"])
        self.assertEqual([], actor.calls)

    def test_policy_derived_initial_route_is_allowed_without_prior_triage_record(self):
        actor, wrapped = guarded()
        routed = observe_route(actor, wrapped)
        self.assertFalse(routed["isError"])
        self.assertEqual("pending_record", routed["_harness_consistency_annotation"]["status"])
        self.assertEqual(["route_alias"], [name for name, _ in actor.calls])
        self.assertNotIn("_harness_consistency_annotation", actor.results["route_alias"])

    def test_record_absence_observed_before_route_must_be_rechecked_after_route(self):
        actor, wrapped = guarded()
        observe_absent(actor, wrapped)
        observe_sla_and_gold(actor, wrapped)
        observe_route(actor, wrapped)
        refusal = wrapped.call("set_alias", set_arguments())
        self.assertEqual("triage_absence_unverified", refusal["error"])
        self.assertEqual("route_alias", actor.calls[-1][0])
        observe_absent(actor, wrapped)
        actor.results["set_alias"] = envelope("triage", triage_record())
        committed = wrapped.call("set_alias", set_arguments())
        self.assertFalse(committed["isError"])

    def test_first_commit_after_route_requires_explicit_absence_and_observed_metadata(self):
        actor, wrapped = guarded()
        prepare_first_commit(actor, wrapped)
        original_args = set_arguments()
        args_snapshot = deepcopy(original_args)
        original_record = triage_record()
        committed = wrapped.call("set_alias", original_args)
        self.assertEqual("present", wrapped._record_state)
        self.assertEqual(original_record, actor.results["set_alias"]["structuredContent"]["triage"])
        self.assertEqual(args_snapshot, original_args)
        self.assertFalse(committed["isError"])
        self.assertEqual("match", committed["_harness_consistency_annotation"]["status"])

    def test_wrong_lane_and_metadata_are_refused_then_correct_first_commit_succeeds(self):
        actor, wrapped = guarded()
        prepare_first_commit(actor, wrapped)

        wrong_lane = wrapped.call("set_alias", set_arguments("nurse_review"))
        wrong_sla = wrapped.call("set_alias", set_arguments(sla_hours=48))
        self.assertEqual("triage_disposition_conflicts_with_route", wrong_lane["error"])
        self.assertEqual("triage_metadata_does_not_match_observations", wrong_sla["error"])
        self.assertTrue(wrong_lane["known_not_dispatched"])
        self.assertTrue(wrong_sla["known_not_dispatched"])
        self.assertNotIn("set_alias", [name for name, _ in actor.calls])

        actor.results["set_alias"] = envelope("triage", triage_record())
        accepted = wrapped.call("set_alias", set_arguments())
        self.assertFalse(accepted["isError"])
        self.assertEqual("set_alias", actor.calls[-1][0])

    def test_declared_disposition_route_mappings_accept_compatible_first_records(self):
        mappings = (
            ("auto_approval", "gold_card_lane"),
            ("auto_approval", "notification_only_lane"),
            ("nurse_review", "standard_um"),
            ("md_review", "standard_um"),
            ("specialty_referral", "specialty_program"),
            ("delegation_transfer", "delegate"),
            ("vendor_transfer", "external_vendor"),
        )
        for disposition, target in mappings:
            with self.subTest(disposition=disposition, target=target):
                actor, wrapped = guarded()
                observe_route(actor, wrapped, target=target)
                observe_absent(actor, wrapped)
                observe_sla_and_gold(actor, wrapped)
                actor.results["set_alias"] = envelope("triage", triage_record(disposition))
                accepted = wrapped.call("set_alias", set_arguments(disposition))
                self.assertFalse(accepted["isError"])

    def test_existing_record_is_immutable_and_cannot_be_amended(self):
        actor, wrapped = guarded()
        actor.results["get_alias"] = envelope("triage", triage_record(disposition="auto_approval"))
        wrapped.call("get_alias", {"case_id": CASE})
        refusal = wrapped.call("set_alias", set_arguments("nurse_review"))
        self.assertEqual("triage_record_immutable", refusal["error"])
        self.assertTrue(refusal["known_not_dispatched"])
        self.assertEqual(["get_alias"], [name for name, _ in actor.calls])

    def test_existing_mismatch_stays_blocked_without_an_amendment_path(self):
        actor, wrapped = guarded()
        observe_route(actor, wrapped)
        actor.results["get_alias"] = envelope("triage", triage_record("nurse_review"))
        wrapped.call("get_alias", {"case_id": CASE})
        amendment = wrapped.call("set_alias", set_arguments())
        letter = wrapped.call("letter_generate", {"case_id": CASE})
        self.assertEqual("triage_record_immutable", amendment["error"])
        self.assertEqual("payer_route_consistency_blocked", letter["error"])
        self.assertEqual(["route_alias", "get_alias"], [name for name, _ in actor.calls])

    def test_repeated_commit_and_route_are_blocked(self):
        actor, wrapped = guarded()
        prepare_first_commit(actor, wrapped)
        wrapped.call("set_alias", set_arguments())
        repeat_commit = wrapped.call("set_alias", set_arguments())
        repeat_route = wrapped.call("route_alias", {"case_id": CASE})
        self.assertEqual("triage_record_immutable", repeat_commit["error"])
        self.assertEqual("route_already_observed", repeat_route["error"])
        self.assertTrue(repeat_commit["known_not_dispatched"])
        self.assertTrue(repeat_route["known_not_dispatched"])
        self.assertEqual(1, [name for name, _ in actor.calls].count("route_alias"))
        self.assertEqual(1, [name for name, _ in actor.calls].count("set_alias"))

    def test_letters_wait_until_first_record_is_committed_and_route_compatible(self):
        actor, wrapped = guarded()
        observe_route(actor, wrapped)
        pending = wrapped.call("letter_generate", {"case_id": CASE})
        self.assertEqual("triage_record_pending", pending["error"])
        observe_absent(actor, wrapped)
        observe_sla_and_gold(actor, wrapped)
        actor.results["set_alias"] = envelope("triage", triage_record())
        wrapped.call("set_alias", set_arguments())
        delivered = wrapped.call("letter_deliver", {"case_id": CASE})
        self.assertFalse(delivered.get("known_not_dispatched", False))
        self.assertEqual("letter_deliver", actor.calls[-1][0])

    def test_failed_or_foreign_get_and_metadata_observations_do_not_authorize_commit(self):
        cases = (
            {"structuredContent": {"triage": None}, "isError": True},
            {"structuredContent": {"other": None}, "isError": False},
            envelope("triage", {"case_id": "other-case"}),
        )
        for get_result in cases:
            with self.subTest(get_result=get_result):
                actor, wrapped = guarded()
                observe_route(actor, wrapped)
                observe_absent(actor, wrapped, get_result)
                observe_sla_and_gold(actor, wrapped)
                refusal = wrapped.call("set_alias", set_arguments())
                self.assertEqual("triage_absence_unverified", refusal["error"])
                self.assertNotIn("set_alias", [name for name, _ in actor.calls])

        actor, wrapped = guarded()
        observe_route(actor, wrapped)
        observe_absent(actor, wrapped)
        observe_sla_and_gold(actor, wrapped, sla={**SLA, "case_id": "other-case"})
        refusal = wrapped.call("set_alias", set_arguments())
        self.assertEqual("triage_metadata_observations_missing", refusal["error"])
        self.assertTrue(refusal["known_not_dispatched"])

        actor, wrapped = guarded()
        observe_route(actor, wrapped)
        observe_absent(actor, wrapped)
        observe_sla_and_gold(actor, wrapped)
        actor.results["gold_alias"] = envelope("gold_card", {"case_id": "other-case", "gold_card_eligible": True})
        wrapped.call("gold_alias", {"case_id": CASE})
        refusal = wrapped.call("set_alias", set_arguments())
        self.assertEqual("triage_metadata_observations_missing", refusal["error"])

    def test_sla_recalculation_replaces_previous_observation_and_gold_card_is_exact(self):
        actor, wrapped = guarded()
        prepare_first_commit(actor, wrapped)
        actor.results["sla_alias"] = envelope("sla", {**SLA, "urgency": "urgent", "hours": 6})
        wrapped.call("sla_alias", {"case_id": CASE, "level_of_urgency": "urgent"})
        refusal = wrapped.call("set_alias", set_arguments(urgency_level="standard"))
        self.assertEqual("triage_metadata_does_not_match_observations", refusal["error"])
        actor.results["set_alias"] = envelope(
            "triage", triage_record(urgency_level="urgent", sla_hours=6))
        accepted = wrapped.call("set_alias", set_arguments(urgency_level="urgent", sla_hours=6))
        self.assertFalse(accepted["isError"])

    def test_unknown_disposition_mapping_is_reported_unknown_and_not_forced(self):
        for disposition, target in (("new_disposition", "gold_card_lane"),
                                   ("auto_approval", "future_routing_lane")):
            with self.subTest(disposition=disposition, target=target):
                actor, wrapped = guarded()
                observe_route(actor, wrapped, target=target)
                observe_absent(actor, wrapped)
                observe_sla_and_gold(actor, wrapped)
                actor.results["set_alias"] = envelope("triage", triage_record(disposition))
                accepted = wrapped.call("set_alias", set_arguments(disposition))
                letter = wrapped.call("letter_generate", {"case_id": CASE})
                self.assertEqual("unknown", accepted["_harness_consistency_annotation"]["status"])
                self.assertFalse(letter.get("known_not_dispatched", False))

    def test_route_unknown_outcome_propagates_unchanged(self):
        actor, wrapped = guarded()
        failure = RuntimeError("route transport outcome is unknown")
        actor.failures["route_alias"] = failure
        with self.assertRaises(RuntimeError) as raised:
            wrapped.call("route_alias", {"case_id": CASE})
        self.assertIs(failure, raised.exception)

    def test_partial_toolset_is_unchanged(self):
        actual_names = {"get_alias": "triage.get", "route_alias": "triage.route_case"}
        actor, wrapped = guarded(Actor(actual_names))
        returned = wrapped.call("route_alias", {"case_id": CASE})
        self.assertFalse(returned["isError"])
        self.assertEqual(["route_alias"], [name for name, _ in actor.calls])

    def test_queue_alias_is_known_not_dispatched_even_when_workflow_guard_is_disabled(self):
        actor, wrapped = guarded(Actor({"queue_alias": "payer_intake_hub.list_intake_queue"}))
        refusal = wrapped.call("queue_alias", {})
        self.assertTrue(refusal["known_not_dispatched"])
        self.assertTrue(refusal["isError"])
        self.assertEqual([], actor.calls)

    def test_core_controller_works_when_optional_sla_and_gold_tools_are_absent(self):
        actual_names = {"get_alias": "triage.get", "set_alias": "triage.set_disposition",
                        "route_alias": "triage.route_case"}
        actor, wrapped = guarded(Actor(actual_names))
        actor.results["get_alias"] = envelope("triage", None)
        actor.results["route_alias"] = route_result()
        actor.results["set_alias"] = envelope("triage", {"case_id": CASE, "disposition": "auto_approval"})
        wrapped.call("route_alias", {"case_id": CASE})
        wrapped.call("get_alias", {"case_id": CASE})
        committed = wrapped.call("set_alias", {"case_id": CASE, "disposition": "auto_approval"})
        self.assertFalse(committed["isError"])
        self.assertEqual("set_alias", actor.calls[-1][0])

    def test_known_gate_refusal_is_completed_failure_not_unknown_write(self):
        actor = Actor()
        actor.actual_names = {"set_alias": "triage.set_disposition"}
        schema = {"type": "object", "required": list(set_arguments()),
                  "properties": {key: {"type": "string"} for key in
                                 ("case_id", "disposition", "urgency_level", "sla_deadline", "sla_rule_source")}
                  | {"sla_hours": {"type": "integer"}, "gold_card_eligible": {"type": "boolean"}},
                  "additionalProperties": False}
        actor.list_tools = lambda: [ToolSpec("set_alias", "set triage", schema, effect="write")]
        guard = PayerRoutingGuard(actor, NAMES)
        registry = ToolRegistry(guard)
        model = _Model([
            ModelReply(tool_calls=(ToolCall("premature", "set_alias", set_arguments()),)),
            ModelReply(content=json.dumps({
                "status": "incomplete",
                "claim": "The immutable record cannot be committed before route readback.",
                "evidence_ids": [],
            })),
        ])
        store = CaseStore(":memory:")
        try:
            final = Harness(store, model, registry).run(SCOPE, "Perform the scoped workflow", "UM")
            actions = store.actions(SCOPE)
            self.assertEqual("unresolved", final["status"])
            self.assertEqual(["completed"], [action["status"] for action in actions])
            self.assertEqual("failure", final["evidence"][0]["outcome"])
            self.assertEqual([], actor.calls)
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
