from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from health_harness_codex.openrouter_judge import OpenRouterJudgeRunner
from health_harness_codex.deferred_grading import DockerOfflineGrader, OpenRouterOfflineGrader


class Response:
    def __init__(self, message):
        self.body = {"choices": [{"message": message}], "usage": {"cost": 0.001}}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, *args): return json.dumps(self.body).encode()


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "input"
        self.workspace.mkdir()
        (self.workspace / "record.json").write_text('{"synthetic":true}')

    def runner(self, opener):
        return OpenRouterJudgeRunner(self.root / "private", opener=opener, key_loader=lambda: "test-secret")

    def test_real_tool_loop_preserves_prompt_and_verdict_and_cost(self):
        captured = []
        answers = [
            {"role": "assistant", "content": None, "tool_calls": [{"id": "r1", "type": "function", "function": {"name": "Read", "arguments": '{"file_path":"record.json"}'}}]},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "w1", "type": "function", "function": {"name": "Write", "arguments": json.dumps({"file_path": "verdicts.json", "content": '{"rubric_verdicts":{}}'})}}]},
            {"role": "assistant", "content": "done"}]
        def opener(request, **kwargs):
            captured.append(json.loads(request.data))
            return Response(answers.pop(0))
        runner = self.runner(opener)
        self.assertEqual("done", runner.run_session("UNCHANGED OFFICIAL PROMPT", self.workspace, ["Read", "Write"]))
        self.assertEqual("UNCHANGED OFFICIAL PROMPT", captured[0]["messages"][0]["content"])
        self.assertIn('"synthetic":true', captured[1]["messages"][-1]["content"])
        self.assertTrue((runner.root / "workspace/verdicts.json").is_file())
        ledger = json.loads(runner.ledger.read_text())
        self.assertAlmostEqual(0.003, sum(x["cost_usd"] for x in ledger["requests"]))
        self.assertNotIn("test-secret", runner.ledger.read_text())

    def test_budget_blocks_before_paid_request(self):
        calls = []
        runner = self.runner(lambda *a, **k: calls.append(a))
        with self.assertRaisesRegex(RuntimeError, "budget"):
            runner.run_session("x" * 60_000, self.workspace, ["Read"])
        self.assertEqual([], calls)

    def test_unknown_request_is_never_retried(self):
        calls = []
        def opener(*a, **k):
            calls.append(a)
            raise TimeoutError()
        runner = self.runner(opener)
        with self.assertRaisesRegex(RuntimeError, "unknown"):
            runner.run_session("prompt", self.workspace, ["Read"])
        with self.assertRaisesRegex(RuntimeError, "no retry"):
            runner.run_session("prompt", self.workspace, ["Read"])
        self.assertEqual(1, len(calls))

    def test_alternate_grader_keeps_score_separate(self):
        grader = OpenRouterOfflineGrader(docker="docker", env_file=self.root / ".env", allow_network=True)
        with patch.object(DockerOfflineGrader, "__call__", return_value={"status": "graded", "official_score": 1.0}):
            result = grader(None, None, None, None)
        self.assertEqual("evaluated", result["status"])
        self.assertEqual(1.0, result["evaluator_score"])
        self.assertIsNone(result["official_score"])
        command = grader.command({"task_id": "synthetic"}, self.root / "output")
        self.assertIn("original_collect", command[-1])
        self.assertIn("kwargs['judge']=runner", command[-1])
        self.assertNotIn("max_retries", command[-1])
        server_grader = OpenRouterOfflineGrader(docker="docker", env_file=self.root / ".env",
            allow_network=True, key_limit_enforced=True)
        self.assertIn("key_limit_enforced=True", server_grader.command({"task_id": "synthetic"}, self.root / "other")[-1])

    def test_verified_server_limit_uses_native_provider_preflight(self):
        methods = []
        def opener(request, **kwargs):
            methods.append(request.get_method())
            response = Response({"role": "assistant", "content": "done"})
            if request.get_method() == "GET":
                response.body = {"data": {"limit": 0.5, "limit_remaining": 0.4, "limit_reset": None, "usage": 0.1}}
            return response
        runner = OpenRouterJudgeRunner(self.root / "server-limit", opener=opener,
            key_loader=lambda: "test", key_limit_enforced=True)
        self.assertEqual("done", runner.run_session("x" * 60_000, self.workspace, ["Read"]))
        self.assertEqual(["GET", "POST"], methods)
        entry = json.loads(runner.ledger.read_text())["requests"][0]
        self.assertEqual("verified_server_key_limit", entry["budget_enforcement"])

    def test_unbounded_server_key_is_refused_before_post(self):
        methods = []
        def opener(request, **kwargs):
            methods.append(request.get_method())
            response = Response({})
            response.body = {"data": {"limit": 5, "limit_remaining": 4}}
            return response
        runner = OpenRouterJudgeRunner(self.root / "unsafe-key", opener=opener,
            key_loader=lambda: "test", key_limit_enforced=True)
        with self.assertRaisesRegex(RuntimeError, "server-side key limit"):
            runner.run_session("prompt", self.workspace, ["Read"])
        self.assertEqual(["GET"], methods)


    def test_complete_verdict_write_stops_without_paid_acknowledgment(self):
        (self.workspace/'rubrics.json').write_text(json.dumps({'rubrics':[{'rubric_id':'synthetic'}]}))
        verdict={'rubric_verdicts':{'synthetic':{'pass':False,'explanation':'Synthetic failure.', 'evidence_refs':[]}}}
        calls=[]
        def opener(*a,**k):
            calls.append(1)
            if len(calls)>1:raise AssertionError('no trailing request')
            return Response({'role':'assistant','tool_calls':[{'id':'write','function':{'name':'Write',
                'arguments':json.dumps({'file_path':'verdicts.json','content':json.dumps(verdict)})}}]})
        runner=self.runner(opener);runner.run_session('prompt',self.workspace,['Write'])
        self.assertEqual(1,len(calls))
        self.assertFalse(json.loads((runner.root/'completion.json').read_text())['trailing_acknowledgment_request_sent'])
        self.assertFalse(json.loads((self.workspace/'verdicts.json').read_text())['rubric_verdicts']['synthetic']['pass'])
        runner.run_session('prompt',self.workspace,['Write'])
        self.assertEqual(1,len(calls))
        (self.workspace/'verdicts.json').write_text('{"rubric_verdicts":{}}')
        with self.assertRaisesRegex(RuntimeError,'refusing automatic restart'):
            runner.run_session('prompt',self.workspace,['Write'])
        self.assertEqual(1,len(calls))

    def test_partial_verdict_cannot_terminate_judge_early(self):
        (self.workspace/'rubrics.json').write_text(json.dumps({'rubrics':[{'rubric_id':'one'},{'rubric_id':'two'}]}))
        (self.workspace/'verdicts.json').write_text(json.dumps({'rubric_verdicts':{'one':{'pass':True,'explanation':'Only one','evidence_refs':[]}}}))
        self.assertFalse(OpenRouterJudgeRunner._complete_verdict(self.workspace))


if __name__ == "__main__": unittest.main()
