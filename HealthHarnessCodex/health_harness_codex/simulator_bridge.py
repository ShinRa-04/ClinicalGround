"""Loopback Anthropic Messages bridge backed by a per-world local spool.

The benchmark container calls this through ``ANTHROPIC_BASE_URL``. A host-side
worker consumes opaque request bodies and writes Anthropic-shaped responses.
The bridge never reads provider credentials, calls a remote service, or logs
request/response contents.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import threading
import tempfile
import time
from typing import Any


SIMULATOR_KINDS = {"cm_patient", "p2p_counterparty"}
LOCAL_API_KEY = "codex-local-bridge"
MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 256 * 1024
DEFAULT_REQUEST_TIMEOUT = 180.0
POLL_INTERVAL = 0.05
_ERROR_CODES = {
    "cancelled_before_submission", "invalid_request", "model_output_invalid",
    "model_usage_unavailable", "request_too_large", "simulator_kind_mismatch",
    "submitted_outcome_unknown", "unsupported_request", "codex_error", "codex_timeout",
    "call_budget_exhausted", "world_char_budget_exhausted", "world_deadline_exceeded",
}


class SimulatorBridgeError(RuntimeError):
    """Safe bridge error containing no request or response content."""

    def __init__(self, code: str, status: int = int(HTTPStatus.BAD_REQUEST)):
        if code not in _ERROR_CODES:
            code = "invalid_request"
        super().__init__(code)
        self.code = code
        self.status = status


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _ensure_spool(spool_root: str | os.PathLike[str]) -> Path:
    root = Path(spool_root)
    if not root.is_absolute():
        raise ValueError("simulator spool root must be absolute")
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("simulator spool root must be a regular directory")
    resolved = root.resolve(strict=True)
    for name in ("inbox", "submitted", "outbox", "claims", "receipts"):
        child = resolved / name
        child.mkdir(exist_ok=True)
        if child.is_symlink() or not child.is_dir() or not child.resolve(strict=True).is_relative_to(resolved):
            raise ValueError("simulator spool subdirectories must remain inside the spool root")
    return resolved


class _IncompleteMarker(Exception):
    """An exclusive marker may be visible before its writer finishes JSON."""


def _read_json(path: Path, max_bytes: int, *, allow_incomplete=False) -> dict[str, Any]:
    if path.is_symlink():
        raise SimulatorBridgeError("invalid_request")
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            with os.fdopen(fd, "rb", closefd=False) as stream:
                raw = stream.read(max_bytes + 1)
        finally:
            os.close(fd)
        if len(raw) > max_bytes:
            raise SimulatorBridgeError("request_too_large")
        value = json.loads(raw)
    except SimulatorBridgeError:
        raise
    except (UnicodeDecodeError,json.JSONDecodeError):
        if allow_incomplete:raise _IncompleteMarker() from None
        raise SimulatorBridgeError("invalid_request") from None
    except OSError:
        raise SimulatorBridgeError("invalid_request") from None
    if not isinstance(value, dict):
        raise SimulatorBridgeError("invalid_request")
    return value


def _exclusive_json(path: Path, value: dict[str, Any]) -> bool:
    """Publish complete JSON atomically without replacing an existing winner.

    A private sibling is written/fsynced first; linking it into place is the
    single-winner operation. Consumers never see a partially written inbox.
    Do not replace this with os.replace: overwriting a claim permits replay.
    """
    if path.is_symlink():
        raise SimulatorBridgeError("invalid_request")
    packed = _canonical_json(value) + b"\n"
    temporary=None
    try:
        fd,temporary_name=tempfile.mkstemp(prefix='.publish-',suffix='.tmp',dir=path.parent)
        temporary=Path(temporary_name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(packed)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary,path)
        except FileExistsError:
            return False
    except OSError:
        raise SimulatorBridgeError("invalid_request") from None
    finally:
        if temporary is not None:
            try:temporary.unlink(missing_ok=True)
            except OSError:pass  # Never remove a published arbitration marker.
    return True


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class SimulatorBridge:
    """Expose a bounded local Anthropic-compatible endpoint for one world."""

    def __init__(self, spool_root: str | os.PathLike[str], simulator_kind: str, *,
                 host: str = "127.0.0.1", port: int = 9765,
                 backend_model: str = "gpt-6-luna", backend_effort: str = "high",
                 local_api_key: str = LOCAL_API_KEY, request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
                 poll_interval: float = POLL_INTERVAL):
        if simulator_kind not in SIMULATOR_KINDS:
            raise ValueError("simulator_kind must be cm_patient or p2p_counterparty")
        if host not in {"127.0.0.1", "::1"}:
            raise ValueError("simulator bridge must bind to loopback only")
        if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65535:
            raise ValueError("bridge port must be between 0 and 65535")
        if not isinstance(backend_model, str) or not backend_model.strip():
            raise ValueError("backend model must be explicit")
        if backend_effort not in {"none", "minimal", "low", "medium", "high", "xhigh", "max", "disabled"}:
            raise ValueError("unsupported Codex reasoning effort")
        if local_api_key != LOCAL_API_KEY:
            raise ValueError("bridge accepts only its local dummy API token")
        if (isinstance(request_timeout, bool) or not isinstance(request_timeout, (int, float))
                or not 1 <= request_timeout <= 1800):
            raise ValueError("request timeout must be between 1 and 1800 seconds")
        if (isinstance(poll_interval, bool) or not isinstance(poll_interval, (int, float))
                or not 0.01 <= poll_interval <= 1):
            raise ValueError("poll interval must be between 0.01 and 1 second")
        self.spool_root = _ensure_spool(spool_root)
        self.simulator_kind = simulator_kind
        self.host = host
        self.port = port
        self.backend_model = backend_model
        self.backend_effort = backend_effort
        self.local_api_key = local_api_key
        self.request_timeout = float(request_timeout)
        self.poll_interval = float(poll_interval)
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._server is not None:
            raise RuntimeError("simulator bridge is already started")
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: Any) -> None:
                # Never write request paths, headers, prompts, or response text.
                return

            def do_GET(self) -> None:
                if self.path != "/health":
                    self._send_error(SimulatorBridgeError("invalid_request"))
                    return
                body = _canonical_json({"status": "ready", "simulator_kind": bridge.simulator_kind})
                self.send_response(int(HTTPStatus.OK))
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:
                try:
                    length = int(self.headers.get("Content-Length", "-1"))
                    if length < 0 or length > MAX_REQUEST_BYTES:
                        self.close_connection = True
                        raise SimulatorBridgeError("request_too_large")
                    # Consume the bounded body even when rejecting credentials.
                    # Otherwise a keep-alive handler parses that JSON as the
                    # next HTTP request and may reset the 401 response socket.
                    self.connection.settimeout(5)
                    raw = self.rfile.read(length)
                    if len(raw) != length:
                        raise SimulatorBridgeError("invalid_request")
                    if self.path != "/v1/messages":
                        raise SimulatorBridgeError("invalid_request")
                    if self.headers.get("x-api-key") != bridge.local_api_key:
                        raise SimulatorBridgeError("invalid_request", int(HTTPStatus.UNAUTHORIZED))
                    body = json.loads(raw)
                    if not isinstance(body, dict):
                        raise SimulatorBridgeError("invalid_request")
                    result = bridge.handle_request(body)
                except SimulatorBridgeError as exc:
                    self._send_error(exc)
                    return
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError, TimeoutError):
                    self.close_connection = True
                    self._send_error(SimulatorBridgeError("invalid_request"))
                    return
                packed = _canonical_json(result)
                self.send_response(int(HTTPStatus.OK))
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(packed)))
                self.end_headers()
                self.wfile.write(packed)

            def _send_error(self, exc: SimulatorBridgeError) -> None:
                body = _canonical_json({"type": "error", "error": {
                    "type": "api_error", "message": f"Local simulator bridge: {exc.code}",
                }})
                self.send_response(exc.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        class Server(ThreadingHTTPServer):
            daemon_threads = True
            allow_reuse_address = True

        try:
            server = Server((self.host, self.port), Handler)
        except OSError:
            raise RuntimeError("simulator bridge could not bind its loopback port") from None
        self._server = server
        self.port = int(server.server_address[1])
        self._thread = threading.Thread(target=server.serve_forever, name="codex-simulator-bridge", daemon=True)
        self._thread.start()

    def serve_forever(self) -> None:
        self.start()
        try:
            while self._thread is not None and self._thread.is_alive():
                self._thread.join()
        except KeyboardInterrupt:
            self.shutdown()
            raise

    def shutdown(self) -> None:
        server = self._server
        if server is None:
            return
        server.shutdown()
        server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._thread = None
        self._server = None

    def handle_request(self, body: dict[str, Any]) -> dict[str, Any]:
        canonical_body = _canonical_json(body)
        if len(canonical_body) > MAX_REQUEST_BYTES:
            raise SimulatorBridgeError("request_too_large")
        request_model = body.get("model")
        if not isinstance(request_model, str) or not request_model.strip() or len(request_model) > 128:
            raise SimulatorBridgeError("invalid_request")
        body_digest = hashlib.sha256(canonical_body).hexdigest()
        request_id = hashlib.sha256(
            self.simulator_kind.encode("utf-8") + b"\0" + self.backend_model.encode("utf-8")
            + b"\0" + self.backend_effort.encode("utf-8") + b"\0" + canonical_body
        ).hexdigest()
        inbox = self.spool_root / "inbox" / f"{request_id}.json"
        outbox = self.spool_root / "outbox" / f"{request_id}.json"
        claim = self.spool_root / "claims" / f"{request_id}.json"
        receipt = self.spool_root / "receipts" / f"{request_id}.json"
        envelope = {
            "schema_version": 1,
            "request_id": request_id,
            "created_at": _now_utc(),
            "simulator_kind": self.simulator_kind,
            "request_model": request_model,
            "backend_model": self.backend_model,
            "backend_effort": self.backend_effort,
            "request_body_b64": base64.b64encode(canonical_body).decode("ascii"),
            "body_sha256": body_digest,
        }
        # Check durable state before recreating an inbox file for an already
        # settled request. The worker removes consumed entries, while outbox
        # and claims remain as the deduplication record.
        if any(path.exists() for path in (outbox, claim, receipt)):
            created = False
        else:
            try:
                created = _exclusive_json(inbox, envelope)
            except SimulatorBridgeError:
                raise
        if not created:
            # SDK retries and concurrent identical requests must join the
            # original turn, never trigger a second inference. Verify the
            # immutable envelope before sharing its result. The worker removes
            # consumed inbox files, so a retry may instead join a durable claim
            # or cached outbox record from the original request.
            if inbox.exists():
                existing = _read_json(inbox, MAX_REQUEST_BYTES + 4096)
                expected = {
                    "schema_version": 1,
                    "request_id": request_id,
                    "simulator_kind": self.simulator_kind,
                    "request_model": request_model,
                    "backend_model": self.backend_model,
                    "backend_effort": self.backend_effort,
                    "request_body_b64": envelope["request_body_b64"],
                    "body_sha256": body_digest,
                }
                if any(existing.get(key) != value for key, value in expected.items()):
                    raise SimulatorBridgeError("invalid_request")
            elif not any(path.exists() for path in (outbox, claim, receipt)):
                # The competing writer may still be creating the inbox entry.
                # A missing entry with no durable state is ambiguous; never
                # manufacture a second turn under the same request ID.
                raise SimulatorBridgeError("submitted_outcome_unknown")
        return self._wait_for_response(request_id, body_digest, outbox, claim, receipt)

    def _wait_for_response(self, request_id: str, body_digest: str, outbox: Path,
                           claim: Path, receipt: Path) -> dict[str, Any]:
        deadline = time.monotonic() + self.request_timeout
        def marker(path,max_bytes):
            try:return _read_json(path,max_bytes,allow_incomplete=True)
            except _IncompleteMarker:
                # Never create a cancellation or a second submission while a
                # durable claim/output exists but its publication is incomplete.
                if time.monotonic()>=deadline:raise SimulatorBridgeError('submitted_outcome_unknown') from None
                return None
        while True:
            if outbox.exists():
                record = marker(outbox, MAX_RESPONSE_BYTES)
                if record is None:
                    time.sleep(self.poll_interval);continue
                if record.get("request_id") != request_id:
                    raise SimulatorBridgeError("invalid_request")
                if record.get("status") == "ok" and isinstance(record.get("anthropic_response"), dict):
                    return record["anthropic_response"]
                if record.get("status") == "error":
                    code = record.get("error_code")
                    raise SimulatorBridgeError(code if isinstance(code, str) else "codex_error")
                raise SimulatorBridgeError("submitted_outcome_unknown")
            if claim.exists():
                claim_marker = marker(claim, 16_384)
                if claim_marker is None:
                    time.sleep(self.poll_interval);continue
                if claim_marker.get("request_id") != request_id or claim_marker.get("body_sha256") != body_digest:
                    raise SimulatorBridgeError("invalid_request")
                if claim_marker.get("status") == "cancelled":
                    raise SimulatorBridgeError("cancelled_before_submission")
                if claim_marker.get("status") != "submitted":
                    raise SimulatorBridgeError("submitted_outcome_unknown")
            if receipt.exists():
                receipt_marker = marker(receipt, 16_384)
                if receipt_marker is None:
                    time.sleep(self.poll_interval);continue
                if receipt_marker.get("request_id") != request_id:
                    raise SimulatorBridgeError("invalid_request")
                status = receipt_marker.get("status")
                if status in {"cancelled_before_submission", "submitted_outcome_unknown"}:
                    raise SimulatorBridgeError(status)
            if time.monotonic() >= deadline:
                cancelled = _exclusive_json(claim, {
                    "schema_version": 1,
                    "request_id": request_id,
                    "status": "cancelled",
                    "body_sha256": body_digest,
                    "claimed_at": _now_utc(),
                })
                if cancelled:
                    _exclusive_json(outbox, {"schema_version": 1, "request_id": request_id,
                                             "status": "error", "error_code": "cancelled_before_submission"})
                    _exclusive_json(receipt, {"schema_version": 1, "request_id": request_id,
                                              "simulator_kind": self.simulator_kind,
                                              "backend_model": self.backend_model,
                                              "backend_effort": self.backend_effort,
                                              "status": "cancelled_before_submission",
                                              "body_sha256": body_digest})
                    raise SimulatorBridgeError("cancelled_before_submission")
                # The worker won the O_EXCL race and has submitted inference.
                # Do not issue or enqueue another request; surface unknown.
                raise SimulatorBridgeError("submitted_outcome_unknown")
            time.sleep(self.poll_interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local Anthropic-compatible Codex simulator bridge")
    parser.add_argument("--spool-root", required=True)
    parser.add_argument("--simulator-kind", choices=sorted(SIMULATOR_KINDS), required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9765)
    parser.add_argument("--backend-model", default="gpt-6-luna")
    parser.add_argument("--backend-effort", default="high")
    parser.add_argument("--local-api-key", default=LOCAL_API_KEY)
    parser.add_argument("--request-timeout", type=float, default=DEFAULT_REQUEST_TIMEOUT)
    parser.add_argument("--poll-interval", type=float, default=POLL_INTERVAL)
    args = parser.parse_args(argv)
    bridge = SimulatorBridge(
        args.spool_root, args.simulator_kind, host=args.host, port=args.port,
        backend_model=args.backend_model, backend_effort=args.backend_effort,
        local_api_key=args.local_api_key, request_timeout=args.request_timeout,
        poll_interval=args.poll_interval,
    )
    try:
        bridge.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        bridge.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
