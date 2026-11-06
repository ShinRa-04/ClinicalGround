# Patient identity ambiguity: diagnosis and model-led investigation

## User decision and scope

On October 23 the user approved model-led investigation of multiple positive
patient matches, with a justified selection or an unresolved result. Root
implements directly. No task answers, fixed clinical weights or hidden fixtures
are used. No additional paid judge call is authorized.

## Why the previous attempt was ambiguous

Run `20261023-policy-grounded-t021-02`, source `6a25c13`, stopped after nine
independent comparisons produced two positive matches. The receipt for
comparison 003 used timeline and treatment-history similarities, while already
recording several clinician, imaging and treatment-history discrepancies and
missing supports. Comparison 007 had more specific clinician, imaging and
treatment-history support, while retaining a real imaging discrepancy.

This primarily establishes weak-positive model judgment plus inadequate
controller recovery. It does not establish missing retrieval, missing records,
or inherent non-identifiability of the task. The weak positive's comparison
already contained the differences: they were not unavailable to the model.
Common symptoms or treatment response can be compatible with an intake without
identifying its subject. Requiring two categories checked the format and source
existence, not whether the evidence was sufficiently distinguishing. The
controller reduced each assessment to a boolean and stopped at two positives.

The stronger-looking candidate is not automatically proven correct by that
comparison. Records/intake still have discrepancies. Whether more information
is truly needed depends on a justified investigation of those differences.
Protected receipts remain in ignored run folders; no source text is copied here.

## Implemented behavior

- Original candidate comparisons remain independent. With multiple positives,
  provider discovery invokes a fresh, read-only identity investigation before
  binding any patient. Zero matches remain unresolved; unique matches retain
  the existing path.
- The investigator sees the public intake and preliminary assessments. It can
  inspect fields/passages from each competing chart already retrieved through
  permitted actor tools. No arbitrary file, hidden fixture, external lookup,
  new patient or clinical write is available in this discovery context.
- The model chooses the distinguishing questions and interprets the records.
  A selected result must explain every competitor using source IDs from its
  successful inspections; code captures the exact returned views and original
  chart hashes. No hardcoded category score, preferred candidate or clinical
  outcome is used. Provenance does not prove semantic correctness.
- The model may report unresolved with the specific missing distinctions.
  Malformed/unread/foreign citations cannot force selection. Six investigation
  model calls and sixteen read proposals are maximums; context is bounded.
  Model calls consume the aggregate run budget, reserving eight for workflow.
- Private investigation receipt records sources and declared decision, not
  hidden reasoning. Cross-candidate discussion is not forwarded to the patient
  worker. Only the selected candidate's original independent assessment enters
  that fresh worker context, which rereads its own chart before clinical use.

Source: `HealthHarnessCodex/health_harness_codex/identity_investigation.py`,
`domain_profiles.py`, `standalone.py`. Logs label investigation start/end.

## Verification state

Implemented, not yet demonstrated on a live ambiguity. Seven new focused tests
cover actual source inspection/selection, fabricated and cross-candidate
references, unresolved results, forbidden operations, budgets and selector
integration. A runner integration test verifies aggregate call accounting and
that another candidate's record/discussion does not reach the worker. Existing
discovery/runner tests pass. Full-suite and native results follow separately.

Prior failed attempts remain separate. Green software tests or a justified
identity selection are not benchmark success; real disposition checks and
official semantic grading remain distinct.


Software release verification: full suite 468 passed in 67.722s, log
`runs/20261023-identity-investigation-release-tests.log`. An additional console
label/allowlist test was added afterward; all five console tests passed. No
new simulator/deferred implementation changes; earlier intermittent failures
remain documented in the prior repair report. Fresh one-case native trial is
next, with source frozen and no live hints or paid grading.


## Actual native verification - October 23

Implementation source `531f85d`, frozen trial source including documentation
`4b49b93`. Infrastructure-only launch `20261023-policy-grounded-t021-03`
failed at world startup because Docker Desktop was closed, before model calls.
Docker was restarted and a separate fresh `20261023-policy-grounded-t021-04`
ran to a preserved, integrity-verified snapshot; its world is stopped.

The approved ambiguity recovery was exercised successfully as a mechanism.
Ten initial comparison calls (one correction included) produced two positives.
Four investigation calls performed six underlying record reads, then justified
one selection and rejected the generic-similarity match. The record retains
an imaging discrepancy rather than conflating clinical agreement with identity.
No case-specific hint or code change was provided during execution. The
selected request's service/procedure/diagnosis/site checks passed in the
key-free diagnostic. This supports resolution in this attempt; it does not
establish identity reliability across the dataset or official semantic accuracy.

This provides stronger evidence about the user's ambiguity question: relevant
distinguishing information was already in the permitted records. A fresh
investigation resolved the competing matches using those records alone. The
initial ambiguity was mainly weak-positive model judgment plus our boolean
selector's inability to investigate, rather than demonstrated absent data.
The intake has no direct patient name/DOB, and genuine clinical discrepancies
remain; this finding does not imply that every ambiguous case is resolvable.

The entire healthcare workflow did **not** pass. Thirty-four owner calls and
192 engine operations followed setup. The worker spent many calls reading and
searching evidence/policy, created the correct service request and draft case,
but did not complete forms, record a policy decision or commit a provider
determination. The final response failed parsing (`invalid arguments_json`)
at aggregate call 48; no retry budget remained. Malformed arguments are
confirmed; output truncation is only a hypothesis and is not established by
usage counts. No proposed effect from that unparseable response was dispatched.
No unknown actions; 29 recorded remote evidence successes and no remote evidence
failures. Source-passage recording was not reached, so its live correctness
remains unverified. Do not describe lack of dispatch here as a guard rejection.

Partial network-free verifier results (semantic judge disabled):

- 8 passed; 3 failed; 1 not applicable.
- Failed: `new_referral.case_status`,
  `provider_pre_submission.provider_determination_present`,
  `provider_pre_submission.final_action`.
- Packet absence passed; the earlier wrong-submission failure has not repeated,
  but missing determination is a different failure, not an overall improvement
  claim based on the unchanged pass count.
- Official strict score: unmeasured. Paid calls: zero. Snapshot integrity passed
  before and after diagnostic grading; disposable grader cleanup confirmed.

Private evidence: `runs/20261023-policy-grounded-t021-04/` contains the batch
manifest/source pins, actor evaluation/state, identity investigation receipt,
verified snapshot, and `deterministic-diagnostic/receipt.json`. Reported
full-segment usage: 1,889,560 input + 40,518 output = 1,930,078 tokens, including
589,696 cached input tokens (not subtracted from the usage total). Aggregate
bootstrap phase 230,040 tokens; owner phase 1,700,038. This remains expensive.

The remaining failure class is ineffective evidence-navigation/task closure,
followed by malformed final output without remaining recovery budget. These
are distinct from the now-exercised identity investigation. They need source-
backed diagnosis and a general repair, not a hardcoded disposition or silently
increasing limits. Previous failures and this development retry remain separate.
