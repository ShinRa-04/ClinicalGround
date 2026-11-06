from __future__ import annotations

import unittest

from health_harness_codex.completion_contracts import (
    build_completion_contract,
    validate_completion_contract,
)


class CompletionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = {"environment": "synthetic", "task": "case", "organization": "org",
                      "principal": "actor", "patient": "patient-1", "case": "case-1"}

    def _ev(self, tool: str, effect: str, result: dict, *, case: str = "case-1") -> dict:
        scope = dict(self.scope, case=case)
        return {"id": f"ev-{len(getattr(self, '_events', []))}", "scope": scope, "tool": tool,
                "effect": effect, "outcome": "success", "observed_result": {"structuredContent": result}}

    def _validate(self, contract: dict, evidence: list[dict]) -> dict:
        return validate_completion_contract(contract, evidence, scope=self.scope)

    def test_provider_conditional_endpoints_require_fresh_case_readback(self) -> None:
        cases = [
            ("provider_not_to_submit", "closed", {"workflow_stage": "closed", "stage_detail": "no_submit"},
             {"complete": False}, []),
            ("provider_more_evidence_required", "docs_needed", {"workflow_stage": "pre_submission", "stage_detail": "docs_needed"},
             {"complete": False}, []),
            ("provider_record_ready_for_submission", "ready_to_submit", {"workflow_stage": "pre_submission", "stage_detail": "ready_to_submit"},
             {"complete": True}, []),
            ("provider_packet_submitted", "submitted", {"workflow_stage": "submitted", "stage_detail": "submitted"},
             {"complete": True}, [{"id": "packet-1"}]),
        ]
        for branch_id, status, workflow_state, validation, packets in cases:
            with self.subTest(branch=branch_id):
                directive = {
                    "provider_not_to_submit": "Task: do not submit this request when authorization is not required.",
                    "provider_more_evidence_required": "Task: gather more evidence and record the case as docs_needed.",
                    "provider_record_ready_for_submission": "Task: prepare the case and mark it ready to submit.",
                    "provider_packet_submitted": "Task: submit the prior-authorization request to the payer.",
                }[branch_id]
                contract = build_completion_contract("public-case-a", "pa_provider", directive, self.scope)
                self.assertEqual(contract["mapping_status"], "mapped")
                self.assertEqual([b["id"] for b in contract["branches"]], [branch_id])
                writes = [self._ev("cases.create_from_order", "write", {"case": {"id": "actual-case"}})]
                writes.append(self._ev("cases.get_case", "read", {"case": {"id": "actual-case", "status": "draft"}}))
                if branch_id == "provider_packet_submitted":
                    writes.append(self._ev("auth.submit_authorization", "write", {"case": {"id": "actual-case", "status": status}}))
                else:
                    writes.append(self._ev("auth.finalize_provider_determination", "write",
                                           {"case": {"id": "actual-case", "status": status}}))
                readback = self._ev("cases.get_case", "read", {
                    "case": {"id": "actual-case", "status": status},
                    "workflow_state": workflow_state,
                    "form_validation": validation,
                    "submission_packets": packets,
                })
                result = self._validate(contract, [*writes, readback])
                self.assertTrue(result["accepted"], result)
                self.assertEqual(result["branch_id"], branch_id)
                # A post-decision read is not proof the actor inspected current
                # requirements before deciding; both dependencies matter.
                self.assertFalse(self._validate(contract, [writes[0], *writes[2:], readback])["accepted"])

    def test_provider_explicit_submit_goal_does_not_accept_docs_needed(self) -> None:
        contract = build_completion_contract("any-id", "pa_provider",
            "Prepare the supported packet and submit the prior authorization request.", self.scope)
        self.assertEqual([b["id"] for b in contract["branches"]], ["provider_packet_submitted"])
        evidence = [
            self._ev("auth.finalize_provider_determination", "write", {"case": {"status": "docs_needed"}}),
            self._ev("cases.get_case", "read", {"case": {"id": "actual-case", "status": "docs_needed"},
                         "workflow_state": {"workflow_stage": "pre_submission", "stage_detail": "docs_needed"}}),
        ]
        self.assertFalse(self._validate(contract, evidence)["accepted"])

    def test_provider_readback_must_match_created_actual_case(self) -> None:
        contract = build_completion_contract("any-id", "pa_provider",
            "Task: do not submit this request when authorization is not required.", self.scope)
        evidence = [
            self._ev("cases.create_from_order", "write", {"case": {"id": "actual-case"}}),
            self._ev("auth.finalize_provider_determination", "write", {"case": {"id": "actual-case", "status": "closed"}}),
            self._ev("cases.get_case", "read", {"case": {"id": "other-case", "status": "closed"},
                "workflow_state": {"workflow_stage": "closed", "stage_detail": "no_submit"}}),
        ]
        self.assertFalse(self._validate(contract, evidence)["accepted"])

    def test_provider_intake_maps_role_goal_without_prescribing_clinical_answer(self) -> None:
        narrative = "Clinical intake. A referring clinician recommends further evaluation and treatment."
        left = build_completion_contract("public-task-a", "pa_provider", narrative, self.scope)
        right = build_completion_contract("public-task-b", "pa_provider", narrative, self.scope)
        self.assertEqual(left["mapping_status"], "mapped")
        self.assertEqual(left["role_workflow_context"], "prepare_provider_side_pa_record")
        self.assertEqual(left["branches"], right["branches"])
        self.assertEqual(len(left["branches"]), 3)
        self.assertNotIn("provider_record_ready_for_submission", [b["id"] for b in left["branches"]])
        self.assertEqual(self._validate(left, [self._ev("cases.get_case", "read", {"case": {"status": "closed"}})])[
            "reason_code"], "required_milestones_unobserved")

    def test_provider_quoted_clinical_history_does_not_create_submission_goal(self) -> None:
        narrative = ('Clinical intake. The patient says, "Please submit the prior-authorization request"; '
                     'the referring clinician recommends further evaluation.')
        contract = build_completion_contract("public-task", "pa_provider", narrative, self.scope)
        self.assertEqual(contract["mapping_status"], "mapped")
        self.assertEqual(contract["explicit_task_endpoint"], None)

    def test_referral_ready_state_is_not_completion_but_submission_is(self):
        contract = build_completion_contract("arbitrary-id", "pa_provider",
            "Clinical intake. The clinician recommends a treatment requiring provider evaluation.", self.scope)
        ready = {"case": {"id": "actual-case", "status": "ready_to_submit"},
                 "form_validation": {"complete": True}, "submission_packets": []}
        evidence = [self._ev("cases.create_from_order", "write", {"case": {"id": "actual-case"}}),
            self._ev("cases.get_case", "read", {"case": {"id": "actual-case", "status": "draft"}}),
            self._ev("auth.finalize_provider_determination", "write", ready),
            self._ev("cases.get_case", "read", ready)]
        self.assertFalse(self._validate(contract, evidence)["accepted"])
        submitted = {"case": {"id": "actual-case", "status": "submitted"},
                     "submission_packets": [{"id": "packet-1"}]}
        evidence += [self._ev("auth.submit_authorization", "write", submitted),
                     self._ev("cases.get_case", "read", submitted)]
        self.assertEqual("provider_packet_submitted", self._validate(contract, evidence)["branch_id"])

    def test_unassigned_provider_goal_still_fails_closed(self) -> None:
        contract = build_completion_contract("public-task", "pa_provider", "Read this unspecified record.", self.scope)
        self.assertEqual(contract["mapping_status"], "unverified")

    def test_um_denial_is_a_valid_terminal_outcome_only_with_notice_and_readback(self) -> None:
        instruction = ("MD Review. Record the MD decision, run the peer-to-peer first if the case requires one, "
                       "and finalize the determination yourself.")
        contract = build_completion_contract("um-task", "pa_um", instruction, self.scope)
        self.assertFalse(any(requirement["id"] == "p2p_outcome_recorded"
                             for branch in contract["branches"] for requirement in branch["requirements"]))
        evidence = [
            self._ev("review.submit_md_case_decision", "write", {"case_decision": {"case_id": "case-1", "decision": "deny"}}),
            self._ev("determination.finalize", "write", {"case": {"status": "denied"},
                         "determination": {"case_id": "case-1", "decision": "denied"}}),
            self._ev("payer_letter_center.deliver", "write", {"letter": {"case_id": "case-1", "delivered_at": "2030-01-01T00:00:00Z"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "denied",
                         "determination": {"decision": "denied"}}),
        ]
        result = self._validate(contract, evidence)
        self.assertTrue(result["accepted"], result)
        self.assertFalse(self._validate(contract, evidence[:-1])["accepted"])

    def test_um_route_that_finalizes_the_case_is_a_distinct_supported_branch(self) -> None:
        instruction = ("Triage Routing. Ready to route this case. Pick the right review lane, then work the case "
                       "through clinical review, MD decision, and any P2P to final determination yourself.")
        contract = build_completion_contract("um-triage", "pa_um", instruction, self.scope)
        self.assertIn("um_route_finalized_determination", [b["id"] for b in contract["branches"]])
        finalized = [
            self._ev("triage.route_case", "write", {"route_record": {"case_id": "case-1"},
                                                    "case": {"id": "case-1", "status": "approved"}}),
            self._ev("triage.set_disposition", "write", {"triage": {"case_id": "case-1", "disposition": "synthetic"}}),
            self._ev("payer_letter_center.deliver", "write", {"letter": {"case_id": "case-1", "delivered_at": "2030-01-01T00:00:00Z"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "approved",
                                                           "determination": {"final_decision": "approved"}}),
        ]
        result = self._validate(contract, finalized)
        self.assertTrue(result["accepted"], result)
        # A route that leaves the case pending cannot use this branch.
        pending = [dict(finalized[0], observed_result={"structuredContent": {
            "route_record": {"case_id": "case-1"}, "case": {"id": "case-1", "status": "pending_review"}}}), *finalized[1:]]
        self.assertFalse(self._validate(contract, pending)["accepted"])
        # Disposition and notice remain required.
        self.assertFalse(self._validate(contract, [finalized[0], finalized[3]])["accepted"])

    def test_um_full_intake_requires_each_stage_not_just_terminal_citation(self) -> None:
        instruction = ("New Intake. Walk the intake checklist, route it, then drive clinical review, "
                       "MD decision, and any P2P through to final determination yourself.")
        contract = build_completion_contract("um-intake", "pa_um", instruction, self.scope)
        evidence = [
            self._ev("payer_intake_hub.confirm_decisions", "write", {"status": "complete"}),
            self._ev("triage.route_case", "write", {"route_record": {"case_id": "case-1", "route_target": "standard_um"}}),
            self._ev("review.submit_nurse_case_recommendation", "write", {"case_recommendation": {"case_id": "case-1", "recommendation": "escalate"}}),
            self._ev("review.submit_md_case_decision", "write", {"case_decision": {"case_id": "case-1", "decision": "approve"}}),
            self._ev("determination.finalize", "write", {"case": {"status": "approved"},
                         "determination": {"decision": "approved"}}),
            self._ev("payer_letter_center.deliver", "write", {"letter": {"case_id": "case-1", "delivered_at": "2030-01-01T00:00:00Z"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "approved",
                         "determination": {"decision": "approved"}}),
        ]
        result = self._validate(contract, evidence)
        self.assertTrue(result["accepted"], result)
        self.assertFalse(self._validate(contract, evidence[1:])["accepted"])

    def test_um_conditional_rejection_or_review_handoff_has_distinct_branches(self) -> None:
        instruction = ("New Intake. Complete the intake checklist. If a failed check requires rejection, "
                       "finalize the denial and issue the required letter. Otherwise, route the case and "
                       "complete clinical review, the physician decision, and any required peer-to-peer review.")
        contract = build_completion_contract("um-conditional", "pa_um", instruction, self.scope)
        self.assertEqual(contract["endpoint_kind"], "um_intake_conditional_rejection_or_review_handoff")
        common = [self._ev("payer_intake_hub.confirm_decisions", "write", {"case_id": "case-1", "status": "complete"})]
        denial = [*common,
            self._ev("determination.finalize", "write", {"determination": {"case_id": "case-1", "decision": "denied"}}),
            self._ev("payer_letter_center.deliver", "write", {"letter": {"case_id": "case-1", "delivered_at": "2030-01-01T00:00:00Z"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "denied", "determination": {"case_id": "case-1", "decision": "denied"}}),
        ]
        self.assertEqual(self._validate(contract, denial)["branch_id"], "um_intake_failure_denial_and_notice")

        review = [*common,
            self._ev("triage.route_case", "write", {"route_record": {"case_id": "case-1", "route_target": "standard_um"}}),
            self._ev("review.submit_nurse_case_recommendation", "write", {"case_recommendation": {"case_id": "case-1", "recommendation": "escalate"}}),
            self._ev("review.submit_md_case_decision", "write", {"case_decision": {"case_id": "case-1", "decision": "approve"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "under_review", "md_decision": {"case_id": "case-1", "decision": "approve"}}),
        ]
        self.assertEqual(self._validate(contract, review)["branch_id"], "um_review_completed_without_p2p")

        p2p = [*common,
            self._ev("triage.route_case", "write", {"route_record": {"case_id": "case-1", "route_target": "standard_um"}}),
            self._ev("review.submit_nurse_case_recommendation", "write", {"case_recommendation": {"case_id": "case-1", "recommendation": "escalate"}}),
            self._ev("review.submit_md_case_decision", "write", {"case_decision": {"case_id": "case-1", "decision": "p2p_review"}}),
            self._ev("p2p.record_outcome", "write", {"p2p_request": {"status": "completed"}, "case": {"id": "case-1"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "under_review", "md_decision": {"case_id": "case-1", "decision": "p2p_review"}}),
        ]
        self.assertEqual(self._validate(contract, p2p)["branch_id"], "um_review_completed_after_p2p")

    def test_um_explicit_peer_session_requires_recorded_outcome(self) -> None:
        instruction = ("Peer-to-Peer Session. Run it and record the outcome, then finalize the determination.")
        contract = build_completion_contract("um-p2p", "pa_um", instruction, self.scope)
        evidence = [
            self._ev("p2p.record_outcome", "write", {"p2p_request": {"status": "completed"},
                 "case": {"id": "case-1"}}),
            self._ev("determination.finalize", "write", {"case": {"status": "denied"},
                 "determination": {"case_id": "case-1", "decision": "denied"}}),
            self._ev("payer_letter_center.deliver", "write", {"letter": {"case_id": "case-1", "delivered_at": "2030-01-01T00:00:00Z"}}),
            self._ev("determination.get_summary", "read", {"case_id": "case-1", "case_status": "denied",
                 "determination": {"case_id": "case-1", "decision": "denied"}}),
        ]
        result = self._validate(contract, evidence)
        self.assertTrue(result["accepted"], result)
        self.assertFalse(self._validate(contract, evidence[1:])["accepted"])

    def test_cm_finalized_plan_and_refusal_are_distinct_committed_endpoints(self) -> None:
        instruction = "Complete intake and outreach; proceed according to the care management workflow."
        contract = build_completion_contract("cm-task", "cm", instruction, self.scope)
        plan = [
            self._ev("cm_intake.open_case", "write", {"case_id": "case-1"}),
            self._ev("cm_chart.submit_chart_review", "write", {"case_id": "case-1"}),
            self._ev("cm_outreach.end_outreach_call", "write", {"case_id": "case-1", "engagement_status": "engaged", "consent_obtained": True}),
            self._ev("cm_assessment.complete_assessment", "write", {"case_id": "case-1", "status": "complete"}),
            self._ev("cm_care_plan.finalize", "write", {"case_id": "case-1", "status": "finalized",
                 "problems": [{"problem_id": "p1", "goals": [{"interventions": [{}]}]}],
                 "escalation_conditions": ["trigger"], "follow_up_cadence_kind": "weekly"}),
        ]
        result = self._validate(contract, plan)
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["proof_kind"], "terminal_write_response")

        refusal = [
            self._ev("cm_intake.open_case", "write", {"case_id": "case-1"}),
            self._ev("cm_chart.submit_chart_review", "write", {"case_id": "case-1"}),
            self._ev("cm_outreach.end_outreach_call", "write", {"case_id": "case-1", "engagement_status": "refused", "consent_obtained": False, "notes": "Documented the member's refusal."}),
            self._ev("cm_intake.disenroll_case", "write", {"case_id": "case-1", "status": "disenrolled"}),
        ]
        result = self._validate(contract, refusal)
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["branch_id"], "cm_documented_refusal_and_disenrollment")

    def test_cm_terminal_write_must_be_latest_write_and_same_case(self) -> None:
        contract = build_completion_contract("cm-task", "cm",
            "Take the case through to a finalized care plan.", self.scope)
        evidence = [
            self._ev("cm_intake.open_case", "write", {"case_id": "case-1"}),
            self._ev("cm_chart.submit_chart_review", "write", {"case_id": "case-1"}),
            self._ev("cm_outreach.end_outreach_call", "write", {"case_id": "case-1", "engagement_status": "engaged", "consent_obtained": True}),
            self._ev("cm_assessment.complete_assessment", "write", {"case_id": "case-1", "status": "complete"}),
            self._ev("cm_care_plan.finalize", "write", {"case_id": "case-1", "status": "finalized",
                 "problems": [{"problem_id": "p1", "goals": [{"interventions": [{}]}]}],
                 "escalation_conditions": ["trigger"], "follow_up_cadence_kind": "weekly"}),
        ]
        stale = [*evidence, self._ev("cm_care_plan.save_care_plan", "write", {"case_id": "case-1"})]
        wrong_scope = [self._ev("cm_intake.open_case", "write", {"case_id": "other-case"}, case="other-case")]
        self.assertFalse(self._validate(contract, stale)["accepted"])
        self.assertFalse(self._validate(contract, wrong_scope)["accepted"])

    def test_unmapped_public_goal_fails_closed_without_patient_data_diagnostics(self) -> None:
        contract = build_completion_contract("unmapped", "pa_um", "Case review.", self.scope)
        result = self._validate(contract, [self._ev("determination.finalize", "write", {"case": {"status": "denied"}})])
        self.assertEqual(contract["mapping_status"], "unverified")
        self.assertEqual(result["reason_code"], "goal_unverified")
        self.assertEqual(result["missing_milestones"], [])

    def test_validator_rejects_empty_or_untrusted_branches(self) -> None:
        base = build_completion_contract("um-task", "pa_um",
            "MD Review. Record the physician decision and finalize the determination.", self.scope)
        empty = dict(base, branches=[{"id": "empty", "requirements": []}])
        no_terminal = dict(base, branches=[{"id": "presence-only", "requirements": [
            {"id": "weak", "tools": ["determination.finalize"], "phase": "any",
             "predicate": {"path": "status", "op": "present", "value": None}},
        ]}])
        evidence = [self._ev("determination.finalize", "write", {"status": "approved"})]
        self.assertEqual(self._validate(empty, evidence)["reason_code"], "completion_contract_invalid")
        self.assertEqual(self._validate(no_terminal, evidence)["reason_code"], "completion_contract_invalid")

    def test_boolean_predicates_do_not_accept_integer_one(self) -> None:
        contract = {
            "mapping_status": "mapped", "verified_task_goal": True, "task_id": "case",
            "endpoint_kind": "synthetic", "scope": self.scope,
            "branches": [{"id": "strict-boolean", "requirements": [
                {"id": "flag", "tools": ["records.lookup"], "phase": "final_readback",
                 "predicate": {"path": "flag", "op": "eq", "value": True}},
            ]}],
        }
        evidence = [self._ev("records.lookup", "read", {"flag": 1})]
        self.assertFalse(self._validate(contract, evidence)["accepted"])


if __name__ == "__main__":
    unittest.main()
