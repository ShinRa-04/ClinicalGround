"""Research-agent-authored adjudication basis; not independent human clinical/legal review."""

REVIEWS={}


def reviewed(id, evidence, duty_verdict, rationale, alternatives, complexity, duty_exceptions=None):
    REVIEWS[id]=dict(evidence=[tuple(x.split('|',1)) for x in evidence.split(';;')],
        duty_verdict=duty_verdict,rationale=rationale,alternatives=alternatives,
        complexity=complexity,duty_exceptions=duty_exceptions or {})


reviewed('P01','A01|right to make informed decisions;;R22|needs and preferences','SUPPORTED_WITHIN_SCOPE',
 'Patient participation and informed choices are directly described; reporting history/barriers is coordination context rather than a universal mandatory patient duty.',
 'Patient may participate directly or through a lawful representative where applicable.',
 'Patient rights do not create entitlement to inappropriate treatment; capacity, minors and emergency rules require case-specific law.',
 {1:'SUPPORTED_CONTEXTUAL: giving history is a care-assessment input, not a legally compulsory duty.',3:'SUPPORTED_CONTEXTUAL: communication of acceptance/refusal derives from rights; no prescribed wording/form is established.'})
reviewed('P02','A09|family members;;R30|caregiver','SUPPORTED_CONTEXTUAL',
 'Guidance recognizes people involved in care and caregiver education. The particular practical tasks are illustrative, not a verified mandatory family job.',
 'Paid carers, family, friends, or no informal caregiver; patient wishes and lawful involvement control.',
 'Being helpful or related does not by itself establish access to all records or substitute decision authority.')
reviewed('P03','A09|scope;;A09|abuse','SUPPORTED_WITHIN_SCOPE',
 'HHS explicitly ties representation and relevant information rights to the authority under applicable law and describes exceptions.',
 'Broad healthcare authority or limited task/treatment authority; different rules for minors.',
 'Authority can be limited and safety exceptions exist. No universal national family-priority order is established.')
reviewed('P04','R20|appointment;;R15|assignment of benefits','SUPPORTED_WITHIN_SCOPE',
 'Appointment and scope requirements are directly documented in the Medicare representation guidance; provider benefits assignment is distinct.',
 'Self-representation, appointed lay representative or qualified professional under the actual route.',
 'An appeal appointment does not establish treatment proxy authority; filing/standing details differ by product.')
reviewed('P05','B23|Render spoken messages;;R21|interpreter','SUPPORTED_GENERAL_DESCRIPTION',
 'Government descriptions distinguish accurate interpretation and access assistance from substantive clinical decision-making.',
 'Spoken-language or signed interpretation; other accessible communication support where appropriate.',
 'Qualification, language and communication needs matter; no independent medical decision is conferred by interpreting.')
reviewed('P06','B23|written communication;;B23|source language','SUPPORTED_GENERAL_DESCRIPTION',
 'Written translation is distinct from interpretation; fidelity of content is supported. Escalation of ambiguous wording is a proposed quality-control action.',
 'One worker may perform both functions if qualified, but the skills remain distinct.',
 'Producing a translation does not demonstrate comprehension or valid consent.',
 {3:'INTERPRETATION: flagging source ambiguity is a reasonable quality-control recommendation, not a verified employer procedure.'})
reviewed('P07','R04|Patient Relations;;A01|grievance','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The hospital example describes patient-concern handling; federal hospital grievance requirements support a route distinct from coverage appeals.',
 'Patient relations, grievance office, navigator or other designated function; not always a separate advocate.',
 'Patient advocacy title alone does not confer legal representation or power to reverse coverage.')
reviewed('C01','B01|Take a patient;;B01|Recommend, design;;A15|authenticated','SUPPORTED_GENERAL_DESCRIPTION',
 'History/examination, tests, documentation, treatment recommendations and patient questions appear in physician duties; authentication is setting-specific.',
 'Ordering and treating roles may coincide; another authorized profession may order permitted services.',
 'Clinical recommendation, patient participation and coverage are separate functions; privileges and jurisdiction remain local facts.')
reviewed('C02','B01|Family medicine;;R22|referral','SUPPORTED_CONTEXTUAL',
 'Primary-care and coordination sources support continuity/referral work. This is a function across several professions, not a new universal credential.',
 'Physician, NP or PA may perform the function within their actual scope; the referrer and treating clinician may be the same person.',
 'A referral is not insurance authorization; receiving-specialist input does not prove a universal reporting hierarchy.')
reviewed('C03','B01|specialize;;R22|Specialists','SUPPORTED_GENERAL_DESCRIPTION',
 'Specialty clinical assessment and treatment are documented, while referral/return communication is supported as coordination.',
 'One specialist may order and perform a service; several specialists can contribute with separate responsibilities.',
 'Specialty expertise does not itself establish final signoff over every PCP decision or coverage.')
