"""Private spool worker that supplies a host model as a χ-Bench simulator.

This adapter is experimental: it substitutes Codex or subscription Claude CLI
for the benchmark's pinned API simulator. It receives only the simulator's own
Anthropic-compatible request, calls the selected model boundary with no tools, and returns a
text-only message envelope. It does not read task fixtures or actor workspaces.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Callable

from .codex_provider import CodexSessionModel
from .models import ModelReply
from .providers import ProviderError


BACKEND_MODEL = "gpt-6-luna"
BACKEND_EFFORT = "high"
# The official simulator disables thinking; lower efforts approximate that more closely.
SIMULATOR_EFFORTS = ("none", "minimal", "low", "medium", "high")
APPROVED_INSTRUCTION_SOURCE = Path("C:/Users/prath/.codex/AGENTS.md")
APPROVED_INSTRUCTION_SHA256 = "1c683adadd4bffe13c4ff0700dc824fd3f3f35c024ffc3b6c68959f887318f96"
SIMULATOR_KINDS = {"cm_patient", "p2p_counterparty"}
SIMULATOR_OUTPUT_ADVISORY = {"cm_patient": 1024, "p2p_counterparty": 512}
MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_INPUT_CHARS = 180_000
MAX_OUTPUT_BYTES = 16_384
MAX_MESSAGES = 256
MAX_TEXT_BLOCKS = 128
MAX_MODEL_NAME_CHARS = 128
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_EXCEPTION_TYPE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
_SAFE_FAILURE_CATEGORIES = {
    f"{method}:{status}:{info}"
    for method in ("turn_completed", "turn_failed", "turn_interrupted", "error")
    for status in ("failed", "interrupted", "inProgress", "completed", "unknown")
    for info in (
        "contextWindowExceeded", "sessionBudgetExceeded", "usageLimitExceeded",
        "rateLimitExceeded", "flexUnavailable", "serverOverloaded", "cyberPolicy",
        "misalignmentPolicyViolation", "tooManyDenials", "internalServerError",
        "unauthorized", "badRequest", "threadRollbackFailed", "sandboxError",
        "responseStreamDisconnected", "responseTooManyFailedAttempts",
        "httpConnectionFailed", "responseStreamConnectionFailed",
        "activeTurnNotSteerable", "other",
    )
} | {
    f"{method}:{status}"
    for method in ("turn_completed", "turn_failed", "turn_interrupted", "error")
    for status in ("failed", "interrupted", "inProgress", "completed", "unknown")
}
_ALLOWED_ERROR_CODES = {
    "call_budget_exhausted",
    "cancelled_before_submission",
    "codex_error",
    "codex_timeout",
    "invalid_request",
    "model_output_invalid",
    "model_usage_unavailable",
    "request_too_large",
    "simulator_kind_mismatch",
    "submitted_outcome_unknown",
    "unsupported_request",
    "world_char_budget_exhausted",
    "world_deadline_exceeded",
}
_EVENT_STATUSES = {"submitted", "completed", "cached_response", "cancelled_before_submission"}


class SimulatorWorkerError(RuntimeError):
    """A safe, body-free host simulator worker error."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _ensure_private_run_path(spool_root: Path) -> Path:
    configured_runs_root = Path(__file__).resolve().parents[1] / "runs"
    if configured_runs_root.is_symlink():
        raise SimulatorWorkerError("ignored local runs directory may not be a symlink")
    runs_root = configured_runs_root
    try:
        runs_root = runs_root.resolve(strict=True)
    except OSError:
        raise SimulatorWorkerError("ignored local runs directory is unavailable") from None
    if not spool_root.is_absolute():
        raise SimulatorWorkerError("simulator spool path must be absolute")

    # Check every existing component from the ignored run root down so an
    # attacker cannot redirect a later write through a symlinked directory.
    try:
        candidate = spool_root.absolute()
        if not candidate.is_relative_to(runs_root):
            raise SimulatorWorkerError("simulator spool must be inside ignored local run data")
        relative = candidate.relative_to(runs_root)
        current = runs_root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise SimulatorWorkerError("simulator spool directories may not be symlinks")
        candidate.mkdir(parents=True, exist_ok=True)
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(runs_root):
            raise SimulatorWorkerError("simulator spool escaped ignored local run data")
    except SimulatorWorkerError:
        raise
    except OSError:
        raise SimulatorWorkerError("simulator spool directory could not be created") from None
    return resolved


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    """Write one JSON record without replacing an existing receipt."""
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    payload = _canonical_json(value) + b"\n"
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists() or path.is_symlink():
            temporary.unlink(missing_ok=True)
            raise SimulatorWorkerError("simulator receipt already exists")
        temporary.replace(path)
    except SimulatorWorkerError:
        raise
    except OSError:
        temporary.unlink(missing_ok=True)
        raise SimulatorWorkerError("simulator receipt could not be saved") from None


def _exclusive_json(path: Path, value: dict[str, Any]) -> None:
    """Create a single-winner arbitration marker with O_EXCL semantics."""
    payload = _canonical_json(value) + b"\n"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SimulatorWorkerError("request claim already exists") from None
    except OSError:
        raise SimulatorWorkerError("request claim could not be created") from None
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        # The claim file remains as an indeterminate, non-replayable marker.
        raise SimulatorWorkerError("request claim write failed") from None


