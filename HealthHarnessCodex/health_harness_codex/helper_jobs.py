"""Sequential, case-scoped delegated workers over the owner's guarded dispatcher."""
from __future__ import annotations

from copy import deepcopy
import json
import uuid

from .models import ModelReply, IsolationError, UnknownOutcomeError, ConflictError
from .providers import ModelResponseFormatError, format_correction, response_retry_limit, validate_reply_structure
from .roles import roles_for, helper_prompt
from .schema import validate_arguments
from .planning import source
from .working_set import business, canonical, normalize_mcp


def observed_resource_handles(state, specs):
    """Satisfy tool-input data dependencies with exact observed identifiers.

    No inferred IDs, string parsing or permission grants. Handles may refer to
    ended sessions; the reviewer must read their current state before acting.
    """
    from .schema import tool_parameter_schema, _expand_refs
    needed=set()
    for spec in specs:
        try:schema=_expand_refs(tool_parameter_schema(spec.input_schema))
        except (ValueError,TypeError):continue  # Optional handle projection never grants permissions.
        needed.update(k for k in schema.get('required',[]) if k.endswith('_id')
                      and k not in {'patient_id','case_id','principal_id','actor_id'})
    result=[];seen=set()
    for e in reversed(state.get('evidence',[])):
        if (e.get('scope')!=state.get('scope') or e.get('outcome')!='success'
                or canonical(e.get('tool','')).startswith(('case.','workspace.'))):
            continue
        stack=[('',business(e.get('observed_result')))];visited=0
        while stack and visited<200 and len(result)<8:
            path,value=stack.pop();visited+=1
            if isinstance(value,dict):
                for k,v in value.items():
                    child=path+'/'+str(k).replace('~','~0').replace('/','~1')
                    if k in needed and isinstance(v,str) and v and len(v)<=256 and (k,v) not in seen:
                        seen.add((k,v));result.append({'field':k,'value':v,'evidence_id':e['id'],
                            'path':child,'tool':e['tool'],'grants_additional_permissions':False})
                    elif isinstance(v,(dict,list)):stack.append((child,v))
            elif isinstance(value,list):
                stack.extend((path+'/'+str(i),v) for i,v in enumerate(value[:100]) if isinstance(v,(dict,list)))
        if len(result)>=8:break
    return result


CONVERSATION_MOVES = ('answer', 'ask_priority', 'invite_decision', 'confirm_consent', 'gather_information',
                      'respect_decline', 'close')
NEED_STATUSES = ('answered', 'declined', 'partial', 'open')
CLOSED_NEEDS = {'answered', 'declined'}


def _with_conversation_move(spec):
    """Worker-only view of a counterparty message tool; the field never dispatches."""
    from dataclasses import replace
    schema = deepcopy(spec.input_schema)
    move = {'type': 'string', 'enum': list(CONVERSATION_MOVES),
            'description': 'What this message does. Use invite_decision when asking directly whether the counterparty '
                           'wants to proceed; gather_information for questions collecting your information_needs; '
                           'close for any message offering to end or finish contact.'}
    covers = {'type': 'array', 'maxItems': 12, 'items': {'type': 'integer', 'minimum': 1},
              'description': 'Numbers (1 = first) of your pinned information_needs this message asks about.'}
    updates = {'type': 'array', 'maxItems': 12, 'items': {
        'type': 'object', 'additionalProperties': False, 'required': ['need', 'status'],
        'properties': {'need': {'type': 'integer', 'minimum': 1}, 'status': {'type': 'string', 'enum': list(NEED_STATUSES)}}},
        'description': "Status of information_needs from the counterparty's replies so far (declined = they chose not to answer)."}
    # Declaring properties on an open object would close it; only extend a declared schema.
    if isinstance(schema.get('properties'), dict):
        schema['properties'].update(conversation_move=move, covers_needs=covers, need_status_updates=updates)
    schema['required'] = list(dict.fromkeys([*schema.get('required', []), 'conversation_move']))
    return replace(spec, input_schema=schema)


def _open_needs(job, needs):
    """(number, need) for pinned needs not answered or declined, in the worker's priority order."""
    status = job.get('need_status', {})
    return [(i, n['need']) for i, n in enumerate(needs, 1) if status.get(n['need']) not in CLOSED_NEEDS]


def _needs_view(items):
    return [{'number': i, 'need': n[:160]} for i, n in items]


