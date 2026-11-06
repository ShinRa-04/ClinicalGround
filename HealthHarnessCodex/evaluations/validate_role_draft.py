"""Validate the approved role record offline against final and pinned pre-revision catalogs."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASELINE_REVISION='514a890f7d1f03537de7c1b5f87ec149ceba9306'
EXPECTED_REDEFINED = set('CM-01 CM-03 CM-04 CM-09 CM-11 CM-13 CM-14 CM-15 CM-16 CM-20 PA-09 PA-14 PA-15 PA-16 UM-08 UM-13 UM-14 UM-17'.split())
VERBS = r'(?:approve|decide|issue|recommend|represent|seek|conduct|send|record|review|route|choose|apply|assess|plan|coordinate|explain|document|authorize|finalize|submit|determine|interpret|select|accept|reject)'


def validate():
    def read(path):
        return json.loads((ROOT / path).read_text(encoding='utf-8'))
    draft = read('Progress/role_authority_draft.json')
    catalog = {r['id']: r for r in read('HealthHarnessCodex/health_harness_codex/data/micro_roles.json')}
    original = {r['id']:r for r in json.loads(subprocess.check_output(
        ['git','show',BASELINE_REVISION+':HealthHarnessCodex/health_harness_codex/data/micro_roles.json'],cwd=ROOT))}
    hospital = {r['id'] for r in read('Plan/HealthcareRoles/data/roles.json')}
    errors = []
    suspects = []
    ids = [r.get('id') for r in draft]
    if len(ids) != 66 or len(set(ids)) != 66 or set(ids) != set(catalog):
        errors.append('Draft must contain exactly the 66 distinct catalog IDs')
    if {r['id'] for r in draft if 'changes' in r} != EXPECTED_REDEFINED:
        errors.append('Redefinition set differs from the explicit Phase 1 task')
    for row in draft:
        rid = row['id']
        if not isinstance(row['hospital_roles'], list) or any(h not in hospital for h in row['hospital_roles']):
            errors.append(f'{rid}: invalid hospital mapping')
        if not row.get('hospital_source_note') or (not row['hospital_roles'] and row['hospital_source_note'] != 'code-only safeguard'):
            errors.append(f'{rid}: missing mapping explanation')
        expected = 'executing_worker' if rid in {'CM-04', 'SH-10'} else 'prompt_contract'
        if row.get('status_label') != expected:
            errors.append(f'{rid}: incorrect descriptive status label')
        for field in ('authority', 'approach'):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > (200 if field=='approach' else 160 if rid!='CM-04' else 400):
                errors.append(f'{rid}/{field}: empty, non-text or over the approved length cap')
                continue
            if re.search(r'\b(?:pa|um|cm)_[a-z0-9_]+|CM-(?:CASE|PAT)', value, re.I):
                errors.append(f'{rid}/{field}: prohibited task/patient identifier')
            # Flag name-like proper nouns for human review without reading saved patient data.
            # Arbitrary names cannot be proven absent by a finite deny-list.
            for match in re.finditer(r'\b[A-Z][a-z]+\b', value):
                prefix = value[:match.start()].rstrip()
                if prefix and prefix[-1] not in '.!?':
                    errors.append(f'{rid}/{field}: unexpected name-like proper noun (review required)')
                    break
            if re.search(r'\b(?:patient|member)\s+(?:named|name\s*:)\b', value, re.I):
                errors.append(f'{rid}/{field}: personal-name attribution')
        if 'within the assigned task and retrieved policy' in row['authority']:
            errors.append(f'{rid}: repeated common qualification')
        if not re.match(r'^[A-Z][a-z]+(?:s|es)\b',row['authority']):
            errors.append(f'{rid}: authority must start with an active mandate')
        if row.get('model_visible') != catalog[rid]['model_visible']:
            errors.append(f'{rid}: invalid model visibility')
        for field in ('hospital_roles','authority','approach','status_label'):
            if row[field] != catalog[rid][field]:errors.append(f'{rid}/{field}: final catalog differs')
        authority = row['authority']
        # A chain with at least two comma-separated verb continuations is suspect.
        chains = re.findall(rf',\s*(?:(?:and|or)\s+)?{VERBS}\b', authority, re.I)
        if rid != 'CM-04' and (len(chains) > 1 or re.search(r'(?:^|\s)(?:[1-9][.)]|[-*])\s+' + VERBS, authority, re.I)):
            suspects.append({'id': rid, 'reason': 'possible enumerated authority action list'})
        for field, change in row.get('changes', {}).items():
            if field not in catalog.get(rid, {}) or change.get('old') != original[rid][field]:
                errors.append(f'{rid}/{field}: old value does not match pinned pre-revision catalog')
            if change.get('old') == change.get('new'):
                errors.append(f'{rid}/{field}: no actual redefinition')
            if field == 'boundary':
                errors.append(f'{rid}: boundary edits require separate protection review; this draft preserves all')
    result = {'status': 'FAIL' if errors else 'PASS', 'ids': len(ids),
        'mapped': sum(bool(r['hospital_roles']) for r in draft),
        'unmapped_code_only': sum(not r['hospital_roles'] for r in draft),
        'redefined': len(EXPECTED_REDEFINED),
        'max_authority_chars': max(len(r['authority']) for r in draft),
        'max_approach_chars': max(len(r['approach']) for r in draft),
        'errors': errors, 'authority_action_list_suspects': suspects,
        'limits': 'Identifier patterns and unexpected proper nouns checked in proposed authority/approach. '
                  'This cannot prove absence of all personal names or semantic task specificity; human review remains required. '
                  'Action-list detection is heuristic and suspects do not fail validation.'}
    print(json.dumps(result, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(validate())
