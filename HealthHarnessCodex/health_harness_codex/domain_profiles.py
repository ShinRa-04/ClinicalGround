"""Domain configuration and public-actor case discovery for χ-Bench.

Domain selection is based on the dataset directory that contains a task, never
on a task filename or on patient data. Runtime discovery is restricted to the
selected actor's public tools and public task instruction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import time
from types import MappingProxyType
from typing import Any, Callable, Mapping
import unicodedata

from .intake_sources import find_intake_request_form


@dataclass(frozen=True, slots=True)
class DomainSpec:
    """Immutable runtime contract for one χ-Bench actor domain."""

    name: str
    engine_domain: str
    port: int
    workspace_role: str
    namespaces: tuple[str, ...]
    identity_source_tools: tuple[str, ...]
    discovery_only_tools: tuple[str, ...]
    case_scoped_tools: tuple[str, ...]
    patient_scoped_tools: tuple[str, ...]
    case_identity_tools: tuple[str, ...]
    identity_source: str
    readback_tool: str


_UM_IDENTITY_TOOLS = (
    "payer_intake_hub.get_intake_case",
    "triage.get",
    "triage.route_case",
    "review.get_nurse_review_data",
    "review.get_md_review_data",
    "determination.get_summary",
)

_PROFILES = {
    "pa_provider": DomainSpec(
        name="pa_provider",
        engine_domain="PA",
        port=8020,
        workspace_role="provider",
        namespaces=("chart", "cases", "inbox", "docs", "forms", "auth", "people", "p2p_session"),
        identity_source_tools=("chart.search_patients", "chart.get_patient_chart_by_patient", "cases.get_case"),
        discovery_only_tools=("chart.search_patients", "cases.list_cases"),
        case_scoped_tools=("inbox.list_messages",),
        patient_scoped_tools=("chart.get_patient_chart_by_patient",),
        case_identity_tools=("cases.create_from_order",),
        identity_source="actor_visible_public_patient_search_and_chart_readback",
        readback_tool="cases.get_case",
    ),
    "pa_um": DomainSpec(
        name="pa_um",
        engine_domain="UM",
        port=8100,
        workspace_role="payer",
        namespaces=("payer_intake_hub", "triage", "review", "determination", "p2p", "p2p_session",
                    "payer_letter_center"),
        identity_source_tools=_UM_IDENTITY_TOOLS,
        discovery_only_tools=("payer_intake_hub.list_intake_queue",),
        case_scoped_tools=(),
        patient_scoped_tools=(),
        case_identity_tools=(),
        identity_source="actor_visible_public_queue_and_readback",
        readback_tool="determination.get_summary",
    ),
    "cm": DomainSpec(
        name="cm",
        engine_domain="CM",
        port=8200,
        workspace_role="care-manager",
        namespaces=("cm_intake", "cm_chart", "cm_outreach", "cm_assessment", "cm_care_plan"),
        identity_source_tools=("cm_intake.get_referral", "cm_chart.get_chart_data"),
        discovery_only_tools=("cm_intake.list_referral_queue",),
        case_scoped_tools=(),
        patient_scoped_tools=(),
        case_identity_tools=(),
        identity_source="actor_visible_public_referral_queue_and_readback",
        readback_tool="cm_chart.get_chart_data",
    ),
}

DOMAIN_PROFILES: Mapping[str, DomainSpec] = MappingProxyType(_PROFILES)

_DATASET_MARKERS = {
    "prior_auth_provider": "pa_provider",
    "prior_auth_um": "pa_um",
    "care_management": "cm",
}


def _emit_discovery_progress(progress: Callable[..., Any] | None, event: str,
                             domain: str, **fields: Any) -> None:
    """Send only fixed phase labels and aggregate counts to an optional logger."""
    if not callable(progress):
        return
    try:
        progress(event, domain=domain, **fields)
    except Exception:
        # Observability must not change actor selection or workflow behavior.
        return

# The official chart.search_patients tool accepts limits from 1 through 5000.
# Keep discovery comfortably above the observed public roster while bounding
# the number of chart records that this bootstrap path can inspect.
_PROVIDER_PATIENT_ROSTER_LIMIT = 256


def domain_for_task(task_path: Path, override: str | None = None) -> DomainSpec:
    """Resolve the task's domain from its dataset ancestor or a validated override.

    A task path such as ``.../prior_auth_um/tasks/pa_t012`` is assigned by the
    ``prior_auth_um/tasks`` dataset boundary. Synthetic/legacy paths may use an
    explicit profile key override. No portion of the task name is interpreted
    as a domain or identity.
    """
    parts = tuple(part.casefold() for part in Path(task_path).parts)
    matches = {
        _DATASET_MARKERS[parts[index]]
        for index in range(len(parts) - 1)
        if parts[index] in _DATASET_MARKERS and parts[index + 1] == "tasks"
    }
    if len(matches) != 1:
        if matches:
            raise ValueError("task path contains multiple χ-Bench dataset boundaries")
        if override is None:
            raise ValueError("task path is outside a recognized χ-Bench dataset; supply an explicit domain override")
    if override is not None:
        if not isinstance(override, str) or override not in DOMAIN_PROFILES:
            raise ValueError("domain override must be one of: pa_provider, pa_um, cm")
        if matches and override != next(iter(matches)):
            raise ValueError("domain override conflicts with the task path's recognized dataset")
        return DOMAIN_PROFILES[override]
    return DOMAIN_PROFILES[matches.pop()]


def discover_domain_case(
    actor: Any,
    profile: DomainSpec,
    public_instruction: str,
    case_id: str | None = None,
    allow_case_subject_namespace: bool = False,
    legacy_um_discover: Callable[..., dict[str, Any]] | None = None,
    semantic_patient_matcher: Callable[[str, Mapping[str, Any]], bool] | None = None,
    intake_context_reader: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
    progress: Callable[..., Any] | None = None,
    excluded_patient_ids: tuple[str, ...] = (),
    excluded_case_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Discover the exact case using only public instruction and actor readbacks.

    UM reuses the existing public-queue discovery implementation through an
    injected callback to avoid a circular dependency. Provider discovery reads
    the public patient roster and locally checks bounded chart readbacks; only
    the uniquely selected patient identity and its fingerprint are returned.
    CM discovery selects a unique public referral and verifies it with a scoped
    readback. No bootstrap path performs a clinical write.
    """
    if not isinstance(public_instruction, str) or not public_instruction.strip():
        raise ValueError("public_instruction must be non-empty public task text")
    started = time.monotonic()
    _emit_discovery_progress(progress, "discovery_started", profile.name)
    if case_id is not None and case_id in excluded_case_ids:
        raise ValueError('explicit case identity was rejected; cannot silently override the assigned case')
    if profile.name == "pa_um":
        if legacy_um_discover is None:
            raise ValueError("pa_um discovery requires the existing standalone discovery callback")
        if case_id is not None:
            observed = legacy_um_discover(
                actor, case_id=case_id,
                allow_case_subject_namespace=allow_case_subject_namespace,
                task_instruction=public_instruction,
            )
            _validate_observed_case(observed)
            result = dict(observed)
            _emit_discovery_progress(progress, "discovery_finished", profile.name,
                                     selection_method=result.get("selection_method", "unknown"),
                                     elapsed_seconds=time.monotonic() - started)
            return result
        observed, method, matcher_invocations, intake_source_sha256 = _discover_um_case(
            actor, public_instruction, legacy_um_discover,
            allow_case_subject_namespace, semantic_patient_matcher,
            intake_context_reader, progress, excluded_patient_ids, excluded_case_ids,
        )
        if not isinstance(observed, dict):
            raise ValueError("actor discovery callback must return an observed identifier mapping")
        _validate_observed_case(observed)
        result = {key: observed[key] for key in
                  ("case_id", "patient_id", "intake_id", "organization_id", "principal_id")
                  if key in observed}
        result.update({
            "case_payload_sha256": observed["case_payload_sha256"],
            "selection_method": method,
            "semantic_matcher_invocations": matcher_invocations,
        })
        if intake_source_sha256:
            result["intake_source_sha256"] = intake_source_sha256
        _emit_discovery_progress(progress, "discovery_finished", profile.name,
                                 selection_method=method, elapsed_seconds=time.monotonic() - started)
        return result
    if profile.name == "pa_provider":
        if case_id is not None:
            raise ValueError("provider bootstrap does not accept a manual case ID; no actor case exists yet")
        result = _discover_provider_patient(actor, public_instruction, semantic_patient_matcher, progress, excluded_patient_ids)
        _emit_discovery_progress(progress, "discovery_finished", profile.name,
                                 selection_method=result.get("selection_method", "unknown"),
                                 elapsed_seconds=time.monotonic() - started)
        return result
    if profile.name == "cm":
        result = _discover_cm_referral(actor, public_instruction, case_id, progress, excluded_patient_ids, excluded_case_ids)
        _emit_discovery_progress(progress, "discovery_finished", profile.name,
                                 selection_method=result.get("selection_method", "unknown"),
                                 elapsed_seconds=time.monotonic() - started)
        return result
    raise ValueError(f"unknown domain profile {profile.name!r}")