def _order_gate(job, move, covered, needs):
    """Once per need: hold a message that asks lower-ranked needs while a higher-ranked one is still open."""
    consented = move == 'gather_information' or {'confirm_consent', 'gather_information'} & set(job.get('conversation_moves', []))
    if not needs or not consented or move in {'answer', 'respect_decline', 'close'}:
        return None
    open_needs = _open_needs(job, needs)
    if move in {'gather_information', 'ask_priority'} and not covered and open_needs \
            and not job.get('covers_feedback_given'):
        job['covers_feedback_given'] = True
        return {'error': 'message_not_sent', 'reason': 'covers_needs_missing',
                'open_information_needs': _needs_view(open_needs[:6]),
                'instruction': 'Not sent; no counterparty turn was used. Declare covers_needs (the numbers this message '
                               'asks about), or [] if it asks none of them, and update need_status_updates from replies.'}
    # Breadth first under a turn cap: every need is asked once before follow-up detail on any.
    asked = set(job.get('needs_asked', []))
    unasked = [(i, n) for i, n in open_needs if n not in asked and i not in covered]
    if not covered or not unasked:
        return None
    held = set(job.get('order_held', []))
    skipped = [(i, n) for i, n in unasked if i < min(covered) and n not in held]
    if skipped:
        job['order_held'] = sorted(held | {n for _, n in skipped})
        return {'error': 'message_not_sent', 'reason': 'higher_ranked_needs_unasked',
                'open_information_needs': _needs_view(skipped[:6]),
                'instruction': 'Not sent; no counterparty turn was used. You ranked these needs higher and have not asked '
                               'them yet. Ask them first, using the actual items where a named instrument applies, or '
                               'mark them answered/declined in need_status_updates if replies already settled them. '
                               "Answering the counterparty's own question or an urgent safety concern comes first and is "
                               'never held.'}
    if all(needs[i - 1]['need'] in asked for i in covered) and not job.get('breadth_held'):
        job['breadth_held'] = True
        return {'error': 'message_not_sent', 'reason': 'unasked_needs_remain',
                'open_information_needs': _needs_view(unasked[:6]),
                'instruction': 'Not sent; no counterparty turn was used. Contact may end at any reply. This asks follow-up '
                               'detail on needs already asked while these were never asked; ask each need once first, '
                               'then return to detail. Record partial answers as partial.'}
    return None


def _conversation_gate(job, call, needs=()):
    """Strip worker-only fields; return feedback once if contact is closed early or ranked needs are skipped."""
    move = call.arguments.pop('conversation_move', None)
    covers = call.arguments.pop('covers_needs', None)
    covered = sorted({i for i in covers if type(i) is int and 1 <= i <= len(needs)}) if isinstance(covers, list) else []
    updates = call.arguments.pop('need_status_updates', None)
    for update in updates if isinstance(updates, list) else []:
        number = update.get('need') if isinstance(update, dict) else None
        if type(number) is int and 1 <= number <= len(needs) and update.get('status') in NEED_STATUSES:
            job.setdefault('need_status', {})[needs[number - 1]['need']] = update['status']
    result = _gate_decision(job, move, covered, needs)
    job.setdefault('conversation_log', []).append(
        {'move': move, 'covers_needs': covered, 'held': result.get('reason') if result else None})
    return result


def _gate_decision(job, move, covered, needs):
    moves = job.setdefault('conversation_moves', [])
    if move == 'close' and 'invite_decision' not in moves and 'respect_decline' not in moves \
            and not job.get('close_feedback_given'):
        job['close_feedback_given'] = True
        return {'error': 'message_not_sent', 'reason': 'close_before_decision_invitation',
                'instruction': 'Not sent. Before offering to end contact, answer any open question and ask directly, '
                               'once, whether they want to proceed (invite_decision); if they declined, respect it '
                               '(respect_decline). Offering time to decide comes after the invitation. No pressure.'}
    if move == 'close':
        held = _return_gate(job, needs)
        if held:
            return {**held, 'error': 'message_not_sent'}
    held = _order_gate(job, move, covered, needs)
    if held:
        return held
    for i in covered:
        job.setdefault('need_status', {}).setdefault(needs[i - 1]['need'], 'open')
        job['needs_asked'] = list(dict.fromkeys([*job.get('needs_asked', []), needs[i - 1]['need']]))
    moves.append(move)
    return None


