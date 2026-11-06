"""Experimental, budget-fenced OpenRouter Batch transport for Claude Opus 4.7.

This is an alternate judge transport, not the pinned official judge protocol.
It deliberately implements only the Anthropic Messages request shape and never
falls back to a synchronous endpoint.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Any, Callable


API_ROOT = "https://openrouter.ai/api/v1"
MODEL = "anthropic/claude-opus-4.7"
BATCH_MODEL = "anthropic/claude-opus-4.7:batch"
ENDPOINT = "/v1/messages"
INPUT_USD_PER_MILLION = 2.50
INPUT_CACHE_WRITE_USD_PER_MILLION = INPUT_USD_PER_MILLION * 1.25
OUTPUT_USD_PER_MILLION = 12.50
DEFAULT_MAX_BUDGET_USD = 0.50
MAX_REQUEST_BYTES = 2_000_000
MAX_TOOL_SCHEMA_BYTES = 128_000
MAX_TOOL_RESULT_BYTES = 64_000
MAX_WORKSPACE_FILE_BYTES = 2_000_000
MAX_TURNS = 8
MAX_TOKENS = 4096
MAX_HTTP_TIMEOUT_SECONDS = 40
INPUT_PROTOCOL_MARGIN_TOKENS = 64
RUNS_ROOT = Path(__file__).resolve().parents[1] / "runs"
KEY_FILE = Path(__file__).resolve().parents[2] / "Runner" / ".env"
LEDGER_NAME = "openrouter_batch_ledger.json"
_BATCH_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,160}$")


class OpenRouterBatchError(RuntimeError):
    """Safe-to-display failure; messages intentionally omit provider bodies."""


class OpenRouterBatchPending(OpenRouterBatchError):
    def __init__(self, batch_id: str, status: str, session_id: str | None = None):
        self.batch_id = batch_id
        self.status = status
        self.session_id = session_id
        super().__init__(f"batch {batch_id} is still {status}; resume it with a separate poll call")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _safe_run_dir(run_dir: Path, *, create: bool = False) -> Path:
    path = Path(run_dir)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    try:
        resolved = path.resolve(strict=True)
        root = RUNS_ROOT.resolve(strict=True)
    except OSError:
        raise OpenRouterBatchError("run directory does not exist") from None
    if not resolved.is_relative_to(root) or resolved == root:
        raise OpenRouterBatchError("run directory must be a child of ignored HealthHarnessCodex/runs")
    if path.is_symlink():
        raise OpenRouterBatchError("run directory cannot be a symbolic link")
    return resolved


def _read_api_key() -> str:
    """Read only OPENROUTER_API_KEY from the exact local Runner/.env file."""
    try:
        if KEY_FILE.is_symlink() or not KEY_FILE.is_file():
            raise OpenRouterBatchError("OpenRouter key file is unavailable at the configured local Runner/.env path")
        for line in KEY_FILE.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == "OPENROUTER_API_KEY":
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                if value and "\r" not in value and "\n" not in value:
                    return value
                break
    except UnicodeError:
        pass
    except OSError:
        pass
    raise OpenRouterBatchError("OPENROUTER_API_KEY is missing or invalid in the configured local Runner/.env file")


def _canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        raise OpenRouterBatchError("request is not valid JSON data") from None


def _number(value: Any, *, default: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        return default
    return float(value)


def _safe_provider_error(code: int, raw: bytes, api_key: str) -> dict[str, Any]:
    """Keep a short diagnostic in ignored local state; never return it to CLI output."""
    result: dict[str, Any] = {"http_status": code}
    try:
        value = json.loads(raw[:65536].decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, UnicodeError):
        return result
    err = value.get("error") if isinstance(value, dict) else None
    if isinstance(err, dict):
        for key in ("code", "type"):
            item = err.get(key)
            if isinstance(item, (str, int)) and len(str(item)) <= 120:
                result[key] = item
        message = err.get("message")
        if isinstance(message, str):
            message = message[:1200]
            if api_key:
                message = message.replace(api_key, "[REDACTED]")
            message = re.sub(r"(?i)bearer\s+\S+", "Bearer [REDACTED]", message)
            message = re.sub(r"(?i)(api[_-]?key\s*[=:]\s*)[^\s,;]+", r"\1[REDACTED]", message)
            result["message"] = message
    return result


def validate_request(body: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise OpenRouterBatchError("request body must be an object")
    allowed = {"model", "messages", "max_tokens", "system", "tools"}
    extra = set(body) - allowed
    if extra:
        raise OpenRouterBatchError("unsupported request parameter")
    if body.get("model", MODEL) != MODEL:
        raise OpenRouterBatchError("only anthropic/claude-opus-4.7 is permitted")
    messages = body.get("messages")
    max_tokens = body.get("max_tokens")
    if (not isinstance(messages, list) or not messages or
            isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or
            not 1 <= max_tokens <= MAX_TOKENS):
        raise OpenRouterBatchError("messages and a max_tokens value from 1 to 4096 are required")
    if any(not isinstance(item, dict) or item.get("role") not in {"user", "assistant"} or
           "content" not in item for item in messages):
        raise OpenRouterBatchError("messages must use the Anthropic Messages role/content shape")
    tools = body.get("tools", [])
    if not isinstance(tools, list) or len(_canonical_json(tools)) > MAX_TOOL_SCHEMA_BYTES:
        raise OpenRouterBatchError("tool schema is invalid or too large")
    if "system" in body and not isinstance(body["system"], (str, list)):
        raise OpenRouterBatchError("system must be text or Anthropic text blocks")
    clean = dict(body)
    clean.pop("model", None)  # The batch-level model is authoritative.
    return clean


def estimate_cost(body: dict[str, Any]) -> dict[str, Any]:
    clean = validate_request(body)
    raw = _canonical_json(clean)
    if len(raw) > MAX_REQUEST_BYTES:
        raise OpenRouterBatchError("request exceeds the 2 MB safety limit")
    # UTF-8 bytes upper-bound text tokens. Add a fixed protocol margin, and
    # reserve every input token at cache-write worst-case pricing.
    input_token_reservation = len(raw) + INPUT_PROTOCOL_MARGIN_TOKENS
    output_token_reservation = clean["max_tokens"]
    input_cost = input_token_reservation * INPUT_CACHE_WRITE_USD_PER_MILLION / 1_000_000
    output_cost = output_token_reservation * OUTPUT_USD_PER_MILLION / 1_000_000
    return {
        "model": MODEL,
        "request_model": MODEL,
        "batch_variant": BATCH_MODEL,
        "endpoint": ENDPOINT,
        "request_utf8_bytes": len(raw),
        "reserved_input_tokens": input_token_reservation,
        "reserved_output_tokens": output_token_reservation,
        "input_cost_usd": round(input_cost, 12),
        "output_cost_usd": round(output_cost, 12),
        "reservation_usd": round(input_cost + output_cost, 12),
        "input_rate_usd_per_million": INPUT_USD_PER_MILLION,
        "input_reservation_rate_usd_per_million": INPUT_CACHE_WRITE_USD_PER_MILLION,
        "output_rate_usd_per_million": OUTPUT_USD_PER_MILLION,
        "cache_write_worst_case_reserved": True,
    }


class _LedgerLock:
    """Small cross-process lock, with a bounded wait and no stale-lock guessing."""
    def __init__(self, path: Path):
        self.path = path
        self.fd: int | None = None

    def __enter__(self):
        deadline = time.monotonic() + 10
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.write(self.fd, str(os.getpid()).encode("ascii"))
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise OpenRouterBatchError("budget ledger is locked; inspect and resume manually") from None
                time.sleep(0.05)
            except OSError:
                raise OpenRouterBatchError("could not lock budget ledger") from None

    def __exit__(self, exc_type, exc, tb):
        if self.fd is not None:
            os.close(self.fd)
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass


class OpenRouterBatchTransport:
    """Durable, single-batch-at-a-time transport with cumulative USD cap."""

    def __init__(self, run_dir: Path, *, max_budget_usd: float = DEFAULT_MAX_BUDGET_USD,
                 opener: Callable[..., Any] | None = None,
                 key_loader: Callable[[], str] = _read_api_key):
        if isinstance(max_budget_usd, bool) or not isinstance(max_budget_usd, (int, float)) or not (0 < max_budget_usd <= DEFAULT_MAX_BUDGET_USD):
            raise OpenRouterBatchError("maximum cumulative budget must be greater than zero and at most $0.50")
        self.run_dir = _safe_run_dir(run_dir, create=True)
        self.ledger_path = self.run_dir / LEDGER_NAME
        if self.ledger_path.is_symlink():
            raise OpenRouterBatchError("budget ledger cannot be a symbolic link")
        self.lock_path = self.run_dir / (LEDGER_NAME + ".lock")
        self.max_budget_usd = float(max_budget_usd)
        self._opener = opener or urllib.request.urlopen
        self._key_loader = key_loader

    def _load_ledger(self) -> dict[str, Any]:
        if not self.ledger_path.exists():
            return {"version": 1, "model": MODEL, "max_budget_usd": self.max_budget_usd,
                    "actual_cost_usd": 0.0, "jobs": []}
        if self.ledger_path.is_symlink():
            raise OpenRouterBatchError("budget ledger cannot be a symbolic link")
        try:
            data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise OpenRouterBatchError("budget ledger is unreadable; no request was sent") from None
        if (not isinstance(data, dict) or data.get("version") != 1 or data.get("model") != MODEL or
                not isinstance(data.get("jobs"), list) or
                not math.isclose(_number(data.get("max_budget_usd"), default=-1), self.max_budget_usd, abs_tol=1e-12)):
            raise OpenRouterBatchError("budget ledger configuration does not match; no request was sent")
        return data

    def _save_ledger(self, data: dict[str, Any]) -> None:
        tmp = self.run_dir / (LEDGER_NAME + ".tmp")
        if tmp.exists() or tmp.is_symlink():
            tmp.unlink()
        try:
            with tmp.open("xb") as f:
                f.write(_canonical_json(data))
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.ledger_path)
        except OSError:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise OpenRouterBatchError("could not durably save budget ledger; no request was sent") from None

    @staticmethod
    def _reserved(data: dict[str, Any]) -> float:
        total = 0.0
        for job in data["jobs"]:
            status = job.get("status")
            if status in {"prepared", "submitting", "unknown", "submitted", "validating", "in_progress", "finalizing", "cancelling", "failed_unknown_cost", "completed_unknown_cost", "expired", "cancelled"}:
                total += _number(job.get("reservation_usd"))
        return total

    def estimate(self, body: dict[str, Any]) -> dict[str, Any]:
        estimate = estimate_cost(body)
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            used = _number(ledger.get("actual_cost_usd")) + self._reserved(ledger)
            estimate.update({"actual_cost_to_date_usd": _number(ledger.get("actual_cost_usd")),
                             "reserved_cost_usd": self._reserved(ledger),
                             "budget_remaining_usd": max(0.0, self.max_budget_usd - used),
                             "max_budget_usd": self.max_budget_usd,
                             "would_fit": used + estimate["reservation_usd"] <= self.max_budget_usd + 1e-12})
        return estimate

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None,
                 *, timeout: float = 30) -> tuple[int, dict[str, Any]]:
        key = self._key_loader()
        data = None if body is None else _canonical_json(body)
        request = urllib.request.Request(API_ROOT + path, data=data, method=method,
                                         headers={"Authorization": f"Bearer {key}",
                                                  "Content-Type": "application/json",
                                                  "Accept": "application/json"})
        try:
            with self._opener(request, timeout=min(max(float(timeout), 1), MAX_HTTP_TIMEOUT_SECONDS)) as response:
                code = int(response.status)
                payload = response.read(8_000_000)
        except urllib.error.HTTPError as exc:
            try:
                diagnostic = _safe_provider_error(int(exc.code), exc.read(65536), key)
            except Exception:
                diagnostic = {"http_status": int(exc.code)}
            return int(exc.code), {"_http_error": diagnostic}
        except Exception as exc:
            raise OpenRouterBatchError(f"OpenRouter request outcome is unknown ({type(exc).__name__}); reservation retained") from None
        try:
            decoded = json.loads(payload.decode("utf-8")) if payload else {}
        except (UnicodeError, json.JSONDecodeError):
            raise OpenRouterBatchError("OpenRouter returned invalid JSON; request outcome is retained for manual reconciliation") from None
        if not isinstance(decoded, dict):
            raise OpenRouterBatchError("OpenRouter returned an invalid response; request outcome is retained for manual reconciliation")
        return code, decoded

    def submit(self, body: dict[str, Any], *, custom_id: str | None = None,
               session_state: dict[str, Any] | None = None) -> dict[str, Any]:
        clean = validate_request(body)
        estimate = estimate_cost(clean)
        job_id = str(uuid.uuid4())
        custom_id = custom_id or job_id
        session_snapshot = None
        if session_state is not None:
            try:
                session_snapshot = json.loads(_canonical_json(session_state).decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                raise OpenRouterBatchError("session checkpoint is invalid") from None
            session_snapshot["submission_job_id"] = job_id
            session_snapshot["phase"] = "submitting"
        payload = {"endpoint": ENDPOINT, "model": MODEL,
                   "provider": {"only": ["anthropic"], "allow_fallbacks": False},
                   "requests": [{"custom_id": custom_id, "body": clean}]}
        # Persist the complete request and reservation before any network call.
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            current = _number(ledger.get("actual_cost_usd")) + self._reserved(ledger)
            if current + estimate["reservation_usd"] > self.max_budget_usd + 1e-12:
                raise OpenRouterBatchError("cumulative $0.50 budget would be exceeded; no request was sent")
            job = {"job_id": job_id, "custom_id": custom_id, "status": "prepared",
                   "created_at": _utc_now(), "reservation_usd": estimate["reservation_usd"],
                   "estimate": estimate, "batch_id": None, "usage": None, "actual_cost_usd": None,
                   "request": payload, "result": None, "session": session_snapshot,
                   "tool_execution": {}, "tool_results": {}}
            ledger["jobs"].append(job)
            self._save_ledger(ledger)
            job["status"] = "submitting"
            job["submit_started_at"] = _utc_now()
            self._save_ledger(ledger)
        try:
            code, response = self._request("POST", "/batches", payload)
        except OpenRouterBatchError:
            # Existing 'submitting' reservation is deliberately kept unknown.
            with _LedgerLock(self.lock_path):
                ledger = self._load_ledger()
                self._find_job(ledger, job_id)["status"] = "unknown"
                self._save_ledger(ledger)
            raise
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            stored = self._find_job(ledger, job_id)
            batch_id = response.get("id")
            if code == 202 and isinstance(batch_id, str) and _BATCH_ID_RE.fullmatch(batch_id):
                returned_status = response.get("status")
                returned_model = response.get("model")
                if (returned_status not in {"validating", "in_progress", "finalizing"} or
                        (returned_model is not None and returned_model not in {MODEL, BATCH_MODEL})):
                    stored.update({"batch_id": batch_id, "status": "unknown",
                                   "submitted_at": _utc_now(), "provider": response.get("provider"),
                                   "error": "202 response had an unexpected status or model"})
                    self._save_ledger(ledger)
                    raise OpenRouterBatchError("202 response status/model was unexpected; batch ID recorded and reservation retained")
                if stored.get("session") is not None:
                    stored["session"].update({"phase": "waiting", "pending_batch": {
                        "job_id": job_id, "batch_id": batch_id, "custom_id": custom_id}})
                stored.update({"batch_id": batch_id, "status": returned_status,
                               "submitted_at": _utc_now(), "provider": response.get("provider")})
                self._save_ledger(ledger)
                return {"job_id": job_id, "custom_id": custom_id, "batch_id": batch_id,
                        "status": stored["status"], "reservation_usd": stored["reservation_usd"], "estimate": estimate}
            if 400 <= code < 500:
                stored.update({"status": "failed_no_cost", "http_status": code,
                               "error": "request rejected synchronously",
                               "error_metadata": response.get("_http_error")})
                self._save_ledger(ledger)
                raise OpenRouterBatchError(f"OpenRouter rejected batch submission with HTTP {code}; reservation released")
            stored.update({"status": "unknown", "http_status": code or None,
                           "error": "submission response did not confirm a batch ID"})
            self._save_ledger(ledger)
        raise OpenRouterBatchError("submission outcome is unknown; reservation retained and POST will not be retried")

    def save_session(self, job_id: str, session_state: dict[str, Any]) -> None:
        try:
            snapshot = json.loads(_canonical_json(session_state).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            raise OpenRouterBatchError("session checkpoint is invalid") from None
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            job = self._find_job(ledger, job_id)
            job["session"] = snapshot
            job["session_updated_at"] = _utc_now()
            self._save_ledger(ledger)

    def load_session(self, session_id: str) -> dict[str, Any]:
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            matches = [job for job in ledger["jobs"]
                       if isinstance(job.get("session"), dict) and job["session"].get("session_id") == session_id]
            if not matches:
                raise OpenRouterBatchError("session is not recorded in this run ledger")
            state = matches[-1]["session"]
            return json.loads(_canonical_json(state).decode("utf-8"))

    def job_for_session(self, session_id: str) -> dict[str, Any]:
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            matches = [job for job in ledger["jobs"]
                       if isinstance(job.get("session"), dict) and job["session"].get("session_id") == session_id]
            if not matches:
                raise OpenRouterBatchError("session is not recorded in this run ledger")
            return {key: matches[-1].get(key) for key in ("job_id", "batch_id", "status", "session")}

    def execute_tool_once(self, job_id: str, tool_id: str, action: Callable[[], str]) -> str:
        if not isinstance(tool_id, str) or not tool_id or len(tool_id) > 256:
            raise OpenRouterBatchError("workspace tool call has an invalid stable ID")
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            job = self._find_job(ledger, job_id)
            cached = job.setdefault("tool_results", {}).get(tool_id)
            if isinstance(cached, dict) and cached.get("status") == "completed":
                return str(cached.get("content", ""))
            execution = job.setdefault("tool_execution", {})
            if execution.get(tool_id) == "executing":
                raise OpenRouterBatchError("workspace tool outcome is uncertain; refusing to replay it")
            execution[tool_id] = "executing"
            self._save_ledger(ledger)
        try:
            content = action()
        except Exception as exc:
            # The durable executing marker makes a possibly partial write fail closed.
            raise OpenRouterBatchError(f"workspace tool outcome is uncertain ({type(exc).__name__}); refusing replay") from None
        if not isinstance(content, str):
            raise OpenRouterBatchError("workspace tool returned an invalid result; refusing replay")
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            job = self._find_job(ledger, job_id)
            if job.setdefault("tool_execution", {}).get(tool_id) != "executing":
                raise OpenRouterBatchError("workspace tool checkpoint changed; refusing to continue")
            job["tool_results"][tool_id] = {"status": "completed", "content": content,
                                            "completed_at": _utc_now()}
            job["tool_execution"][tool_id] = "completed"
            self._save_ledger(ledger)
        return content

    @staticmethod
    def _find_job(ledger: dict[str, Any], job_id_or_batch_id: str) -> dict[str, Any]:
        for job in ledger["jobs"]:
            if job.get("job_id") == job_id_or_batch_id or job.get("batch_id") == job_id_or_batch_id:
                return job
        raise OpenRouterBatchError("batch is not recorded in this run ledger")

    @staticmethod
    def _cost_from_usage(batch: dict[str, Any]) -> tuple[float | None, dict[str, Any] | None]:
        usage = batch.get("usage")
        if isinstance(usage, dict):
            reported = usage.get("cost")
            if isinstance(reported, (int, float)) and not isinstance(reported, bool) and math.isfinite(float(reported)) and reported >= 0:
                if usage.get("is_byok") is True:
                    details = usage.get("cost_details")
                    upstream = details.get("upstream_inference_cost") if isinstance(details, dict) else None
                    if not isinstance(upstream, (int, float)) or isinstance(upstream, bool) or not math.isfinite(float(upstream)) or upstream < 0:
                        return None, usage
                    return float(reported) + float(upstream), usage
                return float(reported), usage
        return None, usage if isinstance(usage, dict) else None

    def poll(self, batch_id: str, *, timeout: float = 30) -> dict[str, Any]:
        if not isinstance(batch_id, str) or not _BATCH_ID_RE.fullmatch(batch_id):
            raise OpenRouterBatchError("invalid batch ID")
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            job = self._find_job(ledger, batch_id)
            if not job.get("batch_id"):
                raise OpenRouterBatchError("batch has no confirmed remote ID; inspect ledger and reconcile manually")
        code, response = self._request("GET", "/batches/" + batch_id, timeout=timeout)
        if code != 200:
            raise OpenRouterBatchError(f"OpenRouter batch poll returned HTTP {code}; ledger reservation retained")
        status = response.get("status")
        if status not in {"validating", "in_progress", "finalizing", "completed", "failed", "expired", "cancelling", "cancelled"}:
            raise OpenRouterBatchError("OpenRouter returned an unknown status; ledger reservation retained")
        returned_model = response.get("model")
        if returned_model is not None and returned_model not in {MODEL, BATCH_MODEL}:
            raise OpenRouterBatchError("OpenRouter batch model does not match Claude Opus 4.7; reservation retained")
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
            job = self._find_job(ledger, batch_id)
            job["status"] = status
            job["last_polled_at"] = _utc_now()
            job["request_counts"] = response.get("request_counts") if isinstance(response.get("request_counts"), dict) else None
            job["provider"] = response.get("provider", job.get("provider"))
            job["usage"], actual_cost = response.get("usage"), None
            if status == "completed":
                actual_cost, usage = self._cost_from_usage(response)
                job["usage"] = usage
                if actual_cost is not None:
                    old = job.get("actual_cost_usd")
                    if old is None:
                        ledger["actual_cost_usd"] = round(_number(ledger.get("actual_cost_usd")) + actual_cost, 12)
                    else:
                        ledger["actual_cost_usd"] = round(_number(ledger.get("actual_cost_usd")) - _number(old) + actual_cost, 12)
                    job["actual_cost_usd"] = round(actual_cost, 12)
                    job["status"] = "completed"
                else:
                    job["status"] = "completed_unknown_cost"
            elif status in {"failed", "expired", "cancelled"}:
                # Release only if OpenRouter explicitly reports zero cost.
                actual_cost, usage = self._cost_from_usage(response)
                job["usage"] = usage
                if actual_cost == 0:
                    job["status"] = "failed_no_cost"
                elif actual_cost is not None:
                    old = job.get("actual_cost_usd")
                    ledger["actual_cost_usd"] = round(_number(ledger.get("actual_cost_usd")) - _number(old) + actual_cost, 12)
                    job.update({"actual_cost_usd": round(actual_cost, 12), "status": "failed_cost_known"})
                else:
                    job["status"] = "failed_unknown_cost"
            if status == "completed":
                job["result"] = response
            self._save_ledger(ledger)
            return {"job_id": job.get("job_id"), "custom_id": job.get("custom_id"),
                    "batch_id": batch_id, "status": status,
                    "request_counts": job.get("request_counts"), "usage": job.get("usage"),
                    "actual_cost_usd": job.get("actual_cost_usd"),
                    "reservation_usd": job.get("reservation_usd"),
                    "result": response if status == "completed" else None}

    def ledger_summary(self) -> dict[str, Any]:
        with _LedgerLock(self.lock_path):
            ledger = self._load_ledger()
        reserved = self._reserved(ledger)
        return {"model": MODEL, "max_budget_usd": self.max_budget_usd,
                "actual_cost_usd": _number(ledger.get("actual_cost_usd")),
                "reserved_cost_usd": round(reserved, 12),
                "remaining_usd": max(0.0, self.max_budget_usd - _number(ledger.get("actual_cost_usd")) - reserved),
                "jobs": [{"job_id": j.get("job_id"), "batch_id": j.get("batch_id"),
                          "status": j.get("status"), "reservation_usd": j.get("reservation_usd"),
                          "actual_cost_usd": j.get("actual_cost_usd"), "usage": j.get("usage")}
                         for j in ledger["jobs"]]}


def _resolve_workspace(cwd: Path) -> Path:
    root = Path(cwd).resolve(strict=True)
    if not root.is_dir():
        raise OpenRouterBatchError("workspace must be an existing directory")
    return root


def _confined_path(root: Path, raw: str, *, must_exist: bool = False) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise OpenRouterBatchError("workspace tool path is invalid")
    candidate = Path(raw)
    if candidate.is_absolute():
        path = candidate
    else:
        path = root / candidate
    # Refuse symlinks in every existing component, including links that resolve
    # back inside the workspace, so tool access cannot escape via later changes.
    current = root
    try:
        rel = path.relative_to(root)
    except ValueError:
        raise OpenRouterBatchError("workspace tool path escapes cwd") from None
    for part in rel.parts:
        if part in {"", ".", ".."}:
            raise OpenRouterBatchError("workspace tool path escapes cwd")
        current = current / part
        if current.is_symlink():
            raise OpenRouterBatchError("workspace tool path crosses a symbolic link")
    resolved = path.resolve(strict=must_exist)
    if not resolved.is_relative_to(root):
        raise OpenRouterBatchError("workspace tool path escapes cwd")
    return resolved


def _tool_schemas(names: set[str]) -> list[dict[str, Any]]:
    definitions = {
        "Read": {"name": "Read", "description": "Read a UTF-8 text file inside the current workspace.",
                 "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}, "offset": {"type": "integer"}, "limit": {"type": "integer"}}, "required": ["file_path"], "additionalProperties": False}},
        "Glob": {"name": "Glob", "description": "List files matching a workspace-relative glob pattern.",
                 "input_schema": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"], "additionalProperties": False}},
        "Grep": {"name": "Grep", "description": "Search UTF-8 text files by literal text inside the workspace.",
                 "input_schema": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "glob": {"type": "string"}}, "required": ["pattern"], "additionalProperties": False}},
        "Write": {"name": "Write", "description": "Create or replace a UTF-8 text file inside the workspace.",
                  "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"], "additionalProperties": False}},
        "Edit": {"name": "Edit", "description": "Replace one exact text occurrence in a UTF-8 workspace file.",
                 "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["file_path", "old_string", "new_string"], "additionalProperties": False}},
    }
    unknown = names - definitions.keys()
    if unknown:
        raise OpenRouterBatchError("allowed tool list contains unsupported tool names")
    return [definitions[k] for k in definitions if k in names]


def _execute_workspace_tool(root: Path, name: str, args: dict[str, Any]) -> str:
    if not isinstance(args, dict):
        return "Tool error: arguments must be an object"
    try:
        if name == "Glob":
            pattern = args.get("pattern")
            if not isinstance(pattern, str) or ".." in Path(pattern).parts or Path(pattern).is_absolute():
                raise OpenRouterBatchError("glob pattern must remain inside cwd")
            matches = []
            for path in root.glob(pattern):
                if path.is_symlink():
                    continue
                try:
                    resolved = _confined_path(root, path.relative_to(root).as_posix(), must_exist=True)
                except OpenRouterBatchError:
                    continue
                if resolved.is_file():
                    matches.append(resolved.relative_to(root).as_posix())
                if len(matches) >= 500:
                    break
            return "\n".join(sorted(matches))[:MAX_TOOL_RESULT_BYTES]
        if name == "Grep":
            needle, base = args.get("pattern"), args.get("path", ".")
            if not isinstance(needle, str) or not needle or len(needle) > 2000:
                raise OpenRouterBatchError("grep pattern must be non-empty text")
            target = _confined_path(root, base, must_exist=True)
            file_glob = args.get("glob", "*")
            if not isinstance(file_glob, str) or Path(file_glob).is_absolute() or ".." in Path(file_glob).parts:
                raise OpenRouterBatchError("grep glob must remain inside cwd")
            files = [target] if target.is_file() else list(target.rglob(file_glob))
            hits: list[str] = []
            scanned_bytes = 0
            for path in files[:500]:
                if path.is_symlink() or not path.is_file():
                    continue
                try:
                    path = _confined_path(root, path.relative_to(root).as_posix(), must_exist=True)
                    size = path.stat().st_size
                    if size > MAX_WORKSPACE_FILE_BYTES or scanned_bytes + size > MAX_WORKSPACE_FILE_BYTES:
                        continue
                    scanned_bytes += size
                    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                        if needle in line:
                            hits.append(f"{path.relative_to(root).as_posix()}:{line_no}:{line[:1000]}")
                            if len(hits) >= 200:
                                break
                except (OSError, UnicodeError):
                    continue
                if len(hits) >= 200:
                    break
            return "\n".join(hits)[:MAX_TOOL_RESULT_BYTES]
        raw = args.get("file_path")
        path = _confined_path(root, raw, must_exist=name in {"Read", "Edit"})
        if name == "Read":
            if not path.is_file():
                raise OpenRouterBatchError("read target is not a file")
            if path.stat().st_size > MAX_WORKSPACE_FILE_BYTES:
                raise OpenRouterBatchError("read target exceeds the workspace file-size limit")
            offset = args.get("offset", 0)
            limit = args.get("limit", 2000)
            if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0 or isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10000:
                raise OpenRouterBatchError("read offset/limit is invalid")
            return "\n".join(path.read_text(encoding="utf-8").splitlines()[offset:offset + limit])[:MAX_TOOL_RESULT_BYTES]
        if name == "Write":
            content = args.get("content")
            if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_TOOL_RESULT_BYTES:
                raise OpenRouterBatchError("write content is invalid or too large")
            relative = path.relative_to(root)
            parent = root
            for part in relative.parts[:-1]:
                parent = parent / part
                if parent.is_symlink():
                    raise OpenRouterBatchError("workspace tool path crosses a symbolic link")
                if not parent.exists():
                    parent.mkdir()
            # Revalidate after directory creation to catch linked parents.
            path = _confined_path(root, raw)
            path.write_text(content, encoding="utf-8", newline="")
            return f"Wrote {path.relative_to(root).as_posix()}"
        if name == "Edit":
            if not path.is_file():
                raise OpenRouterBatchError("edit target is not a file")
            old, new = args.get("old_string"), args.get("new_string")
            if not isinstance(old, str) or not old or not isinstance(new, str):
                raise OpenRouterBatchError("edit strings are invalid")
            content = path.read_text(encoding="utf-8")
            if content.count(old) != 1:
                raise OpenRouterBatchError("old_string must match exactly once")
            path.write_text(content.replace(old, new), encoding="utf-8", newline="")
            return f"Edited {path.relative_to(root).as_posix()}"
        raise OpenRouterBatchError("tool is not permitted")
    except OpenRouterBatchError as exc:
        return "Tool error: " + str(exc)
    except (OSError, UnicodeError, ValueError) as exc:
        return f"Tool error: {type(exc).__name__}"


class OpenRouterBatchJudgeRunner:
    """Experimental WorkspaceJudge-compatible tool runner.

    Each model turn is a separate asynchronous batch. The same official prompt
    string is sent unchanged. A pending batch is surfaced for a later poll call.
    """

    def __init__(self, run_dir: Path, *, max_budget_usd: float = DEFAULT_MAX_BUDGET_USD,
                 transport: OpenRouterBatchTransport | None = None):
        self.transport = transport or OpenRouterBatchTransport(run_dir, max_budget_usd=max_budget_usd)
        self._sessions: dict[str, dict[str, Any]] = {}

    def run_session(self, prompt: str, cwd: Path, allowed_tools: list[str],
                    add_dirs: list[Path] | None = None, timeout_seconds: float = 40) -> str:
        if not isinstance(prompt, str) or not prompt:
            raise OpenRouterBatchError("judge prompt must be non-empty text")
        root = _resolve_workspace(Path(cwd))
        for extra in add_dirs or []:
            resolved = _resolve_workspace(Path(extra))
            if not resolved.is_relative_to(root):
                raise OpenRouterBatchError("additional workspace directories must remain inside cwd")
        tools = _tool_schemas(set(allowed_tools))
        session_id = str(uuid.uuid4())
        session = {"session_id": session_id, "cwd": str(root), "allowed_tools": allowed_tools,
                   "messages": [{"role": "user", "content": prompt}], "tools": tools,
                   "turn": 0, "phase": "ready",
                   "deadline": time.monotonic() + min(max(timeout_seconds, 1), MAX_HTTP_TIMEOUT_SECONDS)}
        return self._advance(session)

    def resume_session(self, session_id: str) -> str:
        session = self.transport.load_session(session_id)
        session["deadline"] = time.monotonic() + MAX_HTTP_TIMEOUT_SECONDS
        return self._advance(session)

    def _advance(self, session: dict[str, Any]) -> str:
        root = Path(session["cwd"]).resolve(strict=True)
        while session["turn"] < MAX_TURNS:
            if time.monotonic() >= session["deadline"]:
                raise OpenRouterBatchError("judge session reached its 40-second process window")
            if session.get("phase") == "complete":
                return str(session.get("final_text", ""))
            submitted = session.get("pending_batch")
            if submitted is None:
                if session.get("submission_job_id"):
                    detail = self.transport.job_for_session(session["session_id"])
                    raise OpenRouterBatchError(
                        f"previous submission is {detail.get('status')}; refusing an automatic POST retry")
                session["turn"] += 1
                body = {"messages": session["messages"], "max_tokens": MAX_TOKENS}
                if session["tools"]:
                    body["tools"] = session["tools"]
                submitted = self.transport.submit(body, session_state=session)
                session["submission_job_id"] = submitted["job_id"]
                session["pending_batch"] = {"job_id": submitted["job_id"],
                                             "batch_id": submitted["batch_id"],
                                             "custom_id": submitted["custom_id"]}
                session["phase"] = "waiting"
            while time.monotonic() < session["deadline"]:
                polled = self.transport.poll(submitted["batch_id"], timeout=min(20, max(1, session["deadline"] - time.monotonic())))
                if polled["status"] == "completed":
                    results = polled.get("result", {}).get("results")
                    expected_custom_id = submitted.get("custom_id", submitted.get("job_id"))
                    if not isinstance(results, list) or len(results) != 1 or results[0].get("custom_id") != expected_custom_id:
                        raise OpenRouterBatchError("completed batch has no matching single request result")
                    job_id = polled.get("job_id")
                    response = results[0].get("response")
                    if not isinstance(response, dict) or response.get("status_code") != 200:
                        raise OpenRouterBatchError("judge request failed; details withheld")
                    answer = response.get("body")
                    if not isinstance(answer, dict) or not isinstance(answer.get("content"), list):
                        raise OpenRouterBatchError("Anthropic Messages response shape is invalid")
                    tool_uses = [part for part in answer["content"] if isinstance(part, dict) and part.get("type") == "tool_use"]
                    text_blocks = [part.get("text", "") for part in answer["content"] if isinstance(part, dict) and part.get("type") == "text"]
                    if not tool_uses:
                        answer_text = "\n".join(item for item in text_blocks if isinstance(item, str))
                        session.pop("pending_batch", None)
                        session.pop("submission_job_id", None)
                        session["phase"] = "complete"
                        session["final_text"] = answer_text
                        self.transport.save_session(job_id, session)
                        return answer_text
                    session["messages"].append({"role": "assistant", "content": answer["content"]})
                    tool_results = []
                    permitted = set(session["allowed_tools"])
                    for call in tool_uses:
                        name = call.get("name")
                        if name not in permitted:
                            result_text = "Tool error: tool is not permitted"
                        else:
                            result_text = self.transport.execute_tool_once(
                                job_id, call.get("id", ""),
                                lambda name=name, arguments=call.get("input"): _execute_workspace_tool(root, name, arguments))
                        tool_results.append({"type": "tool_result", "tool_use_id": call.get("id", ""),
                                             "content": result_text, "is_error": result_text.startswith("Tool error:")})
                    session["messages"].append({"role": "user", "content": tool_results})
                    session.pop("pending_batch", None)
                    session.pop("submission_job_id", None)
                    session["phase"] = "ready"
                    self.transport.save_session(job_id, session)
                    break
                if polled["status"] in {"failed", "expired", "cancelled"}:
                    raise OpenRouterBatchError(f"batch ended with status {polled['status']}; see local ledger")
                # The next status GET is a new API call. No individual request blocks >40s.
                time.sleep(min(1.0, max(0.0, session["deadline"] - time.monotonic())))
            else:
                raise OpenRouterBatchPending(submitted["batch_id"], "pending", session["session_id"])
        raise OpenRouterBatchError(f"judge exceeded the {MAX_TURNS}-turn tool loop limit")


def _smoke_body() -> dict[str, Any]:
    return {"messages": [{"role": "user", "content": "Reply with exactly BATCH_OK and nothing else."}],
            "max_tokens": 32}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Experimental OpenRouter Batch smoke; alternate judge transport")
    parser.add_argument("--run-dir", required=True, type=Path, help="ignored HealthHarnessCodex/runs/ child")
    parser.add_argument("--max-budget-usd", type=float, default=DEFAULT_MAX_BUDGET_USD)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--submit-smoke", action="store_true", help="submit one synthetic BATCH_OK request")
    action.add_argument("--poll", metavar="BATCH_ID", help="perform one separate status/result GET")
    args = parser.parse_args(argv)
    try:
        transport = OpenRouterBatchTransport(args.run_dir, max_budget_usd=args.max_budget_usd)
        if args.poll:
            status = transport.poll(args.poll)
            print(json.dumps({k: v for k, v in status.items() if k != "result"}, sort_keys=True))
            if status.get("status") == "completed":
                results = (status.get("result") or {}).get("results") or []
                if results and isinstance(results[0].get("response"), dict):
                    blocks = results[0]["response"].get("body", {}).get("content", [])
                    text = "".join(x.get("text", "") for x in blocks if isinstance(x, dict) and x.get("type") == "text")
                    print("smoke_text=" + text[:100])
            return 0
        estimate = transport.estimate(_smoke_body())
        print(json.dumps(estimate, sort_keys=True))
        if not args.submit_smoke:
            print("plan_only=true; no request or ledger mutation")
            return 0
        if not estimate["would_fit"]:
            raise OpenRouterBatchError("smoke reservation exceeds remaining cumulative budget")
        submitted = transport.submit(_smoke_body())
        print(json.dumps(submitted, sort_keys=True))
        return 0
    except OpenRouterBatchError as exc:
        print(f"openrouter_batch_error={exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
