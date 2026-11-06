"""Real localhost HTTP checks against synthetic protocol responses only."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import unittest
from unittest.mock import patch

from health_harness_codex.engine import Harness
from health_harness_codex.cli import _operator_observation_contract
from health_harness_codex.models import Scope
from health_harness_codex.providers import OpenAICompatibleModel
from health_harness_codex.store import CaseStore
from health_harness_codex.tools import MCPClient, ToolRegistry


class ProtocolStub(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.received.append((self.path, request, dict(self.headers)))
        if self.path == "/v1/chat/completions":
            self.server.model_requests += 1
            messages = request["messages"]
            for tool in request.get("tools", []):
                if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", tool["function"]["name"]):
                    self.reply(400, {"error": "invalid tool name"})
                    return
            if any(message["role"] == "tool" for message in messages):
                message = {"role": "assistant", "content": json.dumps({
                    "status": "complete", "claim": "The synthetic observation was received.",
                    "evidence_ids": ["ev:m1:wire-read"],
                })}
            else:
                tool = next(t for t in request["tools"] if "WIRE_OBSERVATION_TOOL" in t["function"]["description"])
                message = {"role": "assistant", "content": "", "tool_calls": [{
                    "id": "wire-read", "type": "function", "function": {
                        "name": tool["function"]["name"],
                        "arguments": json.dumps({"patient_id": self.server.active_scope.patient}),
                    },
                }]}
            self.reply(200, {"choices": [{"message": message}], "usage": {
                "prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10,
                "prompt_tokens_details": {"cached_tokens": 1},
            }})
            return
        if self.path != "/mcp":
            self.reply(404, {})
            return
        method = request["method"]
        if method == "initialize":
            self.reply(200, {"jsonrpc": "2.0", "id": request["id"], "result": {
                "protocolVersion": "2025-03-26", "capabilities": {},
                "serverInfo": {"name": "synthetic-wire-check", "version": "1"},
            }}, session=True)
        elif self.headers.get("Mcp-Session-Id") != "wire-session":
            self.reply(400, {"error": "missing session header"})
        elif method == "notifications/initialized":
            self.reply(202, None)
        elif method == "tools/list":
            self.reply(200, {"jsonrpc": "2.0", "id": request["id"], "result": {"tools": [{
                "name": "wire.observation", "description": "WIRE_OBSERVATION_TOOL returns synthetic data.",
                "inputSchema": {"type": "object", "required": ["patient_id"],
                                "properties": {"patient_id": {"type": "string"}},
                                "additionalProperties": False},
                # No purity hint: the client must conservatively journal this as a write.
            }]}})
        elif method == "tools/call":
            self.server.tool_requests += 1
            if self.server.fail_tool:
                self.reply(503, {"error": "synthetic uncertain transport outcome"})
                return
            scope = self.server.active_scope
            patient = scope.patient + "-FOREIGN" if self.server.foreign else scope.patient
            result = {"content": [{"type": "text", "text": json.dumps({
                "patient_id": patient, "case_id": scope.case,
                "status": "recorded",
                "marker": "FOREIGN-PATIENT-MARKER" if self.server.foreign else "synthetic observation",
            })}]}
            # Exercise actual SSE decoding, including unrelated notifications/responses.
            events = [
                {"jsonrpc": "2.0", "method": "notifications/progress", "params": {}},
                {"jsonrpc": "2.0", "id": 999999, "result": {}},
                {"jsonrpc": "2.0", "id": request["id"], "result": result},
            ]
            body = "".join("event: message\ndata: " + json.dumps(e) + "\n\n" for e in events).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.reply(400, {"error": "unexpected method"})

    def reply(self, status, payload, *, session=False):
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if session:
            self.send_header("Mcp-Session-Id", "wire-session")
        self.end_headers()
        if body:
            self.wfile.write(body)


class HTTPIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), ProtocolStub)
        self.server.received = []
        self.server.model_requests = 0
        self.server.tool_requests = 0
        self.server.foreign = False
        self.server.fail_tool = False
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = CaseStore(Path(self.temp.name) / "cases.sqlite")
        self.addCleanup(self.store.close)
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def make_harness(self, domain="PA"):
        scope = Scope("synthetic", f"wire-{domain}", "test-org", "test-principal",
                      f"synthetic-patient-{domain}", f"synthetic-case-{domain}")
        self.server.active_scope = scope
        model = OpenAICompatibleModel("synthetic-model", self.base_url + "/v1", "dummy-test-key", timeout=3)
        # Match the tool-alias namespace used by the synthetic operator-owned
        # contract so its canonical tool name resolves to the registered name.
        tools = ToolRegistry(MCPClient(self.base_url + "/mcp", timeout=3,
                                       namespace="chi-bench-real-case"))
        contract = _operator_observation_contract(
            scope, domain, "wire.observation", "status", "recorded",
            phase="terminal_write_response")
        return scope, Harness(self.store, model, tools), contract

    def test_all_domains_run_over_actual_local_http_and_sse(self):
        for domain in ("PA", "UM", "CM"):
            with self.subTest(domain=domain):
                scope, harness, contract = self.make_harness(domain)
                result = harness.run(scope, "Read the synthetic observation.", domain,
                                     completion_contract=contract)
                self.assertEqual("complete", result["status"], result)
                self.assertTrue(result["completion_gate"]["accepted"])
                self.assertIsInstance(result["completion_gate"]["branch_id"], str)
                self.assertEqual(2, result["model_calls"])
                self.assertEqual("write", result["evidence"][0]["effect"])
                self.assertEqual({"input_tokens": 14, "output_tokens": 6, "total_tokens": 20,
                                  "cached_input_tokens": 2}, result["usage"])
        self.assertEqual(6, self.server.model_requests)
        self.assertEqual(3, self.server.tool_requests)

    def test_foreign_json_text_result_blocks_before_another_provider_request(self):
        self.server.foreign = True
        scope, harness, contract = self.make_harness()
        result = harness.run(scope, "Read the synthetic observation.", "PA",
                             completion_contract=contract)
        self.assertEqual("blocked", result["status"])
        self.assertEqual(1, self.server.model_requests)
        self.assertNotIn("FOREIGN-PATIENT-MARKER", json.dumps(self.store.load_case(scope)))

    def test_uncertain_effect_is_not_retried_by_http_or_resume(self):
        self.server.fail_tool = True
        scope, harness, contract = self.make_harness()
        first = harness.run(scope, "Read the synthetic observation.", "PA",
                            completion_contract=contract)
        second = harness.run(scope, "Read the synthetic observation.", "PA", resume=True,
                             completion_contract=contract)
        self.assertEqual("blocked", first["status"])
        self.assertEqual("blocked", second["status"])
        self.assertEqual(1, self.server.model_requests)
        self.assertEqual(1, self.server.tool_requests)

    def test_cli_configured_path_uses_only_local_synthetic_endpoints(self):
        from health_harness_codex.cli import main

        scope, _, contract = self.make_harness()
        root = Path(self.temp.name)
        config = {
            "scope": scope.to_dict(), "domain": "PA", "instruction": "Read the synthetic observation.",
            "provider": {"model": "synthetic-model", "base_url": self.base_url + "/v1",
                         "key_env": "HEALTH_HARNESS_TEST_TOKEN"},
            "completion_contract": contract,
            "mcp_servers": [{"url": self.base_url + "/mcp", "namespace": "chi-bench-real-case"}],
            "storage": "cli-state.sqlite", "workspace": "artifacts", "output_dir": "receipts",
        }
        config_path = root / "wire.local.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        output = io.StringIO()
        with patch.dict(os.environ, {"HEALTH_HARNESS_TEST_TOKEN": "dummy-test-key"}), redirect_stdout(output):
            code = main(["--config", str(config_path), "--live"])
        self.assertEqual(0, code, output.getvalue())
        report = json.loads(output.getvalue())
        self.assertEqual("complete", report["status"])
        receipt = json.loads(Path(report["receipt"]).read_text(encoding="utf-8"))
        self.assertEqual("task-contract verified local workflow; not official benchmark success",
                         receipt["completion"]["kind"])
        self.assertTrue(receipt["completion_gate"]["accepted"])
        self.assertEqual(2, self.server.model_requests)
        self.assertEqual(1, self.server.tool_requests)


if __name__ == "__main__":
    unittest.main()