def readback_domain_case(actor: Any, profile: DomainSpec, observed_ids: Mapping[str, Any]) -> dict[str, Any]:
    """Read public state and preserve the existing standalone readback envelope."""
    tool = profile.readback_tool
    arguments: dict[str, Any]
    observation_kind = "case_state"
    if profile.name == "pa_um":
        arguments = {"case_id": observed_ids["case_id"]}
        observation_kind = "determination_state"
    elif profile.name == "pa_provider":
        if observed_ids.get("case_namespace_kind") == "patient_subject_namespace":
            tool = "chart.get_patient_chart_by_patient"
            arguments = {"patient_id": observed_ids["patient_id"]}
            observation_kind = "patient_chart_state_not_case_finalization"
        else:
            arguments = {"case_id": observed_ids["case_id"]}
            observation_kind = "prior_authorization_case_state"
    elif profile.name == "cm":
        arguments = {"case_id": observed_ids["case_id"]}
        observation_kind = "care_management_case_chart_state"
    else:
        return {"status": "unavailable", "error_type": "ValueError", "reason": "unknown_domain_profile"}
    try:
        result = _call_named_tool(actor, tool, arguments)
    except Exception as exc:
        return {"status": "unavailable", "tool": tool, "error_type": type(exc).__name__,
                "reason": "actor_public_readback_failed"}
    return {"status": "observed", "tool": tool, "observation_kind": observation_kind, "result": result}


