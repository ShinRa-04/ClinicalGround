# Completion validation and stopped-batch audit — October 22, 2026

## Final repair and verification

The root cause was an absent task-completion requirement in the acceptance
path: successful citation IDs and closed model-authored obligations were
accepted without proving the assigned workflow endpoint. Post-run readbacks
were recorded but did not prevent that acceptance. Earlier tests exercised
those bookkeeping rules and consequently missed the task-goal gap. Reporting
then gave the local completion flag a stronger meaning than its evidence
supported. Narrative provider prompts also lack a selected terminal endpoint;
neither a draft nor a docs-needed state alone establishes success or failure.

The repaired engine pins a harness-owned public-goal contract and its hash,
checks same-case terminal evidence and freshness before completion, and
rejects missing, changed, malformed or unverified contracts. Mapped goals can
receive at most two corrective turns within the existing model/tool budgets;
no unknown write is automatically repeated. Custom configured CLI flows need
an explicit scope-matched operator contract; demos and smoke tests use
separate synthetic contracts. UM handoff completion remains distinct from
whole-case finalization in both the gate and evaluation.

The public-goal inventory is **50 mapped (25 UM, 25 CM) and 25 provider goals
unverified**. These are mapping-coverage counts, not verified outcomes or
scores. A provider endpoint must be established from an authoritative task
requirement before that case can receive a verified completion label.

Root's final integrated offline suite passed **397 tests in 56.598 seconds**.
It includes builder-to-engine success and rejection, identity/freshness,
contract tampering, bounded correction, continuation, reporting, and actual
localhost HTTP/SSE integration. An intermittent fake-world ID collision in a
concurrent test was separately fixed using locked allocation and a forced
two-thread regression; production world allocation was unchanged. All 33
original `HealthHarness/` file hashes still match the duplication baseline.

Offline replays against preserved actor observations independently confirmed:

- t008 and t011 are rejected with `goal_unverified` instead of accepting their
  recorded completion claims.
- The preserved CM COPD refusal/disenrollment evidence is accepted as
  `cm_documented_refusal_and_disenrollment`, using its successful committed
  terminal-write response.

The replays changed no original result/database/WAL/SHM files. They used no
grader exports, hidden expectations, new model calls, clinical writes or
resumed worlds. The current dataset batch remains stopped, with three worlds
paused. No new end-to-end native benchmark trial or official grading was
performed after this repair. Keep earlier run outputs and failure logs intact;
any future controlled trial needs a fresh run directory and frozen source.

## Purpose and boundaries

This note records the completion-label gap found while the user-directed
`20261022-full-dataset-codex-sim-01` run was stopped. It separates the local
harness claim, same-case citation integrity, public workflow observations,
task-goal verification, and official grading. A successful evidence-ID check
only shows that the cited IDs exist in the local successful-action journal; it
does not show that those observations support the claim or that the assigned
public workflow goal was reached.

No grading, new inference, clinical write, judge call, or world restart was
performed for this audit. The original batch manifest and event journal remain
unchanged. Do not resume this batch automatically. Its three manifest entries
still say `running` as a historical status; the private stop receipt records
that they were paused after the stop request.

## Stop receipt and preservation

The ignored receipt is
`HealthHarnessCodex/runs/20261022-full-dataset-codex-sim-01/stop-receipt.private.json`.
It records the root/child process IDs and their observed absence, the seven
container bindings and immutable runtime image digest, container states and
mounts, source commit/fingerprint, manifest and event hashes, and the 75-task
status inventory. The three interrupted attempt directories were copied to
`stop-recovery/attempts/` under the ignored run directory. The 18 copied files
include mounted logs/spool files and SQLite/WAL sidecars; every copy hash
matched its source. This is byte preservation only, not a claim that a copied
SQLite set is a transactionally consistent snapshot or a public-state readback.

At audit time, 75 tasks were planned: four snapshots were already settled as
`deferred_ready`, three manifest entries remained `running` but their owned
worlds were paused, and 68 tasks were pending. There were no official grades.
The batch process and all listed Windows process IDs were absent. Three owned
containers were paused and retained; four had already exited. All seven
referenced `bigdata-chi-bench:runtime-4444a07` with image digest
`sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66`.

## Settled-case audit

