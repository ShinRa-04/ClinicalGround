"""Stateless OpenAI-compatible Chat Completions client and local scripted model."""

from __future__ import annotations

import json
import hashlib
import re
import math
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import ModelReply, ToolCall, ToolSpec
from .schema import tool_parameter_schema

REQUEST_STAGES = {'validating_input','starting_process','initializing','preflight',
                  'starting_thread','starting_turn','awaiting_turn','parsing_reply','completed'}
NATIVE_EVENTS = {'turn_started','turn_completed','turn_error','reasoning_progress',
                 'assistant_progress','usage','item_completed','other'}
RESPONSE_FORMAT_STAGES = {'outer_json','arguments_json','reply_shape','content_shape','tool_calls_shape',
    'tool_call_shape','tool_call_id','tool_name','arguments_shape','duplicate_json_key','nonfinite_json','response_size','response_repetition','response_whitespace','output_token_limit'}
MAX_OUTPUT_LIMIT_CORRECTIONS = 3


def response_retry_limit(error):
    return MAX_OUTPUT_LIMIT_CORRECTIONS if getattr(error,'stage',None)=='output_token_limit' else 1


def can_retry_disconnected_generation(error):
    """Only a classified, cleaned-up native generation with no proposal dispatch."""
    category=getattr(error,'failure_category',None)
    parts=category.split(':') if isinstance(category,str) else []
    diagnostics=safe_request_diagnostics(getattr(error,'diagnostics',{}))
    return (len(parts)==3 and parts[0] in {'error','turn_completed','turn_failed','turn_interrupted'}
            and parts[1] in {'unknown','failed','interrupted'} and parts[2]=='responseStreamDisconnected'
            and getattr(error,'proposal_dispatch_safe',False) is True
            and getattr(error,'transient_retry_eligible',False) is True
            and diagnostics.get('cleanup_confirmed') is True
            and diagnostics.get('request_timed_out') is False)


def safe_token_usage(value):
    if not isinstance(value,dict):return {}
    keys={'input_tokens','output_tokens','total_tokens','cached_input_tokens',
          'reasoning_output_tokens','cache_write_input_tokens'}
    return {k:v for k,v in value.items() if k in keys and type(v) is int and v>=0}


def safe_request_diagnostics(value):
    """Allow only operational enums/counts; never RPC params or arbitrary text."""
    if not isinstance(value,dict):return {}
    out={}
    enums={'request_stage':REQUEST_STAGES,'last_native_event':NATIVE_EVENTS,
           'argument_decoding_mode':{'tool_schema','host_validated'},
           'response_failure_stage':RESPONSE_FORMAT_STAGES,
           'token_estimate_method':{'characters_div4'},
           'timeout_reason':{'idle','active_total'},
           'last_rpc_method':{'initialize','initialized','account/read','config/read','skills/list','thread/start','turn/start','other'},
           'timeout_phase':{'stdin_write','transport_read','deadline'}}
    for key,allowed in enums.items():
        if isinstance(value.get(key),str) and value[key] in allowed:out[key]=value[key]
    for key in ('timeout_seconds','active_timeout_seconds','request_elapsed_seconds','native_idle_seconds','transport_idle_seconds',
                'notifications_received','reasoning_updates','assistant_updates','rpc_requests_sent','messages_received',
                'stderr_bytes_seen','engine_payload_chars','tool_schema_chars','message_content_chars','response_call_index'):
        v=value.get(key)
        if type(v) in (int,float) and math.isfinite(v) and 0<=v<=2**53:out[key]=v
    for key in ('reply_chars_received','reply_bytes_received','reply_stream_updates','estimated_reply_tokens',
                'reported_output_tokens','reported_reasoning_tokens'):
        v=value.get(key)
        if type(v) is int and 0<=v<=2**53:out[key]=v
    v=value.get('reply_idle_seconds')
    if type(v) in (int,float) and math.isfinite(v) and 0<=v<=2**53:out['reply_idle_seconds']=v
    for key in ('request_timed_out','process_started','process_running','process_was_running_at_close','cleanup_confirmed'):
        if type(value.get(key)) is bool:out[key]=value[key]
    v=value.get('process_exit_code')
    if type(v) is int and -2**31<=v<=2**32:out['process_exit_code']=v
    return out

