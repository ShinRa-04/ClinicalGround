import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from health_harness_codex.models import ModelReply
from health_harness_codex.providers import ProviderError
from health_harness_codex.simulator_worker import (
    APPROVED_INSTRUCTION_SHA256,
    APPROVED_INSTRUCTION_SOURCE,
    BACKEND_EFFORT,
    BACKEND_MODEL,
    MAX_OUTPUT_BYTES,
    SimulatorWorker,
    SimulatorWorkerError,
    _canonical_json,
)


_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_RUNS_ROOT = _PACKAGE_ROOT / "runs"


class _FakeCodex:
    def __init__(self, reply=None, error=None):
        self.reply = reply or ModelReply(
            content="A synthetic text-only reply.",
            usage={"input_tokens": 7, "output_tokens": 5},
        )
        self.error = error
        self.calls = []

    def complete(self, messages, tools, *, max_output_tokens):
        self.calls.append((messages, list(tools), max_output_tokens))
        if self.error is not None:
            raise self.error
        return self.reply


class SimulatorWorkerTests(TestCase):
    def setUp(self):
        _RUNS_ROOT.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=str(_RUNS_ROOT))
        self.spool = Path(self.temp.name) / "simulator-spool"
        self.kind = "cm_patient"
        self.instances = []
        self.factory_kwargs = []

    def tearDown(self):
        self.temp.cleanup()

    def _factory(self, reply=None, error=None):
        def create(executable, **kwargs):
            self.factory_kwargs.append(dict(kwargs))
            self.assertTrue(Path(executable).is_absolute())
            self.assertEqual(BACKEND_MODEL, kwargs["model"])
            self.assertEqual(BACKEND_EFFORT, kwargs["reasoning_effort"])
            model = _FakeCodex(reply=reply, error=error)
            self.instances.append(model)
            return model
        return create

    def _worker(self, **kwargs):
        model_factory = kwargs.pop("model_factory", None)
        if model_factory is None:
            model_factory = self._factory(reply=kwargs.pop("reply", None), error=kwargs.pop("error", None))
        kwargs.setdefault("allowed_instruction_sources", {
            str(APPROVED_INSTRUCTION_SOURCE): APPROVED_INSTRUCTION_SHA256,
        })
        return SimulatorWorker(
            self.spool,
            self.kind,
            Path("C:/Codex/codex.exe"),
            model_factory=model_factory,
            **kwargs,
        )

    def _body(self, **overrides):
        body = {
            "model": "claude-sonnet-5",
            "max_tokens": 1024,
            "system": "Synthetic simulator system prompt.",
            "messages": [{"role": "user", "content": "Synthetic simulator input."}],
            "stream": False,
        }
        body.update(overrides)
        return body

    def _envelope(self, body=None, *, kind=None):
        body = self._body() if body is None else body
        kind = self.kind if kind is None else kind
        canonical = _canonical_json(body)
        body_sha256 = hashlib.sha256(canonical).hexdigest()
        request_id = hashlib.sha256(
            kind.encode() + b"\0" + BACKEND_MODEL.encode() + b"\0" + BACKEND_EFFORT.encode()
            + b"\0" + canonical
        ).hexdigest()
        return request_id, {
            "schema_version": 1,
            "request_id": request_id,
            "created_at": "2026-10-21T00:00:00Z",
            "simulator_kind": kind,
            "request_model": body["model"],
            "backend_model": BACKEND_MODEL,
            "backend_effort": BACKEND_EFFORT,
            "request_body_b64": base64.b64encode(canonical).decode("ascii"),
            "body_sha256": body_sha256,
        }

    def _enqueue(self, body=None, *, kind=None):
        request_id, envelope = self._envelope(body, kind=kind)
        inbox = self.spool / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        path = inbox / f"{request_id}.json"
        path.write_bytes(_canonical_json(envelope) + b"\n")
        return request_id, path

    def _outbox(self, request_id):
        return json.loads((self.spool / "outbox" / f"{request_id}.json").read_text(encoding="utf-8"))

    def test_valid_request_uses_fresh_codex_call_without_tools_and_preserves_actual_usage(self):
        approved_sources = {
            "C:/Users/prath/.codex/AGENTS.md":
                "1c683adadd4bffe13c4ff0700dc824fd3f3f35c024ffc3b6c68959f887318f96",
        }
        worker = self._worker(allowed_instruction_sources=approved_sources)
        request_id, _ = self._enqueue()

        self.assertTrue(worker.run_once())

        self.assertEqual(1, len(self.instances))
        messages, tools, max_output_tokens = self.instances[0].calls[0]
        self.assertEqual([
            {"role": "system", "content": "Synthetic simulator system prompt."},
            {"role": "user", "content": "Synthetic simulator input."},
        ], messages)
        self.assertEqual([], tools)
        self.assertEqual(1024, max_output_tokens)
        self.assertEqual(approved_sources, self.factory_kwargs[0]["allowed_instruction_sources"])
        response = self._outbox(request_id)
        self.assertEqual("ok", response["status"])
        wire = response["anthropic_response"]
        self.assertEqual("gpt-6-luna", wire["model"])
        self.assertEqual("A synthetic text-only reply.", wire["content"][0]["text"])
        self.assertEqual({"input_tokens": 7, "output_tokens": 5}, wire["usage"])
        self.assertEqual({"id", "type", "role", "model", "content", "stop_reason", "stop_sequence", "usage"},
                         set(wire))
        self.assertEqual(1, worker.summary().submitted_calls)
        self.assertEqual(1, worker.summary().completed_calls)
        self.assertTrue((self.spool / "submitted" / f"{request_id}.json").is_file())
        receipt = json.loads((self.spool / "receipts" / f"{request_id}.json").read_text(encoding="utf-8"))
        self.assertEqual("gpt-6-luna", receipt["backend_model"])
        self.assertEqual("claude-sonnet-5", receipt["upstream_requested_model"])
        self.assertEqual(1024, receipt["requested_max_output_tokens_advisory"])
        self.assertNotIn("Synthetic simulator", (self.spool / "worker.events.jsonl").read_text(encoding="utf-8"))

    def test_marker_only_patient_stop_uses_second_budgeted_call_and_retains_stop(self):
        replies = iter(["  ###STOP###\n", "Goodbye. ###STOP###"])
        def factory(*args, **kwargs):
            model = _FakeCodex(reply=ModelReply(content=next(replies), usage={"input_tokens":7,"output_tokens":5}))
            self.instances.append(model)
            return model
        worker = self._worker(model_factory=factory)
        request_id, _ = self._enqueue()
        self.assertTrue(worker.run_once())
        text = self._outbox(request_id)["anthropic_response"]["content"][0]["text"]
        self.assertEqual("Goodbye. ###STOP###", text)
        self.assertTrue(text.replace("###STOP###", "").strip())
        self.assertEqual(2, len(self.instances))
        self.assertEqual(2, worker.summary().submitted_calls)
        self.assertEqual(2, worker.summary().completed_calls)
        receipt = json.loads((self.spool / "receipts" / f"{request_id}.json").read_text())
        self.assertEqual("  ###STOP###\n", receipt["output_adaptation"]["raw_text"])
        self.assertEqual('budgeted_stop_farewell',receipt['output_adaptation']['kind'])
        self.assertEqual(5, receipt["output_tokens"])
        self.assertEqual({'input_tokens':14,'output_tokens':10}, self._outbox(request_id)['anthropic_response']['usage'])
        self.assertEqual(2, self._worker().summary().submitted_calls)

    def test_marker_only_stop_cannot_bypass_model_budget_or_recurse(self):
        for cap, expected_calls, code in [(1,1,'call_budget_exhausted'),(8,2,'model_output_invalid')]:
            with self.subTest(cap=cap):
                # Each scenario has its own per-world spool.
                self.spool = self.spool.parent / f'stop-budget-{cap}'
                self.instances.clear()
                worker = self._worker(max_calls=cap,reply=ModelReply(content='###STOP###',usage={'input_tokens':1,'output_tokens':1}))
                request_id,_=self._enqueue()
                self.assertTrue(worker.run_once())
                self.assertEqual(expected_calls, len(self.instances))
                self.assertEqual(expected_calls,worker.summary().submitted_calls)
                self.assertEqual('error',self._outbox(request_id)['status'])
                self.assertEqual(code,self._outbox(request_id)['error_code'])
                saved=json.loads((self.spool/f'stop-{request_id}.private.json').read_text())
                self.assertEqual('###STOP###',saved['raw_text'])
                self.assertEqual({'input_tokens':1,'output_tokens':1},saved['usage'])

    def test_farewell_correction_respects_shared_character_and_request_time_budgets(self):
        # A fast fake model may finish inside one monotonic-clock tick. Advance
        # an explicit clock during inference so deadline coverage is deterministic.
        clock = [1000.0]
        original_complete = _FakeCodex.complete
        def complete(model, *args, **kwargs):
            reply = original_complete(model, *args, **kwargs)
            clock[0] += 0.25
            return reply
        for constraint in ('characters','time'):
            with self.subTest(constraint=constraint), patch(
                    'health_harness_codex.simulator_worker.time.monotonic', side_effect=lambda: clock[0]), patch.object(
                    _FakeCodex, 'complete', complete):
                self.spool=self.spool.parent/f'stop-{constraint}'
                self.instances.clear()
                worker=self._worker(reply=ModelReply(content='###STOP###',usage={'input_tokens':1,'output_tokens':1}),
                    **({'max_total_chars_per_world':4} if constraint=='characters' else {'request_timeout':1}))
                request_id,_=self._enqueue(self._body(system='s',messages=[{'role':'user','content':'abc'}]))
                self.assertTrue(worker.run_once())
                self.assertEqual(1,len(self.instances))
                self.assertEqual('error',self._outbox(request_id)['status'])
                self.assertEqual('world_char_budget_exhausted' if constraint=='characters' else 'world_deadline_exceeded',
                    self._outbox(request_id)['error_code'])

    def test_stop_with_patient_words_is_preserved_verbatim(self):
        text = "I need to end this call. ###STOP###"
        worker = self._worker(reply=ModelReply(content=text, usage={"input_tokens": 7, "output_tokens": 5}))
        request_id, _ = self._enqueue()
        self.assertTrue(worker.run_once())
        self.assertEqual(text, self._outbox(request_id)["anthropic_response"]["content"][0]["text"])
        receipt = json.loads((self.spool / "receipts" / f"{request_id}.json").read_text())
        self.assertNotIn("output_adaptation", receipt)
        self.assertNotIn("Synthetic simulator", (self.spool / "receipts" / f"{request_id}.json").read_text(encoding="utf-8"))

    def test_identical_request_after_success_uses_cached_response_without_second_inference(self):
        worker = self._worker()
        request_id, _ = self._enqueue()
        worker.run_once()
        self._enqueue()

        worker.run_once()

        self.assertEqual(1, len(self.instances[0].calls))
        self.assertEqual("ok", self._outbox(request_id)["status"])
        events = [json.loads(line) for line in (self.spool / "worker.events.jsonl").read_text().splitlines()]
        self.assertEqual("cached_response", events[-1]["status"])

    def test_concurrent_claims_for_same_request_make_one_codex_call(self):
        worker = self._worker()
        request_id, _ = self._enqueue()
        barrier = threading.Barrier(3)
        results = []

        def run_worker_once():
            barrier.wait()
            try:
                results.append(worker.run_once())
            except SimulatorWorkerError:
                results.append("owner_locked")

        threads = [threading.Thread(target=run_worker_once) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join(timeout=10)

        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(1, len(self.instances))
        self.assertEqual(1, len(self.instances[0].calls))
        self.assertEqual("ok", self._outbox(request_id)["status"])
        self.assertEqual(1, results.count(True))
        self.assertEqual(1, results.count("owner_locked"))

    def test_second_worker_cannot_recover_or_mutate_a_live_world_spool(self):
        entered = threading.Event()
        release = threading.Event()

        class BlockingCodex(_FakeCodex):
            def complete(self, messages, tools, *, max_output_tokens):
                self.calls.append((messages, list(tools), max_output_tokens))
                entered.set()
                if not release.wait(timeout=5):
                    raise TimeoutError()
                return self.reply

        def first_factory(_executable, **_kwargs):
            model = BlockingCodex()
            self.instances.append(model)
            return model

        first = self._worker(model_factory=first_factory)
        request_id, _ = self._enqueue()
        first.start()
        self.assertTrue(entered.wait(timeout=5))

        child_script = """
import sys
from pathlib import Path
from health_harness_codex.simulator_worker import (
    APPROVED_INSTRUCTION_SHA256, APPROVED_INSTRUCTION_SOURCE,
    SimulatorWorker, SimulatorWorkerError,
)
worker = SimulatorWorker(
    Path(sys.argv[1]), "cm_patient", Path("C:/Codex/codex.exe"),
    model_factory=lambda *_args, **_kwargs: None,
    allowed_instruction_sources={str(APPROVED_INSTRUCTION_SOURCE): APPROVED_INSTRUCTION_SHA256},
)
try:
    worker.start()
except SimulatorWorkerError as exc:
    if "already owned" not in str(exc):
        raise
else:
    worker.stop(timeout=5)
    raise SystemExit("second process acquired the live spool")
"""
        child = subprocess.run(
            [sys.executable, "-c", child_script, str(self.spool)],
            cwd=str(_PACKAGE_ROOT), capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(0, child.returncode, child.stderr)
        self.assertFalse((self.spool / "outbox" / f"{request_id}.json").exists())
        self.assertEqual("submitted", json.loads(
            (self.spool / "claims" / f"{request_id}.json").read_text(encoding="utf-8")
        )["status"])

        second = self._worker()
        with self.assertRaisesRegex(SimulatorWorkerError, "already owned"):
            second.start()
        self.assertFalse((self.spool / "outbox" / f"{request_id}.json").exists())
        self.assertEqual("submitted", json.loads(
            (self.spool / "claims" / f"{request_id}.json").read_text(encoding="utf-8")
        )["status"])

        release.set()
        summary = first.stop(timeout=10)
        self.assertEqual("ok", self._outbox(request_id)["status"])
        self.assertEqual(1, summary.completed_calls)
        self.assertTrue(summary.settled)

    def test_submitted_claim_without_response_is_unknown_and_never_replayed(self):
        request_id, _ = self._enqueue()
        claims = self.spool / "claims"
        claims.mkdir()
        (claims / f"{request_id}.json").write_text(json.dumps({
            "request_id": request_id, "status": "submitted", "body_sha256": self._envelope()[1]["body_sha256"],
            "input_chars": 61,
        }), encoding="utf-8")
        worker = self._worker()

        worker._recover_submitted_without_response()
        worker.run_once()

        self.assertEqual([], self.instances)
        self.assertEqual("submitted_outcome_unknown", self._outbox(request_id)["error_code"])
        self.assertEqual(1, worker.summary().unknown_calls)

    def test_cancel_claim_wins_before_worker_and_prevents_late_inference(self):
        request_id, _ = self._enqueue()
        claims = self.spool / "claims"
        claims.mkdir()
        (claims / f"{request_id}.json").write_text(json.dumps({
            "request_id": request_id, "status": "cancelled", "body_sha256": self._envelope()[1]["body_sha256"],
        }), encoding="utf-8")
        worker = self._worker()

        worker.run_once()

        self.assertEqual([], self.instances)
        self.assertEqual("cancelled_before_submission", self._outbox(request_id)["error_code"])

    def test_codex_exception_after_submission_is_unknown_and_never_reinferred(self):
        worker = self._worker(model_factory=self._factory(error=TimeoutError()))
        request_id, _ = self._enqueue()

        worker.run_once()
        self._enqueue()
        worker.run_once()

        self.assertEqual(1, len(self.instances[0].calls))
        self.assertEqual("submitted_outcome_unknown", self._outbox(request_id)["error_code"])
        self.assertEqual(1, worker.summary().unknown_calls)

    def test_provider_failure_metadata_is_allowlisted_and_unknown_is_not_replayed(self):
        sensitive_message = "SYNTHETIC-PRIVATE provider diagnostic prose"
        error = ProviderError(
            sensitive_message,
            failure_category="turn_failed:failed:serverOverloaded",
            proposal_dispatch_safe=True,
            transient_retry_eligible=True,
        )
        worker = self._worker(error=error)
        request_id, _ = self._enqueue()

        worker.run_once()
        self._enqueue()
        worker.run_once()

        self.assertEqual(1, len(self.instances[0].calls))
        self.assertEqual("submitted_outcome_unknown", self._outbox(request_id)["error_code"])
        receipt = json.loads((self.spool / "receipts" / f"{request_id}.json").read_text(encoding="utf-8"))
        self.assertEqual("ProviderError", receipt["exception_type"])
        self.assertEqual("turn_failed:failed:serverOverloaded", receipt["failure_category"])
        self.assertIs(receipt["proposal_dispatch_safe"], True)
        events = [json.loads(line) for line in (self.spool / "worker.events.jsonl").read_text(encoding="utf-8").splitlines()]
        event = next(record for record in events if record.get("exception_type") == "ProviderError")
        self.assertEqual("submitted_outcome_unknown", event["status"])
        self.assertEqual("ProviderError", event["exception_type"])
        self.assertEqual("turn_failed:failed:serverOverloaded", event["failure_category"])
        self.assertIs(event["proposal_dispatch_safe"], True)
        self.assertNotIn(sensitive_message, json.dumps(receipt))
        self.assertNotIn(sensitive_message, json.dumps(event))
        self.assertEqual("cached_response", events[-1]["status"])

    def test_unrecognized_provider_failure_category_is_not_persisted(self):
        error = ProviderError(
            "SYNTHETIC-PRIVATE unrecognized category",
            failure_category="turn_failed:failed:SENSITIVE-UNALLOWLISTED",
            proposal_dispatch_safe="yes",
        )
        worker = self._worker(error=error)
        request_id, _ = self._enqueue()

        worker.run_once()

        receipt = json.loads((self.spool / "receipts" / f"{request_id}.json").read_text(encoding="utf-8"))
        self.assertEqual("ProviderError", receipt["exception_type"])
        self.assertNotIn("failure_category", receipt)
        self.assertNotIn("proposal_dispatch_safe", receipt)
        self.assertNotIn("SENSITIVE-UNALLOWLISTED", json.dumps(receipt))

    def test_wrong_kind_is_rejected_before_codex_and_has_no_raw_text_in_receipt(self):
        request_id, _ = self._enqueue(kind="p2p_counterparty")
        worker = self._worker()

        worker.run_once()

        self.assertEqual([], self.instances)
        self.assertEqual("simulator_kind_mismatch", self._outbox(request_id)["error_code"])
        receipt = (self.spool / "receipts" / f"{request_id}.json").read_text(encoding="utf-8")
        self.assertNotIn("Synthetic simulator", receipt)

    def test_p2p_request_respects_advisory_output_limit(self):
        self.kind = "p2p_counterparty"
        worker = self._worker()
        valid_id, _ = self._enqueue(self._body(max_tokens=512))

        worker.run_once()

        self.assertEqual(512, self.instances[0].calls[0][2])
        self.assertEqual("ok", self._outbox(valid_id)["status"])
        oversized_id, _ = self._enqueue(self._body(max_tokens=513))
        worker.run_once()
        self.assertEqual("unsupported_request", self._outbox(oversized_id)["error_code"])
        self.assertEqual(1, len(self.instances))

    def test_bad_body_hash_is_rejected_without_inference(self):
        request_id, path = self._enqueue()
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["body_sha256"] = "0" * 64
        path.write_bytes(_canonical_json(envelope))
        worker = self._worker()

        worker.run_once()

        self.assertEqual([], self.instances)
        self.assertEqual("invalid_request", self._outbox(request_id)["error_code"])

    def test_tool_use_streaming_and_stop_sequences_are_rejected_without_call(self):
        invalid_bodies = (
            self._body(tools=[{"name": "submit", "input_schema": {}}]),
            self._body(stream=True),
            self._body(stop_sequences=["END"]),
        )
        worker = self._worker()
        for body in invalid_bodies:
            request_id, _ = self._enqueue(body)
            worker.run_once()
            self.assertEqual("unsupported_request", self._outbox(request_id)["error_code"])
        self.assertEqual([], self.instances)

    def test_missing_usage_is_an_explicit_error_not_zero_measurements(self):
        worker = self._worker(reply=ModelReply(content="A synthetic reply.", usage={}))
        request_id, _ = self._enqueue()

        worker.run_once()

        self.assertEqual("model_usage_unavailable", self._outbox(request_id)["error_code"])
        receipt = json.loads((self.spool / "receipts" / f"{request_id}.json").read_text(encoding="utf-8"))
        self.assertNotIn("input_tokens", receipt)
        self.assertNotIn("output_tokens", receipt)

    def test_oversized_model_text_is_rejected_without_truncation_or_body_logging(self):
        secret = "SYNTHETIC-PRIVATE-" + ("x" * MAX_OUTPUT_BYTES)
        worker = self._worker(reply=ModelReply(
            content=secret, usage={"input_tokens": 1, "output_tokens": 2}))
        request_id, _ = self._enqueue()

        worker.run_once()

        self.assertEqual("model_output_invalid", self._outbox(request_id)["error_code"])
        self.assertNotIn("anthropic_response", self._outbox(request_id))
        for path in (self.spool / "worker.events.jsonl", self.spool / "receipts" / f"{request_id}.json"):
            self.assertNotIn("SYNTHETIC-PRIVATE", path.read_text(encoding="utf-8"))

    def test_total_character_budget_and_world_deadline_are_enforced_before_model_call(self):
        worker = self._worker(max_total_chars_per_world=10)
        body = self._body(system="s", messages=[{"role": "user", "content": "abc"}])
        first_id, _ = self._enqueue(body)
        worker.run_once()
        self.assertEqual("ok", self._outbox(first_id)["status"])
        second_body = self._body(system="long", messages=[{"role": "user", "content": "long text"}])
        second_id, _ = self._enqueue(second_body)

        worker.run_once()

        self.assertEqual("world_char_budget_exhausted", self._outbox(second_id)["error_code"])
        self.assertEqual(1, sum(len(model.calls) for model in self.instances))

        deadline_worker = self._worker(max_world_deadline_seconds=1)
        deadline_worker._started_monotonic -= 2
        deadline_id, _ = self._enqueue()
        deadline_worker.run_once()
        self.assertEqual("world_deadline_exceeded", self._outbox(deadline_id)["error_code"])
        self.assertEqual(1, sum(len(model.calls) for model in self.instances))

    def test_call_budget_is_separate_and_summary_records_advisory_limits(self):
        worker = self._worker(max_calls=1)
        first_id, _ = self._enqueue()
        worker.run_once()
        second_body = self._body(messages=[{"role": "user", "content": "Different input."}])
        second_id, _ = self._enqueue(second_body)

        worker.run_once()

        self.assertEqual("call_budget_exhausted", self._outbox(second_id)["error_code"])
        summary = worker.summary()
        self.assertEqual(1, summary.max_calls)
        self.assertEqual(0, summary.max_total_chars_per_world)
        self.assertEqual(0, summary.max_world_deadline_seconds)
        self.assertEqual(1, summary.submitted_calls)
        self.assertEqual("ok", self._outbox(first_id)["status"])

    def test_zero_patient_quotas_allow_longer_dialogue_without_replay(self):
        worker=self._worker(max_calls=0,max_total_chars_per_world=0,max_world_deadline_seconds=0)
        worker._started_monotonic -= 10000
        for index in range(12):
            request_id,_=self._enqueue(self._body(system='s'*16000,
                messages=[{'role':'user','content':f'New question {index}'}]))
            self.assertTrue(worker.run_once())
            self.assertEqual('ok',self._outbox(request_id)['status'])
        self.assertEqual(12,worker.summary().completed_calls)
        self.assertGreater(worker.summary().total_input_chars,180000)
        self.assertEqual(12,len(self.instances))

    def test_stop_cancels_unclaimed_inbox_without_model_call_and_reports_settled(self):
        worker = self._worker()
        request_id, _ = self._enqueue()

        summary = worker.stop()

        self.assertEqual([], self.instances)
        self.assertEqual("cancelled_before_submission", self._outbox(request_id)["error_code"])
        self.assertEqual(0, summary.pending_inbox_requests)
        self.assertEqual(1, summary.cancelled_requests)
        self.assertEqual(0, summary.unresolved_requests)
        self.assertTrue(summary.settled)

    def test_stop_marks_submitted_without_response_unresolved(self):
        request_id, _ = self._enqueue()
        claims = self.spool / "claims"
        claims.mkdir()
        (claims / f"{request_id}.json").write_text(json.dumps({
            "request_id": request_id, "status": "submitted",
            "body_sha256": self._envelope()[1]["body_sha256"], "input_chars": 61,
        }), encoding="utf-8")
        worker = self._worker()

        summary = worker.stop()

        self.assertEqual([], self.instances)
        self.assertEqual("submitted_outcome_unknown", self._outbox(request_id)["error_code"])
        self.assertEqual(1, summary.unknown_calls)
        self.assertEqual(1, summary.unresolved_requests)
        self.assertFalse(summary.settled)

    def test_symlinked_inbox_request_is_never_followed(self):
        worker = self._worker()
        inbox = self.spool / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        external = Path(self.temp.name) / "outside.json"
        external.write_text("{}", encoding="utf-8")
        request_id = "a" * 64
        link = inbox / f"{request_id}.json"
        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is not available in this Windows environment")

        worker.run_once()

        self.assertEqual("{}", external.read_text(encoding="utf-8"))
        self.assertEqual([], self.instances)
        self.assertEqual("invalid_request", json.loads(
            (self.spool / "worker.events.jsonl").read_text(encoding="utf-8").splitlines()[-1]
        )["status"])

    def test_request_path_outside_ignored_runs_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaisesRegex(SimulatorWorkerError, "inside ignored local run data"):
                SimulatorWorker(
                    Path(outside) / "simulator-spool", self.kind, Path("C:/Codex/codex.exe"),
                    model_factory=self._factory())

    def test_worker_rejects_unapproved_instruction_hash_before_spool_setup(self):
        with self.assertRaisesRegex(SimulatorWorkerError, "unapproved Codex instruction hash"):
            SimulatorWorker(
                self.spool, self.kind, Path("C:/Codex/codex.exe"),
                allowed_instruction_sources={str(APPROVED_INSTRUCTION_SOURCE): "0" * 64},
                model_factory=self._factory(),
            )
        self.assertFalse((self.spool / "inbox").exists())
        self.assertFalse((self.spool / "claims").exists())

    def test_symlinked_spool_root_outside_ignored_runs_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=str(_RUNS_ROOT)) as link_parent, \
                tempfile.TemporaryDirectory() as outside:
            link = Path(link_parent) / "simulator-spool"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is not available in this Windows environment")
            with self.assertRaisesRegex(SimulatorWorkerError, "may not be symlinks"):
                SimulatorWorker(link, self.kind, Path("C:/Codex/codex.exe"),
                                model_factory=self._factory())


class SimulatorEffortTests(TestCase):
    def test_effort_is_validated_and_defaults_to_high(self):
        from health_harness_codex.simulator_worker import SIMULATOR_EFFORTS, BACKEND_EFFORT
        self.assertEqual('high', BACKEND_EFFORT)
        self.assertIn('low', SIMULATOR_EFFORTS)
        with self.assertRaises(ValueError):
            SimulatorWorker(tempfile.mkdtemp(), 'cm_patient', sys.executable, backend_effort='bogus')
