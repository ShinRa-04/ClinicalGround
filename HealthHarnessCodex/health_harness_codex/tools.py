"""Standard-library MCP and confined per-scope workspace tool clients."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import Scope, ToolSpec


class MCPError(RuntimeError):
    pass


class MCPToolError(MCPError):
    """Returned tool error with case-private evidence, never public exception text.

    An MCP error flag does not establish whether a write had side effects.
    Retaining the response must not turn it into a retryable failure.
    """

    def __init__(self, result: dict[str, Any]):
        super().__init__("MCP tool reported an error; inspect case-private tool failure evidence")
        self.diagnostic_result = result


class MCPClient:
    PROTOCOL_VERSION = "2025-03-26"

    def __init__(self, url: str, timeout: float = 30, namespace: str | None = None):
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ValueError("MCP URL must be an explicit HTTP(S) endpoint")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.url = url
        self.timeout = timeout
        self.namespace = namespace or url
        self.session_id: str | None = None
        self._next_id = 0
        self._initialized = False
        self._actual_names: dict[str, str] = {}
        self._specs: list[ToolSpec] | None = None
        self._bound_scope: Scope | None = None

    def bind_scope(self, scope: Scope) -> None:
        if self._bound_scope is not None and self._bound_scope != scope:
            raise ValueError("MCPClient is bound to one full case scope; create a fresh client for another case")
        self._bound_scope = scope

    def list_tools(self) -> list[ToolSpec]:
        self._initialize()
        if self._specs is not None:
            return list(self._specs)
        tools: list[dict[str, Any]] = []
        cursor = None
        seen_cursors: set[str] = set()
        for _ in range(100):
            params = {"cursor": cursor} if cursor is not None else {}
            result = self._request("tools/list", params)
            page = result.get("tools", [])
            if not isinstance(page, list):
                raise MCPError("MCP tools/list response has an invalid tools field")
            tools.extend(page)
            cursor = result.get("nextCursor")
            if not cursor:
                break
            if not isinstance(cursor, str) or cursor in seen_cursors:
                raise MCPError("MCP tools/list returned an invalid or repeated cursor")
            seen_cursors.add(cursor)
        else:
            raise MCPError("MCP tools/list pagination exceeded 100 pages")
        specs = []
        used: set[str] = set()
        actual_names: set[str] = set()
        for item in tools:
            actual = item.get("name")
            if not isinstance(actual, str) or not actual:
                raise MCPError("MCP tool has no valid name")
            if actual in actual_names:
                raise MCPError(f"MCP tools/list returned duplicate tool name {actual!r}")
            actual_names.add(actual)
            schema = item.get("inputSchema", {"type": "object"})
            if not isinstance(schema, dict):
                raise MCPError(f"MCP tool {actual!r} has an invalid input schema")
            schema = json.loads(json.dumps(schema))
            identity_fields = item.get("identityFields", schema.pop("x-identity-fields", ()))
            if not isinstance(identity_fields, (list, tuple)) or any(not isinstance(path, str) for path in identity_fields):
                raise MCPError(f"MCP tool {actual!r} has invalid identityFields metadata")
            annotations = item.get("annotations") or {}
            # Annotation hints are not authorization. Unknown tools default to write.
            effect = "read" if isinstance(annotations, dict) and annotations.get("readOnlyHint") is True else "write"
            alias = _tool_alias(self.namespace, actual)
            base = alias
            suffix = 1
            while alias in used:
                suffix += 1
                alias = f"{base}_{suffix}"
            used.add(alias)
            self._actual_names[alias] = actual
            description = str(item.get("description") or "")
            specs.append(ToolSpec(alias, f"Original MCP tool name: {actual}. {description}".strip(), schema, effect, tuple(identity_fields)))
        self._specs = specs
        return list(specs)

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if not self._initialized:
            self._initialize()
        if name not in self._actual_names:
            self.list_tools()
        actual = self._actual_names.get(name)
        if actual is None:
            raise MCPError("unknown MCP tool alias")
        result = self._request("tools/call", {"name": actual, "arguments": arguments})
        if result.get("isError") is True:
            raise MCPToolError(result)
        return _normalize_tool_result(result)

    def _initialize(self) -> None:
        if self._initialized:
            return
        result = self._request("initialize", {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "health-harness-codex", "version": "0.1.0"},
        })
        negotiated = result.get("protocolVersion")
        if not isinstance(negotiated, str):
            raise MCPError("MCP initialize response omitted protocolVersion")
        if negotiated != self.PROTOCOL_VERSION:
            raise MCPError(f"MCP protocol version mismatch: server={negotiated}")
        self._notify("notifications/initialized", {})
        self._initialized = True

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._next_id += 1
        request_id = self._next_id
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        envelope = self._post(payload, expected_id=request_id)
        if envelope.get("error"):
            raise MCPError(f"MCP request {method} failed with JSON-RPC code {envelope['error'].get('code')}")
        result = envelope.get("result")
        if not isinstance(result, dict):
            raise MCPError(f"MCP response for {method} has no result object")
        return result

    def _notify(self, method: str, params: dict[str, Any]) -> None:
        self._post({"jsonrpc": "2.0", "method": method, "params": params}, expected_id=None)

    def _post(self, payload: dict[str, Any], expected_id: int | None) -> dict[str, Any]:
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": self.PROTOCOL_VERSION}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        request = Request(self.url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                          headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                returned_session = response.headers.get("Mcp-Session-Id")
                if returned_session:
                    self.session_id = returned_session
                body = response.read()
                if not body:
                    return {}
                content_type = response.headers.get("Content-Type", "")
        except HTTPError as exc:
            # Requests are never retried, especially tools/call mutations.
            raise MCPError(f"MCP endpoint returned HTTP {exc.code}") from None
        except URLError as exc:
            raise MCPError(f"MCP endpoint connection failed: {type(exc.reason).__name__}") from None
        except (TimeoutError, OSError) as exc:
            raise MCPError(f"MCP endpoint request failed: {type(exc).__name__}") from None
        envelope = _decode_json_or_sse(body, content_type, expected_id)
        if expected_id is None:
            return envelope or {}
        if envelope is None:
            raise MCPError("MCP stream ended without the matching JSON-RPC response")
        if envelope.get("id") != expected_id:
            raise MCPError("MCP returned a response with a mismatched request ID")
        return envelope


class ToolRegistry:
    """Merge MCP and local tool providers without allowing name collisions."""

    def __init__(self, *providers: Any):
        self.providers = list(providers)
        self._routes: dict[str, Any] = {}

    def bind_scope(self, scope: Scope) -> None:
        for provider in self.providers:
            binder = getattr(provider, "bind_scope", None)
            if callable(binder):
                binder(scope)

    def list_tools(self) -> list[ToolSpec]:
        combined: list[ToolSpec] = []
        routes: dict[str, Any] = {}
        for provider in self.providers:
            for spec in provider.list_tools():
                if spec.name in routes:
                    raise ValueError(f"tool namespace collision: {spec.name}")
                routes[spec.name] = provider
                combined.append(spec)
        self._routes = routes
        return combined

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        provider = self._routes.get(name)
        if provider is None:
            self.list_tools()
            provider = self._routes.get(name)
        if provider is None:
            raise KeyError(f"unknown tool: {name}")
        return provider.call(name, arguments)


class WorkspaceTools:
    """Read configured reference roots and write only within one case folder."""

    def __init__(self, root: str | Path, scope: Scope, read_roots: Iterable[str | Path] = (), max_read_bytes: int = 1_000_000):
        self.root = Path(root).resolve()
        self.scope = scope
        self.case_root = (self.root / scope.key).resolve()
        if not _is_relative_to(self.case_root, self.root):
            raise PermissionError("case workspace resolves outside configured workspace root")
        self.case_root.mkdir(parents=True, exist_ok=True)
        self.read_roots = tuple(Path(path).resolve() for path in read_roots)
        self.max_read_bytes = max_read_bytes
        self._specs = [
            ToolSpec("workspace.read_file", "Read a UTF-8 file from this case workspace or configured read-only references.", {
                "type": "object", "required": ["path"], "additionalProperties": False,
                "properties": {"path": {"type": "string", "minLength": 1}, "max_bytes": {"type": "integer", "minimum": 1, "maximum": max_read_bytes}},
            }, effect="read"),
            ToolSpec("workspace.write_file", "Write a UTF-8 artifact inside this case's workspace.", {
                "type": "object", "required": ["path", "content"], "additionalProperties": False,
                "properties": {"path": {"type": "string", "minLength": 1}, "content": {"type": "string"}},
            }, effect="write"),
            ToolSpec("workspace.list_files", "List files only within this case's workspace.", {
                "type": "object", "required": [], "additionalProperties": False,
                "properties": {"path": {"type": "string"}},
            }, effect="read"),
        ]

    def bind_scope(self, scope: Scope) -> None:
        if self.scope != scope:
            raise ValueError("WorkspaceTools is bound to a different case scope; create a fresh workspace provider")

    def list_tools(self) -> list[ToolSpec]:
        return list(self._specs)

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "workspace.read_file":
            path = self._resolve_read(arguments["path"])
            cap = min(arguments.get("max_bytes", self.max_read_bytes), self.max_read_bytes)
            data = path.read_bytes()
            if len(data) > cap:
                raise ValueError(f"file exceeds read limit ({cap} bytes)")
            return {"path": str(path), "text": data.decode("utf-8"), "bytes": len(data)}
        if name == "workspace.write_file":
            path = self._resolve_workspace(arguments["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            data = arguments["content"].encode("utf-8")
            if len(data) > self.max_read_bytes:
                raise ValueError("workspace artifact exceeds configured size limit")
            handle, temporary = tempfile.mkstemp(prefix=".hh-write-", dir=str(path.parent))
            try:
                with os.fdopen(handle, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                Path(temporary).replace(path)
            finally:
                Path(temporary).unlink(missing_ok=True)
            return {"path": str(path), "bytes_written": len(data)}
        if name == "workspace.list_files":
            base = self._resolve_workspace(arguments.get("path", "."))
            if not base.exists():
                return {"files": []}
            return {"files": [str(p.relative_to(self.case_root)) for p in base.rglob("*") if p.is_file()]}
        raise KeyError(f"unknown workspace tool: {name}")

    def _resolve_workspace(self, value: str) -> Path:
        if not isinstance(value, str) or not value:
            raise ValueError("workspace path must be a non-empty string")
        candidate = (self.case_root / value).resolve()
        if not _is_relative_to(candidate, self.case_root):
            raise PermissionError("workspace path escapes the active case folder")
        return candidate

    def _resolve_read(self, value: str) -> Path:
        candidate = Path(value)
        if not candidate.is_absolute():
            return self._resolve_workspace(value)
        resolved = candidate.resolve()
        if _is_relative_to(resolved, self.case_root) or any(_is_relative_to(resolved, root) for root in self.read_roots):
            return resolved
        raise PermissionError("read path is outside the active case and configured reference roots")


def _tool_alias(namespace: str, name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")[:36] or "tool"
    digest = hashlib.sha256(f"{namespace}\0{name}".encode("utf-8")).hexdigest()[:12]
    return f"mcp_{slug}_{digest}"


def _normalize_tool_result(result: dict[str, Any]) -> Any:
    structured = result.get("structuredContent")
    content = result.get("content", [])
    normalized_content = []
    for block in content if isinstance(content, list) else []:
        if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
            text = block["text"]
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
            normalized_content.append({"type": "text", "text": text, "parsed_json": parsed})
        else:
            normalized_content.append(block)
    return {"structuredContent": structured, "content": normalized_content, "isError": False}


def _decode_json_or_sse(body: bytes, content_type: str, expected_id: int | None) -> dict[str, Any] | None:
    decoded = body.decode("utf-8", errors="strict")
    if "text/event-stream" not in content_type and not decoded.lstrip().startswith(("data:", "event:", ":")):
        try:
            value = json.loads(decoded)
        except json.JSONDecodeError as exc:
            raise MCPError("MCP endpoint returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise MCPError("MCP response must be a JSON object")
        return value
    data_lines: list[str] = []
    for line in decoded.splitlines():
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
        elif not line.strip() and data_lines:
            candidate = "\n".join(data_lines)
            data_lines.clear()
            try:
                value = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and value.get("id") == expected_id:
                return value
    if data_lines:
        try:
            value = json.loads("\n".join(data_lines))
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict) and value.get("id") == expected_id:
            return value
    return None


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