def _discover_provider_patient(actor: Any, instruction: str,
                               semantic_patient_matcher: Callable[[str, Mapping[str, Any]], bool] | None = None,
                               progress: Callable[..., Any] | None = None,
                               excluded_patient_ids: tuple[str, ...] = (),
                               ) -> dict[str, Any]:
    result = _call_named_tool(actor, "chart.search_patients", {"limit": _PROVIDER_PATIENT_ROSTER_LIMIT})
    payload = _tool_payload(result)
    patients = payload.get("items") if isinstance(payload, dict) else None
    total = payload.get("total") if isinstance(payload, dict) else None
    if not isinstance(patients, list) or not patients or len(patients) > _PROVIDER_PATIENT_ROSTER_LIMIT:
        raise ValueError("provider public patient search did not return a bounded, non-empty roster")
    if isinstance(total, bool) or not isinstance(total, int) or total < 1:
        raise ValueError("provider public patient search did not return a valid total count")
    if total > _PROVIDER_PATIENT_ROSTER_LIMIT or total != len(patients):
        raise ValueError("provider public patient roster is not complete within the bounded discovery limit")
    patient_ids = []
    for record in patients:
        if not isinstance(record, dict):
            raise ValueError("provider public patient roster contains an invalid record")
        patient_id = _required_string(record, "id")
        if len(patient_id) > 256 or any(ord(character) < 32 or ord(character) == 127 for character in patient_id):
            raise ValueError("provider public patient roster contains an invalid patient ID")
        patient_ids.append(patient_id)
    if len(set(patient_ids)) != len(patient_ids):
        raise ValueError("provider public patient roster contains duplicate patient IDs")
    patients=[p for p in patients if p['id'] not in excluded_patient_ids]
    if not patients:raise ValueError('no eligible patient remains after model-requested identity rejection')
    _emit_discovery_progress(progress, "discovery_roster_loaded", "pa_provider",
                             current=0, total=len(patients))

    anchor_text, _clinical_intro = _provider_instruction_anchor(instruction)
    instruction_tokens = _tokens(anchor_text)
    named = _matching_patient_names(patients, instruction_tokens)
    selected_chart = None
    semantic_matcher_invocations = 0
    if len(named) == 1 and _contains_phrase(instruction_tokens, _tokens(named[0].get("patient_name"))):
        selected = named[0]
        selection_method = "public_instruction_exact_patient_name"
        _emit_discovery_progress(progress, "discovery_chart_progress", "pa_provider",
                                 current=0, total=1)
        selected_chart = _call_named_tool(actor, "chart.get_patient_chart_by_patient",
                                          {"patient_id": _required_string(selected, "id")})
        _validate_provider_patient_chart(_tool_payload(selected_chart), _required_string(selected, "id"))
        _emit_discovery_progress(progress, "discovery_chart_progress", "pa_provider",
                                 current=1, total=1)
    else:
        # The chart content stays in this host-side bootstrap function. It is
        # never returned or logged; only a unique candidate's IDs and digest
        # leave this function.
        charts = []
        total_charts = len(patients)
        _emit_discovery_progress(progress, "discovery_chart_progress", "pa_provider",
                                 current=0, total=total_charts)
        for index, record in enumerate(patients, 1):
            patient_id = _required_string(record, "id")
            chart = _call_named_tool(actor, "chart.get_patient_chart_by_patient", {"patient_id": patient_id})
            _validate_provider_patient_chart(_tool_payload(chart), patient_id)
            charts.append((record, chart))
            if index % 10 == 0 or index == total_charts:
                _emit_discovery_progress(progress, "discovery_chart_progress", "pa_provider",
                                         current=index, total=total_charts)
        charts_by_id: dict[str, Any] = {}
        for record, chart in charts:
            charts_by_id[_required_string(record, "id")] = _tool_payload(chart)
        selected, selection_method, semantic_matcher_invocations = _select_provider_patient(
            patients, charts_by_id, instruction, semantic_patient_matcher
        )
        selected_chart = next(chart for record, chart in charts if record.get("id") == selected.get("id"))
        # If duplicate roster entries have the same name, chart uniqueness may
        # resolve them only when the selected patient's clinical cue is unique.
        if len(named) > 1 and not _provider_chart_selection_respects_names(
                patients, instruction_tokens, selected):
            raise ValueError("provider patient name and chart cue did not identify the same roster entry")

    patient_id = _required_string(selected, "id")
    observed = {
        "patient_id": patient_id,
        "case_id": f"case-subject:{patient_id}",
        "case_namespace_kind": "patient_subject_namespace",
        "case_payload_sha256": _fingerprint({"patient_roster_record": selected, "selected_chart": selected_chart}),
        "selection_method": selection_method,
        "semantic_matcher_invocations": semantic_matcher_invocations,
    }
    if selection_method in {'public_instruction_isolated_semantic_match','public_instruction_investigated_match'}:
        observed['identity_comparison_context_sha256'] = _fingerprint(_tool_payload(selected_chart))
    return observed