reviewed('C04','B03|scope of practice varies;;V02|103 NP;;V02|standardized procedures','SUPPORTED_CONDITIONAL',
 'Advanced practice duties are described generally; the California regulator gives concrete alternative practice categories and employer conditions.',
 'California traditional standardized-procedure practice, 103 category and 104 statutory pathway differ; other states have different arrangements.',
 'California page includes prospective/stale 104 availability wording. Its pathway description does not verify current certification of an individual or present application availability.')
reviewed('C05','B02|collaboration;;V03|collaboration agreement','SUPPORTED_CONDITIONAL',
 'Clinical PA duties have general support. Oregon demonstrates a collaboration framework and associate terminology, preventing a universal supervision inference.',
 'State-specific supervision/collaboration; Oregon requires a written agreement with physician or employer as described by its board.',
 'National occupational summaries are not substitutes for state practice law. Physician assistant/associate terminology itself varies.')
reviewed('C06','B04|Assess patients;;B04|Administer;;V10|prohibited','SUPPORTED_GENERAL_DESCRIPTION',
 'RN assessment, treatment, teaching, observation and communication are supported as general duties; task permission is constrained separately.',
 'Direct-care, UM and case-management RN functions differ despite the same underlying nursing credential.',
 'Assignment is not evidence of legal delegation; additional APRN authority cannot be inferred from RN status alone.')
reviewed('C07','B05|Monitor patients;;B05|vary;;V10|competence','SUPPORTED_CONDITIONAL',
 'Practical nursing tasks, reporting and state-dependent permissions are explicit in the occupational description and scope framework.',
 'LPN/LVN terminology and permitted procedures/supervision differ by jurisdiction and setting.',
 'No national assertion is made about IV therapy, independent assessment or direct supervision in a particular case.')
reviewed('C08','B06|administrative and clinical;;B02|do not practice medicine','SUPPORTED_CONDITIONAL',
 'Administrative support and permitted directed clinical tasks are described; this is explicitly distinct from PA clinical practice.',
 'Administrative-focused, clinical-focused or mixed assignments; permissible tasks differ by state/employer.',
 'Job assignment or training alone cannot establish every clinical permission.')

reviewed('O01','R04|obtaining prior authorizations;;R05|Obtain insurance approvals','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Accessible provider descriptions support assembling relevant record information, tracking requests and appeals. Expired Mayo R03 is not needed for support.',
 'Dedicated authorization specialist or a combined scheduling/referral position.',
 'Requests, receipt, approval, scheduling and delivery are distinct events; title alone does not grant clinical decision authority.')
reviewed('O02','R05|Referral/Authorization Coordinator;;R22|Referral staff','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Provider role description directly combines referrals with scheduling/authorization, and AHRQ explains information-loss risks across referrals.',
 'Combined role or separately staffed referral function.',
 'Closed-loop follow-up is a coordination recommendation, not a nationally prescribed form or signoff sequence.')
reviewed('O03','R04|Registers and schedules;;R06|verifies your insurance','SUPPORTED_CONTEXTUAL',
 'Registration and insurance verification are documented functions; resolving identity discrepancies is an operational safety interpretation.',
 'Registration, patient access and benefit verification may be split or combined.',
 'Actual identity-matching procedure and permitted correction rights are institution-specific.',
 {2:'MODEL_RECOMMENDATION: resolving mismatches is a proposed control; the exact institutional process is not documented here.'})
reviewed('O04','R06|verifies your insurance;;R05|insurance','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Provider sources directly distinguish eligibility/benefits and patient responsibility from authorization/payment.',
 'Dedicated benefits staff, registration staff or authorization worker may perform the function.',
 'Verification and cost estimates do not guarantee coverage or final payment; exact benefit interpretations require the plan.')
reviewed('O05','R05|scheduling;;R04|Provides scheduling','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Scheduling duties and coordination with clinicians/services are directly described; readiness gates are modeled, not an observed universal protocol.',
 'Standalone scheduler or combined referral/authorization worker.',
 'A booking is not proof of clinical readiness, consent, authorization or service completion.')
reviewed('O06','R07|ROI specialists;;B20|gatekeepers;;A10|treatment purposes','SUPPORTED_GENERAL_DESCRIPTION',
 'Record retrieval/disclosure roles are supported; HHS directly documents purpose-dependent minimum-necessary exceptions.',
 'Patient access, treatment, payment and other requests can have different permission rules.',
 'No blanket written-consent rule for every treatment disclosure; exceptions do not remove other privacy protections.')
reviewed('O07','B20|assign clinical codes;;R08|coding','SUPPORTED_GENERAL_DESCRIPTION',
 'Coding supported clinical information is directly documented; queries and clinician clarification are supported by the documentation example.',
 'Pre-service code clarification and downstream claim coding differ.',
 'Code assignment is not independent diagnosis or coverage adjudication.')
reviewed('O08','R08|clinical documentation;;A15|authenticated','SUPPORTED_HISTORICAL_EXAMPLE',
 'The accessible professional-association article supports CDI/coding collaboration in denial management. It is dated and is not a current mandatory local procedure.',
 'A dedicated CDI specialist or collaboration between clinicians and HIM/coding staff.',
 'Clinical author authentication and permitted correction remain setting-specific; clarification is not permission to invent diagnoses.')