def _contact_results(state, job):
    for e in state.get('evidence', []):
        if e.get('helper_job_id') != job['id'] or e.get('outcome') != 'success':
            continue
        result = business(e.get('observed_result'))
        if isinstance(result, dict) and isinstance(result.get('content'), list) and result['content'] \
                and isinstance(result['content'][0], dict):
            result = result['content'][0].get('parsed_json', result)
        if isinstance(result, dict):
            yield result


def _contact_note(state, job, needs):
    """Observed turn use and the worker's own open needs; facts and labels only, no wording judged."""
    turns = [r['turn_number'] for r in _contact_results(state, job) if type(r.get('turn_number')) is int]
    if not turns and not needs:
        return ''
    note = (f" Contact: turn_number {max(turns)} reached; the cap is undisclosed and contact may end at any reply."
            if turns else ' Contact: no turn used yet; the cap is undisclosed.')
    open_needs = _open_needs(job, needs)
    if needs:
        note += (' Open information_needs (your order): '
                 + '; '.join(f"{i}. {'' if n in job.get('needs_asked', []) else '[not yet asked] '}{n[:80]}"
                             for i, n in open_needs[:8]) if open_needs
                 else ' All pinned information_needs are answered or declined.')
    return note


def _contact_ended(state, job):
    """True once this job observed its contact as ended (send result or transcript read)."""
    return any(r.get('session_status') == 'ended' or r.get('stopped') is True
               or (r.get('status') == 'ended' and 'messages' in r) for r in _contact_results(state, job))


CONTACT_ENDED = {'error': 'message_not_sent', 'reason': 'contact_ended',
                 'instruction': 'Not sent: this contact was observed as ended and cannot be reopened. Do not send '
                                'further messages; return JSON with status, conclusion, original evidence_ids and '
                                'open_questions, naming information still needed as unresolved.'}


def _return_gate(job, needs=()):
    """Once, before a conversation worker closes or returns while contact it cannot reopen is still open."""
    moves = job.get('conversation_moves', [])
    if job.get('contact_ended') or job.get('return_feedback_given') \
            or not {'invite_decision', 'confirm_consent', 'gather_information'} & set(moves) \
            or 'respect_decline' in moves:
        return None
    job['return_feedback_given'] = True
    return {'error': 'result_not_returned', 'reason': 'contact_still_open',
            'open_information_needs': _needs_view(_open_needs(job, needs)[:8]),
            'instruction': 'Held once. Contact is still open; once it ends (owner close, a closing offer, or the turn '
                           'cap) it cannot be reopened. If the counterparty agreed to proceed, retrieve the governing '
                           'standards for the later stages in your handoff and ask now, within the given consent and '
                           'permissions, for what only the counterparty can provide (your pinned information_needs), in grouped questions and '
                           'respecting any declined topic. If they declined or deferred, or nothing more is needed '
                           'from them, proceed: close, or return JSON with status, conclusion, original evidence_ids '
                           'and open_questions.'}


