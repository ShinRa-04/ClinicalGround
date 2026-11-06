"""Safe, concise operational messages for interactive and batch runs.

This module deliberately accepts only a small set of public operational
fields. Prompts, model replies, tool arguments/results, and patient identity
must never be passed to the console logger.
"""

from __future__ import annotations

import math
import re
import sys
import threading
from datetime import datetime, timezone, timedelta
from typing import Any
from .providers import RESPONSE_FORMAT_STAGES

_IST = timezone(timedelta(hours=5, minutes=30), "IST")
_PRINT_LOCK = threading.RLock()
_FIELD_ORDER = (
    "stage", "response_failure_stage", "response_call_index", "error_type", "elapsed_seconds", "timeout_seconds", "active_timeout_seconds", "timeout_reason", "model",
    "reasoning_effort", "model_calls", "tool_calls", "turns", "assistant_messages_seen", "task_index",
    "total_tasks", "selected_tasks", "concurrency", "settled", "active",
    "pending", "saved", "failed", "reconciliation", "grading_status",
    "harness_status", "execution_state", "goal_status", "call_number", "proposal_count", "input_tokens",
    "output_tokens", "total_tokens", "reasoning_output_tokens",
    "result_status", "status", "name", "operation", "tool_name",
    "current", "total", "selection_method", "comparison_number", "matched", "validation_passed", "candidate_count", "resolved",
    "settled_tasks", "active_attempts", "pending_attempts", "saved_snapshots",
    "failed_attempts", "ungraded_attempts", "reconciliation_attempts", "attempts", "tool_count",
    "role", "role_id", "helper_id", "model_role", "runtime_status", "argument_decoding_mode", "composition", "invocation", "after_model_call", "declared_effect", "file_count", "count", "error_code",
    "cache_hits", "cache_misses",
    "last_event", "native_idle_seconds", "notifications_received", "process_running", "cleanup_confirmed", "request_timed_out",
    "reply_chars_received","reply_bytes_received","reply_stream_updates","reply_idle_seconds",
    "estimated_reply_tokens","token_estimate_method","reported_output_tokens","reported_reasoning_tokens",
)
_ALLOWED_FIELDS = set(_FIELD_ORDER)
_SAFE_ENUMS = {
    'runtime_status':{'stopped','unavailable','unverified'},
    'argument_decoding_mode':{'tool_schema','host_validated'},
    'timeout_reason':{'idle','active_total'},
    'response_failure_stage':RESPONSE_FORMAT_STAGES,
    'token_estimate_method':{'characters_div4'},
    'last_event':{'turn_started','turn_completed','turn_error','reasoning_progress','assistant_progress','usage','item_completed','other'},
    "status": {"started", "starting", "waiting", "ready", "finished", "completed",
               "failed", "error", "stopped", "preserved", "settled", "saved",
               "not_dispatched", "unknown", "running", "pending", "skipped", "deferred",
               "inline", "setup_failure", "interrupted", "needs_reconciliation", "deferred_ready",
                "ungraded", "graded", "unresolved", "blocked", "budget_exhausted", "resumed",
               "stopped_early", "not_ready", "approved", "rejected", "incomplete", "reselection_requested"},
    "result_status": {"success", "error", "unknown", "not_dispatched", "completed"},
    "grading_status": {"not_started", "pending", "running", "complete", "failed", "unknown", "deferred", "inline", "not_ready"},
    "harness_status": {"complete", "incomplete", "error", "failed", "exhausted", "unknown", "running",
                       "setup_failure", "interrupted", "unresolved", "needs_reconciliation", "deferred_ready",
                       "ungraded", "graded", "blocked", "budget_exhausted", "not_ready", "reselection_requested"},
    "reconciliation": {"not_needed", "pending", "required", "complete", "failed", "unknown"},
    "reasoning_effort": {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"},
    "model_role": {"identity_comparison", "identity_investigation", "workflow", "helper"},
    "composition": {"combined","helpers","team"},
    "invocation":{'owner','recovery_audit','terminal_review'},
    "execution_state":{'running','stopped','finished'},
    "goal_status":{'achieved','unmet','unverified'},
    "declared_effect": {"read", "write", "unknown"},
    "error_code": {"patient_identity_conflict", "incomplete_public_roster", "native_executable_missing", "setup_error"},
}
_EVENTS = {
    'claude_actor_progress': ('INFO', 'CLAUDE_ACTOR', 'Claude Code actor progress'),
    'cm_dialogue_worker_started':('INFO','CM_DIALOGUE_WORKER_START','CM conversation coordinator started with scoped dialogue authority'),
    'cm_dialogue_worker_finished':('INFO','CM_DIALOGUE_WORKER_END','CM conversation coordinator returned; owner must verify original transcript'),
    'conversation_repetition_stopped':('WARNING','DIALOGUE_REPEAT_STOP','Further dialogue stopped after three identical completed exchanges; patient choice is unchanged'),
    'conversation_write_deferred':('WARNING','RESPONSE_BEFORE_WRITE','Write deferred until the owner observes the preceding conversation response'),
    'terminal_review_started':('WARNING','TERMINAL_REVIEW','Checking a terminal proposal against unfinished requested work'),
    'terminal_review_finished':('INFO','TERMINAL_REVIEW_END','Read-only challenge returned; owner must reconsider before dispatch'),
    'stop_review_started':('WARNING','STOP_REVIEW','Reviewing a proposed stop while the requested goal is unmet'),
    'stop_review_finished':('INFO','STOP_REVIEW_END','Read-only stopping review returned to the owner'),
    'write_payload_warning':('WARNING','PAYLOAD_EMPTY','Accepted operation returned empty collections with omitted payload inputs; inspect execution feedback'),
    'blocker_audit_started':('WARNING','BLOCKER_AUDIT','Recurring blocker triggered a read-only helper review'),
    'blocker_audit_finished':('INFO','BLOCKER_AUDIT_END','Read-only blocker review returned to the owner'),
    "helper_started": ("INFO", "HELPER_START", "Delegated helper job started"),
    "helper_finished": ("INFO", "HELPER_END", "Delegated helper job returned"),
    "progress_recovery": ("WARNING", "REPLAN", "Unchanged observations triggered plan reconsideration"),
    "bootstrap_format_correction": ("WARNING", "BOOTSTRAP_FORMAT", "Bootstrap response format rejected before dispatch"),
    "local_tool_started": ("INFO", "LOCAL_TOOL_START", "Internal tool requested"),
    "local_tool_finished": ("INFO", "LOCAL_TOOL_END", "Internal tool returned"),
    "retrieval_progress": ("INFO", "RETRIEVAL", "Local retrieval progress"),
    "run_started": ("INFO", "ACTOR_SETUP", "Actor setup started"),
    "environment_starting": ("INFO", "ENV_START", "Starting task environment"),
    "health_waiting": ("INFO", "ENV_WAIT", "Waiting for environment health"),
    "discovery_started": ("INFO", "DISCOVERY_START", "Starting actor discovery"),
    "discovery_roster_loaded": ("INFO", "DISCOVERY_ROSTER", "Actor roster loaded"),
    "discovery_chart_progress": ("INFO", "DISCOVERY_PROGRESS", "Discovery chart progress"),
    "discovery_source_progress": ("INFO", "DISCOVERY_SOURCE", "Reading discovery source"),
    "discovery_finished": ("INFO", "DISCOVERY_END", "Actor discovery finished"),
    "identity_matching": ("INFO", "IDENTITY_MATCH", "Matching task identity"),
    "identity_comparison_result": ("INFO", "IDENTITY_RESULT", "Candidate identity assessment recorded"),
    "identity_investigation_started": ("INFO", "IDENTITY_INVESTIGATION_START", "Investigating competing patient matches"),
    "identity_investigation_finished": ("INFO", "IDENTITY_INVESTIGATION_END", "Patient identity investigation finished"),
    "identity_reset_started": ("INFO", "IDENTITY_RESET", "Previous context quarantined; restarting identity investigation"),
    "identity_reset_blocked": ("WARNING", "IDENTITY_RESET_BLOCKED", "Identity reset requires reconciliation or remaining budget"),
    "simulator_worker_stopped": ("INFO", "SIMULATOR_STOPPED", "Counterparty simulator worker stopped"),
    "setup_stage_started": ("INFO", "SETUP_STAGE", "Starting setup stage"),
    "setup_failed": ("ERROR", "SETUP_FAILED", "Task setup failed"),
    "environment_case_bound": ("INFO", "CASE_BOUND", "Task environment identity bound"),
    "workflow_readback": ("INFO", "WORKFLOW_READBACK", "Workflow outcome read back"),
    "grading_started": ("INFO", "GRADING_START", "Evaluation grading started"),
    "grading_finished": ("INFO", "GRADING_END", "Evaluation grading finished"),
    "workflow_started": ("INFO", "WORKFLOW_START", "Workflow started"),
    "model_call_started": ("INFO", "MODEL_START", "Model call started"),
    "model_waiting": ("INFO", "MODEL_WAIT", "No new reply text received"),
    "model_receiving": ("INFO", "MODEL_RECEIVING", "Receiving model reply"),
    "model_call_finished": ("INFO", "MODEL_END", "Model call finished"),
    "model_call_failed": ("ERROR", "MODEL_ERROR", "Model call failed"),
    "response_correction": ("WARNING", "REPLY_CORRECTION", "Proposal not dispatched; requesting bounded response correction"),
    "model_transport_retry": ("WARNING", "MODEL_RETRY", "Native stream disconnected; no proposal dispatched; retrying generation once"),
    "world_unavailable": ("ERROR", "WORLD_UNAVAILABLE", "Task runtime unavailable; stopping inference and preserving state"),
    "tool_call_planned": ("INFO", "TOOL_REQUEST", "Tool request submitted to local dispatcher"),
    "tool_waiting": ("INFO", "TOOL_WAIT", "Still waiting for tool response"),
    "tool_call_finished": ("INFO", "TOOL_END", "Tool dispatch returned"),
    "tools_binding_failed": ("ERROR", "TOOL_BIND_ERROR", "Tool binding failed"),
    "tools_bound": ("INFO", "TOOLS_BOUND", "Tools bound to task"),
    "tools_listed": ("INFO", "TOOLS_DISCOVERED", "Actor capabilities discovered"),
    "run_finished": ("INFO", "WORKFLOW_END", "Workflow execution ended"),
    "batch_started": ("INFO", "BATCH_START", "Batch started"),
    "resume_state": ("INFO", "RESUME_STATE", "Batch resume state loaded"),
    "task_started": ("INFO", "TASK_START", "Task started"),
    "world_starting": ("INFO", "WORLD_START", "Starting task world"),
    "world_started": ("INFO", "WORLD_STARTED", "Task world started"),
    "world_waiting": ("INFO", "WORLD_WAIT", "Waiting for task world"),
    "world_ready": ("INFO", "WORLD_READY", "Task world ready"),
    "actor_starting": ("INFO", "ACTOR_START", "Starting actor"),
    "actor_finished": ("INFO", "ACTOR_END", "Actor finished"),
    "snapshot_starting": ("INFO", "SNAPSHOT_START", "Saving task snapshot"),
    "snapshot_saved": ("INFO", "SNAPSHOT_SAVED", "Task snapshot saved"),
    "world_stopped": ("INFO", "WORLD_STOPPED", "Task world stopped"),
    "world_preserved": ("WARNING", "WORLD_PRESERVED", "Task world preserved for recovery"),
    "task_settled": ("INFO", "TASK_SETTLED", "Task settled"),
    "batch_progress": ("INFO", "BATCH_PROGRESS", "Batch progress"),
    "batch_finished": ("INFO", "BATCH_END", "Batch finished"),
    "batch_stopped_early": ("WARNING", "BATCH_STOPPED", "Batch stopped early"),
    "stage_error": ("ERROR", "STAGE_ERROR", "Operational stage failed"),
}
_BATCH_EVENTS = {
    "batch_started", "resume_state", "batch_progress", "batch_finished", "batch_stopped_early",
}


def _label(value: Any, *, limit: int = 72) -> str:
    """Return a single-line, bounded label with control chars escaped/removed."""
    raw = str(value)
    raw = "".join(ch if ch.isprintable() and ch not in "\r\n\t" else " " for ch in raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:limit] or "unknown"


def _safe_value(key: str, value: Any) -> str | None:
    if key == 'helper_id':
        return value if isinstance(value,str) and re.fullmatch(r'helper-[0-9a-f]{12}',value) else None
    if key == 'role_id':
        return value if isinstance(value,str) and re.fullmatch(r'(?:PA|UM|CM|SH)-[0-9]{2}',value) else None
    if key not in _ALLOWED_FIELDS or value is None:
        return None
    if key in _SAFE_ENUMS:
        normalized = _label(value, limit=32).lower()
        return normalized if normalized in _SAFE_ENUMS[key] else None
    if key in {"stage", "error_type", "model", "name", "operation", "tool_name", "selection_method", "role"}:
        return _label(value)
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            return None
        if key.endswith("_seconds"):
            if value < 0:
                return None
            return f"{value:.1f}s"
        if int(value) == value and value >= 0:
            return str(int(value))
    return None


def format_event(event: str, *, task_id: str | None = None, domain: str | None = None,
                 attempt: int | str | None = None, timestamp: datetime | None = None,
                 **fields: Any) -> str:
    """Format a known operational event without printing sensitive values.

    ``timestamp`` is injectable for deterministic callers; production uses
    local wall time in India Standard Time.
    """
    now = timestamp or datetime.now(_IST)
    if now.tzinfo is None:
        now = now.replace(tzinfo=_IST)
    stamp = now.astimezone(_IST).strftime("%H:%M:%S IST")
    context = "BATCH" if event in _BATCH_EVENTS else "task-unknown"
    if task_id is not None:
        safe_task = _label(task_id, limit=100)
        parts = []
        if domain:
            parts.append(_label(domain, limit=24))
        parts.append(safe_task)
        if attempt is not None:
            safe_attempt = _safe_value("call_number", attempt)
            if safe_attempt:
                parts.append(f"a{safe_attempt}")
        context = "/".join(parts)
    config = _EVENTS.get(event)
    if config is None:
        return f"[{stamp}] INFO [{context}] UNKNOWN {_label(event, limit=64)}"
    level, code, message = config
    if event == "resume_state":
        message = ("Fresh batch; no earlier task progress" if fields.get("status") == "started"
                   else "Batch resume state loaded")
    terminal_status = fields.get("harness_status")
    if terminal_status in {"blocked", "error", "failed", "unresolved", "setup_failure",
                           "needs_reconciliation", "interrupted", "budget_exhausted"}:
        level = "ERROR"
    elif terminal_status in {"incomplete", "deferred_ready", "ungraded"}:
        level = "WARNING"
    elif fields.get('execution_state')=='finished' and fields.get('goal_status')=='unmet':
        level = "WARNING"
    status = fields.get("status")
    if status in {"blocked", "error", "failed", "unresolved", "setup_failure", "needs_reconciliation"}:
        level = "ERROR"
    elif event == "tool_call_finished" and (status == "not_dispatched" or fields.get("result_status") == "error"):
        level = "WARNING"
    elif event == "tool_call_finished" and status in {"failed", "unknown"}:
        level = "ERROR"
    details = []
    for key in _FIELD_ORDER:
        safe = _safe_value(key, fields.get(key))
        if safe is not None:
            # Map implementation field names to compact readable labels.
            details.append(f"{key}={safe}")
    suffix = f" {' '.join(details)}" if details else ""
    return f"[{stamp}] {level} [{context}] {code} {message}{suffix}"


def log_event(event: str, *, task_id: str | None = None, domain: str | None = None,
              attempt: int | str | None = None, **fields: Any) -> str:
    """Print one flushed operational line and return it for live logs/tests."""
    line = format_event(event, task_id=task_id, domain=domain, attempt=attempt, **fields)
    with _PRINT_LOCK:
        print(line, file=sys.stdout, flush=True)
    return line
