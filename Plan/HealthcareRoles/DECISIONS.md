# Decision matrix

A decision is scoped to a domain and process. The actors column does not mean every listed actor has identical authority.

<a id="d01"></a>
## D01 — Who chooses whether to accept proposed treatment?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: Hospital patient participation/refusal and bounded representative authority are explicit. Separating consent from insurance/scheduling is a reasoned domain distinction.

**Domain:** consent

**Actors:** [P01 Patient / insured member](roles/P01.md), [P03 Legally recognized personal representative](roles/P03.md), [C01 Ordering / treating physician](roles/C01.md)

**Decision rule:** Patient participates and may request/refuse care; representative acts only under applicable authority.

**Does not establish:** Insurer approval, scheduling or management preference is not patient consent.

**Review/escalation:** Clarify understanding, capacity and lawful representative; use applicable clinical/legal process for disputes.

**Applicability:** Hospital rights under A01; capacity/minor/emergency and other exceptions require additional applicable law.

**Evidence:** [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13), [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html)

**Review reasoning:** Hospital patient participation/refusal and bounded representative authority are explicit. Separating consent from insurance/scheduling is a reasoned domain distinction.

**Other documented possibilities:** Direct patient decision or a legally appropriate representative; specific exceptions require the actual law/case.

**Complexity / unresolved facts:** No universal surrogate order, capacity finding or emergency-consent outcome is established.

**Captured supporting passage locations:**

- [A01](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13) — tool line 118; access: tool_excerpt. Passage anchor: `request or refuse treatment`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 65; access: tool_excerpt. Passage anchor: `scope`.

[Assertion review](verification/assertions/D01.md)

<a id="d02"></a>
## D02 — Who establishes representative authority?

**Evidence status:** SUPPORTED_CONDITIONAL: HHS defines healthcare representation and separately describes appointment for Medicare appeals.

**Domain:** representation

**Actors:** [P03 Legally recognized personal representative](roles/P03.md), [P04 Appointed appeal representative](roles/P04.md), [G10 Privacy officer / HIM privacy specialist](roles/G10.md), [G17 Legal adviser / specialist legal representative](roles/G17.md)

**Decision rule:** Recognize authority from applicable law/instrument/appointment and its actual scope, not family relationship alone.

**Does not establish:** Appeal appointment does not automatically authorize treatment decisions.

**Review/escalation:** Privacy/legal or applicable appointment process resolves uncertainty.

**Applicability:** Healthcare personal representation and appeal standing are separate determinations.

**Evidence:** [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html), [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html)

**Review reasoning:** HHS defines healthcare representation and separately describes appointment for Medicare appeals.

**Other documented possibilities:** Broad or limited healthcare authority; appointed appeal representative; statutory authority where applicable.

**Complexity / unresolved facts:** Two scopes can belong to the same person, but neither follows merely from family relationship or a generic signature.

**Captured supporting passage locations:**

- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 65; access: tool_excerpt. Passage anchor: `scope`.
- [R20](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html) — tool line 30; tool line 39; access: tool_excerpt. Passage anchor: `appointment`.

[Assertion review](verification/assertions/D02.md)

<a id="d03"></a>
## D03 — Who recommends/orders clinical treatment?

**Evidence status:** SUPPORTED_CONDITIONAL: Treating-professional functions and hospital order authentication are supported; profession/jurisdiction/privileges condition the permission.

**Domain:** treatment

**Actors:** [C01 Ordering / treating physician](roles/C01.md), [C03 Treating / performing specialist](roles/C03.md), [C04 Nurse practitioner](roles/C04.md), [C05 Physician assistant / associate (jurisdiction-specific title)](roles/C05.md)

**Decision rule:** Authorized treating practitioner makes clinical recommendations/orders within license and privileges.

**Does not establish:** Coordinator, coder, reviewer title or managerial rank alone does not confer prescribing authority.

**Review/escalation:** Clinical reassessment, appropriate consultation and applicable professional escalation.

**Applicability:** Profession/state/practice arrangement and patient consent must be established.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [B02: Physician assistants](https://www.bls.gov/ooh/healthcare/physician-assistants.htm), [B03: Advanced practice nurses](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

**Review reasoning:** Treating-professional functions and hospital order authentication are supported; profession/jurisdiction/privileges condition the permission.

**Other documented possibilities:** Physician, NP, PA or other allowed practitioner for a specific activity/setting.

**Complexity / unresolved facts:** Sources do not establish any actual individual license, privileges or authorization; no universal prescribing permission is certified.

**Captured supporting passage locations:**

- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 230; access: tool_excerpt. Passage anchor: `treatment plan`.
- [B03](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm) — tool line 221; access: tool_excerpt. Passage anchor: `scope of practice varies`.
- [A15](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24) — tool line 113; tool line 120; access: tool_excerpt. Passage anchor: `ordering practitioner`.

[Assertion review](verification/assertions/D03.md)

<a id="d04"></a>
## D04 — Does a treating specialist automatically outrank the PCP?

**Evidence status:** INTERPRETATION_WITH_SOURCE_CONTEXT: Sources describe different expertise and coordination. They do not establish a universal specialty-over-PCP command hierarchy.

**Domain:** treatment

**Actors:** [C02 Referring / primary-care clinician](roles/C02.md), [C03 Treating / performing specialist](roles/C03.md)

**Decision rule:** They contribute different expertise/responsibilities; identify the clinician responsible for the disputed service.

**Does not establish:** No universal organizational or clinical-superiority edge is inferred from specialty title.

**Review/escalation:** Reconcile recommendations with patient and responsible clinical team.

**Applicability:** Actual episode, privileges and local responsibility assignment determine signoff.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse)

**Review reasoning:** Sources describe different expertise and coordination. They do not establish a universal specialty-over-PCP command hierarchy.

**Other documented possibilities:** Responsibility can be assigned by episode, institution, admitting/attending arrangement and privileges.

**Complexity / unresolved facts:** No universal hierarchy is inferred; this is an evidence boundary, not proof that no institution can assign one.

**Captured supporting passage locations:**

- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 233; tool line 235; tool line 238; tool line 240; access: tool_excerpt. Passage anchor: `specialize`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 52; access: tool_excerpt. Passage anchor: `primary care physicians`.

[Assertion review](verification/assertions/D04.md)

<a id="d05"></a>
## D05 — Can an NP act independently?

**Evidence status:** SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES: The occupational summary and California regulator establish variation and multiple arrangements.

**Domain:** professional_scope

**Actors:** [C04 Nurse practitioner](roles/C04.md)

**Decision rule:** Activity depends on state scope, population focus and privileges/practice arrangement.

**Does not establish:** Neither universal physician supervision nor universal unrestricted independence is asserted.

**Review/escalation:** Check current governing rules and required professional support.

**Applicability:** State and actual activity must be specified.

