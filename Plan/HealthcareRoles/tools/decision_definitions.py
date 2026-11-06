"""Scoped decision rights; these are not interchangeable with reporting rank."""

DECISIONS = []


def decision(id, question, domain, actors, rule, cannot, review, condition, sources):
    DECISIONS.append(dict(id=id, question=question, domain=domain, actors=actors.split(),
        rule=rule, cannot=cannot, review=review, condition=condition, sources=sources.split()))


decision('D01','Who chooses whether to accept proposed treatment?','consent','P01 P03 C01',
 'Patient participates and may request/refuse care; representative acts only under applicable authority.',
 'Insurer approval, scheduling or management preference is not patient consent.',
 'Clarify understanding, capacity and lawful representative; use applicable clinical/legal process for disputes.',
 'Hospital rights under A01; capacity/minor/emergency and other exceptions require additional applicable law.', 'A01 A09')
decision('D02','Who establishes representative authority?','representation','P03 P04 G10 G17',
 'Recognize authority from applicable law/instrument/appointment and its actual scope, not family relationship alone.',
 'Appeal appointment does not automatically authorize treatment decisions.',
 'Privacy/legal or applicable appointment process resolves uncertainty.',
 'Healthcare personal representation and appeal standing are separate determinations.', 'A09 R20 R15')
decision('D03','Who recommends/orders clinical treatment?','treatment','C01 C03 C04 C05',
 'Authorized treating practitioner makes clinical recommendations/orders within license and privileges.',
 'Coordinator, coder, reviewer title or managerial rank alone does not confer prescribing authority.',
 'Clinical reassessment, appropriate consultation and applicable professional escalation.',
 'Profession/state/practice arrangement and patient consent must be established.', 'B01 B02 B03 A15')
decision('D04','Does a treating specialist automatically outrank the PCP?','treatment','C02 C03',
 'They contribute different expertise/responsibilities; identify the clinician responsible for the disputed service.',
 'No universal organizational or clinical-superiority edge is inferred from specialty title.',
 'Reconcile recommendations with patient and responsible clinical team.',
 'Actual episode, privileges and local responsibility assignment determine signoff.', 'B01 R22 R24')
decision('D05','Can an NP act independently?','professional_scope','C04',
 'Activity depends on state scope, population focus and privileges/practice arrangement.',
 'Neither universal physician supervision nor universal unrestricted independence is asserted.',
 'Check current governing rules and required professional support.',
 'State and actual activity must be specified.', 'B03 A13 A14')
decision('D06','Who supervises PA practice?','professional_scope','C05 C01',
 'Apply the actual state and practice requirements for collaboration/supervision.',
 'Do not infer one national supervision arrangement or confuse PA with medical assistant.',
 'Responsible practice/medical leadership and governing scope rules.',
 'State, privileges and agreement are unresolved until identified.', 'B02 A15')
decision('D07','Can an RN delegate any assigned task?','professional_scope','C06 C07 C08 M21',
 'Assignment/delegation must fit applicable law, competence, supervision and policy.',
 'Manager instruction does not legalize a task beyond professional scope.',
 'Qualified nursing/professional supervisor and scope framework.',
 'No nationwide permission for a specific drug, IV task or assessment is assumed.', 'A13 A14 B04 B05 B06 B19')
decision('D08','Who supplies the clinical facts in a request?','documentation','C01 O06 O08 O13',
 'Responsible service author authenticates clinical content; custodians transfer and CDI requests clarification.',
 'Administrative staff cannot invent a diagnosis or revise facts to match payer criteria.',
 'Query author and follow correction/authentication process.',
 'Hospital authentication requirement A15; other settings need their rules.', 'A15 B20 R07 R08')
decision('D09','Who selects supported administrative codes?','coding','O07 O08 C01',
 'Coding specialist assigns supported codes; clinical ambiguity goes back to responsible author.',
 'Code selection is not independent medical diagnosis or authorization.',
 'Clinician/CDI/HIM and claim-correction pathway.',
 'Code system, service and documentation must match actual context.', 'B20 R08 A15')
