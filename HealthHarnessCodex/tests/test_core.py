from __future__ import annotations

import tempfile
import unittest
import time
from pathlib import Path

from health_harness_codex.models import ConflictError, IsolationError, Scope, ToolSpec, UnknownOutcomeError, Limits, budget_is_reduction
from health_harness_codex.roles import roles_for, system_prompt
from health_harness_codex.schema import validate_arguments
from health_harness_codex.store import CaseStore


def scope(patient: str = "p-1", case: str = "c-1") -> Scope:
    return Scope("env", "task-1", "org", "principal", patient, case)


class CaseStoreTests(unittest.TestCase):
    def test_maintained_claim_keeps_same_fence_and_excludes_another_owner(self):
        token=self.store.claim(self.a,'owner',ttl_seconds=.5)
        with self.store.maintained_claim(self.a,'owner',token,ttl_seconds=.5,interval_seconds=.05):
            time.sleep(.7)
            self.store.assert_claim(self.a,'owner',token)
            with self.assertRaises(ConflictError):self.store.claim(self.a,'other')
        self.store.assert_claim(self.a,'owner',token)
        self.store.release(self.a,'owner',token)

    def test_renew_never_resurrects_expired_or_stale_ownership(self):
        token=self.store.claim(self.a,'owner',ttl_seconds=.001)
        time.sleep(.01)
        with self.assertRaises(ConflictError):self.store.renew(self.a,'owner',token)
        new_token=self.store.claim(self.a,'other')
        self.assertGreater(new_token,token)
        with self.assertRaises(ConflictError):self.store.renew(self.a,'owner',token)
        self.store.assert_claim(self.a,'other',new_token)

    def test_maintained_claim_rejects_result_after_ownership_changes(self):
        token=self.store.claim(self.a,'owner')
        with self.assertRaises(ConflictError):
            with self.store.maintained_claim(self.a,'owner',token):
                self.store.release(self.a,'owner',token)
                replacement=self.store.claim(self.a,'other')
        self.store.assert_claim(self.a,'other',replacement)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = CaseStore(Path(self.temp.name) / "cases.sqlite")
        self.a = scope()
        self.b = scope("p-2", "c-2")
        self.store.open_case(self.a, "Review this request", "PA")
        self.store.open_case(self.b, "Review this request", "PA")

    def tearDown(self) -> None:
        self.store.close()
        self.temp.cleanup()

    def test_cases_are_isolated_and_immutable_scope_is_checked(self) -> None:
        state = self.store.load_case(self.a)
        state["evidence"].append({"source": "only-a"})
        self.store.save_case(self.a, state, 0)
        self.assertEqual([], self.store.load_case(self.b)["evidence"])
        self.assertEqual("p-1", self.store.load_case(self.a)["scope"]["patient"])
        with self.assertRaises(ConflictError):
            self.store.open_case(self.a, "Different instruction", "PA")
        changed = self.store.load_case(self.a)
        changed["scope"] = self.b.to_dict()
        with self.assertRaises(IsolationError):
            self.store.save_case(self.a, changed, 1)

    def test_optimistic_versions_reject_stale_writers(self) -> None:
        first = self.store.load_case(self.a)
        stale = self.store.load_case(self.a)
        self.assertEqual(1, self.store.save_case(self.a, first, 0))
        with self.assertRaises(ConflictError):
            self.store.save_case(self.a, stale, 0)

    def test_lease_fence_blocks_old_owner_after_expiry_and_reclaim(self) -> None:
        fence1 = self.store.claim(self.a, "worker-a", ttl_seconds=0.02)
        with self.assertRaises(ConflictError):
            self.store.claim(self.a, "worker-b", ttl_seconds=1)
        import time
        time.sleep(0.04)
        fence2 = self.store.claim(self.a, "worker-b", ttl_seconds=1)
        self.assertGreater(fence2, fence1)
        with self.assertRaises(ConflictError):
            self.store.assert_claim(self.a, "worker-a", fence1)
        self.store.assert_claim(self.a, "worker-b", fence2)
        # A stale worker cannot mutate even if it happens to know the newest
        # optimistic version; lease fencing is checked in the write transaction.
        candidate = self.store.load_case(self.a)
        with self.assertRaises(ConflictError):
            self.store.save_case(self.a, candidate, candidate["version"], owner="worker-a", fence=fence1)
        self.store.release(self.a, "worker-b", fence2)
        candidate = self.store.load_case(self.a)
        with self.assertRaises(ConflictError):
            self.store.save_case(self.a, candidate, candidate["version"], owner="worker-b", fence=fence2)

    def test_action_journal_never_replays_unknown_write(self) -> None:
        first = self.store.reserve_action(self.a, "act-1", "submit", {"case_id": "c-1"}, "write")
        self.assertEqual("pending", first["status"])
        self.store.unknown_action(self.a, "act-1", "transport ended after dispatch")
        with self.assertRaises(UnknownOutcomeError):
            self.store.reserve_action(self.a, "act-1", "submit", {"case_id": "c-1"}, "write")
        with self.assertRaises(ConflictError):
            self.store.reserve_action(self.a, "act-1", "submit", {"case_id": "other"}, "write")
        read = self.store.reserve_action(self.a, "act-r", "lookup", {}, "read")
        self.store.finish_action(self.a, "act-r", {"found": True})
        again = self.store.reserve_action(self.a, "act-r", "lookup", {}, "read")
        self.assertEqual("completed", again["status"])
        self.assertEqual({"found": True}, again["result"])

    def test_actions_are_partitioned_by_full_scope(self) -> None:
        self.store.reserve_action(self.a, "same-id", "lookup", {}, "read")
        self.assertEqual([], self.store.actions(self.b))
        with self.assertRaises(KeyError):
            self.store.finish_action(self.b, "same-id", {})


