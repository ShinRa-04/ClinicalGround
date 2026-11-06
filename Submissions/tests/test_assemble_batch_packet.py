from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO / "HealthHarnessCodex" / "runs"
SCRIPT = REPO / "Submissions" / "tools" / "assemble_batch_packet.py"
SPEC = importlib.util.spec_from_file_location("assemble_batch_packet", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PACKET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKET)


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


class FullBatchPacketTests(unittest.TestCase):
    def setUp(self):
        RUNS_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="full-batch-packet-test-", dir=RUNS_ROOT)
        self.root = Path(self.temp.name)
        self.batch_root = self.root / "batch"
        self.output_root = self.root / "packet-output"
        self.payloads = []
        self._build_batch()

    def tearDown(self):
        self.temp.cleanup()

    def _build_batch(self):
        source_commit = "0123456789abcdef0123456789abcdef01234567"
        source_fingerprint = "a" * 64
        tasks = []
        task_hashes = {}
        pass_count = 0
        for domain in PACKET.DOMAINS:
            for index in range(25):
                task_id = f"{domain}_synthetic_{index:02d}"
                task_key = f"{domain}/{task_id}"
                task_hash = hashlib.sha256(task_key.encode()).hexdigest()
                task_hashes[task_key] = task_hash
                relative_attempt = Path(domain) / task_id / "attempt-1"
                attempt_dir = self.batch_root / relative_attempt
                verifier = attempt_dir / "container_logs" / "official_1"
                verifier.mkdir(parents=True)
                reward = 0 if index % 4 == 0 else 1
                pass_count += reward
                checks = ({"criterion-1": "passed"} if reward else
                          {"criterion-1": "passed", "criterion-2": "failed"})
                scorecard = {"checks": checks, "total_checks": len(checks), "binary_reward": reward}
                reward_doc = {"reward": reward}
                context = {"judge_unavailable_reason": None, "degraded_rubric_ids": []}
                exported = {"export_schema": "synthetic-public-summary"}
                official = {"reward.json": reward_doc, "scorecard.json": scorecard,
                            "exported_state.json": exported, "verifier_context.json": context}
                official_hashes = {}
                for filename, content in official.items():
                    path = verifier / filename
                    _write_json(path, content)
                    official_hashes[filename.removesuffix(".json")] = {
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}

                local_status = "complete" if index % 2 else "unresolved"
                metadata = {"task_id": task_id, "task": task_id,
                            "source_commit": source_commit, "source_fingerprint": source_fingerprint,
                            "task_instruction_sha256": task_hash, "model": "gpt-6-luna",
                            "reasoning_effort": "high", "budgets": {"max_model_calls": 48},
                            "composition": "combined"}
                evaluation = {"metadata": metadata, "harness_status": local_status,
                              "metrics": {"elapsed_seconds": 12.5 + index}}
                run_result = {"task": task_id, "task_instruction_sha256": task_hash,
                              "container_identity": f"synthetic-{task_id}", "elapsed_seconds": 12.5 + index,
                              "local_harness": {"status": local_status, "model_calls": 3, "tool_calls": 7}}
                _write_json(attempt_dir / "evaluation.json", evaluation)
                result_bytes = (json.dumps(run_result, ensure_ascii=False, indent=2) + "\n").encode()
                (attempt_dir / "run.result.json").write_bytes(result_bytes)
                events = [{"kind": "run_started", "time": 1792470000 + index},
                          {"kind": "run_finished", "time": 1792470030 + index}]
                (attempt_dir / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
                snapshot_path = attempt_dir / "state.snapshot.sqlite"
                database = sqlite3.connect(snapshot_path)
                database.execute("CREATE TABLE cases (state_json TEXT NOT NULL)")
                messages = [{"role": "user", "content": f"synthetic public text {domain} {index}"},
                            {"role": "assistant", "content": f"synthetic response {index}"}]
                database.execute("INSERT INTO cases VALUES (?)", (json.dumps({"messages": messages}),))
                database.commit()
                database.close()
                actor_hashes = {filename: {"sha256": hashlib.sha256((attempt_dir / filename).read_bytes()).hexdigest(),
                                           "bytes": (attempt_dir / filename).stat().st_size}
                                for filename in ("run.result.json", "evaluation.json", "state.snapshot.sqlite")}
                receipt = {"schema_version": 1, "task_id": task_id, "domain": domain, "attempt": 1,
                           "container_identity": f"synthetic-{task_id}", "source_commit": source_commit,
                           "source_fingerprint": source_fingerprint, "selected_output": "official_1",
                           "grader_runs": [{"output": "official_1", "returncode": 0 if reward else 1}],
                           "status": "graded", "actor_artifacts": actor_hashes, "artifacts": official_hashes}
                receipt_path = attempt_dir / "official-evaluation-receipt.json"
                _write_json(receipt_path, receipt)
                attempts = [{"attempt": 1, "status": "graded", "official_score": reward,
                             "local_status": local_status,
                             "attempt_dir": relative_attempt.as_posix(),
                             "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest()}]
                tasks.append({"domain": domain, "task_id": task_id,
                              "instruction_sha256": task_hash, "attempts": attempts})
        domain_coverage = {domain: True for domain in PACKET.DOMAINS}
        manifest = {"schema_version": 1, "created_at": "2026-10-20T00:00:00Z",
                    "updated_at": "2026-10-20T00:10:00Z",
                    "frozen_config": {"domains": list(PACKET.DOMAINS), "attempts": 1,
                                      "task_instruction_sha256": task_hashes,
                                      "source_commit": source_commit, "source_fingerprint": source_fingerprint,
                                      "model": "gpt-6-luna", "reasoning_effort": "high",
                                      "budgets": {"max_model_calls": 48, "max_tool_calls": 240,
                                                  "max_context_chars": 180000},
                                      "composition": "combined", "runtime_image": "bigdata-chi-bench:runtime-4444a07",
                                      "runtime_image_sha256": "sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66"},
                    "summary": {"full_dataset_coverage_complete": True,
                                "full_domain_coverage_complete": domain_coverage},
                    "tasks": tasks}
        _write_json(self.batch_root / "batch.manifest.json", manifest)
        self.expected_passes = pass_count

    def _fake_packer(self, source, destination):
        self.payloads.append(json.loads(source.read_text(encoding="utf-8")))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"synthetic-zstd19-packet-trajectory")

    def test_builds_full_packet_preserving_zero_rewards_and_native_artifacts(self):
        output = PACKET.assemble_full_batch_packet(self.batch_root, self.output_root, "all_domains_2026",
                                                   "2026-10-20", "Example Team", "contact@example.test",
                                                   packer=self._fake_packer)
        manifest = json.loads((output / "submission.json").read_text(encoding="utf-8"))
        self.assertEqual(75, manifest["results"]["overall"]["n_tasks"])
        self.assertEqual(75, manifest["results"]["overall"]["n_trials"])
        self.assertEqual(self.expected_passes / 75, manifest["results"]["overall"]["pass_at_1"])
        self.assertNotIn("mean_cost_usd", manifest["results"])
        for domain in PACKET.DOMAINS:
            self.assertEqual(25, manifest["results"]["per_domain"][domain]["n_trials"])
            self.assertEqual(25, manifest["results"]["per_domain"][domain]["n_tasks"])
        self.assertFalse(manifest["submission"]["publication_ready"])
        self.assertEqual("official-runtime-verifier", manifest["provenance"]["judge_model"])
        self.assertEqual(PACKET.CHI_BENCH_COMMIT, manifest["provenance"]["chi_bench_git_sha"])

        files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
        self.assertEqual(5 + 75 * 4, len(files))
        self.assertIn("README.md", files)
        self.assertEqual(75, len(self.payloads))
        for domain in PACKET.DOMAINS:
            matches = [path for path in files if path.startswith(f"trials/{domain}/") and path.endswith("/result.json")]
            self.assertEqual(25, len(matches))

        source_task = self.batch_root / "pa_provider" / "pa_provider_synthetic_00" / "attempt-1"
        output_task = output / "trials" / "pa_provider" / "pa_provider_synthetic_00__attempt_1"
        self.assertEqual((source_task / "run.result.json").read_bytes(), (output_task / "result.json").read_bytes())
        self.assertEqual((source_task / "container_logs" / "official_1" / "reward.json").read_bytes(),
                         (output_task / "verifier" / "reward.json").read_bytes())
        self.assertEqual((source_task / "container_logs" / "official_1" / "scorecard.json").read_bytes(),
                         (output_task / "verifier" / "scorecard.json").read_bytes())
        trajectory = self.payloads[0]
        self.assertEqual("health-harness/native-transcript/v1", trajectory["schema_version"])
        self.assertTrue(trajectory["session_id"].startswith("sqlite-sha256:"))
        self.assertEqual("synthetic public text pa_provider 0", trajectory["steps"][0]["content"])
        with (output / "results.csv").open(encoding="utf-8", newline="") as stream:
            self.assertEqual(4, len(list(csv.DictReader(stream))))

    def test_refuses_ungraded_task_or_incomplete_domain_counts(self):
        manifest_path = self.batch_root / "batch.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tasks"][0]["attempts"][0]["status"] = "ungraded"
        manifest["tasks"][0]["attempts"][0]["official_score"] = None
        _write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PACKET.BatchPacketError, "actual strict official reward"):
            PACKET.assemble_full_batch_packet(self.batch_root, self.output_root, "all_domains_2026",
                                              "2026-10-20", "Example Team", "contact@example.test",
                                              packer=self._fake_packer)
        self.assertFalse(self.output_root.exists())

    def test_rejects_corrupted_official_receipt_artifact_hash(self):
        scorecard = (self.batch_root / "pa_um" / "pa_um_synthetic_00" / "attempt-1" /
                     "container_logs" / "official_1" / "scorecard.json")
        scorecard.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(PACKET.BatchPacketError, "integrity check failed"):
            PACKET.assemble_full_batch_packet(self.batch_root, self.output_root, "all_domains_2026",
                                              "2026-10-20", "Example Team", "contact@example.test",
                                              packer=self._fake_packer)
        self.assertFalse(self.output_root.exists())

    def test_refuses_count_inconsistency_and_existing_packet(self):
        manifest_path = self.batch_root / "batch.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tasks"].pop()
        _write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PACKET.BatchPacketError, "75 graded first attempts"):
            PACKET.assemble_full_batch_packet(self.batch_root, self.output_root, "all_domains_2026",
                                              "2026-10-20", "Example Team", "contact@example.test",
                                              packer=self._fake_packer)
        self.assertFalse(self.output_root.exists())


if __name__ == "__main__":
    unittest.main()
