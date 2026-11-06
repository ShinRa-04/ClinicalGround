"""Authored hypothetical design catalogue; no agents/services are instantiated."""
MODULES=[]


def module(id,name,kind,principal,roles,trigger,work,writes,boundary,services):
    MODULES.append(dict(id=id,name=name,kind=kind,principal=principal,source_roles=roles.split(),trigger=trigger,
        responsibility=work,allowed_write_intent=writes,retained_boundary=boundary,service_ids=services.split(),
        status='HYPOTHETICAL_NOT_IMPLEMENTED',instances='On demand by organization, case, assignment and role; not one global persona.'))


module('A01','Hospital operations coordinator','controller','hospital','O12',
 'A patient journey or capacity/ownership exception needs cross-department coordination.',
 'Track queues, responsible departments, blocked obligations, capacity and service handoffs using a minimal operational view.',
 'Operational tasks, assignments and proposed scheduling changes under actual scope.',
 'Does not overrule patient consent, clinical judgment, payer decisions or external appeal bodies.', 'S01 S08 S09 S10 S14 S15 S16 S17')
module('A02','Provider PA case owner','case_owner','provider','O01 O10',
 'An assigned provider authorization/request/dispute task needs action.',
 'Maintain the supported request, evidence gaps, submission/receipt, payer correspondence and correct dispute route.',
 'Provider case workspace, submissions and observed status through permitted operations.',
 'Cannot invent clinical facts or treat submission, authorization, scheduling and payment as one state.', 'S01 S02 S03 S04 S05 S07 S12 S13 S14 S17')
module('A03','Payer UM case owner','case_owner','payer','U01 U08 U10 U11 U17',
 'An assigned payer case arrives or review/notice/implementation work remains.',
 'Coordinate intake, benefit context, applicable review, actual authority assignment, determination and notice obligations.',
 'Payer case transitions only with the applicable operation-level task/role permission.',
 'Payer is a separate organization; operational coordination does not itself supply clinical signoff or appeals delegation.', 'S01 S02 S03 S04 S06 S07 S12 S13 S14 S17')
module('A04','CM journey owner','case_owner','care_program','M01 M30',
 'An assigned engagement, assessment, care-plan, transition or follow-up obligation is active.',
 'Maintain actual patient responses, goals, assessments, plan contributions, referrals, barriers and observed follow-through.',
 'CM tasks, sourced assessment/plan records and permitted referral/outreach operations.',
 'Cannot infer consent, fabricate answers, alter treatment without assigned scope or mark arranged services delivered.', 'S01 S02 S07 S08 S09 S10 S12 S13 S14 S17')
module('A05','Patient interaction endpoint','external_participant_interface','patient','P01',
 'The assigned task needs an actual supplied patient interaction or response.',
 'Obtain and preserve separately attributed preferences, recollections, symptoms and decisions through the supplied interface.',
 'Observed patient messages and explicit preference/consent events, not internally invented answers.',
 'A harness patient persona cannot replace the supplied patient interface. Self-report is not automatically clinical ground truth.', 'S01 S07 S15 S17')
module('A06','Caregiver and representative endpoints','external_participant_interface','support_person','P02 P03',
 'A caregiver observation or specifically authorized representative contribution is required.',
 'Provide separately attributed support/observations and exercise only recorded representation scope.',
 'Own communications and scoped representative decisions, not arbitrary patient/case facts.',
 'Different people retain separate identities, preferences and appointments; family status is not blanket authority.', 'S01 S07 S15 S17')
module('A07','Treating clinician role templates','staff_role_or_service_interface','provider','C01 C02 C03 C04 C05 O11 M06 M27',
 'A clinical order, evidence author contribution, referral, specialist input or peer exchange is assigned.',
 'Perform the actually assigned clinical-workflow function and maintain source-attributed contributions.',
 'Clinical notes/orders or peer statements only through assigned clinical-service contracts.',
 'One template is not one interchangeable credential. Perform assigned reviews/documents without inventing an examination or supplied result.', 'S01 S02 S07 S17 S19')
