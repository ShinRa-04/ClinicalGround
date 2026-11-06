"""Read-only package copy of the approved general responsibility contracts."""

from __future__ import annotations

from functools import lru_cache
import json
from importlib.resources import files
from typing import Any

from .models import Scope

_DOMAINS = {"PA", "UM", "CM"}
_COMPOSITIONS = {"combined", "helpers", "team"}


@lru_cache(maxsize=1)
def _catalogue() -> tuple[dict[str, Any], ...]:
    source = files("health_harness").joinpath("data/micro_roles.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 66:
        raise RuntimeError("packaged responsibility catalogue must contain exactly 66 contracts")
    ids = [item.get("id") for item in data]
    if len(set(ids)) != len(ids) or any(item.get("domain") not in ("PA", "UM", "CM", "SH") for item in data):
        raise RuntimeError("packaged responsibility catalogue has invalid IDs or domains")
    return tuple(data)


def roles_for(domain: str) -> list[dict[str, Any]]:
    key = domain.upper() if isinstance(domain, str) else ""
    if key not in _DOMAINS:
        raise ValueError("domain must be PA, UM, or CM")
    # Return detached records: consumers can annotate their working copy without
    # mutating the shared, versioned general-role catalogue.
    return [dict(role) for role in _catalogue() if role["domain"] in (key, "SH")]


def system_prompt(domain: str, scope: Scope, composition: str = "combined") -> str:
    key = domain.upper() if isinstance(domain, str) else ""
    if key not in _DOMAINS:
        raise ValueError("domain must be PA, UM, or CM")
    if composition not in _COMPOSITIONS:
        raise ValueError("composition must be combined, helpers, or team")
    roles = roles_for(key)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for role in roles:
        grouped.setdefault(_group_name(key, role["id"]), []).append(role)
    role_lines = []
    for group, members in grouped.items():
        role_lines.append(f"\n{group}:")
        role_lines.extend(
            f"- {role['id']} {role['name']}: {role['decision_scope']} Output: {role['output']} "
            f"Boundary: {role['boundary']} Check: {role['completion_check']}"
            for role in members
        )
    scope_json = json.dumps(scope.to_dict(), sort_keys=True, ensure_ascii=False)
    composition_note = {
        "combined": "One case owner performs relevant responsibilities in a single scoped context.",
        "helpers": "The owner may request one focused read-only role analysis at a time, limited to explicitly selected case evidence.",
        "team": "The owner may select several role-scoped workers in one turn; each gets a separate read-only prompt and runs sequentially with the same configured model. This prototype has no concurrent worker processes.",
    }[composition]
    return (
        "You are a task-scoped operational assistant using supplied observations as the authoritative environment. "
        "Do not invent clinical facts, identities, policies, tool outcomes, receipts, availability, or authority. "
        "Separate observed facts, attributed evidence, interpretation, unknowns, and proposed next steps. "
        "Do not claim a draft was sent, a submission was accepted, an appointment was booked, or care was delivered "
        "unless the current scoped observations establish it. Preserve unresolved obligations and source references. "
        "Only work for the case namespace below. No patient-derived context, summaries, habits, or learning may cross cases. "
        "Shared role definitions are read-only general procedures, never patient memory. "
        "Use case.add_obligation for each concrete unfinished requirement and close it only after case-local observed support. "
        "Observed tool results are exposed as evidence IDs of the form ev:m<model-call>:<tool-call-id>; helper analysis is not evidence. "
        "When finished, return one JSON object with status='complete', a narrow claim about this assigned work, and evidence_ids "
        "from successful current-case tool observations. Pure prose, unsupported claims, open obligations, and tool errors remain unresolved. "
        "This is a local harness status, never an official benchmark score or verifier result. "
        f"\n\nCase namespace: {scope_json}\nDomain: {key}\nComposition: {composition_note}\n"
        "Relevant general responsibility groups and contracts:\n" + "\n".join(role_lines)
    )


def _group_name(domain: str, role_id: str) -> str:
    if role_id.startswith("SH-"):
        return "Shared case safeguards"
    number = int(role_id.split("-")[1])
    if domain == "PA":
        if number <= 5: return "PA orientation and applicability"
        if number <= 10: return "PA evidence and coding analysis"
        if number <= 13: return "PA packet and operation"
        return "PA response and episode closure"
    if domain == "UM":
        if number <= 4: return "UM intake and route"
        if number <= 8: return "UM criteria and evidence"
        if number <= 14: return "UM determination and notice"
        return "UM review, effectuation, and closure"
    if number <= 6: return "CM orientation and outreach"
    if number <= 13: return "CM needs and planning"
    if number <= 18: return "CM service handoffs"
    return "CM reconciliation and closure"
