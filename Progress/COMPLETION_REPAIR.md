# Consistent completion and evidence-backed stopping

October 24, 2026. Root implementation; original HealthHarness unchanged.

## User definition and repaired cause

The testcase can finish when no further useful permitted action remains in its
assignment. Ambiguity is a reason to investigate, not a sufficient reason to
stop. A request for information and a pending case state alone do not prove
that no other work is possible. Judge scoring remains separate from execution.

The previous failure was deterministic integration code, not changing checker
requirements: an assignment audit accepted UM external waiting, while a separate
provider-only finalization rule rejected deferred work. Incomplete model replies
also bypassed final state assessment and triggered generic early-stop recovery.
See [the causal trace](COMPLETION_CONSISTENCY_ANALYSIS.md).

## Implemented processing

1. `closure.assess_closure` checks the pinned contract, trusted scoped effects,
   outstanding obligations and evidenced deferrals. The assignment audit and
   finalization use this same function. Permission to await external information
   is branch metadata (`allows_external_wait`), not a provider branch-name
   exception. If multiple structural branches match, matching obligations must
   also be considered before choosing an acceptable branch.
2. The finalizer runs that assessment even if the model says incomplete. It
   retains the model's original response rather than editing it retroactively.
3. For a pending-information endpoint the worker must provide a stop_assessment:
   no_further_permitted_action, reason, original evidence_ids,
   investigations_performed, other_work_considered and
   waiting_on_obligation_ids. Investigation entries must be actual successful
   same-case read source IDs. Waiting IDs must account for every deferred
   obligation. References and effects must be valid; a boolean claim is not enough.
4. An explicit source-backed no-further-action report can finish execution even
   when the original status word says incomplete about future clinical work.
   The original word is retained in model_reported_status. A missing report or
   reported remaining action instead prompts targeted reconciliation; the code
   does not turn structural acceptance alone into completion.
5. Missing required effects, open internal obligations, unmatched deferrals,
   unsupported sources, stale/wrong-case observations and altered contracts still
   prevent completion. Original deferrals stay deferred; they are not erased or
   falsely marked completed. No clinical outcome is selected by this code.
6. Recovery asks which useful action remains or why the remaining work cannot
   currently proceed. It no longer asserts that a recorded acceptable endpoint
   must be unfinished. This scope assessment stays with the owner rather than
   automatically spending a helper review merely to restate closure semantics.
7. Reporting uses the accepted contract's case_can_remain_pending metadata
   instead of its own list of UM branch names. It retains no-further-action
   validation separately from official grading and observed patient-case state.

Code verifies reference integrity and recorded effects; it cannot prove that
the model has exhaustively considered every useful clinical investigation.
Actionability remains the model's source-backed judgment, explicitly labeled
semantic_actionability_verified=false. Official semantic grading is still
needed to measure whether the decisions were appropriate. Budget exhaustion,
tool failure or an ambiguous record must not masquerade as legitimate waiting.

## Additional live finding and correction

The second synthetic model probe cited a successful local assignment audit as
an invented ev: source. That audit is derived code output, not an original
clinical observation. The guard correctly rejected it, but originally aborted
without a reference correction. Audits now explicitly state creates_evidence=false
and explain which original observations to cite.

There is also one bounded tool-free final-reference correction. It supplies
valid same-case source IDs, tool names and read markers without medical text.
It shares the existing format/schema correction allowance, preserves clinical
claims, never dispatches tools and never accepts the invented source. A repeated
bad reference remains rejected. The earlier rehydration-source regression was
updated to exercise this one correction instead of exhausting its old fake reply
sequence; its original-source-only requirement remains enforced.

## Verification

Fourteen new closure regressions cover the full UM chain from actual local
deferral through finalization/reporting, both complete and incomplete words,
generic operator branch names, branch-order independence, open internal work,
missing notice, identity/source integrity, remaining investigations, malformed
status, bounded citation correction and preserved deferrals. Existing provider
end-to-end fixtures now include the explicit stopping assessment. No task ID,
patient answer or hidden expected disposition is used by the new module.

**614 tests pass in 79.102 seconds**, source frozen for final acceptance.
Receipt: `HealthHarnessCodex/runs/20261024-closure-final-acceptance.log`.
Earlier intermediate suites: 609 tests passed, then 611 passed. The 614-test first acceptance attempt
had one old rehydration test stub run out of replies after the new correction;
the stub was corrected, and its full 45-test engine suite passed afterward.

Real GPT-6 Luna high through existing Codex sign-in, synthetic in-memory tools
only (no dataset actor and no paid judge):

| Ignored run | Actual result | Reported usage |
| --- | --- | --- |
| `runs/20261024-closure-native-01` | Eight-call probe exhausted before final response; MD request, notice and ledger work performed. Preserved as a failed development probe | 8 model calls, 166,492 tokens |
| `runs/20261024-closure-native-02` | Nine calls; final report contained invented local-audit references and was rejected. Exposed the provenance-feedback gap above | 9 model calls, 212,375 tokens |
| `runs/20261024-closure-native-03` | Complete with valid source-backed no-further-action report; MD request_info, delivered notice and fresh readback. No final-reference retry needed | 5 model calls, 5 proposals, 87,442 tokens |

These are separate development attempts, not a reliability estimate. The final
probe used four actual synthetic actor operations and one local audit. It did
not create a deferred obligation; the separate full-chain regression covers
deferral/finalization/reporting together. Do not claim a real dataset score or
that native execution proved every clinical or deferred-work path.

## Next real execution

Preserve previous t033 runs and frozen contracts. The next command should use
fresh `runs/20261024-random-um-t033-11`, exactly one task, helpers/auto,
100 model calls/500 proposals and deferred grading. No new dataset actor,
official submission or paid judge was launched as part of this repair.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex

& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261024-random-um-t033-11 `
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
