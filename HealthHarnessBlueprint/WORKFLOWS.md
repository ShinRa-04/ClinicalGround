# How the hospital organization processes work

The three service blueprints below are proposed operating patterns. They do not redefine χ-Bench's statuses or require every listed step for every task. A job starts from the supplied instruction/current state, activates the necessary micro-responsibilities, and stops at the actual assigned terminal/exception condition.

## Provider PA desk

**Composite job:** A02, the provider PA owner. Relevant support includes registration/benefits, evidence/policy/coding capabilities, artifact operations and actual clinician/service interfaces.

| Phase | Patient/requester action | Visible evidence/interaction | Frontstage staff work | Backstage micro-responsibilities | Support and failure ownership |
| --- | --- | --- | --- | --- | --- |
| Understand assigned work | Existing service request or supplied case is the input | Task/request and current case record | Explain/clarify only what this task needs | PA-01 request interpretation; PA-02 identity; PA-03 coverage | SH-01/02/09 establish scope; PA owner retains unmatched/uncertain identity |
| Establish requirements | Supply allowed evidence/answers when requested | Actual benefits/requirements/policy observations | Route a specific clarification if needed | PA-04 requirement scout; PA-05 applicability; PA-06 evidence collection | Policy registry and records; no invented PA rule or clinical result |
| Build supported case | Actual source author may answer a gap | Evidence bundle and specific missing/conflicting items | Ask the appropriate question rather than filling it internally | PA-07 linking; PA-08 gaps; PA-09 clarification; PA-10 coding | SH-03/04 source ledger; original author remains source of clinical facts |
| Prepare and submit if assigned | Requester receives supported status | Packet/version and actual submission receipt | Submit through permitted operation and communicate observed status | PA-11 composer; PA-12 preflight; PA-13 operator | SH-05/06 preserve draft/final/submitted differences and unknown effects |
| Work actual response | Supply additional information or use permitted challenge route | Actual RFI/decision/peer correspondence | Respond to what the payer actually requested | PA-14 classifier; PA-15 RFI responder; PA-16 route coordinator | Provider owner tracks response obligations; no synthetic payer outcome |
| Handoff or close | Patient/receiver participates in any actual next step | Actual authorization/other disposition and handoff evidence | Coordinate only assigned downstream access work | PA-17 scheduling/access; PA-18 closure | Booking, performed service and payment remain separate observations |

**Illustrative internal work states:** scoped, evidence-pending, ready-for-permitted-action, submitted-observed, response-pending, action-required, assigned-work-complete, outcome-unknown or exception. These are our internal labels, not a verified simulator state machine.

A one-agent arrangement can perform several neighboring analysis responsibilities in one context. A delegated arrangement may separate policy selection, contradiction analysis and composition. Both must retain the same source/scope/receipt obligations. A task beginning at response handling should not resubmit merely because earlier micro-roles exist.

## Payer UM desk

**Composite job:** A03, with explicit A21 review and A22 reconsideration functions where assigned. The payer office is a distinct organizational principal; its conclusions are not controlled by a hospital coordinator's preferences.

| Phase | Provider/member interaction | Visible evidence/interaction | Frontstage staff work | Backstage micro-responsibilities | Support and failure ownership |
| --- | --- | --- | --- | --- | --- |
| Resolve intake | Actual request enters the supplied workspace | Received request, IDs and record status | Collect/clarify the actual intake needs | UM-01 intake; UM-02 product/benefits; UM-03 route/delegation | SH-01/09 identity/scope; valid administrative terminal routes remain possible |
| Establish governing evidence | Actual records/policy context are available or requested | Policy/version, chart facts, dated evidence | Request relevant missing information through permitted interface | UM-04 policy; UM-05 logic; UM-06 facts; UM-07 chronology | SH-03/04 preserve applicability, source and unknown dates |
| Perform appropriate initial review | Provider may answer a targeted question | Criteria assessment and actual additional-information status | Communicate scoped requests and next review stage | UM-08 matcher; UM-09 ambiguity; UM-10 information; UM-11 consultation | Review scope is assigned, not inferred from a persona name |
| Make the assigned determination | Authorized role contribution becomes part of the record | Actual decision/finalization evidence | Communicate the recorded result, not a new invented outcome | UM-12 authority checker; UM-13 determination | Actual task/operation envelope controls; case owner is continuity owner, not every signatory |
| Produce/deliver notice | Correct recipient receives applicable correspondence | Draft/final notice and observed delivery result | Deliver and preserve reason/outcome/recipient/version | UM-14 content mapper; UM-15 delivery/readback | SH-05/06; delivery failure or unknown remains explicit |
| Review if properly invoked | Actual appeal/challenge is submitted | Correct route/file and actual review response | Preserve standing, route and required independence facts | UM-16 appeal intake; UM-17 reconsideration | External review adapter observes actual eligible forum outcomes; no local critic creates them |
| Implement/close assigned work | Outcome creates actual effectuation/notice obligations | Observed implementation or pending/exception status | Track remaining responsibilities truthfully | UM-18 effectuation/closure | A favorable review is not automatically care delivered or payment complete |