def run_helper(harness, scope, state, call, owner, fence, *, invocation='owner', stage_handoff=None, preparation=False,
               conversation_tools=()):
    if harness.composition == "combined":
        raise ValueError("helpers are disabled in combined composition")
    if harness._helper_channel:
        raise ValueError("recursive helper delegation is not permitted")
    args = call.arguments
    role = next((r for r in roles_for(state["domain"]) if r["id"] == args["role_id"]), None)
    if role is None:
        raise IsolationError("helper role must belong to the current domain/shared responsibility catalog")
    if not role['model_visible']:
        raise ValueError('Code-only safeguards are not model-worker roles; case.get_role remains available')
    evidence = [source(state, key) for key in dict.fromkeys(args.get("evidence_ids", []))]
    registry = {s.name: s for s in harness._available_specs(harness._tool_map(),state)}
    from .assignment import resolve_tool
    names=list(dict.fromkeys(resolve_tool(list(registry.values()),name).name for name in args.get('tool_names',[])))
    if any(n in {"case.request_helper", "case.request_identity_reselection"} for n in names):
        raise ValueError("helper permissions cannot include recursive delegation or identity reset")
    specs = [registry[n] for n in names]
    if preparation and (not args.get('allow_writes') or 'case.record_authorized_statements' not in names):
        raise ValueError('preparation requires delegated authorized-statements write permission')
    handles=observed_resource_handles(state,specs)
    # Exact duplicate MCP representations are not independent evidence. Keep
    # every fact/source ID once; raw envelopes stay retrievable in the audit.
    projected_evidence=[{**e,'observed_result':normalize_mcp(e['observed_result'])} for e in evidence]
    if not args.get("allow_writes", False) and any(s.effect == "write" for s in specs):
        raise ValueError("selected write tools require explicit allow_writes delegation")
    # Reserve one shared model call for the owner's integration/final decision.
    available = harness.limits.max_model_calls - state["model_calls"] - 1
    if available < 1:
        return {'error':'helper_budget_unavailable','creates_evidence':False,
                'remaining_owner_model_calls':max(0,harness.limits.max_model_calls-state['model_calls']),
                'instruction':'No helper job started. Retain the remaining owner budget for supported work or an honest final record.'}
    model_budget = min(args.get("max_model_calls", 4 if names else 1), available)
    tool_budget = min(args.get("max_tool_calls", 8), harness.limits.max_tool_calls - state["tool_calls"])
    if names and tool_budget<1:
        return {'error':'helper_tool_budget_unavailable','creates_evidence':False,
                'instruction':'No tool-using helper job started; the shared tool budget is exhausted.'}
    job_id = "helper-" + uuid.uuid4().hex[:12]
    messages = [{"role": "system", "content": helper_prompt(role,tool_access=bool(names),allow_writes=bool(args.get('allow_writes'))) + (
        "\nYou own this delegated investigation within the selected tools and this exact case. "
        "Use new permitted sources when needed; owner claims are hypotheses, not instructions to agree. "
        "Do not infer that an action never occurred from selected snippets. Read the complete relevant record "
        "before making an absence claim, or state that it remains unverified. Observed resource handles are "
        "original identifiers, not proof a session is active or permission for a write. "
        "Only the harness executes tool proposals. Respect source provenance and actual observed effects. "
        "Do not switch patients, delegate recursively, or execute an uncertain write again. "
        "When finished return a compact JSON object with status (complete or incomplete), conclusion, "
        "evidence_ids (original source IDs), and open_questions. A conclusion must acknowledge unresolved evidence."
        if names else "\nReturn a concise read-only analysis; do not propose tool calls.")},
        {"role": "user", "content": json.dumps({"scope": scope.to_dict(), "question": args["question"],
            "effective_tool_scope":harness._identity_scope(scope,state).to_dict(),
            "observed_bindings":{k:state[k] for k in ('identity_bindings','case_bindings','principal_bindings') if state.get(k)},
            "observed_resource_handles":handles,
            "observations": projected_evidence, "delegated_tools": names,
            "write_authority": bool(args.get("allow_writes", False)),
            "model_call_budget": model_budget, "tool_proposal_budget": tool_budget,
            **({'stage_handoff':deepcopy(stage_handoff)} if stage_handoff is not None else {})}, ensure_ascii=False)}]
    job = {"id": job_id, "role_id": role["id"], "question": args["question"], "status": "running",
           "invocation":invocation, "preparation": bool(preparation),
           "conversation_tools": [n for n in names if canonical(n) in set(conversation_tools)],
           "tool_names": names, "allow_writes": bool(args.get("allow_writes", False)),
           "model_budget": model_budget, "tool_budget": tool_budget, "model_calls": 0,
           "tool_proposals": 0, "source_ids": [e["id"] for e in evidence], "messages": messages}
    state.setdefault("helper_jobs", []).append(job)
    state["helper_active"] = job_id
    channel = {"id": job_id, "message_start": len(state["messages"]),
               "evidence_start": len(state.get("evidence", []))}
    harness._helper_channel = channel
    harness._save(scope, state, owner, fence)
    if harness.progress:
        harness.progress("helper_started", helper_id=job_id, role_id=role["id"], tool_count=len(specs),invocation=invocation)
    recorder = getattr(harness.model, "recorder", None)
    previous_role = recorder.metadata.get("model_role", "workflow") if recorder else None
    if recorder:
        recorder.metadata["model_role"] = "helper"
    finished_status = "interrupted"
    try:
        # Long permitted retrieval/indexing must retain the SAME owner fence,
        # including time outside model inference.
        with harness.store.maintained_claim(scope,owner,fence):
            result = _work(harness, scope, owner, fence, job, messages, specs)
        finished_status = "completed" if result["status"] == "complete" else "incomplete"
        state = harness.store.load_case(scope)
        durable = next(j for j in state["helper_jobs"] if j["id"] == job_id)
        durable.update(job)
        durable.update(status=result["status"], result=deepcopy(result), messages=messages)
        state.pop("helper_active", None)
        harness._save(scope, state, owner, fence)
        return {"helper_id": job_id, "role_id": role["id"], **result,
                "warning": "Helper conclusion is an interpretation; cited tool observations retain their original authority."}
    except (UnknownOutcomeError, ConflictError):
        # Leave durable helper_active set. Interrupted/uncertain work must be
        # reconciled rather than silently starting this delegated task again.
        raise
    finally:
        harness._helper_channel = None
        if recorder:
            recorder.metadata["model_role"] = previous_role
        if harness.progress:
            harness.progress("helper_finished", helper_id=job_id, role_id=role["id"], status=finished_status)