decision('D10','Is benefit verification the same as authorization?','coverage','O04 U02 O01',
 'Membership/benefit information and request authorization are distinct findings.',
 'Eligibility, an estimate or a case number does not prove clinical approval or final payment.',
 'Payer benefit/UM contacts and appropriate dispute route.',
 'Plan and service determine required checks.', 'R03 R06 R13')
decision('D11','Can first-level UM approve a request?','coverage','U03 U04 U06 U07',
 'A reviewer may approve only under documented delegation, competence and applicable criteria.',
 'RN/pharmacist/reviewer title alone does not establish unlimited approval or denial authority.',
 'Escalate where criteria, evidence or authority are insufficient.',
 'R12/R13 are example programs; no universal program permission is inferred.', 'R12 R13 A02')
decision('D12','Who reviews anticipated adverse MA medical necessity?','coverage','U03 U04 U05 U06',
 'Before issuance, 422.566(d) requires a physician OR other appropriate licensed healthcare professional with relevant expertise and Medicare-criteria knowledge.',
 'Do not replace this with a physician-only rule for every initial denial; do not use an unqualified clerk.',
 'Appropriate licensed expert review; subsequent applicable reconsideration.',
 'MA initial adverse medical necessity; integrated-plan exception in 422.566(a) and different decision types must be checked.', 'A02')
decision('D13','Who may reconsider an MA medical-necessity denial?','appeal','U13 U12',
 'Under 422.590(h), reconsiderers were not involved in the initial decision; medical-necessity reconsideration is made by an appropriately expert physician.',
 'A more senior initial reviewer does not satisfy independence merely by rank.',
 'Remaining adverse MA issues proceed under independent-review requirements.',
 'Specified MA reconsideration route; not a universal rule for every product/dispute.', 'A03 A04')
decision('D14','Does peer-to-peer discussion replace appeal?','appeal','O11 U04 O10',
 'Peer discussion exchanges clinical information under the plan process.',
 'Do not assume it is an appeal, guarantees reversal, or preserves a filing deadline.',
 'Use actual formal route/notice for unresolved decision.',
 'Plan/state/service process determines relationship between discussion and appeal.', 'R15')
decision('D15','Can MA independent review reverse payer review?','appeal','U14 U13 U09',
 'CMS-contracted independent entity resolves remaining disputed issues; reversal triggers scoped effectuation obligations.',
 'Payer management is not free to disregard applicable independent reversal.',
 'Further eligible MA appeal level; document implementation.',
 '422.592 and 422.618; deadlines and further appeal rights differ by decision type.', 'A04 A16 A11')
decision('D16','Can commercial independent review supersede insurer denial?','appeal','U18 U15',
 'In the applicable external-review process described by HealthCare.gov, insurer must accept the external decision.',
 'Do not apply commercial IRO route automatically to MA, every plan or every denial.',
 'Follow applicable state/federal process and actual notice.',
 'Determine product, eligibility, issue and route first.', 'A12 R17')
decision('D17','Are later MA appeal forums above the prior decision?','appeal','J01 J02 J03',
 'CMS lists plan reconsideration, IRE, adjudication, Council and district-court review as successive appeal levels.',
 'Diagram is not an automatic entitlement or claim that every later forum reviews every issue.',
 'Follow eligibility, jurisdiction, filing and notice requirements at each level.',
 'A16 includes a Council-review effectuation exception; further appeal can affect implementation.', 'A11 A16')
decision('D18','Does coverage approval order the clinician to treat?','treatment_vs_coverage','U04 C01 P01',
 'Coverage, professional treatment judgment and patient willingness are separate domains.',
 'Coverage approval is not a treatment order or consent; clinical recommendation is not automatic benefit coverage.',
 'Resolve clinical questions with treating team and coverage disputes through review.',
 'Functional separation; actual service and rights still apply.', 'A01 A02 A17 B01')
decision('D19','Who approves MA utilization policy?','policy','G03 G02 G08',
 '422.137 requires UM committee review/approval of MA UM policies and documented decisions within governing criteria.',
 'An analyst draft or CEO preference does not substitute for required policy governance.',
 'Committee/regulatory correction for criteria issues; separate appeal process for individual case.',
 'MA-specific committee requirements; other products need their own governance.', 'A05 A17')