def _read_json(path: Path, limit: int) -> dict[str, Any]:
    if path.is_symlink():
        raise SimulatorWorkerError("simulator spool symlinks are not allowed")
    try:
        raw = path.read_bytes()
    except OSError:
        raise SimulatorWorkerError("simulator request could not be read") from None
    if len(raw) > limit:
        raise SimulatorWorkerError("request_too_large")
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise SimulatorWorkerError("invalid_request") from None
    if not isinstance(value, dict):
        raise SimulatorWorkerError("invalid_request")
    return value


def _text_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, list) or len(value) > MAX_TEXT_BLOCKS:
        raise SimulatorWorkerError("unsupported_request")
    pieces: list[str] = []
    for block in value:
        if not isinstance(block, dict) or block.get("type") != "text" or not isinstance(block.get("text"), str):
            raise SimulatorWorkerError("unsupported_request")
        pieces.append(block["text"])
    return "".join(pieces)


def _validate_and_convert_request(body: Any, simulator_kind: str) -> tuple[list[dict[str, Any]], int, str, int]:
    if not isinstance(body, dict):
        raise SimulatorWorkerError("invalid_request")
    if body.get("stream", False) is not False:
        raise SimulatorWorkerError("unsupported_request")
    if body.get("tools") not in (None, []):
        raise SimulatorWorkerError("unsupported_request")
    if body.get("tool_choice") not in (None, "none"):
        raise SimulatorWorkerError("unsupported_request")
    thinking = body.get("thinking")
    if thinking not in (None, {"type": "disabled"}):
        raise SimulatorWorkerError("unsupported_request")
    for parameter in ("temperature", "top_p", "top_k"):
        if body.get(parameter) is not None:
            raise SimulatorWorkerError("unsupported_request")

    request_model = body.get("model")
    if (not isinstance(request_model, str) or not request_model.strip()
            or len(request_model) > MAX_MODEL_NAME_CHARS):
        raise SimulatorWorkerError("invalid_request")
    max_tokens = body.get("max_tokens")
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens < 1:
        raise SimulatorWorkerError("invalid_request")
    if max_tokens > SIMULATOR_OUTPUT_ADVISORY[simulator_kind]:
        raise SimulatorWorkerError("unsupported_request")

    stop_sequences = body.get("stop_sequences", [])
    if stop_sequences not in (None, []):
        raise SimulatorWorkerError("unsupported_request")

    messages = body.get("messages")
    if not isinstance(messages, list) or not 1 <= len(messages) <= MAX_MESSAGES:
        raise SimulatorWorkerError("invalid_request")
    converted: list[dict[str, Any]] = []
    input_chars = 0
    system = body.get("system")
    if system is not None:
        system_text = _text_content(system)
        input_chars += len(system_text)
        converted.append({"role": "system", "content": system_text})
    for message in messages:
        if not isinstance(message, dict) or message.get("role") not in {"user", "assistant"}:
            raise SimulatorWorkerError("unsupported_request")
        content = _text_content(message.get("content"))
        input_chars += len(content)
        converted.append({"role": message["role"], "content": content})
    if input_chars > MAX_INPUT_CHARS:
        raise SimulatorWorkerError("request_too_large")
    return converted, max_tokens, request_model, input_chars


@dataclass(frozen=True, slots=True)
class SimulatorWorkerSummary:
    submitted_calls: int
    completed_calls: int
    failed_calls: int
    unknown_calls: int
    simulator_kind: str
    backend_model: str
    backend_effort: str
    max_calls: int
    max_total_chars_per_world: int
    max_world_deadline_seconds: float
    total_input_chars: int
    elapsed_seconds: float
    pending_inbox_requests: int
    submitted_without_response: int
    outbox_successes: int
    outbox_errors: int
    cancelled_requests: int
    unresolved_requests: int
    settled: bool


