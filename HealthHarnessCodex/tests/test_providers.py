import json
import re
import unittest
from io import BytesIO
from unittest.mock import patch

from health_harness_codex.models import ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.providers import OpenAICompatibleModel


class FakeHTTPResponse:
    def __init__(self, payload):
        self.data = json.dumps(payload).encode()
        self.headers = {"Content-Type": "application/json"}

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.data


class ProviderTests(unittest.TestCase):
    def test_dotted_and_local_tool_names_are_presented_as_valid_provider_aliases(self):
        specs = [
            ToolSpec("case.add_obligation", "local", {"type": "object"}),
            ToolSpec("mcp_records.get_by_id_ab12", "remote", {"type": "object"}),
        ]
        captured = []

        def fake_urlopen(request, timeout):
            body = json.loads(request.data)
            captured.append(body)
            if len(captured) == 1:
                functions = [t["function"] for t in body["tools"]]
                self.assertTrue(all(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", f["name"]) for f in functions))
                self.assertEqual(2, len({f["name"] for f in functions}))
                self.assertEqual("Bearer secret-test-key", request.get_header("Authorization"))
                return FakeHTTPResponse({"choices": [{"message": {"content": None, "tool_calls": [{
                    "id": "call-1", "type": "function", "function": {
                        "name": functions[0]["name"], "arguments": '{"id":"x"}'
                    }
                }]}}], "usage": {"prompt_tokens": 13, "completion_tokens": 4, "total_tokens": 17,
                               "prompt_tokens_details": {"cached_tokens": 5}}})
            sent = body["messages"][-1]["tool_calls"][0]["function"]["name"]
            self.assertEqual(body["tools"][0]["function"]["name"], sent)
            return FakeHTTPResponse({"choices": [{"message": {"content": "ok"}}]})

        model = OpenAICompatibleModel("explicit-model", "https://example.test/v1", "secret-test-key")
        with patch("health_harness_codex.providers.urlopen", fake_urlopen):
            first = model.complete([{"role": "user", "content": "do it"}], specs, max_output_tokens=100)
            second = model.complete([
                {"role": "assistant", "content": "", "tool_calls": [{"id": first.tool_calls[0].id,
                 "name": first.tool_calls[0].name, "arguments": first.tool_calls[0].arguments}]}
            ], specs, max_output_tokens=100)
        self.assertEqual("case.add_obligation", first.tool_calls[0].name)
        self.assertEqual({"input_tokens": 13, "output_tokens": 4, "total_tokens": 17, "cached_input_tokens": 5}, first.usage)
        self.assertEqual("ok", second.content)

    def test_provider_requires_explicit_configuration_and_does_not_infer_usage(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleModel("m", "https://example.test/v1", "")
        model = OpenAICompatibleModel("m", "https://example.test/v1", "k")
        with patch("health_harness_codex.providers.urlopen", lambda *a, **k: FakeHTTPResponse({"choices": [{"message": {"content": "ok"}}]})):
            reply = model.complete([{"role": "user", "content": "x"}], [], max_output_tokens=20)
        self.assertEqual({}, reply.usage)


if __name__ == "__main__":
    unittest.main()
