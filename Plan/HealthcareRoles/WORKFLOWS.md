# Workflow dependencies, information and exception handling

[Role index](ROLE_INDEX.md) · [Handoff contracts](INFORMATION_FLOWS.md) · [Every-role interfaces](SERVICE_INTERFACES.md) · [Decision matrix](DECISIONS.md)

**Evidence status:** workflow sequences, dependency links, fields, exception ownership and primary-contact choices are **synthesized models; not confirmed actual institutional procedures**. Cited role descriptions and scoped rules informed them but do not directly prove every connection. See [evidence register](EVIDENCE_REGISTER.md).

## What the arrows mean

| Record/diagram type | Meaning | Does not imply |
| --- | --- | --- |
| DEP coordination dependency | A role may need information, context or service from another role when that pathway participates | Universal predecessor, mandatory approval, employment supervision |
| F information handoff | A named artifact/message moves between roles, with suggested fields, acknowledgement and failure route | A universally mandated form or identical procedure in every institution |
| S service interface | An illustrative request/response boundary for every role, showing a modeled primary contact and work product | Exclusive information source, observed local protocol or expanded authority |
| Reporting example | Described management/supervision within the named organization | Universal hierarchy or clinical override |
| Appeal review | A scoped process can review/reverse a prior determination if conditions are met | Ordinary managerial rank or an automatic right to every stage |

Dependencies and care coordination contain feedback cycles. A global acyclic "all people must act in this order" graph would misrepresent the work. The full network is for completeness; workflow and individual-neighborhood views are for reading.

## Provider authorization

1. **Clinical origin:** C01/C03/C04/C05 documents a supported request; the function must have actual professional permission. C02/O02 can supply referral context.
2. **Administrative preparation:** O03 verifies identifiers, O04 clarifies benefits/requirements, O06 supplies authentic records, and O01 assembles/submits. These functions can overlap in one employee.
3. **Payer exchange:** O01 receives a submission receipt and responds to information requests. Clinical gaps return to the clinician; staff do not invent evidence.
4. **Outcome:** The authorized determination and applicable notice are distinct from a provider status note. O05 coordinates scheduling and remaining prerequisites; booking is not clinical clearance or completed care.
5. **Dispute:** O10/O11/P04 use the actual correction, peer-discussion or appeal route. They preserve the distinction between procedural filing and clinical argument.

Key records: F01–F06, F12–F16. Views: [provider dependencies](graphs/provider-dependencies.svg), [provider information](graphs/provider-information.svg).

## Payer UM and appeals

1. **Intake:** U01 receives and routes the request. U02 resolves benefit/enrollment questions rather than inventing medical conclusions.
2. **Clinical review:** U03/U06/U07 applies only the permitted scope. R12/R13 provide example staged processes; D12 and D13 state the separate MA initial/reconsideration rules.
3. **Escalation:** U04 and U05 resolve the assigned clinical question. A consultation, review recommendation and authorized determination are separate work products.
4. **Notice:** U09 communicates the authorized record. U10/U11 explain or route status; their communication is not automatically a new determination.
5. **Review route:** U12 verifies the correct route/standing. In the scoped MA process, U13 and then U14 handle review as specified. U18 represents eligible commercial external review, not the MA ladder. J01–J03 are conditional later MA forums.
6. **Implementation:** A reversal is not the same event as authorization/service/payment implementation. A16 conditions remain applicable.

**Alternative and ambiguity:** the clinical-review stage is conditional, not a claim that every intake must receive nurse/physician review. R13 permits specified limited nonclinical approvals and assigned benefit decisions under delegation, while medical-necessity denials remain distinct. Its wider professional-category list and medical-director final-responsibility wording do not settle every actual signatory. R13 also explicitly retains appeals at the health plan rather than delegating AZPC appeal decisions. Eligible urgent commercial internal/external reviews can run concurrently (V19); applicable integrated MA routes require a route check before the standard ladder. See D11, D16 and the corrected review diagrams.

Key records: F07–F20, F42–F44. Views: [payer dependencies](graphs/payer-dependencies.svg), [payer/appeal information](graphs/payer-appeal-information.svg), [MA appeal hierarchy](graphs/ma-appeals.svg), [commercial review](graphs/commercial-appeals.svg).

