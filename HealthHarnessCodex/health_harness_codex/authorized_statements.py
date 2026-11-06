"""Actor-authored preparation: shape and source provenance only."""
from copy import deepcopy

from .models import IsolationError, Scope, ToolSpec
from .schema import validate_arguments
from .planning import source

NAME = 'case.record_authorized_statements'
SPEC = ToolSpec(NAME, 'Replace your source-linked speaking preparation. Interpretations, not policy or new evidence; optional before speaking.', {
    'type': 'object', 'additionalProperties': False, 'required': ['statements'],
    'properties': {'statements': {'type': 'array', 'maxItems': 6, 'items': {
        'type': 'object', 'additionalProperties': False,
        'required': ['text', 'source_evidence_id', 'policy_condition', 'condition_status', 'condition_evidence_ids'],
        'properties': {
            'text': {'type': 'string', 'minLength': 1, 'maxLength': 600},
            'source_evidence_id': {'type': 'string', 'minLength': 1, 'maxLength': 160},
            'policy_condition': {'anyOf': [{'type': 'null'}, {'type': 'string', 'minLength': 1, 'maxLength': 300}]},
            'condition_status': {'type': 'string', 'enum': ['met', 'not_met', 'not_applicable', 'unknown']},
            'condition_evidence_ids': {'type': 'array', 'maxItems': 8, 'items': {'type': 'string', 'minLength': 1, 'maxLength': 160}},
            'scope_note': {'type': 'string', 'maxLength': 300},
            'settling_record_type': {'type': 'string', 'maxLength': 200},
            'settling_record_available': {'type': 'boolean'}
        }}},
        'information_needs': {'type': 'array', 'maxItems': 12, 'items': {
            'type': 'object', 'additionalProperties': False, 'required': ['need', 'source_evidence_id'],
            'properties': {
                'need': {'type': 'string', 'minLength': 1, 'maxLength': 400},
                'source_evidence_id': {'type': 'string', 'minLength': 1, 'maxLength': 160}}}}}}, effect='write')


def record(state, arguments):
    validate_arguments(SPEC, arguments, Scope(**state['scope']))
    cited = [i for item in arguments['statements'] for i in (item['source_evidence_id'], *item['condition_evidence_ids'])]
    cited += [item['source_evidence_id'] for item in arguments.get('information_needs', [])]
    # Report every unusable citation at once so one correction can fix them all.
    problems = []
    for evidence_id in dict.fromkeys(cited):
        try:
            source(state, evidence_id)
        except IsolationError as exc:
            problems.append(str(exc))
    if problems:
        raise IsolationError(' | '.join(problems)[:3000])
    for item in arguments['statements']:
        if item['condition_status'] == 'met' and not item['condition_evidence_ids']:
            raise ValueError('met requires condition_evidence_ids: cite the observed record(s) that satisfy the '
                             'condition (for example the record establishing the relevant status), then keep met')
        if item['condition_status'] == 'not_met' and not item['condition_evidence_ids']:
            raise ValueError('not_met requires condition_evidence_ids citing an observed record that contradicts the '
                             'condition; a record that is silent on it is not a contradiction. Re-judge as met '
                             '(citing supporting records) or unknown (naming an available record that is missing)')
        if item['condition_status'] == 'not_applicable' and item.get('policy_condition'):
            raise ValueError('a statement with a policy_condition must decide it (met, not_met or unknown); '
                             'not_applicable is only for unconditional statements')
        if item['condition_status'] == 'unknown':
            if not item.get('settling_record_type') or 'settling_record_available' not in item:
                raise ValueError('unknown requires settling_record_type and settling_record_available: name the record '
                                 'that would settle the condition and whether that record type exists in this system')
            if item['settling_record_available'] is False:
                raise ValueError('unknown rests on a record type this system does not hold; re-judge the condition from the '
                                 'records it does hold (met or not_met), or name an available record that is missing or conflicting')
    state['authorized_statements'] = deepcopy(arguments['statements'])
    state['information_needs'] = deepcopy(arguments.get('information_needs', []))
    state['authorized_statements_source_count'] = len(state.get('evidence', []))
    return {'recorded': len(arguments['statements']), 'information_needs': len(state['information_needs']),
            'creates_evidence': False,
            'interpretation_verified': False}


def view(state):
    return {'kind': 'actor_source_linked_preparation_not_policy',
            'statements': deepcopy(state.get('authorized_statements', [])),
            'information_needs': deepcopy(state.get('information_needs', [])),
            'interpretation_verified': False}


def pin(messages, state):
    """Replace the current context pin without accumulating stale preparation."""
    import json
    if 'authorized_statements' in state:
        marker = chr(10) + 'Actor preparation (not policy): '
        base = messages[0]['content'].split(marker, 1)[0]
        messages[0]['content'] = base + marker + json.dumps(view(state), ensure_ascii=False, separators=(',', ':'))
