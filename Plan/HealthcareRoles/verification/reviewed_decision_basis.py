"""Reviewed decision assertions: evidence-backed scope is distinct from local permission."""
REVIEWS={}


def reviewed(id,evidence,verdict,rationale,alternatives,complexity):
    REVIEWS[id]=dict(evidence=[tuple(x.split('|',1)) for x in evidence.split(';;')],verdict=verdict,
        rationale=rationale,alternatives=alternatives,complexity=complexity)


reviewed('D01','A01|request or refuse treatment;;A09|scope','SUPPORTED_WITHIN_SCOPE',
 'Hospital patient participation/refusal and bounded representative authority are explicit. Separating consent from insurance/scheduling is a reasoned domain distinction.',
 'Direct patient decision or a legally appropriate representative; specific exceptions require the actual law/case.',
 'No universal surrogate order, capacity finding or emergency-consent outcome is established.')
reviewed('D02','A09|scope;;R20|appointment','SUPPORTED_CONDITIONAL',
 'HHS defines healthcare representation and separately describes appointment for Medicare appeals.',
 'Broad or limited healthcare authority; appointed appeal representative; statutory authority where applicable.',
 'Two scopes can belong to the same person, but neither follows merely from family relationship or a generic signature.')
reviewed('D03','B01|treatment plan;;B03|scope of practice varies;;A15|ordering practitioner','SUPPORTED_CONDITIONAL',
 'Treating-professional functions and hospital order authentication are supported; profession/jurisdiction/privileges condition the permission.',
 'Physician, NP, PA or other allowed practitioner for a specific activity/setting.',
 'Sources do not establish any actual individual license, privileges or authorization; no universal prescribing permission is certified.')
reviewed('D04','B01|specialize;;R22|primary care physicians','INTERPRETATION_WITH_SOURCE_CONTEXT',
 'Sources describe different expertise and coordination. They do not establish a universal specialty-over-PCP command hierarchy.',
 'Responsibility can be assigned by episode, institution, admitting/attending arrangement and privileges.',
 'No universal hierarchy is inferred; this is an evidence boundary, not proof that no institution can assign one.')
reviewed('D05','B03|scope of practice varies;;V02|103 NP;;V02|furnishing authority','SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES',
 'The occupational summary and California regulator establish variation and multiple arrangements.',
 'California traditional/103/104 pathways have different conditions; furnishing authority and employer requirements are additional issues.',
 'The California page has prospective 104 availability wording that does not itself prove current individual certification or operational application availability.')
reviewed('D06','B02|collaboration;;V03|collaboration agreement','SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES',
 'Oregon explicitly describes collaborative practice and associate terminology, limiting broad national supervision summaries.',
 'Different states/practice arrangements; physician or employer agreement as specified by Oregon.',
 'National occupational text is not a state practice act; no universal supervision ratio or boss chain is established.')
reviewed('D07','V10|prohibited;;V10|competence;;A14|state','SUPPORTED_PROFESSIONAL_FRAMEWORK',
 'The decision framework checks legal prohibition, education/competence, policy and accountability. It is professional guidance, not itself every state law.',
 'Assignment, delegation and supervision vary by activity/state/credential.',
 'Specific task permission remains unresolved until the actual practice act and case facts are checked.')
reviewed('D08','A15|authenticated;;B20|clinical codes;;R08|documentation','SUPPORTED_WITHIN_SETTING_PLUS_INTERPRETATION',
 'Hospital authentication is explicit; coding/CDI sources support clarification rather than independently creating clinical facts.',
 'Responsible author and permitted countersign/correction arrangements depend on setting.',
 'The hospital rule is not silently generalized to all clinics or used as a complete record-correction policy.')
reviewed('D09','B20|assign clinical codes;;R08|coding','SUPPORTED_GENERAL_DESCRIPTION',
 'The occupational description supports code assignment from clinical information; documentation/denial example supports collaboration.',
 'Pre-service clarification, coding, CDI and downstream claim correction can be separate work.',
 'The exact coding standard/query process must be specified; coding alone is not clinical diagnosis or payer adjudication.')
reviewed('D10','R06|prior authorization;;R13|eligibility and benefits','SUPPORTED_SOURCE_EXAMPLES',
 'The sources distinguish benefits, authorization and financial responsibility.',
 'Separate or combined staff can perform these checks; final claim/payment depends on its own applicable rules.',
 'Do not infer final coverage or zero patient cost from eligibility, estimates or a case identifier.')
reviewed('D11','R13|Non-clinical personnel may;;R13|Non-licensed personnel may;;R12|first-level','SUPPORTED_ORGANIZATION_EXAMPLES_WITH_CORRECTION',
 'The program allows limited nonclinical approvals under explicit criteria as well as licensed review; the earlier clinical-only emphasis was incomplete.',
 'Nonclinical limited approval, benefit-only decision, licensed approval, or clinical escalation depending on documented delegation.',
 'R13 also describes medical-director final responsibility and broader professional categories; exact signing rights require program/product clarification.')
