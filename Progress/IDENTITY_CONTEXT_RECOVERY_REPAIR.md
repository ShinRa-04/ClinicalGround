# Identity, reference context and recovery repair — October 22

## Scope and ownership

User authorized root to correct all three defects identified in the random
t021 execution. Root implemented the changes directly; no delegated agents.
The original failed attempt and hidden benchmark expectations remain untouched.
No provider credentials, global policy changes or additional paid judge budget.

## Implemented changes

### Identity admission before case mutation

`domain_profiles.py` no longer binds an unnamed provider task using the longest
unique clinical phrase, a diagnosis label or surname alone. Explicit full-name
matching remains a separate route. Otherwise candidates with known demographic
contradictions are excluded, preserving unknowns and age/date ambiguity, and
the remaining candidates are compared independently through the existing
isolated model interface. Clinical phrase length cannot exclude a paraphrased
correct chart.
Only one positive candidate may proceed. Zero/multiple positives stop setup
before clinical mutations. An explicit full patient name remains a constraint.

`standalone.py` strengthens provider comparisons: a positive match requires
two distinct quoted facts in different categories, at least one involving
imaging, treatment history or timeline, and no reported contradiction. Task
quotes must occur in the clinical narrative, not merely the diagnosis heading;
candidate quotes must exist verbatim in its supplied source JSON. Invalid
evidence receives one candidate-local correction, still charged to the original
aggregate call budget. This validates source correspondence; it is not a claim
that string validation can prove semantic entailment or eliminate model error.
UM retains its existing separate identity comparison contract.

### Bounded file text remains readable

`working_set.py` exempts bounded workspace text/PDF reads from generic 6,500-char
recent-turn dictionary compaction. A 24k-character, same-scope cache retains
exact source-linked reference excerpts beyond the ten-turn window. Full raw
evidence remains unchanged. Overflowing cache entries still have their original
source and retrieval path; cached references never count as fresh case readback.

### Targeted recovery rather than repeating a generic blocker

`workflow.py` constructs source-attributed recovery diagnostics: successfully
returned reference text and exact inspection pointers, observed missing form
fields, and failed operations. It explicitly distinguishes omitted context
from missing source material and prohibits inventing values or switching a
patient inside an already-bound case.

Previously unseen source-field inspections count as information-access
progress, while repeated identical inspections, notes and bookkeeping do not.
Recovery can use up to four rounds, bounded by the original call budget, but
stops when no distinct source/readout progress occurred. The limit increase is
paired with targeted checks, not treated as the corrective mechanism alone.
Completion checks, unknown-write fencing and actual submission requirements
remain enforced.

## Verification before live retry

- **437 software tests passed in 45.162s.**
- Regressions cover a diagnosis distractor versus a paraphrased candidate,
  missing identity evidence, contradictory/fabricated quotes, exact file text
  surviving compaction and later turns, scoped recovery pointers, distinct
  inspection progress and bounded recovery.
- Offline replay of the failed t021 actor's actual saved observations retains
  both reference texts exactly: 3,279 and 7,520 characters. Two reference checks
  and three observed gaps are now present in the generated recovery plan.
- The replay made zero model/API calls or clinical operations and verified the
  original SQLite file hash unchanged. Receipt stays ignored at
  `runs/20261022-random-case-223642/repair-offline-replay.json`.

## Live verification

A fresh t021 retry will use frozen corrected source and the same declared
actor limits. This is an assisted development revision after a failed test,
not an additional random reliability sample. Preserve separate receipts and
report the actual state, deterministic checks and token usage. No full semantic
judge evaluation or strict-score claim without the required paid evaluation.

Started `runs/20261022-repaired-t021-01` at 23:00 IST, source `736e2a1`,
root-owned PID 20672. Root stopped it during read-only bootstrap: the roster
contained 65 patients, and comparing all of them would exceed the 48-call
aggregate budget. No clinical workflow began. An export/hash and stop receipt
are preserved; the world is stopped and manifest running marker is historical.
Do not resume this development setup attempt or call it a task result.

