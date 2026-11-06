import json
from pathlib import Path
import tempfile
import time
import unittest

from health_harness_codex.evaluation import (
    RecordingModel,
    RecordingTools,
    RunRecorder,
    _completion_verification_summary,
    classify_result,
    compare_reports,
)
from health_harness_codex.models import ModelReply, ToolCall, ToolSpec
from health_harness_codex.providers import ModelResponseFormatError, ProviderError


class EvaluationTests(unittest.TestCase):
    def test_returned_tool_error_capture_is_private_redacted_and_no_replay(self):
        from health_harness_codex.tools import MCPToolError
        failure = MCPToolError({"isError": True, "content": [{"type": "text",
            "text": "private reason; Bearer sensitive-value sk-example0123456789"}],
            "api_key": "never-save-this"})
        class Tools:
            calls = 0
            def list_tools(self):
                return [ToolSpec("write", "", {"type": "object"}, effect="write")]
            def call(self, name, arguments):
                self.calls += 1
                raise failure
        delegate = Tools()
        proxy = RecordingTools(delegate, self.recorder)
        with self.assertRaises(MCPToolError) as caught:
            proxy.call("write", {})
        self.assertIs(failure, caught.exception)
        self.assertEqual(1, delegate.calls)
        captured = (self.run_dir / "tool-failures/dispatch-0001.private.json").read_text()
        self.assertIn("private reason", captured)
        for secret in ("sensitive-value", "sk-example0123456789", "never-save-this"):
            self.assertNotIn(secret, captured)
        self.assertNotIn("private reason", self.recorder.events_path.read_text())
        self.assertNotIn("private reason", self.recorder.live_path.read_text())
        data = json.loads(captured)
        self.assertTrue(data["outcome_requires_reconciliation"])
        # Existing evidence must never be overwritten by a new proxy instance.
        second = RecordingTools(delegate, self.recorder)
        with self.assertRaises(MCPToolError):
            second.call("write", {})
        self.assertEqual(captured, (self.run_dir / "tool-failures/dispatch-0001.private.json").read_text())

    def test_failure_logs_sanitized_stage_and_cleanup_and_preserves_exception(self):
        failure=ProviderError('synthetic timeout',diagnostics={'request_stage':'awaiting_turn',
            'request_timed_out':True,'timeout_seconds':180,'last_native_event':'reasoning_progress',
            'notifications_received':3,'native_idle_seconds':14,'cleanup_confirmed':True,
            'private_payload':'PRIVATE_PATIENT'})
        class Model:
            def complete(self,*args,**kwargs):raise failure
            def request_diagnostics(self):raise RuntimeError('PRIVATE_DIAGNOSTIC_FAILURE')
        with self.assertRaises(ProviderError) as caught:RecordingModel(Model(),self.recorder).complete([],[],max_output_tokens=10)
        self.assertIs(failure,caught.exception)
        text=self.recorder.events_path.read_text(encoding='utf-8')
        failed=next(json.loads(l) for l in text.splitlines() if json.loads(l)['kind']=='model_call_failed')
        self.assertEqual('awaiting_turn',failed['request_diagnostics']['request_stage'])
        self.assertTrue(failed['request_timed_out']);self.assertTrue(failed['cleanup_confirmed'])
        self.assertNotIn('PRIVATE',text)
        live=self.recorder.live_path.read_text(encoding='utf-8')
        self.assertIn('stage=awaiting_turn',live);self.assertIn('cleanup_confirmed=true',live)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.temp.name) / "runs" / "case-1"
        self.recorder = RunRecorder(self.run_dir, {
            "task_id": "task-a", "model": "test-model", "reasoning_effort": "high",
            "budgets": {"model_calls": 3, "max_output_tokens": 99}, "initial_state_fingerprint": "state-1",
            "source_commit": "abc", "composition": "single", "api_key": "private",
        })

    def tearDown(self):
        self.temp.cleanup()

    def test_model_wrapper_preserves_reply_and_logs_only_fingerprints_and_proposals(self):
        reply = ModelReply(content="private clinical response", tool_calls=(ToolCall("c1", "lookup", {}),),
                           usage={"input_tokens": 11, "output_tokens": 3})

        class Model:
            def complete(self, messages, tools, *, max_output_tokens):
                self.seen = (messages, tools, max_output_tokens)
                return reply

        model = Model()
        messages = [{"role": "user", "content": "secret patient text"}]
        tools = [ToolSpec("lookup", "lookup", {"type": "object"})]
        wrapped = RecordingModel(model, self.recorder)
        self.assertIs(wrapped.complete(messages, tools, max_output_tokens=91), reply)
        self.assertEqual(model.seen, (messages, tools, 91))
        live = (self.run_dir / "run.live.md").read_text(encoding="utf-8")
        events = (self.run_dir / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("secret patient text", live)
        self.assertNotIn("private clinical response", live)
        self.assertNotIn("secret patient text", events)
        event_objects = [json.loads(row) for row in events.splitlines()]
        ended = next(event for event in event_objects if event["kind"] == "model_call_finished")
        self.assertEqual(ended["proposed_tool_names"], ["lookup"])
        self.assertEqual(ended["usage"]["input_tokens"], 11)
        self.assertEqual(len(next(event for event in event_objects if event["kind"] == "model_call_started")["context_fingerprint"]), 64)
        self.assertEqual(next(event for event in event_objects if event["kind"] == "model_call_started")["call_number"], 1)
        self.assertIn("MODEL_START", live)
        self.assertIn("task-a", live)
        self.assertEqual(self.recorder.metadata["budgets"]["max_output_tokens"], 99)
        self.assertEqual(self.recorder.metadata["api_key"], "[redacted]")

    def test_failed_format_response_usage_is_recorded_without_reply_body(self):
        class Model:
            def complete(self, messages, tools, *, max_output_tokens):
                raise ModelResponseFormatError("outer_json", {"input_tokens": 13, "output_tokens": 5})

        with self.assertRaises(ModelResponseFormatError):
            RecordingModel(Model(), self.recorder).complete([], [], max_output_tokens=10)
        report = self.recorder.finish({"status": "error", "message": "Model response format failure."}, 0.2)
        self.assertEqual({"input_tokens": 13, "output_tokens": 5}, report["metrics"]["reported_usage_this_segment"])
        events = [json.loads(row) for row in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        failed = next(event for event in events if event["kind"] == "model_call_failed")
        self.assertEqual({"input_tokens": 13, "output_tokens": 5}, failed["usage"])

    def test_tool_wrapper_preserves_bind_list_call_and_logs_outcome_without_payload(self):
        spec = ToolSpec("record", "record", {"type": "object"}, effect="write")

        class Tools:
            def __init__(self):
                self.bound = None
                self.args = None

            def bind_scope(self, scope):
                self.bound = scope

            def list_tools(self):
                return [spec]

            def call(self, name, arguments):
                self.args = (name, arguments)
                return {"status": "ok", "body": "private tool response"}

        delegate = Tools()
        wrapped = RecordingTools(delegate, self.recorder)
        wrapped.bind_scope("case-scope")
        self.assertEqual(delegate.bound, "case-scope")
        self.assertEqual(wrapped.list_tools(), [spec])
        args = {"body": "sensitive tool args"}
        value = wrapped.call("record", args)
        self.assertEqual(value, {"status": "ok", "body": "private tool response"})
        self.assertEqual(delegate.args, ("record", args))
        live = (self.run_dir / "run.live.md").read_text(encoding="utf-8")
        self.assertNotIn("sensitive tool args", live)
        self.assertNotIn("private tool response", live)
        events = [json.loads(row) for row in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        finished = next(event for event in events if event["kind"] == "tool_call_finished")
        self.assertEqual(finished["declared_effect"], "write")
        self.assertEqual(finished["actual_effect"]["result_keys"], ["body", "status"])

    def test_tool_exception_is_logged_and_reraised_without_retry(self):
        class Tools:
            attempts = 0

            def list_tools(self):
                return [ToolSpec("write", "write", {"type": "object"}, effect="write")]

            def call(self, name, arguments):
                self.attempts += 1
                raise RuntimeError("raw protected diagnostic")

        delegate = Tools()
        wrapped = RecordingTools(delegate, self.recorder)
        wrapped.list_tools()
        with self.assertRaisesRegex(RuntimeError, "raw protected diagnostic"):
            wrapped.call("write", {"payload": "private"})
        self.assertEqual(delegate.attempts, 1)
        event = [json.loads(row) for row in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        failed = next(e for e in event if e["kind"] == "tool_call_finished")
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed["error_type"], "RuntimeError")
        live = (self.run_dir / "run.live.md").read_text(encoding="utf-8")
        self.assertNotIn("raw protected diagnostic", live)
        self.assertIn("TOOL_END", live)
        self.assertIn("error_type=RuntimeError", live)
        result = self.recorder.finish({"status": "error", "message": "tool dispatch failed"}, 0.2)
        self.assertEqual(result["metrics"]["tool_dispatch_attempts"], {"write": 1})
        self.assertEqual(result["metrics"]["tool_dispatch_completed"], {})
        self.assertEqual(result["metrics"]["tool_dispatch_statuses"], {"failed": 1})

    def test_guard_response_is_recorded_as_attempt_without_remote_dispatch(self):
        spec = ToolSpec("mcp_triage.route_case", "route", {"type": "object"}, effect="write")
        result_value = {"isError": True, "known_not_dispatched": True, "error": "blocked by local guard"}

        class Tools:
            def list_tools(self):
                return [spec]

            def call(self, name, arguments):
                return result_value

        wrapped = RecordingTools(Tools(), self.recorder)
        wrapped.list_tools()
        self.assertEqual(result_value, wrapped.call("mcp_triage.route_case", {"case_id": "case-1"}))
        events = [json.loads(row) for row in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        finished = next(event for event in events if event["kind"] == "tool_call_finished")
        self.assertEqual("not_dispatched", finished["status"])
        report = self.recorder.finish({"status": "blocked", "message": "guard blocked operation"}, 0.1)
        self.assertEqual({"mcp_triage.route_case": 1}, report["metrics"]["tool_dispatch_attempts"])
        self.assertEqual({}, report["metrics"]["tool_dispatch_completed"])
        self.assertEqual({"mcp_triage.route_case": 1}, report["metrics"]["tool_dispatch_not_dispatched"])

    def test_mcp_error_result_means_dispatch_returned_with_error_result(self):
        spec = ToolSpec("lookup", "lookup", {"type": "object"})

        class Tools:
            def list_tools(self):
                return [spec]

            def call(self, name, arguments):
                return {"isError": True, "content": [{"text": "protected response"}]}

        wrapped = RecordingTools(Tools(), self.recorder)
        wrapped.list_tools()
        wrapped.call("lookup", {})
        events = [json.loads(row) for row in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        finished = next(e for e in events if e["kind"] == "tool_call_finished")
        self.assertEqual("completed", finished["status"])
        self.assertEqual("error", finished["result_status"])
        report = self.recorder.finish({"status": "error"}, 0.1)
        self.assertEqual({"lookup": 1}, report["metrics"]["tool_dispatch_completed"])

    def test_plain_workspace_error_is_logged_as_error(self):
        class Tools:
            def list_tools(self): return [ToolSpec("workspace.read_file", "read", {"type": "object"}, effect="read")]
            def call(self, name, arguments): return {"error": {"code": "file_not_found"}}
        wrapped = RecordingTools(Tools(), self.recorder)
        wrapped.call("workspace.read_file", {"path": "missing.txt"})
        events = [json.loads(row) for row in (self.run_dir / "events.jsonl").read_text().splitlines()]
        finished = next(e for e in events if e["kind"] == "tool_call_finished")
        self.assertEqual("error", finished["result_status"])
        report = self.recorder.finish({"status": "error"}, 0.1)
        self.assertEqual({"workspace.read_file": 1}, report["metrics"]["tool_dispatch_completed"])

    def test_console_uses_canonical_tool_name_from_discovery_metadata(self):
        self.recorder.metadata["actor_tool_names"] = {"short_alias": "mcp_triage.inspect_public_queue"}
        spec = ToolSpec("short_alias", "lookup", {"type": "object"})

        class Tools:
            def list_tools(self):
                return [spec]

            def call(self, name, arguments):
                return {"ok": True}

        wrapped = RecordingTools(Tools(), self.recorder)
        wrapped.list_tools()
        wrapped.call("short_alias", {})
        live = (self.run_dir / "run.live.md").read_text(encoding="utf-8")
        self.assertIn("tool_name=mcp_triage.inspect_public_queue", live)
        self.assertNotIn("tool_name=short_alias", live)

    def test_model_wait_heartbeat_stops_after_success_and_exception(self):
        from health_harness_codex.evaluation import _Heartbeat

        original_interval = _Heartbeat.INTERVAL_SECONDS
        _Heartbeat.INTERVAL_SECONDS = 0.01
        try:
            class SlowModel:
                def __init__(self, fail=False):
                    self.fail = fail

                def complete(self, messages, tools, *, max_output_tokens):
                    time.sleep(0.035)
                    if self.fail:
                        raise RuntimeError("private diagnostic")
                    return ModelReply(content="ok")

            for fail in (False, True):
                wrapped = RecordingModel(SlowModel(fail), self.recorder)
                if fail:
                    with self.assertRaisesRegex(RuntimeError, "private diagnostic"):
                        wrapped.complete([], [], max_output_tokens=10)
                else:
                    wrapped.complete([], [], max_output_tokens=10)
                before = len(self.recorder._read_events())
                time.sleep(0.03)
                after_events = self.recorder._read_events()
                self.assertEqual(before, len(after_events), "heartbeat continued after the operation settled")
            waits = [e for e in self.recorder._read_events() if e["kind"] == "model_waiting"]
            self.assertGreaterEqual(len(waits), 2)
            model_calls = [e for e in self.recorder._read_events()
                           if e["kind"] in {"model_call_started", "model_call_finished", "model_call_failed"}]
            self.assertEqual([1, 1, 2, 2], [e["call_number"] for e in model_calls])

            class SlowTools:
                def __init__(self, fail=False):
                    self.fail = fail

                def list_tools(self):
                    return [ToolSpec("read_public", "read", {"type": "object"})]

                def call(self, name, arguments):
                    time.sleep(0.035)
                    if self.fail:
                        raise RuntimeError("private tool diagnostic")
                    return {"ok": True}

            for fail in (False, True):
                wrapped = RecordingTools(SlowTools(fail), self.recorder)
                wrapped.list_tools()
                if fail:
                    with self.assertRaisesRegex(RuntimeError, "private tool diagnostic"):
                        wrapped.call("read_public", {})
                else:
                    wrapped.call("read_public", {})
                before = len(self.recorder._read_events())
                time.sleep(0.03)
                self.assertEqual(before, len(self.recorder._read_events()),
                                 "tool heartbeat continued after the operation settled")
            tool_waits = [e for e in self.recorder._read_events() if e["kind"] == "tool_waiting"]
            self.assertGreaterEqual(len(tool_waits), 2)
        finally:
            _Heartbeat.INTERVAL_SECONDS = original_interval

    def test_report_keeps_local_completion_ungraded_and_flags_explicit_nonterminal_readback(self):
        result = {"status": "complete", "model_calls": 2, "tool_calls": 1,
                  "usage": {"input_tokens": 12}, "evidence": [{"outcome": "success"}],
                  "obligations": [{"status": "closed"}], "final": "private final answer"}
        report = self.recorder.finish(result, 1.75, {"public_determination_terminal": False})
        self.assertEqual(report["classification"], "incomplete_workflow")
        self.assertTrue(report["local_completion_claim"])
        self.assertTrue(report["harness_claim_environment_mismatch"])
        self.assertIsNone(report["official_success"])
        self.assertIsNone(report["official_score"])
        self.assertEqual(report["metrics"]["evidence_successes"], 1)
        self.assertEqual(json.loads((self.run_dir / "result.private.json").read_text(encoding="utf-8"))["final"], "private final answer")
        self.assertEqual(json.loads((self.run_dir / "evaluation.json").read_text(encoding="utf-8"))["official_success"], None)
        self.assertIsNone(report["final_evidence_valid"])
        self.assertEqual([], report["unsupported_final_evidence_ids"])
        self.assertIn("unknown", (self.run_dir / "run.live.md").read_text(encoding="utf-8"))

    def test_incomplete_final_reports_unsupported_and_failed_evidence_ids(self):
        result = {
            "status": "unresolved",
            "message": "The audit remains incomplete.",
            "final": {"status": "incomplete", "claim": "The required audit is not complete.",
                      "evidence_ids": ["ev:m24:read_triage_routing_policy",
                                       "ev:m13:member_notice",
                                       "ev:m25:triage_routing_policy_remainder",
                                       "ev:m27:rehydrate_member_notice"]},
            "evidence": [
                {"id": "ev:m24:read_triage_routing_policy", "outcome": "success"},
                {"id": "ev:m13:member_notice", "outcome": "success"},
                {"id": "ev:m25:triage_routing_policy_remainder", "outcome": "failure"},
            ],
            "obligations": [],
        }

        report = self.recorder.finish(result, 1.0)

        self.assertEqual("incomplete_workflow", report["classification"])
        self.assertFalse(report["final_evidence_valid"])
        self.assertEqual(["ev:m25:triage_routing_policy_remainder", "ev:m27:rehydrate_member_notice"],
                         report["unsupported_final_evidence_ids"])
        self.assertIsNone(report["official_success"])
        self.assertEqual("unresolved", report["harness_status"])

    def test_valid_original_evidence_ids_are_accepted_for_incomplete_final(self):
        result = {"status": "unresolved", "final": {
            "status": "incomplete", "claim": "The task still needs additional work.",
            "evidence_ids": ["ev:m24:read_triage_routing_policy", "ev:m13:member_notice"]},
            "evidence": [
                {"id": "ev:m24:read_triage_routing_policy", "outcome": "success"},
                {"id": "ev:m13:member_notice", "outcome": "success"},
            ]}

        report = self.recorder.finish(result, 0.5)

        self.assertTrue(report["final_evidence_valid"])
        self.assertEqual([], report["unsupported_final_evidence_ids"])

    def test_failure_taxonomy_is_operational_and_cautious(self):
        self.assertEqual(classify_result({"status": "blocked"}), "incomplete_workflow")
        self.assertEqual(classify_result({"status": "blocked", "message": "Wrong patient identity; content quarantined."}),
                         "schema_or_scope_rejection")
        self.assertEqual(classify_result({"status": "blocked", "message": "Wrong patient identity; content quarantined.",
                                          "journal_statuses": {"unknown": 1}}), "unknown_effect")
        self.assertEqual(classify_result({"status": "error", "journal_statuses": {"unknown": 0}},
                                         {"unknown": 1}), "setup_failure")
        self.assertEqual(classify_result({"status": "exhausted"}), "budget_exhausted")
        self.assertEqual(classify_result({"status": "error", "message": "Tool arguments failed schema validation"}),
                         "schema_or_scope_rejection")
        self.assertEqual(classify_result({"status": "error", "message": "Model request failed: ProviderError"}),
                         "inference_failure")
        self.assertEqual(classify_result({"status": "complete"}), "locally_complete_ungraded")
        self.assertEqual(classify_result({"status": "running"}), "incomplete_workflow")
        self.assertEqual(classify_result({"status": "unresolved", "message": "The structured response did not claim scoped completion."}),
                         "incomplete_workflow")

    def test_unverified_public_goal_is_not_reported_as_incomplete_workflow(self):
        result = {"status": "unresolved", "completion_gate": {
            "accepted": False, "branch_id": None, "missing_milestones": [],
            "reason_code": "goal_unverified",
        }}
        self.assertEqual("goal_unverified", classify_result(result))

    def test_mapped_contract_with_missing_milestones_remains_incomplete(self):
        result = {"status": "unresolved", "completion_gate": {
            "accepted": False, "branch_id": None,
            "missing_milestones": ["milestone_a", "milestone_b"],
            "reason_code": "required_milestones_unobserved",
        }}
        self.assertEqual("incomplete_workflow", classify_result(result))

    def test_rejected_invalid_contract_cannot_be_labeled_locally_complete(self):
        result = {"status": "complete", "completion_gate": {
            "accepted": False, "branch_id": None, "missing_milestones": [],
            "reason_code": "completion_contract_invalid",
        }}
        self.assertEqual("unverified", _completion_verification_summary(result)["status"])
        self.assertEqual("goal_unverified", classify_result(result))

    def test_rejected_gate_with_unknown_reason_fails_closed(self):
        result = {"status": "complete", "completion_gate": {
            "accepted": False, "branch_id": None, "missing_milestones": [],
            "reason_code": "unexpected_future_rejection",
        }}
        self.assertEqual("unverified", _completion_verification_summary(result)["status"])
        self.assertEqual("goal_unverified", classify_result(result))

    def test_completion_verification_and_model_claim_are_safely_separated(self):
        result = {
            "status": "unresolved",
            "final": {"status": "complete", "claim": "private claim text", "evidence_ids": []},
            "completion_gate": {
                "accepted": False, "branch_id": None, "missing_milestones": [],
                "reason_code": "goal_unverified", "private_detail": "private source text",
            },
        }

        report = self.recorder.finish(result, 0.5)

        self.assertEqual("goal_unverified", report["classification"])
        self.assertTrue(report["model_claimed_complete"])
        self.assertFalse(report["harness_accepted_completion"])
        self.assertFalse(report["local_completion_claim"])
        self.assertEqual({"status": "unverified", "accepted": False, "branch_id": None,
                          "missing_milestone_count": 0, "reason_code": "goal_unverified"},
                         report["completion_verification"])
        saved = json.loads((self.run_dir / "evaluation.json").read_text(encoding="utf-8"))
        self.assertNotIn("private claim text", json.dumps(saved))
        self.assertNotIn("private source text", json.dumps(saved))

    def test_accepted_um_review_handoff_can_be_complete_without_final_case_terminal_state(self):
        branches = ("um_review_completed_without_p2p", "um_review_completed_after_p2p")
        for index, branch in enumerate(branches):
            with self.subTest(branch=branch):
                recorder = RunRecorder(self.run_dir.parent / f"handoff-{index}", {})
                result = {
                    "status": "complete",
                    "final": {"status": "complete", "claim": "synthetic scoped review endpoint"},
                    "completion": {"branch_id": branch},
                    "completion_gate": {"accepted": True, "branch_id": branch,
                                        "case_can_remain_pending":True,
                                        "missing_milestones": [], "reason_code": "accepted"},
                }
                report = recorder.finish(result, 0.5, {"public_determination_terminal": False})
                self.assertEqual("locally_complete_ungraded", report["classification"])
                self.assertFalse(report["harness_claim_environment_mismatch"])
                self.assertFalse(report["whole_case_terminal_observed"])
                self.assertTrue(report["harness_accepted_completion"])
                self.assertIsNone(report["official_success"])

    def test_finalized_determination_branch_still_flags_nonterminal_world_readback(self):
        result = {
            "status": "complete",
            "final": {"status": "complete", "claim": "synthetic final determination"},
            "completion": {"branch_id": "um_finalized_determination"},
            "completion_gate": {"accepted": True, "branch_id": "um_finalized_determination",
                                "missing_milestones": [], "reason_code": "accepted"},
        }

        report = self.recorder.finish(result, 0.5, {"public_determination_terminal": False})

        self.assertEqual("incomplete_workflow", report["classification"])
        self.assertTrue(report["harness_claim_environment_mismatch"])
        self.assertFalse(report["whole_case_terminal_observed"])
        self.assertTrue(report["harness_accepted_completion"])
        self.assertIsNone(report["official_success"])

    def test_comparison_marks_unknown_metadata_and_controlled_composition_difference(self):
        a = {"metadata": {"task": "task-a", "model": "model-x", "effort": "high", "limits": {"calls": 3},
                           "initial_state_fingerprint": "s", "source_commit": "abc", "source_fingerprint": "src-1",
                           "composition": "single"},
             "metrics": {"model_calls": 2, "elapsed_seconds": 5}, "classification": "incomplete_workflow", "official_success": None}
        b = {"metadata": {"task": "task-a", "model": "model-x", "effort": "high", "limits": {"calls": 3},
                           "initial_state_fingerprint": "s", "source_commit": "abc", "source_fingerprint": "src-2",
                           "composition": "team"},
             "metrics": {"model_calls": 3, "elapsed_seconds": 7}, "classification": "incomplete_workflow", "official_success": None}
        comparison = compare_reports(a, b)
        self.assertEqual(comparison["comparability"]["task_id"], "same")
        self.assertEqual(comparison["comparability"]["composition"], "controlled_difference")
        self.assertEqual(comparison["comparability"]["source_fingerprint"], "different")
        self.assertEqual(comparison["comparison_scope"], "operational metrics only; no clinical or quality gain is inferred")
        self.assertEqual(comparison["deltas_b_minus_a"], {"model_calls": 1, "elapsed_seconds": 2})
        incomplete = compare_reports({"metadata": {}, "metrics": {}}, {"metadata": {}, "metrics": {}})
        self.assertEqual(incomplete["comparability"]["task_id"], "unknown")
        self.assertEqual(incomplete["comparability"]["source_commit"], "unknown")

    def test_journal_counts_override_wrapper_exception_counts_and_environment_stays_out_of_live_log(self):
        private_readback = {"public_determination_terminal": False, "summary_text": "protected determination body"}
        report = self.recorder.finish({"status": "blocked", "message": "case scope conflict",
                                       "journal_statuses": {"completed": 4, "pending": 1, "unknown": 0}},
                                      2.0, private_readback)
        self.assertEqual(report["classification"], "schema_or_scope_rejection")
        self.assertEqual(report["metrics"]["unknown_actions"], 0)
        self.assertEqual(report["actual_environment_observations"], private_readback)
        self.assertNotIn("protected determination body", (self.run_dir / "run.live.md").read_text(encoding="utf-8"))

    def test_run_directory_must_be_under_ignored_runs(self):
        with self.assertRaisesRegex(ValueError, "inside an ignored runs"):
            RunRecorder(Path(self.temp.name) / "outside", {})


if __name__ == "__main__":
    unittest.main()
