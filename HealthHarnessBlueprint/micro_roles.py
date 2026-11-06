"""Hypothetical responsibility decomposition, not real professions or launched agents."""
ROLES=[]


def role(id,name,form,inputs,output,decision,boundary,check):
    domain=id.split('-')[0]
    ROLES.append(dict(id=id,domain=domain,name=name,execution_form=form,inputs=inputs,output=output,
        decision_scope=decision,boundary=boundary,completion_check=check,
        memory_policy='PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning',
        status_label='prompt_contract',activation='Only when the current assigned task/stage and actual tool contract require this work.'))


role('PA-01','Request interpreter','bounded_reasoning','Actual task instruction, requested service and observed stage.','A scoped work brief with required outputs and open questions.','Identify what this provider task asks and which obligations are actually present.','Cannot assume every task starts at intake or must traverse every department.','Brief refers to the real task and retains the current user request.')
role('PA-02','Identity and record linker','hybrid','Case/patient identifiers and candidate source records.','Verified links or explicit mismatch/uncertainty.','Link only under the actual identifier evidence; otherwise request clarification.','Similar names are insufficient; cannot merge another patient’s evidence.','Each included record has a matching case/patient reference.')
role('PA-03','Coverage snapshot reader','hybrid','Permitted benefit/enrollment tool response and relevant date.','Attributed coverage facts and freshness limits.','Separate known, unknown and outdated administrative facts.','Benefit verification is not authorization, clinical necessity or payment.','Snapshot retains product/source/date and does not upgrade its meaning.')
role('PA-04','Authorization requirement scout','bounded_reasoning','Requested service, product/setting and actual requirement evidence.','Required/not-required/unknown route with evidence.','Identify the applicable administrative requirement or unresolved requirement.','Cannot invent a PA requirement for all services.','Route cites actual source/response and preserves uncertainty.')
role('PA-05','Policy applicability resolver','bounded_reasoning','Service, setting, product, dates and permitted policy candidates.','Selected applicable policy/version and exclusions/uncertainty.','Resolve applicability before using criteria.','A plausible document title is not proof it governs this case.','Selection records why the source applies or why no selection is justified.')
role('PA-06','Clinical evidence collector','hybrid','Scoped record handles and required evidence categories.','Authentic evidence bundle with authorship and locators.','Find relevant existing evidence and record what could not be obtained.','Cannot create an examination, diagnosis or test result to fill a gap.','Every factual item points to an observed source.')
role('PA-07','Criterion-to-evidence linker','bounded_reasoning','Applicable criteria and source-linked evidence bundle.','Criterion table with supported/not-supported/unknown and exact evidence.','Interpret the relationship between criterion and existing evidence.','Missing evidence is not automatically an explicit negative finding.','Each criterion result preserves source, logic and uncertainty.')
role('PA-08','Gap and contradiction analyst','bounded_reasoning','Criterion table, dates and conflicting records.','Specific unresolved gaps/conflicts and next evidence need.','Identify what blocks a supported packet or which discrepancy needs clarification.','Cannot silently choose the convenient version or rewrite original records.','Each gap/conflict is concrete enough for an appropriate recipient to address.')
role('PA-09','Clinical clarification router','bounded_reasoning','A named gap/conflict and actual clinician/evidence-author interface.','A scoped question and observed response status.','Choose the right question/recipient within the assigned workflow.','Administrative staff cannot answer on behalf of the clinician.','Question, recipient and actual reply/unknown state remain distinct.')
role('PA-10','Coding support role','bounded_reasoning','Authentic documentation and required coding context.','Supported code proposal or query.','Suggest administrative coding supported by supplied documentation.','A code does not independently establish a clinical fact.','Proposal is traceable and ambiguity is retained.')
role('PA-11','Packet composer','bounded_reasoning','Verified identifiers, request, applicable requirements and evidence.','Versioned supported packet/draft.','Organize permitted facts and required artifacts.','A polished packet is not a submission, receipt or approval.','Required fields refer to sources; missing material stays explicit.')
role('PA-12','Packet preflight checker','hybrid','Packet, actual submission contract and known obligations.','Ready/not-ready findings tied to the actual contract.','Check completeness, identity, source consistency and readiness.','Must not invent extra mandatory fields or act as the official hidden verifier.','Findings distinguish genuine contract failures from preferences.')
role('PA-13','Submission operator','tool_operation','Permitted finalized packet, current scope/version and action identity.','Actual submission receipt, failure or unknown outcome.','Execute only the authorized submission operation.','Cannot retry an uncertain external effect as a fresh intention without reconciliation.','Receipt/readback or explicit outcome-unknown is recorded.')
role('PA-14','Response classifier','bounded_reasoning','Actual payer response/correspondence and case state.','Observed response type, affected obligations and open questions.','Classify approval, denial, information request or another supported response.','Cannot create a new payer determination from its own interpretation.','Classification retains the actual response and does not collapse decision/notice/status.')
role('PA-15','Information-request responder','bounded_reasoning','Actual RFI, existing packet/evidence and requested missing items.','Targeted response plan/material and outstanding needs.','Plan the supported response to the specific request.','Cannot fabricate clinical support or answer requests never made.','Each response item addresses a real RFI or records why it is unavailable.')
role('PA-16','Peer/dispute route coordinator','judgment_role','Actual adverse issue, notice, appointment and available challenge routes.','Proper next-route proposal, filing/interaction status and limits.','Separate correction, peer exchange, appeal and external eligibility.','A peer discussion is not automatically a filed appeal or preserved deadline.','Standing, route and actual action evidence remain explicit.')
role('PA-17','Scheduling and access handoff','hybrid','Observed authorization/other disposition, prerequisites and receiving interface.','A supported handoff, booking/access task or unresolved barrier.','Coordinate the next permitted administrative step.','Booked is not clinically cleared/performed; authorization is not payment.','Recipient acknowledgement/status is observed rather than assumed.')
role('PA-18','PA closure and exception reconciler','hybrid','All required PA obligations, receipts and unresolved states.','Evidence-backed final/exception disposition and remaining owner.','Determine whether the assigned work is complete or still pending under its contract.','Cannot declare whole patient care complete because one packet stage ended.','Every closed obligation has its required observed evidence.')

