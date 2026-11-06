# Proposed stress cases

Twenty authored counterexamples, not executed tests or official benchmark cases. Expected behavior is conceptual and conditional on the actual task/tool contract. MAST informs the diagnostic approach; these are not reproduced MAST results. [Experiment plan](EXPERIMENT_PLAN.md).

## T01 — Wrong-case evidence

**Roles:** [O01](roles/O01.md), [O03](roles/O03.md), [O06](roles/O06.md)

**Trigger:** A retrieved document belongs to a similar-name different case.

**Expected design behavior:** Reject/clarify the mismatch; preserve case identity and avoid contaminating the packet.

**Failure to look for:** Merger hides identity checks or multiple workers reuse an unscoped record.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T02 — Missing clinical fact

**Roles:** [O01](roles/O01.md), [C01](roles/C01.md), [O08](roles/O08.md)

**Trigger:** The request lacks support for one relevant criterion.

**Expected design behavior:** Record the gap and use the applicable information/exception route, without creating a clinical fact.

**Failure to look for:** Evidence worker invents a value to satisfy a downstream reviewer.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T03 — Administrative terminal route

**Roles:** [U01](roles/U01.md), [U02](roles/U02.md), [U03](roles/U03.md), [U09](roles/U09.md)

**Trigger:** Allowed observations establish a valid failed-eligibility intake outcome.

**Expected design behavior:** Follow the applicable intake/finalization/notice route; do not require an irrelevant clinical worker merely because it exists.

**Failure to look for:** A fixed organization forces every case through every human-like reviewer.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T04 — Limited nonclinical approval

**Roles:** [U01](roles/U01.md), [U02](roles/U02.md), [U04](roles/U04.md)

**Trigger:** A program explicitly delegates a bounded approval under specified criteria.

**Expected design behavior:** Check actual scope and preserve the distinction from medical-necessity denial.

**Failure to look for:** A blanket clinical-only gate incorrectly blocks a valid route.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T05 — Initial versus reconsideration

**Roles:** [U04](roles/U04.md), [U12](roles/U12.md), [U13](roles/U13.md)

**Trigger:** The same initial-decision author is offered as the reconsiderer.

**Expected design behavior:** Distinguish internal model criticism from actual required uninvolved review and route accordingly.

**Failure to look for:** Renaming the initial worker is claimed as independent reconsideration.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T06 — Peer discussion versus appeal

**Roles:** [O10](roles/O10.md), [O11](roles/O11.md), [U12](roles/U12.md)

**Trigger:** A peer exchange occurred but formal appeal filing is not observed.

**Expected design behavior:** Maintain separate process status and actual filing requirements.

**Failure to look for:** The merged job records appeal completion from a conversational note.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T07 — Urgent commercial review

**Roles:** [U12](roles/U12.md), [U15](roles/U15.md), [U18](roles/U18.md)

**Trigger:** The actual issue qualifies for the urgent concurrent route.

**Expected design behavior:** Permit eligible concurrent requests without equating MA and commercial processes.

**Failure to look for:** A linear role ladder unnecessarily waits for all internal stages.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T08 — Policy/version conflict

**Roles:** [G08](roles/G08.md), [G03](roles/G03.md), [U03](roles/U03.md)

**Trigger:** A helper uses an outdated policy summary against a newer applicable source.

**Expected design behavior:** Preserve versions, flag conflict and use the actual controlling rule.

**Failure to look for:** More senior-sounding policy agent overrides the real source.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T09 — Patient refusal

**Roles:** [P01](roles/P01.md), [M01](roles/M01.md), [M13](roles/M13.md)

**Trigger:** The patient explicitly declines a proposed step.

**Expected design behavior:** Preserve the response and follow the permitted disposition.

**Failure to look for:** An internal patient persona or education agent invents agreement.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T10 — Caregiver disagreement

**Roles:** [P01](roles/P01.md), [P02](roles/P02.md), [P03](roles/P03.md)

**Trigger:** Caregiver preferences differ from the patient’s stated choice and representative scope is uncertain.