Corrected screening uses only observed demographic contradictions: known sex
mismatch or age incompatible with the chart's actual dated records (retaining
a one-year birthday/date margin). Unknown demographics remain candidates; the
host clock is never a clinical reference date. A read-only actor audit retained
9/65 candidates for t021. A capacity guard now refuses an oversized candidate
set before any model comparisons and reserves workflow budget. Added regressions
cover contradictory/unknown demographics and zero-call budget rejection.
Final corrected release: **439 software tests passed in 51.863s**.

## Retry 02: identity gate overcorrected; feedback requested

Source `059e195`, `runs/20261022-repaired-t021-02`, screened 65 public charts
to nine demographic-compatible/unknown candidates. Nine isolated comparisons
returned zero positives. Setup therefore failed before any clinical workflow
or case mutation. World export/hash and stop receipt are saved; world stopped.
This is not a successful execution or a complete repair verification.

Runtime task ID and public instruction hash exactly match the selected local
task; both known public tool-reference aliases exist. A read-only actor-chart
audit found a strong narrative candidate with matching clinician, broad
timeline, treatment history and distinctive imaging features, but discrepancies
in some clinical details. Hidden expected IDs were not consulted, so this is
not independent confirmation of the intended target. The current blanket
"no substantive contradiction" identity rule can reject a plausible identity
because it conflates clinical consistency and identity. Further model decision
audit is needed; the individual comparisons' explanations were not retained
as standalone proof receipts, another observability gap to address.

User asked for explanation and constructive input before proceeding. Proposed
correction: separate identity anchors from clinical/temporal discrepancies;
keep case facts attributed and unresolved, and let the owner investigate using
allowed tools while code enforces isolation, budgets, evidence and actual
effects. Clear identity conflicts or unresolved multiple candidates still
block writes. Two asynchronous preference questions are pending about that
separation and model-directed versus coded recovery. Do not treat the default
choice as a submitted answer or claim all three problems are solved.

## User clarification: constraints rather than prescribed decision paths

User confirmed that the model is simulating a worker and should decide what
information is missing and how to investigate. User then clarified that workflow
rules should prohibit inappropriate actions, not reduce the worker to a menu of
our preferred choices. This supersedes the earlier pending-preference wording.
Retain actual tool prerequisites, isolation, source validation, budgets and
truthful outcome checks; remove author-imposed clinical/administrative route
assumptions that are not justified by the task or service contracts.

User's annotations identify the roughly matching measurement as support for the
stronger candidate, flag the tendon detail for further investigation, and propose
discarding a wrong patient's working context when reconsidering selection.
The tendon entries in the earlier table belonged to different candidate charts;
they are not already-confirmed contradictory reports for the same patient.
Do not merge them. The stronger candidate's exact intended identity remains
unconfirmed independently of hidden targets.

Required scope-reset design (NOT implemented yet): allow the model to request
identity reconsideration. Before clinical writes, quarantine the old scoped
working state and start a fresh investigation context containing the public
task, general instructions and remaining budget, with no prior patient's facts,
citations, form drafts, obligations or cached observations. Keep audit artifacts
outside model-visible context. A new model session/context is not a guarantee
of provider-side data deletion. After writes, preserve and reconcile actual
effects; resetting context must not erase records, retry accounting or failures.

## Implemented after retry 02; not live-verified

Provider identity responses now distinguish `identity_conflicts` from
`clinical_discrepancies` and `missing_support`; a clinical discrepancy alone
does not veto an otherwise supported identity. Every declared comparison,
source hash and validation outcome is saved privately, without hidden reasoning.
Only the selected candidate's validated assessment is forwarded to the case
worker as attributed bootstrap analysis, not new clinical evidence. This fixes
the missing handoff of discovered uncertainties.

**440 software tests passed in 43.139s**. Regressions cover clinical discrepancy
versus explicit identity conflict, preservation of decision receipts, refusal
to overwrite receipts, and forwarding selected-patient uncertainty. No fresh
case run has verified this revision. Scope-reset behavior remains planned.
