import asyncio
import base64
import io
import hashlib
import json
import os
import shlex
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from health_harness import chi_bench


class FakeEnvironment:
    def __init__(self, fail_at=None, exit_code=0):
        self.commands = []
        self.fail_at = fail_at
        self.exit_code = exit_code

    async def exec_as_root(self, environment, *, command):
        self.commands.append(command)
        if self.fail_at is not None and len(self.commands) == self.fail_at:
            raise RuntimeError("remote command failed")
        if command.startswith("python -c") and "tarfile.open" in command:
            return {"exit_code": self.exit_code}
        return {"exit_code": 0}


class FakeAgent(chi_bench.HealthHarnessAgent):
    def __init__(self):
        self._extra_env = {
            "HEALTH_HARNESS_DOMAIN": "UM",
            "HEALTH_HARNESS_SCOPE_JSON": json.dumps(dict(environment="e", task="t", organization="o",
                principal="p", patient="pt", case="../../case")),
            "HEALTH_HARNESS_MODEL": "model-test",
            "HEALTH_HARNESS_BASE_URL": "https://model.invalid/v1",
            "HEALTH_HARNESS_API_KEY": "secret-value",
            "HEALTH_HARNESS_COMPOSITION": "team",
            "HEALTH_HARNESS_LIMITS_JSON": '{"max_tool_calls":5}',
            "HEALTH_HARNESS_CASE_FOLDER": "/logs/artifacts/task-1",
        }
        self.mcp_servers = [type("Server", (), {"url": "http://mcp.invalid/mcp"})()]
        self.call = None

    async def exec_as_agent(self, environment, *, command, env):
        self.call = (command, env)


class ChiBenchAdapterTests(unittest.TestCase):
    def test_install_sends_bounded_chunks_and_preserves_command_failure(self):
        adapter = chi_bench.HealthHarnessAgent()
        fake = FakeEnvironment()
        adapter.exec_as_root = fake.exec_as_root
        with patch.object(chi_bench, "HARBOR_AVAILABLE", True):
            asyncio.run(adapter.install(fake))
        self.assertGreater(len(fake.commands), 3)
        append_commands = fake.commands[1:-1]
        encoded = "".join(shlex.split(command)[2] for command in append_commands)
        raw = base64.b64decode(encoded, validate=True)
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as bundle:
            names = set(bundle.getnames())
        self.assertIn("health_harness/engine.py", names)
        self.assertIn("health_harness/data/micro_roles.json", names)
        self.assertTrue(all(len(shlex.split(command)[2]) <= 16000 for command in append_commands))
        self.assertTrue(all("secret" not in command for command in fake.commands))
        failing = FakeEnvironment(fail_at=2)
        adapter.exec_as_root = failing.exec_as_root
        with patch.object(chi_bench, "HARBOR_AVAILABLE", True):
            with self.assertRaisesRegex(RuntimeError, "remote command failed"):
                asyncio.run(adapter.install(failing))
        failed_exit = FakeEnvironment(exit_code=23)
        adapter.exec_as_root = failed_exit.exec_as_root
        with patch.object(chi_bench, "HARBOR_AVAILABLE", True):
            with self.assertRaisesRegex(RuntimeError, "exit 23"):
                asyncio.run(adapter.install(failed_exit))

    def test_missing_harbor_is_actionable(self):
        with patch.object(chi_bench, "HARBOR_AVAILABLE", False):
            with self.assertRaisesRegex(RuntimeError, "pinned chi-bench Harbor runner"):
                asyncio.run(chi_bench.HealthHarnessAgent().install(FakeEnvironment()))

    def test_run_forwards_explicit_config_without_putting_key_in_command(self):
        agent = FakeAgent()
        with patch.object(chi_bench, "HARBOR_AVAILABLE", True):
            asyncio.run(chi_bench.HealthHarnessAgent.run(agent, "instruction", object(), object()))
        command, env = agent.call
        self.assertIn("HEALTH_HARNESS_API_KEY", env)
        self.assertNotIn("secret-value", command)
        self.assertIn("HEALTH_HARNESS_SCOPE_JSON", env)
        self.assertIn("HEALTH_HARNESS_LIMITS_JSON", env)
        self.assertIn("HEALTH_HARNESS_CASE_FOLDER", env)
        self.assertIn("/logs/agent/health-harness-", command)

    def test_runner_config_is_scope_hashed_and_uses_narrow_roots(self):
        scope = dict(environment="e", task="t", organization="o", principal="p", patient="pt", case="../../bad")
        env = {
            "HEALTH_HARNESS_DOMAIN": "CM", "HEALTH_HARNESS_SCOPE_JSON": json.dumps(scope),
            "HEALTH_HARNESS_MODEL": "m", "HEALTH_HARNESS_BASE_URL": "https://model.invalid/v1",
            "HEALTH_HARNESS_API_KEY": "secret", "HEALTH_HARNESS_MCP_URL": "http://mcp.invalid/mcp",
            "HEALTH_HARNESS_INSTRUCTION_B64": base64.b64encode(b"instruction").decode(),
            "HEALTH_HARNESS_CASE_FOLDER": "/logs/artifacts/task-a",
            "HEALTH_HARNESS_COMPOSITION": "helpers", "HEALTH_HARNESS_LIMITS_JSON": '{"max_tool_calls":9}',
        }
        captured = {}

        def fake_run_config(path, *, resume):
            captured.update(json.loads(Path(path).read_text(encoding="utf-8")))
            captured["resume"] = resume
            return 0

        with patch.dict(os.environ, env, clear=True), patch("health_harness.cli._run_config", fake_run_config):
            self.assertEqual(0, chi_bench._run_inside_environment())
        self.assertEqual("helpers", captured["composition"])
        self.assertEqual({"max_tool_calls": 9}, captured["limits"])
        self.assertIn("/logs/artifacts/task-a/", captured["workspace"].replace("\\", "/"))
        self.assertTrue(captured["storage"].replace("\\", "/").startswith("/logs/agent/"))
        self.assertTrue(captured["output_dir"].replace("\\", "/").startswith("/logs/agent/"))
        expected_case = "case-" + hashlib.sha256(b"../../bad").hexdigest()[:16]
        self.assertTrue(captured["workspace"].replace("\\", "/").endswith(f"/{expected_case}/care-manager"))
        self.assertEqual(["/workspace/skills/managed-care-operations-handbook",
                          "/opt/healthverse-task-assets/tool_reference.md",
                          "\\logs\\artifacts\\task-a\\" + expected_case + "\\care-manager\\incoming_request"],
                         captured["read_roots"])
        self.assertEqual("HEALTH_HARNESS_API_KEY", captured["provider"]["key_env"])
        self.assertNotIn("secret", json.dumps(captured))


if __name__ == "__main__":
    unittest.main()
