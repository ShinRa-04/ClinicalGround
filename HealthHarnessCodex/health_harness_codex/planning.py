"""Source-backed working notes and progress feedback, without clinical routing."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .models import IsolationError
from .working_set import business, canonical, pointer, missing_path_feedback, packed


SOURCE_REQUIRED = "working records require successful original evidence in this exact case"


def source(state, source_id):
    item = next((e for e in state.get("evidence", []) if e.get("id") == source_id), None)
    if item is None or item.get("scope") != state.get("scope") or item.get("outcome") != "success":
        raise IsolationError(_source_error(state, source_id, item))
    return item


def _source_error(state, source_id, item):
    """Name a mistyped ID and this case's closest returned IDs; never reveal foreign or failed sources."""
    if item is not None or not isinstance(source_id, str):
        return SOURCE_REQUIRED
    import difflib
    known = [e["id"] for e in state.get("evidence", [])
             if e.get("scope") == state.get("scope") and e.get("outcome") == "success" and isinstance(e.get("id"), str)]
    close = difflib.get_close_matches(source_id, known, n=3, cutoff=0.8)
    return (f"{SOURCE_REQUIRED}: cited id {source_id[:200]!r} was not returned in this case"
            + (f"; closest returned ids: {close}" if close else "")
            + ". Copy evidence IDs exactly as returned.")


def capture_reference(state, ref):
    item = source(state, ref["evidence_id"])
    path = ref.get("path", "")
    data = business(item["observed_result"])
    try:
        value = pointer(data, path)
    except (KeyError, TypeError):
        return {"evidence_id": item["id"], **missing_path_feedback(data, path)}
    if isinstance(value, str):
        if value=='' and 'start' not in ref and 'end' not in ref:
            return {'evidence_id':item['id'],'path':path,'start':0,'end':0,'text':'',
                    'full_field_chars':0,'partial':False,'field_status':'present','empty':True,
                    'source_text_sha256':hashlib.sha256(b'').hexdigest()}
        start, end = ref.get("start", 0), ref.get("end", min(len(value), 4000))
        if not 0 <= start < end <= len(value) or end - start > 4000:
            raise ValueError("working reference ranges must be valid original text slices of at most 4000 characters")
        captured = value[start:end]
        return {"evidence_id": item["id"], "path": path, "start": start, "end": end,
                "text": captured, "full_field_chars": len(value), "partial": start != 0 or end != len(value),
                "field_status": "present", "source_text_sha256": hashlib.sha256(value.encode()).hexdigest()}
    # Return type/shape rather than duplicating a whole clinical record.
    return {"evidence_id": item["id"], "path": path, "field_status": "present",
            "type": type(value).__name__, "item_count": len(value) if isinstance(value, (dict, list)) else None}


def record_blocker(state, args, specs):
    affected = list(dict.fromkeys(args.get('affected_obligation_ids',[])))
    known_work = {o['id'] for o in state.get('obligations',[])}
    if not set(affected) <= known_work:
        raise ValueError('affected_obligation_ids must identify existing work in this case')
    refs = [capture_reference(state, ref) for ref in args.get("sources", [])]
    kind = args["basis_kind"]
    facts = {"source_references": refs, "clinical_interpretation_verified": False}
    support = "unverified_hypothesis"
    if kind == "tool_field":
        from .assignment import resolve_tool
        spec=resolve_tool(specs,args.get('tool_name',''))
        from .schema import _expand_refs, tool_parameter_schema
        schema = _expand_refs(tool_parameter_schema(spec.input_schema))
        schema_path = args.get('schema_path','')
        try:
            schema = pointer(schema,schema_path)
        except (KeyError,TypeError):
            raise ValueError('schema_path must identify an actual object in the permitted tool schema') from None
        if not isinstance(schema,dict):
            raise ValueError('schema_path must identify a schema object')
        name = args.get("field_name", "")
        required = schema.get("required", [])
        declared = schema.get("properties", {})
        support = ("schema_required_field" if name in required else
                   "schema_optional_field" if name in declared else "field_not_declared_in_input_contract")
        facts.update(tool_name=spec.name, field_name=name, schema_path=schema_path, required_input_fields=required,
                     declared_input_fields=list(declared),
                     instruction="Input-schema requiredness is not a clinical-policy decision. "
                     "An optional input or absent output does not establish a mandatory prerequisite. "
                     "A separate policy-based requirement needs its own source reference.")
    elif kind == "policy":
        if not refs or not any("text" in ref for ref in refs):
            raise ValueError("policy prerequisites need an original retrieved text passage reference")
        from .policy_grounding import _policy_text_source
        for ref in args["sources"]:
            item = source(state, ref["evidence_id"])
            value = pointer(business(item["observed_result"]), ref.get("path", ""))
            if not _policy_text_source(item, ref.get("path", ""), value,
                                       allow_workflow=(state.get('completion_contract') or {}).get('domain')=='cm'):
                raise ValueError("policy prerequisite citations must identify retrieved policy text")
        support = "policy_passage_provenance_verified"
    elif kind == "observed_gap":
        if not refs:
            raise ValueError("an observed gap needs an original case observation reference")
        support = "observation_referenced_necessity_unverified"
    record = {"id": args["id"], "blocked_action": args["blocked_action"], "claim": args["claim"],
              "basis_kind": kind, "support": support, "facts": facts,
              "model_call": state.get("model_calls", 0), "status": args.get("status", "open")}
    if state.get('goal_planning_enabled'):
        record.update(goal_id='primary',affected_obligation_ids=affected,
            next_investigation=args.get('next_investigation',''),scope_of_claim='named_action_only')
    records = state.setdefault("prerequisite_records", [])
    records[:] = [x for x in records if x["id"] != record["id"]]
    records.append(record)
    return {**deepcopy(record), "creates_evidence": False,
            "instruction": "This records your prerequisite claim and verifies source/schema facts only. "
            "You retain responsibility for necessity and clinical interpretation; reconsider unsupported assumptions."}


