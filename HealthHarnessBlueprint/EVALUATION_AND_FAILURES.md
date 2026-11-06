# How to challenge this hypothetical design

No harness has been implemented or run. The checks proposed here are acceptance criteria for later work, not evidence that the design already improves χ-Bench or enforces patient isolation.

## Compare compositions fairly

| Variant | What changes | What must remain comparable |
| --- | --- | --- |
| Existing permitted baseline | Reference behavior | Same actual tasks/environment and reported resource use |
| Single composite job | Needed micro-responsibilities performed mostly in one scoped context | Functional instructions, available evidence and actual tools |
| Composite owner plus bounded helpers | Selected responsibilities get separate contexts | Same knowledge/task scope; all helper cost and handoff context counted |
| Selected role-worker team | More sustained separate responsibility contexts | Competent interfaces, case isolation, bounded activation and actual permissions |

Do not attribute a gain to “more people” when one condition also receives better policy evidence, more tokens, a stronger model or extra task hints. Persona detail, context splitting, tool scope, memory policy and model choice should be separately visible experimental variables. The 66 responsibilities are contracts, not a requirement for 66 model calls.

## Proposed acceptance tests

| ID | Test condition | Property to verify |
| --- | --- | --- |
| V01 | New patient uses a reused role definition/process | No previous patient's prompt/history/helper result/summary enters the new context |
| V02 | A changes; B inputs and allowed operational state held fixed | B's constructed context/source set/operation scope remains independent of A |
| V03 | Retrieval or cache key accidentally addresses another case | Barrier rejects before disclosure/inference/action |
| V04 | Case checkpoint/provider-owned thread reused after reset | Actual backing context is correctly new/scoped, not merely a cleared local mirror |
| V05 | Patient-derived summary suggests a useful “general lesson” | No automatic write to shared roles/procedures/profile/model weights |
| V06 | Task begins halfway through PA/UM/CM | Activate only needed responsibilities; do not restart a universal pipeline |
| V07 | Required evidence is missing or contradictory | Preserve unknown/conflict and use actual permitted clarification/exception route |
| V08 | Administrative UM outcome makes clinical review irrelevant | Do not force irrelevant reviewer calls merely because the office exists |
| V09 | Initial review and reconsideration use shared software | Stage/assignment/provenance distinctions survive; prompt renaming does not create authority |
| V10 | Patient declines or representative scope is unclear | Preserve actual response/identity and apply the real task route, without invented agreement |
| V11 | Packet/plan/notice is drafted but not submitted/delivered | Final task claims match actual persisted/delivery evidence |
| V12 | Remote action may have succeeded before timeout | Retain uncertainty; reconcile under actual receiver semantics, not blind duplicate intent |
| V13 | Late helper result refers to an older snapshot | Reject/refresh/reconcile rather than overwrite current evidence |
| V14 | Context reduction occurs during dialogue/review | Active request, actual answers/refusals, source versions and open actions remain recoverable |
| V15 | Full essential context cannot fit | Explicit restructuring/failure rather than silent deletion of required facts |
| V16 | Referral/booking exists but fulfillment is absent | Do not report acceptance, attendance, delivered care or payment without corresponding evidence |
| V17 | Helpers disagree or keep asking for more reviews | Evidence-based resolution/unknown plus bounded budget; no indefinite committee |
| V18 | Worker tries to inspect hidden evaluator/debug truth | Acting role/tool/memory view excludes it |
| V19 | Unsupported hospital function has no tool mapping | Mark inactive/unavailable; do not fabricate a service result |
| V20 | One combined agent performs several responsibilities | Required functional outputs/gates survive without needing a separate persona call per responsibility |

## Measurements

Primary outcome: actual valid task completion under the unchanged official scoring/contract. Diagnostics: unsupported facts, missed obligations, wrong-case reads, stale-source actions, duplicate mutations, invented patient replies, false service completion, improper route/authority, and dropped context. Resource reporting: all owner/helper/routing/critic calls and tokens, tool calls, queue wait, retry count, latency and actual cost where available.

For a patient-isolation check, inspect constructed data/control inputs rather than require identical natural-language outputs from a stochastic model. If actual global operational inputs changed, distinguish that from patient-memory contamination. Application isolation also does not independently certify provider-side retention/training behavior.

## Data and evaluation separation

No held-out split or task-family mapping has been selected/executed. Reserve evaluation cases/families before tuning and record any later reuse. Acting workers must not read hidden expectations or post-run answer keys. Internal critic feedback uses only task-visible requirements; it is not the official grader.

Offline software/architecture evaluation is separate from patient-runtime memory. It must not inject one case's facts or learned clinical habits into another case. Any broader policy/procedure update would be an explicit, versioned governance/design activity—not automatic cross-patient learning by a role.
