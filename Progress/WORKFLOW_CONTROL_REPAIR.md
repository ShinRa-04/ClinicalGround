# Workflow-control repair — October 22, 2026

## Confirmed cause and evidence

The stopped t011 attempt treated an empty existing-order list as a prerequisite
failure. I investigated and implemented this repair directly, without delegating
coding. A fresh, isolated public-actor diagnostic read all 65 visible patient
charts and candidate-order lists. Every patient had zero existing orders; both
chart and order endpoints agreed. No fixture expectations, solution files,
judge state, or hidden target metadata were inspected.

The public `cases.create_from_order` contract explicitly makes `source_order_id`
optional. It either adopts an existing order or creates a NEW ServiceRequest
and draft case using supported intake fields. Thus the absence of existing
orders does not itself prevent provider workflow execution. The model's earlier
stopping rationale was not justified by that absence alone, and our execution
loop did not diagnose this before ending the attempt. The diagnostic did not
prove every case's clinical interpretation or patient selection correct.

Source: `Runner/chi-bench/src/chi_bench/services/cases.py` `create_from_order`
signature/docstring; `services/chart.py` public chart and order queries.
The fresh read-only world was stopped after the probe. Its body-free candidate
scores/counts and script are local-only under
`HealthHarnessCodex/runs/20261022-workflow-repair-readonly-01/`.

## Implemented changes

- `workflow.py` derives the new-request capability from the actual tool schema.
  Structured incomplete finals can trigger at most two diagnostic/replanning
  turns within the original model/tool limits. Repeating a stop without new
  source evidence ends recovery. This does not resubmit a failed action, change
  case identity, or override unknown-write protections.
- Tool and task guidance explains the difference between recording an
  authorized NEW request and inventing a historical order. It directs the actor
  to resolve actual providers and ground clinical/coding fields in the task,
  chart, and approved references. Optional fields are not mandatory blockers.
- Case obligations can declare prerequisites. Unknown/cyclic dependencies and
  closing a dependent obligation before its prerequisite are rejected. The
  model sees ready obligations and execution capabilities in its case ledger.
  Planning obligations do not replace the independent completion contract.
- The Docker actor adapter supplies audited read semantics for known public
  retrieval methods whose MCP catalog omits read-only hints. Previously real
  chart reads were labelled writes; that could also make final-readback proof
  impossible. Unknown tools and mutating methods still default to writes.
- Narrative Clinical Intake tasks use the assigned provider role's supported
  disposition alternatives. The task need not prescribe the clinical answer in
  advance. Each accepted branch still requires observed disposition/submission
  and fresh same-case readback. Explicit task endpoints narrow the alternatives;
  genuinely unassigned goals remain unverified. Role-level process completion
  is not proof of clinical appropriateness or an official benchmark score.
- Evaluation records recovery count and stable stop-reason codes separately.

## Verification checkpoint

The first integrated suite passed 404 tests in 47.959 seconds. Focused recovery
tests exercise an empty order list followed by a supported new request,
disposition, and verified readback; no-progress termination; budget enforcement;
optional versus required source-order fields; dependency rejection; and audited
read metadata while retaining write defaults for unknown/mutating methods.

One fresh t011 actor trial is planned after source freeze. No original paused
world will be resumed or restarted, and no paid provider-key or judge call is
part of this diagnostic. Live results must be recorded below before claiming
the case is solved. The original `HealthHarness/` remains untouched.

## First fresh t011 trial and additional ordering repair

At source `8f02c6f`, fresh t011 created its new ServiceRequest and case on model
call 4, then recorded `gather_more_evidence` and read back `docs_needed`.
The eight-call attempt had 12 engine operations, no failed evidence or unknown
actions, and a hash-verified deferred snapshot. Its local process gate passed;
the packet was not submitted, forms were incomplete, and no official score was
measured. No claim of clinical appropriateness follows from this observation.