reviewed('O09','R06|financial counselor;;R09|assistance','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Benefits explanation and assistance logistics are directly illustrated. R09 is an earlier retrieved historical example with fresh access failure recorded.',
 'Hospital financial counselor or medication-assistance staff/program.',
 'The counselor does not automatically decide assistance eligibility, benefit coverage or final claim payment.')
reviewed('O10','R04|appeals;;R08|appeals process;;R15|pre-service appeal','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The provider role supports authorization appeals and the professional article describes claims-denial work; the two must not be collapsed.',
 'Pre-service coverage challenge, correction/peer discussion or downstream claim appeal as applicable.',
 'Standing and representation need separate verification; a billing/appeal job title is not a patient appointment.')
reviewed('O11','R15|discussion;;R15|medical director','SUPPORTED_PROCESS_EXAMPLE',
 'Payer documentation supports clinician peer discussion and clarifies its relationship to pre-service appeal.',
 'Treating clinician or an appropriately assigned provider adviser; formal appeal remains a separate possible route.',
 'Payer-specific timing text differs between retrieved views. No deadline or preservation rule is inferred from a generic peer-discussion label.')
reviewed('O12','B22|Recruit, train;;R05|supervisor','SUPPORTED_GENERAL_DESCRIPTION',
 'Health-service management descriptions support operational staffing and supervision; exact escalation routing is a model.',
 'Practice management, centralized patient access or other assigned supervisory post.',
 'Operational reporting rank does not establish clinical license or insurer signoff authority.')
reviewed('O13','A15|authenticated;;B20|retrieve','COMPOSITE_FUNCTION_NOT_SINGLE_OCCUPATION',
 'Clinical report authors and record custodians have distinct evidenced functions. The combined profile is a modeling convenience, not one verified profession.',
 'Interpreting physician, diagnostic professional, therapist or records custodian depending on the evidence.',
 'The report author and person transmitting it may be different people with different permissions.')

reviewed('U01','R13|Non-clinical staff are responsible;;R13|Non-licensed personnel may','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The program explicitly assigns intake, data entry, information requests, routing and notification to nonclinical staff.',
 'The same program allows limited approvals under explicit criteria and assigned benefit-only actions; intake is not necessarily a no-decision clerical role.',
 'This is organization-specific delegation. Clinical medical-necessity denial is treated differently from benefit-only decisions; do not infer national authority.')
reviewed('U02','R13|eligibility and benefits;;R13|benefit only','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Administrative benefit evaluation and assigned benefit-only decisions are explicit in the program.',
 'Benefit verification without decision power, or delegated administrative approval/denial, depending on the assignment.',
 'A benefits title alone does not establish signatory power. Administrative coverage exclusions and clinical medical necessity need different reasoning/review.')
reviewed('U03','R12|first-level medical necessity;;R12|physician advisor;;R13|Licensed nurse reviewers','SUPPORTED_CONDITIONAL',
 'Clinical review/approval and escalation are directly described in example policies; profession alone does not establish authority for a particular product.',
 'First-level approval, clarification or escalation; some administrative decisions can be delegated without the same clinical review route.',
 'R13 contains both medical-director final responsibility and a wider professional-denial list; exact signing/review authority requires its specific policy/delegation and product.')
reviewed('U04','A02|must be reviewed by a physician;;R18|medical directors','SUPPORTED_WITHIN_SCOPE',
 'The MA requirement supports qualified initial review, while insurer material illustrates physician case-review functions.',
 'MA initial review may be by another appropriate licensed professional; a program may impose medical-director signoff beyond that minimum.',
 'Initial review, final institutional accountability and independent reconsideration are separate; medical director is not a universal superior over the treating clinician.')
reviewed('U05','R18|Independent Review;;R18|independent medical experts','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Insurer public material describes specialist expertise helping medical directors with complex cases.',
 'Internal consultant, contracted expert or a separately appointed decision-maker; statutory external review is a distinct role.',
 'The insurer page is undated and does not independently verify its current staffing/contracts. Consultant independence and final authority cannot be inferred from the name.')
reviewed('U06','R13|Designated Behavioral Healthcare Practitioner;;R13|behavioral healthcare denials','SUPPORTED_CONDITIONAL',
 'The program documents behavioral-health oversight and service-appropriate qualified review. Oversight and individual case decision authority must be distinguished.',
 'Different qualified professions may contribute depending on service, state and delegation.',
 'A designated behavioral program leader is not automatically the reviewer of every case; counselor, psychologist and physician qualifications are not interchangeable.')
reviewed('U07','R10|Prior Authorization;;R13|Pharmacists','SUPPORTED_CONDITIONAL',
 'The professional description supports medication-program review; the program example permits pharmacy-specific professional denial review.',
 'Pharmacist review/recommendation, protocol-based approval, or additional physician review according to the product.',
 'Do not apply a medical-service Part C appeal rule to every drug benefit. Coverage review and prescribing remain different authorities.')
