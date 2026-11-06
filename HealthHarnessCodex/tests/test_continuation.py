from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from health_harness_codex import continuation
from health_harness_codex.models import Limits, Scope, ToolSpec
from health_harness_codex.store import CaseStore


_RUNS_ROOT = Path(continuation.__file__).resolve().parents[1] / "runs"
_CONTAINER = "owned-test-container"
_TASK_ID = "pa_test_continuation"
_CASE_ID = "CASE-CONT-42"
_PATIENT_ID = "PATIENT-CONT-9"
_NOTE = "Audit the saved task against its observed evidence and continue only supported remaining work."
_TASK_TEXT = "Synthetic public UM task instruction."
_SOURCE_BUDGETS = {"max_model_calls": 4, "max_tool_calls": 8,
                   "max_context_chars": 12000, "max_output_tokens": 2048}
_NEW_LIMITS = Limits(max_model_calls=12, max_tool_calls=30,
                     max_context_chars=50000, max_output_tokens=4096)


def _summary(case_id=_CASE_ID, determination_id="DET-7", decision="approved",
             workflow_stage="determination", stage_detail="finalized", outcome="approved",
             action_owner="none"):
    return {"structuredContent": {
        "case_id": case_id,
        "case_status": decision,
        "determination": {"id": determination_id, "case_id": case_id,
                          "final_decision": decision},
        "workflow_state": {"workflow_stage": workflow_stage, "stage_detail": stage_detail,
                           "outcome": outcome, "action_owner": action_owner},
    }}


class FakeExecutor:
    def __init__(self, *args, **kwargs):
        self.validated_task = None

    def validate_owned_trial(self, task_id):
        self.validated_task = task_id


class FakeActor:
    next_summary = _summary()
    last_instance = None

    def __init__(self, *args, **kwargs):
        type(self).last_instance = self
        self._actual_names = {
            "summary_alias": "determination.get_summary",
            "route_alias": "triage.route_case",
            "disposition_alias": "triage.set_disposition",
            "nurse_alias": "review.get_nurse_review_data",
            "md_alias": "review.get_md_review_data",
            "letter_alias": "letters.list_letters",
        }
        self._specs = [
            ToolSpec("summary_alias", "public determination summary", {
                "type": "object", "required": ["case_id"], "additionalProperties": False,
                "properties": {"case_id": {"type": "string"}},
            }),
            *[ToolSpec(name, actual, {"type": "object", "properties": {}})
              for name, actual in self._actual_names.items() if name != "summary_alias"],
        ]
        self.calls = []

    def list_tools(self):
        return self._specs

    def call(self, name, arguments):
        self.calls.append((name, dict(arguments)))
        return type(self).next_summary