reviewed('D12','A02|expects to issue;;A02|unrestricted license','SUPPORTED_WITHIN_SCOPE',
 'The retrieved section directly requires appropriate physician or other qualified professional review before the specified adverse MA medical-necessity determination.',
 'Physician or another appropriate licensed expert; organization policy can set additional requirements.',
 'Integrated-plan and decision-type conditions matter; the rule is not physician-only for every initial denial.')
reviewed('D13','A03|not involved;;A03|made by a physician','SUPPORTED_WITHIN_SCOPE',
 'Noninvolvement and physician expertise for the specified MA medical-necessity reconsideration are explicit.',
 'Reviewer need not always have identical specialty; other products/types have their own requirements.',
 'Higher rank does not by itself establish independence or case eligibility.')
reviewed('D14','R15|discussion;;R15|pre-service appeal','SUPPORTED_PROCESS_EXAMPLE_WITH_LIMITS',
 'Payer material separately describes peer discussion and pre-service appeal. Deadline preservation is not established and is intentionally not assumed.',
 'Peer discussion, formal appeal or another correction route under actual product/notice.',
 'Retrieved deadline presentations differ. Do not select one as a universal rule or infer that discussion preserves filing rights.')
reviewed('D15','A04|remain in dispute;;A16|reversed in whole or in part','SUPPORTED_WITHIN_SCOPE',
 'Independent MA review and scoped reversal effectuation are explicit.',
 'Outcome may affirm, reverse, dismiss/remand where allowed; implementation depends on decision category and further-review conditions.',
 'A favorable decision and actual authorization/provision/payment are distinct; no universal deadline is supplied.')
reviewed('D16','A12|required by law to accept;;R17|non-grandfathered;;V19|same time','SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES',
 'Guidance supports binding acceptance within its applicable external-review route and identifies product/process limits.',
 'State/federal qualifying routes; eligible urgent internal/external requests may run concurrently.',
 'The prior simple linear diagram was incomplete for urgent cases. MA IRE and this external process must remain distinct.')
reviewed('D17','A11|five successive levels;;A16|Council review','SUPPORTED_WITHIN_SCOPE',
 'The MA overview names successive levels, while the effectuation rule provides a Council-review exception.',
 'Further appeal is conditional on actual standing/jurisdiction/filing; reversals can have implementation conditions.',
 'This is not an employment ladder or a guarantee every case may reach every forum; no threshold amounts are invented.')
reviewed('D18','A01|informed decisions;;A02|benefits an enrollee;;B01|treatment plan','INTERPRETATION_OF_DISTINCT_AUTHORITIES',
 'Different source provisions address participation, clinical care and benefits. The domain separation is a reasoned synthesis rather than one quoted universal hierarchy statute.',
 'Clinical recommendations and coverage/consent outcomes may agree or conflict and require their own processes.',
 'The reference does not decide a real individual case or eliminate any actual legal constraint.')
reviewed('D19','A05|reviewed and approved;;A05|Document in writing;;A17|coverage criteria','SUPPORTED_WITHIN_SCOPE',
 'The MA committee approval/documentation and criteria constraints are explicit.',
 'Other products may use different governance; analyst drafting and institutional approval are different functions.',
 'Policy approval does not itself adjudicate all individual case disputes.')
reviewed('D20','A05|policies and procedures;;A04|independent, outside entity','INTERPRETATION_WITH_SCOPED_RULES',
 'Sources assign different policy-governance and case-review functions. No committee command over the independent entity is evidenced.',
 'Systemic policy review and an individual appeal can both be pursued through their own authorized mechanisms.',
 'The absence of a command edge is a conservative modeling choice, not a claim to have audited every possible internal organogram.')
reviewed('D21','R22|proactive care plan;;R24|social worker/nurse practitioner;;R32|Nurse Case Manager','SUPPORTED_PROGRAM_MODELS_NOT_UNIVERSAL_AUTHORITY',
 'Published programs support coordinating plans with patient and other professionals, with different staffing.',
 'RN case management, NP/SW teams and mixed staff programs; underlying clinical authority stays credential-dependent.',
 'Coordination ownership is not a verified national prescribing/coverage permission or a prevalence statement.')
reviewed('D22','A06|appropriately qualified personnel','SUPPORTED_WITHIN_SCOPE',
 'The hospital provision explicitly allows development by or under RN, social worker or other qualified personnel.',
 'Several qualified staffing models, not RN-only planning.',
 'Planning, medical readiness, patient participation and receiving-service availability remain distinct.')
reviewed('D23','A07|signed by;;A07|consulted to approve;;A07|Verbal orders','SUPPORTED_WITHIN_SCOPE',
 'The home-health provision distinguishes plan/signature, orders, permitted verbal orders and revisions.',
 'Physician/allowed practitioner within applicable scope; agency coordination and clinical signatures are different roles.',
 'Do not transplant hospice certification or another setting\'s signatory rules into home health.')
