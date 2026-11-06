"""Synthetic provenance and integration checks; no inference."""
from contextlib import closing
from copy import deepcopy
import json
from unittest import TestCase

from health_harness_codex.authorized_statements import NAME, SPEC, record, view
from health_harness_codex.engine import Harness, _LOCAL_SPECS
from health_harness_codex.models import IsolationError, ModelReply, ToolCall
from health_harness_codex.store import CaseStore
from health_harness_codex.context import project_context
from test_goal_planning import base, ev, SCOPE
from test_dialogue_worker import seed, Tools, before_send, SEND


def arguments():
    return {'statements': [{'text': 'Synthetic policy-backed statement.', 'source_evidence_id': 'ev:0',
        'policy_condition': 'Synthetic record condition', 'condition_status': 'met',
        'condition_evidence_ids': ['ev:1']}]}


def state():
    s = base()
    ev(s, 'policy.read', {'text': 'Synthetic policy.'}, 'read')
    ev(s, 'records.read', {'status': 'observed'}, 'read')
    return s


class AuthorizedStatementsTests(TestCase):
    def test_shape_and_provenance_reject_atomically(self):
        for mutation in ('unknown', 'foreign', 'failed', 'met_empty', 'count', 'text', 'condition', 'scope_note', 'ids', 'status', 'extra'):
            with self.subTest(mutation=mutation):
                s = state(); a = arguments(); item = a['statements'][0]
                if mutation == 'unknown': item['source_evidence_id'] = 'missing'
                if mutation == 'foreign': s['evidence'][1]['scope'] = {**s['scope'], 'case': 'foreign'}
                if mutation == 'failed': s['evidence'][1]['outcome'] = 'error'
                if mutation == 'met_empty': item['condition_evidence_ids'] = []
                if mutation == 'count': a['statements'] *= 7
                if mutation == 'text': item['text'] = 'x' * 601
                if mutation == 'condition': item['policy_condition'] = 'x' * 301
                if mutation == 'scope_note': item['scope_note'] = 'x' * 301
                if mutation == 'ids': item['condition_evidence_ids'] *= 9
                if mutation == 'status': item['condition_status'] = 'approved'
                if mutation == 'extra': item['permission'] = True
                original = deepcopy(s)
                with self.assertRaises((ValueError, IsolationError)): record(s, a)
                self.assertEqual(original, s)

    def test_domain_neutral_exact_text_latest_list_and_owner_pin(self):
        for domain in ('CM', 'PA', 'UM'):
            s = state(); s['domain'] = domain
            from health_harness_codex.completion_contracts import build_completion_contract
            s['completion_contract'] = build_completion_contract(SCOPE.task, {'CM': 'cm', 'PA': 'pa_provider', 'UM': 'pa_um'}[domain], 'Synthetic task', SCOPE.to_dict())
            a = arguments(); original = deepcopy(a)
            result = record(s, a)
            self.assertEqual(original, a)
            self.assertEqual(a['statements'], view(s)['statements'])
            self.assertFalse(result['creates_evidence'])
            context = project_context(s['messages'], s, [], 200000)
            self.assertIn('actor_source_linked_preparation_not_policy', context[0]['content'])
            self.assertIn(a['statements'][0]['text'], context[0]['content'])
            s.pop('completion_contract')
            generic = project_context(s['messages'], s, [], 200000)
            self.assertIn(a['statements'][0]['text'], generic[0]['content'])
            record(s, {'statements': []})
            self.assertEqual([], s['authorized_statements'])

    def test_local_dispatch_persists_without_external_dispatch(self):
        with closing(CaseStore(':memory:')) as store:
            s = store.open_case(SCOPE, base()['instruction'], 'CM'); s.update(state())
            tools = Tools(); h = Harness(store, None, tools)
            owner = 'owner'; fence = store.claim(SCOPE, owner); h._save(SCOPE, s, owner, fence)
            s, _ = h._execute_calls(SCOPE, s, [{'id': 'prep', 'name': NAME, 'arguments': arguments()}], h._tool_map(), owner, fence)
            self.assertEqual(arguments()['statements'], store.load_case(SCOPE)['authorized_statements'])
            self.assertEqual([], tools.calls)
            self.assertTrue(any(m.get('name') == NAME for m in s['messages']))
            self.assertIn(NAME, [t.name for t in h._available_specs(h._tool_map(), s)])
            self.assertIn(SPEC, _LOCAL_SPECS)

    def test_worker_can_prepare_and_next_context_is_pinned(self):
        class Model:
            def __init__(self): self.contexts = []; self.specs = []
            def complete(self, messages, specs, **kwargs):
                self.contexts.append(deepcopy(messages)); self.specs.append(specs)
                if len(self.contexts) == 1:
                    return ModelReply(tool_calls=[ToolCall('prep', NAME, {'statements': [{
                        'text': 'Synthetic statement unchanged.', 'source_evidence_id': 'ev:0',
                        'policy_condition': None, 'condition_status': 'not_applicable', 'condition_evidence_ids': []}]})])
                return ModelReply(content=json.dumps({'status': 'complete', 'conclusion': 'Prepared only', 'evidence_ids': [], 'open_questions': []}))
        with closing(CaseStore(':memory:')) as store:
            s = seed(store); tools = Tools(); model = Model()
            h = Harness(store, model, tools, composition='helpers', recovery_helper_policy='auto')
            owner = 'owner'; fence = store.claim(SCOPE, owner); h._save(SCOPE, s, owner, fence)
            before_send(h, SCOPE, s, ToolCall('draft', SEND, {'session_id': 's', 'message': 'Unsent'}), owner, fence, 'm1')
            self.assertIn('Synthetic statement unchanged.', model.contexts[1][0]['content'])
            self.assertEqual([NAME], [t.name for t in model.specs[0]])
            writes = {t.name for t in model.specs[1] if t.effect == 'write'}
            self.assertEqual({NAME, SEND}, writes)
            self.assertEqual([], tools.calls)


    def test_repin_replaces_stale_preparation_without_rewriting_text(self):
        from health_harness_codex.authorized_statements import pin
        s = state(); record(s, arguments())
        messages = [{'role': 'system', 'content': 'Original instructions'}]
        pin(messages, s)
        changed = arguments(); changed['statements'][0]['text'] = 'Replacement verbatim: ?.'
        record(s, changed); pin(messages, s)
        self.assertEqual(1, messages[0]['content'].count('Actor preparation (not policy):'))
        self.assertNotIn('Synthetic policy-backed statement.', messages[0]['content'])
        self.assertIn('Replacement verbatim: ?.', messages[0]['content'])


    def test_condition_standard_once_in_owner_and_helper_prompts(self):
        from health_harness_codex import roles
        standard = 'Judge conditions by what available records can show:'
        self.assertIn('do not demand record types the system lacks', roles.STATEMENT_PREPARATION)
        self.assertIn('records that would settle it are missing or conflict', roles.STATEMENT_PREPARATION)
        for domain in ('PA', 'UM', 'CM'):
            for composition in ('combined', 'helpers', 'team'):
                self.assertEqual(1, roles.system_prompt(domain, SCOPE, composition).count(standard))
        for role in roles._catalogue():
            if role.get('model_visible') is not False:
                self.assertEqual(1, roles.helper_prompt(role).count(standard))


