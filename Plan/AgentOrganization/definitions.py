"""Authored organizational hypotheses; not an implemented runtime or authority grant."""

PACKAGES={}


def package(id,title,roles,mode,work,merge,retain,test):
    PACKAGES[id]=dict(id=id,title=title,roles=roles.split(),mode=mode,work=work,merge_rationale=merge,retained_boundary=retain,split_trigger=test,status='PROPOSED_NOT_EMPIRICALLY_TESTED')


package('W01','Patient and support participants','P01 P02 P03','external',
 'Obtain goals, observations and applicable representation facts through permitted interaction.',
 'Represent related participants in one case model, with separate identities and statement attribution; do not replace them with a worker that supplies convenient answers.',
 'Patient choice, caregiver observation and lawful representation are different facts. Family relationship does not establish decision authority.',
 'A merged record attributes caregiver wishes to the patient or treats missing consent as agreement.')
package('W02','Advocacy and assistance interfaces','P04 P07 U16','external',
 'Clarify complaints, access barriers and permitted representative assistance.',
 'Shared navigation and document-preparation capability may support several functions, while appointments and authority remain explicit.',
 'Appeal appointment is distinct from treatment representation; assistance is not insurer or adjudicator decision power.',
 'One general advocate label silently grants authority over every dispute or patient decision.')
package('W03','Language and communication support','P05 P06','capability',
 'Support oral/written communication without changing the substantive author or decision owner.',
 'One language service can expose separate interpretation and translation operations; a persistent autonomous persona is not inherently needed.',
 'Written fidelity, oral turn-taking, participant comprehension and substantive consent must remain distinguishable. Qualification is not proved by a language prompt.',
 'Translation drops a negation, invents an answer, or is recorded as informed understanding without evidence.')
package('W04','Treating-team and clinical-evidence interfaces','C01 C02 C03 C04 C05 C06 C07 C08 O13 M06 M27','external',
 'Request and attribute existing clinical assessments, orders, referral context and externally produced evidence.',
 'A shared evidence-request adapter may serve these contacts; that is an interface merger, not one interchangeable clinical occupation.',
 'Credential, jurisdiction, privileges, authorship and treating relationship remain distinct; reading a chart is not performing treatment or acquiring prescribing authority.',
 'The harness fabricates a clinician statement or treats every clinical title as equivalent signatory permission.')
package('W05','Provider access and authorization operations','O01 O02 O03 O04 O05 O09 O12','merge_candidate',
 'Identify the case, check administrative requirements, assemble supported materials, submit, track and coordinate scheduling/access barriers.',
 'These operations can share a case record and an accountable workflow owner; combining them may reduce summary handoffs.',
 'Identity, coverage verification, authorization outcome, financial estimate and service booking are different states. Management rank does not confer clinical power.',
 'Measured merged execution repeatedly confuses administrative states, loses obligations or lacks genuinely different access scopes.')
package('W06','Records, coding and documentation support','O06 O07 O08','capability',
 'Retrieve authentic records and identify coding/documentation questions with source attribution.',
 'A bounded evidence-preparation capability can combine retrieval and consistency checks without multiple autonomous writers.',
 'Record release, coding interpretation, clinical clarification and authentication are distinct. Staff must not create unsupported clinical facts.',
 'A merged evidence worker silently repairs a clinical fact instead of requesting clarification or preserving uncertainty.')
package('W07','Provider dispute preparation and clinical exchange','O10 O11','conditional',
 'Assemble the correct challenge and preserve clinical contributions and process status.',
 'Administrative filing preparation and evidence collection may share a workflow; clinical peer participation remains an explicitly authorized interface.',
 'Peer discussion is not automatically formal appeal; filing, clinical argument, appointment, deadline and acceptance are separate.',
 'A merged job claims a successful appeal from a peer-discussion note or submits an unattributed clinical opinion.')
package('W08','Payer intake, benefits and status operations','U01 U02 U10 U11 U17','merge_candidate',
 'Establish administrative context, collect information, route work and communicate observed status.',
 'A common payer case owner can combine collection and service/status functions with role-scoped operations.',
 'Limited delegated nonclinical decisions are program-specific; medical-necessity denial and general benefits/status work remain different permissions.',
 'Status communication becomes an invented determination, or a clinically complete review is forced after a valid administrative terminal path.')