Inspection of that actual action sequence found the actor had made its
disposition before reading the new case's current requirements. I added an
explicit `before_write` contract dependency and pre-dispatch guard: a fresh,
same-case requirements read must precede disposition/submission. A missing
prerequisite returns a known-not-dispatched tool result, allowing normal
replanning; it creates no pending action and does not bypass an existing
pending/unknown journal entry. Final verification checks this ordering too.
Tests now exercise rejection of the premature mutation, the necessary read,
and exactly one subsequent successful disposition. The integrated suite passed
404 tests in 54.458 seconds. A separate fresh trial will verify the final order.

## Ordered workflow trials and external-work handoff

At `977a62a`, two fresh, source-frozen provider checks finished and preserved
their snapshots. t011 created a new case, read its requirements before its
disposition, and read back the result; its local gate accepted a documented
`gather_more_evidence` outcome in 8 model calls / 10 operations. This was not a
submission or approval. t008 prepared its forms (`complete=true`) and recorded
the same waiting-for-evidence branch, but ended unresolved in 11 calls / 18
operations because an external-document obligation remained open. A premature
decision in that attempt was correctly refused before dispatch until a fresh
requirements read was obtained.

I added `case.defer_obligation` for this specific, verifiable handoff condition.
It requires the independent contract to accept the current provider
information-gathering branch, completed forms, and successful fresh same-case
readback evidence. The obligation stays `deferred`, never `closed`; its next
action and source evidence remain in the ledger. The operation sends no
notification. A final result must explicitly preserve `has_deferred_work`, and
the evaluator counts active versus deferred obligations separately. A deferred
obligation cannot silently accompany an unrelated completion branch.

An offline replay of t008's copied actual state successfully recorded that
handoff with one deferred obligation and no active obligations; original
DB/WAL/SHM/result hashes stayed unchanged. No model or actor call was used.
The body-free receipt is under ignored
`runs/20261022-workflow-repair-handoff-replay/`.

The integrated release suite passed **410 tests in 51.728 seconds**. Tests
include rejection of forged deferral evidence and of deferring unfinished form
preparation. Full-suite testing also exposed two implementation defects that I
fixed: the localhost simulator HTTP handler did not consume an unauthorized
request body before reusing its connection, and Windows readers could briefly
deny atomic manifest replacement. Both have deterministic regressions;
metadata retries never repeat a clinical/model action, and permanent denial
preserves the previous valid manifest.

## Final fresh single-task execution

The user explicitly authorized a full fresh single-task viability check.
At source commit `8bbac0f561c46e0f5deb9a666da7da00659e0873`, t008 ran in a
new isolated Docker world using the existing Codex sign-in, GPT-6 Luna high,
and the original 48-model-call / 240-operation limits. The run finished at
11:21:12 IST on October 22, saved its deferred-grading snapshot, and stopped
its world. No other cases were scheduled in this run.

Observed outcomes, independently read from result, actor evidence, local state,
and final environment readback:

| Check | Actual result |
| --- | --- |
| Actor model calls | 11 |
| Engine operations (includes local tools and guards) | 30 |
| Completed external actor calls | 13 |
| Workflow time / whole attempt time | 163.2s / 198.3s |
| New request and case | Created using the supported public tool |
| Forms | Required-field validation complete; this alone is not clinical adequacy |
| Provider disposition / case status | `gather_more_evidence` / `docs_needed` |
| Submitted authorization packets | 0 |
| Outstanding work | 0 active, 1 explicitly deferred external-document obligation |
| Local handoff call | `case.defer_obligation` actually executed once |
| Deferral flags | `notification_sent=false`, `obligation_completed=false` |
| Prerequisite guard | 1 premature decision refused before dispatch; subsequent fresh case read preceded the actual decision |
| Final readback | Successful same-case read after the disposition |
| Failed evidence / model errors / unknown actions | 0 / 0 / 0 |
| Recovery turns | 0; the actor continued through tool-level prerequisite feedback |
| Counterparty simulator model calls | 0; this case did not exercise that path |
| Snapshot integrity | Passed `_verify_deferred_attempt` against the frozen manifest |
| Official score / clinical correctness | Unmeasured |