module('A08','Diagnostic evidence and consultation interface','specialist_or_adapter','assigned_organization','O13 U05',
 'The case needs an external result, custodian response or bounded independent specialty contribution.',
 'Obtain attributable results or analyze a bounded question from the permitted evidence view.',
 'Source-linked consultation proposal or observed evidence receipt.',
 'A model opinion cannot create a laboratory result or binding determination. Actor author and service observation are distinct.', 'S01 S02 S03 S07 S13 S17 S19')
module('A09','Nursing and direct-care role templates','staff_role_or_service_interface','care_provider','C06 C07 C08 M21',
 'A scoped nursing/support/direct-care activity is assigned or observed.',
 'Represent the specifically assigned care activity and communicate actual observations/events.',
 'Role-scoped observations/tasks; physical completion only from actual environment/service evidence.',
 'RN, LPN/LVN, clinical assistant and aide remain distinct qualifications/functions, not a merged universal scope.', 'S01 S02 S07 S08 S11 S17 S19')
module('A10','Registration and benefits desk','role_mode_or_tool','assigned_organization','O03 O04 U02',
 'Identity, coverage, eligibility or administrative requirements must be established.',
 'Match the correct person/case and retrieve scoped coverage/benefit facts.',
 'Verified administrative records and only explicitly delegated benefit operations.',
 'Provider and payer instances use separate principals. Benefits are not authorization or guaranteed payment.', 'S01 S04 S05 S06 S14 S17')
module('A11','Evidence and documentation auditor','bounded_capability','caller_scope','O06 O08',
 'Missing, conflicting, stale or unauthorized documentation needs inspection.',
 'Assemble provenance, identify gaps/contradictions and recommend clarification.',
 'Read-only findings/proposals by default; no silent repair of substantive clinical facts.',
 'Release purpose, source author and documentation meaning remain separate; requester cannot self-supply missing evidence.', 'S01 S02 S03 S13 S17')
module('A12','Policy and criteria specialist','bounded_capability','caller_scope','G08',
 'Applicable policy/version or criterion-evidence mapping needs analysis.',
 'Return sourced criteria, applicability/exception questions, evidence links and unresolved items.',
 'Version-linked interpretation proposal; controlling policy is immutable to ordinary workers.',
 'Generated policy summaries cannot approve or replace governing rules.', 'S01 S02 S03 S13 S17')
module('A13','Coding support','bounded_capability','provider','O07',
 'A supported code/documentation mapping is required by the assigned workflow.',
 'Suggest coding from authentic source documentation and flag ambiguity.',
 'Coding proposals/queries or scoped administrative edits when assigned.',
 'A code does not create a diagnosis or replace clinician-authored facts.', 'S01 S02 S05 S12 S17')
module('A14','Artifact and handoff writer','bounded_capability','caller_scope','',
 'A task requires a packet, summary, care-plan section or handoff artifact.',
 'Render source-linked documents from approved facts/proposals with explicit unknowns and status.',
 'Draft artifacts; final publication only through the actual case/action authority.',
 'Writing convincing prose is not substantive approval, delivery or independent evidence.', 'S01 S02 S08 S12 S13 S17')
module('A15','Conversation and access support','role_mode_or_capability','caller_scope','P05 P06 M13',
 'Outreach, interview, interpretation, translation or education support is needed.',
 'Track speakers, questions, actual answers, language needs, refusals and unresolved comprehension.',
 'Attributed conversation events and education/communication artifacts.',
 'Translation, interpretation, understanding and consent are different; use actual qualification/task scope.', 'S01 S07 S08 S12 S13 S17')
module('A16','Navigation and transitions desk','role_mode_or_capability','care_program','O02 P04 P07 U16 M09 M10 M11 M18',
 'Referral coordination, access assistance, transition ownership or scoped advocacy is active.',
 'Connect the right recipient, track acceptance/obligations and retain appointment/representation limits.',
 'Referral/navigation tasks, observed replies and scoped filing assistance.',
 'This template combines reusable plumbing, not all advocacy, discharge and clinical decision powers.', 'S01 S05 S07 S08 S09 S10 S12 S17')
