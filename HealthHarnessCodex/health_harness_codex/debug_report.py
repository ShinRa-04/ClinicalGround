"""Build a sanitized, all-case diagnostic ledger from a completed batch.

This module reads only the public batch manifest and allowlisted local actor
evaluation/event metadata. It never reads verifier expectations, judge output,
patient text, model answers, tool arguments, or exported clinical state.
Generated JSON/CSV belong under the ignored ``runs/`` directory.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any


class DebugReportError(RuntimeError):
    """The selected run or report inputs are invalid."""


_SAFE_LOCAL_STATUSES = {
    "complete", "unresolved", "error", "blocked", "setup_failure",
    "interrupted", "needs_reconciliation", "deferred_ready", "ungraded", "graded", "not_started",
}
_SAFE_BATCH_STATUSES = {
    "complete", "deferred_ready", "setup_failure", "needs_reconciliation", "interrupted",
    "graded", "ungraded", "running", "pending",
}
_SAFE_CLASSIFICATIONS = {
    "locally_complete_ungraded", "incomplete_workflow", "schema_or_scope_rejection",
    "unknown_effect", "inference_failure", "setup_failure", "interrupted", "not_started",
    "goal_unverified",
}
_SAFE_EVENT_KINDS = {
    "setup_failed", "model_call_failed", "model_call_finished", "tool_call_finished", "workflow_readback",
    "run_finished", "reconciliation_observation",
}
_SAFE_EVENT_TEXT = {
    "stage": {"provider_initialization", "ownership_validation", "actor_discovery"},
    "error_code": {"patient_identity_conflict", "setup_error"},
    "error_type": {"ProviderError", "MCPToolError", "StandaloneError", "ValueError"},
    "status": {"failed", "completed", "error", "setup_failure", "blocked", "complete", "unresolved"},
}
_METRIC_FIELDS = {
    "model_calls", "tool_calls", "tool_dispatch_attempts", "tool_dispatch_completed",
    "tool_dispatch_not_dispatched", "evidence_successes", "evidence_failures",
    "open_obligations", "unknown_actions", "model_errors",
}
_ISSUE_BY_CLASSIFICATION = {
    "locally_complete_ungraded": "RUN03-LOCAL-COMPLETE-UNGRADED",
    "incomplete_workflow": "RUN03-INCOMPLETE-WORKFLOW",
    "schema_or_scope_rejection": "RUN03-SCHEMA-SCOPE-REJECTION",
    "unknown_effect": "RUN03-UNKNOWN-EFFECT-BLOCK",
    "inference_failure": "RUN03-INFERENCE-FAILURE",
    "setup_failure": "RUN03-SETUP-DISCOVERY-FAILURE",
    "interrupted": "RUN03-INTERRUPTED",
    "not_started": "RUN03-PENDING-NOT-STARTED",
    "goal_unverified": "RUN03-GOAL-UNVERIFIED",
}
_ISSUE_BY_CLOSURE = {
    "final_prose_without_completion_record": "RUN03-FINAL-PROSE-NO-RECORD",
    "structured_final_status_not_complete": "RUN03-FINAL-STATUS-INCOMPLETE",
    "open_obligations_remain": "RUN03-OPEN-OBLIGATIONS",
    "completion_cites_unobserved_evidence": "RUN03-UNOBSERVED-EVIDENCE",
}
_DEFAULT_ISSUES = {
    "RUN03-LOCAL-COMPLETE-UNGRADED": {
        "root_cause": "No local failure is recorded; official grading was not run.",
        "fix_source": "No code fix indicated by local status.",
        "tests": "No issue-specific fix test identified.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Official grading remains unavailable.",
    },
    "RUN03-INCOMPLETE-WORKFLOW": {
        "root_cause": "Local workflow ended unresolved; official verifier evidence is unavailable.",
        "fix_source": "Pending lane diagnosis.",
        "tests": "Pending lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Determine whether the actor can close the public task workflow.",
    },
    "RUN03-SCHEMA-SCOPE-REJECTION": {
        "root_cause": "The local harness classified a schema or scope rejection; case-specific cause requires safe event review.",
        "fix_source": "Pending runtime/domain lane report.",
        "tests": "Pending lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Confirm the failing contract from public task instructions and safe local events.",
    },
    "RUN03-UNKNOWN-EFFECT-BLOCK": {
        "root_cause": "The harness blocked an action whose effect was not safely classified.",
        "fix_source": "Pending runtime/domain lane report.",
        "tests": "Pending lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Confirm whether the effect contract can be made explicit without weakening safety gates.",
    },
    "RUN03-INFERENCE-FAILURE": {
        "root_cause": "The provider adapter recorded an inference failure; historical status or transport details may be incomplete.",
        "fix_source": "Pending runtime lane report.",
        "tests": "Pending runtime lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Use a fresh isolated diagnostic run to determine whether the failure recurs.",
    },
    "RUN03-SETUP-DISCOVERY-FAILURE": {
        "root_cause": "Actor setup or case discovery failed before tool dispatch.",
        "fix_source": "Pending runtime/domain lane report.",
        "tests": "Pending lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Keep the failed attempt ungraded; verify any correction in a fresh isolated attempt.",
    },
    "RUN03-INTERRUPTED": {
        "root_cause": "The attempt was interrupted before completion.",
        "fix_source": "No fix identified.",
        "tests": "No issue-specific fix test identified.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Reconcile preserved evidence before any fresh attempt.",
    },
    "RUN03-PENDING-NOT-STARTED": {
        "root_cause": "The selected attempt remained pending when the batch was stopped.",
        "fix_source": "No attempt ran; no source cause is assigned.",
        "tests": "No attempt-specific software result exists.",
        "rerun_status": "Not run; the stopped batch is not resumed automatically.",
        "outstanding": "Any future run requires an explicitly authorized fresh or resumed execution plan.",
    },
    "RUN03-GOAL-UNVERIFIED": {
        "root_cause": "The public task instructions and approved role material do not establish a verifiable task endpoint.",
        "fix_source": "No model or workflow failure is inferred from an unmapped public goal.",
        "tests": "Completion mapping must remain unverified until the task endpoint is explicit.",
        "rerun_status": "Not rerun; this classification is about available task-contract evidence.",
        "outstanding": "Clarify or map the public task goal before treating a completion claim as accepted.",
    },
    "RUN03-FINAL-PROSE-NO-RECORD": {
        "root_cause": "The local engine recorded a prose final without the required structured completion record.",
        "fix_source": "Pending runtime lane report.",
        "tests": "Pending runtime lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Any format correction must be bounded, charged, and still pass the same-case closure gates.",
    },
    "RUN03-FINAL-STATUS-INCOMPLETE": {
        "root_cause": "The final structured response used an incomplete or pending status.",
        "fix_source": "Pending runtime/domain lane report.",
        "tests": "Pending lane report.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "The public task must actually close before any completion claim is accepted.",
    },
    "RUN03-OPEN-OBLIGATIONS": {
        "root_cause": "The local engine rejected a completion claim while same-case obligations remained open.",
        "fix_source": "No safety-gate bypass is planned.",
        "tests": "Existing same-case obligation closure checks apply.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Resolve obligations using observed case evidence; do not infer or force closure.",
    },
    "RUN03-UNOBSERVED-EVIDENCE": {
        "root_cause": "The local engine rejected a completion citation outside the successful same-case evidence journal.",
        "fix_source": "No evidence validation bypass is planned.",
        "tests": "Existing same-case evidence citation checks apply.",
        "rerun_status": "Not rerun in this diagnostic ledger.",
        "outstanding": "Use only successful evidence IDs recorded for that same case.",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_file(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _run_root(path: str | Path) -> Path:
    root = Path(path).resolve(strict=True)
    runs_root = Path(__file__).resolve().parents[1] / "runs"
    if not root.is_relative_to(runs_root.resolve()):
        raise DebugReportError("run directory must be inside ignored HealthHarnessCodex/runs")
    manifest = root / "batch.manifest.json"
    if manifest.is_symlink() or not manifest.is_file():
        raise DebugReportError("batch manifest is missing or linked")
    return root


def _safe_text(event: dict[str, Any], field: str) -> str | None:
    value = event.get(field)
    allowed = _SAFE_EVENT_TEXT.get(field)
    if isinstance(value, str) and allowed and value in allowed:
        return value
    return None


def _safe_event_evidence(events_path: Path) -> tuple[list[dict[str, Any]], dict[str, list[int]], dict[str, int]]:
    safe_events: list[dict[str, Any]] = []
    indices: dict[str, list[int]] = {}
    counts = {
        "model_calls_observed": 0, "identity_comparison_calls": 0, "model_call_failures": 0,
        "tool_calls_planned": 0, "tool_call_failures": 0, "tool_call_events": 0,
    }
    if events_path.is_symlink() or not events_path.is_file():
        return safe_events, indices, counts
    for line_number, line in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("kind")
        if kind == "model_call_started":
            counts["model_calls_observed"] += 1
            if event.get("model_role") == "identity_comparison":
                counts["identity_comparison_calls"] += 1
        if kind == "model_call_failed":
            counts["model_call_failures"] += 1
        if kind == "tool_call_planned":
            counts["tool_calls_planned"] += 1
        if kind == "tool_call_finished":
            counts["tool_call_events"] += 1
            if event.get("status") == "failed":
                counts["tool_call_failures"] += 1
        if kind not in _SAFE_EVENT_KINDS:
            continue
        indices.setdefault(kind, []).append(line_number)
        record: dict[str, Any] = {"event_number": line_number, "kind": kind}
        for field in ("stage", "error_code", "error_type", "status"):
            value = _safe_text(event, field)
            if value is not None:
                record[field] = value
        for field in ("call_number", "model_calls", "tool_calls", "observed_model_calls", "observed_tool_events"):
            value = event.get(field)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                record[field] = value
        safe_events.append(record)
    return safe_events, indices, counts


def _metrics(evaluation: dict[str, Any]) -> dict[str, int]:
    metrics = evaluation.get("metrics")
    if not isinstance(metrics, dict):
        return {}
    return {
        key: value for key, value in metrics.items()
        if key in _METRIC_FIELDS and isinstance(value, int) and not isinstance(value, bool) and value >= 0
    }


def _classification(evaluation: dict[str, Any], status: str) -> str:
    value = evaluation.get("classification")
    if isinstance(value, str) and value in _SAFE_CLASSIFICATIONS:
        return value
    if status == "not_started":
        return "not_started"
    return status if status in _SAFE_CLASSIFICATIONS else "unknown"


def _closure_subcategory(result_path: Path, classification: str) -> str | None:
    """Map only known fixed harness messages; never retain model or patient text."""
    if classification != "incomplete_workflow":
        return None
    result = _json_file(result_path)
    local = result.get("local_harness")
    message = local.get("message") if isinstance(local, dict) else None
    if not isinstance(message, str):
        return None
    if message == "The model returned prose without the required structured completion record.":
        return "final_prose_without_completion_record"
    if message == "The structured response did not claim scoped completion.":
        return "structured_final_status_not_complete"
    if message.startswith("Completion is blocked by open obligations:"):
        return "open_obligations_remain"
    if message == "Completion cited evidence outside this case's observed action journal.":
        return "completion_cites_unobserved_evidence"
    return None


def _grade_availability(attempt: dict[str, Any]) -> str:
    if attempt.get("status") == "graded":
        return "official_grade_present"
    if attempt.get("status") == "deferred_ready":
        return "not_run_snapshot_available"
    if attempt.get("status") == "needs_reconciliation":
        return "unavailable_attempt_needs_reconciliation"
    if attempt.get("status") == "setup_failure":
        return "unavailable_attempt_setup_failure"
    return "unavailable_no_verified_snapshot"


def _execution_state_at_observation(status: str, task_id: str, stopped_task_ids: set[str]) -> str:
    if status == "pending":
        return "pending_not_started"
    if status == "running":
        return "paused_after_stop" if task_id in stopped_task_ids else "running_state_unreconciled"
    if status == "deferred_ready":
        return "snapshot_saved_grading_deferred"
    if status in {"setup_failure", "needs_reconciliation", "interrupted"}:
        return "settled_requires_reconciliation"
    if status in {"graded", "ungraded", "complete"}:
        return "settled"
    return "unknown"


def _completion_audit(evaluation: dict[str, Any], local_result: dict[str, Any]) -> dict[str, Any]:
    """Keep local claim, citation integrity, contract gate, and public goal separate.

    Valid evidence IDs establish reference integrity only. A local ``complete``
    status without an explicit public-task contract gate is reported as
    unverified and is never upgraded to a verified workflow outcome here.
    """
    local_status = evaluation.get("harness_status")
    if local_status not in _SAFE_LOCAL_STATUSES:
        local_status = local_result.get("status")
    local_claim = evaluation.get("harness_accepted_completion")
    if not isinstance(local_claim, bool):
        local_claim = evaluation.get("local_completion_claim")
    if not isinstance(local_claim, bool):
        local_claim = local_status == "complete"

    final_record = local_result.get("final")
    final_status = final_record.get("status") if isinstance(final_record, dict) else None
    if final_status not in {"complete", "incomplete", "pending", "unresolved", "blocked"}:
        final_status = None
    model_claim = evaluation.get("model_claimed_complete")
    if not isinstance(model_claim, bool):
        model_claim = final_status == "complete"

    citation_valid = evaluation.get("final_evidence_valid")
    citation_integrity = ("valid" if citation_valid is True else
                          "invalid" if citation_valid is False else "not_checked")

    gate = evaluation.get("completion_gate")
    if not isinstance(gate, dict):
        gate = evaluation.get("completion_verification")
    if not isinstance(gate, dict):
        gate = local_result.get("completion_gate")
    if not isinstance(gate, dict):
        gate = {}

    accepted = gate.get("accepted")
    if not isinstance(accepted, bool):
        decision = gate.get("decision")
        accepted = True if decision == "accepted" else False if decision == "rejected" else None
    gate_decision = "accepted" if accepted is True else "rejected" if accepted is False else "not_recorded"

    branch = gate.get("branch_id")
    if not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,96}", branch):
        branch = None
    reason = gate.get("reason_code")
    if not isinstance(reason, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,96}", reason):
        reason = None
    missing = gate.get("missing_milestones")
    missing_count = len(missing) if isinstance(missing, list) else gate.get("missing_milestone_count")
    if not isinstance(missing_count, int) or isinstance(missing_count, bool) or missing_count < 0:
        missing_count = None
    verification_status = gate.get("status")
    if verification_status not in {"verified", "incomplete", "unverified", "not_verified", "unknown"}:
        verification_status = None

    explicit_goal_status = gate.get("public_goal_status")
    if explicit_goal_status not in {"verified", "unverified", "not_applicable"}:
        explicit_goal_status = None
    if explicit_goal_status:
        public_goal_status = explicit_goal_status
    elif accepted is True:
        public_goal_status = "verified_by_local_contract_gate"
    elif verification_status == "unverified" or reason == "goal_unverified" or reason == "completion_contract_missing":
        public_goal_status = "unverified"
    elif verification_status == "incomplete" or (accepted is False and missing_count):
        public_goal_status = "incomplete_under_contract"
    elif accepted is False:
        public_goal_status = "unverified"
    elif model_claim or local_claim:
        public_goal_status = "unverified"
    else:
        public_goal_status = "not_claimed"

    return {
        "structured_final_status": final_status,
        "structured_completion_claim": True if final_status == "complete" else
        False if final_status in {"incomplete", "pending", "unresolved", "blocked"} else None,
        "model_claimed_complete": model_claim,
        "local_completion_claim": local_claim,
        "harness_accepted_completion": local_claim,
        "completion_verification_status": verification_status or "not_recorded",
        "completion_gate_decision": gate_decision,
        "completion_gate_branch_id": branch,
        "completion_gate_reason_code": reason,
        "missing_milestone_count": missing_count,
        "citation_integrity": citation_integrity,
        "citation_count": len(local_result.get("final", {}).get("evidence_ids", []))
        if isinstance(local_result.get("final"), dict) and
        isinstance(local_result.get("final", {}).get("evidence_ids"), list) else None,
        "public_goal_status": public_goal_status,
    }


def build_case_debug_report(
    run_dir: str | Path,
    *,
    issue_resolutions: dict[str, dict[str, str]] | None = None,
    case_annotations: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a row for every selected attempt, with only allowlisted metadata."""
    run_root = _run_root(run_dir)
    manifest = _json_file(run_root / "batch.manifest.json")
    stop_receipt = _json_file(run_root / "stop-receipt.private.json")
    stopped_tasks = stop_receipt.get("current_interrupted")
    stopped_task_ids = {
        item.get("task_id") for item in stopped_tasks
        if isinstance(item, dict) and isinstance(item.get("task_id"), str)
    } if isinstance(stopped_tasks, list) else set()
    frozen = manifest.get("frozen_config")
    tasks = manifest.get("tasks")
    if not isinstance(frozen, dict) or not isinstance(tasks, list) or not tasks:
        raise DebugReportError("batch manifest does not contain frozen selected tasks")
    resolutions = issue_resolutions or {}
    annotations = case_annotations or {}
    rows: list[dict[str, Any]] = []
    for task in tasks:
        if not isinstance(task, dict):
            raise DebugReportError("batch contains an invalid task record")
        task_id, domain, attempts = task.get("task_id"), task.get("domain"), task.get("attempts")
        if (not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", task_id) or
                not isinstance(domain, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", domain) or
                not isinstance(attempts, list) or not attempts):
            raise DebugReportError("batch contains an invalid public task identity")
        for attempt in attempts:
            if not isinstance(attempt, dict) or not isinstance(attempt.get("attempt"), int):
                raise DebugReportError("batch contains an invalid attempt record")
            attempt_dir_rel = attempt.get("attempt_dir")
            attempt_status = attempt.get("status")
            if not isinstance(attempt_dir_rel, str) or Path(attempt_dir_rel).is_absolute():
                if attempt_status in {"pending", "running"} and attempt_dir_rel in {None, ""}:
                    attempt_dir = None
                else:
                    raise DebugReportError("attempt directory binding is invalid")
            elif not attempt_dir_rel:
                if attempt_status in {"pending", "running"}:
                    attempt_dir = None
                else:
                    raise DebugReportError("attempt directory binding is invalid")
            else:
                attempt_dir = run_root / attempt_dir_rel
                if not attempt_dir.resolve().is_relative_to(run_root):
                    raise DebugReportError("attempt directory escaped the run root")
            evaluation = _json_file(attempt_dir / "evaluation.json") if attempt_dir else {}
            source_local_status = evaluation.get("harness_status")
            if not isinstance(source_local_status, str) or source_local_status not in _SAFE_LOCAL_STATUSES:
                source_local_status = None
            source_local_classification = evaluation.get("classification")
            if not isinstance(source_local_classification, str) or source_local_classification not in _SAFE_CLASSIFICATIONS:
                source_local_classification = None
            source_local_completion_claim = evaluation.get("local_completion_claim")
            if not isinstance(source_local_completion_claim, bool):
                source_local_completion_claim = None
            local_status = evaluation.get("harness_status")
            if not isinstance(local_status, str) or local_status not in _SAFE_LOCAL_STATUSES:
                local_status = "unknown"
            if local_status == "unknown" and attempt_status == "pending":
                local_status = "not_started"
            elif local_status == "unknown" and attempt_status == "running" and task_id in stopped_task_ids:
                local_status = "interrupted"
            classification = _classification(evaluation, local_status)
            issue_id = _ISSUE_BY_CLASSIFICATION.get(classification, "RUN03-UNCLASSIFIED-LOCAL-OUTCOME")
            closure_subcategory = (_closure_subcategory(attempt_dir / "run.result.json", classification)
                                   if attempt_dir else None)
            closure_issue_id = _ISSUE_BY_CLOSURE.get(closure_subcategory or "")
            issue_ids = [issue_id]
            if closure_issue_id:
                issue_ids.append(closure_issue_id)
            issue = dict(_DEFAULT_ISSUES.get(issue_id, {
                "root_cause": "The local outcome is not classified by the diagnostic allowlist.",
                "fix_source": "Pending review.", "tests": "Pending review.",
                "rerun_status": "Not rerun in this diagnostic ledger.",
                "outstanding": "Review the safe actor event ledger.",
            }))
            if closure_issue_id:
                issue.update(_DEFAULT_ISSUES[closure_issue_id])
            for resolved_id in issue_ids:
                override = resolutions.get(resolved_id, {})
                if isinstance(override, dict):
                    for key in ("root_cause", "fix_source", "tests", "rerun_status", "outstanding"):
                        value = override.get(key)
                        if isinstance(value, str) and value and len(value) <= 600 and "\n" not in value:
                            issue[key] = value
            annotation = annotations.get(task_id, {})
            if isinstance(annotation, dict):
                annotated_ids = annotation.get("issue_ids")
                if (isinstance(annotated_ids, list) and annotated_ids and
                        all(isinstance(value, str) and re.fullmatch(r"[A-Z0-9_.-]{1,96}", value)
                            for value in annotated_ids)):
                    issue_ids = list(dict.fromkeys(annotated_ids))
                for key in ("root_cause", "fix_source", "tests", "rerun_status", "outstanding"):
                    value = annotation.get(key)
                    if isinstance(value, str) and value and len(value) <= 600 and "\n" not in value:
                        issue[key] = value
            event_path = attempt_dir / "events.jsonl" if attempt_dir else None
            if event_path:
                safe_events, event_numbers, event_counts = _safe_event_evidence(event_path)
            else:
                safe_events, event_numbers, event_counts = [], {}, {
                    "model_calls_observed": 0, "identity_comparison_calls": 0, "model_call_failures": 0,
                    "tool_calls_planned": 0, "tool_call_failures": 0, "tool_call_events": 0,
                }
            run_result = _json_file(attempt_dir / "run.result.json") if attempt_dir else {}
            local_result = run_result.get("local_harness") if isinstance(run_result.get("local_harness"), dict) else {}
            metrics = _metrics(evaluation)
            completion_audit = _completion_audit(evaluation, local_result)
            workflow_calls = local_result.get("model_calls")
            bootstrap_calls = run_result.get("bootstrap_model_calls", local_result.get("bootstrap_model_calls"))
            if not isinstance(workflow_calls, int) or isinstance(workflow_calls, bool) or workflow_calls < 0:
                workflow_calls = metrics.get("model_calls", 0)
            if not isinstance(bootstrap_calls, int) or isinstance(bootstrap_calls, bool) or bootstrap_calls < 0:
                bootstrap_calls = event_counts["identity_comparison_calls"]
            total_calls = run_result.get("model_calls_total_observed")
            if not isinstance(total_calls, int) or isinstance(total_calls, bool) or total_calls < 0:
                total_calls = event_counts["model_calls_observed"] or workflow_calls + bootstrap_calls
            tool_calls = local_result.get("tool_calls")
            if not isinstance(tool_calls, int) or isinstance(tool_calls, bool) or tool_calls < 0:
                tool_calls = metrics.get("tool_calls")
            if not isinstance(tool_calls, int) or isinstance(tool_calls, bool) or tool_calls < 0:
                tool_calls = event_counts["tool_calls_planned"]
            metrics.update({
                "model_calls": total_calls,
                "model_calls_bootstrap": bootstrap_calls,
                "model_calls_workflow": workflow_calls,
                "tool_calls": tool_calls,
            })
            final_model_events = event_numbers.get("model_call_finished", [])
            closure_event_numbers = {
                "last_model_call_finished": final_model_events[-1:] if final_model_events else [],
                "run_finished": event_numbers.get("run_finished", []),
                "workflow_readback": event_numbers.get("workflow_readback", []),
            }
            setup_path = attempt_dir / ".setup-exception.private.json" if attempt_dir else None
            setup = _json_file(setup_path) if setup_path else {}
            setup_type = setup.get("exception_type") if setup.get("exception_type") in {"ValueError", "StandaloneError"} else None
            setup_stage = setup.get("stage") if setup.get("stage") in {"actor_discovery", "ownership_validation", "provider_initialization"} else None
            evidence_paths = []
            if attempt_dir:
                evidence_paths.extend([
                    (attempt_dir / "evaluation.json").relative_to(run_root).as_posix(),
                    event_path.relative_to(run_root).as_posix(),
                ])
            if closure_subcategory:
                evidence_paths.append((attempt_dir / "run.result.json").relative_to(run_root).as_posix())
            if (setup_type or setup_stage) and setup_path:
                evidence_paths.append(setup_path.relative_to(run_root).as_posix())
            if attempt.get("status") == "needs_reconciliation":
                evidence_paths.append("recovery/retained-worlds-recovery.json")
            elif attempt.get("status") == "deferred_ready" and attempt_dir:
                evidence_paths.append((attempt_dir / "deferred_snapshot" / "metadata.json").relative_to(run_root).as_posix())
            rows.append({
                "task_id": task_id,
                "domain": domain,
                "attempt": attempt["attempt"],
                # Preserve the manifest's historical status verbatim. A
                # separate field records the stop-receipt observation so the
                # historical manifest does not need rewriting.
                "batch_status": attempt.get("status") if attempt.get("status") in _SAFE_BATCH_STATUSES else "unknown",
                "execution_state_at_observation": _execution_state_at_observation(
                    attempt.get("status") if attempt.get("status") in _SAFE_BATCH_STATUSES else "unknown",
                    task_id, stopped_task_ids),
                "source_local_harness_status": source_local_status,
                "source_local_classification": source_local_classification,
                "source_local_completion_claim": source_local_completion_claim,
                "local_status": local_status,
                "classification": classification,
                "closure_subcategory": closure_subcategory,
                "issue_ids": issue_ids,
                "root_cause": issue["root_cause"],
                "evidence_paths": evidence_paths,
                "evidence_event_numbers": event_numbers,
                "closure_event_numbers": closure_event_numbers,
                "safe_event_evidence": safe_events,
                "event_counts": event_counts,
                "metrics": metrics,
                "model_calls": total_calls,
                "model_calls_bootstrap": bootstrap_calls,
                "model_calls_workflow": workflow_calls,
                "tool_calls": tool_calls,
                "final_evidence_valid": evaluation.get("final_evidence_valid")
                if isinstance(evaluation.get("final_evidence_valid"), bool) else None,
                "unsupported_final_evidence_count": len(evaluation.get("unsupported_final_evidence_ids", []))
                if isinstance(evaluation.get("unsupported_final_evidence_ids"), list) else None,
                "harness_claim_environment_mismatch": evaluation.get("harness_claim_environment_mismatch")
                if isinstance(evaluation.get("harness_claim_environment_mismatch"), bool) else None,
                "workflow_terminal_observed": (evaluation.get("actual_environment_observations", {}).get(
                    "public_determination_terminal")
                    if isinstance(evaluation.get("actual_environment_observations"), dict) and
                    isinstance(evaluation.get("actual_environment_observations", {}).get(
                        "public_determination_terminal"), bool) else None),
                "completion_audit": completion_audit,
                "setup_stage": setup_stage,
                "setup_exception_type": setup_type,
                "fix_source": issue["fix_source"],
                "tests": issue["tests"],
                "rerun_status": issue["rerun_status"],
                "outstanding": issue["outstanding"],
                "official_grade_availability": _grade_availability(attempt),
                "snapshot_status": attempt.get("status"),
            })
    rows.sort(key=lambda row: (row["domain"], row["task_id"], row["attempt"]))
    counts: dict[str, dict[str, int]] = {}
    batch_status_counts: Counter[str] = Counter()
    local_status_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    deferred_local_status_counts: Counter[str] = Counter()
    execution_state_counts: Counter[str] = Counter()
    public_goal_status_counts: Counter[str] = Counter()
    model_claimed_goal_status_counts: Counter[str] = Counter()
    harness_accepted_goal_status_counts: Counter[str] = Counter()
    model_claimed_citation_integrity_counts: Counter[str] = Counter()
    harness_accepted_citation_integrity_counts: Counter[str] = Counter()
    structured_final_status_counts: Counter[str] = Counter()
    verification_status_counts: Counter[str] = Counter()
    model_claim_count = 0
    harness_accepted_count = 0
    for row in rows:
        key = f"{row['domain']}:{row['local_status']}"
        if key not in counts:
            counts[key] = {"count": 0}
        counts[key]["count"] += 1
        batch_status_counts[row["batch_status"]] += 1
        local_status_counts[row["local_status"]] += 1
        classification_counts[row["classification"]] += 1
        execution_state_counts[row["execution_state_at_observation"]] += 1
        if row["batch_status"] == "deferred_ready":
            deferred_local_status_counts[row["local_status"]] += 1
        audit = row["completion_audit"]
        if audit["structured_final_status"]:
            structured_final_status_counts[audit["structured_final_status"]] += 1
        verification_status_counts[audit["completion_verification_status"]] += 1
        public_goal_status_counts[audit["public_goal_status"]] += 1
        if audit["model_claimed_complete"]:
            model_claim_count += 1
            model_claimed_goal_status_counts[audit["public_goal_status"]] += 1
            model_claimed_citation_integrity_counts[audit["citation_integrity"]] += 1
        if audit["local_completion_claim"]:
            harness_accepted_count += 1
            harness_accepted_goal_status_counts[audit["public_goal_status"]] += 1
            harness_accepted_citation_integrity_counts[audit["citation_integrity"]] += 1
    official_grades = sum(row["official_grade_availability"] == "official_grade_present" for row in rows)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "run_dir": run_root.name,
        "source_commit": frozen.get("source_commit") if isinstance(frozen.get("source_commit"), str) else None,
        "source_fingerprint": frozen.get("source_fingerprint") if isinstance(frozen.get("source_fingerprint"), str) else None,
        "task_count": len(tasks),
        "attempt_count": len(rows),
        "official_grade_availability": "present_for_some_attempts" if official_grades else "unavailable_not_run",
        "official_grades": official_grades,
        "batch_status_counts": dict(sorted(batch_status_counts.items())),
        "execution_state_counts": dict(sorted(execution_state_counts.items())),
        "structured_final_status_counts": dict(sorted(structured_final_status_counts.items())),
        "model_claimed_complete_count": model_claim_count,
        "harness_accepted_completion_count": harness_accepted_count,
        "completion_verification_status_counts": dict(sorted(verification_status_counts.items())),
        "public_goal_status_counts": dict(sorted(public_goal_status_counts.items())),
        "model_claimed_public_goal_status_counts": dict(sorted(model_claimed_goal_status_counts.items())),
        "harness_accepted_public_goal_status_counts": dict(sorted(harness_accepted_goal_status_counts.items())),
        "model_claimed_citation_integrity_counts": dict(sorted(model_claimed_citation_integrity_counts.items())),
        "harness_accepted_citation_integrity_counts": dict(sorted(harness_accepted_citation_integrity_counts.items())),
        "local_status_counts": dict(sorted(local_status_counts.items())),
        "local_classification_counts": dict(sorted(classification_counts.items())),
        "incomplete_workflow_count": classification_counts["incomplete_workflow"],
        "blocked_local_outcome_count": local_status_counts["blocked"],
        "deferred_ready_local_status_counts": dict(sorted(deferred_local_status_counts.items())),
        "local_counts_by_domain_and_status": counts,
        "cases": rows,
    }