The pinned benchmark architecture documents a failed-eligibility intake route without required clinical review; this illustrates why every case must not be forced through every reviewer. Actual task/tool contracts determine applicable steps. The prior legal/program examples remain scoped; they are not universal rules transplanted into the simulator. [B02](SOURCES.md#b02), [B04](SOURCES.md#b04).

## CM desk

**Composite job:** A04, with conversation/access support, targeted medication/psychosocial/discipline capabilities and actual receiving-service interfaces.

| Phase | Patient/representative action | Visible evidence/interaction | Frontstage staff work | Backstage micro-responsibilities | Support and failure ownership |
| --- | --- | --- | --- | --- | --- |
| Orient and establish contact scope | Actual participant/contact is supplied or reached | Current chart/task, speaker and representation facts | Use permitted contact and clarify authority/communication needs | CM-01 orienter; CM-02 scope; CM-03 outreach | SH-02/09 case boundary; contact is not assumed consent |
| Conduct required interaction | Person gives actual answers, questions, goals or refusal | Exact dialogue and unresolved questions | Ask relevant next questions without repetition or coercive assumption | CM-04 conversation; CM-05 extraction; CM-06 obligation tracking | Preserve actual sources through checkpoints; no internally generated patient reply |
| Understand needs/goals | Person states priorities/barriers | Attributed assessment/goal evidence | Clarify and route relevant professional/resource questions | CM-07 needs; CM-08 scope flags; CM-09 goals; CM-10 medication; CM-11 psychosocial | Discipline contributions remain scoped; missing evidence stays unknown |
| Compose the plan | Patient participates as the actual task permits | Versioned plan, responsibilities and unresolved items | Describe the agreed/proposed next work accurately | CM-12 dependencies; CM-13 care-plan composition | Plan is not a new treatment order or proof the service occurred |
| Coordinate services | Receiver/patient provides actual replies | Referral receipt, acceptance, scheduling or explicit unavailable status | Send permitted referrals and track response/access barriers | CM-14 operator; CM-15 acknowledgement; CM-16 access | SH-06 action journal; resource listing is not acceptance or delivery |
| Handoff, follow up and reconcile | Person/receiver supplies new actual information | Handoff, acknowledgements and current obligations | Preserve uncertainty and named ownership | CM-17 handoff; CM-18 follow-up; CM-19 new-information reconciliation | Sent is not understood/accepted; late helper results cannot overwrite newer evidence |
| Close the assigned episode | Actual appropriate outcome/refusal/exception is recorded | Task-required disposition and remaining next owners | State what is complete and what remains | CM-20 closure | A good conversation or plan alone does not prove downstream care completed |

## Handoffs across desks

Use correlation references to the actual patient/task/episode, applicable purpose and source version. Send the required work product and unresolved obligation, not every participant's private notes. A receiver acknowledges the task/artifact separately from making a substantive decision. AHRQ handoff guidance informs these proposed ownership checks; it does not prescribe our API or transfer professional credentials. [B06](SOURCES.md#b06).

The three desks are available organizational patterns. They are not a mandatory PA→UM→CM chain. If the environment assigns only provider work, our internal UM persona cannot supply the missing insurer decision. If it assigns a UM review, the actual task-authorized review function can be performed. The adapter is the boundary between work organization and observed external state.
