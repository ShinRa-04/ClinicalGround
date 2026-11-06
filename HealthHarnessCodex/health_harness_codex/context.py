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
    messages = [m for m in messages if not m.get('helper_job_id')]
    if len(messages) < 2:
        return None
    if max_chars==0:max_chars=float('inf')
    from .working_set import clinical, normalize_message, project_working_context
    if clinical(state):
        return project_working_context(messages, state, tools, max_chars, _turn_groups)
    messages = [normalize_message(m) for m in messages]
    evidence_index = []
    for evidence in state.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        entry = {"id": evidence.get("id"), "tool": evidence.get("tool"),
                 "outcome": evidence.get("outcome"), "action_id": evidence.get("action_id")}
        entry.update(_safe_source_metadata(evidence.get("observed_result")))
        evidence_index.append(entry)
    from .authorized_statements import view as statement_view
    manifest = {
        "authorized_statements": statement_view(state),
        "case_scope": state.get("scope"),
        "observed_identity_binding": state.get("identity_bindings", {}),
        "observed_principal_binding": state.get("principal_bindings", {}),
        "observed_case_binding": state.get("case_bindings", {}),
        "open_obligations": [o for o in state.get("obligations", []) if o.get("status") not in {"closed", "deferred"}],
        "evidence_index": evidence_index,
        "instruction": "Evidence previews are partial. Search with the original evidence ID, then rehydrate with that same ID and returned offset; local reads add no evidence.",
    }
    deferred = [o for o in state.get("obligations", []) if o.get("status") == "deferred"]
    if deferred:
        manifest["deferred_obligations"] = deferred
    if state.get("workflow_capabilities", {}).get("new_request_creation") or state.get("workflow_recoveries"):
        manifest["workflow_execution"] = {
            "capabilities": state.get("workflow_capabilities", {}),
            "recovery_turns": len(state.get("workflow_recoveries", [])),
            "ready_obligations": [item["id"] for item in state.get("obligations", [])
                                  if item.get("status") == "open" and all(
                                      any(other["id"] == dep and other.get("status") == "closed"
                                          for other in state.get("obligations", []))
                                      for dep in item.get("depends_on", []))],
        }
    contract = state.get("completion_contract")
    if contract is not None:
        manifest["trusted_completion_contract"] = contract
        manifest["completion_verification"] = state.get("completion_gate")
        manifest["completion_rule"] = (
            "The harness accepts complete only when this fixed contract's milestones have successful same-case "
            "support and required readbacks follow the latest write.")
    else:
        manifest["completion_rule"] = "No trusted task contract is present, so complete claims remain unresolved."
    prefix = [dict(messages[0]), dict(messages[1])]
    prefix[0]["content"] = str(prefix[0].get("content", "")) + "\n\nCurrent case ledger (source index and open obligations):\n" + json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    groups = _turn_groups(messages[2:])
    schemas = _tool_schemas(tools)
    base = {"messages": prefix, "tool_schemas": schemas}
    if _size(base) > max_chars:
        return None
    raw_groups = [group for group in groups]
    raw_messages = prefix + [message for group in raw_groups for message in group]
    if _size({"messages": raw_messages, "tool_schemas": schemas}) <= max_chars:
        return raw_messages
    if not groups:
        return prefix

    newest = groups[-1]
    newest_candidate = prefix + newest
    if _size({"messages": newest_candidate, "tool_schemas": schemas}) <= max_chars:
        selected = [newest]
    else:
        compact_newest = _compact_group(newest, state, large_tool_chars, force=True)
        newest_candidate = prefix + compact_newest
        if compact_newest == newest or _size({"messages": newest_candidate, "tool_schemas": schemas}) > max_chars:
            return None
        selected = [compact_newest]

    for group in reversed(groups[:-1]):
        raw_candidate = [group, *selected]
        candidate_messages = prefix + [message for chosen in raw_candidate for message in chosen]
        if _size({"messages": candidate_messages, "tool_schemas": schemas}) <= max_chars:
            selected = raw_candidate
            continue
        compacted = _compact_group(group, state, large_tool_chars, force=True)
        if compacted == group:
            continue
        compact_candidate = [compacted, *selected]
        candidate_messages = prefix + [message for chosen in compact_candidate for message in chosen]
        if _size({"messages": candidate_messages, "tool_schemas": schemas}) <= max_chars:
            selected = compact_candidate
    projected_messages = prefix + [message for group in selected for message in group]
    if _size({"messages": projected_messages, "tool_schemas": schemas}) > max_chars:
        return None
    return projected_messages


