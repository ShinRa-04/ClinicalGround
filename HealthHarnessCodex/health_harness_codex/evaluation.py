"""Private run recording and operational comparisons for standalone trials.

This module records what the harness and its tools report. It does not grade
clinical correctness or infer an official benchmark outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Any

from .providers import ModelResponseFormatError
from .console_logs import log_event


_TAXONOMY = {
    "setup_failure", "inference_failure", "schema_or_scope_rejection",
    "unknown_effect", "budget_exhausted", "incomplete_workflow",
    "locally_complete_ungraded", "goal_unverified",
    "response_contract_failure",
    "finished_goal_unmet",
}
_COMPARE_KEYS = ("task_id", "model", "reasoning_effort", "budgets",
                 "initial_state_fingerprint", "source_commit", "source_fingerprint",
                 "task_instruction_sha256", "allowed_instruction_source_sha256")
_SECRET_KEYS = ("key", "token", "secret", "password", "authorization", "credential")
_SAFE_TOKEN_COUNTERS = {"max_output_tokens", "input_tokens", "output_tokens", "total_tokens",
                         "cached_input_tokens", "reasoning_output_tokens", "cache_write_input_tokens"}
_SAFE_COMPLETION_REASONS = {
    "accepted", "goal_unverified", "completion_contract_missing", "completion_contract_task_mismatch",
    "completion_contract_integrity_error", "completion_contract_invalid", "completion_identity_binding_invalid",
    "completion_validator_unavailable",
    "completion_validator_invalid_result", "required_milestones_unobserved", "invalid_evidence",
    "completion_not_verified",
    "open_obligations", "deferred_work_requires_matching_handoff",
}


def _jsonable(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, default=str, allow_nan=False))
    except (TypeError, ValueError):
        return repr(value)


def _safe_metadata(value: Any) -> Any:
    """Remove obvious credentials from metadata before it reaches disk."""
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            token_counter = lowered in _SAFE_TOKEN_COUNTERS and isinstance(item, int) and not isinstance(item, bool)
            secret_field = any(part in lowered for part in _SECRET_KEYS) and not token_counter
            safe[str(key)] = "[redacted]" if secret_field else _safe_metadata(item)
        return safe
    if isinstance(value, list):
        return [_safe_metadata(item) for item in value]
    return _jsonable(value)


def _fingerprint_messages(messages: list[dict[str, Any]]) -> str:
    packed = json.dumps(messages, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(packed.encode("utf-8")).hexdigest()


def _tool_names(reply: Any) -> list[str]:
    calls = getattr(reply, "tool_calls", ()) or ()
    return [str(getattr(call, "name", "unknown")) for call in calls]


class RunRecorder:
    """Persist raw local results and a redacted, readable live event stream."""

    def __init__(self, run_dir: Path, metadata: dict[str, Any]):
        self.run_dir = Path(run_dir).resolve()
        if not any(parent.name.lower() == "runs" for parent in self.run_dir.parents):
            raise ValueError("run_dir must be inside an ignored runs/ directory")
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = _safe_metadata(metadata)
        self.events_path = self.run_dir / "events.jsonl"
        self.live_path = self.run_dir / "run.live.md"
        self._started_at = time.time()
        self._model_calls = 0
        self._planned_tool_calls: dict[str, int] = {}
        self._completed_tool_dispatches: dict[str, int] = {}
        self._not_dispatched_tool_calls: dict[str, int] = {}
        self._tool_statuses: dict[str, int] = {}
        self._latencies: list[float] = []
        self._usage: dict[str, int] = {}
        self._io_lock = threading.RLock()
        self.emit("run_started", metadata=self.metadata)
        self._live(f"# Run in progress\n\nStarted: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

    def _live(self, text: str) -> None:
        with self._io_lock:
            with self.live_path.open("a", encoding="utf-8") as stream:
                stream.write(text.rstrip() + "\n")
                stream.flush()

    def emit(self, kind: str, **fields: Any) -> None:
        if kind in {"model_call_started","model_call_finished","model_call_failed","model_waiting","model_receiving"}:
            fields.setdefault('model_role',self.metadata.get('model_role','workflow'))
        event = {"time": time.time(), "kind": kind, **_jsonable(fields)}
        with self._io_lock:
            with self.events_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                stream.flush()
            context = {
                "task_id": self.metadata.get("task_id", self.metadata.get("task", self.run_dir.name)),
                "domain": self.metadata.get("domain"),
                "attempt": self.metadata.get("attempt"),
            }
            display_kind = kind
            safe_fields = dict(fields)
            if kind in {"model_call_started", "model_call_finished", "model_call_failed"}:
                safe_fields["model_role"] = fields.get('model_role',self.metadata.get("model_role", "workflow"))
            if kind in {"tool_call_planned", "tool_call_finished", "tool_waiting"}:
                alias = str(fields.get("name", "unknown"))
                mapping = self.metadata.get("actor_tool_names", {})
                if isinstance(mapping, dict):
                    safe_fields["tool_name"] = mapping.get(alias, alias)
                safe_fields.pop("name", None)
            if kind == "model_call_finished":
                proposed = fields.get("proposed_tool_names", [])
                safe_fields["proposal_count"] = len(proposed) if isinstance(proposed, list) else None
            # Event context comes from the recorder's fixed per-run metadata.
            # Some event producers include a domain label too; keep the context
            # canonical and avoid passing duplicate keyword arguments.
            safe_fields.pop("task_id", None)
            safe_fields.pop("domain", None)
            safe_fields.pop("attempt", None)
            usage = fields.get("usage")
            if isinstance(usage, dict):
                safe_fields.update({key: usage[key] for key in
                                    ("input_tokens", "output_tokens", "total_tokens", "reasoning_output_tokens")
                                    if key in usage})
            line = log_event(display_kind, **context, **safe_fields)
            self._live(line)
        if kind == "model_call_started":
            self._model_calls += 1
        if kind in {"model_call_finished", "model_call_failed"}:
            elapsed = fields.get("elapsed_seconds")
            if isinstance(elapsed, (int, float)):
                self._latencies.append(float(elapsed))
            usage = fields.get("usage")
            if isinstance(usage, dict):
                for name, value in usage.items():
                    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                        self._usage[name] = self._usage.get(name, 0) + value
        if kind in {"tool_call_planned", "tool_call_finished"}:
            name = str(fields.get("name", "unknown"))
            if kind == "tool_call_planned":
                self._planned_tool_calls[name] = self._planned_tool_calls.get(name, 0) + 1
            else:
                status = str(fields.get("status", "unknown"))
                self._tool_statuses[status] = self._tool_statuses.get(status, 0) + 1
                if status == "completed":
                    self._completed_tool_dispatches[name] = self._completed_tool_dispatches.get(name, 0) + 1
                elif status == "not_dispatched":
                    self._not_dispatched_tool_calls[name] = self._not_dispatched_tool_calls.get(name, 0) + 1

    def finish(self, result: dict[str, Any], elapsed_seconds: float,
               environment_observations: dict[str, Any] | None = None) -> dict[str, Any]:
        result = _jsonable(result)
        env = _jsonable(environment_observations or {})
        classification = classify_result(result, self._tool_statuses)
        terminal = env.get("public_determination_terminal")
        if terminal is None and isinstance(env.get("public_determination"), dict):
            terminal = env["public_determination"].get("terminal")
        mismatch = None
        if isinstance(terminal, bool) and result.get("status") == "complete":
            gate = result.get("completion_gate") if isinstance(result.get("completion_gate"), dict) else {}
            completion = result.get("completion") if isinstance(result.get("completion"), dict) else {}
            accepted_handoff = (gate.get("accepted") is True and terminal is False and
                                gate.get('case_can_remain_pending') is True)
            mismatch = terminal is False and not accepted_handoff
        if mismatch and classification != "goal_unverified":
            classification = "incomplete_workflow"
        verification = _completion_verification_summary(result)
        final = result.get("final")
        model_claimed_complete = (final.get("status") == "complete"
                                  if isinstance(final, dict) and isinstance(final.get("status"), str)
                                  else None)
        gate = result.get("completion_gate") if isinstance(result.get("completion_gate"), dict) else None
        harness_accepted_completion = (result.get("status") == "complete" and
                                       (gate is None or gate.get("accepted") is not False))
        final_evidence_valid, unsupported_final_evidence_ids = _validate_final_evidence(result)
        report = {
            "schema_version": 1,
            "metadata": self.metadata,
            "harness_status": result.get("status", "unknown"),
            "local_completion_claim": result.get("status") == "complete",
            "model_claimed_complete": model_claimed_complete,
            "harness_accepted_completion": harness_accepted_completion,
            "completion_verification": verification,
            "execution_assessment": result.get('execution_assessment'),
            "execution_endpoint":(result.get('completion') or {}).get('execution_endpoint'),
            "stop_assessment_validation":result.get('stop_assessment_validation'),
            "verified_stage_handoff": bool(
                isinstance(result.get("completion"), dict) and result["completion"].get("has_deferred_work") is True
                and isinstance(result.get("completion_gate"), dict) and result["completion_gate"].get("accepted") is True),
            "workflow_recovery": {
                "turns": len(result.get("workflow_recoveries", []))
                         if isinstance(result.get("workflow_recoveries", []), list) else 0,
                "stop_reason": result.get("workflow_stop_reason") if result.get("workflow_stop_reason") in {
                    "model_budget_exhausted", "stop_recovery_limit_reached",
                    "no_new_source_evidence_after_recovery"} else None,
            },
            "classification": classification,
            "policy_grounding": {
                "required":result.get('policy_grounding_required',False),
                "decision_records": len(result.get('policy_decisions',[])),
                "refused_operations": result.get('policy_decision_refusals',[]),
                "semantic_correctness": "not_assessed_by_local_guard",
            },
            "actual_environment_observations": env,
            "whole_case_terminal_observed": terminal if isinstance(terminal, bool) else None,
            "harness_claim_environment_mismatch": mismatch,
            "final_evidence_valid": final_evidence_valid,
            "unsupported_final_evidence_ids": unsupported_final_evidence_ids,
            "official_success": None,
            "official_score": None,
            "metrics": {
                "model_calls": result.get("model_calls", self._model_calls),
                "model_calls_observed_this_segment": self._model_calls,
                "tool_calls": result.get("tool_calls", sum(self._planned_tool_calls.values())),
                "model_response_format_retry_count": result.get("model_response_format_retry_count", 0),
                "model_transport_retry_count": len(result.get("model_transport_retries", [])),
                "planned_tools": dict(self._planned_tool_calls),
                "tool_dispatch_attempts": dict(self._planned_tool_calls),
                "tool_dispatch_completed": dict(self._completed_tool_dispatches),
                "tool_dispatch_not_dispatched": dict(self._not_dispatched_tool_calls),
                "tool_dispatch_statuses": dict(self._tool_statuses),
                "model_latency_seconds": self._latencies,
                "tool_latency_seconds": [float(event["elapsed_seconds"]) for event in self._read_events()
                                          if event.get("kind") == "tool_call_finished"
                                          and isinstance(event.get("elapsed_seconds"), (int, float))],
                "elapsed_seconds": float(elapsed_seconds),
                "reported_usage": _jsonable(result.get("usage", self._usage)),
                "reported_usage_this_segment": dict(self._usage),
                "context_characters_total": sum(
                    int(event.get("context_characters", 0)) for event in self._read_events()
                    if event.get("kind") == "model_call_started"
                ),
                "evidence_successes": sum(e.get("outcome") == "success" for e in result.get("evidence", []) if isinstance(e, dict)),
                "evidence_failures": sum(e.get("outcome") == "failure" for e in result.get("evidence", []) if isinstance(e, dict)),
                "open_obligations": sum(o.get("status") not in {"closed", "deferred"} for o in result.get("obligations", []) if isinstance(o, dict)),
                "deferred_obligations": sum(o.get("status") == "deferred" for o in result.get("obligations", []) if isinstance(o, dict)),
                "unknown_actions": _unknown_journal_count(result, self._tool_statuses),
                "model_errors": sum(event.get("kind") == "model_call_failed" for event in self._read_events()),
            },
        }
        (self.run_dir / "result.private.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        (self.run_dir / "evaluation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.emit("run_finished", harness_status=report["harness_status"], classification=classification,
                  execution_state=(result.get('execution_assessment') or {}).get('execution_state'),
                  goal_status=(result.get('execution_assessment') or {}).get('requested_outcome',{}).get('status'),
                  model_calls=report["metrics"]["model_calls"], tool_calls=report["metrics"]["tool_calls"],
                  grading_status="pending", elapsed_seconds=float(elapsed_seconds),
                  official_success=None, official_score=None)
        self._live(f"\n## Result\n\n- Harness status: `{report['harness_status']}`\n- Classification: `{classification}`\n- Requested outcome: `{(result.get('execution_assessment') or {}).get('requested_outcome',{}).get('status','unverified')}`\n- Official success: unknown\n- Official score: unknown\n")
        return report

    def _read_events(self) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self.events_path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
        return events


class _Heartbeat:
    """Emit periodic waiting events for blocking operations; always stop cleanly."""

    INTERVAL_SECONDS = 15.0

    def __init__(self, recorder: RunRecorder, event: str, progress=None, interval_seconds=None, **fields: Any):
        self.recorder, self.event, self.fields = recorder, event, fields
        self.progress=progress
        self.interval_seconds=interval_seconds if interval_seconds is not None else self.INTERVAL_SECONDS
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="health-harness-heartbeat", daemon=True)

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            fields=dict(self.fields)
            if self.progress is not None:
                try:fields.update(self.progress())
                except Exception:pass # Diagnostics must not alter execution.
            requested=fields.pop('_event',None)
            event=(requested if self.event=='model_waiting' and requested in {'model_waiting','model_receiving'} else self.event)
            self.recorder.emit(event, **fields)

    def __enter__(self) -> "_Heartbeat":
        self._thread.start()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join()


class RecordingModel:
    """Observe model requests and replies without recording prompt or answer text."""

    def __init__(self, model: Any, recorder: RunRecorder):
        self.model, self.recorder = model, recorder
        self._last_sampled_reply_chars=0

    def _diagnostics(self):
        from .providers import safe_request_diagnostics
        try:
            getter=getattr(self.model,'request_diagnostics',None)
            return safe_request_diagnostics(getter() if callable(getter) else getattr(self.model,'last_request_metrics',{}))
        except Exception:return {} # Optional diagnostics must never mask the model error.

    def _capture_failure(self,call_number,messages,tools):
        """Case-local replay evidence; never console output or tracked content."""
        try:
            root=self.recorder.run_dir/'model-failures'
            if root.is_symlink():return False
            root.mkdir(exist_ok=True)
            if root.resolve().parent!=self.recorder.run_dir.resolve():return False
            getter=getattr(self.model,'failure_response',None)
            response=getter() if callable(getter) else {}
            if not isinstance(response,dict):response={}
            text=response.get('text')
            captured={'text':text[:60000] if isinstance(text,str) else '',
                      'generation_completed':response.get('generation_completed') is True,
                      'text_truncated':response.get('text_truncated') is True}
            request={'messages':messages,'tools':[{'name':s.name,'description':s.description,
                'input_schema':s.input_schema,'effect':s.effect,'identity_fields':list(s.identity_fields)} for s in tools]}
            packed=json.dumps(request,ensure_ascii=False,allow_nan=False)
            if len(packed.encode('utf-8'))>4*1024*1024:
                request={'omitted':'request exceeds private capture bound','sha256':hashlib.sha256(packed.encode('utf-8')).hexdigest()}
            path=root/f'call-{call_number:04d}.private.json'
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
            with os.fdopen(fd,'w',encoding='utf-8') as stream:
                json.dump({'model_call':call_number,'request':request,'assistant_response':captured},stream,
                          ensure_ascii=False,allow_nan=False)
            return True
        except Exception:return False # Preserve the original failure if diagnostics cannot be saved.

    def _wait_fields(self):
        d=self._diagnostics()
        received=d.get('reply_chars_received',0)
        growing=received>self._last_sampled_reply_chars
        self._last_sampled_reply_chars=received
        return {'_event':'model_receiving' if growing else 'model_waiting',
                **{k:v for k,v in d.items() if k in {'timeout_seconds','active_timeout_seconds','notifications_received','native_idle_seconds','process_running',
                    'reply_chars_received','reply_bytes_received','reply_stream_updates','reply_idle_seconds',
                    'estimated_reply_tokens','token_estimate_method','reported_output_tokens','reported_reasoning_tokens'}},
                **({'stage':d['request_stage']} if 'request_stage' in d else {}),
                **({'last_event':d['last_native_event']} if 'last_native_event' in d else {})}

    def complete(self, messages: list[dict[str, Any]], tools: list[Any], *, max_output_tokens: int) -> Any:
        started = time.monotonic()
        self._last_sampled_reply_chars=0
        call_number = self.recorder._model_calls + 1
        declared = [{"name": str(getattr(spec, "name", "unknown")), "effect": getattr(spec, "effect", None)} for spec in tools]
        self.recorder.emit("model_call_started", context_fingerprint=_fingerprint_messages(messages),
                           call_number=call_number,
                           model=self.recorder.metadata.get("model"),
                           context_characters=sum(len(str(m.get("content", ""))) for m in messages),
                           declared_tools=declared, max_output_tokens=max_output_tokens,
                           engine_payload_characters=len(json.dumps({'messages':messages,'tools':[
                               {'name':s.name,'description':s.description,'input_schema':s.input_schema,
                                'effect':s.effect,'identity_fields':list(s.identity_fields)} for s in tools],
                               'max_output_tokens':max_output_tokens},ensure_ascii=False,separators=(',',':'))))
        try:
            with _Heartbeat(self.recorder, "model_waiting", progress=self._wait_fields,
                            interval_seconds=min(_Heartbeat.INTERVAL_SECONDS,5.0),call_number=call_number):
                reply = self.model.complete(messages, tools, max_output_tokens=max_output_tokens)
        except Exception as exc:
            from .providers import safe_request_diagnostics
            from .providers import safe_token_usage
            usage = safe_token_usage(getattr(exc,'usage',{}))
            diagnostics=safe_request_diagnostics(getattr(exc,'diagnostics',{}))
            diagnostics.update(self._diagnostics())
            captured=self._capture_failure(call_number,messages,tools)
            self.recorder.emit("model_call_failed", call_number=call_number,
                               **{k:v for k,v in diagnostics.items() if k in {'reply_chars_received','reply_bytes_received',
                                   'reply_stream_updates','reply_idle_seconds','estimated_reply_tokens','token_estimate_method',
                                   'reported_output_tokens','reported_reasoning_tokens'}},
                               elapsed_seconds=time.monotonic() - started,
                               error_type=type(exc).__name__, usage=usage,request_diagnostics=diagnostics,
                               private_failure_capture_saved=captured,
                               response_failure_stage=diagnostics.get('response_failure_stage'),
                               response_call_index=diagnostics.get('response_call_index'),
                               stage=diagnostics.get('request_stage'),timeout_seconds=diagnostics.get('timeout_seconds'),
                               active_timeout_seconds=diagnostics.get('active_timeout_seconds'),
                               timeout_reason=diagnostics.get('timeout_reason'),
                               request_timed_out=diagnostics.get('request_timed_out'),
                               last_event=diagnostics.get('last_native_event'),
                               native_idle_seconds=diagnostics.get('native_idle_seconds'),
                               notifications_received=diagnostics.get('notifications_received'),
                               cleanup_confirmed=diagnostics.get('cleanup_confirmed'))
            raise
        usage = getattr(reply, "usage", {})
        self.recorder.emit("model_call_finished", call_number=call_number,
                           **{k:v for k,v in self._diagnostics().items() if k in {'reply_chars_received','reply_bytes_received',
                               'reply_stream_updates','reply_idle_seconds','estimated_reply_tokens','token_estimate_method',
                               'reported_output_tokens','reported_reasoning_tokens'}},
                           elapsed_seconds=time.monotonic() - started,
                           proposed_tool_names=_tool_names(reply), usage=usage if isinstance(usage, dict) else {},
                           native_metrics=getattr(self.model,'last_request_metrics',{}))
        return reply


class RecordingTools:
    """Transparent tool proxy; all authorization and execution stay downstream."""

    def __init__(self, tools: Any, recorder: RunRecorder):
        self.tools, self.recorder = tools, recorder
        self._specs: dict[str, Any] = {}
        self._dispatch_number = 0

    def _capture_tool_failure(self, exc: Exception, name: str) -> bool:
        """Keep bounded error evidence locally; never publish service text.

        This is diagnostic evidence, not authorization to retry a mutation.
        Transport failures without a returned response remain uncaptured.
        """
        from .tools import MCPToolError
        if not isinstance(exc, MCPToolError):
            return False
        try:
            root = self.recorder.run_dir / "tool-failures"
            if root.is_symlink():
                return False
            root.mkdir(exist_ok=True)
            if root.resolve().parent != self.recorder.run_dir.resolve():
                return False
            # The response can contain patient information, hence only this
            # case-private file receives it. Redact recognizable credentials
            # in strings as well as credential-shaped object keys.
            def redact(value):
                if isinstance(value, dict):
                    return {str(k): ("[redacted]" if any(s in str(k).lower() for s in _SECRET_KEYS)
                                     else redact(v)) for k, v in value.items()}
                if isinstance(value, list):
                    return [redact(v) for v in value]
                if isinstance(value, str):
                    value = re.sub(r"(?i)Bearer\s+\S+", "Bearer [redacted]", value)
                    return re.sub(r"\bsk-[A-Za-z0-9_-]{12,}", "[redacted]", value)
                return value
            response = redact(exc.diagnostic_result)
            packed = json.dumps(response, ensure_ascii=False, allow_nan=False)
            data = {"dispatch_number": self._dispatch_number, "tool": name,
                    "error_type": "MCPToolError", "outcome_requires_reconciliation": True,
                    "response": response}
            if len(packed.encode("utf-8")) > 65536:
                data["response"] = {"omitted": "response exceeds private capture bound",
                                    "redacted_sha256": hashlib.sha256(packed.encode("utf-8")).hexdigest()}
            path = root / f"dispatch-{self._dispatch_number:04d}.private.json"
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, allow_nan=False)
            return True
        except Exception:
            return False  # Optional capture must preserve the original error.

    def bind_scope(self, scope: Any) -> Any:
        binder = getattr(self.tools, "bind_scope", None)
        if callable(binder):
            return self._bind_call("bind_scope", binder, scope)
        binder = getattr(self.tools, "bind", None)
        if callable(binder):
            return self._bind_call("bind", binder, scope)
        return None

    def bind(self, *args: Any, **kwargs: Any) -> Any:
        binder = getattr(self.tools, "bind", None) or getattr(self.tools, "bind_scope", None)
        if callable(binder):
            return self._bind_call("bind", binder, *args, **kwargs)
        return None

    def _bind_call(self, operation: str, binder: Any, *args: Any, **kwargs: Any) -> Any:
        started = time.monotonic()
        try:
            value = binder(*args, **kwargs)
        except Exception as exc:
            self.recorder.emit("tools_binding_failed", operation=operation,
                               elapsed_seconds=time.monotonic() - started, error_type=type(exc).__name__)
            raise
        self.recorder.emit("tools_bound", operation=operation, elapsed_seconds=time.monotonic() - started)
        return value

    def list_tools(self) -> list[Any]:
        specs = self.tools.list_tools()
        self._specs = {str(spec.name): spec for spec in specs}
        self.recorder.emit("tools_listed", tools=[{"name": name, "effect": getattr(spec, "effect", None)}
                                                    for name, spec in self._specs.items()])
        return specs

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        spec = self._specs.get(name)
        if spec is None:
            # Preserve the delegate's routing behavior and discover its actual declaration.
            self.list_tools()
            spec = self._specs.get(name)
        effect = getattr(spec, "effect", "unknown")
        self._dispatch_number += 1
        self.recorder.emit("tool_call_planned", name=name, declared_effect=effect)
        started = time.monotonic()
        try:
            with _Heartbeat(self.recorder, "tool_waiting", name=name):
                value = self.tools.call(name, arguments)
        except Exception as exc:
            captured = self._capture_tool_failure(exc, name)
            category = "unknown" if type(exc).__name__ == "UnknownOutcomeError" else "failed"
            self.recorder.emit("tool_call_finished", name=name, declared_effect=effect, status=category,
                               elapsed_seconds=time.monotonic() - started, error_type=type(exc).__name__,
                               private_failure_capture_saved=captured)
            raise
        status = ("not_dispatched" if isinstance(value, dict) and value.get("isError") is True
                  and value.get("known_not_dispatched") is True else "completed")
        result_status = "error" if isinstance(value, dict) and ("error" in value or value.get("isError") is True) else "success"
        self.recorder.emit("tool_call_finished", name=name, declared_effect=effect, status=status,
                           result_status=result_status,
                           elapsed_seconds=time.monotonic() - started,
                           actual_effect={"result_type": type(value).__name__,
                                          "result_keys": sorted(map(str, value.keys())) if isinstance(value, dict) else []})
        return value


def classify_result(result: dict[str, Any], tool_statuses: dict[str, int] | None = None) -> str:
    """Map observed operational state to a cautious, non-quality classification."""
    status = str(result.get("status", "")).lower()
    message = str(result.get("message", "")).lower()
    if _unknown_journal_count(result, tool_statuses):
        return "unknown_effect"
    if any(term in message for term in ("schema validation", "failed schema", "schema or case-identity",
                                       "scope conflict", "scope rejection", "outside the active scope",
                                       "wrong patient", "wrong case", "identity mismatch", "arguments rejected")):
        return "schema_or_scope_rejection"
    if status == "unknown" or any(term in message for term in ("unknown outcome", "may have executed", "needs reconciliation", "unknown action")):
        return "unknown_effect"
    if status in {"exhausted", "budget_exhausted"} or "budget exhausted" in message or "budget" in message and "exhaust" in message:
        return "budget_exhausted"
    if status in {"error", "failed", "setup_failure"}:
        failure=result.get('model_failure') or {}
        category=failure.get('failure_category')
        if isinstance(category,str) and category.startswith(('response_format:','response_limit:')):
            return 'response_contract_failure'
        return "inference_failure" if "model" in message or "inference" in message else "setup_failure"
    if status=='complete' and (result.get('execution_assessment') or {}).get('requested_outcome',{}).get('status')=='unmet':
        return 'finished_goal_unmet'
    verification = _completion_verification_summary(result)
    if status in {"complete", "unresolved", "blocked"} and verification:
        if verification["status"] == "unverified":
            return "goal_unverified"
        if verification["status"] == "incomplete":
            return "incomplete_workflow"
    if status == "complete":
        return "locally_complete_ungraded"
    return "incomplete_workflow"


def _completion_verification_summary(result: dict[str, Any]) -> dict[str, Any] | None:
    """Return a small allowlisted completion-gate summary without evidence values."""
    gate = result.get("completion_gate")
    if not isinstance(gate, dict):
        gate = result.get("completion_verification")
    if not isinstance(gate, dict):
        return None
    accepted = gate.get("accepted") if isinstance(gate.get("accepted"), bool) else None
    reason = gate.get("reason_code")
    if reason not in _SAFE_COMPLETION_REASONS:
        reason = None
    branch = gate.get("branch_id")
    if not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,96}", branch):
        branch = None
    missing = gate.get("missing_milestones")
    missing_count = len(missing) if isinstance(missing, list) else (
        gate.get("missing_milestone_count") if isinstance(gate.get("missing_milestone_count"), int)
        and not isinstance(gate.get("missing_milestone_count"), bool) and gate.get("missing_milestone_count") >= 0
        else None)
    if accepted is True:
        status = "verified"
    elif reason in {"goal_unverified", "completion_contract_missing", "completion_contract_task_mismatch",
                    "completion_contract_integrity_error", "completion_contract_invalid",
                    "completion_identity_binding_invalid", "completion_validator_unavailable",
                    "completion_validator_invalid_result"}:
        status = "unverified"
    elif reason in {'required_milestones_unobserved','open_obligations','deferred_work_requires_matching_handoff'} or (missing_count is not None and missing_count > 0):
        status = "incomplete"
    elif accepted is False:
        # Rejected gates fail closed. Only a known mapped-goal milestone
        # failure is classified incomplete; every other rejection is
        # unverified rather than a model/workflow failure.
        status = "unverified"
    else:
        status = "unknown"
    return {"status": status, "accepted": accepted, "branch_id": branch,
            "missing_milestone_count": missing_count, "reason_code": reason}


def _unknown_journal_count(result: dict[str, Any], tool_statuses: dict[str, int] | None = None) -> int:
    statuses = result.get("journal_statuses")
    if isinstance(statuses, dict):
        value = statuses.get("unknown", 0)
        return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0
    return int((tool_statuses or {}).get("unknown", 0))


def _validate_final_evidence(result: dict[str, Any]) -> tuple[bool | None, list[Any]]:
    """Check final citations against successful evidence in this case result.

    This is reference integrity only; it does not assess whether evidence
    substantively supports the final claim.
    """
    final = result.get("final")
    if not isinstance(final, dict) or "evidence_ids" not in final:
        return None, []
    citations = final.get("evidence_ids")
    if not isinstance(citations, list) or not citations:
        return None, []
    successful_ids = {evidence.get("id") for evidence in result.get("evidence", [])
                      if isinstance(evidence, dict) and evidence.get("outcome") == "success"
                      and isinstance(evidence.get("id"), str) and evidence.get("id")}
    unsupported = []
    for evidence_id in citations:
        if not isinstance(evidence_id, str) or not evidence_id or evidence_id not in successful_ids:
            if evidence_id not in unsupported:
                unsupported.append(evidence_id)
    return not unsupported, unsupported


def compare_reports(report_a: dict[str, Any], report_b: dict[str, Any]) -> dict[str, Any]:
    """Compare operational metrics and state exactly what is comparable."""
    ma, mb = report_a.get("metadata", {}), report_b.get("metadata", {})
    checks: dict[str, str] = {}
    aliases = {"task_id": "task", "reasoning_effort": "effort", "budgets": "limits"}
    for key in _COMPARE_KEYS:
        a, b = ma.get(key, ma.get(aliases.get(key, ""))), mb.get(key, mb.get(aliases.get(key, "")))
        checks[key] = "unknown" if a is None or b is None else ("same" if a == b else "different")
    controlled = ma.get("composition") is not None and mb.get("composition") is not None
    checks["composition"] = "controlled_difference" if controlled and ma["composition"] != mb["composition"] else (
        "same" if controlled else "unknown")
    metrics_a, metrics_b = report_a.get("metrics", {}), report_b.get("metrics", {})
    deltas: dict[str, float] = {}
    for key in ("model_calls", "tool_calls", "elapsed_seconds", "context_characters_total",
                "evidence_successes", "evidence_failures", "open_obligations", "unknown_actions"):
        a, b = metrics_a.get(key), metrics_b.get(key)
        if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
            deltas[key] = b - a
    usage_a = metrics_a.get("reported_usage", {})
    usage_b = metrics_b.get("reported_usage", {})
    if isinstance(usage_a, dict) and isinstance(usage_b, dict):
        for key in sorted(set(usage_a) & set(usage_b)):
            a, b = usage_a[key], usage_b[key]
            if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
                deltas[f"reported_usage.{key}"] = b - a
    return {"comparability": checks, "deltas_b_minus_a": deltas,
            "metrics": {"a": _jsonable(metrics_a), "b": _jsonable(metrics_b)},
            "comparison_scope": "operational metrics only; no clinical or quality gain is inferred",
            "classification_a": report_a.get("classification"), "classification_b": report_b.get("classification"),
            "official_outcomes": {"a": report_a.get("official_success"), "b": report_b.get("official_success")}}


def _load_report(path: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not an evaluation report object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare local operational evaluation reports")
    sub = parser.add_subparsers(dest="command", required=True)
    compare = sub.add_parser("compare", help="compare two evaluation.json reports")
    compare.add_argument("report_a")
    compare.add_argument("report_b")
    args = parser.parse_args(argv)
    print(json.dumps(compare_reports(_load_report(args.report_a), _load_report(args.report_b)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
