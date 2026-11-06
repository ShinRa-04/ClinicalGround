from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_AGGREGATOR_PATH = Path(__file__).resolve().parents[1] / "evaluations" / "aggregate_official_pilot.py"
_SPEC = importlib.util.spec_from_file_location("aggregate_official_pilot", _AGGREGATOR_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_AGGREGATOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_AGGREGATOR)
PilotAggregationError = _AGGREGATOR.PilotAggregationError
aggregate_pilot = _AGGREGATOR.aggregate_pilot
write_reports = _AGGREGATOR.write_reports


RUNS_ROOT = Path(__file__).resolve().parents[1] / "runs"
TASK_ID = "pa_synthetic_pilot"
_BASE_METADATA = {
    "source_commit": "a" * 40,
    "source_fingerprint": "b" * 64,
    "task_id": TASK_ID,
    "task_instruction_sha256": "c" * 64,
    "model": "gpt-6-luna",
    "reasoning_effort": "high",
    "budgets": {"model_calls": 48, "tool_calls": 240, "context_chars": 180000},
    "initial_state_fingerprint": "d" * 64,
    "allowed_instruction_source_sha256": {"C:/approved/AGENTS.md": "e" * 64},
    "composition": "combined",
}


class OfficialPilotAggregationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="official-pilot-test-", dir=str(RUNS_ROOT))
        self.root = Path(self.temp.name)
        self._make_pilot([1, 0, 0], ["complete", "complete", "unresolved"])

    def tearDown(self):
        self.temp.cleanup()

    def _make_pilot(self, rewards, local_statuses):
        for index, (reward, local_status) in enumerate(zip(rewards, local_statuses), start=1):
            trial_root = self.root / f"trial-{index}"
            attempt = trial_root / "attempt-1"
            verifier_dir = trial_root / "container_logs" / f"verifier_official_attempt_{index}"
            attempt.mkdir(parents=True)
            verifier_dir.mkdir(parents=True)
            metadata = copy.deepcopy(_BASE_METADATA)
            metrics = {
                "model_calls_observed_this_segment": 7 + index,
                "model_calls": 7 + index,
                "tool_calls": 40 + index,
                "elapsed_seconds": 100.5 + index,
                "reported_usage_this_segment": {"input_tokens": 1000 + index, "total_tokens": 1200 + index},
                "reported_usage": {"input_tokens": 1000 + index, "total_tokens": 1200 + index},
                "tool_dispatch_attempts": {"mcp_actor_lookup": 20, "mcp_triage.route_case": 2,
                                           "workspace.read_pdf": 4, "case.search_evidence": 3},
                "tool_dispatch_not_dispatched": {"mcp_triage.route_case": 1},
            }
            evaluation = {"metadata": metadata, "harness_status": local_status,
                          "classification": "locally_complete_ungraded" if local_status == "complete" else "incomplete_workflow",
                          "metrics": metrics}
            run_result = {"task": TASK_ID, "container_identity": f"trial-container-{index}",
                          "local_harness": {"status": local_status, "model_calls": 7 + index,
                                             "tool_calls": 40 + index}}
            (attempt / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
            (attempt / "run.result.json").write_text(json.dumps(run_result), encoding="utf-8")
            scorecard = {
                "checks": [
                    {"name": "synthetic.check.positive", "status": "passed"},
                    {"name": "synthetic.check.negative", "status": "passed" if reward else "failed"},
                    {"name": "synthetic.check.na", "status": "N/A"},
                ],
                "counts": {"passed": 2 if reward else 1, "failed": 0 if reward else 1,
                           "not_applicable": 1, "total": 3, "applicable": 2},
                "failed_checks": [] if reward else ["synthetic.check.negative"],
            }
            reward_data = {"reward": float(reward)}
            context = {"semantic_degraded_reason": None, "semantic_unavailable_reason": None,
                       "judge_invoked": False}
            files = {"reward.json": reward_data, "scorecard.json": scorecard,
                     "verifier_context.json": context}
            hashes = {}
            for name, data in files.items():
                path = verifier_dir / name
                path.write_text(json.dumps(data), encoding="utf-8")
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = {"verifier_dir": str(verifier_dir.relative_to(trial_root)).replace("\\", "/"),
                       "artifact_sha256": hashes}
            (trial_root / "official-evaluation-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")

    def _rehash_receipt(self, trial_number, filename):
        trial = self.root / f"trial-{trial_number}"
        receipt_path = trial / "official-evaluation-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        target = trial / receipt["verifier_dir"] / filename
        receipt["artifact_sha256"][filename] = hashlib.sha256(target.read_bytes()).hexdigest()
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    def test_accepts_complete_and_partial_binary_scores_without_conflating_local_status(self):
        report = aggregate_pilot(self.root)
        self.assertEqual([1, 0, 0], [trial["official_reward"] for trial in report["trials"]])
        self.assertEqual(["complete", "complete", "unresolved"],
                         [trial["local_harness_status"] for trial in report["trials"]])
        self.assertEqual({"passed": 2, "failed": 0, "not_applicable": 1, "non_na": 2, "total": 3},
                         {key: report["trials"][0]["scorecard"][key]
                          for key in ("passed", "failed", "not_applicable", "non_na", "total")})
        self.assertEqual(1 / 3, report["one_task_pilot_metrics"]["pass_at_1"])
        self.assertEqual(1, report["one_task_pilot_metrics"]["pass_at_3"])
        self.assertEqual(0, report["one_task_pilot_metrics"]["pass_power_3"])
        self.assertEqual(8, report["trials"][0]["model_calls"])
        self.assertEqual(41, report["trials"][0]["engine_tool_calls"])
        self.assertEqual(22, report["trials"][0]["actor_tool_attempts"])
        self.assertEqual(21, report["trials"][0]["actor_mcp_dispatches"])
        self.assertEqual(4, report["trials"][0]["workspace_dispatches"])
        self.assertEqual({"input_tokens": 1001, "total_tokens": 1201}, report["trials"][0]["reported_usage"])
        self.assertIsNone(report["trials"][0]["cost_estimate"])
        self.assertEqual("reason_none", report["trials"][0]["semantic_evaluation"]["status"])

        original_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in self.root.rglob("*") if path.is_file()}
        json_path, md_path = write_reports(self.root, report)
        self.assertTrue(json_path.is_file())
        self.assertTrue(md_path.is_file())
        self.assertIn("single-task three-trial pilot", md_path.read_text(encoding="utf-8"))
        for path, digest in original_hashes.items():
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_rejects_noncomparable_trial_metadata(self):
        evaluation_path = self.root / "trial-3" / "attempt-1" / "evaluation.json"
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        evaluation["metadata"]["source_fingerprint"] = "f" * 64
        evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")
        with self.assertRaisesRegex(PilotAggregationError, "incomparable: source_fingerprint"):
            aggregate_pilot(self.root)

    def test_rejects_reward_hash_mismatch_or_binary_reward_disagreement(self):
        reward_path = self.root / "trial-2" / "container_logs" / "verifier_official_attempt_2" / "reward.json"
        reward_path.write_text(json.dumps({"reward": 1}), encoding="utf-8")
        with self.assertRaisesRegex(PilotAggregationError, "hash mismatch for reward.json"):
            aggregate_pilot(self.root)
        self._rehash_receipt(2, "reward.json")
        with self.assertRaisesRegex(PilotAggregationError, "reward.json disagrees with scorecard"):
            aggregate_pilot(self.root)

    def test_rejects_incoherent_declared_scorecard_counts(self):
        scorecard_path = self.root / "trial-1" / "container_logs" / "verifier_official_attempt_1" / "scorecard.json"
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        scorecard["counts"]["failed"] = 1
        scorecard_path.write_text(json.dumps(scorecard), encoding="utf-8")
        self._rehash_receipt(1, "scorecard.json")
        with self.assertRaisesRegex(PilotAggregationError, "declared failed count is inconsistent"):
            aggregate_pilot(self.root)

    def test_accepts_native_primitive_na_scorecard_shape(self):
        verifier = self.root / "trial-1" / "container_logs" / "verifier_official_attempt_1"
        checks = {f"passed-{index}": "passed" for index in range(2)}
        checks.update({f"failed-{index}": "failed" for index in range(13)})
        checks.update({f"na-{index}": "not_applicable" for index in range(4)})
        scorecard = {"checks": checks, "total_checks": 15, "binary_reward": 0,
                     "failed_checks": [f"failed-{index}" for index in range(13)]}
        (verifier / "scorecard.json").write_text(json.dumps(scorecard), encoding="utf-8")
        (verifier / "reward.json").write_text(json.dumps({"reward": 0}), encoding="utf-8")
        self._rehash_receipt(1, "scorecard.json")
        self._rehash_receipt(1, "reward.json")

        trial = aggregate_pilot(self.root)["trials"][0]
        self.assertEqual(0, trial["official_reward"])
        self.assertEqual({"passed": 2, "failed": 13, "not_applicable": 4, "non_na": 15, "total": 19},
                         {key: trial["scorecard"][key]
                          for key in ("passed", "failed", "not_applicable", "non_na", "total")})

    def test_rejects_semantic_degraded_or_unavailable_reason(self):
        context_path = self.root / "trial-1" / "container_logs" / "verifier_official_attempt_1" / "verifier_context.json"
        context_path.write_text(json.dumps({"semantic_unavailable_reason": "native judge not available"}), encoding="utf-8")
        self._rehash_receipt(1, "verifier_context.json")
        with self.assertRaisesRegex(PilotAggregationError, "semantic evaluation is degraded or unavailable"):
            aggregate_pilot(self.root)

    def test_rejects_native_top_level_judge_unavailable_reason(self):
        context_path = self.root / "trial-1" / "container_logs" / "verifier_official_attempt_1" / "verifier_context.json"
        context_path.write_text(json.dumps({"judge_unavailable_reason": "native semantic judge unavailable"}), encoding="utf-8")
        self._rehash_receipt(1, "verifier_context.json")
        with self.assertRaisesRegex(PilotAggregationError, "semantic evaluation is degraded or unavailable"):
            aggregate_pilot(self.root)

    def test_rejects_degraded_rubric_ids_and_unavailable_judge_session(self):
        context_path = self.root / "trial-1" / "container_logs" / "verifier_official_attempt_1" / "verifier_context.json"
        for context in ({"degraded_rubric_ids": ["criterion-1"]},
                        {"judge_session_metadata": {"status": "unavailable"}}):
            with self.subTest(context=context):
                context_path.write_text(json.dumps(context), encoding="utf-8")
                self._rehash_receipt(1, "verifier_context.json")
                with self.assertRaisesRegex(PilotAggregationError, "semantic evaluation is degraded or unavailable"):
                    aggregate_pilot(self.root)

    def test_rejects_scorecard_binary_reward_mismatch(self):
        scorecard_path = self.root / "trial-1" / "container_logs" / "verifier_official_attempt_1" / "scorecard.json"
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        scorecard["binary_reward"] = 0
        scorecard_path.write_text(json.dumps(scorecard), encoding="utf-8")
        self._rehash_receipt(1, "scorecard.json")
        with self.assertRaisesRegex(PilotAggregationError, "reward.json disagrees with scorecard reward"):
            aggregate_pilot(self.root)

    def test_rejects_missing_trial_input(self):
        (self.root / "trial-3" / "attempt-1" / "evaluation.json").unlink()
        with self.assertRaisesRegex(PilotAggregationError, "evaluation.json"):
            aggregate_pilot(self.root)

    def test_rejects_active_trial(self):
        evaluation_path = self.root / "trial-2" / "attempt-1" / "evaluation.json"
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        evaluation["harness_status"] = "running"
        evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")
        run_path = self.root / "trial-2" / "attempt-1" / "run.result.json"
        run_result = json.loads(run_path.read_text(encoding="utf-8"))
        run_result["local_harness"]["status"] = "running"
        run_path.write_text(json.dumps(run_result), encoding="utf-8")
        with self.assertRaisesRegex(PilotAggregationError, "settled local run result"):
            aggregate_pilot(self.root)

    def test_rejects_more_than_three_numbered_trials(self):
        extra = self.root / "trial-4"
        extra.mkdir()
        with self.assertRaisesRegex(PilotAggregationError, "exactly trial-1"):
            aggregate_pilot(self.root)

    def test_rejects_verifier_directory_traversal(self):
        receipt_path = self.root / "trial-1" / "official-evaluation-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["verifier_dir"] = "../outside"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaisesRegex(PilotAggregationError, "must remain inside"):
            aggregate_pilot(self.root)

    def test_rejects_impossible_or_unknown_not_dispatched_counts(self):
        evaluation_path = self.root / "trial-1" / "attempt-1" / "evaluation.json"
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        evaluation["metrics"]["tool_dispatch_not_dispatched"]["mcp_triage.route_case"] = 3
        evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")
        with self.assertRaisesRegex(PilotAggregationError, "exceeds tool attempts"):
            aggregate_pilot(self.root)

        evaluation["metrics"]["tool_dispatch_not_dispatched"] = {"mcp_unknown.tool": 1}
        evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")
        with self.assertRaisesRegex(PilotAggregationError, "names an unknown tool"):
            aggregate_pilot(self.root)


if __name__ == "__main__":
    unittest.main()
