"""Public-instruction completion contracts for the standalone runner.

Contracts are compiled by the harness from the task text and documented role
workflow. Model claims never create or weaken a contract. Predicates inspect
only successful, case-scoped actor observations already in the evidence log.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


_ALIAS_NAMESPACE = "chi-bench-real-case"
_PA_CASE_FINAL = ("approved", "partially_approved", "denied")


def contract_hash(contract):
    if contract is None:
        return None
    encoded = json.dumps(contract, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def build_completion_contract(task_id: str, domain: str, public_instruction: str,
                              scope: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Compile a JSON-only, harness-owned goal contract from public text.

    ``task_id`` is provenance only; no task-name answer mapping is used. A
    contract that cannot identify a documented task endpoint is explicitly
    unverified and cannot satisfy completion.
    """
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty string")
    if domain not in {"pa_provider", "pa_um", "cm"}:
        raise ValueError("domain must be pa_provider, pa_um, or cm")
    if not isinstance(public_instruction, str) or not public_instruction.strip():
        raise ValueError("public_instruction must be non-empty public task text")

    normalized = re.sub(r"\s+", " ", public_instruction).strip().casefold()
    base: dict[str, Any] = {
        "version": 1,
        "task_id": task_id,
        "domain": domain,
        "instruction_sha256": hashlib.sha256(public_instruction.encode("utf-8")).hexdigest(),
        # Preserve the exact assignment separately from the runner's execution
        # wrapper (observed IDs, workspace instructions, bootstrap analysis).
        "public_instruction": public_instruction,
        "scope": dict(scope) if isinstance(scope, Mapping) else None,
        "mapping_status": "mapped",
        "verified_task_goal": True,
        "role_workflow_context": None,
        "mapping_basis": "public task instruction and documented role workflow",
        "endpoint_kind": "",
        "branches": [],
    }

    if domain == "pa_provider":
        base.update(_provider_contract(normalized))
    elif domain == "pa_um":
        base.update(_um_contract(normalized))
        forbidden=bool(re.search(r'\b(?:do not|must not|never)\s+(?:pend|request (?:additional|more) information)\b',normalized))
        if forbidden:
            base['branches']=[b for b in base['branches'] if b['id']!='um_md_information_handoff']
        elif not any(b['id']=='um_md_information_handoff' for b in base['branches']):
            # Conditional intake has a separate rejection/review template. Its
            # review path still permits the documented MD information handoff.
            review=next((b for b in base['branches'] if b['id']=='um_review_completed_without_p2p'),None)
            if review:base['branches'].extend(_um_information_handoff(review['requirements']))
    else:
        base.update(_cm_contract(normalized))
    if base.get('mapping_status') == 'mapped':
        base.setdefault('requested_branch_ids', [b['id'] for b in base['branches']])
    return base


