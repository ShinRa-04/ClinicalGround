# Information-flow contracts

These are explicit illustrative handoff contracts, not a claim that each organization uses these forms or that every field is legally mandated. A cited regulation controls only its stated setting. Select a flow by ID in the diagrams.

<a id="f01"></a>
## F01 — Identity / insurance information

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [P01 Patient / insured member](roles/P01.md) → [O03 Registration / patient-access representative](roles/O03.md)

**Condition:** When registering/requesting service

**Suggested identifying/content fields:**

- Patient identifier.
- Insurance identifiers.
- Contact details.

**Acknowledgement/completion evidence:** Registration match or mismatch recorded

**If missing, rejected or inconsistent:** Resolve mismatch before attaching another person's records

**Evidence:** [R03: Mayo: Precertification and Authorization Representative](https://jobs.mayoclinic.org/job/rochester/precertification-and-authorization-rep-hybrid/33647/100997191200), [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/)

<a id="f02"></a>
## F02 — Clinical service request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [C01 Ordering / treating physician](roles/C01.md) → [O01 Provider authorization / precertification specialist](roles/O01.md)

**Condition:** When service requires authorization work

**Suggested identifying/content fields:**

- Patient.
- Requested service.
- Clinical rationale.
- Responsible author/date.

**Acknowledgement/completion evidence:** Request accepted into provider queue

**If missing, rejected or inconsistent:** Ask author for clarification; do not invent rationale

**Evidence:** [R03: Mayo: Precertification and Authorization Representative](https://jobs.mayoclinic.org/job/rochester/precertification-and-authorization-rep-hybrid/33647/100997191200), [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

<a id="f03"></a>
## F03 — Benefits / requirement finding

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O04 Provider insurance-verification / benefits specialist](roles/O04.md) → [O01 Provider authorization / precertification specialist](roles/O01.md)

**Condition:** Plan/service-specific check

**Suggested identifying/content fields:**

- Plan.
- Service.
- Verification source/date.
- Unresolved requirements.

**Acknowledgement/completion evidence:** Coordinator records status and next check

**If missing, rejected or inconsistent:** Contact payer on discrepancy

**Evidence:** [R03: Mayo: Precertification and Authorization Representative](https://jobs.mayoclinic.org/job/rochester/precertification-and-authorization-rep-hybrid/33647/100997191200), [R06: UCSD: billing and insurance FAQs](https://health.ucsd.edu/insurance-billing/paying/faq/)

<a id="f04"></a>
## F04 — Supporting record package

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O06 HIM / release-of-information specialist](roles/O06.md) → [O01 Provider authorization / precertification specialist](roles/O01.md)

**Condition:** When additional records needed

**Suggested identifying/content fields:**

- Patient match.
- Source/date.
- Relevant clinical reports.
- Release basis.

**Acknowledgement/completion evidence:** Records linked to correct request

**If missing, rejected or inconsistent:** Query source for missing/incorrect records

**Evidence:** [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes), [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html)

<a id="f05"></a>
## F05 — Authorization submission

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O01 Provider authorization / precertification specialist](roles/O01.md) → [U01 Payer UM intake coordinator](roles/U01.md)

**Condition:** When request submitted

**Suggested identifying/content fields:**

- Patient/plan.
- Service.
- Requesting professional.
- Supporting record.

**Acknowledgement/completion evidence:** Payer receipt/case identifier

**If missing, rejected or inconsistent:** Track failed transmission and missing items

**Evidence:** [R03: Mayo: Precertification and Authorization Representative](https://jobs.mayoclinic.org/job/rochester/precertification-and-authorization-rep-hybrid/33647/100997191200), [R04: UR Medicine Noyes job descriptions](https://www.urmc.rochester.edu/noyes/careers-noyes/current-job-openings), [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx)

<a id="f06"></a>
## F06 — Missing-information request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U01 Payer UM intake coordinator](roles/U01.md) → [O01 Provider authorization / precertification specialist](roles/O01.md)

**Condition:** When intake/review needs clarification

**Suggested identifying/content fields:**

- Case identifier.
- Requested missing items.
- Response channel.

**Acknowledgement/completion evidence:** Provider records request and response ownership

**If missing, rejected or inconsistent:** Escalate clinical gaps to author

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf)

