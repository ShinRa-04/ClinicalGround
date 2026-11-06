from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from dataclasses import replace

from health_harness_codex.batch import BatchConfig, run_batch
from health_harness_codex.deferred_grading import (
    DeferredGradingError,
    DockerOfflineGrader,
    plan_deferred_grading,
    run_grade_later,
)


REPO = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO / "runs"


class _World:
    def __init__(self):
        self.started = []
        self.stopped = []
        self.graded = []

    def start(self, task, name, logs_dir):
        self.started.append(name)
        logs_dir.mkdir(parents=True, exist_ok=True)
        (logs_dir / "artifacts").mkdir()
        (logs_dir / "artifacts" / "actor.log").write_text("synthetic-private-payload", encoding="utf-8")
        return name

    def preflight(self, container, task, timeout):
        return ["synthetic.actor.read"]

    def export_state(self, container, timeout):
        return {"synthetic": True, "workspace_root": "/logs/artifacts"}

    def grade(self, container, task, output_name, timeout):
        self.graded.append(container)
        raise AssertionError("deferred batch must not run an inline grader")

    def stop(self, container):
        self.stopped.append(container)
        return None


class DeferredGradingTests(unittest.TestCase):
    def setUp(self):
        RUNS_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="deferred-grade-tests-", dir=RUNS_ROOT)
        self.root = Path(self.temp.name)
        self.dataset = self.root / "dataset"
        self.task_ids = ("pa_provider_synthetic_00", "pa_provider_synthetic_01")
        for task_id in self.task_ids:
            task = self.dataset / "prior_auth_provider" / "tasks" / task_id
            task.mkdir(parents=True)
            (task / "instruction.md").write_text(f"Public synthetic instruction for {task_id}\n", encoding="utf-8")
            # This sentinel stands for hidden benchmark material and is intentionally never opened.
            (task / "fixtures").mkdir()
            (task / "fixtures" / "expectations.json").write_text("PRIVATE_SENTINEL", encoding="utf-8")
        self.config = BatchConfig(
            dataset_root=self.dataset, run_dir=self.root / "batch",
            domains=("pa_provider",), task_ids=self.task_ids,
            attempts=1, concurrency=1, instruction_sources=(), expected_instruction_hashes=(),
            defer_grading=True)
        self.world = _World()
        self.actor_calls = []
        run_batch(self.config, world=self.world, case_runner=self._actor,
                  source_identity=self._source_identity)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _source_identity():
        return {"source_commit": "synthetic-source", "source_fingerprint": "a" * 64, "source_files": 1}

    def _actor(self, container, task_dir, run_dir, executable, pins, **kwargs):
        self.actor_calls.append(task_dir.name)
        run_dir.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(run_dir / "state.sqlite")
        try:
            db.execute("CREATE TABLE actions (id TEXT)")
            db.commit()
        finally:
            db.close()
        result = {"local_harness": {"status": "complete", "model_calls": 1, "tool_calls": 1}}
        (run_dir / "run.result.json").write_text(json.dumps(result), encoding="utf-8")
        (run_dir / "evaluation.json").write_text(json.dumps({
            "metadata": {"source_commit": "synthetic-source", "source_fingerprint": "a" * 64},
            "harness_status": "complete",
        }), encoding="utf-8")
        return result

    def test_plan_is_read_only_and_lists_only_hashes_and_public_identity(self):
        plan = plan_deferred_grading(self.config.run_dir, self.dataset)
        self.assertTrue(plan["no_docker_no_inference_no_grading"])
        self.assertEqual(2, plan["selected_tasks"])
        self.assertEqual(2, plan["selected_attempts"])
        rendered = json.dumps(plan)
        self.assertNotIn("PRIVATE_SENTINEL", rendered)
        self.assertNotIn("synthetic-private-payload", rendered)
        self.assertEqual(2, len(self.world.stopped))
        self.assertEqual([], self.world.graded)

    def test_grade_waits_for_all_world_checks_then_keeps_fake_scores_unscored(self):
        actor_manifest = self.config.run_dir / "batch.manifest.json"
        before = hashlib.sha256(actor_manifest.read_bytes()).hexdigest()
        world_checks = []
        grader_calls = []

        def stopped(name):
            world_checks.append(name)
            return True

        def fake_grade(snapshot, task, attempt, output_dir):
            grader_calls.append((task["task_id"], attempt["attempt"]))
            return {"status": "test_unscored", "transport": "synthetic_test_runner"}

        result = run_grade_later(self.config.run_dir, self.dataset, plan_only=False,
                                 offline_grader=fake_grade, container_state_check=stopped)
        self.assertEqual(2, len(world_checks))
        self.assertEqual(2, len(grader_calls))
        self.assertEqual(set(self.world.started), set(world_checks))
        self.assertTrue(all(item["status"] == "test_unscored" and item["official_score"] is None
                            for item in result["results"]))
        self.assertEqual(before, hashlib.sha256(actor_manifest.read_bytes()).hexdigest())
        self.assertTrue(Path(result["grade_manifest"]).is_file())
        self.assertNotIn("PRIVATE_SENTINEL", Path(result["grade_manifest"]).read_text(encoding="utf-8"))

    def test_active_or_unverifiable_world_blocks_every_grade_before_runner(self):
        calls = []
        state = {name: True for name in self.world.started}
        state[self.world.started[-1]] = False

        def stopped(name):
            return state[name]

        def fake_grade(snapshot, task, attempt, output_dir):
            calls.append(task["task_id"])
            return {"status": "test_unscored"}

        with self.assertRaisesRegex(DeferredGradingError, "active or its stopped state"):
            run_grade_later(self.config.run_dir, self.dataset, plan_only=False,
                            offline_grader=fake_grade, container_state_check=stopped)
        self.assertEqual([], calls)

    def test_tampered_snapshot_fails_plan_before_world_check_or_grade(self):
        snapshot = (self.config.run_dir / "pa_provider" / self.task_ids[0] / "attempt-1" /
                    "deferred_snapshot" / "logs" / "artifacts" / "actor.log")
        snapshot.write_text("tampered", encoding="utf-8")
        world_checks = []
        grades = []
        with self.assertRaisesRegex(Exception, "inventory changed"):
            run_grade_later(self.config.run_dir, self.dataset, plan_only=False,
                            offline_grader=lambda *args: grades.append(args),
                            container_state_check=lambda name: world_checks.append(name) or True)
        self.assertEqual([], world_checks)
        self.assertEqual([], grades)

    def test_manifest_cannot_drop_a_frozen_task_or_relabel_attempt_numbers(self):
        path = self.config.run_dir / "batch.manifest.json"
        original = path.read_bytes()
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["tasks"].pop()
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(DeferredGradingError, "task set differs"):
            plan_deferred_grading(self.config.run_dir, self.dataset)
        path.write_bytes(original)
        manifest = json.loads(original)
        manifest["tasks"][0]["attempts"][0]["attempt"] = 2
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(DeferredGradingError, "unique frozen numbers"):
            plan_deferred_grading(self.config.run_dir, self.dataset)

    def test_actor_batch_rejects_grade_mode_change_on_resume(self):
        changed = replace(self.config, defer_grading=False)
        with self.assertRaisesRegex(Exception, "configuration differ"):
            run_batch(changed, world=self.world, case_runner=self._actor,
                      source_identity=self._source_identity)
        self.assertEqual(2, len(self.actor_calls))

    def test_experimental_codex_simulator_batch_is_ineligible_for_official_grading(self):
        path = self.config.run_dir / "batch.manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["frozen_config"]["simulator"] = {
            "backend": "codex", "experimental_official_grade_eligible": False,
        }
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(DeferredGradingError, "not eligible for official grading"):
            plan_deferred_grading(self.config.run_dir, self.dataset)
        # Alternate evaluation validates the same snapshots without claiming
        # that a changed simulator or provider is competition-approved.
        plan = plan_deferred_grading(self.config.run_dir, self.dataset, allow_experimental=True)
        self.assertEqual(2, plan["selected_attempts"])

    def test_direct_grader_command_uses_pinned_image_and_official_single_vote_model(self):
        env_file = self.root / "local.env"
        env_file.write_text("SYNTHETIC_KEY=value\n", encoding="utf-8")
        work_dir = self.root / "late-grade" / "case-1"
        grader = DockerOfflineGrader(docker="docker", env_file=env_file, allow_network=True)
        command = grader.command({"task_id": self.task_ids[0]}, work_dir)
        self.assertEqual(batch_image_digest(), command[command.index("--entrypoint") + 2])
        self.assertEqual("/workspace/.venv/bin/python", command[command.index("--entrypoint") + 1])
        self.assertIn("CHI_BENCH_JUDGE_MODEL=claude-opus-4-7", command)
        self.assertIn("CHI_BENCH_JUDGE_NUM_VOTES=1", command)
        self.assertGreater(command.index("--env-file"), command.index("--mount"))
        self.assertNotIn("SYNTHETIC_KEY=value", json.dumps(command))
        self.assertNotIn("--rm", command)


def batch_image_digest():
    from health_harness_codex.batch import RUNTIME_IMAGE_SHA256
    return RUNTIME_IMAGE_SHA256


if __name__ == "__main__":
    unittest.main()
