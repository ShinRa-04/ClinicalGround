"""Link observed case-file excerpts to actor-listed attachments, without I/O."""
from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath

from .working_set import business, canonical


class AttachmentSourceError(ValueError):
    pass


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def _path(value, case):
    if not isinstance(value, str) or not value or any(p in {'.', '..'} for p in value.split('/')):
        return None
    root = PurePosixPath('/logs/artifacts/workspaces') / case
    path = PurePosixPath(value)
    if not path.is_absolute():
        path = root.parent / path if path.parts[0] == case else root / path
    return str(path) if path.is_relative_to(root) else None


def _documents(value, pointer=''):
    if isinstance(value, dict):
        if 'case_id' in value and 'artifact_type' in value and ('relative_path' in value or 'path' in value):
            yield pointer, value
        for key, child in value.items():
            escaped = str(key).replace('~', '~0').replace('/', '~1')
            yield from _documents(child, pointer + '/' + escaped)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _documents(child, pointer + '/' + str(index))


def _file_reads(item):
    name = canonical(item.get('tool', ''))
    data = business(item['observed_result'])
    if name in {'workspace.read_file', 'workspace.read_pdf'}:
        yield '', data
    elif name == 'workspace.read_many' and isinstance(data, dict):
        for index, child in enumerate(data.get('items', [])):
            if child.get('operation') in {'read_file', 'read_pdf'}:
                yield f'/items/{index}/result', child.get('result')


def attachment_receipts(state, item, actual_scope):
    """Only exact scoped paths and typed actor metadata establish the link.

    Filenames alone, arbitrary local files and generated workspace drafts do
    not qualify. These are provenance receipts, not clinical truth judgments.
    A batch may contain fixed references alongside verified attachments.
    """
    case = actual_scope.get('case')
    if not isinstance(case, str) or not case or '/' in case or case in {'.', '..'}:
        raise AttachmentSourceError('an observed case binding is required for attachment evidence')
    listing = {}
    authored = set()
    for source in state.get('evidence', []):
        if source.get('outcome') != 'success' or source.get('scope') != state.get('scope'):
            continue
        name = canonical(source.get('tool', ''))
        data = business(source.get('observed_result'))
        if name == 'workspace.write_file' and isinstance(data, dict):
            authored.add(_path(data.get('path'), case))
        method = name.partition('.')[2]
        if name.startswith(('workspace.', 'case.')) or not method.startswith(('get', 'read', 'list', 'search')):
            continue
        for pointer, doc in _documents(data):
            if doc.get('case_id') != case or doc.get('artifact_type') not in {'document', 'clinical_document', 'intake_request_form'}:
                continue
            if doc.get('patient_id') is not None and doc['patient_id'] != actual_scope.get('patient'):
                continue
            path = _path(doc.get('relative_path', doc.get('path')), case)
            if path and isinstance(doc.get('id'), str) and doc['id']:
                listing.setdefault(path, []).append((source, pointer, doc))
    receipts = []
    for pointer, data in _file_reads(item):
        if not isinstance(data, dict) or 'error' in data:
            continue
        raw_path = data.get('path', '')
        if isinstance(raw_path, str) and raw_path.startswith('/workspace/skills/managed-care-operations-handbook/'):
            continue  # A fixed reference is not a patient's clinical attachment.
        path = _path(raw_path, case)
        digest = data.get('sha256')
        text_present = bool(data.get('text')) or any(isinstance(p, dict) and p.get('text') for p in data.get('pages', []))
        valid_hash = isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)
        if not path or path in authored or path not in listing or not valid_hash or not text_present:
            raise AttachmentSourceError('case file evidence must be an exact actor-listed attachment with retrieved text and SHA-256; '
                'read the actor document relative_path, not an unlisted filename alias or generated draft')
        candidates = [(source, loc, doc) for source, loc, doc in listing[path]
                      if doc.get('sha256') in (None, digest)]
        if not candidates:
            raise AttachmentSourceError('retrieved attachment hash differs from its actor listing')
        source, loc, doc = candidates[0]
        receipts.append({'evidence_id': item['id'], 'result_pointer': pointer, 'path': path,
                         'sha256': digest, 'observation_sha256': _digest(data),
                         'listing_source_id': source['id'], 'listing_pointer': loc,
                         'document_id': doc['id'], 'listing_sha256': _digest(doc)})
    if not receipts:
        raise AttachmentSourceError('no verified actor-listed clinical attachment text exists in this source')
    return receipts
