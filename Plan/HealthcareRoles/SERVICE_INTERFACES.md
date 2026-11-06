# Illustrative service interfaces for every role

These request/response models make input/output responsibilities explicit for all roles. They are synthesized examples, not observed local protocols. A primary contact is one modeled requester/recipient, not a supervisor or the exclusive source of all information. Fields are suggested modeling fields, not universal legal mandates.

<a id="s-p01"></a>
## S-P01 — Patient / insured member

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [P01 Patient / insured member](roles/P01.md)

**Request/context:** Question/referral/task and available relevant context for: Express personal goals and make applicable informed choices about participation and care.

**Additional information needed:**

- Understandable clinical explanation.
- Options and relevant coverage information.

**Response/work product:**

- Preferences and reported history.
- Consent/refusal or request for clarification.

**Permitted decision domain:**

- Accept or refuse proposed care when legally able to decide.
- Choose permitted representatives and communication preferences.

**Not granted by this interaction:**

- Cannot require a clinician to provide inappropriate treatment.
- Cannot unilaterally establish insurance coverage or another person's legal authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Treating clinician for clinical explanation; patient advocate for process concerns; applicable representative process if decision-making authority is uncertain.

**Applicability:** Capacity, minors, emergencies and surrogate authority require applicable law and case facts; this is not a blanket consent rule.

**Evidence:** [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13), [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html)

<a id="s-p02"></a>
## S-P02 — Informal caregiver / family support person

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [P02 Informal caregiver / family support person](roles/P02.md)

**Request/context:** Question/referral/task and available relevant context for: Support the patient with practical help and observations.

**Additional information needed:**

- Patient involvement preferences.
- Relevant instructions.

**Response/work product:**

- Support availability and observations.
- Report of barriers or change.

**Permitted decision domain:**

- Agree to tasks they can actually undertake.
- Raise concerns about feasibility.

**Not granted by this interaction:**

- Family relationship alone does not grant treatment or appeal authority.
- Cannot silently substitute personal preferences for the patient's.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Care manager for resources; clinician for clinical concerns; verify representative status before using substitute authority.

**Applicability:** Information sharing depends on permitted involvement; access is not automatically access to the entire record.

**Evidence:** [R19: HHS: personal representatives](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-p03"></a>
## S-P03 — Legally recognized personal representative

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [P03 Legally recognized personal representative](roles/P03.md)

**Request/context:** Question/referral/task and available relevant context for: Exercise only the healthcare/information authority established for this patient.

**Additional information needed:**

- Authority instrument and applicable circumstances.
- Clinical explanation and patient preferences.

**Response/work product:**

- Documented scope of representation.
- Decisions within scope.

**Permitted decision domain:**

- Make decisions or exercise information rights within established authority.

**Not granted by this interaction:**

- No authority outside the instrument or applicable law.
- Not automatically the representative for every benefit appeal.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical/legal/privacy channels when authority, patient wishes, safety or conflicting representatives are in dispute.

**Applicability:** No universal national ordering of spouses, adult children or guardians is asserted; resolve governing state law and actual appointment.

**Evidence:** [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13), [R19: HHS: personal representatives](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html)

<a id="s-p04"></a>
## S-P04 — Appointed appeal representative

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U12 Internal appeal / grievance coordinator](roles/U12.md) ↔ [P04 Appointed appeal representative](roles/P04.md)

**Request/context:** Question/referral/task and available relevant context for: Pursue a coverage dispute within the appointment and applicable appeal route.

**Additional information needed:**

- Appointment/authority.
- Adverse notice and supporting record.

**Response/work product:**

- Appeal submission.
- Procedural communications and patient updates.

**Permitted decision domain:**

- Submit or pursue procedural requests permitted by the appointment.

**Not granted by this interaction:**

- Appointment is not an unrestricted healthcare proxy.
- Cannot manufacture clinical evidence or guarantee reversal.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Appeal coordinator for filing issues; treating clinician for clinical support; appropriate adjudicator for review.

**Applicability:** Verify standing, consent, route and deadlines from the actual notice; Medicare and commercial routes differ.

**Evidence:** [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html), [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html), [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview)

<a id="s-p05"></a>
## S-P05 — Healthcare interpreter / communication-access professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [P05 Healthcare interpreter / communication-access professional](roles/P05.md)

**Request/context:** Question/referral/task and available relevant context for: Enable accurate spoken or signed communication.

**Additional information needed:**

- Speaker's actual message.
- Communication/language needs.

**Response/work product:**

- Interpreted message.
- Clarification or access concern.

**Permitted decision domain:**

- Flag a communication problem and request clarification.

**Not granted by this interaction:**

- Does not make the medical or coverage decision.
- Does not become a representative merely by interpreting.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Requesting team for another qualified access arrangement; clinician for unresolved comprehension of clinical content.

**Applicability:** Qualification and access arrangements must fit the communication need; interpreting is distinct from written translation.