module('A17','Medication expertise and access interfaces','bounded_specialist_or_adapter','assigned_organization','M04 M05',
 'A medication evidence, pharmacy review or access/fulfillment question is relevant.',
 'Separate medication expertise, existing instructions, allowed protocol activity and technician/access work.',
 'Scoped recommendations/access tasks; therapy changes only through the assigned order contract.',
 'Inventory or authorization success does not establish a new treatment order or administration.', 'S01 S02 S03 S04 S09 S11 S17 S19')
module('A18','Psychosocial, behavioral and safeguarding interfaces','bounded_specialist_or_adapter','assigned_organization','M02 M03 M07 M08 M31',
 'A psychosocial need, specialist input, restricted material or protection concern is present.',
 'Identify the relevant function, credential/mandate and appropriate information/escalation pathway.',
 'Bounded specialist contribution, resource/protection routing and permitted case records.',
 'Resource support, therapy, prescribing and protection authority are distinct; sensitive evidence views remain scoped.', 'S01 S02 S07 S08 S09 S13 S17')
module('A19','Rehabilitation, nutrition and respiratory interfaces','bounded_specialist_or_adapter','care_provider','M12 M14 M15 M16 M17',
 'The actual case needs discipline-specific assessment/evidence or service coordination.',
 'Produce or obtain specifically attributed discipline contributions from permitted task evidence.',
 'Scoped recommendations/referrals and observed discipline records.',
 'A common interface does not make these professions clinically interchangeable or prove service delivery.', 'S01 S02 S08 S09 S11 S17 S19')
module('A20','Access, receiving services and fulfillment network','external_service_adapter','external_service','O05 O09 M19 M20 M22 M23 M24 M25 M26 G15',
 'Capacity, placement, booking, financial support, transport, equipment or receiving-service status is needed.',
 'Coordinate requests with distinct service organizations and observe acceptance, reservations and fulfillment.',
 'Permitted reservations/requests and attributable status/financial events.',
 'Dispatch is not driving; booking is not attendance; request is not acceptance; authorization is not payment.', 'S01 S07 S09 S10 S11 S12 S15 S17 S20')
module('A21','Initial UM clinical review roles','assigned_review_role','payer','U03 U04 U06 U07',
 'Actual criteria/stage require the assigned qualified review or specialty analysis.',
 'Apply applicable evidence and criteria; recommend/escalate or determine only under the specific assignment.',
 'Stage-scoped review contribution and authorized outcome where the task/profile permits.',
 'Initial review, consultation and reconsideration are distinct; no universal physician-only or unrestricted denial rule is invented.', 'S01 S02 S03 S06 S07 S13 S17')
module('A22','Appeal administration and reconsideration roles','separate_review_role','payer_or_review_body','U12 U13',
 'A proper appeal/reconsideration route is invoked and within scope.',
 'Separate route/standing/file preparation from the required reconsidered decision and independence conditions.',
 'Scoped appeal records and observed/authorized reconsideration contributions.',
 'Independent actor assignment is more than a new prompt; a software simulation does not certify real human legal qualification.', 'S01 S02 S03 S06 S07 S12 S17')
module('A23','External review, regulator and court adapters','external_participant_adapter','external_review_body','U14 U15 U18 G16 J01 J02 J03',
 'The identified product/issue/stage permits an external route.',
 'Represent distinct eligible forums and ingest their attributable supplied outcomes.',
 'Route-specific transmission/status and outcomes only through the corresponding environment service.',
 'A local critic cannot issue a binding IRE/IRO/court result. Routes and later-stage eligibility are not automatic.', 'S01 S06 S07 S12 S15 S17')
module('A24','Determination notice operation','controlled_operation','payer','U09',
 'An actual authorized determination requires a notice/delivery action.',
 'Generate and deliver the corresponding reason/outcome/recipient/version and preserve delivery evidence.',
 'Notice artifacts and observed delivery receipts, not the underlying decision itself.',
 'A draft notice cannot change a decision or be represented as delivered.', 'S01 S06 S12 S14 S17')
