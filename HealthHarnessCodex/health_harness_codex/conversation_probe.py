"""Repeated, non-dispatching replay of a saved CM-04 conversation boundary."""
from __future__ import annotations

import argparse
from contextlib import closing
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess

from .dialogue_worker import before_send
from .engine import Harness, _LOCAL_SPECS
from .models import IsolationError, Limits, ModelReply, Scope, ToolCall, ToolSpec
from .store import CaseStore
from .working_set import business, canonical


class NoDispatchTools:
    """Only a schema inventory; even reads must never reach a real tool."""

    def __init__(self, specs):
        self.specs = list(specs)

    def list_tools(self):
        return list(self.specs)

    def call(self, name, arguments):
        raise RuntimeError('Conversation probes cannot dispatch tools')


def load_saved(run):
    paths = list(Path(run).glob('cm/*/attempt-1/state.sqlite'))
    if len(paths) != 1:
        raise ValueError('Expected exactly one CM attempt-1/state.sqlite')
    with closing(sqlite3.connect(paths[0].resolve().as_uri() + '?mode=ro', uri=True)) as db:
        rows = db.execute('SELECT state_json FROM cases').fetchall()
    candidates = []
    for row in rows:
        state = json.loads(row[0])
        for job in state.get('helper_jobs', []):
            if job.get('role_id') == 'CM-04' and job.get('invocation') == 'cm_dialogue_worker':
                candidates.append((state, job))
    if len(candidates) != 1:
        raise ValueError('Expected exactly one CM-04 cm_dialogue_worker conversation')
    return paths[0], *candidates[0]


def select_turn(messages, turn):
    """Count successful send-message replies, not transcript copies or MCP duplicates."""
    if type(turn) is not int or turn < 1:
        raise ValueError('turn must be a positive patient-reply number')
    sends = set()
    count = 0
    for index, message in enumerate(messages):
        if message.get('role') == 'assistant':
            sends.update(c['id'] for c in message.get('tool_calls', [])
                         if canonical(c['name']) == 'cm_outreach.send_message')
        if message.get('role') != 'tool' or message.get('tool_call_id') not in sends:
            continue
        observation = json.loads(message['content'])
        result = business(observation.get('observed_result'))
        if observation.get('outcome') != 'success' or not isinstance(result, dict):
            continue
        reply = result.get('patient_response')
        if isinstance(reply, str):
            count += 1
            if count == turn:
                return deepcopy(messages[:index + 1]), reply
    raise ValueError(f'Patient reply {turn} unavailable; found {count}')


def build_tools(schema_path, scope):
    # Construction/listing only: DockerWorkspaceTools does no I/O until call().
    from .docker_bridge import DockerMCPClient, DockerWorkspaceTools
    entries = json.loads(Path(schema_path).read_text(encoding='utf-8'))
    specs = [ToolSpec(e['alias'], e['description'], e['schema'],
                      effect='read' if e['actual'] in DockerMCPClient.AUDITED_READS else e['effect'])
             for e in entries]
    workspace = DockerWorkspaceTools('probe-never-dispatched', '/probe', scope)
    return NoDispatchTools([*specs, *workspace.list_tools()])


class _Captured(BaseException):
    """Stop offline construction before any completion or local preparation."""


class _Capture:
    def __init__(self):
        self.messages = None
        self.specs = None

    def complete(self, messages, tools, **kwargs):
        if self.messages is not None:
            raise AssertionError('Prompt capture must finish on its first call')
        self.messages, self.specs = deepcopy(messages), list(tools)
        raise _Captured()


