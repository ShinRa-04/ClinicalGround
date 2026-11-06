"""Optional direct Harbor adapter; no upstream chi-bench registry patch."""

from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path
import re
import shlex
import tarfile
import tempfile
from typing import Any
import hashlib

from .models import Scope

try:  # Harbor is present only in the official runner container.
    from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
    HARBOR_AVAILABLE = True
except ImportError:  # Keep normal offline package imports independent of Harbor.
    HARBOR_AVAILABLE = False
    class BaseInstalledAgent:  # type: ignore[no-redef]
        pass

    def with_prompt_template(function):  # type: ignore[no-redef]
        return function


class HealthHarnessAgent(BaseInstalledAgent):
    """Run the local harness in the fresh trial container using explicit scope config."""

    SUPPORTS_ATIF = False

    @staticmethod
    def name() -> str:
        return "health-harness"

    def get_version_command(self) -> str | None:
        return "PYTHONPATH=/tmp/health-harness-source python -c 'import health_harness; print(\"0.1.0\")'"

    async def install(self, environment: Any) -> None:
        if not HARBOR_AVAILABLE:
            raise RuntimeError("Harbor is not installed; launch this adapter through the pinned chi-bench Harbor runner")
        package_dir = Path(__file__).resolve().parent
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as bundle:
            for source in sorted(package_dir.rglob("*")):
                if source.is_file() and (source.suffix == ".py" or source.suffix == ".json"):
                    bundle.add(source, arcname=source.relative_to(package_dir.parent).as_posix())
        encoded = base64.b64encode(archive.getvalue()).decode("ascii")
        chunks = [encoded[i:i + 16000] for i in range(0, len(encoded), 16000)]
        result = await self.exec_as_root(environment, command="rm -f /tmp/health-harness-source.b64")
        _check_exec_success(result, "remove previous package staging file")
        for chunk in chunks:
            result = await self.exec_as_root(environment, command=f"printf %s {shlex.quote(chunk)} >> /tmp/health-harness-source.b64")
            _check_exec_success(result, "append package staging chunk")
        extract = (
            "import base64,pathlib,tarfile;"
            "p=pathlib.Path('/tmp/health-harness-source.b64');"
            "raw=base64.b64decode(p.read_bytes(),validate=True);"
            "root=pathlib.Path('/tmp/health-harness-source');root.mkdir(parents=True,exist_ok=True);"
            "tarfile.open(fileobj=__import__('io').BytesIO(raw),mode='r:gz').extractall(root);p.unlink()"
        )
        result = await self.exec_as_root(environment, command=f"python -c {shlex.quote(extract)}")
        _check_exec_success(result, "decode and extract package")

    @with_prompt_template
    async def run(self, instruction: str, environment: Any, context: Any) -> None:
        extra = dict(getattr(self, "_extra_env", {}) or {})
        mcp_url = next((server.url for server in getattr(self, "mcp_servers", []) if getattr(server, "url", None)), None)
        mcp_url = mcp_url or extra.get("HEALTH_HARNESS_MCP_URL")
        required = {
            "HEALTH_HARNESS_DOMAIN": extra.get("HEALTH_HARNESS_DOMAIN"),
            "HEALTH_HARNESS_SCOPE_JSON": extra.get("HEALTH_HARNESS_SCOPE_JSON"),
            "HEALTH_HARNESS_MODEL": extra.get("HEALTH_HARNESS_MODEL"),
            "HEALTH_HARNESS_BASE_URL": extra.get("HEALTH_HARNESS_BASE_URL"),
            "HEALTH_HARNESS_API_KEY": extra.get("HEALTH_HARNESS_API_KEY"),
            "HEALTH_HARNESS_MCP_URL": mcp_url,
        }
        missing = [key for key, value in required.items() if not isinstance(value, str) or not value]
        if missing:
            raise RuntimeError("explicit harness configuration is missing: " + ", ".join(missing))
        if required["HEALTH_HARNESS_DOMAIN"] not in {"PA", "UM", "CM"}:
            raise RuntimeError("HEALTH_HARNESS_DOMAIN must be explicitly set to PA, UM, or CM")
        try:
            scope = Scope(**json.loads(required["HEALTH_HARNESS_SCOPE_JSON"]))
        except Exception as exc:
            raise RuntimeError("HEALTH_HARNESS_SCOPE_JSON must explicitly contain all six scope identities") from exc
        instruction_b64 = base64.b64encode(instruction.encode("utf-8")).decode("ascii")
        log_path = f"/logs/agent/health-harness-{scope.key}.log"
        env = {**required, "HEALTH_HARNESS_INSTRUCTION_B64": instruction_b64}
        for name in ("HEALTH_HARNESS_COMPOSITION", "HEALTH_HARNESS_LIMITS_JSON", "HEALTH_HARNESS_CASE_FOLDER"):
            if name in extra:
                env[name] = extra[name]
        command = (
            "mkdir -p /logs/agent && python -c 'import os,base64,pathlib;pathlib.Path(\"/tmp/health-harness-instruction.md\").write_bytes("
            "base64.b64decode(os.environ[\"HEALTH_HARNESS_INSTRUCTION_B64\"]))' && "
            "PYTHONPATH=/tmp/health-harness-source${PYTHONPATH:+:$PYTHONPATH} "
            f"python -m health_harness.chi_bench >> {shlex.quote(log_path)} 2>&1"
        )
        result = await self.exec_as_agent(environment, command=command, env=env)
        _check_exec_success(result, "run health harness")


