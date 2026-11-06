"""Shared immutable contracts and errors for the local healthcare harness."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Literal, TypedDict


class CompletionRequirement(TypedDict, total=False):
    """Publicly derived terminal milestone checked against observed case evidence."""

    id: str
    tools: list[str]
    predicate: dict[str, Any]
    phase: Literal["any", "terminal_write_response", "final_readback", "before_write"]
    before_tools: list[str]


class CompletionBranch(TypedDict):
    id: str
    requirements: list[CompletionRequirement]
    proof_kind: Literal["terminal_write_response", "fresh_case_readback"]


class CompletionContract(TypedDict, total=False):
    """Trusted task contract; model replies cannot create or change this value."""

    version: int
    task_id: str
    domain: str
    instruction_sha256: str
    mapping_status: Literal["mapped", "unverified"]
    verified_task_goal: bool
    role_workflow_context: str | None
    branches: list[CompletionBranch]
    source_refs: list[str]


class CompletionGateResult(TypedDict, total=False):
    accepted: bool
    branch_id: str | None
    missing_milestones: list[str]
    reason_code: str


class HarnessError(Exception):
    """Base class for expected harness failures."""


class IsolationError(HarnessError):
    """Raised when data or an operation crosses its declared case scope."""


class ConflictError(HarnessError):
    """Raised when an optimistic update or lease ownership check fails."""


class UnknownOutcomeError(HarnessError):
    """An external write may have happened; it must be reconciled, not replayed."""


class WorldUnavailableError(HarnessError):
    """The task runtime cannot support further inference or tool execution."""

    def __init__(self, reason='unavailable'):
        self.reason=reason if reason in {'stopped','unavailable','unverified'} else 'unavailable'
        super().__init__('Task world is '+self.reason+'; preserve its state and stop further requests.')


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
    max_context_chars: int = 0
    max_output_tokens: int = 4000

    def __post_init__(self) -> None:
        for name in ("max_model_calls", "max_tool_calls", "max_context_chars", "max_output_tokens"):
            value = getattr(self, name)
            if name=='max_context_chars' and type(value) is int and value==0:continue
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")


def budget_is_reduction(name: str, proposed: int, previous: int) -> bool:
    """Zero context budget means no harness cap, rather than a smaller budget."""
    if name=='max_context_chars':
        return proposed!=0 and (previous==0 or proposed<previous)
    return proposed<previous