The accepted branch was `provider_more_evidence_required`. This is a verified
local provider-stage handoff with outstanding work, not a submitted or approved
authorization. It is also not an official successful benchmark run: no official
judge ran, and the experimental Codex-simulator configuration remains marked
ineligible for the official grading path even though no simulator call was
needed in this particular attempt. No paid provider-key call occurred.

Private artifacts are in
`HealthHarnessCodex/runs/20261022-workflow-repair-handoff-03/`, including
`verification.receipt.json`, `batch.manifest.json`, per-attempt results,
evaluation, state, and immutable snapshot. Do not track/upload those payloads.
This attempt is a development check; do not pool it or prior assisted revisions
into a reliability estimate.

The run still exposes context inefficiency: reported actor usage was 539,160
input tokens (57,216 cached), 6,004 output tokens, and 545,164 total tokens across
11 calls. These are model-reported usage, not a provider invoice. Fourteen local
evidence searches were made. The repair demonstrated forward progress and
honest outstanding-work tracking; it does not establish efficient retrieval or
performance across all 75 tasks. UM bootstrap cost and broader task quality
remain unmeasured in this checkpoint.

All 33 original `HealthHarness/` baseline hashes still match. The six old
interrupted worlds remain paused. No full 75-case restart occurred. Next work
should separately measure actual clinical/competition correctness through the
supported grading path and diagnose context/retrieval overhead; changing the
local completion label is insufficient evidence for either.

## Additional fresh t012 check

On the user's request for another single case, root ran t012 alone at unchanged
source `d17960cdccf926e00dc2d8c38b813f0e4f27a2e0`, GPT-6 Luna high, one attempt,
48 model calls / 240 engine-operation limits. The attempt finished at 11:33:31
IST on October 22. No delegated agent was used, no additional case scheduled,
and no paid provider-key or official judge call occurred.

The final actor readback confirms `ready_to_submit`, required forms complete,
and zero submitted authorization packets. The actor created a document bundle,
read the updated case, recorded its provider determination, and read the case
again. The local gate accepted `provider_record_ready_for_submission`. This
is preparation-stage completion, not an authorization submission or official
benchmark pass; the correctness of stopping at that stage is ungraded.

Actual counters: 19 model calls, 55 engine operations, 23 external dispatches
returned, 275.984 seconds of workflow execution. Two responses were application
failures despite normal transport completion: `workspace.search_files` returned
`access_denied`, and `workspace.read_pdf` returned `file_not_found`. Thus the
console's `result_status=success` in these instances means dispatcher return,
not successful evidence retrieval. The evidence ledger correctly retains both
as failures. The actor continued afterward; this does not establish that the
unread PDF was unnecessary or adequately replaced. No model errors, unknown
actions, active/deferred obligations, workflow recoveries, or prerequisite
refusals were recorded. No counterparty simulator call was required.

Snapshot verification passed `_verify_deferred_attempt`; the process and fresh
world are stopped. All six previous worlds remain paused. Results, snapshot,
and body-free `verification.receipt.json` remain ignored under
`HealthHarnessCodex/runs/20261022-workflow-repair-t012-01/`.

Reported usage: 1,392,183 input tokens (546,560 cached), 10,411 output tokens,
1,402,594 total across 19 calls. This aggregate is not the size of one model
context window or a provider invoice. No context-window overflow was observed.
The harness projects messages/evidence to a configured character budget and
retains full evidence for retrieval, but repeated prompt/context material still
incurs substantial usage. The exact contributions of tool schemas, instructions,
history, and runtime overhead have not been measured in this check. No source
changes or software-test rerun were needed to execute this additional trial.