FORMAT_CORRECTION = (
    'Formatting correction only: the prior assistant response failed the required JSON/proposal contract. '
    'No proposal from that response was executed. Return exactly one valid JSON object '
    'matching the required response schema, with a content string and tool_calls array. '
    'Use a JSON object for each tool call arguments field, matching its declared schema; '
    'do not stringify or double-encode arguments. '
    'For Codex proposals provide only the tool name and arguments; the adapter attaches request-tracking IDs. '
    'Do not include markdown or commentary. Continue from the successful observations '
    'already in this conversation; do not repeat completed actions or invent source IDs. '
    'Follow the original task and declared tool contracts.')


def format_correction(error):
    if getattr(error,'stage',None)=='response_whitespace':
        return ('The reply emitted hundreds of insignificant JSON spaces/tabs outside a string without finishing. '
                'No proposal executed. Return compact finite JSON, with no indentation or padding outside quoted text. '
                'Keep the same needed tool values and return only the next necessary operation. '+FORMAT_CORRECTION)
    if getattr(error,'stage',None)=='output_token_limit':
        return ('The native response ended incomplete because its output-token limit was reached; the numerical cap was not reported. '
                'No proposal from it was executed. Return a shorter finite response with concise content and only the next necessary operations. '
                'Split a large proposed batch across subsequent replies instead of repeating completed actions. '+FORMAT_CORRECTION)
    if getattr(error, 'stage', None) in {'response_size','response_repetition'}:
        reason=('The prior reply exceeded the existing 60000-character response bound while generating. '
                if error.stage=='response_size' else 'The prior reply generated a long repeating character pattern instead of a finite response. ')
        return (reason +
                'No proposal from it was executed. Return a concise finite JSON response with only the next needed operations; '
                'do not repeat characters or pad identifiers. Use observed identifiers when required. '
                'Optional audit inputs may be omitted to use their documented tool defaults. '
                + FORMAT_CORRECTION)
    return FORMAT_CORRECTION


class ProviderError(RuntimeError):
    def __init__(self, message: str, *, failure_category: str | None = None,
                 proposal_dispatch_safe: bool = False, transient_retry_eligible: bool = False,
                 diagnostics: dict[str, Any] | None = None, usage: dict[str,int] | None = None):
        super().__init__(message)
        self.failure_category = failure_category
        self.proposal_dispatch_safe = proposal_dispatch_safe
        self.transient_retry_eligible = transient_retry_eligible
        self.diagnostics = safe_request_diagnostics(diagnostics)
        self.usage = safe_token_usage(usage)


class ModelResponseFormatError(ProviderError):
    """A response contract failed before any proposal dispatch."""

    def __init__(self, stage: str, usage: dict[str, int] | None = None):
        if stage not in RESPONSE_FORMAT_STAGES:
            raise ValueError("unsupported response-format failure stage")
        self.stage = stage
        message=('native response incomplete: output token limit reached; numerical cap unreported'
                 if stage=='output_token_limit' else f"model response contains invalid {stage}")
        super().__init__(message,usage=usage,
            failure_category='response_format:'+stage,proposal_dispatch_safe=True,
            diagnostics={'response_failure_stage':stage})


def validate_reply_structure(reply: ModelReply, allowed_names) -> None:
    """Reject a malformed batch atomically before dispatch, for every backend.

    Argument schemas/identity are checked later against the current state of
    each action. This preflight checks only the proposal envelope, not clinical
    dependencies that may legitimately change after an earlier action.
    """
    if not isinstance(reply.content,str):raise ModelResponseFormatError('content_shape',reply.usage)
    seen=set()
    for index,call in enumerate(reply.tool_calls):
        stage=None
        if not isinstance(call,ToolCall):stage='tool_call_shape'
        elif not isinstance(call.id,str) or not call.id.strip() or call.id in seen:stage='tool_call_id'
        elif not isinstance(call.name,str) or call.name not in allowed_names:stage='tool_name'
        elif not isinstance(call.arguments,dict):stage='arguments_shape'
        if stage:
            error=ModelResponseFormatError(stage,reply.usage)
            error.diagnostics['response_call_index']=index
            raise error
        seen.add(call.id)


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
                "name": aliases[spec.name], "description": spec.description,
                "parameters": tool_parameter_schema(spec.input_schema),
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
