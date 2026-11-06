"""Offline replay tests: synthetic state, fake model, no saved-run dependency."""
from copy import deepcopy
from contextlib import closing
import io
import hashlib
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from health_harness_codex import conversation_probe as cp
from health_harness_codex.cm_guidance import PROGRAM_DESCRIPTION
from health_harness_codex.models import Limits, ModelReply, ToolCall, ToolSpec, IsolationError
from health_harness_codex.providers import ModelResponseFormatError
from test_goal_planning import base, ev, SCOPE


SEND = 'cm_outreach.send_message'


class FakeModel:
    def __init__(self):
        self.calls = []

    def complete(self, messages, specs, **kwargs):
        self.calls.append((deepcopy(messages), list(specs)))
        return ModelReply(tool_calls=[ToolCall('new', SEND, {'session_id': 's', 'message': 'Proposed only'})],
                          usage={'input_tokens': 17})


def fixture():
    state = base()
    state['budgets'] = {k: getattr(Limits(), k) for k in
                        ('max_model_calls', 'max_tool_calls', 'max_context_chars', 'max_output_tokens')}
    ev(state, 'cm_intake.get_referral', {'case_id': 'case'}, 'read')
    ev(state, 'cm_outreach.start_outreach_call', {'session_id': 's', 'status': 'active'})
    ev(state, 'cm_intake.disenroll_case', {'future_secret': 'must not enter initial context'})
    state['cm_dialogue_worker'] = {'session_id': 's', 'status': 'settled'}
    state['working_notes'] = ['FUTURE_NOTE']
    initial = {'observed_bindings': {}, 'model_call_budget': 25, 'tool_proposal_budget': 95}
    messages = [{'role': 'system', 'content': 'OLD_SYSTEM'},
                {'role': 'user', 'content': json.dumps(initial)}]
    for n in (1, 2):
        messages.extend([
            {'role': 'user', 'content': f'Saved budget {n}'},
            {'role': 'assistant', 'content': '', 'tool_calls': [
                {'id': f'send{n}', 'name': SEND, 'arguments': {'message': f'question{n}', 'session_id': 's'}}]},
            {'role': 'tool', 'tool_call_id': f'send{n}', 'content': json.dumps({
                'outcome': 'success', 'observed_result': {'structuredContent': {'patient_response': f'reply{n}'},
                'content': [{'text': json.dumps({'patient_response': f'reply{n}'})}]}})},
            {'role': 'assistant', 'content': '', 'tool_calls': [
                {'id': f'read{n}', 'name': 'cm_outreach.get_transcript', 'arguments': {}}]},
            {'role': 'tool', 'tool_call_id': f'read{n}', 'content': json.dumps({
                'outcome': 'success', 'observed_result': {'patient_response': 'transcript duplicate'}})}])
    job = {'role_id': 'CM-04', 'invocation': 'cm_dialogue_worker', 'messages': messages,
           'tool_names': [SEND, 'cm_outreach.get_transcript']}
    state['helper_jobs'] = [job]
    tools = cp.NoDispatchTools([ToolSpec(SEND, 'Send', {'type': 'object'}, effect='write'),
                               ToolSpec('cm_outreach.get_transcript', 'Read', {'type': 'object'}, effect='read')])
    return state, job, tools