def rebuild_context(saved, job, tools):
    """Start from a fresh store; copy only pre-outreach evidence and task metadata."""
    scope = Scope(**saved['scope'])
    initial = json.loads(job['messages'][1]['content'])
    session = saved['cm_dialogue_worker']['session_id']
    starts = [i for i, e in enumerate(saved['evidence'])
              if e.get('scope') == scope.to_dict() and e.get('outcome') == 'success'
              and canonical(e.get('tool', '')) == 'cm_outreach.start_outreach_call'
              and isinstance(business(e.get('observed_result')), dict)
              and business(e.get('observed_result')).get('session_id') == session
              and business(e.get('observed_result')).get('status') == 'active']
    if len(starts) != 1:
        raise ValueError('Expected one active outreach-start source for this worker')
    capture = _Capture()
    limits = Limits(**saved.get('budgets', {}))
    with closing(CaseStore(':memory:')) as store:
        state = store.open_case(scope, saved['instruction'], saved['domain'])
        for key in ('completion_contract', 'completion_contract_sha256', 'goal_planning_enabled'):
            if key in saved:
                state[key] = deepcopy(saved[key])
        state.update(deepcopy(initial.get('observed_bindings', {})))
        state['evidence'] = deepcopy(saved['evidence'][:starts[0] + 1])
        # A latest list recorded after outreach started is not an opening preparation.
        if ('authorized_statements' in saved
                and saved.get('authorized_statements_source_count', len(saved['evidence'])) <= starts[0]):
            from .authorized_statements import record
            record(state, {'statements': saved['authorized_statements']})
        # Recover launch budgets from the saved initial worker packet, not final counters.
        state.update(status='running', composition='helpers',
                     model_calls=limits.max_model_calls - initial['model_call_budget'] - 2,
                     tool_calls=limits.max_tool_calls - initial['tool_proposal_budget'])
        if state['model_calls'] < 0 or state['tool_calls'] < 0:
            raise ValueError('Saved worker budgets exceed saved case limits')
        case_sources = tuple({state['case_bindings']['source_tool']} if state.get('case_bindings') else ())
        principal = state.get('principal_bindings')
        h = Harness(store, capture, tools, limits, composition='helpers', recovery_helper_policy='auto',
                    case_identity_tools=case_sources,
                    principal_identity_result_paths={principal['source_tool']: ('principal_id',)} if principal else {})
        owner = 'conversation-probe'
        fence = store.claim(scope, owner)
        h._save(scope, state, owner, fence)
        try:
            before_send(h, scope, state, ToolCall('capture', 'cm_outreach.send_message',
                        {'session_id': session, 'message': 'Unsent capture placeholder'}), owner, fence, 'probe')
        except _Captured:
            pass
        if capture.messages:
            names = json.loads(capture.messages[1]['content'])['delegated_tools']
            registry = {s.name: s for s in h._available_specs(h._tool_map(), state)}
            capture.specs = [registry[n] for n in names]

    if capture.messages is None:
        raise ValueError('Current dialogue worker did not start')
    return capture.messages[:2], capture.specs


def prepare_probe(saved, job, turn, mode, tools):
    history, patient = select_turn(job['messages'], turn)
    if mode == 'baseline':
        registry = {s.name: s for s in [*tools.list_tools(), *_LOCAL_SPECS]}
        specs = [registry[name] for name in job['tool_names']]
        return history, specs, patient
    if mode != 'current':
        raise ValueError('mode must be current or baseline')
    initial, specs = rebuild_context(saved, job, tools)
    return [*initial, *history[2:]], specs, patient


def probe(saved, job, turn, mode, tools, model, repeat=1, prepare=False):
    messages, specs, patient = prepare_probe(saved, job, turn, mode, tools)
    return repeated_probe(saved, job, turn, mode, model, messages, specs, patient, repeat, prepare)


