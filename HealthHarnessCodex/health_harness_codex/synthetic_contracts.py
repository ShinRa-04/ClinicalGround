"""Explicit operator-owned completion contracts for synthetic checks only."""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from .models import Scope


def operator_observation_contract(scope: Scope, domain: str, tool: str,
                                 predicates: Sequence[Mapping[str, Any]], *,
                                 phase: str = "final_readback",
                                 branch_id: str = "synthetic_terminal_observation") -> dict[str, Any]:
    """Build a fixed synthetic/operator contract from explicit observed-output predicates.

    This helper is for local demos and synthetic tests. Clinical task contracts
    must use the public-task contract builder instead.
    """
    if not isinstance(scope, Scope):
        raise TypeError("scope must be an explicit Scope")
    if domain not in {"PA", "UM", "CM"}:
        raise ValueError("domain must be PA, UM, or CM")
    if not isinstance(tool, str) or not tool.strip():
        raise ValueError("tool must be a non-empty name")
    if phase not in {"any", "final_readback", "terminal_write_response"}:
        raise ValueError("phase must be a supported evidence phase")
    if not isinstance(branch_id, str) or not branch_id.strip():
        raise ValueError("branch_id must be non-empty")
    if not isinstance(predicates, Sequence) or isinstance(predicates, (str, bytes)) or not predicates:
        raise ValueError("at least one explicit terminal predicate is required")
    requirements = []
    for index, source in enumerate(predicates):
        if not isinstance(source, Mapping):
            raise TypeError("each predicate must be an object")
        path = source.get("path")
        op = source.get("op")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("predicate path must be non-empty")
        if op not in {"eq", "in", "present", "truthy", "nonempty"}:
            raise ValueError("predicate operation is not supported for synthetic contracts")
        predicate = {"path": path, "op": op, "value": source.get("value")}
        json.dumps(predicate, ensure_ascii=False, allow_nan=False)
        requirements.append({"id": str(source.get("id") or f"terminal_predicate_{index + 1}"),
                             "tools": [tool], "phase": phase, "predicate": predicate})
    proof_kind = "terminal_write_response" if phase == "terminal_write_response" else "fresh_case_readback"
    return {
        "version": 1,
        "task_id": scope.task,
        "domain": domain,
        "mapping_status": "mapped",
        "verified_task_goal": True,
        "role_workflow_context": "explicit operator-owned synthetic observation",
        "mapping_basis": "synthetic fixture terminal output predicates",
        "endpoint_kind": "synthetic_operator_observation",
        "scope": scope.to_dict(),
        "branches": [{"id": branch_id, "proof_kind": proof_kind,
                       "requirements": requirements}],
    }