reviewed('D24','R22|Monitoring and followup;;R28|track','OPERATIONAL_MODEL_NOT_EMPIRICAL_ASSERTION',
 'Separating sent/accepted/scheduled/completed states is a proposed control informed by coordination needs, not a verified universal state machine.',
 'Organizations use different status fields, acknowledgements and closure criteria.',
 'The model cannot prove delivery or clinical benefit; actual evidence must be obtained in its local workflow.')
reviewed('D25','B08|under the supervision;;B07|Supervise;;V13|therapeutic decisions','SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES',
 'Professional task separation is supported; Washington illustrates separately authorized pharmacist therapy decisions.',
 'Technician support, pharmacist professional decision and prescriber/protocol actions differ.',
 'Not every pharmacist change requires a new individual physician instruction; no general independent technician therapy authority follows from title.')
reviewed('D26','B10|Clinical and counseling;;V04|Prescription Certificate','SUPPORTED_CONDITIONAL_WITH_ALTERNATIVES',
 'New Mexico provides a concrete additional certification route, while general clinical psychology duties are separately described.',
 'Ordinary psychology license and additional conditional/full prescribing qualification are distinct.',
 'No universal psychologist prescribing rule or verified permission for an individual is established.')
reviewed('D27','A10|treatment purposes;;A09|scope;;V15|specific consent','SUPPORTED_CONDITIONAL_WITH_COMPLEXITY',
 'HIPAA minimum-necessary exceptions, representative authority and specific Part 2 protections show that information-sharing permission depends on more than a treatment label.',
 'Different purposes, record regimes and consent/exception pathways; applicable Part 2 TPO consent differs from special counseling notes.',
 'The treatment exception is not an unrestricted all-records disclosure rule. No patient/program-specific legal determination is made.')
reviewed('D28','B23|Render spoken messages;;R28|navigator;;A09|authority','INTERPRETATION_WITH_PROFESSIONAL_CONTEXT',
 'Communication/navigation functions are documented; no medical/coverage/proxy power is inferred merely from performing them.',
 'One person may hold additional independent qualifications or appointment, which must be established separately.',
 'The role boundary is not proof that an interpreter/navigator can never have another legitimate authority.')
reviewed('D29','B22|supervise staff;;V10|prohibited;;A03|not involved','SUPPORTED_FRAMEWORK_AND_SCOPED_BOUNDARY',
 'Management, practice-scope guidance and reconsideration independence are separately evidenced.',
 'Administrative reporting, professional supervision and statutory case review can follow different chains.',
 'A local organogram is not supplied; no universal authority ordering between licenses or job titles is certified.')
reviewed('D30','V08|permissions;;A10|persons or classes;;A15|authenticated','SUPPORTED_CONTEXT_WITH_LOCAL_PERMISSION_UNKNOWN',
 'IT permissions, healthcare access-purpose controls and hospital authentication are documented in their settings.',
 'Technical administration can be assigned separately from clinical/policy authorship.',
 'Actual system access is not proof of permission to alter clinical facts; exact change-control process remains local.')
reviewed('D31','R11|Standard Written Order;;V14|transportation','SERVICE_MODEL_WITH_SCOPED_SOURCE_CONTEXT',
 'Equipment and Medicaid transport sources establish service-specific responsibilities; a general suitability workflow is a model.',
 'Different equipment, transport administration, vehicle and attendant arrangements.',
 'A generic driver/dispatcher/delivery title does not establish clinical qualification; actual orders/protocols are not provided.')
reviewed('D32','R06|financial responsibility;;R09|assistance','SUPPORTED_CONTEXT_NOT_PROGRAM_SIGNOFF',
 'Cost and assistance support are documented, but the actual administrator\'s approval authority depends on the named program.',
 'Counseling, assistance decisions, claims and coverage are separate, possibly held by different organizations.',
 'No assistance eligibility outcome, final payment guarantee or universal financial-decision hierarchy is established.')
reviewed('D33','V11|designate a registered nurse;;V16|Sources of certification;;V17|Admission to hospice','SUPPORTED_DATED_RULES_WITH_ADDED_DISTINCTIONS',
 'Official October 2025 codification strengthens the earlier limited composition snapshot and separates IDG coordination, attending, certification and admission.',
 'Designated RN coordination; specified physicians certify/admit within the codified rules; attending may be a different allowed professional.',
 'These are distinct decisions and a group is not one professional. A complete current-2026 regulatory update audit is not claimed from the dated codification.')
reviewed('D34','R35|complaint;;R17|external review;;A11|appeal','SUPPORTED_CONTEXT_WITH_MANDATE_LIMITS',
 'Sources describe different assistance, complaint and appeal pathways; routing depends on the actual issue.',
 'Insurer appeal, public counseling, quality complaint or oversight mechanism as applicable.',
 'A complaint does not automatically establish an appeal, jurisdiction or reversal; the exact agency mandate remains case-specific.')
