import json
import unittest

from health_harness_codex.engine import Harness
from health_harness_codex.models import Limits, ModelReply, Scope, ToolCall, ToolSpec
from health_harness_codex.store import CaseStore
from health_harness_codex.synthetic_contracts import operator_observation_contract


class Model:
    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []

    def complete(self, messages, tools, **kwargs):
        self.seen.append(messages)
        return self.replies.pop(0)


class Tools:
    def __init__(self):
        self.calls = []

    def list_tools(self):
        return [ToolSpec("case_lookup", "Read the current case", {"type": "object",
                         "properties": {"case_id": {"type": "string"}}, "required": ["case_id"]})]

    def call(self, name, args):
        self.calls.append((name, args))
        return {"case_id": args["case_id"], "status": "observed"}


class ContinuationEngineTests(unittest.TestCase):
    def setUp(self):
        self.store = CaseStore(":memory:")
        self.scope = Scope("env", "task", "org", "actor", "p", "c")
        self.tools = Tools()
        self.limits = Limits(4, 8, 60000, 4096)
        self.contract = operator_observation_contract(
            self.scope, "UM", "case_lookup", [
                {"id": "case_identity", "path": "case_id", "op": "eq", "value": self.scope.case},
                {"id": "readback_status", "path": "status", "op": "eq", "value": "observed"},
            ])
        self.first = self.execute([
            ModelReply(tool_calls=(ToolCall("r", "case_lookup", {"case_id": "c"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "Read observed", "evidence_ids": ["ev:m1:r"]})),
        ])

    def tearDown(self):
        self.store.close()

    def execute(self, replies, **kwargs):
        self.model = Model(replies)
        return Harness(self.store, self.model, self.tools, self.limits).run(
            self.scope, "Read current case", "UM", completion_contract=self.contract, **kwargs)

    def test_explicit_audit_preserves_previous_result_and_never_replays_old_read(self):
        result = self.execute([
            ModelReply(tool_calls=(ToolCall("audit", "case_lookup", {"case_id": "c"}),)),
            ModelReply(content=json.dumps({"status": "complete", "claim": "Audit observed", "evidence_ids": ["ev:m3:audit"]})),
        ], resume=True, continuation_note="Audit unmet requirements using actual readbacks.",
           continuation_limits=Limits(8, 16, 60000, 4096))
        self.assertEqual(result["status"], "complete")
        self.assertEqual(len(self.tools.calls), 2)
        state = self.store.load_case(self.scope)
        self.assertEqual(state["continuations"][0]["previous_completion"], self.first["completion"])
        self.assertTrue(state["continuations"][0]["previous_completion_gate"]["accepted"])
        self.assertEqual(state["continuations"][0]["model_calls_at_start"], 2)
        self.assertEqual(state["budgets"]["max_model_calls"], 8)
        self.assertEqual(state["scope"], self.scope.to_dict())
        self.assertIn("Audit unmet requirements", json.dumps(self.model.seen[0]))
        ledger_text = self.model.seen[0][0]["content"].split(
            "Current case ledger (source index and open obligations):\n", 1)[1]
        self.assertIsNone(json.loads(ledger_text)["completion_verification"])

    def test_plain_resume_does_not_reopen_completion_or_accept_implicit_budget_change(self):
        result = self.execute([], resume=True)
        self.assertEqual(result["completion"], self.first["completion"])
        self.assertEqual(len(self.tools.calls), 1)
        with self.assertRaises(ValueError):
            self.execute([], resume=True, continuation_note="")
        with self.assertRaises(ValueError):
            self.execute([], resume=True, continuation_limits=Limits(8, 16, 60000, 4096))
        with self.assertRaises(ValueError):
            self.execute([], resume=True, continuation_note="Audit", continuation_limits=Limits(3, 8, 60000, 4096))

    def test_unknown_write_blocks_audit_before_any_model_or_tool_replay(self):
        self.store.reserve_action(self.scope, "uncertain", "write", {}, "write")
        self.store.unknown_action(self.scope, "uncertain", "needs actual readback")
        result = self.execute([], resume=True, continuation_note="Audit completion")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(len(self.model.seen), 0)
        self.assertEqual(len(self.tools.calls), 1)
        self.assertEqual(self.store.actions(self.scope)[-1]["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