def complete_probe(saved, turn, mode, model, messages, specs, patient):
    reply = model.complete(messages, specs, max_output_tokens=saved.get('budgets', {}).get('max_output_tokens', 4000))
    calls = [asdict(c) for c in reply.tool_calls]
    return {'mode': mode, 'turn': turn, 'patient_reply': patient, 'content': reply.content,
            'proposed_messages': [c['arguments'].get('message') for c in calls
                                  if canonical(c['name']) == 'cm_outreach.send_message'],
            'tool_proposals': calls, 'usage': reply.usage, 'tools_dispatched': 0,
            'context_sha256': hashlib.sha256(json.dumps(messages, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}



def preparation_state(saved, job, turn):
    """Copy only evidence observed by the selected history boundary."""
    history, _ = select_turn(job['messages'], turn)
    ids = set()
    for message in history:
        if message.get('evidence_id'):
            ids.add(message['evidence_id'])
        if message.get('role') == 'tool':
            payload = json.loads(message['content'])
            if isinstance(payload, dict):
                ids.update(payload[k] for k in ('evidence_id', 'id') if isinstance(payload.get(k), str))
    # Outreach start is necessarily before this worker's first patient reply.
    scope = saved['scope']
    session = saved['cm_dialogue_worker']['session_id']
    boundary = -1
    for i, e in enumerate(saved.get('evidence', [])):
        value = business(e.get('observed_result'))
        if (e.get('id') in ids or (e.get('scope') == scope and e.get('outcome') == 'success'
                and canonical(e.get('tool', '')) == 'cm_outreach.start_outreach_call'
                and isinstance(value, dict) and value.get('session_id') == session)):
            boundary = i
    return {'scope': deepcopy(scope), 'evidence': deepcopy(saved.get('evidence', [])[:boundary + 1])}


from .worker_preparation import apply_preparation, prepare as prepare_worker


def repeated_probe(saved, job, turn, mode, model, messages, specs, patient, repeat=1, prepare=False):
    from .authorized_statements import SPEC, pin
    if type(repeat) is not int or not 1 <= repeat <= 5:
        raise ValueError('repeat must be between 1 and 5')
    if prepare and mode != 'current':
        raise ValueError('--prepare requires current mode')
    messages = deepcopy(messages)
    state = preparation_state(saved, job, turn)
    preparation = None
    preparation_calls = 0
    if prepare:
        context = deepcopy(messages)
        context.append({'role': 'user', 'content': json.dumps({'observations': [
            e for e in state['evidence'] if e.get('scope') == state['scope'] and e.get('outcome') == 'success']}, ensure_ascii=False)})
        preparation = prepare_worker(context, state, lambda ctx, selected: model.complete(
            ctx, selected, max_output_tokens=saved.get('budgets', {}).get('max_output_tokens', 4000)),
            apply=apply_preparation)
        preparation_calls = preparation['model_calls']
        # Failure is reported, but does not prevent probing the original turn.
        pin(messages, state)
    samples = []
    for i in range(repeat):
        context, sample_state = deepcopy(messages), deepcopy(state)
        initial_hash = hashlib.sha256(json.dumps(context, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        attempts = []
        for call_index in range(2):
            sample = complete_probe(saved, turn, mode, model, context, list(specs), patient)
            calls = sample['tool_proposals']
            # A speaking proposal is reported only; mixed/other tools are never applied.
            if sample['proposed_messages'] or not calls or any(c['name'] != SPEC.name for c in calls):
                break
            reply = ModelReply(content=sample['content'], tool_calls=[ToolCall(**c) for c in calls], usage=sample['usage'])
            attempts.append(apply_preparation(reply, context, sample_state))
            # One follow-up only: correction or message; never a third completion.
        local_preparation = ({**attempts[-1], 'attempts': attempts} if attempts else None)
        sample.update(preparation=local_preparation,
                      recorded_statements=deepcopy(sample_state.get('authorized_statements', [])),
                      message=sample['proposed_messages'][0] if sample['proposed_messages'] else None,
                      model_calls=call_index + 1, context_sha256=initial_hash)
        samples.append(sample)
        text = ' '.join(str(x) for x in sample['proposed_messages']) or sample['content'] or '[no proposed message]'
        print(f"Sample {i + 1} ({sample['model_calls']} calls): {text[:300]}", flush=True)
        print('Recorded statements: ' + json.dumps(sample['recorded_statements'], ensure_ascii=False), flush=True)
    return {**samples[0], 'samples': samples, 'repeat': repeat, 'prepare': prepare,
            'preparation': preparation, 'model_calls': preparation_calls + sum(s['model_calls'] for s in samples)}


def source_info():
    root = Path(__file__).resolve().parents[1]
    files = sorted((root / 'health_harness_codex').rglob('*.py')) + sorted((root / 'health_harness_codex/data').glob('*.json'))
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode() + b'\0' + path.read_bytes())
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    return {'commit': commit, 'current_source_sha256': digest.hexdigest()}


def output_path(run, out=None):
    run = Path(run).resolve()
    path = Path(out).resolve() if out else run.parent / (
        run.name + '-conversation-probe-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    if path == run or run in path.parents:
        raise ValueError('Probe output must be outside the saved run')
    if any(part.startswith('attempt-') for part in path.parts):
        raise ValueError('Probe output cannot be inside any saved attempt')
    if path.exists():
        raise ValueError('Probe output already exists; choose a fresh path')
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--turn', required=True, type=int)
    parser.add_argument('--mode', choices=('current', 'baseline'), default='current')
    parser.add_argument('--model', default='gpt-6-luna')
    parser.add_argument('--effort', default='high')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--repeat', type=int, choices=range(1, 6), default=1)
    parser.add_argument('--prepare', action='store_true', help='Current mode only: up to two local preparation calls before samples')
    args = parser.parse_args(argv)
    if args.prepare and args.mode != 'current':
        parser.error('--prepare requires --mode current')
    destination = output_path(args.run, args.out)
    db, state, job = load_saved(args.run)
    tools = build_tools(Path(__file__).resolve().parents[1] / 'runs/20261020-domain-contracts/cm/public-tool-schemas.json', Scope(**state['scope']))
    messages, specs, patient = prepare_probe(state, job, args.turn, args.mode, tools)
    source = source_info()
    print(f'Patient reply {args.turn}: {patient}', flush=True)
    from . import batch
    from .codex_provider import CodexSessionModel
    model = CodexSessionModel(batch.DEFAULT_CODEX_EXECUTABLE, model=args.model, reasoning_effort=args.effort,
                             timeout=180, active_timeout=600,
                             allowed_instruction_sources={str(batch.DEFAULT_INSTRUCTION): batch.DEFAULT_INSTRUCTION_SHA256})
    result = repeated_probe(state, job, args.turn, args.mode, model, messages, specs, patient, args.repeat, args.prepare)
    result.update(model=args.model, effort=args.effort, source=source, source_database=str(db.resolve()),
                  approximation='Saved history was produced by the old prompt; independent continuations from one context, not a new trajectory. Current rebuild cannot replay preparation absent from the old run; --prepare adds up to two model calls and applies only validated local preparation in memory.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f'Output: {destination}')


if __name__ == '__main__':
    main()
