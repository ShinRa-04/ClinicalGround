"""Fail-closed resolution of actor-observed patient identity for one case."""

from __future__ import annotations

import json
from typing import Any

from .models import Scope


_MAX_JSON_TEXT = 1_000_000
_MAX_NODES = 100_000
_MAX_DEPTH = 64


class IdentityResolutionError(ValueError):
    """An actor result contains contradictory or unsafe identity evidence."""


def resolve_patient_identity(result: Any, scope: Scope,
                             existing_patient_id: str | None = None) -> str | None:
    """Resolve a patient ID only from one object binding it to ``scope.case``.

    Supported roots include ordinary dictionaries, MCP ``structuredContent``,
    and JSON objects carried in MCP ``content[].text``. Duplicate encodings are
    harmless. The internal case-subject namespace in ``scope.patient`` is never
    returned as an observed patient ID.

    Conflicting case IDs, patient IDs, or an ID conflicting with an already
    resolved mapping reject the entire payload. Unbound patient IDs never
    establish a mapping; callers may retain an explicitly resolved existing ID.
    """
    if not isinstance(scope, Scope):
        raise TypeError("scope must be a Scope")
    existing = _validate_candidate_id(existing_patient_id, scope, "existing patient ID")
    roots = _result_roots(result)
    case_ids: set[str] = set()
    patient_ids: set[str] = set()
    bound_patient_ids: set[str] = set()
    visited = 0

    def walk(node: Any, depth: int = 0, is_case_object: bool = False) -> None:
        nonlocal visited
        visited += 1
        if visited > _MAX_NODES or depth > _MAX_DEPTH:
            raise IdentityResolutionError("actor identity payload exceeds safe traversal bounds")
        if isinstance(node, dict):
            local_cases = _identifiers(node, "case", include_object_id=is_case_object)
            local_patients = _identifiers(node, "patient")
            case_ids.update(local_cases)
            patient_ids.update(local_patients)
            if scope.case in local_cases:
                bound_patient_ids.update(local_patients)
            for key, child in node.items():
                walk(child, depth + 1, is_case_object=(key == "case" and isinstance(child, dict)))
        elif isinstance(node, list):
            for child in node:
                walk(child, depth + 1, is_case_object=False)

    for root in roots:
        walk(root)

    if any(case_id != scope.case for case_id in case_ids):
        raise IdentityResolutionError("actor identity payload contains a case ID outside the active case")
    if len(patient_ids) > 1:
        raise IdentityResolutionError("actor identity payload contains conflicting patient IDs")
    if existing and patient_ids and patient_ids != {existing}:
        raise IdentityResolutionError("actor identity payload conflicts with the resolved patient mapping")
    if len(bound_patient_ids) > 1:
        raise IdentityResolutionError("actor identity payload binds multiple patient IDs to the active case")
    if not bound_patient_ids:
        return existing

    resolved = next(iter(bound_patient_ids))
    if resolved.startswith("case-subject:"):
        raise IdentityResolutionError("internal case-subject namespace cannot be adopted as a patient ID")
    if existing and resolved != existing:
        raise IdentityResolutionError("actor identity payload conflicts with the resolved patient mapping")
    return resolved


def validate_patient_identity_result(result: Any, scope: Scope, patient_id: str) -> str:
    """Require ``patient_id`` to be explicitly bound to this case in ``result``."""
    candidate = _validate_candidate_id(patient_id, scope, "patient ID")
    resolved = resolve_patient_identity(result, scope)
    if resolved is None:
        raise IdentityResolutionError("actor identity payload does not bind a patient ID to the active case")
    if resolved != candidate:
        raise IdentityResolutionError("actor identity payload does not validate the requested patient ID")
    return resolved


def resolve_patient_identity_at_path(result: Any, scope: Scope, path: tuple[str, ...],
                                     existing_patient_id: str | None = None) -> str | None:
    """Resolve a patient only from one explicitly trusted nested actor record.

    Unlike ``resolve_patient_identity``, this function never searches other
    response roots, sibling objects, or JSON text for a binding. Callers use it
    only for a tool-specific authoritative record path.
    """
    if not isinstance(path, tuple) or not path or any(not isinstance(part, str) or not part for part in path):
        raise ValueError("trusted identity path must be a non-empty tuple of object keys")
    node = result
    for part in path:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    if not isinstance(node, dict):
        return None
    case_id = node.get("id")
    if not isinstance(case_id, str) or not case_id.strip():
        return None
    if case_id != scope.case:
        raise IdentityResolutionError("trusted patient source record ID does not match the active case")
    patient_id = node.get("patient_id")
    if patient_id is None:
        return None
    normalized = {"case": {"id": case_id, "patient_id": patient_id}}
    return resolve_patient_identity(normalized, scope, existing_patient_id)


