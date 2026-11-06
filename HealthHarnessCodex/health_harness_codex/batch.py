"""Fresh-world, resumable batch execution for the three public χ-Bench domains.

The batch runner reads public instruction files only. It never opens fixture,
expectation, registry-answer, test, or solution files. Docker and verifier work
is kept behind a small adapter so planning and tests remain offline.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from typing import Any, Callable, Protocol

from .console_logs import log_event


DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_EFFORT = "high"
DEFAULT_LIMITS = {"max_model_calls": 48, "max_tool_calls": 240,
                  "max_context_chars": 0, "max_output_tokens": 4000}
DEFAULT_TIMEOUT = 180
SIMULATOR_BACKENDS = {"official", "codex", "claude-cli"}
SPOOL_BACKENDS = {"codex", "claude-cli"}
SIMULATOR_MODEL = "gpt-6-luna"
SIMULATOR_EFFORT = "high"
SIMULATOR_MAX_OUTPUT_TOKENS = {"cm_patient": 1024, "p2p_counterparty": 512}
SIMULATOR_KIND_BY_DOMAIN = {"cm": "cm_patient", "pa_provider": "p2p_counterparty", "pa_um": "p2p_counterparty"}
SIMULATOR_BRIDGE_HOST = "127.0.0.1"
SIMULATOR_BRIDGE_PORT = 9765
SIMULATOR_BRIDGE_TARGET = "/opt/codex-simulator/simulator_bridge.py"
PRE_MODEL_SETUP_FAILURE_STOP_THRESHOLD = 3
DEFAULT_INSTRUCTION = Path("C:/Users/prath/.codex/AGENTS.md")
DEFAULT_INSTRUCTION_SHA256 = "1c683adadd4bffe13c4ff0700dc824fd3f3f35c024ffc3b6c68959f887318f96"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
def _discover_codex_executable(installation_root: Path | None = None) -> Path:
    """Discover official desktop installations; freeze the chosen file per batch."""
    root = installation_root or Path(os.environ.get(
        "LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "OpenAI/Codex/bin"
    candidates = [path for path in root.glob("*/codex.exe") if path.is_file()]
    if candidates:
        return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))
    # Leave the missing-file diagnosis to preflight; never move a binary or
    # silently switch a resumed batch to a different installation.
    return root / "codex.exe"


DEFAULT_CODEX_EXECUTABLE = _discover_codex_executable()
RUNTIME_IMAGE = "bigdata-chi-bench:runtime-4444a07"
RUNTIME_IMAGE_SHA256 = "sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66"
ROOT_LABEL = "BigData/HealthHarnessCodex"
CANONICAL_DOMAINS = {
    "pa_provider": "prior_auth_provider",
    "pa_um": "prior_auth_um",
    "cm": "care_management",
}
SETTLED_STATUSES = {"graded", "ungraded", "deferred_ready", "setup_failure", "interrupted", "needs_reconciliation"}


class BatchError(RuntimeError):
    """Batch inputs or frozen execution state are invalid."""


@dataclass(frozen=True, slots=True)
class PublicTask:
    domain: str
    task_id: str
    task_dir: Path
    instruction_sha256: str


@dataclass(frozen=True, slots=True)
class BatchConfig:
    dataset_root: Path
    run_dir: Path
    domains: tuple[str, ...] = tuple(CANONICAL_DOMAINS)
    task_ids: tuple[str, ...] = ()
    attempts: int = 1
    concurrency: int = 1
    model: str = DEFAULT_MODEL
    reasoning_effort: str = DEFAULT_EFFORT
    composition: str = "helpers"
    recovery_helper_policy: str = "auto"
    budgets: dict[str, int] | None = None
    timeout: int = DEFAULT_TIMEOUT
    active_timeout: int | None = None
    codex_executable: str = str(DEFAULT_CODEX_EXECUTABLE)
    docker_executable: str = "docker"
    instruction_sources: tuple[str, ...] = (str(DEFAULT_INSTRUCTION),)
    expected_instruction_hashes: tuple[str, ...] = (DEFAULT_INSTRUCTION_SHA256,)
    benchmark_env_file: Path | None = None
    allow_benchmark_network: bool = False
    defer_grading: bool = False
    simulator_backend: str = "official"
    simulator_max_model_calls: int = 0
    simulator_max_total_chars: int = 0
    simulator_world_deadline_seconds: int = 0
    simulator_request_timeout_seconds: int = 180
    simulator_claude_model: str = "claude-sonnet-5"
    simulator_claude_executable: str = "claude"
    simulator_effort: str = SIMULATOR_EFFORT
    actor_backend: str = "harness"
    claude_model: str = "claude-sonnet-5-5"
    claude_effort: str = "high"
    claude_executable: str = "claude"
    claude_timeout_seconds: int = 1800

    def __post_init__(self):
        if self.actor_backend == "claude-code-container" and self.benchmark_env_file is not None:
            raise ValueError("container Claude cannot use a benchmark provider env file")
        if self.actor_backend not in {"harness", "claude-code", "claude-code-container"}:
            raise ValueError("actor_backend must be harness, claude-code or claude-code-container")
        if not self.claude_model or not self.claude_executable or self.claude_effort not in {"low", "medium", "high", "max"}:
            raise ValueError("Claude model, executable and effort must be explicit")
        if type(self.claude_timeout_seconds) is not int or not 1 <= self.claude_timeout_seconds <= 1800:
            raise ValueError("Claude whole-attempt timeout must be between 1 and 1800 seconds")
        if self.actor_backend in {"claude-code", "claude-code-container"} and (self.domains != ("cm",) or len(self.task_ids) != 1
                or self.attempts != 1 or self.concurrency != 1 or self.simulator_backend != "codex"
                or not self.defer_grading):
            raise ValueError("Claude lane requires one explicit CM task/attempt, Codex patient and deferred grading")
        if not 1 <= self.attempts <= 3:
            raise ValueError("attempts must be between 1 and 3")
        if not 1 <= self.concurrency <= 3:
            raise ValueError("concurrency must be between 1 and 3")
        if not isinstance(self.timeout, int) or isinstance(self.timeout, bool) or not 1 <= self.timeout <= 1800:
            raise ValueError("timeout must be between 1 and 1800 seconds")
        from .codex_provider import validate_active_timeout
        validate_active_timeout(self.timeout, self.active_timeout)
        if not self.model or self.reasoning_effort != "high":
            raise ValueError("batch model and reasoning effort must be explicit")
        if self.composition not in {"combined","helpers","team"}:
            raise ValueError("composition must be combined, helpers or team")
        if self.recovery_helper_policy not in {'off','auto'}:raise ValueError('recovery_helper_policy must be off or auto')
        if len(self.instruction_sources) != len(self.expected_instruction_hashes):
            raise ValueError("instruction source paths and hashes must have matching lengths")
        if self.simulator_backend == "claude-cli" and self.benchmark_env_file is not None:
            raise ValueError("Claude patient cannot use benchmark credentials")
        if self.benchmark_env_file is not None:
            _benchmark_environment(self.benchmark_env_file, self.allow_benchmark_network)
        if self.simulator_backend not in SIMULATOR_BACKENDS:
            raise ValueError("simulator_backend must be official, codex or claude-cli")
        for name, value, minimum, maximum in (
                ("simulator_max_model_calls", self.simulator_max_model_calls, 0, 64),
                ("simulator_max_total_chars", self.simulator_max_total_chars, 0, 180_000),
                ("simulator_world_deadline_seconds", self.simulator_world_deadline_seconds, 0, 900),
                ("simulator_request_timeout_seconds", self.simulator_request_timeout_seconds, 1, 180)):
            if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
                raise ValueError(f"{name} must be between {minimum} and {maximum}")
        from .simulator_worker import SIMULATOR_EFFORTS
        if self.simulator_effort not in SIMULATOR_EFFORTS:
            raise ValueError("simulator_effort must be one of " + ", ".join(SIMULATOR_EFFORTS))
        if self.simulator_backend == "claude-cli" and (not self.simulator_claude_model.strip()
                                                       or not self.simulator_claude_executable.strip()):
            raise ValueError("Claude patient model and executable must be explicit")
        if self.simulator_backend == "claude-cli" and self.allow_benchmark_network:
            raise ValueError("Claude patient requires network none in the benchmark container")
        if self.simulator_backend in SPOOL_BACKENDS:
            if not self.defer_grading:
                raise ValueError("the experimental Codex simulator backend requires deferred grading")
            if self.benchmark_env_file is not None or (self.allow_benchmark_network and self.actor_backend != "claude-code-container"):
                raise ValueError("the Codex simulator backend cannot use benchmark credentials or egress")
            # The simulator worker independently pins its model/effort. Actor
            # model selection must not silently select or constrain the patient.


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _save_stage_diagnostic(attempt_dir: Path, stage: str, exc: Exception) -> bool:
    """Private OS/frame facts only; no exception bodies, locals or payloads."""
    try:
        if not attempt_dir.is_dir() or attempt_dir.is_symlink():return False
        record={'stage':stage,'error_type':type(exc).__name__,
            'frames':[{'file':Path(f.filename).name,'function':f.name,'line':f.lineno}
                      for f in traceback.extract_tb(exc.__traceback__)[-20:]]}
        if isinstance(exc,OSError):
            for name in ('errno','winerror'):
                value=getattr(exc,name,None)
                if type(value) is int:record[name]=value
            for name in ('filename','filename2'):
                value=getattr(exc,name,None)
                if isinstance(value,str):record[name]=value[:2000]
        target=attempt_dir/'stage-error.private.json'
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as handle:json.dump(record,handle,ensure_ascii=False,indent=2)
        return True
    except (OSError,ValueError,TypeError):return False


def _container_name(run_root: Path, task: PublicTask, attempt: int) -> str:
    batch_key = hashlib.sha256(str(Path(run_root).resolve()).encode("utf-8")).hexdigest()[:12]
    task_key = hashlib.sha256(task.task_id.encode("utf-8")).hexdigest()[:8]
    return f"bigdata-health-codex-{batch_key}-{task.domain}-{task_key}-a{attempt}"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _codex_executable_sha256(value: str | Path, *, required: bool) -> str | None:
    """Validate/hash the configured native executable without launching it."""
    path = Path(value)
    if not path.is_absolute():
        if required:
            raise BatchError("Codex executable path must be absolute")
        return None
    if path.is_symlink():
        if required:
            raise BatchError("Codex executable must not be a symlink")
        return None
    if not path.is_file():
        if required:
            raise BatchError("Codex executable is missing or is not a regular file")
        return None
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_absolute() or not resolved.is_file():
            raise OSError("not a regular file")
        return _sha256_file(resolved)
    except OSError:
        if required:
            raise BatchError("Codex executable could not be read") from None
        return None


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


_BATCH_EVENT_FIELDS = {
    "stage", "error_type", "elapsed_seconds", "timeout_seconds", "active_timeout_seconds", "timeout_reason", "model", "reasoning_effort",
    "model_calls", "tool_calls", "turns", "assistant_messages_seen", "task_index", "total_tasks", "selected_tasks", "concurrency",
    "settled", "active", "pending", "saved", "failed", "reconciliation", "grading_status",
    "harness_status", "execution_state", "goal_status", "status", "current", "total", "task_count", "tool_count", "attempts",
    "settled_tasks", "active_attempts", "pending_attempts", "saved_snapshots", "failed_attempts",
    "reconciliation_attempts", "ungraded_attempts",
}


def _batch_progress_fields(manifest: dict[str, Any]) -> dict[str, int]:
    tasks = manifest.get("tasks", [])
    attempts = [attempt for task in tasks for attempt in task.get("attempts", [])]
    return {
        "selected_tasks": len(tasks),
        "settled_tasks": sum(bool(task.get("attempts")) and all(
            item.get("status") in SETTLED_STATUSES for item in task.get("attempts", [])) for task in tasks),
        "active_attempts": sum(item.get("status") == "running" for item in attempts),
        "pending_attempts": sum(item.get("status") == "pending" for item in attempts),
        "saved_snapshots": sum(item.get("status") == "deferred_ready" for item in attempts),
        "failed_attempts": sum(item.get("status") in {"setup_failure", "interrupted"}
                                for item in attempts),
        "ungraded_attempts": sum(item.get("status") == "ungraded" for item in attempts),
        "reconciliation_attempts": sum(item.get("status") == "needs_reconciliation" for item in attempts),
    }


def _evaluation_summary(attempt_dir: Path) -> dict[str, Any]:
    """Return only safe local status and counters from an evaluation receipt."""
    path = attempt_dir / "evaluation.json"
    if path.is_symlink() or not path.is_file():
        return {}
    try:
        evaluation = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    metrics = evaluation.get("metrics") if isinstance(evaluation, dict) else None
    result: dict[str, Any] = {}
    status = evaluation.get("harness_status") if isinstance(evaluation, dict) else None
    if isinstance(status, str):
        result["harness_status"] = status
    if isinstance(metrics, dict):
        for field in ("model_calls", "tool_calls"):
            value = metrics.get(field)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                result[field] = value
    return result


_SAFE_HARNESS_STATUSES = {
    "complete", "incomplete", "error", "failed", "exhausted", "running",
    "setup_failure", "interrupted", "unresolved", "needs_reconciliation",
    "deferred_ready", "ungraded", "graded",
}


def _safe_harness_status(value: Any) -> str:
    return value if isinstance(value, str) and value in _SAFE_HARNESS_STATUSES else "unknown"


_BATCH_TEXT_FIELDS = {"stage", "error_type", "model", "reasoning_effort", "grading_status",
                      "harness_status", "execution_state", "goal_status", "status"}


def _append_batch_event(path: Path, write_lock: threading.RLock, event: str, *,
                        task_id: str | None = None, domain: str | None = None,
                        attempt: int | None = None, **fields: Any) -> str:
    safe_fields: dict[str, Any] = {}
    for key, value in fields.items():
        if key not in _BATCH_EVENT_FIELDS or value is None:
            continue
        if key in _BATCH_TEXT_FIELDS:
            if isinstance(value, str):
                text_value = "".join(ch for ch in value if ch.isprintable() and ch not in "\r\n\t")[:96]
                if text_value:
                    safe_fields[key] = text_value
        elif isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
            safe_fields[key] = value
    safe_task_id = re.sub(r"[^A-Za-z0-9_.-]", "_", task_id)[:96] if task_id is not None else None
    safe_domain = re.sub(r"[^A-Za-z0-9_.-]", "_", domain)[:48] if domain is not None else None
    record = {"time": _utc_now(), "kind": event, "task_id": safe_task_id,
              "domain": safe_domain, "attempt": attempt, **safe_fields}
    with write_lock:
        line = log_event(event, task_id=safe_task_id, domain=safe_domain, attempt=attempt, **safe_fields)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            stream.flush()
    return line


def _benchmark_environment(env_file: Path | None, allow_network: bool) -> dict[str, Any]:
    if env_file is None:
        return {"mode": "no_benchmark_keys", "network": "bridge" if allow_network else "none",
                "env_file": None}
    if not allow_network:
        raise BatchError("--benchmark-env-file requires explicit --allow-benchmark-network")
    original = Path(env_file)
    if original.is_symlink():
        raise BatchError("benchmark environment file must not be a symlink")
    try:
        path = original.resolve(strict=True)
    except OSError:
        raise BatchError("benchmark environment file is unavailable") from None
    expected = PROJECT_ROOT / "Runner" / ".env"
    if path != expected.resolve() or path.name != ".env" or not path.is_file():
        raise BatchError("benchmark environment must be the ignored local Runner/.env file")
    return {"mode": "explicit_local_benchmark_env_file", "network": "bridge", "env_file": str(path)}


def enumerate_public_tasks(dataset_root: Path, domains: tuple[str, ...] | None = None,
                           task_ids: tuple[str, ...] = ()) -> list[PublicTask]:
    root = Path(dataset_root).resolve(strict=True)
    if not root.is_dir():
        raise BatchError("dataset root must be a directory")
    selected = tuple(domains or CANONICAL_DOMAINS)
    if not selected or len(set(selected)) != len(selected) or any(d not in CANONICAL_DOMAINS for d in selected):
        raise BatchError("domains must be unique canonical values: pa_provider, pa_um, cm")
    tasks: list[PublicTask] = []
    for domain in selected:
        tasks_dir = root / CANONICAL_DOMAINS[domain] / "tasks"
        if tasks_dir.is_symlink() or not tasks_dir.is_dir():
            raise BatchError(f"public task directory is missing or linked for {domain}")
        domain_tasks: list[PublicTask] = []
        for task_dir in sorted(tasks_dir.iterdir(), key=lambda p: p.name):
            if task_dir.is_symlink() or not task_dir.is_dir():
                continue
            task_id = task_dir.name
            instruction = task_dir / "instruction.md"
            if instruction.is_symlink() or not instruction.is_file():
                raise BatchError(f"{domain}/{task_id} has no regular public instruction.md")
            try:
                body = instruction.read_bytes()
                body.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                raise BatchError(f"{domain}/{task_id} public instruction is unreadable") from None
            if not body or len(body) > 250_000:
                raise BatchError(f"{domain}/{task_id} public instruction is empty or oversized")
            domain_tasks.append(PublicTask(domain, task_id, task_dir.resolve(), _sha256_bytes(body)))
        if not task_ids and len(domain_tasks) != 25:
            raise BatchError(f"expected exactly 25 public tasks in {domain}; found {len(domain_tasks)}")
        tasks.extend(domain_tasks)
    if task_ids:
        if len(set(task_ids)) != len(task_ids):
            raise BatchError("task-id selection must not contain duplicates")
        by_id: dict[str, list[PublicTask]] = {}
        for task in tasks:
            by_id.setdefault(task.task_id, []).append(task)
        missing = [task_id for task_id in task_ids if task_id not in by_id]
        if missing:
            raise BatchError("one or more exact task IDs were not found in selected public domains")
        ambiguous = [task_id for task_id in task_ids if len(by_id[task_id]) > 1]
        if ambiguous:
            raise BatchError("an exact task ID is duplicated across selected domains; select one --domain")
        tasks = [by_id[task_id][0] for task_id in task_ids]
    if not tasks:
        raise BatchError("no public tasks selected")
    return tasks


def _source_identity() -> dict[str, Any]:
    from .standalone import _source_commit, _source_fingerprint
    from .hybrid_search import runtime_config

    package_root = Path(__file__).resolve().parent
    files = [*package_root.rglob("*.py"), *(package_root / 'data').glob('*.json')]
    return {"source_fingerprint": _source_fingerprint(), "source_commit": _source_commit(),
            'retrieval_runtime':runtime_config(),
            "source_files": sum(path.is_file() and "__pycache__" not in path.parts for path in files)}


def _instruction_pins(config: BatchConfig) -> dict[str, str]:
    pins: dict[str, str] = {}
    for source, expected in zip(config.instruction_sources, config.expected_instruction_hashes):
        original = Path(source)
        if original.is_symlink():
            raise BatchError("approved instruction source must not be a symlink")
        path = original.resolve(strict=True)
        if not path.is_file():
            raise BatchError("approved instruction source must be a regular file")
        digest = _sha256_file(path)
        if digest != expected:
            raise BatchError("approved instruction source changed from its reviewed hash")
        pins[str(path)] = digest
    return pins


def _frozen_config(config: BatchConfig, tasks: list[PublicTask], pins: dict[str, str],
                   source: dict[str, Any], codex_executable_sha256: str | None = None) -> dict[str, Any]:
    actor_settings = {}
    patient_settings = {}
    if config.simulator_backend == "claude-cli":
        from .claude_cli_patient import provenance
        patient_settings = provenance(config.simulator_claude_executable, config.simulator_claude_model)
    if config.actor_backend == "claude-code":
        from .claude_code_actor import ISOLATED_SETTINGS, MAX_MCP_OUTPUT_TOKENS, SERVER
        executable = shutil.which(config.claude_executable)
        path = Path(executable or config.claude_executable)
        actor_settings = {"actor_backend": "claude-code", "claude_code": {
            "model": config.claude_model, "effort": config.claude_effort,
            "executable": str(path.resolve()) if path.is_file() else config.claude_executable,
            "executable_sha256": _sha256_file(path) if path.is_file() else None,
            "timeout_seconds": config.claude_timeout_seconds,
            "max_mcp_output_tokens": MAX_MCP_OUTPUT_TOKENS,
            "setting_sources": [], "settings": ISOLATED_SETTINGS,
            "mcp_server": SERVER, "builtin_tools": [], "permission_mode": "dontAsk",
            "prompt": "public_instruction_verbatim", "harness_helpers": False,
            "harness_budgets_applied": False}}
    elif config.actor_backend == "claude-code-container":
        from .claude_code_container_actor import MCP_CONFIG
        actor_settings = {"actor_backend": config.actor_backend, "claude_code": {
            "model": config.claude_model, "effort": config.claude_effort,
            "timeout_seconds": config.claude_timeout_seconds,
            "installation": "harbor-0.20.0-check-existing-or-native-bootstrap", "cli_version_pin": None,
            "mcp": MCP_CONFIG, "cwd": "/workspace", "user": "root", "IS_SANDBOX": "1",
            "permission_mode": "bypassPermissions", "filesystem_isolation": "Landlock-ABI>=3",
            "session_persistence": False, "prompt": "public_instruction_verbatim_stdin",
            "harness_helpers": False, "harness_budgets_applied": False,
            "authentication": "exec_only_subscription_oauth"}}
    return {
        **actor_settings,
        "dataset_root_name": Path(config.dataset_root).resolve().name,
        "domains": list(config.domains),
        "task_instruction_sha256": {f"{task.domain}/{task.task_id}": task.instruction_sha256 for task in tasks},
        "attempts": config.attempts,
        "concurrency": config.concurrency,
        "model": config.claude_model if config.actor_backend.startswith("claude-code") else config.model,
        "reasoning_effort": config.claude_effort if config.actor_backend.startswith("claude-code") else config.reasoning_effort,
        "composition": config.composition,
        "recovery_helper_policy":config.recovery_helper_policy,
        "budgets": dict(config.budgets or DEFAULT_LIMITS),
        "model_request_timeout_seconds": config.timeout,
        "model_request_active_timeout_seconds": config.active_timeout,
        "codex_executable": str(Path(config.codex_executable)),
        "codex_executable_sha256": codex_executable_sha256,
        "allowed_instruction_source_sha256": pins,
        **source,
        "runtime_image": RUNTIME_IMAGE,
        "runtime_image_sha256": RUNTIME_IMAGE_SHA256,
        "benchmark_environment": _benchmark_environment(config.benchmark_env_file,
                                                           config.allow_benchmark_network or config.actor_backend == "claude-code-container"),
        "defer_grading": config.defer_grading,
        "simulator": {
            "backend": config.simulator_backend,
            "model": SIMULATOR_MODEL if config.simulator_backend in SPOOL_BACKENDS else None,
            "reasoning_effort": config.simulator_effort if config.simulator_backend in SPOOL_BACKENDS else None,
            "max_model_calls_per_world": config.simulator_max_model_calls,
            "max_total_chars_per_world": config.simulator_max_total_chars,
            "world_deadline_seconds": config.simulator_world_deadline_seconds,
            "request_timeout_seconds": config.simulator_request_timeout_seconds,
            "requested_max_output_tokens_advisory": (dict(SIMULATOR_MAX_OUTPUT_TOKENS)
                                                       if config.simulator_backend in SPOOL_BACKENDS else None),
            "network_mode": ("bridge" if config.actor_backend == "claude-code-container" else "none") if config.simulator_backend in SPOOL_BACKENDS else None,
            "host_ports": [],
            "bridge_sha256": (_sha256_file(Path(__file__).with_name("simulator_bridge.py"))
                              if config.simulator_backend in SPOOL_BACKENDS else None),
            "experimental_official_grade_eligible": config.simulator_backend == "official",
            **patient_settings,
        },
    }


def _replace_with_reader_retry(source: Path, destination: Path) -> None:
    """Windows readers can briefly deny atomic replacement; never retry actions."""
    for attempt in range(20):
        try:
            source.replace(destination)
            return
        except PermissionError as exc:
            if os.name != "nt" or getattr(exc, "winerror", None) not in {5, 32} or attempt == 19:
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.1))


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}-", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_reader_retry(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _write_grade_csv(path: Path, tasks: list[dict[str, Any]]) -> None:
    rows = []
    for task in tasks:
        attempts = task.get("attempts", [])
        if not attempts:
            continue
        first = attempts[0]
        if first.get("status") == "graded" and first.get("official_score") in (0, 1):
            rows.append({"task_id": task["task_id"], "reward": first["official_score"]})
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}-", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=("task_id", "reward"))
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_reader_retry(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _aggregator_helpers():
    path = Path(__file__).resolve().parents[1] / "evaluations" / "aggregate_official_pilot.py"
    spec = importlib.util.spec_from_file_location("batch_official_result_helpers", path)
    if spec is None or spec.loader is None:
        raise BatchError("official result validation helpers are unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorldAdapter(Protocol):
    def start(self, task: PublicTask, container_name: str, logs_dir: Path) -> str: ...
    def preflight(self, container: str, task: PublicTask, timeout: float, *, attempt_number: int | None = None,
                  event_logger: Callable[..., str] | None = None) -> list[str]: ...
    def grade(self, container: str, task: PublicTask, output_name: str, timeout: float) -> dict[str, Any]: ...
    def export_state(self, container: str, timeout: float) -> dict[str, Any]: ...
    def stop(self, container: str) -> str | None: ...


class DockerWorldAdapter:
    """Start one isolated runtime and use fixed read-only preflight/grading calls."""

    def __init__(self, docker: str = "docker", benchmark_env_file: Path | None = None,
                 allow_benchmark_network: bool = False, *, actor_backend: str = "harness"):
        self.docker = docker
        self.actor_backend = actor_backend
        self.benchmark_env = _benchmark_environment(benchmark_env_file, allow_benchmark_network or actor_backend == "claude-code-container")
        self._logs_by_container: dict[str, Path] = {}

    def _verify_runtime_image(self) -> str:
        try:
            result = subprocess.run([self.docker, "image", "inspect", "--format", "{{.Id}}", RUNTIME_IMAGE],
                                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                                    timeout=15, check=False,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BatchError(f"runtime image identity check failed ({type(exc).__name__})") from None
        image_id = result.stdout.strip()
        if result.returncode != 0 or image_id != RUNTIME_IMAGE_SHA256:
            raise BatchError("runtime image tag does not resolve to the frozen image digest")
        return image_id

    def start(self, task: PublicTask, container_name: str, logs_dir: Path, *,
              simulator_backend: str = "official", simulator_spool: Path | None = None,
              simulator_effort: str = SIMULATOR_EFFORT,
              simulator_model: str = SIMULATOR_MODEL) -> str:
        self._verify_runtime_image()
        logs_dir.mkdir(parents=True, exist_ok=True)
        network = self.benchmark_env["network"]
        if simulator_backend == "claude-cli" and (network != "none" or self.benchmark_env.get("env_file")):
            raise BatchError("Claude patient requires network none and no benchmark credentials")
        if simulator_backend in SPOOL_BACKENDS and network != "none" and self.actor_backend != "claude-code-container":
            raise BatchError("Codex patient egress requires the container Claude actor backend")
        command = [self.docker, "run", "-d", "--name", container_name, "--network", network,
                   "--label", f"com.bigdata.workspace={ROOT_LABEL}",
                   "--label", "com.bigdata.ownedcase=1",
                   "--env", f"CHI_BENCH_TASK_ID={task.task_id}",
                   "--env", "CHI_BENCH_TASKS_ROOT=/opt/chi-bench/tasks",
                   "--mount", f"type=bind,source={logs_dir.resolve()},target=/logs",
                  ]
        if simulator_backend in SPOOL_BACKENDS:
            if simulator_spool is None:
                raise BatchError("experimental simulator spool path is required")
            bridge_source = Path(__file__).with_name("simulator_bridge.py").resolve(strict=True)
            command.extend([
                "--mount", f"type=bind,source={simulator_spool.resolve()},target=/simulator-spool",
                "--mount", f"type=bind,source={bridge_source},target={SIMULATOR_BRIDGE_TARGET},readonly",
                "--env", "ANTHROPIC_BASE_URL=http://127.0.0.1:9765",
                "--env", "ANTHROPIC_API_KEY=codex-local-bridge",
                "--env", f"CHI_BENCH_SIMULATOR_KIND={SIMULATOR_KIND_BY_DOMAIN[task.domain]}",
                "--env", "CHI_BENCH_SIMULATOR_SPOOL=/simulator-spool",
                "--env", f"CHI_BENCH_SIMULATOR_BACKEND_MODEL={simulator_model}",
                "--env", f"CHI_BENCH_SIMULATOR_BACKEND_EFFORT={simulator_effort}",
            ])
        env_file = self.benchmark_env.get("env_file")
        if env_file:
            command.extend(["--env-file", env_file])
        elif simulator_backend not in SPOOL_BACKENDS:
            command.extend(["--env", "HF_TOKEN=", "--env", "ANTHROPIC_API_KEY=", "--env", "OPENAI_API_KEY=",
                            "--env", "OPENAI_BASE_URL=", "--env", "HEALTH_HARNESS_API_KEY="])
        else:
            command.extend(["--env", "HF_TOKEN=", "--env", "OPENAI_API_KEY=", "--env", "OPENAI_BASE_URL=",
                            "--env", "HEALTH_HARNESS_API_KEY="])
        command.extend([RUNTIME_IMAGE, "sleep", "infinity"])
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=60, check=False,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BatchError(f"Docker world could not start ({type(exc).__name__})") from None
        if result.returncode != 0:
            raise BatchError(f"Docker world could not start (exit {result.returncode})")
        try:
            inspected = subprocess.run([self.docker, "inspect", "--format", "{{.Image}}", container_name],
                                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                                       timeout=15, check=False,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired) as exc:
            subprocess.run([self.docker, "stop", "--time", "2", container_name], capture_output=True,
                           timeout=10, check=False)
            raise BatchError(f"started world image identity could not be checked ({type(exc).__name__})") from None
        if inspected.returncode != 0 or inspected.stdout.strip() != RUNTIME_IMAGE_SHA256:
            subprocess.run([self.docker, "stop", "--time", "2", container_name], capture_output=True,
                           timeout=10, check=False)
            raise BatchError("started world did not use the frozen runtime image digest")
        container = result.stdout.strip() or container_name
        self._logs_by_container[container] = logs_dir.resolve()
        return container

    def start_simulator_bridge(self, container: str, task: PublicTask, *, request_timeout: int,
                               simulator_effort: str = SIMULATOR_EFFORT,
                               simulator_model: str = SIMULATOR_MODEL) -> None:
        from .docker_bridge import DockerExecutor
        command = [self.docker, "exec", "-d", container, "python", SIMULATOR_BRIDGE_TARGET,
                   "--spool-root", "/simulator-spool", "--host", SIMULATOR_BRIDGE_HOST,
                   "--port", str(SIMULATOR_BRIDGE_PORT), "--simulator-kind", SIMULATOR_KIND_BY_DOMAIN[task.domain],
                   "--backend-model", simulator_model, "--backend-effort", simulator_effort,
                   "--request-timeout", str(request_timeout)]
        try:
            launched = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                      errors="replace", timeout=10, check=False,
                                      creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BatchError(f"experimental simulator bridge launch failed ({type(exc).__name__})") from None
        if launched.returncode:
            raise BatchError("experimental simulator bridge launch failed")
        executor = DockerExecutor(container, docker=self.docker, timeout=10)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                result = executor.python_json(
                    "import json,urllib.request; r=urllib.request.urlopen('http://127.0.0.1:9765/health',timeout=2); print(json.dumps({'ready':r.status==200}))",
                    {}, timeout=4)
                if isinstance(result, dict) and result.get("ready") is True:
                    return
            except Exception:
                time.sleep(0.2)
        raise BatchError("experimental simulator bridge did not become healthy")

    def preflight(self, container: str, task: PublicTask, timeout: float, *, attempt_number: int | None = None,
                  event_logger: Callable[..., str] | None = None) -> list[str]:
        from .docker_bridge import DockerExecutor, DockerMCPClient
        from .domain_profiles import domain_for_task

        profile = domain_for_task(task.task_dir)
        executor = DockerExecutor(container, docker=self.docker, timeout=min(40, timeout))
        executor.validate_owned_trial(task.task_id)
        deadline = time.monotonic() + min(120.0, timeout)
        next_notice = time.monotonic() + 30
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                health = executor.python_json(
                    "import hashlib,json,pathlib,sys,urllib.request; d=json.load(sys.stdin); "
                    "r=urllib.request.urlopen('http://127.0.0.1:'+str(d['port'])+'/health',timeout=3); "
                    "p=pathlib.Path('/opt/chi-bench/tasks')/d['task_id']/'instruction.md'; "
                    "h=hashlib.sha256(p.read_bytes()).hexdigest(); "
                    "print(json.dumps({'healthy':r.status==200,'instruction_matches':h==d['instruction_sha256']}))",
                    {"port": 8023, "task_id": task.task_id,
                     "instruction_sha256": task.instruction_sha256},
                    timeout=min(5, max(1, deadline - time.monotonic())))
                if not isinstance(health, dict) or health.get("healthy") is not True:
                    raise BatchError("runtime health endpoint did not return healthy")
                if health.get("instruction_matches") is not True:
                    raise BatchError("baked public task instruction hash differs from frozen host instruction")
                client = DockerMCPClient(container, port=profile.port, timeout=min(10, timeout), executor=executor)
                names = [str(spec.name) for spec in client.list_tools()]
                if not names:
                    raise BatchError("selected actor exposed no tools")
                return names
            except Exception as exc:
                last_error = exc
                if time.monotonic() >= next_notice:
                    logger = event_logger or log_event
                    logger("world_waiting", task_id=task.task_id, domain=task.domain,
                           attempt=attempt_number, stage="runtime health and actor tool preflight",
                           elapsed_seconds=min(120.0, timeout) - max(0.0, deadline - time.monotonic()),
                           timeout_seconds=min(120.0, timeout), status="waiting")
                    next_notice = time.monotonic() + 30
                time.sleep(min(2, max(0, deadline - time.monotonic())))
        raise BatchError(f"runtime health/tool preflight failed ({type(last_error).__name__ if last_error else 'timeout'})")

    def grade(self, container: str, task: PublicTask, output_name: str, timeout: float) -> dict[str, Any]:
        from .docker_bridge import DockerExecutor

        executor = DockerExecutor(container, docker=self.docker, timeout=min(130, timeout))
        script = r'''import json,pathlib,subprocess,sys
d=json.load(sys.stdin); task=d['task_id']; out=pathlib.Path('/logs')/d['output_name']; out.mkdir(parents=True,exist_ok=True)
names={'reward':'reward.json','scorecard':'scorecard.json','export':'exported_state.json','context':'verifier_context.json'}
cmd=[sys.executable,'-m','chi_bench.verifier.task_runtime','verify','--expectations-path',f'/opt/chi-bench/tasks/{task}/fixtures/expectations.json','--verifier-host','127.0.0.1','--verifier-port','8023','--reward-path',str(out/names['reward']),'--scorecard-path',str(out/names['scorecard']),'--exported-state-path',str(out/names['export']),'--verifier-context-path',str(out/names['context'])]
try:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=d['timeout'],check=False)
 stdout,stderr=p.stdout or '',p.stderr or ''; code=p.returncode; timed=False
except subprocess.TimeoutExpired as e:
 stdout=e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or '')
 stderr=e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
 code=None; timed=True
(out/'verifier.private.log').write_text(stdout+'\n'+stderr,encoding='utf-8')
low=(stdout+'\n'+stderr).casefold(); export_timeout=timed and 'export' in low or ('export' in low and ('timed out' in low or 'timeout' in low))
print(json.dumps({'returncode':code,'timed_out':timed,'export_timeout':bool(export_timeout),
 'artifacts':{k:{'exists':(out/v).is_file(),'bytes':(out/v).stat().st_size if (out/v).is_file() else None} for k,v in names.items()}}))
'''
        inner_timeout = min(120, max(10, timeout - 10))
        return executor.python_json(script, {"task_id": task.task_id, "output_name": output_name,
                                             "timeout": inner_timeout}, timeout=min(130, timeout))

    def export_state(self, container: str, timeout: float) -> dict[str, Any]:
        """Capture the actor's actual verifier export without invoking grading."""
        from .docker_bridge import DockerExecutor

        logs_dir = self._logs_by_container.get(container)
        if logs_dir is None:
            raise BatchError("world adapter has no bound actor log directory for verifier export")
        filename = f".deferred-export-{threading.get_ident()}-{time.monotonic_ns()}.json"
        target = logs_dir / filename
        if target.exists() or target.is_symlink():
            raise BatchError("deferred export capture path already exists")
        script = r'''import hashlib,json,pathlib,sys,urllib.request
d=json.load(sys.stdin); name=d['name']
if '/' in name or '\\' in name or not name.startswith('.deferred-export-'): raise RuntimeError('bad_capture_path')
with urllib.request.urlopen('http://127.0.0.1:8023/export',timeout=float(d['timeout'])) as r:
 data=r.read(100*1024*1024+1)
if len(data)>100*1024*1024: raise RuntimeError('export_too_large')
value=json.loads(data.decode('utf-8'))
if not isinstance(value,dict): raise RuntimeError('export_not_object')
p=pathlib.Path('/logs')/name; tmp=p.with_suffix('.tmp'); tmp.write_bytes(data); tmp.replace(p)
print(json.dumps({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}))
'''
        executor = DockerExecutor(container, docker=self.docker, timeout=min(130, timeout))
        try:
            receipt = executor.python_json(script, {"name": filename, "timeout": max(1, min(120, timeout))},
                                           timeout=min(130, timeout))
            if not isinstance(receipt, dict) or not isinstance(receipt.get("bytes"), int):
                raise BatchError("verifier export transport returned an invalid receipt")
            if target.is_symlink() or not target.is_file() or target.stat().st_size != receipt["bytes"]:
                raise BatchError("verifier export capture is missing or changed")
            raw = target.read_bytes()
            if _sha256_bytes(raw) != receipt.get("sha256"):
                raise BatchError("verifier export capture digest mismatch")
            if len(raw) > 100 * 1024 * 1024:
                raise BatchError("verifier export exceeds deferred snapshot size limit")
            exported = json.loads(raw.decode("utf-8"))
            if not isinstance(exported, dict):
                raise BatchError("verifier export did not return an object")
            return exported
        finally:
            if target.exists() and not target.is_symlink():
                target.unlink()

    def stop(self, container: str) -> str | None:
        try:
            stopped = subprocess.run([self.docker, "stop", "--time", "5", container], capture_output=True,
                                     text=True, timeout=20, check=False,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
            inspected = subprocess.run([self.docker, "inspect", "--format", "{{.State.Running}}", container],
                                       capture_output=True, text=True, timeout=10, check=False,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return f"stop_or_inspect_failed:{type(exc).__name__}"
        if inspected.returncode == 0 and inspected.stdout.strip() == "false":
            return None
        if stopped.returncode != 0 or inspected.returncode != 0:
            return "stop_or_inspect_failed"
        return "container_still_running"


def _snapshot_sqlite(source: Path, destination: Path) -> str:
    if not source.is_file():
        raise BatchError("native case state database is missing")
    uri = "file:" + source.resolve().as_posix().replace("?", "%3F") + "?mode=ro"
    try:
        src = sqlite3.connect(uri, uri=True, timeout=10)
        try:
            src.execute("PRAGMA query_only=ON")
            check = src.execute("PRAGMA integrity_check").fetchone()
            if not check or check[0] != "ok":
                raise BatchError("native case state failed SQLite integrity_check")
            dst = sqlite3.connect(destination)
            try:
                src.backup(dst)
                check_dst = dst.execute("PRAGMA integrity_check").fetchone()
                if not check_dst or check_dst[0] != "ok":
                    raise BatchError("read-only SQLite snapshot failed integrity_check")
            finally:
                dst.close()
        finally:
            src.close()
    except BatchError:
        raise
    except sqlite3.Error:
        raise BatchError("native SQLite state snapshot failed") from None
    return _sha256_file(destination)


def _official_grade(logs_dir: Path, output_name: str,
                    verifier_returncode: int | None) -> tuple[str, dict[str, Any]]:
    helpers = _aggregator_helpers()
    verifier = logs_dir / output_name
    paths = {name: verifier / filename for name, filename in (
        ("reward", "reward.json"), ("scorecard", "scorecard.json"), ("context", "verifier_context.json"),
        ("export", "exported_state.json"))}
    if not all(paths[name].is_file() for name in ("reward", "scorecard", "context", "export")):
        return "ungraded", {"reason": "official_artifact_missing"}
    try:
        reward_doc = json.loads(paths["reward"].read_text(encoding="utf-8"))
        scorecard = json.loads(paths["scorecard"].read_text(encoding="utf-8"))
        context = json.loads(paths["context"].read_text(encoding="utf-8"))
        if not all(isinstance(doc, dict) for doc in (reward_doc, scorecard, context)):
            raise ValueError("artifact root is not object")
        reward = helpers._extract_binary_reward(reward_doc)
        counts = helpers._summarize_scorecard(scorecard)
        scorecard_reward = helpers._optional_scorecard_reward(scorecard)
        if scorecard_reward is not None and scorecard_reward != reward:
            return "ungraded", {"reason": "reward_scorecard_disagreement"}
        scorecard_binary = int(counts["failed"] == 0 and counts["non_na"] > 0)
        if reward != scorecard_binary:
            return "ungraded", {"reason": "reward_check_disagreement"}
    except Exception as exc:
        return "ungraded", {"reason": "official_artifact_invalid", "error_type": type(exc).__name__}
    try:
        semantic = helpers._validate_semantic_status({}, scorecard, context, counts["check_names"])
    except Exception:
        availability = _safe_judge_availability(context, scorecard, counts["check_names"])
        if availability["status"] != "ok":
            return "ungraded", {"reason": availability["reason"],
                                "judge_availability": availability["status"]}
        return "ungraded", {"reason": "official_semantic_status_invalid"}
    expected_returncode = 0 if reward == 1 else 1
    if verifier_returncode != expected_returncode:
        return "ungraded", {"reason": "official_verifier_exit_code_disagrees_with_reward",
                            "returncode": verifier_returncode}
    return "graded", {"reward": reward,
                       "checks": {key: counts[key] for key in ("passed", "failed", "not_applicable", "total")},
                       "failed_check_names": counts["failed_check_names"], "semantic_evaluation": semantic,
                       "verifier_artifacts": {key: {"path": path.name, "sha256": _sha256_file(path),
                                                    "bytes": path.stat().st_size}
                                              for key, path in paths.items() if path.is_file()}}


def _safe_judge_availability(context: dict[str, Any], scorecard: dict[str, Any],
                             check_names: list[str]) -> dict[str, str]:
    reason_keys = {"judge_unavailable_reason", "semantic_judge_unavailable_reason",
                   "semantic_unavailable_reason"}
    if any(context.get(key) is not None for key in reason_keys if key in context):
        return {"status": "unavailable", "reason": "official_judge_unavailable"}
    degraded = context.get("degraded_rubric_ids", scorecard.get("degraded_rubric_ids"))
    if degraded not in (None, [], {}):
        return {"status": "degraded", "reason": "semantic_evaluation_degraded"}
    session = context.get("judge_session_metadata")
    if isinstance(session, dict):
        status = session.get("status", session.get("state"))
        if isinstance(status, str) and status.casefold() in {"unavailable", "degraded", "failed", "skipped"}:
            return {"status": "unavailable" if status.casefold() == "unavailable" else "degraded",
                    "reason": "official_judge_unavailable" if status.casefold() == "unavailable"
                    else "semantic_evaluation_degraded"}
    judge_checks = [name for name in check_names if "judge" in name.casefold() and "semantic" in name.casefold()]
    if judge_checks:
        has_status = any(key in context for key in reason_keys) or isinstance(session, dict)
        if not has_status:
            return {"status": "unverified", "reason": "official_judge_availability_unverified"}
    return {"status": "ok", "reason": ""}


def _summary(manifest: dict[str, Any]) -> dict[str, Any]:
    tasks = manifest["tasks"]
    entries = [trial for task in tasks for trial in task["attempts"]]
    domains = sorted({task["domain"] for task in tasks})
    attempts_per_task = int(manifest["frozen_config"]["attempts"])

    def block(selected_tasks: list[dict[str, Any]]) -> dict[str, Any]:
        planned = len(selected_tasks)
        complete_groups: list[list[dict[str, Any]]] = []
        first_attempts = [task["attempts"][0] for task in selected_tasks if task.get("attempts")]
        for task in selected_tasks:
            attempts = task.get("attempts", [])
            if len(attempts) == attempts_per_task and all(
                    a.get("status") == "graded" and isinstance(a.get("official_score"), int) for a in attempts):
                complete_groups.append(attempts)
        complete = len(complete_groups) == planned and planned > 0
        task_pass_rates = [sum(a["official_score"] == 1 for a in group) / attempts_per_task
                           for group in complete_groups]
        any_pass_rates = [float(any(a["official_score"] == 1 for a in group)) for group in complete_groups]
        all_pass_rates = [float(all(a["official_score"] == 1 for a in group)) for group in complete_groups]
        first_graded = sum(a.get("status") == "graded" and isinstance(a.get("official_score"), int)
                           for a in first_attempts)
        result = {"planned_tasks": planned, "evaluated_tasks": len(complete_groups),
                  "ungraded_tasks": planned - len(complete_groups), "coverage_complete": complete,
                  "attempts_per_task": attempts_per_task,
                  "planned_attempts": planned * attempts_per_task,
                  "graded_attempts": sum(a.get("status") == "graded" for task in selected_tasks
                                          for a in task.get("attempts", [])),
                  "first_attempt_graded_tasks": first_graded,
                  "first_attempt_coverage_complete": first_graded == planned and planned > 0,
                  "pass_at_1": (sum(task_pass_rates) / planned) if complete else None,
                  "observed_pass_at_1_partial": (sum(task_pass_rates) / len(task_pass_rates)
                                                 if task_pass_rates and not complete else None),
                  "strict_passes": sum(a.get("official_score") == 1 for task in selected_tasks
                                        for a in task.get("attempts", []) if a.get("status") == "graded"),
                  "ungraded_attempts": sum(a.get("status") == "ungraded" for task in selected_tasks
                                            for a in task.get("attempts", [])),
                  "deferred_ready_attempts": sum(a.get("status") == "deferred_ready" for task in selected_tasks
                                                 for a in task.get("attempts", []))}
        if attempts_per_task == 3:
            result["pass_at_3"] = sum(any_pass_rates) / planned if complete else None
            result["pass_power_3"] = sum(all_pass_rates) / planned if complete else None
        else:
            result["pass_at_3"] = None
            result["pass_power_3"] = None
        return result

    overall = block(tasks)
    per_domain = {domain: block([task for task in tasks if task["domain"] == domain]) for domain in domains}
    full_domain = {domain: (len([task for task in tasks if task["domain"] == domain]) == 25 and
                            per_domain[domain]["first_attempt_coverage_complete"])
                   for domain in domains}
    overall["full_dataset_coverage_complete"] = (len(tasks) == 75 and
        set(domains) == set(CANONICAL_DOMAINS) and overall["first_attempt_coverage_complete"] and
        all(sum(task["domain"] == domain for task in tasks) == 25 for domain in CANONICAL_DOMAINS))
    for domain in domains:
        per_domain[domain]["full_domain_coverage_complete"] = full_domain[domain]

    return {"overall": overall, "per_domain": per_domain,
            "full_dataset_coverage_complete": overall["full_dataset_coverage_complete"],
            "full_domain_coverage_complete": full_domain,
            "selected_domain_keys": domains,
            "selected_task_count": len(tasks),
            "attempts_total": len(entries),
            "graded_attempts": sum(a.get("status") == "graded" for a in entries),
            "ungraded_attempts": sum(a.get("status") == "ungraded" for a in entries),
            "deferred_ready_attempts": sum(a.get("status") == "deferred_ready" for a in entries),
            "pending_attempts": sum(a.get("status") == "pending" for a in entries),
            "execution_stop_reason": manifest.get("execution_stop_reason"),
            "nonretryable_attempts": sum(a.get("status") in {"setup_failure", "interrupted", "needs_reconciliation"}
                                          for a in entries)}


def run_batch(config: BatchConfig, *, plan_only: bool = False,
              world: WorldAdapter | None = None,
              case_runner: Callable[..., dict[str, Any]] | None = None,
              source_identity: Callable[[], dict[str, Any]] = _source_identity) -> dict[str, Any]:
    dataset_root = Path(config.dataset_root).resolve(strict=True)
    run_root = Path(config.run_dir).resolve()
    runs_root = Path(__file__).resolve().parents[1] / "runs"
    if not run_root.is_relative_to(runs_root):
        raise BatchError("run_dir must be inside ignored HealthHarnessCodex/runs")
    tasks = enumerate_public_tasks(dataset_root, tuple(config.domains), tuple(config.task_ids))
    # These pins still govern the independent Codex patient worker. Claude
    # receives none of these instruction sources (see its frozen settings).
    pins = _instruction_pins(config)
    native_case_runner = case_runner is None
    explicit_executable = Path(config.codex_executable) != DEFAULT_CODEX_EXECUTABLE
    executable_hash_required = native_case_runner and not plan_only
    executable_hash = None
    if native_case_runner or explicit_executable:
        executable_hash = _codex_executable_sha256(config.codex_executable,
                                                   required=executable_hash_required)
    frozen = _frozen_config(config, tasks, pins, source_identity(), executable_hash)
    if plan_only:
        return {"status": "plan_only", "frozen_config": frozen,
                "tasks": [{"domain": t.domain, "task_id": t.task_id,
                           "instruction_sha256": t.instruction_sha256} for t in tasks],
                "no_inference_or_docker": True}
    if config.actor_backend == "claude-code" and native_case_runner and not frozen["claude_code"]["executable_sha256"]:
        raise BatchError("Claude executable is unavailable; supply --claude-executable with its absolute path")
    actor_secret = None
    if config.actor_backend == "claude-code-container":
        from .claude_code_container_actor import read_oauth_token
        # No token in config, manifest, arguments or plan. Fail before world start.
        actor_secret = read_oauth_token()
    manifest_path = run_root / "batch.manifest.json"
    lock = threading.RLock()
    resumed_existing = manifest_path.exists()
    if resumed_existing:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            raise BatchError("existing batch manifest is unreadable; preserving run directory") from None
        if not isinstance(manifest, dict) or _canonical(manifest.get("frozen_config")) != _canonical(frozen):
            raise BatchError("existing batch source, task hashes, native executable, model, budgets, or configuration differ; use a new run directory")
        expected_keys = {(t.domain, t.task_id) for t in tasks}
        existing_keys = {(t.get("domain"), t.get("task_id")) for t in manifest.get("tasks", []) if isinstance(t, dict)}
        if existing_keys != expected_keys:
            raise BatchError("existing batch task selection differs; use a new run directory")
        for task in manifest["tasks"]:
            for attempt in task.get("attempts", []):
                if attempt.get("status") == "running":
                    attempt.update(status="needs_reconciliation", reason="process_interrupted_during_attempt")
                elif attempt.get("status") in {"graded", "ungraded"}:
                    _verify_completed_attempt(run_root, task, attempt, frozen)
                elif attempt.get("status") == "deferred_ready":
                    _verify_deferred_attempt(run_root, task, attempt, frozen)
    else:
        if run_root.exists() and any(run_root.iterdir()):
            raise BatchError("run_dir is non-empty without a batch manifest; refusing to overwrite or adopt it")
        run_root.mkdir(parents=True, exist_ok=True)
        manifest = {"schema_version": 1, "created_at": _utc_now(), "updated_at": _utc_now(),
                    "frozen_config": frozen,
                    "tasks": [{"domain": task.domain, "task_id": task.task_id,
                               "instruction_sha256": task.instruction_sha256,
                               "attempts": [{"attempt": index, "status": "pending"}
                                            for index in range(1, config.attempts + 1)]}
                              for task in tasks]}
    batch_events_path = run_root / "batch.events.jsonl"
    if batch_events_path.is_symlink():
        raise BatchError("batch event log must not be a symlink")
    try:
        batch_events_path.touch(exist_ok=True)
    except OSError:
        raise BatchError("batch event log cannot be created") from None
    batch_event_lock = threading.RLock()

    def emit(event: str, *, task_id: str | None = None, domain: str | None = None,
             attempt: int | None = None, **fields: Any) -> str:
        return _append_batch_event(batch_events_path, batch_event_lock, event,
                                   task_id=task_id, domain=domain, attempt=attempt, **fields)

    if world is None:
        world = DockerWorldAdapter(config.docker_executable, config.benchmark_env_file,
                                   config.allow_benchmark_network,
                                   **({"actor_backend": config.actor_backend} if config.actor_backend == "claude-code-container" else {}))
    if case_runner is None and config.actor_backend == "harness":
        from .standalone import run_case as case_runner
    budgets = dict(config.budgets or DEFAULT_LIMITS)

    def save() -> None:
        with lock:
            manifest["updated_at"] = _utc_now()
            manifest["summary"] = _summary(manifest)
            _atomic_json(manifest_path, manifest)

    save()
    task_by_key = {(t.domain, t.task_id): t for t in tasks}
    jobs = [(task, index) for task in manifest["tasks"] for index in range(1, config.attempts + 1)
            if task["attempts"][index - 1].get("status") == "pending"]
    progress = _batch_progress_fields(manifest)
    emit("batch_started", status="started", model=config.model,
         reasoning_effort=config.reasoning_effort, concurrency=config.concurrency,
         selected_tasks=len(tasks), grading_status="deferred" if config.defer_grading else "inline")
    emit("resume_state", status="resumed" if resumed_existing else "started",
         selected_tasks=len(tasks), settled=progress["settled_tasks"],
         pending=progress["pending_attempts"], saved=progress["saved_snapshots"],
         failed=progress["failed_attempts"], ungraded_attempts=progress["ungraded_attempts"],
         reconciliation=progress["reconciliation_attempts"])
    task_index_by_key = {(task.domain, task.task_id): index for index, task in enumerate(tasks, start=1)}
    stop_scheduling = threading.Event()
    scheduling_lock = threading.Lock()
    pre_model_setup_failure_streak = 0

    def execute(job: tuple[dict[str, Any], int]) -> None:
        nonlocal pre_model_setup_failure_streak
        task_record, attempt_number = job
        task = task_by_key[(task_record["domain"], task_record["task_id"])]
        attempt_record = task_record["attempts"][attempt_number - 1]
        attempt_dir = run_root / task.domain / task.task_id / f"attempt-{attempt_number}"
        container_logs = attempt_dir / "container_logs"
        container_name = _container_name(run_root, task, attempt_number)
        task_index = task_index_by_key[(task.domain, task.task_id)]
        started = _utc_now()
        started_monotonic = time.monotonic()
        with scheduling_lock:
            if stop_scheduling.is_set():
                return
            with lock:
                attempt_record.update(status="running", started_at=started,
                                      container_name=container_name, attempt_dir=attempt_dir.relative_to(run_root).as_posix())
                save()
        emit("task_started", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
             status="started", task_index=task_index, total_tasks=len(tasks))
        container: str | None = None
        simulator_worker = None
        simulator_worker_summary: dict[str, Any] | None = None
        simulator_worker_unresolved = False
        actor_invocation_started = False
        deferred_snapshot_valid = False
        actor_finished_logged = False
        actor_started_monotonic: float | None = None
        stop_issue: str | None = None
        stage = "source validation"
        try:
            current_source = source_identity()
            if (current_source["source_fingerprint"] != frozen["source_fingerprint"] or
                    current_source.get('retrieval_runtime')!=frozen.get('retrieval_runtime')):
                raise BatchError("actor source changed after batch freeze")
            if _sha256_file(task.task_dir / "instruction.md") != task.instruction_sha256:
                raise BatchError("public task instruction changed after batch freeze")
            stage = "world startup"
            if config.simulator_backend in SPOOL_BACKENDS:
                attempt_dir.mkdir(parents=True, exist_ok=True)
                simulator_spool = attempt_dir / "simulator-spool"
                simulator_spool.mkdir(mode=0o700, exist_ok=False)
            emit("world_starting", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="starting", stage="fresh Docker world startup", task_index=task_index,
                 total_tasks=len(tasks))
            if config.simulator_backend in SPOOL_BACKENDS and isinstance(world, DockerWorldAdapter):
                patient = frozen["simulator"]
                claude_patient = config.simulator_backend == "claude-cli"
                patient_kwargs = ({"simulator_model": patient["model"]} if claude_patient else {})
                if claude_patient:
                    from .claude_cli_patient import provenance
                    current = provenance(patient["executable"], config.simulator_claude_model)
                    if any(patient.get(k) != v for k, v in current.items()):
                        raise BatchError("Claude patient configuration changed after freeze")
                container = world.start(task, container_name, container_logs,
                                        simulator_backend=config.simulator_backend, simulator_spool=simulator_spool,
                                        simulator_effort=patient["reasoning_effort"], **patient_kwargs)
                from .simulator_worker import SimulatorWorker
                simulator_worker = SimulatorWorker(
                    simulator_spool, SIMULATOR_KIND_BY_DOMAIN[task.domain],
                    patient["executable"] if claude_patient else config.codex_executable,
                    max_calls=config.simulator_max_model_calls,
                    max_total_chars_per_world=config.simulator_max_total_chars,
                    max_world_deadline_seconds=config.simulator_world_deadline_seconds,
                    request_timeout=config.simulator_request_timeout_seconds,
                    allowed_instruction_sources=pins,
                    backend_effort=patient["reasoning_effort"],
                    **({"backend": "claude-cli", "backend_model": patient["model"]} if claude_patient else {}),
                )
                simulator_worker.start()
                world.start_simulator_bridge(container, task,
                                              request_timeout=config.simulator_request_timeout_seconds,
                                              simulator_effort=patient["reasoning_effort"], **patient_kwargs)
            else:
                if config.simulator_backend in SPOOL_BACKENDS:
                    raise BatchError("the experimental simulator backend requires the native Docker world adapter")
                container = world.start(task, container_name, container_logs)
            emit("world_started", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="started", elapsed_seconds=time.monotonic() - started_monotonic,
                 task_index=task_index, total_tasks=len(tasks))
            preflight_timeout = min(120, config.timeout)
            stage = "world preflight"
            preflight_started = time.monotonic()
            emit("world_waiting", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="waiting", stage="runtime health and actor tool preflight",
                 elapsed_seconds=0.0, timeout_seconds=preflight_timeout,
                 task_index=task_index, total_tasks=len(tasks))
            if isinstance(world, DockerWorldAdapter):
                tool_names = world.preflight(container, task, preflight_timeout,
                                             attempt_number=attempt_number, event_logger=emit)
            else:
                tool_names = world.preflight(container, task, preflight_timeout)
            emit("world_ready", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="ready", elapsed_seconds=time.monotonic() - preflight_started,
                 timeout_seconds=preflight_timeout, tool_count=len(tool_names),
                 task_index=task_index, total_tasks=len(tasks))
            current_source = source_identity()
            if (current_source["source_fingerprint"] != frozen["source_fingerprint"] or current_source.get("source_commit") != frozen.get("source_commit") or
                    current_source.get('retrieval_runtime')!=frozen.get('retrieval_runtime')):
                raise BatchError("actor source changed during world preflight")
            if _sha256_file(task.task_dir / "instruction.md") != task.instruction_sha256:
                raise BatchError("public task instruction changed before model execution")
            attempt_dir.mkdir(parents=True, exist_ok=True)
            actor_invocation_started = True
            stage = "actor workflow"
            actor_started_monotonic = time.monotonic()
            emit("actor_starting", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="starting", stage="Claude Code actor" if config.actor_backend.startswith("claude-code") else "Codex actor workflow",
                 model=config.claude_model if config.actor_backend.startswith("claude-code") else config.model,
                 task_index=task_index, total_tasks=len(tasks))
            if config.actor_backend == "claude-code-container":
                from .claude_code_container_actor import run_case as container_runner
                def actor_progress(event, **fields):
                    emit(event, task_id=task.task_id, domain=task.domain, attempt=attempt_number, **fields)
                report = (case_runner or container_runner)(container, task.task_dir, attempt_dir,
                    config, frozen, actor_progress, oauth_token=actor_secret)
            elif config.actor_backend == "claude-code":
                from .claude_code_actor import run_case as claude_runner
                selected_claude = Path(frozen["claude_code"]["executable"])
                if native_case_runner and _sha256_file(selected_claude) != frozen["claude_code"]["executable_sha256"]:
                    raise BatchError("Claude executable changed after batch freeze")
                def actor_progress(event, **fields):
                    emit(event, task_id=task.task_id, domain=task.domain, attempt=attempt_number, **fields)
                report = (case_runner or claude_runner)(container, task.task_dir, attempt_dir,
                                                       config, frozen, actor_progress)
            else:
                report = case_runner(container, task.task_dir, attempt_dir, config.codex_executable, pins,
                                 max_model_calls=budgets["max_model_calls"],
                                 max_tool_calls=budgets["max_tool_calls"],
                                 max_context_chars=budgets["max_context_chars"], timeout=config.timeout,
                                 active_timeout=config.active_timeout,
                                 model_name=config.model,
                                 composition=config.composition,recovery_helper_policy=config.recovery_helper_policy, allow_case_subject_namespace=True,
                                 domain=task.domain, attempt_number=attempt_number)
            if simulator_worker is not None:
                summary = simulator_worker.stop()
                simulator_worker = None
                simulator_worker_summary = asdict(summary)
                attempt_record["simulator"] = {
                    **simulator_worker_summary,
                    "backend": config.simulator_backend,
                    "model": frozen["simulator"]["model"],
                    "reasoning_effort": frozen["simulator"]["reasoning_effort"],
                    "official_grade_eligible": False,
                    "spool_path": simulator_spool.relative_to(run_root).as_posix(),
                }
                save()
                emit("simulator_worker_stopped", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                     status="settled" if summary.settled else "unresolved",
                     model_calls=summary.completed_calls, elapsed_seconds=summary.elapsed_seconds)
                if not summary.settled:
                    simulator_worker_unresolved = True
                    raise BatchError("experimental simulator worker did not settle all requests; preserving world")
            local_result = report.get("local_harness", {}) if isinstance(report, dict) else {}
            eval_result = _evaluation_summary(attempt_dir)
            emit("actor_finished", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 execution_state=(local_result.get('execution_assessment') or {}).get('execution_state'),
                 goal_status=(local_result.get('execution_assessment') or {}).get('requested_outcome',{}).get('status'),
                 status="finished", harness_status=_safe_harness_status(
                     local_result.get("status", eval_result.get("harness_status"))),
                 model_calls=local_result.get("model_calls", eval_result.get("model_calls")),
                 tool_calls=local_result.get("tool_calls", eval_result.get("tool_calls")),
                 turns=local_result.get("num_turns"),
                 elapsed_seconds=time.monotonic() - actor_started_monotonic,
                 task_index=task_index, total_tasks=len(tasks))
            actor_finished_logged = True
            if not _evaluation_matches_frozen(attempt_dir, frozen):
                raise BatchError("standalone evaluation provenance differs from frozen batch source")
            current_source = source_identity()
            if (current_source["source_fingerprint"] != frozen["source_fingerprint"] or current_source.get("source_commit") != frozen.get("source_commit") or
                    current_source.get('retrieval_runtime')!=frozen.get('retrieval_runtime')):
                raise BatchError("actor source changed during the standalone attempt; preserving outputs")
            _snapshot_sqlite(attempt_dir / "state.sqlite", attempt_dir / "state.snapshot.sqlite")
            if config.defer_grading:
                stage = "actor export and deferred snapshot"
                snapshot_started = time.monotonic()
                emit("snapshot_starting", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                     status="starting", stage="verifier export and actor log copy",
                     task_index=task_index, total_tasks=len(tasks))
                exported = world.export_state(container, min(120, config.timeout))
                snapshot_receipt = _capture_deferred_snapshot(attempt_dir, task, frozen, exported)
                with lock:
                    attempt_record.update(
                        grading_status="pending", official_score=None,
                        deferred_snapshot=snapshot_receipt,
                        local_status=(report.get("local_harness", {}).get("status")
                                      if isinstance(report, dict) else None),
                        actor_tool_names=tool_names,
                        actor_finished_at=_utc_now(),
                    )
                    save()
                _verify_deferred_snapshot(attempt_dir, task_record, attempt_record, frozen)
                deferred_snapshot_valid = True
                emit("snapshot_saved", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                     status="saved", saved=1, total=snapshot_receipt.get("file_count"),
                     elapsed_seconds=time.monotonic() - snapshot_started,
                     task_index=task_index, total_tasks=len(tasks))
                return
            stage = "official grading"
            grading_started = time.monotonic()
            emit("grading_started", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="starting", stage="official verifier", grading_status="running",
                 task_index=task_index, total_tasks=len(tasks))
            grade_output = None
            grade_launches = []
            for grade_number in range(1, 4):
                output_name = f"official_{grade_number}"
                grade_output = world.grade(container, task, output_name, 130)
                grade_launches.append({"output": output_name,
                                       "returncode": grade_output.get("returncode"),
                                       "timed_out": grade_output.get("timed_out"),
                                       "export_timeout": grade_output.get("export_timeout")})
                if (container_logs / output_name / "scorecard.json").is_file():
                    break
                if grade_output.get("export_timeout") is not True or grade_number == 3:
                    break
            selected_output = grade_launches[-1]["output"] if grade_launches else "official_1"
            grade_status, grade = _official_grade(container_logs, selected_output,
                                                  grade_launches[-1].get("returncode") if grade_launches else None)
            emit("grading_finished", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status=grade_status, grading_status="complete" if grade_status == "graded" else "failed",
                 elapsed_seconds=time.monotonic() - grading_started,
                 task_index=task_index, total_tasks=len(tasks))
            official_receipt = {"schema_version": 1, "task_id": task.task_id, "domain": task.domain,
                                "attempt": attempt_number, "container_identity": container,
                                "source_commit": frozen["source_commit"],
                                "source_fingerprint": frozen["source_fingerprint"],
                                "grader_runs": grade_launches, "selected_output": selected_output,
                                "status": grade_status,
                                "actor_artifacts": {name: {"sha256": _sha256_file(attempt_dir / name),
                                                            "bytes": (attempt_dir / name).stat().st_size}
                                                    for name in ("run.result.json", "evaluation.json", "state.snapshot.sqlite")
                                                    if (attempt_dir / name).is_file()},
                                "artifacts": {name: {"sha256": _sha256_file(path), "bytes": path.stat().st_size}
                                              for name, path in _official_paths(container_logs, selected_output).items()
                                              if path.is_file()}}
            _atomic_json(attempt_dir / "official-evaluation-receipt.json", official_receipt)
            with lock:
                attempt_record.update(status=grade_status, finished_at=_utc_now(),
                                      local_status=(report.get("local_harness", {}).get("status")
                                                    if isinstance(report, dict) else None),
                                      actor_tool_names=tool_names, grade=grade,
                                      official_score=grade.get("reward") if grade_status == "graded" else None,
                                      receipt_sha256=_sha256_file(attempt_dir / "official-evaluation-receipt.json"))
                save()
        except Exception as exc:
            known_pre_model_setup_failure = (_is_pre_model_setup_failure(attempt_dir)
                                             if actor_invocation_started else False)
            if known_pre_model_setup_failure:
                stage = "actor pre-model setup"
            if actor_invocation_started and not actor_finished_logged:
                actor_info = _evaluation_summary(attempt_dir)
                emit("actor_finished", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                     status="failed", harness_status=_safe_harness_status(
                         actor_info.get("harness_status", "setup_failure" if known_pre_model_setup_failure else "unknown")),
                     model_calls=actor_info.get("model_calls"), tool_calls=actor_info.get("tool_calls"),
                     elapsed_seconds=(time.monotonic() - actor_started_monotonic
                                      if actor_started_monotonic is not None else 0.0),
                     task_index=task_index, total_tasks=len(tasks))
                actor_finished_logged = True
            emit("stage_error", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="failed", stage=stage, error_type=type(exc).__name__,
                 task_index=task_index, total_tasks=len(tasks))
            diagnostic_saved=_save_stage_diagnostic(attempt_dir,stage,exc)
            with lock:
                setup_failure = (not actor_invocation_started or _is_setup_failure_without_actions(attempt_dir))
                attempt_record.update(status="setup_failure" if setup_failure else "interrupted",
                                      finished_at=_utc_now(),
                                      reason_type=type(exc).__name__,
                                      private_stage_diagnostic_saved=diagnostic_saved,
                                      recovery="manual reconciliation required; attempt will not be replayed")
                save()
        finally:
            if simulator_worker is not None:
                try:
                    summary = simulator_worker.stop()
                    simulator_worker = None
                    simulator_worker_summary = asdict(summary)
                    attempt_record["simulator"] = {
                        **simulator_worker_summary, "backend": config.simulator_backend,
                        "model": frozen["simulator"]["model"],
                        "reasoning_effort": frozen["simulator"]["reasoning_effort"],
                        "official_grade_eligible": False,
                        "spool_path": simulator_spool.relative_to(run_root).as_posix(),
                    }
                    save()
                    if not summary.settled:
                        simulator_worker_unresolved = True
                        stop_issue = "simulator_worker_unresolved"
                except Exception as exc:
                    attempt_record["simulator"] = {"backend": config.simulator_backend, "status": "stop_error",
                                                     "error_type": type(exc).__name__,
                                                     "official_grade_eligible": False}
                    save()
                    simulator_worker_unresolved = True
                    stop_issue = "simulator_worker_stop_failed"
            known_pre_model_setup_failure = _is_pre_model_setup_failure(attempt_dir) if actor_invocation_started else False
            preserve_world_for_reconciliation = (
                simulator_worker_unresolved
                or (config.defer_grading and actor_invocation_started and not deferred_snapshot_valid
                    and not known_pre_model_setup_failure)
            )
            if container is not None and not preserve_world_for_reconciliation:
                try:
                    stop_issue = world.stop(container)
                except Exception as exc:
                    stop_issue = f"stop_failed:{type(exc).__name__}"
                with lock:
                    attempt_record["container_stopped"] = stop_issue is None
                    if stop_issue is not None:
                        attempt_record["container_stop_issue"] = stop_issue
                    save()
                if stop_issue is None:
                    emit("world_stopped", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                         status="stopped", elapsed_seconds=time.monotonic() - started_monotonic,
                         task_index=task_index, total_tasks=len(tasks))
                else:
                    emit("stage_error", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                         status="failed", stage="world cleanup", error_type="WorldStopError",
                         task_index=task_index, total_tasks=len(tasks))
            elif container is not None:
                with lock:
                    attempt_record.update(container_stopped=False,
                                          world_preserved_for_reconciliation=True)
                    save()
                emit("world_preserved", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                     status="preserved", stage="deferred snapshot could not be verified",
                     task_index=task_index, total_tasks=len(tasks))
            if config.defer_grading:
                with lock:
                    if deferred_snapshot_valid and attempt_record.get("deferred_snapshot"):
                        if container is not None and stop_issue is None:
                            attempt_record.update(status="deferred_ready", finished_at=_utc_now(),
                                                  grading_status="pending")
                        else:
                            attempt_record.update(status="needs_reconciliation", finished_at=_utc_now(),
                                                  grading_status="not_ready",
                                                  reason="snapshot_captured_but_world_not_confirmed_stopped")
                    elif actor_invocation_started and not known_pre_model_setup_failure:
                        attempt_record.update(status="needs_reconciliation", finished_at=_utc_now(),
                                              grading_status="not_ready", official_score=None,
                                              container_stopped=False,
                                              world_preserved_for_reconciliation=container is not None,
                                              reason="deferred_snapshot_failed_actor_world_preserved_for_manual_reconciliation")
                        save()
                    elif known_pre_model_setup_failure:
                        attempt_record.update(status="setup_failure", finished_at=_utc_now(),
                                              grading_status="not_ready", official_score=None,
                                              reason="pre_model_setup_failure_zero_model_calls")
                    save()
            with scheduling_lock:
                if known_pre_model_setup_failure:
                    pre_model_setup_failure_streak += 1
                else:
                    pre_model_setup_failure_streak = 0
                if (pre_model_setup_failure_streak >= PRE_MODEL_SETUP_FAILURE_STOP_THRESHOLD and
                        not stop_scheduling.is_set()):
                    stop_scheduling.set()
                    with lock:
                        manifest["execution_stop_reason"] = {
                            "kind": "consecutive_pre_model_setup_failures",
                            "stage": "actor_pre_model_setup",
                            "threshold": PRE_MODEL_SETUP_FAILURE_STOP_THRESHOLD,
                            "consecutive_failures": pre_model_setup_failure_streak,
                            "stopped_at": _utc_now(),
                        }
                        save()
                    emit("batch_stopped_early", status="stopped_early",
                         stage="actor pre-model setup", failed=pre_model_setup_failure_streak,
                         pending=_batch_progress_fields(manifest)["pending_attempts"])
            with lock:
                settled_status = attempt_record.get("status", "unknown")
                save()
                progress = _batch_progress_fields(manifest)
            emit("task_settled", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status=settled_status, elapsed_seconds=time.monotonic() - started_monotonic,
                 task_index=task_index, total_tasks=len(tasks))
            emit("batch_progress", task_id=task.task_id, domain=task.domain, attempt=attempt_number,
                 status="running", settled=progress["settled_tasks"],
                 selected_tasks=progress["selected_tasks"], active=progress["active_attempts"],
                 pending=progress["pending_attempts"], saved=progress["saved_snapshots"],
                 failed=progress["failed_attempts"], ungraded_attempts=progress["ungraded_attempts"],
                 reconciliation=progress["reconciliation_attempts"])

    with ThreadPoolExecutor(max_workers=config.concurrency, thread_name_prefix="chi-batch") as pool:
        futures = [pool.submit(execute, job) for job in jobs]
        for future in as_completed(futures):
            future.result()
    save()
    if manifest["summary"]["full_dataset_coverage_complete"]:
        _write_grade_csv(run_root / "kaggle_submission.csv", manifest["tasks"])
    else:
        _write_grade_csv(run_root / "graded_results.partial.csv", manifest["tasks"])
    final_progress = _batch_progress_fields(manifest)
    emit("batch_stopped_early" if manifest.get("execution_stop_reason") else "batch_finished",
         status="stopped_early" if manifest.get("execution_stop_reason") else "finished",
         stage=(manifest.get("execution_stop_reason") or {}).get("stage", "batch complete"),
         grading_status="deferred" if config.defer_grading else "complete",
         settled=final_progress["settled_tasks"], selected_tasks=final_progress["selected_tasks"],
         active=final_progress["active_attempts"], pending=final_progress["pending_attempts"],
         saved=final_progress["saved_snapshots"], failed=final_progress["failed_attempts"],
         ungraded_attempts=final_progress["ungraded_attempts"],
         reconciliation=final_progress["reconciliation_attempts"])
    return manifest


def _official_paths(logs_dir: Path, output_name: str) -> dict[str, Path]:
    base = logs_dir / output_name
    return {"reward": base / "reward.json", "scorecard": base / "scorecard.json",
            "exported_state": base / "exported_state.json", "verifier_context": base / "verifier_context.json"}


def _verify_completed_attempt(run_root: Path, task_record: dict[str, Any], attempt_record: dict[str, Any],
                              frozen: dict[str, Any]) -> None:
    relative = attempt_record.get("attempt_dir")
    if not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise BatchError("completed attempt path is invalid; preserving batch")
    attempt_dir = run_root / Path(relative)
    if attempt_dir.is_symlink() or not attempt_dir.resolve(strict=True).is_relative_to(run_root.resolve()):
        raise BatchError("completed attempt escaped batch root; preserving batch")
    receipt_path = attempt_dir / "official-evaluation-receipt.json"
    if not receipt_path.is_file() or receipt_path.is_symlink() or _sha256_file(receipt_path) != attempt_record.get("receipt_sha256"):
        raise BatchError("completed attempt receipt changed or is missing; preserving batch")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise BatchError("completed attempt receipt is invalid; preserving batch") from None
    if (receipt.get("task_id") != task_record.get("task_id") or
            receipt.get("domain") != task_record.get("domain") or
            receipt.get("source_commit") != frozen.get("source_commit") or
            receipt.get("source_fingerprint") != frozen.get("source_fingerprint") or
            receipt.get("status") != attempt_record.get("status")):
        raise BatchError("completed attempt receipt no longer matches frozen configuration")
    base = attempt_dir / "container_logs" / receipt.get("selected_output", "")
    if base.is_symlink() or not base.resolve(strict=True).is_relative_to((attempt_dir / "container_logs").resolve()):
        raise BatchError("completed verifier artifacts escaped the attempt directory")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict):
        raise BatchError("completed attempt receipt has no artifact hashes")
    official_file_names = {"reward": "reward.json", "scorecard": "scorecard.json",
                           "exported_state": "exported_state.json", "verifier_context": "verifier_context.json"}
    for name, record in artifacts.items():
        if name not in official_file_names:
            raise BatchError("completed attempt receipt names an unexpected official artifact")
        path = base / official_file_names[name]
        if (not isinstance(record, dict) or path.is_symlink() or not path.is_file() or
                path.stat().st_size != record.get("bytes") or _sha256_file(path) != record.get("sha256")):
            raise BatchError("completed official artifact changed; preserving batch")
    actor_artifacts = receipt.get("actor_artifacts")
    if not isinstance(actor_artifacts, dict):
        raise BatchError("completed attempt receipt has no actor artifact hashes")
    for name, record in actor_artifacts.items():
        if name not in {"run.result.json", "evaluation.json", "state.snapshot.sqlite"}:
            raise BatchError("completed receipt names an unexpected actor artifact")
        path = attempt_dir / name
        if (not isinstance(record, dict) or path.is_symlink() or not path.is_file() or
                path.stat().st_size != record.get("bytes") or _sha256_file(path) != record.get("sha256")):
            raise BatchError("completed actor artifact changed; preserving batch")


def _evaluation_matches_frozen(attempt_dir: Path, frozen: dict[str, Any]) -> bool:
    path = attempt_dir / "evaluation.json"
    if not path.is_file() or path.is_symlink():
        return False
    try:
        evaluation = json.loads(path.read_text(encoding="utf-8"))
        metadata = evaluation.get("metadata", {})
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return False
    return (metadata.get("source_fingerprint") == frozen.get("source_fingerprint") and
            metadata.get('retrieval_runtime')==frozen.get('retrieval_runtime') and
            metadata.get("source_commit") == frozen.get("source_commit"))


def _is_setup_failure_without_actions(attempt_dir: Path) -> bool:
    evaluation_path = attempt_dir / "evaluation.json"
    if not evaluation_path.is_file():
        return False
    try:
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return False
    if evaluation.get("harness_status") != "setup_failure":
        return False
    state_path = attempt_dir / "state.sqlite"
    if not state_path.exists():
        return True
    try:
        uri = "file:" + state_path.resolve().as_posix().replace("?", "%3F") + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        try:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "actions" not in tables:
                return True
            return connection.execute("SELECT COUNT(*) FROM actions").fetchone()[0] == 0
        finally:
            connection.close()
    except (sqlite3.Error, OSError):
        return False


def _is_pre_model_setup_failure(attempt_dir: Path) -> bool:
    """Count only explicit zero-model setup failures with no journaled writes."""
    path = attempt_dir / "evaluation.json"
    if path.is_symlink() or not path.is_file():
        return False
    try:
        evaluation = json.loads(path.read_text(encoding="utf-8"))
        metrics = evaluation.get("metrics")
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return False
    model_calls = metrics.get("model_calls") if isinstance(metrics, dict) else None
    return (evaluation.get("harness_status") == "setup_failure" and
            isinstance(model_calls, int) and not isinstance(model_calls, bool) and model_calls == 0 and
            _is_setup_failure_without_actions(attempt_dir))


def _tree_inventory(root: Path) -> dict[str, Any]:
    """Hash a private snapshot tree without printing or loading file payloads."""
    files: list[dict[str, Any]] = []
    directories: list[str] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative == "snapshot.manifest.json":
            continue
        if path.is_symlink():
            raise BatchError("deferred snapshot contains a symlink")
        if path.is_dir():
            directories.append(relative)
        elif path.is_file():
            files.append({"path": relative, "bytes": path.stat().st_size, "sha256": _sha256_file(path)})
        else:
            raise BatchError("deferred snapshot contains a non-regular entry")
    return {"directories": directories, "files": files}


def _capture_deferred_snapshot(attempt_dir: Path, task: PublicTask, frozen: dict[str, Any],
                               exported: dict[str, Any]) -> dict[str, Any]:
    """Atomically freeze the actor logs, provenance files and actual /export."""
    destination = attempt_dir / "deferred_snapshot"
    if destination.exists() or destination.is_symlink():
        raise BatchError("deferred snapshot already exists; preserving it")
    encoded = json.dumps(exported, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > 100 * 1024 * 1024:
        raise BatchError("verifier export exceeds deferred snapshot size limit")
    source_logs = attempt_dir / "container_logs"
    if source_logs.is_symlink() or not source_logs.is_dir():
        raise BatchError("actor log tree is missing or linked")
    source_inventory_before = _tree_inventory(source_logs)
    staging = attempt_dir / f".deferred_snapshot-{os.getpid()}-{threading.get_ident()}"
    if staging.exists() or staging.is_symlink():
        raise BatchError("deferred snapshot staging path already exists")
    staging.mkdir()
    try:
        shutil.copytree(source_logs, staging / "logs", dirs_exist_ok=True, symlinks=False)
        actor_files: list[dict[str, Any]] = []
        required_actor_files = {"run.result.json", "evaluation.json", "state.snapshot.sqlite"}
        if any(not (attempt_dir / name).is_file() or (attempt_dir / name).is_symlink()
               for name in required_actor_files):
            raise BatchError("required successful actor artifacts are missing or linked")
        names = ["run.result.json", "evaluation.json", "state.sqlite", "state.snapshot.sqlite"]
        if frozen.get("actor_backend") in {"claude-code", "claude-code-container"}:
            names += ["claude-stream.private.jsonl", "claude-stderr.private.log",
                      "claude-mcp.private.jsonl", "claude-progress.json", "claude-mcp.json"]
        for name in names:
            source = attempt_dir / name
            if source.is_symlink():
                raise BatchError("actor artifact is linked")
            if source.is_file():
                target = staging / "actor" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                actor_files.append({"path": f"actor/{name}", "bytes": target.stat().st_size,
                                    "sha256": _sha256_file(target)})
        source_inventory_after = _tree_inventory(source_logs)
        copied_logs_inventory = _tree_inventory(staging / "logs")
        if source_inventory_before != source_inventory_after or source_inventory_after != copied_logs_inventory:
            raise BatchError("actor log tree changed while the deferred snapshot was copied")
        export_path = staging / "exported_state.json"
        export_path.write_bytes(encoded)
        inventory = _tree_inventory(staging)
        metadata = {
            "schema_version": 1,
            "created_at": _utc_now(),
            "transport": "actual_verifier_http_export",
            "task_id": task.task_id,
            "domain": task.domain,
            "task_instruction_sha256": task.instruction_sha256,
            "source_commit": frozen.get("source_commit"),
            "source_fingerprint": frozen.get("source_fingerprint"),
            "model": frozen.get("model"),
            "reasoning_effort": frozen.get("reasoning_effort"),
            "actor_files": actor_files,
            "inventory": inventory,
        }
        _atomic_json(staging / "snapshot.manifest.json", metadata)
        staging.replace(destination)
        return {"directory": "deferred_snapshot", "manifest_sha256": _sha256_file(destination / "snapshot.manifest.json"),
                "inventory_sha256": _sha256_bytes(_canonical(inventory).encode("utf-8")),
                "file_count": len(inventory["files"]), "directory_count": len(inventory["directories"])}
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def _verify_deferred_snapshot(attempt_dir: Path, task_record: dict[str, Any],
                              attempt_record: dict[str, Any], frozen: dict[str, Any]) -> Path:
    snapshot = attempt_dir / "deferred_snapshot"
    manifest_path = snapshot / "snapshot.manifest.json"
    if snapshot.is_symlink() or not snapshot.is_dir() or manifest_path.is_symlink() or not manifest_path.is_file():
        raise BatchError("deferred snapshot is missing or linked")
    try:
        metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise BatchError("deferred snapshot manifest is invalid") from None
    if (not isinstance(metadata, dict) or metadata.get("schema_version") != 1 or
            metadata.get("task_id") != task_record.get("task_id") or
            metadata.get("domain") != task_record.get("domain") or
            metadata.get("task_instruction_sha256") != task_record.get("instruction_sha256") or
            metadata.get("source_commit") != frozen.get("source_commit") or
            metadata.get("source_fingerprint") != frozen.get("source_fingerprint") or
            metadata.get("transport") != "actual_verifier_http_export"):
        raise BatchError("deferred snapshot provenance differs from frozen actor")
    recorded = metadata.get("inventory")
    current = _tree_inventory(snapshot)
    if not isinstance(recorded, dict) or _canonical(recorded) != _canonical(current):
        raise BatchError("deferred snapshot inventory changed; preserving data")
    pointer = attempt_record.get("deferred_snapshot")
    if (not isinstance(pointer, dict) or
            pointer.get("manifest_sha256") != _sha256_file(manifest_path) or
            pointer.get("inventory_sha256") != _sha256_bytes(_canonical(current).encode("utf-8"))):
        raise BatchError("deferred snapshot receipt changed or is missing")
    export_path = snapshot / "exported_state.json"
    try:
        exported = json.loads(export_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise BatchError("deferred verifier export is invalid") from None
    if not isinstance(exported, dict):
        raise BatchError("deferred verifier export is not an object")
    return snapshot


def _verify_deferred_attempt(run_root: Path, task_record: dict[str, Any],
                             attempt_record: dict[str, Any], frozen: dict[str, Any]) -> Path:
    relative = attempt_record.get("attempt_dir")
    if not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise BatchError("deferred attempt path is invalid; preserving batch")
    attempt_dir = run_root / Path(relative)
    if attempt_dir.is_symlink() or not attempt_dir.resolve(strict=True).is_relative_to(run_root.resolve()):
        raise BatchError("deferred attempt escaped batch root; preserving batch")
    if attempt_record.get("status") != "deferred_ready" or attempt_record.get("grading_status") != "pending":
        raise BatchError("deferred attempt is not ready for later grading")
    if attempt_record.get("container_stopped") is not True:
        raise BatchError("deferred attempt world was not confirmed stopped")
    if not isinstance(attempt_record.get("container_name"), str):
        raise BatchError("deferred attempt has no recorded world identity")
    return _verify_deferred_snapshot(attempt_dir, task_record, attempt_record, frozen)


def _cli_config(args: argparse.Namespace) -> BatchConfig:
    return BatchConfig(dataset_root=args.dataset_root.resolve(strict=True), run_dir=args.run_dir,
                       actor_backend=args.actor_backend, claude_model=args.claude_model,
                       claude_effort=args.claude_effort, claude_executable=args.claude_executable,
                       claude_timeout_seconds=args.claude_timeout_seconds,
                       domains=tuple(args.domains or CANONICAL_DOMAINS), task_ids=tuple(args.task_id),
                       attempts=args.attempts, concurrency=args.concurrency, timeout=args.timeout,
                       active_timeout=args.active_timeout,
                       model=args.model,
                       composition=args.composition,
                       recovery_helper_policy=args.recovery_helper_policy,
                       codex_executable=args.codex_executable, docker_executable=args.docker,
                       benchmark_env_file=args.benchmark_env_file,
                       allow_benchmark_network=args.allow_benchmark_network,
                       # CLI batch runs finish every actor before grading. Programmatic
                       # callers may still select the legacy inline behavior explicitly.
                       defer_grading=True,
                       simulator_backend=args.simulator_backend,
                       simulator_claude_model=args.simulator_claude_model,
                       simulator_claude_executable=args.simulator_claude_executable,
                       simulator_max_model_calls=args.simulator_max_model_calls,
                       simulator_max_total_chars=args.simulator_max_total_chars,
                       simulator_world_deadline_seconds=args.simulator_world_deadline_seconds,
                       simulator_request_timeout_seconds=args.simulator_request_timeout_seconds,
                       simulator_effort=args.simulator_effort,
                       budgets={"max_model_calls": args.max_model_calls, "max_tool_calls": args.max_tool_calls,
                                "max_context_chars": args.max_context_chars, "max_output_tokens": DEFAULT_LIMITS["max_output_tokens"]})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fresh-world native batch runner for public χ-Bench tasks")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--domains", nargs="+", choices=tuple(CANONICAL_DOMAINS))
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--actor-backend", choices=("harness", "claude-code", "claude-code-container"), default="harness")
    parser.add_argument("--claude-model", default="claude-sonnet-5-5")
    parser.add_argument("--claude-effort", choices=("low", "medium", "high", "max"), default="high")
    parser.add_argument("--claude-executable", default="claude")
    parser.add_argument("--claude-timeout-seconds", type=int, default=1800)
    parser.add_argument('--model',default=DEFAULT_MODEL,
                        help='case-worker Codex model; independent of the fixed experimental patient model')
    parser.add_argument("--composition", choices=("combined","helpers","team"), default="helpers",
                        help="case owner with optional delegated helper jobs (default), single combined owner, or sequential multiple jobs")
    parser.add_argument('--recovery-helper-policy',choices=('off','auto'),default='auto',
                        help='scoped CM conversation worker and bounded recovery audits; disabled in combined mode')
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="model setup/silence timeout; hard request timeout when --active-timeout is omitted")
    parser.add_argument('--active-timeout', type=int,
                        help='total model request cap while generation is active; --timeout remains the silence/setup cap')
    parser.add_argument("--max-model-calls", type=int, default=DEFAULT_LIMITS["max_model_calls"])
    parser.add_argument("--max-tool-calls", type=int, default=DEFAULT_LIMITS["max_tool_calls"])
    parser.add_argument("--max-context-chars", type=int, default=DEFAULT_LIMITS["max_context_chars"], help="Working-context character cap; 0 disables the harness cap.")
    parser.add_argument("--codex-executable", default=str(DEFAULT_CODEX_EXECUTABLE))
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--benchmark-env-file", type=Path,
                        help="explicit ignored local Runner/.env for benchmark-side model/judge credentials")
    parser.add_argument("--allow-benchmark-network", action="store_true",
                        help="explicitly use Docker bridge egress for benchmark model/judge services")
    parser.add_argument("--simulator-backend", choices=sorted(SIMULATOR_BACKENDS), default="official",
                        help="official benchmark simulator (default), local Codex, or subscription Claude CLI patient")
    parser.add_argument("--simulator-claude-model", default="claude-sonnet-5")
    parser.add_argument("--simulator-claude-executable", default="claude")
    parser.add_argument("--simulator-max-model-calls", type=int, default=0,
                        help="per-world Codex simulator call quota; 0 disables it; actor budgets remain separate")
    parser.add_argument("--simulator-max-total-chars", type=int, default=0,
                        help="cumulative simulator input-character quota; 0 disables it")
    parser.add_argument("--simulator-world-deadline-seconds", type=int, default=0,
                        help="simulator world deadline; 0 disables it; per-request timeouts remain")
    parser.add_argument("--simulator-request-timeout-seconds", type=int, default=180)
    parser.add_argument("--simulator-effort", default=SIMULATOR_EFFORT,
                        help="Codex patient reasoning effort; the official simulator disables thinking (none/low are closer)")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--json-summary", action="store_true",
                        help="print the full machine-readable batch summary at completion")
    args = parser.parse_args(argv)
    try:
        config = _cli_config(args)
        result = run_batch(config, plan_only=args.plan_only)
    except Exception as exc:
        print(json.dumps({"status": "rejected", "error_type": type(exc).__name__, "reason": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    if args.plan_only:
        print(json.dumps(result, ensure_ascii=False))
        return 0
    manifest_path = str(config.run_dir / "batch.manifest.json")
    if args.json_summary:
        print(json.dumps({"status": "batch_stopped_early" if result.get("execution_stop_reason") else "batch_finished",
                          "manifest": manifest_path,
                          "summary": result.get("summary")}, ensure_ascii=False))
    else:
        summary = result.get("summary", {})
        progress = _batch_progress_fields(result)
        if result.get("execution_stop_reason"):
            print(f"Batch stopped early: {progress['settled_tasks']}/{progress['selected_tasks']} tasks settled; "
                  f"{progress['pending_attempts']} attempts pending; {progress['saved_snapshots']} snapshots saved; "
                  f"{progress['failed_attempts']} failed; {progress['ungraded_attempts']} ungraded; "
                  f"{progress['reconciliation_attempts']} need reconciliation.")
        elif config.defer_grading:
            print(f"Batch actors settled: {progress['settled_tasks']}/{progress['selected_tasks']} tasks; "
                  f"{progress['saved_snapshots']} snapshots saved; {progress['pending_attempts']} attempts pending; "
                  f"{progress['failed_attempts']} failed; {progress['ungraded_attempts']} ungraded; "
                  f"{progress['reconciliation_attempts']} need reconciliation; "
                  "grading deferred.")
        else:
            overall = summary.get("overall", {})
            print(f"Batch finished: {progress['settled_tasks']}/{progress['selected_tasks']} tasks settled; "
                  f"{overall.get('graded_attempts', 0)} official grades; "
                  f"{overall.get('ungraded_attempts', 0)} ungraded; {progress['failed_attempts']} failures; "
                  f"{progress['reconciliation_attempts']} need reconciliation.")
        print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