def _work(h, scope, owner, fence, job, messages, specs):
    if job.get('preparation'):
        _prepare_worker(h, scope, owner, fence, job, messages)
    conversation_tools = set(job.get('conversation_tools', []))
    specs = [_with_conversation_move(s) if s.name in conversation_tools else s for s in specs]
    registry = {s.name: s for s in specs}
    format_retry_used = 0
    validation_retry_used = False
    for _ in range(job["model_budget"] - job["model_calls"]):
        h._check_runtime()
        state = h.store.load_case(scope)
        if state["model_calls"] >= h.limits.max_model_calls - 1:
            break
        job["model_calls"] += 1
        state["model_calls"] += 1
        durable = next(j for j in state["helper_jobs"] if j["id"] == job["id"])
        durable.update(job)
        h._save(scope, state, owner, fence)
        messages.append({'role':'user','content':
            f"Delegated job budget: this is model call {job['model_calls']} of {job['model_budget']}; "
            f"{job['tool_budget']-job['tool_proposals']} tool proposals remain in this job. "
            + ('This is the last allowed model call: return the delegated result from observed sources, with honest unresolved questions, rather than requesting more investigation.'
               if job['model_calls']==job['model_budget'] else
               'Prioritize the specific assigned question and reserve a model turn for your concise source-linked conclusion.')
            + (_contact_note(state, job, state.get('information_needs', [])) if conversation_tools else '')})
        # The owner's generic/clinical completion ledger must NOT enter a
        # delegated subtask. Its completion is defined by the assigned question;
        # only the owner passes the independent whole-case completion contract.
        from .working_set import normalize_message
        context=[normalize_message(m) for m in deepcopy(messages)]
        from .authorized_statements import pin
        pin(context, state)
        size=len(json.dumps({'messages':context,'tools':[{'name':s.name,'description':s.description,
            'input_schema':s.input_schema} for s in specs]},ensure_ascii=False,separators=(',',':')))
        if h.limits.max_context_chars and size>h.limits.max_context_chars:
            return _result(job, "incomplete", "Helper context does not fit the explicitly configured budget.")
        failed_spec = None
        try:
            with h.store.maintained_claim(scope, owner, fence):
                reply = h.model.complete(context, specs, max_output_tokens=h.limits.max_output_tokens)
            if not isinstance(reply, ModelReply):
                raise TypeError("helper backend must return ModelReply")
            validate_reply_structure(reply,registry)
        except (UnknownOutcomeError, ConflictError):
            raise
        except Exception as exc:
            state = h.store.load_case(scope)
            h._merge_usage(state, getattr(exc, "usage", {}))
            if (job['model_calls']<job['model_budget']
                    and state['model_calls']<h.limits.max_model_calls-1
                    and h._request_disconnection_retry(state,exc,helper_id=job['id'])):
                h._save(scope,state,owner,fence)
                continue
            h._save(scope, state, owner, fence)
            if isinstance(exc, ModelResponseFormatError) and format_retry_used < response_retry_limit(exc):
                messages.append({"role": "user", "content": format_correction(exc)})
                format_retry_used += 1
                continue
            return _result(job, "incomplete", "Helper model request failed; preserved successful work.",
                           error_type=type(exc).__name__)
        state = h.store.load_case(scope)
        state['model_transport_retry_streak']=0
        h._merge_usage(state, reply.usage)
        h._save(scope, state, owner, fence)
        if not reply.tool_calls:
            if not specs:  # backwards-compatible read-only role analysis
                return _result(job, "complete", reply.content[:4000])
            held = (_return_gate(job, state.get('information_needs', [])) if conversation_tools and job['model_calls'] < job['model_budget']
                    and state['model_calls'] < h.limits.max_model_calls - 2 else None)
            if held:
                messages.append({'role': 'assistant', 'content': reply.content})
                messages.append({'role': 'user', 'content': json.dumps(held, ensure_ascii=False)})
                continue
            try:
                final = json.loads(reply.content)
                ids = final.get("evidence_ids", []) if isinstance(final, dict) else None
                questions = final.get('open_questions',[]) if isinstance(final,dict) else None
                known = {e["id"] for e in state.get("evidence", []) if e.get("outcome") == "success"
                         and e.get("scope") == scope.to_dict()}
                if (not isinstance(final, dict) or final.get("status") not in {"complete", "incomplete"}
                        or not isinstance(final.get("conclusion"), str) or not isinstance(ids, list)
                        or not isinstance(questions,list) or any(not isinstance(q,str) for q in questions)
                        or any(not isinstance(i, str) for i in ids)):
                    raise ValueError("unsupported helper result")
                # Unreturned (often mistyped) IDs are not evidence; drop them visibly instead of losing the result.
                dropped = [i for i in ids if i not in known]
                return _result(job, final["status"], final["conclusion"][:4000],
                               evidence_ids=[i for i in ids if i in known],
                               open_questions=[q[:600] for q in questions[:8]],
                               **({'dropped_unreturned_evidence_ids': [i[:200] for i in dropped[:8]]} if dropped else {}))
            except (ValueError, TypeError, AttributeError):
                if not format_retry_used:
                    messages.append({"role": "user", "content": "Return the delegated task result as JSON with status, conclusion, original evidence_ids and open_questions. Do not repeat completed actions."})
                    format_retry_used += 1
                    continue
                return _result(job, "incomplete", "Helper did not provide a supported structured conclusion.")
        if job["tool_proposals"] + len(reply.tool_calls) > job["tool_budget"]:
            return _result(job, "incomplete", "Delegated tool budget reached; no excess proposal dispatched.")
        if state["tool_calls"] + len(reply.tool_calls) > h.limits.max_tool_calls:
            return _result(job, "incomplete", "Shared tool budget reached; no excess proposal dispatched.")
        job["tool_proposals"] += len(reply.tool_calls)
        # Persist attempted work before dispatch, including the interruption/
        # unknown-write path where the normal job-finalization code cannot run.
        next(j for j in state['helper_jobs'] if j['id']==job['id']).update(job)
        h._save(scope,state,owner,fence)
        # Validate the WHOLE group before invoking the authoritative dispatcher.
        # Invalid siblings cannot cause a partial unapproved write.
        try:
            ids = [c.id for c in reply.tool_calls]
            if len(ids) != len(set(ids)) or any(not isinstance(i, str) or not i for i in ids):
                raise ValueError("helper call IDs must be unique nonempty strings")
            for c in reply.tool_calls:
                if c.name not in registry:
                    raise IsolationError("helper proposed a tool outside its delegated permissions")
                failed_spec = registry[c.name]
                validate_arguments(registry[c.name], c.arguments, h._identity_scope(scope, state))
        except (ValueError, IsolationError) as exc:
            from .engine import _safe_validation_feedback
            feedback = _safe_validation_feedback(exc, failed_spec) if failed_spec else {"category": "delegated_proposal_not_permitted"}
            state["tool_calls"] += len(reply.tool_calls)
            h._save(scope, state, owner, fence)
            messages.append({"role": "user", "content": json.dumps({"error": "helper_proposals_not_dispatched",
                "feedback": feedback, "allowed_tools": list(registry), "instruction": "Correct only from observed evidence and the declared permissions. No rejected proposal executed."})})
            if validation_retry_used:
                return _result(job, "incomplete", "Repeated delegated proposal validation failure.")
            validation_retry_used = True
            continue
        needs = state.get('information_needs', [])
        gated = [(c, CONTACT_ENDED if job.get('contact_ended') else _conversation_gate(job, c, needs))
                 for c in reply.tool_calls if c.name in conversation_tools]
        blocked = [(c, feedback) for c, feedback in gated if feedback]
        if blocked:
            # Nothing in this proposal group dispatches; the worker revises once.
            job["tool_proposals"] -= len(reply.tool_calls)
            next(j for j in state['helper_jobs'] if j['id'] == job['id']).update(job)
            h._save(scope, state, owner, fence)
            if h.progress:
                h.progress('conversation_close_deferred', helper_id=job['id'])
            messages.append({"role": "user", "content": json.dumps(blocked[0][1])})
            continue
        calls = [{"id": c.id, "name": c.name, "arguments": c.arguments,
                  "journal_id": f"{job['id']}:m{state['model_calls']}:{c.id}"} for c in reply.tool_calls]
        start = len(state["messages"])
        state["messages"].append({"role": "assistant", "content": reply.content, "tool_calls": calls})
        h._save(scope, state, owner, fence)
        state, fence = h._execute_calls(scope, state, calls, h._tool_map(), owner, fence)
        messages.extend(deepcopy(state["messages"][start:]))
        # Strip audit channel tags from this worker's own isolated conversation.
        for m in messages:
            m.pop("helper_job_id", None)
        job["source_ids"] = list(dict.fromkeys([*job["source_ids"], *[
            e["id"] for e in state.get("evidence", []) if e.get("helper_job_id") == job["id"] and e.get("outcome") == "success"]]))
        if conversation_tools and not job.get('contact_ended') and _contact_ended(state, job):
            job['contact_ended'] = True
        if state.get("status") != "running":
            return _result(job, "incomplete", "Delegated execution reached a guarded stop; owner must inspect it.")
    return _result(job, "incomplete", "Delegated model budget reached; successful observations preserved.")


