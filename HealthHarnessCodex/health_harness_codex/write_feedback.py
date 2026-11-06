"""Factual payload/result shape feedback; never decides clinical content."""
from .schema import tool_parameter_schema
from .working_set import business, canonical


def _collection(schema):
    if not isinstance(schema, dict): return False
    return (schema.get('type') in ('array', 'object')
            or any(_collection(s) for s in schema.get('anyOf', []) + schema.get('oneOf', [])))


def _empty(value, path=''):
    if isinstance(value, (dict, list)) and not value:
        yield path
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _empty(child, path + '/' + str(key).replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        for index, child in enumerate(value): yield from _empty(child, path + '/' + str(index))


def assess_write_payload(spec, arguments, result, evidence_id):
    if spec.effect != 'write': return None
    method = canonical(spec.name).partition('.')[2]
    if method.startswith(('get', 'read', 'list', 'search', 'check', 'calculate')): return None
    if not isinstance(result, dict) or 'error' in result or result.get('isError'): return None
    schema = tool_parameter_schema(spec.input_schema)
    omitted = [name for name, child in schema.get('properties', {}).items()
               if name not in arguments and _collection(child)]
    empty = list(_empty(business(result)))[:32]
    if not omitted or not empty: return None
    return {'source_evidence_id': evidence_id, 'omitted_collection_inputs': omitted,
            'observed_empty_collections': empty, 'creates_evidence': False,
            'interpretation_verified': False,
            'instruction': 'The API accepted this operation, but these payload fields were not sent and these returned collections are empty. '
                'Narrative plans do not populate tool arguments. If you intend to save content, supply its declared payload field and verify the readback. '
                'An empty draft may be intentional; code does not infer that content is mandatory or choose its clinical values.'}
