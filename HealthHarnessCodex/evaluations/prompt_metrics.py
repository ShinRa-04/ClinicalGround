"""Offline prompt baseline. Never prints saved dialogue, records or policy content.

Run from repository root: python -B -X utf8 HealthHarnessCodex/evaluations/prompt_metrics.py
Counts Unicode characters, not tokens; JSON sizes use compact ensure_ascii=False.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'HealthHarnessCodex'))
from health_harness_codex import roles, assignment
from health_harness_codex.models import Scope
from health_harness_codex.cm_guidance import PROGRAM_DESCRIPTION, CAPABILITY_LIMITS
from health_harness_codex.completion_contracts import build_completion_contract
from health_harness_codex import conversation_probe

SAVED = ROOT / 'HealthHarnessCodex/runs/20261103-cm-dm-low-coop-luna-03/cm/cm_dm_low_coop_001/attempt-1/state.sqlite'
FAMILIES = {
    'unsupported_facts_authority': r'\b(?:invent\w*|fabricat\w*|unsupported)\b',
    'completed_effects_delivery': r'\b(?:receipt\w*|deliver\w*|completed action\w*|observed effect\w*)\b',
    'guarantees_immediacy': r'\b(?:guarantee\w*|promis\w*|immediate\w*)\b',
    'pressure_participation': r'\b(?:pressur\w*|manipulat\w*|coerc\w*)\b',
    'consent_privacy_identity': r'\b(?:consent|privacy|identit\w*|permission\w*)\b',
    'unavailable_capability': r'\b(?:unavailable|absent|capability|capabilities|execution limit\w*)\b',
    'stop_decline': r'\b(?:stop|refus\w*|declin\w*|ended conversation)\b',
    'provenance_isolation': r'\b(?:provenance|cross.patient|source.backed|source.linked|case.local)\b',
}


def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def counts(text):
    # Family counts are lexical indicators, not a semantic count of prohibitions.
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    return {name: {'matches': len(re.findall(pattern, text, re.I)),
                   'matching_statements': sum(bool(re.search(pattern, s, re.I)) for s in sentences)}
            for name, pattern in FAMILIES.items()}


def offline_probe_metrics():
    """Rebuild current messages without inference/dispatch; export lengths and booleans only."""
    results=[]
    for name,turn in [('20261103-cm-dm-low-coop-luna-03',4),
                      ('20261103-cm-dm-low-coop-luna-01',7)]:
        run=ROOT/'HealthHarnessCodex/runs'/name
        db,state,job=conversation_probe.load_saved(run)
        before=hashlib.sha256(db.read_bytes()).hexdigest()
        tools=conversation_probe.build_tools(ROOT/'HealthHarnessCodex/runs/20261020-domain-contracts/cm/public-tool-schemas.json',Scope(**state['scope']))
        messages,_,_=conversation_probe.prepare_probe(state,job,turn,'current',tools)
        system=messages[0]['content']
        question=json.loads(messages[1]['content'])['question']
        authority=next(r['authority'] for r in roles.roles_for('CM') if r['id']=='CM-04')
        results.append({'run':name,'turn':turn,'mode':'current','system_chars':len(system),
            'question_chars':len(question),'system_plus_question_chars':len(system)+len(question),
            'cm04_authority_present':authority in system,
            'source_database_unchanged':before==hashlib.sha256(db.read_bytes()).hexdigest()})
    return results


def measure(saved=SAVED):
    scope = Scope('synthetic', 'goal-task', 'org', 'actor', 'patient', 'case')
    texts = {}
    owners = []
    for domain in ('PA', 'UM', 'CM'):
        for composition in ('combined', 'helpers'):
            value = roles.system_prompt(domain, scope, composition)
            texts[f'owner/{domain}/{composition}'] = value
            owners.append({'domain': domain, 'composition': composition, 'chars': len(value)})
    instruction = 'Complete intake, outreach, assessment and a finalized care plan.'
    state = {'scope': scope.to_dict(), 'instruction': instruction, 'domain': 'CM',
             'completion_contract': build_completion_contract(scope.task, 'cm', instruction, scope.to_dict()),
             'evidence': []}
    stages = []
    steps = [(None, None), ('cm_intake.open_case', {'case_id': 'case'}),
             ('cm_outreach.end_outreach_call', {'case_id': 'case', 'consent_obtained': True}),
             ('cm_assessment.complete_assessment', {'case_id': 'case'}),
             ('cm_care_plan.finalize', {'case_id': 'case', 'status': 'finalized'})]
    for tool, result in steps:
        if tool:
            state['evidence'].append({'id': f'ev:{len(state["evidence"])}', 'scope': scope.to_dict(),
                'outcome': 'success', 'tool': tool, 'effect': 'write', 'observed_result': result})
        packet = assignment.stage_guidance(state)
        phase = packet['current_responsibility']
        texts[f'stage/{phase}'] = packed(packet)
        stages.append({'phase': phase, 'guidance_chars': len(packet['guidance']),
                       'responsibility_packet_chars': len(packed(packet['responsibility_packet'])),
                       'full_packet_chars': len(packed(packet))})
    with sqlite3.connect(saved.resolve().as_uri() + '?mode=ro', uri=True) as conn:
        conn.execute('PRAGMA query_only=ON')
        rows = conn.execute('SELECT state_json FROM cases').fetchall()
        if len(rows) != 1:
            raise ValueError('Expected exactly one saved case')
        messages = json.loads(rows[0][0])['helper_jobs'][0]['messages'][:2]
    saved_metrics = []
    for index, msg in enumerate(messages):
        content = msg['content']
        if not isinstance(content, str):
            raise TypeError('Expected saved text content')
        texts[f'saved/CM-04/{index}'] = content
        saved_metrics.append({'message_index': index, 'role': msg['role'], 'chars': len(content),
            'PROGRAM_DESCRIPTION': content.count(PROGRAM_DESCRIPTION.strip()),
            'CAPABILITY_LIMITS': content.count(CAPABILITY_LIMITS.strip())})
    question = json.loads(messages[1]['content'])['question']
    saved_metrics.append({'message_index': '1/question (subset)', 'role': 'question', 'chars': len(question),
        'PROGRAM_DESCRIPTION': question.count(PROGRAM_DESCRIPTION.strip()),
        'CAPABILITY_LIMITS': question.count(CAPABILITY_LIMITS.strip())})
    paths = ['HealthHarnessCodex/health_harness_codex/' + n + '.py' for n in
             ('roles', 'assignment', 'cm_guidance', 'working_set', 'planning', 'dialogue_worker', 'closure', 'recovery_audit', 'terminal_review')]
    inventory = {}
    for path in paths:
        tree = ast.parse((ROOT / path).read_text(encoding='utf-8'))
        fragments = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)
                     and isinstance(n.value, str) and len(n.value) > 40 and ' ' in n.value]
        inventory[path] = counts('\n'.join(fragments))
    return {'measurement': 'Unicode chars; compact JSON packets; exact guidance substring repetitions',
            'synthetic_scope': scope.to_dict(), 'owner_prompts': owners, 'cm_stages': stages,
            'saved_messages': saved_metrics, 'saved_database': str(saved.relative_to(ROOT)),
            'current_offline_probes':offline_probe_metrics(),
            'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
            'caution_method': 'Overlapping lexical families; matches plus sentence/newline units containing each family. '
                              'Positive duties also match. Rendered surfaces are counted separately, not one conversation; '
                              'other dynamic paths and tool schemas are not covered. No semantic deduplication claim.',
            'caution_patterns': FAMILIES,
            'caution_by_surface': {k: counts(v) for k, v in texts.items()},
            'caution_rendered_totals': counts('\n'.join(texts.values())),
            'source_literal_inventory_method': 'AST string constants longer than 40 chars containing a space, '
                'counted once per syntax occurrence. Candidate model-facing text includes diagnostics/docstrings; '
                'not all is delivered in one call. Concatenated references are not expanded. '
                'This separate static inventory is not added to rendered counts.',
            'caution_source_literal_inventory': inventory}


def table(result):
    lines = ['| Domain | Combined chars | Helpers chars |', '| --- | ---: | ---: |']
    for domain in ('PA', 'UM', 'CM'):
        values = [r['chars'] for r in result['owner_prompts'] if r['domain'] == domain]
        lines.append(f'| {domain} | {values[0]} | {values[1]} |')
    lines += ['', '| CM phase | Guidance | Role packet | Full packet |', '| --- | ---: | ---: | ---: |']
    lines += [f"| {r['phase']} | {r['guidance_chars']} | {r['responsibility_packet_chars']} | {r['full_packet_chars']} |" for r in result['cm_stages']]
    lines += ['', '| Saved CM-04 message | Chars | PROGRAM_DESCRIPTION | CAPABILITY_LIMITS |', '| --- | ---: | ---: | ---: |']
    lines += [f"| {r['role']} [{r['message_index']}] | {r['chars']} | {r['PROGRAM_DESCRIPTION']} | {r['CAPABILITY_LIMITS']} |" for r in result['saved_messages']]
    lines += ['', '| Caution family (rendered surfaces) | Lexical matches | Matching statements |',
              '| --- | ---: | ---: |']
    lines += [f"| {family} | {value['matches']} | {value['matching_statements']} |"
              for family, value in result['caution_rendered_totals'].items()]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Write sanitized Markdown with full JSON results')
    parser.add_argument('--after-report',type=Path,help='Append after measurements, preserving the Phase 0 record')
    args = parser.parse_args()
    result = measure()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('\n' + table(result))
    if args.after_report:
        before={('PA','combined'):22195,('PA','helpers'):16529,('UM','combined'):21992,
            ('UM','helpers'):16331,('CM','combined'):27613,('CM','helpers'):21469}
        rows=['## Phase 2 after measurements','',
            'Offline current-code measurement, 2026-11-03. The Phase 0 tables above remain historical. Saved message sizes in the script output are historical; the current worker sizes below come from prepare_probe, without inference or dispatch.','',
            '| Domain / composition | Before | After | Growth |','| --- | ---: | ---: | ---: |']
        for row in result['owner_prompts']:
            old=before[row['domain'],row['composition']]
            rows.append(f"| {row['domain']} / {row['composition']} | {old} | {row['chars']} | {(row['chars']/old-1)*100:+.2f}% |")
            assert row['chars']<=old*1.15,row
        rows+=['','| Offline current probe | Turn | System | Question | Sum | Exact authority / DB unchanged |',
            '| --- | ---: | ---: | ---: | ---: | --- |']
        for row in result['current_offline_probes']:
            rows.append(f"| {row['run']} | {row['turn']} | {row['system_chars']} | {row['question_chars']} | {row['system_plus_question_chars']} | {row['cm04_authority_present']} / {row['source_database_unchanged']} |")
            assert row['system_plus_question_chars']<=6572+4408
            assert row['question_chars']<=3000 and row['cm04_authority_present'] and row['source_database_unchanged']
        rows+=['','Command: `python -X utf8 HealthHarnessCodex/evaluations/prompt_metrics.py --after-report Progress/ROLE_PROMPT_BASELINE.md`. Character counts are Unicode, not tokens. Full sanitized results stay in local runs/; no saved record, dialogue or protected policy text is exported.','']
        text=args.after_report.read_text(encoding='utf-8').split('## Phase 2 after measurements')[0].rstrip()
        args.after_report.write_text(text+'\n\n'+'\n'.join(rows),encoding='utf-8')
    if args.report:
        command = 'python -B -X utf8 HealthHarnessCodex/evaluations/prompt_metrics.py --report Progress/ROLE_PROMPT_BASELINE.md'
        args.report.write_text('# Role prompt baseline — Phase 0\n\nOffline measurement on 2026-11-03. '
            'No model, Docker, dataset trial or judge was invoked. Saved database opened read-only; '
            'only lengths/counts are exported, with no dialogue or handbook text.\n\n'
            'Command from `C:\\Projects\\BigData`:\n\n```powershell\n' + command + '\n```\n\n'
            + table(result) + '\n\nCaution counts cover the six owner prompts, five stage packets and two saved worker messages. '
            'Families overlap and include positive statements; these are reproducible lexical indicators, '
            'not a claim to classify every semantic caution in every possible runtime path. '
            'Synthetic stage fixtures follow the successful same-scope evidence pattern in tests/test_goal_planning.py. '
            'Packet serialization is defined by this script; caller formatting can change delivered size. '
            'Source hashes pin this baseline; no patient identifiers or saved content are exported.\n\n'
            'A separate AST inventory covers candidate model-facing literals in nine runtime modules, '
            'including reviewer text; its counts include diagnostic/docstring false positives and do not '
            'expand imported constants. This is supplementary static evidence, not delivered-message size.\n\n'
            '## Complete sanitized results\n\n```json\n' + json.dumps(result, ensure_ascii=False, indent=2) + '\n```\n', encoding='utf-8')


if __name__ == '__main__':
    main()
