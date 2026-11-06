"""Deterministic context projection; the complete audit record stays in SQLite."""

from __future__ import annotations

import json
from typing import Any

from .models import ToolSpec


def project_context(messages: list[dict[str, Any]], state: dict[str, Any], tools: list[ToolSpec], max_chars: int,
                    large_tool_chars: int = 2500) -> list[dict[str, Any]] | None:
    """Keep the original request, current ledger, and newest complete turns.

    This is a deterministic projection, not a semantic summary. Full messages
    and evidence remain persisted; omitted tool output can be rehydrated by ID.
    """
    if len(messages) < 2:
        return None
    manifest = {
        "case_scope": state.get("scope"),
        "open_obligations": [o for o in state.get("obligations", []) if o.get("status") != "closed"],
        "evidence_index": [{"id": e["id"], "tool": e.get("tool"), "outcome": e.get("outcome"),
                            "action_id": e.get("action_id")} for e in state.get("evidence", [])],
        "instruction": "Use case.read_evidence with an evidence ID and character offset to rehydrate omitted tool output.",
    }
    prefix = [dict(messages[0]), dict(messages[1])]
    prefix[0]["content"] = str(prefix[0].get("content", "")) + "\n\nCurrent case ledger (source index and open obligations):\n" + json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    groups = _turn_groups(messages[2:])
    selected: list[list[dict[str, Any]]] = []
    base = {"messages": prefix, "tool_schemas": _tool_schemas(tools)}
    if _size(base) > max_chars:
        return None
    for group in reversed(groups):
        candidate_groups = [group, *reversed(selected)]
        candidate_messages = prefix + [m for g in candidate_groups for m in g]
        projected = _summarize_large_tools(candidate_messages, state, large_tool_chars)
        if _size({"messages": projected, "tool_schemas": _tool_schemas(tools)}) > max_chars:
            break
        selected.append(group)
    ordered_groups = list(reversed(selected))
    projected_messages = prefix + [m for group in ordered_groups for m in group]
    projected_messages = _summarize_large_tools(projected_messages, state, large_tool_chars)
    if _size({"messages": projected_messages, "tool_schemas": _tool_schemas(tools)}) > max_chars:
        return None
    return projected_messages


def _turn_groups(messages: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    index = 0
    while index < len(messages):
        message = messages[index]
        group = [message]
        index += 1
        if message.get("role") == "assistant" and message.get("tool_calls"):
            call_ids = {call.get("id") for call in message["tool_calls"]}
            seen: set[Any] = set()
            while index < len(messages) and messages[index].get("role") == "tool":
                group.append(messages[index])
                seen.add(messages[index].get("tool_call_id"))
                index += 1
                if call_ids <= seen:
                    break
        groups.append(group)
    return groups


def _summarize_large_tools(messages: list[dict[str, Any]], state: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    by_id = {e["id"]: e for e in state.get("evidence", [])}
    output = []
    for message in messages:
        copy = dict(message)
        content = copy.get("content")
        if copy.get("role") == "tool" and isinstance(content, str) and len(content) > limit:
            evidence_id = copy.get("evidence_id")
            evidence = by_id.get(evidence_id)
            if evidence:
                copy["content"] = json.dumps({"evidence_id": evidence_id, "tool": evidence.get("tool"),
                                               "outcome": evidence.get("outcome"),
                                               "omitted_chars": len(content),
                                               "instruction": "Rehydrate with case.read_evidence."}, ensure_ascii=False)
        output.append(copy)
    return output


def _tool_schemas(tools: list[ToolSpec]) -> list[dict[str, Any]]:
    return [{"name": t.name, "description": t.description, "input_schema": t.input_schema,
             "effect": t.effect, "identity_fields": t.identity_fields} for t in tools]


def _size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, default=str))