def _discover_um_case(
    actor: Any,
    instruction: str,
    legacy_um_discover: Callable[..., dict[str, Any]],
    allow_case_subject_namespace: bool,
    semantic_patient_matcher: Callable[[str, Mapping[str, Any]], bool] | None,
    intake_context_reader: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None,
    progress: Callable[..., Any] | None = None,
    excluded_patient_ids: tuple[str, ...] = (),
    excluded_case_ids: tuple[str, ...] = (),
) -> tuple[dict[str, Any], str, int, str | None]:
    """Select from public UM queue evidence, then let legacy code read identity."""
    queue_result = _call_named_tool(actor, "payer_intake_hub.list_intake_queue", {})
    records = _um_queue_records(_tool_payload(queue_result))
    records=[r for r in records if r.get('patient_id') not in excluded_patient_ids and r.get('case_id') not in excluded_case_ids]
    if not records or len(records) > 25:
        raise ValueError("UM public intake queue must contain between 1 and 25 observed cases")
    _emit_discovery_progress(progress, "discovery_roster_loaded", "pa_um",
                             current=0, total=len(records))

    exact = _select_um_by_provider_procedure(records, instruction)
    selected_record: dict[str, Any] | None = None
    selection_method: str | None = None
    matcher_invocations = 0
    source_hash: str | None = None
    if len(records) == 1:
        selected_record = records[0]
        selection_method = "single_actor_queue_case"
    elif len(exact) == 1:
        selected_record = exact[0]
        selection_method = "public_instruction_provider_procedure"
    else:
        # Procedure text narrows plausible cases when it is explicit in the
        # task. A missing/ambiguous queue anchor leaves the full bounded queue.
        procedure_candidates = _select_um_by_procedure(records, instruction)
        plausible = procedure_candidates or records
        if intake_context_reader is None:
            raise ValueError("UM public selection needs the bounded actor intake-form reader")
        contexts: list[tuple[dict[str, Any], str, Mapping[str, Any]]] = []
        _emit_discovery_progress(progress, "discovery_source_progress", "pa_um",
                                 current=0, total=len(plausible))
        for index, record in enumerate(plausible, 1):
            case_id = _required_string(record, "case_id")
            documents = _call_named_tool(actor, "payer_intake_hub.list_documents", {"case_id": case_id})
            metadata = find_intake_request_form(documents, case_id)
            context = intake_context_reader(case_id, metadata)
            if not isinstance(context, Mapping):
                raise ValueError("UM intake reader must return one bounded candidate context")
            text = context.get("text")
            digest = context.get("source_sha256")
            truncated = context.get("truncated", False)
            if not isinstance(text, str) or len(text) > 20_000:
                raise ValueError("UM intake context text is absent or exceeds its configured bound")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("UM intake context source hash is invalid")
            if not isinstance(truncated, bool):
                raise ValueError("UM intake context truncation marker must be boolean")
            # The semantic callback sees one case only. Do not pass its other
            # actor-visible candidates, document URLs, or non-source metadata.
            candidate_context = {"queue_record": dict(record), "intake_form_text": text,
                                 "intake_form_truncated": truncated}
            contexts.append((record, digest, candidate_context))
            if index % 10 == 0 or index == len(plausible):
                _emit_discovery_progress(progress, "discovery_source_progress", "pa_um",
                                         current=index, total=len(plausible))

        if semantic_patient_matcher is None:
            raise ValueError("UM public case did not have one deterministic provider/procedure anchor")
        positives: list[tuple[dict[str, Any], str]] = []
        for record, digest, candidate_context in contexts:
            matched = semantic_patient_matcher(instruction, candidate_context)
            matcher_invocations += 1
            if not isinstance(matched, bool):
                raise ValueError("UM semantic matcher must return a boolean for each isolated case")
            if matched:
                positives.append((record, digest))
        if len(positives) != 1:
            raise ValueError(
                "isolated UM semantic matching did not uniquely identify one actor-visible case "
                f"({len(positives)} positive candidates)"
            )
        selected_record, source_hash = positives[0]
        selection_method = "public_instruction_isolated_semantic_match"

    assert selected_record is not None and selection_method is not None
    selected_case_id = _required_string(selected_record, "case_id")
    observed = legacy_um_discover(
        actor,
        case_id=selected_case_id,
        allow_case_subject_namespace=allow_case_subject_namespace,
        task_instruction=instruction,
    )
    if not isinstance(observed, dict):
        raise ValueError("actor discovery callback must return an observed identifier mapping")
    if observed.get("case_id") != selected_case_id:
        raise ValueError("legacy UM actor readback disagreed with the selected public queue case")
    observed["selection_method"] = selection_method
    observed["semantic_matcher_invocations"] = matcher_invocations
    return observed, selection_method, matcher_invocations, source_hash


