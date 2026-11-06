"""Audited continuation of one persisted standalone run in a fresh run directory."""

from __future__ import annotations

from dataclasses import replace

from .models import budget_is_reduction

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from typing import Any

from .codex_provider import CodexSessionModel, validate_active_timeout
from .domain_profiles import DOMAIN_PROFILES, domain_for_task
from .docker_bridge import DockerExecutor, DockerMCPClient, DockerWorkspaceTools
from .engine import Harness
from .evaluation import RecordingModel, RecordingTools, RunRecorder
from .models import Limits, Scope
from .standalone import (
    _CaseSubjectNamespaceTools,
    _path_component,
    _read_determination_summary,
    _source_commit,
    _source_fingerprint,
    _terminal_value,
    _write_report,
)
from .store import CaseStore
from .tools import ToolRegistry
from .workflow_guard import PayerRoutingGuard


_MAX_NOTE_BYTES = 50_000
_MAX_TASK_BYTES = 250_000
_SIGNATURE_FIELDS = ("workflow_stage", "stage_detail", "outcome", "action_owner")


class ContinuationError(RuntimeError):
    pass


class _CompletedEffectGuard:
    """Hide completed terminal mutations and reject their direct redispatch."""

    def __init__(self, tools: ToolRegistry, actor_names: dict[str, str], actions: list[dict[str, Any]]):
        self.tools = tools
        self.actor_names = dict(actor_names)
        completed_suffixes = set()
        for action in actions:
            if action.get("status") != "completed":
                continue
            action_name = action.get("tool")
            actual = self.actor_names.get(action_name, action_name)
            suffix = _actor_tool_suffix(actual) if isinstance(actual, str) else None
            if suffix in {"route_case", "set_disposition"}:
                completed_suffixes.add(suffix)
        self.blocked_actual_names = completed_suffixes
        self.blocked_aliases = {alias for alias, actual in self.actor_names.items()
                                if _actor_tool_suffix(actual) in completed_suffixes}

    def bind_scope(self, scope: Scope) -> None:
        self.tools.bind_scope(scope)

    def list_tools(self):
        return [spec for spec in self.tools.list_tools() if spec.name not in self.blocked_aliases]

    def call(self, name: str, arguments: dict[str, Any]):
        if name in self.blocked_aliases:
            raise ContinuationError("this terminal mutation already completed in the source run and cannot be repeated")
        return self.tools.call(name, arguments)