package('W09','Initial review and specialty reasoning','U03 U04 U05 U06 U07 U08','conditional',
 'Evaluate applicable criteria and evidence, request needed specialty input, and propose only authorized case actions.',
 'Shared policy/evidence machinery can serve distinct review modes; separate bounded reasoning calls may be useful for genuinely different questions.',
 'Professional expertise, delegation, recommendation versus determination, and actual signoff remain separate. R13 signoff tension is unresolved; delegation may exclude appeals.',
 'A shared review mode crosses product/delegation limits, hides conflicting evidence or requires more independent expertise than its input supports.')
package('W10','Notice preparation and delivery','U09','capability',
 'Render and deliver the observed authorized decision with the appropriate reason and review information.',
 'This can be a controlled operation of the payer workflow owner rather than another open-ended agent.',
 'The notice must derive from the authoritative decision/version; drafting or delivery must not change the substantive decision.',
 'Notice text contradicts the stored decision, wrong recipient is used, or draft is recorded as delivered.')
package('W11','Internal appeal administration and reconsideration','U12 U13','protected_review',
 'Establish standing/route, assemble the appeal record and obtain the applicable reconsideration outcome.',
 'Filing support may share software, but do not collapse initial-decision ownership and a required uninvolved reconsideration function.',
 'For the cited MA rule, actual uninvolved persons and appropriate physician expertise are requirements; a fresh LLM context is not proof of those human qualifications.',
 'The initial author self-certifies independent reconsideration merely by changing its role label.')
package('W12','External review and adjudication interfaces','U14 U15 U18 G16 J01 J02 J03','external_review',
 'Identify the applicable external route, transmit authorized material, and observe externally issued outcomes.',
 'A routing adapter can share transport/record plumbing, while preserving distinct institutions, jurisdiction, eligibility and decision authority.',
 'MA IRE, commercial IRO, regulator, ALJ, Council and court are not one escalating internal worker. External decisions cannot be invented by a local reviewer persona.',
 'A harness creates a binding external reversal or moves automatically through every forum without eligibility.')
package('W13','Care coordination and follow-through','M01 M09 M10 M11 M13 M18 M30','merge_candidate',
 'Maintain goals, assessment context, referrals, outreach, barriers and observed follow-through across care transitions.',
 'A case owner can combine administrative coordination, navigation and general education support while invoking specific expertise when needed.',
 'Clinical assessment permissions, patient statements, discharge authority and professional education scope remain explicit; coordination is not physical service delivery.',
 'A merged worker loses patient dialogue state, invents assessment answers, or marks a referral as completed care.')
package('W14','Psychosocial and behavioral-health interfaces','M02 M03 M07 M08','conditional',
 'Identify psychosocial needs and interpret or request appropriate specialist contributions.',
 'Common intake/resource-finding support can be shared; separate expertise and restricted information views may be necessary for specialist reasoning.',
 'Job title, independent clinical licensure and additional prescribing certification differ. Do not collapse social support, therapy and prescribing.',
 'A generic behavioral-health persona acts beyond its assigned function or exposes protected material to unrelated work.')
package('W15','Medication review and access','M04 M05','conditional',
 'Distinguish medication expertise, existing therapy instructions and administrative access/fulfillment work.',
 'Share a medication evidence record and access workflow, while separating clinical proposals from technician/access operations.',
 'Protocol-authorized pharmacist activity, general prescribing and technician tasks are not equivalent; local authority is unresolved.',
 'Medication availability is treated as a treatment order or access staff alter therapy.')
package('W16','Rehabilitation, nutrition and respiratory interfaces','M12 M14 M15 M16 M17','conditional',
 'Request or summarize discipline-specific assessments and service needs.',
 'Use a common referral/evidence adapter with discipline-specific capability selection; persistent workers only if workload and errors justify them.',
 'Different disciplines assess different functions and have different scope; one capability catalogue is not interchangeable clinical expertise.',
 'A general specialist output substitutes nutrition, mobility, daily-function, communication or respiratory evidence for one another.')
