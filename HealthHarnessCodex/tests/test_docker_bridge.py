import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import TestCase
from unittest.mock import patch

from health_harness_codex.docker_bridge import DockerExecutor, DockerMCPClient, DockerWorkspaceTools, _WORKSPACE_SCRIPT
from health_harness_codex.models import Scope, ToolSpec


class DockerBridgeTests(TestCase):
    @staticmethod
    def _run_workspace(data, timeout=10):
        return subprocess.run([sys.executable, "-c", _WORKSPACE_SCRIPT], input=json.dumps(data),
                              text=True, capture_output=True, timeout=timeout)

    @staticmethod
    def _write_synthetic_pdf(path, page_texts, password=None):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

        writer = PdfWriter()
        for text in page_texts:
            page = writer.add_blank_page(width=300, height=300)
            font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                    NameObject("/Subtype"): NameObject("/Type1"),
                                    NameObject("/BaseFont"): NameObject("/Helvetica")})
            fonts = DictionaryObject({NameObject("/F1"): writer._add_object(font)})
            page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): fonts})
            stream = DecodedStreamObject()
            encoded = text.encode("latin-1", errors="replace").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
            stream.set_data(b"BT /F1 12 Tf 20 250 Td (" + encoded + b") Tj ET")
            page[NameObject("/Contents")] = writer._add_object(stream)
        if password is not None:
            writer.encrypt(password)
        with path.open("wb") as target:
            writer.write(target)

    def test_actual_workspace_script_enforces_roots_traversal_and_hidden_files(self):
        # Exercise the exact fixed program used in Docker, without a model or Docker.
        with tempfile.TemporaryDirectory(prefix="hh-boundary-") as folder:
            base = Path(folder)
            owned, reference, foreign = [base / name for name in ("owned", "reference", "foreign")]
            for path in (owned, reference, foreign):
                path.mkdir()
            private_spool = foreign / "simulator-spool"
            private_spool.mkdir()
            (private_spool / "opaque-request.json").write_text("synthetic-spool-secret", encoding="utf-8")
            (reference / "handbook.md").write_text("approved reference", encoding="utf-8")
            (reference / "expectations.json").write_text("hidden", encoding="utf-8")
            (reference / ".hidden-note.md").write_text("hidden", encoding="utf-8")
            (foreign / "record.md").write_text("other case", encoding="utf-8")
            def invoke(**fields):
                data = {"case_root": str(owned), "read_roots": [str(reference)], **fields}
                return subprocess.run([sys.executable, "-c", _WORKSPACE_SCRIPT],
                                      input=json.dumps(data), text=True, capture_output=True, timeout=5)
            self.assertEqual(invoke(operation="write", path="notes.md", content="own case").returncode, 0)
            self.assertEqual((owned / "notes.md").read_text(encoding="utf-8"), "own case")
            read = invoke(operation="read", path=str(reference / "handbook.md"))
            self.assertEqual(json.loads(read.stdout)["text"], "approved reference")
            self.assertEqual(json.loads(read.stdout)["bytes"], len(b"approved reference"))
            self.assertEqual(json.loads(read.stdout)["total_chars"], len("approved reference"))
            self.assertFalse(json.loads(read.stdout)["has_more"])
            self.assertEqual(json.loads(read.stdout)["sha256"], __import__("hashlib").sha256(b"approved reference").hexdigest())
            reference_listing = invoke(operation="list", path=str(reference))
            self.assertEqual(reference_listing.returncode, 0, reference_listing.stderr)
            reference_files = json.loads(reference_listing.stdout)
            self.assertIn((reference / "handbook.md").resolve(),
                          [Path(name).resolve() for name in reference_files["files"]])
            self.assertTrue(all(Path(name).is_absolute() for name in reference_files["files"]))
            self.assertNotIn(str(reference / "expectations.json"), reference_files["files"])
            self.assertNotIn(str(reference / ".hidden-note.md"), reference_files["files"])
            own_listing = invoke(operation="list", path=".")
            self.assertEqual(own_listing.returncode, 0, own_listing.stderr)
            self.assertTrue(all(not Path(name).is_absolute() for name in json.loads(own_listing.stdout)["files"]))
            foreign_listing = invoke(operation="list", path=str(foreign))
            self.assertEqual(foreign_listing.returncode, 0, foreign_listing.stderr)
            self.assertEqual(json.loads(foreign_listing.stdout)["error"]["code"], "access_denied")
            try:
                (reference / "outside-link.md").symlink_to(foreign / "record.md")
            except (OSError, NotImplementedError):
                pass
            else:
                linked = invoke(operation="list", path=str(reference))
                self.assertEqual(linked.returncode, 0, linked.stderr)
                linked_files = json.loads(linked.stdout)["files"]
                self.assertNotIn(str(foreign / "record.md"), linked_files)
                self.assertNotIn(str(reference / "outside-link.md"), linked_files)
            for path in (str(foreign / "record.md"), "../foreign/record.md",
                         str(private_spool / "opaque-request.json"), str(private_spool),
                         str(reference / "expectations.json")):
                with self.subTest(operation="read", path=path):
                    denied_read = invoke(operation="read", path=path)
                    self.assertEqual(denied_read.returncode, 0, denied_read.stderr)
                    self.assertEqual(json.loads(denied_read.stdout)["error"]["code"], "access_denied")
            denied_write = invoke(operation="write", path=str(reference / "handbook.md"), content="forbidden")
            self.assertNotEqual(denied_write.returncode, 0)
            self.assertEqual((reference / "handbook.md").read_text(encoding="utf-8"), "approved reference")

    def test_large_utf8_file_excerpt_resumes_without_breaking_codepoints(self):
        with tempfile.TemporaryDirectory(prefix="hh-read-offset-") as folder:
            owned = Path(folder) / "owned"
            owned.mkdir()
            content = "é🙂cafe\u0301|" * 5000
            raw = content.encode("utf-8")
            file = owned / "large.txt"
            file.write_bytes(raw)
            offset = 0
            chunks = []
            while True:
                data = {"operation": "read", "case_root": str(owned), "read_roots": [],
                        "path": "large.txt", "max_bytes": 30000, "offset_chars": offset}
                result = self._run_workspace(data)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertLessEqual(len(payload["text"].encode("utf-8")), 30000)
                self.assertEqual(payload["offset_chars"], offset)
                self.assertEqual(payload["bytes"], len(raw))
                self.assertEqual(payload["total_chars"], len(content))
                self.assertEqual(payload["sha256"], __import__("hashlib").sha256(raw).hexdigest())
                chunks.append(payload["text"])
                offset = payload["next_offset"]
                if not payload["has_more"]:
                    break
                self.assertGreater(offset, payload["offset_chars"])
            self.assertEqual("".join(chunks), content)

    def test_bound_case_document_paths_resolve_without_cross_case_access(self):
        with tempfile.TemporaryDirectory(prefix="hh-path-alias-") as folder:
            base = Path(folder) / "workspaces"
            case = base / "CASE-ONE"
            private = case / "provider" / "scope-key"
            shared = case / "shared" / "intake"
            foreign = base / "CASE-TWO" / "shared"
            for p in (private, shared, foreign): p.mkdir(parents=True)
            (shared / "document.txt").write_text("current case text")
            (foreign / "document.txt").write_text("other case secret")
            def read(path):
                result = self._run_workspace({"operation": "read", "case_root": str(private),
                    "read_roots": [str(case / "shared")], "path": path})
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)
            for path in ("CASE-ONE/shared/intake/document.txt", "shared/intake/document.txt"):
                self.assertEqual("current case text", read(path)["text"])
            denied = read("CASE-TWO/shared/document.txt")
            self.assertIn("error", denied)
            self.assertNotIn("other case secret", json.dumps(denied))
            self.assertEqual([str(private.resolve()), str((case / "shared").resolve())], denied["error"]["allowed_read_roots"])

    def test_workspace_read_errors_are_structured_and_contain_no_file_body(self):
        with tempfile.TemporaryDirectory(prefix="hh-read-errors-") as folder:
            owned = Path(folder) / "owned"
            owned.mkdir()
            large = owned / "large.txt"
            large.write_text("PRIVATE-BODY-" + ("x" * 1_000_010), encoding="utf-8")
            binary = owned / "binary.bin"
            binary.write_bytes(b"\x00\xffprivate")
            invalid = owned / "invalid.txt"
            invalid.write_bytes(b"\xffprivate")
            for path, expected in ((large, "file_too_large"), (binary, "binary_or_invalid_utf8"),
                                   (invalid, "binary_or_invalid_utf8"),
                                   (owned / "missing.txt", "file_not_found")):
                with self.subTest(expected=expected):
                    result = self._run_workspace({"operation": "read", "case_root": str(owned), "read_roots": [],
                                                  "path": str(path), "max_bytes": 20})
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["error"]["code"], expected)
                    self.assertNotIn("PRIVATE-BODY", result.stdout)
                    self.assertNotIn("private", result.stdout)

    def test_search_returns_literal_snippets_offsets_hashes_and_result_cap(self):
        with tempfile.TemporaryDirectory(prefix="hh-search-utf8-") as folder:
            owned = Path(folder) / "owned"
            owned.mkdir()
            text = "Straße on line one.\nxx TARGET phrase in the middle.\nTARGET PHRASE again.\n"
            raw = text.encode("utf-8")
            file = owned / "notes.txt"
            file.write_bytes(raw)
            data = {"operation": "search", "case_root": str(owned), "read_roots": [],
                    "path": ".", "query": "strasse", "max_results": 99}
            result = self._run_workspace(data)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(1, len(payload["matches"]))
            match = payload["matches"][0]
            self.assertEqual("notes.txt", match["path"])
            self.assertEqual(text.index("Straße"), match["char_offset"])
            self.assertIn("Straße", match["snippet"])
            self.assertEqual(__import__("hashlib").sha256(raw).hexdigest(), match["sha256"])
            self.assertLessEqual(len(match["snippet"]), 400)
            self.assertLessEqual(payload["limits"]["results"], 10)

            capped = self._run_workspace({**data, "query": "target phrase", "max_results": 1})
            capped_payload = json.loads(capped.stdout)
            self.assertEqual(1, len(capped_payload["matches"]))
            self.assertTrue(capped_payload["truncated"])
            self.assertIn("results", capped_payload["limits_hit"])

    def test_search_respects_roots_blocked_names_and_symlinks(self):
        with tempfile.TemporaryDirectory(prefix="hh-search-roots-") as folder:
            base = Path(folder)
            owned, reference, foreign = [base / name for name in ("owned", "reference", "foreign")]
            for path in (owned, reference, foreign):
                path.mkdir()
            (reference / "policy.txt").write_text("Approved Phrase", encoding="utf-8")
            (reference / "expectations.json").write_text("Approved Phrase hidden", encoding="utf-8")
            (reference / ".hidden-note.txt").write_text("Approved Phrase hidden", encoding="utf-8")
            (foreign / "secret.txt").write_text("Approved Phrase foreign", encoding="utf-8")

            def search(path):
                return self._run_workspace({"operation": "search", "case_root": str(owned),
                                            "read_roots": [str(reference)], "path": str(path),
                                            "query": "approved phrase"})

            reference_result = search(reference)
            self.assertEqual(reference_result.returncode, 0, reference_result.stderr)
            refs = json.loads(reference_result.stdout)
            self.assertEqual([str((reference / "policy.txt").resolve())],
                             [m["path"] for m in refs["matches"]])
            denied = search(foreign)
            self.assertEqual(denied.returncode, 0, denied.stderr)
            denied_payload = json.loads(denied.stdout)
            self.assertEqual("access_denied", denied_payload["error"]["code"])
            self.assertNotIn("foreign", denied.stdout)
            try:
                (reference / "outside-link.txt").symlink_to(foreign / "secret.txt")
            except (OSError, NotImplementedError):
                pass
            else:
                linked = json.loads(search(reference).stdout)
                self.assertEqual([str((reference / "policy.txt").resolve())],
                                 [m["path"] for m in linked["matches"]])

    def test_workspace_listing_caps_names_and_marks_truncation(self):
        with tempfile.TemporaryDirectory(prefix="hh-list-cap-") as folder:
            base = Path(folder)
            owned = base / "owned"
            owned.mkdir()
            for index in range(1002):
                (owned / f"note-{index:04d}.md").touch()
            data = {"operation": "list", "case_root": str(owned), "read_roots": [], "path": "."}
            result = subprocess.run([sys.executable, "-c", _WORKSPACE_SCRIPT], input=json.dumps(data),
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(1000, len(payload["files"]))
            self.assertTrue(payload["truncated"])

    def test_uncreated_owned_workspace_lists_and_searches_as_empty(self):
        with tempfile.TemporaryDirectory(prefix="hh-empty-workspace-") as folder:
            root = Path(folder) / "not-created-yet"
            for operation, expected_key in (("list", "files"), ("search", "matches")):
                data = {"operation": operation, "case_root": str(root), "read_roots": [], "path": "."}
                if operation == "search":
                    data["query"] = "anything"
                result = self._run_workspace(data)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual([], payload[expected_key])
                self.assertFalse(payload["truncated"])
                self.assertFalse(root.exists())

    def test_dot_workspace_with_current_case_reference_roots_does_not_index_empty_parts(self):
        with tempfile.TemporaryDirectory(prefix="hh-current-case-") as folder:
            case = Path(folder) / "workspaces" / "synthetic-case"
            shared = case / "shared"
            shared.mkdir(parents=True)
            root = case / "care-manager"
            for operation, key in (("list", "files"), ("search", "matches")):
                data = {"operation": operation, "case_root": str(root), "read_roots": [str(shared)],
                        "path": ".", "query": "synthetic"}
                result = self._run_workspace(data)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual([], json.loads(result.stdout)[key])
            self.assertFalse(root.exists())

    def test_search_marks_files_and_total_scan_limits(self):
        with tempfile.TemporaryDirectory(prefix="hh-search-limits-") as folder:
            owned = Path(folder) / "owned"
            owned.mkdir()
            (owned / "too-large.txt").write_bytes(b"no match " + b"x" * 1_000_001)
            per_file = self._run_workspace({"operation": "search", "case_root": str(owned), "read_roots": [],
                                            "path": ".", "query": "no match"})
            per_file_payload = json.loads(per_file.stdout)
            self.assertTrue(per_file_payload["truncated"])
            self.assertIn("per_file_bytes", per_file_payload["limits_hit"])
            self.assertEqual(1, per_file_payload["skipped_large_files"])

        with tempfile.TemporaryDirectory(prefix="hh-search-total-limit-") as folder:
            owned = Path(folder) / "owned"
            owned.mkdir()
            block = b"x" * 999_999
            for index in range(21):
                (owned / f"file-{index:02d}.txt").write_bytes(block)
            result = self._run_workspace({"operation": "search", "case_root": str(owned), "read_roots": [],
                                          "path": ".", "query": "never-present"}, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["truncated"])
            self.assertIn("bytes", payload["limits_hit"])
            self.assertLessEqual(payload["scanned_bytes"], 20_000_000)

    def test_read_pdf_extracts_selected_pages_and_resumes_bounded_text_layer(self):
        with tempfile.TemporaryDirectory(prefix="hh-read-pdf-") as folder:
            owned = Path(folder) / "owned"
            owned.mkdir()
            path = owned / "synthetic.pdf"
            page_texts = ["Synthetic first page text", "Synthetic second page has more text", "Synthetic third page"]
            self._write_synthetic_pdf(path, page_texts)
            digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()

            first = self._run_workspace({"operation": "read_pdf", "case_root": str(owned), "read_roots": [],
                                         "path": "synthetic.pdf", "page_start": 2, "page_count": 2,
                                         "max_chars": 10})
            self.assertEqual(first.returncode, 0, first.stderr)
            payload = json.loads(first.stdout)
            self.assertEqual(digest, payload["sha256"])
            self.assertEqual(3, payload["total_pages"])
            self.assertEqual("pypdf text-layer extraction", payload["extraction_method"])
            self.assertTrue(payload["text_layer_only"])
            self.assertFalse(payload["ocr_performed"])
            self.assertTrue(payload["no_layout_validation"])
            self.assertTrue(payload["truncated"])
            self.assertTrue(payload["has_more"])
            self.assertEqual(2, payload["next_page"])
            self.assertEqual(10, payload["next_char_offset"])
            self.assertEqual("Synthetic ", payload["pages"][0]["text"])
            self.assertLessEqual(sum(len(page["text"]) for page in payload["pages"]), 10)
            self.assertEqual(20_000, payload["parser_budget"]["max_output_chars"])

            resumed = self._run_workspace({"operation": "read_pdf", "case_root": str(owned), "read_roots": [],
                                           "path": "synthetic.pdf", "page_start": payload["next_page"],
                                           "page_char_offset": payload["next_char_offset"], "page_count": 2,
                                           "max_chars": 20000})
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            resumed_payload = json.loads(resumed.stdout)
            self.assertEqual("Synthetic second page has more text", payload["pages"][0]["text"] +
                             resumed_payload["pages"][0]["text"])
            self.assertEqual("Synthetic third page", resumed_payload["pages"][1]["text"])
            self.assertFalse(resumed_payload["has_more"])
            self.assertIsNone(resumed_payload["next_page"])

    def test_read_pdf_rejects_foreign_roots_symlinks_malformed_encrypted_and_scanned(self):
        with tempfile.TemporaryDirectory(prefix="hh-read-pdf-boundary-") as folder:
            base = Path(folder)
            owned, reference, foreign = [base / name for name in ("owned", "reference", "foreign")]
            for path in (owned, reference, foreign):
                path.mkdir()
            allowed = reference / "allowed.pdf"
            self._write_synthetic_pdf(allowed, ["Synthetic allowed reference page"])
            malformed = reference / "malformed.pdf"
            malformed.write_bytes(b"not a PDF file")
            encrypted = reference / "encrypted.pdf"
            self._write_synthetic_pdf(encrypted, ["Synthetic encrypted page"], password="test-only")
            scanned = reference / "scanned.pdf"
            self._write_synthetic_pdf(scanned, [""])
            foreign_pdf = foreign / "foreign.pdf"
            self._write_synthetic_pdf(foreign_pdf, ["SYNTHETIC-FOREIGN-BODY"])
            read_roots = [str(reference)]

            def read_pdf(path):
                return self._run_workspace({"operation": "read_pdf", "case_root": str(owned),
                                            "read_roots": read_roots, "path": str(path)})

            success = read_pdf(allowed)
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertIn("Synthetic allowed reference page", json.loads(success.stdout)["pages"][0]["text"])
            denied = read_pdf(foreign_pdf)
            self.assertEqual(denied.returncode, 0, denied.stderr)
            self.assertEqual("access_denied", json.loads(denied.stdout)["error"]["code"])
            self.assertNotIn("SYNTHETIC-FOREIGN-BODY", denied.stdout)
            for path, expected in ((malformed, "invalid_pdf"), (encrypted, "encrypted_pdf"),
                                   (scanned, "text_unavailable")):
                result = read_pdf(path)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual("", result.stderr)
                self.assertEqual(expected, json.loads(result.stdout)["error"]["code"])
                if expected == "text_unavailable":
                    self.assertIn("OCR is required", json.loads(result.stdout)["error"]["message"])
            try:
                (reference / "outside.pdf").symlink_to(foreign_pdf)
            except (OSError, NotImplementedError):
                pass
            else:
                linked = read_pdf(reference / "outside.pdf")
                self.assertEqual("access_denied", json.loads(linked.stdout)["error"]["code"])
                self.assertNotIn("SYNTHETIC-FOREIGN-BODY", linked.stdout)

    def test_pdf_reader_tool_is_registered_read_only_and_uses_bounded_arguments(self):
        class Executor:
            def __init__(self):
                self.data = []
            def python_json(self, script, data, timeout=None):
                self.data.append(data)
                return {"pages": [], "has_more": False}

        scope = Scope("docker:test", "pa_test", "org", "payer", "patient", "case")
        executor = Executor()
        tools = DockerWorkspaceTools("owned-case", "/logs/workspaces", scope,
                                     read_roots=("/workspace/skills/handbook",), executor=executor)
        spec = next(item for item in tools.list_tools() if item.name == "workspace.read_pdf")
        self.assertEqual("read", spec.effect)
        tools.call("workspace.read_pdf", {"path": "/workspace/skills/handbook/policy.pdf"})
        self.assertEqual("read_pdf", executor.data[-1]["operation"])
        self.assertEqual(3, executor.data[-1]["page_count"])
        self.assertEqual(20_000, executor.data[-1]["max_chars"])

    def test_executor_uses_fixed_docker_exec_no_shell_and_bounded_json(self):
        with patch("health_harness_codex.docker_bridge.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = '{"answer":42}'
            value = DockerExecutor("owned-case", timeout=2).python_json("print('{}')", {"x": "y"})
        self.assertEqual(value, {"answer": 42})
        args, kwargs = run.call_args
        self.assertEqual(args[0][:5], ["docker", "exec", "-i", "owned-case", "/workspace/.venv/bin/python"])
        self.assertEqual(args[0][-2:], ["-c", "print('{}')"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(json.loads(kwargs["input"]), {"x": "y"})
        self.assertEqual(kwargs["timeout"], 2)

    def test_executor_rejects_invalid_container_and_bounded_timeout(self):
        with self.assertRaises(ValueError):
            DockerExecutor("bad;docker rm")
        with self.assertRaises(ValueError):
            DockerExecutor("owned-case", timeout=0)

    def test_mcp_adapter_uses_container_loopback_and_preserves_session(self):
        class Executor:
            def __init__(self):
                self.inputs = []

            def python_json(self, script, data, timeout=None):
                self.inputs.append((script, data, timeout))
                payload = data["payload"]
                if payload["method"] == "initialize":
                    result = {"protocolVersion": "2025-03-26"}
                elif payload["method"] == "tools/list":
                    result = {"tools": [{"name": "payer_intake_hub.list_intake_queue",
                                          "inputSchema": {"type": "object", "properties": {}}}]}
                else:
                    result = {}
                envelope = {"jsonrpc": "2.0", "id": payload.get("id"), "result": result}
                return {"status": 200,
                        "headers": {"Content-Type": "application/json", "Mcp-Session-Id": "session-1"},
                        "body": base64.b64encode(json.dumps(envelope).encode()).decode()}

        executor = Executor()
        client = DockerMCPClient("owned-case", executor=executor)
        specs = client.list_tools()
        self.assertEqual(len(specs), 1)
        self.assertEqual(client.session_id, "session-1")
        self.assertEqual(executor.inputs[-1][1]["port"], 8100)
        self.assertEqual(executor.inputs[-1][1]["payload"]["method"], "tools/list")
        self.assertEqual(executor.inputs[-1][1]["headers"]["Mcp-Session-Id"], "session-1")

    def test_mcp_port_allowlist_is_closed(self):
        for port in (22, 3000, 8101):
            with self.subTest(port=port), self.assertRaises(ValueError):
                DockerMCPClient("owned-case", port=port)

    def test_trial_validation_checks_only_owned_label_and_task_match(self):
        class Executor(DockerExecutor):
            def python_json(self, script, data, timeout=None):
                self.task_probe = (script, data)
                return {"task_matches": True}

        with patch("health_harness_codex.docker_bridge.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = 'true|{"com.bigdata.workspace":"BigData/HealthHarnessCodex"}'
            executor = Executor("bigdata-health-codex-um-test")
            executor.validate_owned_trial("pa_t012_case")
        args = run.call_args.args[0]
        self.assertEqual(args[1], "inspect")
        self.assertIn(".Config.Labels", args[3])
        self.assertEqual(executor.task_probe[1], {"task_id": "pa_t012_case"})

    def test_trial_validation_rejects_nonowned_or_wrong_task(self):
        with patch("health_harness_codex.docker_bridge.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = 'true|{"unrelated":"yes"}'
            with self.assertRaisesRegex(Exception, "owned-case"):
                DockerExecutor("unowned").validate_owned_trial("pa_t012_case")

    def test_workspace_tools_scope_write_and_reference_roots_are_explicit(self):
        class Executor:
            def __init__(self):
                self.data = []

            def python_json(self, script, data, timeout=None):
                self.data.append(data)
                return {"files": []}

        scope = Scope("docker:test", "pa_test", "org", "payer", "patient", "case")
        executor = Executor()
        tools = DockerWorkspaceTools("owned-case", "/logs/workspaces", scope,
                                     read_roots=("/workspace/skills/handbook",), executor=executor)
        specs = {spec.name: spec for spec in tools.list_tools()}
        self.assertEqual(specs["workspace.write_file"].effect, "write")
        self.assertEqual(specs["workspace.read_file"].effect, "read")
        self.assertEqual(specs["workspace.search_files"].effect, "read")
        tools.call("workspace.read_file", {"path": "reference.md"})
        self.assertEqual(executor.data[-1]["case_root"], f"/logs/workspaces/{scope.key}")
        self.assertIn("/workspace/skills/handbook", executor.data[-1]["read_roots"])
        tools.call("workspace.search_files", {"query": "policy phrase", "path": "/workspace/skills/handbook"})
        self.assertEqual(executor.data[-1]["operation"], "search")
        self.assertEqual(executor.data[-1]["query"], "policy phrase")
        self.assertEqual(executor.data[-1]["max_results"], 3)
        self.assertIn('"expectations"', __import__("health_harness_codex.docker_bridge", fromlist=["_WORKSPACE_SCRIPT"])._WORKSPACE_SCRIPT)
        with self.assertRaises(ValueError):
            tools.bind_scope(Scope("docker:test", "pa_test", "org", "payer", "other-patient", "case"))


if __name__ == "__main__":
    import unittest
    unittest.main()
