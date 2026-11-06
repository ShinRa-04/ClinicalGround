# UM assignment, stage guidance and MD information handoff

User approved October 24 after the t033 -07 result and public nurse-to-MD
sequence check. Root owns coding; no delegated coding agents or dataset reruns.

## Implemented

- `assignment.py`: readonly structural assignment audit and per-call stage
  guidance. Public assignment stays fixed; model plan/clinical choice remains
  editable; actual scoped operation records establish effects. The audit is
  explicitly a structural interpretation, not official or clinical ground truth.
- UM owner focus changes across intake/triage, nurse review, physician review,
  peer-to-peer, determination/notice and information handoff as the actual
  assigned obligations and observed records change. Nurse request_info does not
  waive an assigned MD decision. Treating-provider authorization is distinct
  from an authored reviewer decision/sign-off under the actual task authority.
- Completion now has a generic MD information-request branch: preserve assigned
  upstream stages; require MD request_info/rationale/deadline/sign-off/case ID,
  a pend notice delivered AFTER that decision, and fresh matching MD/pending
  readback. No forced approval/denial or case-specific expected answer. Explicit
  task restrictions and required P2P are retained.
- Provider-only local deferral is hidden/refused in UM. A distinct UM external
  handoff record can defer an outstanding dependency only after the MD handoff
  is structurally proved; it does not obtain records or send notices.
- Canonical operation names resolve uniquely within the existing permitted
  registry for contract inspection, prerequisite records and delegated tool
  selection. No new permissions are created by name resolution.
- `recovery_audit.py`: one bounded read-only SH-10 critique after a recurring
  unresolved final or persisted stagnant blocker. Uses permitted read tools,
  shared case budgets and original sources. Owner integrates advice and retains
  all clinical-write responsibility. New policy auto/off is frozen in batch
  config; combined mode still disables helpers. Core callers default off; batch
  explicitly defaults auto. At most one automatic critique per case, with up to
  three helper model calls and ten read proposals, reserving two owner calls.
  Owner-invoked helper jobs remain separate. Helpers do not spawn more helpers.
  The automatic review can advise a new investigation, not authorize a write
  or impose a clinical disposition. BLOCKER_AUDIT/END identify this in logs.

The domain mission already differed across PA, UM and CM. The missing part was
specific stage responsibility inside that mission. The same case owner now
receives refreshed stage guidance and a compact assignment audit on each call.
The cycle is assignment -> editable plan -> observed evidence -> revised plan
and current stage. A stage transition does not automatically launch another
worker. Safety/isolation rules remain shared; the model keeps investigation
and clinical interpretation choices.

## Current verification

- **596 tests pass in 68.355s**, source frozen for the final guarded full suite.
  Receipt: `HealthHarnessCodex/runs/20261024-md-stage-guarded-tests.log`.
  Ten new assignment/stage tests cover MD evidence, case identity, fresh readback,
  notification order, explicit P2P/no-pend restrictions, actual per-call stage
  changes, domain filtering and canonical aliases. Five recovery-audit tests
  cover bounded review, readonly tools, shared budgets and disabled modes.
  Batch tests check configuration forwarding and reproducibility.
- Older standalone/continuation test doubles needed the new optional constructor
  argument. These adapters were repaired; this was not a production failure.
- Earlier full-suite attempts intermittently failed synthetic deferred-snapshot
  setup. The exact failures passed in isolation, thirty repeated setup checks
  passed, and the final full suite passed. The original cause is **unconfirmed**.
  The guarded diagnostic run captured no stage exceptions or failed tests.
  Do not claim that the unrelated simulator marker repair explains those errors.
- Pinned service synthetic nurse-pend -> MD information-request test was already
  executed with actual ReviewService and enabled routing guard; original case,
  hidden fixtures and provider credentials were not used. See T033_07_RESULT.md.

## Actual Codex/Luna synthetic checks

All used GPT-6 Luna high through existing Codex sign-in, synthetic records and
an in-memory tool environment. No benchmark actor or paid semantic judge ran.
These development variants must not be pooled into reliability measurements.

| Local run under HealthHarnessCodex/runs/ | Observed result | Calls and reported usage |
| --- | --- | --- |
| `20261024-md-information-native-01` | MD request_info, delivered pend notice and fresh summary satisfy the structural branch | 5 calls, 5 proposals, 84,728 tokens |
| `20261024-md-recovery-native-01` | Early audit exceeded its six-read allowance; owner later completed. Preserved as development failure, not final acceptance | 9 counted calls, 7 native calls, 118,514 tokens |
| `20261024-md-recovery-native-02` | With ten reads and budget reminders, audit refuted a mandatory-catalog assumption; owner remained unresolved over an absent deadline | 10 counted calls, 8 native calls, 150,992 tokens |
| `20261024-md-recovery-native-03` | Explicit synthetic policy supplied seven calendar days. One readonly audit completed, then owner authored request_info, delivered notice and obtained matching readback | 10 counted calls, 8 native calls, 17 proposals, 156,605 tokens |

Recovery probes injected two initial owner blocker replies to exercise the
fallback deterministically; those are counted in engine calls but are not
native inference. Source-linked conclusions are advice. The missing-deadline
probe does not prove that authoring a deadline was impossible under every real
policy; its authority had not been supplied. No efficiency claim follows from
these token counts. Context management still needs measurement on actual runs.

## Additional protocol verification

A simulator claim uses exclusive creation, so the reader can briefly observe
its file before JSON publication finishes. Previously this could produce
invalid_request. The reader now waits within the original deadline for partial
claim/receipt/output markers, never cancelling or resubmitting that uncertain
operation; deadline expiry reports submitted_outcome_unknown. Complete invalid
identities, hashes and forbidden links remain rejected. A deterministic partial
publication regression and the targeted eight-test simulator suite pass.

A local diagnostic wrapper initially lacked the Windows multiprocessing main
guard and recursively ran tests in child processes. Its retrieval timeout is
not evidence of a production retrieval regression. The corrected guarded full
suite is the 596-test acceptance receipt above.

## Next execution and limits

Plan-only verification selected **exactly one** task with helpers/auto, Luna high,
GPU retrieval configuration and deferred grading, with no inference or Docker
launch. Original t033 -07 and stopped -03/-04 artifacts remain unchanged. The
new branch is our structural interpretation of public assignment/API effects,
not clinical ground truth or an official judge verdict. In particular, the next
real actor must demonstrate that it actually performs the missing MD work.

Fresh single-case command (grading remains deferred):

```powershell
cd C:\Projects\BigData\HealthHarnessCodex

& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261024-random-um-t033-08 `
  --domains pa_um `
  --task-id pa_t033_t033_o001_p01_triage_payer `
  --composition helpers `
  --recovery-helper-policy auto `
  --concurrency 1 `
  --attempts 1 `
  --timeout 180 `
  --max-model-calls 100 `
  --max-tool-calls 500 `
  --max-context-chars 0 `
  --simulator-backend codex `
  --simulator-max-model-calls 8
```

Docker must be available; no pre-existing task container is needed. Do not
reuse -08 after a failed launch with changed source/configuration; preserve it
and choose a new run directory. The Codex simulator is experimental and remains
marked ineligible for an official-grade claim. No paid judging is authorized
by this repair. Inspect the saved execution/MD records before declaring success.
