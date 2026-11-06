# Model-requested identity reconsideration and clean context

User authorized implementation after clarifying that the model simulates a
worker and should choose its investigation. Workflow code supplies boundaries,
not a fixed clinical decision path. Root implemented this directly.

## Implemented behavior

The model can call `case.request_identity_reselection(reason, evidence_ids)`
when it concludes the current patient/case binding is unjustified. The reason
is retained for audit; it is not copied into the next patient's prompt. Optional
citations must belong to successful observations in the current scope.

The engine stops the tool batch immediately, marking subsequent sibling calls
as not dispatched. The controller independently checks the action journal:

- Before external writes: actor messages, state, evidence, obligations, caches
  and identity-decision receipts move into a private `quarantine/episode-NNN/`
  archive with file hashes. No records are deleted. Fresh discovery excludes
  the identity the model explicitly rejected, without sending its medical
  details to candidate comparisons or the next case worker.
- After external writes, pending writes, unknown outcomes, or unavailable
  journal evidence: automatic reset is blocked for reconciliation. Changing
  context cannot undo or hide actual environment effects.
- A trusted explicit pre-dispatch rejection is known effect-free and does not
  block reset. A generic error response is not treated as proof of no effect.
- Completed workspace drafts can be abandoned without treating them as clinical
  mutations. Their old case directory is outside the new worker's permitted
  workspace roots. An uncertain workspace write still blocks reset.

Fresh episodes read the original public task, use the general instructions,
revalidate the model connection, discover actor identities and create a new
SQLite working state. Previous clinical facts, conclusions, form drafts,
obligations, citations, helper discussions and cached readouts are not inherited.
Only the new candidate's own validated identity assessment may enter its case.
This is context isolation, not a claim about provider-side deletion.

The original model/tool budgets remain cumulative, including bootstrap calls;
they do not reset. Default reset limit is two, configurable programmatically
from zero to four, with the original budgets still limiting every episode.
If no candidate remains, or fresh discovery fails, the attempt remains failed
with its quarantine and reset history intact. There is no fabricated recovery.
Existing externally mutated worlds are never reset or silently replaced.

## Code and records

- [Controller](../HealthHarnessCodex/health_harness_codex/reselection.py):
  journal recheck, quarantine, cumulative budgets and episode orchestration.
- [Engine](../HealthHarnessCodex/health_harness_codex/engine.py): model-facing
  request tool, citation validation, write barrier and sibling-call stop.
- [Standalone](../HealthHarnessCodex/health_harness_codex/standalone.py):
  new episode connection/scope and final rejected-identity check.
- [Discovery](../HealthHarnessCodex/health_harness_codex/domain_profiles.py):
  provider, UM and CM exclusion before selecting another subject.
- Ignored `identity-resets.private.json` records transitions and accounting;
  quarantined file hashes preserve audit integrity. Final actor evidence and
  current-scope state remain distinct from aggregate usage across episodes.

## Verification scope

Integration tests exercise an actual Harness/SQLite episode that reads patient A,
creates an obligation, requests reset and proposes a later write. That write
does not run. A fresh episode reads patient B; assertions reject any occurrence
of patient A's secret marker or obligation in its model input. The old database
and result remain archived, while cumulative call counts remain charged.

Other tests cover completed external writes, pending writes, a falsely declared
safe reset independently rejected by the controller, depleted budgets, and
excluded provider/CM identities not being read into new discovery.
This is software/integration evidence, not an official dataset score. See
[repair chronology](IDENTITY_CONTEXT_RECOVERY_REPAIR.md) for prior live failures.

Final full suite: **447 tests passed in 53.955s**. An earlier full run failed
one existing simulator timeout/claim timing test; it passed in isolation and
the repeated full suite passed. A later run exposed an existing concurrency
test barrier firing twice during recursive directory creation; precreating its
parent directory fixes the test synchronization without changing production
behavior. Its isolated check and the final full suite pass. Simulator code
was not changed by this repair.
No new paid judge call or native dataset run was used for this software result.

## Cross-project preference

At the user's explicit request, a small note was saved under the shared Codex
memory extensions folder: when repeated failures implicate an assistant-chosen
design decision, explain concrete evidence and ask the user for constructive
feedback before repeating that approach. No global AGENTS file, instruction
hash pin or credential was changed.
