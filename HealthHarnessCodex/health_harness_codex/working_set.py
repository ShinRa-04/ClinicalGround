"""Deterministic, source-linked working views; never changes durable evidence."""
from __future__ import annotations

from copy import deepcopy
import json
import re
from typing import Any


def packed(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def clinical(state):
    return isinstance(state.get("completion_contract"), dict) and state["completion_contract"].get("domain") in {"pa_provider", "pa_um", "cm"}


def canonical(name: str) -> str:
    if name.startswith("mcp_"):
        name = re.sub(r"_[a-f0-9]{12}$", "", name[4:])
        for namespace in ("payer_intake_hub", "payer_letter_center", "payer_policy_library", "p2p_session", "cm_care_plan",
                          "cm_assessment", "cm_outreach", "cm_intake", "cm_chart"):
            if name.startswith(namespace + "_"):
                return namespace + "." + name[len(namespace) + 1:]
        return name.replace("_", ".", 1)
    return name


def business(result):
    """Prefer structured business data, preserving raw source elsewhere."""
    if isinstance(result, dict) and isinstance(result.get("structuredContent"), (dict, list)):
        return result["structuredContent"]
    return result


def normalize_mcp(value):
    if not isinstance(value, dict) or "structuredContent" not in value:
        return value
    parts = value.get("content")
    if not isinstance(parts, list) or len(parts) != 1 or not isinstance(parts[0], dict):
        return value
    try:
        same = parts[0].get("type") == "text" and json.dumps(json.loads(parts[0]["text"]),sort_keys=True) == json.dumps(value["structuredContent"],sort_keys=True)
    except (KeyError, ValueError, TypeError):
        return value
    if not same:
        return value
    return {k: v for k, v in value.items() if k != "content"}


def normalize_message(message):
    if message.get("role") != "tool" or not isinstance(message.get("content"), str):
        return message
    try:
        payload = json.loads(message["content"])
    except ValueError:
        return message
    if not isinstance(payload, dict):
        return message
    source = payload.get("observed_result", payload)
    normalized = normalize_mcp(source)
    if normalized == source:
        return message
    payload = {**payload, "observed_result": normalized} if "observed_result" in payload else normalized
    return {**message, "content": packed(payload)}


def pointer(value, path):
    if path == "":
        return value
    if not isinstance(path, str) or not path.startswith("/") or len(path) > 1000:
        raise ValueError("path must be a JSON pointer relative to the business result")
    for part in path[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict): value = value[part]
        elif isinstance(value, list) and part.isdigit():
            try: value = value[int(part)]
            except IndexError: raise KeyError("source index does not exist") from None
        else: raise KeyError("source pointer does not exist")
    return value


_PRIORITY = ("case", "case_id", "status", "patient", "patient_id", "form_validation", "workflow_state",
             "next_actions", "readiness", "submission_packets", "determination", "case_decision",
             "case_recommendation", "route_record", "service_request", "bundle_document", "included_document_ids",
             "conditions", "medications", "observations", "allergies", "forms", "questionnaire",
             "missing_information", "missing_required_fields", "items", "text", "pages", "summary")


def preview(value, limit=2200):
    if len(packed(value)) <= limit:
        return {"value": value, "partial": False}
    if isinstance(value, dict):
        selected = {}; omitted = []
        keys = sorted(value, key=lambda k: (_PRIORITY.index(k) if k in _PRIORITY else len(_PRIORITY), k))
        for key in keys:
            child = value[key]
            path = "/" + str(key).replace("~", "~0").replace("/", "~1")
            if len(packed({**selected, key: child})) <= limit:
                selected[key] = child
            else:
                omitted.append({"path": path, "type": type(child).__name__, "chars": len(packed(child))})
        return {"selected_fields": selected, "omitted_fields": omitted[:40], "partial": True,
                "instruction": "Omitted fields are unread here. Use case.inspect_evidence with the original source ID and JSON pointer."}
    return {"partial": True, "type": type(value).__name__, "chars": len(packed(value)),
            "instruction": "Read this source with case.inspect_evidence; no missing value is inferred."}


def inspect_source(value, path="", offset=0, limit=20, max_chars=6000, representation="business"):
    if representation not in {'business','raw'}: raise ValueError('unknown source representation')
    target = pointer(business(value) if representation == 'business' else value, path)
    out = {"path": path, "representation": representation, "field_status":"present"}
    if isinstance(target, (list, str)):
        stop = min(len(target), offset + limit)
        segment = target[offset:stop]
        # Fit an exact slice rather than silently dropping the requested text.
        while len(packed(segment)) > max_chars and stop > offset:
            stop = offset + (stop - offset) // 2
            segment = target[offset:stop]
        if stop == offset and offset < len(target):
            return {**out, "partial": True, "total_items": len(target), "child_path": path + "/" + str(offset),
                    "instruction": "Element exceeds output budget; inspect that child pointer."}
        out.update(value=segment, total_items=len(target), offset=offset,
                   next_offset=stop if stop < len(target) else None, partial=stop < len(target) or offset > 0)
    else:
        out.update(preview(target, max_chars))
        for child in out.get('omitted_fields', []): child['path'] = path + child['path']
    return out


def missing_path_feedback(value, path, representation="business"):
    """Describe absence in an ORIGINAL observation, not a truncated preview."""
    target = business(value) if representation == "business" else value
    parent = ""
    for part in path[1:].split("/") if path else []:
        key = part.replace("~1", "/").replace("~0", "~")
        if isinstance(target, dict) and key in target:
            target = target[key]
        elif isinstance(target, list) and key.isdigit() and int(key) < len(target):
            target = target[int(key)]
        else:
            fields = list(target) if isinstance(target, dict) else []
            return {"error": "source_path_absent", "field_status": "absent_in_original_observation",
                    "path": path, "representation": representation, "parent_path": parent,
                    "available_fields": fields[:40], "available_field_count": len(fields),
                    "array_length": len(target) if isinstance(target, list) else None,
                    "partial": False, "creates_evidence": False,
                    "instruction": "This pointer is absent in this stored original observation, not merely omitted by a preview. "
                    "It does not establish absence in other sources or a clinical prerequisite. "
                    "The root pointer is the empty string, not '/'. Inspect an available child or recover an omitted field by its pointer. "
                    "An optional output field need not exist; check the actual tool contract and policy before requiring it."}
        parent += "/" + part
    return {"error": "source_path_unavailable", "path": path, "creates_evidence": False}


def successful(state, name):
    return any(e.get("outcome") == "success" and canonical(e.get("tool", "")) == name
               for e in state.get("evidence", []))


def rank_tools(specs, query):
    stop = {'the','a','an','and','to','for','by','id','with','of','or','in','please'}
    words = lambda text: set(re.findall(r'[a-z0-9]+',text.casefold())) - stop
    terms = words(query)
    ranked = []
    for spec in specs:
        name = canonical(spec.name).casefold()
        score = 6*len(terms & words(name)) + len(terms & words(spec.description))
        if query.casefold() in name: score += 50
        if score: ranked.append((score,spec))
    return [s for _,s in sorted(ranked,key=lambda x:(-x[0],x[1].name))]


def stage(state):
    domain = (state.get("completion_contract") or {}).get("domain")
    if domain == "pa_provider":
        if not state.get("case_bindings"): return "identify"
        if successful(state, "auth.submit_authorization"): return "followup"
        if successful(state, "auth.finalize_provider_determination"): return "submit"
        return "prepare"
    if domain == "pa_um":
        milestones = {r['id'] for b in state.get('completion_contract',{}).get('branches',[]) for r in b['requirements']}
        if successful(state, "determination.finalize"): return "notice"
        if successful(state, "triage.route_case"): return "review"
        if 'intake_completed' not in milestones and 'case_routed' not in milestones: return "review"
        return "intake"
    if domain == "cm":
        for e in reversed(state.get('evidence',[])):
            if e.get('scope')!=state.get('scope') or e.get('outcome')!='success':continue
            value=business(e.get('observed_result'));name=canonical(e.get('tool',''))
            if isinstance(value,dict) and ((name=='cm_intake.disenroll_case' and value.get('status')=='disenrolled')
                    or (name=='cm_care_plan.finalize' and value.get('status')=='finalized')):
                return 'closure'
        if successful(state, "cm_assessment.complete_assessment"): return "plan"
        if successful(state, "cm_outreach.end_outreach_call"): return "assessment"
        if successful(state, "cm_intake.open_case"): return "outreach"
        return "intake"
    return "all"


def select_tools(specs, state):
    if not clinical(state): return specs
    domain = state["completion_contract"]["domain"]; current = stage(state)
    selected = set()
    if domain == "pa_provider":
        selected = {"chart.get_patient_chart_by_patient", "chart.list_candidate_orders", "people.list_ordering_providers",
                    "cases.create_from_order", "cases.get_case"}
        if current != "identify":
            selected = {"cases.get_case"}
            selected |= {"docs.list_case_documents", "docs.get_document", "docs.create_submission_bundle",
                         "forms.list_required_forms", "forms.save_form_response", "forms.validate_form",
                         "inbox.list_messages", "inbox.read_message", "auth.finalize_provider_determination",
                         "auth.submit_authorization", "auth.check_status"}
        if current == "followup": selected |= {canonical(s.name) for s in specs if canonical(s.name).startswith("auth.")}
    elif domain == "pa_um":
        prefixes = ("payer_intake_hub.", "triage.", "determination.") if current == "intake" else (
            "review.", "determination.", "p2p.", "p2p_session.", "payer_letter_center.")
        selected = {canonical(s.name) for s in specs if canonical(s.name).startswith(prefixes)}
    else:
        prefixes = {"intake": ("cm_intake.", "cm_chart."),
                    "outreach": ("cm_intake.", "cm_chart.", "cm_outreach."),
                    "assessment": ("cm_chart.", "cm_outreach.", "cm_assessment.", "cm_intake."),
                    "plan": ("cm_care_plan.", "cm_chart.", "cm_outreach.", "cm_assessment.", "cm_intake."),
                    "closure": ("cm_intake.","cm_chart.","cm_outreach.","cm_assessment.","cm_care_plan.")}[current]
        selected = {canonical(s.name) for s in specs if canonical(s.name).startswith(prefixes)}
    activated = set(state.get("activated_tools", []))
    return [s for s in specs if s.name.startswith(("case.", "workspace.")) or canonical(s.name) in selected or s.name in activated]


def project_working_context(messages, state, tools, max_chars, turn_groups):
    from .policy_grounding import decision_view
    from .retrieval import field_overview
    prefix = deepcopy(messages[:2])
    all_evidence = [e for e in state.get("evidence", []) if e.get('scope') == state.get('scope')]
    # Helper originals remain accessible by ID, but their full documents do not
    # automatically enter the owner's views or retained-reference context.
    evidence = [e for e in all_evidence if not e.get('helper_job_id')]
    index = [{"id": e["id"], "tool": canonical(e.get("tool", "")), "outcome": e.get("outcome")}
             for e in all_evidence[-32:]]
    latest = {}; sticky = {}
    for e in evidence:
        name = canonical(e.get("tool", ""))
        if e.get("outcome") == "success":
            latest[name] = e
            if name in {"chart.get_patient_chart_by_patient", "forms.list_required_forms", "cm_intake.get_referral"}:
                sticky[name] = e
    for name in ('cases.get_case','determination.get_summary','cm_chart.get_chart_data'):
        if name in latest: sticky[name] = latest[name]
    recent = []
    for e in reversed(evidence):
        if e.get('outcome') == 'success' and canonical(e.get('tool','')) not in {canonical(x['tool']) for x in recent}:
            recent.append(e)
        if len(recent) == 3: break
    chosen = list({e['id']: e for e in [*sticky.values(), *recent]}.values())
    views = [{"id": e["id"], "tool": canonical(e['tool']), **field_overview(business(e['observed_result'])),
              "additional_mcp_content_available": bool(isinstance(e['observed_result'],dict)
                  and e['observed_result'].get('content') and normalize_mcp(e['observed_result']) == e['observed_result']),
              "raw_source_access": "case.inspect_evidence representation=raw; original evidence ID"} for e in chosen]
    contract = state.get("completion_contract", {})
    milestones = [{"branch": b['id'], "milestones": list(dict.fromkeys(r['id'] for r in b['requirements']))}
                  for b in contract.get('branches', [])]
    # Explicitly inspected fields must survive beyond the recent-turn window.
    # Cache only trusted local tool replies linked to successful scoped sources;
    # this is deterministic source retention, not a model-authored fact summary.
    known = {e['id'] for e in all_evidence if e.get('outcome') == 'success'}
    readouts = {}
    for m in messages:
        if m.get('role') != 'tool' or m.get('name') not in {'case.inspect_evidence','case.retrieve_evidence','case.search_narrative'}: continue
        try: value = json.loads(m.get('content',''))
        except (ValueError,TypeError): continue
        if (isinstance(value,dict) and value.get('field_status')=='absent_in_original_observation'
                and value.get('id') in known):
            readout={k:value[k] for k in ('id','path','representation','field_status','available_fields') if k in value}
            readout['historical_observation_only']=True
            key=(value['id'],value.get('path',''),0,value.get('representation','business'))
            readouts.pop(key,None);readouts[key]=readout
            continue
        if not isinstance(value,dict) or 'error' in value: continue
        if m.get('name')=='case.search_narrative':
            for match in value.get('matches',[]):
                source=match.get('source',{});source_id=source.get('evidence_id')
                if source_id not in known:continue
                field={'id':source_id,'path':source['text_pointer'],'offset':match['start'],'end':match['end'],
                       'value':match['text'],'partial':True,'semantic_rank_not_fact':True}
                key=(source_id,field['path'],field['offset'],'business');readouts.pop(key,None);readouts[key]=field
            continue
        entries=value.get('results',[]) if m.get('name')=='case.retrieve_evidence' else [value]
        for entry in entries:
            if not isinstance(entry,dict) or entry.get('id') not in known:continue
            fields=entry.get('fields',[]) if m.get('name')=='case.retrieve_evidence' else [entry]
            fields=[*fields,*[{'path':p['text_pointer'],'offset':p['start'],'value':p['text'],
                              'end':p['end'],'partial':True} for p in entry.get('passages',[])]]
            if 'overview' in entry:fields.append({'path':'','overview':entry['overview']})
            for field in fields:
                readout={'id':entry['id'],**field}
                key=(entry['id'],field.get('path',''),field.get('offset',0),field.get('representation','business'))
                readouts.pop(key,None);readouts[key]=readout
    focused = []; focused_chars = 0
    for value in reversed(list(readouts.values())):
        length = len(packed(value))
        if focused_chars + length <= 20_000:
            focused.insert(0,value);focused_chars += length
    # File readers already enforce bounded excerpts. Do not discard their text
    # merely because a whole string cannot fit inside a dictionary preview.
    references = {}; reference_views = []; reference_chars = 0
    for e in evidence:
        if e.get('outcome') != 'success' or canonical(e.get('tool','')) not in {'workspace.read_file','workspace.read_pdf','workspace.read_many','workspace.hybrid_search'}:
            continue
        value = business(e['observed_result'])
        if not isinstance(value,dict): continue
        children=[(None,value)]
        if canonical(e['tool'])=='workspace.read_many':
            children=[(f'/items/{i}/result',child['result']) for i,child in enumerate(value.get('items',[]))
                      if child.get('operation') in {'read_file','read_pdf'} and isinstance(child.get('result'),dict)
                      and 'error' not in child['result']]
        elif canonical(e['tool'])=='workspace.hybrid_search':
            documents={d['document_id']:d for d in value.get('documents',[])}
            children=[]
            for i,hit in reversed(list(enumerate(value.get('matches',[])))):
                meta=documents.get(hit.get('document_id'),{})
                children.append((f'/matches/{i}',{'path':hit.get('source',{}).get('path'),
                    'sha256':hit.get('source',{}).get('sha256'),'text':hit.get('text',''),
                    'offset_chars':hit.get('start',0),'end':hit.get('end'),
                    'original_text_pointer':f'/matches/{i}/text','header':meta.get('header'),
                    'qualifying_sections':meta.get('qualifying_sections',[]),'qualifications_complete':False}))
        for pointer_prefix,child in children:
            key = (child.get('path'),child.get('offset_chars',0),child.get('page_start'),child.get('page_char_offset',0))
            references.pop(key,None)
            references[key] = {'id':e['id'],'tool':canonical(e['tool']),'value':child,
                               'text_pointer_prefix':pointer_prefix or '', 'historical':True}
    for value in reversed(list(references.values())):
        length = len(packed(value))
        if reference_chars + length <= 24_000:
            reference_views.insert(0,value);reference_chars += length
    notes = [{k:n[k] for k in ('id','kind','summary','evidence_ids','status','is_observed_fact') if k in n}
             for n in state.get('working_notes',[]) if not n.get('helper_job_id') and n.get('status')!='resolved'][-8:]
    prerequisites=[]
    for record in state.get('prerequisite_records',[]):
        if record.get('helper_job_id') or record.get('status')=='resolved':continue
        facts=record['facts']
        prerequisites.append({k:record[k] for k in ('id','blocked_action','claim','basis_kind','support')} | {
            'schema_facts':{k:facts[k] for k in ('tool_name','field_name','schema_path','required_input_fields','declared_input_fields') if k in facts},
            'source_refs':[{k:r[k] for k in ('evidence_id','path','start','end','field_status') if k in r} for r in facts.get('source_references',[])],
            'interpretation_verified':False})
    jobs=[{k:j[k] for k in ('id','role_id','status','model_calls','tool_proposals','source_ids') if k in j}
          | {'conclusion':str(j.get('result',{}).get('conclusion',j.get('result',{}).get('proposal','')))[:1500]} for j in state.get('helper_jobs',[])[-4:]]
    from .authorized_statements import view as statement_view
    ledger = {"authorized_statements": statement_view(state), "scope": state.get("scope"), "bindings": {k: state[k] for k in
              ("identity_bindings", "principal_bindings", "case_bindings") if state.get(k)},
              "stage": stage(state), "completion": {"authority": "pinned engine contract; model cannot waive milestones",
                  "mapped": contract.get("mapping_status"), "alternatives": milestones, "last_check": state.get("completion_gate")},
              "outstanding_work": [o for o in state.get("obligations", []) if o.get("status") != "closed"],
              "recent_sources": index, "source_count": len(all_evidence), "working_observations": views,
              "working_notes":notes, "current_plan":state.get('current_plan'),
              "stage_guidance":state.get('stage_guidance'),
              "assignment_audit":{k:v for k,v in state.get('assignment_audit',{}).items() if k!='branches'} | {
                  'branches':[{k:v for k,v in b.items() if k!='requirements'} for b in state.get('assignment_audit',{}).get('branches',[])]},
              "working_record_counts":{k:len(state.get(v,[])) for k,v in
                  (('notes','working_notes'),('blockers','prerequisite_records'),('jobs','helper_jobs'))},
              "working_record_rule":"Notes, reported plans, prerequisite claims and helper conclusions are interpretations. Recover older entries with case.get_working_record; cite original evidence for facts.",
              "prerequisite_records":prerequisites[-6:], "delegated_jobs":jobs,
              "unchanged_operations":[{k:v[k] for k in ('tool','latest_evidence_id','first_matching_evidence_id','unchanged_count')}
                    for v in state.get('operation_progress',{}).values() if v.get('unchanged_count',0)>=1][-6:],
              "retained_source_readouts": focused,
              "retained_reference_excerpts": reference_views,
              "policy_decision": decision_view(state),
              "write_payload_feedback": [e['execution_feedback'] for e in all_evidence
                  if e.get('execution_feedback')][-6:],
              "permitted_operation_index": state.get('tool_name_index',[]),
              "capability_rule": "The index is complete for this actor, including discoverable tools. Stage selection changes presentation only; use it to identify callable operations under the system capability rule.",
              "readout_rule": "These are already-read historical source fields, not new evidence or proof of a fresh readback. Reuse them rather than repeating the same inspection; follow next_offset for unread ranges.",
              "instruction": "Views are attributed excerpts, not new evidence. Omitted fields are not absent. Reuse retained_source_readouts before another inspection; follow continuation markers for unread ranges. Group related fields and phrases with case.retrieve_evidence, including several original sources per request. Owner role summaries are supplied; full contracts are available via case.get_role. Use case.find_evidence for older source IDs. Other allowed tools can be activated with case.discover_tools."}
    if state.get('goal_planning_enabled'):
        from .goal_state import view as goal_view
        ledger['goal_state'] = goal_view(state)
        # Replace duplicate work descriptions instead of adding a full graph.
        ledger.pop('prerequisite_records',None)
        ledger.pop('outstanding_work',None)
    prefix[0]['content'] += '\n\nCurrent case working set:\n' + packed(ledger)
    schemas = [{"name": t.name, "description": t.description, "input_schema": t.input_schema,
                "effect": t.effect, "identity_fields": t.identity_fields} for t in tools]
    size = lambda ms: len(packed({"messages": ms, "tool_schemas": schemas}))
    if size(prefix) > max_chars: return None
    target = min(max_chars, 100_000)
    retained_exact = {v['id']:v for v in reference_views
                      if not v.get('text_pointer_prefix') and v.get('tool') in {'workspace.read_file','workspace.read_pdf'}}
    selected = []
    groups = turn_groups(messages[2:])[-10:]
    for group in reversed(groups):
        view = []
        for m in group:
            m = normalize_message(m)
            retained=retained_exact.get(m.get('evidence_id'))
            if m.get('role')=='tool' and retained:
                try:observed=json.loads(m.get('content','')).get('observed_result')
                except (ValueError,AttributeError):observed=None
                if observed is not None and packed(business(observed))==packed(retained['value']):
                    # The entire identical body is already visible above. No
                    # summarization, source loss or original-record mutation.
                    m={**m,'content':packed({'evidence_id':m['evidence_id'],'outcome':'success',
                        'original_body_in':'Current case working set.retained_reference_excerpts',
                        'instruction':'The complete identical business result is retained there under this source ID. Raw source remains retrievable.'})}
            explicit_reads = {'case.inspect_evidence','case.read_evidence','case.search_evidence','case.retrieve_evidence','case.search_narrative','case.get_role',
              'workspace.read_file','workspace.read_pdf','workspace.read_many','workspace.hybrid_search','case.audit_assignment'}
            if (m.get('role') == 'tool' and canonical(m.get('name','')) not in explicit_reads
                    and len(str(m.get('content',''))) > 6500):
                try: raw = json.loads(m['content'])
                except ValueError: raw = m['content']
                value = raw.get('observed_result', raw) if isinstance(raw,dict) else raw
                m = {**m, 'content': packed({'id': m.get('evidence_id'), **preview(business(value), 3000)})}
            view.append(m)
        candidate = prefix + view + [x for g in selected for x in g]
        if size(candidate) <= (max_chars if not selected else target): selected.insert(0, view)
        elif not selected: return None
    return prefix + [x for g in selected for x in g]