class RoleAndSchemaTests(unittest.TestCase):
    def test_zero_context_disables_only_context_cap_and_continuation_order_is_correct(self):
        self.assertEqual(0,Limits(max_context_chars=0).max_context_chars)
        for field in ('max_model_calls','max_tool_calls','max_output_tokens'):
            with self.assertRaises(ValueError):Limits(**{field:0})
        for bad in (-1,False,1.5):
            with self.assertRaises(ValueError):Limits(max_context_chars=bad)
        self.assertFalse(budget_is_reduction('max_context_chars',0,180000))
        self.assertFalse(budget_is_reduction('max_context_chars',0,0))
        self.assertTrue(budget_is_reduction('max_context_chars',180000,0))
        self.assertTrue(budget_is_reduction('max_context_chars',100,180000))

    def test_catalogue_has_expected_domains_and_is_detached(self) -> None:
        pa = roles_for("PA")
        self.assertEqual(28, len(pa))  # 18 PA + 10 shared contracts
        self.assertEqual(66, sum(len(roles_for(domain)) - 10 for domain in ("PA", "UM", "CM")) + 10)
        pa[0]["name"] = "tampered"
        self.assertNotEqual("tampered", roles_for("PA")[0]["name"])
        prompt = system_prompt("PA", scope())
        self.assertIn('"patient": "p-1"', prompt)
        self.assertIn("No patient-derived context", prompt)

    def test_schema_and_identity_are_both_required(self) -> None:
        spec = ToolSpec(
            "record.read", "read a scoped record",
            {"type": "object", "required": ["patient_id", "limit"], "additionalProperties": False,
             "properties": {"patient_id": {"type": "string"}, "limit": {"type": "integer", "minimum": 1}}},
            effect="read", identity_fields=("patient_id",),
        )
        validate_arguments(spec, {"patient_id": "p-1", "limit": 3}, scope())
        with self.assertRaises(IsolationError):
            validate_arguments(spec, {"patient_id": "p-2", "limit": 3}, scope())
        with self.assertRaises(ValueError):
            validate_arguments(spec, {"patient_id": "p-1", "limit": True}, scope())
        with self.assertRaises(ValueError):
            validate_arguments(spec, {"patient_id": "p-1", "limit": 3, "patient_name": "A"}, scope())

    def test_missing_identity_and_unsupported_schema_fail_closed(self) -> None:
        spec = ToolSpec("get", "", {"type": "object", "additionalProperties": True}, identity_fields=("case_id",))
        with self.assertRaises(IsolationError):
            validate_arguments(spec, {}, scope())
        unsupported = ToolSpec("get", "", {"type": "object", "unevaluatedProperties": False})
        with self.assertRaises(ValueError):
            validate_arguments(unsupported, {}, scope())
        nested_unsupported = ToolSpec("get", "", {"anyOf": [{"type": "object"}, {"unevaluatedProperties": False}]})
        with self.assertRaises(ValueError):
            validate_arguments(nested_unsupported, {}, scope())
        with self.assertRaises(ValueError):
            validate_arguments(ToolSpec("get", "", {}), {"bad": float("nan")}, scope())
        with self.assertRaises(IsolationError):
            validate_arguments(ToolSpec("unmarked", "", {"type": "object"}), {"patient_id": "p-2"}, scope())

    def test_provider_date_time_and_binary_formats_are_narrowly_supported(self):
        spec = ToolSpec("create", "", {
            "type": "object", "properties": {
                "requested_date": {"type": "string", "format": "date-time"},
                "document": {"type": "string", "format": "binary"},
                "maybe_date": {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}]},
            }, "additionalProperties": False,
        })
        validate_arguments(spec, {"document": "base64-or-opaque-string", "maybe_date": None}, scope())
        validate_arguments(spec, {"requested_date": "2026-10-20T16:30:00Z", "document": "opaque",
                                  "maybe_date": "2026-10-20T16:30:00+05:30"}, scope())
        for value in ("2026-10-20T16:30:00", "2026-02-30T16:30:00Z", "2026-10-20 16:30:00Z"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "RFC 3339"):
                validate_arguments(spec, {"requested_date": value}, scope())
        unsupported = ToolSpec("get", "", {"type": "object", "properties": {
            "id": {"type": "string", "format": "uuid"}}, "additionalProperties": False})
        with self.assertRaisesRegex(ValueError, "unsupported JSON schema format"):
            validate_arguments(unsupported, {"id": "not-validated"}, scope())

    def test_internal_case_subject_namespace_cannot_be_sent_as_case_id(self):
        provider_scope = scope("patient-1", "case-subject:patient-1")
        spec = ToolSpec("case.read", "", {"type": "object", "required": ["case_id"],
                            "properties": {"case_id": {"type": "string"}},
                            "additionalProperties": False})
        with self.assertRaisesRegex(IsolationError, "internal case-subject namespace"):
            validate_arguments(spec, {"case_id": provider_scope.case}, provider_scope)

    def test_local_pydantic_references_and_boolean_enum_are_handled(self) -> None:
        spec = ToolSpec("nested", "", {
            "$defs": {"Patient": {"type": "object", "required": ["patient_id"], "properties": {"patient_id": {"type": "string"}}}},
            "type": "object", "required": ["patient"], "properties": {"patient": {"$ref": "#/$defs/Patient"}},
        }, identity_fields=("patient.patient_id",))
        validate_arguments(spec, {"patient": {"patient_id": "p-1"}}, scope())
        with self.assertRaises(ValueError):
            validate_arguments(ToolSpec("enum", "", {"enum": [1]}), {"value": True}, scope())


if __name__ == "__main__":
    unittest.main()