class ConversationProbeTests(TestCase):
    def test_turn_selection_counts_patient_replies_and_excludes_later_messages(self):
        state, job, tools = fixture()
        first, patient = cp.select_turn(job['messages'], 1)
        self.assertEqual('reply1', patient)
        self.assertEqual(job['messages'][:5], first)
        second, patient = cp.select_turn(job['messages'], 2)
        self.assertEqual('reply2', patient)
        self.assertEqual(job['messages'][:10], second)
        for invalid in (0, -1, 3, True):
            with self.assertRaises(ValueError):
                cp.select_turn(job['messages'], invalid)

    def test_baseline_verbatim_one_call_no_dispatch(self):
        state, job, tools = fixture()
        model = FakeModel()
        with patch.object(tools, 'call', side_effect=AssertionError('No dispatch')) as dispatch:
            result = cp.probe(state, job, 2, 'baseline', tools, model)
        self.assertEqual(1, len(model.calls))
        self.assertEqual(job['messages'][:10], model.calls[0][0])
        self.assertEqual(job['tool_names'], [s.name for s in model.calls[0][1]])
        self.assertEqual(['Proposed only'], result['proposed_messages'])
        self.assertEqual({'input_tokens': 17}, result['usage'])
        dispatch.assert_not_called()

    def test_current_rebuilds_prompt_and_keeps_history_without_mutating_source(self):
        state, job, tools = fixture()
        original = deepcopy(state)
        model = FakeModel()
        with patch.object(tools, 'call', side_effect=AssertionError('No dispatch')) as dispatch:
            result = cp.probe(state, job, 2, 'current', tools, model)
        messages = model.calls[0][0]
        self.assertEqual(1, len(model.calls))
        self.assertNotEqual('OLD_SYSTEM', messages[0]['content'])
        self.assertIn(PROGRAM_DESCRIPTION, messages[0]['content'])
        self.assertNotIn(PROGRAM_DESCRIPTION, messages[1]['content'])
        self.assertEqual(job['messages'][2:10], messages[2:])
        self.assertNotIn('future_secret', str(messages[:2]))
        self.assertNotIn('FUTURE_NOTE', str(messages[:2]))
        self.assertEqual(original, state)
        self.assertEqual('current', result['mode'])
        dispatch.assert_not_called()

    def test_identity_bindings_are_taken_from_launch_packet(self):
        state, job, tools = fixture()
        scope = {**SCOPE.to_dict(), 'case': 'case-subject:patient'}
        state['scope'] = scope
        for e in state['evidence']:
            e['scope'] = scope
        binding = {'case_namespace': scope['case'], 'patient_id': 'patient', 'case_id': 'resolved-case',
                   'source_tool': 'cm_intake.open_case', 'source_evidence_id': 'ev:0'}
        initial = json.loads(job['messages'][1]['content'])
        initial['observed_bindings'] = {'case_bindings': binding}
        job['messages'][1]['content'] = json.dumps(initial)
        # A final binding is deliberately inconsistent; it must not leak backward.
        state['case_bindings'] = {'case_id': 'wrong-future-binding'}
        messages, specs = cp.rebuild_context(state, job, tools)
        user = json.loads(messages[1]['content'])
        self.assertEqual('resolved-case', user['effective_tool_scope']['case'])
        self.assertEqual(binding, user['observed_bindings']['case_bindings'])

    def test_saved_database_read_only_and_probe_does_not_change_it(self):
        state, job, tools = fixture()
        with TemporaryDirectory() as tmp:
            run = Path(tmp) / 'run'
            db_path = run / 'cm/synthetic/attempt-1/state.sqlite'
            db_path.parent.mkdir(parents=True)
            with closing(sqlite3.connect(db_path)) as db:
                with db:
                    db.execute('CREATE TABLE cases(state_json TEXT)')
                    db.execute('INSERT INTO cases VALUES (?)', (json.dumps(state),))
            before = hashlib.sha256(db_path.read_bytes()).hexdigest()
            connect = sqlite3.connect
            with patch.object(cp.sqlite3, 'connect', wraps=connect) as spy:
                path, loaded, worker = cp.load_saved(run)
                self.assertTrue(spy.call_args.args[0].endswith('?mode=ro'))
                self.assertTrue(spy.call_args.kwargs['uri'])
            for mode in ('baseline', 'current'):
                cp.probe(loaded, worker, 1, mode, tools, FakeModel())
            self.assertEqual(before, hashlib.sha256(db_path.read_bytes()).hexdigest())
            self.assertEqual([db_path], list(run.rglob('*sqlite*')))

    def test_refuse_dispatch_and_unsafe_output_locations(self):
        with self.assertRaises(RuntimeError):
            cp.NoDispatchTools([]).call('read', {})
        with TemporaryDirectory() as tmp:
            run = Path(tmp) / 'run'
            self.assertEqual(run.parent, cp.output_path(run).parent)
            with self.assertRaises(ValueError):
                cp.output_path(run, run / 'cm/task/attempt-1/probe.json')
            existing = Path(tmp) / 'existing.json'
            existing.write_text('{}')
            with self.assertRaises(ValueError):
                cp.output_path(run, existing)

    def test_schema_inventory_uses_public_aliases_local_and_workspace_specs(self):
        with TemporaryDirectory() as tmp:
            schema = Path(tmp) / 'schemas.json'
            schema.write_text(json.dumps([{'alias': 'mcp_cm_outreach_get_transcript_da2e4f5e0117',
                'actual': 'cm_outreach.get_transcript', 'description': 'Read transcript',
                'schema': {'type': 'object'}, 'effect': 'write'}]))
            tools = cp.build_tools(schema, SCOPE)
            self.assertEqual('read', tools.list_tools()[0].effect)
            self.assertIn('workspace.read_many', [s.name for s in tools.list_tools()])
            self.assertIn('case.find_evidence', [s.name for s in cp._LOCAL_SPECS])

    def test_cli_uses_pinned_provider_once_and_writes_output_outside_run(self):
        from health_harness_codex import batch
        for mode in ('baseline', 'current'):
            with self.subTest(mode=mode), TemporaryDirectory() as tmp:
                state, job, tools = fixture()
                model = FakeModel()
                run = Path(tmp) / 'saved'
                with patch.object(cp, 'load_saved', return_value=(run / 'state.sqlite', state, job)), \
                     patch.object(cp, 'build_tools', return_value=tools), \
                     patch.object(cp, 'source_info', return_value={'commit': 'fake', 'current_source_sha256': 'fake'}), \
                     patch('health_harness_codex.codex_provider.CodexSessionModel', return_value=model) as provider, \
                     patch('sys.stdout', new_callable=io.StringIO) as stdout:
                    cp.main(['--run', str(run), '--turn', '1', '--mode', mode])
                self.assertEqual(1, len(model.calls))
                self.assertEqual(batch.DEFAULT_CODEX_EXECUTABLE, provider.call_args.args[0])
                self.assertEqual('gpt-6-luna', provider.call_args.kwargs['model'])
                self.assertEqual('high', provider.call_args.kwargs['reasoning_effort'])
                self.assertEqual({str(batch.DEFAULT_INSTRUCTION): batch.DEFAULT_INSTRUCTION_SHA256},
                                 provider.call_args.kwargs['allowed_instruction_sources'])
                paths = list(Path(tmp).glob('*.json'))
                self.assertEqual(1, len(paths))
                result = json.loads(paths[0].read_text(encoding='utf-8'))
                self.assertEqual(mode, result['mode'])
                self.assertEqual(['Proposed only'], result['proposed_messages'])
                self.assertIn('Patient reply 1: reply1', stdout.getvalue())