class FakeHarness:
    last_instance = None

    def __init__(self, store, model, tools, limits, composition, patient_identity_tools=(),recovery_helper_policy='off'):
        type(self).last_instance = self
        self.store = store
        self.model = model
        self.tools = tools
        self.limits = limits
        self.composition = composition
        self.patient_identity_tools = patient_identity_tools
        self.run_arguments = None

    def run(self, scope, instruction, domain, **kwargs):
        self.run_arguments = (scope, instruction, domain, kwargs)
        return {"status": "unresolved", "message": "synthetic continuation result",
                "model_calls": 5, "tool_calls": 9,
                "model_calls_observed_this_segment": 1,
                "tool_calls_observed_this_segment": 1,
                "reported_usage_this_segment": {"total_tokens": 25},
                "identity_bindings": {"patient_id": _PATIENT_ID, "case_id": scope.case},
                "evidence": [], "obligations": []}


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="continuation-test-", dir=str(_RUNS_ROOT))
        self.root = Path(self.temp.name)
        self.source = self.root / "attempt-3"
        self.source.mkdir()
        self.destination = self.root / "attempt-3-audit"
        self.task_dir = self.root / _TASK_ID
        self.task_dir.mkdir()
        (self.task_dir / "instruction.md").write_text(_TASK_TEXT, encoding="utf-8")
        self.task_hash = hashlib.sha256((_TASK_TEXT).encode()).hexdigest()
        self.scope = Scope(f"docker:{_CONTAINER}", _TASK_ID, "payer-org", "payer-actor",
                           f"case-subject:{_CASE_ID}", _CASE_ID)
        self._write_source_run()
        FakeActor.next_summary = _summary()
        FakeHarness.last_instance = None

    def tearDown(self):
        self.temp.cleanup()

    def _write_source_run(self):
        self.source_db = self.source / "state.sqlite"
        store = CaseStore(self.source_db)
        try:
            state = store.open_case(self.scope, "Original full public task prompt", "UM")
            state.update({"status": "complete", "model_calls": 4, "tool_calls": 8,
                          "budgets": dict(_SOURCE_BUDGETS), "composition": "combined",
                          "usage": {"total_tokens": 100},
                          "messages": [{"role": "system", "content": "synthetic"},
                                       {"role": "user", "content": "synthetic"},
                                       {"role": "assistant", "content": "completed"}],
                          "identity_bindings": {"patient_id": _PATIENT_ID, "case_id": _CASE_ID},
                          "final": {"status": "complete"},
                          "completion": {"claim": "synthetic", "evidence_ids": ["ev:m1:read"]}})
            store.save_case(self.scope, state, 0)
            for action_id, tool in (("m1:route", "route_alias"), ("m2:disposition", "disposition_alias")):
                action = store.reserve_action(self.scope, action_id, tool, {"case_id": _CASE_ID}, "write")
                store.finish_action(self.scope, action_id, {"completed": True})
        finally:
            store.close()
        self.source_db_hash = continuation._sha256_file(self.source_db)
        evaluation = {"metadata": {"task_id": _TASK_ID, "task_instruction_sha256": self.task_hash,
                                   "container_identity": _CONTAINER, "source_fingerprint": "source-fingerprint",
                                   "source_commit": "a" * 40}}
        report = {"mode": "real-case-unscored", "task": _TASK_ID, "scope": self.scope.to_dict(),
                  "container_identity": _CONTAINER, "task_instruction_sha256": self.task_hash,
                  "local_harness": {"status": "complete", "model_calls": 4, "tool_calls": 8,
                                    "identity_bindings": {"patient_id": _PATIENT_ID, "case_id": _CASE_ID}},
                  "actual_determination_readback": {"status": "observed", "tool": "determination.get_summary",
                                                     "result": _summary()}}
        (self.source / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
        (self.source / "run.result.json").write_text(json.dumps(report), encoding="utf-8")

    def _run_patches(self):
        return (
            patch.object(continuation, "DockerExecutor", FakeExecutor),
            patch.object(continuation, "DockerMCPClient", FakeActor),
            patch.object(continuation, "CodexSessionModel", lambda *args, **kwargs: object()),
            patch.object(continuation, "Harness", FakeHarness),
        )

    def _run(self):
        return continuation.run_continuation(
            _CONTAINER, self.task_dir, self.source, self.destination,
            "C:/Codex/codex.exe", {"C:/approved/AGENTS.md": "a" * 64},
            _NOTE, _NEW_LIMITS, domain="pa_um",
        )

    def test_matching_public_readback_resumes_copy_with_note_and_explicit_budgets(self):
        source_hash = continuation._sha256_file(self.source_db)
        patches = self._run_patches()
        for item in patches:
            item.start()
        try:
            result = self._run()
        finally:
            for item in reversed(patches):
                item.stop()

        self.assertEqual("unresolved", result["local_harness"]["status"])
        self.assertEqual(self.scope.to_dict(), FakeHarness.last_instance.run_arguments[0].to_dict())
        _, instruction, domain, kwargs = FakeHarness.last_instance.run_arguments
        self.assertEqual("Original full public task prompt", instruction)
        self.assertEqual("UM", domain)
        self.assertTrue(kwargs["resume"])
        self.assertEqual(_NOTE, kwargs["continuation_note"])
        self.assertEqual(_NEW_LIMITS, kwargs["continuation_limits"])
        self.assertEqual(source_hash, continuation._sha256_file(self.source_db))
        self.assertEqual(source_hash, result["continuation_of"]["source_state_sha256"])
        self.assertEqual(4, result["starting_counts"]["model_calls"])
        self.assertEqual(8, result["starting_counts"]["tool_calls"])
        self.assertEqual(0, result["observed_this_segment"]["model_calls"])
        listed = FakeHarness.last_instance.tools.tools.tools.list_tools()
        names = {spec.name for spec in listed}
        self.assertNotIn("route_alias", names)
        self.assertNotIn("disposition_alias", names)
        self.assertIn("nurse_alias", names)
        self.assertIn("md_alias", names)
        self.assertIn("letter_alias", names)
        guard = FakeHarness.last_instance.tools.tools.tools
        with self.assertRaisesRegex(continuation.ContinuationError, "already completed"):
            guard.call("route_alias", {"case_id": _CASE_ID})
        with self.assertRaisesRegex(continuation.ContinuationError, "already completed"):
            guard.call("disposition_alias", {"case_id": _CASE_ID})
        evaluation = json.loads((self.destination / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(["route_case", "set_disposition"],
                         evaluation["metadata"]["completed_terminal_effects_filtered"])
        self.assertTrue((self.destination / "run.result.json").is_file())
        copied = CaseStore(self.destination / "state.sqlite")
        try:
            persisted = copied.load_case(self.scope)
            self.assertEqual(self.scope.to_dict(), persisted["scope"])
            self.assertEqual(_PATIENT_ID, persisted["identity_bindings"]["patient_id"])
        finally:
            copied.close()

    def test_older_run_with_a_larger_saved_output_cap_still_resumes(self):
        # The output cap is advisory; runs saved at 4096 must resume after the 4000 default.
        store = CaseStore(self.source_db)
        try:
            state = store.load_case(self.scope)
            state["budgets"] = {**_SOURCE_BUDGETS, "max_output_tokens": 4096}
            store.save_case(self.scope, state, state["version"])
        finally:
            store.close()
        patches = self._run_patches()
        for item in patches:
            item.start()
        try:
            continuation.run_continuation(
                _CONTAINER, self.task_dir, self.source, self.destination,
                "C:/Codex/codex.exe", {"C:/approved/AGENTS.md": "a" * 64},
                _NOTE, Limits(max_model_calls=12, max_tool_calls=30, max_context_chars=50000,
                              max_output_tokens=4000), domain="pa_um")
        finally:
            for item in reversed(patches):
                item.stop()
        self.assertEqual(4096, FakeHarness.last_instance.run_arguments[3]["continuation_limits"].max_output_tokens)

    def test_actor_reset_or_changed_determination_refuses_before_harness_resume(self):
        FakeActor.next_summary = _summary(determination_id="DET-RESET", decision="pending",
                                          workflow_stage="intake", stage_detail="triage",
                                          outcome="pending", action_owner="payer")
        patches = self._run_patches()
        for item in patches:
            item.start()
        try:
            with self.assertRaisesRegex(continuation.ContinuationError, "no longer matches"):
                self._run()
        finally:
            for item in reversed(patches):
                item.stop()
        self.assertIsNone(FakeHarness.last_instance)
        self.assertEqual(self.source_db_hash, continuation._sha256_file(self.source_db))
        self.assertFalse((self.destination / "run.result.json").exists())
        self.assertEqual("setup_failure", json.loads((self.destination / "result.private.json").read_text())["status"])

    def test_continuation_remains_um_only_until_other_profiles_are_validated(self):
        with patch.object(continuation, "DockerExecutor") as executor:
            with self.assertRaisesRegex(continuation.ContinuationError, "only for the validated UM"):
                continuation.run_continuation(
                    _CONTAINER, self.task_dir, self.source, self.destination,
                    "C:/Codex/codex.exe", {"C:/approved/AGENTS.md": "a" * 64},
                    _NOTE, _NEW_LIMITS, domain="pa_provider")
            executor.assert_not_called()

    def test_foreign_case_readback_refuses_continuation(self):
        FakeActor.next_summary = _summary(case_id="CASE-FOREIGN")
        patches = self._run_patches()
        for item in patches:
            item.start()
        try:
            with self.assertRaisesRegex(continuation.ContinuationError, "case ID does not match"):
                self._run()
        finally:
            for item in reversed(patches):
                item.stop()
        self.assertIsNone(FakeHarness.last_instance)
        self.assertEqual(self.source_db_hash, continuation._sha256_file(self.source_db))


if __name__ == "__main__":
    unittest.main()
