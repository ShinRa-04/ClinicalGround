# Separate execution and grading — October 21, 2026

The user requires all selected actor tasks to finish before paid judge work
starts. They selected **Claude Opus 4.7 through OpenRouter Batch** for the
desired judge transport; the model must not be substituted.

## Implemented and verified

Luna-high `deferred_grading` implemented `batch.py`, `deferred_grading.py` and
tests; Luna-high `openrouter_batch` implemented the experimental Batch transport
and tests. Both are finished. Root reviewed, tested, performed real Docker/API
checks, and owns documentation and commits.

The normal actor batch CLI now defaults to deferred grading, with no inline
grading toggle. Completed attempts preserve the final verifier export and
filesystem artifacts with hashes before stopping their worlds. They remain
`deferred_ready`, with no official score. A separate grading command validates
the exact frozen task/attempt set, all snapshots and stopped worlds before any
judge work. It grades a disposable copy without calling the actor. Failed
export or snapshot validation preserves the original world for reconciliation;
it must not destroy the only final state. Programmatic legacy callers still
have the earlier inline option; the CLI does not expose it.

Root independently passed **278 software tests** (32.039 seconds). Root's native
transport-only check captured the actual verifier export and **219 files**,
stopped the original world, and ran the pinned verifier in a fresh image from
the snapshot. Live/offline checks and binary reward matched, the filesystem
probe survived, and the original snapshot hashes stayed unchanged. Model
sessions were deliberately blocked and network disabled: this is transport
verification, not a clinical actor trial or new benchmark score.

Original snapshots and earlier grading attempts must remain unchanged.
Grade outputs, secrets, patient data, protected policies and verifier material
remain ignored. Only the official verifier process may read scoring fixtures;
the acting model never receives them.

## OpenRouter Batch compatibility findings

**Confirmed:** OpenRouter lists the Opus 4.7 batch variant at $2.50 per million
input tokens and $12.50 per million output tokens. Its asynchronous Batch API
accepts Anthropic Messages, chat completions and Responses requests. Submission
is followed by polling/result retrieval, with a 24-hour completion window.
`stream: true` is rejected. Tool schemas may be supplied, but OpenRouter does
not execute the judge's local filesystem tools for the client.

**Confirmed from the pinned official implementation:** `WorkspaceJudge`
invokes `ClaudeAgentRunner.run_session` with `Read`, `Glob`, `Grep`, `Write`
and `Edit`, a local workspace and a 900-second session timeout. The runner
launches Claude Code and explicitly removes `ANTHROPIC_BASE_URL` so its judge
calls use the direct Anthropic endpoint. A zero-key, network-disabled Docker
check of that exact runner confirmed the URL removal. Its receipt is ignored
under `HealthHarnessCodex/runs/20261021-deferred-grading-qa/`.

**Conclusion:** the unchanged judge cannot be connected to OpenRouter Batch
by changing a key, model name or URL. Using the same Opus 4.7 model does not
provide the missing API/session integration. An alternate adapter could in
principle submit each model turn asynchronously, wait, execute requested tools
in the isolated judge workspace and submit the next turn. This is an
engineering possibility, not a working or authenticated integration here.
Dependent turns cannot all be submitted in advance; the permitted per-request
batch delay can exceed the current judge session timeout.

## Actual OpenRouter test result

The user authorized testing the locally configured OpenRouter key with a
**$0.50 cumulative cap**. Read-only key checks confirmed the cap and final
**usage $0.00 / remaining $0.50**. No key values are recorded here.

The experimental adapter now has durable pre-request cost reservations,
pending-batch polling without automatic resubmission, reported-cost-only
reconciliation, and confined/checkpointed filesystem tools. Its **14 focused
offline tests** pass. This does not establish real API compatibility.

Five small synthetic submissions were attempted with a 32-output-token cap and
a conservative $0.000925 reservation per request. Every POST was rejected with
HTTP 400 before a batch ID or model response. The first lacked saved error-body
metadata; diagnostics on subsequent requests said the requested Opus 4.7 model
"does not have a :batch endpoint."

| Request | Model route | Batch request shape | Result |
|---|---|---|---|
| 1 | Base Opus 4.7 | Anthropic Messages | HTTP 400, no batch ID |
| 2 | Same, with private diagnostic capture | Anthropic Messages | Same rejection |
| 3 | Explicit Opus 4.7 `:batch` variant | Anthropic Messages | Same rejection |
| 4 | Base Opus 4.7 | Chat completions | Same rejection |
| 5 | Base Opus 4.7, Anthropic provider pinned, fallback disabled | Anthropic Messages | Same rejection |

