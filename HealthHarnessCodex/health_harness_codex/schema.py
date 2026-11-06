"""Strict JSON-schema subset and case-identity validation for tool arguments."""

from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any

from .models import IsolationError, Scope, ToolSpec

_ANNOTATIONS = {"$schema", "$id", "title", "description", "default", "examples", "deprecated", "readOnly", "writeOnly", "discriminator"}
_SUPPORTED = {
    "type", "properties", "required", "additionalProperties", "items", "enum", "const",
    "minLength", "maxLength", "pattern", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minItems", "maxItems", "uniqueItems", "minProperties", "maxProperties", "anyOf", "oneOf", "allOf",
    "$ref", "$defs", "definitions", "format",
}
_RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_RFC3339_DATE = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
_ALIASES = {
    "environment_id": "environment", "env": "environment",
    "task_id": "task", "episode": "task", "episode_id": "task",
    "organization_id": "organization", "org": "organization", "org_id": "organization",
    "principal_id": "principal", "user_id": "principal", "actor": "principal",
    "patient_id": "patient", "case_id": "case",
}


class UnexpectedParameterError(ValueError):
    """A named tool parameter is undeclared; never echo the supplied key/value."""

    def __init__(self, allowed_fields):
        self.allowed_fields = tuple(sorted(allowed_fields))
        super().__init__("undeclared top-level tool parameter")