class SimulatorWorker:
    """Poll one ignored, per-world spool and make at most one model call per ID.

    A submitted marker is durable before inference starts. If a process restarts
    and finds a marker without a matching outbox response, it records an unknown
    result and never reissues the model request.
    """

    def __init__(self, spool_root: str | os.PathLike[str], simulator_kind: str,
                 codex_executable: str | os.PathLike[str], *, max_calls: int = 0,
                 max_total_chars_per_world: int = 0,
                 max_world_deadline_seconds: float = 0,
                 request_timeout: float = 180, poll_interval: float = 0.1,
                 model_factory: Callable[..., Any] | None = None,
                 allowed_instruction_sources: dict[str, str] | None = None,
                 backend_effort: str = BACKEND_EFFORT,
                 backend: str = "codex", backend_model: str | None = None):
        if backend not in {"codex", "claude-cli"}:
            raise ValueError("unsupported simulator backend")
        self.backend = backend
        self.backend_model = BACKEND_MODEL
        if backend == "claude-cli":
            from .claude_cli_patient import ClaudeCliPatientModel
            self.backend_model = backend_model or "claude-sonnet-5"
            backend_effort = "disabled"
            model_factory = model_factory or ClaudeCliPatientModel
        if backend == "codex" and backend_effort not in SIMULATOR_EFFORTS:
            raise ValueError('backend_effort must be one of ' + ', '.join(SIMULATOR_EFFORTS))
        self.backend_effort = backend_effort
        if simulator_kind not in SIMULATOR_KINDS:
            raise ValueError("simulator_kind must be cm_patient or p2p_counterparty")
        if isinstance(max_calls, bool) or not isinstance(max_calls, int) or max_calls < 0:
            raise ValueError("max_calls must be a nonnegative integer; zero disables the quota")
        if (isinstance(max_total_chars_per_world, bool) or not isinstance(max_total_chars_per_world, int)
                or max_total_chars_per_world < 0):
            raise ValueError("max_total_chars_per_world must be nonnegative; zero disables the quota")
        if (isinstance(max_world_deadline_seconds, bool)
                or not isinstance(max_world_deadline_seconds, (int, float))
                or not (max_world_deadline_seconds == 0 or 1 <= max_world_deadline_seconds <= 7200)):
            raise ValueError("max_world_deadline_seconds must be zero (disabled) or between 1 and 7200 seconds")
        if (isinstance(request_timeout, bool) or not isinstance(request_timeout, (int, float))
                or not 1 <= request_timeout <= 1800):
            raise ValueError("request_timeout must be between 1 and 1800 seconds")
        if (isinstance(poll_interval, bool) or not isinstance(poll_interval, (int, float))
                or not 0.01 <= poll_interval <= 5):
            raise ValueError("poll_interval must be between 0.01 and 5 seconds")
        executable = Path(codex_executable)
        if not executable.is_absolute():
            raise ValueError("Codex executable must be an explicit absolute path")
        self.spool_root = _ensure_private_run_path(Path(spool_root))
        self.kind = simulator_kind
        self.executable = str(executable)
        self.max_calls = max_calls
        self.max_total_chars_per_world = max_total_chars_per_world
        self.max_world_deadline_seconds = float(max_world_deadline_seconds)
        self.request_timeout = float(request_timeout)
        self.poll_interval = float(poll_interval)
        self.claude_provenance = None
        if backend == "claude-cli":
            from .claude_cli_patient import provenance
            self.claude_provenance = provenance(self.executable, self.backend_model)
        self.model_factory = model_factory or CodexSessionModel
        self.allowed_instruction_sources = dict(allowed_instruction_sources or {})
        if backend == "codex":
            self._validate_instruction_sources(self.allowed_instruction_sources)
        self._started_monotonic = time.monotonic()
        self.directories = {
            name: self.spool_root / name
            for name in ("inbox", "claims", "submitted", "outbox", "receipts")
        }
        for directory in self.directories.values():
            if directory.is_symlink():
                raise SimulatorWorkerError("simulator spool directories may not be symlinks")
            directory.mkdir(exist_ok=True)
            if directory.resolve(strict=True).parent != self.spool_root:
                raise SimulatorWorkerError("simulator spool directory escaped its per-world root")
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._owner_file = None
        self._owns_owner_lock = False
        self._submitted_calls = self._count_submitted()
        self._total_input_chars = self._count_submitted_input_chars()
        self._completed_calls = 0
        self._failed_calls = 0
        self._unknown_calls = 0
        self._farewell_deadline: float | None = None

    @staticmethod
    def _validate_instruction_sources(sources: dict[str, str]) -> None:
        """Fail before any durable request claim unless the reviewed source is pinned."""
        if len(sources) != 1:
            raise SimulatorWorkerError("simulator worker requires the reviewed Codex instruction source")
        source, digest = next(iter(sources.items()))
        if not isinstance(source, str) or not isinstance(digest, str):
            raise SimulatorWorkerError("approved Codex instruction pin is invalid")
        approved = APPROVED_INSTRUCTION_SOURCE
        candidate = Path(source)
        if not candidate.is_absolute() or candidate.is_symlink():
            raise SimulatorWorkerError("approved Codex instruction source is invalid")
        try:
            canonical = candidate.resolve(strict=True)
            if os.path.normcase(str(canonical)) != os.path.normcase(str(approved.resolve(strict=True))):
                raise SimulatorWorkerError("simulator worker received an unapproved Codex instruction path")
            if digest != APPROVED_INSTRUCTION_SHA256 or not _HEX64.fullmatch(digest):
                raise SimulatorWorkerError("simulator worker received an unapproved Codex instruction hash")
            actual = hashlib.sha256(canonical.read_bytes()).hexdigest()
        except SimulatorWorkerError:
            raise
        except OSError:
            raise SimulatorWorkerError("approved Codex instruction source is unavailable") from None
        if actual != APPROVED_INSTRUCTION_SHA256:
            raise SimulatorWorkerError("approved Codex instruction source changed after review")

    def _count_submitted(self) -> int:
        total = 0
        for path in self.directories["claims"].glob("*.json"):
            if path.is_symlink() or not _HEX64.fullmatch(path.stem):
                continue
            try:
                state = _read_json(path, 16_384)
            except SimulatorWorkerError:
                total += 1  # A malformed claim is indeterminate, never replay it.
                continue
            if state.get("status") == "submitted":
                total += 1
        return total

    def _count_submitted_input_chars(self) -> int:
        total = 0
        for path in self.directories["claims"].glob("*.json"):
            if path.is_symlink() or not _HEX64.fullmatch(path.stem):
                continue
            try:
                marker = _read_json(path, 16_384)
            except SimulatorWorkerError:
                continue
            if marker.get("status") != "submitted":
                continue
            value = marker.get("input_chars")
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                total += value
        return total

    def summary(self) -> SimulatorWorkerSummary:
        residual = self._residual_counts()
        return SimulatorWorkerSummary(
            submitted_calls=self._submitted_calls,
            completed_calls=self._completed_calls,
            failed_calls=self._failed_calls,
            unknown_calls=self._unknown_calls,
            simulator_kind=self.kind,
            backend_model=self.backend_model,
            backend_effort=self.backend_effort,
            max_calls=self.max_calls,
            max_total_chars_per_world=self.max_total_chars_per_world,
            max_world_deadline_seconds=self.max_world_deadline_seconds,
            total_input_chars=self._total_input_chars,
            elapsed_seconds=round(time.monotonic() - self._started_monotonic, 3),
            pending_inbox_requests=residual["pending_inbox_requests"],
            submitted_without_response=residual["submitted_without_response"],
            outbox_successes=residual["outbox_successes"],
            outbox_errors=residual["outbox_errors"],
            cancelled_requests=residual["cancelled_requests"],
            unresolved_requests=residual["unresolved_requests"],
            settled=residual["unresolved_requests"] == 0,
        )

    def start(self) -> None:
        if self._thread is not None:
            raise SimulatorWorkerError("simulator worker is already started")
        self._acquire_owner_lock()
        self._owns_owner_lock = True
        self._stop.clear()
        self._started_monotonic = time.monotonic()
        self._thread = threading.Thread(target=self.serve, name=f"simulator-worker-{self.kind}", daemon=True)
        try:
            self._thread.start()
        except Exception:
            self._thread = None
            self._owns_owner_lock = False
            self._release_owner_lock()
            raise

    def stop(self, timeout: float | None = None) -> SimulatorWorkerSummary:
        self._stop.set()
        if self._thread is not None:
            wait_budget = min(timeout or self.request_timeout + 5,
                              self.request_timeout + 5,
                              self.max_world_deadline_seconds + 5)
            self._thread.join(timeout=wait_budget)
            if self._thread.is_alive():
                raise SimulatorWorkerError("simulator worker did not stop before its deadline")
            self._thread = None
        acquired_here = not self._owns_owner_lock
        if acquired_here:
            self._acquire_owner_lock()
        try:
            self._drain_pending_inbox()
            self._recover_submitted_without_response()
        finally:
            self._owns_owner_lock = False
            self._release_owner_lock()
        return self.summary()

    def serve(self) -> None:
        acquired_here = self._owner_file is None
        if acquired_here:
            self._acquire_owner_lock()
            self._owns_owner_lock = True
        try:
            self._recover_submitted_without_response()
            while not self._stop.is_set():
                did_work = self.run_once()
                if not did_work:
                    self._stop.wait(self.poll_interval)
        finally:
            if acquired_here:
                self._owns_owner_lock = False
                self._release_owner_lock()

    def run_once(self) -> bool:
        """Process the lexicographically first pending request; return if found."""
        acquired_here = not self._owns_owner_lock
        if acquired_here:
            self._acquire_owner_lock()
        try:
            with self._lock:
                inbox = self.directories["inbox"]
                pending = sorted(inbox.glob("*.json"), key=lambda path: path.name)
                if not pending:
                    return False
                request_path = pending[0]
                if request_path.is_symlink() or not _HEX64.fullmatch(request_path.stem):
                    self._write_error_for_invalid_path(request_path)
                    return True
                self._process_request(request_path)
                return True
        finally:
            if acquired_here:
                self._release_owner_lock()

    def _acquire_owner_lock(self) -> None:
        if self._owner_file is not None:
            raise SimulatorWorkerError("simulator spool lock is already held by this worker")
        path = self.spool_root / "owner.lock"
        if path.is_symlink():
            raise SimulatorWorkerError("simulator spool owner lock may not be a symlink")
        try:
            owner_file = path.open("a+b")
            owner_file.seek(0, os.SEEK_END)
            if owner_file.tell() == 0:
                owner_file.write(b"\0")
                owner_file.flush()
            owner_file.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(owner_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(owner_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._owner_file = owner_file
        except (BlockingIOError, PermissionError, OSError) as exc:
            if 'owner_file' in locals():
                owner_file.close()
            if isinstance(exc, OSError) and exc.errno not in (None, errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                raise SimulatorWorkerError("simulator spool owner lock could not be acquired") from None
            raise SimulatorWorkerError("simulator spool is already owned by another worker") from None

    def _release_owner_lock(self) -> None:
        owner_file = self._owner_file
        if owner_file is None:
            return
        try:
            if os.name == "nt":
                import msvcrt
                owner_file.seek(0)
                msvcrt.locking(owner_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(owner_file.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            owner_file.close()
            self._owner_file = None

    def _process_request(self, request_path: Path) -> None:
        request_id = request_path.stem
        outbox = self.directories["outbox"] / f"{request_id}.json"
        claim = self.directories["claims"] / f"{request_id}.json"
        submitted = self.directories["submitted"] / f"{request_id}.json"
        receipt = self.directories["receipts"] / f"{request_id}.json"
        if any(path.is_symlink() for path in (outbox, claim, submitted, receipt)):
            self._failed_calls += 1
            self._append_event(request_id, None, "invalid_request")
            request_path.unlink(missing_ok=True)
            return
        if outbox.exists():
            self._append_event(request_id, None, "cached_response")
            request_path.unlink(missing_ok=True)
            return
        if claim.exists():
            self._handle_existing_claim(request_id, claim, outbox, receipt, request_path)
            return
        if submitted.exists():
            self._write_unknown_if_missing(request_id, submitted, outbox, receipt, "submitted_outcome_unknown")
            request_path.unlink(missing_ok=True)
            return

        try:
            envelope = _read_json(request_path, MAX_REQUEST_BYTES * 2)
            body, body_bytes = self._decode_envelope(request_id, envelope)
            body_digest = hashlib.sha256(body_bytes).hexdigest()
            kind = envelope.get("simulator_kind")
            if kind != self.kind:
                raise SimulatorWorkerError("simulator_kind_mismatch")
            if not _HEX64.fullmatch(str(envelope.get("body_sha256", ""))) or envelope.get("body_sha256") != body_digest:
                raise SimulatorWorkerError("invalid_request")
            model_messages, max_tokens, request_model, input_chars = _validate_and_convert_request(body, self.kind)
        except SimulatorWorkerError as exc:
            code = _normalize_error_code(str(exc))
            self._write_error(request_id, outbox, receipt, code, body_sha256=self._safe_hash(envelope if "envelope" in locals() else {}))
            self._failed_calls += 1
            self._append_event(request_id, self._safe_hash(envelope if "envelope" in locals() else {}), code)
            request_path.unlink(missing_ok=True)
            return

        if self.max_calls and self._submitted_calls >= self.max_calls:
            self._write_error(request_id, outbox, receipt, "call_budget_exhausted", body_sha256=body_digest)
            self._failed_calls += 1
            self._append_event(request_id, body_digest, "call_budget_exhausted")
            request_path.unlink(missing_ok=True)
            return
        elapsed_world = time.monotonic() - self._started_monotonic
        if self.max_world_deadline_seconds and elapsed_world >= self.max_world_deadline_seconds:
            self._write_error(request_id, outbox, receipt, "world_deadline_exceeded", body_sha256=body_digest)
            self._failed_calls += 1
            self._append_event(request_id, body_digest, "world_deadline_exceeded")
            request_path.unlink(missing_ok=True)
            return
        if self.max_total_chars_per_world and self._total_input_chars + input_chars > self.max_total_chars_per_world:
            self._write_error(request_id, outbox, receipt, "world_char_budget_exhausted", body_sha256=body_digest)
            self._failed_calls += 1
            self._append_event(request_id, body_digest, "world_char_budget_exhausted")
            request_path.unlink(missing_ok=True)
            return
        effective_timeout = self.request_timeout
        if self.max_world_deadline_seconds:
            effective_timeout = min(effective_timeout, self.max_world_deadline_seconds - elapsed_world)
        if self._farewell_deadline is not None:
            effective_timeout = min(effective_timeout, self._farewell_deadline - time.monotonic())
        if effective_timeout < 1:
            self._write_error(request_id, outbox, receipt, "world_deadline_exceeded", body_sha256=body_digest)
            self._failed_calls += 1
            self._append_event(request_id, body_digest, "world_deadline_exceeded")
            request_path.unlink(missing_ok=True)
            return

        submitted_at = _now_utc()
        marker = {
            "schema_version": 1,
            "request_id": request_id,
            "body_sha256": body_digest,
            "simulator_kind": self.kind,
            "backend_model": self.backend_model,
            "backend_effort": self.backend_effort,
            "input_chars": input_chars,
            "status": "submitted",
            "submitted_at": submitted_at,
        }
        try:
            # The bridge competes for this one atomic claim when its HTTP wait
            # expires. Exactly one side wins: submitted means one Codex call;
            # cancelled means no model call may start.
            _exclusive_json(claim, {"schema_version": 1, "request_id": request_id,
                                    "status": "submitted", "body_sha256": body_digest,
                                    "input_chars": input_chars, "claimed_at": submitted_at})
        except SimulatorWorkerError:
            self._handle_existing_claim(request_id, claim, outbox, receipt, request_path)
            return
        self._submitted_calls += 1
        self._total_input_chars += input_chars
        try:
            _atomic_json(submitted, marker)
        except SimulatorWorkerError:
            self._write_unknown_if_missing(request_id, claim, outbox, receipt, "submitted_outcome_unknown")
            request_path.unlink(missing_ok=True)
            return
        started = time.monotonic()
        self._append_event(request_id, body_digest, "submitted")
        try:
            if self.claude_provenance is not None:
                from .claude_cli_patient import provenance
                if provenance(self.executable, self.backend_model) != self.claude_provenance:
                    raise SimulatorWorkerError("unsupported_request")
            model = self.model_factory(
                self.executable,
                model=self.backend_model,
                reasoning_effort=self.backend_effort,
                timeout=effective_timeout,
                runtime_dir=str(self.spool_root),
                allowed_instruction_sources=self.allowed_instruction_sources,
            )
            reply = model.complete(model_messages, [], max_output_tokens=max_tokens)
            if not isinstance(reply, ModelReply):
                raise SimulatorWorkerError("model_output_invalid")
            if reply.tool_calls:
                raise SimulatorWorkerError("unsupported_request")
            if not isinstance(reply.content, str) or not reply.content:
                raise SimulatorWorkerError("model_output_invalid")
            response_text = reply.content
            output_adaptation = None
            usage = _actual_usage(reply.usage)
            wire_usage = usage
            # A marker-only stop contains no patient utterance. The runtime
            # strips the marker and rejects an empty ConversationMessage,
            # leaving an apparently active session. Preserve the actual stop
            # with one separate, budgeted model request for a minimal farewell.
            # Do not manufacture dialogue, consent or refusal in ordinary code.
            if (self.kind == "cm_patient" and "###STOP###" in response_text
                    and not response_text.replace("###STOP###", "").strip()):
                if self._farewell_deadline is not None:
                    raise SimulatorWorkerError("model_output_invalid")
                _exclusive_json(self.spool_root / f"stop-{request_id}.private.json", {
                    'request_id':request_id,'raw_text':reply.content,'usage':usage,
                    'purpose':'retain the completed marker-only generation before bounded correction'})
                self._farewell_deadline = started + effective_timeout
                try:
                    correction_id, correction = self._stop_farewell(body, reply.content)
                finally:
                    self._farewell_deadline = None
                response_text = correction['content'][0]['text']
                if "###STOP###" not in response_text or not response_text.replace("###STOP###", "").strip():
                    raise SimulatorWorkerError("model_output_invalid")
                wire_usage = {key: usage[key] + correction['usage'][key] for key in ('input_tokens','output_tokens')}
                output_adaptation = {"kind": "budgeted_stop_farewell", "raw_text": reply.content,
                                     "farewell_request_id": correction_id, "wire_text": response_text}
            response_bytes = response_text.encode("utf-8")
            if len(response_bytes) > MAX_OUTPUT_BYTES:
                raise SimulatorWorkerError("model_output_invalid")
            response = _anthropic_response(request_id, response_text, wire_usage, self.backend_model)
            _exclusive_json(outbox, {
                "schema_version": 1,
                "request_id": request_id,
                "status": "ok",
                "anthropic_response": response,
            })
            _atomic_json(receipt, {
                "schema_version": 1,
                "request_id": request_id,
                "body_sha256": body_digest,
                "simulator_kind": self.kind,
                "upstream_requested_model": request_model,
                "backend_model": self.backend_model,
                "backend_effort": self.backend_effort,
                "status": "completed",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "requested_max_output_tokens_advisory": max_tokens,
                **({"output_adaptation": output_adaptation} if output_adaptation else {}),
            })
            self._completed_calls += 1
            self._append_event(request_id, body_digest, "completed", usage)
        except Exception as exc:
            code = _error_code(exc)
            # Once `complete` is entered, a transport/model exception can hide
            # whether the inference ran. Never resubmit it automatically.
            if not isinstance(exc, SimulatorWorkerError):
                code = "submitted_outcome_unknown"
            diagnostics = _safe_exception_diagnostics(exc)
            self._write_error(request_id, outbox, receipt, code, body_sha256=body_digest,
                              elapsed_ms=round((time.monotonic() - started) * 1000),
                              submitted=True, **diagnostics)
            if code == "submitted_outcome_unknown":
                self._unknown_calls += 1
            else:
                self._failed_calls += 1
            self._append_event(request_id, body_digest, code, **diagnostics)
        finally:
            request_path.unlink(missing_ok=True)

    def _stop_farewell(self, body: dict[str, Any], raw_text: str) -> tuple[str, dict[str, Any]]:
        """One separately journaled generation, never another patient turn.

        Reuse the normal budget, claim, crash-fencing and usage paths. The
        correction remains inside the original HTTP/world deadline. A second
        marker-only answer fails closed; it cannot recursively ask again.
        """
        corrected = json.loads(json.dumps(body))
        corrected['messages'].extend([
            {'role':'assistant','content':raw_text},
            {'role':'user','content':
                'Protocol formatting correction only: you already chose to end this conversation. '
                'Preserve that decision. Return one brief farewell followed by ###STOP###. '
                'Include nonempty words outside the stop marker. Do not reopen the conversation, '
                'add medical facts or preferences, or state consent or refusal to care management. '
                'Do not explain these formatting instructions.'},
        ])
        canonical = _canonical_json(corrected)
        digest = hashlib.sha256(canonical).hexdigest()
        request_id = hashlib.sha256(self.kind.encode() + b'\0' + self.backend_model.encode()
                                   + b'\0' + self.backend_effort.encode() + b'\0' + canonical).hexdigest()
        path = self.directories['inbox'] / f'{request_id}.json'
        if not path.exists():
            _exclusive_json(path, {'schema_version':1,'request_id':request_id,'created_at':_now_utc(),
                'simulator_kind':self.kind,'request_model':corrected['model'],
                'backend_model':self.backend_model,'backend_effort':self.backend_effort,
                'request_body_b64':base64.b64encode(canonical).decode('ascii'),'body_sha256':digest})
        self._process_request(path)
        result = _read_json(self.directories['outbox'] / f'{request_id}.json', MAX_OUTPUT_BYTES * 2)
        if result.get('status') != 'ok':
            raise SimulatorWorkerError(_normalize_error_code(result.get('error_code','model_output_invalid')))
        return request_id, result['anthropic_response']

    def _decode_envelope(self, request_id: str, envelope: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
        required = {"schema_version", "request_id", "created_at", "simulator_kind", "request_model",
                    "backend_model", "backend_effort", "request_body_b64", "body_sha256"}
        if set(envelope) != required or envelope.get("schema_version") != 1 or envelope.get("request_id") != request_id:
            raise SimulatorWorkerError("invalid_request")
        if envelope.get("backend_model") != self.backend_model or envelope.get("backend_effort") != self.backend_effort:
            raise SimulatorWorkerError("unsupported_request")
        envelope_kind = envelope.get("simulator_kind")
        if envelope_kind not in SIMULATOR_KINDS or envelope_kind != self.kind:
            raise SimulatorWorkerError("simulator_kind_mismatch")
        created_at = envelope.get("created_at")
        if not isinstance(created_at, str) or len(created_at) > 64:
            raise SimulatorWorkerError("invalid_request")
        encoded = envelope.get("request_body_b64")
        if not isinstance(encoded, str) or len(encoded) > (MAX_REQUEST_BYTES * 4 // 3) + 8:
            raise SimulatorWorkerError("request_too_large")
        try:
            raw = base64.b64decode(encoded, validate=True)
            if len(raw) > MAX_REQUEST_BYTES:
                raise SimulatorWorkerError("request_too_large")
            body = json.loads(raw)
        except SimulatorWorkerError:
            raise
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            raise SimulatorWorkerError("invalid_request") from None
        if not isinstance(body, dict):
            raise SimulatorWorkerError("invalid_request")
        canonical = _canonical_json(body)
        computed_hash = hashlib.sha256(canonical).hexdigest()
        expected_id = hashlib.sha256(
            envelope_kind.encode("utf-8") + b"\0" + self.backend_model.encode("utf-8") + b"\0"
            + self.backend_effort.encode("utf-8") + b"\0" + canonical
        ).hexdigest()
        if envelope.get("body_sha256") != computed_hash or request_id != expected_id:
            raise SimulatorWorkerError("invalid_request")
        if envelope.get("request_model") != body.get("model"):
            raise SimulatorWorkerError("invalid_request")
        return body, canonical

    def _write_error(self, request_id: str, outbox: Path, receipt: Path, code: str,
                     body_sha256: str | None = None, elapsed_ms: int | None = None,
                     submitted: bool = False, exception_type: str | None = None,
                     failure_category: str | None = None,
                     proposal_dispatch_safe: bool | None = None) -> None:
        code = _normalize_error_code(code)
        try:
            _exclusive_json(outbox, {"schema_version": 1, "request_id": request_id,
                                     "status": "error", "error_code": code})
        except SimulatorWorkerError:
            # A prior response is immutable; still attempt the body-free receipt.
            pass
        record = {"schema_version": 1, "request_id": request_id, "simulator_kind": self.kind,
                  "backend_model": self.backend_model, "backend_effort": self.backend_effort,
                  "status": code}
        if body_sha256 and _HEX64.fullmatch(body_sha256):
            record["body_sha256"] = body_sha256
        if elapsed_ms is not None:
            record["elapsed_ms"] = elapsed_ms
        if submitted:
            record["submitted"] = True
        if exception_type:
            record["exception_type"] = exception_type
        if failure_category:
            record["failure_category"] = failure_category
        if proposal_dispatch_safe is not None:
            record["proposal_dispatch_safe"] = proposal_dispatch_safe
        if not receipt.exists():
            try:
                _atomic_json(receipt, record)
            except SimulatorWorkerError:
                pass

    def _write_unknown_if_missing(self, request_id: str, submitted: Path, outbox: Path,
                                  receipt: Path, code: str) -> None:
        if outbox.exists():
            return
        body_hash = None
        try:
            marker = _read_json(submitted, 16_384)
            value = marker.get("body_sha256")
            body_hash = value if isinstance(value, str) and _HEX64.fullmatch(value) else None
        except SimulatorWorkerError:
            pass
        self._write_error(request_id, outbox, receipt, code, body_sha256=body_hash, submitted=True)
        self._unknown_calls += 1
        self._append_event(request_id, body_hash, code)

    def _handle_existing_claim(self, request_id: str, claim: Path, outbox: Path,
                               receipt: Path, request_path: Path) -> None:
        try:
            state = _read_json(claim, 16_384)
        except SimulatorWorkerError:
            state = {}
        if state.get("status") == "cancelled":
            self._write_error(request_id, outbox, receipt, "cancelled_before_submission",
                              body_sha256=state.get("body_sha256"))
            self._failed_calls += 1
            self._append_event(request_id, state.get("body_sha256"), "cancelled_before_submission")
        else:
            self._write_unknown_if_missing(request_id, claim, outbox, receipt, "submitted_outcome_unknown")
        request_path.unlink(missing_ok=True)

    def _recover_submitted_without_response(self) -> None:
        for marker in sorted(self.directories["claims"].glob("*.json"), key=lambda path: path.name):
            if marker.is_symlink() or not _HEX64.fullmatch(marker.stem):
                continue
            request_id = marker.stem
            outbox = self.directories["outbox"] / f"{request_id}.json"
            receipt = self.directories["receipts"] / f"{request_id}.json"
            if not outbox.exists():
                try:
                    state = _read_json(marker, 16_384)
                except SimulatorWorkerError:
                    state = {}
                if state.get("status") == "cancelled":
                    self._write_error(request_id, outbox, receipt, "cancelled_before_submission",
                                      body_sha256=state.get("body_sha256"))
                    self._failed_calls += 1
                    self._append_event(request_id, state.get("body_sha256"), "cancelled_before_submission")
                else:
                    self._write_unknown_if_missing(request_id, marker, outbox, receipt,
                                                   "submitted_outcome_unknown")

    def _drain_pending_inbox(self) -> None:
        """Cancel work that never won the submitted claim before shutdown."""
        inbox = self.directories["inbox"]
        for request_path in sorted(inbox.glob("*.json"), key=lambda path: path.name):
            request_id = request_path.stem
            if request_path.is_symlink() or not _HEX64.fullmatch(request_id):
                continue
            outbox = self.directories["outbox"] / f"{request_id}.json"
            claim = self.directories["claims"] / f"{request_id}.json"
            receipt = self.directories["receipts"] / f"{request_id}.json"
            if outbox.exists():
                request_path.unlink(missing_ok=True)
                continue
            if claim.exists():
                self._handle_existing_claim(request_id, claim, outbox, receipt, request_path)
                continue
            try:
                _exclusive_json(claim, {"schema_version": 1, "request_id": request_id,
                                        "status": "cancelled", "simulator_kind": self.kind,
                                        "claimed_at": _now_utc()})
            except SimulatorWorkerError:
                self._handle_existing_claim(request_id, claim, outbox, receipt, request_path)
                continue
            self._write_error(request_id, outbox, receipt, "cancelled_before_submission")
            self._failed_calls += 1
            self._append_event(request_id, None, "cancelled_before_submission")
            request_path.unlink(missing_ok=True)

    def _residual_counts(self) -> dict[str, int]:
        inbox = self.directories["inbox"]
        claims = self.directories["claims"]
        outbox = self.directories["outbox"]
        pending_ids = {path.stem for path in inbox.glob("*.json")}
        submitted_without_response: set[str] = set()
        cancelled_ids: set[str] = set()
        for path in claims.glob("*.json"):
            if path.is_symlink() or not _HEX64.fullmatch(path.stem):
                continue
            try:
                state = _read_json(path, 16_384)
            except SimulatorWorkerError:
                submitted_without_response.add(path.stem)
                continue
            if state.get("status") == "submitted" and not (outbox / f"{path.stem}.json").exists():
                submitted_without_response.add(path.stem)
            elif state.get("status") == "cancelled":
                cancelled_ids.add(path.stem)

        success_ids: set[str] = set()
        error_ids: set[str] = set()
        unknown_ids: set[str] = set()
        for path in outbox.glob("*.json"):
            if path.is_symlink() or not _HEX64.fullmatch(path.stem):
                continue
            try:
                result = _read_json(path, MAX_OUTPUT_BYTES * 2)
            except SimulatorWorkerError:
                error_ids.add(path.stem)
                unknown_ids.add(path.stem)
                continue
            if result.get("status") == "ok":
                success_ids.add(path.stem)
            else:
                error_ids.add(path.stem)
                if result.get("error_code") == "submitted_outcome_unknown":
                    unknown_ids.add(path.stem)
        unresolved = pending_ids | submitted_without_response | unknown_ids
        return {
            "pending_inbox_requests": len(pending_ids),
            "submitted_without_response": len(submitted_without_response),
            "outbox_successes": len(success_ids),
            "outbox_errors": len(error_ids),
            "cancelled_requests": len(cancelled_ids),
            "unresolved_requests": len(unresolved),
        }

    def _write_error_for_invalid_path(self, path: Path) -> None:
        # No response can be safely correlated to a malformed or symlinked path.
        # Keep a counter-only event and leave the untrusted object untouched.
        self._failed_calls += 1
        self._append_event("invalid-request-id", None, "invalid_request")

    @staticmethod
    def _safe_hash(value: Any) -> str | None:
        if isinstance(value, dict):
            digest = value.get("body_sha256")
            return digest if isinstance(digest, str) and _HEX64.fullmatch(digest) else None
        return None

    def _append_event(self, request_id: str, body_sha256: str | None, status: str,
                      usage: dict[str, int] | None = None, exception_type: str | None = None,
                      failure_category: str | None = None,
                      proposal_dispatch_safe: bool | None = None) -> None:
        record: dict[str, Any] = {"time": _now_utc(), "request_id": request_id,
                                  "simulator_kind": self.kind,
                                  "status": status if status in _EVENT_STATUSES else _normalize_error_code(status)}
        if body_sha256 and _HEX64.fullmatch(body_sha256):
            record["body_sha256"] = body_sha256
        if usage:
            record.update({key: usage[key] for key in ("input_tokens", "output_tokens")})
        if exception_type:
            record["exception_type"] = exception_type
        if failure_category:
            record["failure_category"] = failure_category
        if proposal_dispatch_safe is not None:
            record["proposal_dispatch_safe"] = proposal_dispatch_safe
        path = self.spool_root / "worker.events.jsonl"
        if path.is_symlink():
            raise SimulatorWorkerError("simulator event log symlink is not allowed")
        try:
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            # Observability failure must not trigger a second inference.
            return


def _actual_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        raise SimulatorWorkerError("model_usage_unavailable")
    required = ("input_tokens", "output_tokens")
    if any(isinstance(value.get(name), bool) or not isinstance(value.get(name), int) or value[name] < 0
           for name in required):
        raise SimulatorWorkerError("model_usage_unavailable")
    return {name: value[name] for name in required}


def _safe_exception_diagnostics(exc: Exception) -> dict[str, Any]:
    """Extract bounded, allowlisted metadata without retaining exception prose."""
    raw_type = type(exc).__name__
    exception_type = raw_type if isinstance(raw_type, str) and _SAFE_EXCEPTION_TYPE.fullmatch(raw_type) else "OtherException"
    category = getattr(exc, "failure_category", None)
    failure_category = category if isinstance(category, str) and category in _SAFE_FAILURE_CATEGORIES else None
    dispatch_safe = getattr(exc, "proposal_dispatch_safe", None)
    if not isinstance(dispatch_safe, bool):
        dispatch_safe = None
    return {
        "exception_type": exception_type,
        "failure_category": failure_category,
        "proposal_dispatch_safe": dispatch_safe,
    }


def _anthropic_response(request_id: str, text: str, usage: dict[str, int], model: str = BACKEND_MODEL) -> dict[str, Any]:
    if len(text.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise SimulatorWorkerError("model_output_invalid")
    return {
        "id": "msg_" + request_id[:24],
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]},
    }


def _normalize_error_code(value: str) -> str:
    return value if value in _ALLOWED_ERROR_CODES else "codex_error"


def _error_code(exc: Exception) -> str:
    if isinstance(exc, SimulatorWorkerError):
        return _normalize_error_code(str(exc))
    if isinstance(exc, (TimeoutError,)):
        return "codex_timeout"
    if isinstance(exc, ProviderError):
        return "codex_timeout" if "timeout" in str(exc).casefold() else "codex_error"
    return "codex_error"


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