def _actor_tool_suffix(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower().replace("-", "_")


def run_continuation(container: str, task_dir: Path, source_run_dir: Path, run_dir: Path,
                     executable: str, allowed_instruction_sources: dict[str, str],
                     continuation_note: str, limits: Limits, timeout: float = 180,
                     composition: str = "combined", domain: str | None = None,
                     active_timeout: float | None = None) -> dict[str, Any]:
    """Continue a settled run after validating the public actor state.

    The source SQLite database is opened read-only and backed up to a fresh
    ignored run directory. The actor's public determination summary must still
    match the source receipt before the copied case state is resumed.
    """
    if not isinstance(executable, str) or not Path(executable).is_absolute():
        raise ValueError("codex executable must be an absolute path")
    if not isinstance(continuation_note, str) or not continuation_note.strip():
        raise ValueError("continuation note must be explicit and non-empty")
    if len(continuation_note.encode("utf-8")) > _MAX_NOTE_BYTES:
        raise ValueError("continuation note exceeds the configured size bound")
    if not isinstance(limits, Limits):
        raise TypeError("continuation limits must be an explicit Limits value")
    if composition not in {"combined", "helpers", "team"}:
        raise ValueError("composition must be combined, helpers, or team")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 1 <= timeout <= 1800:
        raise ValueError("timeout must be between 1 and 1800 seconds")
    validate_active_timeout(timeout, active_timeout)

    package_root = Path(__file__).resolve().parents[1]
    runs_root = package_root / "runs"
    source = Path(source_run_dir).resolve(strict=True)
    destination = Path(run_dir).resolve()
    task_dir = Path(task_dir).resolve(strict=True)
    try:
        profile = domain_for_task(task_dir, override=domain)
    except ValueError as exc:
        raise ContinuationError(str(exc)) from None
    if profile.name != "pa_um":
        raise ContinuationError("audit continuation is currently supported only for the validated UM workflow")
    if not source.is_dir() or not source.is_relative_to(runs_root):
        raise ContinuationError("source run must be inside HealthHarnessCodex/runs/")
    if destination == source or not destination.is_relative_to(runs_root):
        raise ContinuationError("destination must be a different directory inside HealthHarnessCodex/runs/")
    if destination.exists() and any(destination.iterdir()):
        raise ContinuationError("destination run directory must be fresh and empty")
    if not re.fullmatch(r"pa_[A-Za-z0-9_-]{1,100}", task_dir.name):
        raise ContinuationError("continuation requires an explicit public PA/UM task directory")
    instruction_path = task_dir / "instruction.md"
    if not task_dir.is_dir() or not instruction_path.is_file() or instruction_path.is_symlink():
        raise ContinuationError("task directory must contain a regular public instruction.md")
    instruction_bytes = instruction_path.read_bytes()
    if len(instruction_bytes) > _MAX_TASK_BYTES:
        raise ContinuationError("public task instruction exceeds the configured size bound")
    task_hash = hashlib.sha256(instruction_bytes).hexdigest()

    source_report_path = source / "run.result.json"
    source_evaluation_path = source / "evaluation.json"
    source_db_path = source / "state.sqlite"
    for path in (source_report_path, source_evaluation_path, source_db_path):
        if not path.is_file() or path.is_symlink():
            raise ContinuationError("source run is missing a regular report, evaluation, or state database")
    report = _read_json(source_report_path, "source run report")
    evaluation = _read_json(source_evaluation_path, "source evaluation")
    scope, case_state = _read_source_case(source_db_path)
    _validate_source(report, evaluation, case_state, scope, task_dir.name, task_hash, container)
    previous_signature = _determination_signature(report.get("actual_determination_readback"), scope.case)
    source_result_hash = _sha256_file(source_report_path)
    source_db_hash = _sha256_file(source_db_path)
    source_eval_hash = _sha256_file(source_evaluation_path)
    source_meta = evaluation.get("metadata", {})
    starting_counts = {
        "model_calls": case_state.get("model_calls", 0),
        "tool_calls": case_state.get("tool_calls", 0),
        "reported_usage": case_state.get("usage", {}),
    }
    old_budgets = case_state.get("budgets", {})
    # The output cap is advisory; resume an older run with its own larger saved value.
    if isinstance(old_budgets.get("max_output_tokens"), int) and old_budgets["max_output_tokens"] > limits.max_output_tokens:
        limits = replace(limits, max_output_tokens=old_budgets["max_output_tokens"])
    for name in ("max_model_calls", "max_tool_calls", "max_context_chars", "max_output_tokens"):
        if budget_is_reduction(name,getattr(limits,name),int(old_budgets.get(name,0))):
            raise ContinuationError("continuation limits cannot reduce persisted run budgets")

    destination.mkdir(parents=True, exist_ok=True)
    destination_db_path = destination / "state.sqlite"
    _backup_readonly_database(source_db_path, destination_db_path, source_db_hash)
    metadata = {
        "mode": "real-case-audit-continuation-unscored",
        "domain": profile.name,
        "task": scope.task,
        "task_id": scope.task,
        "task_instruction_sha256": task_hash,
        "container_identity": container,
        "model": "gpt-6-luna",
        "reasoning_effort": "high",
        "limits": {"max_model_calls": limits.max_model_calls, "max_tool_calls": limits.max_tool_calls,
                   "max_context_chars": limits.max_context_chars, "max_output_tokens": limits.max_output_tokens,
                   "timeout_seconds": float(timeout), "active_timeout_seconds": active_timeout},
        "budgets": {"model_calls": limits.max_model_calls, "tool_calls": limits.max_tool_calls,
                    "context_chars": limits.max_context_chars},
        "source_commit": _source_commit(),
        "source_fingerprint": _source_fingerprint(),
        "allowed_instruction_source_sha256": dict(allowed_instruction_sources),
        "composition": composition,
        "continuation_of": {
            "source_run": source.name,
            "source_report_sha256": source_result_hash,
            "source_evaluation_sha256": source_eval_hash,
            "source_state_sha256": source_db_hash,
            "source_code_fingerprint": source_meta.get("source_fingerprint"),
            "source_commit": source_meta.get("source_commit"),
        },
        "starting_counts": starting_counts,
        "continuation_note_sha256": hashlib.sha256(continuation_note.encode("utf-8")).hexdigest(),
        "started_unix": time.time(),
    }
    recorder = RunRecorder(destination, metadata)
    setup_started = time.monotonic()
    try:
        executor = DockerExecutor(container, timeout=min(40, float(timeout)))
        executor.validate_owned_trial(scope.task)
        actor = DockerMCPClient(container, port=profile.port, timeout=min(30, float(timeout)), executor=executor)
        actor.list_tools()
        observed_ids = {"case_id": scope.case}
        binding = case_state.get("identity_bindings", {})
        if isinstance(binding, dict) and isinstance(binding.get("patient_id"), str):
            observed_ids["patient_id"] = binding["patient_id"]
        elif not scope.patient.startswith("case-subject:"):
            observed_ids["patient_id"] = scope.patient
        live_readback = _read_determination_summary(actor, observed_ids)
        live_signature = _determination_signature(live_readback, scope.case)
        if live_signature != previous_signature:
            raise ContinuationError("public actor determination no longer matches the source run; refusing continuation")
    except Exception as exc:
        elapsed = time.monotonic() - setup_started
        result = {"status": "setup_failure", "error_type": type(exc).__name__,
                  "message": f"Continuation setup failed with {type(exc).__name__}; see the private run record."}
        recorder.finish(result, elapsed, environment_observations={"setup_error_type": type(exc).__name__})
        raise

    case_workspace_root = f"/logs/artifacts/workspaces/{_path_component(scope.case)}"
    case_role_root = f"{case_workspace_root}/{profile.workspace_role}"
    workspace = DockerWorkspaceTools(
        container, case_role_root, scope,
        read_roots=("/workspace/skills/managed-care-operations-handbook",
                    "/opt/healthverse-task-assets/tool_reference.md",
                    f"{case_role_root}/incoming_request", f"{case_workspace_root}/shared/handoff",
                    f"{case_workspace_root}/shared/intake"),
        executor=executor,
    )
    actor_tools = PayerRoutingGuard(actor, actor._actual_names) if profile.name == "pa_um" else actor
    tools = ToolRegistry(actor_tools, workspace)
    store = CaseStore(destination_db_path)
    source_actions = store.actions(scope)
    guarded_tools = _CompletedEffectGuard(tools, actor._actual_names, source_actions)
    model = CodexSessionModel(executable, model="gpt-6-luna", reasoning_effort="high", timeout=timeout,
                              active_timeout=active_timeout,
                              allowed_instruction_sources=allowed_instruction_sources)
    recorder.metadata.update({"scope": scope.to_dict(), "verified_source_determination": previous_signature,
                              "verified_current_determination": live_signature,
                              "completed_terminal_effects_filtered": sorted(guarded_tools.blocked_actual_names)})
    recorder.emit("continuation_source_verified", source_run=source.name,
                  determination_id=previous_signature["determination_id"],
                  case_id=scope.case)
    recording_model = RecordingModel(model, recorder)
    recording_tools = RecordingTools(_CaseSubjectNamespaceTools(
        guarded_tools, scope.patient, scope.patient.startswith("case-subject:"), actor._actual_names,
        discovery_only_names=profile.discovery_only_tools,
        allowed_actor_namespaces=profile.namespaces or None,
        patient_scoped_names=profile.patient_scoped_tools), recorder)
    started = time.monotonic()
    run_exception: Exception | None = None
    result: dict[str, Any]
    try:
        identity_sources = tuple(alias for alias, actual in actor._actual_names.items()
                                 if actual in profile.identity_source_tools)
        harness = Harness(store, recording_model, recording_tools, limits=limits,
                          recovery_helper_policy=case_state.get('recovery_helper_policy','off'),
                          composition=composition, patient_identity_tools=identity_sources)
        result = harness.run(scope, case_state["instruction"], case_state["domain"], resume=True,
                             continuation_note=continuation_note, continuation_limits=limits)
    except Exception as exc:
        run_exception = exc
        result = {"status": "runtime_failure", "error_type": type(exc).__name__,
                  "message": f"Continuation failed with {type(exc).__name__}; see the private run record."}
    try:
        statuses: dict[str, int] = {}
        try:
            for action in store.actions(scope):
                key = str(action.get("status", "unknown"))
                statuses[key] = statuses.get(key, 0) + 1
        except Exception as exc:
            statuses = {"journal_read_error": 1}
            result["journal_read_error_type"] = type(exc).__name__
        result["journal_statuses"] = statuses
    finally:
        store.close()
    elapsed = time.monotonic() - started
    final_readback = ({"status": "skipped_after_run_exception", "reason_type": type(run_exception).__name__}
                      if run_exception else _read_determination_summary(actor, observed_ids))
    report_out = {
        "mode": "real-case-audit-continuation-unscored",
        "task": scope.task,
        "scope": scope.to_dict(),
        "local_harness": result,
        "official_score": "unknown; no judge invoked",
        "actual_determination_readback": final_readback,
        "model": "gpt-6-luna",
        "reasoning_effort": "high",
        "task_instruction_sha256": task_hash,
        "elapsed_seconds": elapsed,
        "container_identity": container,
        "continuation_of": metadata["continuation_of"],
        "starting_counts": starting_counts,
        "observed_this_segment": {
            "model_calls": result.get("model_calls_observed_this_segment"),
            "reported_usage": result.get("reported_usage_this_segment"),
        },
    }
    env = {"case_identity": observed_ids, "source_determination": previous_signature,
           "determination_readback": final_readback}
    terminal = _terminal_value(final_readback)
    if terminal is not None:
        env["public_determination_terminal"] = terminal
    recorder.emit("determination_readback", status=final_readback.get("status"), terminal=terminal)
    evaluation_report = recorder.finish(result, elapsed, environment_observations=env)
    segment_metrics = evaluation_report.get("metrics", {})
    report_out["observed_this_segment"] = {
        "model_calls": segment_metrics.get("model_calls_observed_this_segment"),
        "tool_calls": sum(segment_metrics.get("tool_dispatch_attempts", {}).values()),
        "reported_usage": segment_metrics.get("reported_usage_this_segment", {}),
    }
    _write_report(destination / "run.result.json", report_out)
    if _sha256_file(source_db_path) != source_db_hash:
        raise ContinuationError("source run state changed during continuation")
    return report_out


def _read_source_case(path: Path) -> tuple[Scope, dict[str, Any]]:
    uri = path.resolve().as_uri() + "?mode=ro"
    try:
        db = sqlite3.connect(uri, uri=True)
        try:
            rows = db.execute("SELECT scope_json, state_json FROM cases").fetchall()
        finally:
            db.close()
    except sqlite3.Error:
        raise ContinuationError("source state database could not be read in read-only mode") from None
    if len(rows) != 1:
        raise ContinuationError("source database must contain exactly one isolated case")
    try:
        saved_scope = json.loads(rows[0][0])
        state = json.loads(rows[0][1])
        scope = Scope(**saved_scope)
    except (ValueError, TypeError, json.JSONDecodeError):
        raise ContinuationError("source case state has an invalid scope or JSON record") from None
    if not isinstance(state, dict) or state.get("scope") != scope.to_dict():
        raise ContinuationError("source case state does not match its immutable scope")
    if not isinstance(state.get("instruction"), str) or not isinstance(state.get("domain"), str):
        raise ContinuationError("source case state lacks its original instruction or domain")
    return scope, state


def _validate_source(report: dict[str, Any], evaluation: dict[str, Any], state: dict[str, Any],
                     scope: Scope, task_id: str, task_hash: str, container: str) -> None:
    if report.get("container_identity") != container or scope.environment != f"docker:{container}":
        raise ContinuationError("source run container identity does not match the requested container")
    if report.get("task") != task_id or scope.task != task_id or report.get("scope") != scope.to_dict():
        raise ContinuationError("source run task or case scope does not match the selected public task")
    if report.get("task_instruction_sha256") != task_hash:
        raise ContinuationError("public task instruction differs from the source run")
    metadata = evaluation.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("task_instruction_sha256") != task_hash:
        raise ContinuationError("source evaluation does not confirm the public task instruction hash")
    if metadata.get("container_identity") != container or metadata.get("task_id") != task_id:
        raise ContinuationError("source evaluation container or task does not match the requested run")
    if state.get("status") not in {"complete", "unresolved", "exhausted", "error"}:
        raise ContinuationError("source case is not in a continuable settled status")
    if report.get("local_harness", {}).get("status") != state.get("status"):
        raise ContinuationError("source report and persisted case status disagree")


def _determination_signature(readback: Any, expected_case: str) -> dict[str, Any]:
    if not isinstance(readback, dict) or readback.get("status") != "observed":
        raise ContinuationError("public determination readback is unavailable")
    result = readback.get("result")
    if not isinstance(result, dict):
        raise ContinuationError("public determination readback has no result object")
    roots: list[Any] = [result]
    structured = result.get("structuredContent")
    if structured is not None:
        roots.append(structured)
    content = result.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                try:
                    roots.append(json.loads(block["text"]))
                except (json.JSONDecodeError, RecursionError):
                    continue
    cases: set[str] = set()
    determinations: list[dict[str, Any]] = []
    workflows: list[dict[str, Any]] = []
    nodes = 0

    def visit(node: Any) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > 100_000:
            raise ContinuationError("public determination readback exceeds traversal bounds")
        if isinstance(node, dict):
            for key in ("case_id", "caseId"):
                value = node.get(key)
                if isinstance(value, str):
                    cases.add(value)
            case_obj = node.get("case")
            if isinstance(case_obj, dict) and isinstance(case_obj.get("id"), str):
                cases.add(case_obj["id"])
            determination = node.get("determination")
            if isinstance(determination, dict):
                determinations.append(determination)
            workflow = node.get("workflow_state")
            if isinstance(workflow, dict):
                workflows.append(workflow)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    for root in roots:
        visit(root)
    if not cases or cases != {expected_case}:
        raise ContinuationError("public determination readback case ID does not match the source case")
    normalized_determinations = set()
    for item in determinations:
        identity = (item.get("id"), item.get("case_id"), item.get("final_decision"))
        if all(isinstance(value, str) and value for value in identity):
            normalized_determinations.add(identity)
    if len(normalized_determinations) != 1:
        raise ContinuationError("public readback lacks one stable determination ID and final decision")
    determination_id, determination_case, decision = next(iter(normalized_determinations))
    if determination_case != expected_case:
        raise ContinuationError("public determination belongs to a different case")
    normalized_workflows = set()
    for item in workflows:
        if all(key in item for key in _SIGNATURE_FIELDS):
            normalized_workflows.add(tuple(item[key] for key in _SIGNATURE_FIELDS))
    if len(normalized_workflows) != 1:
        raise ContinuationError("public readback lacks one stable workflow state")
    workflow = dict(zip(_SIGNATURE_FIELDS, next(iter(normalized_workflows))))
    return {"case_id": expected_case, "determination_id": determination_id,
            "final_decision": decision, "workflow_state": workflow}


def _backup_readonly_database(source: Path, destination: Path, expected_hash: str) -> None:
    if destination.exists():
        raise ContinuationError("destination state database already exists")
    source_uri = source.resolve().as_uri() + "?mode=ro"
    try:
        source_db = sqlite3.connect(source_uri, uri=True)
        destination_db = sqlite3.connect(destination)
        try:
            source_db.backup(destination_db)
        finally:
            destination_db.close()
            source_db.close()
    except sqlite3.Error:
        raise ContinuationError("source state could not be copied through read-only SQLite backup") from None
    if _sha256_file(source) != expected_hash:
        raise ContinuationError("source state changed while creating continuation snapshot")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise ContinuationError(f"{label} is missing or invalid JSON") from None
    if not isinstance(value, dict):
        raise ContinuationError(f"{label} must be a JSON object")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="health-harness-codex-continue-audit")
    parser.add_argument("--container", required=True)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--source-run-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--codex-executable", required=True)
    parser.add_argument("--codex-instruction-source", type=Path, action="append", default=[])
    parser.add_argument("--note-file", type=Path, required=True,
                        help="ignored local UTF-8 file with the explicit continuation audit note")
    parser.add_argument("--max-model-calls", type=int, required=True)
    parser.add_argument("--max-tool-calls", type=int, required=True)
    parser.add_argument("--max-context-chars", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument('--active-timeout', type=float, help='total active model request cap; --timeout remains the silence/setup cap')
    parser.add_argument("--composition", choices=("combined", "helpers", "team"), default="combined")
    parser.add_argument("--domain", choices=tuple(DOMAIN_PROFILES),
                        help="explicit profile override for synthetic or legacy task paths; UM only")
    args = parser.parse_args(argv)
    if not Path(args.codex_executable).is_absolute():
        parser.error("--codex-executable must be an absolute path")
    package_root = Path(__file__).resolve().parents[1]
    runs_root = package_root / "runs"
    note_path = args.note_file.resolve(strict=True)
    if not note_path.is_relative_to(runs_root) or note_path.is_symlink() or not note_path.is_file():
        parser.error("--note-file must be a regular ignored file under HealthHarnessCodex/runs/")
    note_bytes = note_path.read_bytes()
    if len(note_bytes) > _MAX_NOTE_BYTES:
        parser.error("--note-file exceeds the configured size bound")
    try:
        note = note_bytes.decode("utf-8")
    except UnicodeDecodeError:
        parser.error("--note-file must be UTF-8")
    try:
        approved = {}
        for source in args.codex_instruction_source:
            canonical = source.resolve(strict=True)
            if not canonical.is_file():
                raise ContinuationError("instruction source must be a regular file")
            approved[str(canonical)] = hashlib.sha256(canonical.read_bytes()).hexdigest()
        result = run_continuation(
            args.container, args.task_dir, args.source_run_dir, args.run_dir,
            args.codex_executable, approved, note,
            Limits(max_model_calls=args.max_model_calls, max_tool_calls=args.max_tool_calls,
                   max_context_chars=args.max_context_chars, max_output_tokens=4000),
            timeout=args.timeout, composition=args.composition, domain=args.domain,
            active_timeout=args.active_timeout,
        )
        local = result["local_harness"]
        segment = result.get("observed_this_segment", {})
        print(json.dumps({"status": local.get("status", "unknown"),
                          "model_calls": segment.get("model_calls"),
                          "tool_calls": segment.get("tool_calls"),
                          "result_path": str(args.run_dir / "run.result.json"),
                          "trace_path": str(args.run_dir / "run.live.md")}, ensure_ascii=False))
        return 0 if local.get("status") == "complete" else 2
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__,
                          "run_dir": str(args.run_dir)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