decision('D20','Does policy committee rank supersede every case appeal?','policy_vs_case','G03 U13 U14',
 'Policy approval and case adjudication are different functions.',
 'Committee existence does not eliminate individual review or higher appeal rights.',
 'Separate systemic policy correction from case reconsideration.',
 'No committee-to-IRE command edge exists in this map.', 'A05 A03 A04')
decision('D21','Who owns the shared care-coordination plan?','coordination','M01 P01 C02',
 'Lead coordinator integrates needs, goals and assigned follow-up with patient and responsible professionals.',
 'Coordination ownership alone does not grant authority to change clinical orders or benefit decisions.',
 'Send clinical changes to responsible clinician; resource gaps to service/management owner.',
 'Program-specific professional background and permissions.', 'R22 R23 R25')
decision('D22','Who develops hospital discharge planning?','transition','M18 C06 M02',
 '482.43(a)(5) permits development by or under an RN, social worker or other appropriately qualified personnel.',
 'Do not impose RN-only staffing or treat a planner as sole medical discharge authority.',
 'Qualified plan supervision and responsible clinical team.',
 'Hospital discharge setting; patient goals/access and information transfer requirements also apply.', 'A06')
decision('D23','Who signs/changes the home-health medical plan?','home_health','M19 C01 C04 C05',
 '484.60 identifies physician/allowed-practitioner plan establishment/signature and scoped order/revision requirements.',
 'Agency coordinator cannot freely rewrite medical orders; authorized signatory is setting-specific.',
 'Consult responsible physician/allowed practitioner for required additions/changes.',
 'Home-health setting; state law and agency policy apply to verbal orders and allowed activities.', 'A07')
decision('D24','Does referral acceptance mean the service happened?','service_completion','M01 M18 M19 M20 O05',
 'Referral sent, accepted, scheduled and completed are different events.',
 'Do not close unmet need solely because a document or booking exists.',
 'Confirm relevant receiving-service status and return unresolved barriers to coordinator.',
 'Operational synthesis supporting closed-loop coordination, not a universal mandated form.', 'R22 R28 A06')
decision('D25','Can a technician change medication therapy?','medication','M05 M04 C01',
 'Technician processes permitted tasks; pharmacist/prescriber provides the relevant professional judgment.',
 'No independent therapy-change authority follows from medication-access assignment.',
 'Pharmacist then prescriber or authorized protocol as relevant.',
 'Specific technician, pharmacist and prescribing permissions remain state/program-specific.', 'B07 B08 R09')
decision('D26','Does psychologist/counselor title imply prescribing?','behavioral','M06 M07 M08',
 'Use actual license and separately granted permissions.',
 'Neither all psychologists prescribe nor a blanket national prohibition is inferred; counselor and psychiatrist roles differ.',
 'Qualified prescribing clinician for medication need.',
 'Jurisdiction and specialty qualification required.', 'B01 B10 B11')
decision('D27','Who can approve information sharing?','privacy','G10 O06 P03',
 'Use purpose, applicable rule/authority and scope; privacy/HIM process resolves uncertain releases.',
 'No blanket all-sharing-needs-written-consent rule; no unrestricted access merely from treating or administrative title.',
 'Privacy/legal channel for unclear authorization or specially protected data.',
 'A10 lists minimum-necessary exceptions including specified treatment disclosures; other protections still apply.', 'A09 A10 R07')
decision('D28','Can interpreter or navigator decide for the patient?','communication','P05 P06 M09 M10',
 'Communication/navigation functions support understanding and access.',
 'No substitute medical/coverage/consent authority follows from those functions.',
 'Return substantive decision to patient/qualified role.',
 'Additional independent license/appointment, if any, must be established separately.', 'B23 R21 R28 A09')
decision('D29','Can a manager overrule a licensed professional on any task?','management','O12 U17 G04 G05',
 'Management may assign work within organizational mandate and lawful scope.',
 'Reporting rank does not expand licensure or satisfy required review independence.',
 'Professional, compliance or appropriate appeal process rather than blind upward approval.',
 'Actual organogram and professional/practice rules required.', 'B22 A13 A14 A03')