**Evidence:** [B23: Interpreters and translators](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm), [R21: HHS: telehealth communication access](https://www.hhs.gov/civil-rights/for-individuals/disability/guidance-on-nondiscrimination-in-telehealth/index.html)

<a id="s-p06"></a>
## S-P06 — Healthcare translator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U09 Determination / notification coordinator](roles/U09.md) ↔ [P06 Healthcare translator](roles/P06.md)

**Request/context:** Question/referral/task and available relevant context for: Render written information accurately in another language.

**Additional information needed:**

- Authoritative document version.
- Target language and audience needs.

**Response/work product:**

- Translated version with provenance.
- Questions about ambiguous source text.

**Permitted decision domain:**

- Select faithful terminology and seek source clarification.

**Not granted by this interaction:**

- Cannot change the determination or add clinical advice.
- Translation does not itself prove patient understanding.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Document author for substantive ambiguity; communication-access team for alternative formats.

**Applicability:** Language/format needs and quality review are organization-specific; the document author retains substantive responsibility.

**Evidence:** [B23: Interpreters and translators](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm), [R21: HHS: telehealth communication access](https://www.hhs.gov/civil-rights/for-individuals/disability/guidance-on-nondiscrimination-in-telehealth/index.html)

<a id="s-p07"></a>
## S-P07 — Patient-relations advocate

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [P07 Patient-relations advocate](roles/P07.md)

**Request/context:** Question/referral/task and available relevant context for: Help route concerns and improve access to the appropriate resolution process.

**Additional information needed:**

- Patient concern.
- Relevant service/process facts.

**Response/work product:**

- Routed complaint.
- Response tracking and explanation.

**Permitted decision domain:**

- Route a concern and request operational investigation.

**Not granted by this interaction:**

- Does not independently prescribe or overturn coverage.
- Not automatically a legal or appeal representative.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical leader for care issues; formal grievance mechanism for unresolved complaints; privacy officer for access concerns.

**Applicability:** A complaint about service and an appeal of a coverage decision are separate routes; a job title does not establish appointment.

**Evidence:** [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings), [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13), [R35: Medicare: help with rights and protections](https://www.medicare.gov/basics/your-medicare-rights/get-help-with-your-rights-protections)

<a id="s-c01"></a>
## S-C01 — Ordering / treating physician

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [C01 Ordering / treating physician](roles/C01.md)

**Request/context:** Question/referral/task and available relevant context for: Assess the clinical problem and recommend or order appropriate care.

**Additional information needed:**

- Patient history and examination.
- Results and specialist information.

**Response/work product:**

- Authenticated clinical note/order.
- Clinical rationale and instructions.

**Permitted decision domain:**

- Make clinical recommendations and orders within privileges.
- Revise the treatment recommendation when evidence changes.

**Not granted by this interaction:**

- An order does not establish benefit coverage.
- Cannot override applicable patient consent or another profession's scope.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Relevant specialist for expertise; urgent clinical pathway for deterioration; provider adviser or appeal process for coverage disputes.

**Applicability:** License, privileges and clinical setting control the activity; this is not a hierarchy over insurer employees.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [R01: Official benchmark repository](https://github.com/actava-ai/chi-bench#what-this-benchmark-measures)

<a id="s-c02"></a>
## S-C02 — Referring / primary-care clinician

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [C02 Referring / primary-care clinician](roles/C02.md)

**Request/context:** Question/referral/task and available relevant context for: Maintain clinical continuity and connect the patient to an appropriate service.

**Additional information needed:**

- Patient needs.
- Existing clinical record.

**Response/work product:**

- Referral and clinical question.
- Follow-up clinical plan.

**Permitted decision domain:**

- Make or revise referrals within professional scope.

**Not granted by this interaction:**

- Referral is not insurance authorization.
- Does not automatically supersede a specialist's separate professional judgment.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Receiving specialist for an unresolved clinical question; coordinator for failed referral communication.

**Applicability:** May be a physician, NP or PA under the relevant professional rules; this is a functional role, not an additional credential.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html)

<a id="s-c03"></a>
## S-C03 — Treating / performing specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C02 Referring / primary-care clinician](roles/C02.md) ↔ [C03 Treating / performing specialist](roles/C03.md)

**Request/context:** Question/referral/task and available relevant context for: Provide condition- or procedure-specific clinical evaluation and recommendations.

**Additional information needed:**

- Referral question.
- Relevant history/results and patient preferences.

**Response/work product:**

- Specialist assessment.
- Proposed service and clinical report.

**Permitted decision domain:**

- Make specialty recommendations/orders within privileges.
- Decide clinical readiness within assigned responsibility.

**Not granted by this interaction:**

- Specialty expertise is not unilateral coverage authority.
- Does not erase the patient's participation or other clinicians' responsibilities.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Referrer or multidisciplinary review for conflicting recommendations; authorization team for administrative obstacles.

**Applicability:** Clinical responsibility must be assigned for the actual service; specialist is not necessarily the organizational supervisor of the PCP.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [R01: Official benchmark repository](https://github.com/actava-ai/chi-bench#what-this-benchmark-measures), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html)

<a id="s-c04"></a>
## S-C04 — Nurse practitioner

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [C04 Nurse practitioner](roles/C04.md)

**Request/context:** Question/referral/task and available relevant context for: Provide advanced nursing/clinical care within authorized practice.

**Additional information needed:**

- History/findings.
- Current plan and professional permissions.

**Response/work product:**

- Clinical assessment/orders within scope.
- Follow-up instructions.

**Permitted decision domain:**

- Diagnose, order or prescribe only where authorized by applicable practice rules and privileges.

**Not granted by this interaction:**

- Do not assume identical independence in every state.
- NP title does not grant insurance appeal or policy authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Collaborating or relevant clinician as required by practice arrangement or complexity; care manager for coordination.

**Applicability:** Specify state, population focus, privileges and any required practice arrangement before concluding independent authority. California examples separate practice category, furnishing authority and employer requirements. Prospective 104-availability wording is not proof of present individual certification or application availability.

**Evidence:** [B03: Advanced practice nurses](https://www.bls.gov/ooh/healthcare/nurse-anesthetists-nurse-midwives-and-nurse-practitioners.htm), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page), [A07: Home-health plan and coordination](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60), [V02: California Board of Registered Nursing: AB 890 pathways](https://www.rn.ca.gov/practice/ab890.shtml)

<a id="s-c05"></a>
## S-C05 — Physician assistant / associate (jurisdiction-specific title)

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [C05 Physician assistant / associate (jurisdiction-specific title)](roles/C05.md)

**Request/context:** Question/referral/task and available relevant context for: Provide clinical assessment and treatment within the applicable PA practice arrangement.

**Additional information needed:**

- Patient history/results.
- Applicable practice arrangement.

**Response/work product:**

- Clinical assessment and authorized orders.
- Progress documentation.

**Permitted decision domain:**

- Clinical actions within state law, privileges and required collaboration/supervision arrangement.

**Not granted by this interaction:**

- Not a medical assistant.
- Do not infer a uniform national supervision ratio or unrestricted independence.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible/collaborating physician or specialty team according to the case and practice requirements.

**Applicability:** PA means physician assistant in this profile; prior authorization is written out to avoid acronym confusion.

**Evidence:** [B02: Physician assistants](https://www.bls.gov/ooh/healthcare/physician-assistants.htm), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [V03: Oregon Medical Board: PA collaborative practice](https://www.oregon.gov/omb/Topics-of-Interest/Pages/PA-Modernization-Bill.aspx)

<a id="s-c06"></a>
## S-C06 — Registered nurse providing direct care

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [C06 Registered nurse providing direct care](roles/C06.md)

**Request/context:** Question/referral/task and available relevant context for: Assess nursing needs and provide/co-ordinate nursing care.

**Additional information needed:**

- Orders/care plan.
- Nursing assessment and observations.

**Response/work product:**

- Nursing documentation.
- Education and change/escalation report.

**Permitted decision domain:**

- Make nursing judgments and carry out authorized care.
- Escalate unexpected findings.

**Not granted by this interaction:**

- RN status alone is not prescribing or payer-decision authority.
- Delegation does not transfer all accountability to unlicensed staff.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinician for treatment issues; nursing supervisor for scope/delegation questions.

**Applicability:** A direct-care RN, payer UM nurse and nurse case manager are different functions even if one person can hold more than one role.

**Evidence:** [B04: Registered nurses](https://www.bls.gov/ooh/healthcare/registered-nurses.htm), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page)

<a id="s-c07"></a>
## S-C07 — Licensed practical / vocational nurse

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C06 Registered nurse providing direct care](roles/C06.md) ↔ [C07 Licensed practical / vocational nurse](roles/C07.md)

**Request/context:** Question/referral/task and available relevant context for: Provide authorized practical nursing care and report patient status.

**Additional information needed:**

- Assigned plan and supervision.
- Patient observations.

**Response/work product:**

- Care/task record.
- Reported changes and concerns.

**Permitted decision domain:**

- Carry out activities permitted by training, state rules and supervision.

**Not granted by this interaction:**

- No universal national list of IV/assessment permissions is assumed.
- Cannot act as an RN merely because assigned similar tasks.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** RN, advanced-practice clinician or physician according to the practice and urgency.

**Applicability:** State law and setting determine supervision and permitted activities; staffing title alone is insufficient.

**Evidence:** [B05: Practical and vocational nurses](https://www.bls.gov/ooh/healthcare/licensed-practical-and-licensed-vocational-nurses.htm), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page)

<a id="s-c08"></a>
## S-C08 — Medical assistant / clinical-support assistant

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [C08 Medical assistant / clinical-support assistant](roles/C08.md)

**Request/context:** Question/referral/task and available relevant context for: Support clinic operations and delegated clinical/administrative tasks.

**Additional information needed:**

- Clinician instructions.
- Patient information and task queue.

**Response/work product:**

- Entered observations and administrative updates.
- Questions requiring clinician response.

**Permitted decision domain:**

- Perform assigned administrative and permitted clinical tasks.
- Flag missing information.

**Not granted by this interaction:**

- Does not independently practice medicine.
- Cannot create a diagnosis, prescription or coverage decision from an administrative assignment.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Directing clinician or clinic supervisor when task is outside training, unclear or clinically concerning.

**Applicability:** Specific clinical tasks depend on state rules and training; this role is not interchangeable with a physician assistant.

**Evidence:** [B06: Medical assistants](https://www.bls.gov/ooh/healthcare/medical-assistants.htm), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [B02: Physician assistants](https://www.bls.gov/ooh/healthcare/physician-assistants.htm)

<a id="s-o01"></a>
## S-O01 — Provider authorization / precertification specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [O01 Provider authorization / precertification specialist](roles/O01.md)

**Request/context:** Question/referral/task and available relevant context for: Move a supported request through the provider's authorization workflow.

**Additional information needed:**

- Clinician order/rationale.
- Patient/benefit details and records.

**Response/work product:**

- Authorization packet and submission receipt.
- Status/outcome and pending-work record.

**Permitted decision domain:**

- Choose operational next step under procedure.
- Return incomplete material for clarification.

**Not granted by this interaction:**

- Cannot invent medical evidence or decide clinical appropriateness.
- Submission or a tracking number is not approval.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Ordering clinician for clinical gaps; payer contact for status; provider appeal specialist for adverse outcome.

**Applicability:** Works for requester; not payer intake. Local payer requirements and request stage determine the needed packet.

**Evidence:** [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings), [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R05: Michigan: Patient Services Intermediate](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate)

<a id="s-o02"></a>
## S-O02 — Referral coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C02 Referring / primary-care clinician](roles/C02.md) ↔ [O02 Referral coordinator](roles/O02.md)

**Request/context:** Question/referral/task and available relevant context for: Connect the referring and receiving services and close referral communication.

**Additional information needed:**

- Referral and contact information.
- Receiving-service requirements.

**Response/work product:**

- Routed referral.
- Acceptance/appointment or unresolved-referral status.

**Permitted decision domain:**

- Route and follow up referrals under local procedure.

**Not granted by this interaction:**

- Cannot substitute a referral for prior authorization.
- Cannot choose an unsupported medical indication.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Referring clinician for medical question; scheduler/service team for availability or rejection.

**Applicability:** May share a job with scheduling or authorization; preserve those functions as separate milestones.

**Evidence:** [R05: Michigan: Patient Services Intermediate](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html)

<a id="s-o03"></a>
## S-O03 — Registration / patient-access representative

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [O03 Registration / patient-access representative](roles/O03.md)

**Request/context:** Question/referral/task and available relevant context for: Establish accurate administrative identity and encounter information.

**Additional information needed:**

- Patient-supplied identifiers.
- Existing registration record.

**Response/work product:**

- Verified or unresolved demographic/insurance details.
- Encounter record.

**Permitted decision domain:**

- Correct administrative fields according to verification procedure.

**Not granted by this interaction:**

- Identity entry does not confer clinical consent or guarantee coverage.
- Cannot silently merge conflicting patient records.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Registration supervisor or HIM for identity mismatch; benefits staff for coverage questions.

**Applicability:** Identity, benefits verification and authorization are distinct checks even if performed by the same employee.

**Evidence:** [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm)

<a id="s-o04"></a>
## S-O04 — Provider insurance-verification / benefits specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O03 Registration / patient-access representative](roles/O03.md) ↔ [O04 Provider insurance-verification / benefits specialist](roles/O04.md)

**Request/context:** Question/referral/task and available relevant context for: Clarify administrative coverage information needed to arrange a service.

**Additional information needed:**

- Insurance identifiers.
- Proposed service and payer response.

**Response/work product:**

- Benefits/requirement record.
- Unresolved coverage questions.

**Permitted decision domain:**

- Record verified benefits information and route discrepancies.

**Not granted by this interaction:**

- Benefits verification is not a medical-necessity approval.
- Cannot promise final payment solely from eligibility.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Payer benefits/provider services for discrepancy; financial counselor for affordability.

**Applicability:** Uses plan-specific information; a coverage estimate is not final claim adjudication.

**Evidence:** [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/), [R11: CMS: power mobility devices](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices)

<a id="s-o05"></a>
## S-O05 — Scheduler / procedure coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O02 Referral coordinator](roles/O02.md) ↔ [O05 Scheduler / procedure coordinator](roles/O05.md)

**Request/context:** Question/referral/task and available relevant context for: Arrange feasible service timing, location and staff availability.

**Additional information needed:**

- Referral/order.
- Availability and recorded prerequisite status.

**Response/work product:**

- Appointment/booking record.
- Instructions and unmet-prerequisite report.

**Permitted decision domain:**

- Offer available appointments and apply scheduling procedure.

**Not granted by this interaction:**

- Appointment is not clinical clearance or authorization.
- Cannot disregard a clinical safety concern to fill a slot.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical team for readiness; authorization coordinator for approval status; supervisor for scheduling conflicts.

**Applicability:** Scheduling may occur before authorization, but completion/readiness must not be inferred from booking alone.

**Evidence:** [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings), [R05: Michigan: Patient Services Intermediate](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate)

<a id="s-o06"></a>
## S-O06 — HIM / release-of-information specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O01 Provider authorization / precertification specialist](roles/O01.md) ↔ [O06 HIM / release-of-information specialist](roles/O06.md)

**Request/context:** Question/referral/task and available relevant context for: Retrieve and appropriately disclose authentic health information.

**Additional information needed:**

- Record request and purpose.
- Identity/authority and record location.

**Response/work product:**

- Released records and provenance.
- Access/release question or exception.

**Permitted decision domain:**

- Process or escalate a release request under applicable rules and policy.

**Not granted by this interaction:**

- Cannot change clinical facts to improve coverage.
- No blanket assumption that every treatment exchange requires signed authorization.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Privacy officer for unclear permission; authoring service for absent or disputed documentation.

**Applicability:** Purpose matters: HIPAA minimum-necessary exceptions include specified treatment disclosures; other privacy requirements can still apply.

**Evidence:** [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [V15: HHS 42 CFR Part 2 final rule and consent distinctions](https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html)

<a id="s-o07"></a>
## S-O07 — Medical coding specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G15 Billing / patient accounts / claim-denial worker](roles/G15.md) ↔ [O07 Medical coding specialist](roles/O07.md)

**Request/context:** Question/referral/task and available relevant context for: Translate documented services and diagnoses into appropriate codes.

**Additional information needed:**

- Authenticated documentation.
- Relevant coding requirements.

**Response/work product:**

- Supported code assignment.
- Documentation/coding query.

**Permitted decision domain:**

- Select supported codes and flag a coding inconsistency.

**Not granted by this interaction:**

- Cannot create a clinical diagnosis or change the underlying facts.
- Coding does not decide treatment or authorize coverage.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Documenting clinician/CDI for ambiguity; billing team for claim correction.

**Applicability:** Authorization and claims can involve different code requirements; this role is conditional, not mandatory on every case.

**Evidence:** [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

<a id="s-o08"></a>
## S-O08 — Clinical-documentation-integrity specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O07 Medical coding specialist](roles/O07.md) ↔ [O08 Clinical-documentation-integrity specialist](roles/O08.md)

**Request/context:** Question/referral/task and available relevant context for: Help clarify documentation needed to accurately represent the care provided.

**Additional information needed:**

- Clinical record.
- Coding/denial question.

**Response/work product:**

- Clarification query.
- Documentation-quality finding.

**Permitted decision domain:**

- Identify a documentation gap and request clarification.

**Not granted by this interaction:**

- Cannot dictate an unsupported diagnosis or retrospectively fabricate evidence.
- Clinician remains responsible for authenticated clinical content.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinician for substantive clarification; HIM/compliance for unresolved query issues.

**Applicability:** Documentation improvement is not permission to rewrite clinical facts to match coverage criteria.

**Evidence:** [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

<a id="s-o09"></a>
## S-O09 — Financial counselor / assistance specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [O09 Financial counselor / assistance specialist](roles/O09.md)

**Request/context:** Question/referral/task and available relevant context for: Help the patient understand costs and available assistance options.

**Additional information needed:**

- Patient financial concerns.
- Benefits/cost information and program criteria.

**Response/work product:**

- Cost explanation/estimate.
- Assistance application or referral.

**Permitted decision domain:**

- Explain program options and assist applications within assigned procedure.

**Not granted by this interaction:**

- Cannot independently guarantee coverage, funding or payment.
- Financial clearance does not establish consent or clinical readiness.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Benefits/billing for disputed amount; program administrator for assistance eligibility; clinician for treatment questions.

**Applicability:** Estimates, assistance approvals, authorization and final claims are separate records and decisions.

**Evidence:** [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/), [R09: ASHP: specialty-pharmacy technicians](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles)

<a id="s-o10"></a>
## S-O10 — Provider denial / appeal specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O01 Provider authorization / precertification specialist](roles/O01.md) ↔ [O10 Provider denial / appeal specialist](roles/O10.md)

**Request/context:** Question/referral/task and available relevant context for: Organize the provider response to an adverse outcome.

**Additional information needed:**

- Adverse notice.
- Request/record and representation information.

**Response/work product:**

- Appeal/correction packet.
- Submission tracking and unresolved issues.

**Permitted decision domain:**

- Select procedural workflow under approved policy and established standing.

**Not granted by this interaction:**

- Cannot supply unsupported clinical rationale.
- Does not automatically hold patient appeal authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Treating clinician/provider adviser for clinical issue; appointed representative or legal channel for standing.

**Applicability:** Separate pre-service authorization disputes from post-service claim denials; actual notice determines route and deadlines.

**Evidence:** [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html), [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html), [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html)

<a id="s-o11"></a>
## S-O11 — Provider physician adviser / peer-discussion clinician

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O10 Provider denial / appeal specialist](roles/O10.md) ↔ [O11 Provider physician adviser / peer-discussion clinician](roles/O11.md)

**Request/context:** Question/referral/task and available relevant context for: Present or assess the provider's clinical position in a review dispute.

**Additional information needed:**

- Clinical evidence and denial rationale.
- Question for peer discussion.

**Response/work product:**

- Clinical opinion/discussion record.
- Recommended next clinical/procedural action.

**Permitted decision domain:**

- Give a clinical opinion and recommend revision/escalation.

**Not granted by this interaction:**

- Peer discussion does not itself confer payer decision authority.
- Cannot assume it substitutes for a formal appeal.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Treating team for revised clinical plan; formal appeal route for unresolved coverage.

**Applicability:** May be the treating physician rather than a separate employee; duties depend on relationship to the patient and organization.

**Evidence:** [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html), [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm)

<a id="s-o12"></a>
## S-O12 — Practice / patient-access supervisor

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O01 Provider authorization / precertification specialist](roles/O01.md) ↔ [O12 Practice / patient-access supervisor](roles/O12.md)

**Request/context:** Question/referral/task and available relevant context for: Manage the provider operation and resolve work-routing problems.

**Additional information needed:**

- Queue/status reports.
- Staff/process problems.

**Response/work product:**

- Work assignment and process resolution.
- Escalated clinical/privacy issues.

**Permitted decision domain:**

- Allocate operational work and approve permitted process exceptions.

**Not granted by this interaction:**

- Management rank does not create clinical licensure.
- Cannot authorize insurer coverage by instructing staff.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical leader, privacy or payer contact according to the issue rather than one universal chain.

**Applicability:** Specific reporting lines are organization-specific and are not inferred from a generic title.

**Evidence:** [B22: Medical and health services managers](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm), [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings)

<a id="s-o13"></a>
## S-O13 — External diagnostic / clinical evidence author or custodian

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [O13 External diagnostic / clinical evidence author or custodian](roles/O13.md)

**Request/context:** Question/referral/task and available relevant context for: Supply authentic reports relevant to the clinical question.

**Additional information needed:**

- Relevant order/referral.
- Findings or existing source record.

**Response/work product:**

- Authenticated report/result.
- Record availability or correction response.

**Permitted decision domain:**

- Make findings only within the actual professional role.
- Release/correct reports through approved process.

**Not granted by this interaction:**

- A custodian is not necessarily the interpreting clinician.
- No one may substitute fabricated evidence for a missing report.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Authoring clinician for interpretation; HIM/privacy channel for release questions.

**Applicability:** This is an evidence-supply function spanning distinct professions, not a claim that laboratory staff, radiologists and therapists have identical permissions.

**Evidence:** [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24), [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm)

<a id="s-u01"></a>
## S-U01 — Payer UM intake coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O01 Provider authorization / precertification specialist](roles/O01.md) ↔ [U01 Payer UM intake coordinator](roles/U01.md)

**Request/context:** Question/referral/task and available relevant context for: Create and route a reviewable request record for the reviewing organization.

**Additional information needed:**

- Provider request and identifiers.
- Submitted records.

**Response/work product:**

- Review case/queue item.
- Missing-information/status communication.

**Permitted decision domain:**

- Make operational decisions and only explicitly delegated limited nonclinical/benefit decisions under the applicable program criteria.

**Not granted by this interaction:**

- Cannot infer medical necessity from missing paperwork alone.
- An intake receipt is not approval.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical reviewer for medical questions; benefits specialist for administrative coverage; manager for urgent routing.

**Applicability:** Different employer/function from provider authorization specialist; decisions follow the actual plan/delegation. R13 describes some limited nonclinical approvals and assigned benefit-only decisions; it is not a national permission or medical-necessity-denial grant.

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf)

<a id="s-u02"></a>
## S-U02 — Payer eligibility / benefit specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U01 Payer UM intake coordinator](roles/U01.md) ↔ [U02 Payer eligibility / benefit specialist](roles/U02.md)

**Request/context:** Question/referral/task and available relevant context for: Apply the plan's administrative membership and benefit information.

**Additional information needed:**

- Enrollment/benefit record.
- Requested service details.

**Response/work product:**

- Benefit/eligibility finding.
- Administrative explanation or referral.

**Permitted decision domain:**

- Make administrative benefit determinations only within delegated authority.

**Not granted by this interaction:**

- Administrative benefit issue is not interchangeable with adverse medical necessity.
- Cannot create clinical rationale for a denial.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Designated benefit decision-maker/compliance for ambiguity; clinical reviewer for medical-necessity issue.

**Applicability:** Exact benefit authority and decision notice are plan-specific; not every benefits specialist is authorized to issue a denial. R13 permits some assigned benefit-only decisions; actual signatory authority still requires the plan/delegation.

**Evidence:** [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [R16: CMS: organization determinations](https://www.cms.gov/medicare/appeals-grievances/managed-care/organization-determinations), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

<a id="s-u03"></a>
## S-U03 — Payer nurse / licensed UM clinical reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U01 Payer UM intake coordinator](roles/U01.md) ↔ [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md)

**Request/context:** Question/referral/task and available relevant context for: Assess the submitted clinical evidence under the assigned review program.

**Additional information needed:**

- Complete relevant records.
- Applicable criteria and authorized review scope.

**Response/work product:**

- Clinical review and evidence gaps.
- Approval or escalated recommendation within scope.

**Permitted decision domain:**

- Approve under documented delegation when criteria and program permit.
- Recommend or escalate when not able to approve.

**Not granted by this interaction:**

- Do not infer unrestricted denial authority from RN status.
- Cannot replace the treating clinician's treatment relationship.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Appropriate medical/other licensed reviewer and UM manager according to clinical and operational issues.

**Applicability:** Under MA 422.566(d), anticipated adverse medical necessity requires appropriate licensed professional review; local policy may impose stricter physician escalation. R13 has both a wider professional-category list and medical-director final-responsibility language. Specific case review/signoff must be clarified, not inferred from either statement alone.

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page)

<a id="s-u04"></a>
## S-U04 — Payer physician reviewer / medical director acting on a case

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md) ↔ [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md)

**Request/context:** Question/referral/task and available relevant context for: Perform assigned clinical coverage review and document the rationale.

**Additional information needed:**

- Review record and criteria.
- Escalation question.

**Response/work product:**

- Clinical coverage rationale.
- Determination or request for further evidence.

**Permitted decision domain:**

- Issue/recommend a clinical coverage determination within assigned authority.

**Not granted by this interaction:**

- Not the patient's treating physician by virtue of coverage review.
- Cannot override governing coverage rules or patient consent.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Specialist consultant for expertise; applicable appeal route if challenged; policy governance for systemic criteria questions.

**Applicability:** Case-review function is distinct from organization-wide CMO governance; authority depends on product, license, expertise and delegation. R13 has both a wider professional-category list and medical-director final-responsibility language. Specific case review/signoff must be clarified, not inferred from either statement alone.

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R18: Cigna: healthcare coverage policies](https://www.cigna.com/legal/members/member-rights-and-responsibilities/cigna-health-care-policies), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566), [A17: MA coverage criteria](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101)

<a id="s-u05"></a>
## S-U05 — Independent clinical / specialty consultant

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md) ↔ [U05 Independent clinical / specialty consultant](roles/U05.md)

**Request/context:** Question/referral/task and available relevant context for: Provide specialist expertise to the designated reviewing decision-maker.

**Additional information needed:**

- Review question and relevant record.
- Applicable clinical context.

**Response/work product:**

- Specialty opinion with reasoning.
- Further information needs.

**Permitted decision domain:**

- Give a specialty opinion.
- Decide a case only if separately appointed and authorized.

**Not granted by this interaction:**

- Consultation alone is not final appeal authority.
- Independence must not be assumed from the word consultant.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Requesting reviewer for unresolved record gaps or conflict of expertise.

**Applicability:** Differentiate contracted expertise, internal consultation and statutory independent review.

**Evidence:** [R18: Cigna: healthcare coverage policies](https://www.cigna.com/legal/members/member-rights-and-responsibilities/cigna-health-care-policies), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

<a id="s-u06"></a>
## S-U06 — Payer behavioral-health reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U01 Payer UM intake coordinator](roles/U01.md) ↔ [U06 Payer behavioral-health reviewer](roles/U06.md)

**Request/context:** Question/referral/task and available relevant context for: Review behavioral-health service requests within the assigned professional scope.

**Additional information needed:**

- Behavioral-health request/evidence.
- Program criteria and professional permissions.

**Response/work product:**

- Review rationale.
- Decision or escalation within delegated scope.

**Permitted decision domain:**

- Make delegated review decisions compatible with professional qualifications.

**Not granted by this interaction:**

- No universal authority for every mental-health profession.
- Reviewer role does not establish a treating relationship.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Designated behavioral clinical leader or appropriate appeal reviewer.

**Applicability:** Psychiatrist, psychologist and counselor credentials are not interchangeable; apply actual product and review requirements. R13 has both a wider professional-category list and medical-director final-responsibility language. Specific case review/signoff must be clarified, not inferred from either statement alone.

**Evidence:** [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

<a id="s-u07"></a>
## S-U07 — Managed-care pharmacist / pharmacy reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U01 Payer UM intake coordinator](roles/U01.md) ↔ [U07 Managed-care pharmacist / pharmacy reviewer](roles/U07.md)

**Request/context:** Question/referral/task and available relevant context for: Evaluate medication evidence and pharmacy-program requirements.

**Additional information needed:**

- Medication request/history.
- Applicable pharmacy criteria.

**Response/work product:**

- Medication review.
- Recommendation/decision and evidence requirements.

**Permitted decision domain:**

- Make pharmacy review decisions within program and professional authority.

**Not granted by this interaction:**

- Pharmacist license alone does not establish every product's denial authority.
- Cannot automatically alter the prescriber's order.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Prescriber for clinical clarification; designated physician/appeal reviewer when required.

**Applicability:** Medication pathways can differ from medical-service prior authorization and Part C item/service appeals. R13 has both a wider professional-category list and medical-director final-responsibility language. Specific case review/signoff must be clarified, not inferred from either statement alone.

**Evidence:** [R10: AMCP: managed-care pharmacists](https://www.amcp.org/about/managed-care-pharmacy/what-do-managed-care-pharmacists-do), [B07: Pharmacists](https://www.bls.gov/ooh/healthcare/pharmacists.htm), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf)

<a id="s-u08"></a>
## S-U08 — Delegated medical-group / review-vendor reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U01 Payer UM intake coordinator](roles/U01.md) ↔ [U08 Delegated medical-group / review-vendor reviewer](roles/U08.md)

**Request/context:** Question/referral/task and available relevant context for: Execute contracted review functions for the accountable organization.

**Additional information needed:**

- Delegation scope and case.
- Applicable review policies.

**Response/work product:**

- Delegated work product.
- Decision/status and oversight records.

**Permitted decision domain:**

- Only decisions explicitly within the delegation and professional scope.

**Not granted by this interaction:**

- Contract does not confer a clinical license.
- Delegation does not mean the vendor can ignore governing product requirements.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Delegating organization for limits or conflicts; relevant professional leader for clinical issues.

**Applicability:** Functional wrapper, not an extra profession; identify both employer and actual licensed/intake role. In R13, AZPC explicitly retains no delegation to process, decide or notify appeals; the plan handles that review.

**Evidence:** [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [R14: UCSD: RN Manager, Utilization Management](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

<a id="s-u09"></a>
## S-U09 — Determination / notification coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md) ↔ [U09 Determination / notification coordinator](roles/U09.md)

**Request/context:** Question/referral/task and available relevant context for: Deliver the authorized outcome with accurate procedural information.

**Additional information needed:**

- Authorized determination and rationale.
- Recipient and route information.

**Response/work product:**

- Decision notice.
- Dispatch/communication record.

**Permitted decision domain:**

- Apply notice/communication workflow.
- Escalate mismatch or missing rationale.

**Not granted by this interaction:**

- Cannot change the substantive decision while formatting a letter.
- Notice sent is not evidence that services were delivered.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Decision author for inconsistency; appeal operations for procedural information; manager for failed delivery.

**Applicability:** Contents, recipients and deadlines depend on the actual product/process; no universal time limit is encoded here.

**Evidence:** [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566), [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html)

<a id="s-u10"></a>
## S-U10 — Member-services representative

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [U10 Member-services representative](roles/U10.md)

**Request/context:** Question/referral/task and available relevant context for: Help the patient navigate benefits, status and the right contact.

**Additional information needed:**

- Patient question.
- Verified benefit/status information.

**Response/work product:**

- Explanation/referral.
- Contact record and unresolved concern.

**Permitted decision domain:**

- Operational routing and permitted administrative assistance.

**Not granted by this interaction:**

- Cannot substitute a call-center explanation for an authorized medical determination.
- Cannot claim appointment as patient representative without authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** UM/appeal team for determination questions; benefits staff for enrollment; formal complaint route as appropriate.

**Applicability:** Explanation may be limited; the determination and notice remain the source for procedural rights.

**Evidence:** [R16: CMS: organization determinations](https://www.cms.gov/medicare/appeals-grievances/managed-care/organization-determinations), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [R35: Medicare: help with rights and protections](https://www.medicare.gov/basics/your-medicare-rights/get-help-with-your-rights-protections)

<a id="s-u11"></a>
## S-U11 — Provider-services representative

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O01 Provider authorization / precertification specialist](roles/O01.md) ↔ [U11 Provider-services representative](roles/U11.md)

**Request/context:** Question/referral/task and available relevant context for: Help requesting organizations navigate operational payer processes.

**Additional information needed:**

- Provider inquiry/case identifier.
- Current case status.

**Response/work product:**

- Status/process response.
- Routed follow-up.

**Permitted decision domain:**

- Operational guidance and routing within assigned scope.

**Not granted by this interaction:**

- Status advice is not a new clinical determination.
- Cannot override coverage solely during a service call.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** UM reviewer for clinical issue; benefits/delegation team for administrative discrepancy.

**Applicability:** May be combined with other service functions; do not infer final decision power from access to the case.

**Evidence:** [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="s-u12"></a>
## S-U12 — Internal appeal / grievance coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P04 Appointed appeal representative](roles/P04.md) ↔ [U12 Internal appeal / grievance coordinator](roles/U12.md)

**Request/context:** Question/referral/task and available relevant context for: Route a challenge through the correct dispute process.

**Additional information needed:**

- Challenge and adverse notice.
- Standing/appointment and supporting record.

**Response/work product:**

- Appeal/grievance case.
- Review assignment and communications.

**Permitted decision domain:**

- Procedural routing and requests for missing material within rules.

**Not granted by this interaction:**

- Cannot relabel an appeal to avoid review.
- Cannot supply independent physician judgment when not qualified.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Qualified reconsideration reviewer; procedural/legal lead for jurisdiction or standing dispute.

**Applicability:** For MA, distinguish integrated plans and other applicable routes; grievance resolution is not necessarily coverage reversal.

**Evidence:** [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html), [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

<a id="s-u13"></a>
## S-U13 — Medical-necessity appeal / reconsideration physician

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U12 Internal appeal / grievance coordinator](roles/U12.md) ↔ [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md)

**Request/context:** Question/referral/task and available relevant context for: Make the applicable reconsideration judgment independently of the initial decision-making.

**Additional information needed:**

- Appeal case and initial rationale.
- Relevant record and criteria.

**Response/work product:**

- Reconsidered determination.
- Rationale and onward-review record when required.

**Permitted decision domain:**

- Affirm or reverse within reconsideration authority.

**Not granted by this interaction:**

- For MA 422.590(h), reviewer must not have participated in initial determination.
- Cannot treat higher job rank as adequate substitute for independence/expertise.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** MA independent entity for remaining adverse issues under applicable rules; designated route for other products.

**Applicability:** MA medical-necessity denial reconsideration requires an appropriately expert physician; do not extend this exact requirement to all products and dispute types.

**Evidence:** [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590), [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="s-u14"></a>
## S-U14 — Medicare Advantage independent-review entity reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md) ↔ [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md)

**Request/context:** Question/referral/task and available relevant context for: Review remaining disputed issues through the CMS-contracted independent route.

**Additional information needed:**

- Forwarded MA case and explanation.
- Relevant appeal evidence.

**Response/work product:**

- Independent decision.
- Notice or remand/disposition where applicable.

**Permitted decision domain:**

- Issue an independent review decision within jurisdiction.

**Not granted by this interaction:**

- Not an internal payer supervisor.
- Decision does not confer clinical treatment consent or unlimited jurisdiction.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Further appeal level when permitted; administrative process for incomplete record or jurisdiction issues.

**Applicability:** This is MA IRE review; do not label a commercial IRO or an Original Medicare contractor as the same route.

**Evidence:** [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592), [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="s-u15"></a>
## S-U15 — External-review administrator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P04 Appointed appeal representative](roles/P04.md) ↔ [U15 External-review administrator](roles/U15.md)

**Request/context:** Question/referral/task and available relevant context for: Administer intake and record movement for the specified external-review route.

**Additional information needed:**

- External-review request/case.
- Route and standing information.

**Response/work product:**

- Administrative case record.
- Assigned review and procedural communication.

**Permitted decision domain:**

- Procedural actions within the governing process.

**Not granted by this interaction:**

- Administrative case handling is not clinical review judgment.
- Cannot assume MA and commercial routes use identical criteria.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Review entity for merits; route administrator for eligibility/jurisdiction disputes.

**Applicability:** Exact administrator and permissible actions must be identified from product and notice.

**Evidence:** [R17: CMS: federal external review](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts), [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592), [A12: Applicable commercial external review](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/)

<a id="s-u16"></a>
## S-U16 — SHIP / consumer-assistance / ombudsman counselor

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [U16 SHIP / consumer-assistance / ombudsman counselor](roles/U16.md)

**Request/context:** Question/referral/task and available relevant context for: Help people understand rights and find the appropriate assistance channel.

**Additional information needed:**

- Patient concern and relevant notice.
- Program eligibility/context.

**Response/work product:**

- Explanation/referral.
- Assistance record.

**Permitted decision domain:**

- Advice and routing within the assistance program.

**Not granted by this interaction:**

- Not automatically a clinical reviewer, court or appointed representative.
- Cannot promise a coverage reversal.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Correct insurer, external reviewer or oversight office according to the issue.

**Applicability:** SHIP is Medicare-specific; ombudsman and consumer-assistance mandates differ and are not interchangeable.

**Evidence:** [R35: Medicare: help with rights and protections](https://www.medicare.gov/basics/your-medicare-rights/get-help-with-your-rights-protections), [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html)

<a id="s-u17"></a>
## S-U17 — UM manager / operational supervisor

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md) ↔ [U17 UM manager / operational supervisor](roles/U17.md)

**Request/context:** Question/referral/task and available relevant context for: Manage review operations, staffing and escalation.

**Additional information needed:**

- Case queues and performance issues.
- Review/staffing constraints.

**Response/work product:**

- Assignments and process resolutions.
- Escalation and oversight reports.

**Permitted decision domain:**

- Allocate work and route escalation within delegated management authority.

**Not granted by this interaction:**

- Management rank alone cannot replace required licensed or independent review.
- Cannot override external decision simply as supervisor.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Medical leadership for clinical authority; compliance for product rules; qualified appeal process for contested outcome.

**Applicability:** UCSD documents supervision of nurse case managers/referral coordinators in its own example; no universal payer organization chart is asserted.

**Evidence:** [R14: UCSD: RN Manager, Utilization Management](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518), [B22: Medical and health services managers](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

<a id="s-u18"></a>
## S-U18 — Applicable commercial independent-review organization reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U15 External-review administrator](roles/U15.md) ↔ [U18 Applicable commercial independent-review organization reviewer](roles/U18.md)

**Request/context:** Question/referral/task and available relevant context for: Review an eligible dispute under the applicable external-review process.

**Additional information needed:**

- Eligible external-review case.
- Denial and clinical/benefit evidence.

**Response/work product:**

- External-review outcome.
- Result communicated for implementation.

**Permitted decision domain:**

- Uphold or reverse within the identified external-review jurisdiction.

**Not granted by this interaction:**

- Not the MA IRE route.
- Do not assume every plan or denial is eligible or that a reviewer controls treatment consent.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Applicable process administrator for eligibility/filing issues; follow actual notice for further permissible remedies.

**Applicability:** HealthCare.gov describes required insurer acceptance in the process it covers; determine state/federal/plan route before applying it.

**Evidence:** [A12: Applicable commercial external review](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/), [R17: CMS: federal external review](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts)

<a id="s-m01"></a>
## S-M01 — Lead care manager / case manager

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C02 Referring / primary-care clinician](roles/C02.md) ↔ [M01 Lead care manager / case manager](roles/M01.md)

**Request/context:** Question/referral/task and available relevant context for: Coordinate a patient-centered plan and track unresolved needs.

**Additional information needed:**

- Patient preferences and assessment.
- Clinical plan and service responses.

**Response/work product:**

- Shared coordination plan.
- Assigned follow-up and unresolved-need record.

**Permitted decision domain:**

- Prioritize coordination tasks and propose plan changes.
- Make professional decisions only within underlying qualifications.

**Not granted by this interaction:**

- Title alone is not prescribing authority.
- A written referral is not proof a service was received.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Treating clinician for clinical changes; supervisor for resources; appropriate specialist for needs beyond qualifications.

**Applicability:** Credential may be nursing, social work or another background; separate coordination authority from that credential. Published staffing examples differ; this is not evidence of national role prevalence.

**Evidence:** [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse)

<a id="s-m02"></a>
## S-M02 — Medical social worker (credential-dependent practice)

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M02 Medical social worker (credential-dependent practice)](roles/M02.md)

**Request/context:** Question/referral/task and available relevant context for: Assess psychosocial and practical support needs and connect appropriate resources.

**Additional information needed:**

- Patient goals and social assessment.
- Available resources.

**Response/work product:**

- Psychosocial/resource assessment.
- Referral and follow-up.

**Permitted decision domain:**

- Choose appropriate social-service referrals within role.
- Identify need for licensed clinical or protection support.

**Not granted by this interaction:**

- Do not infer authority to diagnose or provide psychotherapy without required clinical qualification.
- Cannot decide insurance coverage.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical social worker or clinician for clinical treatment; safeguarding channel for applicable protection concerns.

**Applicability:** Job titles and licensure differ; distinguish supportive casework from licensed clinical treatment. UCLA describes a pre-licensure Clinical Social Worker II assignment; clinical job wording does not establish independent clinical licensure.

**Evidence:** [B09: Social workers](https://www.bls.gov/ooh/community-and-social-service/social-workers.htm), [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="s-m03"></a>
## S-M03 — Licensed clinical social worker

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M03 Licensed clinical social worker](roles/M03.md)

**Request/context:** Question/referral/task and available relevant context for: Provide qualified clinical social-work assessment and treatment alongside coordination.

**Additional information needed:**

- Clinical/social history and patient goals.
- Relevant referral.

**Response/work product:**

- Clinical assessment/intervention plan.
- Progress and coordination communication.

**Permitted decision domain:**

- Clinical social-work assessment/treatment within license.
- Appropriate resource/referral decisions.

**Not granted by this interaction:**

- Not automatically medication-prescribing authority.
- Clinical license does not grant payer appeal authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Psychiatrist or other clinician for medication/medical needs; applicable professional supervisor for scope issues.

**Applicability:** Exact clinical activities and independent practice depend on state license and setting, not a national generic job description.

**Evidence:** [B09: Social workers](https://www.bls.gov/ooh/community-and-social-service/social-workers.htm), [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers)

<a id="s-m04"></a>
## S-M04 — Clinical / community pharmacist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M04 Clinical / community pharmacist](roles/M04.md)

**Request/context:** Question/referral/task and available relevant context for: Support safe and effective medication use.

**Additional information needed:**

- Prescription and medication history.
- Relevant clinical information.

**Response/work product:**

- Verified dispensing/counseling record.
- Medication recommendation or clarification request.

**Permitted decision domain:**

- Make pharmacy professional judgments.
- Modify/initiate therapy only when separately authorized.

**Not granted by this interaction:**

- Cannot assume unrestricted prescribing.
- A clinical recommendation does not itself change payer coverage.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Prescriber for unresolved order/therapy issues; pharmacy/payer review for access barriers.

**Applicability:** Professional scope, collaborative arrangements and specific state permissions must be identified for therapy changes. Washington CDTA is one documented pathway for specified therapy activity; no universal requirement for a new physician instruction on each authorized action is inferred.

**Evidence:** [B07: Pharmacists](https://www.bls.gov/ooh/healthcare/pharmacists.htm), [R10: AMCP: managed-care pharmacists](https://www.amcp.org/about/managed-care-pharmacy/what-do-managed-care-pharmacists-do), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse), [V13: Washington pharmacist collaborative drug therapy agreement rule](https://app.leg.wa.gov/WAC/default.aspx?cite=246-945-350)

<a id="s-m05"></a>
## S-M05 — Pharmacy technician / medication-access coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M04 Clinical / community pharmacist](roles/M04.md) ↔ [M05 Pharmacy technician / medication-access coordinator](roles/M05.md)

**Request/context:** Question/referral/task and available relevant context for: Support medication operations and access logistics.

**Additional information needed:**

- Prescription and patient/benefit details.
- Pharmacist/prescriber instructions.

**Response/work product:**

- Processed access/refill task.
- Status and clinical clarification request.

**Permitted decision domain:**

- Administrative processing and permitted technical tasks.

**Not granted by this interaction:**

- Does not replace pharmacist clinical verification.
- Cannot invent clinical appeal rationale or independently change therapy.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Pharmacist for medication questions; prescriber for clinical support; financial assistance contact for access costs.

**Applicability:** Technician permissions vary; medication-access work can be an advanced assignment but remains distinct from pharmacist judgment.

**Evidence:** [B08: Pharmacy technicians](https://www.bls.gov/ooh/healthcare/pharmacy-technicians.htm), [R09: ASHP: specialty-pharmacy technicians](https://news.ashp.org/news/ashp-news/2019/11/21/Specialty-Pharmacy-Technicians-Assume-Advanced-Roles)

<a id="s-m06"></a>
## S-M06 — Treating psychiatrist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M06 Treating psychiatrist](roles/M06.md)

**Request/context:** Question/referral/task and available relevant context for: Provide medical specialty care for psychiatric needs.

**Additional information needed:**

- Patient history and assessment.
- Relevant medical/behavioral information.

**Response/work product:**

- Psychiatric clinical plan.
- Orders and progress communication.

**Permitted decision domain:**

- Medical/psychiatric diagnosis and treatment within physician privileges.

**Not granted by this interaction:**

- Not automatically the insurer behavioral reviewer.
- Cannot bypass applicable consent or coverage process.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Relevant clinical/emergency pathway for acute concern; care manager for access coordination.

**Applicability:** Treating psychiatrist and coverage reviewer must be identified separately even where both are physicians.

**Evidence:** [B01: Physicians and surgeons](https://www.bls.gov/ooh/healthcare/physicians-and-surgeons.htm), [B11: Behavioral and substance-use counselors](https://www.bls.gov/ooh/community-and-social-service/substance-abuse-behavioral-disorder-and-mental-health-counselors.htm), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse)

<a id="s-m07"></a>
## S-M07 — Clinical psychologist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M07 Clinical psychologist](roles/M07.md)

**Request/context:** Question/referral/task and available relevant context for: Provide qualified psychological assessment and treatment.

**Additional information needed:**

- Patient history/goals.
- Relevant referral and assessment information.

**Response/work product:**

- Psychological assessment/treatment plan.
- Progress or referral communication.

**Permitted decision domain:**

- Psychological assessment and treatment within license.

**Not granted by this interaction:**

- Do not assume either universal prescribing permission or an absolute national ban.
- Does not determine insurance coverage unless separately appointed.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Medical/prescribing clinician when needed; relevant professional lead for scope questions.

**Applicability:** Prescribing and specialty testing permissions are jurisdiction- and qualification-specific. New Mexico documents additional conditional/full prescribing certification; ordinary psychology licensure alone does not establish it.

**Evidence:** [B10: Psychologists](https://www.bls.gov/ooh/life-physical-and-social-science/psychologists.htm), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse), [V04: New Mexico psychology licensing and prescribing certificates](https://www.rld.nm.gov/boards-and-commissions/individual-boards-and-commissions/psychologist-examiners/licensing-registration-and-renewal/)

<a id="s-m08"></a>
## S-M08 — Licensed behavioral-health / substance-use counselor

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M08 Licensed behavioral-health / substance-use counselor](roles/M08.md)

**Request/context:** Question/referral/task and available relevant context for: Provide the counseling and recovery support permitted by the actual qualification.

**Additional information needed:**

- Patient goals and counseling assessment.
- Relevant referral/history.

**Response/work product:**

- Counseling plan and progress.
- Coordination/referral.

**Permitted decision domain:**

- Counseling and referral decisions within credential.

**Not granted by this interaction:**

- Not automatically a psychiatrist, psychologist or prescribing clinician.
- Cannot assume all counselor titles have the same license.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Appropriate medical/behavioral clinician for needs outside scope; protection/emergency route when indicated.

**Applicability:** Mental-health, addiction, marriage/family and peer credentials have different requirements; establish the specific credential before assigning clinical authority.

**Evidence:** [B11: Behavioral and substance-use counselors](https://www.bls.gov/ooh/community-and-social-service/substance-abuse-behavioral-disorder-and-mental-health-counselors.htm)

<a id="s-m09"></a>
## S-M09 — Community health worker

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M09 Community health worker](roles/M09.md)

**Request/context:** Question/referral/task and available relevant context for: Connect people and communities with accessible health and social support.

**Additional information needed:**

- Patient priorities and community context.
- Resource information.

**Response/work product:**

- Barrier/resource findings.
- Navigation and follow-up record.

**Permitted decision domain:**

- Choose navigation actions within program.
- Raise unmet need.

**Not granted by this interaction:**

- Not a prescriber or coverage reviewer by title.
- Cannot assume patient participation from outreach alone.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Care manager for clinical coordination; relevant service/clinical professional for unmet need.

**Applicability:** Community trust does not substitute for clinical licensure; program training and role determine permitted services.

**Evidence:** [B12: Community health workers](https://www.bls.gov/ooh/community-and-social-service/community-health-workers.htm), [R29: CDC: community health workers](https://www.cdc.gov/chronic-disease/php/community-health-worker-resources/index.html)

<a id="s-m10"></a>
## S-M10 — Patient navigator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M10 Patient navigator](roles/M10.md)

**Request/context:** Question/referral/task and available relevant context for: Help a person traverse appointments, referrals and practical access barriers.

**Additional information needed:**

- Patient access needs.
- Referral and service availability.

**Response/work product:**

- Navigation plan.
- Connection/status and unresolved barriers.

**Permitted decision domain:**

- Navigation/routing and follow-up actions.

**Not granted by this interaction:**

- Title does not establish clinical license.
- Cannot guarantee service acceptance or coverage.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Lead coordinator or service owner for failed connection; qualified clinician for clinical questions.

**Applicability:** May be a nurse, social worker, CHW or other trained worker; apply the actual credentials in addition to navigation role.

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [B12: Community health workers](https://www.bls.gov/ooh/community-and-social-service/community-health-workers.htm)

<a id="s-m11"></a>
## S-M11 — Health-care guide / nonclinical care guide

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M11 Health-care guide / nonclinical care guide](roles/M11.md)

**Request/context:** Question/referral/task and available relevant context for: Help members connect with resources and coordinate practical benefit access.

**Additional information needed:**

- Assigned member needs.
- Resource/benefit information.

**Response/work product:**

- Resource connection/status.
- Escalated unresolved need.

**Permitted decision domain:**

- Resource navigation within assigned program.

**Not granted by this interaction:**

- Not automatically clinical case management authority.
- Cannot substitute guide judgment for licensed clinical assessment.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical case manager for clinical concerns; supervisor for unresolved resources.

**Applicability:** Partnership HealthPlan documents this title as an organizational example; do not impose it on every care program.

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [R29: CDC: community health workers](https://www.cdc.gov/chronic-disease/php/community-health-worker-resources/index.html)

<a id="s-m12"></a>
## S-M12 — Registered dietitian / qualified nutrition professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M12 Registered dietitian / qualified nutrition professional](roles/M12.md)

**Request/context:** Question/referral/task and available relevant context for: Assess and support nutrition-related needs within qualification.

**Additional information needed:**

- Clinical/nutrition history.
- Patient goals and practical constraints.

**Response/work product:**

- Nutrition assessment/plan.
- Response and recommendations.

**Permitted decision domain:**

- Nutrition assessment/interventions within authorized scope.

**Not granted by this interaction:**

- Do not equate every nutritionist title with an RD credential.
- Cannot independently change unrelated medical treatment or coverage.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinician for medical concerns; care manager for affordability/resource barriers.

**Applicability:** Credential, state rules, referral/order and facility privileges determine specific clinical permissions.

**Evidence:** [B14: Dietitians and nutritionists](https://www.bls.gov/ooh/healthcare/dietitians-and-nutritionists.htm), [R31: Mayo: palliative care](https://www.mayoclinic.org/departments-centers/general-internal-medicine/palliative-care-minnesota/overview?p=1)

<a id="s-m13"></a>
## S-M13 — Health educator / self-management coach

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M13 Health educator / self-management coach](roles/M13.md)

**Request/context:** Question/referral/task and available relevant context for: Help people understand and implement relevant health-management skills.

**Additional information needed:**

- Learning goals and approved plan.
- Patient understanding/preferences.

**Response/work product:**

- Education/coaching record.
- Learning needs and follow-up.

**Permitted decision domain:**

- Select educational approach within program.

**Not granted by this interaction:**

- Education alone is not prescribing or medical diagnosis.
- Cannot assume a coaching title confers clinical licensure.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical team for treatment questions; care manager for barriers beyond education.

**Applicability:** A licensed clinician may also provide education; distinguish the educational function from any separate clinical authority.

**Evidence:** [B13: Health education specialists](https://www.bls.gov/ooh/community-and-social-service/health-educators.htm)

<a id="s-m14"></a>
## S-M14 — Physical therapist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M14 Physical therapist](roles/M14.md)

**Request/context:** Question/referral/task and available relevant context for: Assess and improve movement/function within physical-therapy practice.

**Additional information needed:**

- History/referral where required.
- Functional assessment and goals.

**Response/work product:**

- Therapy plan/progress.
- Functional recommendations.

**Permitted decision domain:**

- Physical-therapy assessment and interventions within scope.

**Not granted by this interaction:**

- Does not unilaterally decide insurance coverage.
- Referral/direct-access rules and other medical needs remain distinct.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Referring/responsible clinician for medical concerns; coordinator for access or equipment.

**Applicability:** State/direct-access, order and payer requirements can differ; do not infer one universal physician-supervision hierarchy. No particular state direct-access rule was established in this audit; attempted V20 was unavailable and is not used as proof.

**Evidence:** [B15: Physical therapists](https://www.bls.gov/ooh/healthcare/physical-therapists.htm), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-m15"></a>
## S-M15 — Occupational therapist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M15 Occupational therapist](roles/M15.md)

**Request/context:** Question/referral/task and available relevant context for: Support safe performance of daily activities and relevant adaptations.

**Additional information needed:**

- Functional history and goals.
- Relevant environment/service information.

**Response/work product:**

- OT plan/progress.
- Adaptation/equipment recommendations.

**Permitted decision domain:**

- Occupational-therapy assessment and interventions within scope.

**Not granted by this interaction:**

- Equipment recommendation is not benefit authorization.
- Cannot substitute for medical treatment outside OT scope.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical team for medical issues; service/equipment coordinator for implementation.

**Applicability:** Order, setting and scope requirements must be identified for the actual service.

**Evidence:** [B16: Occupational therapists](https://www.bls.gov/ooh/healthcare/occupational-therapists.htm), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-m16"></a>
## S-M16 — Speech-language pathologist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M16 Speech-language pathologist](roles/M16.md)

**Request/context:** Question/referral/task and available relevant context for: Assess and treat relevant communication or swallowing difficulties.

**Additional information needed:**

- Clinical history/referral.
- Functional assessment and goals.

**Response/work product:**

- Assessment and therapy plan.
- Recommendations and progress.

**Permitted decision domain:**

- Speech-language/swallowing assessment and intervention within qualification.

**Not granted by this interaction:**

- Not an interpreter by virtue of speech training.
- Cannot assume authority over unrelated medical or coverage decisions.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinical team for medical concerns; communication-access service for language interpretation.

**Applicability:** Language access and speech/swallowing impairment are different needs and may require different professionals.

**Evidence:** [B17: Speech-language pathologists](https://www.bls.gov/ooh/healthcare/speech-language-pathologists.htm), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-m17"></a>
## S-M17 — Respiratory therapist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [M17 Respiratory therapist](roles/M17.md)

**Request/context:** Question/referral/task and available relevant context for: Provide assigned cardiopulmonary assessment, treatment and education.

**Additional information needed:**

- Relevant clinical order/plan.
- Respiratory assessment and equipment needs.

**Response/work product:**

- Respiratory treatment/monitoring record.
- Education and clinical concern report.

**Permitted decision domain:**

- Respiratory-care decisions within license/protocol/order.

**Not granted by this interaction:**

- Cannot infer unrestricted prescribing or coverage authority.
- Equipment setup does not prove patient can use it safely.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinician for deterioration or order issues; service team for equipment problems.

**Applicability:** Specific protocols and privileges determine independent adjustments; state and setting must be checked.

**Evidence:** [B18: Respiratory therapists](https://www.bls.gov/ooh/healthcare/respiratory-therapists.htm), [R33: UCLA: respiratory care](https://www.uclahealth.org/medical-services/respiratory-care)

<a id="s-m18"></a>
## S-M18 — Discharge planner / transitions coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [M18 Discharge planner / transitions coordinator](roles/M18.md)

**Request/context:** Question/referral/task and available relevant context for: Coordinate a feasible transition and transfer necessary information.

**Additional information needed:**

- Clinical course/goals.
- Functional and social needs.
- Receiving-service availability.

**Response/work product:**

- Discharge/transition plan.
- Transfer record and unmet needs.

**Permitted decision domain:**

- Coordinate and revise transition arrangements within role.

**Not granted by this interaction:**

- Does not independently establish medical discharge readiness or force an unsafe/unaccepted service.
- A referral is not acceptance.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinician for readiness; qualified supervisor for plan barriers; patient rights process for disputes.

**Applicability:** Hospital 482.43 permits development by or under RN, social worker or other qualified personnel; do not impose RN-only staffing nationally.

**Evidence:** [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43), [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [R27: UCLA: hospital staff roles](https://www.uclahealth.org/hospitals/santa-monica/patients-visitors/know-your-hospital-staff)

<a id="s-m19"></a>
## S-M19 — Home-health intake / coordination clinician

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M18 Discharge planner / transitions coordinator](roles/M18.md) ↔ [M19 Home-health intake / coordination clinician](roles/M19.md)

**Request/context:** Question/referral/task and available relevant context for: Coordinate acceptance and services for a home-health plan.

**Additional information needed:**

- Referral and clinical needs.
- Allowed-practitioner plan/orders.

**Response/work product:**

- Acceptance/service arrangements.
- Coordinated plan and status/change report.

**Permitted decision domain:**

- Accept/coordinate services within agency authority.
- Seek authorized plan changes.

**Not granted by this interaction:**

- Not unrestricted authority to rewrite prescriber orders.
- Acceptance is not proof every ordered visit occurred.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible physician/allowed practitioner for order changes; agency leader for unmet capacity.

**Applicability:** Home-health rules apply to the specified setting; signatory and verbal-order acceptance requirements remain scoped.

**Evidence:** [A07: Home-health plan and coordination](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-m20"></a>
## S-M20 — Skilled-nursing / rehabilitation receiving-team coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M18 Discharge planner / transitions coordinator](roles/M18.md) ↔ [M20 Skilled-nursing / rehabilitation receiving-team coordinator](roles/M20.md)

**Request/context:** Question/referral/task and available relevant context for: Coordinate receipt of the patient and information at the receiving facility.

**Additional information needed:**

- Transition referral and clinical information.
- Facility capability/availability.

**Response/work product:**

- Acceptance/transfer response.
- Receiving plan and unresolved issues.

**Permitted decision domain:**

- Operational acceptance within facility authority.
- Route clinical decisions to responsible practitioners.

**Not granted by this interaction:**

- Cannot assume transfer acceptance means benefit approval or all clinical orders authenticated.
- Not a universal discharge decision-maker.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Receiving clinical lead for clinical orders; sending transition team for missing information.

**Applicability:** This is a receiving coordination function; profession, orders and facility rules determine actual treatment authority.

**Evidence:** [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43), [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [R27: UCLA: hospital staff roles](https://www.uclahealth.org/hospitals/santa-monica/patients-visitors/know-your-hospital-staff)

<a id="s-m21"></a>
## S-M21 — Home-health aide / personal-care worker

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M19 Home-health intake / coordination clinician](roles/M19.md) ↔ [M21 Home-health aide / personal-care worker](roles/M21.md)

**Request/context:** Question/referral/task and available relevant context for: Provide assigned personal support and report relevant changes.

**Additional information needed:**

- Assigned plan and instructions.
- Patient needs/preferences.

**Response/work product:**

- Completed-task record.
- Observed changes and unmet-support report.

**Permitted decision domain:**

- Carry out permitted assigned support tasks.
- Report inability or change.

**Not granted by this interaction:**

- No automatic diagnosis/prescribing authority.
- Home-health aide and other personal-care permissions can differ.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Supervising professional/agency for clinical concern or task outside training.

**Applicability:** Health-related tasks depend on state, training and supervision; personal support is not equivalent to skilled nursing.

**Evidence:** [B19: Home health and personal care aides](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-m22"></a>
## S-M22 — Community resource / housing / food / benefit-support worker

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M10 Patient navigator](roles/M10.md) ↔ [M22 Community resource / housing / food / benefit-support worker](roles/M22.md)

**Request/context:** Question/referral/task and available relevant context for: Deliver the assigned practical support or resource assessment.

**Additional information needed:**

- Appropriate referral and agreed information.
- Program eligibility/capacity.

**Response/work product:**

- Service acceptance/refusal or assistance record.
- Remaining barrier.

**Permitted decision domain:**

- Resource/program decisions only within the organization's authority.

**Not granted by this interaction:**

- Not clinical treatment or insurer coverage authority.
- A resource directory entry is not a guaranteed available service.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Referring coordinator for alternatives; program supervisor for eligibility or capacity dispute.

**Applicability:** Broad service-partner family, not a single licensed occupation; record the actual agency and job before assigning permissions.

**Evidence:** [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [R29: CDC: community health workers](https://www.cdc.gov/chronic-disease/php/community-health-worker-resources/index.html)

<a id="s-m23"></a>
## S-M23 — Transportation coordinator / dispatcher

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M23 Transportation coordinator / dispatcher](roles/M23.md)

**Request/context:** Question/referral/task and available relevant context for: Arrange the practical transport needed for an agreed journey.

**Additional information needed:**

- Appointment/trip details.
- Relevant accessibility requirements.

**Response/work product:**

- Trip booking/status.
- Unresolved travel barrier.

**Permitted decision domain:**

- Operational booking/routing within service rules.

**Not granted by this interaction:**

- Cannot decide clinical transport appropriateness without qualified input.
- Booking is not completed attendance.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical team for medical transport requirements; referring coordinator for failed arrangement.

**Applicability:** Functional synthesis from access-barrier and transport-support evidence; exact broker rules and payment route are not established here.

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [B19: Home health and personal care aides](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm), [V05: CMS Medicaid transportation requirements and state options](https://www.medicaid.gov/medicaid/benefits/assurance-of-transportation), [V14: Medicaid transportation coverage guide](https://www.medicaid.gov/sites/default/files/2023-09/smd23006.pdf)

<a id="s-m24"></a>
## S-M24 — Transport driver / service-delivery worker

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M23 Transportation coordinator / dispatcher](roles/M23.md) ↔ [M24 Transport driver / service-delivery worker](roles/M24.md)

**Request/context:** Question/referral/task and available relevant context for: Deliver the arranged transport within the assigned service.

**Additional information needed:**

- Confirmed trip and access details.
- Service instructions.

**Response/work product:**

- Pickup/completion or failure status.
- Operational concern.

**Permitted decision domain:**

- Safe operational execution within driver/service qualification.

**Not granted by this interaction:**

- Not emergency clinical triage by default.
- Cannot change treatment destination or disclose records beyond authorized need.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Dispatcher for trip issues; appropriate emergency service if an actual emergency arises.

**Applicability:** Operational synthesis; vehicle, attendant and medical-transport qualification must be determined for the actual journey.

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [B19: Home health and personal care aides](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [V05: CMS Medicaid transportation requirements and state options](https://www.medicaid.gov/medicaid/benefits/assurance-of-transportation), [V14: Medicaid transportation coverage guide](https://www.medicaid.gov/sites/default/files/2023-09/smd23006.pdf)

<a id="s-m25"></a>
## S-M25 — Equipment supplier / delivery or fitting staff

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [M25 Equipment supplier / delivery or fitting staff](roles/M25.md)

**Request/context:** Question/referral/task and available relevant context for: Arrange and document the ordered equipment service.

**Additional information needed:**

- Order and equipment needs.
- Relevant authorization/service requirements.

**Response/work product:**

- Fulfillment/fitting/service record.
- Missing-order or service problem.

**Permitted decision domain:**

- Supplier operational actions and qualified service tasks.

**Not granted by this interaction:**

- Cannot substitute unsupported equipment/order or assume medical necessity from delivery.
- Supplier role is not prescriber authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Ordering practitioner for clinical/order question; access team for coverage; supervisor for service problem.

**Applicability:** The CMS power-mobility example has specific requirements; do not apply those mechanically to all equipment.

**Evidence:** [R11: CMS: power mobility devices](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="s-m26"></a>
## S-M26 — Infusion / other receiving-service coordinator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [M26 Infusion / other receiving-service coordinator](roles/M26.md)

**Request/context:** Question/referral/task and available relevant context for: Arrange a service-specific handoff and readiness check.

**Additional information needed:**

- Clinical order and referral.
- Required service/coverage information.

**Response/work product:**

- Acceptance/booking response.
- Missing requirements or completed handoff.

**Permitted decision domain:**

- Scheduling/intake actions within service authority.

**Not granted by this interaction:**

- Coordinator title does not grant infusion clinical credentials.
- Cannot treat booking as approval, consent or completed administration.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Service clinician for treatment questions; referring/access team for missing documentation.

**Applicability:** Operational service-coordination model; exact service procedure and clinical signoffs require the actual provider protocol.

**Evidence:** [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings)

<a id="s-m27"></a>
## S-M27 — Palliative-care clinical team member

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [M27 Palliative-care clinical team member](roles/M27.md)

**Request/context:** Question/referral/task and available relevant context for: Contribute qualified serious-illness symptom and goals support.

**Additional information needed:**

- Clinical situation and patient goals.
- Treating-team information.

**Response/work product:**

- Serious-illness assessment/recommendation.
- Coordinated support plan.

**Permitted decision domain:**

- Clinical/support decisions within underlying profession and assigned responsibility.

**Not granted by this interaction:**

- Palliative care is not automatically hospice enrollment.
- Team label does not give every member physician authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Treating/specialty clinician for medical decisions; relevant psychosocial/spiritual professional for needs.

**Applicability:** A team function comprising different professions, each retaining its own scope; identify the actual clinician for an order.

**Evidence:** [R31: Mayo: palliative care](https://www.mayoclinic.org/departments-centers/general-internal-medicine/palliative-care-minnesota/overview?p=1), [A01: Hospital patient rights](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-B/section-482.13)

<a id="s-m28"></a>
## S-M28 — Hospice interdisciplinary group and attending functions (distinct roles)

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C06 Registered nurse providing direct care](roles/C06.md) ↔ [M28 Hospice interdisciplinary group and attending functions (distinct roles)](roles/M28.md)

**Request/context:** Question/referral/task and available relevant context for: Coordinate hospice care while distinguishing interdisciplinary, RN coordination, attending and certifying/admission functions.

**Additional information needed:**

- Hospice referral/context and goals.
- Professional assessments.

**Response/work product:**

- Interdisciplinary care plan.
- Patient/family support and change communication.

**Permitted decision domain:**

- Team/attending decisions only within the applicable hospice roles and requirements.

**Not granted by this interaction:**

- Not interchangeable with general palliative care.
- Cannot infer each team member's prescribing or certification authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Designated hospice clinical/attending leader for clinical issues; program administration for service eligibility questions.

**Applicability:** V11, V16 and V17 are the official October 2025 codification, not a complete current-2026 update check. They distinguish IDG/designated RN coordination, physician certification and admission. A patient-designated attending may have a different allowed credential; that does not grant every attending terminal-illness certification authority.

**Evidence:** [A08: Hospice interdisciplinary team](https://www.cms.gov/files/document/r222soma.pdf), [R34: Medicare: hospice benefits](https://www.medicare.gov/publications/02154-medicare-hospice-benefits.pdf), [V11: Official 2025 CFR hospice care planning snapshot](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-56.pdf), [V16: Official 2025 hospice certification rules](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-22.pdf), [V17: Official 2025 hospice admission rules](https://www.govinfo.gov/content/pkg/CFR-2025-title42-vol3/pdf/CFR-2025-title42-vol3-sec418-25.pdf)

<a id="s-m29"></a>
## S-M29 — Chaplain / spiritual-care professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M27 Palliative-care clinical team member](roles/M27.md) ↔ [M29 Chaplain / spiritual-care professional](roles/M29.md)

**Request/context:** Question/referral/task and available relevant context for: Offer desired spiritual or existential support.

**Additional information needed:**

- Patient wishes and relevant referral.
- Agreed context.

**Response/work product:**

- Support provided.
- Relevant agreed team communication.

**Permitted decision domain:**

- Spiritual-support approach within professional role and patient preference.

**Not granted by this interaction:**

- Cannot determine clinical treatment or insurance coverage.
- Spiritual care must not be assumed to replace consent or medical advice.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical or psychosocial team for needs beyond spiritual role.

**Applicability:** Participation is needs/preference-dependent; protect the distinction between support and clinical decision authority.

**Evidence:** [R27: UCLA: hospital staff roles](https://www.uclahealth.org/hospitals/santa-monica/patients-visitors/know-your-hospital-staff), [R31: Mayo: palliative care](https://www.mayoclinic.org/departments-centers/general-internal-medicine/palliative-care-minnesota/overview?p=1), [A08: Hospice interdisciplinary team](https://www.cms.gov/files/document/r222soma.pdf)

<a id="s-m30"></a>
## S-M30 — Administrative care coordinator / scheduling support

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [M30 Administrative care coordinator / scheduling support](roles/M30.md)

**Request/context:** Question/referral/task and available relevant context for: Keep assigned coordination logistics and communications organized.

**Additional information needed:**

- Assigned coordination plan.
- Contacts and service responses.

**Response/work product:**

- Schedules/status updates.
- Routed unresolved items.

**Permitted decision domain:**

- Administrative work-routing and scheduling decisions.

**Not granted by this interaction:**

- Cannot independently rewrite clinical plans or determine coverage.
- Closing a task administratively is not proof of service completion.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Lead care manager for unmet need; clinician for clinical questions; supervisor for workload.

**Applicability:** Administrative coordinator and licensed case manager may be distinct posts; do not infer credentials from title.

**Evidence:** [R26: UCLA: care-coordination department](https://www.uclahealth.org/programs/ccsw/about-us), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="s-m31"></a>
## S-M31 — Safeguarding / protection-service professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M02 Medical social worker (credential-dependent practice)](roles/M02.md) ↔ [M31 Safeguarding / protection-service professional](roles/M31.md)

**Request/context:** Question/referral/task and available relevant context for: Handle a referred protection concern within the relevant service's mandate.

**Additional information needed:**

- Specific concern/referral.
- Appropriate facts and authority.

**Response/work product:**

- Protection-process response.
- Appropriate service communication.

**Permitted decision domain:**

- Actions permitted by actual protection-service mandate and professional authority.

**Not granted by this interaction:**

- No universal investigation/removal authority is assigned by this generic label.
- Not every concern permits unrestricted record sharing.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Relevant designated protection authority or clinical/emergency route according to the actual situation.

**Applicability:** State reporting law and actual agency mandate are unresolved case variables; this card does not invent national reporting thresholds. The cited 2024 APS fact sheet has a 2028 full-compliance date; it does not prove uniform present implementation in every state or child-protection setting.

**Evidence:** [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [V12: ACL APS final rule fact sheet (dated compliance schedule)](https://acl.gov/sites/default/files/2024-05/APS%20Regs%20-%20Long%20Fact%20sheet.pdf)

<a id="s-g01"></a>
## S-G01 — Provider medical director / chief medical officer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [C01 Ordering / treating physician](roles/C01.md) ↔ [G01 Provider medical director / chief medical officer](roles/G01.md)

**Request/context:** Question/referral/task and available relevant context for: Provide assigned clinical-program leadership in the provider organization.

**Additional information needed:**

- Clinical quality/escalation findings.
- Applicable professional and organizational requirements.

**Response/work product:**

- Clinical-program policy/escalation response.
- Improvement direction.

**Permitted decision domain:**

- Clinical-program governance within organizational mandate.

**Not granted by this interaction:**

- Title alone does not establish final authority over all individual treatment.
- Cannot supersede license restrictions or automatically decide insurer benefits.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Appropriate medical-staff/governing process for unresolved clinical governance; legal/privacy channel for those issues.

**Applicability:** Actual reporting lines, medical-staff authority and privileges require local bylaws/organization chart; no universal CMO-boss graph is asserted.

**Evidence:** [B22: Medical and health services managers](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm), [R14: UCSD: RN Manager, Utilization Management](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

<a id="s-g02"></a>
## S-G02 — Payer medical director / clinical-program leader

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [U17 UM manager / operational supervisor](roles/U17.md) ↔ [G02 Payer medical director / clinical-program leader](roles/G02.md)

**Request/context:** Question/referral/task and available relevant context for: Lead the assigned payer clinical review program.

**Additional information needed:**

- Review quality/escalation reports.
- Coverage/policy requirements.

**Response/work product:**

- Clinical-program direction.
- Policy-governance input.

**Permitted decision domain:**

- Program leadership and any separately delegated case decisions.

**Not granted by this interaction:**

- Leadership is not a substitute for independent appeal review.
- Cannot unilaterally override governing coverage standards.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** UM committee for criteria governance; qualified appeal route for case challenge; compliance for legal requirements.

**Applicability:** In MA the UM committee is led by the plan medical director; governance and case-review roles are not the same authority edge.

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590), [R18: Cigna: healthcare coverage policies](https://www.cigna.com/legal/members/member-rights-and-responsibilities/cigna-health-care-policies)

<a id="s-g03"></a>
## S-G03 — UM / medical-policy committee and specialty members

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G08 Policy analyst / clinical regulatory adviser](roles/G08.md) ↔ [G03 UM / medical-policy committee and specialty members](roles/G03.md)

**Request/context:** Question/referral/task and available relevant context for: Review and approve the program's applicable utilization policies.

**Additional information needed:**

- Evidence and coverage rules.
- Policy proposals and quality feedback.

**Response/work product:**

- Approved/revised policy.
- Governance rationale.

**Permitted decision domain:**

- Approve/revise policy within governing product constraints.

**Not granted by this interaction:**

- Policy committee is not necessarily the tribunal for each case.
- Cannot approve criteria contrary to governing coverage requirements.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Applicable regulatory/clinical leadership for conflicting requirements; case appeal route for individual dispute.

**Applicability:** MA committee requirements are explicit in A05; do not assume identical statutory composition for all insurance products.

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A17: MA coverage criteria](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101), [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R18: Cigna: healthcare coverage policies](https://www.cigna.com/legal/members/member-rights-and-responsibilities/cigna-health-care-policies)

<a id="s-g04"></a>
## S-G04 — Care-management director / manager

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [G04 Care-management director / manager](roles/G04.md)

**Request/context:** Question/referral/task and available relevant context for: Lead care-coordination operations and service improvement.

**Additional information needed:**

- Program metrics and escalations.
- Resource and policy requirements.

**Response/work product:**

- Resource/process direction.
- Program evaluation and escalation response.

**Permitted decision domain:**

- Program staffing/process decisions within mandate.

**Not granted by this interaction:**

- Cannot convert managerial approval into clinical consent or license.
- Does not replace treating-clinician or payer authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Relevant clinical leader for clinical questions; organization leadership for resources; regulatory staff for compliance.

**Applicability:** Partnership documents several management levels; exact titles and reporting relationships elsewhere remain local.

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [B22: Medical and health services managers](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm)

<a id="s-g05"></a>
## S-G05 — Clinical / case-management supervisor

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [M01 Lead care manager / case manager](roles/M01.md) ↔ [G05 Clinical / case-management supervisor](roles/G05.md)

**Request/context:** Question/referral/task and available relevant context for: Supervise assigned staff and support complex case coordination.

**Additional information needed:**

- Case-manager escalation.
- Team workload and quality issues.

**Response/work product:**

- Supervisory guidance and case review.
- Escalation to appropriate professional.

**Permitted decision domain:**

- Assigned supervisory and professional decisions within license.

**Not granted by this interaction:**

- Supervisor title does not permit activities beyond license.
- A nonclinical supervisor cannot supply missing clinical authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** CM manager or relevant clinician for unresolved issue; discipline-specific supervisor for licensing questions.

**Applicability:** R32 distinguishes RN, LVN, nonclinical and social-work supervisors; those qualifications must not be collapsed into one scope.

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page), [A14: Nurse Practice Acts](https://ncsbn.org/policy/npa.page)

<a id="s-g06"></a>
## S-G06 — Quality-improvement / audit professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G04 Care-management director / manager](roles/G04.md) ↔ [G06 Quality-improvement / audit professional](roles/G06.md)

**Request/context:** Question/referral/task and available relevant context for: Identify and help correct recurring process/quality problems.

**Additional information needed:**

- Authorized operational/clinical data.
- Audit criteria.

**Response/work product:**

- Quality findings.
- Improvement recommendations and follow-up.

**Permitted decision domain:**

- Classify audit findings within mandate.
- Recommend corrective actions.

**Not granted by this interaction:**

- Audit finding alone is not a new patient diagnosis or coverage decision.
- Cannot edit underlying evidence to improve metrics.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Responsible clinical/operational leader; compliance/privacy channels for their respective issues.

**Applicability:** Audit access and methods must be authorized; observational findings are not automatically causal evidence.

**Evidence:** [R14: UCSD: RN Manager, Utilization Management](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm)

<a id="s-g07"></a>
## S-G07 — Trainer / clinical educator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G04 Care-management director / manager](roles/G04.md) ↔ [G07 Trainer / clinical educator](roles/G07.md)

**Request/context:** Question/referral/task and available relevant context for: Develop and deliver the assigned workforce training.

**Additional information needed:**

- Approved policies and tools.
- Identified learning gaps.

**Response/work product:**

- Training materials and learning record.
- Escalated policy question.

**Permitted decision domain:**

- Educational methods and training evaluation within assignment.

**Not granted by this interaction:**

- Training does not expand professional license or delegate prohibited activity.
- Cannot treat attendance as independent credentialing.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Policy owner for ambiguity; professional supervisor for competence/scope concerns.

**Applicability:** A clinical educator may hold a clinical license, but its separate practice permissions are not supplied by the training title.

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [B13: Health education specialists](https://www.bls.gov/ooh/community-and-social-service/health-educators.htm), [A13: Nursing scope framework](https://ncsbn.org/nursing-regulation/practice/decision-making-framework.page)

<a id="s-g08"></a>
## S-G08 — Policy analyst / clinical regulatory adviser

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G03 UM / medical-policy committee and specialty members](roles/G03.md) ↔ [G08 Policy analyst / clinical regulatory adviser](roles/G08.md)

**Request/context:** Question/referral/task and available relevant context for: Maintain traceable policy analysis and draft operational requirements.

**Additional information needed:**

- Requirements/evidence.
- Operational feedback and policy versions.

**Response/work product:**

- Policy analysis/draft.
- Change-impact and approval request.

**Permitted decision domain:**

- Draft and recommend revisions.
- Approve only if separately designated.

**Not granted by this interaction:**

- Analysis is not enactment or unrestricted clinical authority.
- Draft policy is not automatically effective policy.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Designated committee/owner for approval; compliance/legal for interpretation uncertainty.

**Applicability:** Clinical adviser and nonclinical analyst may be separate professions; any clinical decision requires the actual credential and assignment.

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A17: MA coverage criteria](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101)

<a id="s-g09"></a>
## S-G09 — Compliance / regulatory professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G04 Care-management director / manager](roles/G04.md) ↔ [G09 Compliance / regulatory professional](roles/G09.md)

**Request/context:** Question/referral/task and available relevant context for: Support adherence to applicable program and organizational requirements.

**Additional information needed:**

- Applicable rules and oversight findings.
- Operational concerns.

**Response/work product:**

- Compliance guidance/action plan.
- Escalated interpretive issue.

**Permitted decision domain:**

- Compliance recommendations and assigned administrative actions.

**Not granted by this interaction:**

- Cannot independently authorize treatment or assume an adjudicator's power.
- Legal obligations are not created merely by internal interpretation.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Designated legal/regulatory authority or leadership according to the issue.

**Applicability:** Actual legal interpretation and enforcement authority depend on role; local compliance staff are not the regulator.

**Evidence:** [R14: UCSD: RN Manager, Utilization Management](https://employment.ucsd.edu/rn-manager-utilization-management-140306/job/2BD7908FE0FC2DE4369E0F492FCDD518), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [B22: Medical and health services managers](https://www.bls.gov/ooh/management/medical-and-health-services-managers.htm)

<a id="s-g10"></a>
## S-G10 — Privacy officer / HIM privacy specialist

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O06 HIM / release-of-information specialist](roles/O06.md) ↔ [G10 Privacy officer / HIM privacy specialist](roles/G10.md)

**Request/context:** Question/referral/task and available relevant context for: Resolve assigned health-information access and privacy questions.

**Additional information needed:**

- Access/disclosure request.
- Purpose and relevant authority facts.

**Response/work product:**

- Access/disclosure guidance.
- Privacy escalation/action record.

**Permitted decision domain:**

- Privacy/access determinations within mandate and governing law.

**Not granted by this interaction:**

- Cannot decide treatment or benefit coverage merely by controlling record access.
- No blanket claim that all sharing needs authorization or that all treatment data are unrestricted.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Appropriate legal/regulatory process for unresolved law or conflicting rights; record author for clinical accuracy.

**Applicability:** Treatment, payment, patient access, representative authority and specially protected data can invoke different rules.

**Evidence:** [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [V15: HHS 42 CFR Part 2 final rule and consent distinctions](https://www.hhs.gov/hipaa/for-professionals/regulatory-initiatives/fact-sheet-42-cfr-part-2-final-rule/index.html)

<a id="s-g11"></a>
## S-G11 — Health-services / population-health data analyst

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G04 Care-management director / manager](roles/G04.md) ↔ [G11 Health-services / population-health data analyst](roles/G11.md)

**Request/context:** Question/referral/task and available relevant context for: Produce accurate authorized information about service and program performance.

**Additional information needed:**

- Authorized data and measure definitions.
- Operational questions.

**Response/work product:**

- Reports and limitations.
- Data-quality findings.

**Permitted decision domain:**

- Analytical methods and reports within assignment.

**Not granted by this interaction:**

- Analysis does not itself order patient care or change coverage.
- Cannot infer clinical outcome solely from an administrative completion field.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Data/system owner for integrity; clinical/operational owner for action on findings.

**Applicability:** Reporting access and measure interpretation require actual data governance; algorithm output is not automatically a clinical determination.

**Evidence:** [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="s-g12"></a>
## S-G12 — Business / workflow analyst

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G04 Care-management director / manager](roles/G04.md) ↔ [G12 Business / workflow analyst](roles/G12.md)

**Request/context:** Question/referral/task and available relevant context for: Translate operational needs into documented process/system changes.

**Additional information needed:**

- User/process requirements.
- Operational and system findings.

**Response/work product:**

- Process/system requirements.
- Acceptance findings and unresolved questions.

**Permitted decision domain:**

- Propose specifications and test acceptance within assignment.

**Not granted by this interaction:**

- Cannot independently rewrite medical policy or professional scope.
- Requirements document is not clinical approval.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Business/policy owner for decisions; technical owner for implementation constraints.

**Applicability:** Systems analyst authority is change-process authority, not authority over patient treatment.

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm)

<a id="s-g13"></a>
## S-G13 — EHR / clinical informatics / application-support professional

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G12 Business / workflow analyst](roles/G12.md) ↔ [G13 EHR / clinical informatics / application-support professional](roles/G13.md)

**Request/context:** Question/referral/task and available relevant context for: Support reliable health-information systems and authorized workflows.

**Additional information needed:**

- Approved requirements.
- Incident and data-quality reports.

**Response/work product:**

- System change/support resolution.
- Audit and validation information.

**Permitted decision domain:**

- Technical configuration/actions within approved change permissions.

**Not granted by this interaction:**

- Technical access does not authorize clinical record fabrication or independent medical decisions.
- A system rule is not necessarily governing policy.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Clinical/policy owner for substantive workflow content; privacy/security for access issues.

**Applicability:** Clinical informaticists may hold additional licenses; distinguish technical permissions from those independent credentials.

**Evidence:** [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

<a id="s-g14"></a>
## S-G14 — Identity / portal-access administrator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [O01 Provider authorization / precertification specialist](roles/O01.md) ↔ [G14 Identity / portal-access administrator](roles/G14.md)

**Request/context:** Question/referral/task and available relevant context for: Administer assigned user-access controls and account problems.

**Additional information needed:**

- Approved access request.
- Identity and technical incident details.

**Response/work product:**

- Provisioned/corrected access.
- Audit and unresolved incident record.

**Permitted decision domain:**

- Technical account/access actions under approved policy.

**Not granted by this interaction:**

- Cannot use admin access as authorization to view/disclose every patient record.
- Cannot decide clinical or coverage merits.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Privacy/security owner for authorization; system support for technical fault.

**Applicability:** Operational synthesis of access-control support; actual IAM owner and escalation line must be locally identified.

**Evidence:** [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes), [V08: BLS systems administrator duties](https://www.bls.gov/ooh/computer-and-information-technology/network-and-computer-systems-administrators.htm)

<a id="s-g15"></a>
## S-G15 — Billing / patient accounts / claim-denial worker

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P01 Patient / insured member](roles/P01.md) ↔ [G15 Billing / patient accounts / claim-denial worker](roles/G15.md)

**Request/context:** Question/referral/task and available relevant context for: Process payment/claim work and explain or correct administrative account issues.

**Additional information needed:**

- Service/coding record.
- Benefit and claim response.

**Response/work product:**

- Claim/account record.
- Correction or payment-dispute follow-up.

**Permitted decision domain:**

- Administrative account/claim actions within assigned permissions.

**Not granted by this interaction:**

- Prior authorization is not a guarantee of final payment.
- Cannot change clinical facts or make unsupported promises to patient.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Coding/clinical documentation team for support; payer process for payment dispute; financial counselor for assistance.

**Applicability:** Downstream claim adjudication and pre-service authorization are distinct; exact payment rules are outside a generic role title.

**Evidence:** [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [V18: BLS financial clerks duties](https://www.bls.gov/ooh/office-and-administrative-support/financial-clerks.htm)

<a id="s-g16"></a>
## S-G16 — Regulator / oversight official

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G09 Compliance / regulatory professional](roles/G09.md) ↔ [G16 Regulator / oversight official](roles/G16.md)

**Request/context:** Question/referral/task and available relevant context for: Exercise the specific public oversight authority assigned by law.

**Additional information needed:**

- Applicable oversight issue.
- Authorized complaint/evidence.

**Response/work product:**

- Oversight disposition or required action.
- Referral to proper forum.

**Permitted decision domain:**

- Only decisions/enforcement within actual jurisdiction and process.

**Not granted by this interaction:**

- Not a universal next-level doctor.
- Complaint handling does not automatically reverse a coverage decision.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Correct agency/adjudicative route when jurisdiction lies elsewhere.

**Applicability:** Identify agency, program and legal route; no blanket authority is assigned to every regulator or ombudsman.

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [R17: CMS: federal external review](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts), [R35: Medicare: help with rights and protections](https://www.medicare.gov/basics/your-medicare-rights/get-help-with-your-rights-protections)

<a id="s-g17"></a>
## S-G17 — Legal adviser / specialist legal representative

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P04 Appointed appeal representative](roles/P04.md) ↔ [G17 Legal adviser / specialist legal representative](roles/G17.md)

**Request/context:** Question/referral/task and available relevant context for: Provide the legal advice or representation actually authorized for the issue.

**Additional information needed:**

- Issue and relevant record.
- Representation scope.

**Response/work product:**

- Legal advice/submission.
- Procedural recommendation.

**Permitted decision domain:**

- Advice and procedural representation within retainer/appointment.

**Not granted by this interaction:**

- Legal advice does not itself overturn coverage or authorize clinical care.
- Appointment and conflicts must be checked.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Proper adjudicator or regulator rather than an invented clinical-superiority chain.

**Applicability:** A lawyer is not automatically needed in ordinary authorization work; professional and appointment rules are issue-specific.

**Evidence:** [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html), [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A12: Applicable commercial external review](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/), [V07: BLS lawyers duties](https://www.bls.gov/ooh/legal/lawyers.htm)

<a id="s-j01"></a>
## S-J01 — MA administrative law judge / applicable adjudicator

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P04 Appointed appeal representative](roles/P04.md) ↔ [J01 MA administrative law judge / applicable adjudicator](roles/J01.md)

**Request/context:** Question/referral/task and available relevant context for: Decide the appeal within the authorized hearing/adjudication jurisdiction.

**Additional information needed:**

- Eligible timely appeal.
- Prior decision and case record.

**Response/work product:**

- Adjudicative decision.
- Applicable onward-review information.

**Permitted decision domain:**

- Affirm/reverse/remand as permitted by the actual appeal process.

**Not granted by this interaction:**

- No universal entitlement to this stage.
- Not treating-clinician or consent authority.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Medicare Appeals Council route if available and properly pursued.

**Applicability:** Standing, filing and any amount-in-controversy rules must be checked; no threshold amounts are invented here.

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="s-j02"></a>
## S-J02 — Medicare Appeals Council reviewer

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [P04 Appointed appeal representative](roles/P04.md) ↔ [J02 Medicare Appeals Council reviewer](roles/J02.md)

**Request/context:** Question/referral/task and available relevant context for: Review the applicable appealed adjudicative decision under Council jurisdiction.

**Additional information needed:**

- Proper Council request.
- Prior adjudicative decision and record.

**Response/work product:**

- Council disposition.
- Applicable further-review information.

**Permitted decision domain:**

- Council review decisions within jurisdiction.

**Not granted by this interaction:**

- Not every dissatisfied party automatically reaches this stage.
- Does not become the patient's clinical supervisor.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Federal district-court route where legally available and properly pursued.

**Applicability:** The precise review scope and procedural requirements require the actual notice/rules; no automatic appeal entitlement is implied.

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="s-j03"></a>
## S-J03 — Federal district court in an eligible Medicare appeal

**Evidence status:** SYNTHESIZED MODEL: primary contact and transaction are NOT CONFIRMED institutional practice.

**Modeled contact ↔ role:** [G17 Legal adviser / specialist legal representative](roles/G17.md) ↔ [J03 Federal district court in an eligible Medicare appeal](roles/J03.md)

**Request/context:** Question/referral/task and available relevant context for: Exercise judicial review when the statutory conditions are met.

**Additional information needed:**

- Eligible judicial filing.
- Administrative record and legal issues.

**Response/work product:**

- Judicial decision/order.

**Permitted decision domain:**

- Judicial relief within jurisdiction.

**Not granted by this interaction:**

- Not a routine step in a clinical workflow.
- Does not grant universal authority to prescribe or override consent.

**Acknowledgement:** Named recipient records receipt, result/status and any unresolved need; receipt is not substantive approval.

**If unresolved:** Further judicial process is outside the scope of this role map.

**Applicability:** Exhaustion, standing, filing and threshold conditions matter; the map is not a procedural filing guide.

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)
