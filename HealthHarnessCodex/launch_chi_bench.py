"""Print the direct Harbor trial command; execution requires explicit --execute."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


IMPORT_PATH = "health_harness_codex.chi_bench:HealthHarnessAgent"


def build_argv(args: argparse.Namespace) -> list[str]:
    if getattr(args, "provider_type", "openai_compatible") == "codex_app_server":
        raise ValueError("Codex-hosted inference cannot run inside the Docker trial container; the host trial bridge is not implemented")
    scope = json.loads(Path(args.scope_json).read_text(encoding="utf-8"))
    if not isinstance(scope, dict) or set(scope) != {"environment", "task", "organization", "principal", "patient", "case"}:
        raise ValueError("scope JSON must contain exactly the six explicit scope identities")
    if any(not isinstance(value, str) or not value for value in scope.values()):
        raise ValueError("all scope identities must be non-empty strings")
    if args.domain not in {"PA", "UM", "CM"}:
        raise ValueError("domain must be PA, UM, or CM")
    if not Path(args.task_folder, "task.toml").is_file():
        raise ValueError("task-folder must point to one task directory containing task.toml")
    values = {
        "HEALTH_HARNESS_DOMAIN": args.domain,
        "HEALTH_HARNESS_SCOPE_JSON": json.dumps(scope, separators=(",", ":")),
        "HEALTH_HARNESS_MODEL": args.model,
        "HEALTH_HARNESS_BASE_URL": args.base_url,
        "HEALTH_HARNESS_MCP_URL": args.mcp_url,
        "HEALTH_HARNESS_API_KEY": "${" + args.key_env + "}",
        "HEALTH_HARNESS_COMPOSITION": args.composition,
        "HEALTH_HARNESS_CASE_FOLDER": args.case_folder,
    }
    command = [args.harbor, "trials", "start", "-p", str(Path(args.task_folder).resolve()),
               "--agent-import-path", IMPORT_PATH,
               "--environment-import-path", "chi_bench.experiment.docker_env:ChiBenchDockerEnvironment",
               "-m", args.model, "--trials-dir", str(Path(args.trials_dir).resolve())]
    for name, value in values.items():
        command.extend(["--ae", f"{name}={value}"])
    if args.limits_json:
        limits = json.loads(Path(args.limits_json).read_text(encoding="utf-8"))
        if not isinstance(limits, dict):
            raise ValueError("limits JSON must be an object")
        command.extend(["--ae", f"HEALTH_HARNESS_LIMITS_JSON={json.dumps(limits, separators=(',', ':'))}"])
    return command


def controller_environment(existing: dict[str, str] | None = None) -> dict[str, str]:
    child_env = dict(os.environ if existing is None else existing)
    package_root = str(Path(__file__).resolve().parent)
    current_path = child_env.get("PYTHONPATH", "")
    child_env["PYTHONPATH"] = package_root + (os.pathsep + current_path if current_path else "")
    return child_env


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-folder", required=True, help="one supplied task folder containing task.toml")
    parser.add_argument("--scope-json", required=True, help="local JSON with the six explicit scope identities")
    parser.add_argument("--domain", required=True, choices=("PA", "UM", "CM"))
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--mcp-url", required=True)
    parser.add_argument("--key-env", default="HEALTH_HARNESS_API_KEY", help="environment variable holding the provider key")
    parser.add_argument("--provider-type", choices=("openai_compatible", "codex_app_server"),
                        default="codex_app_server", help="trial provider backend (Codex host bridge is not yet implemented)")
    parser.add_argument("--codex-executable", help="absolute Codex executable path for a future host bridge")
    parser.add_argument("--case-folder", default="/logs/artifacts/workspaces")
    parser.add_argument("--trials-dir", default="/runner/logs/health-harness-codex-trials")
    parser.add_argument("--composition", choices=("combined", "helpers", "team"), default="combined")
    parser.add_argument("--limits-json", help="optional local JSON with explicit harness limits")
    parser.add_argument("--harbor", default="harbor", help="Harbor executable")
    parser.add_argument("--execute", action="store_true", help="execute the displayed Harbor trial")
    args = parser.parse_args(argv)
    try:
        if args.provider_type == "codex_app_server":
            if args.execute:
                raise ValueError("Codex-hosted inference cannot run inside the Docker trial container; the host trial bridge is not implemented")
            print(json.dumps({
                "mode": "planned",
                "provider": "codex_app_server",
                "codex_executable": args.codex_executable,
                "execution": "unsupported: Codex host-to-trial bridge is not implemented; no Docker trial can be launched",
            }, indent=2))
            return 0
        if args.execute:
            if args.key_env not in os.environ or not os.environ[args.key_env]:
                raise ValueError(f"provider key environment variable is missing: {args.key_env}")
            command = build_argv(args)
            return subprocess.run(command, check=False, env=controller_environment()).returncode
        command = build_argv(args)
        controller_path = controller_environment()["PYTHONPATH"]
        print(json.dumps({"mode": "planned", "argv": command,
                          "controller_env": {"PYTHONPATH": controller_path},
                          "execution": "requires --execute"}, indent=2))
        return 0
    except Exception as exc:
        print(f"chi-bench launcher: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
