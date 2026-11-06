from __future__ import annotations

import base64
import hashlib
import http.client
import json
import os
from pathlib import Path
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from health_harness_codex.simulator_bridge import SimulatorBridge


LOCAL_KEY = "codex-local-bridge"


def _body() -> dict:
    return {
        "model": "claude-sonnet-5",
        "max_tokens": 512,
        "system": "Synthetic simulator instruction.",
        "messages": [{"role": "user", "content": "Synthetic user turn."}],
        "thinking": {"type": "disabled"},
    }


def _exclusive_json(path: Path, value: dict) -> None:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


class SimulatorBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = self.enterContext(__import__("tempfile").TemporaryDirectory())
        self.bridge = SimulatorBridge(
            Path(self.temp) / "spool", "p2p_counterparty", port=0,
            request_timeout=1, poll_interval=0.01,
        )
        self.bridge.start()
        self.url = f"http://127.0.0.1:{self.bridge.port}"

    def tearDown(self):
        self.bridge.shutdown()

    def _post(self, body: dict, *, api_key: str = LOCAL_KEY):
        request = Request(
            self.url + "/v1/messages",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-api-key": api_key},
            method="POST",
        )
        return urlopen(request, timeout=3)

    def _write_fake_success(self, envelope: dict, text: str = "Synthetic counterpart reply."):
        request_id = envelope["request_id"]
        spool = Path(self.temp) / "spool"
        _exclusive_json(spool / "claims" / f"{request_id}.json", {
            "schema_version": 1, "request_id": request_id, "status": "submitted",
            "body_sha256": envelope["body_sha256"],
        })
        _exclusive_json(spool / "submitted" / f"{request_id}.json", {
            "schema_version": 1, "request_id": request_id, "status": "submitted",
            "body_sha256": envelope["body_sha256"],
        })
        _exclusive_json(spool / "outbox" / f"{request_id}.json", {
            "schema_version": 1, "request_id": request_id, "status": "ok",
            "anthropic_response": {
                "id": "msg-synthetic", "type": "message", "role": "assistant",
                "model": "gpt-6-luna", "content": [{"type": "text", "text": text}],
                "stop_reason": "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 3},
            },
        })

    def test_health_is_loopback_ready_without_model_call(self):
        with urlopen(self.url + "/health", timeout=2) as response:
            self.assertEqual(200, response.status)
            value = json.loads(response.read())
        self.assertEqual({"status": "ready", "simulator_kind": "p2p_counterparty"}, value)
        self.assertEqual([], list((Path(self.temp) / "spool" / "inbox").glob("*.json")))

    def test_post_spools_canonical_envelope_and_returns_cached_response(self):
        body = _body()
        inbox = Path(self.temp) / "spool" / "inbox"
        worker_calls = []
        stop = threading.Event()

        def worker():
            while not stop.is_set():
                files = list(inbox.glob("*.json"))
                if files:
                    envelope = json.loads(files[0].read_text(encoding="utf-8"))
                    worker_calls.append(envelope)
                    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True,
                                           separators=(",", ":")).encode("utf-8")
                    body_hash = hashlib.sha256(canonical).hexdigest()
                    expected_id = hashlib.sha256(
                        b"p2p_counterparty\0gpt-6-luna\0high\0" + canonical
                    ).hexdigest()
                    self.assertEqual(expected_id, envelope["request_id"])
                    self.assertEqual(body_hash, envelope["body_sha256"])
                    self.assertEqual(canonical, base64.b64decode(envelope["request_body_b64"], validate=True))
                    self.assertEqual("claude-sonnet-5", envelope["request_model"])
                    self._write_fake_success(envelope)
                    # The real worker consumes the inbox file after writing
                    # its durable outbox response.
                    files[0].unlink()
                    return
                time.sleep(0.005)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        with self._post(body) as response:
            first = json.loads(response.read())
        thread.join(timeout=2)
        with self._post(body) as response:
            cached = json.loads(response.read())
        stop.set()
        self.assertEqual(first, cached)
        self.assertEqual("gpt-6-luna", first["model"])
        self.assertEqual("Synthetic counterpart reply.", first["content"][0]["text"])
        self.assertEqual(1, len(worker_calls))
        self.assertEqual([], list(inbox.glob("*.json")))

    def test_concurrent_identical_posts_share_one_pending_request(self):
        body = _body()
        inbox = Path(self.temp) / "spool" / "inbox"
        worker_calls = []
        results = []
        failures = []
        start = threading.Barrier(3)

        def poster():
            try:
                start.wait(timeout=2)
                with self._post(body) as response:
                    results.append(json.loads(response.read()))
            except Exception as exc:  # surfaced in the assertion below
                failures.append(type(exc).__name__)

        def worker():
            while not list(inbox.glob("*.json")):
                time.sleep(0.002)
            time.sleep(0.05)  # let the duplicate POST join the pending turn
            envelope = json.loads(next(inbox.glob("*.json")).read_text(encoding="utf-8"))
            worker_calls.append(envelope["request_id"])
            self._write_fake_success(envelope)

        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        posters = [threading.Thread(target=poster, daemon=True) for _ in range(2)]
        for thread in posters:
            thread.start()
        start.wait(timeout=2)
        for thread in posters:
            thread.join(timeout=3)
        worker_thread.join(timeout=2)

        self.assertEqual([], failures)
        self.assertEqual(2, len(results))
        self.assertEqual(results[0], results[1])
        self.assertEqual(1, len(worker_calls))
        self.assertEqual(1, len(list(inbox.glob("*.json"))))

    def test_cancelled_claim_prevents_late_model_submission(self):
        bridge = SimulatorBridge(
            Path(self.temp) / "cancel-spool", "cm_patient", port=0,
            request_timeout=1, poll_interval=0.01,
        )
        bridge.start()
        self.addCleanup(bridge.shutdown)
        request = Request(
            f"http://127.0.0.1:{bridge.port}/v1/messages",
            data=json.dumps(_body()).encode(), headers={"x-api-key": LOCAL_KEY}, method="POST",
        )
        with self.assertRaises(HTTPError) as raised:
            urlopen(request, timeout=2)
        self.assertEqual(400, raised.exception.code)
        spool = Path(self.temp) / "cancel-spool"
        claim = next((spool / "claims").glob("*.json"))
        receipt = json.loads(claim.read_text(encoding="utf-8"))
        self.assertEqual("cancelled", receipt["status"])
        error = json.loads(raised.exception.read())
        self.assertIn("cancelled_before_submission", error["error"]["message"])

    def test_submitted_claim_timeout_is_unknown_and_never_cancelled(self):
        bridge = SimulatorBridge(
            Path(self.temp) / "submitted-spool", "p2p_counterparty", port=0,
            request_timeout=1, poll_interval=0.01,
        )
        bridge.start()
        self.addCleanup(bridge.shutdown)
        spool = Path(self.temp) / "submitted-spool"
        stop = threading.Event()

        def worker_claims_once():
            while not stop.is_set():
                files = list((spool / "inbox").glob("*.json"))
                if files:
                    envelope = json.loads(files[0].read_text(encoding="utf-8"))
                    _exclusive_json(spool / "claims" / f"{envelope['request_id']}.json", {
                        "schema_version": 1, "request_id": envelope["request_id"],
                        "status": "submitted", "body_sha256": envelope["body_sha256"],
                    })
                    return
                time.sleep(0.002)

        worker = threading.Thread(target=worker_claims_once, daemon=True)
        worker.start()
        request = Request(
            f"http://127.0.0.1:{bridge.port}/v1/messages",
            data=json.dumps(_body()).encode(), headers={"x-api-key": LOCAL_KEY}, method="POST",
        )
        with self.assertRaises(HTTPError) as raised:
            urlopen(request, timeout=2)
        worker.join(timeout=1)
        stop.set()
        self.assertEqual(400, raised.exception.code)
        claim = next((spool / "claims").glob("*.json"))
        self.assertEqual("submitted", json.loads(claim.read_text(encoding="utf-8"))["status"])
        self.assertIn("submitted_outcome_unknown", json.loads(raised.exception.read())["error"]["message"])
        self.assertEqual([], list((spool / "outbox").glob("*.json")))

    def test_publication_is_complete_before_target_becomes_visible(self):
        from unittest.mock import patch
        from health_harness_codex import simulator_bridge as module
        target=Path(self.temp)/'published.json';fsync_reached=threading.Event();release=threading.Event()
        original_fsync=module.os.fsync;errors=[]
        def held_fsync(fd):
            original_fsync(fd);fsync_reached.set()
            if not release.wait(2):raise TimeoutError('test did not release publisher')
        def publish():
            try:module._exclusive_json(target,{'complete':'x'*20000})
            except Exception as exc:errors.append(exc)
        with patch.object(module.os,'fsync',held_fsync):
            writer=threading.Thread(target=publish)
            writer.start()
            try:
                self.assertTrue(fsync_reached.wait(2))
                self.assertFalse(target.exists(),'request must not be visible before publication finishes')
            finally:release.set();writer.join(timeout=2)
        self.assertEqual([],errors)
        self.assertEqual({'complete':'x'*20000},json.loads(target.read_text(encoding='utf-8')))
        self.assertEqual([],list(Path(self.temp).glob('.publish-*.tmp')))

    def test_concurrent_publication_keeps_one_complete_winner_without_overwriting(self):
        from health_harness_codex import simulator_bridge as module
        target=Path(self.temp)/'arbitration.json';barrier=threading.Barrier(2);outcomes=[]
        def publish(value):
            barrier.wait();outcomes.append(module._exclusive_json(target,{'winner':value}))
        writers=[threading.Thread(target=publish,args=(i,)) for i in range(2)]
        for writer in writers:writer.start()
        for writer in writers:writer.join(timeout=2)
        self.assertEqual([False,True],sorted(outcomes))
        before=target.read_bytes()
        self.assertFalse(module._exclusive_json(target,{'winner':'late-overwrite'}))
        self.assertEqual(before,target.read_bytes())
        self.assertEqual([],list(Path(self.temp).glob('.publish-*.tmp')))

    def test_partial_claim_publication_is_waited_for_and_never_cancelled(self):
        from unittest.mock import patch
        from health_harness_codex import simulator_bridge as module
        bridge=SimulatorBridge(Path(self.temp)/'partial-spool','p2p_counterparty',port=0,request_timeout=1,poll_interval=.01)
        claim=bridge.spool_root/'claims'/'request.json';claim.write_text('{',encoding='utf-8')
        seen=threading.Event();original=module._read_json
        def observed(*args,**kwargs):
            try:return original(*args,**kwargs)
            except (module._IncompleteMarker,module.SimulatorBridgeError):
                seen.set();raise
        def publish():
            if seen.wait(2):claim.write_text(json.dumps({'request_id':'request','body_sha256':'digest','status':'submitted'}),encoding='utf-8')
        writer=threading.Thread(target=publish);writer.start()
        try:
            with patch.object(module,'_read_json',side_effect=observed):
                with self.assertRaises(module.SimulatorBridgeError) as caught:
                    bridge._wait_for_response('request','digest',bridge.spool_root/'outbox'/'request.json',claim,bridge.spool_root/'receipts'/'request.json')
            self.assertEqual('submitted_outcome_unknown',caught.exception.code)
            self.assertEqual('submitted',json.loads(claim.read_text(encoding='utf-8'))['status'])
        finally:seen.set();writer.join(timeout=2)

    def test_wrong_local_api_token_is_rejected_without_spooling(self):
        with self.assertRaises(HTTPError) as raised:
            self._post(_body(), api_key="wrong-local-token")
        self.assertEqual(401, raised.exception.code)
        self.assertEqual([], list((Path(self.temp) / "spool" / "inbox").glob("*.json")))

    def test_auth_rejection_consumes_body_before_next_keepalive_request(self):
        import http.client
        client = http.client.HTTPConnection("127.0.0.1", self.bridge.port, timeout=3)
        self.addCleanup(client.close)
        client.request("POST", "/v1/messages", json.dumps(_body()), {"x-api-key": "wrong-local-token"})
        response = client.getresponse()
        self.assertEqual(401, response.status)
        response.read()
        client.request("GET", "/health")
        health = client.getresponse()
        self.assertEqual(200, health.status)
        health.read()
        self.assertEqual([], list((Path(self.temp) / "spool" / "inbox").glob("*.json")))


if __name__ == "__main__":
    unittest.main()
