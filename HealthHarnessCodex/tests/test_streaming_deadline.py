"""Deterministic deadlines exercise progress rather than live model latency."""
import json
import sys
import unittest
from unittest.mock import patch

from health_harness_codex.codex_provider import CodexSessionModel
from health_harness_codex.codex_transport import AppServerError
from health_harness_codex.providers import ProviderError
from test_codex_provider import FakeAppServer


class StreamingDeadlineTests(unittest.TestCase):
    def run_timeline(self, timeline, active_timeout=600):
        clock = [0.0]

        class TimedServer(FakeAppServer):
            def _events(server):
                return list(timeline)

            def next_event(server, *, deadline):
                when, event = server.events[0] if server.events else (float('inf'), None)
                if when >= deadline:
                    clock[0] = deadline
                    raise AppServerError('App Server request timed out', timeout_phase='transport_read')
                server.events.pop(0)
                clock[0] = when
                return event

        model = CodexSessionModel(sys.executable, timeout=180, active_timeout=active_timeout)
        with patch('health_harness_codex.codex_provider.time.monotonic', side_effect=lambda: clock[0]), \
             patch('health_harness_codex.codex_provider.AppServerClient', TimedServer):
            try:
                reply = model.complete([], [], max_output_tokens=32)
                return model, reply, None, clock[0]
            except ProviderError as error:
                return model, None, error, clock[0]

    @staticmethod
    def delta(when, method='item/agentMessage/delta', text='x', **overrides):
        return when, {'method': method, 'params': {
            'threadId': 'thread-1', 'turnId': 'turn-1', 'delta': text, **overrides}}

    @staticmethod
    def completed(when):
        return when, {'method': 'turn/completed', 'params': {'threadId': 'thread-1',
            'turn': {'id': 'turn-1', 'status': 'completed', 'items': [
                {'type': 'agentMessage', 'phase': 'final_answer', 'text': '{"content":"ok","tool_calls":[]}'}]}}}

    def test_active_generation_can_complete_after_old_hard_deadline(self):
        model, reply, error, elapsed = self.run_timeline([
            self.delta(150), self.delta(300), self.delta(450), self.completed(590)])
        self.assertIsNone(error)
        self.assertEqual('ok', reply.content)
        self.assertEqual(590, elapsed)
        self.assertEqual(600, model.request_diagnostics()['active_timeout_seconds'])

    def test_silent_stream_expires_at_idle_deadline(self):
        _, reply, error, elapsed = self.run_timeline([self.delta(100)])
        self.assertIsNone(reply)
        self.assertEqual(280, elapsed)
        self.assertEqual('idle', error.diagnostics['timeout_reason'])
        self.assertTrue(error.diagnostics['request_timed_out'])

    def test_metadata_and_empty_deltas_do_not_reset_silence(self):
        for event in [self.delta(170, text=''),
                (170, {'method': 'thread/tokenUsage/updated', 'params': {'threadId': 'thread-1'}}),
                (170, {'method': 'item/started', 'params': {'threadId': 'thread-1', 'turnId': 'turn-1',
                    'item': {'type': 'reasoning'}}})]:
            with self.subTest(event=event):
                _, _, error, elapsed = self.run_timeline([event])
                self.assertEqual(180, elapsed)
                self.assertEqual('idle', error.diagnostics['timeout_reason'])

    def test_reasoning_text_is_progress_but_never_captured(self):
        model, reply, error, _ = self.run_timeline([
            self.delta(150, method='item/reasoning/textDelta', text='PRIVATE_REASONING'),
            self.delta(300, method='item/reasoning/summaryTextDelta', text='PRIVATE_REASONING'),
            self.completed(310)])
        self.assertIsNone(error)
        self.assertEqual('ok', reply.content)
        self.assertNotIn('PRIVATE_REASONING', json.dumps(model.failure_response()))

    def test_foreign_generation_is_rejected_before_extending_deadline(self):
        _, _, error, elapsed = self.run_timeline([self.delta(170, threadId='foreign')])
        self.assertIn('thread ID did not match', str(error))
        self.assertEqual(170, elapsed)
        self.assertNotIn('timeout_reason', error.diagnostics)

    def test_active_total_cap_cannot_be_extended(self):
        _, _, error, elapsed = self.run_timeline([
            self.delta(150), self.delta(300), self.delta(450), self.delta(590), self.completed(700)])
        self.assertEqual(600, elapsed)
        self.assertEqual('active_total', error.diagnostics['timeout_reason'])

    def test_omitting_new_option_preserves_existing_hard_timeout(self):
        _, _, error, elapsed = self.run_timeline([self.delta(150), self.completed(190)], active_timeout=None)
        self.assertEqual(180, elapsed)
        self.assertNotIn('timeout_reason', error.diagnostics)

    def test_oversized_stream_stops_before_waiting_for_completion(self):
        model, reply, error, elapsed = self.run_timeline([
            self.delta(20, text='0' * 60001), self.completed(590)])
        self.assertIsNone(reply)
        self.assertEqual('response_size', error.stage)
        self.assertEqual(20, elapsed)
        self.assertEqual('response_size', error.diagnostics['response_failure_stage'])
        self.assertFalse(error.diagnostics['request_timed_out'])
        self.assertEqual(60000, len(model.failure_response()['text']))
        self.assertFalse(model.failure_response()['generation_completed'])

    def test_exact_size_limit_does_not_reject_a_valid_reply(self):
        text=''.join(str(i)+',' for i in range(20000))[:60000]
        _, reply, error, _ = self.run_timeline([self.delta(20, text=text), self.completed(30)])
        self.assertIsNone(error)
        self.assertEqual('ok', reply.content)

    def test_ascii_and_unicode_short_period_runaway_get_bounded_format_recovery(self):
        for text in ['0'*4096, chr(0x2753)*4096, ('ab'*2048)]:
            model, reply, error, elapsed = self.run_timeline([self.delta(25,text=text), self.completed(590)])
            self.assertIsNone(reply)
            self.assertEqual('response_repetition', error.stage)
            self.assertEqual(25, elapsed)
            self.assertFalse(model.failure_response()['generation_completed'])

    def test_repetition_tail_is_reset_before_a_different_request(self):
        model, _, _, _ = self.run_timeline([self.delta(25,text='0'*4096)])
        self.assertTrue(model._reply_tail)
        with self.assertRaises(ProviderError):model.complete('invalid next case',[],max_output_tokens=32)
        self.assertEqual('',model._reply_tail)

    def test_invalid_timeout_options_fail_before_starting_native_process(self):
        for active in [True, 179, 1801, float('nan'), float('inf'), '600']:
            with self.subTest(active=active), self.assertRaises(ValueError):
                CodexSessionModel(sys.executable, timeout=180, active_timeout=active)


if __name__ == '__main__':
    unittest.main()
