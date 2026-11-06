# Virtual organization, roles and jobs

“Virtual hospital” means an explicit operational organization, not a room full of unconstrained professional personas. Its purpose is to preserve realistic responsibility and information flow while letting us merge compatible work and test alternate organizations.

## Organizational zones

| Zone | Functions modeled | Primary control boundary |
| --- | --- | --- |
| Patient and support network | Patient, caregiver, representative, communication support | Separate identity, actual statements/preferences and representation scope |
| Hospital access/PA | Registration, benefits, referrals, evidence packet, submission, scheduling and access barriers | Requesting-provider task ownership and supported evidence |
| Hospital clinical services | Treating/referring/specialist/nursing contributions, diagnostics and medication/discipline interfaces | Specifically assigned authorship/operation scope and observable service evidence |
| Payer organization | Intake, benefits, initial review, specialty consultation, determination and notice | Separate institution, product/delegation and review-stage authority |
| Appeal/external review | Route/standing administration, reconsideration and eligible independent forums | Correct issue/route and any required independence; no invented local binding ruling |
| CM/transitions | Outreach, assessment, goals, shared plan, referrals, navigation and follow-up | Journey continuity plus discipline-specific contributions |
| Receiving/community services | Home/facility services, resources, transport, equipment and fulfillment | Acceptance/capacity/delivery are external observations, not coordinator wishes |
| Governance/infrastructure | Approved policy, assignment, quality, privacy, records, systems and metrics | Configuration/version/purpose boundaries; management is not global clinical override |

The payer is deliberately not a hospital subordinate. Nor are patient consent or external review decisions. The hospital's chart of managers is one graph; substantive decision precedence is several scoped graphs.

## What makes an actor unique?

An instance is keyed by identity, organization, assignment, case/episode and role—not just a profession string. Two clinicians can use the same template but have different evidence, authority and prior involvement. One employee may hold several compatible functions while the system retains which function authored each action. The composite hospice profile must be decomposed into its relevant group/RN/attending/certification/support functions before assigning work.

An actor profile contains declared expertise, purpose, accessible evidence, allowed operations, pending obligations, communication relationships and memory policy. It should not contain a fabricated biography that replaces actual task facts. Persona style can be an experiment, separate from functional correctness.

## Suggested initial execution shape

Use one active owner for the assigned PA, UM or CM episode, with explicit modes and a small on-demand capability set. Other logical modules can remain idle or be deterministic services. Instantiate a separate role context when the actual task requires a distinct function/view, when independent investigation is useful, or when tests reveal context interference.

For UM, keep initial review and reconsideration clearly identifiable even if software is shared. A fresh model context alone is not evidence of real institutional independence. In a benchmark-assigned simulated review, do the permitted function without inventing extra real-person approval steps; outside that simulation, no real licensure/compliance claim follows.

## Merging examples

- Provider registration/benefits/packet tracking can share a case owner if identity, coverage, authorization, scheduling and payment remain distinct.
- Care outreach/navigation/general education/follow-up can share a journey owner if speakers, refusals, clinical scope and service completion remain explicit.
- Payer intake/status/notice plumbing can share state; final decision and notice delivery must still have the actual authority and source/version relationship.
- Common referral, policy-retrieval or documentation code can serve different institutions through separate principals. Sharing code does not mean sharing every record or approving one another's decisions.

## Boundaries I would retain

Patient versus caregiver; provider request versus payer decision; initial determination versus applicable reconsideration; internal critic versus external adjudication; policy draft versus approved rule; referral/scheduling versus actual fulfillment; clinical record author versus evidence assembler; actor belief versus environment truth; and acting workspace versus hidden evaluation.

These are proposed software/model boundaries informed by the earlier scoped research, not an assertion that every hospital has this staffing chart. [Module catalogue](MODULE_CATALOG.md) defines all 29 logical modules, and [role coverage](ROLE_COVERAGE.md) maps every one of the 97 prior functional profiles. Neither count is a recommended number of simultaneous agents.