The public task IDs below are the only case identifiers in this summary. Safe
state fields were extracted from the actual local workflow readback; no patient
text, tool arguments, model response, hidden fixture, grader expectation, or
protected handbook content is reproduced here.

| Public task ID | Local harness result | Safe observed workflow fields | Goal / grading interpretation |
| --- | --- | --- | --- |
| `pa_t008_t008_o002_p01_new_referral_provider` | `complete`; local completion claim; citation IDs are recorded; four private obligations closed | `pre_submission`; outcome `none`; form validation `false`; 17 missing-field count | The assigned intake narrative does not state an explicit terminal submission or determination milestone. The readback and citations do not prove the public task goal. Goal mapping is **unverified**; official grade unavailable. |
| `pa_t011_t011_o003_p01_new_referral_provider` | `complete`; local completion claim; citation IDs are recorded; one private obligation closed | `pre_submission`; outcome `none`; form validation `false`; 16 missing-field count | Same limitation: no explicit terminal milestone in the assigned intake narrative. Goal mapping is **unverified**; official grade unavailable. |
| `pa_t012_t012_o001_p01_new_referral_provider` | `unresolved`; two obligations remain open; no local completion claim | `pre_submission`; outcome `none`; form validation `false`; two missing-field count | Local workflow is incomplete. No official grade. Do not use this readback alone to invent additional public requirements. |
| `pa_t014_t014_o001_p01_new_referral_provider` | `unresolved`; one obligation remains open; no local completion claim | No provider form-validation object or explicit public terminal flag was recorded in the safe readback projection | Goal outcome is unverified; no official grade. |

The four statuses describe the local recorder and readback only. In particular,
the two local `complete` labels do not mean a submitted packet, completed
clinical workflow, official success, or verified task-goal completion. The
local evidence-ID integrity field is not a substantive evidence-support test.
The completion-contract review concluded that t008/t011 identify a provider
role-level outcome but do not select a verifiable provider endpoint. The
task-goal mapping is therefore `unverified`, not a confirmed unfinished
workflow. The report must not upgrade the local claim or turn this ambiguity
into an incomplete-task finding.

## Public-role source audit

Read-only review of the local public competition materials and the approved
handbook found a **role-level preparation goal**, but no unambiguous task-level
terminal branch for these clinical-intake tasks. The public track summaries
describe a broad provider workflow that may include submission and subsequent
response work; they do not say that every clinical-intake prompt must submit,
choose a particular disposition, or stop after a provider determination.
The public t008/t011 instructions contain 19 lines each and do not state an
endpoint verb; their clinical narratives are intentionally not reproduced.

The local approved handbook copy is pinned to commit
`f1210b294904792541116852f6074df8b84d89dd` (Dataset/README.md:13). Its provider
role card and workflow SOP scope the role to preparation of a provider-side PA
record. The SOP includes a conditional packet-handoff check and says incomplete
records should remain identified as incomplete; it does not prescribe an
unconditional handoff or choose among terminal provider dispositions. No
protected handbook text is copied here.

Source provenance (line references are section/statement locations; hashes
identify the exact files reviewed):

| Source | Lines / section | SHA-256 |
| --- | --- | --- |
| `Runner/chi-bench/README.md` | 43, provider-track summary | `945589ffb0820100fe59a172ad0c7b6b365b995385fa22e6ddda2c3e1c2726f2` |
| `Runner/chi-bench/docs/competition-rules-draft.md` | 19, challenge scope | `bd05a5bed97939adfda63ee6461b1abbcb83c655b4a2e9c0971dad9fcca3c33b` |
| `Plan/Source/01-competition-description.txt` | 1–8, overview and task count | `bf4ab98d865b787d29fc2127acfc67a1398d809d64fcee61a9f8184d19fd8521` |
| `Dataset/chi-bench/prior_auth_provider/tasks/pa_t008_t008_o002_p01_new_referral_provider/instruction.md` | 19-line public instruction; endpoint absent | `67dc4e1c1ec516fefd18bc1574ba4af236e1b484e1ebc201f6e1cf1258ca32c1` |
| `Dataset/chi-bench/prior_auth_provider/tasks/pa_t011_t011_o003_p01_new_referral_provider/instruction.md` | 19-line public instruction; endpoint absent | `5a93e018d2ebdb489bfe3db8fbe88e50c68a09058650e2eb331aacba36391a07` |
| Approved handbook `references/provider-pa/SKILL.md` | Role section, lines 8–12 | `58a400aee1a71f93e63df9e6d63b190342e8c1ebf385e2e2d83737161f234c1a` |
| Approved handbook `references/provider-pa/01-workflow.md` | Role/scope lines 8–12; handoff lines 93–96 | `f5b6ed290837d04aa53fbeac26d8aa1b88e457d9eac38327d0019da9fbe0a677` |