## Care management and transitions

1. **Engagement/assessment:** P01/P02/P03 supply the relevant goals, supports and authority facts; M01 identifies needs and clinical ownership. P05/P06 provide access support as needed.
2. **Plan:** M01 coordinates a shared plan while clinical, psychosocial, medication and other professionals retain their own scope.
3. **Services:** Referrals may go to social work, pharmacy, navigation, rehabilitation, nutrition, respiratory care or community supports. Availability, patient wishes and actual professional permissions determine participation.
4. **Transitions:** M18 organizes information and service arrangements. A06 governs the cited hospital setting; A07 separately identifies home-health plan/order responsibilities. Receiving acceptance must be recorded, not assumed.
5. **Follow-through:** M01/M30 tracks service status and barriers. A failed appointment or unavailable resource returns to the appropriate owner; a task label should not silently become "patient received service."
6. **Change:** Clinical changes reach the responsible clinician, resource issues reach service/management owners, and privacy/representation questions reach the appropriate channel.

Key records: F21–F36. Views: [care dependencies](graphs/care-dependencies.svg), [care information](graphs/care-information.svg). Every supporting discipline also has a separate dossier and S interface.

**Hospice nuance:** this reference now separates interdisciplinary-group planning, designated RN coordination, attending functions, terminal-illness certification and admission recommendation. V11/V16/V17 establish the official October 2025 codification; a complete current-2026 amendment check and actual hospice assignments remain unconfirmed. A single attending or generic care coordinator cannot be assumed to own all these functions. See M28 and D33 for the scoped evidence and exceptions.

## Exception ownership

| Problem | Appropriate first owner | What must not be assumed |
| --- | --- | --- |
| Patient/case identity mismatch | Registration/HIM, with the relevant requester | That similar names justify merging records |
| Missing clinical support | Responsible clinician or evidence author | Administrative staff can create facts |
| Wrong or unclear benefit/product | Payer benefits/designated decision owner | Clinical recommendation alone changes plan benefits |
| Reviewer lacks permission/expertise | Appropriate professional review/UM leadership | Seniority substitutes for qualification |
| Same person involved in scoped MA reconsideration | Appeal operations to assign compliant reviewer | Higher title cures initial involvement |
| Patient disagrees/refuses | Patient and responsible clinical team; lawful representative process if relevant | Coverage approval or family preference is consent |
| Caregiver/appeal representative authority unclear | Appropriate representation/privacy/legal channel | Family or a generic signature grants unlimited authority |
| Communication access failure | Qualified access service and decision participants | Silence or translated text alone proves informed understanding |
| Record access/sharing uncertain | HIM/privacy with the actual purpose and material | Either all sharing is forbidden or all is unrestricted |
| Service not available/accepted | Referring coordinator and receiving service, with clinical input | A sent referral establishes capacity |
| Clinical change during coordination | Responsible clinical professional / actual urgent pathway | A coordinator should alter treatment without authority |
| Coverage dispute | Actual peer/correction/appeal pathway | Complaint and appeal are identical |
| Favorable review not implemented | Accountable plan/process owner and applicable escalation | A favorable letter proves delivery/payment |
| Technical failure | System/access support plus clinical/process owner | IT can change clinical facts or create approval |

These ownership suggestions synthesize role duties; they are not a substitute for the institution's emergency, safeguarding, reporting or legal procedures.

## Information provenance and least ambiguity

For each handoff, distinguish case identity, substantive author, version/date, status and recipient. Mark whether a document is a draft, request, recommendation, determination, notice or completed-service record. The exact legally required fields differ; the F contracts label their proposed modeling fields accordingly.

Do not forward every record to every role simply because the graph shows a connection. Determine purpose and appropriate information scope; A10's treatment exception does not remove other privacy protections. The information diagrams are conceptual role/artifact maps, not a system security architecture or a list of mandatory API calls.

## Benchmark boundary

The diagrams describe real-world functions using public sources and explicit operational synthesis. They do not assert all 97 roles are separately simulated, prescribe an agent architecture, or derive hidden verifier requirements. Mapping to the 75 public task instructions remains a separate unperformed study.