<a id="f07"></a>
## F07 — Clinical review case

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U01 Payer UM intake coordinator](roles/U01.md) → [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md)

**Condition:** When clinical review required

**Suggested identifying/content fields:**

- Matched identifiers.
- Request.
- Submitted evidence.
- Relevant benefit context.

**Acknowledgement/completion evidence:** Assigned reviewer/status

**If missing, rejected or inconsistent:** Return factual gaps; route urgency by policy

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf)

<a id="f08"></a>
## F08 — Applicable approved criteria

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [G03 UM / medical-policy committee and specialty members](roles/G03.md) → [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md)

**Condition:** Approved-policy use; MA requirements separately A05/A17

**Suggested identifying/content fields:**

- Policy/version.
- Product/service.
- Effective scope.
- Evidence/rule basis.

**Acknowledgement/completion evidence:** Reviewer identifies correct version

**If missing, rejected or inconsistent:** Resolve version/product mismatch

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [A17: MA coverage criteria](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.101), [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx)

<a id="f09"></a>
## F09 — Clinical escalation

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md) → [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md)

**Condition:** When delegated first level cannot resolve

**Suggested identifying/content fields:**

- Question.
- Evidence assessed.
- Criteria.
- Unresolved reason.

**Acknowledgement/completion evidence:** Qualified reviewer accepts case

**If missing, rejected or inconsistent:** Do not treat inability to approve as unreviewed denial

**Evidence:** [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

<a id="f10"></a>
## F10 — Specialty consultation request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md) → [U05 Independent clinical / specialty consultant](roles/U05.md)

**Condition:** When specialist opinion needed

**Suggested identifying/content fields:**

- Defined question.
- Relevant record.
- Scope and conflict information.

**Acknowledgement/completion evidence:** Opinion returned with rationale

**If missing, rejected or inconsistent:** Request missing evidence/appropriate expertise

**Evidence:** [R18: Cigna: healthcare coverage policies](https://www.cigna.com/legal/members/member-rights-and-responsibilities/cigna-health-care-policies), [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566)

<a id="f11"></a>
## F11 — Peer clinical discussion

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O11 Provider physician adviser / peer-discussion clinician](roles/O11.md) → [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md)

**Condition:** Plan-specific peer process

**Suggested identifying/content fields:**

- Case.
- Disputed rationale.
- Additional relevant evidence.
- Discussion record.

**Acknowledgement/completion evidence:** Outcome and next formal step recorded

**If missing, rejected or inconsistent:** Preserve applicable appeal route independently

**Evidence:** [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html)

<a id="f12"></a>
## F12 — Authorized clinical determination

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md) → [U09 Determination / notification coordinator](roles/U09.md)

**Condition:** When case decision made

**Suggested identifying/content fields:**

- Decision.
- Rationale.
- Scope/service.
- Author.
- Applicable procedural information.

**Acknowledgement/completion evidence:** Notice prepared from authorized record

**If missing, rejected or inconsistent:** Return inconsistency to decision author

**Evidence:** [A02: Initial MA organization determination review](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.566), [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf)

<a id="f13"></a>
## F13 — Decision notice

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U09 Determination / notification coordinator](roles/U09.md) → [P01 Patient / insured member](roles/P01.md)

**Condition:** Recipients/contents depend on route

**Suggested identifying/content fields:**

- Outcome.
- Reason.
- Service/case.
- Applicable review information.

**Acknowledgement/completion evidence:** Communication sent/status recorded

**If missing, rejected or inconsistent:** Correct failed/mismatched notice through process

**Evidence:** [R16: CMS: organization determinations](https://www.cms.gov/medicare/appeals-grievances/managed-care/organization-determinations), [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

<a id="f14"></a>
## F14 — Provider outcome communication

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U09 Determination / notification coordinator](roles/U09.md) → [O01 Provider authorization / precertification specialist](roles/O01.md)

**Condition:** As required/permitted in actual process

**Suggested identifying/content fields:**

- Case.
- Service.
- Outcome.
- Scope/conditions.
- Next action.

**Acknowledgement/completion evidence:** Provider updates queue and readiness checks

**If missing, rejected or inconsistent:** Clarify ambiguity before assuming approval