Read-only model endpoint discovery nevertheless lists one Anthropic Opus 4.7
Batch endpoint at the quoted $2.50/$12.50 rates. Both versioned and beta batch
listing endpoints authenticated successfully and showed zero batches. The
catalog/Batch-submit mismatch is confirmed; its underlying cause is **not**
confirmed. Account eligibility, provider routing and service configuration are
possible explanations, not established diagnoses. No standard-priced fallback
or alternate model was used. Further submissions stopped after the targeted
checks. Private request/error/budget receipts are under ignored
`HealthHarnessCodex/runs/20261021-openrouter-batch-test/`.

No actual Opus judge verdict, completed model inference or equivalence
comparison was obtained. Competition acceptance of an alternate runner is
unconfirmed. The experimental tool loop uses our bounded file tools rather
than Claude Code's built-in tools; same-model execution alone cannot prove
protocol equivalence. Keep these boundaries explicit.

### User-supplied reference reproduction

The user supplied screenshots and a Batch API example containing both the
batch-level model and the same model inside each request body. Earlier tests
omitted the nested model, as the official documentation allows inheritance.
Root reproduced the supplied payload structure, including both model fields,
`/v1/chat/completions`, no provider override, and the user's example question,
using an independent standard-library HTTPS client instead of the adapter.
The only added payload field was `max_tokens: 32` to respect the $0.50 cap.

This **sixth** submission also returned HTTP 400, no batch ID, and the identical
model-has-no-Batch-endpoint error. Its pre-request conservative reservation was
$0.001434375; the synchronous rejection released it. A fresh authenticated key
check still reported usage **$0.00**, remaining **$0.50**. The nested-model
difference did not resolve the rejection. This does not establish the precise
underlying cause or prove a global OpenRouter service limitation.

The independent reproduction script, complete request and redacted response
remain ignored under the existing API test directory. Its durable reservation
uses the same shared budget ledger. Unknown outcomes would retain their
reservation and never be automatically resubmitted. No production source was
changed for this diagnostic and no live judge score was generated.

## Commands

### Standard endpoint diagnostic (one explicitly authorized request)

After the reference Batch reproduction, the user requested testing the normal
endpoint once. Root made exactly one standard
`POST https://openrouter.ai/api/v1/chat/completions` using Opus 4.7, Anthropic
provider pinned with fallback disabled, and `max_tokens:32`. It returned HTTP
200 and `NORMAL_OK`, finish reason `stop`. OpenRouter reported 32 prompt tokens,
12 completion tokens, 44 total, and **$0.00046** actual cost. The conservative
pre-request reservation was $0.00263125 and was reconciled to the reported cost
in the same shared ledger. No second standard inference or automatic retry ran.

This verifies the configured key and standard Opus 4.7 connection. It narrows
the remaining issue to the Batch API/request/routing path without establishing
the exact cause. It is not a judge verdict, score or authorization to replace
the user's desired Batch grading route with standard-priced grading. Private
receipts and the guarded one-shot reproduction script are preserved in the
existing API test directory.

From `C:/Projects/BigData/HealthHarnessCodex`, actor execution only (Codex
inference, no inline paid judge):

```powershell
python -X utf8 -m health_harness_codex.batch --dataset-root C:/Projects/BigData/Dataset/chi-bench --run-dir runs/NEW_DEFERRED_BATCH --concurrency 3 --attempts 1
```

Add `--plan-only` to inventory tasks without Docker or model calls. Once every
selected task has a valid snapshot, validate the late-grading plan without
Docker or inference:

```powershell
python -X utf8 -m health_harness_codex.deferred_grading --dataset-root C:/Projects/BigData/Dataset/chi-bench --run-dir runs/NEW_DEFERRED_BATCH
```

The current production `--grade-later` path is direct Anthropic only; the
OpenRouter experimental runner has not passed live inference and is not
connected to an accepted full-batch scoring/export workflow. Its read-only
smoke plan is:

```powershell
python -X utf8 -m health_harness_codex.openrouter_batch --run-dir runs/20261021-openrouter-batch-test --max-budget-usd 0.50
```

`--submit-smoke` sends a request; `--poll BATCH_ID` reads an accepted job.
Do not resubmit a pending/unknown job. No accepted job exists in this test.

## Sources and evidence boundaries

- [OpenRouter Opus 4.7 batch pricing](https://openrouter.ai/anthropic/claude-opus-4.7:batch).
- [OpenRouter Batch API specification](https://github.com/OpenRouterTeam/docs/blob/main/batch-quickstart.mdx).
- [Pinned official judge runner](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/verifier/judge/claude_runner.py),
  especially `_subprocess_env` and `run_session`.
- [Pinned workspace judge](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/verifier/judge/workspace_judge.py).
- [Official rejudge procedure](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/docs/judge.md)
  establishes that judge execution after actor completion is supported in
  principle. The new native-run snapshot transport passed the key-free replay
  check above; earlier stopped worlds lacking that snapshot are not assumed
  recoverable. Full 75-task clinical execution has not been performed.

See [judge commands and cost calculations](../Runner/JUDGE.md). Token-cost
examples are scenarios rather than observed consumption or spending caps.