def tool_parameter_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Close implicit function parameter maps, preserving explicitly open maps.

    This is an adapter contract approved by the operator, not JSON Schema's
    default semantics. Apply only to the parameter root, never nested data maps.
    Do not mutate the published source schema or make optional values required.
    """
    if "additionalProperties" in schema:
        return schema
    parameter_root = schema
    seen = set()
    while "$ref" in parameter_root and not isinstance(parameter_root.get("properties"), dict):
        ref = parameter_root["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/") or ref in seen:
            return schema  # ordinary schema validation reports invalid references
        seen.add(ref)
        target = schema
        for part in ref[2:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            if not isinstance(target, dict) or part not in target:
                return schema
            target = target[part]
        if not isinstance(target, dict):
            return schema
        parameter_root = target
    props = parameter_root.get("properties")
    if isinstance(props, dict) and parameter_root.get("additionalProperties", False) is False:
        return {**schema, "properties": props, "additionalProperties": False}
    return schema


def validate_arguments(spec: ToolSpec, arguments: dict[str, Any], scope: Scope) -> None:
    """Raise ValueError for schema violations and IsolationError for identity mismatch.

    Unsupported schema assertions fail closed. Schema annotations are accepted
    but do not confer permission; the actual tool remains the authority gate.
    """
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be a JSON object")
    _json_key(arguments)
    if scope.case.startswith("case-subject:"):
        _reject_internal_case_namespace(arguments, scope.case)
    parameter_schema = tool_parameter_schema(spec.input_schema)
    expanded_schema = _expand_refs(parameter_schema)
    _preflight_schema(expanded_schema, "$", 0)
    props = parameter_schema.get("properties")
    if (isinstance(props, dict) and parameter_schema.get("additionalProperties") is False
            and set(arguments) - set(props)):
        raise UnexpectedParameterError(props)
    _validate_schema(expanded_schema, arguments, "$", 0)
    scope_values = scope.to_dict()
    _validate_declared_identity_values(arguments, scope_values)
    for declared in spec.identity_fields:
        path = _parse_path(declared)
        actual = _lookup(arguments, path)
        leaf = path[-1]
        canonical = _ALIASES.get(leaf, leaf)
        if canonical not in scope_values:
            raise ValueError(f"identity field {declared!r} does not identify a known scope component")
        expected = scope_values[canonical]
        if not isinstance(actual, str) or actual != expected:
            raise IsolationError(f"tool identity field {declared!r} does not match current case scope")


def _validate_schema(schema: Any, value: Any, path: str, depth: int) -> None:
    if depth > 32:
        raise ValueError("schema nesting exceeds supported depth")
    if not isinstance(schema, dict):
        raise ValueError(f"schema at {path} must be an object")
    for union_key in ("anyOf", "oneOf", "allOf"):
        if union_key in schema:
            branches = schema[union_key]
            if not isinstance(branches, list) or not branches:
                raise ValueError(f"{union_key} at {path} must be a non-empty array")
            results = []
            for branch in branches:
                try:
                    _validate_schema(branch, value, path, depth + 1)
                    results.append(True)
                except ValueError:
                    results.append(False)
            matches = sum(results)
            if (union_key == "anyOf" and matches < 1) or (union_key == "oneOf" and matches != 1) or (union_key == "allOf" and matches != len(branches)):
                raise ValueError(f"value at {path} does not satisfy {union_key}")
    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(expected_type, value):
        raise ValueError(f"expected {expected_type} at {path}, got {_type_name(value)}")
    if schema.get("format") == "date-time" and isinstance(value, str) and not _is_rfc3339_date_time(value):
        raise ValueError(f"string at {path} must be a timezone-qualified RFC 3339 date-time")
    if schema.get('format')=='date' and isinstance(value,str):
        try:
            if not _RFC3339_DATE.fullmatch(value):raise ValueError()
            date.fromisoformat(value)
        except ValueError:raise ValueError(f'string at {path} must be a valid RFC 3339 calendar date') from None
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"value at {path} does not match const")
    if "enum" in schema:
        enum = schema["enum"]
        if not isinstance(enum, list) or not any(_json_equal(value, item) for item in enum):
            raise ValueError(f"value at {path} is not an allowed enum value")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        if not isinstance(props, dict):
            raise ValueError(f"properties at {path} must be an object")
        required = schema.get("required", [])
        if not isinstance(required, list) or any(not isinstance(k, str) for k in required):
            raise ValueError(f"required at {path} must be an array of strings")
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError(f"missing required field(s) at {path}: {', '.join(missing)}")
        if len(value) < schema.get("minProperties", 0) or len(value) > schema.get("maxProperties", math.inf):
            raise ValueError(f"object property count at {path} is out of bounds")
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                _validate_schema(props[key], item, f"{path}.{key}", depth + 1)
            elif additional is False:
                raise ValueError(f"unexpected field at {path}: {key}")
            elif isinstance(additional, dict):
                _validate_schema(additional, item, f"{path}.{key}", depth + 1)
            elif additional is not True:
                raise ValueError(f"additionalProperties at {path} must be boolean or schema")
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", math.inf):
            raise ValueError(f"array length at {path} is out of bounds")
        if schema.get("uniqueItems") is True:
            if len({_json_key(item) for item in value}) != len(value):
                raise ValueError(f"array at {path} contains duplicate items")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_schema(schema["items"], item, f"{path}[{index}]", depth + 1)
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", math.inf):
            raise ValueError(f"string length at {path} is out of bounds")
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], value) is None:
                    raise ValueError(f"string at {path} does not match pattern")
            except re.error as exc:
                raise ValueError(f"invalid pattern at {path}") from exc
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value):
            raise ValueError(f"number at {path} must be finite")
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"number at {path} is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"number at {path} exceeds maximum")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            raise ValueError(f"number at {path} does not exceed exclusiveMinimum")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            raise ValueError(f"number at {path} does not satisfy exclusiveMaximum")


def _matches_type(expected: Any, value: Any) -> bool:
    expected_types = expected if isinstance(expected, list) else [expected]
    if any(not isinstance(t, str) for t in expected_types):
        raise ValueError("schema type must be a string or array of strings")
    allowed = {"object", "array", "string", "integer", "number", "boolean", "null"}
    if set(expected_types) - allowed:
        raise ValueError("unsupported JSON schema type")
    return any({
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda: isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": lambda: isinstance(value, bool),
        "null": lambda: value is None,
    }[kind]() for kind in expected_types)


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return "integer" if isinstance(value, int) else "number" if isinstance(value, float) else "string"


def _is_rfc3339_date_time(value: str) -> bool:
    if _RFC3339_DATE_TIME.fullmatch(value) is None:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _parse_path(path: str) -> list[str]:
    if not isinstance(path, str) or not path:
        raise ValueError("identity paths must be non-empty strings")
    if path.startswith("/"):
        parts = [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]
    else:
        parts = path.split(".")
    if any(not part for part in parts):
        raise ValueError(f"invalid identity path: {path!r}")
    return parts


def _lookup(root: Any, path: list[str]) -> Any:
    value = root
    for part in path:
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        else:
            raise IsolationError(f"declared identity path {'/'.join(path)!r} is missing")
    return value


def _validate_declared_identity_values(value: Any, scope_values: dict[str, str], path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            canonical = _ALIASES.get(key, key)
            expected = scope_values.get(canonical)
            if expected is not None and key in _ALIASES:
                if item != expected:
                    raise IsolationError(f"argument identity at {path}.{key} does not match current case scope")
            if key in {"patient", "case"} and isinstance(item, dict) and "id" in item:
                if item["id"] != scope_values[key]:
                    raise IsolationError(f"argument identity at {path}.{key}.id does not match current case scope")
            _validate_declared_identity_values(item, scope_values, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_declared_identity_values(item, scope_values, f"{path}[{index}]")


def _reject_internal_case_namespace(value: Any, internal_case: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"case_id", "caseId"} and item == internal_case:
                raise IsolationError("internal case-subject namespace cannot be sent as an actor case ID")
            if key == "case" and isinstance(item, dict) and item.get("id") == internal_case:
                raise IsolationError("internal case-subject namespace cannot be sent as an actor case ID")
            _reject_internal_case_namespace(item, internal_case)
    elif isinstance(value, list):
        for item in value:
            _reject_internal_case_namespace(item, internal_case)


def _json_key(value: Any) -> str:
    import json
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("tool arguments must contain JSON-compatible values") from exc


def _json_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        return left == right
    return type(left) is type(right) and left == right


def _expand_refs(schema: Any) -> Any:
    root = schema

    def expand(node: Any, refs: tuple[str, ...], depth: int) -> Any:
        if depth > 32 or not isinstance(node, dict):
            raise ValueError("schema reference nesting exceeds supported depth or contains a non-object")
        if "$ref" in node:
            ref = node["$ref"]
            if not isinstance(ref, str) or not ref.startswith("#/"):
                raise ValueError("only local JSON Pointer schema references are supported")
            if ref in refs:
                raise ValueError(f"recursive schema reference is unsupported: {ref}")
            target: Any = root
            for segment in ref[2:].split("/"):
                segment = segment.replace("~1", "/").replace("~0", "~")
                if not isinstance(target, dict) or segment not in target:
                    raise ValueError(f"unresolved schema reference: {ref}")
                target = target[segment]
            base = expand(target, (*refs, ref), depth + 1)
            siblings = {key: value for key, value in node.items() if key != "$ref"}
            return {"allOf": [base, expand(siblings, refs, depth + 1)]} if siblings else base
        result: dict[str, Any] = {}
        for key, value in node.items():
            if key in ("$defs", "definitions"):
                if not isinstance(value, dict):
                    raise ValueError(f"{key} must be an object")
                result[key] = {name: expand(child, refs, depth + 1) for name, child in value.items()}
            elif key == "properties" and isinstance(value, dict):
                result[key] = {name: expand(child, refs, depth + 1) for name, child in value.items()}
            elif key in ("anyOf", "oneOf", "allOf") and isinstance(value, list):
                result[key] = [expand(child, refs, depth + 1) for child in value]
            elif key == "items" and isinstance(value, dict):
                result[key] = expand(value, refs, depth + 1)
            elif key == "additionalProperties" and isinstance(value, dict):
                result[key] = expand(value, refs, depth + 1)
            else:
                result[key] = value
        return result

    return expand(schema, (), 0)


def _preflight_schema(schema: Any, path: str, depth: int) -> None:
    """Reject malformed or unsupported assertions, including inactive branches."""
    if depth > 32:
        raise ValueError("schema nesting exceeds supported depth")
    if not isinstance(schema, dict):
        raise ValueError(f"schema at {path} must be an object")
    unsupported = set(schema) - _SUPPORTED - _ANNOTATIONS
    if unsupported:
        raise ValueError(f"unsupported JSON schema keyword(s) at {path}: {', '.join(sorted(unsupported))}")
    if 'discriminator' in schema:
        # OpenAPI dispatch hint only: the original oneOf/const assertions,
        # not this annotation, determine which argument objects are valid.
        hint=schema['discriminator']
        if (not isinstance(hint,dict) or set(hint)-{'propertyName','mapping'}
                or not isinstance(hint.get('propertyName'),str) or not hint['propertyName']
                or not isinstance(hint.get('mapping',{}),dict)
                or any(not isinstance(k,str) or not isinstance(v,str) for k,v in hint.get('mapping',{}).items())):
            raise ValueError(f'malformed discriminator annotation at {path}')
    if "format" in schema:
        format_name = schema["format"]
        if format_name not in {"date-time", "date", "binary"}:
            raise ValueError(f"unsupported JSON schema format at {path}: {format_name!r}")
        expected = schema.get("type")
        expected_types = expected if isinstance(expected, list) else [expected]
        if "string" not in expected_types:
            raise ValueError(f"format at {path} is supported only for string schemas")
    for name in ("anyOf", "oneOf", "allOf"):
        if name in schema:
            branches = schema[name]
            if not isinstance(branches, list) or not branches:
                raise ValueError(f"{name} at {path} must be a non-empty array")
            for i, child in enumerate(branches):
                _preflight_schema(child, f"{path}.{name}[{i}]", depth + 1)
    props = schema.get("properties", {})
    if "properties" in schema and not isinstance(props, dict):
        raise ValueError(f"properties at {path} must be an object")
    for key, child in props.items():
        _preflight_schema(child, f"{path}.properties.{key}", depth + 1)
    if isinstance(schema.get("items"), dict):
        _preflight_schema(schema["items"], f"{path}.items", depth + 1)
    if isinstance(schema.get("additionalProperties"), dict):
        _preflight_schema(schema["additionalProperties"], f"{path}.additionalProperties", depth + 1)
