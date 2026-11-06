# Official single-task pilots — October 20, 2026

**Current October 20:** frozen actor source `03c845d` scored **3/3 official passes, 21/21 checks in every trial**, on the same public UM development task. Its single-task pass@1/pass@3/pass^3 are all 100%; this is not a full-dataset or held-out result. Root passed **187 software tests** (20.628 seconds) and matched all 33 original harness hashes. Two trials retained local `unresolved` because the model returned prose without the required structured completion record; the official grader independently passed their actual worlds. The third was locally complete. All three worlds are stopped after official receipts and integrity-checked SQLite backups; no inference is active. No PR or submission is authorized. See [measured pilots](HEALTH_HARNESS_PILOT_RESULTS.md) and [official evaluation](HEALTH_HARNESS_OFFICIAL_EVALUATION.md).

## Scope and protocol

Every row below is exactly three fresh worlds for **one public UM task**, `pa_t012_t012_o001_p01_triage_payer`. Actor: GPT-6 Luna high via the existing native Codex sign-in. Per-trial caps: 48 model calls, 240 engine operations, 180,000 context characters. All trials within each batch use a frozen source version and matching task, model, budget, instruction-source and initial-world fingerprints. Different versions are never pooled.

The unchanged pinned official verifier scores the actor's settled world. Strict reward is 1 only when all applicable checks pass. A model's completion claim, terminal approval or fractional diagnostic reward is insufficient. No operator task follow-ups, manually injected case identifiers or hidden expected values are supplied to the actor. The grader alone reads its fixture. Public actor contracts and resulting scorecard feedback are used for development; this is a development task, **not held-out validation or a full 75-task benchmark result**.

Runtime: `bigdata-chi-bench:runtime-4444a07`, image `sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66`. Worlds have network disabled, no ports and no provider keys. This particular fixture has deterministic checks and needs no judge inference. That finding does not cover other tasks or standard submission requirements.

## Measured batches

### Baseline — `d865c53`

| Trial | Official reward | Passed/applicable | N/A | Local result | Model calls | Engine operations | Actor dispatch attempts | Seconds |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| trial-1 | 0 | 18/21 | 0 | complete | 12 | 58 | 14 | 199.032 |
| trial-2 | 1 | 21/21 | 0 | complete | 16 | 79 | 17 | 272.000 |
| trial-3 | 1 | 21/21 | 0 | complete | 13 | 52 | 16 | 203.875 |

Single-task pass@1 **2/3 (66.7%)**, pass@3 **100%**, pass^3 **0%**. Ignored root: `HealthHarnessCodex/runs/20261020-um-frozen-pilot/`.

### Record-before-route guard — `69bc127`

| Trial | Official reward | Passed/applicable | N/A | Local result | Model calls | Engine operations | Actor dispatch attempts | Seconds |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| trial-1 | 0 | 2/15 | 4 | error | 9 | 44 | 6 | 177.844 |
| trial-2 | 1 | 21/21 | 0 | complete | 16 | 56 | 13 | 270.750 |
| trial-3 | 0 | 20/21 | 0 | unresolved | 16 | 80 | 20 | 321.375 |

Single-task pass@1 **1/3 (33.3%)**, pass@3 **100%**, pass^3 **0%**. Ignored root: `HealthHarnessCodex/runs/20261020-um-guarded-pilot/`.

### Format retry and route consistency — `6b702f4`

| Trial | Official reward | Passed/applicable | N/A | Local result | Model calls | Engine operations | Actor dispatch attempts | Seconds |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| trial-1 | 0 | 19/21 | 0 | unresolved | 15 | 70 | 11 | 298.813 |
| trial-2 | 1 | 21/21 | 0 | complete | 12 | 38 | 13 | 174.344 |
| trial-3 | 0 | 19/21 | 0 | unresolved | 13 | 63 | 10 | 232.297 |

Single-task pass@1 **1/3 (33.3%)**, pass@3 **100%**, pass^3 **0%**. Ignored root: `HealthHarnessCodex/runs/20261020-um-contract-pilot/`.

### Route before immutable metadata — `4b5d88d`

| Trial | Official reward | Passed/applicable | N/A | Local result | Model calls | Engine operations | Actor dispatch attempts | Seconds |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| trial-1 | 1 | 21/21 | 0 | complete | 12 | 49 | 17 | 236.625 |
| trial-2 | 1 | 21/21 | 0 | complete | 15 | 76 | 18 | 226.875 |
| trial-3 | 0 | 2/15 | 4 | blocked | 1 | 1 | 1 | 16.750 |

Single-task pass@1 **2/3 (66.7%)**, pass@3 **100%**, pass^3 **0%**. Ignored root: `HealthHarnessCodex/runs/20261020-um-ordered-pilot/`.

### Scoped case-worker catalogue — `03c845d`

| Trial | Official reward | Passed/applicable | N/A | Local result | Model calls | Engine operations | Actor dispatch attempts | Seconds |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| trial-1 | 1 | 21/21 | 0 | unresolved | 14 | 75 | 23 | 232.016 |
| trial-2 | 1 | 21/21 | 0 | unresolved | 9 | 41 | 18 | 176.203 |
| trial-3 | 1 | 21/21 | 0 | complete | 13 | 54 | 16 | 221.828 |