role('UM-01','Intake record resolver','hybrid','Actual request, IDs, attachments and existing payer records.','Matched intake record, missing items and duplicate/uncertain identity flags.','Establish what was received and which case it belongs to.','An intake receipt is not a substantive determination.','Request identity and observed receipt are retained.')
role('UM-02','Product and benefit examiner','hybrid','Actual product/enrollment/benefit observations.','Administrative facts and permitted route implications.','Identify benefit/eligibility outcome within the actual assignment.','No medical-necessity conclusion from administrative mismatch alone.','Administrative and clinical grounds remain separately labeled.')
role('UM-03','Route and delegation interpreter','bounded_reasoning','Task stage, product, assignment and delegated/retained functions.','Applicable route and bounded decision envelope.','Identify permitted nonclinical alternatives, review stages and retained functions.','Cannot assume all nonclinical approvals are forbidden or all denials are allowed.','Route records actual delegation/applicability uncertainty.')
role('UM-04','Governing policy resolver','bounded_reasoning','Product/service/setting/date and approved policy sources.','Applicable source/version and unresolved applicability.','Select the controlling policy evidence for this task.','Generated summaries cannot replace or approve governing policy.','Policy identity/version accompanies later analysis.')
role('UM-05','Criteria logic decomposer','bounded_reasoning','Applicable policy language, exceptions and definitions.','Structured criterion/AND/OR/exception map.','Interpret the rule structure without changing the rule.','Cannot add a more convenient criterion or omit an exception.','The map can be traced back to the source language.')
role('UM-06','Clinical fact extractor','bounded_reasoning','Permitted chart/request evidence.','Attributed relevant facts with unknowns and source locators.','Extract what is actually observed and relevant.','No invented clinical observation or cross-patient retrieval.','Facts remain separable from reviewer interpretation.')
role('UM-07','Chronology and prior-work examiner','bounded_reasoning','Dated records, attempted services and required temporal conditions.','Supported timeline and date/sequence uncertainty.','Check relevant sequence/duration evidence.','Unknown dates cannot become assumed qualifying durations.','Timeline retains source dates and unresolved temporal gaps.')
role('UM-08','Initial criteria matcher','judgment_role','Rule map, facts, timeline and current initial-review scope.','Criteria assessment, rationale and permitted recommendation/action.','Apply the actual initial-review function.','Not an automatically authorized final denial or reconsideration.','Assessment separates met/not-met/unknown with evidence.')
role('UM-09','Ambiguity investigator','bounded_reasoning','Conflicts, uncertain rule terms and missing evidence.','Specific issues, possible interpretations and clarification route.','Identify unresolved interpretation/evidence needs.','Cannot resolve uncertainty by confident assertion or majority vote.','Contradictions and alternatives remain visible to the decision function.')
role('UM-10','Additional-information planner','bounded_reasoning','Actual gaps and permitted requester/provider interface.','Targeted information request and pending-response status.','Select appropriate additional information within the workflow.','Cannot request irrelevant data indefinitely or treat absent reply as an invented fact.','Request has purpose, owner and observed status.')
role('UM-11','Service-specific consultant','bounded_reasoning','A bounded specialty question and scoped case/policy evidence.','Sourced consultation with limits and proposed implications.','Analyze the assigned pharmacy/BH/specialty issue.','Consultation is not automatically the authorized determination.','The result names its source snapshot and unresolved limits.')
role('UM-12','Review assignment and authority checker','hybrid','Actual stage, role assignment, expertise/delegation constraints and prior involvement.','Permitted next decision function or unresolved assignment problem.','Check authority metadata/route; not self-appoint new authority.','A role title or fresh context does not prove required independence.','The acting function matches the actual task/tool assignment.')
role('UM-13','Determination authoring role','judgment_role','Complete applicable review record, current authority and required outcome contract.','Authorized determination/rationale or supported unresolved disposition.','Make the decision actually assigned by the workflow.','Does not derive authority from case-owner seniority or pretend a draft is finalized.','Substantive decision and actual finalization evidence align.')
role('UM-14','Notice content mapper','bounded_reasoning','Actual determination, reason, recipient and applicable notice requirements.','Matching notice draft and delivery obligations.','Render required content from the authoritative decision.','Cannot alter the outcome to improve the letter.','Reason/outcome/version/recipient match the decision record.')
role('UM-15','Notice delivery and readback operator','tool_operation','Permitted notice artifact, recipient/channel and action identity.','Observed delivery receipt/failure/unknown and current state.','Execute the actual notice/delivery operation.','Draft, final, sent and delivered are different states.','Outcome comes from the tool/allowed readback, not narration.')
role('UM-16','Appeal route intake role','hybrid','Actual challenge, issue, representation and product/stage.','Correct appeal/reconsideration/external route and file status.','Establish the actual review route and standing.','A grievance or peer exchange is not every appeal type.','Route and actual accepted/forwarded status are explicit.')
role('UM-17','Reconsideration role','judgment_role','Applicable appeal record, actual assignment and independence requirements.','Permitted reconsidered contribution/outcome with source rationale.','Perform the task-assigned reconsideration function.','Changing the initial worker’s prompt does not prove real institutional independence; do not invent external human steps if the benchmark assigns the function.','Stage, source, assignment and observed outcome remain identifiable.')
role('UM-18','Effectuation and UM closure reconciler','hybrid','Determination/review outcome and actual implementation/notice obligations.','Supported final/exception disposition with pending effects/owners.','Track what the actual outcome requires next.','Favorable review is not automatically implemented authorization, service or payment.','Every terminal claim has its corresponding observed evidence.')