class ProbeRepeatTests(TestCase):
    def test_repeat_independent_identical_contexts(self):
        state, job, tools = fixture(); model = FakeModel()
        result = cp.probe(state, job, 1, 'current', tools, model, repeat=3)
        self.assertEqual(3, len(model.calls))
        self.assertEqual(3, len(result['samples']))
        self.assertEqual(model.calls[0][0], model.calls[2][0])
        for invalid in (0, 6, True):
            with self.assertRaises(ValueError): cp.probe(state, job, 1, 'current', tools, model, repeat=invalid)

    def test_prepare_once_validated_local_only_and_source_immutable(self):
        from health_harness_codex.authorized_statements import NAME
        class Preparing(FakeModel):
            def complete(self, messages, specs, **kwargs):
                if not self.calls:
                    self.calls.append((deepcopy(messages), list(specs)))
                    return ModelReply(tool_calls=[ToolCall('prep', NAME, {'statements': [{
                        'text': 'Synthetic prepared statement.', 'source_evidence_id': 'ev:0',
                        'policy_condition': None, 'condition_status': 'not_applicable', 'condition_evidence_ids': []}]})])
                return super().complete(messages, specs, **kwargs)
        state, job, tools = fixture(); original = deepcopy(state); model = Preparing()
        with patch.object(tools, 'call', side_effect=AssertionError('No external dispatch')) as dispatch:
            result = cp.probe(state, job, 1, 'current', tools, model, repeat=3, prepare=True)
        self.assertEqual(4, len(model.calls)); self.assertEqual(3, len(result['samples']))
        self.assertEqual([NAME], [s.name for s in model.calls[0][1]])
        self.assertIn('Synthetic prepared statement.', model.calls[1][0][0]['content'])
        self.assertNotIn('future_secret', str(model.calls[0][0]))
        self.assertEqual(original, state); dispatch.assert_not_called()
        with self.assertRaises(ValueError): cp.probe(state, job, 1, 'baseline', tools, model, prepare=True)

    def test_prepare_rejects_other_tools_and_future_foreign_unknown_sources(self):
        from health_harness_codex.authorized_statements import NAME
        state, job, tools = fixture()
        for name, source_id in ((SEND, 'ev:0'), (NAME, 'missing'), (NAME, 'ev:2')):
            class Invalid:
                def complete(self, *args, **kwargs):
                    return ModelReply(tool_calls=[ToolCall('bad', name, {'statements': [{
                        'text': 'Synthetic', 'source_evidence_id': source_id, 'policy_condition': None,
                        'condition_status': 'not_applicable', 'condition_evidence_ids': []}]})])
            result = cp.probe(state, job, 1, 'current', tools, Invalid(), prepare=True)
            self.assertFalse(result['preparation']['local_preparation_applied'])
            self.assertEqual(2, result['preparation']['model_calls'])
            self.assertIn('error', result['preparation']['validation'])
            self.assertLessEqual(result['model_calls'], 4)


    def test_boundary_uses_history_evidence_ids_and_excludes_later_observations(self):
        state, job, _ = fixture()
        state['evidence'][2]['observed_result'] = {'historical': 'visible at selected reply'}
        job['messages'][4]['evidence_id'] = 'ev:2'
        ev(state, 'records.read', {'later': 'excluded'}, 'read')
        limited = cp.preparation_state(state, job, 1)
        self.assertEqual(['ev:0', 'ev:1', 'ev:2'], [e['id'] for e in limited['evidence']])
        self.assertNotIn('excluded', str(limited))

    def test_cli_repeat_and_prepare_output_and_early_argument_validation(self):
        from health_harness_codex.authorized_statements import NAME
        class Preparing(FakeModel):
            def complete(self, messages, specs, **kwargs):
                if not self.calls:
                    self.calls.append((deepcopy(messages), list(specs)))
                    return ModelReply(tool_calls=[ToolCall('prep', NAME, {'statements': []})])
                return super().complete(messages, specs, **kwargs)
        with TemporaryDirectory() as tmp:
            state, job, tools = fixture(); model = Preparing(); run = Path(tmp) / 'saved'
            with patch.object(cp, 'load_saved', return_value=(run / 'state.sqlite', state, job)), \
                 patch.object(cp, 'build_tools', return_value=tools), \
                 patch.object(cp, 'source_info', return_value={}), \
                 patch('health_harness_codex.codex_provider.CodexSessionModel', return_value=model), \
                 patch('sys.stdout', new_callable=io.StringIO):
                cp.main(['--run', str(run), '--turn', '1', '--repeat', '3', '--prepare'])
            result = json.loads(next(Path(tmp).glob('*.json')).read_text(encoding='utf-8'))
            self.assertEqual(4, len(model.calls)); self.assertEqual(3, len(result['samples']))
            self.assertTrue(result['prepare']); self.assertEqual(4, result['model_calls'])
        for flags in (['--repeat', '6'], ['--mode', 'baseline', '--prepare']):
            with patch.object(cp, 'load_saved') as load, patch('sys.stderr', new_callable=io.StringIO):
                with self.assertRaises(SystemExit): cp.main(['--run', 'unused', '--turn', '1', *flags])
                load.assert_not_called()


    def test_opening_pin_only_restores_pre_outreach_preparation(self):
        state, job, tools = fixture()
        state['authorized_statements'] = [{'text': 'Synthetic opening preparation.', 'source_evidence_id': 'ev:0',
            'policy_condition': None, 'condition_status': 'not_applicable', 'condition_evidence_ids': []}]
        state['authorized_statements_source_count'] = 1
        messages, _, _ = cp.prepare_probe(state, job, 1, 'current', tools)
        self.assertIn('Synthetic opening preparation.', messages[0]['content'])
        state['authorized_statements_source_count'] = 2
        messages, _, _ = cp.prepare_probe(state, job, 1, 'current', tools)
        self.assertNotIn('Synthetic opening preparation.', messages[0]['content'])


    def test_follow_through_isolated_samples_feedback_and_two_call_cap(self):
        from health_harness_codex.authorized_statements import NAME
        for invalid in (False, True):
            with self.subTest(invalid=invalid):
                class Preparing(FakeModel):
                    def complete(self, messages, specs, **kwargs):
                        if len(self.calls) % 2 == 0:
                            self.calls.append((deepcopy(messages), list(specs)))
                            return ModelReply(tool_calls=[ToolCall('prep', NAME, {'statements': [{
                                'text': 'Synthetic statement.', 'source_evidence_id': 'missing' if invalid else 'ev:0',
                                'policy_condition': 'Observed condition', 'condition_status': 'met',
                                'condition_evidence_ids': ['ev:1']}]})])
                        return super().complete(messages, specs, **kwargs)
                state, job, tools = fixture(); original = deepcopy(state); model = Preparing()
                with patch.object(tools, 'call', side_effect=AssertionError('No dispatch')) as dispatch:
                    result = cp.probe(state, job, 1, 'current', tools, model, repeat=3)
                self.assertEqual(6, result['model_calls'])
                self.assertEqual(model.calls[0][0], model.calls[2][0])
                feedback = json.loads(model.calls[1][0][-1]['content'])
                if invalid:
                    self.assertEqual('IsolationError', feedback['error'])
                    self.assertTrue(feedback['detail'].startswith('working records require successful original evidence in this exact case'))
                    self.assertIn("'missing'", feedback['detail'])
                else:
                    self.assertEqual(1, feedback['recorded'])
                for sample in result['samples']:
                    self.assertEqual(2, sample['model_calls'])
                    self.assertEqual('Proposed only', sample['message'])
                    self.assertEqual(not invalid, sample['preparation']['local_preparation_applied'])
                    if not invalid:
                        self.assertEqual('met', sample['recorded_statements'][0]['condition_status'])
                self.assertEqual(original, state); dispatch.assert_not_called()

    def test_prepare_error_corrective_call_and_continued_turn(self):
        from health_harness_codex.authorized_statements import NAME
        class Correcting(FakeModel):
            def complete(self, messages, specs, **kwargs):
                if len(self.calls) < 2:
                    self.calls.append((deepcopy(messages), list(specs)))
                    return ModelReply(tool_calls=[ToolCall('prep', NAME, {'statements': [{
                        'text': 'Synthetic statement.', 'source_evidence_id': 'missing' if len(self.calls) == 1 else 'ev:0',
                        'policy_condition': None, 'condition_status': 'not_applicable', 'condition_evidence_ids': []}]})])
                return super().complete(messages, specs, **kwargs)
        state, job, tools = fixture(); model = Correcting()
        result = cp.probe(state, job, 1, 'current', tools, model, repeat=3, prepare=True)
        self.assertEqual('IsolationError', json.loads(model.calls[1][0][-1]['content'])['error'])
        self.assertTrue(result['preparation']['local_preparation_applied'])
        self.assertEqual(5, result['model_calls'])
        self.assertEqual(2, len(result['preparation']['attempts']))
        self.assertTrue(all(s['message'] == 'Proposed only' for s in result['samples']))

    def test_perpetual_preparation_is_bounded_and_other_tools_never_applied(self):
        from health_harness_codex.authorized_statements import NAME
        for name in (NAME, 'case.add_note', SEND):
            class Proposing(FakeModel):
                def complete(self, messages, specs, **kwargs):
                    self.calls.append((deepcopy(messages), list(specs)))
                    return ModelReply(tool_calls=[ToolCall('proposal', name, {'statements': []})])
            state, job, tools = fixture(); model = Proposing(); original = deepcopy(state)
            with patch.object(cp, 'apply_preparation', wraps=cp.apply_preparation) as apply:
                result = cp.probe(state, job, 1, 'current', tools, model, repeat=3, prepare=True)
            self.assertLessEqual(result['model_calls'], 8)
            self.assertTrue(all(s['model_calls'] <= 2 for s in result['samples']))
            if name != NAME:
                self.assertEqual(2, apply.call_count)  # shared preparation rejects, never dispatches
            self.assertEqual(original, state)


    def test_in_turn_correction_can_record_but_cannot_make_third_call(self):
        from health_harness_codex.authorized_statements import NAME
        class Correcting(FakeModel):
            def complete(self, messages, specs, **kwargs):
                self.calls.append((deepcopy(messages), list(specs)))
                return ModelReply(tool_calls=[ToolCall('prep', NAME, {'statements': [{
                    'text': 'Synthetic corrected statement.', 'source_evidence_id': 'missing' if len(self.calls) == 1 else 'ev:0',
                    'policy_condition': None, 'condition_status': 'not_applicable', 'condition_evidence_ids': []}]})])
        state, job, tools = fixture(); model = Correcting()
        result = cp.probe(state, job, 1, 'current', tools, model)
        self.assertEqual(2, len(model.calls))
        self.assertIsNone(result['samples'][0]['message'])
        self.assertTrue(result['samples'][0]['preparation']['local_preparation_applied'])
        self.assertEqual('IsolationError', result['samples'][0]['preparation']['attempts'][0]['validation']['error'])
