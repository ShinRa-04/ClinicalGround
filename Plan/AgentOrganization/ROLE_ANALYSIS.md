# Analysis of all 97 functions

These are conditional organizational-design judgments, not verified assignments for every benchmark task or permission grants. All 97 functions are accounted for once in a primary work package. A profile can be an external interface, role mode, capability or composite rather than a separate running agent. No runtime benefit is established.

[Main analysis](ANALYSIS.md) · [Work packages](WORK_PACKAGES.md) · [Questions](QUESTIONS.md) · [Original audited roles](../HealthcareRoles/ROLE_INDEX.md)

| Role | Proposed representation | Primary package | Specific question |
| --- | --- | --- | --- |
| [P01 Patient / insured member](roles/P01.md) | external_actor | [W01](WORK_PACKAGES.md#w01) | Whose expressed preference is being recorded, and what observation establishes it? |
| [P02 Informal caregiver / family support person](roles/P02.md) | external_actor | [W01](WORK_PACKAGES.md#w01) | Is this statement a caregiver observation or the patient’s own choice? |
| [P03 Legally recognized personal representative](roles/P03.md) | external_actor | [W01](WORK_PACKAGES.md#w01) | What establishes this representative’s authority for this specific decision? |
| [P04 Appointed appeal representative](roles/P04.md) | external_actor | [W02](WORK_PACKAGES.md#w02) | Does the appointment cover this dispute, this action and this stage? |
| [P05 Healthcare interpreter / communication-access professional](roles/P05.md) | communication_adapter | [W03](WORK_PACKAGES.md#w03) | Does the interpreter preserve speaker attribution and unanswered questions? |
| [P06 Healthcare translator](roles/P06.md) | communication_adapter | [W03](WORK_PACKAGES.md#w03) | Can the written output be checked for omissions, negation and ambiguity? |
| [P07 Patient-relations advocate](roles/P07.md) | external_actor | [W02](WORK_PACKAGES.md#w02) | Is this an access complaint, clinical issue or formal appeal? |
| [C01 Ordering / treating physician](roles/C01.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Which clinical facts/orders were actually authored by the treating professional? |
| [C02 Referring / primary-care clinician](roles/C02.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Does the referral establish an indication, an order, or only a request for evaluation? |
| [C03 Treating / performing specialist](roles/C03.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | What specialty evidence is available and which missing assessment needs an external contribution? |
| [C04 Nurse practitioner](roles/C04.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Which jurisdiction, practice category, furnishing authority and employer conditions apply? |
| [C05 Physician assistant / associate (jurisdiction-specific title)](roles/C05.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Does the applicable arrangement require supervision, collaboration or another defined condition? |
| [C06 Registered nurse providing direct care](roles/C06.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Is the task nursing assessment, care coordination or direct service documentation? |
| [C07 Licensed practical / vocational nurse](roles/C07.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | What activity is permitted under the actual license and supervision arrangement? |
| [C08 Medical assistant / clinical-support assistant](roles/C08.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Which administrative/support observation needs review by an authorized clinician? |
| [O01 Provider authorization / precertification specialist](roles/O01.md) | task_scoped_worker | [W05](WORK_PACKAGES.md#w05) | What observable event shows the supported request was submitted and what remains unresolved? |
| [O02 Referral coordinator](roles/O02.md) | role_mode | [W05](WORK_PACKAGES.md#w05) | Who owns the unanswered referral and what shows it reached the receiver? |
| [O03 Registration / patient-access representative](roles/O03.md) | tool_supported_mode | [W05](WORK_PACKAGES.md#w05) | Which identifiers prove the evidence and task concern the same case? |
| [O04 Provider insurance-verification / benefits specialist](roles/O04.md) | role_mode | [W05](WORK_PACKAGES.md#w05) | Is this a benefit fact, an authorization requirement or a guarantee of payment? |
| [O05 Scheduler / procedure coordinator](roles/O05.md) | role_mode | [W05](WORK_PACKAGES.md#w05) | What prerequisites and actual capacity must be satisfied before booking? |
| [O06 HIM / release-of-information specialist](roles/O06.md) | bounded_capability | [W06](WORK_PACKAGES.md#w06) | What records may be released for this purpose and who authored them? |
| [O07 Medical coding specialist](roles/O07.md) | bounded_capability | [W06](WORK_PACKAGES.md#w06) | Does a code reflect supplied documentation or an unsupported diagnostic inference? |
| [O08 Clinical-documentation-integrity specialist](roles/O08.md) | bounded_capability | [W06](WORK_PACKAGES.md#w06) | Should an inconsistency trigger a clarification query rather than an automated repair? |
| [O09 Financial counselor / assistance specialist](roles/O09.md) | role_mode | [W05](WORK_PACKAGES.md#w05) | Which affordability barrier and assistance option are actually supported? |
| [O10 Provider denial / appeal specialist](roles/O10.md) | task_scoped_worker | [W07](WORK_PACKAGES.md#w07) | Which dispute route preserves the correct issue, standing and filing status? |
| [O11 Provider physician adviser / peer-discussion clinician](roles/O11.md) | external_actor | [W07](WORK_PACKAGES.md#w07) | What actual clinician contribution is required for this peer exchange? |
| [O12 Practice / patient-access supervisor](roles/O12.md) | configuration_or_escalation | [W05](WORK_PACKAGES.md#w05) | Is the issue workload/process authority or a substantive clinical/coverage decision? |
| [O13 External diagnostic / clinical evidence author or custodian](roles/O13.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Can the result be traced to an actual test, assessor, document or custodian? |
| [U01 Payer UM intake coordinator](roles/U01.md) | task_scoped_worker | [W08](WORK_PACKAGES.md#w08) | Is this collection/routing or an explicitly delegated limited nonclinical decision? |
| [U02 Payer eligibility / benefit specialist](roles/U02.md) | role_mode | [W08](WORK_PACKAGES.md#w08) | Which product/eligibility facts authorize this particular administrative outcome? |
| [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md) | task_scoped_review_mode | [W09](WORK_PACKAGES.md#w09) | What can the initial reviewer conclude versus recommend or escalate? |
| [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md) | task_scoped_review_mode | [W09](WORK_PACKAGES.md#w09) | Which case decision is authorized, and is this person/function initial reviewer or reconsiderer? |
| [U05 Independent clinical / specialty consultant](roles/U05.md) | bounded_specialist | [W09](WORK_PACKAGES.md#w09) | Is the consultant offering evidence/advice or issuing the authoritative determination? |
| [U06 Payer behavioral-health reviewer](roles/U06.md) | bounded_specialist | [W09](WORK_PACKAGES.md#w09) | Does the service require behavioral-health criteria or restricted evidence handling? |
| [U07 Managed-care pharmacist / pharmacy reviewer](roles/U07.md) | bounded_specialist | [W09](WORK_PACKAGES.md#w09) | Is this pharmacy coverage review, medication advice or treatment authority? |
| [U08 Delegated medical-group / review-vendor reviewer](roles/U08.md) | delegation_boundary | [W09](WORK_PACKAGES.md#w09) | What is delegated for this product, including what is expressly retained by the plan? |
| [U09 Determination / notification coordinator](roles/U09.md) | controlled_operation | [W10](WORK_PACKAGES.md#w10) | Does the notice exactly correspond to the stored decision, version and recipient? |
| [U10 Member-services representative](roles/U10.md) | role_mode | [W08](WORK_PACKAGES.md#w08) | What status can be truthfully explained from the current authoritative record? |
| [U11 Provider-services representative](roles/U11.md) | role_mode | [W08](WORK_PACKAGES.md#w08) | What does the provider need to supply or do next, and is that an observed requirement? |
| [U12 Internal appeal / grievance coordinator](roles/U12.md) | task_scoped_worker | [W11](WORK_PACKAGES.md#w11) | Is the submission a grievance, reconsideration, external request or another route? |
| [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md) | protected_review | [W11](WORK_PACKAGES.md#w11) | How is uninvolved review established beyond using a different prompt? |
| [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md) | external_review_actor | [W12](WORK_PACKAGES.md#w12) | What actual CMS-contracted review outcome and route apply? |
| [U15 External-review administrator](roles/U15.md) | external_route_adapter | [W12](WORK_PACKAGES.md#w12) | Which state/federal process and eligibility govern the external-review request? |
| [U16 SHIP / consumer-assistance / ombudsman counselor](roles/U16.md) | external_actor | [W02](WORK_PACKAGES.md#w02) | Does the assistance function inform, represent, or decide the matter? |
| [U17 UM manager / operational supervisor](roles/U17.md) | configuration_or_escalation | [W08](WORK_PACKAGES.md#w08) | Can a process manager resolve this queue issue without changing clinical judgment? |
| [U18 Applicable commercial independent-review organization reviewer](roles/U18.md) | external_review_actor | [W12](WORK_PACKAGES.md#w12) | Does this issue qualify for the applicable commercial external route, including urgent concurrency? |
| [M01 Lead care manager / case manager](roles/M01.md) | task_scoped_worker | [W13](WORK_PACKAGES.md#w13) | What unresolved patient goal or service obligation still has a named owner? |
| [M02 Medical social worker (credential-dependent practice)](roles/M02.md) | bounded_specialist | [W14](WORK_PACKAGES.md#w14) | What social-work function and credential level are actually relevant? |
| [M03 Licensed clinical social worker](roles/M03.md) | external_actor | [W14](WORK_PACKAGES.md#w14) | Is the requested contribution clinical social-work assessment/therapy or practical resource coordination? |
| [M04 Clinical / community pharmacist](roles/M04.md) | bounded_specialist | [W15](WORK_PACKAGES.md#w15) | Which medication action is advice, protocol-authorized activity or a new order? |
| [M05 Pharmacy technician / medication-access coordinator](roles/M05.md) | role_mode | [W15](WORK_PACKAGES.md#w15) | What access/fulfillment information is missing without requiring clinical medication decisions? |
| [M06 Treating psychiatrist](roles/M06.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | What psychiatric assessment/order is present versus needing an external clinician? |
| [M07 Clinical psychologist](roles/M07.md) | bounded_specialist | [W14](WORK_PACKAGES.md#w14) | Does this contribution require ordinary psychology scope or additional prescribing certification? |
| [M08 Licensed behavioral-health / substance-use counselor](roles/M08.md) | external_actor | [W14](WORK_PACKAGES.md#w14) | What counseling function and restricted-record conditions apply to this service? |
| [M09 Community health worker](roles/M09.md) | role_mode | [W13](WORK_PACKAGES.md#w13) | Which practical barrier comes from the patient/community context rather than chart inference? |
| [M10 Patient navigator](roles/M10.md) | role_mode | [W13](WORK_PACKAGES.md#w13) | What obstacle is being navigated and which recipient owns the next response? |
| [M11 Health-care guide / nonclinical care guide](roles/M11.md) | role_mode | [W13](WORK_PACKAGES.md#w13) | Which task is nonclinical support and which needs clinical interpretation? |
| [M12 Registered dietitian / qualified nutrition professional](roles/M12.md) | bounded_specialist | [W16](WORK_PACKAGES.md#w16) | What nutrition assessment or plan contribution is actually evidenced? |
| [M13 Health educator / self-management coach](roles/M13.md) | role_mode | [W13](WORK_PACKAGES.md#w13) | Does education reflect an existing plan and the person’s stated understanding? |
| [M14 Physical therapist](roles/M14.md) | bounded_specialist | [W16](WORK_PACKAGES.md#w16) | Which mobility/rehabilitation facts support this referral and what local access rule is unknown? |
| [M15 Occupational therapist](roles/M15.md) | bounded_specialist | [W16](WORK_PACKAGES.md#w16) | What daily-activity/environment assessment differs from mobility-only evidence? |
| [M16 Speech-language pathologist](roles/M16.md) | bounded_specialist | [W16](WORK_PACKAGES.md#w16) | Is the need communication, swallowing or another documented function requiring the right evidence? |
| [M17 Respiratory therapist](roles/M17.md) | bounded_specialist | [W16](WORK_PACKAGES.md#w16) | What respiratory assessment/instruction is present and which service needs professional input? |
| [M18 Discharge planner / transitions coordinator](roles/M18.md) | role_mode | [W13](WORK_PACKAGES.md#w13) | Which transition tasks are complete, and what clinical discharge authority is outside coordination? |
| [M19 Home-health intake / coordination clinician](roles/M19.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | Has the receiving home-health service accepted the referral and documented its actual prerequisites? |
| [M20 Skilled-nursing / rehabilitation receiving-team coordinator](roles/M20.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | What shows receiving-facility acceptance, capacity and handoff acknowledgement? |
| [M21 Home-health aide / personal-care worker](roles/M21.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | What evidence shows personal-care work actually occurred rather than being arranged? |
| [M22 Community resource / housing / food / benefit-support worker](roles/M22.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | Which resource is eligible, available and actually accepted for this person? |
| [M23 Transportation coordinator / dispatcher](roles/M23.md) | role_mode | [W17](WORK_PACKAGES.md#w17) | Is the trip merely requested, confirmed, dispatched or completed? |
| [M24 Transport driver / service-delivery worker](roles/M24.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | What observation establishes pickup, delivery or a failed trip? |
| [M25 Equipment supplier / delivery or fitting staff](roles/M25.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | What confirms supply, delivery/fitting and any required receiving acknowledgement? |
| [M26 Infusion / other receiving-service coordinator](roles/M26.md) | external_service_actor | [W17](WORK_PACKAGES.md#w17) | Which receiving-service acceptance, scheduling and clinical prerequisites remain outstanding? |
| [M27 Palliative-care clinical team member](roles/M27.md) | external_actor | [W04](WORK_PACKAGES.md#w04) | Which palliative contribution is relevant without assuming hospice enrollment? |
| [M28 Hospice interdisciplinary group and attending functions (distinct roles)](roles/M28.md) | composite_external_functions | [W18](WORK_PACKAGES.md#w18) | Which IDG, RN coordination, attending, certification or admission function is needed? |
| [M29 Chaplain / spiritual-care professional](roles/M29.md) | external_actor | [W18](WORK_PACKAGES.md#w18) | What spiritual support did the person request or accept? |
| [M30 Administrative care coordinator / scheduling support](roles/M30.md) | role_mode | [W13](WORK_PACKAGES.md#w13) | Which scheduling/follow-up task can be closed with an observed response? |
| [M31 Safeguarding / protection-service professional](roles/M31.md) | external_actor | [W19](WORK_PACKAGES.md#w19) | Which actual protection pathway, jurisdiction and mandate must be established? |
| [G01 Provider medical director / chief medical officer](roles/G01.md) | governance_interface | [W20](WORK_PACKAGES.md#w20) | Is this a provider governance mandate or a case-level treating/review function? |
| [G02 Payer medical director / clinical-program leader](roles/G02.md) | governance_interface | [W20](WORK_PACKAGES.md#w20) | Is the action policy/program oversight or a separately assigned case determination? |
| [G03 UM / medical-policy committee and specialty members](roles/G03.md) | governance_interface | [W20](WORK_PACKAGES.md#w20) | Which policy/version was actually approved by the relevant process? |
| [G04 Care-management director / manager](roles/G04.md) | configuration_or_escalation | [W21](WORK_PACKAGES.md#w21) | What management decision concerns assignment/process rather than clinical override? |
| [G05 Clinical / case-management supervisor](roles/G05.md) | configuration_or_escalation | [W21](WORK_PACKAGES.md#w21) | Which supervision relationship and professional scope are actually documented? |
| [G06 Quality-improvement / audit professional](roles/G06.md) | development_capability | [W21](WORK_PACKAGES.md#w21) | Is this an internal quality check, an independent review or the official benchmark result? |
| [G07 Trainer / clinical educator](roles/G07.md) | development_capability | [W21](WORK_PACKAGES.md#w21) | Which observed failure justifies a reusable instruction change? |
| [G08 Policy analyst / clinical regulatory adviser](roles/G08.md) | bounded_capability | [W20](WORK_PACKAGES.md#w20) | Is a retrieved rule current/applicable, a draft interpretation or an approved controlling policy? |
| [G09 Compliance / regulatory professional](roles/G09.md) | governance_interface | [W20](WORK_PACKAGES.md#w20) | What requirement applies to the actual product/setting and what remains unverified? |
| [G10 Privacy officer / HIM privacy specialist](roles/G10.md) | configuration_or_escalation | [W22](WORK_PACKAGES.md#w22) | What purpose, recipient and protected material determine this information view? |
| [G11 Health-services / population-health data analyst](roles/G11.md) | development_capability | [W21](WORK_PACKAGES.md#w21) | Which aggregate outcome metric is observed rather than inferred from a role narrative? |
| [G12 Business / workflow analyst](roles/G12.md) | development_capability | [W21](WORK_PACKAGES.md#w21) | Which process bottleneck is supported by measured traces rather than a diagram edge? |
| [G13 EHR / clinical informatics / application-support professional](roles/G13.md) | infrastructure | [W22](WORK_PACKAGES.md#w22) | Does a technical operation alter presentation, access or substantive clinical state? |
| [G14 Identity / portal-access administrator](roles/G14.md) | infrastructure | [W22](WORK_PACKAGES.md#w22) | Which identity and tool permission are granted for this exact task principal? |
| [G15 Billing / patient accounts / claim-denial worker](roles/G15.md) | external_service_actor | [W23](WORK_PACKAGES.md#w23) | Which payment/claim event is actually in scope and observed? |
| [G16 Regulator / oversight official](roles/G16.md) | external_review_actor | [W12](WORK_PACKAGES.md#w12) | What oversight power and case route are actually invoked? |
| [G17 Legal adviser / specialist legal representative](roles/G17.md) | governance_interface | [W20](WORK_PACKAGES.md#w20) | Is this administrative assistance, legal analysis or actual authorized representation? |
| [J01 MA administrative law judge / applicable adjudicator](roles/J01.md) | external_review_actor | [W12](WORK_PACKAGES.md#w12) | Are this appeal’s jurisdiction and procedural prerequisites established? |
| [J02 Medicare Appeals Council reviewer](roles/J02.md) | external_review_actor | [W12](WORK_PACKAGES.md#w12) | What actual Council review/disposition is available for this case? |
| [J03 Federal district court in an eligible Medicare appeal](roles/J03.md) | external_review_actor | [W12](WORK_PACKAGES.md#w12) | Which judicial prerequisites and actual disposition are established? |
