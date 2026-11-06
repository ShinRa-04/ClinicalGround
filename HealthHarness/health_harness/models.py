"""Shared immutable contracts and errors for the local healthcare harness."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Literal


class HarnessError(Exception):
    """Base class for expected harness failures."""


class IsolationError(HarnessError):
    """Raised when data or an operation crosses its declared case scope."""


class ConflictError(HarnessError):
    """Raised when an optimistic update or lease ownership check fails."""


class UnknownOutcomeError(HarnessError):
    """An external write may have happened; it must be reconciled, not replayed."""


class BudgetError(HarnessError):
    """A configured execution budget has been exhausted."""


@dataclass(frozen=True, slots=True)
class Scope:
    environment: str
    task: str
    organization: str
    principal: str
    patient: str
    case: str

    def __post_init__(self) -> None:
        for name in ("environment", "task", "organization", "principal", "patient", "case"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"scope {name} must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        return {name: getattr(self, name) for name in ("environment", "task", "organization", "principal", "patient", "case")}

    @property
    def key(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    effect: Literal["read", "write"] = "read"
    identity_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("tool name must be a non-empty string")
        if self.effect not in ("read", "write"):
            raise ValueError("tool effect must be 'read' or 'write'")
        if not isinstance(self.input_schema, dict):
            raise TypeError("input_schema must be a JSON schema object")
        object.__setattr__(self, "identity_fields", tuple(self.identity_fields))


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ModelReply:
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    usage: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_calls", tuple(self.tool_calls))


@dataclass(frozen=True, slots=True)
class Limits:
    max_model_calls: int = 30
    max_tool_calls: int = 100
    max_context_chars: int = 60000
    max_output_tokens: int = 4096

    def __post_init__(self) -> None:
        for name in ("max_model_calls", "max_tool_calls", "max_context_chars", "max_output_tokens"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