**Evidence:** [R13: Arizona Priority Care: 2026 UM program](https://azprioritycare.com/wp-content/uploads/2026/03/2026-AZPC-Utilization-Management-Program.pdf), [R15: UHC: appeals and reconsiderations](https://www.uhcprovider.com/en/claims-payments-billing/appeals.html)

<a id="f15"></a>
## F15 — Recorded authorization status

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O01 Provider authorization / precertification specialist](roles/O01.md) → [O05 Scheduler / procedure coordinator](roles/O05.md)

**Condition:** When scheduling depends on status

**Suggested identifying/content fields:**

- Service.
- Case.
- Outcome/conditions.
- Remaining prerequisites.

**Acknowledgement/completion evidence:** Scheduler records booking or unresolved status

**If missing, rejected or inconsistent:** Do not equate booking and clinical readiness

**Evidence:** [R03: Mayo: Precertification and Authorization Representative](https://jobs.mayoclinic.org/job/rochester/precertification-and-authorization-rep-hybrid/33647/100997191200), [R05: Michigan: Patient Services Intermediate](https://careernavigator.umich.edu/job_detail/103767/patient-services-intermediate)

<a id="f16"></a>
## F16 — Appeal request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [P04 Appointed appeal representative](roles/P04.md) → [U12 Internal appeal / grievance coordinator](roles/U12.md)

**Condition:** Actual appeal rights and deadlines

**Suggested identifying/content fields:**

- Authority/standing.
- Challenged notice.
- Grounds.
- Supporting record.

**Acknowledgement/completion evidence:** Proper route/case acknowledgement

**If missing, rejected or inconsistent:** Resolve missing standing or wrong route

**Evidence:** [R20: HHS OMHA: right to representation](https://www.hhs.gov/about/agencies/omha/filing-an-appeal/your-right-to-representation/index.html), [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

<a id="f17"></a>
## F17 — MA reconsideration case

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U12 Internal appeal / grievance coordinator](roles/U12.md) → [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md)

**Condition:** MA route described by A03

**Suggested identifying/content fields:**

- Initial record.
- New material.
- Disputed question.
- Reviewer independence check.

**Acknowledgement/completion evidence:** Reconsideration assignment/decision

**If missing, rejected or inconsistent:** Use appropriate uninvolved physician for scoped medical-necessity reconsideration

**Evidence:** [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

<a id="f18"></a>
## F18 — Remaining adverse MA case

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md) → [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md)

**Condition:** When MA adverse reconsideration remains

**Suggested identifying/content fields:**

- Disputed issues.
- Case file.
- Written explanation.

**Acknowledgement/completion evidence:** IRE review/disposition recorded

**If missing, rejected or inconsistent:** Follow applicable forwarding and record requirements

**Evidence:** [A03: MA reconsideration independence and expertise](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590), [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592)

<a id="f19"></a>
## F19 — MA independent-review decision

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md) → [U09 Determination / notification coordinator](roles/U09.md)

**Condition:** MA decision and A16 conditions

**Suggested identifying/content fields:**

- Case.
- Outcome.
- Scope of reversal.
- Implementation requirement.

**Acknowledgement/completion evidence:** Effectuation status recorded/communicated

**If missing, rejected or inconsistent:** Escalate failure to implement to correct route

**Evidence:** [A04: MA independent entity reconsideration](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.592), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="f20"></a>
## F20 — Commercial external-review case

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U15 External-review administrator](roles/U15.md) → [U18 Applicable commercial independent-review organization reviewer](roles/U18.md)

**Condition:** Eligible commercial external-review process

**Suggested identifying/content fields:**

- Applicable route.
- Eligibility.
- Denial.
- Record.

**Acknowledgement/completion evidence:** External-review disposition

**If missing, rejected or inconsistent:** Do not route MA automatically here