package('W17','Receiving services and real-world fulfillment','M19 M20 M21 M22 M23 M24 M25 M26','external_service',
 'Coordinate service acceptance, availability, scheduling and observed delivery/attendance evidence.',
 'A shared logistics coordinator can manage requests; providers, workers and actual delivery remain distinct external parties/events.',
 'Referral sent, accepted, scheduled, delivered and completed are separate states. Capacity and actual attendance must come from allowed observations.',
 'A dispatcher persona or optimistic plan is used as evidence that a person received care, transport, food or equipment.')
package('W18','Hospice and spiritual-care interfaces','M28 M29','external',
 'Coordinate the appropriate hospice group/attending and spiritual support contributions.',
 'Common communication plumbing may connect participants; the composite hospice profile must be decomposed into functions before creating worker identities.',
 'IDG planning, designated RN coordination, attending, certification/admission and spiritual support are distinct; the cited hospice evidence is the 2025 edition.',
 'One hospice agent is assigned all professional decisions or spiritual support is treated as clinical certification.')
package('W19','Safeguarding and protection interface','M31','external',
 'Recognize a potential protection concern and follow an actually applicable reporting/escalation pathway.',
 'Detection and routing can be a capability of a case owner; legal investigation/protection authority remains external.',
 'Applicable mandate, jurisdiction, urgency and APS phase-in facts cannot be inferred from a generic concern. Child/adult pathways are not identical.',
 'A model resolves a safeguarding case by assertion or invents a universal reporting rule.')
package('W20','Policy, legal and clinical governance','G01 G02 G03 G08 G09 G17','governance',
 'Establish applicable policies, approved versions and unresolved governance/legal questions.',
 'Share policy retrieval and change tracking; proposal, clinical governance, committee approval and legal advice remain separately attributed functions.',
 'An analyst draft or agent-generated rule is not approved policy. Provider and payer leaders have different mandates; hierarchy is not global authority.',
 'A task worker rewrites the controlling rule or approves its own policy revision to make a case pass.')
package('W21','Management, quality, analytics and learning','G04 G05 G06 G07 G11 G12','governance',
 'Manage process design, training, workload and aggregate quality analysis outside ordinary case execution.',
 'A design-time analysis service may cover several functions, while runtime checks remain bounded and separate from official grading.',
 'Operational management is not clinical or appeal authority; internal diagnostics must not read hidden verifier answers or masquerade as official scores.',
 'Training feedback contaminates held-out evaluation, or a self-audit is reported as independent official success.')
package('W22','Privacy and system-access controls','G10 G13 G14','infrastructure',
 'Constrain record access, authorized operations and technical identity/support.',
 'Prefer explicit permission/configuration machinery plus escalation where uncertain; a persona alone cannot enforce access.',
 'Technical access is not consent, clinical permission or substantive authorship; privacy purpose and special restrictions remain explicit.',
 'Every worker receives all tools/data because one shared model is assumed to have global authority.')
package('W23','Billing and post-service account interface','G15','external_service',
 'Track account/claim status and administrative payment questions when actually in scope.',
 'Share identifiers and authorized documents with access/dispute workflows; invoke payment reasoning only where needed.',
 'Prior authorization, benefit verification, claim acceptance, adjudication and payment are different states.',
 'Authorization success is reported as a paid claim or a completed financial outcome without evidence.')


ROLE_NOTES={}


def role(id,package,form,question,distinction,failure):
    ROLE_NOTES[id]=dict(package=package,representation=form,key_question=question,distinction=distinction,counterexample=failure)


