"""Opus 4.7 runner for the benchmark's WorkspaceJudge injection seam.

Only the model transport/tool executor changes. Prompts, rubric creation and
verdict parsing stay with the benchmark. Files and requests are private.
"""
from __future__ import annotations

import json
import hashlib
import math
import os
from pathlib import Path
import shutil
import time
import urllib.request

from . import openrouter_batch as shared


class OpenRouterJudgeRunner:
    def __init__(self, run_dir: Path, *, max_budget_usd: float = 0.50,
                 opener=None, key_loader=None, max_turns: int = 16,
                 key_limit_enforced: bool = False):
        if not math.isfinite(max_budget_usd) or not 0 < max_budget_usd <= 0.50:
            raise ValueError("judge budget must be positive and at most $0.50")
        self.root = Path(run_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.ledger = self.root / "requests.json"
        self.cap = max_budget_usd
        self.opener = opener or urllib.request.urlopen
        self.key_loader = key_loader or (lambda: os.environ.get("OPENROUTER_API_KEY", ""))
        self.max_turns = max_turns
        self.key_limit_enforced = key_limit_enforced

    def _key_budget(self, key):
        request = urllib.request.Request(shared.API_ROOT + "/key", headers={"Authorization": "Bearer " + key})
        with self.opener(request, timeout=20) as response:
            data = json.loads(response.read(65536))["data"]
        limit, remaining = data.get("limit"), data.get("limit_remaining")
        if (isinstance(limit, bool) or not isinstance(limit, (int, float)) or
                not 0 < limit <= self.cap or data.get("limit_reset") or
                isinstance(remaining, bool) or not isinstance(remaining, (int, float)) or
                not math.isfinite(remaining) or remaining <= 0):
            raise RuntimeError("a non-resetting server-side key limit within the authorized budget is required")
        return {"limit": limit, "remaining": remaining, "usage": data.get("usage")}

    def _save(self, state):
        temporary = self.ledger.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(state, stream, allow_nan=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.ledger)

    def _complete(self, messages, tools, timeout):
        # Lock across reservation, request, and reconciliation. A crash leaves
        # an unknown reservation; neither restart nor timeout retries a POST.
        with shared._LedgerLock(self.root / "requests.lock"):
            state = json.loads(self.ledger.read_text()) if self.ledger.exists() else {
                "model": shared.MODEL, "cap_usd": self.cap, "requests": []}
            if state.get("model") != shared.MODEL or state.get("cap_usd") != self.cap:
                raise RuntimeError("judge ledger configuration changed")
            if any(x["status"] == "unknown" for x in state["requests"]):
                raise RuntimeError("previous judge request has unknown outcome; no retry sent")
            used = sum(x.get("cost_usd", x["reservation_usd"]) for x in state["requests"])
            body = {"model": shared.MODEL, "messages": messages, "tools": tools,
                    "max_tokens": 2048, "stream": False,
                    "provider": {"order": ["Anthropic"], "allow_fallbacks": False}}
            # UTF-8 bytes bound text tokens. Reserve all input at the published
            # 1-hour cache-write maximum, output at standard completion pricing.
            raw = shared._canonical_json(body)
            reservation = (len(raw) + 512) * 0.000010 + 2048 * 0.000025
            if not self.key_limit_enforced and used + reservation > self.cap:
                raise RuntimeError("next judge request exceeds remaining $0.50 budget; no request sent")
            key = self.key_loader()
            if not key:
                raise RuntimeError("OPENROUTER_API_KEY is missing")
            key_budget = self._key_budget(key) if self.key_limit_enforced else None
            if self.key_limit_enforced and used >= self.cap:
                raise RuntimeError("reported judge spend reached authorized budget")
            item = {"number": len(state["requests"]) + 1, "status": "unknown",
                    "reservation_usd": reservation, "request_bytes": len(raw)}
            if key_budget is not None:
                item.update(server_key_budget=key_budget, budget_enforcement="verified_server_key_limit")
            state["requests"].append(item)
            self._save(state)
            stem = self.root / f"request-{item['number']:03d}"
            stem.with_suffix(".input.json").write_bytes(raw)
            request = urllib.request.Request(shared.API_ROOT + "/chat/completions", data=raw,
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
            try:
                with self.opener(request, timeout=min(timeout, 60)) as response:
                    answer = json.loads(response.read(8_000_000))
            except Exception as exc:
                item["error_type"] = type(exc).__name__
                self._save(state)
                raise RuntimeError("judge request failed or outcome unknown; reservation retained") from None
            stem.with_suffix(".output.json").write_text(json.dumps(answer), encoding="utf-8")
            cost, usage = shared.OpenRouterBatchTransport._cost_from_usage(answer)
            if cost is not None:
                item.update(status="completed", cost_usd=cost, usage=usage)
            else:
                item.update(status="completed_cost_unreported", usage=usage)
            self._save(state)
            if not self.key_limit_enforced and cost is not None and cost > reservation:
                raise RuntimeError("reported judge cost exceeded conservative reservation; stopped")
            try:
                message = answer["choices"][0]["message"]
                if not isinstance(message, dict):
                    raise ValueError()
                return message
            except (KeyError, IndexError, TypeError, ValueError):
                raise RuntimeError("judge response has no valid message") from None

    def run_session(self, prompt: str, cwd: Path, allowed_tools, add_dirs=(), timeout_seconds=900):
        try:
            return self._run_session(prompt, cwd, allowed_tools, add_dirs, timeout_seconds)
        finally:
            # Preserve verdicts even after partial/budget-limited sessions.
            shutil.copytree(cwd, self.root / "workspace", dirs_exist_ok=True)

    def _run_session(self, prompt: str, cwd: Path, allowed_tools, add_dirs, timeout_seconds):
        root = shared._resolve_workspace(cwd)
        if add_dirs:
            raise RuntimeError("additional judge directories are unsupported")
        definitions = shared._tool_schemas(set(allowed_tools))
        tools = [{"type": "function", "function": {
            "name": d["name"], "description": d["description"],
            "parameters": d["input_schema"]}} for d in definitions]
        checkpoint = self.root / "session.json"
        if checkpoint.exists():
            session = json.loads(checkpoint.read_text())
            if session.get("prompt") != prompt or session.get("tools") != tools:
                raise RuntimeError("judge continuation prompt/tools differ")
            if session.get('completion') == 'complete_verdict_file':
                verdict = root/'verdicts.json'
                if (not self._complete_verdict(root) or
                        hashlib.sha256(verdict.read_bytes()).hexdigest() != session.get('verdict_sha256')):
                    raise RuntimeError('completed judge verdict changed; refusing automatic restart')
                return 'The unchanged complete verdict is already saved; no request sent.'
            messages = session["messages"]
            recorded = json.loads(self.ledger.read_text())["requests"] if self.ledger.exists() else []
            if session.get("completed_requests") != len(recorded):
                raise RuntimeError("judge checkpoint/request mismatch; no retry sent; reconcile response before continuing")
        else:
            messages = [{"role": "user", "content": prompt}]
        deadline = time.monotonic() + timeout_seconds
        for _ in range(self.max_turns):
            recorded = json.loads(self.ledger.read_text())["requests"] if self.ledger.exists() else []
            checkpoint.write_text(json.dumps({"prompt": prompt, "tools": tools, "messages": messages,
                "completed_requests": len(recorded)}), encoding="utf-8")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("judge session deadline reached")
            message = self._complete(messages, tools, remaining)
            calls = message.get("tool_calls") or []
            messages.append({k: message[k] for k in ("role", "content", "tool_calls") if k in message})
            if not calls:
                return message.get("content") or ""
            wrote_verdict = False
            for call in calls:
                function = call.get("function", {})
                name = function.get("name")
                try:
                    args = json.loads(function.get("arguments", "{}"))
                    result = shared._execute_workspace_tool(root, name, args) if name in allowed_tools else "Tool error: forbidden tool"
                except (ValueError, TypeError):
                    result = "Tool error: malformed arguments"
                if (name in {'Write','Edit'} and not result.startswith('Tool error:') and isinstance(args,dict)
                        and isinstance(args.get('file_path'),str)
                        and (root/args['file_path']).resolve() == root/'verdicts.json'):
                    wrote_verdict = True
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
            if wrote_verdict and self._complete_verdict(root):
                checkpoint.write_text(json.dumps({'prompt':prompt,'tools':tools,'messages':messages,
                    'completed_requests':len(json.loads(self.ledger.read_text())['requests']),
                    'completion':'complete_verdict_file',
                    'verdict_sha256':hashlib.sha256((root/'verdicts.json').read_bytes()).hexdigest()}),encoding='utf-8')
                (self.root/'completion.json').write_text(json.dumps({'reason':'complete_verdict_file',
                    'trailing_acknowledgment_request_sent':False}),encoding='utf-8')
                return 'Complete verdict file written; benchmark parser retains final authority.'
        raise RuntimeError("judge tool-turn limit reached")

    @staticmethod
    def _complete_verdict(root):
        """Stop only on complete typed verdicts; leave semantic parsing upstream."""
        try:
            rubrics=json.loads((root/'rubrics.json').read_text())['rubrics']
            ids=[r['rubric_id'] for r in rubrics]
            verdicts=json.loads((root/'verdicts.json').read_text())['rubric_verdicts']
            return bool(ids) and len(set(ids))==len(ids) and all(
                isinstance(verdicts.get(r),dict) and isinstance(verdicts[r].get('pass'),bool)
                and isinstance(verdicts[r].get('explanation'),str) and bool(verdicts[r]['explanation'].strip())
                and isinstance(verdicts[r].get('evidence_refs'),list)
                and all(isinstance(x,str) for x in verdicts[r]['evidence_refs']) for r in ids)
        except (OSError,ValueError,KeyError,TypeError):
            return False
