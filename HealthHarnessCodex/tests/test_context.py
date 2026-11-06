import copy
import json
import unittest
import tempfile
from pathlib import Path

from health_harness_codex.context import project_context
from health_harness_codex.models import Scope, ToolSpec
from health_harness_codex.store import CaseStore


class ContextProjectionTests(unittest.TestCase):
    def test_projection_keeps_request_ledger_and_complete_recent_turns(self):
        state = {
            "scope": {"patient": "p-1", "case": "c-1"},
            "obligations": [{"id": "todo", "status": "open", "description": "still pending"}],
            "evidence": [
                {"id": "ev:old", "tool": "records.read", "outcome": "success", "action_id": "m1:old", "observed_result": {"large": "x" * 5000}},
                {"id": "ev:new", "tool": "records.read", "outcome": "success", "action_id": "m2:new", "observed_result": {"ok": True}},
            ],
        }
        messages = [
            {"role": "system", "content": "immutable role prompt"},
            {"role": "user", "content": "original assigned request"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "old", "name": "records.read", "arguments": {}}]},
            {"role": "tool", "tool_call_id": "old", "name": "records.read", "evidence_id": "ev:old", "content": "x" * 5000},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "new", "name": "records.read", "arguments": {}}]},
            {"role": "tool", "tool_call_id": "new", "name": "records.read", "evidence_id": "ev:new", "content": '{"ok":true}'},
        ]
        projected = project_context(messages, state, [], max_chars=2400, large_tool_chars=100)
        self.assertIsNotNone(projected)
        text = str(projected)
        self.assertIn("immutable role prompt", text)
        self.assertIn("original assigned request", text)
        self.assertIn("todo", text)
        self.assertIn("ev:old", text)  # retained source index allows rehydration
        self.assertIn("ev:new", text)
        self.assertNotIn("x" * 5000, text)
        self.assertIn("partial_preview", text)
        self.assertIn("preview_is_partial", text)
        assistant_calls = {call["id"] for m in projected if m.get("role") == "assistant" for call in m.get("tool_calls", [])}
        tool_results = {m.get("tool_call_id") for m in projected if m.get("role") == "tool"}
        self.assertEqual(assistant_calls, tool_results)

    def test_raw_recent_tool_result_is_preserved_when_it_fits_even_above_compaction_threshold(self):
        source_text = "Observed long record: " + ("padding " * 300) + "DEEP_FACT=SYNTHETIC-OBSERVATION"
        raw_tool_content = json.dumps({"evidence_id": "ev:m1:read", "outcome": "success",
                                       "observed_result": {"text": source_text}}, ensure_ascii=False)
        messages = [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "Read the record"},
            {"role": "assistant", "content": "Reading the requested record.",
             "tool_calls": [{"id": "read", "name": "records.read", "arguments": {}}]},
            {"role": "tool", "tool_call_id": "read", "name": "records.read",
             "evidence_id": "ev:m1:read", "content": raw_tool_content},
        ]
        state = {"scope": {"case": "case-1", "patient": "patient-1"}, "obligations": [],
                 "evidence": [{"id": "ev:m1:read", "tool": "records.read", "outcome": "success",
                               "action_id": "m1:read", "observed_result": {"text": source_text}}]}

        projected = project_context(messages, state, [], max_chars=7000, large_tool_chars=100)

        self.assertIsNotNone(projected)
        observed_tool = next(message for message in projected if message.get("role") == "tool")
        self.assertEqual(raw_tool_content, observed_tool["content"])
        self.assertIn("DEEP_FACT=SYNTHETIC-OBSERVATION", observed_tool["content"])

    def test_tight_budget_compacts_older_evidence_group_and_keeps_latest_group_raw(self):
        old_result = {"path": "/approved/reference/medical-policy.pdf", "sha256": "a" * 64,
                      "total_pages": 4, "page_start": 2, "pages": [{"page": 2, "text": "private page body"}],
                      "extraction_method": "pypdf text-layer extraction", "truncated": True,
                      "has_more": True}
        old_raw = json.dumps({"evidence_id": "ev:m1:pdf", "outcome": "success",
                              "observed_result": {**old_result, "padding": "z" * 5000}}, ensure_ascii=False)
        latest_raw = '{"evidence_id":"ev:m2:status","outcome":"success","observed_result":{"status":"pending"}}'
        messages = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "Review the record"},
            {"role": "assistant", "content": "Read the policy", "tool_calls": [
                {"id": "pdf", "name": "workspace.read_pdf", "arguments": {"path": "/approved/reference/medical-policy.pdf"}}]},
            {"role": "tool", "tool_call_id": "pdf", "name": "workspace.read_pdf", "evidence_id": "ev:m1:pdf", "content": old_raw},
            {"role": "assistant", "content": "Check current status", "tool_calls": [
                {"id": "status", "name": "records.summary", "arguments": {}}]},
            {"role": "tool", "tool_call_id": "status", "name": "records.summary", "evidence_id": "ev:m2:status", "content": latest_raw},
        ]
        original = copy.deepcopy(messages)
        state = {"scope": {"case": "case-1", "patient": "patient-1"}, "obligations": [], "evidence": [
            {"id": "ev:m1:pdf", "tool": "workspace.read_pdf", "outcome": "success", "action_id": "m1:pdf",
             "observed_result": old_result},
            {"id": "ev:m2:status", "tool": "records.summary", "outcome": "success", "action_id": "m2:status",
             "observed_result": {"status": "pending"}},
        ]}

        projected = project_context(messages, state, [], max_chars=3200, large_tool_chars=100)

        self.assertIsNotNone(projected)
        self.assertEqual(original, messages, "context projection must not modify persisted input messages")
        old_tool = next(message for message in projected if message.get("evidence_id") == "ev:m1:pdf")
        latest_tool = next(message for message in projected if message.get("evidence_id") == "ev:m2:status")
        self.assertNotEqual(old_raw, old_tool["content"])
        summary = json.loads(old_tool["content"])
        self.assertEqual("ev:m1:pdf", summary["evidence_id"])
        self.assertTrue(summary["preview_is_partial"])
        self.assertEqual("/approved/reference/medical-policy.pdf", summary["source_metadata"]["source_path"])
        self.assertEqual([2], summary["source_metadata"]["source_pages"])
        self.assertEqual(latest_raw, latest_tool["content"])
        call_ids = {call["id"] for message in projected for call in message.get("tool_calls", [])}
        result_ids = {message.get("tool_call_id") for message in projected if message.get("role") == "tool"}
        self.assertEqual(call_ids, result_ids)

    def test_oversized_newest_complete_group_returns_none_instead_of_dropping_its_result(self):
        state = {"scope": {"case": "case-1"}, "obligations": [],
                 "evidence": [{"id": "ev:m1:latest", "tool": "records.lookup", "outcome": "success",
                               "observed_result": {"text": "x" * 5000}}]}
        messages = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "Current request"},
            {"role": "assistant", "content": "lookup", "tool_calls": [{"id": "latest", "name": "records.lookup",
             "arguments": {"large_argument": "a" * 4000}}]},
            {"role": "tool", "tool_call_id": "latest", "name": "records.lookup",
             "evidence_id": "ev:m1:latest", "content": "x" * 5000},
        ]
        original = copy.deepcopy(messages)

        projected = project_context(messages, state, [], max_chars=1800, large_tool_chars=100)

        self.assertIsNone(projected)
        self.assertEqual(original, messages)

    def test_partial_tool_groups_and_orphan_tool_messages_are_never_projected(self):
        messages = [
            {"role": "system", "content": "system"}, {"role": "user", "content": "request"},
            {"role": "assistant", "content": "two calls", "tool_calls": [
                {"id": "a", "name": "a", "arguments": {}}, {"id": "b", "name": "b", "arguments": {}}]},
            {"role": "tool", "tool_call_id": "a", "name": "a", "content": "only one response"},
            {"role": "tool", "tool_call_id": "orphan", "name": "orphan", "content": "orphan response"},
        ]
        state = {"scope": {"case": "case-1"}, "obligations": [], "evidence": []}

        projected = project_context(messages, state, [], max_chars=5000)

        self.assertEqual(["system", "user"], [message["role"] for message in projected])
        self.assertNotIn("only one response", str(projected))
        self.assertNotIn("orphan response", str(projected))

    def test_evidence_manifest_keeps_pdf_source_metadata_without_page_text(self):
        state = {"scope": {"case": "case-1"}, "obligations": [], "evidence": [{
            "id": "ev:pdf", "tool": "workspace.read_pdf", "outcome": "success", "action_id": "m1:pdf",
            "observed_result": {"path": "/approved/source.pdf", "sha256": "b" * 64,
                                "total_pages": 5, "page_start": 2,
                                "pages": [{"page": 2, "text": "PDF BODY MUST NOT ENTER INDEX"}],
                                "extraction_method": "pypdf text-layer extraction", "text_layer_only": True,
                                "truncated": True, "has_more": True},
        }]}
        messages = [{"role": "system", "content": "system"}, {"role": "user", "content": "request"}]

        projected = project_context(messages, state, [], max_chars=5000)
        system = projected[0]["content"]

        self.assertIn("/approved/source.pdf", system)
        self.assertIn("source_pages", system)
        self.assertIn("pypdf text-layer extraction", system)
        self.assertNotIn("PDF BODY MUST NOT ENTER INDEX", system)

    def test_protected_essentials_that_exceed_limit_return_none(self):
        state = {"scope": {"case": "c"}, "obligations": [], "evidence": []}
        projected = project_context([
            {"role": "system", "content": "x" * 500},
            {"role": "user", "content": "request"},
        ], state, [ToolSpec("t", "", {"type": "object"})], max_chars=100)
        self.assertIsNone(projected)

    def test_changing_patient_a_state_does_not_change_b_model_context(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CaseStore(Path(temp) / "state.sqlite")
            a = Scope("env", "task-a", "org", "principal", "patient-a", "case-a")
            b = Scope("env", "task-b", "org", "principal", "patient-b", "case-b")
            state_a = store.open_case(a, "A instruction", "PA")
            state_b = store.open_case(b, "B instruction", "PA")
            try:
                state_b["messages"] = [{"role": "system", "content": "B system"}, {"role": "user", "content": "B task"}]
                state_b["version"] = store.save_case(b, state_b, 0)
                before = project_context(state_b["messages"], state_b, [], 10000)
                state_a["evidence"].append({"id": "private-A", "outcome": "success", "observed_result": {"note": "A marker"}})
                state_a["messages"] = [{"role": "system", "content": "A system"}, {"role": "user", "content": "A marker"}]
                store.save_case(a, state_a, 0)
                current_b = store.load_case(b)
                after = project_context(current_b["messages"], current_b, [], 10000)
                self.assertEqual(before, after)
                self.assertNotIn("A marker", str(after))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