module('A25','Quality and workflow analyst','bounded_critic_or_design_capability','permitted_audit_scope','G06 G11 G12',
 'A meaningful checkpoint needs an invariant review, or permitted post-run aggregate analysis is requested.',
 'Inspect source/state consistency, missing obligations and actual process metrics.',
 'Findings/proposals and scoped audit summaries; no automatic world truth or official grade.',
 'An internal critic is not independent reconsideration or the hidden evaluator; aggregate evidence is not a patient fact.', 'S01 S02 S03 S13 S16 S17')
module('A26','Governance and staffing configuration','configuration_or_governance_interface','organization_governance','G01 G02 G03 G04 G05 G07 G09 G17',
 'Work needs approved policy, actual assignment, staffing or governance clarification.',
 'Supply versioned mandates/approval records and distinct institutional governance actors.',
 'Design-time approved configuration or specifically authorized governance records.',
 'Ordinary task workers cannot rewrite policy, appoint themselves to every role or override other organizations.', 'S01 S03 S16 S17')
module('A27','Privacy, identity and infrastructure guard','deterministic_service','runtime_control','G10 G13 G14',
 'Every retrieval, prompt build, delegation and operation crosses a scope/resource boundary.',
 'Enforce principal/purpose/version/tool constraints and retain diagnostic provenance.',
 'Permission/audit decisions, scoped technical state and declared exceptions.',
 'A guard is not legal certification; technical access does not establish clinical authorship or consent.', 'S01 S13 S14 S16 S17')
module('A28','Benchmark adapter and evaluation boundary','boundary_service','runtime_boundary','',
 'A supplied task is admitted, a concrete tool is called or post-run evaluation is inspected.',
 'Map internal work to actual task instructions and tool contracts while isolating official grading from acting inputs.',
 'Adapter/session metadata and observed response receipts; never hidden world or expected-answer state.',
 'The supplied environment owns facts and counterparties. This is an interface boundary, not a second simulator or an acting evaluator.', 'S01 S14 S15 S16 S18 S19')
module('A29','Hospice and spiritual-care pathway','composite_pathway','care_provider','M28 M29',
 'The assigned case actually includes a hospice/palliative/spiritual-support pathway.',
 'Route distinct IDG, RN coordination, attending, certification/admission and requested spiritual-support contributions.',
 'Pathway tasks and specifically attributed role contributions under the applicable task/policy.',
 'A composite profile must not become one all-powerful hospice agent; prior hospice evidence is a dated codification.', 'S01 S02 S07 S08 S09 S17 S19')