decision('D30','Does an EHR administrator have clinical editing authority?','systems','G13 G14 C01',
 'Technical changes/access require authorized purpose and change permissions.',
 'Technical ability is not permission to fabricate clinical content or approve care.',
 'Clinical/policy author for substantive change; privacy/security for access.',
 'Hospital authentication A15 and applicable access controls.', 'A15 A10 B21')
decision('D31','Who decides equipment or transport suitability?','service','M25 M23 M24 C01',
 'Service staff coordinate fulfillment; qualified clinical input handles medical requirements.',
 'Driver, dispatcher or delivery title does not establish clinical assessment authority.',
 'Ordering/responsible clinician and actual qualified service staff.',
 'Exact equipment/transport protocol not established universally; CMS device example is service-specific.', 'R11 R28 R30')
decision('D32','Who approves financial assistance or final payment?','finance','O09 G15 O04',
 'Actual assistance administrator/payer adjudication decides under its program; counselors explain and help applications.',
 'Counseling, eligibility and authorization do not guarantee final payment.',
 'Appropriate assistance/payment-dispute route.',
 'Program and claim rules must be identified.', 'R06 R08 R09')
decision('D33','Does hospice team composition create one boss over every profession?','hospice','M28 C01 C06 M03 M29',
 'CMS 2024 guidance describes qualified interdisciplinary roles; members retain distinct professional scope.',
 'Team label is not identical authority for every member or proof of current complete regulation.',
 'Identify current hospice/attending responsibilities and relevant professional lead.',
 'A08 is a dated transmittal; operational use requires current full applicable hospice requirements.', 'A08 R34')
decision('D34','Does a complaint to a regulator automatically reverse coverage?','oversight','G16 P07 U16',
 'Oversight, consumer assistance and case appeal have distinct mandates.',
 'A complaint is not automatically an appeal or a reversal.',
 'Identify the agency and correct clinical/coverage/rights forum.',
 'Agency jurisdiction and program rules determine action.', 'R35 A11 A12')


# Each flow is an illustrative operational contract unless its sources specify a scoped requirement.
FLOWS = []


def flow(id, sender, receiver, artifact, fields, acknowledgement, failure, condition, sources):
    FLOWS.append(dict(id=id, sender=sender, receiver=receiver, artifact=artifact,
        fields=fields.split('; '), acknowledgement=acknowledgement, failure=failure,
        condition=condition, sources=sources.split(), evidence='Operational synthesis; scoped requirements cited separately'))


