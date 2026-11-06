"""API-key stand-in for the Codex session adapter (published copy only).

The original module drove the locally installed Codex app (App Server) on a
ChatGPT subscription. That was a development workaround and is not published.
This drop-in keeps the same names and call shape so the rest of the harness is
unchanged, but sends each turn to an OpenAI-compatible Chat Completions API.

Configuration (environment variables):
  CLINICALGROUND_API_KEY   required; the API key (never logged or stored)
  CLINICALGROUND_BASE_URL  optional; default https://api.openai.com/v1
  CLINICALGROUND_MODEL     optional; overrides the model name the harness passes
  CLINICALGROUND_REASONING_EFFORT  optional; e.g. low/medium/high, or "none" to omit

The `executable` and `allowed_instruction_sources` arguments are accepted for
compatibility and ignored: there is no local Codex binary or instruction file.
"""
from __future__ import annotations

import math
import os
import time
from typing import Any

from .models import ModelReply, ToolSpec
from .providers import OpenAICompatibleModel, ProviderError, safe_request_diagnostics

# Read by batch.py: no Codex executable or Codex instruction file is required.
API_ADAPTER = True
DEFAULT_BASE_URL = "https://api.openai.com/v1"


def validate_active_timeout(timeout: float, active_timeout: float | None) -> None:
    if active_timeout is not None and (isinstance(active_timeout, bool)
            or not isinstance(active_timeout, (int, float)) or not math.isfinite(active_timeout)
            or not timeout <= active_timeout <= 1800):
        raise ValueError('active_timeout must be between timeout and 1800 seconds')


class CodexSessionModel:
    """Same constructor and complete() contract as the original Codex adapter."""

    def __init__(self, executable: Any = None, model: str = "gpt-6-luna",
                 reasoning_effort: str = "high", timeout: float = 120,
                 runtime_dir: Any = None, allowed_instruction_sources: dict[str, str] | None = None,
                 active_timeout: float | None = None):
        validate_active_timeout(timeout, active_timeout)
        api_key = os.environ.get("CLINICALGROUND_API_KEY", "")
        if not api_key:
            raise ProviderError("CLINICALGROUND_API_KEY is not set; this published copy needs an "
                                "OpenAI-compatible API key (see README.md)")
        effort = os.environ.get("CLINICALGROUND_REASONING_EFFORT", reasoning_effort)
        self.model = os.environ.get("CLINICALGROUND_MODEL") or model
        self.timeout = float(active_timeout or timeout)
        self._client = OpenAICompatibleModel(
            self.model, os.environ.get("CLINICALGROUND_BASE_URL") or DEFAULT_BASE_URL, api_key,
            timeout=self.timeout, reasoning_effort=None if effort in {"", "none"} else effort)
        self.last_request_metrics: dict[str, Any] = {}
        self._last_reply = ""

    def complete(self, messages: list[dict[str, Any]], tools: list[ToolSpec], *,
                 max_output_tokens: int) -> ModelReply:
        started = time.monotonic()
        self._last_reply = ""
        self.last_request_metrics = {"request_stage": "awaiting_turn"}
        try:
            reply = self._client.complete(messages, tools, max_output_tokens=max_output_tokens)
        finally:
            self.last_request_metrics["request_elapsed_seconds"] = time.monotonic() - started
        self._last_reply = reply.content or ""
        self.last_request_metrics["request_stage"] = "completed"
        return reply

    def probe(self) -> dict[str, Any]:
        return {"initialized": True, "authenticated": True, "account_type": "api_key",
                "model_configured": self.model, "inference_performed": False}

    def failure_response(self) -> dict[str, Any]:
        return {"text": self._last_reply[:20000], "generation_completed": bool(self._last_reply),
                "text_truncated": len(self._last_reply) > 20000}

    def request_diagnostics(self) -> dict[str, Any]:
        return safe_request_diagnostics(dict(self.last_request_metrics))
