from __future__ import annotations

import hashlib
import contextlib
import csv
import json
import io
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from health_harness_codex.batch import BatchConfig, BatchError, enumerate_public_tasks, main, run_batch


REPO = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO / "runs"


class FakeWorld:
    def __init__(self, *, missing_grade=False, reward=1):
        self.started = []
        self.preflighted = []
        self.stopped = []
        self.graded = []
        self.exported = []
        self.missing_grade = missing_grade
        self.reward = reward
        self.logs = {}
        self._start_lock = threading.Lock()
        self._start_sequence = 0

    def start(self, task, container_name, logs_dir):
        with self._start_lock:
            self._start_sequence += 1
            container = f"container-{self._start_sequence}"
            self.started.append((task.domain, task.task_id, container_name))
            self.logs[container] = logs_dir
        logs_dir.mkdir(parents=True, exist_ok=True)
        return container

    def preflight(self, container, task, timeout):
        self.preflighted.append((container, task.domain, timeout))
        return ["synthetic.actor.read"]

    def grade(self, container, task, output_name, timeout):
        self.graded.append((container, task.task_id, output_name))
        if not self.missing_grade:
            verifier = self.logs[container] / output_name
            verifier.mkdir(parents=True, exist_ok=True)
            (verifier / "reward.json").write_text(json.dumps({"reward": self.reward}), encoding="utf-8")
            (verifier / "scorecard.json").write_text(json.dumps({
                "checks": {"synthetic.check": "passed" if self.reward else "failed"},
                "total_checks": 1, "binary_reward": self.reward,
            }), encoding="utf-8")
            (verifier / "verifier_context.json").write_text(json.dumps({
                "judge_unavailable_reason": None, "degraded_rubric_ids": [],
            }), encoding="utf-8")
            (verifier / "exported_state.json").write_text("{}", encoding="utf-8")
        return {"returncode": 0 if self.reward else 1, "timed_out": False, "export_timeout": False}

    def stop(self, container):
        self.stopped.append(container)

    def export_state(self, container, timeout):
        self.exported.append((container, timeout))
        return {"fixture": "opaque synthetic export", "workspace_root": "/logs/artifacts"}


class BatchTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows sharing-violation behavior")
    def test_atomic_manifest_retries_transient_reader_lock_without_replaying_work(self):
        from health_harness_codex.batch import _atomic_json
        target = self.root / "metadata.json"
        target.write_text('{"revision":1}')
        original_replace = Path.replace
        calls = []
        busy = PermissionError("synthetic reader lock")
        busy.winerror = 32

        def replace(source, destination):
            calls.append(1)
            if len(calls) < 3:
                raise busy
            return original_replace(source, destination)

        with patch.object(Path, "replace", autospec=True, side_effect=replace), patch("health_harness_codex.batch.time.sleep"):
            _atomic_json(target, {"revision": 2})
        self.assertEqual(3, len(calls))
        self.assertEqual({"revision": 2}, json.loads(target.read_text()))

    @unittest.skipUnless(os.name == "nt", "Windows sharing-violation behavior")
    def test_atomic_manifest_permanent_denial_preserves_previous_valid_file(self):
        from health_harness_codex.batch import _atomic_json
        target = self.root / "metadata.json"
        target.write_text('{"revision":1}')
        busy = PermissionError("synthetic persistent denial")
        busy.winerror = 5
        with patch.object(Path, "replace", side_effect=busy) as replace, patch("health_harness_codex.batch.time.sleep"):
            with self.assertRaises(PermissionError):
                _atomic_json(target, {"revision": 2})
        self.assertEqual(20, replace.call_count)
        self.assertEqual({"revision": 1}, json.loads(target.read_text()))
        self.assertEqual([], list(self.root.glob(".metadata.json-*.tmp")))

    def setUp(self):
        self._console_log_patch = patch("health_harness_codex.batch.log_event", return_value="")
        self._console_log_patch.start()
        RUNS_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="batch-tests-", dir=RUNS_ROOT)
        self.root = Path(self.temp.name)
        self.dataset = self.root / "dataset"
        self._make_domain("prior_auth_provider", "pa_provider", "pa_provider", 25)
        self._make_domain("prior_auth_um", "pa_um", "pa_um", 25)
        self._make_domain("care_management", "cm", "cm", 25)

    def tearDown(self):
        self.temp.cleanup()
        self._console_log_patch.stop()

    def _make_domain(self, folder, domain, prefix, count):
        tasks_root = self.dataset / folder / "tasks"
        for index in range(count):
            task_id = f"{prefix}_synthetic_{index:02d}"
            task = tasks_root / task_id
            task.mkdir(parents=True)
            (task / "instruction.md").write_text(f"Synthetic public task {domain} {index}\n", encoding="utf-8")
            # Enumeration must not inspect hidden contents; this sentinel is never copied into a plan.
            fixtures = task / "fixtures"
            fixtures.mkdir()
            (fixtures / "expectations.json").write_text("never read", encoding="utf-8")

    def _config(self, run_name="batch", **overrides):
        synthetic_executable = self.root / "synthetic-codex.exe"
        if not synthetic_executable.exists():
            synthetic_executable.write_bytes(b"synthetic executable identity for offline batch tests")
        values = {"dataset_root": self.dataset, "run_dir": self.root / run_name,
                  "domains": ("pa_provider",), "attempts": 1, "concurrency": 1,
                  "codex_executable": str(synthetic_executable),
                  "budgets": {"max_model_calls": 48, "max_tool_calls": 240, "max_context_chars": 180000,
                              "max_output_tokens": 4000},
                  "instruction_sources": (), "expected_instruction_hashes": ()}
        values.update(overrides)
        return BatchConfig(**values)

    @staticmethod
    def _source_identity():
        return {"source_commit": "test-source", "source_fingerprint": "a" * 64, "source_files": 1}

    @staticmethod
    def _case_runner(container, task_dir, run_dir, executable, pins, **kwargs):
        run_dir.mkdir(parents=True, exist_ok=True)
        state = sqlite3.connect(run_dir / "state.sqlite")
        state.execute("CREATE TABLE cases (state_json TEXT NOT NULL)")
        state.execute("INSERT INTO cases VALUES (?)", (json.dumps({"messages": []}),))
        state.commit()
        state.close()
        local = {"status": "complete", "model_calls": 2, "tool_calls": 1}
        (run_dir / "run.result.json").write_text(json.dumps({"local_harness": local}), encoding="utf-8")
        (run_dir / "evaluation.json").write_text(json.dumps({
            "metadata": {"source_commit": "test-source", "source_fingerprint": "a" * 64},
            "harness_status": "complete",
        }), encoding="utf-8")
        return {"local_harness": local}

    def test_fake_world_allocates_unique_container_bindings_under_concurrent_start(self):
        world = FakeWorld()
        tasks = [SimpleNamespace(domain="pa_provider", task_id="synthetic-a"),
                 SimpleNamespace(domain="pa_provider", task_id="synthetic-b")]
        log_dirs = [self.root / "logs" / "attempt-a", self.root / "logs" / "attempt-b"]
        # Synchronize the two start calls, not Path.mkdir's recursive retry
        # after a missing parent (which can enter this barrier a second time).
        log_dirs[0].parent.mkdir(parents=True,exist_ok=True)
        rendezvous = threading.Barrier(2)
        original_mkdir = Path.mkdir

        def synchronized_mkdir(path, *args, **kwargs):
            if path in log_dirs:
                rendezvous.wait(timeout=5)
            return original_mkdir(path, *args, **kwargs)

        with patch.object(Path, "mkdir", synchronized_mkdir):
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(world.start, task, f"logical-{index}", log_dir)
                           for index, (task, log_dir) in enumerate(zip(tasks, log_dirs))]
                containers = [future.result(timeout=10) for future in futures]

        self.assertEqual(2, len(set(containers)))
        self.assertEqual(2, len(world.started))
        self.assertEqual({str(log_dirs[0]), str(log_dirs[1])},
                         {str(world.logs[container]) for container in containers})

    def test_composition_is_frozen_and_forwarded_to_actual_actor_invocation(self):
        for composition in ('combined','helpers','team'):
            seen=[]
            def actor(*args,**kwargs):
                seen.append(kwargs['composition'])
                self.assertEqual('auto',kwargs['recovery_helper_policy'])
                self.assertEqual(600,kwargs['active_timeout'])
                self.assertEqual('gpt-6-luna',kwargs['model_name'])
                return self._case_runner(*args,**kwargs)
            result=run_batch(self._config(run_name='composition-'+composition,composition=composition,active_timeout=600),
                world=FakeWorld(),case_runner=actor,source_identity=self._source_identity)
            self.assertTrue(seen)
            self.assertEqual({composition},set(seen))
            self.assertEqual(composition,result['frozen_config']['composition'])
            self.assertEqual('auto',result['frozen_config']['recovery_helper_policy'])
            self.assertEqual(600,result['frozen_config']['model_request_active_timeout_seconds'])
        self.assertEqual('helpers',self._config().composition)

    def test_enumerates_three_domains_and_plan_only_never_calls_world_or_actor(self):
        tasks = enumerate_public_tasks(self.dataset)
        self.assertEqual(75, len(tasks))
        self.assertEqual({"pa_provider": 25, "pa_um": 25, "cm": 25},
                         {domain: sum(task.domain == domain for task in tasks)
                          for domain in ("pa_provider", "pa_um", "cm")})
        world = FakeWorld()
        plan = run_batch(self._config("plan", domains=("pa_provider", "pa_um", "cm")),
                         plan_only=True, world=world, case_runner=self._case_runner,
                         source_identity=self._source_identity)
        self.assertEqual("plan_only", plan["status"])
        self.assertEqual(75, len(plan["tasks"]))
        self.assertTrue(plan["no_inference_or_docker"])
        self.assertEqual([], world.started)
        self.assertEqual([], world.preflighted)
        self.assertTrue(all(len(task["instruction_sha256"]) == 64 for task in plan["tasks"]))
        self.assertNotIn("never read", json.dumps(plan))

    def test_batch_cli_defaults_to_deferred_grading_without_extra_flag(self):
        observed = []

        def fake_run_batch(config, *, plan_only=False):
            observed.append((config.defer_grading, plan_only))
            return {"status": "plan_only"}

        stdout = io.StringIO()
        with patch("health_harness_codex.batch.run_batch", side_effect=fake_run_batch), \
                contextlib.redirect_stdout(stdout):
            result = main(["--dataset-root", str(self.dataset), "--run-dir", str(self.root / "cli"),
                           "--plan-only"])
        self.assertEqual(0, result)
        self.assertEqual([(True, True)], observed)
        self.assertIn('"status": "plan_only"', stdout.getvalue())

    def test_batch_cli_default_final_output_is_concise_and_distinguishes_saved_from_failed(self):
        cases = [
            ("saved", {
                "summary": {"overall": {"graded_attempts": 0, "ungraded_attempts": 0}},
                "tasks": [{"attempts": [{"status": "deferred_ready"}]}],
            }, "Batch actors settled: 1/1 tasks; 1 snapshots saved; 0 attempts pending; 0 failed; 0 ungraded; 0 need reconciliation; grading deferred."),
            ("stopped", {
                "execution_stop_reason": {"kind": "consecutive_pre_model_setup_failures"},
                "summary": {"overall": {"graded_attempts": 0, "ungraded_attempts": 0}},
                "tasks": [{"attempts": [{"status": "setup_failure"}]},
                          {"attempts": [{"status": "pending"}]}],
            }, "Batch stopped early: 1/2 tasks settled; 1 attempts pending; 0 snapshots saved; 1 failed; 0 ungraded; 0 need reconciliation."),
        ]
        for name, batch_result, expected in cases:
            with self.subTest(name=name):
                stdout = io.StringIO()
                with patch("health_harness_codex.batch.run_batch", return_value=batch_result), \
                        contextlib.redirect_stdout(stdout):
                    result = main(["--dataset-root", str(self.dataset), "--run-dir", str(self.root / name)])
                self.assertEqual(0, result)
                self.assertIn(expected, stdout.getvalue())
                self.assertIn(f"Manifest: {self.root / name / 'batch.manifest.json'}", stdout.getvalue())
                self.assertNotIn("clinical", stdout.getvalue().casefold())

    def test_batch_cli_json_summary_flag_preserves_machine_output(self):
        batch_result = {"summary": {"overall": {"graded_attempts": 1}}, "tasks": []}
        stdout = io.StringIO()
        with patch("health_harness_codex.batch.run_batch", return_value=batch_result), \
                contextlib.redirect_stdout(stdout):
            result = main(["--dataset-root", str(self.dataset), "--run-dir", str(self.root / "json"),
                           "--json-summary"])
        self.assertEqual(0, result)
        rendered = json.loads(stdout.getvalue())
        self.assertEqual("batch_finished", rendered["status"])
        self.assertEqual(batch_result["summary"], rendered["summary"])
        self.assertEqual(str(self.root / "json" / "batch.manifest.json"), rendered["manifest"])

    def test_default_codex_executable_uses_current_installed_official_path(self):
        from health_harness_codex.batch import DEFAULT_CODEX_EXECUTABLE, _discover_codex_executable
        self.assertEqual(_discover_codex_executable(), DEFAULT_CODEX_EXECUTABLE)
        self.assertEqual(str(DEFAULT_CODEX_EXECUTABLE), BatchConfig(dataset_root=self.dataset,
                                                    run_dir=self.root / "default-codex").codex_executable)

    def test_codex_discovery_handles_version_directory_replacement(self):
        from health_harness_codex.batch import _discover_codex_executable
        install = self.root / "official-bin"
        older = install / "old-version" / "codex.exe"
        newer = install / "new-version" / "codex.exe"
        for path in (older, newer):
            path.parent.mkdir(parents=True)
            path.write_bytes(b"synthetic executable")
        os.utime(older, (100, 100))
        os.utime(newer, (200, 200))
        self.assertEqual(newer, _discover_codex_executable(install))
        newer.unlink()
        self.assertEqual(older, _discover_codex_executable(install))
        older.unlink()
        self.assertEqual(install / "codex.exe", _discover_codex_executable(install))

    def test_native_executable_preflight_rejects_bad_paths_before_world_creation(self):
        cases = [
            (str(self.root / "missing-codex.exe"), "missing or is not a regular file"),
            (str(self.root), "missing or is not a regular file"),
            ("relative-codex.exe", "must be absolute"),
        ]
        for index, (executable, reason) in enumerate(cases):
            with self.subTest(executable=executable):
                config = self._config(f"bad-codex-{index}", task_ids=("pa_provider_synthetic_00",),
                                      codex_executable=executable)
                world = FakeWorld()
                with self.assertRaisesRegex(BatchError, reason):
                    run_batch(config, world=world, source_identity=self._source_identity)
                self.assertEqual([], world.started)

    def test_native_executable_hash_change_refuses_resume_before_world_creation(self):
        config = self._config("changed-codex", task_ids=("pa_provider_synthetic_00",))
        world = FakeWorld()
        first = run_batch(config, world=world, case_runner=self._case_runner,
                          source_identity=self._source_identity)
        attempt = first["tasks"][0]["attempts"][0]
        self.assertEqual(64, len(first["frozen_config"]["codex_executable_sha256"]))
        self.assertEqual("graded", attempt["status"])
        Path(config.codex_executable).write_bytes(b"different synthetic executable identity")

        world_after = FakeWorld()
        with self.assertRaisesRegex(BatchError, "native executable"):
            run_batch(config, world=world_after, case_runner=self._case_runner,
                      source_identity=self._source_identity)
        self.assertEqual([], world_after.started)

    def test_settled_run_grades_once_and_resume_skips_exact_completed_attempt(self):
        task_id = "pa_provider_synthetic_00"
        config = self._config(task_ids=(task_id,))
        world = FakeWorld()
        calls = []

        def case_runner(*args, **kwargs):
            calls.append((args, kwargs))
            return self._case_runner(*args, **kwargs)

        first = run_batch(config, world=world, case_runner=case_runner, source_identity=self._source_identity)
        initial_container_name = world.started[0][2]
        self.assertEqual(1, len(world.started))
        self.assertEqual(1, len(world.preflighted))
        self.assertEqual(1, len(world.stopped))
        attempt = first["tasks"][0]["attempts"][0]
        self.assertEqual("graded", attempt["status"])
        self.assertEqual(1, attempt["official_score"])
        self.assertTrue((config.run_dir / "pa_provider" / task_id / "attempt-1" / "state.snapshot.sqlite").is_file())
        second = run_batch(config, world=world, case_runner=case_runner, source_identity=self._source_identity)
        self.assertEqual(1, len(world.started))
        self.assertEqual(initial_container_name, world.started[0][2])
        self.assertEqual(1, len(calls))
        self.assertTrue(second["summary"]["overall"]["coverage_complete"])
        self.assertEqual(1.0, second["summary"]["overall"]["pass_at_1"])
        self.assertFalse(second["summary"]["full_dataset_coverage_complete"])
        self.assertTrue((config.run_dir / "graded_results.partial.csv").is_file())
        self.assertFalse((config.run_dir / "kaggle_submission.csv").exists())
        event_records = [json.loads(line) for line in
                         (config.run_dir / "batch.events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(event["kind"] == "grading_started" for event in event_records))
        self.assertTrue(any(event["kind"] == "grading_finished" and event.get("status") == "graded"
                            for event in event_records))
        self.assertTrue(any(event["kind"] == "task_settled" and event.get("status") == "graded"
                            for event in event_records))
        self.assertTrue(any(event["kind"] == "batch_finished" and event.get("failed") == 0 and
                            event.get("saved") == 0 for event in event_records))

    def test_deferred_actor_snapshots_actual_export_then_stops_without_grading_or_replay(self):
        task_id = "pa_provider_synthetic_00"
        config = self._config(task_ids=(task_id,), defer_grading=True)
        world = FakeWorld()
        actor_calls = []

        def actor(*args, **kwargs):
            actor_calls.append(1)
            return self._case_runner(*args, **kwargs)

        first = run_batch(config, world=world, case_runner=actor, source_identity=self._source_identity)
        record = first["tasks"][0]["attempts"][0]
        self.assertEqual("deferred_ready", record["status"])
        self.assertEqual("pending", record["grading_status"])
        self.assertIsNone(record["official_score"])
        self.assertEqual([], world.graded)
        self.assertEqual(1, len(world.exported))
        self.assertEqual(1, len(world.stopped))
        from health_harness_codex.batch import _verify_deferred_attempt
        task_record = first["tasks"][0]
        snapshot = _verify_deferred_attempt(config.run_dir, task_record, record,
                                            first["frozen_config"])
        self.assertEqual("opaque synthetic export",
                         json.loads((snapshot / "exported_state.json").read_text(encoding="utf-8"))["fixture"])
        self.assertTrue((snapshot / "logs").is_dir())
        # Generic resume validation checks snapshot integrity regardless of
        # experimental provenance; official grading has its own backend gate.
        codex_frozen = {**first["frozen_config"], "simulator": {
            "backend": "codex", "experimental_official_grade_eligible": False,
        }}
        self.assertEqual(snapshot, _verify_deferred_attempt(config.run_dir, task_record, record, codex_frozen))
        second = run_batch(config, world=world, case_runner=actor, source_identity=self._source_identity)
        self.assertEqual(1, len(actor_calls))
        self.assertEqual(1, len(world.started))
        self.assertEqual("deferred_ready", second["tasks"][0]["attempts"][0]["status"])

    def test_concurrent_deferred_batch_events_are_ordered_and_task_correlated(self):
        task_ids = tuple(f"pa_provider_synthetic_{index:02d}" for index in range(3))
        config = self._config("lifecycle-events", task_ids=task_ids, concurrency=3, defer_grading=True)
        world = FakeWorld()
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = run_batch(config, world=world, case_runner=self._case_runner,
                               source_identity=self._source_identity)
        event_path = config.run_dir / "batch.events.jsonl"
        events = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(3, len(world.started))
        self.assertEqual(3, len(world.stopped))
        self.assertEqual(3, result["summary"]["deferred_ready_attempts"])
        self.assertEqual(3, sum(event["kind"] == "batch_progress" for event in events))
        for task_id in task_ids:
            correlated = [event for event in events if event.get("task_id") == task_id]
            self.assertTrue(all(event.get("domain") == "pa_provider" and event.get("attempt") == 1
                                for event in correlated))
            kinds = [event["kind"] for event in correlated]
            ordered = ["task_started", "world_starting", "world_started", "world_waiting",
                       "world_ready", "actor_starting", "actor_finished", "snapshot_starting",
                       "snapshot_saved", "world_stopped", "task_settled", "batch_progress"]
            positions = [kinds.index(kind) for kind in ordered]
            self.assertEqual(positions, sorted(positions))
            actor_finished = correlated[kinds.index("actor_finished")]
            self.assertEqual("complete", actor_finished["harness_status"])
            task_settled = correlated[kinds.index("task_settled")]
            self.assertEqual("deferred_ready", task_settled["status"])
        rendered = event_path.read_text(encoding="utf-8") + stdout.getvalue()
        self.assertNotIn("never read", rendered)
        self.assertNotIn("official_score", rendered)
        self.assertNotIn("clinical", rendered.casefold())

    def test_failed_deferred_export_preserves_final_world_for_reconciliation(self):
        class ExportFailureWorld(FakeWorld):
            def export_state(self, container, timeout):
                raise RuntimeError("synthetic export unavailable")

        task_id = "pa_provider_synthetic_00"
        config = self._config(task_ids=(task_id,), defer_grading=True)
        world = ExportFailureWorld()
        actor_calls = []

        def actor(*args, **kwargs):
            actor_calls.append(1)
            return self._case_runner(*args, **kwargs)

        first = run_batch(config, world=world, case_runner=actor, source_identity=self._source_identity)
        attempt = first["tasks"][0]["attempts"][0]
        attempt_dir = config.run_dir / "pa_provider" / task_id / "attempt-1"
        self.assertEqual("needs_reconciliation", attempt["status"])
        self.assertEqual("not_ready", attempt["grading_status"])
        self.assertFalse(attempt["container_stopped"])
        self.assertTrue(attempt["world_preserved_for_reconciliation"])
        self.assertIsNone(attempt["official_score"])
        self.assertFalse((attempt_dir / "deferred_snapshot").exists())
        self.assertEqual([], world.stopped)
        self.assertEqual([], world.graded)

        second = run_batch(config, world=world, case_runner=actor, source_identity=self._source_identity)
        self.assertEqual(1, len(actor_calls))
        self.assertEqual(1, len(world.started))
        self.assertEqual([], world.stopped)
        self.assertEqual("needs_reconciliation", second["tasks"][0]["attempts"][0]["status"])

    def test_failed_deferred_snapshot_preserves_final_world_for_reconciliation(self):
        task_id = "pa_provider_synthetic_00"
        config = self._config("snapshot-failure", task_ids=(task_id,), defer_grading=True)
        world = FakeWorld()
        actor_calls = []

        def actor(*args, **kwargs):
            actor_calls.append(1)
            return self._case_runner(*args, **kwargs)

        with patch("health_harness_codex.batch._capture_deferred_snapshot",
                   side_effect=BatchError("synthetic snapshot write failure")):
            result = run_batch(config, world=world, case_runner=actor, source_identity=self._source_identity)
        attempt = result["tasks"][0]["attempts"][0]
        self.assertEqual("needs_reconciliation", attempt["status"])
        self.assertFalse(attempt["container_stopped"])
        self.assertTrue(attempt["world_preserved_for_reconciliation"])
        self.assertEqual([], world.stopped)
        self.assertEqual([], world.graded)
        self.assertFalse((config.run_dir / "pa_provider" / task_id / "attempt-1" /
                          "deferred_snapshot").exists())

    def test_container_names_hash_full_batch_path_not_truncated_prefix(self):
        from health_harness_codex.batch import _container_name
        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        run_a = self.root / "long-batch-root-prefix-1234567890-A"
        run_b = self.root / "long-batch-root-prefix-1234567890-B"
        self.assertEqual(run_a.name[:18], run_b.name[:18])
        name_a = _container_name(run_a, task, 1)
        name_b = _container_name(run_b, task, 1)
        self.assertNotEqual(name_a, name_b)
        self.assertTrue(name_a.startswith("bigdata-health-codex-"))

    def test_changed_public_instruction_refuses_resume_before_start(self):
        task_id = "pa_provider_synthetic_00"
        config = self._config(task_ids=(task_id,))
        world = FakeWorld()
        run_batch(config, world=world, case_runner=self._case_runner, source_identity=self._source_identity)
        instruction = self.dataset / "prior_auth_provider" / "tasks" / task_id / "instruction.md"
        instruction.write_text("changed public instruction\n", encoding="utf-8")
        world_after = FakeWorld()
        with self.assertRaisesRegex(BatchError, "configuration differ"):
            run_batch(config, world=world_after, case_runner=self._case_runner,
                      source_identity=self._source_identity)
        self.assertEqual([], world_after.started)

    def test_tampered_completed_artifact_is_not_skipped_or_reexecuted(self):
        config = self._config(task_ids=("pa_provider_synthetic_00",))
        world = FakeWorld()
        initial=run_batch(config, world=world, case_runner=self._case_runner, source_identity=self._source_identity)
        attempt=initial['tasks'][0]['attempts'][0]
        self.assertEqual('graded',attempt['status'],json.dumps(attempt,default=str))
        receipt_path=config.run_dir/attempt['attempt_dir']/'official-evaluation-receipt.json'
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        self.assertEqual('official_1',receipt['selected_output'])
        self.assertEqual({'reward','scorecard','exported_state','verifier_context'},set(receipt['artifacts']))
        scorecard = (config.run_dir / "pa_provider" / "pa_provider_synthetic_00" / "attempt-1" /
                     "container_logs" / "official_1" / "scorecard.json")
        scorecard.write_text("{}", encoding="utf-8")
        world_after = FakeWorld()
        with self.assertRaisesRegex(BatchError, "official artifact changed"):
            run_batch(config, world=world_after, case_runner=self._case_runner,
                      source_identity=self._source_identity)
        self.assertEqual([], world_after.started)

    def test_missing_official_scorecard_is_ungraded_not_a_synthetic_zero(self):
        config = self._config(task_ids=("pa_provider_synthetic_00",))
        result = run_batch(config, world=FakeWorld(missing_grade=True), case_runner=self._case_runner,
                           source_identity=self._source_identity)
        attempt = result["tasks"][0]["attempts"][0]
        self.assertEqual("ungraded", attempt["status"])
        self.assertIsNone(attempt["official_score"])
        self.assertEqual("official_artifact_missing", attempt["grade"]["reason"])
        self.assertEqual(0, result["summary"]["overall"]["evaluated_tasks"])
        self.assertIsNone(result["summary"]["overall"]["pass_at_1"])

    def test_reward_zero_with_failed_check_and_official_exit_one_is_graded(self):
        config = self._config(task_ids=("pa_provider_synthetic_00",))
        result = run_batch(config, world=FakeWorld(reward=0), case_runner=self._case_runner,
                           source_identity=self._source_identity)
        attempt = result["tasks"][0]["attempts"][0]
        self.assertEqual("graded", attempt["status"])
        self.assertEqual(0, attempt["official_score"])
        self.assertEqual(1, result["summary"]["overall"]["evaluated_tasks"])
        self.assertEqual(0.0, result["summary"]["overall"]["pass_at_1"])

    def test_judge_unavailability_is_ungraded_with_safe_reason_only(self):
        from health_harness_codex.batch import _official_grade
        verifier = self.root / "safe-judge-check" / "official_1"
        verifier.mkdir(parents=True)
        (verifier / "reward.json").write_text(json.dumps({"reward": 1}), encoding="utf-8")
        (verifier / "scorecard.json").write_text(json.dumps({
            "checks": {"judge.semantic_quality": "passed"}, "total_checks": 1, "binary_reward": 1,
        }), encoding="utf-8")
        secret_detail = "synthetic private auth diagnostic"
        (verifier / "verifier_context.json").write_text(json.dumps({
            "judge_unavailable_reason": secret_detail,
        }), encoding="utf-8")
        (verifier / "exported_state.json").write_text("{}", encoding="utf-8")

        status, result = _official_grade(verifier.parent, "official_1", 0)
        self.assertEqual("ungraded", status)
        self.assertEqual("official_judge_unavailable", result["reason"])
        self.assertEqual("unavailable", result["judge_availability"])
        self.assertNotIn(secret_detail, json.dumps(result))

    def test_full_dataset_csv_is_created_only_after_all_75_first_attempts_are_graded(self):
        config = self._config("full", domains=("pa_provider", "pa_um", "cm"), concurrency=3)
        with contextlib.redirect_stderr(io.StringIO()):
            result = run_batch(config, world=FakeWorld(), case_runner=self._case_runner,
                               source_identity=self._source_identity)
        self.assertEqual(75, result["summary"]["overall"]["first_attempt_graded_tasks"])
        self.assertTrue(result["summary"]["full_dataset_coverage_complete"])
        self.assertEqual(1.0, result["summary"]["overall"]["pass_at_1"])
        with (config.run_dir / "kaggle_submission.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(75, len(rows))
        self.assertEqual({"task_id", "reward"}, set(rows[0]))
        self.assertFalse((config.run_dir / "graded_results.partial.csv").exists())

    def test_interrupted_actor_attempt_is_preserved_and_never_replayed(self):
        config = self._config(task_ids=("pa_provider_synthetic_00",))
        world = FakeWorld()
        calls = []

        def interrupted(*args, **kwargs):
            calls.append(1)
            raise RuntimeError("synthetic unknown write interruption")

        first = run_batch(config, world=world, case_runner=interrupted, source_identity=self._source_identity)
        self.assertEqual("interrupted", first["tasks"][0]["attempts"][0]["status"])
        second = run_batch(config, world=world, case_runner=interrupted, source_identity=self._source_identity)
        self.assertEqual(1, len(calls))
        self.assertEqual(1, len(world.started))
        self.assertEqual("interrupted", second["tasks"][0]["attempts"][0]["status"])

    def test_case_discovery_setup_failure_without_actions_is_not_an_unknown_write(self):
        config = self._config(task_ids=("pa_provider_synthetic_00",))
        world = FakeWorld()
        calls = []

        def failed_discovery(container, task_dir, run_dir, executable, pins, **kwargs):
            calls.append(1)
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "evaluation.json").write_text(json.dumps({
                "metadata": {"source_commit": "test-source", "source_fingerprint": "a" * 64},
                "harness_status": "setup_failure",
            }), encoding="utf-8")
            raise RuntimeError("synthetic actor discovery setup failure")

        first = run_batch(config, world=world, case_runner=failed_discovery,
                          source_identity=self._source_identity)
        self.assertEqual("setup_failure", first["tasks"][0]["attempts"][0]["status"])
        self.assertEqual([], world.graded)
        events = [json.loads(line) for line in (config.run_dir / "batch.events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(event["kind"] == "actor_finished" and
                            event.get("harness_status") == "setup_failure" for event in events))
        self.assertTrue(any(event["kind"] == "stage_error" and event.get("stage") == "actor workflow"
                            and event.get("error_type") == "RuntimeError" for event in events))
        self.assertTrue(any(event["kind"] == "task_settled" and event.get("status") == "setup_failure"
                            for event in events))
        second = run_batch(config, world=world, case_runner=failed_discovery,
                           source_identity=self._source_identity)
        self.assertEqual(1, len(calls))
        self.assertEqual([], world.graded)
        self.assertEqual("setup_failure", second["tasks"][0]["attempts"][0]["status"])

    def test_three_consecutive_zero_model_setup_failures_halt_new_scheduling(self):
        task_ids = tuple([f"pa_provider_synthetic_{index:02d}" for index in range(25)] +
                         [f"pa_um_synthetic_{index:02d}" for index in range(25)] +
                         [f"cm_synthetic_{index:02d}" for index in range(25)])
        config = self._config("setup-fail-fast", domains=("pa_provider", "pa_um", "cm"),
                              task_ids=task_ids, concurrency=3, defer_grading=True)
        world = FakeWorld()
        calls = []

        def failed_before_model(container, task_dir, run_dir, executable, pins, **kwargs):
            calls.append(task_dir.name)
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "evaluation.json").write_text(json.dumps({
                "metadata": {"source_commit": "test-source", "source_fingerprint": "a" * 64},
                "harness_status": "setup_failure",
                "metrics": {"model_calls": 0, "model_calls_observed_this_segment": 0},
            }), encoding="utf-8")
            raise RuntimeError("synthetic pre-model setup failure")

        result = run_batch(config, world=world, case_runner=failed_before_model,
                           source_identity=self._source_identity)
        statuses = [attempt["status"] for task in result["tasks"] for attempt in task["attempts"]]
        stop = result.get("execution_stop_reason")
        self.assertEqual("consecutive_pre_model_setup_failures", stop["kind"])
        self.assertEqual(3, stop["threshold"])
        self.assertEqual("actor_pre_model_setup", stop["stage"])
        self.assertGreaterEqual(statuses.count("pending"), 70)
        self.assertLessEqual(len(world.started), 3 + config.concurrency - 1)
        self.assertEqual(len(world.started), len(calls))
        self.assertTrue(all(status in {"setup_failure", "pending"} for status in statuses))
        self.assertEqual([], world.graded)
        self.assertEqual(statuses.count("pending"), result["summary"]["pending_attempts"])
        events = [json.loads(line) for line in
                  (config.run_dir / "batch.events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(event["kind"] == "stage_error" and
                            event.get("stage") == "actor pre-model setup" and
                            event.get("error_type") == "RuntimeError" for event in events))
        self.assertTrue(any(event["kind"] == "actor_finished" and
                            event.get("harness_status") == "setup_failure" and
                            event.get("model_calls") == 0 for event in events))
        stopped = [event for event in events if event["kind"] == "batch_stopped_early"]
        self.assertGreaterEqual(len(stopped), 1)
        self.assertGreaterEqual(stopped[-1].get("failed", 0), 3)
        self.assertEqual(0, stopped[-1].get("saved", -1))
        self.assertEqual("stopped_early", stopped[-1].get("status"))
        rendered = (config.run_dir / "batch.events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("synthetic pre-model setup failure", rendered)

    def test_duplicate_or_unknown_exact_task_ids_fail_closed(self):
        with self.assertRaisesRegex(BatchError, "must not contain duplicates"):
            enumerate_public_tasks(self.dataset, ("pa_provider",),
                                   ("pa_provider_synthetic_00", "pa_provider_synthetic_00"))
        with self.assertRaisesRegex(BatchError, "not found"):
            enumerate_public_tasks(self.dataset, ("pa_provider",), ("not_a_public_task",))

    def test_batch_source_fingerprint_matches_standalone_receipt_fingerprint(self):
        from health_harness_codex.batch import _source_identity as batch_source_identity
        from health_harness_codex.standalone import _source_commit, _source_fingerprint
        source = batch_source_identity()
        self.assertEqual(_source_fingerprint(), source["source_fingerprint"])
        self.assertEqual(_source_commit(), source["source_commit"])

    def test_runtime_image_tag_mismatch_blocks_container_start(self):
        from health_harness_codex.batch import DockerWorldAdapter
        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        adapter = DockerWorldAdapter("docker")
        mismatch = type("Result", (), {"returncode": 0, "stdout": "sha256:" + "f" * 64})()
        with patch("health_harness_codex.batch.subprocess.run", return_value=mismatch) as run:
            with self.assertRaisesRegex(BatchError, "tag does not resolve"):
                adapter.start(task, "container-1", self.root / "logs")
            self.assertEqual(1, run.call_count)
            self.assertIn("image", run.call_args.args[0])

    def test_container_with_wrong_image_digest_is_stopped_before_preflight(self):
        from health_harness_codex.batch import DockerWorldAdapter, RUNTIME_IMAGE_SHA256
        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        adapter = DockerWorldAdapter("docker")
        responses = [
            subprocess.CompletedProcess([], 0, stdout=RUNTIME_IMAGE_SHA256, stderr=""),
            subprocess.CompletedProcess([], 0, stdout="container-id", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="sha256:" + "f" * 64, stderr=""),
            subprocess.CompletedProcess([], 0, stdout="container-name", stderr=""),
        ]
        with patch("health_harness_codex.batch.subprocess.run", side_effect=responses) as run:
            with self.assertRaisesRegex(BatchError, "did not use the frozen runtime image"):
                adapter.start(task, "container-name", self.root / "logs")
        self.assertEqual(4, run.call_count)
        self.assertEqual("stop", run.call_args_list[-1].args[0][1])

    def test_preflight_rejects_baked_instruction_hash_drift_before_tool_listing(self):
        from types import SimpleNamespace
        from health_harness_codex.batch import DockerWorldAdapter

        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        calls = []

        class FakeExecutor:
            def __init__(self, *args, **kwargs): pass
            def validate_owned_trial(self, task_id): calls.append(("validate", task_id))
            def python_json(self, script, data, timeout=None):
                calls.append(("health", data))
                return {"healthy": True, "instruction_matches": False}

        class FakeMCP:
            def __init__(self, *args, **kwargs): pass
            def list_tools(self):
                calls.append(("tools", None))
                return [SimpleNamespace(name="synthetic.tool")]

        with patch("health_harness_codex.docker_bridge.DockerExecutor", FakeExecutor), \
                patch("health_harness_codex.docker_bridge.DockerMCPClient", FakeMCP):
            with self.assertRaisesRegex(BatchError, "health/tool preflight failed"):
                DockerWorldAdapter().preflight("container", task, 2)
        self.assertEqual(["validate", "health"], [entry[0] for entry in calls])
        self.assertEqual(task.instruction_sha256, calls[1][1]["instruction_sha256"])

    def test_default_docker_world_uses_no_keys_and_network_none(self):
        from health_harness_codex.batch import DockerWorldAdapter, RUNTIME_IMAGE_SHA256
        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            if command[1:3] == ["image", "inspect"]:
                return subprocess.CompletedProcess(command, 0, stdout=RUNTIME_IMAGE_SHA256 + "\n", stderr="")
            if command[1:3] == ["inspect", "--format"]:
                return subprocess.CompletedProcess(command, 0, stdout=RUNTIME_IMAGE_SHA256 + "\n", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="container-id\n", stderr="")

        with patch("health_harness_codex.batch.subprocess.run", side_effect=fake_run):
            DockerWorldAdapter("docker").start(task, "container-1", self.root / "logs")
        docker_run = next(command for command in calls if len(command) > 1 and command[1] == "run")
        self.assertEqual("none", docker_run[docker_run.index("--network") + 1])
        self.assertNotIn("--env-file", docker_run)
        self.assertIn("HF_TOKEN=", docker_run)
        self.assertIn("ANTHROPIC_API_KEY=", docker_run)
        self.assertFalse(any("SECRET" in value for value in docker_run))

    def test_codex_simulator_world_has_loopback_only_bridge_and_private_spool_mount(self):
        from health_harness_codex.batch import DockerWorldAdapter, RUNTIME_IMAGE_SHA256, SIMULATOR_BRIDGE_TARGET
        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        spool = self.root / "attempt-1" / "simulator-spool"
        spool.mkdir(parents=True)
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            if command[1:3] == ["image", "inspect"]:
                return subprocess.CompletedProcess(command, 0, stdout=RUNTIME_IMAGE_SHA256, stderr="")
            if command[1:3] == ["inspect", "--format"]:
                return subprocess.CompletedProcess(command, 0, stdout=RUNTIME_IMAGE_SHA256, stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="container-id", stderr="")

        with patch("health_harness_codex.batch.subprocess.run", side_effect=fake_run):
            DockerWorldAdapter("docker").start(task, "container-codex", self.root / "logs-codex",
                                                 simulator_backend="codex", simulator_spool=spool)
        docker_run = next(command for command in calls if command[1] == "run")
        self.assertEqual("none", docker_run[docker_run.index("--network") + 1])
        self.assertNotIn("--publish", docker_run)
        self.assertIn(f"type=bind,source={spool.resolve()},target=/simulator-spool", docker_run)
        self.assertIn(f"target={SIMULATOR_BRIDGE_TARGET},readonly", " ".join(docker_run))
        self.assertIn("ANTHROPIC_BASE_URL=http://127.0.0.1:9765", docker_run)
        self.assertIn("ANTHROPIC_API_KEY=codex-local-bridge", docker_run)
        for variable in ("HF_TOKEN=", "OPENAI_API_KEY=", "OPENAI_BASE_URL=", "HEALTH_HARNESS_API_KEY="):
            self.assertIn(variable, docker_run)
        self.assertEqual(1, docker_run.count("ANTHROPIC_API_KEY=codex-local-bridge"))
        self.assertFalse(any("--env-file" == value for value in docker_run))

    def test_experimental_backend_requires_deferred_and_key_free_execution(self):
        base = {"dataset_root": self.dataset, "run_dir": self.root / "codex", "simulator_backend": "codex",
                "model": "gpt-6-luna", "reasoning_effort": "high", "instruction_sources": (),
                "expected_instruction_hashes": ()}
        with self.assertRaisesRegex(ValueError, "requires deferred"):
            BatchConfig(**base)
        with self.assertRaisesRegex(ValueError, "cannot use benchmark credentials"):
            BatchConfig(**{**base, "defer_grading": True, "allow_benchmark_network": True})
        cfg = BatchConfig(**{**base, "defer_grading": True})
        self.assertEqual("codex", cfg.simulator_backend)
        self.assertEqual(0, cfg.simulator_max_model_calls)
        self.assertEqual(0, cfg.simulator_max_total_chars)
        self.assertEqual(0, cfg.simulator_world_deadline_seconds)
        from health_harness_codex.batch import _frozen_config
        stronger=BatchConfig(**{**base,'defer_grading':True,'model':'gpt-6.1-sol'})
        frozen=_frozen_config(stronger,[],{}, {})
        self.assertEqual('gpt-6.1-sol',frozen['model'])
        self.assertEqual('gpt-6-luna',frozen['simulator']['model'])
        self.assertEqual('high',frozen['simulator']['reasoning_effort'])

    def test_cli_explicit_actor_model_reaches_config_without_changing_patient(self):
        with patch('health_harness_codex.batch.run_batch',return_value={'status':'planned'}) as run,contextlib.redirect_stdout(io.StringIO()):
            code=main(['--dataset-root',str(self.dataset),'--run-dir',str(self.root/'different-model'),
                '--domains','cm','--task-id','cm_000','--model','gpt-6.1-sol',
                '--simulator-backend','codex','--plan-only'])
        self.assertEqual(0,code)
        cfg=run.call_args.args[0]
        self.assertEqual('gpt-6.1-sol',cfg.model)
        self.assertEqual(('cm_000',),cfg.task_ids)
        from health_harness_codex.batch import _frozen_config
        self.assertEqual('gpt-6-luna',_frozen_config(cfg,[],{}, {})['simulator']['model'])
        self.assertTrue(run.call_args.kwargs['plan_only'])

    def test_selected_actor_model_reaches_actual_case_runner(self):
        task=enumerate_public_tasks(self.dataset,('cm',))[0]
        seen=[]
        def actor(*args,**kwargs):
            seen.append(kwargs['model_name']);return self._case_runner(*args,**kwargs)
        cfg=self._config(run_name='selected-actor',domains=('cm',),task_ids=(task.task_id,),model='gpt-6.1-sol')
        result=run_batch(cfg,world=FakeWorld(),case_runner=actor,source_identity=self._source_identity)
        self.assertEqual(['gpt-6.1-sol'],seen)
        self.assertEqual('gpt-6.1-sol',result['frozen_config']['model'])

    def test_codex_simulator_preserves_world_after_unsettled_worker(self):
        from types import SimpleNamespace
        from health_harness_codex.batch import (DEFAULT_INSTRUCTION, DEFAULT_INSTRUCTION_SHA256,
                                                DockerWorldAdapter)

        received_instruction_pins = []

        class CodexWorld(DockerWorldAdapter):
            def __init__(self):
                self.started, self.stopped, self.exported = [], [], []
            def start(self, task, container_name, logs_dir, **kwargs):
                logs_dir.mkdir(parents=True, exist_ok=True)
                self.started.append(container_name)
                return "codex-container"
            def start_simulator_bridge(self, container, task, *, request_timeout, **kwargs):
                self.bridge_timeout = request_timeout
            def preflight(self, container, task, timeout, **kwargs):
                return ["synthetic.actor.read"]
            def export_state(self, container, timeout):
                self.exported.append(container)
                return {"fixture": "opaque synthetic export", "workspace_root": "/logs/artifacts"}
            def stop(self, container):
                self.stopped.append(container)

        class Worker:
            def __init__(self, *args, **kwargs):
                received_instruction_pins.append(kwargs.get("allowed_instruction_sources"))
            def start(self):
                pass
            def stop(self):
                return SimpleNamespace(settled=False, completed_calls=0, elapsed_seconds=0.1,
                                       status="unresolved")

        config = self._config("codex-unsettled", task_ids=("pa_provider_synthetic_00",),
                              defer_grading=True, simulator_backend="codex",
                              model="gpt-6-luna", reasoning_effort="high",
                              instruction_sources=(str(DEFAULT_INSTRUCTION),),
                              expected_instruction_hashes=(DEFAULT_INSTRUCTION_SHA256,))
        world = CodexWorld()
        with patch("health_harness_codex.simulator_worker.SimulatorWorker", Worker):
            result = run_batch(config, world=world, case_runner=self._case_runner,
                               source_identity=self._source_identity)
        attempt = result["tasks"][0]["attempts"][0]
        self.assertEqual(180, world.bridge_timeout)
        self.assertEqual([{str(DEFAULT_INSTRUCTION.resolve()): DEFAULT_INSTRUCTION_SHA256}],
                         received_instruction_pins)
        self.assertEqual([], world.stopped)
        self.assertTrue(attempt["world_preserved_for_reconciliation"])
        self.assertFalse(attempt["container_stopped"])

    def test_settled_simulator_does_not_allow_stop_after_snapshot_failure(self):
        from types import SimpleNamespace
        from health_harness_codex.batch import DockerWorldAdapter

        class CodexWorld(DockerWorldAdapter):
            def __init__(self):
                self.stopped = []
            def start(self, task, container_name, logs_dir, **kwargs):
                logs_dir.mkdir(parents=True, exist_ok=True)
                return "codex-container"
            def start_simulator_bridge(self, container, task, *, request_timeout, **kwargs):
                pass
            def preflight(self, container, task, timeout, **kwargs):
                return ["synthetic.actor.read"]
            def export_state(self, container, timeout):
                return {"fixture": "opaque synthetic export", "workspace_root": "/logs/artifacts"}
            def stop(self, container):
                self.stopped.append(container)

        class Worker:
            def __init__(self, *args, **kwargs):
                pass
            def start(self):
                pass
            def stop(self):
                return SimpleNamespace(settled=True, completed_calls=1, elapsed_seconds=0.1,
                                       status="settled")

        config = self._config("codex-snapshot-fail", task_ids=("pa_provider_synthetic_00",),
                              defer_grading=True, simulator_backend="codex",
                              model="gpt-6-luna", reasoning_effort="high")
        world = CodexWorld()
        with patch("health_harness_codex.simulator_worker.SimulatorWorker", Worker):
            with patch("health_harness_codex.batch._capture_deferred_snapshot",
                       side_effect=BatchError("synthetic snapshot failure")):
                result = run_batch(config, world=world, case_runner=self._case_runner,
                                   source_identity=self._source_identity)
        attempt = result["tasks"][0]["attempts"][0]
        self.assertEqual([], world.stopped)
        self.assertTrue(attempt["world_preserved_for_reconciliation"])
        self.assertFalse(attempt["container_stopped"])

    def test_explicit_ignored_env_file_requires_opt_in_and_values_are_not_persisted(self):
        from health_harness_codex.batch import DockerWorldAdapter, RUNTIME_IMAGE_SHA256, _benchmark_environment
        fake_project = self.root / "project"
        runner = fake_project / "Runner"
        runner.mkdir(parents=True)
        env_file = runner / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=SYNTHETIC_SECRET\n", encoding="utf-8")
        with patch("health_harness_codex.batch.PROJECT_ROOT", fake_project):
            with self.assertRaisesRegex(BatchError, "requires explicit"):
                _benchmark_environment(env_file, False)
            configured = _benchmark_environment(env_file, True)
        self.assertEqual("explicit_local_benchmark_env_file", configured["mode"])
        self.assertEqual("bridge", configured["network"])
        self.assertNotIn("SYNTHETIC_SECRET", json.dumps(configured))

        task = enumerate_public_tasks(self.dataset, ("pa_provider",), ("pa_provider_synthetic_00",))[0]
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            if command[1:3] == ["image", "inspect"]:
                return subprocess.CompletedProcess(command, 0, stdout=RUNTIME_IMAGE_SHA256, stderr="")
            if command[1:3] == ["inspect", "--format"]:
                return subprocess.CompletedProcess(command, 0, stdout=RUNTIME_IMAGE_SHA256, stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="container-id", stderr="")

        with patch("health_harness_codex.batch.PROJECT_ROOT", fake_project), \
                patch("health_harness_codex.batch.subprocess.run", side_effect=fake_run):
            adapter = DockerWorldAdapter("docker", env_file, True)
            adapter.start(task, "container-env", self.root / "logs-env")
        docker_run = next(command for command in calls if command[1] == "run")
        self.assertEqual("bridge", docker_run[docker_run.index("--network") + 1])
        self.assertEqual(str(env_file), docker_run[docker_run.index("--env-file") + 1])
        self.assertNotIn("SYNTHETIC_SECRET", json.dumps(docker_run))


if __name__ == "__main__":
    unittest.main()