flow('F01','P01','O03','Identity / insurance information','Patient identifier; Insurance identifiers; Contact details','Registration match or mismatch recorded','Resolve mismatch before attaching another person\'s records','When registering/requesting service','R03 R06')
flow('F02','C01','O01','Clinical service request','Patient; Requested service; Clinical rationale; Responsible author/date','Request accepted into provider queue','Ask author for clarification; do not invent rationale','When service requires authorization work','R03 R04 A15')
flow('F03','O04','O01','Benefits / requirement finding','Plan; Service; Verification source/date; Unresolved requirements','Coordinator records status and next check','Contact payer on discrepancy','Plan/service-specific check','R03 R06')
flow('F04','O06','O01','Supporting record package','Patient match; Source/date; Relevant clinical reports; Release basis','Records linked to correct request','Query source for missing/incorrect records','When additional records needed','R07 B20 A10')
flow('F05','O01','U01','Authorization submission','Patient/plan; Service; Requesting professional; Supporting record','Payer receipt/case identifier','Track failed transmission and missing items','When request submitted','R03 R04 R12')
flow('F06','U01','O01','Missing-information request','Case identifier; Requested missing items; Response channel','Provider records request and response ownership','Escalate clinical gaps to author','When intake/review needs clarification','R12 R13')
flow('F07','U01','U03','Clinical review case','Matched identifiers; Request; Submitted evidence; Relevant benefit context','Assigned reviewer/status','Return factual gaps; route urgency by policy','When clinical review required','R12 R13')
flow('F08','G03','U03','Applicable approved criteria','Policy/version; Product/service; Effective scope; Evidence/rule basis','Reviewer identifies correct version','Resolve version/product mismatch','Approved-policy use; MA requirements separately A05/A17','A05 A17 R12')
flow('F09','U03','U04','Clinical escalation','Question; Evidence assessed; Criteria; Unresolved reason','Qualified reviewer accepts case','Do not treat inability to approve as unreviewed denial','When delegated first level cannot resolve','R12 A02')
flow('F10','U04','U05','Specialty consultation request','Defined question; Relevant record; Scope and conflict information','Opinion returned with rationale','Request missing evidence/appropriate expertise','When specialist opinion needed','R18 A02')
flow('F11','O11','U04','Peer clinical discussion','Case; Disputed rationale; Additional relevant evidence; Discussion record','Outcome and next formal step recorded','Preserve applicable appeal route independently','Plan-specific peer process','R15')
flow('F12','U04','U09','Authorized clinical determination','Decision; Rationale; Scope/service; Author; Applicable procedural information','Notice prepared from authorized record','Return inconsistency to decision author','When case decision made','A02 R13')
flow('F13','U09','P01','Decision notice','Outcome; Reason; Service/case; Applicable review information','Communication sent/status recorded','Correct failed/mismatched notice through process','Recipients/contents depend on route','R16 R15 A03')
flow('F14','U09','O01','Provider outcome communication','Case; Service; Outcome; Scope/conditions; Next action','Provider updates queue and readiness checks','Clarify ambiguity before assuming approval','As required/permitted in actual process','R13 R15')
flow('F15','O01','O05','Recorded authorization status','Service; Case; Outcome/conditions; Remaining prerequisites','Scheduler records booking or unresolved status','Do not equate booking and clinical readiness','When scheduling depends on status','R03 R05')
flow('F16','P04','U12','Appeal request','Authority/standing; Challenged notice; Grounds; Supporting record','Proper route/case acknowledgement','Resolve missing standing or wrong route','Actual appeal rights and deadlines','R20 A03')
flow('F17','U12','U13','MA reconsideration case','Initial record; New material; Disputed question; Reviewer independence check','Reconsideration assignment/decision','Use appropriate uninvolved physician for scoped medical-necessity reconsideration','MA route described by A03','A03')
flow('F18','U13','U14','Remaining adverse MA case','Disputed issues; Case file; Written explanation','IRE review/disposition recorded','Follow applicable forwarding and record requirements','When MA adverse reconsideration remains','A03 A04')
flow('F19','U14','U09','MA independent-review decision','Case; Outcome; Scope of reversal; Implementation requirement','Effectuation status recorded/communicated','Escalate failure to implement to correct route','MA decision and A16 conditions','A04 A16')
flow('F20','U15','U18','Commercial external-review case','Applicable route; Eligibility; Denial; Record','External-review disposition','Do not route MA automatically here','Eligible commercial external-review process','A12 R17')
flow('F21','P01','M01','Care-management goals and needs','Patient goals; Preferences; Reported barriers; Involvement choices','Needs reflected in coordination assessment','Clarify disagreement; do not invent consent','Program/patient participation context','R22 R23')
flow('F22','C02','M01','Clinical context / referral','Clinical plan; Responsible clinician; Relevant concerns; Follow-up needs','Care-manager review and coordination task','Clarify missing medical ownership','When coordination referred/needed','R22 R24')
flow('F23','M01','M02','Psychosocial resource referral','Specific need; Agreed information; Desired follow-up','Assessment/resource response','Return unmet need to coordinator','When appropriate social support needed','R25 B09')
flow('F24','M01','M04','Medication review request','Medication information; Clinical question; Responsible prescriber','Pharmacist recommendation/clarification','Refer order changes to authorized prescriber/protocol','When medication review needed','B07 R24')
flow('F25','M04','C01','Medication recommendation','Identified concern; Evidence; Recommendation; Urgency/context','Prescriber response or authorized protocol action','Do not silently assume recommendation changed order','Professional relationship/protocol-specific','B07 A15')
flow('F26','M01','M10','Navigation task','Barrier; Patient preference; Service contact; Follow-up need','Connection/status returned','Report unresolved access rather than assume success','When navigation assigned','R28')
flow('F27','M10','M22','Community service referral','Agreed need; Relevant eligibility information; Contact','Service acceptance/status','Notify coordinator of waiting/refusal/absence','Agency-specific sharing and availability','R28 R29 A10')
flow('F28','M01','M23','Transport arrangement','Appointment/trip; Contact; Accessibility needs','Booking status returned','Clarify clinical transport needs','When travel support needed','R28 B19')
flow('F29','M23','M24','Assigned transport','Pickup/destination; Time/contact; Necessary access instructions','Completion/failure status','Notify dispatcher of failed trip','Actual service qualification and permissions','R28 A10')
flow('F30','C01','M25','Equipment order','Patient; Ordered equipment; Clinical/order author; Requirements','Supplier acceptance/service status','Resolve missing order or unsuitable service with clinician','Equipment-specific pathway','R11 R30')
flow('F31','M18','M19','Home-health transition referral','Clinical course; Goals/preferences; Orders/plan; Pending needs','Agency acceptance/capacity and plan coordination','Return unavailable service or missing order','Hospital transition plus home-health setting','A06 A07')
flow('F32','M18','M20','Facility transition record','Clinical course; Goals; Relevant care needs; Pending issues','Receiving service acceptance/handoff','Resolve missing/unavailable care with sending team','Hospital to receiving facility','A06')
flow('F33','M19','C01','Home-health change request','Changed assessment; Need/response; Proposed plan revision','Authorized response and plan communication','Do not freely rewrite orders','484.60 setting and signatory rules','A07')
flow('F34','M21','C06','Home-support observations','Assigned task; Completion; Observed concern','Qualified review/escalation','Use supervising professional for concern outside training','Actual home-aide supervision','B19 B04')
flow('F35','M14','M01','Functional progress','Assessment; Goals; Response; Unresolved needs','Coordination plan updated','Route medical or resource issue to owner','When PT involved','B15 R22')
flow('F36','M01','G05','Complex-case escalation','Unmet need; Actions attempted; Clinical/resource question','Assigned supervisory response','Separate clinical authority from workload decision','Assigned supervisory relationship only','R32')
flow('F37','G06','G03','Policy-quality finding','Pattern; Measure/record basis; Policy version; Limitations','Policy review/revision disposition','Do not retroactively change case evidence','When systemic criteria issue identified','A05 R12')
flow('F38','G08','G07','Approved procedural change','Approved version; Effective scope; Training implications','Training updated and delivered','Do not teach draft as approved policy','Designated approval/change process','R32')
flow('F39','G10','G14','Access authorization decision','User/role; Purpose; Permitted scope; Approval','Access provisioning/audit result','Escalate unmatched permissions','Authorized local access-control process','A10 B21')
flow('F40','G12','G13','Approved system requirements','Business owner; Intended behavior; Permissions; Acceptance conditions','Validated implementation or rejected change','Clinical/policy owner resolves substantive ambiguity','Authorized change process','B21 R32')
flow('F41','O07','G15','Supported claim coding','Service/documentation; Supported codes; Relevant clarification','Claim/account work recorded','Return unsupported code or documentation issue','Downstream billing, not authorization completion','B20 R08')
flow('F42','U14','J01','Eligible MA further appeal record','Prior decision; Proper request; Record; Jurisdiction conditions','Adjudicative disposition','No automatic right inferred from dissatisfaction','When further MA appeal is available','A11 A16')
flow('F43','J01','J02','Eligible Council review','Prior decision; Eligible request; Record','Council disposition','Follow actual review notice/rules','When Council review properly pursued','A11 A16')
flow('F44','J02','J03','Eligible judicial review','Administrative record; Eligible filing; Legal issues','Judicial disposition','Check jurisdiction/exhaustion/thresholds','When judicial review legally available','A11')
flow('F45','P05','C01','Interpreted patient-clinician message','Original meaning; Relevant clarification; Communication context','Participants can clarify meaning','Return substantive question to patient/clinician','When qualified interpretation needed','B23 R21')
flow('F46','O06','G10','Unclear disclosure request','Request/purpose; Identity/authority; Specific privacy question','Scoped privacy guidance','Do not release all data from uncertainty','When release authority/purpose unclear','A09 A10 R07')