reviewed('U08','R13|not delegated for processing;;R14|delegation','SUPPORTED_CONDITIONAL',
 'Delegation is documented but bounded: AZPC explicitly says it is not delegated to process, determine or notify appeals in the retrieved program.',
 'A vendor/group may handle initial UM while the health plan retains appeals, or have a different expressly documented delegation.',
 'The same organization cannot be assumed to own the whole workflow; professional license, contractual scope and product requirements all matter.')
reviewed('U09','R13|coordinating delivery of notifications;;R13|All denial communications','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Program duties and notice content are explicit. A notification task is not identical to making the substantive clinical decision.',
 'Notices may be sent through different permitted media and to different required recipients.',
 'Receipt, decision, dispatch and implementation are separate events. Actual timing/contents must be resolved for the route.')
reviewed('U10','R35|Medicare representative;;R32|Member Services','SUPPORTED_CONTEXTUAL',
 'Public help channels and plan member-services functions support explanation/navigation, but the detailed contact workflow is not independently established.',
 'Member services, clinical case team, dedicated appeals staff or public assistance channel may handle different questions.',
 'Access to a status screen does not establish authority to decide merits; no universal call-center delegation is confirmed.')
reviewed('U11','R15|Provider;;R32|Provider Services','SUPPORTED_CONTEXTUAL',
 'Provider-facing operational contact is documented, while the precise staff task allocation is a synthesized functional description.',
 'Provider services, UM intake or a delegated organization may be the contact.',
 'The correct counterparty and what it can decide must be confirmed for the actual case.')
reviewed('U12','A03|reconsideration;;R15|pre-service appeals;;R20|representative','SUPPORTED_CONTEXTUAL',
 'The appeal process requires proper case handling and representation, but a specific national appeal-coordinator job is not mandated by these sources.',
 'Appeals and grievance operations may be combined or separated; a delegated initial reviewer may forward appeals to the plan.',
 'Routing/standing checks are operational responsibilities; clinical reconsideration authority must be separately qualified.')
reviewed('U13','A03|not involved;;A03|must be made by a physician','SUPPORTED_WITHIN_SCOPE',
 'The specified MA reconsideration requires prior noninvolvement and appropriate physician expertise for medical-necessity denial.',
 'The professional need not always match the treating specialty; non-medical-necessity and other product procedures can differ.',
 'Independence is not merely seniority. This card does not establish the credentials/delegation of any actual reviewer.')
reviewed('U14','A04|independent, outside entity;;A16|independent outside entity','SUPPORTED_WITHIN_SCOPE',
 'MA remaining-dispute review and applicable effectuation duties are explicit.',
 'Decision, remand/dismissal and eligibility for later appeal are distinct outcomes.',
 'An IRE reviewer is not an internal supervisor; an external-review label alone does not identify the correct statutory route.')
reviewed('U15','R17|administrative functions;;A04|independent','SUPPORTED_CONTEXTUAL',
 'Federal external-review administration is described; a generic administrator profile is a functional model across different programs.',
 'Different state/federal contractors and MA/commercial routes.',
 'Administrative eligibility/file handling must not be confused with medical merits or universal agency jurisdiction.')
reviewed('U16','R35|SHIP;;R35|complaint','SUPPORTED_CONDITIONAL',
 'The source identifies Medicare help/counseling and complaint contacts; each has a different mandate.',
 'SHIP counseling, insurer assistance, quality-of-care complaint support or another appropriate ombudsman route.',
 'These are several functions, not one credential or one organization that can reverse every denial.')
reviewed('U17','R14|supervises;;R14|prioritizes UM team workload','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The UCSD role directly describes supervision, staffing, routine/expedited/complex review coordination and escalation.',
 'UM can operate within a provider-affiliated IPA or health plan/delegate; scope differs by organization.',
 'Documented operational supervision does not establish every professional signoff, appeal-review power or cross-organization hierarchy.')
reviewed('U18','A12|required by law to accept;;R17|independent review organization','SUPPORTED_WITHIN_SCOPE',
 'The relevant external-review guidance supports an independent outcome binding on the insurer within its covered process.',
 'State external review, HHS-administered route or qualifying IRO arrangement; eligibility and expedited handling differ.',
 'Do not apply this route to every plan/denial, or substitute it for MA IRE review. Further legal remedies are not comprehensively audited here.')

reviewed('M01','R24|social worker/nurse practitioner;;R25|integrated model;;R32|Nurse Case Manager I','SUPPORTED_MULTIPLE_PROGRAM_EXAMPLES',
 'Several accessible programs demonstrate assessment, shared planning, coordination and follow-through, with different staffing.',
 'UCLA describes RN case managers; GRACE uses NP/social-work support teams; Partnership combines case managers, social workers and guides.',
 'These examples do not establish national prevalence. Coordination title is not a license or independent prescribing credential; unavailable R23 is not needed to establish these examples.')
reviewed('M02','B09|Assess clients;;R25|unlicensed;;R32|Social Worker I','SUPPORTED_CONDITIONAL',
 'Social assessment, resources, coping and coordination are supported. The prior label nonclinical would be too restrictive for all medical social workers.',
 'Resource/social casework, clinically supervised pre-licensure practice, or separately licensed clinical work according to state and employer.',
 'UCLA describes an unlicensed Clinical Social Worker II role. A job title containing clinical does not establish independent clinical licensure.')