def record_note(state, args):
    ids = list(dict.fromkeys(args.get("evidence_ids", [])))
    for source_id in ids:
        source(state, source_id)
    if args["kind"] == "finding" and not ids:
        raise ValueError("a finding requires original observed source IDs")
    note = {"id": args["id"], "kind": args["kind"], "summary": args["summary"],
            "evidence_ids": ids, "model_call": state.get("model_calls", 0),
            "status": args.get("status", "active"), "is_observed_fact": False}
    notes = state.setdefault("working_notes", [])
    notes[:] = [x for x in notes if x["id"] != note["id"]]
    notes.append(note)
    return {**note, "creates_evidence": False, "warning": "source-linked worker interpretation, not new clinical evidence"}


def capture_public_plan(state, content):
    try:
        value = json.loads(content)
    except (ValueError, TypeError):
        return
    if not isinstance(value, dict):
        return
    if not any(isinstance(value.get(k),str) and value[k].strip() for k in ('claim','next_step','patient_priority','unresolved_question')):
        return
    # Public operational summaries only, never private reasoning or new facts.
    blocker = value.get("blocker")
    state["current_plan"] = {"claim": str(value.get("claim", ""))[:1600],
        "model_call": state.get("model_calls", 0), "is_observed_fact": False}
    for key in ('next_step','patient_priority','unresolved_question'):
        if isinstance(value.get(key),str):state['current_plan'][key]=value[key][:500]
    known={e['id'] for e in state.get('evidence',[]) if e.get('scope')==state.get('scope') and e.get('outcome')=='success'}
    ids=value.get('evidence_ids',[])
    if isinstance(ids,list):state['current_plan']['evidence_ids']=[i for i in ids if isinstance(i,str) and i in known][:8]
    if isinstance(blocker, dict):
        state["current_plan"]["reported_blocker"] = {k: str(blocker[k])[:1200] for k in
            ("blocked_action", "missing_information", "why_required", "next_required_action") if k in blocker}
        state["current_plan"]["blocker_verification"] = "reported_only; see source-backed prerequisite_records"


def working_record_view(state,args):
    kind=args['kind'];key={'notes':'working_notes','blockers':'prerequisite_records','jobs':'helper_jobs','work':'obligations','decisions':'policy_decisions'}[kind]
    records=state.get(key,[])
    if args.get('id') is not None:records=[r for r in records if r['id']==args['id']]
    offset=args.get('offset',0);limit=args.get('limit',5);items=[];used=0
    for record in records[offset:offset+limit]:
        view={k:deepcopy(v) for k,v in record.items() if kind!='jobs' or k!='messages'}
        if kind=='blockers':
            for ref in view.get('facts',{}).get('source_references',[]):
                if 'text' in ref:
                    text=ref.pop('text');ref.update(text_excerpt=text[:300],text_partial=len(text)>300)
        size=len(packed(view))
        if items and used+size>12000:break
        items.append(view);used+=size
    next_offset=offset+len(items)
    return {'kind':kind,'items':items,'total':len(records),
        'next_offset':next_offset if next_offset<len(records) else None,'creates_evidence':False,
        'instruction':'Working notes, prerequisite claims and helper conclusions are interpretations, not new clinical facts. '
        'Original evidence IDs/pointers in citations retrieve full captured passages. Helper transcripts stay in the audit store.'}