role('P01','W01','external_actor','Whose expressed preference is being recorded, and what observation establishes it?','Patient answers must be observed; a simulated internal patient must never supply the benchmark patient response.','A coordinator writes consent because its own patient persona agreed.')
role('P02','W01','external_actor','Is this statement a caregiver observation or the patient’s own choice?','Practical support and representative authority are separate.','Caregiver availability is mistaken for patient willingness.')
role('P03','W01','external_actor','What establishes this representative’s authority for this specific decision?','Appointment/scope evidence belongs in state, not an assumed family-role prompt.','A family contact receives unrestricted records without applicable authority.')
role('P04','W02','external_actor','Does the appointment cover this dispute, this action and this stage?','Dispute representation is not treatment consent or insurer decision power.','A generic advocate drafts an authorized signature it cannot substantiate.')
role('P05','W03','communication_adapter','Does the interpreter preserve speaker attribution and unanswered questions?','Interpretation supports the conversation; it cannot create clinical answers.','An interpreter fills a missing assessment answer to keep dialogue moving.')
role('P06','W03','communication_adapter','Can the written output be checked for omissions, negation and ambiguity?','Translation and comprehension are separate evidence.','A translated letter is recorded as proof the patient understood it.')
role('P07','W02','external_actor','Is this an access complaint, clinical issue or formal appeal?','Navigation may be shared; case resolution authority must be identified.','A patient-relations response is treated as a coverage reversal.')
role('C01','W04','external_actor','Which clinical facts/orders were actually authored by the treating professional?','The solver may organize evidence without impersonating the author.','A stronger medical rationale is invented and attributed to the physician.')
role('C02','W04','external_actor','Does the referral establish an indication, an order, or only a request for evaluation?','Referral and authorization functions can share tracking but retain different authors.','A referral becomes specialist acceptance without a receiving response.')
role('C03','W04','external_actor','What specialty evidence is available and which missing assessment needs an external contribution?','Specialty framing is not evidence that an examination or procedure occurred.','A specialist persona supplies a result absent from the permitted record.')
role('C04','W04','external_actor','Which jurisdiction, practice category, furnishing authority and employer conditions apply?','One clinician interface can support several credentials without treating them as interchangeable.','The harness converts an NP role prompt into universal independent prescribing permission.')
role('C05','W04','external_actor','Does the applicable arrangement require supervision, collaboration or another defined condition?','Terminology and practice arrangement vary; fixed national hierarchy is unsupported.','A universal physician-signoff requirement is imposed or removed without evidence.')
role('C06','W04','external_actor','Is the task nursing assessment, care coordination or direct service documentation?','The same RN may hold several functions; the assigned function and observed work still matter.','A care-coordination note is recorded as a completed nursing visit.')
role('C07','W04','external_actor','What activity is permitted under the actual license and supervision arrangement?','Shared nursing data does not erase RN/LPN role differences.','A merged nursing agent inherits the most permissive scope of either label.')
role('C08','W04','external_actor','Which administrative/support observation needs review by an authorized clinician?','Clinical support can share collection tools without autonomous medical conclusions.','Rooming/support information becomes an independent diagnosis.')
role('O01','W05','task_scoped_worker','What observable event shows the supported request was submitted and what remains unresolved?','Preparation, submission, receipt and outcome must remain separate.','A polished packet is reported as submitted without a tool receipt.')
role('O02','W05','role_mode','Who owns the unanswered referral and what shows it reached the receiver?','Common tracking can merge with authorization, but referral acceptance is its own event.','A sent referral is mistaken for accepted service.')
role('O03','W05','tool_supported_mode','Which identifiers prove the evidence and task concern the same case?','Identity checking should be explicit even when the same worker assembles the packet.','A similar-name record is merged into the wrong case.')
role('O04','W05','role_mode','Is this a benefit fact, an authorization requirement or a guarantee of payment?','Benefits lookup can share the workflow owner without deciding clinical necessity.','Verified benefits are treated as service approval.')
role('O05','W05','role_mode','What prerequisites and actual capacity must be satisfied before booking?','Scheduling may merge administratively; booked, cleared and performed remain distinct.','A scheduled visit closes the care-completion obligation.')
role('O06','W06','bounded_capability','What records may be released for this purpose and who authored them?','Authenticity, release authority and clinical meaning need separate provenance.','The evidence worker fabricates a missing clinical detail while assembling records.')
role('O07','W06','bounded_capability','Does a code reflect supplied documentation or an unsupported diagnostic inference?','Code suggestions can be a module; they do not establish new clinical facts.','A billing code is used to prove a diagnosis absent clinical support.')
role('O08','W06','bounded_capability','Should an inconsistency trigger a clarification query rather than an automated repair?','Documentation consistency review can be shared; substantive corrections require appropriate authorship.','The agent resolves a conflict by silently rewriting the clinical source.')
role('O09','W05','role_mode','Which affordability barrier and assistance option are actually supported?','Financial coordination can merge with access work; eligibility/awards remain observed outcomes.','An assistance application is reported as approved funding.')
role('O10','W07','task_scoped_worker','Which dispute route preserves the correct issue, standing and filing status?','Administrative dispute preparation can be shared without impersonating clinical peer review.','A complaint or peer discussion is treated as a filed formal appeal.')
role('O11','W07','external_actor','What actual clinician contribution is required for this peer exchange?','Clinical argument and filing mechanics have different owners even if software coordinates both.','A local reviewer persona is presented as the real participating physician.')
role('O12','W05','configuration_or_escalation','Is the issue workload/process authority or a substantive clinical/coverage decision?','Operational supervision can be a routing policy; it does not enlarge permissions.','A supervisor override bypasses a clinical requirement.')
role('O13','W04','external_actor','Can the result be traced to an actual test, assessor, document or custodian?','Evidence requests and evidence creation cannot collapse into the same unsupported assertion.','The harness invents a missing external result to complete the packet.')
role('U01','W08','task_scoped_worker','Is this collection/routing or an explicitly delegated limited nonclinical decision?','Do not prohibit every nonclinical approval or grant unrestricted denial power.','An intake case is denied for medical necessity by an unqualified administrative mode.')
role('U02','W08','role_mode','Which product/eligibility facts authorize this particular administrative outcome?','Benefit-only and medical-necessity conclusions remain distinct.','A coverage mismatch becomes an unsupported clinical denial.')
role('U03','W09','task_scoped_review_mode','What can the initial reviewer conclude versus recommend or escalate?','Reusable policy checks need an explicit review-stage and permission envelope.','The first-level mode assumes it can sign every denial.')
role('U04','W09','task_scoped_review_mode','Which case decision is authorized, and is this person/function initial reviewer or reconsiderer?','Expert review does not supply independence from an earlier determination.','A medical-director title is used to make a self-review independent.')
role('U05','W09','bounded_specialist','Is the consultant offering evidence/advice or issuing the authoritative determination?','A fresh specialist context may broaden analysis without owning the decision.','A consultation recommendation is persisted as a final outcome without the authorized step.')
role('U06','W09','bounded_specialist','Does the service require behavioral-health criteria or restricted evidence handling?','Specialty scope and information sensitivity can justify isolation; frequency still needs measurement.','A general review mode ignores behavioral-health-specific requirements.')
role('U07','W09','bounded_specialist','Is this pharmacy coverage review, medication advice or treatment authority?','A pharmacy capability may share evidence infrastructure without acquiring all three powers.','A formulary observation is converted into a medication change.')
role('U08','W09','delegation_boundary','What is delegated for this product, including what is expressly retained by the plan?','Delegated initial review does not automatically include appeals processing or signoff.','The delegate agent decides an appeal excluded by its actual agreement.')
role('U09','W10','controlled_operation','Does the notice exactly correspond to the stored decision, version and recipient?','Rendering and delivery can merge into a workflow owner; neither may invent an outcome.','A generated notice changes the reason or outcome without updating authority/state.')
role('U10','W08','role_mode','What status can be truthfully explained from the current authoritative record?','Member-facing wording differs from decision authority.','A reassuring conversation is recorded as approval.')
role('U11','W08','role_mode','What does the provider need to supply or do next, and is that an observed requirement?','Provider-service communication can share intake state with explicit provenance.','A service representative invents an additional clinical criterion.')
role('U12','W11','task_scoped_worker','Is the submission a grievance, reconsideration, external request or another route?','Appeal administration is separable from substantive reconsideration.','Administrative acceptance is mistaken for a favorable appeal decision.')
role('U13','W11','protected_review','How is uninvolved review established beyond using a different prompt?','The cited human independence/expertise rule is not satisfied by naming an LLM physician.','The initial author changes its persona and self-certifies compliant reconsideration.')
role('U14','W12','external_review_actor','What actual CMS-contracted review outcome and route apply?','MA independent review is not an internal model critic or commercial IRO.','A harness-generated critique is called an official IRE reversal.')
role('U15','W12','external_route_adapter','Which state/federal process and eligibility govern the external-review request?','Routing administration can share transport code without owning adjudication.','The request is sent through a convenient but inapplicable route.')
role('U16','W02','external_actor','Does the assistance function inform, represent, or decide the matter?','Consumer assistance does not imply insurer or court authority.','Advice from an assistance persona is recorded as binding coverage.')
role('U17','W08','configuration_or_escalation','Can a process manager resolve this queue issue without changing clinical judgment?','Operational allocation is a separate axis from reviewer expertise.','Higher operational rank overrides a scoped clinical requirement.')
role('U18','W12','external_review_actor','Does this issue qualify for the applicable commercial external route, including urgent concurrency?','Commercial review remains separate from MA IRE and ordinary peer discussion.','The system forces all urgent cases to finish every internal step first.')
role('M01','W13','task_scoped_worker','What unresolved patient goal or service obligation still has a named owner?','One case owner can combine coordination functions while retaining evidence and professional boundaries.','A plan exists but outreach, referral response or follow-up is never completed.')
role('M02','W14','bounded_specialist','What social-work function and credential level are actually relevant?','Clinical job wording may include supervised pre-licensure work; title is not independent licensure.','A generic social-work persona supplies unrestricted psychotherapy authority.')
role('M03','W14','external_actor','Is the requested contribution clinical social-work assessment/therapy or practical resource coordination?','Share referral plumbing while preserving independent clinical scope and source attribution.','A resource-coordination summary is treated as a completed clinical assessment.')
role('M04','W15','bounded_specialist','Which medication action is advice, protocol-authorized activity or a new order?','Pharmacist pathways vary; neither universal physician reapproval nor universal independence is inferred.','The system changes therapy based solely on its pharmacist label.')
role('M05','W15','role_mode','What access/fulfillment information is missing without requiring clinical medication decisions?','Technician/access operations can share medication state but not clinical permissions.','A stock or authorization issue is resolved by changing the medication.')
role('M06','W04','external_actor','What psychiatric assessment/order is present versus needing an external clinician?','Specialist evidence may be requested; a solver prompt is not an actual consultation.','An invented psychiatric evaluation fills an evidence gap.')
role('M07','W14','bounded_specialist','Does this contribution require ordinary psychology scope or additional prescribing certification?','Additional local certification is not implied by general psychology credentials.','A psychologist persona is granted prescribing authority in every jurisdiction.')
role('M08','W14','external_actor','What counseling function and restricted-record conditions apply to this service?','Counseling, diagnosis and information-sharing permissions must be specified separately.','A general case summary discloses specially protected material to every worker.')
role('M09','W13','role_mode','Which practical barrier comes from the patient/community context rather than chart inference?','Community navigation can share coordination state without inventing local resource availability.','A plausible community resource is described as accepting the patient without confirmation.')
role('M10','W13','role_mode','What obstacle is being navigated and which recipient owns the next response?','Navigation and provider/care coordination overlap but do not grant every institution’s access.','The agent treats navigation across organizations as unrestricted write access.')
role('M11','W13','role_mode','Which task is nonclinical support and which needs clinical interpretation?','A combined case owner must retain activity-level limits.','A nonclinical guide interprets clinical change as a treatment decision.')
role('M12','W16','bounded_specialist','What nutrition assessment or plan contribution is actually evidenced?','Diet education and individualized professional assessment are different contributions.','A generic healthy-eating paragraph is called a completed nutrition assessment.')
role('M13','W13','role_mode','Does education reflect an existing plan and the person’s stated understanding?','General education can merge into outreach; it must not replace consent or invent comprehension.','Information delivered is reported as demonstrated patient understanding.')
role('M14','W16','bounded_specialist','Which mobility/rehabilitation facts support this referral and what local access rule is unknown?','The previous audit did not establish a specific direct-access state rule.','The harness assumes either universal direct access or universal physician referral.')
role('M15','W16','bounded_specialist','What daily-activity/environment assessment differs from mobility-only evidence?','Shared rehabilitation routing must preserve occupational-therapy content.','A physical-therapy summary substitutes for daily-function assessment.')
role('M16','W16','bounded_specialist','Is the need communication, swallowing or another documented function requiring the right evidence?','Speech-language expertise is not generic language translation.','The communication adapter claims a clinical speech/swallow evaluation.')
role('M17','W16','bounded_specialist','What respiratory assessment/instruction is present and which service needs professional input?','Equipment logistics and respiratory clinical assessment cannot be equated.','An oxygen/equipment delivery record is used as evidence of clinical reassessment.')
role('M18','W13','role_mode','Which transition tasks are complete, and what clinical discharge authority is outside coordination?','Transition coordination can share a case owner without owning every discharge decision.','The coordinator declares medical readiness from an administrative checklist.')
role('M19','W17','external_service_actor','Has the receiving home-health service accepted the referral and documented its actual prerequisites?','Sending, acceptance, ordered plan and actual visit are separate events.','Home-health referral sent is recorded as a completed visit.')
role('M20','W17','external_service_actor','What shows receiving-facility acceptance, capacity and handoff acknowledgement?','A local coordinator cannot invent another institution’s bed or acceptance decision.','A preferred discharge destination is treated as an accepted placement.')
role('M21','W17','external_service_actor','What evidence shows personal-care work actually occurred rather than being arranged?','A physical service worker is not an LLM reasoning role.','A scheduled aide visit is represented as delivered care.')
role('M22','W17','external_service_actor','Which resource is eligible, available and actually accepted for this person?','Resource discovery, application, approval and delivery need distinct states.','A housing/food resource listed online is reported as secured assistance.')
role('M23','W17','role_mode','Is the trip merely requested, confirmed, dispatched or completed?','Transport coordination can merge with logistics; execution remains externally observed.','A trip request is treated as attendance at care.')
role('M24','W17','external_service_actor','What observation establishes pickup, delivery or a failed trip?','A driver persona cannot physically deliver a person.','The model invents transport completion to close the case.')
role('M25','W17','external_service_actor','What confirms supply, delivery/fitting and any required receiving acknowledgement?','Ordering equipment and its real fulfillment are separate responsibilities.','An equipment order is reported as installed and usable without confirmation.')
role('M26','W17','external_service_actor','Which receiving-service acceptance, scheduling and clinical prerequisites remain outstanding?','Service coordination cannot supply all fulfillment/clinical evidence itself.','An infusion referral is labeled administered treatment.')
role('M27','W04','external_actor','Which palliative contribution is relevant without assuming hospice enrollment?','Palliative care and hospice participation are not interchangeable pathways.','A palliative referral triggers an invented hospice certification.')
role('M28','W18','composite_external_functions','Which IDG, RN coordination, attending, certification or admission function is needed?','The existing composite profile is a warning against one-role/one-agent mapping.','A single hospice worker is assigned every signatory function from a group description.')
role('M29','W18','external_actor','What spiritual support did the person request or accept?','Spiritual support can be coordinated without assuming beliefs or clinical decision authority.','The model invents spiritual preferences or treats support as clinical consent.')
role('M30','W13','role_mode','Which scheduling/follow-up task can be closed with an observed response?','Administrative care support can share the case owner while clinical conclusions remain scoped.','A reminder sent becomes a completed assessment.')
role('M31','W19','external_actor','Which actual protection pathway, jurisdiction and mandate must be established?','Concern detection and mandated reporting/investigation are different functions.','A protection persona is assumed to resolve a legally governed safeguarding matter.')
role('G01','W20','governance_interface','Is this a provider governance mandate or a case-level treating/review function?','A leadership title is not authority over payer determinations.','Provider leadership is modeled as the payer reviewer’s boss.')
role('G02','W20','governance_interface','Is the action policy/program oversight or a separately assigned case determination?','One person can hold both functions, but attribution and authority still differ.','Program leadership is treated as independent appeal jurisdiction.')
role('G03','W20','governance_interface','Which policy/version was actually approved by the relevant process?','A committee is a governance function, not one agent whose generated opinion changes rules.','A policy-synthesis agent approves its own novel criterion.')
role('G04','W21','configuration_or_escalation','What management decision concerns assignment/process rather than clinical override?','Shared operational control can allocate work without inventing clinical seniority.','The orchestrator is labeled director and given every professional permission.')
role('G05','W21','configuration_or_escalation','Which supervision relationship and professional scope are actually documented?','RN/LVN/nonclinical supervisory titles do not prove identical powers.','A manager/supervisor collaboration edge becomes a universal command chain.')
role('G06','W21','development_capability','Is this an internal quality check, an independent review or the official benchmark result?','A bounded critic can aid quality without becoming an adjudicator or hidden verifier.','A model’s own success declaration is reported as official pass evidence.')
role('G07','W21','development_capability','Which observed failure justifies a reusable instruction change?','Training updates should use permitted development evidence and preserve held-out evaluation.','A task-specific answer is embedded into a general role prompt.')
role('G08','W20','bounded_capability','Is a retrieved rule current/applicable, a draft interpretation or an approved controlling policy?','Retrieval and policy interpretation can be shared; policy approval remains separate.','A generated policy summary overrides the actual cited rule.')
role('G09','W20','governance_interface','What requirement applies to the actual product/setting and what remains unverified?','Compliance review can identify questions without inventing permissions or deadlines.','A generic compliance persona certifies every jurisdiction.')
role('G10','W22','configuration_or_escalation','What purpose, recipient and protected material determine this information view?','Prompt separation alone is not access control; treatment exceptions and other restrictions remain scoped.','All workers receive the whole chart because they belong to one software system.')
role('G11','W21','development_capability','Which aggregate outcome metric is observed rather than inferred from a role narrative?','Population analysis is design-time unless the assigned task actually requires it.','Aggregate data is treated as a patient-specific fact or an unmeasured improvement.')
role('G12','W21','development_capability','Which process bottleneck is supported by measured traces rather than a diagram edge?','The old dependency graph is a model, not measured interaction frequency.','Clustering the 219 modeled arrows is presented as an empirically optimal architecture.')
role('G13','W22','infrastructure','Does a technical operation alter presentation, access or substantive clinical state?','An EHR support interface is infrastructure, not a hidden source of decision power.','System access is used to rewrite a clinical fact without an authorized author.')
role('G14','W22','infrastructure','Which identity and tool permission are granted for this exact task principal?','Use explicit scoped operations; one shared model identity does not imply global access.','Role prompts are treated as enforceable security while every worker retains all credentials.')
role('G15','W23','external_service_actor','Which payment/claim event is actually in scope and observed?','Account handling can share documents with authorization while preserving distinct financial state.','Authorization or coverage verification is reported as a paid claim.')
role('G16','W12','external_review_actor','What oversight power and case route are actually invoked?','A regulator is not a universal super-agent or ordinary appeal endpoint.','A local model manufactures a regulatory ruling to resolve disagreement.')
role('G17','W20','governance_interface','Is this administrative assistance, legal analysis or actual authorized representation?','A legal capability does not make a model a licensed representative or court.','A generated legal argument is labeled a binding legal outcome.')
role('J01','W12','external_review_actor','Are this appeal’s jurisdiction and procedural prerequisites established?','Adjudication is an external process; an internal reviewer cannot supply its ruling.','An agent judge is substituted for the actual eligible appeal forum.')
role('J02','W12','external_review_actor','What actual Council review/disposition is available for this case?','This is a distinct forum, not the next internal managerial approval.','The system assumes every ALJ case automatically proceeds to Council.')
role('J03','W12','external_review_actor','Which judicial prerequisites and actual disposition are established?','A court is neither a callable internal helper nor a guaranteed final step.','A simulated court persona creates an authoritative judgment.')