Single-task pass@1 **3/3 (100%)**, pass@3 **1/1 (100%)**, pass^3 **1/1 (100%)**. Ignored root: `HealthHarnessCodex/runs/20261020-um-scoped-pilot/`. All source/configuration/initial-observation fingerprints match within the batch and current package bytes match its frozen source fingerprint. Each official grade is 21/21 with no N/A. This fixture emitted no LLM-judge checks and no judge-unavailability reason; no external semantic assessment was performed. The first grading exports for trials 1/3 timed out; read-only retries completed without rerunning either actor. Receipts hash the exact selected verifier directories (attempt 2 for trials 1/3, attempt 1 for trial 2).

**Local completion limitation:** trials 1/2 returned prose instead of the harness's required structured completion record and kept local status unresolved. Their original exit codes and open local bookkeeping are preserved; neither is relabeled locally complete. The official verifier nevertheless passed their actual final worlds. Trial 3 closed its structured completion normally. No pending/unknown writes remain in any of the three journals. A later improvement may add a bounded format-only request for that final record, with no replay of completed work; it is not implemented or claimed as tested here.

## Diagnosed failures and corrections

- Baseline trial 1 advanced without a triage record: 18/21 checks, failing disposition, urgency and eligibility. The public trace contains no disposition write; independent actor readback confirmed absence. Other baseline trials passed.
- The first guard required a committed record before routing. Its trial 1 stopped on malformed model tool-argument JSON (no proposal from that response executed); its trial 3 saved nurse review before default routing selected a different lane. The guard reduced omissions but introduced an ordering trap.
- The next version added one bounded, format-only retry before execution and blocked dependent letters when the saved record conflicted with the actual route. Its trial 2 exercised the formatting recovery and passed. Trials 1/3 were 19/21, failing letter type and disposition: they could not correct the saved record. The earlier assumption that this API permitted an amendment was wrong.
- Public tool contracts and a separate fresh-world scripted API probe established that `triage.set_disposition` is a one-time record, while the default `triage.route_case` derives its route from case policy. A previously saved disposition does not control it. The supported tested order is: observe SLA/eligibility, route, read explicit `triage=null`, create the first matching metadata record, read back and complete correspondence. The probe is integration QA, not autonomous performance evidence. An initial probe omitted required urgency and failed; it was preserved and the corrected probe used a separate world.
- Version `4b5d88d` mechanically enforces that order without selecting a clinical outcome or inventing values. Both trials that reached it passed 21/21. Trial 3 instead re-requested the all-case queue after setup. The existing isolation guard correctly quarantined that response and stopped the worker. The scoped version hides that discovery capability after scope binding and refuses direct attempts before dispatch; bootstrap discovery remains separate. All three scoped trials passed official grading, and their recorded model tool catalogues contain no queue capability.

These small development batches demonstrate concrete failures and actual passes, but do not establish a causal performance improvement or general reliability. No failed attempt is discarded. No synthetic probe is counted toward official metrics.

## Evidence, accounting and retained artifacts

Each ignored trial contains the original events, full case-local state, final evaluation/result, read-only SQLite snapshot with integrity check, and an `official-evaluation-receipt.json` hashing reward, scorecard, exported state and verifier context. The operator-only aggregator validates exactly three trials, settled results, matching configuration, artifact hashes, native binary/check consistency and judge availability. Native `total_checks` excludes N/A checks. Reports retain N/A separately rather than counting them as successes.

Some initial official export requests hit the upstream five-second timeout. When no scorecard existed, a read-only grading retry used a new output directory. The agent/world was not rerun and no existing scorecard was replaced. All failed grading logs remain. Grading data is outside the actor's readable roots. No fixture, solution or hidden expected result was inspected by the actor or reviewer.

Actor counts are **remote dispatch attempts**, excluding known local refusals; a dispatch alone does not prove a successful effect. Engine counts also include local evidence/obligation operations. Dollar cost is unknown; reported native usage is retained only when supplied. The guarded version lost usage from its malformed response, so that version's billing totals are incomplete. Later retry accounting records available failed-response usage and counts both requests against the model-call cap.

All evaluated pilot worlds above are stopped and retained after grading/backup. Root independently passed 187 software tests and verified all 33 original HealthHarness baseline hashes; no original file changed. Restarting a runtime resets its world: never replay an old journal against a restarted instance. Private payloads, handbook material, receipts and run data stay ignored. Original `HealthHarness/` stays unchanged. No official submission packet or PR has been produced or authorized.

## Reproduce and extend

See [evaluation procedure](../HealthHarnessCodex/EVALUATION.md) and [official verifier invocation](HEALTH_HARNESS_OFFICIAL_EVALUATION.md). Keep configuration frozen during a three-trial batch and grade each final world before stopping it. Run `python -X utf8 evaluations/aggregate_official_pilot.py --pilot-root runs/<batch>` from `HealthHarnessCodex/` after writing and validating receipts. The aggregator refuses incomplete or incomparable input rather than inventing scores.

The next substantial evidence gap is coverage beyond this development UM task: PA and CM live execution, additional routing branches, genuinely held-out tasks and full submission-format integration remain unverified. The original architecture supports more roles than this standalone adapter has actually exercised.