SERVICES=[
 ('S01','Identity, representation and scope','Principal, organization, patient/case IDs, purpose, representation, resource permissions.','Authorization checks and scoped identity matches; no role prompt can bypass the gate.'),
 ('S02','Clinical record and evidence','Versioned source notes, orders, observations, diagnostic reports and document provenance.','Reads and attributed writes follow assigned operation scope; agents cannot create unobserved test results.'),
 ('S03','Policy and criteria registry','Product/jurisdiction/setting/version/effective-date rules and approval history.','Ordinary workers read; approved governance controls change versions.'),
 ('S04','Coverage and benefit facts','Enrollment/benefit snapshots, requirements and administrative determinations.','Product-specific administrative scope; not clinical necessity or payment assurance.'),
 ('S05','Provider authorization workspace','Requests, packet versions, submissions, RFIs and provider disputes.','Versioned mutation, stable action identity and observable submission/receipt.'),
 ('S06','Payer review and appeal workspace','Intake/review episodes, qualification/assignment, determination and appeal state.','Actual stage/route and signoff envelope; no universal forced stage sequence.'),
 ('S07','Conversation and correspondence','Patient, representative, clinician and interorganization exchanges.','Preserve speaker, actual observed answer, scope, channel, status and reply correlation.'),
 ('S08','Care journey and obligations','Assessments, goals, plan contributions, outreach and follow-up ownership.','Attributed updates with unknowns, refusal and pending/exception dispositions.'),
 ('S09','Referrals and resource directory','Receiving providers, community supports, service eligibility and acceptance.','Resource listing, referral, acceptance and actual fulfillment remain distinct.'),
 ('S10','Capacity, staffing and scheduling','Beds, slots, shifts, resources, reservations and waitlists.','No double allocation; reservations/expiry follow only exposed authoritative version/time semantics.'),
 ('S11','Service fulfillment and delivery','Visits, transport, supplies, placement, administration and no-shows.','Only environment/service events establish delivery; a plan or actor narration alone cannot.'),
 ('S12','Artifacts, notices and delivery','Draft/final packet, note, plan, handoff, notice and delivery receipt.','Author/source/decision/version link; draft, final and delivered are separate.'),
 ('S13','Scoped memory and retrieval','Per-actor/case working context, episodes, policy/procedure knowledge and indexes.','Scope/trust/provenance filters before injection and delegation; index freshness explicit.'),
 ('S14','Action journal and recovery','Intents, canonical payload hashes, attempts, receipts, unknown outcomes and replay.','Stable intent keys, actual receiver contract, fenced publication and reconciliation.'),
 ('S15','Work events, queues and task clock','Observed task events, internal timers, deadlines and waiting obligations.','Use actual task/environment time where exposed; do not advance a fictional hospital clock.'),
 ('S16','Audit and observability','Permitted action/source/context/usage trace and aggregate operational metrics.','Separate actor-visible diagnostics from hidden oracle/debug data; retention/purpose apply.'),
 ('S17','Actor assignments and authority','People/positions, recorded role/task scope, delegation, scope, ownership and conflicts.','Distinct organization/decision domains; policy-configured independence and actual assignment checks.'),
 ('S18','Benchmark boundary and evaluation output','Supplied task input/tool contracts and separate post-run result receipts.','No acting prompt/tool may query hidden expected answers; official grading remains outside our acting organization.'),
 ('S19','Clinical evidence and diagnostic interfaces','Supplied clinical observations, orders, diagnostic evidence and exposed service results.','No physiology/world engine: accept actual observations and distinguish a new review judgment from an invented test result.'),
 ('S20','Billing, assistance and payment','Estimates, assistance applications, claims, adjudication and observed payment.','Not inferred from authorization; financial outcomes require their own service evidence.')
]


MEMORY_LAYERS=[
 ('M01','Authoritative supplied environment state','Environment services; never replaced by a summary','Supplied domain records under actual write contracts','No global actor read; no direct acting-worker access to hidden truth'),
 ('M02','Case/journey working state','Per organization and patient/task','Goals, observed stage, obligations, unknowns and source/version links','Separate hospital/payer/CM views even when correlated by journey'),
 ('M03','Conversation episodes','Per participant/conversation with scope','Exact observed messages, asked questions, answers, refusal and channel status','Do not merge speakers or assume a silence/translation is consent'),
 ('M04','Reusable job definition and assignment','Approved role definition plus case-local assignment','Mandate, allowed scope, specialty, organization and output contract; no patient-derived profile','Shared job definition does not retain patient memories or acquire authority from its title'),
 ('M05','Policy/reference knowledge','Versioned scoped registry','Approved rules, terminology and source documents','Applicability/effective version checked; summaries remain derived'),
 ('M06','Approved general procedures','Read-only approved shared versions','General methods, prerequisites and tool/version assumptions','No patient-derived automatic learning or procedure/skill promotion across patients'),
 ('M07','Case-local episodic history','Current permitted patient/case/task namespace only','This case’s observations, attempts, outcomes and uncertainty','No cross-patient recall, learned habits, summaries or patient-derived procedural transfer'),
 ('M08','Execution checkpoints/actions','Runtime owner/aggregate','Program position, source/task version, pending actions and unknown receipts','Local checkpoint does not guarantee external exactly-once effects'),
 ('M09','Active model context','One scoped inference request','Protected request, role, relevant evidence, recent coherent exchanges and bounded recall','Budget reserves and complete call/result units; fail explicitly if essentials cannot fit'),
 ('M10','Retrieval and computation caches','Versioned derived scope','Lexical/vector indexes, tool-result caches and provider prompt cache where available','Different invalidation/retention; cache does not create new knowledge or permission')
]