**Evidence:** [B03: Advanced practice nurses](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page), [V02: California Board of Registered Nursing: AB 890 pathways](https://www.rn.ca.gov/practice/ab890.shtml)

**Review reasoning:** The occupational summary and California regulator establish variation and multiple arrangements.

**Other documented possibilities:** California traditional/103/104 pathways have different conditions; furnishing authority and employer requirements are additional issues.

**Complexity / unresolved facts:** The California page has prospective 104 availability wording that does not itself prove current individual certification or operational application availability.

**Captured supporting passage locations:**

- [B03](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm) — tool line 221; access: tool_excerpt. Passage anchor: `scope of practice varies`.
- [V02](https://www.rn.ca.gov/practice/ab890.shtml) — tool line 113; tool line 117; tool line 118; tool line 135; access: tool_excerpt. Passage anchor: `103 NP`.
- [V02](https://www.rn.ca.gov/practice/ab890.shtml) — tool line 207; access: tool_excerpt. Passage anchor: `furnishing authority`.

[Assertion review](verification/assertions/D05.md)

<a id="d06"></a>
## D06 — Who supervises PA practice?

**Evidence status:** SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES: Oregon explicitly describes collaborative practice and associate terminology, limiting broad national supervision summaries.

**Domain:** professional_scope

**Actors:** [C05 Physician assistant / associate (jurisdiction-specific title)](roles/C05.md), [C01 Ordering / treating physician](roles/C01.md)

**Decision rule:** Apply the actual state and practice requirements for collaboration/supervision.

**Does not establish:** Do not infer one national supervision arrangement or confuse PA with medical assistant.

**Review/escalation:** Responsible practice/medical leadership and governing scope rules.

**Applicability:** State, privileges and agreement are unresolved until identified.

**Evidence:** [B02: Physician assistants](https://www.bls.gov/ooh/healthcare/physician-assistants.htm), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [V03: Oregon Medical Board: PA collaborative practice](https://www.oregon.gov/omb/Topics-of-Interest/Pages/PA-Modernization-Bill.aspx)

**Review reasoning:** Oregon explicitly describes collaborative practice and associate terminology, limiting broad national supervision summaries.

**Other documented possibilities:** Different states/practice arrangements; physician or employer agreement as specified by Oregon.

**Complexity / unresolved facts:** National occupational text is not a state practice act; no universal supervision ratio or boss chain is established.

**Captured supporting passage locations:**

- [B02](https://www.bls.gov/ooh/healthcare/physician-assistants.htm) — tool line 236; tool line 274; access: tool_excerpt. Passage anchor: `collaboration`.
- [V03](https://www.oregon.gov/omb/Topics-of-Interest/Pages/PA-Modernization-Bill.aspx) — tool line 45; tool line 50; tool line 53; tool line 61; access: tool_excerpt. Passage anchor: `collaboration agreement`.

[Assertion review](verification/assertions/D06.md)

<a id="d07"></a>
## D07 — Can an RN delegate any assigned task?

**Evidence status:** SUPPORTED_PROFESSIONAL_FRAMEWORK: The decision framework checks legal prohibition, education/competence, policy and accountability. It is professional guidance, not itself every state law.

**Domain:** professional_scope

**Actors:** [C06 Registered nurse providing direct care](roles/C06.md), [C07 Licensed practical / vocational nurse](roles/C07.md), [C08 Medical assistant / clinical-support assistant](roles/C08.md), [M21 Home-health aide / personal-care worker](roles/M21.md)

**Decision rule:** Assignment/delegation must fit applicable law, competence, supervision and policy.

**Does not establish:** Manager instruction does not legalize a task beyond professional scope.

**Review/escalation:** Qualified nursing/professional supervisor and scope framework.

**Applicability:** No nationwide permission for a specific drug, IV task or assessment is assumed.

**Evidence:** [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page), [B04: Registered nurses](https://www.bls.gov/ooh/healthcare/registered-nurses.htm), [B05: Practical and vocational nurses](https://www.bls.gov/ooh/healthcare/licensed-practical-and-licensed-vocational-nurses.htm), [B06: Medical assistants](https://www.bls.gov/ooh/healthcare/medical-assistants.htm), [B19: Home health and personal care aides](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm), [V10: NCSBN scope decision framework](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf)

**Review reasoning:** The decision framework checks legal prohibition, education/competence, policy and accountability. It is professional guidance, not itself every state law.

**Other documented possibilities:** Assignment, delegation and supervision vary by activity/state/credential.

**Complexity / unresolved facts:** Specific task permission remains unresolved until the actual practice act and case facts are checked.

**Captured supporting passage locations:**

- [V10](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf) — tool line 62 / PDF page 3; access: tool_excerpt. Passage anchor: `prohibited`.
- [V10](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf) — tool line 9 / PDF page 1; tool line 75 / PDF page 3; access: tool_excerpt. Passage anchor: `competence`.
- [A14](https://ncsbn.org/policy/npa.page) — tool line 26; tool line 40; tool line 41; access: tool_excerpt. Passage anchor: `state`.

[Assertion review](verification/assertions/D07.md)

<a id="d08"></a>
## D08 — Who supplies the clinical facts in a request?

**Evidence status:** SUPPORTED_WITHIN_SETTING_PLUS_INTERPRETATION: Hospital authentication is explicit; coding/CDI sources support clarification rather than independently creating clinical facts.

**Domain:** documentation

**Actors:** [C01 Ordering / treating physician](roles/C01.md), [O06 HIM / release-of-information specialist](roles/O06.md), [O08 Clinical-documentation-integrity specialist](roles/O08.md), [O13 External diagnostic / clinical evidence author or custodian](roles/O13.md)

**Decision rule:** Responsible service author authenticates clinical content; custodians transfer and CDI requests clarification.

**Does not establish:** Administrative staff cannot invent a diagnosis or revise facts to match payer criteria.

**Review/escalation:** Query author and follow correction/authentication process.

**Applicability:** Hospital authentication requirement A15; other settings need their rules.

**Evidence:** [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html)

**Review reasoning:** Hospital authentication is explicit; coding/CDI sources support clarification rather than independently creating clinical facts.

**Other documented possibilities:** Responsible author and permitted countersign/correction arrangements depend on setting.

**Complexity / unresolved facts:** The hospital rule is not silently generalized to all clinics or used as a complete record-correction policy.

**Captured supporting passage locations:**

- [A15](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24) — tool line 112; tool line 113; tool line 120; access: tool_excerpt. Passage anchor: `authenticated`.
- [B20](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm) — tool line 228; access: tool_excerpt. Passage anchor: `clinical codes`.
- [R08](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html) — HTML p block 1; access: retrieved. Passage anchor: `documentation`.

[Assertion review](verification/assertions/D08.md)

<a id="d09"></a>
## D09 — Who selects supported administrative codes?

**Evidence status:** SUPPORTED_GENERAL_DESCRIPTION: The occupational description supports code assignment from clinical information; documentation/denial example supports collaboration.

**Domain:** coding

**Actors:** [O07 Medical coding specialist](roles/O07.md), [O08 Clinical-documentation-integrity specialist](roles/O08.md), [C01 Ordering / treating physician](roles/C01.md)

**Decision rule:** Coding specialist assigns supported codes; clinical ambiguity goes back to responsible author.

**Does not establish:** Code selection is not independent medical diagnosis or authorization.

**Review/escalation:** Clinician/CDI/HIM and claim-correction pathway.

**Applicability:** Code system, service and documentation must match actual context.

**Evidence:** [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

**Review reasoning:** The occupational description supports code assignment from clinical information; documentation/denial example supports collaboration.

**Other documented possibilities:** Pre-service clarification, coding, CDI and downstream claim correction can be separate work.

**Complexity / unresolved facts:** The exact coding standard/query process must be specified; coding alone is not clinical diagnosis or payer adjudication.

**Captured supporting passage locations:**

- [B20](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm) — tool line 228; access: tool_excerpt. Passage anchor: `assign clinical codes`.
- [R08](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html) — HTML p block 1; access: retrieved. Passage anchor: `coding`.

[Assertion review](verification/assertions/D09.md)

<a id="d10"></a>
## D10 — Is benefit verification the same as authorization?

**Evidence status:** SUPPORTED_SOURCE_EXAMPLES: The sources distinguish benefits, authorization and financial responsibility.

**Domain:** coverage

**Actors:** [O04 Provider insurance-verification / benefits specialist](roles/O04.md), [U02 Payer eligibility / benefit specialist](roles/U02.md), [O01 Provider authorization / precertification specialist](roles/O01.md)

**Decision rule:** Membership/benefit information and request authorization are distinct findings.

**Does not establish:** Eligibility, an estimate or a case number does not prove clinical approval or final payment.

**Review/escalation:** Payer benefit/UM contacts and appropriate dispute route.

**Applicability:** Plan and service determine required checks.

**Evidence:** [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf)

**Review reasoning:** The sources distinguish benefits, authorization and financial responsibility.

**Other documented possibilities:** Separate or combined staff can perform these checks; final claim/payment depends on its own applicable rules.

**Complexity / unresolved facts:** Do not infer final coverage or zero patient cost from eligibility, estimates or a case identifier.

**Captured supporting passage locations:**

- [R06](https://health.ucsd.edu/insurance-billing/paying/faq/) — HTML h3 block 68; access: retrieved. Passage anchor: `prior authorization`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `eligibility and benefits`.

[Assertion review](verification/assertions/D10.md)

<a id="d11"></a>
## D11 — Can first-level UM approve a request?

**Evidence status:** SUPPORTED_ORGANIZATION_EXAMPLES_WITH_CORRECTION: The program allows limited nonclinical approvals under explicit criteria as well as licensed review; the earlier clinical-only emphasis was incomplete.

**Domain:** coverage

**Actors:** [U01 Payer UM intake coordinator](roles/U01.md), [U02 Payer eligibility / benefit specialist](roles/U02.md), [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md), [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md), [U06 Payer behavioral-health reviewer](roles/U06.md), [U07 Managed-care pharmacist / pharmacy reviewer](roles/U07.md)

**Decision rule:** Published programs may permit limited nonclinical approvals under explicit criteria and assigned benefit decisions, alongside licensed clinical review and escalation; authority is delegation- and product-specific.

**Does not establish:** RN/pharmacist/reviewer title alone does not establish unlimited approval or denial authority.

**Review/escalation:** Escalate where criteria, evidence or authority are insufficient.

**Applicability:** R12/R13 are example programs; no universal program permission is inferred. R13 also states medical-director final responsibility and wider professional categories; exact case signoff needs clarification.

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

**Review reasoning:** The program allows limited nonclinical approvals under explicit criteria as well as licensed review; the earlier clinical-only emphasis was incomplete.

**Other documented possibilities:** Nonclinical limited approval, benefit-only decision, licensed approval, or clinical escalation depending on documented delegation.

**Complexity / unresolved facts:** R13 also describes medical-director final responsibility and broader professional categories; exact signing rights require program/product clarification.

**Captured supporting passage locations:**

- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical personnel may`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [R12](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx) — tool line 114 / PDF page 3; tool line 116 / PDF page 3; access: earlier_tool_excerpt. Passage anchor: `first-level`.

[Assertion review](verification/assertions/D11.md)

<a id="d12"></a>
## D12 — Who reviews anticipated adverse MA medical necessity?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: The retrieved section directly requires appropriate physician or other qualified professional review before the specified adverse MA medical-necessity determination.

**Domain:** coverage

**Actors:** [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md), [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md), [U05 Independent clinical / specialty consultant](roles/U05.md), [U06 Payer behavioral-health reviewer](roles/U06.md)

**Decision rule:** Before issuance, 422.566(d) requires a physician OR other appropriate licensed healthcare professional with relevant expertise and Medicare-criteria knowledge.

**Does not establish:** Do not replace this with a physician-only rule for every initial denial; do not use an unqualified clerk.

**Review/escalation:** Appropriate licensed expert review; subsequent applicable reconsideration.

**Applicability:** MA initial adverse medical necessity; integrated-plan exception in 422.566(a) and different decision types must be checked.

**Evidence:** [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

**Review reasoning:** The retrieved section directly requires appropriate physician or other qualified professional review before the specified adverse MA medical-necessity determination.

**Other documented possibilities:** Physician or another appropriate licensed expert; organization policy can set additional requirements.

**Complexity / unresolved facts:** Integrated-plan and decision-type conditions matter; the rule is not physician-only for every initial denial.

**Captured supporting passage locations:**

- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `expects to issue`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 140; access: tool_excerpt. Passage anchor: `unrestricted license`.

[Assertion review](verification/assertions/D12.md)

<a id="d13"></a>
## D13 — Who may reconsider an MA medical-necessity denial?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: Noninvolvement and physician expertise for the specified MA medical-necessity reconsideration are explicit.

**Domain:** appeal

**Actors:** [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md), [U12 Internal appeal / grievance coordinator](roles/U12.md)

**Decision rule:** Under 422.590(h), reconsiderers were not involved in the initial decision; medical-necessity reconsideration is made by an appropriately expert physician.

**Does not establish:** A more senior initial reviewer does not satisfy independence merely by rank.

**Review/escalation:** Remaining adverse MA issues proceed under independent-review requirements.

**Applicability:** Specified MA reconsideration route; not a universal rule for every product/dispute.

**Evidence:** [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590), [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592)

**Review reasoning:** Noninvolvement and physician expertise for the specified MA medical-necessity reconsideration are explicit.

**Other documented possibilities:** Reviewer need not always have identical specialty; other products/types have their own requirements.

**Complexity / unresolved facts:** Higher rank does not by itself establish independence or case eligibility.

**Captured supporting passage locations:**

- [A03](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590) — tool line 143; access: tool_excerpt. Passage anchor: `not involved`.
- [A03](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590) — tool line 144; access: tool_excerpt. Passage anchor: `made by a physician`.

[Assertion review](verification/assertions/D13.md)

<a id="d14"></a>
## D14 — Does peer-to-peer discussion replace appeal?

**Evidence status:** SUPPORTED_PROCESS_EXAMPLE_WITH_LIMITS: Payer material separately describes peer discussion and pre-service appeal. Deadline preservation is not established and is intentionally not assumed.

**Domain:** appeal

**Actors:** [O11 Provider physician adviser / peer-discussion clinician](roles/O11.md), [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md), [O10 Provider denial / appeal specialist](roles/O10.md)

**Decision rule:** Peer discussion exchanges clinical information under the plan process.

**Does not establish:** Do not assume it is an appeal, guarantees reversal, or preserves a filing deadline.

**Review/escalation:** Use actual formal route/notice for unresolved decision.

**Applicability:** Plan/state/service process determines relationship between discussion and appeal.

**Evidence:** [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html)

**Review reasoning:** Payer material separately describes peer discussion and pre-service appeal. Deadline preservation is not established and is intentionally not assumed.

**Other documented possibilities:** Peer discussion, formal appeal or another correction route under actual product/notice.

**Complexity / unresolved facts:** Retrieved deadline presentations differ. Do not select one as a universal rule or infer that discussion preserves filing rights.

**Captured supporting passage locations:**

- [R15](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html) — HTML p block 10; access: retrieved. Passage anchor: `discussion`.
- [R15](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html) — HTML p block 15; HTML p block 16; HTML p block 17; HTML h3 block 34; access: retrieved. Passage anchor: `pre-service appeal`.

[Assertion review](verification/assertions/D14.md)

<a id="d15"></a>
## D15 — Can MA independent review reverse payer review?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: Independent MA review and scoped reversal effectuation are explicit.

**Domain:** appeal

**Actors:** [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md), [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md), [U09 Determination / notification coordinator](roles/U09.md)

**Decision rule:** CMS-contracted independent entity resolves remaining disputed issues; reversal triggers scoped effectuation obligations.

**Does not establish:** Payer management is not free to disregard applicable independent reversal.

**Review/escalation:** Further eligible MA appeal level; document implementation.

**Applicability:** 422.592 and 422.618; deadlines and further appeal rights differ by decision type.

**Evidence:** [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618), [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview)

**Review reasoning:** Independent MA review and scoped reversal effectuation are explicit.

**Other documented possibilities:** Outcome may affirm, reverse, dismiss/remand where allowed; implementation depends on decision category and further-review conditions.

**Complexity / unresolved facts:** A favorable decision and actual authorization/provision/payment are distinct; no universal deadline is supplied.

**Captured supporting passage locations:**

- [A04](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592) — tool line 108; access: tool_excerpt. Passage anchor: `remain in dispute`.
- [A16](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618) — tool line 114; tool line 116; tool line 117; tool line 119; access: tool_excerpt. Passage anchor: `reversed in whole or in part`.

[Assertion review](verification/assertions/D15.md)

<a id="d16"></a>
## D16 — Can commercial independent review supersede insurer denial?

**Evidence status:** SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES: Guidance supports binding acceptance within its applicable external-review route and identifies product/process limits.

**Domain:** appeal

**Actors:** [U18 Applicable commercial independent-review organization reviewer](roles/U18.md), [U15 External-review administrator](roles/U15.md)

**Decision rule:** In the applicable external-review process described by HealthCare.gov, insurer must accept the external decision.

**Does not establish:** Do not apply commercial IRO route automatically to MA, every plan or every denial.

**Review/escalation:** Follow applicable state/federal process and actual notice.

**Applicability:** Determine product, eligibility, issue and route first. Check the applicable ACA/non-grandfathered context and actual external-review eligibility. Eligible urgent external review may be requested concurrently with internal appeal.

**Evidence:** [A12: Applicable commercial external review](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/), [R17: CMS: federal external review](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts), [V19: HealthCare.gov internal appeals and urgent concurrent review](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/)

**Review reasoning:** Guidance supports binding acceptance within its applicable external-review route and identifies product/process limits.

**Other documented possibilities:** State/federal qualifying routes; eligible urgent internal/external requests may run concurrently.

**Complexity / unresolved facts:** The prior simple linear diagram was incomplete for urgent cases. MA IRE and this external process must remain distinct.

**Captured supporting passage locations:**

- [A12](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/) — tool line 21; access: tool_excerpt. Passage anchor: `required by law to accept`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML p block 4; access: retrieved. Passage anchor: `non-grandfathered`.
- [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/) — tool line 28; tool line 54; access: tool_excerpt. Passage anchor: `same time`.

[Assertion review](verification/assertions/D16.md)

<a id="d17"></a>
## D17 — Are later MA appeal forums above the prior decision?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: The MA overview names successive levels, while the effectuation rule provides a Council-review exception.

**Domain:** appeal

**Actors:** [J01 MA administrative law judge / applicable adjudicator](roles/J01.md), [J02 Medicare Appeals Council reviewer](roles/J02.md), [J03 Federal district court in an eligible Medicare appeal](roles/J03.md)

**Decision rule:** CMS lists plan reconsideration, IRE, adjudication, Council and district-court review as successive appeal levels.

**Does not establish:** Diagram is not an automatic entitlement or claim that every later forum reviews every issue.

**Review/escalation:** Follow eligibility, jurisdiction, filing and notice requirements at each level.

**Applicability:** A16 includes a Council-review effectuation exception; further appeal can affect implementation.

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

**Review reasoning:** The MA overview names successive levels, while the effectuation rule provides a Council-review exception.

**Other documented possibilities:** Further appeal is conditional on actual standing/jurisdiction/filing; reversals can have implementation conditions.

**Complexity / unresolved facts:** This is not an employment ladder or a guarantee every case may reach every forum; no threshold amounts are invented.

**Captured supporting passage locations:**

- [A11](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview) — tool line 687; access: tool_excerpt. Passage anchor: `five successive levels`.
- [A16](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618) — tool line 121; access: tool_excerpt. Passage anchor: `Council review`.

[Assertion review](verification/assertions/D17.md)

<a id="d18"></a>
## D18 — Does coverage approval order the clinician to treat?

**Evidence status:** INTERPRETATION_OF_DISTINCT_AUTHORITIES: Different source provisions address participation, clinical care and benefits. The domain separation is a reasoned synthesis rather than one quoted universal hierarchy statute.

**Domain:** treatment_vs_coverage

**Actors:** [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md), [C01 Ordering / treating physician](roles/C01.md), [P01 Patient / insured member](roles/P01.md)

**Decision rule:** Coverage, professional treatment judgment and patient willingness are separate domains.

**Does not establish:** Coverage approval is not a treatment order or consent; clinical recommendation is not automatic benefit coverage.

**Review/escalation:** Resolve clinical questions with treating team and coverage disputes through review.

**Applicability:** Functional separation; actual service and rights still apply.

**Evidence:** [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566), [A17: MA coverage criteria](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101), [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm)

**Review reasoning:** Different source provisions address participation, clinical care and benefits. The domain separation is a reasoned synthesis rather than one quoted universal hierarchy statute.

**Other documented possibilities:** Clinical recommendations and coverage/consent outcomes may agree or conflict and require their own processes.

**Complexity / unresolved facts:** The reference does not decide a real individual case or eliminate any actual legal constraint.

**Captured supporting passage locations:**

- [A01](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13) — tool line 118; access: tool_excerpt. Passage anchor: `informed decisions`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 107; access: tool_excerpt. Passage anchor: `benefits an enrollee`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 230; access: tool_excerpt. Passage anchor: `treatment plan`.

[Assertion review](verification/assertions/D18.md)

<a id="d19"></a>
## D19 — Who approves MA utilization policy?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: The MA committee approval/documentation and criteria constraints are explicit.

**Domain:** policy

**Actors:** [G03 UM / medical-policy committee and specialty members](roles/G03.md), [G02 Payer medical director / clinical-program leader](roles/G02.md), [G08 Policy analyst / clinical regulatory adviser](roles/G08.md)

**Decision rule:** 422.137 requires UM committee review/approval of MA UM policies and documented decisions within governing criteria.

**Does not establish:** An analyst draft or CEO preference does not substitute for required policy governance.

**Review/escalation:** Committee/regulatory correction for criteria issues; separate appeal process for individual case.

**Applicability:** MA-specific committee requirements; other products need their own governance.

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A17: MA coverage criteria](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101)

**Review reasoning:** The MA committee approval/documentation and criteria constraints are explicit.

**Other documented possibilities:** Other products may use different governance; analyst drafting and institutional approval are different functions.

**Complexity / unresolved facts:** Policy approval does not itself adjudicate all individual case disputes.

**Captured supporting passage locations:**

- [A05](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137) — tool line 109; access: tool_excerpt. Passage anchor: `reviewed and approved`.
- [A05](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137) — tool line 140; access: tool_excerpt. Passage anchor: `Document in writing`.
- [A17](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101) — tool line 123; tool line 125; tool line 130; tool line 133; access: tool_excerpt. Passage anchor: `coverage criteria`.

[Assertion review](verification/assertions/D19.md)

<a id="d20"></a>
## D20 — Does policy committee rank supersede every case appeal?

**Evidence status:** INTERPRETATION_WITH_SCOPED_RULES: Sources assign different policy-governance and case-review functions. No committee command over the independent entity is evidenced.

**Domain:** policy_vs_case

**Actors:** [G03 UM / medical-policy committee and specialty members](roles/G03.md), [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md), [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md)

**Decision rule:** Policy approval and case adjudication are different functions.

**Does not establish:** Committee existence does not eliminate individual review or higher appeal rights.

**Review/escalation:** Separate systemic policy correction from case reconsideration.

**Applicability:** No committee-to-IRE command edge exists in this map.

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590), [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592)

**Review reasoning:** Sources assign different policy-governance and case-review functions. No committee command over the independent entity is evidenced.

**Other documented possibilities:** Systemic policy review and an individual appeal can both be pursued through their own authorized mechanisms.

**Complexity / unresolved facts:** The absence of a command edge is a conservative modeling choice, not a claim to have audited every possible internal organogram.

**Captured supporting passage locations:**

- [A05](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137) — tool line 108; tool line 109; tool line 121; tool line 128; access: tool_excerpt. Passage anchor: `policies and procedures`.
- [A04](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592) — tool line 108; tool line 109; access: tool_excerpt. Passage anchor: `independent, outside entity`.

[Assertion review](verification/assertions/D20.md)

<a id="d21"></a>
## D21 — Who owns the shared care-coordination plan?

**Evidence status:** SUPPORTED_PROGRAM_MODELS_NOT_UNIVERSAL_AUTHORITY: Published programs support coordinating plans with patient and other professionals, with different staffing.

**Domain:** coordination

**Actors:** [M01 Lead care manager / case manager](roles/M01.md), [P01 Patient / insured member](roles/P01.md), [C02 Referring / primary-care clinician](roles/C02.md)

**Decision rule:** Lead coordinator integrates needs, goals and assigned follow-up with patient and responsible professionals.

**Does not establish:** Coordination ownership alone does not grant authority to change clinical orders or benefit decisions.

**Review/escalation:** Send clinical changes to responsible clinician; resource gaps to service/management owner.

**Applicability:** Program-specific professional background and permissions.

**Evidence:** [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

**Review reasoning:** Published programs support coordinating plans with patient and other professionals, with different staffing.

**Other documented possibilities:** RN case management, NP/SW teams and mixed staff programs; underlying clinical authority stays credential-dependent.

**Complexity / unresolved facts:** Coordination ownership is not a verified national prescribing/coverage permission or a prevalence statement.

**Captured supporting passage locations:**

- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 41; access: tool_excerpt. Passage anchor: `proactive care plan`.
- [R24](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse) — HTML p block 5; access: retrieved. Passage anchor: `social worker/nurse practitioner`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 4, block 3; PDF page 14, block 1; access: retrieved. Passage anchor: `Nurse Case Manager`.

[Assertion review](verification/assertions/D21.md)

<a id="d22"></a>
## D22 — Who develops hospital discharge planning?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: The hospital provision explicitly allows development by or under RN, social worker or other qualified personnel.

**Domain:** transition

**Actors:** [M18 Discharge planner / transitions coordinator](roles/M18.md), [C06 Registered nurse providing direct care](roles/C06.md), [M02 Medical social worker (credential-dependent practice)](roles/M02.md)

**Decision rule:** 482.43(a)(5) permits development by or under an RN, social worker or other appropriately qualified personnel.

**Does not establish:** Do not impose RN-only staffing or treat a planner as sole medical discharge authority.

**Review/escalation:** Qualified plan supervision and responsible clinical team.

**Applicability:** Hospital discharge setting; patient goals/access and information transfer requirements also apply.

**Evidence:** [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43)

**Review reasoning:** The hospital provision explicitly allows development by or under RN, social worker or other qualified personnel.

**Other documented possibilities:** Several qualified staffing models, not RN-only planning.

**Complexity / unresolved facts:** Planning, medical readiness, patient participation and receiving-service availability remain distinct.

**Captured supporting passage locations:**

- [A06](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43) — tool line 110; access: tool_excerpt. Passage anchor: `appropriately qualified personnel`.

[Assertion review](verification/assertions/D22.md)

<a id="d23"></a>
## D23 — Who signs/changes the home-health medical plan?

**Evidence status:** SUPPORTED_WITHIN_SCOPE: The home-health provision distinguishes plan/signature, orders, permitted verbal orders and revisions.

**Domain:** home_health

**Actors:** [M19 Home-health intake / coordination clinician](roles/M19.md), [C01 Ordering / treating physician](roles/C01.md), [C04 Nurse practitioner](roles/C04.md), [C05 Physician assistant / associate (jurisdiction-specific title)](roles/C05.md)

**Decision rule:** 484.60 identifies physician/allowed-practitioner plan establishment/signature and scoped order/revision requirements.

**Does not establish:** Agency coordinator cannot freely rewrite medical orders; authorized signatory is setting-specific.

**Review/escalation:** Consult responsible physician/allowed practitioner for required additions/changes.

**Applicability:** Home-health setting; state law and agency policy apply to verbal orders and allowed activities.

**Evidence:** [A07: Home-health plan and coordination](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60)

**Review reasoning:** The home-health provision distinguishes plan/signature, orders, permitted verbal orders and revisions.

**Other documented possibilities:** Physician/allowed practitioner within applicable scope; agency coordination and clinical signatures are different roles.

**Complexity / unresolved facts:** Do not transplant hospice certification or another setting's signatory rules into home health.

**Captured supporting passage locations:**

- [A07](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60) — tool line 106; access: tool_excerpt. Passage anchor: `signed by`.
- [A07](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60) — tool line 107; access: tool_excerpt. Passage anchor: `consulted to approve`.
- [A07](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60) — tool line 140; tool line 147; tool line 148; tool line 149; access: tool_excerpt. Passage anchor: `Verbal orders`.

[Assertion review](verification/assertions/D23.md)

<a id="d24"></a>
## D24 — Does referral acceptance mean the service happened?

**Evidence status:** OPERATIONAL_MODEL_NOT_EMPIRICAL_ASSERTION: Separating sent/accepted/scheduled/completed states is a proposed control informed by coordination needs, not a verified universal state machine.

**Domain:** service_completion

**Actors:** [M01 Lead care manager / case manager](roles/M01.md), [M18 Discharge planner / transitions coordinator](roles/M18.md), [M19 Home-health intake / coordination clinician](roles/M19.md), [M20 Skilled-nursing / rehabilitation receiving-team coordinator](roles/M20.md), [O05 Scheduler / procedure coordinator](roles/O05.md)

**Decision rule:** Referral sent, accepted, scheduled and completed are different events.

**Does not establish:** Do not close unmet need solely because a document or booking exists.

**Review/escalation:** Confirm relevant receiving-service status and return unresolved barriers to coordinator.

**Applicability:** Operational synthesis supporting closed-loop coordination, not a universal mandated form.

**Evidence:** [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43)

**Review reasoning:** Separating sent/accepted/scheduled/completed states is a proposed control informed by coordination needs, not a verified universal state machine.

**Other documented possibilities:** Organizations use different status fields, acknowledgements and closure criteria.

**Complexity / unresolved facts:** The model cannot prove delivery or clinical benefit; actual evidence must be obtained in its local workflow.

**Captured supporting passage locations:**

- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 42; access: tool_excerpt. Passage anchor: `Monitoring and followup`.
- [R28](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html) — tool line 50; access: tool_excerpt. Passage anchor: `track`.

[Assertion review](verification/assertions/D24.md)

<a id="d25"></a>
## D25 — Can a technician change medication therapy?

**Evidence status:** SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES: Professional task separation is supported; Washington illustrates separately authorized pharmacist therapy decisions.

**Domain:** medication

**Actors:** [M05 Pharmacy technician / medication-access coordinator](roles/M05.md), [M04 Clinical / community pharmacist](roles/M04.md), [C01 Ordering / treating physician](roles/C01.md)

**Decision rule:** Technician processes permitted tasks; pharmacist/prescriber provides the relevant professional judgment.

**Does not establish:** No independent therapy-change authority follows from medication-access assignment.

**Review/escalation:** Pharmacist then prescriber or authorized protocol as relevant.

**Applicability:** Specific technician, pharmacist and prescribing permissions remain state/program-specific.

**Evidence:** [B07: Pharmacists](https://www.bls.gov/ooh/healthcare/pharmacists.htm), [B08: Pharmacy technicians](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm), [R09: ASHP: specialty-pharmacy technicians](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles), [V13: Washington pharmacist collaborative drug therapy agreement rule](https://app.leg.wa.gov/WAC/default.aspx?cite=246-945-350)

**Review reasoning:** Professional task separation is supported; Washington illustrates separately authorized pharmacist therapy decisions.

**Other documented possibilities:** Technician support, pharmacist professional decision and prescriber/protocol actions differ.

**Complexity / unresolved facts:** Not every pharmacist change requires a new individual physician instruction; no general independent technician therapy authority follows from title.

**Captured supporting passage locations:**

- [B08](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm) — tool line 234; access: tool_excerpt. Passage anchor: `under the supervision`.
- [B07](https://www.bls.gov/ooh/healthcare/pharmacists.htm) — tool line 232; tool line 274; tool line 423; access: tool_excerpt. Passage anchor: `Supervise`.
- [V13](https://app.leg.wa.gov/WAC/default.aspx?cite=246-945-350) — tool line 145; access: tool_excerpt. Passage anchor: `therapeutic decisions`.

[Assertion review](verification/assertions/D25.md)

<a id="d26"></a>
## D26 — Does psychologist/counselor title imply prescribing?

**Evidence status:** SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES: New Mexico provides a concrete additional certification route, while general clinical psychology duties are separately described.

**Domain:** behavioral

**Actors:** [M06 Treating psychiatrist](roles/M06.md), [M07 Clinical psychologist](roles/M07.md), [M08 Licensed behavioral-health / substance-use counselor](roles/M08.md)

**Decision rule:** Use actual license and separately granted permissions.

**Does not establish:** Neither all psychologists prescribe nor a blanket national prohibition is inferred; counselor and psychiatrist roles differ.

**Review/escalation:** Qualified prescribing clinician for medication need.

**Applicability:** Jurisdiction and specialty qualification required.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [B10: Psychologists](https://www.bls.gov/ooh/life-physical-and-social-science/psychologists.htm), [B11: Behavioral and substance-use counselors](https://www.bls.gov/ooh/community-and-social-service/substance-abuse-behavioral-disorder-and-mental-health-counselors.htm), [V04: New Mexico psychology licensing and prescribing certificates](https://www.rld.nm.gov/boards-and-commissions/individual-boards-and-commissions/psychologist-examiners/licensing-registration-and-renewal/)

**Review reasoning:** New Mexico provides a concrete additional certification route, while general clinical psychology duties are separately described.

**Other documented possibilities:** Ordinary psychology license and additional conditional/full prescribing qualification are distinct.

**Complexity / unresolved facts:** No universal psychologist prescribing rule or verified permission for an individual is established.

**Captured supporting passage locations:**

- [B10](https://www.bls.gov/ooh/life-physical-and-social-science/psychologists.htm) — tool line 238; tool line 239; tool line 240; tool line 253; access: tool_excerpt. Passage anchor: `Clinical and counseling`.
- [V04](https://www.rld.nm.gov/boards-and-commissions/individual-boards-and-commissions/psychologist-examiners/licensing-registration-and-renewal/) — tool line 380; access: tool_excerpt. Passage anchor: `Prescription Certificate`.

[Assertion review](verification/assertions/D26.md)

<a id="d27"></a>
## D27 — Who can approve information sharing?

**Evidence status:** SUPPORTED_CONDITIONAL_WITH_COMPLEXITY: HIPAA minimum-necessary exceptions, representative authority and specific Part 2 protections show that information-sharing permission depends on more than a treatment label.

**Domain:** privacy

**Actors:** [G10 Privacy officer / HIM privacy specialist](roles/G10.md), [O06 HIM / release-of-information specialist](roles/O06.md), [P03 Legally recognized personal representative](roles/P03.md)

**Decision rule:** Use purpose, applicable rule/authority and scope; privacy/HIM process resolves uncertain releases.

**Does not establish:** No blanket all-sharing-needs-written-consent rule; no unrestricted access merely from treating or administrative title.

**Review/escalation:** Privacy/legal channel for unclear authorization or specially protected data.

**Applicability:** A10 lists minimum-necessary exceptions including specified treatment disclosures; other protections still apply. Applicable Part 2 records and separate SUD counseling notes illustrate additional consent distinctions; a HIPAA minimum-necessary exception is not blanket disclosure permission.

**Evidence:** [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes), [V15: HHS 42 CFR Part 2 final rule and consent distinctions](https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html)

**Review reasoning:** HIPAA minimum-necessary exceptions, representative authority and specific Part 2 protections show that information-sharing permission depends on more than a treatment label.

**Other documented possibilities:** Different purposes, record regimes and consent/exception pathways; applicable Part 2 TPO consent differs from special counseling notes.

**Complexity / unresolved facts:** The treatment exception is not an unrestricted all-records disclosure rule. No patient/program-specific legal determination is made.

**Captured supporting passage locations:**

- [A10](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html) — tool line 61; tool line 73; access: tool_excerpt. Passage anchor: `treatment purposes`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 65; access: tool_excerpt. Passage anchor: `scope`.
- [V15](https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html) — tool line 82; tool line 100; access: tool_excerpt. Passage anchor: `specific consent`.

[Assertion review](verification/assertions/D27.md)

<a id="d28"></a>
## D28 — Can interpreter or navigator decide for the patient?

**Evidence status:** INTERPRETATION_WITH_PROFESSIONAL_CONTEXT: Communication/navigation functions are documented; no medical/coverage/proxy power is inferred merely from performing them.

**Domain:** communication

**Actors:** [P05 Healthcare interpreter / communication-access professional](roles/P05.md), [P06 Healthcare translator](roles/P06.md), [M09 Community health worker](roles/M09.md), [M10 Patient navigator](roles/M10.md)

**Decision rule:** Communication/navigation functions support understanding and access.

**Does not establish:** No substitute medical/coverage/consent authority follows from those functions.

**Review/escalation:** Return substantive decision to patient/qualified role.

**Applicability:** Additional independent license/appointment, if any, must be established separately.

**Evidence:** [B23: Interpreters and translators](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm), [R21: HHS: telehealth communication access](https://www.hhs.gov/civil-rights/for-individuals/disability/guidance-on-nondiscrimination-in-telehealth/index.html), [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html)

**Review reasoning:** Communication/navigation functions are documented; no medical/coverage/proxy power is inferred merely from performing them.

**Other documented possibilities:** One person may hold additional independent qualifications or appointment, which must be established separately.

**Complexity / unresolved facts:** The role boundary is not proof that an interpreter/navigator can never have another legitimate authority.

**Captured supporting passage locations:**

- [B23](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm) — tool line 230; access: tool_excerpt. Passage anchor: `Render spoken messages`.
- [R28](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html) — tool line 37; tool line 49; tool line 54; tool line 56; access: tool_excerpt. Passage anchor: `navigator`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 65; tool line 66; tool line 67; tool line 69; access: tool_excerpt. Passage anchor: `authority`.

[Assertion review](verification/assertions/D28.md)

<a id="d29"></a>
## D29 — Can a manager overrule a licensed professional on any task?

**Evidence status:** SUPPORTED_FRAMEWORK_AND_SCOPED_BOUNDARY: Management, practice-scope guidance and reconsideration independence are separately evidenced.

**Domain:** management

**Actors:** [O12 Practice / patient-access supervisor](roles/O12.md), [U17 UM manager / operational supervisor](roles/U17.md), [G04 Care-management director / manager](roles/G04.md), [G05 Clinical / case-management supervisor](roles/G05.md)

**Decision rule:** Management may assign work within organizational mandate and lawful scope.

**Does not establish:** Reporting rank does not expand licensure or satisfy required review independence.

**Review/escalation:** Professional, compliance or appropriate appeal process rather than blind upward approval.

**Applicability:** Actual organogram and professional/practice rules required.

**Evidence:** [B22: Medical and health services managers](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

**Review reasoning:** Management, practice-scope guidance and reconsideration independence are separately evidenced.

**Other documented possibilities:** Administrative reporting, professional supervision and statutory case review can follow different chains.

**Complexity / unresolved facts:** A local organogram is not supplied; no universal authority ordering between licenses or job titles is certified.

**Captured supporting passage locations:**

- [B22](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `supervise staff`.
- [V10](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf) — tool line 62 / PDF page 3; access: tool_excerpt. Passage anchor: `prohibited`.
- [A03](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590) — tool line 143; access: tool_excerpt. Passage anchor: `not involved`.

[Assertion review](verification/assertions/D29.md)

<a id="d30"></a>
## D30 — Does an EHR administrator have clinical editing authority?

**Evidence status:** SUPPORTED_CONTEXT_WITH_LOCAL_PERMISSION_UNKNOWN: IT permissions, healthcare access-purpose controls and hospital authentication are documented in their settings.

**Domain:** systems

**Actors:** [G13 EHR / clinical informatics / application-support professional](roles/G13.md), [G14 Identity / portal-access administrator](roles/G14.md), [C01 Ordering / treating physician](roles/C01.md)

**Decision rule:** Technical changes/access require authorized purpose and change permissions.

**Does not establish:** Technical ability is not permission to fabricate clinical content or approve care.

**Review/escalation:** Clinical/policy author for substantive change; privacy/security for access.

**Applicability:** Hospital authentication A15 and applicable access controls.

**Evidence:** [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm)

**Review reasoning:** IT permissions, healthcare access-purpose controls and hospital authentication are documented in their settings.

**Other documented possibilities:** Technical administration can be assigned separately from clinical/policy authorship.

**Complexity / unresolved facts:** Actual system access is not proof of permission to alter clinical facts; exact change-control process remains local.

**Captured supporting passage locations:**

- [V08](https://www.bls.gov/ooh/computer-and-information-technology/network-and-computer-systems-administrators.htm) — tool line 231; access: tool_excerpt. Passage anchor: `permissions`.
- [A10](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html) — tool line 70; access: tool_excerpt. Passage anchor: `persons or classes`.
- [A15](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24) — tool line 112; tool line 113; tool line 120; access: tool_excerpt. Passage anchor: `authenticated`.

[Assertion review](verification/assertions/D30.md)

<a id="d31"></a>
## D31 — Who decides equipment or transport suitability?

**Evidence status:** SERVICE_MODEL_WITH_SCOPED_SOURCE_CONTEXT: Equipment and Medicaid transport sources establish service-specific responsibilities; a general suitability workflow is a model.

**Domain:** service

**Actors:** [M25 Equipment supplier / delivery or fitting staff](roles/M25.md), [M23 Transportation coordinator / dispatcher](roles/M23.md), [M24 Transport driver / service-delivery worker](roles/M24.md), [C01 Ordering / treating physician](roles/C01.md)

**Decision rule:** Service staff coordinate fulfillment; qualified clinical input handles medical requirements.

**Does not establish:** Driver, dispatcher or delivery title does not establish clinical assessment authority.

**Review/escalation:** Ordering/responsible clinician and actual qualified service staff.

**Applicability:** Exact equipment/transport protocol not established universally; CMS device example is service-specific.

**Evidence:** [R11: CMS: power mobility devices](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices), [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

**Review reasoning:** Equipment and Medicaid transport sources establish service-specific responsibilities; a general suitability workflow is a model.

**Other documented possibilities:** Different equipment, transport administration, vehicle and attendant arrangements.

**Complexity / unresolved facts:** A generic driver/dispatcher/delivery title does not establish clinical qualification; actual orders/protocols are not provided.

**Captured supporting passage locations:**

- [R11](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices) — HTML li block 6; HTML h3 block 111; HTML h3 block 146; access: retrieved. Passage anchor: `Standard Written Order`.
- [V14](https://www.medicaid.gov/sites/default/files/2023-09/smd23006.pdf) — tool line 5 / PDF page 1; tool line 6 / PDF page 1; tool line 11 / PDF page 1; tool line 12 / PDF page 1; access: tool_excerpt. Passage anchor: `transportation`.

[Assertion review](verification/assertions/D31.md)

<a id="d32"></a>
## D32 — Who approves financial assistance or final payment?

**Evidence status:** SUPPORTED_CONTEXT_NOT_PROGRAM_SIGNOFF: Cost and assistance support are documented, but the actual administrator's approval authority depends on the named program.

**Domain:** finance

**Actors:** [O09 Financial counselor / assistance specialist](roles/O09.md), [G15 Billing / patient accounts / claim-denial worker](roles/G15.md), [O04 Provider insurance-verification / benefits specialist](roles/O04.md)

**Decision rule:** Actual assistance administrator/payer adjudication decides under its program; counselors explain and help applications.

**Does not establish:** Counseling, eligibility and authorization do not guarantee final payment.

**Review/escalation:** Appropriate assistance/payment-dispute route.

**Applicability:** Program and claim rules must be identified.

**Evidence:** [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html), [R09: ASHP: specialty-pharmacy technicians](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles)

**Review reasoning:** Cost and assistance support are documented, but the actual administrator's approval authority depends on the named program.

**Other documented possibilities:** Counseling, assistance decisions, claims and coverage are separate, possibly held by different organizations.

**Complexity / unresolved facts:** No assistance eligibility outcome, final payment guarantee or universal financial-decision hierarchy is established.

**Captured supporting passage locations:**

- [R06](https://health.ucsd.edu/insurance-billing/paying/faq/) — HTML p block 69; HTML p block 98; access: retrieved. Passage anchor: `financial responsibility`.
- [R09](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles) — tool line 57; tool line 59; tool line 64; tool line 75; access: earlier_tool_excerpt. Passage anchor: `assistance`.

[Assertion review](verification/assertions/D32.md)

<a id="d33"></a>
## D33 — Does hospice team composition create one boss over every profession?

**Evidence status:** SUPPORTED_DATED_RULES_WITH_ADDED_DISTINCTIONS: Official October 2025 codification strengthens the earlier limited composition snapshot and separates IDG coordination, attending, certification and admission.

**Domain:** hospice

**Actors:** [M28 Hospice interdisciplinary group and attending functions (distinct roles)](roles/M28.md), [C01 Ordering / treating physician](roles/C01.md), [C06 Registered nurse providing direct care](roles/C06.md), [M03 Licensed clinical social worker](roles/M03.md), [M29 Chaplain / spiritual-care professional](roles/M29.md)

**Decision rule:** The official October 2025 hospice codification distinguishes the interdisciplinary group/designated RN coordination from attending, physician certification and admission responsibilities.

**Does not establish:** Team label is not identical authority for every member or proof of current complete regulation.

**Review/escalation:** Identify current hospice/attending responsibilities and relevant professional lead.

**Applicability:** V11/V16/V17 establish that codified edition; a complete current-2026 update audit and actual hospice assignment are not established.

**Evidence:** [A08: Hospice interdisciplinary team](https://www.cms.gov/files/document/r222soma.pdf), [R34: Medicare: hospice benefits](https://www.medicare.gov/publications/02154-medicare-hospice-benefits.pdf), [V11: Official 2025 CFR hospice care planning snapshot](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf), [V16: Official 2025 hospice certification rules](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-22.pdf), [V17: Official 2025 hospice admission rules](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-25.pdf)

**Review reasoning:** Official October 2025 codification strengthens the earlier limited composition snapshot and separates IDG coordination, attending, certification and admission.

**Other documented possibilities:** Designated RN coordination; specified physicians certify/admit within the codified rules; attending may be a different allowed professional.

**Complexity / unresolved facts:** These are distinct decisions and a group is not one professional. A complete current-2026 regulatory update audit is not claimed from the dated codification.

**Captured supporting passage locations:**

- [V11](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `designate a registered nurse`.
- [V16](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-22.pdf) — PDF page 2, block 1; access: retrieved. Passage anchor: `Sources of certification`.
- [V17](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-25.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `Admission to hospice`.

[Assertion review](verification/assertions/D33.md)

<a id="d34"></a>
## D34 — Does a complaint to a regulator automatically reverse coverage?

**Evidence status:** SUPPORTED_CONTEXT_WITH_MANDATE_LIMITS: Sources describe different assistance, complaint and appeal pathways; routing depends on the actual issue.

**Domain:** oversight

**Actors:** [G16 Regulator / oversight official](roles/G16.md), [P07 Patient-relations advocate](roles/P07.md), [U16 SHIP / consumer-assistance / ombudsman counselor](roles/U16.md)

**Decision rule:** Oversight, consumer assistance and case appeal have distinct mandates.

**Does not establish:** A complaint is not automatically an appeal or a reversal.

**Review/escalation:** Identify the agency and correct clinical/coverage/rights forum.

**Applicability:** Agency jurisdiction and program rules determine action.

**Evidence:** [R35: Medicare: help with rights and protections](https://www.medicare.gov/basics/your-medicare-rights/get-help-with-your-rights-protections), [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A12: Applicable commercial external review](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/)

**Review reasoning:** Sources describe different assistance, complaint and appeal pathways; routing depends on the actual issue.

**Other documented possibilities:** Insurer appeal, public counseling, quality complaint or oversight mechanism as applicable.

**Complexity / unresolved facts:** A complaint does not automatically establish an appeal, jurisdiction or reversal; the exact agency mandate remains case-specific.

**Captured supporting passage locations:**

- [R35](https://www.medicare.gov/basics/your-medicare-rights/get-help-with-your-rights-protections) — HTML p block 8; HTML li block 13; HTML p block 18; HTML li block 20; access: retrieved. Passage anchor: `complaint`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML h1 block 2; HTML p block 4; HTML li block 7; HTML p block 8; access: retrieved. Passage anchor: `external review`.
- [A11](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview) — tool line 119; tool line 138; tool line 373; tool line 679; access: tool_excerpt. Passage anchor: `appeal`.

[Assertion review](verification/assertions/D34.md)