def _provider_contract(instruction: str) -> dict[str, Any]:
    """Map explicit task endpoints; retain role outcomes only as planning candidates."""
    branches = [
            {
                "id": "provider_not_to_submit",
                "proof_kind": "fresh_case_readback",
                "requirements": [
                    _req("provider_disposition_closed", "auth.finalize_provider_determination", "any",
                         "case.status", "eq", "closed"),
                    _req("provider_disposition_identity", "auth.finalize_provider_determination", "any",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                    _req("fresh_closed_case_readback", "cases.get_case", "final_readback",
                         "case.status", "eq", "closed"),
                    _req("not_submit_route_readback", "cases.get_case", "final_readback",
                         "workflow_state.stage_detail", "eq", "no_submit"),
                    _req("case_identity_readback", "cases.get_case", "final_readback",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                ],
            },
            {
                "id": "provider_more_evidence_required",
                "proof_kind": "fresh_case_readback",
                "allows_external_wait": True,
                "requirements": [
                    _req("provider_gather_more_disposition", "auth.finalize_provider_determination", "any",
                         "case.status", "eq", "docs_needed"),
                    _req("provider_disposition_identity", "auth.finalize_provider_determination", "any",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                    _req("fresh_docs_needed_readback", "cases.get_case", "final_readback",
                         "case.status", "eq", "docs_needed"),
                    _req("case_identity_readback", "cases.get_case", "final_readback",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                ],
            },
            {
                "id": "provider_record_ready_for_submission",
                "proof_kind": "fresh_case_readback",
                "requirements": [
                    _req("provider_submit_pa_disposition", "auth.finalize_provider_determination", "any",
                         "case.status", "eq", "ready_to_submit"),
                    _req("provider_disposition_identity", "auth.finalize_provider_determination", "any",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                    _req("fresh_ready_case_readback", "cases.get_case", "final_readback",
                         "case.status", "eq", "ready_to_submit"),
                    _req("forms_complete_readback", "cases.get_case", "final_readback",
                         "form_validation.complete", "eq", True),
                    _req("case_identity_readback", "cases.get_case", "final_readback",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                ],
            },
            {
                "id": "provider_packet_submitted",
                "proof_kind": "fresh_case_readback",
                "requirements": [
                    _req("actual_authorization_submission", "auth.submit_authorization", "any",
                         "case.status", "in", ["submitted", "resubmitted", *_PA_CASE_FINAL]),
                    _req("submitted_case_identity", "auth.submit_authorization", "any",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                    _req("fresh_submission_readback", "cases.get_case", "final_readback",
                         "case.status", "in", ["submitted", "resubmitted", *_PA_CASE_FINAL]),
                    _req("submission_packet_readback", "cases.get_case", "final_readback",
                         "submission_packets", "nonempty", None),
                    _req("case_identity_readback", "cases.get_case", "final_readback",
                         "case.id", "matches_evidence", {"tool": "cases.create_from_order", "path": "case.id"}),
                ],
            },
        ]
    for branch in branches:
        prerequisite = _req("provider_case_requirements_reviewed", "cases.get_case", "before_write",
                            "case.id", "matches_evidence",
                            {"tool": "cases.create_from_order", "path": "case.id"})
        prerequisite["before_tools"] = ["auth.finalize_provider_determination", "auth.submit_authorization"]
        branch["requirements"].append(prerequisite)
    explicit = _explicit_provider_endpoint(instruction)
    if explicit is None:
        if "clinical intake" in instruction[:160]:
            # A clinical intake assigns the provider role; the branch is a
            # decision to be made from case evidence, not an answer that the
            # task must prescribe in advance. Verify the role's supported
            # disposition/handoff, while leaving clinical correctness to the
            # independent benchmark evaluator. Readiness alone is an
            # intermediate state, not completion of a referral workflow.
            return {
                "endpoint_kind": "provider_pa_disposition",
                "explicit_task_endpoint": None,
                "role_workflow_context": "prepare_provider_side_pa_record",
                "mapping_basis": "assigned provider role and public provider disposition service contract",
                "goal_authority": "role_workflow",
                "branches": [b for b in branches if b["id"] != "provider_record_ready_for_submission"],
            }
        return {
            "mapping_status": "unverified",
            "verified_task_goal": False,
            "endpoint_kind": "unknown",
            "explicit_task_endpoint": None,
            "role_workflow_context": "prepare_provider_side_pa_record",
            "planning_candidates": [branch["id"] for branch in branches],
            "mapping_reason_code": "provider_task_endpoint_unspecified",
            "mapping_reason": "public task text does not state which provider disposition endpoint is assigned",
            "branches": [],
        }
    branches = [branch for branch in branches if branch["id"] == explicit]
    return {
        "endpoint_kind": "provider_pa_disposition",
        "verified_task_goal": True,
        "explicit_task_endpoint": explicit,
        "role_workflow_context": "prepare_provider_side_pa_record",
        "branches": branches,
    }


def _explicit_provider_endpoint(instruction: str) -> str | None:
    """Read only direct task imperatives, never clinical narrative statements."""
    direct: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", instruction):
        text = sentence.strip().casefold()
        if not text:
            continue
        if re.match(r"^(?:task|goal|objective)\s*[:\-]", text):
            direct.append(re.sub(r"^(?:task|goal|objective)\s*[:\-]\s*", "", text))
            continue
        if re.match(r"^(?:please\b|you must\b|you should\b|your task\b|your goal\b|complete\b|prepare\b|submit\b|send\b|gather\b|record\b|mark\b|do not\b)", text):
            direct.append(text)
    joined = " ".join(direct)
    if re.search(r"\b(do not submit|not appropriate to submit|mark .*not to submit|authorization is not required)\b", joined):
        return "provider_not_to_submit"
    if re.search(r"\b(gather more evidence|request more information|obtain missing information|leave .*docs_needed)\b", joined):
        return "provider_more_evidence_required"
    if re.search(r"\b(mark .*ready to submit|prepare .*ready to submit|leave .*ready_to_submit)\b", joined):
        return "provider_record_ready_for_submission"
    if re.search(r"\b(submit (?:the )?(?:prior[- ]authorization|authorization|pa|request|packet)|send (?:the )?(?:prior[- ]authorization|authorization|pa|request|packet) to the payer)\b", joined):
        return "provider_packet_submitted"
    return None


def _um_contract(instruction: str) -> dict[str, Any]:
    """Map only explicit public UM stage cues; final outcome may vary by evidence."""
    first = instruction[:800]
    if ("if a failed check requires rejection" in first
            and re.search(r"otherwise,?\s+route the case", first)
            and "physician decision" in first):
        common = [
            _req("intake_completed", "payer_intake_hub.confirm_decisions", "any",
                 "status", "eq", "complete"),
            _req("intake_case_identity", "payer_intake_hub.confirm_decisions", "any",
                 "case_id", "matches_scope_case", None),
        ]
        return {
            "endpoint_kind": "um_intake_conditional_rejection_or_review_handoff",
            "branches": [
                {
                    "id": "um_intake_failure_denial_and_notice",
                    "proof_kind": "fresh_case_readback",
                    "requirements": [*common,
                        _req("failure_denial_finalized", "determination.finalize", "any",
                             "determination.decision", "eq", "denied"),
                        _req("denial_case_identity", "determination.finalize", "any",
                             "determination.case_id", "matches_scope_case", None),
                        _req("denial_notice_delivered", "payer_letter_center.deliver", "any",
                             "letter.delivered_at", "present", None),
                        _req("denial_notice_case_identity", "payer_letter_center.deliver", "any",
                             "letter.case_id", "matches_scope_case", None),
                        _req("denied_state_readback", "determination.get_summary", "final_readback",
                             "case_status", "eq", "denied"),
                        _req("denial_readback_identity", "determination.get_summary", "final_readback",
                             "case_id", "matches_scope_case", None),
                        _req("readback_decision_matches", "determination.get_summary", "final_readback",
                             "determination.decision", "matches_evidence",
                             {"tool": "determination.finalize", "path": "determination.decision"}),
                    ],
                },
                {
                    "id": "um_review_completed_without_p2p",
                    "proof_kind": "fresh_case_readback",
                    "case_can_remain_pending": True,
                    "requirements": [*common,
                        _req("case_routed", "triage.route_case", "any",
                             "route_record.case_id", "matches_scope_case", None),
                        _req("nurse_recommendation", "review.submit_nurse_case_recommendation", "any",
                             "case_recommendation.recommendation", "in", ["approve", "escalate", "request_info"]),
                        _req("nurse_case_identity", "review.submit_nurse_case_recommendation", "any",
                             "case_recommendation.case_id", "matches_scope_case", None),
                        _req("physician_decision", "review.submit_md_case_decision", "any",
                             "case_decision.decision", "in", ["approve", "deny", "partial_approve"]),
                        _req("physician_case_identity", "review.submit_md_case_decision", "any",
                             "case_decision.case_id", "matches_scope_case", None),
                        _req("review_stage_readback", "determination.get_summary", "final_readback",
                             "md_decision", "present", None),
                        _req("readback_md_case_identity", "determination.get_summary", "final_readback",
                             "md_decision.case_id", "matches_scope_case", None),
                        _req("readback_md_decision_matches", "determination.get_summary", "final_readback",
                             "md_decision.decision", "matches_evidence",
                             {"tool": "review.submit_md_case_decision", "path": "case_decision.decision"}),
                        _req("review_readback_identity", "determination.get_summary", "final_readback",
                             "case_id", "matches_scope_case", None),
                    ],
                },
                {
                    "id": "um_review_completed_after_p2p",
                    "proof_kind": "fresh_case_readback",
                    "case_can_remain_pending": True,
                    "requirements": [*common,
                        _req("case_routed", "triage.route_case", "any",
                             "route_record.case_id", "matches_scope_case", None),
                        _req("nurse_recommendation", "review.submit_nurse_case_recommendation", "any",
                             "case_recommendation.recommendation", "in", ["approve", "escalate", "request_info"]),
                        _req("nurse_case_identity", "review.submit_nurse_case_recommendation", "any",
                             "case_recommendation.case_id", "matches_scope_case", None),
                        _req("physician_requested_p2p", "review.submit_md_case_decision", "any",
                             "case_decision.decision", "eq", "p2p_review"),
                        _req("physician_case_identity", "review.submit_md_case_decision", "any",
                             "case_decision.case_id", "matches_scope_case", None),
                        _req("p2p_outcome_recorded", "p2p.record_outcome", "any",
                             "p2p_request.status", "eq", "completed"),
                        _req("p2p_case_identity", "p2p.record_outcome", "any",
                             "case.id", "matches_scope_case", None),
                        _req("p2p_stage_readback", "determination.get_summary", "final_readback",
                             "md_decision", "present", None),
                        _req("readback_md_case_identity", "determination.get_summary", "final_readback",
                             "md_decision.case_id", "matches_scope_case", None),
                        _req("readback_md_decision_matches", "determination.get_summary", "final_readback",
                             "md_decision.decision", "matches_evidence",
                             {"tool": "review.submit_md_case_decision", "path": "case_decision.decision"}),
                        _req("p2p_readback_identity", "determination.get_summary", "final_readback",
                             "case_id", "matches_scope_case", None),
                    ],
                },
            ],
        }
    requirements: list[dict[str, Any]] = []
    # Stage milestones follow the public task's explicit handoff wording.
    if any(term in first for term in ("peer-to-peer session", "p2p session", "peer to peer session")):
        requirements.append(_req("p2p_outcome_recorded", "p2p.record_outcome", "any",
                                 "p2p_request.status", "eq", "completed"))
    elif any(term in first for term in ("md review", "medical director", "physician review")):
        requirements.append(_req("md_decision", "review.submit_md_case_decision", "any",
                                 "case_decision.decision", "in",
                                 ["approve", "deny", "partial_approve", "request_info", "p2p_review"]))
        requirements.append(_req("md_decision_case_identity", "review.submit_md_case_decision", "any",
                                 "case_decision.case_id", "matches_scope_case", None))
    elif "nurse" in first and any(term in first for term in ("clinical review", "nurse review", "review queue")):
        requirements.extend([
            _req("nurse_recommendation", "review.submit_nurse_case_recommendation", "any",
                 "case_recommendation.recommendation", "in", ["approve", "escalate", "request_info"]),
            _req("nurse_case_identity", "review.submit_nurse_case_recommendation", "any",
                 "case_recommendation.case_id", "matches_scope_case", None),
            _req("md_decision", "review.submit_md_case_decision", "any",
                 "case_decision.decision", "in", ["approve", "deny", "partial_approve", "request_info", "p2p_review"]),
            _req("md_decision_case_identity", "review.submit_md_case_decision", "any",
                 "case_decision.case_id", "matches_scope_case", None),
        ])
    elif "triage" in first and any(term in first for term in ("routing", "ready for routing", "route this case")):
        requirements.extend([
            _req("case_routed", "triage.route_case", "any", "route_record.case_id", "matches_scope_case", None),
            _req("nurse_recommendation", "review.submit_nurse_case_recommendation", "any",
                 "case_recommendation.recommendation", "in", ["approve", "escalate", "request_info"]),
            _req("nurse_case_identity", "review.submit_nurse_case_recommendation", "any",
                 "case_recommendation.case_id", "matches_scope_case", None),
            _req("md_decision", "review.submit_md_case_decision", "any",
                 "case_decision.decision", "in", ["approve", "deny", "partial_approve", "request_info", "p2p_review"]),
            _req("md_decision_case_identity", "review.submit_md_case_decision", "any",
                 "case_decision.case_id", "matches_scope_case", None),
        ])
    elif any(term in first for term in ("new intake", "intake desk", "intake checklist", "new submission")):
        requirements.extend([
            _req("intake_completed", "payer_intake_hub.confirm_decisions", "any", "status", "eq", "complete"),
            _req("case_routed", "triage.route_case", "any", "route_record.case_id", "matches_scope_case", None),
            _req("nurse_recommendation", "review.submit_nurse_case_recommendation", "any",
                 "case_recommendation.recommendation", "in", ["approve", "escalate", "request_info"]),
            _req("nurse_case_identity", "review.submit_nurse_case_recommendation", "any",
                 "case_recommendation.case_id", "matches_scope_case", None),
            _req("md_decision", "review.submit_md_case_decision", "any",
                 "case_decision.decision", "in", ["approve", "deny", "partial_approve", "request_info", "p2p_review"]),
            _req("md_decision_case_identity", "review.submit_md_case_decision", "any",
                 "case_decision.case_id", "matches_scope_case", None),
        ])
    else:
        return _unverified("pa_um", "no public task-stage endpoint matched")

    p2p_mentioned = bool(re.search(r"\b(?:p2p|peer[- ]to[- ]peer)\b", first))
    p2p_conditional = bool(re.search(
        r"\b(?:p2p|peer[- ]to[- ]peer)\b.{0,100}\b(?:if|when|where|as)\b.{0,60}\b(?:required|needed|appropriate|available)\b",
        first,
    ))
    p2p_required = p2p_mentioned and not p2p_conditional and any(
        cue in first for cue in ("run it and record the outcome", "run the peer-to-peer session",
                                 "run the p2p session", "run the p2p review")
    )
    if p2p_required and not any(item.get("id") == "p2p_outcome_recorded" for item in requirements):
        requirements.append(_req("p2p_outcome_recorded", "p2p.record_outcome", "any",
                                 "p2p_request.status", "eq", "completed"))
        requirements.append(_req("p2p_case_identity", "p2p.record_outcome", "any",
                                 "case.id", "matches_scope_case", None))
    stage_requirements = list(requirements)
    if any(term in first for term in ("finalize the determination", "final determination", "through to final determination")):
        requirements.append(_req("final_determination", "determination.finalize", "any",
                                 "determination.decision", "in", list(_PA_CASE_FINAL)))
        requirements.append(_req("decision_notice_delivered", "payer_letter_center.deliver", "any",
                                 "letter.delivered_at", "present", None))
        requirements.append(_req("decision_notice_case_identity", "payer_letter_center.deliver", "any",
                                 "letter.case_id", "matches_scope_case", None))
        return {
            "endpoint_kind": "um_final_determination_and_notice",
            "branches": [{
                "id": "um_finalized_determination",
                "proof_kind": "fresh_case_readback",
                "requirements": [*requirements,
                    _req("fresh_terminal_determination_readback", "determination.get_summary", "final_readback",
                         "case_status", "in", list(_PA_CASE_FINAL)),
                    _req("readback_case_identity", "determination.get_summary", "final_readback",
                         "case_id", "matches_scope_case", None),
                    _req("determination_present_on_readback", "determination.get_summary", "final_readback",
                         "determination", "present", None),
                    _req("readback_decision_matches", "determination.get_summary", "final_readback",
                         "determination.decision", "matches_evidence",
                         {"tool": "determination.finalize", "path": "determination.decision"}),
                ],
            }, *_um_route_finalized(stage_requirements), *_um_information_handoff(stage_requirements)],
        }
    if any(term in first for term in ("request additional information", "await additional information", "pend the case")):
        requirements.append(_req("information_notice_delivered", "payer_letter_center.deliver", "any",
                                 "letter.delivered_at", "present", None))
        requirements.append(_req("information_notice_case_identity", "payer_letter_center.deliver", "any",
                                 "letter.case_id", "matches_scope_case", None))
        return {
            "endpoint_kind": "um_information_request",
            "branches": [{
                "id": "um_pending_information",
                "proof_kind": "fresh_case_readback",
                "requirements": [*requirements,
                    _req("fresh_pending_case_readback", "determination.get_summary", "final_readback",
                         "case_status", "eq", "pended_action_required"),
                ],
            }],
        }
    return _unverified("pa_um", "public task does not state a verifiable terminal endpoint")


def _um_route_finalized(stage_requirements):
    """A policy-derived route may itself finalize the case (e.g. a streamlined lane).

    Applies only to routing tasks and only when the observed route result
    carries a terminal case status; the remaining duties are the triage
    disposition record and the decision notice. No outcome is chosen here.
    """
    if not any(item.get('id') == 'case_routed' for item in stage_requirements):
        return []
    return [{
        'id': 'um_route_finalized_determination',
        'proof_kind': 'fresh_case_readback',
        'requirements': [
            *[item for item in stage_requirements if item.get('id', '').startswith('intake')],
            _req('case_routed', 'triage.route_case', 'any', 'route_record.case_id', 'matches_scope_case', None),
            _req('route_finalized_case', 'triage.route_case', 'any', 'case.status', 'in', list(_PA_CASE_FINAL)),
            _req('triage_disposition_recorded', 'triage.set_disposition', 'any', 'triage.disposition', 'present', None),
            _req('triage_disposition_case_identity', 'triage.set_disposition', 'any', 'triage.case_id',
                 'matches_scope_case', None),
            _req('decision_notice_delivered', 'payer_letter_center.deliver', 'any', 'letter.delivered_at', 'present', None),
            _req('decision_notice_case_identity', 'payer_letter_center.deliver', 'any', 'letter.case_id',
                 'matches_scope_case', None),
            _req('fresh_terminal_determination_readback', 'determination.get_summary', 'final_readback',
                 'case_status', 'in', list(_PA_CASE_FINAL)),
            _req('readback_case_identity', 'determination.get_summary', 'final_readback', 'case_id',
                 'matches_scope_case', None),
            _req('determination_present_on_readback', 'determination.get_summary', 'final_readback',
                 'determination', 'present', None),
        ],
    }]


def _um_information_handoff(stage_requirements):
    """A documented MD request-info is a handoff, not a fabricated approval.

    Preserve the stages assigned by public text. This structural alternative
    never establishes that requesting information was clinically appropriate.
    Explicitly assigned P2P work is not bypassed by this earlier handoff.
    """
    if (not any('review.submit_md_case_decision' in r['tools'] for r in stage_requirements)
            or any(r['id']=='p2p_outcome_recorded' for r in stage_requirements)):
        return []
    stage_requirements=[r for r in stage_requirements if not (
        'review.submit_md_case_decision' in r['tools'] and r['predicate']['path']=='case_decision.decision')]
    notice=_req('information_notice_delivered','payer_letter_center.deliver','after_operation','letter.delivered_at','present',None)
    notice['after_tools']=['review.submit_md_case_decision']
    return [{'id':'um_md_information_handoff','proof_kind':'fresh_case_readback','allows_external_wait':True,
        'requirements':[*stage_requirements,
            _req('md_requested_information','review.submit_md_case_decision','any','case_decision.decision','eq','request_info'),
            _req('md_request_rationale','review.submit_md_case_decision','any','case_decision.determination_rationale','nonempty',None),
            _req('md_information_requested','review.submit_md_case_decision','any','case_decision.info_requested','nonempty',None),
            _req('md_information_deadline','review.submit_md_case_decision','any','case_decision.info_deadline','nonempty',None),
            _req('md_request_signed_off','review.submit_md_case_decision','any','case_decision.signed_off','eq',True),
            notice,
            _req('information_notice_case_identity','payer_letter_center.deliver','any','letter.case_id','matches_scope_case',None),
            _req('information_notice_type','payer_letter_center.deliver','any','letter.letter_type','eq','pend'),
            _req('fresh_pending_state','determination.get_summary','final_readback','case_status','eq','pended_action_required'),
            _req('pending_case_identity','determination.get_summary','final_readback','case_id','matches_scope_case',None),
            _req('pending_md_decision','determination.get_summary','final_readback','md_decision.decision','eq','request_info'),
            _req('pending_md_case_identity','determination.get_summary','final_readback','md_decision.case_id','matches_scope_case',None),
            _req('pending_md_record_matches','determination.get_summary','final_readback','md_decision.id','matches_evidence',
                 {'tool':'review.submit_md_case_decision','path':'case_decision.id'}),
        ]}]


def _cm_contract(instruction: str) -> dict[str, Any]:
    """Map CM role outcomes and validate committed terminal write responses."""
    # The approved CM role workflow permits either an engaged finalized plan or
    # a policy-supported terminal exit. The refusal branch still requires the
    # same-case structured refusal record and committed terminal disenrollment.
    has_workflow_choice = "proceed according to the care management workflow" in instruction
    explicit_plan = "finalized care plan" in instruction or "final care plan" in instruction
    if not has_workflow_choice and not explicit_plan:
        return _unverified("cm", "public task does not state a verifiable terminal endpoint")

    plan_requirements = [
        _req("case_opened", "cm_intake.open_case", "any", "case_id", "matches_scope_case", None),
        _req("chart_review_recorded", "cm_chart.submit_chart_review", "any", "case_id", "matches_scope_case", None),
        _req("outreach_recorded", "cm_outreach.end_outreach_call", "any", "case_id", "matches_scope_case", None),
        _req("enrollment_consent_recorded", "cm_outreach.end_outreach_call", "any", "consent_obtained", "eq", True),
        _req("assessment_completed", "cm_assessment.complete_assessment", "any", "status", "eq", "complete"),
        _req("assessment_case_identity", "cm_assessment.complete_assessment", "any", "case_id", "matches_scope_case", None),
        _req("finalized_care_plan", "cm_care_plan.finalize", "terminal_write_response", "status", "eq", "finalized"),
        _req("care_plan_case_identity", "cm_care_plan.finalize", "terminal_write_response", "case_id", "matches_scope_case", None),
        _req("care_plan_has_problems", "cm_care_plan.finalize", "terminal_write_response", "problems", "nonempty", None),
        _req("care_plan_has_escalation_conditions", "cm_care_plan.finalize", "terminal_write_response", "escalation_conditions", "nonempty", None),
        _req("care_plan_has_follow_up_cadence", "cm_care_plan.finalize", "terminal_write_response", "follow_up_cadence_kind", "present", None),
    ]
    branches: list[dict[str, Any]] = [{
        "id": "cm_finalized_care_plan",
        "proof_kind": "terminal_write_response",
        "requirements": plan_requirements,
    }]
    if has_workflow_choice or explicit_plan:
        branches.append({
            "id": "cm_documented_refusal_and_disenrollment",
            "proof_kind": "terminal_write_response",
            "requirements": [
                _req("case_opened", "cm_intake.open_case", "any", "case_id", "matches_scope_case", None),
                _req("chart_review_recorded", "cm_chart.submit_chart_review", "any", "case_id", "matches_scope_case", None),
                _req("outreach_case_identity", "cm_outreach.end_outreach_call", "any", "case_id", "matches_scope_case", None),
                _req("documented_refusal", "cm_outreach.end_outreach_call", "any",
                     "engagement_status", "eq", "refused"),
                _req("consent_not_obtained", "cm_outreach.end_outreach_call", "any",
                     "consent_obtained", "eq", False),
                _req("refusal_documented_in_notes", "cm_outreach.end_outreach_call", "any",
                     "notes", "nonempty", None),
                _req("case_disenrolled", "cm_intake.disenroll_case", "terminal_write_response",
                     "status", "eq", "disenrolled"),
                _req("disenrollment_case_identity", "cm_intake.disenroll_case", "terminal_write_response",
                     "case_id", "matches_scope_case", None),
            ],
        })
    return {
        "endpoint_kind": "cm_role_terminal_outcome",
        "branches": branches,
        "requested_branch_ids": (["cm_finalized_care_plan"] if explicit_plan
                                 else [b['id'] for b in branches]),
        "mapping_basis": "public task endpoint plus public CM role workflow and committed service return contract",
        "terminal_branch_basis": "CM role policy permits a finalized plan or policy-supported terminal exit",
    }


def _unverified(domain: str, reason: str) -> dict[str, Any]:
    return {"mapping_status": "unverified", "verified_task_goal": False, "endpoint_kind": "unknown",
            "mapping_reason_code": "public_goal_unmapped", "mapping_reason": reason, "branches": []}


def _req(milestone_id: str, tool: str, phase: str, path: str, op: str, value: Any) -> dict[str, Any]:
    return {"id": milestone_id, "tools": [tool], "phase": phase,
            "predicate": {"path": path, "op": op, "value": value}}


def validate_completion_contract(contract: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]],
                                 scope: Mapping[str, Any] | None = None,
                                 actual_scope: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Validate branch milestones against successful same-scope observations.

    The result contains only stable milestone IDs and reason codes; clinical
    observation values are never copied into failure diagnostics.
    """
    meta = _validation_meta(contract)
    if (not isinstance(contract, Mapping) or contract.get("mapping_status") != "mapped"
            or contract.get("verified_task_goal") is not True):
        return {**meta, "accepted": False, "branch_id": None, "missing_milestones": [],
                "reason_code": "goal_unverified", "proof_kind": None}
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)):
        return {**meta, "accepted": False, "branch_id": None, "missing_milestones": [],
                "reason_code": "invalid_evidence", "proof_kind": None}
    expected_scope = scope if isinstance(scope, Mapping) else contract.get("scope")
    verified_scope = actual_scope if isinstance(actual_scope, Mapping) else expected_scope
    clean = [_clean_evidence(item, expected_scope) for item in evidence]
    latest_write = max((i for i, item in enumerate(clean)
                        if item is not None and item["outcome"] == "success" and item["effect"] == "write"),
                       default=-1)

    branches = contract.get("branches")
    if not isinstance(branches, list) or not branches:
        return {**meta, "accepted": False, "branch_id": None, "missing_milestones": [],
                "reason_code": "goal_unverified", "proof_kind": None}
    if not _valid_branches(branches):
        return {**meta, "accepted": False, "branch_id": None, "missing_milestones": [],
                "reason_code": "completion_contract_invalid", "proof_kind": None}
    best_missing: list[str] | None = None
    for branch in branches:
        if not isinstance(branch, Mapping) or not isinstance(branch.get("requirements"), list):
            continue
        requirements = branch["requirements"]
        missing = [str(req.get("id", "invalid_requirement")) for req in requirements
                   if not _requirement_satisfied(req, clean, latest_write, expected_scope, verified_scope)]
        if not missing:
            return {**meta, "observed_endpoint_verified": True, "accepted": True,
                    "branch_id": branch.get("id"), "missing_milestones": [],
                    "allows_external_wait": branch.get('allows_external_wait', False),
                    "case_can_remain_pending": branch.get('case_can_remain_pending',False) or branch.get('allows_external_wait',False),
                    "reason_code": "accepted", "proof_kind": branch.get("proof_kind")}
        if best_missing is None or len(missing) < len(best_missing):
            best_missing = missing
    return {**meta, "accepted": False, "branch_id": None, "missing_milestones": best_missing or [],
            "reason_code": "required_milestones_unobserved", "proof_kind": None}


def _validation_meta(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, Mapping):
        return {"mapping_status": "unverified", "verified_task_goal": False,
                "observed_endpoint_verified": False,
                "role_workflow_context": None, "endpoint_kind": "unknown"}
    return {"mapping_status": contract.get("mapping_status", "unverified"),
            "verified_task_goal": contract.get("verified_task_goal") is True,
            "observed_endpoint_verified": False,
            "role_workflow_context": contract.get("role_workflow_context"),
            "endpoint_kind": contract.get("endpoint_kind", "unknown"),
            "mapping_reason_code": contract.get("mapping_reason_code")}


def _valid_branches(branches: list[Any]) -> bool:
    """Reject vacuous/malformed branches and branches without trusted terminal proof."""
    valid_phases = {"any", "final_readback", "terminal_write_response", "before_write", "after_operation"}
    valid_ops = {"eq", "in", "present", "nonempty", "truthy", "matches_scope_case", "matches_evidence"}
    branch_ids: set[str] = set()
    for branch in branches:
        if not isinstance(branch, Mapping):
            return False
        branch_id = branch.get("id")
        if not isinstance(branch_id, str) or not branch_id or branch_id in branch_ids:
            return False
        branch_ids.add(branch_id)
        if any(key in branch and not isinstance(branch[key],bool)
               for key in ('allows_external_wait','case_can_remain_pending')):
            return False
        requirements = branch.get("requirements")
        if not isinstance(requirements, list) or not requirements:
            return False
        terminal_proof = False
        requirement_ids: set[str] = set()
        for requirement in requirements:
            if not isinstance(requirement, Mapping):
                return False
            rid = requirement.get("id")
            tools = requirement.get("tools")
            phase = requirement.get("phase", "any")
            if phase=='after_operation' and (not isinstance(requirement.get('after_tools'),list)
                    or not requirement['after_tools'] or any(not isinstance(t,str) or not t for t in requirement['after_tools'])):
                return False
            if phase == "before_write" and (not isinstance(requirement.get("before_tools"), list)
                    or not requirement["before_tools"]
                    or any(not isinstance(tool, str) or not tool for tool in requirement["before_tools"])):
                return False
            predicate = requirement.get("predicate")
            if (not isinstance(rid, str) or not rid or not isinstance(tools, list) or not tools
                    or any(not isinstance(tool, str) or not tool for tool in tools)
                    or not isinstance(phase, str) or phase not in valid_phases or not isinstance(predicate, Mapping)
                    or not isinstance(predicate.get("path"), str) or not predicate.get("path")
                    or not isinstance(predicate.get("op"), str) or predicate.get("op") not in valid_ops
                    or "value" not in predicate
                    or rid in requirement_ids):
                return False
            requirement_ids.add(rid)
            if phase in {"final_readback", "terminal_write_response"}:
                terminal_proof = True
        if not terminal_proof:
            return False
    return True


def _clean_evidence(item: Any, expected_scope: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(item, Mapping) or item.get("outcome") != "success":
        return None
    observed_scope = item.get("scope")
    if expected_scope is not None and not _strict_equal(observed_scope, expected_scope):
        return None
    tool = item.get("tool")
    if not isinstance(tool, str) or not tool:
        return None
    return {"tool": tool, "effect": item.get("effect"), "observed_result": item.get("observed_result"),
            "outcome": item.get("outcome"), "scope": observed_scope}


def _requirement_satisfied(requirement: Any, evidence: list[dict[str, Any] | None],
                           latest_write: int, expected_scope: Mapping[str, Any] | None,
                           verified_scope: Mapping[str, Any] | None) -> bool:
    if not isinstance(requirement, Mapping):
        return False
    tools = requirement.get("tools")
    predicate = requirement.get("predicate")
    if not isinstance(tools, list) or not tools or not isinstance(predicate, Mapping):
        return False
    phase = requirement.get("phase", "any")
    matches: list[tuple[int, dict[str, Any], Any]] = []
    for index, item in enumerate(evidence):
        if item is None or not _tool_matches(item["tool"], tools):
            continue
        value = _payload_path(item["observed_result"], str(predicate.get("path", "")))
        if _predicate_matches(predicate, value, evidence, tools, expected_scope, verified_scope):
            matches.append((index, item, value))
    if not matches:
        return False
    if phase == "any":
        return True
    if phase == 'after_operation':
        targets=requirement.get('after_tools',[])
        indices=[i for i,item in enumerate(evidence) if item is not None and _tool_matches(item['tool'],targets)]
        return bool(indices) and any(i>max(indices) for i,item,value in matches)
    if phase == "before_write":
        targets = requirement.get("before_tools", [])
        indices = [index for index, item in enumerate(evidence)
                   if item is not None and item.get("effect") == "write"
                   and _tool_matches(item["tool"], targets)]
        if not indices:
            return False
        target_index = max(indices)
        previous_write = max((index for index, item in enumerate(evidence[:target_index])
                              if item is not None and item.get("effect") == "write"), default=-1)
        return any(item.get("effect") == "read" and previous_write < index < target_index
                   for index, item, _ in matches)
    if phase == "terminal_write_response":
        terminal_index, terminal_item, _ = max(matches, key=lambda row: row[0])
        return terminal_item.get("effect") == "write" and terminal_index == latest_write
    if phase == "final_readback":
        return any(item.get("effect") == "read" and index > latest_write
                   for index, item, _ in matches)
    return False


def unmet_tool_prerequisites(contract: Any, observations: Any, tool_name: str,
                            scope: Mapping[str, Any], actual_scope: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Check harness-owned read dependencies before any external mutation."""
    if not isinstance(contract, Mapping):
        return []
    evidence = [_clean_evidence(item, scope) for item in observations]
    last_write = max((i for i, item in enumerate(evidence)
                      if item is not None and item.get("effect") == "write"), default=-1)
    missing = {}
    for branch in contract.get("branches", []):
        for requirement in branch.get("requirements", []):
            if (requirement.get("phase") != "before_write"
                    or not _tool_matches(tool_name, requirement.get("before_tools", []))):
                continue
            # The proposed mutation has not happened: require a fresh read of
            # the current state, using exactly the same evidence predicate.
            check = dict(requirement, phase="final_readback")
            if not _requirement_satisfied(check, evidence, last_write, scope, actual_scope):
                missing[requirement["id"]] = {"id": requirement["id"], "read_tools": requirement["tools"]}
    return list(missing.values())


def _tool_matches(observed: str, required: list[Any]) -> bool:
    for canonical in required:
        if not isinstance(canonical, str):
            continue
        slug = re.sub(r"[^A-Za-z0-9_-]+", "_", canonical).strip("_")[:36] or "tool"
        alias = "mcp_" + slug + "_" + hashlib.sha256(
            f"{_ALIAS_NAMESPACE}\0{canonical}".encode("utf-8")).hexdigest()[:12]
        if observed in {canonical, alias}:
            return True
    return False


def _payload_path(value: Any, path: str) -> Any:
    if not path:
        return None
    current = _unwrap(value)
    for part in path.split("."):
        if isinstance(current, Mapping):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return None
    return current


def _unwrap(value: Any) -> Any:
    if not isinstance(value, Mapping):
        return value
    structured = value.get("structuredContent")
    if structured is not None:
        return structured
    content = value.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, Mapping):
                parsed = block.get("parsed_json")
                if isinstance(parsed, (dict, list)):
                    return parsed
                text = block.get("text")
                if isinstance(text, str):
                    try:
                        import json
                        decoded = json.loads(text)
                    except (ValueError, TypeError):
                        continue
                    if isinstance(decoded, (dict, list)):
                        return decoded
    return value


def _predicate_matches(predicate: Mapping[str, Any], actual: Any,
                       evidence: list[dict[str, Any] | None], tools: list[Any],
                       expected_scope: Mapping[str, Any] | None,
                       verified_scope: Mapping[str, Any] | None) -> bool:
    op = predicate.get("op")
    expected = predicate.get("value")
    if op == "eq":
        return _strict_equal(actual, expected)
    if op == "in":
        return isinstance(expected, list) and any(_strict_equal(actual, item) for item in expected)
    if op == "present":
        return actual is not None
    if op == "nonempty":
        return isinstance(actual, (str, list, dict)) and bool(actual)
    if op == "truthy":
        return bool(actual)
    if op == "matches_scope_case":
        if not isinstance(verified_scope, Mapping) or not isinstance(actual, str):
            return False
        return actual == verified_scope.get("case")
    if op == "matches_evidence" and isinstance(expected, Mapping):
        reference_tools = expected.get("tool")
        reference_path = expected.get("path")
        if not isinstance(reference_tools, str) or not isinstance(reference_path, str):
            return False
        for item in evidence:
            if item is None or not _tool_matches(item["tool"], [reference_tools]):
                continue
            reference = _payload_path(item["observed_result"], reference_path)
            if reference is not None and _strict_equal(actual, reference):
                return True
        return False
    return False


def _strict_equal(actual: Any, expected: Any) -> bool:
    """Avoid Python's bool/int equivalence while allowing compatible JSON scalars."""
    if isinstance(actual, bool) != isinstance(expected, bool):
        return False
    if actual is None or expected is None:
        return actual is None and expected is None
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, Mapping):
        return (actual.keys() == expected.keys()
                and all(_strict_equal(actual[key], expected[key]) for key in actual))
    if isinstance(actual, (list, tuple)):
        return len(actual) == len(expected) and all(
            _strict_equal(left, right) for left, right in zip(actual, expected)
        )
    return actual == expected
