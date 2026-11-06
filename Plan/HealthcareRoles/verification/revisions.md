# Reviewed revision delta

157 current narrative/graph units reconciled: 132 unchanged and 25 revised/added, zero pending dispositions. These overlap the original inventory; they are not all additional independent findings.

[Machine-readable revision review](current_revision_review.json) · [Original assertion audit](README.md)

## CURRENT:002 — AUTHORITY

**Evidence status:** this framework and its scoped examples have explicit dispositions in the [defined assertion review](README.md). It remains an interpretation of separate authorities, not independent legal certification. Actual local authority and unprovided exceptions remain unconfirmed. See [evidence limits](../EVIDENCE_REGISTER.md) and [corrections](../FINDINGS.md).

**Verdict:** DOCUMENTATION_SCOPE

**Reason:** Coverage metadata, not expanded legal authority.


## CURRENT:016 — AUTHORITY

The pathway need not be strictly sequential. HealthCare.gov describes eligible urgent external review requested at the same time as internal appeal, without completing all internal steps. Check the applicable plan, issue and external-review eligibility; the CMS overview specifically describes the applicable ACA/non-grandfathered context. [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/), [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts)

**Verdict:** SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES

**Reason:** V19 permits concurrent eligible urgent review; R17 limits plan/process scope.

- [A12](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/) — tool line 21; access: tool_excerpt. Passage anchor: `required by law to accept`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML p block 4; access: retrieved. Passage anchor: `non-grandfathered`.
- [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/) — tool line 28; tool line 54; access: tool_excerpt. Passage anchor: `same time`.

## CURRENT:019 — AUTHORITY

R32 describes associate-director direction of managers and supervisors, and manager/supervisor collaboration in oversight. The graph now distinguishes that collaboration with a dashed edge; it does not invent a manager-to-supervisor direct reporting chain. In the AZPC program example, limited delegated nonclinical approvals/benefit-only decisions coexist with licensed review. R13 also contains wider professional categories alongside medical-director final-responsibility language; exact case signoff remains ambiguous without further delegation/product clarification. That ambiguity does not authorize nonclinical medical-necessity denials. See D11 and U01–U08.

**Verdict:** SUPPORTED_EXAMPLE_WITH_UNRESOLVED_SIGNOFF

**Reason:** Reporting and collaboration are distinct; R13 signoff remains unresolved.

- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 12, block 7; PDF page 13, block 1; access: retrieved. Passage anchor: `Director of Care Coordination`.
- [B22](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `supervise staff`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Supervisor of Case Management`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Non-Clinical Supervisor`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical staff are responsible`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 5; PDF page 20, block 3; access: retrieved. Passage anchor: `not delegated for processing`.
- [R14](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518) — HTML p block 11; HTML li block 28; HTML li block 34; access: retrieved. Passage anchor: `delegation`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical personnel may`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [R12](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx) — tool line 114 / PDF page 3; tool line 116 / PDF page 3; access: earlier_tool_excerpt. Passage anchor: `first-level`.

## CURRENT:023 — AUTHORITY

Applicable Part 2 records add further distinctions: the HHS fact sheet describes a future treatment/payment/operations consent option and separate consent treatment for specified SUD counseling notes. The minimum-necessary exception alone therefore cannot settle every sharing decision. [V15](https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html)

**Verdict:** SUPPORTED_PRIVACY_COMPLEXITY

**Reason:** V15 additional consent distinctions; no blanket permission is inferred.

- [A10](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html) — tool line 61; tool line 73; access: tool_excerpt. Passage anchor: `treatment purposes`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 65; access: tool_excerpt. Passage anchor: `scope`.
- [V15](https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html) — tool line 82; tool line 100; access: tool_excerpt. Passage anchor: `specific consent`.

## CURRENT:034 — WORKFLOWS

**Alternative and ambiguity:** the clinical-review stage is conditional, not a claim that every intake must receive nurse/physician review. R13 permits specified limited nonclinical approvals and assigned benefit decisions under delegation, while medical-necessity denials remain distinct. Its wider professional-category list and medical-director final-responsibility wording do not settle every actual signatory. R13 also explicitly retains appeals at the health plan rather than delegating AZPC appeal decisions. Eligible urgent commercial internal/external reviews can run concurrently (V19); applicable integrated MA routes require a route check before the standard ladder. See D11, D16 and the corrected review diagrams.

**Verdict:** SCOPED_ALTERNATIVES_AND_UNRESOLVED_FACTS

**Reason:** Nonclinical limited decisions, appeals retained by plan, urgent concurrency and route check are conditional.

- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 5; PDF page 20, block 3; access: retrieved. Passage anchor: `not delegated for processing`.
- [R14](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518) — HTML p block 11; HTML li block 28; HTML li block 34; access: retrieved. Passage anchor: `delegation`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical personnel may`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [R12](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx) — tool line 114 / PDF page 3; tool line 116 / PDF page 3; access: earlier_tool_excerpt. Passage anchor: `first-level`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `expects to issue`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 140; access: tool_excerpt. Passage anchor: `unrestricted license`.
- [A12](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/) — tool line 21; access: tool_excerpt. Passage anchor: `required by law to accept`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML p block 4; access: retrieved. Passage anchor: `non-grandfathered`.
- [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/) — tool line 28; tool line 54; access: tool_excerpt. Passage anchor: `same time`.

## CURRENT:038 — WORKFLOWS

**Hospice nuance:** this reference now separates interdisciplinary-group planning, designated RN coordination, attending functions, terminal-illness certification and admission recommendation. V11/V16/V17 establish the official October 2025 codification; a complete current-2026 amendment check and actual hospice assignments remain unconfirmed. A single attending or generic care coordinator cannot be assumed to own all these functions. See M28 and D33 for the scoped evidence and exceptions.

**Verdict:** SUPPORTED_DATED_DISTINCTIONS

**Reason:** Official 2025 edition establishes distinct functions; current-2026 update/actual assignments remain unconfirmed.

- [V11](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `designate a registered nurse`.
- [V11](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf) — PDF page 1, block 1; PDF page 2, block 1; access: retrieved. Passage anchor: `interdisciplinary group`.
- [V16](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-22.pdf) — PDF page 2, block 1; access: retrieved. Passage anchor: `Sources of certification`.
- [V17](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-25.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `Admission to hospice`.
- [V11](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `designate a registered nurse`.
- [V16](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-22.pdf) — PDF page 2, block 1; access: retrieved. Passage anchor: `Sources of certification`.
- [V17](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-25.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `Admission to hospice`.

## CURRENT:046 — WORKFLOW_PEOPLE

**Evidence caution:** this earlier map is synthesis; its substantive narrative/table blocks now have explicit dispositions in the [defined assertion audit](README.md), linked to the detailed role reviews. Composite table review is not independent proof of every possible case. See the [evidence register](../EVIDENCE_REGISTER.md) and [corrections](../FINDINGS.md) for scope, alternatives and unresolved authority.

**Verdict:** DOCUMENTATION_SCOPE

**Reason:** Evidence-review metadata; no new clinical claim.


## CURRENT:053 — WORKFLOW_PEOPLE

| Role | Concrete work | When involved | Evidence |
| --- | --- | --- | --- |
| Ordering/treating physician | Recommends service and supplies clinical rationale and documentation | Usual clinical origin; another authorized practitioner may order | R01–R02, R11; [C01](../roles/C01.md) |
| Nurse practitioner / physician assistant / other authorized practitioner | Orders or supports care within the applicable professional role | May occupy the ordering-clinician function | R11, R25–R26 |
| Referring clinician / primary-care clinician | Sends referral/history and communicates with the receiving service | When referral needed; may also be the ordering clinician | R04–R05; [C02](../roles/C02.md) |
| Receiving specialist / performing clinician | Clarifies proposed service, procedure and relevant evidence | Service-specific; may also be the requester | R01–R05 |
| Clinic nurse / medical assistant / clinical-support staff | Helps collect chart information and coordinate clinician messages | Common support function; duties differ by training | R09, R24–R27 |
| Prior-authorization specialist / precertification representative | Assembles, submits and tracks requests; follows up missing information and outcomes | Central operational function | R04–R05 |
| Referral coordinator | Connects referring/receiving services and tracks referral requirements | Can be combined with authorization or scheduling | R04–R05 |
| Registration / patient-access / insurance-verification staff | Checks patient identity, insurance identifiers and benefits | Modeled function, not always a separate job | R06; [O03](../roles/O03.md) |
| Scheduler / procedure coordinator | Coordinates dates and service availability and reacts to authorization status | Linked scheduling function | R04–R05 |
| Health-information / release-of-information specialist | Processes record requests and appropriate sharing | When record retrieval/disclosure needs this function | R07 |
| Coding / clinical-documentation-integrity specialist | Resolves relevant code/documentation questions | Conditional/adjacent; not mandatory on every request | R08; [M05](../roles/M05.md) |
| Financial counselor / medication-assistance worker | Explains financial exposure or helps access assistance | Conditional affordability issue | R06, R09 |
| Provider denial/appeal specialist | Organizes denial reasons, paperwork and clinical support for an appeal | If a dispute occurs; some also handle later claims denials | R04, R08–R09 |
| Provider physician adviser / treating specialist in peer discussion | Discusses clinical justification with reviewing clinician | Escalation; may be an existing physician performing another task | R15 |
| Practice/patient-access supervisor | Assigns work and handles process/workload escalation | Supervisory or exceptional intervention | R04, R14; [O12](../roles/O12.md) |

**Verdict:** COMPOSITE_MODEL_AND_SCOPED_ROLE_CONTEXT

**Reason:** Corrected source references and qualified title/staffing examples. Each role has its own verdict; this does not certify all table cells as empirical facts.

- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 226; access: tool_excerpt. Passage anchor: `Take a patient`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 230; access: tool_excerpt. Passage anchor: `Recommend, design`.
- [A15](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24) — tool line 112; tool line 113; tool line 120; access: tool_excerpt. Passage anchor: `authenticated`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 239; tool line 247; tool line 261; tool line 369; access: tool_excerpt. Passage anchor: `Family medicine`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 52; tool line 53; access: tool_excerpt. Passage anchor: `referral`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 233; tool line 235; tool line 238; tool line 240; access: tool_excerpt. Passage anchor: `specialize`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 52; access: tool_excerpt. Passage anchor: `Specialists`.
- [B03](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm) — tool line 221; access: tool_excerpt. Passage anchor: `scope of practice varies`.
- [V02](https://www.rn.ca.gov/practice/ab890.shtml) — tool line 113; tool line 117; tool line 118; tool line 135; access: tool_excerpt. Passage anchor: `103 NP`.
- [V02](https://www.rn.ca.gov/practice/ab890.shtml) — tool line 110; tool line 117; tool line 125; tool line 135; access: tool_excerpt. Passage anchor: `standardized procedures`.
- [B02](https://www.bls.gov/ooh/healthcare/physician-assistants.htm) — tool line 236; tool line 274; access: tool_excerpt. Passage anchor: `collaboration`.
- [V03](https://www.oregon.gov/omb/Topics-of-Interest/Pages/PA-Modernization-Bill.aspx) — tool line 45; tool line 50; tool line 53; tool line 61; access: tool_excerpt. Passage anchor: `collaboration agreement`.
- [B04](https://www.bls.gov/ooh/healthcare/registered-nurses.htm) — tool line 227; access: tool_excerpt. Passage anchor: `Assess patients`.
- [B04](https://www.bls.gov/ooh/healthcare/registered-nurses.htm) — tool line 230; access: tool_excerpt. Passage anchor: `Administer`.
- [V10](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf) — tool line 62 / PDF page 3; access: tool_excerpt. Passage anchor: `prohibited`.
- [B05](https://www.bls.gov/ooh/healthcare/licensed-practical-and-licensed-vocational-nurses.htm) — tool line 224; access: tool_excerpt. Passage anchor: `Monitor patients`.
- [B05](https://www.bls.gov/ooh/healthcare/licensed-practical-and-licensed-vocational-nurses.htm) — tool line 229; tool line 424; access: tool_excerpt. Passage anchor: `vary`.
- [V10](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf) — tool line 9 / PDF page 1; tool line 75 / PDF page 3; access: tool_excerpt. Passage anchor: `competence`.
- [B06](https://www.bls.gov/ooh/healthcare/medical-assistants.htm) — tool line 189; tool line 223; tool line 245; tool line 355; access: tool_excerpt. Passage anchor: `administrative and clinical`.
- [B02](https://www.bls.gov/ooh/healthcare/physician-assistants.htm) — tool line 241; access: tool_excerpt. Passage anchor: `do not practice medicine`.
- [B08](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm) — tool line 226; access: tool_excerpt. Passage anchor: `Collect information`.
- [B08](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm) — tool line 189; tool line 222; tool line 229; tool line 233; access: tool_excerpt. Passage anchor: `pharmacists`.
- [R09](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles) — tool line 54; access: earlier_tool_excerpt. Passage anchor: `prior authorizations`.
- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML p block 42; access: retrieved. Passage anchor: `obtaining prior authorizations`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; access: retrieved. Passage anchor: `Obtain insurance approvals`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; access: retrieved. Passage anchor: `Referral/Authorization Coordinator`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 53; access: tool_excerpt. Passage anchor: `Referral staff`.
- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML p block 48; HTML p block 269; access: retrieved. Passage anchor: `Registers and schedules`.
- [R06](https://health.ucsd.edu/insurance-billing/paying/faq/) — HTML p block 69; access: retrieved. Passage anchor: `verifies your insurance`.
- [R06](https://health.ucsd.edu/insurance-billing/paying/faq/) — HTML p block 69; access: retrieved. Passage anchor: `verifies your insurance`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; access: retrieved. Passage anchor: `insurance`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; HTML td block 100; access: retrieved. Passage anchor: `scheduling`.
- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML p block 299; access: retrieved. Passage anchor: `Provides scheduling`.
- [R07](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes) — HTML p block 8; HTML p block 9; access: retrieved. Passage anchor: `ROI specialists`.
- [B20](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm) — tool line 233; access: tool_excerpt. Passage anchor: `gatekeepers`.
- [A10](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html) — tool line 61; tool line 73; access: tool_excerpt. Passage anchor: `treatment purposes`.
- [B20](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm) — tool line 228; access: tool_excerpt. Passage anchor: `assign clinical codes`.
- [R08](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html) — HTML p block 1; access: retrieved. Passage anchor: `coding`.
- [R08](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html) — HTML p block 1; access: retrieved. Passage anchor: `clinical documentation`.
- [A15](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24) — tool line 112; tool line 113; tool line 120; access: tool_excerpt. Passage anchor: `authenticated`.
- [R06](https://health.ucsd.edu/insurance-billing/paying/faq/) — HTML p block 90; access: retrieved. Passage anchor: `financial counselor`.
- [R09](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles) — tool line 57; tool line 59; tool line 64; tool line 75; access: earlier_tool_excerpt. Passage anchor: `assistance`.
- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML p block 42; access: retrieved. Passage anchor: `appeals`.
- [R08](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html) — HTML p block 1; HTML p block 2; access: retrieved. Passage anchor: `appeals process`.
- [R15](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html) — HTML p block 15; HTML p block 16; HTML p block 17; HTML h3 block 34; access: retrieved. Passage anchor: `pre-service appeal`.
- [R15](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html) — HTML p block 10; access: retrieved. Passage anchor: `discussion`.
- [R15](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html) — HTML p block 10; access: retrieved. Passage anchor: `medical director`.
- [B22](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `Recruit, train`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; HTML td block 52; HTML td block 56; HTML td block 84; access: retrieved. Passage anchor: `supervisor`.

## CURRENT:056 — WORKFLOW_PEOPLE

Noyes describes a specialist following authorization requests through appeals [R04]; Michigan describes combined patient-service, scheduling/referral and authorization work [R05]. These are organizational examples, not a national staffing rule. The expired Mayo page R03 could not be verified in this audit and no longer supports this finding.

**Verdict:** SUPPORTED_ORGANIZATION_EXAMPLES

**Reason:** Accessible Noyes/Michigan replace expired Mayo dependence; no national staffing inference.

- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML p block 42; access: retrieved. Passage anchor: `obtaining prior authorizations`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; access: retrieved. Passage anchor: `Obtain insurance approvals`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; access: retrieved. Passage anchor: `Referral/Authorization Coordinator`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 53; access: tool_excerpt. Passage anchor: `Referral staff`.

## CURRENT:061 — WORKFLOW_PEOPLE

R12 is an earlier captured excerpt after a failed fresh retrieval. R13 permits specified limited nonclinical approvals/benefit decisions under delegation, excludes AZPC appeals delegation, and contains unresolved scope tension between wider professional categories and medical-director final responsibility. These qualifications matter before applying a simple intake-to-clinician sequence; see [D11](../DECISIONS.md#d11) and U01–U08.

**Verdict:** SOURCE_LIMIT_AND_UNRESOLVED_PROGRAM_SCOPE

**Reason:** Earlier excerpt and fresh failure are distinct; limited nonclinical activity and retained appeals are scoped.

- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical staff are responsible`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `must be reviewed by a physician`.
- [R18](https://www.cigna.com/legal/members/member-rights-and-responsibilities/cigna-health-care-policies) — HTML p block 102; HTML p block 105; HTML p block 108; HTML p block 129; access: retrieved. Passage anchor: `medical directors`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 5; PDF page 20, block 3; access: retrieved. Passage anchor: `not delegated for processing`.
- [R14](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518) — HTML p block 11; HTML li block 28; HTML li block 34; access: retrieved. Passage anchor: `delegation`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical personnel may`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [R12](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx) — tool line 114 / PDF page 3; tool line 116 / PDF page 3; access: earlier_tool_excerpt. Passage anchor: `first-level`.

## CURRENT:063 — WORKFLOW_PEOPLE

The cited care-program examples use different staffing models: GRACE describes an NP/social-worker team [R24], UCLA describes nurse case management and credential-dependent social-work assignments [R25], and Partnership describes multiple care-coordination roles [R32]. These examples establish variation, not national prevalence. The unavailable AHRQ-hosted guide R23 is not used as current proof. A title alone does not establish RN status or prescribing permission.

**Verdict:** SUPPORTED_DIFFERENT_PROGRAM_EXAMPLES

**Reason:** Program variation is supported, national prevalence is not.

- [R24](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse) — HTML p block 5; access: retrieved. Passage anchor: `social worker/nurse practitioner`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML p block 36; access: retrieved. Passage anchor: `integrated model`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Nurse Case Manager I`.
- [B09](https://www.bls.gov/ooh/community-and-social-service/social-workers.htm) — tool line 231; access: tool_excerpt. Passage anchor: `Assess clients`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML p block 43; access: retrieved. Passage anchor: `unlicensed`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 15, block 2; PDF page 15, block 3; access: retrieved. Passage anchor: `Social Worker I`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 12, block 7; PDF page 13, block 1; access: retrieved. Passage anchor: `Director of Care Coordination`.
- [B22](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `supervise staff`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 41; access: tool_excerpt. Passage anchor: `proactive care plan`.
- [R24](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse) — HTML p block 5; access: retrieved. Passage anchor: `social worker/nurse practitioner`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 4, block 3; PDF page 14, block 1; access: retrieved. Passage anchor: `Nurse Case Manager`.

## CURRENT:064 — WORKFLOW_PEOPLE

| Role | Concrete work | When involved | Evidence |
| --- | --- | --- | --- |
| Patient | Sets goals/preferences and reports lived barriers and changes | Central | R22, R28 |
| Family caregiver / authorized helper / legal representative | Helps implement the plan or acts within established authority | Conditional; these are distinct roles | R19, R24, R30 |
| Lead care manager / case manager | Assesses, plans, coordinates and follows unresolved issues | Program-dependent credential/staffing; no national prevalence established | R24–R26, R32 |
| Primary-care / treating clinician | Makes relevant medical treatment decisions and receives progress/concern reports | Common clinical partner | R22, R24–R26 |
| Nurse practitioner / physician assistant | Provides clinical care within role and may coordinate as well | Program-dependent | R24–R26 |
| Treating specialist(s) | Provides condition-specific treatment and recommendations | Conditional illness/service | R22, R24, R31 |
| Clinic / bedside / home-health nurse | Nursing care, education and observations | Setting/service-dependent | R27, R30 |
| Social worker / clinical social worker | Psychosocial assessment, coping support, resources and transitions | Common complex-case partner; clinical services depend on qualifications | R24–R26 |
| Pharmacist | Medication-related review, reconciliation/education and prescriber communication | Conditional medication needs | R10, R24, R31 |
| Pharmacy technician / medication-access coordinator | Refill/access paperwork, assistance logistics and follow-up | Conditional; different from pharmacist clinical work | R09 |
| Behavioral-health professional | Relevant psychiatric, psychological, counseling or substance-use services | Conditional | R24, R32; [M06](../roles/M06.md), [M07](../roles/M07.md) |
| Community health worker / navigator / health-care guide | Engagement, practical barriers, resource links and referral follow-through | Common program option; training/scope vary | R28–R29, R32 |
| Registered dietitian | Nutrition assessment and support | Conditional | R27, R31; [M12](../roles/M12.md) |
| Health educator / self-management coach | Helps understanding and self-management skills | Conditional program role | R29; [M13](../roles/M13.md) |
| Physical therapist | Mobility and physical function | Conditional | R27, R30 |
| Occupational therapist | Daily activities, function and adaptations | Conditional | R30 |
| Speech-language pathologist | Communication or swallowing support | Conditional | R30 |
| Respiratory therapist | Cardiopulmonary care and related equipment/education | Conditional clinical-service partner | R33 |
| Discharge planner / transition coordinator | Connects hospital care to home/another setting and pending services | Conditional transition | R25–R27 |
| Home-health coordinator / skilled-nursing or rehabilitation receiving team | Accepts referrals, organizes services and exchanges plan/progress information | Conditional setting | R25–R27, R30 |
| Home-health aide / personal-care worker | Supports assigned daily activities | Conditional; distinct from skilled nursing | R30 |
| Community-service / food, housing or benefits-support worker | Helps fulfill practical/social referrals | Conditional; title depends on agency | R22, R28–R29 |
| Transportation contact / dispatcher / driver | Makes arranged travel possible | Conditional service partner; synthesis from access-barrier evidence | R22, R28 |
| Equipment supplier staff | Coordinates ordered equipment and related services | Conditional | R11, R30 |
| Palliative-care professional; chaplain / spiritual-care worker | Serious-illness or spiritual support when relevant and desired | Conditional; not a universal care-management team | R27, R31 |
| Hospice interdisciplinary group / attending / support functions | Distinct planning, designated RN coordination, attending, certification and admission functions | Conditional; 2025 codification scope, not one interchangeable decision-maker | R34; [M28 and V11/V16/V17](../roles/M28.md) |
| Scheduler / administrative coordinator | Appointments, referral logistics and messages | Common support function | R04–R05, R26, R32 |
| Payer benefits / authorization contact | Resolves access to plan-covered services | Conditional intersection with other workflows | R06, R12–R16 |
| Interpreter / communication-access professional | Accessible assessment and communication | Conditional | R21, R25 |
| Patient-relations advocate / safeguarding service | Handles specific concerns/protection needs | Exceptional/conditional | R04, R25 |

**Verdict:** COMPOSITE_MODEL_AND_SCOPED_ROLE_CONTEXT

**Reason:** Corrected source references and qualified title/staffing examples. Each role has its own verdict; this does not certify all table cells as empirical facts.

- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 226; access: tool_excerpt. Passage anchor: `Take a patient`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 230; access: tool_excerpt. Passage anchor: `Recommend, design`.
- [A15](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24) — tool line 112; tool line 113; tool line 120; access: tool_excerpt. Passage anchor: `authenticated`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 239; tool line 247; tool line 261; tool line 369; access: tool_excerpt. Passage anchor: `Family medicine`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 52; tool line 53; access: tool_excerpt. Passage anchor: `referral`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 233; tool line 235; tool line 238; tool line 240; access: tool_excerpt. Passage anchor: `specialize`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 52; access: tool_excerpt. Passage anchor: `Specialists`.
- [B03](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm) — tool line 221; access: tool_excerpt. Passage anchor: `scope of practice varies`.
- [V02](https://www.rn.ca.gov/practice/ab890.shtml) — tool line 113; tool line 117; tool line 118; tool line 135; access: tool_excerpt. Passage anchor: `103 NP`.
- [V02](https://www.rn.ca.gov/practice/ab890.shtml) — tool line 110; tool line 117; tool line 125; tool line 135; access: tool_excerpt. Passage anchor: `standardized procedures`.
- [B02](https://www.bls.gov/ooh/healthcare/physician-assistants.htm) — tool line 236; tool line 274; access: tool_excerpt. Passage anchor: `collaboration`.
- [V03](https://www.oregon.gov/omb/Topics-of-Interest/Pages/PA-Modernization-Bill.aspx) — tool line 45; tool line 50; tool line 53; tool line 61; access: tool_excerpt. Passage anchor: `collaboration agreement`.
- [B04](https://www.bls.gov/ooh/healthcare/registered-nurses.htm) — tool line 227; access: tool_excerpt. Passage anchor: `Assess patients`.
- [B04](https://www.bls.gov/ooh/healthcare/registered-nurses.htm) — tool line 230; access: tool_excerpt. Passage anchor: `Administer`.
- [V10](https://www.ncsbn.org/public-files/2016_Decision-Making-Framework.pdf) — tool line 62 / PDF page 3; access: tool_excerpt. Passage anchor: `prohibited`.
- [R24](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse) — HTML p block 5; access: retrieved. Passage anchor: `social worker/nurse practitioner`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML p block 36; access: retrieved. Passage anchor: `integrated model`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Nurse Case Manager I`.
- [B09](https://www.bls.gov/ooh/community-and-social-service/social-workers.htm) — tool line 231; access: tool_excerpt. Passage anchor: `Assess clients`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML p block 43; access: retrieved. Passage anchor: `unlicensed`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 15, block 2; PDF page 15, block 3; access: retrieved. Passage anchor: `Social Worker I`.
- [B09](https://www.bls.gov/ooh/community-and-social-service/social-workers.htm) — tool line 242; access: tool_excerpt. Passage anchor: `licensed to diagnose`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML p block 43; access: retrieved. Passage anchor: `California-licensed`.
- [B07](https://www.bls.gov/ooh/healthcare/pharmacists.htm) — tool line 227; access: tool_excerpt. Passage anchor: `Check patients`.
- [B07](https://www.bls.gov/ooh/healthcare/pharmacists.htm) — tool line 228; access: tool_excerpt. Passage anchor: `Instruct patients`.
- [V13](https://app.leg.wa.gov/WAC/default.aspx?cite=246-945-350) — tool line 145; access: tool_excerpt. Passage anchor: `therapeutic decisions`.
- [B08](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm) — tool line 226; access: tool_excerpt. Passage anchor: `Collect information`.
- [B08](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm) — tool line 189; tool line 222; tool line 229; tool line 233; access: tool_excerpt. Passage anchor: `pharmacists`.
- [R09](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles) — tool line 54; access: earlier_tool_excerpt. Passage anchor: `prior authorizations`.
- [B01](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm) — tool line 248; tool line 266; tool line 365; tool line 407; access: tool_excerpt. Passage anchor: `Psychiatrists`.
- [B10](https://www.bls.gov/ooh/life-physical-and-social-science/psychologists.htm) — tool line 238; tool line 239; tool line 240; tool line 253; access: tool_excerpt. Passage anchor: `Clinical and counseling`.
- [V04](https://www.rld.nm.gov/boards-and-commissions/individual-boards-and-commissions/psychologist-examiners/licensing-registration-and-renewal/) — tool line 380; access: tool_excerpt. Passage anchor: `Prescription Certificate`.
- [B11](https://www.bls.gov/ooh/community-and-social-service/substance-abuse-behavioral-disorder-and-mental-health-counselors.htm) — tool line 223; access: tool_excerpt. Passage anchor: `Evaluate clients`.
- [B11](https://www.bls.gov/ooh/community-and-social-service/substance-abuse-behavioral-disorder-and-mental-health-counselors.htm) — tool line 224; access: tool_excerpt. Passage anchor: `Develop, recommend`.
- [B12](https://www.bls.gov/ooh/community-and-social-service/community-health-workers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `Coordinate care`.
- [R29](https://www.cdc.gov/chronic-disease/php/community-health-worker-resources/index.html) — tool line 31; access: tool_excerpt. Passage anchor: `trusted`.
- [R28](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html) — tool line 37; tool line 49; tool line 54; tool line 56; access: tool_excerpt. Passage anchor: `patient navigator`.
- [R28](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html) — tool line 37; tool line 39; tool line 51; access: tool_excerpt. Passage anchor: `barriers`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 15, block 3; access: retrieved. Passage anchor: `Health Care Guide I`.
- [B14](https://www.bls.gov/ooh/healthcare/dietitians-and-nutritionists.htm) — tool line 226; access: tool_excerpt. Passage anchor: `Assess clients`.
- [B14](https://www.bls.gov/ooh/healthcare/dietitians-and-nutritionists.htm) — tool line 228; tool line 248; access: tool_excerpt. Passage anchor: `Develop meal`.
- [B13](https://www.bls.gov/ooh/community-and-social-service/health-educators.htm) — tool line 229; access: tool_excerpt. Passage anchor: `Assess the health needs`.
- [B13](https://www.bls.gov/ooh/community-and-social-service/health-educators.htm) — tool line 191; tool line 230; tool line 238; access: tool_excerpt. Passage anchor: `Develop programs`.
- [B15](https://www.bls.gov/ooh/healthcare/physical-therapists.htm) — tool line 229; access: tool_excerpt. Passage anchor: `Develop individualized plans`.
- [B15](https://www.bls.gov/ooh/healthcare/physical-therapists.htm) — tool line 221; tool line 231; access: tool_excerpt. Passage anchor: `Evaluate and record`.
- [B16](https://www.bls.gov/ooh/healthcare/occupational-therapists.htm) — tool line 188; tool line 222; tool line 228; access: tool_excerpt. Passage anchor: `daily living`.
- [B16](https://www.bls.gov/ooh/healthcare/occupational-therapists.htm) — tool line 232; access: tool_excerpt. Passage anchor: `Recommend special equipment`.
- [B17](https://www.bls.gov/ooh/healthcare/speech-language-pathologists.htm) — tool line 222; tool line 226; tool line 232; tool line 237; access: tool_excerpt. Passage anchor: `swallowing`.
- [B17](https://www.bls.gov/ooh/healthcare/speech-language-pathologists.htm) — tool line 228; access: tool_excerpt. Passage anchor: `individualized treatment plan`.
- [B18](https://www.bls.gov/ooh/healthcare/respiratory-therapists.htm) — tool line 228; access: tool_excerpt. Passage anchor: `Consult with physicians`.
- [B18](https://www.bls.gov/ooh/healthcare/respiratory-therapists.htm) — tool line 232; tool line 236; access: tool_excerpt. Passage anchor: `Teach patients`.
- [A06](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43) — tool line 110; access: tool_excerpt. Passage anchor: `appropriately qualified personnel`.
- [A06](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43) — tool line 115; access: tool_excerpt. Passage anchor: `transmission`.
- [A07](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60) — tool line 102; access: tool_excerpt. Passage anchor: `reasonable expectation`.
- [A07](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60) — tool line 159; tool line 163; tool line 165; access: tool_excerpt. Passage anchor: `coordination of care`.
- [A06](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43) — tool line 114; tool line 116; tool line 118; access: tool_excerpt. Passage anchor: `post-acute`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML p block 38; access: retrieved. Passage anchor: `post-acute`.
- [B19](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm) — tool line 227; access: tool_excerpt. Passage anchor: `daily personal tasks`.
- [B19](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm) — tool line 235; tool line 393; tool line 424; access: tool_excerpt. Passage anchor: `supervised`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 44; access: tool_excerpt. Passage anchor: `community resources`.
- [R29](https://www.cdc.gov/chronic-disease/php/community-health-worker-resources/index.html) — tool line 31; access: tool_excerpt. Passage anchor: `social services`.
- [V05](https://www.medicaid.gov/medicaid/benefits/assurance-of-transportation) — tool line 14; access: tool_excerpt. Passage anchor: `States may pay`.
- [V14](https://www.medicaid.gov/sites/default/files/2023-09/smd23006.pdf) — tool line 141 / PDF page 5; tool line 146 / PDF page 6; tool line 174 / PDF page 7; tool line 175 / PDF page 7; access: tool_excerpt. Passage anchor: `broker`.
- [V05](https://www.medicaid.gov/medicaid/benefits/assurance-of-transportation) — tool line 22; tool line 23; tool line 24; tool line 26; access: tool_excerpt. Passage anchor: `individual driver`.
- [V14](https://www.medicaid.gov/sites/default/files/2023-09/smd23006.pdf) — tool line 141 / PDF page 5; tool line 145 / PDF page 6; tool line 218 / PDF page 8; access: tool_excerpt. Passage anchor: `driver`.
- [R11](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices) — HTML td block 110; HTML p block 131; HTML h2 block 145; access: retrieved. Passage anchor: `DMEPOS Suppliers`.
- [R11](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices) — HTML li block 6; HTML h3 block 111; HTML h3 block 146; access: retrieved. Passage anchor: `Standard Written Order`.
- [R31](https://www.mayoclinic.org/departments-centers/general-internal-medicine/palliative-care-minnesota/overview?p=1) — tool line 15; access: tool_excerpt. Passage anchor: `collaborate`.
- [R31](https://www.mayoclinic.org/departments-centers/general-internal-medicine/palliative-care-minnesota/overview?p=1) — tool line 15; tool line 21; access: tool_excerpt. Passage anchor: `dietitians`.
- [V11](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `designate a registered nurse`.
- [V11](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf) — PDF page 1, block 1; PDF page 2, block 1; access: retrieved. Passage anchor: `interdisciplinary group`.
- [V16](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-22.pdf) — PDF page 2, block 1; access: retrieved. Passage anchor: `Sources of certification`.
- [V17](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-25.pdf) — PDF page 1, block 1; access: retrieved. Passage anchor: `Admission to hospice`.
- [R31](https://www.mayoclinic.org/departments-centers/general-internal-medicine/palliative-care-minnesota/overview?p=1) — tool line 15; tool line 19; tool line 69; access: tool_excerpt. Passage anchor: `chaplain`.
- [A08](https://www.cms.gov/files/document/r222soma.pdf) — tool line 32 / PDF page 1; tool line 61 / PDF page 4; access: tool_excerpt. Passage anchor: `pastoral`.
- [R26](https://www.uclahealth.org/programs/ccsw/about-us) — HTML p block 5; access: retrieved. Passage anchor: `Administrative Staff`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 16, block 1; PDF page 17, block 1; access: retrieved. Passage anchor: `Coordinator I`.
- [R25](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers) — HTML li block 7; HTML li block 12; HTML p block 18; HTML p block 40; access: retrieved. Passage anchor: `abuse`.
- [V12](https://acl.gov/sites/default/files/2024-05/APS%20Regs%20-%20Long%20Fact%20sheet.pdf) — tool line 63 / PDF page 1; tool line 257 / PDF page 3; tool line 268 / PDF page 3; access: tool_excerpt. Passage anchor: `Person-Directed`.
- [V12](https://acl.gov/sites/default/files/2024-05/APS%20Regs%20-%20Long%20Fact%20sheet.pdf) — tool line 9 / PDF page 1; tool line 370 / PDF page 5; access: tool_excerpt. Passage anchor: `2028`.
- [R06](https://health.ucsd.edu/insurance-billing/paying/faq/) — HTML p block 69; access: retrieved. Passage anchor: `verifies your insurance`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; access: retrieved. Passage anchor: `insurance`.
- [R05](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate) — HTML p block 3; HTML td block 100; access: retrieved. Passage anchor: `scheduling`.
- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML p block 299; access: retrieved. Passage anchor: `Provides scheduling`.
- [A01](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13) — tool line 118; access: tool_excerpt. Passage anchor: `right to make informed decisions`.
- [R22](https://www.ahrq.gov/ncepcr/care/coordination.html) — tool line 23; tool line 25; access: tool_excerpt. Passage anchor: `needs and preferences`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 59; access: tool_excerpt. Passage anchor: `family members`.
- [R30](https://www.medicare.gov/coverage/home-health-services) — HTML li block 17; HTML li block 19; access: retrieved. Passage anchor: `caregiver`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 65; access: tool_excerpt. Passage anchor: `scope`.
- [A09](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html) — tool line 67; tool line 76; tool line 77; tool line 98; access: tool_excerpt. Passage anchor: `abuse`.
- [B23](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm) — tool line 230; access: tool_excerpt. Passage anchor: `Render spoken messages`.
- [R21](https://www.hhs.gov/civil-rights/for-individuals/disability/guidance-on-nondiscrimination-in-telehealth/index.html) — tool line 54; tool line 79; tool line 80; tool line 92; access: tool_excerpt. Passage anchor: `interpreter`.
- [B23](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm) — tool line 231; access: tool_excerpt. Passage anchor: `written communication`.
- [B23](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm) — tool line 227; tool line 231; tool line 232; tool line 237; access: tool_excerpt. Passage anchor: `source language`.
- [R04](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings) — HTML h1 block 51; HTML p block 311; access: retrieved. Passage anchor: `Patient Relations`.
- [A01](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13) — tool line 108; tool line 109; tool line 110; tool line 112; access: tool_excerpt. Passage anchor: `grievance`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `Non-clinical staff are responsible`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 7, block 1; access: retrieved. Passage anchor: `Non-licensed personnel may`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 6, block 6; access: retrieved. Passage anchor: `eligibility and benefits`.
- [R13](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf) — PDF page 10, block 1; access: retrieved. Passage anchor: `benefit only`.

## CURRENT:075 — MEDICAL_WORKFLOW

**Evidence caution:** this explanation is an interpretation of cited public material. Its substantive blocks now have explicit dispositions in the [defined assertion audit](README.md); invented examples and candidate mechanisms remain illustrations/hypotheses. The [evidence register](../EVIDENCE_REGISTER.md) records scope and unresolved local authority rather than certifying every possible case.

**Verdict:** DOCUMENTATION_SCOPE

**Reason:** Evidence metadata; illustrations/hypotheses and unknown local facts retain that status.


## CURRENT:089 — authority-domains

REVIEWED SCOPED SUMMARY: conditions and unresolved routes remain explicit
Separate authority domains | arrows assign a function, not universal rank

**Verdict:** DOCUMENTATION_SCOPE

**Reason:** Review legend, no new authority.


## CURRENT:106 — ma-appeals

REVIEWED SCOPED SUMMARY: conditions and unresolved routes remain explicit
Medicare Advantage Part C review path | process review, not employment hierarchy
A02-A04, A11, A16 | check integrated-plan route and actual eligibility

**Verdict:** DOCUMENTATION_SCOPE

**Reason:** Review legend; route and eligibility remain conditional.


## CURRENT:107 — ma-appeals

Identify product / decision category
Applicable integrated-plan route?
A02(a) route check first

**Verdict:** SUPPORTED_ROUTE_QUALIFICATION

**Reason:** A02(a) contains the applicable integrated-plan route distinction; detailed integrated rules were not audited.

- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `expects to issue`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 140; access: tool_excerpt. Passage anchor: `unrestricted license`.
- [A03](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590) — tool line 143; access: tool_excerpt. Passage anchor: `not involved`.
- [A03](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590) — tool line 144; access: tool_excerpt. Passage anchor: `made by a physician`.

## CURRENT:108 — ma-appeals

If applicable: identify integrated-plan process
Detailed integrated rules not audited here
Do not apply this standard ladder blindly

**Verdict:** EXPLICIT_UNVERIFIED_ROUTE_LIMIT

**Reason:** Statement of unverified detail and required route check, not a claim to verify the integrated process.

- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `expects to issue`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 140; access: tool_excerpt. Passage anchor: `unrestricted license`.

## CURRENT:116 — ma-appeals

standard MA route applies

**Verdict:** CONDITIONAL_GRAPH_ROUTE_MODEL

**Reason:** Conditional routing illustration, not automatic eligibility.

- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `expects to issue`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 140; access: tool_excerpt. Passage anchor: `unrestricted license`.

## CURRENT:117 — ma-appeals

different applicable route

**Verdict:** CONDITIONAL_GRAPH_ROUTE_MODEL

**Reason:** Separate route must be identified; no specific unverified procedure is invented.

- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 139; access: tool_excerpt. Passage anchor: `expects to issue`.
- [A02](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566) — tool line 140; access: tool_excerpt. Passage anchor: `unrestricted license`.

## CURRENT:128 — commercial-appeals

REVIEWED SCOPED SUMMARY: conditions and unresolved routes remain explicit
Applicable commercial external-review route | not the MA IRE ladder
A12 / HealthCare.gov; R17 | determine plan, issue and state/federal process

**Verdict:** DOCUMENTATION_SCOPE

**Reason:** Review legend; route and eligibility remain conditional.


## CURRENT:129 — commercial-appeals

Identify applicable plan / issue / process
Check ACA / non-grandfathered context
R17; external eligibility is conditional

**Verdict:** SUPPORTED_APPLICABILITY_CONDITION

**Reason:** R17 scope/eligibility condition; does not certify every plan or denial.

- [A12](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/) — tool line 21; access: tool_excerpt. Passage anchor: `required by law to accept`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML p block 4; access: retrieved. Passage anchor: `non-grandfathered`.
- [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/) — tool line 28; tool line 54; access: tool_excerpt. Passage anchor: `same time`.

## CURRENT:134 — commercial-appeals

identified applicable process

**Verdict:** CONDITIONAL_GRAPH_ROUTE_MODEL

**Reason:** Applicability gate is a modeling expression of the reviewed scope limits.

- [A12](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/) — tool line 21; access: tool_excerpt. Passage anchor: `required by law to accept`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML p block 4; access: retrieved. Passage anchor: `non-grandfathered`.
- [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/) — tool line 28; tool line 54; access: tool_excerpt. Passage anchor: `same time`.

## CURRENT:137 — commercial-appeals

eligible urgent review may be requested
concurrently with internal appeal | V19
not required to finish all internal steps

**Verdict:** SUPPORTED_CONCURRENT_ALTERNATIVE

**Reason:** V19 supports same-time urgent requests under eligible circumstances.

- [A12](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/) — tool line 21; access: tool_excerpt. Passage anchor: `required by law to accept`.
- [R17](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts) — HTML p block 4; access: retrieved. Passage anchor: `non-grandfathered`.
- [V19](https://www.healthcare.gov/appeal-insurance-company-decision/internal-appeals/) — tool line 28; tool line 54; access: tool_excerpt. Passage anchor: `same time`.

## CURRENT:154 — reporting-examples

described direction

**Verdict:** SUPPORTED_ORGANIZATION_EXAMPLE

**Reason:** R32 describes associate-director direction of supervisors.

- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 12, block 7; PDF page 13, block 1; access: retrieved. Passage anchor: `Director of Care Coordination`.
- [B22](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `supervise staff`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Supervisor of Case Management`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Non-Clinical Supervisor`.

## CURRENT:155 — reporting-examples

collaborates in oversight
not a documented direct reporting edge

**Verdict:** CORRECTED_RELATIONSHIP_EXAMPLE

**Reason:** R32 collaboration is shown dashed, not an invented direct reporting relation.

- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 12, block 7; PDF page 13, block 1; access: retrieved. Passage anchor: `Director of Care Coordination`.
- [B22](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm) — tool line 228; access: tool_excerpt. Passage anchor: `supervise staff`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Supervisor of Case Management`.
- [R32](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf) — PDF page 14, block 1; access: retrieved. Passage anchor: `Non-Clinical Supervisor`.
