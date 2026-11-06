from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO / "HealthHarnessCodex" / "runs"
SCRIPT = REPO / "Submissions" / "tools" / "assemble_native_packet.py"
SPEC = importlib.util.spec_from_file_location("assemble_native_packet", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PACKET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKET)


class NativePacketTests(unittest.TestCase):
    def setUp(self):
        RUNS_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="packet-fixture-", dir=RUNS_ROOT)
        self.pilot = Path(self.temp.name)
        self.output = Path(self.temp.name) / "packet-output"
        self._build_pilot()
        self.packed_payloads = []

    def tearDown(self):
        self.temp.cleanup()

    def _build_pilot(self):
        metadata = {
            "source_commit": "03c845d1aa4abf6794f87088bcc64a9b265ebffc",
            "source_fingerprint": "a" * 64,
            "task_id": PACKET.TASK_ID,
            "task_instruction_sha256": "b" * 64,
            "model": "gpt-6-luna",
            "reasoning_effort": "high",
            "budgets": {"model_calls": 48, "tool_calls": 240, "context_chars": 180000},
            "initial_state_fingerprint": "c" * 64,
            "allowed_instruction_source_sha256": {"/approved/AGENTS.md": "d" * 64},
            "composition": "combined",
        }
        messages = [{"role": "user", "content": "synthetic test task"},
                    {"role": "assistant", "content": "synthetic response"}]
        for index, status in enumerate(("unresolved", "unresolved", "complete"), start=1):
            trial = self.pilot / f"trial-{index}"
            attempt = trial / "attempt-1"
            verifier = trial / "container_logs" / f"verifier_official_attempt_{index}"
            attempt.mkdir(parents=True)
            verifier.mkdir(parents=True)
            metrics = {"model_calls": index + 2, "model_calls_observed_this_segment": index + 2,
                       "tool_calls": index + 4, "elapsed_seconds": 30.0 + index,
                       "reported_usage_this_segment": {"input_tokens": 100 * index},
                       "tool_dispatch_attempts": {}}
            evaluation = {"metadata": metadata, "harness_status": status, "metrics": metrics}
            result = {"task": PACKET.TASK_ID, "container_identity": f"test-container-{index}",
                      "elapsed_seconds": 30.0 + index,
                      "local_harness": {"status": status, "model_calls": index + 2, "tool_calls": index + 4}}
            (attempt / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
            (attempt / "run.result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            events = [{"kind": "run_started", "time": 1792470000.0 + index},
                      {"kind": "run_finished", "time": 1792470030.0 + index}]
            (attempt / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            db_path = attempt / "state.snapshot.sqlite"
            connection = sqlite3.connect(db_path)
            connection.execute("CREATE TABLE cases (state_json TEXT NOT NULL)")
            connection.execute("INSERT INTO cases VALUES (?)", (json.dumps({"messages": messages}),))
            connection.commit()
            connection.close()

            reward = {"reward": 1}
            scorecard = {"checks": {f"check-{n}": "passed" for n in range(21)},
                         "total_checks": 21, "binary_reward": 1}
            context = {"judge_unavailable_reason": None, "degraded_rubric_ids": []}
            files = {"reward.json": reward, "scorecard.json": scorecard,
                     "verifier_context.json": context}
            hashes = {}
            for name, value in files.items():
                path = verifier / name
                path.write_text(json.dumps(value), encoding="utf-8")
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = {"verifier_dir": str(verifier.relative_to(trial)).replace("\\", "/"),
                       "artifact_sha256": hashes}
            (trial / "official-evaluation-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")

    def _fake_packer(self, source, destination):
        self.packed_payloads.append(json.loads(source.read_text(encoding="utf-8")))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"synthetic packed trajectory")

    def test_builds_exact_allowlisted_packet_from_validated_trials(self):
        output = PACKET.assemble_packet(self.pilot, self.output, team="Example Team",
                                        contact="team@example.test", packer=self._fake_packer)
        self.assertEqual("2026-10-20-submission_1", output.name)
        files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
        self.assertEqual(PACKET.ALLOWED_FILES, files)
        manifest = json.loads((output / "submission.json").read_text(encoding="utf-8"))
        self.assertEqual("chi-bench/submission/v1", manifest["schema"])
        self.assertEqual({"pass_at_1": 1.0, "n_trials": 3, "n_tasks": 1},
                         {key: manifest["results"]["overall"][key]
                          for key in ("pass_at_1", "n_trials", "n_tasks")})
        self.assertEqual(1, manifest["results"]["overall"]["pass_at_3"])
        self.assertEqual(1, manifest["results"]["overall"]["pass_power_3"])
        self.assertNotIn("mean_cost_usd", manifest["results"])
        self.assertFalse(manifest["submission"]["publication_ready"])
        for index, original_status in enumerate(("unresolved", "unresolved", "complete"), start=1):
            source_trial = self.pilot / f"trial-{index}"
            packet_trial = output / "trials" / "pa_um" / f"trial-{index}"
            source_result = source_trial / "attempt-1" / "run.result.json"
            self.assertEqual(source_result.read_bytes(), (packet_trial / "result.json").read_bytes())
            receipt = json.loads((source_trial / "official-evaluation-receipt.json").read_text(encoding="utf-8"))
            verifier = source_trial / receipt["verifier_dir"]
            for name in ("reward.json", "scorecard.json"):
                self.assertEqual((verifier / name).read_bytes(), (packet_trial / "verifier" / name).read_bytes())
            payload = self.packed_payloads[index - 1]
            self.assertEqual("health-harness/native-transcript/v1", payload["schema_version"])
            snapshot = source_trial / "attempt-1" / "state.snapshot.sqlite"
            snapshot_sha = hashlib.sha256(snapshot.read_bytes()).hexdigest()
            self.assertEqual(f"sqlite-sha256:{snapshot_sha}", payload["session_id"])
            self.assertEqual([{"role": "user", "content": "synthetic test task"},
                              {"role": "assistant", "content": "synthetic response"}], payload["steps"])
            self.assertEqual(original_status, json.loads((source_trial / "attempt-1" / "evaluation.json").read_text())["harness_status"])
        provenance = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(3, len(provenance["trials"]))
        self.assertEqual(2, provenance["trials"][0]["native_message_count"])
        self.assertEqual("sha256:" + "420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66",
                         provenance["runtime_image_digest"])
        self.assertEqual("not_applicable:deterministic-verifier", provenance["judge_model"])
        self.assertIn("not_atif_or_harbor", provenance["trajectory"])
        self.assertTrue(provenance["trajectory"]["not_provider_session_id"])

    def test_requires_explicit_unconfirmed_identity_for_placeholders_and_refuses_overwrite(self):
        with self.assertRaisesRegex(PACKET.PacketError, "team and contact are required"):
            PACKET.assemble_packet(self.pilot, self.output, packer=self._fake_packer)
        output = PACKET.assemble_packet(self.pilot, self.output, allow_unconfirmed_identity=True,
                                        packer=self._fake_packer)
        manifest = json.loads((output / "submission.json").read_text(encoding="utf-8"))
        provenance = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual("not provided", manifest["submission"]["team"])
        self.assertEqual("not provided", manifest["submission"]["contact"])
        self.assertFalse(provenance["identity_confirmed"])
        with self.assertRaisesRegex(PACKET.PacketError, "already exists"):
            PACKET.assemble_packet(self.pilot, self.output, allow_unconfirmed_identity=True,
                                   packer=self._fake_packer)

    def test_rejects_unexpected_source_commit_before_creating_output(self):
        eval_path = self.pilot / "trial-3" / "attempt-1" / "evaluation.json"
        evaluation = json.loads(eval_path.read_text(encoding="utf-8"))
        evaluation["metadata"]["source_commit"] = "ffffffffffffffffffffffffffffffffffffffff"
        eval_path.write_text(json.dumps(evaluation), encoding="utf-8")
        with self.assertRaisesRegex(PACKET.PacketError, "pilot validation failed"):
            PACKET.assemble_packet(self.pilot, self.output, team="Example", contact="e@example.test",
                                   packer=self._fake_packer)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
