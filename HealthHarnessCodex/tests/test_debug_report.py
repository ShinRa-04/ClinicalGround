from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest

from health_harness_codex.debug_report import (
    DebugReportError,
    build_case_debug_report,
    write_case_debug_report,
)


REPO = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO / "runs"


class DebugReportTests(unittest.TestCase):
    def setUp(self):
        RUNS_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="debug-report-tests-", dir=RUNS_ROOT)
        self.root = Path(self.temp.name)
        (self.root / "batch.manifest.json").write_text(json.dumps({
            "frozen_config": {"source_commit": "synthetic-source", "source_fingerprint": "a" * 64},
            "tasks": [{
                "task_id": "public_task_01", "domain": "pa_um", "attempts": [{
                    "attempt": 1, "attempt_dir": "pa_um/public_task_01/attempt-1",
                    "status": "deferred_ready",
                }],
            }],
        }), encoding="utf-8")
        self.attempt = self.root / "pa_um/public_task_01/attempt-1"
        self.attempt.mkdir(parents=True)
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "error", "classification": "inference_failure",
            "metrics": {"model_calls": 1, "tool_calls": 0, "patient_text": "DO_NOT_EXPORT"},
            "patient_text": "DO_NOT_EXPORT",
        }), encoding="utf-8")
        (self.attempt / "events.jsonl").write_text("\n".join([
            json.dumps({"kind": "run_started", "patient_text": "DO_NOT_EXPORT"}),
            json.dumps({"kind": "model_call_failed", "error_type": "ProviderError",
                        "error_message": "DO_NOT_EXPORT", "tool_arguments": {"x": "DO_NOT_EXPORT"}}),
            json.dumps({"kind": "run_finished", "harness_status": "error", "official_score": 1}),
        ]) + "\n", encoding="utf-8")
        (self.attempt / ".setup-exception.private.json").write_text(json.dumps({
            "exception_type": "StandaloneError", "stage": "actor_discovery",
            "message": "DO_NOT_EXPORT",
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_all_case_row_uses_safe_whitelist_and_event_line_numbers(self):
        report = build_case_debug_report(self.root)
        self.assertEqual(1, report["task_count"])
        row = report["cases"][0]
        self.assertEqual("RUN03-INFERENCE-FAILURE", row["issue_ids"][0])
        self.assertEqual("not_run_snapshot_available", row["official_grade_availability"])
        self.assertEqual([2], row["evidence_event_numbers"]["model_call_failed"])
        self.assertEqual([3], row["evidence_event_numbers"]["run_finished"])
        safe = json.dumps(report, sort_keys=True)
        self.assertNotIn("DO_NOT_EXPORT", safe)
        self.assertNotIn("official_score", safe)
        self.assertEqual({"model_calls": 1, "model_calls_bootstrap": 0,
                          "model_calls_workflow": 1, "tool_calls": 0}, row["metrics"])

    def test_json_and_csv_are_written_only_under_runs_and_cover_each_case(self):
        json_path, csv_path = write_case_debug_report(self.root)
        self.assertTrue(json_path.is_relative_to(RUNS_ROOT.resolve()))
        self.assertTrue(csv_path.is_relative_to(RUNS_ROOT.resolve()))
        self.assertEqual(1, len(json.loads(json_path.read_text(encoding="utf-8"))["cases"]))
        with csv_path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(1, len(rows))
        self.assertEqual("public_task_01", rows[0]["task_id"])
        self.assertNotIn("DO_NOT_EXPORT", csv_path.read_text(encoding="utf-8"))

    def test_reconciliation_case_stays_unavailable_for_official_grading(self):
        manifest_path = self.root / "batch.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tasks"].append({
            "task_id": "public_task_setup", "domain": "pa_provider", "attempts": [{
                "attempt": 1, "attempt_dir": "pa_provider/public_task_setup/attempt-1",
                "status": "needs_reconciliation",
            }],
        })
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        setup = self.root / "pa_provider/public_task_setup/attempt-1"
        setup.mkdir(parents=True)
        (setup / "evaluation.json").write_text(json.dumps({
            "harness_status": "setup_failure", "classification": "setup_failure",
            "metrics": {"model_calls": 0, "tool_calls": 0},
        }), encoding="utf-8")
        (setup / "events.jsonl").write_text("\n".join([
            json.dumps({"kind": "setup_failed", "stage": "actor_discovery",
                        "error_code": "patient_identity_conflict"}),
            json.dumps({"kind": "run_finished", "harness_status": "setup_failure"}),
            json.dumps({"kind": "reconciliation_observation", "observed_tool_events": 0}),
        ]) + "\n", encoding="utf-8")
        (setup / ".setup-exception.private.json").write_text(json.dumps({
            "exception_type": "ValueError", "stage": "actor_discovery", "message": "DO_NOT_EXPORT",
        }), encoding="utf-8")
        report = build_case_debug_report(self.root)
        row = next(item for item in report["cases"] if item["task_id"] == "public_task_setup")
        self.assertEqual("unavailable_attempt_needs_reconciliation", row["official_grade_availability"])
        self.assertEqual("RUN03-SETUP-DISCOVERY-FAILURE", row["issue_ids"][0])
        self.assertEqual([1], row["evidence_event_numbers"]["setup_failed"])
        self.assertEqual([3], row["evidence_event_numbers"]["reconciliation_observation"])
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(report, sort_keys=True))

    def test_issue_resolution_fields_fill_case_rows_without_raw_event_text(self):
        report = build_case_debug_report(self.root, issue_resolutions={
            "RUN03-INFERENCE-FAILURE": {
                "root_cause": "Transport cause remains unknown.",
                "fix_source": "health_harness_codex/provider.py",
                "tests": "tests/test_provider.py::test_safe_error_classification",
                "rerun_status": "Fresh diagnostic passed; official grade unavailable.",
                "outstanding": "Expand to the remaining affected task IDs.",
            },
        })
        row = report["cases"][0]
        self.assertEqual("Transport cause remains unknown.", row["root_cause"])
        self.assertEqual("health_harness_codex/provider.py", row["fix_source"])
        self.assertEqual("Fresh diagnostic passed; official grade unavailable.", row["rerun_status"])

    def test_closure_reason_uses_fixed_harness_category_without_open_obligation_ids(self):
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "unresolved", "classification": "incomplete_workflow",
            "metrics": {"model_calls": 2, "tool_calls": 1, "open_obligations": 1},
        }), encoding="utf-8")
        (self.attempt / "run.result.json").write_text(json.dumps({
            "local_harness": {
                "status": "unresolved",
                "message": "Completion is blocked by open obligations: PRIVATE_OBLIGATION_ID",
                "final": {"status": "complete"},
            },
        }), encoding="utf-8")
        (self.attempt / "events.jsonl").write_text("\n".join([
            json.dumps({"kind": "model_call_finished", "call_number": 2, "response": "PRIVATE_TEXT"}),
            json.dumps({"kind": "run_finished", "harness_status": "unresolved"}),
        ]) + "\n", encoding="utf-8")
        report = build_case_debug_report(self.root)
        row = report["cases"][0]
        self.assertEqual("open_obligations_remain", row["closure_subcategory"])
        self.assertIn("RUN03-OPEN-OBLIGATIONS", row["issue_ids"])
        self.assertEqual([1], row["closure_event_numbers"]["last_model_call_finished"])
        self.assertNotIn("PRIVATE_OBLIGATION_ID", json.dumps(report, sort_keys=True))
        self.assertNotIn("PRIVATE_TEXT", json.dumps(report, sort_keys=True))

    def test_case_annotation_can_assign_lane_issue_id_and_safe_root_cause(self):
        report = build_case_debug_report(self.root, case_annotations={
            "public_task_01": {
                "issue_ids": ["RUN03-DOMAIN-CASE-BINDING"],
                "root_cause": "The domain lane confirmed a case-local binding mismatch.",
                "fix_source": "health_harness_codex/domain_profiles.py",
                "tests": "tests/test_domain_profiles.py::test_case_local_binding",
                "rerun_status": "Pending fresh isolated run.",
                "outstanding": "Verify the exact public task in a fresh world.",
            },
        })
        row = report["cases"][0]
        self.assertEqual(["RUN03-DOMAIN-CASE-BINDING"], row["issue_ids"])
        self.assertIn("case-local binding mismatch", row["root_cause"])

    def test_call_counts_include_identity_bootstrap_calls(self):
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "error", "classification": "schema_or_scope_rejection",
            "metrics": {"model_calls": 2, "tool_calls": 2},
        }), encoding="utf-8")
        (self.attempt / "run.result.json").write_text(json.dumps({
            "model_calls_total_observed": 3, "bootstrap_model_calls": 1,
            "local_harness": {"model_calls": 2, "tool_calls": 2},
        }), encoding="utf-8")
        (self.attempt / "events.jsonl").write_text("\n".join([
            json.dumps({"kind": "model_call_started", "model_role": "identity_comparison"}),
            json.dumps({"kind": "model_call_started", "model_role": "workflow"}),
            json.dumps({"kind": "model_call_started", "model_role": "workflow"}),
            json.dumps({"kind": "tool_call_planned"}),
            json.dumps({"kind": "run_finished", "harness_status": "error"}),
        ]) + "\n", encoding="utf-8")
        row = build_case_debug_report(self.root)["cases"][0]
        self.assertEqual(3, row["model_calls"])
        self.assertEqual(1, row["model_calls_bootstrap"])
        self.assertEqual(2, row["model_calls_workflow"])
        self.assertEqual(2, row["tool_calls"])
        self.assertEqual(3, row["event_counts"]["model_calls_observed"])

    def test_valid_citations_do_not_verify_public_goal_without_contract_gate(self):
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "complete", "classification": "locally_complete_ungraded",
            "local_completion_claim": True, "final_evidence_valid": True,
            "metrics": {"model_calls": 2, "tool_calls": 3},
        }), encoding="utf-8")
        (self.attempt / "run.result.json").write_text(json.dumps({
            "local_harness": {
                "status": "complete",
                "final": {"status": "complete", "evidence_ids": ["ev:case:readback"]},
            },
        }), encoding="utf-8")

        report = build_case_debug_report(self.root)
        row = report["cases"][0]
        audit = row["completion_audit"]
        self.assertEqual("valid", audit["citation_integrity"])
        self.assertEqual(1, audit["citation_count"])
        self.assertEqual("complete", audit["structured_final_status"])
        self.assertTrue(audit["structured_completion_claim"])
        self.assertTrue(audit["local_completion_claim"])
        self.assertEqual("complete", row["source_local_harness_status"])
        self.assertEqual("locally_complete_ungraded", row["source_local_classification"])
        self.assertTrue(row["source_local_completion_claim"])
        self.assertEqual("not_recorded", audit["completion_gate_decision"])
        self.assertEqual("unverified", audit["public_goal_status"])
        self.assertEqual(1, report["model_claimed_complete_count"])
        self.assertEqual(1, report["harness_accepted_completion_count"])
        self.assertEqual({"unverified": 1}, report["model_claimed_public_goal_status_counts"])
        self.assertEqual({"unverified": 1}, report["harness_accepted_public_goal_status_counts"])
        self.assertEqual({"valid": 1}, report["model_claimed_citation_integrity_counts"])
        self.assertEqual({"complete": 1}, report["structured_final_status_counts"])

    def test_completion_gate_audit_exports_only_safe_summary_fields(self):
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "unresolved", "classification": "incomplete_workflow",
            "completion_gate": {
                "accepted": False, "branch_id": "intake", "reason_code": "missing_milestone",
                "missing_milestones": ["private milestone body"],
            },
            "metrics": {},
        }), encoding="utf-8")

        report = build_case_debug_report(self.root)
        audit = report["cases"][0]["completion_audit"]
        self.assertEqual("rejected", audit["completion_gate_decision"])
        self.assertEqual("intake", audit["completion_gate_branch_id"])
        self.assertEqual("missing_milestone", audit["completion_gate_reason_code"])
        self.assertEqual(1, audit["missing_milestone_count"])
        self.assertEqual("incomplete_under_contract", audit["public_goal_status"])
        self.assertNotIn("private milestone body", json.dumps(report, sort_keys=True))

    def test_unmapped_public_goal_stays_unverified_when_completion_claim_is_rejected(self):
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "unresolved", "classification": "incomplete_workflow",
            "completion_gate": {
                "accepted": False, "branch_id": None, "reason_code": "goal_unverified",
                "missing_milestones": [],
            },
            "metrics": {},
        }), encoding="utf-8")

        audit = build_case_debug_report(self.root)["cases"][0]["completion_audit"]
        self.assertEqual("rejected", audit["completion_gate_decision"])
        self.assertEqual("unverified", audit["public_goal_status"])

    def test_report_separates_model_complete_claim_from_unverified_harness_outcome(self):
        (self.attempt / "evaluation.json").write_text(json.dumps({
            "harness_status": "unresolved", "classification": "goal_unverified",
            "model_claimed_complete": True, "harness_accepted_completion": False,
            "local_completion_claim": False,
            "completion_verification": {"status": "unverified", "accepted": False,
                                         "branch_id": None, "missing_milestone_count": 0,
                                         "reason_code": "goal_unverified"},
            "metrics": {},
        }), encoding="utf-8")
        (self.attempt / "run.result.json").write_text(json.dumps({
            "local_harness": {"status": "unresolved", "final": {"status": "complete"}},
        }), encoding="utf-8")

        report = build_case_debug_report(self.root)
        row = report["cases"][0]
        self.assertEqual("goal_unverified", row["classification"])
        self.assertEqual("RUN03-GOAL-UNVERIFIED", row["issue_ids"][0])
        self.assertTrue(row["completion_audit"]["model_claimed_complete"])
        self.assertFalse(row["completion_audit"]["harness_accepted_completion"])
        self.assertEqual("unverified", row["completion_audit"]["public_goal_status"])
        self.assertEqual(1, report["model_claimed_complete_count"])
        self.assertEqual(0, report["harness_accepted_completion_count"])
        self.assertEqual({"unverified": 1}, report["completion_verification_status_counts"])

    def test_stop_receipt_separates_historical_manifest_status_from_observed_stop(self):
        manifest_path = self.root / "batch.manifest.json"
        (self.attempt / "evaluation.json").write_text(json.dumps({"metrics": {}}), encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tasks"][0]["attempts"][0]["status"] = "running"
        manifest["tasks"].append({
            "task_id": "public_task_pending", "domain": "pa_provider", "attempts": [{
                "attempt": 1, "attempt_dir": "pa_provider/public_task_pending/attempt-1",
                "status": "pending",
            }],
        })
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        (self.root / "stop-receipt.private.json").write_text(json.dumps({
            "current_interrupted": [{"task_id": "public_task_01"}],
        }), encoding="utf-8")

        report = build_case_debug_report(self.root)
        running = next(row for row in report["cases"] if row["task_id"] == "public_task_01")
        pending = next(row for row in report["cases"] if row["task_id"] == "public_task_pending")
        self.assertEqual("running", running["batch_status"])
        self.assertEqual("paused_after_stop", running["execution_state_at_observation"])
        self.assertEqual("interrupted", running["local_status"])
        self.assertEqual("pending", pending["batch_status"])
        self.assertEqual("pending_not_started", pending["execution_state_at_observation"])
        self.assertEqual("not_started", pending["local_status"])
        self.assertEqual({"pending": 1, "running": 1}, report["batch_status_counts"])

    def test_report_output_cannot_escape_ignored_runs(self):
        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaises(DebugReportError):
                write_case_debug_report(self.root, Path(outside) / "report")


if __name__ == "__main__":
    unittest.main()