def _um_queue_records(payload: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            if _nonempty_string(value.get("case_id")):
                rows.append(dict(value))
                return
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(payload)
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        case_id = _nonempty_string(row.get("case_id"))
        if case_id and case_id not in seen:
            seen.add(case_id)
            result.append(row)
    return result


def _select_um_by_provider_procedure(records: list[dict[str, Any]], instruction: str) -> list[dict[str, Any]]:
    instruction_tokens = _normalized_words(instruction)
    matches = []
    for record in records:
        provider = record.get("requesting_provider")
        provider_name = provider.get("provider_name") if isinstance(provider, Mapping) else provider
        provider_tokens = _normalized_words(provider_name) if isinstance(provider_name, str) else []
        if len(provider_tokens) < 2 or not _contains_word_phrase(instruction_tokens, provider_tokens):
            continue
        if any(_um_procedure_matches(_normalized_words(name), instruction_tokens)
               for name in _um_procedure_names(record)):
            matches.append(record)
    return matches


def _select_um_by_procedure(records: list[dict[str, Any]], instruction: str) -> list[dict[str, Any]]:
    instruction_tokens = _normalized_words(instruction)
    return [record for record in records
            if any(_um_procedure_matches(_normalized_words(name), instruction_tokens)
                   for name in _um_procedure_names(record))]


def _um_procedure_names(record: Mapping[str, Any]) -> list[str]:
    output: list[str] = []
    items = record.get("line_items")
    if not isinstance(items, list):
        return output
    for item in items:
        procedures = item.get("procedures") if isinstance(item, Mapping) else None
        if not isinstance(procedures, list):
            continue
        output.extend(proc["name"] for proc in procedures
                      if isinstance(proc, Mapping) and isinstance(proc.get("name"), str)
                      and proc["name"].strip())
    return output


def _normalized_words(value: str) -> list[str]:
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", value).casefold(), flags=re.UNICODE)


def _contains_word_phrase(haystack: list[str], phrase: list[str]) -> bool:
    if not phrase or len(phrase) > len(haystack):
        return False
    return any(haystack[index:index + len(phrase)] == phrase
               for index in range(len(haystack) - len(phrase) + 1))


def _um_procedure_matches(procedure_tokens: list[str], instruction_tokens: list[str]) -> bool:
    return (len(procedure_tokens) >= 3 and
            (_contains_word_phrase(instruction_tokens, procedure_tokens)
             or _contains_word_phrase(instruction_tokens, procedure_tokens[:6])))


def _discover_cm_referral(actor: Any, instruction: str, case_id: str | None,
                          progress: Callable[..., Any] | None = None,
                          excluded_patient_ids: tuple[str, ...] = (),
                          excluded_case_ids: tuple[str, ...] = ()) -> dict[str, Any]:
    queue_result = _call_named_tool(actor, "cm_intake.list_referral_queue", {})
    payload = _tool_payload(queue_result)
    records = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError("CM public referral queue did not return a list of observed referrals")
    records = [record for record in records if isinstance(record, dict)
               and record.get('patient_id') not in excluded_patient_ids and record.get('case_id') not in excluded_case_ids
               and _nonempty_string(record.get("case_id"))
               and _nonempty_string(record.get("referral_id"))]
    _emit_discovery_progress(progress, "discovery_roster_loaded", "cm",
                             current=0, total=len(records))
    selected = select_cm_referral(records, instruction, case_id=case_id)
    method = "explicit_actor_observed_case_id" if case_id is not None else "public_instruction_exact_referral_cue"
    readback = _call_named_tool(actor, "cm_intake.get_referral", {"referral_id": selected["referral_id"]})
    actual = _find_record_with_identity(_tool_payload(readback), selected["case_id"], selected["referral_id"])
    if actual is None:
        raise ValueError("CM referral readback did not match the selected public queue referral")
    queue_patient_id = _nonempty_string(selected.get("patient_id"))
    actual_patient_id = _nonempty_string(actual.get("patient_id"))
    if queue_patient_id and actual_patient_id and queue_patient_id != actual_patient_id:
        raise ValueError("CM referral readback patient identity disagreed with the selected public queue referral")
    patient_id = actual_patient_id or queue_patient_id
    if not patient_id:
        raise ValueError("CM selected referral did not provide an actor-observed patient ID")
    return {
        "case_id": selected["case_id"],
        "patient_id": patient_id,
        "referral_id": selected["referral_id"],
        "case_payload_sha256": _fingerprint({"queue_record": selected, "referral_readback": readback}),
        "selection_method": method,
    }


def _call_named_tool(actor: Any, actual_name: str, arguments: dict[str, Any]) -> Any:
    aliases = getattr(actor, "_actual_names", None)
    if not isinstance(aliases, Mapping):
        raise ValueError("actor client does not expose its observed actual-tool mapping")
    found = [alias for alias, actual in aliases.items() if actual == actual_name]
    if not found:
        list_tools = getattr(actor, "list_tools", None)
        if not callable(list_tools):
            raise ValueError("actor public catalogue is not initialized and cannot be loaded")
        list_tools()
        aliases = getattr(actor, "_actual_names", None)
        if not isinstance(aliases, Mapping):
            raise ValueError("actor client did not expose its observed actual-tool mapping after catalogue load")
        found = [alias for alias, actual in aliases.items() if actual == actual_name]
    if len(found) != 1:
        raise ValueError(f"actor public catalogue must expose exactly one {actual_name} tool")
    result = actor.call(found[0], arguments)
    if isinstance(result, dict) and (result.get("isError") or result.get("error")):
        raise ValueError(f"actor public read failed for {actual_name}")
    return result


def _tool_payload(result: Any) -> Any:
    if not isinstance(result, dict):
        raise ValueError("actor public read did not return a structured response")
    if result.get("isError"):
        raise ValueError("actor public read returned an MCP error")
    payload = result.get("structuredContent")
    if payload is None:
        for item in result.get("content", []):
            if isinstance(item, dict) and isinstance(item.get("parsed_json"), (dict, list)):
                payload = item["parsed_json"]
                break
    if payload is None:
        raise ValueError("actor public read did not include structured content")
    return payload


def _validate_observed_case(observed: Mapping[str, Any]) -> None:
    required = ("case_id", "case_payload_sha256", "selection_method")
    if any(not isinstance(observed.get(key), str) or not observed[key] for key in required):
        raise ValueError("actor discovery callback omitted required observed case metadata")


def _validate_provider_patient_chart(chart: Any, expected_patient_id: str) -> None:
    patient = chart.get("patient") if isinstance(chart, Mapping) else None
    observed_patient_id = _nonempty_string(patient.get("id")) if isinstance(patient, Mapping) else None
    if observed_patient_id != expected_patient_id:
        raise ValueError("provider chart readback patient identity disagreed with the actor-visible roster")


def _match_public_cues(records: list[dict[str, Any]], instruction: str) -> list[dict[str, Any]]:
    instruction_tokens = _tokens(instruction)
    name_matches = _matching_referral_names(records, instruction_tokens)
    if len(name_matches) == 1:
        return name_matches
    cue_matches: list[dict[str, Any]] = []
    for record in records:
        strings = [record.get(key) for key in ("reason", "notes", "source")]
        strings.extend(record.get(key) for key in ("diagnosis_codes", "utilization_flags")
                       if isinstance(record.get(key), list) for _ in (0,))
        flat_strings = [item for value in strings for item in (value if isinstance(value, list) else [value])]
        if any(_contains_phrase(instruction_tokens, _tokens(value)) for value in flat_strings):
            cue_matches.append(record)
    # Names and exact textual cues are evidence; combining them must still
    # identify one referral. It never falls back to queue order or similarity.
    if len(name_matches) > 1:
        cue_matches = [record for record in cue_matches if record in name_matches]
    return cue_matches


def select_cm_referral(records: list[dict[str, Any]], instruction: str,
                       case_id: str | None = None) -> dict[str, Any]:
    """Purely select one public referral record by exact public cue evidence."""
    valid = [record for record in records if isinstance(record, dict)
             and _nonempty_string(record.get("case_id"))
             and _nonempty_string(record.get("referral_id"))]
    if case_id is not None:
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("explicit case_id must be an actor-observed identifier")
        matches = [record for record in valid if record.get("case_id") == case_id]
    else:
        matches = _match_public_cues(valid, instruction)
    if len(matches) != 1:
        raise ValueError(f"CM public instruction did not uniquely identify a referral ({len(matches)} exact matches)")
    return matches[0]


def select_provider_patient(patient_records: list[dict[str, Any]], charts_by_id: Mapping[str, Any],
                            instruction: str,
                            semantic_patient_matcher: Callable[[str, Mapping[str, Any]], bool] | None = None
                            ) -> dict[str, Any]:
    """Purely select one roster patient using exact public intake and chart text."""
    return _select_provider_patient(patient_records, charts_by_id, instruction, semantic_patient_matcher)[0]


def _select_provider_patient(patient_records: list[dict[str, Any]], charts_by_id: Mapping[str, Any],
                             instruction: str,
                             semantic_patient_matcher: Callable[[str, Mapping[str, Any]], bool] | None = None
                             ) -> tuple[dict[str, Any], str, int]:
    # The public task's first intake heading and clinical narrative are its
    # subject anchor; generic workspace and policy instructions are excluded.
    anchor_text, clinical_intro = _provider_instruction_anchor(instruction)
    tokens = _tokens(anchor_text)
    named = _matching_patient_names(patient_records, tokens)
    if len(named) == 1 and _contains_phrase(tokens, _tokens(named[0].get("patient_name"))):
        return named[0], "public_instruction_exact_patient_name", 0
    # Diagnosis labels, surnames and longest shared phrases are candidate cues,
    # never patient identity. Evaluate every roster candidate independently:
    # a paraphrased correct chart must not lose to a distractor with exact wording.
    if semantic_patient_matcher is None:
        raise ValueError("provider identity requires an explicit full patient name or isolated source-backed clinical comparison; no exact actor-visible chart cue establishes identity")
    candidates = []
    for record in patient_records:
        chart = charts_by_id.get(_required_string(record,'id'))
        if not isinstance(chart,Mapping):
            raise ValueError("bounded actor-visible chart index is missing a roster patient")
        if _provider_demographic_compatible(record,chart,clinical_intro):
            candidates.append(record)
    capacity = getattr(semantic_patient_matcher,'max_candidate_calls',None)
    if isinstance(capacity,int) and len(candidates) > capacity:
        raise ValueError("identity candidate comparisons exceed the reserved setup budget; no model calls or case writes dispatched")
    positive = []
    for record in candidates:
        patient_id = _required_string(record, "id")
        chart = charts_by_id.get(patient_id)
        if not isinstance(chart, Mapping):
            raise ValueError("bounded actor-visible chart index is missing a roster patient")
        matched = semantic_patient_matcher(instruction, chart)
        if not isinstance(matched, bool):
            raise ValueError("semantic patient matcher must return a boolean for each isolated candidate")
        if matched:
            positive.append(record)
    investigated=False
    if len(positive)>1 and callable(getattr(semantic_patient_matcher,'resolve_ambiguity',None)):
        choice=semantic_patient_matcher.resolve_ambiguity(instruction,
            [charts_by_id[_required_string(record,'id')] for record in positive])
        if choice is not None:
            if type(choice) is not int or not 0<=choice<len(positive):
                raise ValueError('identity investigation returned an unavailable candidate')
            positive=[positive[choice]];investigated=True
    if len(positive) != 1:
        raise ValueError(f"isolated semantic matching did not uniquely identify one actor-visible patient ({len(positive)} positive candidates)")
    selected = positive[0]
    if not _provider_chart_selection_respects_names(patient_records, tokens, selected):
        raise ValueError("provider patient name and chart cue did not identify the same roster entry")
    return selected, ("public_instruction_investigated_match" if investigated else
                      "public_instruction_isolated_semantic_match"), len(candidates)


def _provider_demographic_compatible(record, chart, clinical_intro):
    """Exclude known contradictions, retaining unknowns and age/date ambiguity."""
    age,sex = _age_sex_from_public_intro(clinical_intro)
    patient = chart.get('patient') or {}
    value = str(patient.get('sex',record.get('sex',''))).casefold()
    observed_sex = 'male' if value in {'m','male','man'} else 'female' if value in {'f','female','woman'} else None
    if sex is not None and observed_sex is not None and sex != observed_sex: return False
    dates = [row.get(key) for collection,key in (('encounters','occurred_at'),('summaries','signed_at'))
             for row in (chart.get(collection) or []) if isinstance(row,dict) and row.get(key)]
    try:
        birth = date.fromisoformat(str(patient.get('dob',record.get('dob',''))))
        references = [datetime.fromisoformat(str(value).replace('Z','+00:00')).date() for value in dates]
    except (ValueError,TypeError):
        return True
    if age is not None and references:
        ages = [ref.year-birth.year-((ref.month,ref.day)<(birth.month,birth.day)) for ref in references]
        # A narrative may precede/follow a birthday or reference a different
        # dated encounter. Never use the host clock as the clinical date.
        if age < min(ages)-1 or age > max(ages)+1: return False
    return True


def _provider_chart_selection_respects_names(
    patient_records: list[dict[str, Any]], tokens: tuple[str, ...], selected: dict[str, Any]
) -> bool:
    """Treat full patient names as identity constraints, surname-only hits as cues.

    A task can mention a clinician or another person whose surname happens to
    match several roster entries. Such weak matches should not veto a unique
    exact chart phrase. A full patient name remains a hard constraint: chart
    evidence that points elsewhere is ambiguous and must fail closed.
    """
    full_names = [record for record in patient_records if isinstance(record, dict)
                  and _contains_phrase(tokens, _tokens(record.get("patient_name")))]
    return not full_names or selected in full_names


def _matching_patient_names(patient_records: list[dict[str, Any]], tokens: tuple[str, ...]) -> list[dict[str, Any]]:
    return [record for record in patient_records if isinstance(record, dict)
            and (_contains_phrase(tokens, _tokens(record.get("patient_name")))
                 or _contains_single_name_token(tokens, record.get("last_name")))]


def _matching_referral_names(records: list[dict[str, Any]], tokens: tuple[str, ...]) -> list[dict[str, Any]]:
    return [record for record in records if isinstance(record, dict)
            and (_contains_phrase(tokens, _tokens(record.get("patient_name")))
                 or _contains_single_name_token(tokens, record.get("patient_last_name")))]


def _contains_single_name_token(haystack: tuple[str, ...], value: Any) -> bool:
    token = _tokens(value)
    return len(token) == 1 and token[0] in haystack


def _find_record_with_identity(payload: Any, case_id: str, referral_id: str) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        if payload.get("case_id") == case_id and payload.get("referral_id") == referral_id:
            return payload
        for value in payload.values():
            found = _find_record_with_identity(value, case_id, referral_id)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_record_with_identity(value, case_id, referral_id)
            if found is not None:
                return found
    return None


def _clinical_strings(payload: Any, path: tuple[str, ...] = ()):
    clinical_keys = {"condition", "diagnosis", "assessment", "reason", "problem", "complaint",
                     "description", "impression", "clinical", "note", "text", "content", "body",
                     "encounter", "observation", "procedure", "summary", "title", "display"}
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_path = path + (str(key).casefold(),)
            if isinstance(value, str) and any(any(token in part for token in clinical_keys) for part in next_path):
                yield value
            else:
                yield from _clinical_strings(value, next_path)
    elif isinstance(payload, list):
        for value in payload:
            yield from _clinical_strings(value, path)


def _instruction_chart_cues(instruction_tokens: tuple[str, ...], values) -> set[tuple[str, ...]]:
    stop = {"the", "and", "for", "with", "from", "that", "this", "into", "patient", "history",
            "review", "complete", "prepare", "request", "clinical", "chart", "please", "their",
            "about", "care", "management", "authorization"}
    instruction_phrases = {
        instruction_tokens[start:start + size]
        for size in range(3, min(12, len(instruction_tokens)) + 1)
        for start in range(len(instruction_tokens) - size + 1)
        if any(token not in stop for token in instruction_tokens[start:start + size])
    }
    cues: set[tuple[str, ...]] = set()
    for value in values:
        tokens = _tokens(value)
        for size in range(3, min(12, len(tokens)) + 1):
            for start in range(len(tokens) - size + 1):
                phrase = tokens[start:start + size]
                if phrase in instruction_phrases:
                    cues.add(phrase)
    return cues


def _provider_instruction_anchor(instruction: str) -> tuple[str, str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", instruction) if part.strip()]
    if not paragraphs:
        return instruction, instruction
    title = paragraphs[0]
    clinical_intro = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]
    return f"{title}\n{clinical_intro}", clinical_intro


def _age_sex_from_public_intro(clinical_intro: str) -> tuple[int | None, str | None]:
    age_matches = {int(value) for value in re.findall(
        r"\b(\d{1,3})\s*[- ]?\s*years?\s*[- ]?\s*old\b", clinical_intro, flags=re.IGNORECASE
    )}
    sexes = {"male" if value.casefold() in {"male", "man", "boy"} else "female"
             for value in re.findall(r"\b(male|female|man|woman|boy|girl)\b", clinical_intro, flags=re.IGNORECASE)}
    return (next(iter(age_matches)) if len(age_matches) == 1 else None,
            next(iter(sexes)) if len(sexes) == 1 else None)


def _chart_demographics_match(patient_record: Mapping[str, Any], chart: Any,
                              age: int | None, sex: str | None) -> bool:
    patient = chart.get("patient") if isinstance(chart, dict) else None
    if not isinstance(patient, dict):
        return False
    observed_sex = str(patient.get("sex", patient_record.get("sex", ""))).casefold()
    observed_sex = "male" if observed_sex.startswith("m") else "female" if observed_sex.startswith("f") else observed_sex
    if sex is not None and observed_sex != sex:
        return False
    if age is None:
        return sex is not None
    try:
        birth_date = date.fromisoformat(str(patient.get("dob", patient_record.get("dob", ""))))
    except ValueError:
        return False
    observed_dates = []
    for collection, key in (("encounters", "occurred_at"), ("summaries", "signed_at")):
        rows = chart.get(collection, []) if isinstance(chart, dict) else []
        if not isinstance(rows, list):
            continue
        for row in rows:
            value = row.get(key) if isinstance(row, dict) else None
            if isinstance(value, str) and value:
                try:
                    observed_dates.append(datetime.fromisoformat(value.replace("Z", "+00:00")).date())
                except ValueError:
                    continue
    if not observed_dates:
        return False
    reference_date = max(observed_dates)
    age_at_reference = reference_date.year - birth_date.year - (
        (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day)
    )
    if age is None and sex is None:
        return False
    return (sex is None or observed_sex == sex) and (age is None or age_at_reference == age)


def _tokens(value: Any) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return tuple(re.findall(r"[\w]+", normalized, flags=re.UNICODE))


def _contains_phrase(haystack: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    if len(needle) < 2 or len(needle) > len(haystack):
        return False
    return any(haystack[index:index + len(needle)] == needle
               for index in range(len(haystack) - len(needle) + 1))


def _required_string(record: Mapping[str, Any], key: str) -> str:
    value = _nonempty_string(record.get(key))
    if value is None:
        raise ValueError(f"actor public record omitted required {key}")
    return value


def _nonempty_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

