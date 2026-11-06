"""Bounded, stateless-request execution over case-scoped SQLite state."""

from __future__ import annotations

import json
import threading
import uuid
from typing import Any, Protocol

from .models import ConflictError, IsolationError, Limits, ModelReply, Scope, ToolCall, ToolSpec, UnknownOutcomeError, BudgetError
from .context import project_context
from .roles import roles_for, system_prompt
from .schema import validate_arguments
from .store import CaseStore


class Model(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[ToolSpec], *, max_output_tokens: int) -> ModelReply: ...


class Tools(Protocol):
    def list_tools(self) -> list[ToolSpec]: ...
    def call(self, name: str, arguments: dict[str, Any]) -> Any: ...


_LOCAL_SPECS = [
    ToolSpec("case.add_obligation", "Record a case-local task obligation.", {
        "type": "object", "required": ["id", "description"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "description": {"type": "string", "minLength": 1}, "owner": {"type": "string"}},
    }, effect="write"),
    ToolSpec("case.close_obligation", "Close an obligation only with case-local observed evidence.", {
        "type": "object", "required": ["id", "evidence_ids"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "evidence_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}}},
    }, effect="write"),
    ToolSpec("case.read_evidence", "Read a bounded character range from one current-case observed result.", {
        "type": "object", "required": ["id", "offset", "length"], "additionalProperties": False,
        "properties": {"id": {"type": "string", "minLength": 1}, "offset": {"type": "integer", "minimum": 0},
                       "length": {"type": "integer", "minimum": 1, "maximum": 8000}},
    }, effect="read"),
    ToolSpec("case.request_helper", "Ask one bounded read-only role analysis using selected current-case observations.", {
        "type": "object", "required": ["role_id", "question"], "additionalProperties": False,
        "properties": {"role_id": {"type": "string", "minLength": 1}, "question": {"type": "string", "minLength": 1}, "evidence_ids": {"type": "array", "items": {"type": "string"}}},
    }, effect="read"),
]


class Harness:
    def __init__(self, store: CaseStore, model: Model, tools: Tools, limits: Limits | None = None,
                 composition: str = "combined"):
        self.store = store
        self.model = model
        self.tools = tools
        self.limits = limits or Limits()
        if composition not in {"combined", "helpers", "team"}:
            raise ValueError("composition must be combined, helpers, or team")
        self.composition = composition
        self._run_lock = threading.Lock()

    def run(self, scope: Scope, instruction: str, domain: str, resume: bool = False) -> dict[str, Any]:
        if not self._run_lock.acquire(blocking=False):
            raise ConflictError("this Harness instance already has a run in progress")
        try:
            return self._run_owned(scope, instruction, domain, resume)
        finally:
            self._run_lock.release()

    def _run_owned(self, scope: Scope, instruction: str, domain: str, resume: bool = False) -> dict[str, Any]:
        binder = getattr(self.tools, "bind_scope", None)
        if callable(binder):
            binder(scope)
        state = self.store.open_case(scope, instruction, domain)
        configured_limits = self.limits
        owner = f"run-{uuid.uuid4().hex}"
        fence = self.store.claim(scope, owner, ttl_seconds=120)
        try:
            state = self.store.load_case(scope)
            if state["version"] == 0 and not state["messages"]:
                state["budgets"] = {key: getattr(self.limits, key) for key in
                                    ("max_model_calls", "max_tool_calls", "max_context_chars", "max_output_tokens")}
                state["composition"] = self.composition
            else:
                self.limits = Limits(**state.get("budgets", {}))
                if state.get("composition", self.composition) != self.composition:
                    raise ConflictError("composition cannot change while resuming a case")
            state.setdefault("processed_tool_calls", [])
            state.setdefault("usage", {})
            if state["messages"] and not resume:
                raise ConflictError("case already has a conversation; pass resume=True to continue it")
            if resume and state.get("status") == "error":
                # A transient model/schema error may be retried. Any already
                # requested effects still pass through the journal below.
                state["status"] = "running"
                self._save(scope, state, owner, fence)
            if state.get("status") == "complete":
                return self._result(state)
            if not state["messages"]:
                state["messages"] = [
                    {"role": "system", "content": system_prompt(domain, scope, self.composition)},
                    {"role": "user", "content": instruction},
                ]
                state["status"] = "running"
                self._save(scope, state, owner, fence)
            remote = self._tool_map()
            # Finish any response already persisted before a process interruption.
            while state["messages"]:
                pending_round = self._pending_tool_calls(state)
                if pending_round:
                    state, fence = self._execute_calls(scope, state, pending_round, remote, owner, fence)
                    if state.get("status") != "running":
                        return self._result(state)
                if self._should_request_model(state):
                    if state["model_calls"] >= self.limits.max_model_calls:
                        state["status"] = "exhausted"
                        state["message"] = "Model-call budget exhausted with the case unresolved."
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    context_messages = project_context(state["messages"], state, self._available_specs(remote),
                                                       self.limits.max_context_chars)
                    if context_messages is None:
                        state["status"] = "exhausted"
                        state["message"] = "Context budget exhausted; unresolved obligations and source records were preserved."
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    fence = self.store.claim(scope, owner, ttl_seconds=120)
                    state["model_calls"] += 1
                    self._save(scope, state, owner, fence)
                    try:
                        reply = self.model.complete(context_messages, self._available_specs(remote),
                                                    max_output_tokens=self.limits.max_output_tokens)
                        if not isinstance(reply, ModelReply):
                            raise TypeError("model.complete must return ModelReply")
                    except Exception as exc:
                        state = self.store.load_case(scope)
                        state["status"] = "error"
                        state["message"] = f"Model request failed: {type(exc).__name__}: {exc}"
                        self._save(scope, state, owner, fence)
                        return self._result(state)
                    if reply.tool_calls:
                        state = self.store.load_case(scope)
                        self._merge_usage(state, reply.usage)
                        call_ids = [call.id for call in reply.tool_calls]
                        if len(set(call_ids)) != len(call_ids) or any(not isinstance(cid, str) or not cid for cid in call_ids):
                            state["status"] = "error"
                            state["message"] = "Model returned missing or duplicate tool-call IDs."
                            self._save(scope, state, owner, fence)
                            return self._result(state)
                        if self.composition == "helpers" and sum(call.name == "case.request_helper" for call in reply.tool_calls) > 1:
                            state["status"] = "error"
                            state["message"] = "helpers composition permits one bounded role analysis per model turn; use team for selected multiple analyses."
                            self._save(scope, state, owner, fence)
                            return self._result(state)
                        model_round = state["model_calls"]
                        state["messages"].append({"role": "assistant", "content": reply.content,
                                                  "tool_calls": [dict(self._call_dict(call), journal_id=f"m{model_round}:{call.id}")
                                                                 for call in reply.tool_calls]})
                        self._save(scope, state, owner, fence)
                        # The persisted assistant request is replayable for reads only;
                        # journaled writes stop on a pre-existing pending reservation.
                        state, fence = self._execute_calls(scope, state, state["messages"][-1]["tool_calls"], remote, owner, fence)
                        if state.get("status") != "running":
                            return self._result(state)
                        continue
                    state = self.store.load_case(scope)
                    self._merge_usage(state, reply.usage)
                    state["messages"].append({"role": "assistant", "content": reply.content})
                    state = self._accept_final(state, reply.content)
                    self._save(scope, state, owner, fence)
                    return self._result(state)
                # A no-tool assistant message is terminal; this guard avoids a
                # malformed conversation spinning without progress.
                if state["messages"][-1].get("role") == "assistant":
                    return self._result(state)
            state["status"] = "unresolved"
            state["message"] = "No model response was recorded."
            self._save(scope, state, owner, fence)
            return self._result(state)
        except UnknownOutcomeError as exc:
            state = self.store.load_case(scope)
            state["status"] = "blocked"
            state["message"] = str(exc)
            self._save(scope, state, owner, fence)
            return self._result(state)
        except BudgetError as exc:
            state = self.store.load_case(scope)
            state["status"] = "exhausted"
            state["message"] = str(exc)
            self._save(scope, state, owner, fence)
            return self._result(state)
        finally:
            try:
                self.store.release(scope, owner, fence)
            except ConflictError:
                # Lease expired or was taken over; stale code cannot write after
                # that point, and the new owner remains responsible for recovery.
                pass
            self.limits = configured_limits

    def _execute_calls(self, scope: Scope, state: dict[str, Any], calls: list[dict[str, Any]],
                       remote: dict[str, ToolSpec], owner: str, fence: int) -> tuple[dict[str, Any], int]:
        for raw in calls:
            call = ToolCall(raw["id"], raw["name"], raw["arguments"])
            processing_id = raw.get("journal_id", f"m{state['model_calls']}:{call.id}")
            processed = set(state.get("processed_tool_calls", []))
            if processing_id not in processed and state["tool_calls"] >= self.limits.max_tool_calls:
                state["status"] = "exhausted"
                state["message"] = "Tool-call budget exhausted with pending work preserved."
                self._save(scope, state, owner, fence)
                return state, fence
            if processing_id not in processed:
                state.setdefault("processed_tool_calls", []).append(processing_id)
                state["tool_calls"] += 1
                self._save(scope, state, owner, fence)
            spec = next((s for s in _LOCAL_SPECS if s.name == call.name), remote.get(call.name))
            if spec is None:
                state["status"] = "error"
                state["message"] = f"Unknown tool requested: {call.name}"
                self._save(scope, state, owner, fence)
                return state, fence
            try:
                validate_arguments(spec, call.arguments, scope)
            except (ValueError, IsolationError) as exc:
                state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                          "content": json.dumps({"error": "arguments_rejected", "detail": str(exc)})})
                state["status"] = "error"
                state["message"] = f"Tool arguments failed schema or case-identity validation: {exc}"
                self._save(scope, state, owner, fence)
                return state, fence
            if call.name.startswith("case."):
                try:
                    result = self._local_call(scope, state, call, owner, fence)
                except (ValueError, KeyError, ConflictError, IsolationError) as exc:
                    result = {"error": type(exc).__name__, "detail": str(exc)}
                    state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                              "content": json.dumps(result, ensure_ascii=False)})
                    self._save(scope, state, owner, fence)
                    continue
                state = self.store.load_case(scope)
                state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                          "content": json.dumps(result, ensure_ascii=False, default=str)})
                self._save(scope, state, owner, fence)
                continue

            action_id = processing_id
            prior = next((a for a in self.store.actions(scope) if a["id"] == action_id), None)
            try:
                fence = self.store.claim(scope, owner, ttl_seconds=120)
                record = self.store.reserve_action(scope, action_id, call.name, call.arguments, spec.effect,
                                                   owner=owner, fence=fence)
            except UnknownOutcomeError:
                raise
            if prior and prior["status"] == "pending" and spec.effect == "write":
                self.store.unknown_action(scope, action_id, "process stopped after write reservation; reconcile from the actual tool state",
                                          owner=owner, fence=fence)
                raise UnknownOutcomeError(f"write action {action_id!r} was left pending; automatic replay is blocked")
            identity_mismatch = False
            if record["status"] == "completed":
                result = record["result"]
            else:
                try:
                    result = self.tools.call(call.name, call.arguments)
                    # Verify JSON safety before committing the observed result.
                    encoded_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
                    result = json.loads(encoded_result)
                    mismatches = self._result_identity_mismatches(result, scope)
                    if mismatches:
                        identity_mismatch = True
                        result = {"error": "result_identity_mismatch", "mismatched_fields": mismatches,
                                  "detail": "Returned content was quarantined before it entered case context."}
                    fence = self.store.claim(scope, owner, ttl_seconds=120)
                    self.store.finish_action(scope, action_id, result, owner=owner, fence=fence)
                except Exception as exc:
                    if spec.effect == "write":
                        # If the fence was lost, preserve the pending record for
                        # the replacement worker instead of writing stale state.
                        self.store.unknown_action(scope, action_id, f"tool call outcome uncertain: {type(exc).__name__}: {exc}",
                                                  owner=owner, fence=fence)
                        raise UnknownOutcomeError(f"write action {action_id!r} may have executed; reconcile before continuing") from exc
                    result = {"error": type(exc).__name__, "detail": str(exc)}
                    fence = self.store.claim(scope, owner, ttl_seconds=120)
                    self.store.finish_action(scope, action_id, result, owner=owner, fence=fence)
            state = self.store.load_case(scope)
            evidence_id = f"ev:{action_id}"
            evidence = next((item for item in state["evidence"] if item.get("id") == evidence_id), None)
            if evidence is None:
                outcome = "failure" if isinstance(result, dict) and ("error" in result or result.get("isError") is True) else "success"
                evidence = {"id": evidence_id, "scope": scope.to_dict(), "action_id": action_id,
                            "tool": call.name, "effect": spec.effect, "outcome": outcome,
                            "observed_result": result}
                state["evidence"].append(evidence)
            state["messages"].append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                      "evidence_id": evidence_id,
                                      "content": json.dumps({"evidence_id": evidence_id, "outcome": evidence["outcome"],
                                                             "observed_result": result}, ensure_ascii=False, default=str)})
            if identity_mismatch:
                state["status"] = "blocked"
                state["message"] = "A tool returned an explicit patient or case identity outside the active scope; content was quarantined."
            self._save(scope, state, owner, fence)
            if state.get("status") == "blocked":
                return state, fence
        return self.store.load_case(scope), fence

    def _local_call(self, scope: Scope, state: dict[str, Any], call: ToolCall, owner: str, fence: int) -> Any:
        args = call.arguments
        if call.name == "case.add_obligation":
            existing = next((item for item in state["obligations"] if item.get("id") == args["id"]), None)
            proposed = {"id": args["id"], "description": args["description"], "owner": args.get("owner"),
                        "status": "open", "evidence_ids": []}
            if existing and existing != proposed:
                raise ConflictError("obligation ID already exists with different content")
            if not existing:
                state["obligations"].append(proposed)
                self._save(scope, state, owner, fence)
            return {"recorded": True, "obligation": proposed}
        if call.name == "case.close_obligation":
            item = next((item for item in state["obligations"] if item.get("id") == args["id"]), None)
            if item is None:
                raise KeyError("obligation does not exist")
            evidence_by_id = {e["id"]: e for e in state["evidence"]}
            if any(eid not in evidence_by_id or evidence_by_id[eid].get("outcome") != "success" for eid in args["evidence_ids"]):
                raise IsolationError("closure must cite evidence recorded from this case's completed tool actions")
            item["status"] = "closed"
            item["evidence_ids"] = list(dict.fromkeys(args["evidence_ids"]))
            self._save(scope, state, owner, fence)
            return {"closed": True, "id": item["id"], "evidence_ids": item["evidence_ids"]}
        if call.name == "case.read_evidence":
            item = next((item for item in state["evidence"] if item.get("id") == args["id"]), None)
            if item is None:
                raise KeyError("evidence ID is not present in this case")
            serialized = json.dumps(item.get("observed_result"), ensure_ascii=False, sort_keys=True, default=str)
            start = args["offset"]
            end = min(len(serialized), start + args["length"])
            return {"id": item["id"], "offset": start, "total_chars": len(serialized),
                    "text": serialized[start:end], "has_more": end < len(serialized), "outcome": item.get("outcome")}
        if call.name == "case.request_helper":
            if self.composition == "combined":
                raise ValueError("bounded helpers are disabled in combined composition")
            domain_roles = {r["id"]: r for r in roles_for(state["domain"])}
            role = domain_roles.get(args["role_id"])
            if role is None:
                raise ValueError("helper role is not in the current domain's approved catalogue")
            ids = args.get("evidence_ids", [])
            evidence = [e for e in state["evidence"] if e["id"] in ids]
            if len(evidence) != len(set(ids)):
                raise IsolationError("helper evidence IDs must refer only to this case's recorded observations")
            evidence = [item for item in evidence if item.get("outcome") == "success"]
            if len(evidence) != len(set(ids)):
                raise IsolationError("helper context may contain only successful observed tool results")
            if state["model_calls"] >= self.limits.max_model_calls:
                raise BudgetError("model-call budget exhausted before helper request")
            helper_messages = [
                {"role": "system", "content": "Perform bounded read-only analysis. Return a proposal with evidence IDs, unknowns, and limits. Do not execute tools or treat your inference as an observed fact.\n" + json.dumps(role, ensure_ascii=False)},
                {"role": "user", "content": json.dumps({"scope": scope.to_dict(), "question": args["question"], "observations": evidence}, ensure_ascii=False)},
            ]
            if project_context(helper_messages, state, [], self.limits.max_context_chars) is None:
                raise BudgetError("helper context exceeds the configured case context budget")
            state["model_calls"] += 1
            self._save(scope, state, owner, fence)
            try:
                reply = self.model.complete(helper_messages, [], max_output_tokens=min(self.limits.max_output_tokens, 2048))
            except Exception as exc:
                return {"error": "helper_request_failed", "detail": f"{type(exc).__name__}: {exc}"}
            if reply.tool_calls:
                raise ValueError("helper analysis must be read-only and cannot return tool calls")
            self._merge_usage(state, reply.usage)
            self._save(scope, state, owner, fence)
            return {"role_id": role["id"], "proposal": reply.content, "evidence_ids": ids,
                    "warning": "bounded inference; not an observed fact"}
        raise ValueError("unsupported local case operation")

    def _accept_final(self, state: dict[str, Any], content: str) -> dict[str, Any]:
        try:
            payload = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            state["status"] = "unresolved"
            state["message"] = "The model returned prose without the required structured completion record."
            state["final"] = content
            return state
        state["final"] = payload
        if not isinstance(payload, dict) or payload.get("status") != "complete":
            state["status"] = "unresolved"
            state["message"] = "The structured response did not claim scoped completion."
            return state
        claim = payload.get("claim")
        evidence_ids = payload.get("evidence_ids")
        if not isinstance(claim, str) or not claim.strip() or not isinstance(evidence_ids, list) or not evidence_ids:
            state["status"] = "unresolved"
            state["message"] = "Completion requires a claim and supporting observed evidence IDs."
            return state
        if any(not isinstance(evidence_id, str) or not evidence_id for evidence_id in evidence_ids):
            state["status"] = "unresolved"
            state["message"] = "Completion evidence IDs must be non-empty strings."
            return state
        known = {e["id"] for e in state["evidence"]}
        successful = {e["id"] for e in state["evidence"] if e.get("outcome") == "success"}
        if not set(evidence_ids) <= successful:
            state["status"] = "unresolved"
            state["message"] = "Completion cited evidence outside this case's observed action journal."
            return state
        open_items = [o["id"] for o in state["obligations"] if o.get("status") != "closed"]
        if open_items:
            state["status"] = "unresolved"
            state["message"] = "Completion is blocked by open obligations: " + ", ".join(open_items)
            return state
        state["status"] = "complete"
        state["completion"] = {"claim": claim, "evidence_ids": list(dict.fromkeys(evidence_ids)),
                               "scope": state["scope"], "kind": "harness-local scoped claim; not official benchmark success"}
        state["message"] = "The harness accepted a scoped completion claim with case-local observed support."
        return state

    def _tool_map(self) -> dict[str, ToolSpec]:
        specs = self.tools.list_tools()
        names = [spec.name for spec in specs]
        if len(set(names)) != len(names):
            raise ValueError("tool names must be unique before harness execution")
        if set(names) & {spec.name for spec in _LOCAL_SPECS}:
            raise ValueError("remote tools cannot shadow local case operations")
        return {spec.name: spec for spec in specs}

    def _available_specs(self, remote: dict[str, ToolSpec]) -> list[ToolSpec]:
        locals_allowed = [spec for spec in _LOCAL_SPECS if spec.name != "case.request_helper" or self.composition != "combined"]
        return [*remote.values(), *locals_allowed]

    @staticmethod
    def _call_dict(call: ToolCall) -> dict[str, Any]:
        return {"id": call.id, "name": call.name, "arguments": call.arguments}

    @staticmethod
    def _should_request_model(state: dict[str, Any]) -> bool:
        if not state["messages"]:
            return True
        last = state["messages"][-1]
        return last.get("role") != "assistant" or bool(last.get("tool_calls"))

    @staticmethod
    def _pending_tool_calls(state: dict[str, Any]) -> list[dict[str, Any]]:
        for index in range(len(state["messages"]) - 1, -1, -1):
            message = state["messages"][index]
            if message.get("role") == "assistant" and message.get("tool_calls"):
                answered = {m.get("tool_call_id") for m in state["messages"][index + 1:] if m.get("role") == "tool"}
                return [call for call in message["tool_calls"] if call.get("id") not in answered]
        return []

    @staticmethod
    def _result_identity_mismatches(value: Any, scope: Scope) -> list[str]:
        expected = scope.to_dict()
        mismatches: list[str] = []

        def visit(node: Any, path: str = "$") -> None:
            if isinstance(node, dict):
                for key, item in node.items():
                    if key in {"patient_id", "case_id", "patientId", "caseId"}:
                        kind = "patient" if "patient" in key.lower() else "case"
                        if isinstance(item, str) and item != expected[kind]:
                            mismatches.append(f"{path}.{key}")
                    elif key in {"patient", "case"} and isinstance(item, dict) and isinstance(item.get("id"), str):
                        if item["id"] != expected[key]:
                            mismatches.append(f"{path}.{key}.id")
                    visit(item, f"{path}.{key}")
            elif isinstance(node, list):
                for index, item in enumerate(node):
                    visit(item, f"{path}[{index}]")
            elif isinstance(node, str) and node.lstrip().startswith(("{", "[")):
                try:
                    decoded = json.loads(node)
                except json.JSONDecodeError:
                    return
                visit(decoded, f"{path}<json>")

        visit(value)
        return list(dict.fromkeys(mismatches))

    def _save(self, scope: Scope, state: dict[str, Any], owner: str, fence: int) -> None:
        self.store.save_case(scope, state, state["version"], owner=owner, fence=fence)
        state["version"] += 1

    @staticmethod
    def _result(state: dict[str, Any]) -> dict[str, Any]:
        return {"status": state.get("status", "unresolved"), "message": state.get("message", ""),
                "final": state.get("final"), "completion": state.get("completion"),
                "obligations": state.get("obligations", []), "evidence": state.get("evidence", []),
                "model_calls": state.get("model_calls", 0), "tool_calls": state.get("tool_calls", 0),
                "usage": state.get("usage", {}), "version": state.get("version", 0)}

    @staticmethod
    def _merge_usage(state: dict[str, Any], usage: dict[str, Any]) -> None:
        totals = state.setdefault("usage", {})
        if not isinstance(usage, dict):
            return
        for name, value in usage.items():
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                totals[name] = totals.get(name, 0) + value
