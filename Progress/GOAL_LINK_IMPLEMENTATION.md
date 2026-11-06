# Goal links and selective precommit review — October 25

User authorized implementation and requested concrete benefits before accepting
the context cost of a dependency graph. Root implemented this in the existing
Codex fork; no global hospital graph, graph database or new external dependency.
The broader evaluation/model-experiment matrix remains on hold. Clarification
about a fresh single-case execution is pending; no dataset actor or paid judge
has been launched for this implementation.

## Intended benefits and what is actually established

| Problem | Implemented mechanism | Evidence boundary |
| --- | --- | --- |
| One missing fact becomes a whole-case blocker | Existing blocker records link to named current-case obligations and a next investigation; other work remains visible | Offline regression verifies scope of records, not that an LLM will choose the best next action |
| Requested outcome is silently replaced by an acceptable stop | Contract separately identifies requested branches; outcome assessment remains unmet after an alternative terminal branch | Offline CM fixture distinguishes a supported decline from a requested finalized plan |
| Irreversible action happens before its consequences are considered | Source-backed decision must bind exact proposal and explain remaining actions/why now; selective read-only critique returns to a new owner turn before dispatch | Dispatcher regression verifies no write reservation, no stale sibling dispatch, and exactly one later write on re-proposal |
| Unsupported blocker ends execution before investigation | One bounded pre-stop critique for an unmet mapped goal reuses existing recovery helper | Deterministic model stub verifies owner receives feedback and can continue; not a model-quality experiment |
| Work must be falsely marked completed to stop | Source-linked blocked obligations remain open; supported alternative stop needs an explicit acknowledgement and no-further-action record | Tests verify unrelated open work still blocks closure and no obligation is marked completed |
| Context repeats descriptions without actionable links | Bounded current-goal slice replaces duplicated blocker/work lists; full records remain paged in SQLite case state | Projection sizing below; not a full token-efficiency result |

## Representation and boundaries

`goal_state.py` computes the primary requested outcome from the pinned public
instruction contract and original scoped effects. It does not inspect hidden
expectations or choose consent, approval, denial or eligibility. Goal/outcome
interpretation still depends on the existing public endpoint compiler; this is
not a new general natural-language task parser or proof of semantic correctness.

The live links reuse `obligations.depends_on` and `prerequisite_records`.
`affected_obligation_ids` must exist in this case; `next_investigation` remains
the owner's interpretation. These links never disable other tools or certify
that another action is permitted. The primary task marker remains visible.

Full hospital research relationships are not automatically imported or turned
into prerequisites. Existing domain contracts/role descriptions remain the
starting knowledge; active relationships are recorded only for the actual case.
This deliberately narrows the earlier broad graph proposal in response to the
user's context-cost concern. A full template importer remains unimplemented.

The new read tool `case.get_goal_state` pages active blockers and unrelated open
work independently. It can read bounded excerpts of the original task instruction.
`case.get_working_record(kind="work")` retrieves full original obligation records.
Omission/pagination is explicit; no data is discarded from the case store.

## Before consequential actions and stopping

The public contract's alternative terminal branches, or an owner's declaration
of primary-goal impact in a source-backed decision, identify consequential
proposals. The model records `remaining_actions_considered`, `why_act_now`, exact
`bound_arguments`, and `unmet_goal_ids` when applicable. Clinical applicability
remains unverified by code. Unmodeled effects can still be missed by the owner;
this mechanism is not proof against every premature decision across all domains.

`terminal_review.py` uses the existing SH-10 scoped helper with read-only tools,
current case observations and cited policy sources. Helper writes/recursive
delegation are excluded. Shared budgets, transactional fences, source isolation
and existing composition/recovery policy remain authoritative. Helpers disabled
or budget unavailable is recorded as owner-only review, not independent approval.

A review is fingerprinted against the exact action, justification, contract and
source content. Identical content under a new evidence ID does not create a new
review. New proposal/source material can require another review. The helper's
advice is not a judge verdict. The owner must re-propose in a new turn; queued
siblings from the prior proposal are answered as not dispatched.

For any mapped domain, an initial proposed stop with the requested outcome unmet
can trigger the existing bounded read-only recovery review before termination,
instead of waiting for repeated failures. A completed terminal review avoids a
duplicate pre-stop critique. Ordinary actions and achieved goals do not trigger
this pathway. Legacy states without the new feature flag retain old execution
behavior; old run artifacts are not rewritten.

Closure still distinguishes provenance from semantics. A sourced blocker and
stop record do not mathematically prove no useful action exists. The final model
judgment remains subject to evaluation. Unknown writes still require actual
reconciliation; no review authorizes replay. No clinical outcome is hardcoded.

## Output and cost

Results now carry `execution_assessment`: running/stopped/finished, requested
outcome achieved/unmet/unverified, observed endpoint and benchmark unassessed.
Finished/goal-unmet is its own operational classification. Console and batch
events display both execution state and goal status, warning on finished/unmet.
This changes neither official checks nor scoring.

The automatic goal slice is bounded to 3,200 characters. Explicit reads can
retrieve fuller records; the user's overall `--max-context-chars 0` setting is
unchanged. No extra planning model call is required for ordinary operations.

Offline serialized context sizing, same synthetic state before/after the working
projection change, without remote schemas or model inference:

| Active blocker records | Previous projection chars | New projection chars | New goal slice chars |
| --- | ---: | ---: | ---: |
| 0 | 2,845 | 4,160 | 1,321 |
| 1 | 4,054 | 4,770 | 1,914 |
| 6 | 10,104 | 5,988 | 3,100 |
| 25 | 10,111 | 5,993 | 3,104 |

All 25 records remain stored. This has overhead in simple cases and saves repeated
description space in busier cases. It does not measure real model tokens, total
runtime cost or improved task success. A selective helper can add up to three
model calls and eight read proposals, within shared limits, on a consequential
review. Existing recovery review also remains bounded; no recursive review chain.

## Files and verification

- New `health_harness_codex/goal_state.py`, `terminal_review.py`.
- Existing planning, policy grounding, engine, closure, context projection,
  recovery helper, public completion mapping, recording and logs integrated.
- Public CM transcript retrieval is classified as read-only from its service
  contract, allowing scoped read-only reviewers to inspect it.
- `tests/test_goal_planning.py`: targeted offline dispatch, provenance, context,
  pagination, state, reporting and budget regressions.

First integration: 695 regression tests passed in 61.341s before the additional
pre-stop/paging/logging refinements. Final verification: **700 regression tests
pass in 61.954s**, including 19 targeted goal-planning regressions. The final
scope-binding regression ensures planning/reporting use the same host-validated
actor identity as dispatch; invalid binding views become unverified and cannot
prevent error persistence or grant permissions. Private receipt:
`runs/20261025-goal-planning-release-regression.log`.
All 33 original harness baseline hashes match. Both new modules are included in
the batch's source fingerprint (53 package source/data files).
Source fingerprint: `b35e8d419fbbe24b5d0165a16359b2ce4cecfc922449bdb24a2b58ddc3084202`.
Patient simulator and native benchmark runtime are unchanged. Latest actual dataset result
remains CM -04: 2/6 structural pass, 4 fail, 8 N/A; no new performance claim.

## Run boundary

No fresh dataset run until the outstanding scope clarification is answered. The
full repeat command remains in [CM recovery](CM_TOOL_FAILURE_RECOVERY.md); it must
use a fresh directory after this source change. No paid judge is authorized.