def _check_exec_success(result: Any, operation: str) -> None:
    """Honor explicit process statuses returned by Harbor execution adapters."""
    code = getattr(result, "returncode", getattr(result, "exit_code", None))
    if isinstance(result, dict):
        code = result.get("returncode", result.get("exit_code", code))
    if isinstance(code, int) and code != 0:
        raise RuntimeError(f"Harbor command failed while attempting to {operation} (exit {code})")


def _run_inside_environment() -> int:
    required = ("HEALTH_HARNESS_DOMAIN", "HEALTH_HARNESS_SCOPE_JSON", "HEALTH_HARNESS_MODEL",
                "HEALTH_HARNESS_BASE_URL", "HEALTH_HARNESS_API_KEY", "HEALTH_HARNESS_MCP_URL",
                "HEALTH_HARNESS_INSTRUCTION_B64")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("trial environment is missing explicit harness values: " + ", ".join(missing))
    scope = Scope(**json.loads(os.environ["HEALTH_HARNESS_SCOPE_JSON"]))
    instruction = base64.b64decode(os.environ["HEALTH_HARNESS_INSTRUCTION_B64"], validate=True).decode("utf-8")
    case_label = _safe_case_component(scope.case)
    role = {"PA": "provider", "UM": "payer", "CM": "care-manager"}[os.environ["HEALTH_HARNESS_DOMAIN"]]
    case_root = Path(os.environ.get("HEALTH_HARNESS_CASE_FOLDER", "/logs/artifacts/workspaces")) / case_label / role
    private_root = Path("/logs/agent") / scope.key
    limit_data = json.loads(os.environ.get("HEALTH_HARNESS_LIMITS_JSON", "{}"))
    if not isinstance(limit_data, dict):
        raise RuntimeError("HEALTH_HARNESS_LIMITS_JSON must be a JSON object")
    config = {
        "scope": scope.to_dict(),
        "instruction": instruction,
        "domain": os.environ["HEALTH_HARNESS_DOMAIN"],
        "provider": {"model": os.environ["HEALTH_HARNESS_MODEL"],
                     "base_url": os.environ["HEALTH_HARNESS_BASE_URL"],
                     "key_env": "HEALTH_HARNESS_API_KEY"},
        "mcp_servers": [{"url": os.environ["HEALTH_HARNESS_MCP_URL"], "namespace": "chi-bench-case-tools"}],
        "limits": limit_data,
        "storage": str(private_root / "state.sqlite"),
        "workspace": str(case_root),
        "output_dir": str(private_root / "receipts"),
        "read_roots": ["/workspace/skills/managed-care-operations-handbook",
                       "/opt/healthverse-task-assets/tool_reference.md",
                       str(case_root / "incoming_request")],
        "composition": os.environ.get("HEALTH_HARNESS_COMPOSITION", "combined"),
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as config_file:
        json.dump(config, config_file, ensure_ascii=False)
        config_path = Path(config_file.name)
    try:
        from .cli import _run_config
        return _run_config(config_path, resume=os.environ.get("HEALTH_HARNESS_RESUME") == "true")
    finally:
        config_path.unlink(missing_ok=True)


def _safe_case_component(case_id: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", case_id):
        return case_id
    return f"case-{hashlib.sha256(case_id.encode('utf-8')).hexdigest()[:16]}"


if __name__ == "__main__":
    raise SystemExit(_run_inside_environment())
