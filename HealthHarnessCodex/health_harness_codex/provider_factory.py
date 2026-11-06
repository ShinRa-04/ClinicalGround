"""Explicit construction of supported model providers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .providers import OpenAICompatibleModel


def create_model(config: dict[str, Any]):
    """Build a model from provider config without implicit credential lookup.

    Legacy configs with model/base_url/key_env and no ``type`` retain the
    OpenAI-compatible behavior used by the original package.
    """
    provider = config.get("provider")
    if not isinstance(provider, dict):
        raise ValueError("config.provider must be an object")
    backend = provider.get("type")
    if backend is None:
        backend = "openai_compatible"
    if backend == "openai_compatible":
        model_name = provider.get("model")
        base_url = provider.get("base_url")
        key_name = provider.get("key_env")
        if not isinstance(key_name, str) or not key_name:
            raise ValueError("openai_compatible provider requires key_env")
        if key_name not in os.environ or not os.environ[key_name]:
            raise ValueError(f"configured provider key environment variable is missing: {key_name}")
        return OpenAICompatibleModel(
            model_name, base_url, os.environ[key_name], timeout=provider.get("timeout", 60),
            reasoning_effort=provider.get("reasoning_effort"),
        )
    if backend == "codex_app_server":
        executable = provider.get("executable")
        if not isinstance(executable, str) or not executable.strip():
            raise ValueError("codex_app_server provider requires an explicit executable path")
        path = Path(executable)
        if not path.is_absolute():
            raise ValueError("codex_app_server executable must be an absolute path")
        from .codex_provider import CodexSessionModel
        return CodexSessionModel(
            str(path), model=provider.get("model", "gpt-6-luna"),
            reasoning_effort=provider.get("reasoning_effort", "high"),
            timeout=provider.get("timeout", 120), runtime_dir=provider.get("runtime_dir"),
            allowed_instruction_sources=provider.get("allowed_instruction_sources"),
        )
    raise ValueError(f"unsupported provider type: {backend}")
