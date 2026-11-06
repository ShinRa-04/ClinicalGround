import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import launch_chi_bench


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.task = self.root / "task"
        self.task.mkdir()
        (self.task / "task.toml").write_text("[task]\n", encoding="utf-8")
        self.scope = self.root / "scope.json"
        self.scope.write_text(json.dumps(dict(environment="e", task="t", organization="o", principal="p",
                                              patient="pt", case="c")), encoding="utf-8")
        self.args = ["--task-folder", str(self.task), "--scope-json", str(self.scope), "--domain", "PA",
                     "--model", "model-x", "--base-url", "https://model.invalid/v1", "--mcp-url",
                     "http://mcp.invalid/mcp"]

    def tearDown(self):
        self.temp.cleanup()

    def test_default_is_planned_direct_harbor_import(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(0, launch_chi_bench.main(self.args))
        report = json.loads(output.getvalue())
        self.assertEqual("planned", report["mode"])
        self.assertIn("health_harness.chi_bench:HealthHarnessAgent", report["argv"])
        self.assertIn("--environment-import-path", report["argv"])
        self.assertIn("chi_bench.experiment.docker_env:ChiBenchDockerEnvironment", report["argv"])
        self.assertEqual("trials", report["argv"][1])
        self.assertNotIn("--agent", report["argv"])
        self.assertIn("HEALTH_HARNESS_API_KEY=${HEALTH_HARNESS_API_KEY}", report["argv"])
        self.assertIn("--trials-dir", report["argv"])
        controller_path = report["controller_env"]["PYTHONPATH"].split(os.pathsep)[0]
        self.assertEqual(str(Path(launch_chi_bench.__file__).resolve().parent), controller_path)

    def test_execute_requires_key_and_passes_secret_only_to_child_process(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(2, launch_chi_bench.main(self.args + ["--execute"]))
        with patch.dict(os.environ, {"HEALTH_HARNESS_API_KEY": "secret"}, clear=True), \
             patch("launch_chi_bench.subprocess.run") as run:
            run.return_value.returncode = 7
            self.assertEqual(7, launch_chi_bench.main(self.args + ["--execute"]))
            command = run.call_args.args[0]
            self.assertTrue(any(value == "HEALTH_HARNESS_API_KEY=${HEALTH_HARNESS_API_KEY}" for value in command))
            self.assertNotIn("secret", " ".join(command))
            child_env = run.call_args.kwargs["env"]
            self.assertEqual(str(Path(launch_chi_bench.__file__).resolve().parent),
                             child_env["PYTHONPATH"].split(os.pathsep)[0])


if __name__ == "__main__":
    unittest.main()
