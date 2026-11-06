from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any

from health_harness.engine import Harness
from health_harness.models import ConflictError, Limits, ModelReply, Scope, ToolCall, ToolSpec
from health_harness.store import CaseStore
from health_harness.tools import ToolRegistry, WorkspaceTools


def make_scope(patient: str = "p-1", case: str = "c-1") -> Scope:
    return Scope("env", "task", "org", "principal", patient, case)


class FakeModel:
    def __init__(self, replies: list[ModelReply]):
        self.replies = list(replies)
        self.seen: list[list[dict[str, Any]]] = []

    def complete(self, messages, tools, *, max_output_tokens):
        self.seen.append(json.loads(json.dumps(messages)))
        if not self.replies:
            raise AssertionError("unexpected model request")
        return self.replies.pop(0)


class FakeTools:
    def __init__(self, result: Any, *, effect: str = "read"):
        self.result = result
        self.effect = effect
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def list_tools(self):
        return [ToolSpec("records.lookup", "lookup a case record", {
            "type": "object", "required": ["patient_id"], "properties": {"patient_id": {"type": "string"}},
            "additionalProperties": False,
        }, effect=self.effect, identity_fields=("patient_id",))]

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result(arguments) if callable(self.result) else self.result


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CaseStore(Path(self.temp.name) / "state.sqlite")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_scoped_completion_requires_successful_observation_and_closed_obligation(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(tool_calls=(ToolCall("ob1", "case.add_obligation", {"id": "review", "description": "Review the observed response"}),)),
            ModelReply(tool_calls=(ToolCall("close1", "case.close_obligation", {"id": "review", "evidence_ids": ["ev:m1:read"]}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "The assigned lookup returned a case-scoped result.", "evidence_ids": ["ev:m1:read"]})),
        ])
        tools = FakeTools({"patient_id": "p-1", "record_status": "present"})
        harness = Harness(self.store, model, tools)
        result = harness.run(make_scope(), "Check this record", "PA")
        self.assertEqual("complete", result["status"])
        self.assertEqual("closed", result["obligations"][0]["status"])
        self.assertEqual("success", result["evidence"][0]["outcome"])
        self.assertEqual("harness-local scoped claim; not official benchmark success", result["completion"]["kind"])

    def test_foreign_patient_result_is_quarantined_before_any_later_model_call(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content='{"status":"complete","claim":"bad","evidence_ids":["ev:m1:read"]}'),
        ])
        tools = FakeTools({"structuredContent": None, "content": [{"type": "text",
                           "text": '{"patient_id":"p-2","secret":"other patient details"}',
                           "parsed_json": {"patient_id": "p-2", "secret": "other patient details"}}], "isError": False})
        result = Harness(self.store, model, tools).run(make_scope(), "Read this record", "PA")
        self.assertEqual("blocked", result["status"])
        self.assertEqual(1, len(model.seen))
        self.assertNotIn("other patient details", json.dumps(model.seen))
        self.assertNotIn("other patient details", json.dumps(result))
        self.assertEqual("result_identity_mismatch", result["evidence"][0]["observed_result"]["error"])

    def test_bound_workspace_rejects_different_scope_before_model_or_file_access(self):
        scope_a, scope_b = make_scope("p-a", "c-a"), make_scope("p-b", "c-b")
        workspace = WorkspaceTools(Path(self.temp.name) / "work", scope_a)
        workspace.call("workspace.write_file", {"path": "marker.txt", "content": "patient A private"})
        model = FakeModel([])
        harness = Harness(self.store, model, ToolRegistry(workspace))
        with self.assertRaisesRegex(ValueError, "different case scope"):
            harness.run(scope_b, "Read case files", "PA")
        self.assertEqual([], model.seen)
        self.assertEqual("patient A private", workspace.call("workspace.read_file", {"path": "marker.txt"})["text"])

    def test_same_harness_rejects_overlapping_run(self):
        entered_model = threading.Event()
        release_model = threading.Event()

        class BlockingModel:
            def complete(self, messages, tools, *, max_output_tokens):
                entered_model.set()
                if not release_model.wait(3):
                    raise TimeoutError("test model release timed out")
                return ModelReply(content="not a completion record")

        harness = Harness(self.store, BlockingModel(), FakeTools({"patient_id": "p-1"}))
        worker_errors = []

        def first_run():
            try:
                harness.run(make_scope(), "first run", "PA")
            except Exception as exc:
                worker_errors.append(exc)

        worker = threading.Thread(target=first_run)
        worker.start()
        self.assertTrue(entered_model.wait(2), "first run did not reach the model")
        try:
            with self.assertRaisesRegex(ConflictError, "already has a run in progress"):
                harness.run(make_scope("p-2", "c-2"), "second run", "PA")
        finally:
            release_model.set()
            worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertEqual([], worker_errors)

    def test_failed_tool_output_cannot_support_completion_claim(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "done", "evidence_ids": ["ev:m1:read"]})),
        ])
        result = Harness(self.store, model, FakeTools({"error": "not found"})).run(make_scope(), "Read", "PA")
        self.assertEqual("unresolved", result["status"])
        self.assertEqual("failure", result["evidence"][0]["outcome"])

    def test_unknown_write_is_not_retried_on_resume(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("write", "records.lookup", {"patient_id": "p-1"}),)),
        ])
        tools = FakeTools(RuntimeError("connection dropped after dispatch"), effect="write")
        harness = Harness(self.store, model, tools)
        first = harness.run(make_scope(), "Make the assigned change", "PA")
        self.assertEqual("blocked", first["status"])
        self.assertEqual(1, len(tools.calls))
        second = harness.run(make_scope(), "Make the assigned change", "PA", resume=True)
        self.assertEqual("blocked", second["status"])
        self.assertEqual(1, len(tools.calls))

    def test_resume_retries_transient_model_failure_and_executes_effect_once(self):
        class FailThenReplyModel:
            def __init__(self):
                self.calls = 0

            def complete(self, messages, tools, *, max_output_tokens):
                self.calls += 1
                if self.calls == 1:
                    raise OSError("temporary provider interruption")
                if self.calls == 2:
                    return ModelReply(tool_calls=(ToolCall("apply", "records.lookup", {"patient_id": "p-1"}),))
                return ModelReply(content=json.dumps({"status": "complete", "claim": "effect observed",
                                                      "evidence_ids": ["ev:m2:apply"]}))

        model = FailThenReplyModel()
        tools = FakeTools({"patient_id": "p-1", "receipt": "once"}, effect="write")
        harness = Harness(self.store, model, tools, limits=Limits(max_model_calls=3, max_tool_calls=4))
        first = harness.run(make_scope(), "Perform the requested effect", "PA")
        self.assertEqual("error", first["status"])
        second = harness.run(make_scope(), "Perform the requested effect", "PA", resume=True)
        self.assertEqual("complete", second["status"])
        self.assertEqual(3, second["model_calls"])
        self.assertEqual(1, second["tool_calls"])
        self.assertEqual(1, len(tools.calls))
        self.assertEqual(3, self.store.load_case(make_scope())["budgets"]["max_model_calls"])

    def test_helper_and_write_in_same_model_turn_keep_stable_journal_identity(self):
        model = FakeModel([
            ModelReply(tool_calls=(
                ToolCall("helper", "case.request_helper", {"role_id": "PA-01", "question": "Check the request framing"}),
                ToolCall("write", "records.lookup", {"patient_id": "p-1"}),
            )),
            ModelReply(content="bounded proposal"),
            ModelReply(content='{"status":"complete","claim":"change observed","evidence_ids":["ev:m1:write"]}'),
        ])
        tools = FakeTools({"patient_id": "p-1", "receipt": "r-1"}, effect="write")
        result = Harness(self.store, model, tools, composition="helpers").run(make_scope(), "Do task", "PA")
        self.assertEqual("complete", result["status"])
        self.assertEqual("m1:write", self.store.actions(make_scope())[0]["id"])
        self.assertEqual(1, len(tools.calls))

    def test_completed_write_receipt_recovers_without_replaying_after_crash_boundary(self):
        scope = make_scope()
        self.store.open_case(scope, "Do task", "PA")
        state = self.store.load_case(scope)
        state.update({"status": "running", "model_calls": 1, "tool_calls": 1,
                      "processed_tool_calls": ["m1:write"]})
        state["messages"] = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "Do task"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "write", "journal_id": "m1:write",
             "name": "records.lookup", "arguments": {"patient_id": "p-1"}}]},
        ]
        self.store.save_case(scope, state, 0)
        self.store.reserve_action(scope, "m1:write", "records.lookup", {"patient_id": "p-1"}, "write")
        self.store.finish_action(scope, "m1:write", {"patient_id": "p-1", "receipt": "stored-r"})
        model = FakeModel([ModelReply(content=json.dumps({"status": "complete", "claim": "receipt recovered",
                                                          "evidence_ids": ["ev:m1:write"]}))])
        tools = FakeTools({"patient_id": "p-1", "receipt": "should-not-run"}, effect="write")
        result = Harness(self.store, model, tools).run(scope, "Do task", "PA", resume=True)
        self.assertEqual("complete", result["status"])
        self.assertEqual("stored-r", result["evidence"][0]["observed_result"]["receipt"])
        self.assertEqual([], tools.calls)

    def test_pending_write_at_resume_is_quarantined_and_not_dispatched(self):
        scope = make_scope()
        self.store.open_case(scope, "Do task", "PA")
        state = self.store.load_case(scope)
        state.update({"status": "running", "model_calls": 1, "tool_calls": 1,
                      "processed_tool_calls": ["m1:write"]})
        state["messages"] = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "Do task"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "write", "journal_id": "m1:write",
             "name": "records.lookup", "arguments": {"patient_id": "p-1"}}]},
        ]
        self.store.save_case(scope, state, 0)
        self.store.reserve_action(scope, "m1:write", "records.lookup", {"patient_id": "p-1"}, "write")
        model = FakeModel([])
        tools = FakeTools({"patient_id": "p-1"}, effect="write")
        result = Harness(self.store, model, tools).run(scope, "Do task", "PA", resume=True)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("unknown", self.store.actions(scope)[0]["status"])
        self.assertEqual([], tools.calls)

    def test_same_harness_and_model_instance_do_not_carry_patient_a_context_to_b(self):
        model = FakeModel([
            ModelReply(tool_calls=(ToolCall("read-a", "records.lookup", {"patient_id": "p-1"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "A lookup completed", "evidence_ids": ["ev:m1:read-a"]})),
            ModelReply(content="B remains unresolved"),
        ])
        tools = FakeTools(lambda args: {"patient_id": args["patient_id"], "marker": "only-A" if args["patient_id"] == "p-1" else "only-B"})
        harness = Harness(self.store, model, tools)
        self.assertEqual("complete", harness.run(make_scope("p-1", "c-1"), "Review", "PA")["status"])
        self.assertEqual("unresolved", harness.run(make_scope("p-2", "c-2"), "Review", "PA")["status"])
        self.assertNotIn("only-A", json.dumps(model.seen[2]))
        self.assertIn("p-2", str(model.seen[2]))

    def test_schema_and_context_budget_stop_before_provider_execution(self):
        model = FakeModel([ModelReply(content="unused")])
        tools = FakeTools({"patient_id": "p-1"})
        result = Harness(self.store, model, tools, limits=Limits(max_context_chars=32)).run(make_scope(), "Do task", "PA")
        self.assertEqual("exhausted", result["status"])
        self.assertEqual([], model.seen)
        self.assertEqual([], tools.calls)


if __name__ == "__main__":
    unittest.main()