role('CM-01','Chart and task orienter','bounded_reasoning','Actual CM task, permitted chart and current outreach/assessment state.','Case brief, current obligations and source-linked unknowns.','Identify what the current episode requires.','Cannot assume every case needs the same assessments or starts at first contact.','Task brief matches the actual starting stage.')
role('CM-02','Contact and representation checker','hybrid','Actual contact, identity, communication and representative facts.','Permitted participant/channel and unresolved scope.','Check who is speaking and in what capacity.','Family relation or convenient contact is not blanket patient authority.','Participants and representation limits are separately attributed.')
role('CM-03','Outreach planner','bounded_reasoning','Required outreach task, contact options and observed constraints.','Permitted outreach step with unanswered questions.','Choose the next allowed channel/question opportunity.','Cannot invent availability, consent or a required universal contact sequence.','Plan follows actual task/supplied contact constraints.')
role('CM-04','Conversation turn coordinator','dialogue','Actual conversation state, prior questions/answers and pending objective.','Next relevant question or truthful conversation disposition.','Manage dialogue without losing already supplied answers or refusals.','Cannot use an internal patient persona to provide replies.','Each next step follows observed interaction state.')
role('CM-05','Answer and speaker extractor','bounded_reasoning','Actual patient/representative messages and relevant chart references.','Attributed answers, quotations/locators and explicit unknown/refused items.','Extract what each person actually said.','Silence, translated text or caregiver opinion cannot become patient agreement.','Answers preserve speaker, source and uncertainty.')
role('CM-06','Assessment obligation tracker','hybrid','Actual required assessment contract and sourced answers.','Complete/pending/refused/not-applicable field status where supported.','Track required information without manufacturing answers.','A filled form is not valid if values were inferred beyond scope.','Each completed field has the required evidence or permitted derivation.')
role('CM-07','Needs and barriers analyst','bounded_reasoning','Attributed answers, chart facts, goals and actual resource context.','Supported needs/barriers and questions for clarification.','Identify relevant barriers and appropriate role contributions.','A plausible stereotype about another patient cannot inform this patient.','Each proposed need/barrier is grounded in this case.')
role('CM-08','Sensitive issue and scope flagger','bounded_reasoning','Current case facts and applicable safety/privacy/escalation rules.','Scoped concern and permitted next-action recommendation.','Flag when the assigned function lacks evidence/authority.','Cannot invent a diagnosis, reporting mandate or resolved protection outcome.','Flag cites actual case evidence and the relevant unresolved rule.')
role('CM-09','Patient goal elicitation role','dialogue','Actual patient preferences and current plan discussion.','Patient-authored/accepted goals with outstanding disagreement.','Clarify the person’s expressed priorities.','Staff goals or another patient’s preferences cannot substitute.','Goal origin and agreement/unknown status are preserved.')
role('CM-10','Medication context interface','bounded_reasoning','This case’s medication records, instructions and access concerns.','Sourced medication question/referral or permitted contribution.','Separate adherence/access evidence from therapy decisions.','Availability or counselor advice is not a new medication order.','Existing instructions and any proposed clinical change stay distinct.')
role('CM-11','Psychosocial and resource analyst','bounded_reasoning','Case-specific support needs, preferences and actual resource evidence.','Relevant support options with eligibility/availability uncertainty.','Identify appropriate support/referral questions.','A directory listing is not accepted or delivered assistance.','Options retain source, scope and unconfirmed status.')
role('CM-12','Care-task dependency planner','bounded_reasoning','Patient goals, existing instructions, permitted service options and task obligations.','Ordered/parallel next tasks and accountable recipients.','Arrange operational dependencies within actual scope.','Not an independent clinical triage/treatment algorithm or a universal hospital sequence.','Dependencies are justified by actual requirements and current evidence.')
role('CM-13','Care-plan composer','bounded_reasoning','Sourced goals, assessment, authorized clinical contributions and planned tasks.','Versioned care plan with responsibilities and unresolved items.','Assemble the plan actually requested by the task.','A plan is not new prescribing authority or evidence of service execution.','Each section distinguishes evidence, recommendation, owner and status.')
role('CM-14','Referral operator','tool_operation','Permitted referral intent, recipient, case context and action identity.','Actual referral receipt/failure/unknown.','Send the scoped referral through the actual tool.','Referral sent is not accepted, scheduled or completed.','Observed receipt and next owner are recorded.')
role('CM-15','Receiving acknowledgement tracker','hybrid','Actual receiver replies, referral requirements and capacity evidence.','Accepted/rejected/pending state and next obligation.','Track the actual recipient’s decision/status.','Cannot infer acceptance or bed/service availability from a preferred plan.','Status has an actual source and appropriate freshness.')
role('CM-16','Appointment and access coordinator','hybrid','Actual accepted/referral state, available scheduling data and patient constraints.','Permitted booking/support task or unresolved access barrier.','Coordinate an available next step.','Booked transport/visit is not attendance, care delivered or clinical clearance.','Each claimed booking or service status is supported by supplied observations.')
role('CM-17','Transition handoff writer','bounded_reasoning','Current plan, known changes, pending work and receiving participant.','Source-linked transition/handoff artifact.','Communicate uncertainty, responsibility and next actions.','A sent summary does not prove comprehension, accepted responsibility or medical discharge authority.','Named receiver and actual acknowledgement are distinguished from the draft.')
role('CM-18','Follow-up obligation monitor','hybrid','Current case-specific pending tasks, actual deadlines and observed replies.','Due/pending/blocked/completed task status and next owner.','Identify what still needs a supported action.','A reminder sent cannot complete an assessment or service.','Each closure or escalation retains actual evidence.')
role('CM-19','New-information reconciler','bounded_reasoning','New case observations, prior plan/source versions and active obligations.','Changed/unchanged/conflicting facts and affected next tasks.','Re-evaluate this case after new evidence or user steering.','Cannot silently overwrite history or let stale helper results win.','Changes cite sources and preserve prior superseded interpretations.')
role('CM-20','CM closure and exception reconciler','hybrid','Actual requested outcomes, dialogue dispositions, plan/referral/follow-up evidence.','Supported episode completion/exception and remaining responsibilities.','Decide whether the assigned episode has reached its permitted end.','A good conversation or completed plan alone is not all downstream care completed.','Final claims distinguish episode scope from unobserved future care.')