class UnknownConditionTests(TestCase):
    def _unknown(self, **fields):
        a = arguments(); item = a['statements'][0]
        item.update(condition_status='unknown', condition_evidence_ids=[], **fields)
        return a

    def test_unknown_must_name_the_settling_record(self):
        with self.assertRaisesRegex(ValueError, 'settling_record_type'):
            record(state(), self._unknown())

    def test_unknown_resting_on_a_record_type_the_system_lacks_is_rejudged(self):
        with self.assertRaisesRegex(ValueError, 're-judge'):
            record(state(), self._unknown(settling_record_type='A field this system never stores',
                                          settling_record_available=False))

    def test_unknown_with_an_available_but_missing_record_is_accepted(self):
        s = state()
        result = record(s, self._unknown(settling_record_type='A record this system stores but did not return',
                                         settling_record_available=True))
        self.assertEqual(1, result['recorded'])
        self.assertEqual('unknown', s['authorized_statements'][0]['condition_status'])


class NotMetConditionTests(TestCase):
    def test_not_met_needs_contradicting_evidence_and_met_error_says_how_to_fix(self):
        a = arguments(); item = a['statements'][0]
        item.update(condition_status='not_met', condition_evidence_ids=[])
        with self.assertRaisesRegex(ValueError, 'silent on it is not a contradiction'):
            record(state(), a)
        item.update(condition_evidence_ids=['ev:1'])
        self.assertEqual(1, record(state(), a)['recorded'])
        a = arguments(); a['statements'][0]['condition_evidence_ids'] = []
        with self.assertRaisesRegex(ValueError, 'cite the observed record'):
            record(state(), a)