**Evidence:** [A12: Applicable commercial external review](https://www.healthcare.gov/appeal-insurance-company-decision/external-review/), [R17: CMS: federal external review](https://www.cms.gov/cciio/programs-and-initiatives/consumer-support-and-information/csg-ext-appeals-facts)

<a id="f21"></a>
## F21 — Care-management goals and needs

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [P01 Patient / insured member](roles/P01.md) → [M01 Lead care manager / case manager](roles/M01.md)

**Condition:** Program/patient participation context

**Suggested identifying/content fields:**

- Patient goals.
- Preferences.
- Reported barriers.
- Involvement choices.

**Acknowledgement/completion evidence:** Needs reflected in coordination assessment

**If missing, rejected or inconsistent:** Clarify disagreement; do not invent consent

**Evidence:** [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R23: AHRQ-hosted care-management implementation guide](https://www.ahrq.gov/sites/default/files/wysiwyg/evidencenow/tools-and-materials/care-management-implementation-guide.pdf)

<a id="f22"></a>
## F22 — Clinical context / referral

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [C02 Referring / primary-care clinician](roles/C02.md) → [M01 Lead care manager / case manager](roles/M01.md)

**Condition:** When coordination referred/needed

**Suggested identifying/content fields:**

- Clinical plan.
- Responsible clinician.
- Relevant concerns.
- Follow-up needs.

**Acknowledgement/completion evidence:** Care-manager review and coordination task

**If missing, rejected or inconsistent:** Clarify missing medical ownership

**Evidence:** [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse)

<a id="f23"></a>
## F23 — Psychosocial resource referral

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M01 Lead care manager / case manager](roles/M01.md) → [M02 Medical social worker (credential-dependent practice)](roles/M02.md)

**Condition:** When appropriate social support needed

**Suggested identifying/content fields:**

- Specific need.
- Agreed information.
- Desired follow-up.

**Acknowledgement/completion evidence:** Assessment/resource response

**If missing, rejected or inconsistent:** Return unmet need to coordinator

**Evidence:** [R25: UCLA: clinical case managers](https://www.uclahealth.org/programs/ccsw/about-us/rn-clinical-case-managers), [B09: Social workers](https://www.bls.gov/ooh/community-and-social-service/social-workers.htm)

<a id="f24"></a>
## F24 — Medication review request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M01 Lead care manager / case manager](roles/M01.md) → [M04 Clinical / community pharmacist](roles/M04.md)

**Condition:** When medication review needed

**Suggested identifying/content fields:**

- Medication information.
- Clinical question.
- Responsible prescriber.

**Acknowledgement/completion evidence:** Pharmacist recommendation/clarification

**If missing, rejected or inconsistent:** Refer order changes to authorized prescriber/protocol

**Evidence:** [B07: Pharmacists](https://www.bls.gov/ooh/healthcare/pharmacists.htm), [R24: AHRQ PSNet: GRACE model](https://psnet.ahrq.gov/innovation/team-developed-care-plan-and-ongoing-care-management-social-workers-and-nurse)

<a id="f25"></a>
## F25 — Medication recommendation

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M04 Clinical / community pharmacist](roles/M04.md) → [C01 Ordering / treating physician](roles/C01.md)

**Condition:** Professional relationship/protocol-specific

**Suggested identifying/content fields:**

- Identified concern.
- Evidence.
- Recommendation.
- Urgency/context.

**Acknowledgement/completion evidence:** Prescriber response or authorized protocol action

**If missing, rejected or inconsistent:** Do not silently assume recommendation changed order

**Evidence:** [B07: Pharmacists](https://www.bls.gov/ooh/healthcare/pharmacists.htm), [A15: Hospital medical records](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.24)

<a id="f26"></a>
## F26 — Navigation task

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M01 Lead care manager / case manager](roles/M01.md) → [M10 Patient navigator](roles/M10.md)

**Condition:** When navigation assigned

**Suggested identifying/content fields:**

- Barrier.
- Patient preference.
- Service contact.
- Follow-up need.

**Acknowledgement/completion evidence:** Connection/status returned

**If missing, rejected or inconsistent:** Report unresolved access rather than assume success

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html)

<a id="f27"></a>
## F27 — Community service referral

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M10 Patient navigator](roles/M10.md) → [M22 Community resource / housing / food / benefit-support worker](roles/M22.md)

**Condition:** Agency-specific sharing and availability

**Suggested identifying/content fields:**

- Agreed need.
- Relevant eligibility information.
- Contact.

**Acknowledgement/completion evidence:** Service acceptance/status

