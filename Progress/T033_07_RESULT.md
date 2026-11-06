# UM t033 -07 completed attempt: incomplete workflow

Inspected the user-run attempt after it stopped, October 24, 2026.

## Actual execution

- 50 model calls, 91 counted tool proposals, no model/response-format failures.
- Reported usage: 2746890 input,45887 output,2792777 total tokens. Cached input
  600320 is included in input, not additional. No helper selected.
- Triage route/disposition recorded. Two nurse-review saves occurred: one empty,
  followed by a save with9 persisted criterion evaluations.
- Nurse recommendation `request_info` submitted; pend letter delivered. Final
  case readbacks indicate awaiting provider documents. No MD review decision or
  final determination is recorded.
- Worker returned structured `incomplete`. Local outcome `unresolved`, stop
  reason `no_new_source_evidence_after_recovery`. This is not budget exhaustion
  or timeout:50 of100 model calls used. One early-stop recovery and2 progress
  replanning prompts were recorded.
- Model attempted the provider-only `case.defer_obligation` in a payer workflow
  repeatedly; those local calls failed the verified-provider-handoff requirement.
  Two obligations remain open. Do not infer from this deferral failure that the
  real payer handoff was invalid; it is a domain-specific local-tool mismatch.
- Batch status `deferred_ready`, local_status `unresolved`, grading pending.
  Snapshot216 files verified; original world stopped and no actor process active.

## Independent native diagnostic on saved-state copy

Ran the supplied native verifier using a copy of the saved logs/export, without
network or credentials and without restarting/replaying the actor. Original
snapshot integrity verified before and after; diagnostic container removed.
No operator inspection of hidden benchmark fixtures/expected outcomes occurred.

**14 applicable structural checks pass;2 fail.** Diagnostic binary reward0;
fractional reward0.875. Full grading remains `ungraded` because the semantic
judge was unavailable in this isolated key-free diagnostic; no paid judge ran.
Do not treat87.5% structural coverage as a complete official benchmark score.

Failed checks:

- `md.decision_exists`
- `md.audit`

Passed checks include nurse reviews/recommendation/audit, target outcome status,
letter types, triage record/disposition/urgency/gold-card/route/audit, and cross-
stage mutation/forward-transition checks. Thus the observed request-info status
and letters satisfy these native outcome checks; the missing MD stage remains
the structural failure. This does not establish clinical-policy correctness or
which decision the MD should have reached.

Ignored artifacts:

- `HealthHarnessCodex/runs/20261024-random-um-t033-07/`
- `HealthHarnessCodex/runs/20261024-um-t033-07-native-diagnostic/summary.json`
- Diagnostic `logs/late_grade/scorecard.json`, native output and cleanup receipt.

## Remaining investigation

Public-contract follow-up: the actual public instruction explicitly assigns
clinical review, MD decision and applicable downstream work to this actor, and
says no other worker picks it up. Public ReviewService supports an MD
`request_info` decision as distinct from an approval/denial. Thus missing clinical
records alone do not establish that all MD-stage work is impossible. The allowed
ordering and reviewer authority in the observed current state still need to be
verified using public contracts/synthetic transitions before a behaviour change;
the failed checks do not authorize inserting an arbitrary MD decision.

Controlled sequence check actually executed: the pinned runtime's actual
ReviewService, request-missing-information and transition methods were exercised
with a synthetic in-memory case/store and the real enabled PayerRoutingGuard.
Nurse `request_info` moved the case to `pended_action_required`; an MD criteria
save and MD `request_info` then succeeded, persisted an MD decision and emitted
the MD submit audit while leaving the case pended. No hidden fixtures, original
case, provider credentials or model inference were used. Ancillary storage,
letter queue and reviewer identities were synthetic. This proves the service/
routing wrapper does not categorically prohibit that sequence; it does not
certify the original case's clinical decision, identity or every whole-harness
policy guard. Receipt/script: `HealthHarnessCodex/runs/20261024-nurse-md-sequence-check/`.

The stopped case's local completion contract also requires a final approved,
partially-approved or denied determination, despite admitting MD request_info
as an MD decision. That is our hand-written scope interpretation, not official
ground truth. Its treatment of documented information-request handoffs needs
audit; do not force a clinical decision merely to satisfy that local template.

Current responsibility handoffs are not automatic staff orchestration. Official
provider/payer tool catalogs are separated, but local case tools include a
provider-only deferral operation exposed to UM. Helpers run only when the owner
requests an actual delegated job; none was requested here. Completing a nurse
subtask or delivering a provider letter does not spawn an MD worker or complete
an explicit whole-UM assignment.

Proposed general repair: source-backed remaining-stage/completion audit before
stopping; domain-appropriate local tools (provider deferral is not UM closure);
clear canonical-name/schema/citation feedback; and an explicit recovery policy
for whether to request a bounded helper audit when unsupported blockers recur.
That helper-invocation policy needs user feedback before imposing a new default.
No implementation or additional actor/judge execution occurred in this follow-up.

Separate the clinical choice to request more information from the incomplete MD
workflow and the local misuse of provider deferral in UM. The source-backed
blocker/schema tools also had earlier local validation failures. Helpers were
available but none was chosen. Future fixes must address general workflow/tool
semantics, not encode this task's expected decision. No source fix or new actor
attempt was launched as part of this result inspection.
