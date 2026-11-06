"""Offline synthetic demo and explicit opt-in configured execution."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

from .engine import Harness
from .models import Limits, ModelReply, Scope, ToolCall, ToolSpec
from .providers import OpenAICompatibleModel, ScriptedModel
from .store import CaseStore
from .tools import MCPClient, ToolRegistry, WorkspaceTools


class _DemoTools:
    def __init__(self, domain: str):
        self.domain = domain

    def list_tools(self) -> list[ToolSpec]:
        return [ToolSpec("demo.observe", "Return one synthetic observation for the current demonstration case.", {
            "type": "object", "required": ["patient_id", "case_id"], "additionalProperties": False,
            "properties": {"patient_id": {"type": "string"}, "case_id": {"type": "string"}},
        }, effect="read", identity_fields=("patient_id", "case_id"))]

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name != "demo.observe":
            raise KeyError(name)
        return {"patient_id": arguments["patient_id"], "case_id": arguments["case_id"],
                "domain": self.domain, "synthetic": True, "receipt": f"demo-{self.domain.lower()}-observed"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="health-harness", description="Offline healthcare workflow harness")
    parser.add_argument("--config", type=Path, help="local JSON run config (requires --live)")
    parser.add_argument("--live", action="store_true", help="authorize a configured model/MCP run")
    parser.add_argument("--resume", action="store_true", help="resume an existing scoped run")
    parser.add_argument("--demo", action="store_true", help="run only synthetic PA, UM, and CM examples")
    args = parser.parse_args(argv)
    if args.config is None:
        if args.live or args.resume:
            parser.error("--live/--resume require --config")
        return _run_demo()
    if args.demo:
        parser.error("--demo cannot be combined with --config")
    if not args.live:
        parser.error("configured providers and MCP endpoints require explicit --live")
    try:
        return _run_config(args.config.resolve(), resume=args.resume)
    except Exception as exc:
        print(f"health-harness: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


def _run_demo() -> int:
    rows = []
    with tempfile.TemporaryDirectory(prefix="health-harness-demo-") as temp:
        store = CaseStore(Path(temp) / "demo.sqlite")
        try:
            for domain in ("PA", "UM", "CM"):
                case_scope = Scope("synthetic-demo", f"demo-{domain.lower()}", "demo-org", "demo-principal",
                                   f"synthetic-patient-{domain.lower()}", f"synthetic-case-{domain.lower()}")
                replies = [
                    ModelReply(tool_calls=(ToolCall(f"observe-{domain.lower()}", "demo.observe", {
                        "patient_id": case_scope.patient, "case_id": case_scope.case,
                    }),)),
                    ModelReply(content=json.dumps({
                        "status": "complete", "claim": f"Synthetic {domain} demonstration observation was recorded.",
                        "evidence_ids": [f"ev:m1:observe-{domain.lower()}"],
                    })),
                ]
                result = Harness(store, ScriptedModel(replies), _DemoTools(domain)).run(
                    case_scope, f"Demonstrate a synthetic {domain} observation.", domain)
                rows.append({"domain": domain, "status": result["status"], "model_calls": result["model_calls"],
                             "tool_calls": result["tool_calls"], "synthetic_only": True})
        finally:
            store.close()
    print(json.dumps({"mode": "offline-synthetic-demo", "results": rows}, indent=2))
    return 0 if all(row["status"] == "complete" for row in rows) else 2


def _run_config(path: Path, *, resume: bool) -> int:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("run config must be a JSON object")
    if "api_key" in config or (isinstance(config.get("provider"), dict) and "api_key" in config["provider"]):
        raise ValueError("store only a provider key environment-variable name in config, never the secret")
    scope_data = config.get("scope")
    if not isinstance(scope_data, dict):
        raise ValueError("config.scope must explicitly provide all six scope identities")
    scope = Scope(**scope_data)
    instruction = config.get("instruction")
    domain = config.get("domain")
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("config.instruction must be supplied")
    if domain not in {"PA", "UM", "CM"}:
        raise ValueError("config.domain must be PA, UM, or CM")
    provider_cfg = config.get("provider")
    if not isinstance(provider_cfg, dict):
        raise ValueError("config.provider must explicitly specify model, base_url, and key_env")
    key_name = provider_cfg.get("key_env")
    if not isinstance(key_name, str) or not key_name or key_name not in os.environ:
        raise ValueError(f"configured provider key environment variable is missing: {key_name or '<unset>'}")
    model = OpenAICompatibleModel(provider_cfg.get("model"), provider_cfg.get("base_url"), os.environ[key_name],
                                  timeout=provider_cfg.get("timeout", 60),
                                  reasoning_effort=provider_cfg.get("reasoning_effort"))
    limits_data = config.get("limits", {})
    if not isinstance(limits_data, dict):
        raise ValueError("config.limits must be an object")
    limits = Limits(**limits_data)
    composition = config.get("composition", "combined")
    workspace_path = _resolve_config_path(config.get("workspace"), path.parent, required=True)
    store_path = _resolve_config_path(config.get("storage"), path.parent, required=True)
    output_dir = _resolve_config_path(config.get("output_dir", "runs"), path.parent, required=True)
    read_roots = config.get("read_roots", [])
    if not isinstance(read_roots, list) or any(not isinstance(item, str) for item in read_roots):
        raise ValueError("config.read_roots must be an array of configured paths")
    roots = [_resolve_config_path(item, path.parent, required=True) for item in read_roots]
    servers = config.get("mcp_servers")
    if not isinstance(servers, list) or not servers:
        raise ValueError("config.mcp_servers must list at least one authorized MCP endpoint")
    clients = []
    for server in servers:
        if isinstance(server, str):
            clients.append(MCPClient(server))
        elif isinstance(server, dict) and isinstance(server.get("url"), str):
            clients.append(MCPClient(server["url"], timeout=server.get("timeout", 30), namespace=server.get("namespace")))
        else:
            raise ValueError("each MCP server must be a URL or object with url")
    workspace = WorkspaceTools(workspace_path, scope, roots)
    tools = ToolRegistry(*clients, workspace)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    store = CaseStore(store_path)
    try:
        result = Harness(store, model, tools, limits=limits, composition=composition).run(
            scope, instruction, domain, resume=resume)
    finally:
        store.close()
    receipt_path = output_dir / scope.key / "result.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"status": result["status"], "receipt": str(receipt_path),
                      "model_calls": result["model_calls"], "tool_calls": result["tool_calls"],
                      "usage": result.get("usage", {})}, ensure_ascii=False))
    return 0 if result["status"] == "complete" else 2


def _resolve_config_path(value: Any, base: Path, *, required: bool) -> Path:
    if not isinstance(value, str) or not value.strip():
        if required:
            raise ValueError("config path value must be non-empty")
        return base
    candidate = Path(value)
    return (base / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
