# One fresh case with an actual evaluator — October 22

User decision: run a fresh case, then judge it using OpenRouter Claude Opus 4.7,
with a $0.50 total cap. Root owns implementation; no delegated solving. Do not
start a 75-case batch. Keep original paused worlds and saved trials unchanged.

Selected case: `pa_t012_t012_o001_p01_new_referral_provider`. Actor GPT-6 Luna
high with existing Codex sign-in, one fresh isolated attempt. Clinical success
will be assessed by the benchmark's verifier and WorkspaceJudge; local
completion labels are not the final verdict.

## Evaluation connection

The unchanged benchmark exposes a `judge` runner injection argument in
`collect_all_verifier_checks`. `openrouter_judge.py` implements that interface
using the synchronous chat endpoint, Opus 4.7 only, and confined file tools.
The official workspace construction, prompts, verdict parser and deterministic
checks remain unchanged. `OpenRouterOfflineGrader` evaluates an immutable
snapshot through that injection seam in a disposable Docker container.
It preserves `evaluator_score` separately from `official_score`: competition
acceptance of this alternate transport is not established. Experimental actor
snapshots can now be validated/evaluated explicitly through this route; direct
official grading retains its existing guard.

The key has $0.49954 remaining from its original $0.50 limit (read-only API
check); this invocation uses a $0.499 adapter cap. Normal model pricing verified
through OpenRouter's model API: $5/M input, $25/M output. Each request reserves
UTF-8 bytes plus protocol margin at the maximum published cache-write input
rate and maximum output tokens before POST. Unknown outcomes retain reservations
and block automatic retries. Reported cost reconciles completed requests;
unreported cost retains the full reservation. No fallback provider/model.
Budget-limited/missing verdicts must be reported as ungraded, never passes.

## Commands

From `C:/Projects/BigData/HealthHarnessCodex`, the judge command (after the
fresh actor has finished and saved its snapshot) is:

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.deferred_grading `
  --run-dir runs/20261022-single-case-judged-01 `
  --dataset-root C:/Projects/BigData/Dataset/chi-bench `
  --judge-transport openrouter --max-budget-usd 0.499 `
  --grade-later --allow-benchmark-network `
  --benchmark-env-file C:/Projects/BigData/Runner/.env
```

For estimate/planning only, omit `--grade-later`, `--allow-benchmark-network`,
and `--benchmark-env-file`. Typical token-cost examples are $0.15 for 20k
input/2k output or $0.375 for 50k input/5k output; these are estimates, not
measured judge workloads. The ledger prevents a next request whose conservative
reservation exceeds the selected cap, which can also stop a session early.

## Evidence

Focused adapter/deferred-grader tests: 12 passed. Network-disabled pinned-image
adapter import passed. Saved previous t012 packet passes alternate evaluation
planning without changing any actor artifact; that plan made no model calls.
Full suite: 414 tests passed in 43.132s. Source frozen at `4240418`.
Fresh actor launched as PID 22844, private run directory
`HealthHarnessCodex/runs/20261022-single-case-judged-01/`. Actor and judge
execution evidence will be appended after execution.

## Executed outcome

Fresh t012 finished at 11:58:31 IST, source `4240418`, with 20 model calls and
55 engine operations, no failed tool evidence, no unknown actions, and no
counterparty simulator calls. Its final case status was `ready_to_submit`,
forms complete, and zero submitted authorization packets. Snapshot validation
passed and the original world was stopped.

The first judge invocation completed two requests costing $0.065315, then our
byte-based input reservation blocked the next request. This was an adapter
budgeting defect, not an exhausted API key. Its original ungraded artifacts
remain intact. Source `db6806a` adds a mode that verifies a non-resetting
server-side key limit at or below the authorized $0.50 before every request,
and uses OpenRouter's token-aware affordability check. No key limit was raised.
Checkpoint mismatches and unknown request outcomes prevent automatic retries.

Root explicitly reconstructed the completed read-only judge turn from its
saved input, response and immutable workspace, carried the original cost ledger
forward, and continued in a separate disposable grader. No actor action was
replayed and no actor snapshot/manifest was changed. The private recovery
command is `runs/20261022-single-case-judged-01/resume_judge.py`; its invocation
and remaining budget were shown to the user before execution.

Final benchmark-verifier result using OpenRouter Opus 4.7: **strict reward 0**.
All 11 checks were resolved: 9 passed, 1 failed, 1 not applicable. Sole failure:
`new_referral.case_status`. Both semantic WorkspaceJudge checks passed, with no
judge-unavailable reason. Not-applicable is a verifier classification, not an
API-budget omission. No clinical success is claimed, and this alternate
transport's competition acceptance is not established.

Completed request costs: $0.024745, $0.040570, $0.203165, $0.173670; total
**$0.442150**, including the first interrupted invocation's requests. The fourth
response ended the model session normally. Original snapshot hash revalidation
passed after evaluation. The final scorecard, raw judge replies, verdict file,
ledger and continuation receipt remain ignored under
`runs/20261022-single-case-judged-01/late_grades/judge-continuation-c2c5bb39/`.

The exact final scorecard checks are:

| Check | Result |
| --- | --- |
| `new_referral.service_request_created` | Pass |
| `new_referral.procedure_code` | Pass |
| `new_referral.required_diagnosis_codes` | Pass |
| `new_referral.service_type` | Pass |
| `new_referral.site_of_service` | Pass |
| `new_referral.case_created` | Pass |
| `new_referral.case_status` | Fail |
| `provider_pre_submission.required_documents_present` | Not applicable |
| `cross.forward_transitions` | Pass |
| `judge.provider_pre_submission.submission.service_request` | Pass |
| `judge.provider_pre_submission.submission.rationale_scope` | Pass |

Remaining work: diagnose why the actor stopped at an unacceptable case status
using public workflow guidance and evaluator diagnostics, without inserting
hidden case answers into the harness. Any later paid judge must remain within
the current cumulative authorization or receive a new explicit budget.