def _turn_groups(messages: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    index = 0
    while index < len(messages):
        message = messages[index]
        group = [message]
        index += 1
        if message.get("role") == "tool":
            continue
        if message.get("role") == "assistant" and message.get("tool_calls"):
            call_ids_list = [call.get("id") for call in message["tool_calls"] if isinstance(call, dict)]
            call_ids = set(call_ids_list)
            seen: set[Any] = set()
            complete = bool(call_ids) and len(call_ids) == len(call_ids_list)
            while index < len(messages) and messages[index].get("role") == "tool":
                tool_message = messages[index]
                tool_call_id = tool_message.get("tool_call_id")
                if tool_call_id not in call_ids or tool_call_id in seen:
                    complete = False
                else:
                    group.append(tool_message)
                    seen.add(tool_call_id)
                index += 1
                if call_ids <= seen:
                    break
            if complete and call_ids <= seen:
                groups.append(group)
            continue
        groups.append(group)
    return groups


def _compact_group(group: list[dict[str, Any]], state: dict[str, Any], limit: int,
                   force: bool = False) -> list[dict[str, Any]]:
    by_id = {e["id"]: e for e in state.get("evidence", [])}
    output = []
    changed = False
    for message in group:
        copy = dict(message)
        content = copy.get("content")
        if copy.get("role") == "tool" and isinstance(content, str) and (force or len(content) > limit):
            evidence_id = copy.get("evidence_id")
            evidence = by_id.get(evidence_id)
            if evidence:
                preview = content[:min(240, max(1, limit))]
                successful = evidence.get("outcome") == "success"
                copy["content"] = json.dumps({
                    "evidence_id": evidence_id,
                    "tool": evidence.get("tool"),
                    "outcome": evidence.get("outcome"),
                    "omitted_chars": max(0, len(content) - len(preview)),
                    "partial_preview": preview,
                    "preview_is_partial": len(content) > len(preview),
                    "source_metadata": _safe_source_metadata(evidence.get("observed_result")),
                    "instruction": ("This is a partial preview. Search with case.search_evidence, then rehydrate with case.read_evidence using this same original evidence ID and returned source offset. Neither local operation creates a new evidence ID."
                                    if successful else "This is a partial preview of failed evidence; it cannot be rehydrated as successful support."),
                }, ensure_ascii=False)
                if len(copy["content"]) >= len(content):
                    copy["content"] = content
                else:
                    changed = True
        output.append(copy)
    return output if changed else group


def _safe_source_metadata(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {}
    source = result.get("structuredContent") if isinstance(result.get("structuredContent"), dict) else result
    metadata: dict[str, Any] = {}
    for source_key, output_key in (("path", "source_path"), ("sha256", "source_sha256"),
                                   ("extraction_method", "source_extraction_method")):
        value = source.get(source_key)
        if isinstance(value, str) and value:
            metadata[output_key] = value[:500]
    for source_key, output_key in (("total_pages", "source_total_pages"), ("page_start", "source_page_start")):
        value = source.get(source_key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            metadata[output_key] = value
    pages = source.get("pages")
    if isinstance(pages, list):
        page_numbers = [page.get("page") for page in pages if isinstance(page, dict)
                        and isinstance(page.get("page"), int) and not isinstance(page.get("page"), bool)]
        if page_numbers:
            metadata["source_pages"] = page_numbers[:50]
    for source_key in ("truncated", "has_more", "text_layer_only", "ocr_performed", "no_layout_validation"):
        value = source.get(source_key)
        if isinstance(value, bool):
            metadata["source_" + source_key] = value
    return metadata


def _tool_schemas(tools: list[ToolSpec]) -> list[dict[str, Any]]:
    return [{"name": t.name, "description": t.description, "input_schema": t.input_schema,
             "effect": t.effect, "identity_fields": t.identity_fields} for t in tools]


def _size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, default=str))