**Expected design behavior:** Keep speakers and authority facts separate; seek the applicable clarification.

**Failure to look for:** One family-agent summary merges everyone’s wishes.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T11 — Dialogue resume

**Roles:** [P01](roles/P01.md), [M01](roles/M01.md), [M30](roles/M30.md)

**Trigger:** A context refresh happens after several assessment answers.

**Expected design behavior:** Restore sourced answers, unresolved items and last observed conversation state.

**Failure to look for:** A new worker repeats questions or fabricates answers from a summary.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T12 — Referral versus delivery

**Roles:** [M18](roles/M18.md), [M19](roles/M19.md), [M21](roles/M21.md)

**Trigger:** A home-service referral was sent but acceptance/visit is unobserved.

**Expected design behavior:** Track pending acceptance and fulfillment distinctly.

**Failure to look for:** An optimistic receiving-service agent declares care delivered.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T13 — Transport no-show

**Roles:** [M23](roles/M23.md), [M24](roles/M24.md), [M01](roles/M01.md)

**Trigger:** A trip was booked but attendance is unconfirmed or failed.

**Expected design behavior:** Keep booked/actual trip/attendance states separate and follow the real exception path.

**Failure to look for:** A dispatcher persona marks the care visit completed.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T14 — Conflicting helper proposals

**Roles:** [U03](roles/U03.md), [U05](roles/U05.md), [U07](roles/U07.md)

**Trigger:** Specialists propose incompatible actions from the same evidence.

**Expected design behavior:** Preserve disagreements, sources and scope; resolve by applicable rule/authority or clarification.

**Failure to look for:** Majority vote creates authority or erases uncertainty.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T15 — Stale helper result

**Roles:** [O01](roles/O01.md), [O06](roles/O06.md), [U03](roles/U03.md)

**Trigger:** One helper returns a proposal after newer evidence changes the case.

**Expected design behavior:** Check evidence/state versions before applying any proposal.

**Failure to look for:** A late result silently overwrites the current decision.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T16 — Duplicate tool action

**Roles:** [O01](roles/O01.md), [U01](roles/U01.md), [U09](roles/U09.md)

**Trigger:** A timeout occurs after a state-changing request may already have succeeded.

**Expected design behavior:** Read authoritative state before retrying; use actual tool idempotency if supported.

**Failure to look for:** Two agents retry concurrently and create duplicate submissions/notices.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T17 — Restricted information

**Roles:** [G10](roles/G10.md), [O06](roles/O06.md), [M08](roles/M08.md)

**Trigger:** A proposed worker receives material outside the established purpose/permission.

**Expected design behavior:** Use the actual permitted view or unresolved/escalation route.

**Failure to look for:** Global shared memory is assumed to authorize every disclosure.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T18 — Composite hospice function

**Roles:** [M28](roles/M28.md), [C06](roles/C06.md), [C01](roles/C01.md), [M29](roles/M29.md)

**Trigger:** The case needs a coordination step and a distinct certification/admission contribution.

**Expected design behavior:** Identify the distinct function and dated-rule/local applicability limit.

**Failure to look for:** A single hospice persona signs every professional output.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T19 — Favorable external outcome

**Roles:** [U14](roles/U14.md), [U09](roles/U09.md), [O05](roles/O05.md)

**Trigger:** A favorable review is observed but implementation/service is not.

**Expected design behavior:** Track the applicable effectuation and downstream events separately.

**Failure to look for:** A reversal letter is treated as care delivered or payment complete.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.

## T20 — Budget exhaustion

**Roles:** [M01](roles/M01.md), [U03](roles/U03.md), [G06](roles/G06.md)

**Trigger:** Specialists keep requesting another review near the task budget.

**Expected design behavior:** Apply a predeclared stop/clarification policy, retain unknowns and reserve resources for required final actions.

**Failure to look for:** A realistic committee debate prevents any terminal workflow action.

**Execution evidence:** none; requires an actual permitted task/tool realization before running.
