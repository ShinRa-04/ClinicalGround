import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from health_harness_codex.intake_sources import (
    IntakeSourceReader,
    _READ_INTAKE_PDF_SCRIPT,
    find_intake_request_form,
)


class IntakeSourceReaderTests(unittest.TestCase):
    def test_reader_uses_only_supplied_case_metadata_and_returns_bounded_text_hash(self):
        executor = _Executor({
            "text": "Synthetic request form text",
            "source_sha256": "a" * 64,
            "page_count": 1,
            "truncated": False,
        })
        result = IntakeSourceReader(executor)("CASE-1", _form("CASE-1"))
        self.assertEqual("Synthetic request form text", result["text"])
        self.assertEqual("a" * 64, result["source_sha256"])
        self.assertEqual(1, result["page_count"])
        self.assertEqual(1, len(executor.calls))
        script, payload, timeout = executor.calls[0]
        self.assertEqual({"case_id": "CASE-1", "relative_path": "CASE-1/shared/intake/form.pdf"}, payload)
        self.assertEqual(30, timeout)
        self.assertIn("from pypdf import PdfReader", script)
        self.assertIn("base != base_path", script)
        self.assertIn("candidate.relative_to(base)", script)
        self.assertIn("remaining-=len(separator)", script)
        self.assertNotIn("provider_content_url", script)
        self.assertNotIn("payer_content_url", payload)
        self.assertNotIn("content", payload)
        compile(script, "<fixed intake reader>", "exec")

    def test_accepts_case_specific_payer_incoming_request_path(self):
        executor = _Executor({"text": "Synthetic", "source_sha256": "a" * 64})
        result = IntakeSourceReader(executor)(
            "CASE-1", _form("CASE-1", relative_path="CASE-1/payer/incoming_request/form.pdf")
        )
        self.assertEqual("Synthetic", result["text"])
        self.assertEqual("CASE-1/payer/incoming_request/form.pdf", executor.calls[0][1]["relative_path"])

    def test_rejects_foreign_case_before_calling_executor(self):
        executor = _Executor({})
        with self.assertRaisesRegex(ValueError, "does not match"):
            IntakeSourceReader(executor)("CASE-1", _form("CASE-2"))
        self.assertEqual([], executor.calls)

    def test_rejects_path_escape_and_unapproved_workspace_roots(self):
        executor = _Executor({})
        for path in (
            "CASE-1/shared/intake/../other.pdf",
            "CASE-1/provider/incoming_request/form.pdf",
            "CASE-1/shared/clinical/form.pdf",
            "CASE-1/shared/intake\\form.pdf",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                IntakeSourceReader(executor)("CASE-1", _form("CASE-1", relative_path=path))
        self.assertEqual([], executor.calls)

    def test_fixed_reader_rejects_case_root_symlink_to_another_cases_intake(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspaces"
            foreign_root = workspace / "CASE-2" / "shared" / "intake"
            foreign_root.mkdir(parents=True)
            (foreign_root / "form.pdf").write_bytes(b"synthetic")
            case_root = workspace / "CASE-1" / "shared"
            case_root.mkdir(parents=True)
            try:
                (case_root / "intake").symlink_to(foreign_root, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"directory symlinks unavailable: {type(exc).__name__}")
            script = _script_for_workspace(workspace)
            with self.assertRaisesRegex(ValueError, "redirected through a symlink"):
                _execute_fixed_script(script, {"case_id": "CASE-1", "relative_path": "CASE-1/shared/intake/form.pdf"})

    def test_fixed_reader_counts_page_separators_inside_the_text_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspaces"
            root = workspace / "CASE-1" / "shared" / "intake"
            root.mkdir(parents=True)
            (root / "form.pdf").write_bytes(b"synthetic")
            fake_pypdf = types.ModuleType("pypdf")
            fake_pypdf.PdfReader = lambda *_args, **_kwargs: types.SimpleNamespace(
                pages=[_Page("x" * 19999), _Page("second page")]
            )
            script = _script_for_workspace(workspace)
            output = _execute_fixed_script(
                script,
                {"case_id": "CASE-1", "relative_path": "CASE-1/shared/intake/form.pdf"},
                fake_pypdf=fake_pypdf,
            )
        self.assertEqual(20_000, len(output["text"]))
        self.assertTrue(output["truncated"])

    def test_requires_actual_intake_form_metadata_and_pdf(self):
        executor = _Executor({})
        for metadata in (
            _form("CASE-1", artifact_type="document"),
            _form("CASE-1", relative_path="CASE-1/shared/intake/form.txt"),
        ):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                IntakeSourceReader(executor)("CASE-1", metadata)
        self.assertEqual([], executor.calls)

    def test_document_lookup_requires_exactly_one_form_for_selected_case(self):
        result = {"structuredContent": {"items": [
            _form("CASE-OTHER"),
            {**_form("CASE-1"), "artifact_type": "document"},
            _form("CASE-1"),
        ]}}
        self.assertIs(find_intake_request_form(result, "CASE-1"), result["structuredContent"]["items"][2])
        with self.assertRaisesRegex(ValueError, "exactly one"):
            find_intake_request_form({"structuredContent": {"items": [_form("CASE-OTHER")]}}, "CASE-1")

    def test_rejects_bad_hash_or_oversized_reader_result(self):
        for result in (
            {"text": "text", "source_sha256": "not-a-hash"},
            {"text": "x" * 19999 + "\n\n", "source_sha256": "b" * 64},
        ):
            with self.subTest(result_keys=list(result)), self.assertRaises(ValueError):
                IntakeSourceReader(_Executor(result))("CASE-1", _form("CASE-1"))


def _form(case_id, artifact_type="intake_request_form", relative_path=None):
    return {
        "case_id": case_id,
        "artifact_type": artifact_type,
        "relative_path": relative_path or f"{case_id}/shared/intake/form.pdf",
        "payer_content_url": "/payer/workspace/artifacts/capability/content",
        "provider_content_url": "/provider/workspace/artifacts/forbidden/content",
    }


class _Executor:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def python_json(self, script, payload, timeout=None):
        self.calls.append((script, dict(payload), timeout))
        return self.response


class _Page:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


def _script_for_workspace(workspace):
    return _READ_INTAKE_PDF_SCRIPT.replace(
        'Path("/logs/artifacts/workspaces")', f"Path({str(workspace)!r})"
    )


def _execute_fixed_script(script, payload, fake_pypdf=None):
    stdout = io.StringIO()
    if fake_pypdf is None:
        fake_pypdf = types.ModuleType("pypdf")
        fake_pypdf.PdfReader = lambda *_args, **_kwargs: types.SimpleNamespace(pages=[])
    modules = {"pypdf": fake_pypdf}
    with patch.dict(sys.modules, modules), patch("sys.stdin", io.StringIO(json.dumps(payload))), \
            contextlib.redirect_stdout(stdout):
        exec(compile(script, "<fixed intake reader>", "exec"), {})
    return json.loads(stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
