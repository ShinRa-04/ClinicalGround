"""Mechanical controller for one policy-derived route and immutable triage commit."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import Scope


_TRIAGE_GET = "triage.get"
_TRIAGE_SET = "triage.set_disposition"
_TRIAGE_ROUTE = "triage.route_case"
_CALCULATE_SLA = "triage.calculate_sla"
_CHECK_GOLD_CARD = "triage.check_gold_card"
_MD_DECISION = 'review.submit_md_case_decision'
_QUEUE_DISCOVERY = "payer_intake_hub.list_intake_queue"
_CORE_TOOLS = {_TRIAGE_GET, _TRIAGE_SET, _TRIAGE_ROUTE}
_DISPOSITION_TARGETS = {
    "auto_approval": {"gold_card_lane", "notification_only_lane"},
    "nurse_review": {"standard_um"},
    "md_review": {"standard_um"},
    "specialty_referral": {"specialty_program"},
    "delegation_transfer": {"delegate"},
    "vendor_transfer": {"external_vendor"},
}
_KNOWN_ROUTE_TARGETS = set().union(*_DISPOSITION_TARGETS.values())
_SLA_FIELDS = {
    "urgency_level": ("urgency_level", "urgency", "level_of_urgency"),
    "sla_deadline": ("deadline", "sla_deadline"),
    "sla_hours": ("hours", "sla_hours"),
    "sla_rule_source": ("rule_source", "sla_rule_source"),
}
_GOLD_CARD_FIELDS = ("gold_card_eligible", "eligible")


class PayerRoutingGuard:
    """Enforce observed case scope, route order, and one immutable triage commit."""

    def __init__(self, actor: Any, actual_names: dict[str, str]):
        self.actor = actor
        self.actual_names = dict(actual_names)
        actuals = set(self.actual_names.values())
        self._enabled = _CORE_TOOLS.issubset(actuals)
        self._sla_enabled = _CALCULATE_SLA in actuals
        self._gold_card_enabled = _CHECK_GOLD_CARD in actuals
        self._scope: Scope | None = None
        self._record_state = "unknown"  # unknown, absent, present, unknown_after_commit
        self._triage: dict[str, Any] | None = None
        self._absence_verified_after_route = False
        self._commit_attempted = False
        self._sla: dict[str, Any] | None = None
        self._gold_card_eligible: bool | None = None
        self._route_observed = False
        self._route_case_id: str | None = None
        self._route_target: str | None = None
        self._route_status: str | None = None

    def bind_scope(self, scope: Scope) -> None:
        if self._scope is not None and self._scope != scope:
            raise ValueError("payer routing guard is bound to one full case scope")
        self._scope = scope
        binder = getattr(self.actor, "bind_scope", None)
        if callable(binder):
            binder(scope)

    def list_tools(self):
        return self.actor.list_tools()

    def call(self, name: str, arguments: dict[str, Any]):
        actual = self.actual_names.get(name, name)
        if actual == _MD_DECISION:
            if self._scope is None or arguments.get('case_id') != self._scope.case:
                return self._refusal('md_decision_scope_mismatch', 'Submit only the active case MD decision.')
            # The public tool contract permits signed_off=False only for P2P.
            # The pinned service accepts some contrary combinations and makes
            # the resulting decision immutable. Reject before that write;
            # never set a sign-off or choose a clinical outcome on its behalf.
            if arguments.get('decision') != 'p2p_review' and arguments.get('signed_off') is not True:
                return self._refusal('md_signoff_contract_violation',
                    'No MD decision was dispatched. The public review.submit_md_case_decision contract permits signed_off=false only for p2p_review. '
                    'Review the proposed decision and explicitly supply signed_off=true when the assigned MD review is signed off. '
                    'This attests the current reviewer decision, not a missing treating-physician order or approval of the requested treatment. '
                    'Do not change the clinical outcome to bypass this requirement. Do not invent a historical signature.',
                    source='public_tool_contract:review.submit_md_case_decision:signed_off',
                    field='signed_off',decision=arguments.get('decision'))
        if actual == _QUEUE_DISCOVERY:
            return {"error": "queue_discovery_unavailable_after_case_binding",
                    "isError": True, "known_not_dispatched": True,
                    "instruction": "Use the already bound case scope; queue discovery is unavailable to the case worker."}
        if not self._enabled:
            return self.actor.call(name, arguments)

        if actual == _TRIAGE_ROUTE:
            refusal = self._route_precondition(arguments)
            if refusal is not None:
                return refusal
        elif actual == _TRIAGE_SET:
            refusal = self._commit_precondition(arguments)
            if refusal is not None:
                return refusal
        elif self._is_letter_commit(actual):
            if self._route_observed:
                refusal = self._letter_precondition()
                if refusal is not None:
                    return refusal

        if actual == _CALCULATE_SLA and self._active_case(arguments):
            self._sla = None
        elif actual == _CHECK_GOLD_CARD and self._active_case(arguments):
            self._gold_card_eligible = None

        result = self.actor.call(name, arguments)
        if not isinstance(result, dict) or result.get("isError") is True:
            return result
        if actual == _TRIAGE_GET:
            self._observe_triage_get(arguments, result)
            return self._with_annotation(result) if self._route_observed else result
        if actual == _TRIAGE_SET:
            self._commit_attempted = True
            self._observe_triage_set(arguments, result)
            return self._with_annotation(result) if self._route_observed else result
        if actual == _CALCULATE_SLA:
            self._observe_sla(arguments, result)
            return self._with_annotation(result) if self._route_observed else result
        if actual == _CHECK_GOLD_CARD:
            self._observe_gold_card(arguments, result)
            return self._with_annotation(result) if self._route_observed else result
        if actual == _TRIAGE_ROUTE:
            return self._observe_route(arguments, result)
        return result

    @staticmethod
    def _is_letter_commit(actual: str) -> bool:
        if not actual.startswith("payer_letter_center."):
            return False
        operation = set(actual.rsplit(".", 1)[-1].lower().split("_"))
        return bool(operation & {"generate", "generation", "deliver", "delivery", "send", "reissue"})

    def _route_precondition(self, arguments: dict[str, Any]) -> dict[str, Any] | None:
        if self._scope is None or arguments.get("case_id") != self._scope.case:
            return self._refusal("route_scope_mismatch", "Route only the active case using its observed case_id.")
        if self._route_observed:
            return self._refusal("route_already_observed", "The route already completed; do not dispatch it again.",
                                 route_consistency=self._consistency_annotation())
        return None

    def _commit_precondition(self, arguments: dict[str, Any]) -> dict[str, Any] | None:
        if self._scope is None or arguments.get("case_id") != self._scope.case:
            return self._refusal("triage_scope_mismatch", "Commit metadata only for the active case using its observed case_id.")
        if self._commit_attempted or self._record_state in {"present", "unknown_after_commit"}:
            return self._refusal("triage_record_immutable", "A triage record already exists or may have been committed; the API does not permit amendment.",
                                 record_state=self._record_state)
        if not self._route_observed or self._route_case_id != self._scope.case:
            return self._refusal("route_readback_required", "Read the active case route result before creating its one-time triage record.")
        if self._record_state != "absent" or not self._absence_verified_after_route:
            return self._refusal("triage_absence_unverified", "Read triage.get for this active case and require its explicit triage=null result before the first commit.",
                                 record_state=self._record_state)

        missing = []
        if self._sla_enabled and self._sla is None:
            missing.append("triage.calculate_sla result")
        if self._gold_card_enabled and self._gold_card_eligible is None:
            missing.append("triage.check_gold_card result")
        for field in _SLA_FIELDS if self._sla_enabled else ():
            if field not in arguments:
                missing.append(field)
        if self._gold_card_enabled and "gold_card_eligible" not in arguments:
            missing.append("gold_card_eligible")
        disposition = arguments.get("disposition")
        if not isinstance(disposition, str) or not disposition.strip():
            missing.append("disposition")
        if missing:
            return self._refusal("triage_metadata_observations_missing",
                                 "Read the active case SLA and gold-card results when those tools are available, then copy their actual values into the first triage record.",
                                 missing_fields=missing,
                                 observed_sla=deepcopy(self._sla),
                                 observed_gold_card_eligible=self._gold_card_eligible)

        mismatched = ([field for field, value in self._sla.items() if arguments.get(field) != value]
                      if self._sla_enabled and self._sla is not None else [])
        if (self._gold_card_enabled and "gold_card_eligible" in arguments
                and arguments.get("gold_card_eligible") is not self._gold_card_eligible):
            mismatched.append("gold_card_eligible")
        if mismatched:
            return self._refusal("triage_metadata_does_not_match_observations",
                                 "Use the observed current SLA and gold-card values in the immutable first triage record; recompute SLA after any urgency change.",
                                 mismatched_fields=sorted(set(mismatched)),
                                 observed_sla=deepcopy(self._sla),
                                 observed_gold_card_eligible=self._gold_card_eligible)

        compatibility = self._compare_disposition(arguments.get("disposition"), self._route_target)
        if compatibility == "mismatch":
            return self._refusal("triage_disposition_conflicts_with_route",
                                 "Do not commit a disposition that conflicts with the observed route. Resolve the governing case evidence before the one-time commit.",
                                 route_consistency=self._consistency_annotation(arguments.get("disposition")))
        return None

    def _letter_precondition(self) -> dict[str, Any] | None:
        if not self._route_observed:
            return None
        if self._record_state != "present":
            return self._refusal("triage_record_pending",
                                 "The route completed, but its immutable triage record has not yet been confirmed; create and read back the first record before letter work.",
                                 record_state=self._record_state,
                                 route_consistency=self._consistency_annotation())
        if self._route_status in {"mismatch", "unverified"}:
            return self._refusal("payer_route_consistency_blocked",
                                 "The existing triage record is immutable and conflicts with or cannot be matched to the observed route. Preserve the evidence and leave the letter unresolved.",
                                 route_consistency=self._consistency_annotation())
        metadata_status = self._metadata_status()
        if metadata_status != "match":
            return self._refusal("payer_triage_metadata_blocked",
                                 "The immutable triage record does not match current observed SLA and eligibility data. Preserve the evidence and leave dependent letter work unresolved.",
                                 route_consistency=self._consistency_annotation())
        return None

    def _observe_triage_get(self, arguments: dict[str, Any], result: dict[str, Any]) -> None:
        if not self._active_case(arguments) or "triage" not in self._structured(result):
            self._record_state = "unknown"
            self._triage = None
            self._absence_verified_after_route = False
            self._refresh_route_consistency()
            return
        record = self._structured(result)["triage"]
        if record is None:
            self._record_state = "absent"
            self._triage = None
            self._absence_verified_after_route = bool(
                self._route_observed and self._route_case_id == self._scope.case)
        elif isinstance(record, dict) and record.get("case_id") == self._scope.case:
            self._record_state = "present"
            self._triage = deepcopy(record)
            self._absence_verified_after_route = False
        else:
            self._record_state = "unknown"
            self._triage = None
            self._absence_verified_after_route = False
        self._refresh_route_consistency()

    def _observe_triage_set(self, arguments: dict[str, Any], result: dict[str, Any]) -> None:
        structured = self._structured(result)
        record = structured.get("triage")
        if self._active_case(arguments) and isinstance(record, dict) and record.get("case_id") == self._scope.case:
            self._record_state = "present"
            self._triage = deepcopy(record)
            self._absence_verified_after_route = False
        else:
            self._record_state = "unknown_after_commit"
            self._triage = None
            self._absence_verified_after_route = False
        self._refresh_route_consistency()

    def _observe_sla(self, arguments: dict[str, Any], result: dict[str, Any]) -> None:
        if not self._active_case(arguments):
            return
        fields = {name: aliases for name, aliases in _SLA_FIELDS.items()}
        record = self._find_observed_record(self._structured(result), fields)
        if record is None:
            self._sla = None
            return
        values = {field: self._first_value(record, aliases) for field, aliases in _SLA_FIELDS.items()}
        if any(value is None for value in values.values()):
            self._sla = None
            return
        if (not isinstance(values["urgency_level"], str) or not values["urgency_level"].strip()
                or not isinstance(values["sla_deadline"], str) or not values["sla_deadline"].strip()
                or isinstance(values["sla_hours"], bool)
                or not isinstance(values["sla_hours"], (int, float))
                or not isinstance(values["sla_rule_source"], str) or not values["sla_rule_source"].strip()):
            self._sla = None
            return
        self._sla = values

    def _observe_gold_card(self, arguments: dict[str, Any], result: dict[str, Any]) -> None:
        if not self._active_case(arguments):
            return
        record = self._find_observed_record(self._structured(result), {"gold_card_eligible": _GOLD_CARD_FIELDS})
        value = self._first_value(record, _GOLD_CARD_FIELDS) if record is not None else None
        self._gold_card_eligible = value if isinstance(value, bool) else None

    def _observe_route(self, arguments: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        if not self._active_case(arguments):
            return result
        self._route_observed = True
        self._absence_verified_after_route = False
        route_record = self._structured(result).get("route_record")
        if isinstance(route_record, dict):
            self._route_case_id = route_record.get("case_id")
            target = route_record.get("recommended_target")
            self._route_target = target if isinstance(target, str) else None
        else:
            self._route_case_id = None
            self._route_target = None
        self._refresh_route_consistency()
        return self._with_annotation(result)

    def _refresh_route_consistency(self) -> None:
        if not self._route_observed:
            self._route_status = None
        elif self._route_case_id != (self._scope.case if self._scope is not None else None):
            self._route_status = "unverified"
        elif not isinstance(self._route_target, str) or not self._route_target.strip():
            self._route_status = "unknown"
        elif self._route_target.strip().lower() not in _KNOWN_ROUTE_TARGETS:
            self._route_status = "unknown"
        elif self._record_state != "present" or self._triage is None:
            self._route_status = "pending_record"
        else:
            self._route_status = self._compare_disposition(self._triage.get("disposition"), self._route_target)

    def _metadata_status(self) -> str:
        if self._record_state != "present" or self._triage is None:
            return "pending"
        if self._sla_enabled:
            if self._sla is None:
                return "pending"
            if any(self._triage.get(field) != value for field, value in self._sla.items()):
                return "mismatch"
        if self._gold_card_enabled:
            if self._gold_card_eligible is None:
                return "pending"
            if self._triage.get("gold_card_eligible") is not self._gold_card_eligible:
                return "mismatch"
        return "match"

    def _overall_status(self) -> str:
        metadata_status = self._metadata_status()
        if self._route_status == "mismatch" or metadata_status == "mismatch":
            return "mismatch"
        if self._route_status in {"unverified", "pending_record"} or metadata_status == "pending":
            return "pending_record" if self._record_state != "present" else "unverified"
        if self._route_status == "unknown":
            return "unknown"
        return "match"

    @staticmethod
    def _compare_disposition(disposition: Any, target: Any) -> str:
        if not isinstance(target, str) or target.strip().lower() not in _KNOWN_ROUTE_TARGETS:
            return "unknown"
        if not isinstance(disposition, str):
            return "unknown"
        targets = _DISPOSITION_TARGETS.get(disposition.strip().lower())
        if targets is None:
            return "unknown"
        return "match" if target.strip().lower() in targets else "mismatch"

    def _consistency_annotation(self, proposed_disposition: Any = None) -> dict[str, Any]:
        disposition = proposed_disposition
        if disposition is None and self._triage is not None:
            disposition = self._triage.get("disposition")
        status = self._overall_status()
        if proposed_disposition is not None:
            status = self._compare_disposition(proposed_disposition, self._route_target)
        annotation: dict[str, Any] = {
            "status": status,
            "route_status": self._route_status or "unverified",
            "metadata_status": self._metadata_status(),
            "case_id": self._scope.case if self._scope is not None else None,
            "route_record_case_id": self._route_case_id,
            "saved_disposition": disposition,
            "actual_recommended_target": self._route_target,
            "basis": "comparison of observed triage metadata and observed route_record.recommended_target",
        }
        if status == "mismatch":
            annotation["detail"] = "The observed route target is outside the target set mapped from the recorded disposition."
        elif status == "unknown":
            annotation["detail"] = "No known mapping applies to the observed disposition or route target."
        elif status in {"unverified", "pending_record"}:
            annotation["detail"] = "A same-case committed triage record and route record are not both available for comparison."
        return annotation

    def _with_annotation(self, result: Any) -> Any:
        if not isinstance(result, dict):
            return result
        annotated = dict(result)
        annotated["_harness_consistency_annotation"] = self._consistency_annotation()
        return annotated

    def _refusal(self, error: str, instruction: str, **details: Any) -> dict[str, Any]:
        return {"error": error, "isError": True, "known_not_dispatched": True,
                "instruction": instruction, **details}

    def _active_case(self, arguments: dict[str, Any]) -> bool:
        return self._scope is not None and arguments.get("case_id") == self._scope.case

    @staticmethod
    def _structured(result: dict[str, Any]) -> dict[str, Any]:
        structured = result.get("structuredContent")
        return structured if isinstance(structured, dict) else {}

    @staticmethod
    def _first_value(record: dict[str, Any] | None, aliases: tuple[str, ...]) -> Any:
        if not isinstance(record, dict):
            return None
        for alias in aliases:
            if alias in record:
                return record[alias]
        return None

    def _find_observed_record(self, root: Any, fields: dict[str, tuple[str, ...]]) -> dict[str, Any] | None:
        if self._scope is None or not isinstance(root, (dict, list)):
            return None
        stack: list[tuple[Any, str | None]] = [(root, None)]
        seen = 0
        matches = []
        while stack and seen < 10000:
            node, inherited_case = stack.pop()
            seen += 1
            if isinstance(node, dict):
                observed_case = node.get("case_id", inherited_case)
                if observed_case is not None and observed_case != self._scope.case:
                    continue
                if all(self._first_value(node, aliases) is not None for aliases in fields.values()):
                    matches.append(node)
                stack.extend((value, observed_case) for value in node.values())
            elif isinstance(node, list):
                stack.extend((value, inherited_case) for value in node)
        signatures = {}
        for match in matches:
            signature = tuple((field, self._first_value(match, aliases)) for field, aliases in fields.items())
            signatures[repr(signature)] = match
        return next(iter(signatures.values())) if len(signatures) == 1 else None