reviewed('M03','B09|licensed to diagnose;;R25|California-licensed','SUPPORTED_CONDITIONAL',
 'The description supports licensed clinical social-work assessment/treatment while distinguishing supervised/pre-licensure pathways.',
 'Independent or supervised clinical work under the actual license/setting; case management and psychotherapy are not interchangeable functions.',
 'State license/permissions remain necessary; the profile does not establish medication-prescribing or coverage authority.')
reviewed('M04','B07|Check patients;;B07|Instruct patients;;V13|therapeutic decisions','SUPPORTED_CONDITIONAL',
 'Medication review, counseling and professional communication are general duties. Washington provides a concrete delegated drug-therapy pathway.',
 'Dispensing/counseling, clinical recommendations, and separately authorized therapy modification/initiation are different activities.',
 'Do not imply every change requires a fresh individual physician instruction or every pharmacist can independently prescribe; actual legal/program authority controls.')
reviewed('M05','B08|Collect information;;B08|pharmacists;;R09|prior authorizations','SUPPORTED_GENERAL_AND_HISTORICAL_EXAMPLE',
 'Government material supports technical/admin tasks and routing clinical questions; earlier archived ASHP material describes advanced access/appeal logistics.',
 'Dispensing support, specialty access, refill or assistance assignments; training and state permissions differ.',
 'An access assignment does not replace pharmacist/prescriber judgment. R09 historical examples are not proof of current staffing or procedure.')
reviewed('M06','B01|Psychiatrists','SUPPORTED_GENERAL_DESCRIPTION',
 'Psychiatry is documented as a physician specialty; the card restricts medical treatment to actual privileges and patient context.',
 'Treating psychiatrist, consulting psychiatrist or separately assigned reviewer are different functions.',
 'Physician status does not automatically confer a patient relationship or payer-review delegation.')
reviewed('M07','B10|Clinical and counseling;;V04|Prescription Certificate','SUPPORTED_CONDITIONAL',
 'Psychological assessment/treatment is supported; New Mexico documents additional prescribing-certificate pathways.',
 'General psychology license versus additional conditional/full prescribing certification in a jurisdiction that provides it.',
 'Neither a universal prescribing right nor a blanket nationwide prohibition is justified; specific current qualification must be checked.')
reviewed('M08','B11|Evaluate clients;;B11|Develop, recommend','SUPPORTED_CONDITIONAL',
 'Counseling assessment, plans, progress and referrals are described, but credentials within this broad group differ.',
 'Mental-health, addiction, marriage/family and other counseling roles; supervised or independent practice depends on applicable qualification.',
 'Do not infer equivalent clinical scope or prescribing authority across counseling titles.')
reviewed('M09','B12|Coordinate care;;R29|trusted','SUPPORTED_GENERAL_DESCRIPTION',
 'Community linkage, outreach, navigation and practical barrier support are described.',
 'Community health representative, promotor, navigator or another program-specific title can overlap.',
 'Community trust and additional training do not by themselves establish a clinical license or benefit-decision authority.')
reviewed('M10','R28|patient navigator;;R28|barriers','SUPPORTED_PROGRAM_EXAMPLE',
 'CDC describes navigation functions and different possible professional backgrounds in its cancer-program context.',
 'Nurse, social worker, CHW or another appropriately trained navigation role.',
 'Navigation is a function rather than one universal credential; cancer guidance does not prescribe every other program\'s workflow.')
reviewed('M11','R32|Health Care Guide I','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The plan describes guides linking members/families/providers/agencies and resources.',
 'Different guide levels and discretion within the stated program; other organizations use different titles or staff.',
 'The title and hierarchy cannot be transferred nationally or treated as equivalent to licensed clinical case management.')
reviewed('M12','B14|Assess clients;;B14|Develop meal','SUPPORTED_GENERAL_DESCRIPTION',
 'Nutrition assessment, counseling, plans and monitoring are described; credential and practice permissions remain conditional.',
 'Registered dietitian and other nutrition titles may have different credentials and permitted activities.',
 'Do not assume every nutritionist title equals an RD credential or independently grants unrelated treatment authority.')
reviewed('M13','B13|Assess the health needs;;B13|Develop programs','SUPPORTED_GENERAL_DESCRIPTION',
 'Educational needs, materials, teaching and evaluation are documented; coach is a broader functional title.',
 'Health educator, program coach, CHW or licensed clinician providing an educational function.',
 'Providing education is not by itself a medical diagnosis or prescribing grant.')
reviewed('M14','B15|Develop individualized plans;;B15|Evaluate and record','SUPPORTED_CONDITIONAL',
 'Functional evaluation, therapy planning/interventions, monitoring and education are described.',
 'Referral/direct-access and payer requirements can differ; a therapist does not necessarily sit in a universal physician command chain.',
 'Professional clinical assessment and authorization/payment criteria are separate. Actual state/order rules are not nationally resolved.')