The contract-review result is therefore `verified_role_outcome=prepare_provider_side_pa_record`, `verified_task_goal=false` for t008/t011. This supports role-level work while leaving the task completion goal unverified. It does not justify forcing these cases into either a completed or incomplete workflow category.

## Completion-gate implementation evidence

The current source gate requires explicit harness-owned goal mapping and
successful same-scope milestone evidence. It does not accept the model's
structured `complete` status or valid citation IDs by themselves. The public
task contract mapping inventory is **25 unverified goals / 50 mapped goals out
of 75**. These are mapping-coverage counts, not completion counts, grades, or
scores.

Focused negative coverage now distinguishes unverified goals from mapped
workflows missing milestones. It verifies that narrative-only provider intake
and quoted phrases do not manufacture a submission endpoint; a mapped submit
goal does not pass on `docs_needed`; wrong-case readback, missing/invalid
contracts, malformed identities, unknown rejected-gate reasons, stale terminal
writes, and mismatched scopes cannot be reported as verified. A mapped contract
with absent required milestones stays incomplete. Unknown-effect, identity,
and model-error classification precedence remains separate.

Positive offline synthetic contract tests cover a final-care-plan write and a
documented-refusal/disenrollment write as distinct Care Management outcomes;
the same-cases and terminal-write ordering checks must pass. This is software
verification with synthetic evidence, not a model-driven or scored benchmark
run. Earlier synthetic HTTP/CLI and legacy tests were updated to provide
operator-owned explicit terminal contracts and typed synthetic proof. This
keeps completion enforcement in place instead of restoring citation-only
acceptance.

## Reporting change in progress

`HealthHarnessCodex/health_harness_codex/debug_report.py` now adds a distinct
completion audit object per case. It keeps the local claim, citation integrity,
completion-gate decision, missing-milestone count, and public-goal status in
separate fields. It also records the model's structured final status separately
from the harness's local completion flag. A local `complete` claim with valid
citations and no contract gate is reported as public-goal `unverified`. The report also retains
historical manifest statuses such as `running` and adds an observed stop-state
field, so the audit can show `running` in the untouched manifest and
`paused_after_stop` from the private receipt without rewriting history. The
report utility was documented around completed batches; accepting pending and
stopped rows is an audit-support extension for this partial run, not a separate
false-completion root cause. Original recorded status, classification, and
claim fields remain visible beside derived audit labels.

Focused offline tests cover citation-only claims, safe completion-gate
summaries, unmapped versus mapped-missing goals, pending attempts without a
directory, and the historical-running versus paused-stop distinction. The
current focused suites pass: 20 tests in `tests/test_evaluation.py`, 13 in
`tests/test_debug_report.py`, 4 in `tests/test_http_integration.py`, and 3 in
`tests/test_cli.py`. The sanitized all-case report was generated under
the ignored run directory at `debug-report/all-cases.json` and
`debug-report/all-cases.csv`: 75 rows, 4 saved/deferred snapshots, 3 paused
after stop, 68 not started, two structured `complete` finals, two structured
`incomplete` finals, two model completion claims, two historical harness
accepted claims, both public goals unverified, and both citation-ID checks
valid. There are 2 locally unresolved workflows, 0 blocked local outcomes, and
0 official grades. Root owns the integrated suite and any fresh controlled
repro. The report still makes no official-grade claim.

## Next steps

1. Integrate the engine completion-gate result and public-workflow contract
   mapping without treating citations as task-goal proof.
2. Root reviews the source changes, runs the full software suite, and performs
   only an explicitly controlled fresh repro after the stopped batch is
   preserved. The current 75-task batch remains stopped.
3. Rebuild the ignored all-case report from the unchanged historical run,
   showing local execution metrics, goal-verification state, incomplete/blocked
   counts, and official grades as separate dimensions.
4. Update the handoff with the final test/repro evidence. Root owns commits.
