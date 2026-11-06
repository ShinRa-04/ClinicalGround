# User-run t021 after context-reset changes — October 22, 2026

## Scope

Checked user execution `HealthHarnessCodex/runs/20261022-repaired-t021-03`.
Frozen source `86082e8eac175a14847b95fa92aea29fc605e7c1`, Luna high.
The run was not restarted or modified. No hidden expected values were opened.
Root ran isolated deterministic verifier logic with semantic judging disabled,
using the saved immutable export; network disabled and zero paid judge calls.

## Actual execution

| Item | Observed result |
| --- | --- |
| Batch status | `deferred_ready`, grading pending |
| Local harness status | `unresolved` / `incomplete_workflow` |
| Actual case status | `submitted` |
| Forms complete | True |
| SubmissionPacket count | 1 |
| Identity comparisons | 9, one accepted, no validation errors |
| Actor calls / bootstrap / total | 29 / 9 / 38 |
| Engine operations | 54 |
| Reported full-segment input / output | 1,305,174 / 18,558 tokens |
| Reported full-segment total | 1,323,732 tokens |
| Context resets / recovery prompts | 0 / 0 |
| Model errors / unknown actions | 0 / 0 |
| Snapshot integrity | Passed before and after diagnostic |
| Attempt world / diagnostic container | Stopped / removed |

The corrected identity selection now resolves the target service request/case:
their deterministic checks pass, along with procedure, diagnosis, service type
and site. This establishes an improvement over the earlier zero-target-match
failure. It does not establish an overall successful result.

## Deterministic checks: 8 pass, 3 fail, 1 N/A

| Check | Result |
| --- | --- |
| `new_referral.service_request_created` | Pass |
| `new_referral.procedure_code` | Pass |
| `new_referral.required_diagnosis_codes` | Pass |
| `new_referral.service_type` | Pass |
| `new_referral.site_of_service` | Pass |
| `new_referral.case_created` | Pass |
| `new_referral.case_status` | **Fail** |
| `provider_pre_submission.provider_determination_present` | Pass |
| `provider_pre_submission.final_action` | **Fail** |
| `provider_pre_submission.packet_absent` | **Fail** |
| `provider_pre_submission.required_documents_present` | N/A |
| `cross.forward_transitions` | Pass |

The packet-absence and final-action checks fail on an actual submitted request.
These support a remaining disposition/branch problem rather than the old
missing-target problem. No semantic judge ran; the full official score is
unmeasured. The deterministic failures already prevent calling this a successful
benchmark attempt.

The local completion gate also rejected the endpoint: its missing milestones
are `provider_gather_more_disposition`, `fresh_docs_needed_readback` and
`case_identity_readback`. No final-format retry or automatic stop recovery was
recorded. The public task, generated local contract, model disposition rationale
and actual source requirements should be compared before changing decision
rules again. Follow the user's preference: explain recurring design problems
and ask constructive questions rather than repeatedly imposing another route.

## Simulator log line

## Follow-up: why the three checks fail

The recorded provider operation used `final_action=submit_pa`; it then created
a bundle and successfully submitted authorization. Generic verifier code emits
the provider-final-action comparison only for expected non-submit dispositions,
and its packet-absence check rejects a packet, bundle, submission artifact or
submission audit event. Thus the three failed checks share a wrong workflow
action rather than representing three independent tool failures:

- Case status: actual `submitted` does not match the required non-submit state.
- Provider final action: actual `submit_pa` does not match the required
  non-submit disposition. Hidden expected action values were not opened.
- Packet absence: an actual bundle and submission packet exist, with a
  successful submission operation. This check requires their absence.

The model's visible action statements repeatedly cite complete fields and
`ready_to_submit` as the basis for recording submission and sending the bundle.
The site-of-service answer uses the surgeon's planning-note rationale that
preferred fixation equipment is unavailable at a nearby ambulatory facility.
That is authentic documentation of the provider's request, not independent
proof that the payer's hospital-outpatient criteria are met.

The saved actor evidence contains **zero workspace reference-file/PDF reads**.
The first case read contains no policy/criteria fields. The available trace
therefore does not establish that the model actually checked the governing
site-of-service policy before choosing submission. Filled forms and a runtime
readiness state are not semantic validation of policy applicability or medical
necessity. Tool dispatch succeeded; the supported decision basis was deficient.

The exact policy-specific clinical reason for the benchmark's non-submit
expectation remains unconfirmed: no semantic judge or independent governing-
policy review was performed. Do not claim a definitive coverage conclusion or
hardcode this task's expected branch. Compare the actual applicable policy,
source documentation and the actor's stated decision first, and discuss design
changes with the user before imposing another fixed route.

## Simulator shutdown verification

At 23:53:05 IST, `simulator_worker_stopped` recorded status `settled` with zero
model calls. Its manifest summary has zero submitted/completed/failed/unknown
calls, zero pending/unresolved requests and `settled=true`. Its elapsed time is
worker lifetime, not active simulator inference. It was idle and shut down
cleanly; this is not evidence of the task's failure.

`UNKNOWN simulator_worker_stopped` was the console formatter's fallback for a
missing display mapping. Added `SIMULATOR_STOPPED`; four existing console tests
pass and formatting the actual event fields now shows a clear settled event.
Original saved logs remain unchanged.

## Private evidence

### Policy-specific follow-up — October 23

At the user's explicit request, reviewed the permitted written site-of-service
policy and the actor-observed planning note. Found a limiting clause that the
equipment rationale did not satisfy, plus a separate possible qualifying basis
that remains unresolved in the record. These explain the submission's deficient
support without consulting hidden expected actions. This is a payer setting
review, not a conclusion about whether the surgery itself is necessary.

The local reference file hash matches the same approved policy inside the
pinned runtime image. Hash verification used a disposable network-disabled
container, zero model calls and no clinical operations. Protected clauses and
case details are documented only in ignored
`runs/20261022-repaired-t021-03/policy_review.private.md`; verification receipt
is `policy-reference-verification.json`. No hidden fixture/solution reading,
paid evaluation, code change or rerun was needed. No benchmark result changed.

Saved attempt results, evaluation, nine identity comparison receipts, SQLite
state and deferred snapshot remain ignored. Root's additional diagnostic lives
at `deterministic-diagnostic/receipt.json` with integrity and cleanup evidence.
No paid API call, new attempt or hidden-answer inspection occurred.