class ConditionalNotApplicableTests(TestCase):
    def test_conditional_statement_cannot_be_not_applicable(self):
        a = arguments(); a['statements'][0].update(condition_status='not_applicable')
        with self.assertRaisesRegex(ValueError, 'must decide it'):
            record(state(), a)
        a['statements'][0]['policy_condition'] = None
        self.assertEqual(1, record(state(), a)['recorded'])


class InformationNeedsTests(TestCase):
    def test_information_needs_are_cited_pinned_and_replaced(self):
        s = state(); a = arguments()
        a['information_needs'] = [{'need': 'Synthetic counterparty-reported item.', 'source_evidence_id': 'ev:0'}]
        self.assertEqual(1, record(s, a)['information_needs'])
        self.assertEqual(a['information_needs'], view(s)['information_needs'])
        context = project_context(s['messages'], s, [], 200000)
        self.assertIn('Synthetic counterparty-reported item.', context[0]['content'])
        record(s, arguments())
        self.assertEqual([], view(s)['information_needs'])

    def test_uncited_information_need_rejects_atomically(self):
        s = state(); a = arguments(); original = deepcopy(s)
        a['information_needs'] = [{'need': 'Synthetic item.', 'source_evidence_id': 'missing'}]
        with self.assertRaises((ValueError, IsolationError)): record(s, a)
        self.assertEqual(original, s)


class MistypedCitationTests(TestCase):
    def test_mistyped_ids_are_named_with_this_cases_closest_ids_all_at_once(self):
        s = state()
        real = 'ev:m5:req_fe495cee45351f10559a6bbc077c24bda1b483409ab4d06d8ad104035ac12664_1'
        s['evidence'][0]['id'] = real
        typo = 'ev:m5:req_fe495cee45351f10559a6bbc077c24bda1b483ab4d06d8ad104035ac12664_1'
        a = arguments(); a['statements'][0]['source_evidence_id'] = typo
        a['information_needs'] = [{'need': 'Synthetic item.', 'source_evidence_id': 'ev:unknown'}]
        with self.assertRaises(IsolationError) as caught: record(s, a)
        detail = str(caught.exception)
        self.assertIn(repr(typo), detail); self.assertIn(real, detail); self.assertIn("'ev:unknown'", detail)

    def test_foreign_or_failed_sources_are_never_suggested(self):
        s = state(); s['evidence'][1]['scope'] = {**s['scope'], 'case': 'foreign'}
        s['evidence'][1]['id'] = 'ev:foreign-source-0001'
        a = arguments(); a['statements'][0]['condition_evidence_ids'] = ['ev:foreign-source-0002']
        with self.assertRaises(IsolationError) as caught: record(s, a)
        self.assertNotIn('ev:foreign-source-0001', str(caught.exception))