reviewed('M15','B16|daily living;;B16|Recommend special equipment','SUPPORTED_GENERAL_DESCRIPTION',
 'Daily-activity assessment, interventions, adaptations, equipment recommendations and training are described.',
 'Different service settings and referral/order arrangements.',
 'Equipment recommendation is not itself a covered equipment order, supplier acceptance or payment approval.')
reviewed('M16','B17|swallowing;;B17|individualized treatment plan','SUPPORTED_GENERAL_DESCRIPTION',
 'Communication/swallowing evaluation, interventions, progress and family education are described.',
 'Speech/language impairment support and language interpretation may both be needed but are different services.',
 'Speech-language pathology does not make someone a qualified interpreter for every language or an unrelated medical prescriber.')
reviewed('M17','B18|Consult with physicians;;B18|Teach patients','SUPPORTED_CONDITIONAL',
 'Respiratory assessment, treatment, monitoring and equipment/medication education are described.',
 'Authorized protocols and individual orders differ by setting and qualification.',
 'The occupational summary does not establish a particular independent treatment-adjustment permission.')
reviewed('M18','A06|appropriately qualified personnel;;A06|transmission','SUPPORTED_WITHIN_SCOPE',
 'The cited hospital rule directly supports needs/access evaluation, patient discussion, qualified planning and transfer information.',
 'RN, social worker or other appropriately qualified personnel may develop or supervise the plan; exact local roles differ.',
 'Medical readiness, discharge planning, receiving acceptance, coverage and patient rights are distinct; planner title is not sole authority.')
reviewed('M19','A07|reasonable expectation;;A07|coordination of care','SUPPORTED_WITHIN_SCOPE',
 'Home-health acceptance, coordinated disciplines and physician/allowed-practitioner plan/order responsibilities are described.',
 'Agency intake and qualified clinical coordination can be separate functions; allowable signatories depend on setting and scope.',
 'Agency capacity, clinical orders, accepted referral and completed visits are separate. Local intake/acceptance permissions remain unconfirmed.')
reviewed('M20','A06|post-acute;;R25|post-acute','COMPOSITE_FUNCTION_WITH_SOURCE_CONTEXT',
 'Sources establish transfer to receiving facilities and information exchange, not one nationally standardized receiving-coordinator occupation.',
 'Home health, skilled nursing, rehabilitation and other facilities have different intake and clinical assessment arrangements.',
 'Reception/acceptance is not benefit approval or automatic authentication of all medical orders; exact local permissions are not established.')
reviewed('M21','B19|daily personal tasks;;B19|supervised','SUPPORTED_CONDITIONAL',
 'Personal support, recorded observations and supervision are described; permitted health-related tasks vary.',
 'Home-health aide, other personal-care worker or additional trained support with distinct requirements.',
 'Do not apply Medicare coverage conditions to every private aide or treat personal care as equivalent to skilled nursing.')
reviewed('M22','R22|community resources;;R29|social services','COMPOSITE_FUNCTION_NOT_SINGLE_OCCUPATION',
 'Health/social resource connections are supported, but the food/housing/benefit worker grouping is a functional model rather than one verified profession.',
 'Different agencies and eligibility/capacity rules; referral may be accepted, wait-listed or declined.',
 'Directory availability is not service capacity, and the worker cannot be assumed to control health-plan eligibility or clinical treatment.')
reviewed('M23','V05|States may pay;;V14|broker','SUPPORTED_CONTEXT_WITH_MODELED_DUTIES',
 'Medicaid guidance supports several transport-administration models. The detailed dispatch workflow remains a proposed service interface.',
 'Brokered, non-broker and other permissible state arrangements; emergency and non-emergency services differ.',
 'Travel eligibility, accessibility, modality and required clinical attendants cannot be decided from dispatcher title alone.')
reviewed('M24','V05|individual driver;;V14|driver','SUPPORTED_CONTEXT_WITH_MODELED_DUTIES',
 'The guide explicitly addresses transport providers/drivers and program assurances; exact pickup/reporting duties are operational examples, not national job requirements.',
 'Different vehicle/accessibility and attendant qualifications; some services include separately qualified clinical personnel.',
 'Driver title alone does not grant emergency clinical triage authority. A trip booking is not proof of attendance or completed care.')
reviewed('M25','R11|DMEPOS Suppliers;;R11|Standard Written Order','SUPPORTED_SERVICE_EXAMPLE',
 'The CMS power-mobility example supports practitioner/supplier documentation, authorization, assessment and fulfillment distinctions.',
 'Ordering professional or supplier can submit the specified request under the example; not both for that request.',
 'Power-mobility requirements cannot be generalized to all DME, delivery staff or fitting credentials. Supplier is not automatically the prescriber.')
reviewed('M26','A06|service providers and suppliers;;R22|referral','COMPOSITE_MODELED_SERVICE_FUNCTION',
 'General transfer/referral principles support the context; a specific infusion coordinator job, credential or national procedure is not established.',
 'Administrative intake, nursing coordination, pharmacy and service-specific clinical readiness can be handled by different people.',
 'This profile must remain an operational model; booking does not establish clinical readiness or administration.')