def observe_progress(state, name, arguments, result, evidence_id, outcome):
    state.setdefault('last_information_progress_call',0)
    value=business(result)
    query_arguments=arguments
    if name.startswith('case.'):
        known={e.get('id') for e in state.get('evidence',[])}
        def normalize(v):
            if isinstance(v,str) and v in known:return '<original-source-reference>'
            if isinstance(v,dict):return {k:normalize(x) for k,x in v.items()}
            if isinstance(v,list):return [normalize(x) for x in v]
            return v
        value=normalize(value)
        query_arguments=normalize(arguments)
    digest = hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":"), default=str).encode()).hexdigest()
    key = canonical(name)
    latest = state.setdefault("operation_progress", {}).get(key, {})
    query_key=hashlib.sha256(packed({'tool':key,'arguments':query_arguments}).encode()).hexdigest()
    queries=state.setdefault('operation_query_progress',{})
    seen=queries.get(query_key,{})
    if seen.get('result_sha256')!=digest and latest.get('result_sha256')==digest:seen=latest
    unchanged = seen.get("result_sha256") == digest
    from .retrieval_progress import observe_retrieval
    retrieval = observe_retrieval(state, name, arguments, result, evidence_id, outcome)
    if retrieval is not None and not retrieval['new_source_information']:
        # Aggregate across query wording, size parameters, ordering and timing metadata.
        # Keep the original exact-query records too, for existing repeat behavior.
        seen = queries.get('retrieval:no_new_sources', seen)
        unchanged = True
    count = seen.get("unchanged_count", 0) + 1 if unchanged else 0
    current = {"tool": key, "result_sha256": digest, "latest_evidence_id": evidence_id,
               "first_matching_evidence_id": seen.get("first_matching_evidence_id", evidence_id) if unchanged else evidence_id,
               "unchanged_count": count, "model_call": state.get("model_calls", 0),
               "outcome":outcome,
               "arguments_sha256": hashlib.sha256(packed(arguments).encode()).hexdigest()}
    if retrieval is not None:
        current['progress_basis'] = 'returned_source_coverage'
        if not retrieval['new_source_information']:
            current['first_matching_evidence_id'] = retrieval['first_matching_evidence_id']
            queries['retrieval:no_new_sources'] = dict(current)
        else:
            queries.pop('retrieval:no_new_sources', None)
    state["operation_progress"][key] = current
    queries[query_key]=dict(current)
    if not unchanged:
        if outcome=='success':state["last_information_progress_call"] = state.get("model_calls", 0)
        return None
    return {**current, "new_source_information": False,
            "instruction": "This operation returned no new source documents/passages or the same business data as an earlier observation. "
            "A new evidence ID does not make the content new. Reuse known findings, inspect an unread field, "
            "test your prerequisite against its source, or revise your plan. You choose the next investigation; "
            "a fresh read remains permitted when an external change or intervening action justifies it."}


def progress_recovery(state):
    """One visible replanning nudge per stagnant information state, no hard stop."""
    if state.get("helper_active") or state.get("status") != "running":
        return False
    current = state.get("model_calls", 0)
    last = state.get("last_information_progress_call", current)
    operations=state.get('operation_query_progress',state.get('operation_progress',{}))
    repeats = [x for x in operations.values() if x.get("unchanged_count", 0) >= 2]
    if current - last < 3 or not repeats:
        return False
    fingerprint = hashlib.sha256(packed(sorted((k, v["result_sha256"]) for k, v in
        operations.items())).encode()).hexdigest()
    if state.get("last_progress_recovery_fingerprint") == fingerprint:
        return False
    state["last_progress_recovery_fingerprint"] = fingerprint
    event = {"after_model_call": current, "repeated_operations": [{k: x[k] for k in
             ("tool", "latest_evidence_id", "first_matching_evidence_id", "unchanged_count")} for x in repeats[-4:]]}
    state.setdefault("progress_recoveries", []).append(event)
    state["messages"].append({"role": "user", "content":
        "Progress review: recent actions have not changed the observed business information. "
        "Reassess your current plan and each claimed prerequisite against the actual tool contract or retrieved policy. "
        "Use case.record_blocker to distinguish a verified schema requirement, a source-backed policy interpretation "
        "and an unverified hypothesis. Missing optional data is not automatically a prerequisite. "
        "You may delegate a focused investigation when helpers are available. "
        "Distinguish a counterparty decision from a missing search result; apply the system capability rule. "
        "Revise the plan using evidence; do not replay completed writes or force a clinical outcome.\n" + packed(event)})
    return True