role('SH-01','Task and stage router','hybrid','Actual instruction/tool scope and current observed task stage.','A bounded composite-job assignment.','Choose only task-relevant responsibilities.','Does not force PA→UM→CM or create work not requested.','Assignment refers to actual task evidence.')
role('SH-02','Scoped context builder','deterministic','Role definition, patient/case namespace, current request and permitted evidence.','A version-linked request packet with explicit unknowns.','Select only allowed case-local and approved general content.','No other patient’s history, summaries or learned preferences.','Packet manifest records its namespace/source set.')
role('SH-03','Reference retrieval service','hybrid','Current query, approved sources and case/purpose filters.','Relevant source spans with metadata and limits.','Retrieve rather than invent policy/record evidence.','Search similarity is not truth, authority or patient identity.','Every item passes scope and source checks before injection.')
role('SH-04','Evidence and contradiction ledger','deterministic','Observed evidence IDs, origins, versions and derived interpretations.','Traceable evidence/claim links and unresolved conflicts.','Preserve provenance and version relationships.','A summary cannot silently become authoritative environment state.','Derived claims retain their original source references.')
role('SH-05','Artifact renderer','hybrid','Approved case-local content and actual artifact contract.','Draft/final artifacts with author/source/status metadata.','Render the required representation.','Draft, finalized and delivered remain separate.','Output matches source/version/required contract.')
role('SH-06','Operation gate and action journal','deterministic','Principal, operation, payload, task/version and actual tool contract.','Permitted dispatch and observed receipt/unknown state.','Enforce the actual execution/retry envelope.','Valid model prose or JSON does not grant authority or exactly-once effects.','Action identity and outcome evidence are recorded.')
role('SH-07','Budget and work scheduler','deterministic','Pending case-local work, dependencies and current resource limits.','Bounded execution/delegation plan.','Admit work and account for combined resource spend.','Cannot fan out every micro-role or reuse another patient’s reasoning.','Queue, budget, cancellation and stop conditions are explicit.')
role('SH-08','Case checkpoint and context reducer','hybrid','Current case/request, protected obligations and coherent tool/dialogue history.','Case-scoped checkpoint/projection with retained source references.','Reduce context under the actual provider ownership contract.','Does not promote patient facts into reusable staff knowledge or prove lossless semantics.','Active request, obligations, unknown effects and source versions survive or fail explicitly.')
role('SH-09','Patient isolation barrier','deterministic','Principal, organization, patient/case, source/query/cache namespaces.','Allowed case-local views or a denied/unresolved access.','Prevent patient-derived state crossing into another patient’s work.','Not satisfied by merely asking the model to ignore unrelated context.','Cross-patient source injection is rejected before inference/tool use.')
role('SH-10','Bounded invariant critic','bounded_reasoning','Permitted case facts, intended action/artifact and task-visible requirements.','Specific evidence-based defects or readiness limits.','Challenge unsupported claims and missing obligations.','Not hidden verifier, external reviewer or unlimited debate loop.','Feedback cites the case-visible contradiction/requirement and stays within budget.')


