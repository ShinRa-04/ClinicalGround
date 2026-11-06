"""Bounded local speaking preparation shared by runtime workers and probes."""
from copy import deepcopy
from dataclasses import asdict
import json
from .models import IsolationError

INSTRUCTION = (
    "Preparation only: prepare policy-backed statements this role will likely need to speak for its "
    "program or decision: purpose, services relevant to the counterparty's known priorities, cost/fees, "
    "contact cadence, information use/sharing, voluntariness/withdrawal and the counterparty's own choices "
    "(contact method/times, declining questions). Include policy-supported "
    "coordination or referrals answering those priorities, framed as available after enrollment or the "
    "decision, alongside honest execution limits. Cite retrieved policy and records; decide each condition "
    "under the existing judgment rule. Judge by what those records can show; do not demand record types "
    "the system lacks. met cites the records satisfying the condition; not_met cites a record contradicting "
    "it (silence is not contradiction). Use unknown for missing or conflicting deciding records, naming settling_record_type "
    "and whether that record type exists in this system (settling_record_available). Also prepare a direct "
    "decision invitation for when questions are answered. In information_needs, list what later stages' "
    "retrieved standards require from the counterparty (each cited), to gather in grouped turns once they "
    "agree, ordered by what later stages cannot complete without; omit facts the records already show. One need per required instrument or record section; never bundle them. Name any structured instrument a standard "
    "requires: its items must be asked; an informal summary question does not administer it. Record it again "
    "when you retrieve more standards. If policy sources are "
    "missing, record an empty list or supported unknowns; never fabricate. Use only "
    "case.record_authorized_statements once, then stop; do not speak or propose other tools. "
    "This is actor preparation, not policy."
)

def apply_preparation(reply, context, state):
    """Only this local write is applied; validation feedback matches engine case.* errors."""
    from .authorized_statements import SPEC, record, pin
    from .providers import validate_reply_structure, ModelResponseFormatError
    calls = [asdict(c) for c in reply.tool_calls]
    context.append({'role': 'assistant', 'content': reply.content, 'tool_calls': calls})
    try:
        validate_reply_structure(reply, {SPEC.name: SPEC})
        if len(calls) != 1 or calls[0]['name'] != SPEC.name:
            raise ValueError('preparation requires exactly one authorized-statements proposal; nothing dispatched')
        result = record(state, calls[0]['arguments'])
        pin(context, state)
    except (ValueError, KeyError, IsolationError, ModelResponseFormatError) as exc:
        result = {'error': type(exc).__name__, 'detail': str(exc)}
    for call in calls:
        context.append({'role': 'tool', 'tool_call_id': call['id'], 'name': call['name'],
                        'content': json.dumps(result, ensure_ascii=False)})
    if not calls:
        context.append({'role': 'user', 'content': json.dumps(result, ensure_ascii=False)})
    return {'statements': deepcopy(state.get('authorized_statements', [])), 'validation': result,
            'usage': reply.usage, 'tool_proposals': calls,
            'local_preparation_applied': 'error' not in result, 'external_tools_dispatched': 0}


def prepare(messages, state, complete, *, apply=apply_preparation, max_attempts=2):
    """complete may return None when a caller's shared/job budget cannot fit work."""
    from .authorized_statements import SPEC, pin
    context = deepcopy(messages)
    pin(context, state)
    context.append({'role': 'user', 'content': INSTRUCTION})
    attempts = []
    for _ in range(min(2, max_attempts)):
        reply = complete(context, [SPEC])
        if reply is None:
            break
        attempts.append(apply(reply, context, state))
        if attempts[-1]['local_preparation_applied']:
            break
    pin(messages, state)
    return {**(attempts[-1] if attempts else {}), 'attempts': attempts, 'model_calls': len(attempts)}
