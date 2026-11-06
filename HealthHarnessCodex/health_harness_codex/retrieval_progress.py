"""Case-local source coverage, independent of retrieval query/ranking metadata.

Only recognized successful retrieval shapes participate. Versioned source ranges
allow subset pages to reuse earlier coverage; unversioned sources require exact
passage hashes. This is feedback only and never filters results or dispatch.
"""
from __future__ import annotations

import hashlib
import json

from .working_set import business, canonical


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _passage(source, part, offset=0):
    text = part.get('text')
    identity = source.get('path') or source.get('document_id')
    if not isinstance(text, str) or not identity:
        return None
    start = part.get('start', offset)
    if not isinstance(start, int) or start < 0:
        return None
    # Measure actual returned text, never a nominal end that may include truncation.
    return {'source': _hash([identity, source.get('page')]),
            'version': source.get('sha256'), 'start': start, 'end': start + len(text),
            'text_hash': _hash(text)}


def _passages(name, arguments, result):
    value = business(result)
    if not isinstance(value, dict) or 'error' in value:
        return None
    if name == 'workspace.read_file':
        part = _passage(value, value, value.get('offset_chars', arguments.get('offset_chars', 0)))
        return [part] if part else None
    if name == 'workspace.read_many':
        items = value.get('items')
        if not isinstance(items, list) or not items:
            return None
        parts = []
        for item in items:
            if not isinstance(item, dict) or item.get('operation') != 'read_file':
                return None
            nested = _passages('workspace.read_file', {}, item.get('result'))
            if nested is None:
                return None
            parts.extend(nested)
        return parts
    if name != 'workspace.hybrid_search':
        return None
    if not isinstance(value.get('documents'), list) or not isinstance(value.get('matches'), list):
        return None
    parts = []
    for doc in value['documents']:
        if not isinstance(doc, dict):
            return None
        source = doc.get('source', {}) | {'document_id': doc.get('document_id')}
        for part in [doc.get('header', {}), *doc.get('qualifying_sections', [])]:
            passage = _passage(source, part)
            if passage is None:
                return None
            parts.append(passage)
    for match in value['matches']:
        if not isinstance(match, dict):
            return None
        passage = _passage(match.get('source', {}) | {'document_id': match.get('document_id')}, match)
        if passage is None:
            return None
        parts.append(passage)
    if not parts:
        # Rewording a query with no returned sources adds no source information.
        parts = [{'source': _hash(['empty_search', arguments.get('path')]),
                  'version': None, 'start': 0, 'end': 0, 'text_hash': _hash('')}]
    return parts


def observe_retrieval(state, name, arguments, result, evidence_id, outcome):
    if outcome != 'success':
        return None
    parts = _passages(canonical(name), arguments, result)
    if parts is None:
        return None
    seen = state.setdefault('retrieval_source_progress', {})
    new = False
    first = None
    # Compare the entire operation against PREVIOUS operations, not its own headers.
    for part in parts:
        key = _hash([part['source'], part['version']])
        previous = seen.get(key, [])
        exact = next((p for p in previous if all(p[k] == part[k] for k in
                     ('start', 'end', 'text_hash'))), None)
        covered = exact is not None
        if not covered and part['version'] and part['end'] > part['start']:
            cursor = part['start']
            for p in sorted(previous, key=lambda p: p['start']):
                # A changed exact span must not be hidden even if a source's version is stale.
                if p['start'] == part['start'] and p['end'] == part['end']:
                    continue
                if p['start'] <= cursor < p['end']:
                    cursor = p['end']
                if cursor >= part['end']:
                    covered = True
                    break
        new |= not covered
        if covered and first is None and previous:
            first = (exact or previous[0])['evidence_id']
    for part in parts:
        key = _hash([part['source'], part['version']])
        previous = seen.setdefault(key, [])
        if not any(all(p[k] == part[k] for k in ('start', 'end', 'text_hash')) for p in previous):
            previous.append({**{k: part[k] for k in ('start', 'end', 'text_hash')},
                             'evidence_id': evidence_id})
    return {'new_source_information': new, 'first_matching_evidence_id': first}
