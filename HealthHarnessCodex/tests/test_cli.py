import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from health_harness_codex.cli import main


class CLITests(unittest.TestCase):
    def test_default_command_runs_all_three_synthetic_domains(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main([])
        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual(["PA", "UM", "CM"], [item["domain"] for item in report["results"]])
        self.assertTrue(all(item["status"] == "complete" and item["synthetic_only"] for item in report["results"]))

    def test_configured_run_requires_explicit_live_flag_before_any_endpoint_use(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "config.json"
            config.write_text("{}", encoding="utf-8")
            with self.assertRaises(SystemExit) as error:
                main(["--config", str(config)])
            self.assertEqual(2, error.exception.code)

    def test_config_rejects_inline_provider_secret(self):
        from health_harness_codex.cli import _run_config
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "config.json"
            config.write_text(json.dumps({"provider": {"api_key": "must-not-be-here"}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "environment-variable name"):
                _run_config(config, resume=False)

    def test_configured_live_run_requires_scope_bound_operator_contract_before_setup(self):
        from health_harness_codex.cli import _run_config

        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "config.json"
            config.write_text(json.dumps({
                "scope": {"environment": "synthetic", "task": "task-1", "organization": "org",
                          "principal": "actor", "patient": "patient-1", "case": "case-1"},
                "instruction": "Read one synthetic case.", "domain": "PA",
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "completion_contract"):
                _run_config(config, resume=False)


if __name__ == "__main__":
    unittest.main()