**If missing, rejected or inconsistent:** Notify coordinator of waiting/refusal/absence

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [R29: CDC: community health workers](https://www.cdc.gov/chronic-disease/php/community-health-worker-resources/index.html), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html)

<a id="f28"></a>
## F28 — Transport arrangement

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M01 Lead care manager / case manager](roles/M01.md) → [M23 Transportation coordinator / dispatcher](roles/M23.md)

**Condition:** When travel support needed

**Suggested identifying/content fields:**

- Appointment/trip.
- Contact.
- Accessibility needs.

**Acknowledgement/completion evidence:** Booking status returned

**If missing, rejected or inconsistent:** Clarify clinical transport needs

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [B19: Home health and personal care aides](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm)

<a id="f29"></a>
## F29 — Assigned transport

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M23 Transportation coordinator / dispatcher](roles/M23.md) → [M24 Transport driver / service-delivery worker](roles/M24.md)

**Condition:** Actual service qualification and permissions

**Suggested identifying/content fields:**

- Pickup/destination.
- Time/contact.
- Necessary access instructions.

**Acknowledgement/completion evidence:** Completion/failure status

**If missing, rejected or inconsistent:** Notify dispatcher of failed trip

**Evidence:** [R28: CDC: patient navigation](https://www.cdc.gov/cancer/php/interventions/patient-navigation.html), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html)

<a id="f30"></a>
## F30 — Equipment order

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [C01 Ordering / treating physician](roles/C01.md) → [M25 Equipment supplier / delivery or fitting staff](roles/M25.md)

**Condition:** Equipment-specific pathway

**Suggested identifying/content fields:**

- Patient.
- Ordered equipment.
- Clinical/order author.
- Requirements.

**Acknowledgement/completion evidence:** Supplier acceptance/service status

**If missing, rejected or inconsistent:** Resolve missing order or unsuitable service with clinician

**Evidence:** [R11: CMS: power mobility devices](https://www.cms.gov/medicare/payment/fee-schedules/durable-medical-equipment-prosthetic-devices-prosthetics-orthotics-supplies/power-mobility-devices), [R30: Medicare: home health services](https://www.medicare.gov/coverage/home-health-services)

<a id="f31"></a>
## F31 — Home-health transition referral

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M18 Discharge planner / transitions coordinator](roles/M18.md) → [M19 Home-health intake / coordination clinician](roles/M19.md)

**Condition:** Hospital transition plus home-health setting

**Suggested identifying/content fields:**

- Clinical course.
- Goals/preferences.
- Orders/plan.
- Pending needs.

**Acknowledgement/completion evidence:** Agency acceptance/capacity and plan coordination

**If missing, rejected or inconsistent:** Return unavailable service or missing order

**Evidence:** [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43), [A07: Home-health plan and coordination](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60)

<a id="f32"></a>
## F32 — Facility transition record

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M18 Discharge planner / transitions coordinator](roles/M18.md) → [M20 Skilled-nursing / rehabilitation receiving-team coordinator](roles/M20.md)

**Condition:** Hospital to receiving facility

**Suggested identifying/content fields:**

- Clinical course.
- Goals.
- Relevant care needs.
- Pending issues.

**Acknowledgement/completion evidence:** Receiving service acceptance/handoff

**If missing, rejected or inconsistent:** Resolve missing/unavailable care with sending team

**Evidence:** [A06: Hospital discharge planning](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-482/subpart-C/section-482.43)

<a id="f33"></a>
## F33 — Home-health change request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M19 Home-health intake / coordination clinician](roles/M19.md) → [C01 Ordering / treating physician](roles/C01.md)

**Condition:** 484.60 setting and signatory rules

**Suggested identifying/content fields:**

- Changed assessment.
- Need/response.
- Proposed plan revision.

**Acknowledgement/completion evidence:** Authorized response and plan communication

**If missing, rejected or inconsistent:** Do not freely rewrite orders

**Evidence:** [A07: Home-health plan and coordination](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-484/subpart-B/section-484.60)

<a id="f34"></a>
## F34 — Home-support observations

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M21 Home-health aide / personal-care worker](roles/M21.md) → [C06 Registered nurse providing direct care](roles/C06.md)

**Condition:** Actual home-aide supervision

