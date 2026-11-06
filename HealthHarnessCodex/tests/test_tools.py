import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from health_harness_codex.models import Scope
from health_harness_codex.tools import MCPClient, MCPError, MCPToolError, ToolRegistry, WorkspaceTools


class Response:
    def __init__(self, payload=None, *, session=None, content_type="application/json"):
        self.body = b"" if payload is None else json.dumps(payload).encode()
        self.headers = {"Content-Type": content_type}
        if session:
            self.headers["Mcp-Session-Id"] = session
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.body


class ToolsTests(unittest.TestCase):
    def test_returned_error_preserved_privately_and_never_retried(self):
        client = MCPClient("http://example.test/mcp")
        client._initialized = True
        client._actual_names = {"alias": "write.case"}
        calls = []
        result = {"isError": True, "content": [{"type": "text", "text": "private service reason"}]}
        def request(method, params):
            calls.append((method, params))
            return result
        client._request = request
        with self.assertRaises(MCPToolError) as caught:
            client.call("alias", {})
        self.assertEqual(result, caught.exception.diagnostic_result)
        self.assertNotIn("private service reason", str(caught.exception))
        self.assertEqual(1, len(calls))

    def test_mcp_aliases_effect_defaults_session_and_parses_json_text(self):
        requests = []

        def fake_urlopen(request, timeout):
            body = json.loads(request.data)
            requests.append((request, body))
            if body["method"] == "initialize":
                return Response({"jsonrpc": "2.0", "id": body["id"], "result": {
                    "protocolVersion": "2025-03-26", "capabilities": {}, "serverInfo": {"name": "fake", "version": "1"}
                }}, session="session-1")
            if body["method"] == "notifications/initialized":
                return Response()
            if body["method"] == "tools/list":
                return Response({"jsonrpc": "2.0", "id": body["id"], "result": {"tools": [
                    {"name": "patient.lookup", "inputSchema": {"type": "object"}, "annotations": {"readOnlyHint": True}},
                    {"name": "write.case", "inputSchema": {"type": "object"}},
                ]}})
            if body["method"] == "tools/call":
                return Response({"jsonrpc": "2.0", "id": body["id"], "result": {"content": [
                    {"type": "text", "text": '{"patient_id":"p-2","secret":"foreign"}'}
                ]}})
            raise AssertionError(body)

        client = MCPClient("http://127.0.0.1:9999/mcp", namespace="fake-server")
        with patch("health_harness_codex.tools.urlopen", fake_urlopen):
            specs = client.list_tools()
            result = client.call(specs[0].name, {})
        self.assertTrue(all(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", spec.name) for spec in specs))
        self.assertEqual("read", specs[0].effect)
        self.assertEqual("write", specs[1].effect)  # unknown annotation is conservative
        self.assertEqual("patient.lookup", client._actual_names[specs[0].name])
        self.assertIn("patient.lookup", specs[0].description)
        self.assertEqual("p-2", result["content"][0]["parsed_json"]["patient_id"])
        self.assertTrue(any(req.get_header("Mcp-session-id") == "session-1" for req, _ in requests[1:]))
        self.assertTrue(all(req.get_header("Mcp-protocol-version") == "2025-03-26" for req, _ in requests))

    def test_duplicate_tool_names_and_unmatched_sse_fail_closed(self):
        client = MCPClient("http://example.test/mcp")
        client._initialized = True
        client._request = lambda method, params: {"tools": [
            {"name": "same", "inputSchema": {"type": "object"}},
            {"name": "same", "inputSchema": {"type": "object"}},
        ]}
        with self.assertRaises(MCPError):
            client.list_tools()
        payload = b'data: {"jsonrpc":"2.0","id":88,"result":{}}\n\ndata: {"jsonrpc":"2.0","id":7,"result":{"ok":true}}\n\n'
        from health_harness_codex.tools import _decode_json_or_sse
        self.assertEqual({"jsonrpc": "2.0", "id": 7, "result": {"ok": True}},
                         _decode_json_or_sse(payload, "text/event-stream", 7))
        self.assertIsNone(_decode_json_or_sse(payload, "text/event-stream", 9))

    def test_workspace_writes_are_per_case_and_paths_cannot_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "work"
            refs = Path(temp) / "refs"
            refs.mkdir()
            (refs / "guide.txt").write_text("approved reference", encoding="utf-8")
            a = Scope("env", "task", "org", "principal", "p1", "c1")
            b = Scope("env", "task", "org", "principal", "p2", "c2")
            ta = WorkspaceTools(root, a, [refs])
            tb = WorkspaceTools(root, b, [refs])
            ta.call("workspace.write_file", {"path": "artifact.txt", "content": "A only"})
            self.assertEqual({"files": []}, tb.call("workspace.list_files", {}))
            self.assertEqual("approved reference", ta.call("workspace.read_file", {"path": str(refs / "guide.txt")})["text"])
            with self.assertRaises(PermissionError):
                ta.call("workspace.write_file", {"path": "../other.txt", "content": "escape"})
            with self.assertRaises(PermissionError):
                ta.call("workspace.read_file", {"path": str(Path(temp) / "private.txt")})

    def test_tool_registry_rejects_collisions(self):
        class Provider:
            def list_tools(self): return []
        one, two = Provider(), Provider()
        # Use lightweight provider specs to avoid any MCP network request.
        from health_harness_codex.models import ToolSpec
        one.list_tools = lambda: [ToolSpec("same", "", {"type": "object"})]
        two.list_tools = lambda: [ToolSpec("same", "", {"type": "object"})]
        with self.assertRaises(ValueError):
            ToolRegistry(one, two).list_tools()


if __name__ == "__main__":
    unittest.main()