def resolve_actual_case_id(result: Any, scope: Scope) -> str:
    """Resolve a provider case only from its trusted case-creation result.

    The initial provider scope is patient-bound and uses
    ``case-subject:<patient_id>`` only as an internal namespace. This resolver
    requires the raw result to bind one real case ID and that same active
    patient ID in the same actor-returned object.
    """
    if not isinstance(scope, Scope):
        raise TypeError("scope must be a Scope")
    if (not scope.patient or scope.patient.startswith("case-subject:")
            or scope.case != f"case-subject:{scope.patient}"):
        raise IdentityResolutionError("scope is not an unbound patient-subject case namespace")

    roots = _result_roots(result)
    case_ids: set[str] = set()
    patient_ids: set[str] = set()
    bindings: set[tuple[str, str]] = set()
    visited = 0

    def walk(node: Any, depth: int = 0, is_case_object: bool = False) -> None:
        nonlocal visited
        visited += 1
        if visited > _MAX_NODES or depth > _MAX_DEPTH:
            raise IdentityResolutionError("actor case-binding payload exceeds safe traversal bounds")
        if isinstance(node, dict):
            local_cases = _identifiers(node, "case", include_object_id=is_case_object)
            local_patients = _identifiers(node, "patient")
            case_ids.update(local_cases)
            patient_ids.update(local_patients)
            bindings.update((case_id, patient_id) for case_id in local_cases for patient_id in local_patients)
            for key, child in node.items():
                walk(child, depth + 1, is_case_object=(key == "case" and isinstance(child, dict)))
        elif isinstance(node, list):
            for child in node:
                walk(child, depth + 1, is_case_object=False)

    for root in roots:
        walk(root)
    if not case_ids:
        raise IdentityResolutionError("case creation result did not include an actual case ID")
    if any(case_id.startswith("case-subject:") for case_id in case_ids):
        raise IdentityResolutionError("internal case-subject namespace cannot be adopted as an actual case ID")
    if len(case_ids) != 1:
        raise IdentityResolutionError("case creation result contains conflicting case IDs")
    if patient_ids != {scope.patient}:
        raise IdentityResolutionError("case creation result contains a missing or conflicting patient identity")
    actual_case_id = next(iter(case_ids))
    if bindings != {(actual_case_id, scope.patient)}:
        raise IdentityResolutionError("case creation result does not bind the actual case to the active patient")
    return actual_case_id


def _validate_candidate_id(value: str | None, scope: Scope, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise IdentityResolutionError(f"{label} must be a non-empty string")
    if value.startswith("case-subject:"):
        raise IdentityResolutionError("internal case-subject namespace cannot be adopted as a patient ID")
    return value


def _result_roots(result: Any) -> list[Any]:
    roots = [result]
    if isinstance(result, dict):
        structured = result.get("structuredContent")
        if structured is not None:
            roots.append(structured)
        content = result.get("content")
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    if len(text.encode("utf-8")) > _MAX_JSON_TEXT:
                        raise IdentityResolutionError("actor identity JSON text exceeds the configured size bound")
                    try:
                        decoded = json.loads(text)
                    except (json.JSONDecodeError, RecursionError):
                        continue
                    roots.append(decoded)
    return roots


def _identifiers(record: dict[str, Any], kind: str, include_object_id: bool = False) -> set[str]:
    if kind == "case":
        names = ("case_id", "caseId")
        object_name = "case"
    else:
        names = ("patient_id", "patientId")
        object_name = "patient"
    found: set[str] = set()
    for name in names:
        if name in record:
            found.add(_identity_value(record[name], f"{name}"))
    if kind == "case" and include_object_id and "id" in record:
        found.add(_identity_value(record["id"], "case.id"))
    if object_name in record:
        value = record[object_name]
        if isinstance(value, str):
            found.add(_identity_value(value, object_name))
        elif isinstance(value, dict) and "id" in value:
            found.add(_identity_value(value["id"], f"{object_name}.id"))
    return found


def _identity_value(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IdentityResolutionError(f"actor identity field {field} is not a non-empty string")
    return value