_CSV_COLUMNS = (
    "task_id", "domain", "attempt", "batch_status", "execution_state_at_observation",
    "source_local_harness_status", "source_local_classification", "source_local_completion_claim",
    "local_status", "classification", "closure_subcategory",
    "issue_ids", "root_cause", "evidence_paths", "evidence_event_numbers", "fix_source",
    "closure_event_numbers", "final_evidence_valid", "unsupported_final_evidence_count",
    "completion_audit",
    "model_calls", "model_calls_bootstrap", "model_calls_workflow", "tool_calls",
    "workflow_terminal_observed", "harness_claim_environment_mismatch", "tests", "rerun_status",
    "outstanding", "official_grade_availability", "snapshot_status",
)


def write_case_debug_report(
    run_dir: str | Path,
    output_dir: str | Path | None = None,
    *,
    issue_resolutions: dict[str, dict[str, str]] | None = None,
    case_annotations: dict[str, dict[str, Any]] | None = None,
) -> tuple[Path, Path]:
    """Write sanitized JSON and CSV under ignored runs without changing sources."""
    run_root = _run_root(run_dir)
    destination = Path(output_dir) if output_dir else run_root / "debug-report"
    destination.mkdir(parents=True, exist_ok=True)
    destination = destination.resolve()
    runs_root = (Path(__file__).resolve().parents[1] / "runs").resolve()
    if not destination.is_relative_to(runs_root):
        raise DebugReportError("report output must be inside ignored HealthHarnessCodex/runs")
    report = build_case_debug_report(
        run_root, issue_resolutions=issue_resolutions, case_annotations=case_annotations)
    json_path = destination / "all-cases.json"
    csv_path = destination / "all-cases.csv"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=_CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in report["cases"]:
            writer.writerow({
                **row,
                "issue_ids": ";".join(row["issue_ids"]),
                "evidence_paths": ";".join(row["evidence_paths"]),
                "evidence_event_numbers": json.dumps(row["evidence_event_numbers"], sort_keys=True),
                "closure_event_numbers": json.dumps(row["closure_event_numbers"], sort_keys=True),
                "completion_audit": json.dumps(row["completion_audit"], sort_keys=True),
            })
    return json_path, csv_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--issue-resolutions-json", help="Ignored JSON mapping issue IDs to safe report fields")
    parser.add_argument("--case-annotations-json", help="Ignored JSON mapping public task IDs to safe row annotations")
    args = parser.parse_args(argv)
    try:
        resolutions: dict[str, dict[str, str]] | None = None
        annotations: dict[str, dict[str, Any]] | None = None
        if args.issue_resolutions_json:
            run_root = _run_root(args.run_dir)
            resolution_input = Path(args.issue_resolutions_json)
            resolution_path = resolution_input.resolve(strict=True)
            if (resolution_input.is_symlink() or not resolution_path.is_file() or
                    not resolution_path.is_relative_to(run_root)):
                raise DebugReportError("issue resolutions must be a regular file inside the ignored run directory")
            loaded = _json_file(resolution_path)
            if any(not isinstance(key, str) or not isinstance(value, dict)
                   for key, value in loaded.items()):
                raise DebugReportError("issue resolutions must map issue IDs to objects")
            resolutions = loaded
        if args.case_annotations_json:
            run_root = _run_root(args.run_dir)
            annotation_input = Path(args.case_annotations_json)
            annotation_path = annotation_input.resolve(strict=True)
            if (annotation_input.is_symlink() or not annotation_path.is_file() or
                    not annotation_path.is_relative_to(run_root)):
                raise DebugReportError("case annotations must be a regular file inside the ignored run directory")
            loaded = _json_file(annotation_path)
            if any(not isinstance(key, str) or not isinstance(value, dict)
                   for key, value in loaded.items()):
                raise DebugReportError("case annotations must map task IDs to objects")
            annotations = loaded
        json_path, csv_path = write_case_debug_report(
            args.run_dir, args.output_dir, issue_resolutions=resolutions, case_annotations=annotations)
    except DebugReportError as exc:
        parser.error(str(exc))
    print(json.dumps({"task_rows": len(build_case_debug_report(
        args.run_dir, issue_resolutions=resolutions, case_annotations=annotations)["cases"]),
                      "json": str(json_path), "csv": str(csv_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
