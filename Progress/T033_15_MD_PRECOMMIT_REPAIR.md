# t033 -15: 17/18 structural checks; immutable unsigned decision

October25,2026. Root implementation/execution. User authorized autonomous
decisions and requests an explanatory final summary. **No judge** remains binding.

## Actual execution and independent scope

Frozen source `4824f94`, single case `20261025-random-um-t033-15`.
The worker saved8 nurse criteria on its first criteria write, submitted the nurse
recommendation, submitted an MD request-info decision, delivered the pend notice
and obtained fresh readbacks. Policy-decision records carried6 verified clinical
attachment receipts. Triage persistence was performed after the worker inspected
its tool/state requirements. There was no response-format retry or streaming
timeout in this attempt.

The local pending-handoff gate rejected `case_decision.signed_off=false`.
The worker repeatedly investigated and attempted the internal handoff, without
changing that immutable MD record. One recovery helper completed3 model calls
and9 tool proposals; it identified the sign-off inconsistency but could not repair
the submitted decision. Root stopped only the owned model child at call63 after
verifying the runtime behavior and repeated blockage. Batch cleanup saved218
files, verified its snapshot and stopped the world. This was an operator-stopped
development attempt, not a naturally completed testcase.

Recorded63 model calls/142 tool proposals;4,253,770 known reported tokens
(4,196,161 input/57,609 output;1,249,152 cached input included). The interrupted
final call did not report complete usage. Do not pool this or earlier assisted
iterations into a reliability percentage.

Native key-free structural checker on a copy: **17/18 applicable pass,1 fail,
10 N/A**. Failed check: `md.signed_off`. Structural binary0; fractional17/18.
Semantic grading was disabled; no judge, network or credentials were used.
Original snapshot integrity was checked again. These are not full official
benchmark metrics or a clinical-policy verdict.

## Confirmed cause and corrected interpretation

The public MD tool description permits false sign-off only for reserved P2P
review, but its schema defaults tofalse. The pinned runtime accepts an unsigned
request-info decision and makes it immutable. An actual synthetic service check
confirmed the accepted unsigned pending state and rejection of a second decision.
The initial diagnostic caught the wrong exception type; its failed receipt/log is
preserved. Corrected probe `20261025-unsigned-md-contract-02` verified both facts
with no fixtures, inference or benchmark actor.

Root initially suspected the completion checker was too strict. **The native
structural check disproved that conclusion for this benchmark: sign-off itself
is evaluated and failed. The completion requirement is retained.** Runtime
acceptance, documented contract and benchmark correctness are separate facts.

The general harness fault was validating this condition only at completion,
after an irreversible write. The model chose the unsigned flag, and the runtime
accepted it; the controller should have enforced the public conditional contract
before dispatch. No clinical answer or task-specific expected value is needed
to detect that invalid combination.

## Repair

`PayerRoutingGuard` now rejects an unsigned or omitted sign-off for a non-P2P MD
case decision, before the underlying actor is called. It returns an explicit
known-not-dispatched explanation and the public contract source. It never sets
the flag, creates a reviewer identity, chooses a medical outcome, or silently
changes a proposal. The owner must review/correct its own proposed sign-off.
Unsigned P2P reservation remains available. Scope checking applies even where
the separate triage guard is disabled. Final completion checks remain intact.

The feedback distinguishes signing the current review decision from inventing a
treating physician's historical order or asserting that missing facts are known.
This matters because an information request can be signed without becoming an
approval. The tool's actual authority remains the limit.

Triage guidance also now explicitly follows API-supported ordering, removing
the misleading phrase suggesting metadata always precedes routing; the actual
audited routing guard requires route observation before its one-time metadata
commit. No routing preconditions or clinical values were changed.

## Verification

New tests cover non-P2P unsigned/missing flags rejected without actor calls,
explicit signed proposals preserved, unsigned P2P permitted, foreign scope
rejected, and engine-driven correction with exactly one actual MD submission.
Pinned real-service synthetic probe `20261025-md-precommit` verified that the bad
proposal was not persisted, a corrected signed request-info was saved exactly
once, and the case remained pending. No clinical outcome or dataset fixture was
provided. Full regression654 tests pass/92.859s.

## Explicit fresh single-case command

Root executes this after committing source. Do not duplicate while active.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-um-t033-16 `
  --domains pa_um `
  --task-id pa_t033_t033_o001_p01_triage_payer `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```
