"""Stateless OpenAI-compatible Chat Completions client and local scripted model."""

from __future__ import annotations

import json
import hashlib
import re
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import ModelReply, ToolCall, ToolSpec


class ProviderError(RuntimeError):
    pass


class OpenAICompatibleModel:
    """Send one independent request per turn; no implicit key lookup or retry."""

    def __init__(self, model: str, base_url: str, api_key: str, timeout: float = 60,
                 reasoning_effort: str | None = None):
        if not isinstance(model, str) or not model.strip():
            raise ValueError("runtime model ID must be explicitly configured")
        if not isinstance(base_url, str) or not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must be an explicit HTTP(S) endpoint")
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("provider API key must be explicitly supplied")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.model = model
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.timeout = timeout
        self.reasoning_effort = reasoning_effort

    def complete(self, messages: list[dict[str, Any]], tools: list[ToolSpec], *, max_output_tokens: int) -> ModelReply:
        aliases = {spec.name: _provider_alias(spec.name) for spec in tools}
        if len(set(aliases.values())) != len(aliases):
            raise ProviderError("tool presentation alias collision")
        reverse_aliases = {alias: name for name, alias in aliases.items()}
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [_to_provider_message(message, aliases) for message in messages],
            "max_tokens": max_output_tokens,
        }
        if tools:
            body["tools"] = [{"type": "function", "function": {
                "name": aliases[spec.name], "description": spec.description, "parameters": spec.input_schema,
            }} for spec in tools]
            body["tool_choice"] = "auto"
        if self.reasoning_effort:
            body["reasoning_effort"] = self.reasoning_effort
        request = Request(self.endpoint, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), method="POST",
                          headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                                   "Accept": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ProviderError(f"provider returned HTTP {exc.code}") from None
        except URLError as exc:
            raise ProviderError(f"provider connection failed: {type(exc.reason).__name__}") from None
        except (TimeoutError, OSError) as exc:
            raise ProviderError(f"provider request failed: {type(exc).__name__}") from None
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("provider returned invalid JSON") from None
        try:
            choice = payload["choices"][0]["message"]
            content = choice.get("content") or ""
            calls = []
            for item in choice.get("tool_calls", []):
                function = item["function"]
                presented_name = function["name"]
                actual_name = reverse_aliases.get(presented_name)
                if actual_name is None:
                    raise ValueError("provider returned an unknown tool alias")
                args = json.loads(function.get("arguments") or "{}")
                if not isinstance(args, dict):
                    raise ValueError("tool-call arguments must be an object")
                calls.append(ToolCall(str(item["id"]), actual_name, args))
            usage = _normalize_usage(payload.get("usage", {}))
            return ModelReply(content=str(content), tool_calls=tuple(calls), usage=usage)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
            raise ProviderError("provider response did not match the expected Chat Completions shape") from None


class ScriptedModel:
    """Deterministic provider fake for offline demos and tests."""

    def __init__(self, replies: Iterable[ModelReply]):
        self._replies = list(replies)
        self.calls: list[dict[str, Any]] = []

    def complete(self, messages: list[dict[str, Any]], tools: list[ToolSpec], *, max_output_tokens: int) -> ModelReply:
        self.calls.append({"messages": messages, "tools": tools, "max_output_tokens": max_output_tokens})
        if not self._replies:
            raise ProviderError("scripted model has no remaining replies")
        return self._replies.pop(0)


def _to_provider_message(message: dict[str, Any], aliases: dict[str, str]) -> dict[str, Any]:
    role = message.get("role")
    if role not in {"system", "user", "assistant", "tool"}:
        raise ValueError(f"unsupported message role: {role}")
    converted: dict[str, Any] = {"role": role, "content": message.get("content", "")}
    if role == "assistant" and message.get("tool_calls"):
        converted["tool_calls"] = [{"id": call["id"], "type": "function", "function": {
            "name": aliases.get(call["name"], _provider_alias(call["name"])),
            "arguments": json.dumps(call["arguments"], ensure_ascii=False, separators=(",", ":")),
        }} for call in message["tool_calls"]]
    if role == "tool":
        converted["tool_call_id"] = message["tool_call_id"]
    return converted


def _provider_alias(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")[:43] or "tool"
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:12]
    return f"hh_{slug}_{digest}"[:64]


def _normalize_usage(usage: Any) -> dict[str, int]:
    if not isinstance(usage, dict):
        return {}
    result: dict[str, int] = {}
    mapping = {"prompt_tokens": "input_tokens", "completion_tokens": "output_tokens", "total_tokens": "total_tokens"}
    for source, target in mapping.items():
        value = usage.get(source)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            result[target] = value
    details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
    if isinstance(details, dict):
        cached = details.get("cached_tokens")
        if isinstance(cached, int) and not isinstance(cached, bool) and cached >= 0:
            result["cached_input_tokens"] = cached
    return result
