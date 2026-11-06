"""Case-local exact-exchange repetition stop, separate from patient choice."""
import hashlib
import json
import unicodedata

from .working_set import business, canonical


def observe(state, name, arguments, result, evidence_id, outcome):
    if canonical(name) != 'cm_outreach.send_message' or outcome != 'success':
        return False
    data = business(result)
    if not isinstance(data, dict):
        return False
    session = arguments.get('session_id')
    sent, reply = arguments.get('message'), data.get('patient_response')
    if not all(isinstance(v, str) and v.strip() for v in (session, sent, reply)):
        return False
    # Preserve punctuation/numbers: normalization is formatting, not a clinical
    # or semantic equivalence judgment. Never ingest private persona content.
    pair = [' '.join(unicodedata.normalize('NFKC', v).casefold().split()) for v in (sent, reply)]
    digest = hashlib.sha256(json.dumps(pair, ensure_ascii=False).encode()).hexdigest()
    histories = state.setdefault('dialogue_exchange_history', {})
    history = histories.setdefault(session, [])
    if any(x['evidence_id'] == evidence_id for x in history):
        return False  # Journal readback is not another exchange.
    history.append({'sha256': digest, 'evidence_id': evidence_id})
    del history[:-3]
    if len(history) == 3 and len({x['sha256'] for x in history}) == 1:
        state.setdefault('dialogue_repetition_stop', {
            'reason': 'three_consecutive_identical_exchanges', 'session_id': session,
            'evidence_ids': [x['evidence_id'] for x in history],
            'patient_refusal_inferred': False, 'patient_stop_signal_inferred': False,
            'requested_goal_achieved': False})
        return True
    return False


def blocked(state, name):
    stop = state.get('dialogue_repetition_stop')
    if not stop or canonical(name) not in {'cm_outreach.start_outreach_call', 'cm_outreach.send_message'}:
        return None
    return {'error': 'conversation_stopped_for_repetition', 'known_not_dispatched': True,
            'stop': stop, 'instruction': 'Three identical completed exchanges repeated. Further patient dialogue '
            'is stopped for this attempt, including opening a replacement session. Do not infer refusal, consent '
            'or a patient stop signal. Record the actual dialogue and this harness stop separately. Other '
            'permitted documentation/investigation remains available; do not claim the requested goal achieved.'}
