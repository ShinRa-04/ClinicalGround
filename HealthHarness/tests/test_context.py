import unittest
import tempfile
from pathlib import Path

from health_harness.context import project_context
from health_harness.models import Scope, ToolSpec
from health_harness.store import CaseStore


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
        self.assertNotIn("x" * 200, text)
        assistant_calls = {call["id"] for m in projected if m.get("role") == "assistant" for call in m.get("tool_calls", [])}
        tool_results = {m.get("tool_call_id") for m in projected if m.get("role") == "tool"}
        self.assertEqual(assistant_calls, tool_results)

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