def _result(job, status, conclusion, **fields):
    return {"status": status, **({'conclusion':conclusion} if job['tool_names'] else {'proposal':conclusion}),
            "evidence_ids": list(job["source_ids"]), "model_calls": job["model_calls"],
            "tool_proposals": job["tool_proposals"], **fields}


def _prepare_worker(h, scope, owner, fence, job, messages):
    from .worker_preparation import prepare, apply_preparation
    state = h.store.load_case(scope)
    starting_calls = job['model_calls']

    def save():
        next(j for j in state['helper_jobs'] if j['id'] == job['id']).update(job)
        h._save(scope, state, owner, fence)

    def complete(context, specs):
        h._check_runtime()
        # Retain one worker turn and the owner's existing integration reserve.
        if (job['model_calls'] >= job['model_budget'] - 1
                or state['model_calls'] >= h.limits.max_model_calls - 2
                or job['tool_proposals'] >= job['tool_budget']
                or state['tool_calls'] >= h.limits.max_tool_calls):
            return None
        size = len(json.dumps({'messages': context, 'tools': [{'name': s.name, 'description': s.description, 'input_schema': s.input_schema} for s in specs]}, ensure_ascii=False))
        if h.limits.max_context_chars and size > h.limits.max_context_chars:
            return None
        job['model_calls'] += 1
        state['model_calls'] += 1
        save()
        try:
            reply = h.model.complete(context, specs, max_output_tokens=h.limits.max_output_tokens)
        except (UnknownOutcomeError, ConflictError):
            raise
        except Exception as exc:
            h._merge_usage(state, getattr(exc, 'usage', {}))
            save()
            return None  # Ordinary conversation can still proceed.
        h._merge_usage(state, reply.usage)
        save()
        return reply

    def apply(reply, context, current):
        count = len(reply.tool_calls)
        start = len(context)
        if (count > job['tool_budget'] - job['tool_proposals']
                or count > h.limits.max_tool_calls - state['tool_calls']):
            context.append({'role': 'user', 'content': json.dumps({
                'error': 'ValueError', 'detail': 'Preparation tool budget exceeded; nothing dispatched'})})
            result = {'local_preparation_applied': False, 'validation': {'error': 'tool_budget_exceeded'}}
        else:
            job['tool_proposals'] += count
            state['tool_calls'] += count
            result = apply_preparation(reply, context, current)
        # Same helper-owned durable journal as ordinary worker proposals, local only.
        state['messages'].extend({**deepcopy(m), 'helper_job_id': job['id']} for m in context[start:])
        save()
        return result

    result = prepare(messages, state, complete, apply=apply)
    result['model_calls'] = job['model_calls'] - starting_calls
    job['preparation_result'] = result
    save()
    if h.progress:
        h.progress('worker_preparation', helper_id=job['id'], role_id=job['role_id'],
                   model_calls=result['model_calls'], recorded=len(state.get('authorized_statements', [])),
                   statuses=[x['condition_status'] for x in state.get('authorized_statements', [])],
                   applied=bool(result.get('local_preparation_applied')))