**Suggested identifying/content fields:**

- Assigned task.
- Completion.
- Observed concern.

**Acknowledgement/completion evidence:** Qualified review/escalation

**If missing, rejected or inconsistent:** Use supervising professional for concern outside training

**Evidence:** [B19: Home health and personal care aides](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm), [B04: Registered nurses](https://www.bls.gov/ooh/healthcare/registered-nurses.htm)

<a id="f35"></a>
## F35 — Functional progress

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M14 Physical therapist](roles/M14.md) → [M01 Lead care manager / case manager](roles/M01.md)

**Condition:** When PT involved

**Suggested identifying/content fields:**

- Assessment.
- Goals.
- Response.
- Unresolved needs.

**Acknowledgement/completion evidence:** Coordination plan updated

**If missing, rejected or inconsistent:** Route medical or resource issue to owner

**Evidence:** [B15: Physical therapists](https://www.bls.gov/ooh/healthcare/physical-therapists.htm), [R22: AHRQ: care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html)

<a id="f36"></a>
## F36 — Complex-case escalation

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [M01 Lead care manager / case manager](roles/M01.md) → [G05 Clinical / case-management supervisor](roles/G05.md)

**Condition:** Assigned supervisory relationship only

**Suggested identifying/content fields:**

- Unmet need.
- Actions attempted.
- Clinical/resource question.

**Acknowledgement/completion evidence:** Assigned supervisory response

**If missing, rejected or inconsistent:** Separate clinical authority from workload decision

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="f37"></a>
## F37 — Policy-quality finding

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [G06 Quality-improvement / audit professional](roles/G06.md) → [G03 UM / medical-policy committee and specialty members](roles/G03.md)

**Condition:** When systemic criteria issue identified

**Suggested identifying/content fields:**

- Pattern.
- Measure/record basis.
- Policy version.
- Limitations.

**Acknowledgement/completion evidence:** Policy review/revision disposition

**If missing, rejected or inconsistent:** Do not retroactively change case evidence

**Evidence:** [A05: Medicare Advantage UM committee](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-C/section-422.137), [R12: Martin's Point: medical necessity criteria](https://martinspoint.org/-/media/Providers/Documents/Clinical-Documentation/Medical-Necessity-Criteria-Standard.ashx)

<a id="f38"></a>
## F38 — Approved procedural change

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [G08 Policy analyst / clinical regulatory adviser](roles/G08.md) → [G07 Trainer / clinical educator](roles/G07.md)

**Condition:** Designated approval/change process

**Suggested identifying/content fields:**

- Approved version.
- Effective scope.
- Training implications.

**Acknowledgement/completion evidence:** Training updated and delivered

**If missing, rejected or inconsistent:** Do not teach draft as approved policy

**Evidence:** [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="f39"></a>
## F39 — Access authorization decision

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [G10 Privacy officer / HIM privacy specialist](roles/G10.md) → [G14 Identity / portal-access administrator](roles/G14.md)

**Condition:** Authorized local access-control process

**Suggested identifying/content fields:**

- User/role.
- Purpose.
- Permitted scope.
- Approval.

**Acknowledgement/completion evidence:** Access provisioning/audit result

**If missing, rejected or inconsistent:** Escalate unmatched permissions

**Evidence:** [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm)

<a id="f40"></a>
## F40 — Approved system requirements

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [G12 Business / workflow analyst](roles/G12.md) → [G13 EHR / clinical informatics / application-support professional](roles/G13.md)

**Condition:** Authorized change process

**Suggested identifying/content fields:**

- Business owner.
- Intended behavior.
- Permissions.
- Acceptance conditions.

**Acknowledgement/completion evidence:** Validated implementation or rejected change

**If missing, rejected or inconsistent:** Clinical/policy owner resolves substantive ambiguity

**Evidence:** [B21: Health information technologists](https://www.bls.gov/ooh/healthcare/health-information-technologists-and-medical-registrars.htm), [R32: Partnership HealthPlan: 2026 care-coordination program](https://www.partnershiphp.org/Providers/HealthServices/Documents/Physicians_Advisory_Committee_PAC/2026/04-April/Policy_Summary/Care_Coordination/MPCD2013_clean.pdf)

<a id="f41"></a>
## F41 — Supported claim coding

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O07 Medical coding specialist](roles/O07.md) → [G15 Billing / patient accounts / claim-denial worker](roles/G15.md)

**Condition:** Downstream billing, not authorization completion

**Suggested identifying/content fields:**

- Service/documentation.
- Supported codes.
- Relevant clarification.

**Acknowledgement/completion evidence:** Claim/account work recorded

**If missing, rejected or inconsistent:** Return unsupported code or documentation issue

**Evidence:** [B20: Medical records specialists](https://www.bls.gov/ooh/healthcare/medical-records-and-health-information-technicians.htm), [R08: AHIMA: denials-management toolkit announcement](https://journal.ahima.org/AMP_EDN/383/AHIMA-Releases-Denials-Management-Toolkit-1776.amp.html)

<a id="f42"></a>
## F42 — Eligible MA further appeal record

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md) → [J01 MA administrative law judge / applicable adjudicator](roles/J01.md)

**Condition:** When further MA appeal is available

**Suggested identifying/content fields:**

- Prior decision.
- Proper request.
- Record.
- Jurisdiction conditions.

**Acknowledgement/completion evidence:** Adjudicative disposition

**If missing, rejected or inconsistent:** No automatic right inferred from dissatisfaction

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="f43"></a>
## F43 — Eligible Council review

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [J01 MA administrative law judge / applicable adjudicator](roles/J01.md) → [J02 Medicare Appeals Council reviewer](roles/J02.md)

**Condition:** When Council review properly pursued

**Suggested identifying/content fields:**

- Prior decision.
- Eligible request.
- Record.

**Acknowledgement/completion evidence:** Council disposition

**If missing, rejected or inconsistent:** Follow actual review notice/rules

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview), [A16: MA effectuation of decisions](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.618)

<a id="f44"></a>
## F44 — Eligible judicial review

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [J02 Medicare Appeals Council reviewer](roles/J02.md) → [J03 Federal district court in an eligible Medicare appeal](roles/J03.md)

**Condition:** When judicial review legally available

**Suggested identifying/content fields:**

- Administrative record.
- Eligible filing.
- Legal issues.

**Acknowledgement/completion evidence:** Judicial disposition

**If missing, rejected or inconsistent:** Check jurisdiction/exhaustion/thresholds

**Evidence:** [A11: Medicare Advantage appeal levels](https://www.cms.gov/medicare/appeals-grievances/managed-care-appeals-grievances/appeals-overview)

<a id="f45"></a>
## F45 — Interpreted patient-clinician message

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [P05 Healthcare interpreter / communication-access professional](roles/P05.md) → [C01 Ordering / treating physician](roles/C01.md)

**Condition:** When qualified interpretation needed

**Suggested identifying/content fields:**

- Original meaning.
- Relevant clarification.
- Communication context.

**Acknowledgement/completion evidence:** Participants can clarify meaning

**If missing, rejected or inconsistent:** Return substantive question to patient/clinician

**Evidence:** [B23: Interpreters and translators](https://www.bls.gov/ooh/media-and-communication/interpreters-and-translators.htm), [R21: HHS: telehealth communication access](https://www.hhs.gov/civil-rights/for-individuals/disability/guidance-on-nondiscrimination-in-telehealth/index.html)

<a id="f46"></a>
## F46 — Unclear disclosure request

**Evidence status:** SYNTHESIZED MODEL: artifact fields, contacts and routing NOT CONFIRMED as a real institution's procedure.

**From → to:** [O06 HIM / release-of-information specialist](roles/O06.md) → [G10 Privacy officer / HIM privacy specialist](roles/G10.md)

**Condition:** When release authority/purpose unclear

**Suggested identifying/content fields:**

- Request/purpose.
- Identity/authority.
- Specific privacy question.

**Acknowledgement/completion evidence:** Scoped privacy guidance

**If missing, rejected or inconsistent:** Do not release all data from uncertainty

**Evidence:** [A09: Personal representative authority](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/personal-representatives/index.html), [A10: Minimum necessary and treatment exception](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html), [R07: AHIMA: evolving ROI training](https://journal.ahima.org/page/ensure-roi-training-evolves-as-the-industry-changes)
