"""Offline tests for the published API-key adapter (no network, no key needed)."""
import io
import json
import os
import unittest
from unittest.mock import patch

from health_harness_codex import codex_provider
from health_harness_codex.batch import BatchConfig, _api_adapter, _instruction_pins
from health_harness_codex.models import ToolSpec
from health_harness_codex.providers import ProviderError


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _reply(payload):
    return _Response(json.dumps(payload).encode('utf-8'))


class ApiAdapterTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'CLINICALGROUND_API_KEY': 'synthetic-key',
                                           'CLINICALGROUND_BASE_URL': 'https://api.example.test/v1'}, clear=False)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_adapter_is_active_and_skips_codex_only_requirements(self):
        self.assertTrue(_api_adapter())
        self.assertEqual({}, _instruction_pins(BatchConfig.__new__(BatchConfig)))

    def test_missing_key_fails_with_a_clear_message(self):
        with patch.dict(os.environ, {'CLINICALGROUND_API_KEY': ''}):
            with self.assertRaisesRegex(ProviderError, 'CLINICALGROUND_API_KEY'):
                codex_provider.CodexSessionModel(None)

    def test_same_call_shape_returns_tool_calls_from_the_api(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured['url'] = request.full_url
            captured['body'] = json.loads(request.data)
            captured['auth'] = request.headers.get('Authorization')
            return _reply({'choices': [{'message': {'content': 'Checking.', 'tool_calls': [
                {'id': 'call-1', 'type': 'function',
                 'function': {'name': captured['body']['tools'][0]['function']['name'],
                              'arguments': json.dumps({'case_id': 'CASE-1'})}}]}}],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 3}})

        tool = ToolSpec('cases.get_case', 'Read one case.', {'type': 'object', 'required': ['case_id'],
                        'properties': {'case_id': {'type': 'string'}}}, effect='read')
        with patch('health_harness_codex.providers.urlopen', fake_urlopen):
            model = codex_provider.CodexSessionModel('ignored.exe', model='synthetic-model', timeout=30,
                                                     allowed_instruction_sources={'ignored': 'x'})
            reply = model.complete([{'role': 'user', 'content': 'Open the case.'}], [tool], max_output_tokens=500)
        self.assertEqual('https://api.example.test/v1/chat/completions', captured['url'])
        self.assertEqual('synthetic-model', captured['body']['model'])
        self.assertEqual('Bearer synthetic-key', captured['auth'])
        self.assertEqual('cases.get_case', reply.tool_calls[0].name)
        self.assertEqual({'case_id': 'CASE-1'}, reply.tool_calls[0].arguments)
        self.assertEqual('completed', model.request_diagnostics().get('request_stage', 'completed'))

    def test_model_override_and_timeout_validation(self):
        with patch.dict(os.environ, {'CLINICALGROUND_MODEL': 'override-model'}):
            self.assertEqual('override-model', codex_provider.CodexSessionModel(None, model='gpt-6-luna').model)
        with self.assertRaises(ValueError):
            codex_provider.validate_active_timeout(180, 60)


if __name__ == '__main__':
    unittest.main()