reviewed('M27','R31|collaborate;;R31|dietitians','SUPPORTED_MULTIDISCIPLINARY_EXAMPLE',
 'The provider describes a serious-illness multidisciplinary team rather than one interchangeable profession.',
 'Physicians, advanced-practice clinicians, nurses, pharmacy, dietetics, social work and spiritual care may contribute.',
 'Palliative care and hospice are distinct service contexts; team membership does not give every member physician authority.')
reviewed('M28','V11|designate a registered nurse;;V11|interdisciplinary group;;V16|Sources of certification;;V17|Admission to hospice','SUPPORTED_DATED_CODIFICATION_WITH_DISTINCT_AUTHORITIES',
 'Official 2025 codification provides stronger evidence than the earlier 2024 snippet: IDG, designated RN coordination, physician certification and admission functions are distinct.',
 'A patient-designated attending may be physician/NP/PA under the benefit description, but that does not make all of them authorized terminal-illness certifiers.',
 'The IDG is a group, not one individual. Evidence is expressly the October 2025 codification; complete current 2026 hospice-rule verification is not claimed.')
reviewed('M29','R31|chaplain;;A08|pastoral','SUPPORTED_SERVICE_EXAMPLE',
 'Provider team description and dated hospice composition guidance recognize spiritual/pastoral support.',
 'Participation depends on wishes, needs and service setting; may be within or outside hospice.',
 'Spiritual support does not create clinical, coverage or surrogate-decision authority.')
reviewed('M30','R26|Administrative Staff;;R32|Coordinator I','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Administrative coordination, referral distribution, data entry and program support are described.',
 'Separate administrative coordinator or a person combining tasks with another role.',
 'Administrative closure/status changes are not equivalent to clinical decision or confirmed service delivery.')
reviewed('M31','R25|abuse;;V12|Person-Directed;;V12|2028','SUPPORTED_CONTEXT_WITH_MANDATE_LIMITS',
 'Sources establish protection-related referrals and an adult-protective-services policy context; no universal national safeguarding profession/power is established.',
 'Adult APS, child protection, clinical social work and other services have different mandates and reporting law.',
 'The 2024 federal APS rule fact sheet has a later full-compliance date. Do not infer uniform implementation or identical consent/investigation authority in every state.')

reviewed('G01','B22|policies;;A15|medical staff','SUPPORTED_CONTEXT_WITH_LOCAL_GOVERNANCE_UNKNOWN',
 'Health-service management and medical-staff governance support a clinical-leadership context, not a single universal CMO job description.',
 'Clinical-program director, medical-staff leadership and operational executive can be distinct posts.',
 'Exact authority over practitioners requires bylaws, privileges and assignment; the title does not establish a physician-over-all-professions chain.')
reviewed('G02','A05|medical director;;R18|medical directors','SUPPORTED_WITHIN_SCOPE_AND_EXAMPLE',
 'The MA committee rule names medical-director leadership; insurer material illustrates program/case functions.',
 'Clinical-program oversight and separately delegated individual review can be combined or separated.',
 'Program leadership cannot substitute for the independence/expertise required for a particular appeal.')
reviewed('G03','A05|reviewed and approved;;A17|coverage criteria','SUPPORTED_WITHIN_SCOPE',
 'The MA policy-governance obligations are explicit; committee authority is bounded by governing criteria.',
 'Different products and organizations have different committee structures and approval processes.',
 'Policy approval is not adjudication of every case. An earlier rule edition may contain requirements removed or changed later; use the stated edition.')
reviewed('G04','R32|Director of Care Coordination;;B22|supervise staff','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Programme leadership, resources, oversight and outcomes are described; the exact multilevel chart is organization-specific.',
 'Several directors/managers or a combined lead in a smaller program.',
 'Administrative resource authority does not confer prescribing, patient consent or insurer appeal authority.')
reviewed('G05','R32|Supervisor of Case Management;;R32|Non-Clinical Supervisor','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The source explicitly distinguishes RN, LVN, social-work and nonclinical supervision with scope limits.',
 'Administrative supervision and discipline-specific clinical supervision may be different relationships.',
 'A supervisor title does not imply identical clinical powers or a universal ordering between professional licenses.')
reviewed('G06','R32|quality measures;;R14|reports data','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Quality/performance reporting and process improvement are documented; specific audit design is not established universally.',
 'Internal quality review, operational audit, professional peer review and regulatory audit have different mandates.',
 'A finding is not a patient diagnosis, automatic coverage reversal or causal proof of improved outcomes.')
reviewed('G07','R32|Training Specialist;;B13|training','SUPPORTED_ORGANIZATION_EXAMPLE',
 'Training-program design, materials and implementation are described.',
 'Clinical educator, nonclinical trainer or program-specific training specialist.',
 'Course attendance does not grant a license or establish competence for every clinical task.')
reviewed('G08','R32|Policy Analyst;;R32|Clinical Advisor','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The source documents drafting, reviewing, tracking and maintaining policies and operational change support.',
 'Clinical adviser and nonclinical policy analyst can be separate qualifications/functions.',
 'Drafting and approval are distinct. The analyst does not automatically enact policy or decide clinical case merits.')