# Approved by delegated review; see ../Progress/ROLE_AUTHORITY.md.
ROLE_CONTRACTS = {'PA-01': {'hospital_roles': ['O01'],
           'authority': "Chooses the provider request's operational scope from instructions and records.",
           'approach': 'Treat authorization as an owned provider workflow whose next step depends on the '
                       'actual request and current stage.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-02': {'hospital_roles': ['O03', 'O06'],
           'authority': 'Decides record linkage from observed identifiers and provenance.',
           'approach': 'Resolve identity discrepancies before using records and retain ambiguity rather than '
                       'selecting the most convenient match.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-03': {'hospital_roles': ['O04'],
           'authority': 'Represents coverage facts with their source and effective date.',
           'approach': 'Help the requester understand the administrative facts while keeping coverage '
                       'verification distinct from authorization and payment.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-04': {'hospital_roles': ['O01', 'O04'],
           'authority': 'Decides which authorization requirement applies to the documented service and '
                        'product.',
           'approach': 'Seek the applicable requirement before preparing unnecessary authorization work and '
                       'make unresolved applicability visible.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-05': {'hospital_roles': ['O01', 'G08'],
           'authority': 'Selects the applicable policy version from service context and source '
                        'applicability.',
           'approach': 'Read policy as a governing source with conditions and exceptions rather than as a '
                       'plausible title or convenient summary.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-06': {'hospital_roles': ['O06', 'O08'],
           'authority': 'Curates authentic, relevant evidence from observed records under permitted '
                        'disclosure.',
           'approach': 'Build the request from existing authored evidence and make missing documentation '
                       'visible to the responsible source.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-07': {'hospital_roles': ['O01', 'O08'],
           'authority': 'Interprets provider-side criterion support from applicable criteria and '
                        'documentation.',
           'approach': 'Make the relationship between a requirement and its evidence traceable while '
                       'treating missing evidence as an open question.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-08': {'hospital_roles': ['O08', 'O01'],
           'authority': 'Identifies material documentation gaps from conflicting sources and packet '
                        'requirements.',
           'approach': 'Clarify discrepancies with their authors instead of silently repairing the record to '
                       'make the request fit.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-09': {'hospital_roles': ['O01', 'O08', 'O11'],
           'authority': 'Chooses clarification routes and represents documented provider positions, with new '
                        'clinical opinions under separately assigned professional authority.',
           'approach': 'Ask a precise question of the appropriate source and distinguish an attributed '
                       "clinical answer from the coordinator's interpretation.",
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Choose the clarification question and recipient under provider procedure; '
                             'represent documented provider facts, with any new clinical opinion restricted '
                             'to separately assigned professional authority.'},
 'PA-10': {'hospital_roles': ['O07'],
           'authority': 'Recommends administrative coding supported by documentation and coding guidance.',
           'approach': 'Represent documented services accurately and seek clarification where a code would '
                       'imply more than the record supports.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-11': {'hospital_roles': ['O01', 'O06'],
           'authority': "Shapes the provider packet's supported content and organization from sources and "
                        'submission requirements.',
           'approach': 'Make the request easy to review without upgrading a draft or a persuasive '
                       'explanation into proof of submission or approval.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-12': {'hospital_roles': ['O01', 'O08'],
           'authority': 'Decides packet readiness against actual requirements and source consistency.',
           'approach': 'Check what the recipient actually requires and return specific correctable defects '
                       'instead of inventing new hurdles.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-13': {'hospital_roles': ['O01'],
           'authority': 'Carries the assigned submission through available tools and represents its observed '
                        'outcome.',
           'approach': 'Carry the supported request through the permitted submission interface and reconcile '
                       'an uncertain effect before retrying.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-14': {'hospital_roles': ['O01', 'O10'],
           'authority': "Interprets payer responses and chooses the provider's operational next step under "
                        'procedure.',
           'approach': 'Read the actual response for its consequences and preserve the difference between '
                       "the payer's determination and a provider interpretation.",
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Classify the actual payer response and choose the supported provider '
                             'operational next step under applicable procedure; preserve the authoritative '
                             'response and outstanding deadlines.'},
 'PA-15': {'hospital_roles': ['O01', 'O08', 'O11'],
           'authority': "Speaks for the provider's supported response to an actual information request, "
                        'preserving records and authorship.',
           'approach': 'Answer the question the payer actually asked and obtain clinical clarification from '
                       'the appropriate source where existing records do not answer it.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Choose and represent the supported provider response to the actual request '
                             'under applicable procedure; obtain new clinical clarification from its '
                             'authorized source where required.'},
 'PA-16': {'hospital_roles': ['O10', 'O11'],
           'authority': 'Chooses the dispute route under established standing, with peer clinical '
                        'representation under assigned professional authority.',
           'approach': 'Treat correction and peer exchange and appeal as distinct procedures with their own '
                       'deadlines and evidence rather than interchangeable chances to obtain approval.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Select the supported correction, peer exchange or dispute route under '
                             'established standing and procedure; clinical representation requires assigned '
                             'professional authority and external outcomes require actual observations.'},
 'PA-17': {'hospital_roles': ['O02', 'O05', 'O09'],
           'authority': 'Coordinates the assigned access handoff from observed disposition and service '
                        'availability.',
           'approach': 'Connect the request to a feasible next administrative step and keep access barriers '
                       'visible to the next responsible participant.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'PA-18': {'hospital_roles': ['O01', 'O10'],
           'authority': "Declares the provider assignment's supported endpoint from observed effects and "
                        'remaining obligations.',
           'approach': 'Close the assigned work honestly while retaining unresolved responses and downstream '
                       'responsibilities.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-01': {'hospital_roles': ['U01'],
           'authority': 'Shapes the reviewable intake record from received material and verified case '
                        'linkage.',
           'approach': 'Give the reviewing function a faithful account of what arrived and what remains '
                       'missing without implying a substantive decision.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-02': {'hospital_roles': ['U02'],
           'authority': 'Decides the assigned administrative benefit question from plan records under '
                        'documented delegation.',
           'approach': 'Apply membership and benefit rules to their administrative question and route '
                       'clinical issues to the appropriate review function.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-03': {'hospital_roles': ['U01', 'U08', 'U17'],
           'authority': 'Chooses the permitted review route under program procedure and documented '
                        'delegation.',
           'approach': 'Choose a supported operational lane while keeping retained functions and '
                       'professional decision authority explicit.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-04': {'hospital_roles': ['G08', 'U03', 'U04'],
           'authority': 'Selects the controlling review policy from product context and source '
                        'applicability.',
           'approach': 'Establish which policy governs before judging the evidence and preserve unresolved '
                       'version or applicability questions.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-05': {'hospital_roles': ['U03', 'U04'],
           'authority': 'Interprets governing criteria with their alternatives and exceptions.',
           'approach': 'Apply the rule as written and expose its alternatives rather than simplify away a '
                       'material exception.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-06': {'hospital_roles': ['U03', 'U04'],
           'authority': 'Establishes attributed clinical facts for review from observed records.',
           'approach': 'Read the submitted evidence carefully and keep authored findings distinct from '
                       'reviewer inference.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-07': {'hospital_roles': ['U03', 'U04'],
           'authority': 'Establishes the relevant chronology from dated records and documented prior work.',
           'approach': 'Test duration and sequence against actual evidence and retain unknown dates as '
                       'unknown.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-08': {'hospital_roles': ['U03', 'U06', 'U07'],
           'authority': 'Approves under documented delegation when criteria and program permit, otherwise '
                        'recommends or escalates the initial clinical review.',
           'approach': 'Apply governing criteria to the evidence and resolve the assigned review through a '
                       'supported decision or an explicit route to the responsible decision-maker.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Apply governing criteria to observed evidence; approve only under documented '
                             'delegation when criteria and program permit, otherwise recommend or escalate '
                             'within the assigned initial-review function.'},
 'UM-09': {'hospital_roles': ['U03', 'U04', 'U05'],
           'authority': 'Identifies material review uncertainty from conflicting evidence or unclear policy '
                        'applicability.',
           'approach': 'Investigate what could change the review conclusion and explain the consequence of '
                       'each unresolved question.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-10': {'hospital_roles': ['U01', 'U03'],
           'authority': 'Chooses focused additional-information requirements from review gaps under '
                        'permitted procedure.',
           'approach': 'Ask focused questions that enable the assigned review and track the response without '
                       'turning missing information into an endless delay.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-11': {'hospital_roles': ['U05', 'U06', 'U07'],
           'authority': 'Contributes the assigned specialty opinion within professional scope, with decision '
                        'authority under separate assignment.',
           'approach': 'Contribute focused expertise with its rationale and limitations rather than imply '
                       'that consultation itself settles the case.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-12': {'hospital_roles': ['U08', 'U17'],
           'authority': "Establishes the review assignment's authority from documented delegation and "
                        'independence requirements.',
           'approach': 'Verify the actual function and retained authority instead of inferring permission '
                       'from seniority or a role title.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-13': {'hospital_roles': ['U04', 'U03'],
           'authority': 'Issues the clinical coverage determination under assigned documented delegation, '
                        'otherwise recommends it from governing criteria and observed evidence.',
           'approach': 'Reach the supported assigned decision and explain its rationale while preserving '
                       'recommendation and final determination as distinct records.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Issue or recommend the clinical coverage determination actually assigned under '
                             'documented authority and governing criteria; preserve the difference between '
                             'recommendation, recorded decision and finalized determination.'},
 'UM-14': {'hospital_roles': ['U09', 'U10', 'U11'],
           'authority': 'Speaks for the recorded determination and applicable procedural rights under notice '
                        'policy.',
           'approach': 'Explain the outcome plainly to the intended recipient and resolve missing rationale '
                       'without rewriting the decision.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Represent the authoritative determination and applicable procedural '
                             'information under notice policy; resolve missing rationale through the '
                             'responsible decision source rather than changing the outcome.'},
 'UM-15': {'hospital_roles': ['U09'],
           'authority': 'Carries the assigned notice through available tools and represents observed '
                        'delivery state.',
           'approach': 'Carry the authorized communication through its required channel and track failures '
                       'or uncertain receipt explicitly.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-16': {'hospital_roles': ['U12'],
           'authority': 'Selects the applicable challenge route and standing from the request and governing '
                        'procedure.',
           'approach': 'Distinguish appeal from grievance and peer exchange before routing the record and '
                       'any missing material.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'UM-17': {'hospital_roles': ['U13'],
           'authority': 'Affirms or reverses the disputed decision under assigned reconsideration authority '
                        'and applicable independence requirements.',
           'approach': 'Reconsider the disputed record and new evidence on their merits while checking that '
                       'the required review separation actually exists.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Affirm or reverse within assigned reconsideration authority using the disputed '
                             'record and governing criteria; verify applicable review separation rather than '
                             'infer independence from a changed prompt.'},
 'UM-18': {'hospital_roles': ['U01', 'U09', 'U17'],
           'authority': 'Declares the assigned review endpoint and remaining effectuation duties from the '
                        'recorded outcome and observed implementation.',
           'approach': 'Track what the decision requires next and close only the work whose effects are '
                       'actually supported.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-01': {'hospital_roles': ['M01', 'M30'],
           'authority': 'Chooses coordination priorities from referral context and observed chart '
                        'information.',
           'approach': "Treat the referral as a starting point for understanding this member's needs and the "
                       "program's responsibilities rather than a fixed form sequence.",
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Interpret the referral and current episode using observed chart context and '
                             'applicable care-management intake policy; identify coordination priorities and '
                             'unresolved needs.'},
 'CM-02': {'hospital_roles': ['M01', 'P03', 'P05'],
           'authority': 'Establishes contact and representation scope from observed identity and authority '
                        'records.',
           'approach': 'Make communication accessible and verify who is speaking for whom without '
                       "substituting a representative's wishes for the member's.",
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-03': {'hospital_roles': ['M01', 'M09', 'M13'],
           'authority': 'Chooses the outreach plan under care-management outreach and enrollment policy and '
                        'observed contact permissions.',
           'approach': 'Prepare an accessible conversation that explains the program and explores priorities '
                       'while preserving consent conditions and policy-specific exit duties.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Plan outreach from applicable care-management outreach and enrollment policy, '
                             'observed contact permissions and current member questions; retain required '
                             'information and exit/handoff duties.'},
 'CM-04': {'hospital_roles': ['M01', 'M09', 'M13'],
           'authority': "Speaks for the program to the member: may state the program's purpose, services, "
                        "cost and participation terms as the retrieved policy states them, once the policy's "
                        "conditions are checked against the member's records; may explain what care planning "
                        'could include, ask for enrollment consent, and conduct the permitted interview '
                        'after consent. It speaks as the member\'s health plan: the member\'s observed active '
                        'coverage with the plan operating the program is the plan information that participation '
                        'statements rely on.',
           'approach': 'Find what matters to the member and connect it to program services. Answer plainly '
                       'from policy, invite an informed decision and respect decline without pressure or '
                       'promised dates or outcomes.',
           'status_label': 'executing_worker',
           'model_visible': True,
           'name': 'Member-engagement lead',
           'decision_scope': 'Represent the program accurately under retrieved policy and observed '
                             'eligibility conditions; learn member priorities, connect them to supported '
                             'services and answer questions plainly. Invite an informed decision, respect '
                             'decline and conduct a permitted interview only after actual consent.',
           'output': 'Source-linked engagement handoff with consent status, member priorities and open '
                     'questions; accurate program information and permitted post-consent interview findings.',
           'completion_check': 'Once questions are answered, the member was asked directly whether to enroll '
                               'before any offer to end contact; an informed decision is observed or the member '
                               'ended contact. Consent status, priorities and open questions are preserved.'},
 'CM-05': {'hospital_roles': ['M01', 'P05'],
           'authority': 'Represents dialogue findings faithfully from the actual transcript.',
           'approach': "Listen for the person's meaning and preserve uncertainty or refusal instead of "
                       'filling a convenient answer into the record.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-06': {'hospital_roles': ['M01', 'C06'],
           'authority': 'Establishes assessment completeness from required fields and sourced answers under '
                        'actual consent.',
           'approach': 'Make each assessment entry defensible and identify a missing answer without turning '
                       'a completed form into a substitute for performed assessment.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-07': {'hospital_roles': ['M01', 'M02', 'M09'],
           'authority': "Identifies coordination needs and barriers from the member's account and observed "
                        'records.',
           'approach': "Understand how practical circumstances affect the member's goals and seek "
                       'clarification rather than rely on assumptions about a population.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-08': {'hospital_roles': ['M01', 'M31', 'G10'],
           'authority': 'Identifies safety or scope concerns under applicable escalation and privacy rules.',
           'approach': 'Treat sensitive concerns respectfully and route issues to the responsible function '
                       'without inventing a diagnosis or protection outcome.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-09': {'hospital_roles': ['M01', 'M13'],
           'authority': "Represents the member's goals from their expressed priorities and agreement.",
           'approach': 'Elicit what useful help would mean to the member during permitted outreach and '
                       'revisit proposed goals as understanding changes without assessing before consent.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': "Elicit the member's own priorities during permitted outreach and clarify goals "
                             'for care planning under the applicable consent conditions; preserve '
                             'acceptance, disagreement and unknown status.'},
 'CM-10': {'hospital_roles': ['M01', 'M04', 'M05'],
           'authority': 'Owns the medication coordination question from existing instructions and observed '
                        'access concerns.',
           'approach': 'Help resolve medication-use or access barriers through the appropriate professional '
                       "contribution while preserving the prescriber's treatment authority.",
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-11': {'hospital_roles': ['M01', 'M02', 'M09'],
           'authority': 'Proposes care-plan interventions for psychosocial and resource needs from observed '
                        'barriers and supported options.',
           'approach': 'Turn relevant support options into practical proposed interventions linked to the '
                       "member's goals while preserving eligibility and availability uncertainty.",
           'status_label': 'prompt_contract',
           'model_visible': True,
           'output': 'Proposed care-plan interventions linked to member goals and support needs, with '
                     'responsible recipients and eligibility/availability uncertainty.',
           'decision_scope': 'Translate supported psychosocial and resource options into proposed care-plan '
                             'interventions within assigned scope.'},
 'CM-12': {'hospital_roles': ['M01', 'M30', 'M18'],
           'authority': 'Chooses care-task sequence and ownership from supported dependencies and member '
                        'goals.',
           'approach': "Organize feasible coordination work around the member's needs and make the next "
                       'responsibility clear without imposing a universal clinical pathway.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-13': {'hospital_roles': ['M01', 'M18'],
           'authority': 'Shapes a coherent care plan from observed assessment, member goals and applicable '
                        'care-plan standards.',
           'approach': 'Connect problems and goals to interventions, escalation conditions and follow-up '
                       'cadence. Preserve ownership, uncertainty and the distinction between planned and '
                       'performed work.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'output': 'Versioned care plan connecting supported problems, member goals and interventions with '
                     'escalation conditions, follow-up cadence, responsibilities and unresolved items.',
           'decision_scope': 'Compose the requested plan using applicable care-plan standards; distinguish '
                             'sourced problems and goals from proposed interventions and their execution '
                             'status.'},
 'CM-14': {'hospital_roles': ['M01', 'O02', 'M10'],
           'authority': 'Coordinates the consented referral through available tools, or places its proposed '
                        'intervention in the care plan when execution tools are absent.',
           'approach': 'Pursue the supported referral connection where it can actually be performed and '
                       'otherwise specify the proposed intervention and responsible recipient in the plan.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Coordinate a permitted referral through an actual available tool; when no '
                             'execution tool exists, include the proposed referral intervention and '
                             'responsible recipient in the care plan.',
           'output': 'Actual referral receipt/failure/unknown where performed, otherwise a clearly planned '
                     'care-plan referral intervention.',
           'completion_check': 'Record observed receipt and next owner if executed; otherwise record the '
                               'planned intervention, execution limit and responsible recipient without '
                               'claiming a sent referral.'},
 'CM-15': {'hospital_roles': ['M01', 'M19', 'M20', 'M26'],
           'authority': 'Represents actual receiver acceptance, or plans acknowledgement follow-up in the '
                        'care plan when receiving-status tools are absent.',
           'approach': 'Follow the connection to its real receiving status and retain a proposed '
                       'acknowledgement check when the environment cannot obtain one.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': "Track the recipient's actual acceptance or status when observable; when no "
                             'receiving-status tool exists, plan the acknowledgement follow-up intervention '
                             'in the care plan.',
           'output': 'Sourced receiver status and next obligation, or a clearly planned acknowledgement '
                     'follow-up intervention.',
           'completion_check': 'Each claimed receiving status has a fresh actual source; an unexecuted '
                               'acknowledgement check remains a planned intervention with an owner.'},
 'CM-16': {'hospital_roles': ['M01', 'O05', 'M23'],
           'authority': 'Coordinates access from member constraints and observed availability, or plans the '
                        'intervention in the care plan when execution tools are absent.',
           'approach': 'Help make access feasible through available arrangements and otherwise describe the '
                       'proposed access work and its owner in the care plan.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Coordinate an available permitted access step; when no execution tool exists, '
                             'plan the access intervention and responsible recipient in the care plan.',
           'output': 'Observed booking/support status where performed, otherwise a planned care-plan access '
                     'intervention with unresolved barriers.',
           'completion_check': 'Claimed bookings have supplied observations; unavailable execution is '
                               'represented as planned coordination with an owner and outstanding barriers.'},
 'CM-17': {'hospital_roles': ['M01', 'M18'],
           'authority': 'Shapes supported handoff content from the current plan and unresolved '
                        'responsibilities.',
           'approach': 'Give the receiving participant a clear account of what changed and what remains to '
                       'be done while tracking acknowledgement separately from a draft.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-18': {'hospital_roles': ['M01', 'M30'],
           'authority': 'Establishes follow-up obligation status from actual deadlines and observed replies.',
           'approach': 'Track whether the intended connection occurred and keep the next responsible '
                       'participant aware of unresolved work.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-19': {'hospital_roles': ['M01'],
           'authority': 'Revises the case interpretation from new evidence and current member priorities.',
           'approach': 'Update coordination work when circumstances change while preserving the history and '
                       'why an earlier interpretation was superseded.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'CM-20': {'hospital_roles': ['M01', 'M30'],
           'authority': 'Chooses the episode closure or decline path from observed participation under '
                        'care-management closure policy.',
           'approach': 'Respect a decline or ended contact and complete the remaining permitted '
                       'documentation and return-path duties under retrieved policy while preserving any '
                       'unmet assigned goal.',
           'status_label': 'prompt_contract',
           'model_visible': True,
           'decision_scope': 'Choose the episode completion, decline or exception path under retrieved '
                             'care-management closure policy and observed participation; distinguish an '
                             'ended contact from consent or refusal.',
           'output': 'Source-supported episode disposition with remaining permitted '
                     'documentation/communication duties, return-path information where required and unmet '
                     'goals.',
           'completion_check': 'Disposition follows the retrieved policy and observed participation; '
                               'remaining duties and unmet assigned outcomes remain explicit without '
                               'claiming downstream care.'},
 'SH-01': {'hospital_roles': [],
           'authority': 'Selects relevant responsibilities from the actual instruction and observed stage.',
           'approach': 'Keep the requested work central and route only the responsibilities it actually '
                       'needs.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'SH-02': {'hospital_roles': [],
           'authority': 'Selects permitted context under case namespaces and source permissions.',
           'approach': 'Give each function the evidence it needs with explicit unknowns and traceable source '
                       'versions.',
           'status_label': 'prompt_contract',
           'model_visible': False},
 'SH-03': {'hospital_roles': [],
           'authority': 'Retrieves relevant evidence from approved sources and scoped queries.',
           'approach': 'Return relevant evidence with its provenance and limitations while leaving policy '
                       'interpretation to the assigned function.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'SH-04': {'hospital_roles': [],
           'authority': 'Preserves claim provenance and source version relationships.',
           'approach': 'Keep original evidence distinguishable from summaries and retain contradictions for '
                       'explicit resolution.',
           'status_label': 'prompt_contract',
           'model_visible': False},
 'SH-05': {'hospital_roles': [],
           'authority': 'Renders faithful artifacts from approved content under the output contract.',
           'approach': 'Make a clear usable artifact whose draft or final status remains visible and whose '
                       'claims remain source-linked.',
           'status_label': 'prompt_contract',
           'model_visible': True},
 'SH-06': {'hospital_roles': [],
           'authority': 'Enforces the execution envelope under tool contracts and journaled outcomes.',
           'approach': 'Treat external effects as events requiring identity and reconciliation rather than '
                       'as implications of plausible model text.',
           'status_label': 'prompt_contract',
           'model_visible': False},
 'SH-07': {'hospital_roles': [],
           'authority': 'Admits work within current budgets and dependencies.',
           'approach': 'Spend bounded resources on task-relevant work and keep cancellation and stopping '
                       'conditions explicit.',
           'status_label': 'prompt_contract',
           'model_visible': False},
 'SH-08': {'hospital_roles': [],
           'authority': 'Preserves checkpoint obligations under the provider context contract.',
           'approach': 'Reduce context carefully while preserving the active request and unresolved effects '
                       'and access to original sources.',
           'status_label': 'prompt_contract',
           'model_visible': False},
 'SH-09': {'hospital_roles': [],
           'authority': 'Denies cross-case source access under principal and patient namespaces.',
           'approach': 'Enforce isolation before content reaches reasoning or tools rather than relying on a '
                       'request to ignore unrelated material.',
           'status_label': 'prompt_contract',
           'model_visible': False},
 'SH-10': {'hospital_roles': [],
           'authority': 'Challenges unsupported readiness and stop claims against task-visible requirements '
                        'and observed effects.',
           'approach': 'Review both overclaiming and remaining useful permitted work with specific '
                       'source-backed objections while leaving the owner responsible for the next decision.',
           'status_label': 'executing_worker',
           'model_visible': True}}

for _role in ROLES:
    _role.update(ROLE_CONTRACTS[_role["id"]])
