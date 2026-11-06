from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import urllib.error

from health_harness_codex.openrouter_batch import (
    API_ROOT,
    BATCH_MODEL,
    DEFAULT_MAX_BUDGET_USD,
    MODEL,
    OpenRouterBatchError,
    OpenRouterBatchJudgeRunner,
    OpenRouterBatchPending,
    OpenRouterBatchTransport,
    _execute_workspace_tool,
    estimate_cost,
    main,
)


REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "runs"


class _Response:
    def __init__(self, status, value):
        self.status = status
        self.value = value

    def read(self, limit=-1):
        raw = json.dumps(self.value).encode()
        return raw[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


class OpenRouterBatchTests(unittest.TestCase):
    def setUp(self):
        RUNS.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="openrouter-batch-tests-", dir=RUNS)
        self.root = Path(self.temp.name)
        self.calls = []

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def body(prompt="synthetic prompt", max_tokens=32):
        return {"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}

    def transport(self, responder, *, budget=DEFAULT_MAX_BUDGET_USD):
        def opener(request, timeout=30):
            self.calls.append((request, timeout))
            return responder(request, timeout)
        return OpenRouterBatchTransport(self.root, max_budget_usd=budget, opener=opener,
                                        key_loader=lambda: "test-key-do-not-persist")

    def test_cost_reservation_uses_utf8_bytes_protocol_margin_and_full_output_cap(self):
        estimate = estimate_cost(self.body("é", max_tokens=32))
        self.assertGreaterEqual(estimate["reserved_input_tokens"], estimate["request_utf8_bytes"])
        self.assertEqual(estimate["reserved_output_tokens"], 32)
        self.assertTrue(estimate["cache_write_worst_case_reserved"])
        self.assertGreater(estimate["input_reservation_rate_usd_per_million"], estimate["input_rate_usd_per_million"])
        self.assertEqual(estimate["model"], MODEL)
        self.assertEqual(estimate["request_model"], MODEL)
        self.assertEqual(estimate["batch_variant"], BATCH_MODEL)
        self.assertGreater(estimate["reservation_usd"], 0)

    def test_durable_reservation_precedes_post_and_unknown_outcome_is_not_retried(self):
        observed = []
        body = self.body("synthetic patient-like data")
        cap = estimate_cost(body)["reservation_usd"]
        def timeout_after_record(request, _timeout):
            ledger = json.loads((self.root / "openrouter_batch_ledger.json").read_text())
            observed.append((ledger["jobs"][0]["status"], ledger["jobs"][0]["reservation_usd"]))
            raise TimeoutError("OPENROUTER_API_KEY=secret; patient payload must not leak")
        transport = self.transport(timeout_after_record, budget=cap)
        with self.assertRaisesRegex(OpenRouterBatchError, "outcome is unknown") as caught:
            transport.submit(body)
        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(observed[0][0], "submitting")
        ledger_text = (self.root / "openrouter_batch_ledger.json").read_text()
        self.assertNotIn("test-key-do-not-persist", ledger_text)
        self.assertIn("synthetic patient-like data", ledger_text)
        summary = transport.ledger_summary()
        self.assertEqual(summary["jobs"][0]["status"], "unknown")
        self.assertEqual(summary["reserved_cost_usd"], observed[0][1])
        with self.assertRaisesRegex(OpenRouterBatchError, "budget would be exceeded"):
            transport.submit(self.body("second turn"))
        self.assertEqual(len(self.calls), 1)

    def test_submit_shape_poll_result_and_cost_reconciliation(self):
        def responder(request, _timeout):
            if request.method == "POST":
                payload = json.loads(request.data)
                self.assertEqual(request.full_url, API_ROOT + "/batches")
                self.assertEqual(payload["endpoint"], "/v1/messages")
                self.assertEqual(payload["model"], MODEL)
                self.assertEqual(payload["provider"], {"only": ["anthropic"], "allow_fallbacks": False})
                self.assertNotIn("model", payload["requests"][0]["body"])
                self.assertEqual(request.get_header("Authorization"), "Bearer test-key-do-not-persist")
                return _Response(202, {"id": "batch_abc", "status": "validating", "provider": "Anthropic"})
            self.assertEqual(request.full_url, API_ROOT + "/batches/batch_abc")
            return _Response(200, {
                "id": "batch_abc", "status": "completed",
                "request_counts": {"total": 1, "completed": 1, "failed": 0},
                "usage": {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16, "cost": 0.00008},
                "results": [{"custom_id": job_id, "response": {"status_code": 200, "body": {
                    "content": [{"type": "text", "text": "BATCH_OK"}],
                    "usage": {"input_tokens": 12, "output_tokens": 4}}}, "error": None}],
            })
        transport = self.transport(responder)
        submitted = transport.submit(self.body("Reply BATCH_OK"))
        job_id = submitted["job_id"]
        self.assertEqual(submitted["batch_id"], "batch_abc")
        self.assertGreater(transport.ledger_summary()["reserved_cost_usd"], 0)
        polled = transport.poll("batch_abc")
        self.assertEqual(polled["status"], "completed")
        self.assertEqual(polled["actual_cost_usd"], 0.00008)
        summary = transport.ledger_summary()
        self.assertEqual(summary["actual_cost_usd"], 0.00008)
        self.assertEqual(summary["reserved_cost_usd"], 0)
        self.assertEqual(summary["jobs"][0]["usage"]["prompt_tokens"], 12)

    def test_budget_blocks_new_post_and_limits_to_half_dollar(self):
        with self.assertRaises(OpenRouterBatchError):
            OpenRouterBatchTransport(self.root, max_budget_usd=0.500001)
        huge = self.body("x" * 1_000_000, max_tokens=4096)
        transport = self.transport(lambda *_: self.fail("budget check must happen before network"), budget=0.01)
        with self.assertRaisesRegex(OpenRouterBatchError, "budget would be exceeded"):
            transport.submit(huge)
        self.assertEqual(self.calls, [])
        self.assertFalse((self.root / "openrouter_batch_ledger.json").exists())

    def test_definite_rejection_releases_reservation(self):
        transport = self.transport(lambda *_: _Response(400, {"error": {"message": "withheld"}}))
        with self.assertRaisesRegex(OpenRouterBatchError, "HTTP 400"):
            transport.submit(self.body())
        summary = transport.ledger_summary()
        self.assertEqual(summary["jobs"][0]["status"], "failed_no_cost")
        self.assertEqual(summary["reserved_cost_usd"], 0)
        self.assertEqual(summary["actual_cost_usd"], 0)

    def test_http_error_metadata_is_bounded_and_redacted_in_private_ledger(self):
        raw = json.dumps({"error": {"code": 400, "message": "bad key test-key-do-not-persist Bearer test-key-do-not-persist"}}).encode()
        def fail_http(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 400, "bad request", {}, __import__("io").BytesIO(raw))
        transport = self.transport(fail_http)
        with self.assertRaisesRegex(OpenRouterBatchError, "HTTP 400"):
            transport.submit(self.body())
        ledger_text = transport.ledger_path.read_text()
        self.assertIn("bad key [REDACTED]", ledger_text)
        self.assertNotIn("test-key-do-not-persist", ledger_text)

    def test_failed_batch_with_explicit_zero_cost_releases_reservation(self):
        def responder(request, _timeout):
            if request.method == "POST":
                return _Response(202, {"id": "batch_fail", "status": "validating"})
            return _Response(200, {"id": "batch_fail", "status": "failed", "usage": {"cost": 0}, "results": None})
        transport = self.transport(responder)
        transport.submit(self.body())
        result = transport.poll("batch_fail")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(transport.ledger_summary()["reserved_cost_usd"], 0)

    def test_completed_batch_without_reported_cost_keeps_reservation(self):
        def responder(request, _timeout):
            if request.method == "POST":
                return _Response(202, {"id": "batch_nocost", "status": "validating"})
            return _Response(200, {"id": "batch_nocost", "status": "completed",
                                   "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                                   "results": [{"custom_id": job_id, "response": {"status_code": 200,
                                       "body": {"usage": {"input_tokens": 10, "output_tokens": 5},
                                                "content": [{"type": "text", "text": "ok"}]}}, "error": None}]})
        transport = self.transport(responder)
        submitted = transport.submit(self.body())
        job_id = submitted["job_id"]
        polled = transport.poll("batch_nocost")
        self.assertEqual(polled["status"], "completed")
        self.assertIsNone(polled["actual_cost_usd"])
        summary = transport.ledger_summary()
        self.assertEqual(summary["actual_cost_usd"], 0)
        self.assertEqual(summary["reserved_cost_usd"], submitted["reservation_usd"])

    def test_unrecognized_parameters_and_models_are_rejected(self):
        with self.assertRaisesRegex(OpenRouterBatchError, "unsupported request parameter"):
            estimate_cost({**self.body(), "temperature": 0})
        with self.assertRaisesRegex(OpenRouterBatchError, "only anthropic"):
            estimate_cost({**self.body(), "model": "some/other-model"})

    def test_workspace_tool_loop_is_confined_and_uses_results_on_next_turn(self):
        class FakeTransport:
            def __init__(self):
                self.requests = []
                self.n = 0
                self.sessions = {}
                self.tools = {}
            def submit(self, body, session_state=None):
                self.requests.append(body)
                self.n += 1
                job = f"job-{self.n}"
                batch = f"batch-{self.n}"
                self.sessions[session_state["session_id"]] = dict(session_state)
                self.sessions[session_state["session_id"]].update({"submission_job_id": job,
                    "pending_batch": {"job_id": job, "batch_id": batch, "custom_id": job}, "phase": "waiting"})
                return {"job_id": job, "custom_id": job, "batch_id": batch}
            def poll(self, batch_id, timeout=30):
                if batch_id == "batch-1":
                    content = [{"type": "tool_use", "id": "tool-1", "name": "Write",
                                "input": {"file_path": "answer.txt", "content": "local synthetic result"}}]
                    custom = "job-1"
                else:
                    content = [{"type": "text", "text": "judge response"}]
                    custom = "job-2"
                return {"status": "completed", "job_id": custom, "custom_id": custom,
                        "result": {"results": [{"custom_id": custom,
                        "response": {"status_code": 200, "body": {"content": content}}, "error": None}]}}
            def save_session(self, job_id, session_state):
                self.sessions[session_state["session_id"]] = dict(session_state)
            def load_session(self, session_id):
                return dict(self.sessions[session_id])
            def job_for_session(self, _session_id):
                return {"status": "unknown"}
            def execute_tool_once(self, _job_id, tool_id, action):
                if tool_id not in self.tools:
                    self.tools[tool_id] = action()
                return self.tools[tool_id]
        workspace = self.root / "workspace"
        workspace.mkdir()
        fake = FakeTransport()
        runner = OpenRouterBatchJudgeRunner(self.root, transport=fake)
        answer = runner.run_session("synthetic untouched prompt", workspace, ["Read", "Write"])
        self.assertEqual(answer, "judge response")
        self.assertEqual((workspace / "answer.txt").read_text(), "local synthetic result")
        self.assertEqual(fake.requests[0]["messages"][0]["content"], "synthetic untouched prompt")
        self.assertEqual(fake.requests[1]["messages"][-1]["content"][0]["type"], "tool_result")
        self.assertIn("Wrote answer.txt", fake.requests[1]["messages"][-1]["content"][0]["content"])
        self.assertEqual(fake.sessions[next(iter(fake.sessions))]["phase"], "complete")

    def test_durable_pending_resume_polls_existing_batch_without_resubmission(self):
        state = {"gets": 0, "custom_id": None}
        def responder(request, _timeout):
            if request.method == "POST":
                payload = json.loads(request.data)
                state["custom_id"] = payload["requests"][0]["custom_id"]
                return _Response(202, {"id": "batch_resume", "status": "validating"})
            state["gets"] += 1
            if state["gets"] == 1:
                return _Response(200, {"id": "batch_resume", "status": "in_progress"})
            return _Response(200, {"id": "batch_resume", "status": "completed", "results": [
                {"custom_id": state["custom_id"], "response": {"status_code": 200,
                 "body": {"content": [{"type": "text", "text": "resumed answer"}]}}, "error": None}]})
        transport = self.transport(responder)
        workspace = self.root / "workspace-resume"
        workspace.mkdir()
        runner = OpenRouterBatchJudgeRunner(self.root, transport=transport)
        with self.assertRaises(OpenRouterBatchPending) as pending:
            runner.run_session("synthetic prompt", workspace, [], timeout_seconds=1)
        ledger = json.loads((self.root / "openrouter_batch_ledger.json").read_text())
        session_id = pending.exception.session_id
        self.assertIsNotNone(session_id)
        self.assertEqual(ledger["jobs"][0]["session"]["pending_batch"]["batch_id"], "batch_resume")
        self.assertEqual(ledger["jobs"][0]["status"], "in_progress")
        # A fresh runner instance reloads the session from the durable ledger.
        resumed_runner = OpenRouterBatchJudgeRunner(self.root, transport=transport)
        self.assertEqual(resumed_runner.resume_session(session_id), "resumed answer")
        self.assertEqual(sum(1 for request, _ in self.calls if request.method == "POST"), 1)
        self.assertEqual(state["gets"], 2)
        self.assertEqual(transport.ledger_summary()["jobs"][0]["status"], "completed_unknown_cost")

    def test_tool_execution_checkpoint_refuses_replay_after_unknown_outcome(self):
        transport = self.transport(lambda *_: _Response(202, {"id": "batch_tool", "status": "validating"}))
        transport.submit(self.body(), session_state={"session_id": "session-tool", "phase": "ready"})
        summary = transport.ledger_summary()
        job_id = summary["jobs"][0]["job_id"]
        # Simulate a process stopping after the durable pre-effect marker.
        with open(transport.ledger_path, "r+", encoding="utf-8") as f:
            ledger = json.load(f)
            ledger["jobs"][0]["tool_execution"]["tool-1"] = "executing"
            f.seek(0)
            json.dump(ledger, f)
            f.truncate()
        with self.assertRaisesRegex(OpenRouterBatchError, "refusing to replay"):
            transport.execute_tool_once(job_id, "tool-1", lambda: "must not run")

    def test_workspace_tools_reject_parent_and_symlink_escape(self):
        workspace = self.root / "workspace"
        outside = self.root / "outside.txt"
        workspace.mkdir()
        outside.write_text("sentinel")
        self.assertIn("escapes cwd", _execute_workspace_tool(workspace, "Read", {"file_path": "../outside.txt"}))
        (workspace / "link.txt").symlink_to(outside)
        self.assertIn("symbolic link", _execute_workspace_tool(workspace, "Read", {"file_path": "link.txt"}))
        self.assertIn("symbolic link", _execute_workspace_tool(workspace, "Write", {"file_path": "link.txt", "content": "changed"}))
        self.assertEqual(outside.read_text(), "sentinel")

    def test_plan_only_smoke_is_read_only_and_reports_model_budget(self):
        before = list(self.root.iterdir())
        code = main(["--run-dir", str(self.root), "--max-budget-usd", "0.50"])
        after = list(self.root.iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