reviewed('G09','R32|Regulatory Performance;;B22|complies with laws','SUPPORTED_CONTEXTUAL',
 'Compliance monitoring and operational interpretation are documented management functions; legal/enforcement authority remains separately scoped.',
 'Internal compliance staff, legal counsel and external regulator have different roles.',
 'An internal interpretation is not itself law or a clinical/appeal decision.')
reviewed('G10','R32|Privacy Officer;;R07|ROI;;A10|policies and procedures','SUPPORTED_CONTEXTUAL',
 'The program identifies privacy-officer functions; HHS describes organization access/disclosure policies and purpose-dependent requirements.',
 'HIM handling, designated privacy officer, legal advice and security/IAM support may be separate.',
 'Minimum necessary, authorization, representative access and specially protected records are different questions; Part 2 illustrates why treatment is not an unrestricted all-records exception.')
reviewed('G11','B21|Compile data;;R32|Health Services Analyst','SUPPORTED_GENERAL_AND_ORGANIZATION_EXAMPLE',
 'Data validation, reporting, outcomes information and operational analysis are described.',
 'Disease registry, population-health analysis or broader operational reporting functions.',
 'Measure definitions, data access and interpretation must be authorized; administrative task completion cannot be assumed to mean clinical benefit.')
reviewed('G12','R32|Business Analyst;;B21|requirements','SUPPORTED_ORGANIZATION_EXAMPLE',
 'The plan describes operational requirements, test/implementation plans and analytical support.',
 'Business, clinical informatics and technical analysis may be split or combined.',
 'Requirements writing is not medical-policy approval or treatment authority.')
reviewed('G13','B21|implementation of health information systems;;B21|integrity','SUPPORTED_GENERAL_DESCRIPTION',
 'Health-information system implementation, validation, education and integrity support are described.',
 'Clinical informaticist with an additional license versus technical/application professional without that clinical qualification.',
 'Technical configuration permission is not permission to alter clinical facts or approve care.')
reviewed('G14','V08|permissions;;A10|persons or classes','SUPPORTED_CONTEXT_WITH_MODELED_JOB_BOUNDARY',
 'General IT administration supports access-permission work; HIPAA role/purpose controls support the healthcare constraint.',
 'Dedicated IAM administrator, application support or another assigned access-control function.',
 'Exact healthcare provisioning workflow, approval authority and local job title remain unconfirmed; administrator access is not unrestricted PHI permission.')
reviewed('G15','V18|Billing and posting;;R06|claims;;R08|denials','SUPPORTED_GENERAL_AND_SERVICE_CONTEXT',
 'Billing/account work and claim-denial support have primary occupational and medical-service context; no single universal combined job is established.',
 'Patient accounts, insurance-claims processing, coding and provider appeal staff may be separate.',
 'Pre-service authorization, claim adjudication, financial assistance and patient liability are different decisions.')
reviewed('G16','A05|available to CMS;;R17|HHS;;R35|complaint','GENERIC_AUTHORITY_MODEL_WITH_SCOPED_EXAMPLES',
 'Sources establish particular oversight/help routes, not an all-purpose regulator with every power listed by generic title.',
 'CMS, state program, insurance regulator, quality oversight and ombudsman mandates differ.',
 'A complaint may trigger oversight or referral rather than a coverage reversal; identify jurisdiction and legal process.')
reviewed('G17','V07|Advise and represent;;V07|Prepare and file;;R20|representative','SUPPORTED_GENERAL_DESCRIPTION',
 'Legal advice, analysis and authorized submissions are general lawyer duties; healthcare representation also requires the applicable appointment/standing.',
 'Self/lay representation may be permitted in a process; not every appeal requires a lawyer.',
 'Retainer/appointment and professional jurisdiction matter; advice does not itself reverse coverage or grant treatment permission.')
reviewed('J01','A11|Administrative Law Judge;;A16|attorney adjudicator','SUPPORTED_WITHIN_SCOPE',
 'The MA appeal overview and effectuation rule recognize eligible adjudication and attorney-adjudicator dispositions.',
 'Hearing/adjudication, favorable disposition, remand or other permitted outcome under the actual process.',
 'Jurisdiction, filing and threshold conditions apply; a later stage is not automatically available or a clinical supervisory role.')
reviewed('J02','A11|Medicare Appeals Council;;A16|Council review','SUPPORTED_WITHIN_SCOPE',
 'Council review is a named MA level and the effectuation rule contains a Council-review exception.',
 'Further review can be sought under its actual rules; a plan request can affect implementation as described in A16.',
 'Do not infer automatic review entitlement or that every earlier outcome is immediately final/effectuated.')
reviewed('J03','A11|Federal District Court','SUPPORTED_WITHIN_SCOPE',
 'Judicial review is identified as a later MA appeal stage, subject to actual legal requirements.',
 'Only eligible properly pursued judicial cases; further appellate law is outside the described five-level administrative/initial judicial map.',
 'The court is not an ordinary healthcare employee or a routine prerequisite to care.')
