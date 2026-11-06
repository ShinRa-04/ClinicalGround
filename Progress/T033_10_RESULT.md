# t033 -10: structural checks pass; semantic grading and local closure unresolved

Inspected the user-run attempt on October 24, 2026. No actor replay or source
change was made during this inspection.

## Actual execution

Run: `HealthHarnessCodex/runs/20261024-random-um-t033-10/`,
`pa_um/pa_t033_t033_o001_p01_triage_payer/attempt-1`.

- Actor finished at 19:51:29 IST after 690.437 seconds with local status
  `unresolved`, 46 model calls and 99 counted tool proposals. No model failure,
  timeout or model/tool budget exhaustion. Reported usage: 2,762,407 input,
  38,475 output, 2,800,882 total tokens. Cached input 686,976 is included in
  input, not added to it. Do not describe this as efficient execution.
- Observed triage, nurse review/recommendation and MD request_info write.
  Pend notice delivery and fresh MD/case summary reads succeeded. The local
  `um_md_information_handoff` branch is accepted with no missing milestones.
  The finalized-determination branch remains unsatisfied; this does not by
  itself prove that finalization was required instead of the information handoff.
- Two optional-actor validation corrections ran, on triage.set_disposition at
  calls 14 -> 15 and 19 -> 20. The earlier fatal audit-actor rejection did not
  recur. No new identity binding or weakened isolation was needed.
- One automatic recovery audit ran with three model calls/eight proposals. It
  exhausted its delegated model budget and returned incomplete; it did not
  produce a completed source-backed critique. Helper availability/invocation
  must not be described as a successful helper investigation.
- The external-document obligation was recorded as deferred, not falsely
  closed. Final model response still said incomplete while acknowledging the
  structurally verified MD information handoff. Calls 42/44/46 returned finals;
  calls 43/45 rechecked evidence/audit or re-recorded the handoff. No new source
  evidence after recovery caused the final stop. This is a completion/scope
  disagreement; do not automatically override the worker or force a different
  clinical decision merely to produce a local complete flag.
- Batch capture finished at 19:51:38 IST with 216 snapshot files and world stop.
  `deferred_ready` indicates preserved execution, not benchmark success.

## Independent native structural verification

Executed the same key-free offline native diagnostic used for -07 against a
separate copy of this saved export/logs. No actor restarted or replayed, no
credentials supplied, network disabled, diagnostic container removed. Original
snapshot provenance/inventory verification succeeded before and after. Native
verifier consumed its fixtures normally; operator did not inspect hidden
fixture/solution/expectation contents.

**18 applicable structural checks passed; zero failed; ten structural checks
were not applicable.** Diagnostic binary reward 1.0 and fractional reward 1.0
cover only those checks. The earlier md.decision_exists and md.audit failures
now pass, along with MD rationale/sign-off, nurse, outcome, triage and cross-stage
structural checks.

**Thirteen semantic judge checks are unscored.** The diagnostic intentionally
had no judge credentials; verifier metadata reports unavailable authentication.
That says nothing about whether the operator's configured paid connection is
currently usable. No paid judge was attempted. Clinical-policy interpretation,
decision appropriateness and a full official strict score remain unverified.
Do not label the diagnostic reward as a complete competition result.

Ignored evidence:

- Original `...t033-10/` result, events, state and deferred snapshot.
- `runs/20261024-um-t033-10-native-diagnostic/summary.json`.
- Diagnostic `logs/late_grade/scorecard.json`, `reward.json`, private verifier
  output and cleanup receipt.

## Remaining work

Resolve the owner/local-audit disagreement about completing an information
handoff versus resolving the subsequent clinical matter, using public assignment
and observed effects. The model retained that distinction in its final wording
but still selected incomplete. The native structural result supports the
recorded effects; it does not validate policy reasoning. Investigate why the
bounded helper ended without a conclusion. Keep these general issues separate
from task-specific answers, and obtain semantic grading only under authorized
connection/spending settings. No further dataset run was launched in this turn.
