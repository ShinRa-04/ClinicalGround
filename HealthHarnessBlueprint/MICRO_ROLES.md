# Micro-role responsibility contracts

These 66 proposed responsibilities may or may not correspond to separate real-world people. They compose PA/UM/CM jobs and shared support. A responsibility can be ordinary code, a tool operation, in-context reasoning, a bounded call or a worker; the recommended form below is a starting hypothesis. No role is required on a case unless its output is actually needed.

[Composition model](COMPOSITION.md) · [Patient isolation](PATIENT_ISOLATION.md) · [Workflows](WORKFLOWS.md)

# PA responsibilities

<a id="pa-01"></a>
## PA-01 — Request interpreter

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual task instruction, requested service and observed stage.

**Output:** A scoped work brief with required outputs and open questions.

**Decision scope:** Identify what this provider task asks and which obligations are actually present.

**Must not assume/do:** Cannot assume every task starts at intake or must traverse every department.

**Authority:** Chooses the provider request's operational scope from instructions and records.

**Approach:** Treat authorization as an owned provider workflow whose next step depends on the actual request and current stage.

**Hospital roles:** O01

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Brief refers to the real task and retains the current user request.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-02"></a>
## PA-02 — Identity and record linker

**Candidate execution form:** hybrid

**Inputs:** Case/patient identifiers and candidate source records.

**Output:** Verified links or explicit mismatch/uncertainty.

**Decision scope:** Link only under the actual identifier evidence; otherwise request clarification.

**Must not assume/do:** Similar names are insufficient; cannot merge another patient’s evidence.

**Authority:** Decides record linkage from observed identifiers and provenance.

**Approach:** Resolve identity discrepancies before using records and retain ambiguity rather than selecting the most convenient match.

**Hospital roles:** O03, O06

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each included record has a matching case/patient reference.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-03"></a>
## PA-03 — Coverage snapshot reader

**Candidate execution form:** hybrid

**Inputs:** Permitted benefit/enrollment tool response and relevant date.

**Output:** Attributed coverage facts and freshness limits.

**Decision scope:** Separate known, unknown and outdated administrative facts.

**Must not assume/do:** Benefit verification is not authorization, clinical necessity or payment.

**Authority:** Represents coverage facts with their source and effective date.

**Approach:** Help the requester understand the administrative facts while keeping coverage verification distinct from authorization and payment.

**Hospital roles:** O04

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Snapshot retains product/source/date and does not upgrade its meaning.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-04"></a>
## PA-04 — Authorization requirement scout

**Candidate execution form:** bounded_reasoning

**Inputs:** Requested service, product/setting and actual requirement evidence.

**Output:** Required/not-required/unknown route with evidence.

**Decision scope:** Identify the applicable administrative requirement or unresolved requirement.

**Must not assume/do:** Cannot invent a PA requirement for all services.

**Authority:** Decides which authorization requirement applies to the documented service and product.

**Approach:** Seek the applicable requirement before preparing unnecessary authorization work and make unresolved applicability visible.

**Hospital roles:** O01, O04

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Route cites actual source/response and preserves uncertainty.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-05"></a>
## PA-05 — Policy applicability resolver

**Candidate execution form:** bounded_reasoning

**Inputs:** Service, setting, product, dates and permitted policy candidates.

**Output:** Selected applicable policy/version and exclusions/uncertainty.

**Decision scope:** Resolve applicability before using criteria.

**Must not assume/do:** A plausible document title is not proof it governs this case.

**Authority:** Selects the applicable policy version from service context and source applicability.

**Approach:** Read policy as a governing source with conditions and exceptions rather than as a plausible title or convenient summary.

**Hospital roles:** O01, G08

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Selection records why the source applies or why no selection is justified.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-06"></a>
## PA-06 — Clinical evidence collector

**Candidate execution form:** hybrid

**Inputs:** Scoped record handles and required evidence categories.

**Output:** Authentic evidence bundle with authorship and locators.

**Decision scope:** Find relevant existing evidence and record what could not be obtained.

**Must not assume/do:** Cannot create an examination, diagnosis or test result to fill a gap.

**Authority:** Curates authentic, relevant evidence from observed records under permitted disclosure.

**Approach:** Build the request from existing authored evidence and make missing documentation visible to the responsible source.

**Hospital roles:** O06, O08

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Every factual item points to an observed source.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-07"></a>
## PA-07 — Criterion-to-evidence linker

**Candidate execution form:** bounded_reasoning

**Inputs:** Applicable criteria and source-linked evidence bundle.

**Output:** Criterion table with supported/not-supported/unknown and exact evidence.

**Decision scope:** Interpret the relationship between criterion and existing evidence.

**Must not assume/do:** Missing evidence is not automatically an explicit negative finding.

**Authority:** Interprets provider-side criterion support from applicable criteria and documentation.

**Approach:** Make the relationship between a requirement and its evidence traceable while treating missing evidence as an open question.

**Hospital roles:** O01, O08

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each criterion result preserves source, logic and uncertainty.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-08"></a>
## PA-08 — Gap and contradiction analyst

**Candidate execution form:** bounded_reasoning

**Inputs:** Criterion table, dates and conflicting records.

**Output:** Specific unresolved gaps/conflicts and next evidence need.

**Decision scope:** Identify what blocks a supported packet or which discrepancy needs clarification.

**Must not assume/do:** Cannot silently choose the convenient version or rewrite original records.

**Authority:** Identifies material documentation gaps from conflicting sources and packet requirements.

**Approach:** Clarify discrepancies with their authors instead of silently repairing the record to make the request fit.

**Hospital roles:** O08, O01

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each gap/conflict is concrete enough for an appropriate recipient to address.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-09"></a>
## PA-09 — Clinical clarification router

**Candidate execution form:** bounded_reasoning

**Inputs:** A named gap/conflict and actual clinician/evidence-author interface.

**Output:** A scoped question and observed response status.

**Decision scope:** Choose the clarification question and recipient under provider procedure; represent documented provider facts, with any new clinical opinion restricted to separately assigned professional authority.

**Must not assume/do:** Administrative staff cannot answer on behalf of the clinician.

**Authority:** Chooses clarification routes and represents documented provider positions, with new clinical opinions under separately assigned professional authority.

**Approach:** Ask a precise question of the appropriate source and distinguish an attributed clinical answer from the coordinator's interpretation.

**Hospital roles:** O01, O08, O11

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Question, recipient and actual reply/unknown state remain distinct.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-10"></a>
## PA-10 — Coding support role

**Candidate execution form:** bounded_reasoning

**Inputs:** Authentic documentation and required coding context.

**Output:** Supported code proposal or query.

**Decision scope:** Suggest administrative coding supported by supplied documentation.

**Must not assume/do:** A code does not independently establish a clinical fact.

**Authority:** Recommends administrative coding supported by documentation and coding guidance.

**Approach:** Represent documented services accurately and seek clarification where a code would imply more than the record supports.

**Hospital roles:** O07

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Proposal is traceable and ambiguity is retained.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-11"></a>
## PA-11 — Packet composer

**Candidate execution form:** bounded_reasoning

**Inputs:** Verified identifiers, request, applicable requirements and evidence.

**Output:** Versioned supported packet/draft.

**Decision scope:** Organize permitted facts and required artifacts.

**Must not assume/do:** A polished packet is not a submission, receipt or approval.

**Authority:** Shapes the provider packet's supported content and organization from sources and submission requirements.

**Approach:** Make the request easy to review without upgrading a draft or a persuasive explanation into proof of submission or approval.

**Hospital roles:** O01, O06

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Required fields refer to sources; missing material stays explicit.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-12"></a>
## PA-12 — Packet preflight checker

**Candidate execution form:** hybrid

**Inputs:** Packet, actual submission contract and known obligations.

**Output:** Ready/not-ready findings tied to the actual contract.

**Decision scope:** Check completeness, identity, source consistency and readiness.

**Must not assume/do:** Must not invent extra mandatory fields or act as the official hidden verifier.

**Authority:** Decides packet readiness against actual requirements and source consistency.

**Approach:** Check what the recipient actually requires and return specific correctable defects instead of inventing new hurdles.

**Hospital roles:** O01, O08

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Findings distinguish genuine contract failures from preferences.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-13"></a>
## PA-13 — Submission operator

**Candidate execution form:** tool_operation

**Inputs:** Permitted finalized packet, current scope/version and action identity.

**Output:** Actual submission receipt, failure or unknown outcome.

**Decision scope:** Execute only the authorized submission operation.

**Must not assume/do:** Cannot retry an uncertain external effect as a fresh intention without reconciliation.

**Authority:** Carries the assigned submission through available tools and represents its observed outcome.

**Approach:** Carry the supported request through the permitted submission interface and reconcile an uncertain effect before retrying.

**Hospital roles:** O01

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Receipt/readback or explicit outcome-unknown is recorded.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-14"></a>
## PA-14 — Response classifier

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual payer response/correspondence and case state.

**Output:** Observed response type, affected obligations and open questions.

**Decision scope:** Classify the actual payer response and choose the supported provider operational next step under applicable procedure; preserve the authoritative response and outstanding deadlines.

**Must not assume/do:** Cannot create a new payer determination from its own interpretation.

**Authority:** Interprets payer responses and chooses the provider's operational next step under procedure.

**Approach:** Read the actual response for its consequences and preserve the difference between the payer's determination and a provider interpretation.

**Hospital roles:** O01, O10

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Classification retains the actual response and does not collapse decision/notice/status.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-15"></a>
## PA-15 — Information-request responder

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual RFI, existing packet/evidence and requested missing items.

**Output:** Targeted response plan/material and outstanding needs.

**Decision scope:** Choose and represent the supported provider response to the actual request under applicable procedure; obtain new clinical clarification from its authorized source where required.

**Must not assume/do:** Cannot fabricate clinical support or answer requests never made.

**Authority:** Speaks for the provider's supported response to an actual information request, preserving records and authorship.

**Approach:** Answer the question the payer actually asked and obtain clinical clarification from the appropriate source where existing records do not answer it.

**Hospital roles:** O01, O08, O11

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each response item addresses a real RFI or records why it is unavailable.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-16"></a>
## PA-16 — Peer/dispute route coordinator

**Candidate execution form:** judgment_role

**Inputs:** Actual adverse issue, notice, appointment and available challenge routes.

**Output:** Proper next-route proposal, filing/interaction status and limits.

**Decision scope:** Select the supported correction, peer exchange or dispute route under established standing and procedure; clinical representation requires assigned professional authority and external outcomes require actual observations.

**Must not assume/do:** A peer discussion is not automatically a filed appeal or preserved deadline.

**Authority:** Chooses the dispute route under established standing, with peer clinical representation under assigned professional authority.

**Approach:** Treat correction and peer exchange and appeal as distinct procedures with their own deadlines and evidence rather than interchangeable chances to obtain approval.

**Hospital roles:** O10, O11

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Standing, route and actual action evidence remain explicit.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-17"></a>
## PA-17 — Scheduling and access handoff

**Candidate execution form:** hybrid

**Inputs:** Observed authorization/other disposition, prerequisites and receiving interface.

**Output:** A supported handoff, booking/access task or unresolved barrier.

**Decision scope:** Coordinate the next permitted administrative step.

**Must not assume/do:** Booked is not clinically cleared/performed; authorization is not payment.

**Authority:** Coordinates the assigned access handoff from observed disposition and service availability.

**Approach:** Connect the request to a feasible next administrative step and keep access barriers visible to the next responsible participant.

**Hospital roles:** O02, O05, O09

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Recipient acknowledgement/status is observed rather than assumed.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="pa-18"></a>
## PA-18 — PA closure and exception reconciler

**Candidate execution form:** hybrid

**Inputs:** All required PA obligations, receipts and unresolved states.

**Output:** Evidence-backed final/exception disposition and remaining owner.

**Decision scope:** Determine whether the assigned work is complete or still pending under its contract.

**Must not assume/do:** Cannot declare whole patient care complete because one packet stage ended.

**Authority:** Declares the provider assignment's supported endpoint from observed effects and remaining obligations.

**Approach:** Close the assigned work honestly while retaining unresolved responses and downstream responsibilities.

**Hospital roles:** O01, O10

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Every closed obligation has its required observed evidence.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

# UM responsibilities

<a id="um-01"></a>
## UM-01 — Intake record resolver

**Candidate execution form:** hybrid

**Inputs:** Actual request, IDs, attachments and existing payer records.

**Output:** Matched intake record, missing items and duplicate/uncertain identity flags.

**Decision scope:** Establish what was received and which case it belongs to.

**Must not assume/do:** An intake receipt is not a substantive determination.

**Authority:** Shapes the reviewable intake record from received material and verified case linkage.

**Approach:** Give the reviewing function a faithful account of what arrived and what remains missing without implying a substantive decision.

**Hospital roles:** U01

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Request identity and observed receipt are retained.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-02"></a>
## UM-02 — Product and benefit examiner

**Candidate execution form:** hybrid

**Inputs:** Actual product/enrollment/benefit observations.

**Output:** Administrative facts and permitted route implications.

**Decision scope:** Identify benefit/eligibility outcome within the actual assignment.

**Must not assume/do:** No medical-necessity conclusion from administrative mismatch alone.

**Authority:** Decides the assigned administrative benefit question from plan records under documented delegation.

**Approach:** Apply membership and benefit rules to their administrative question and route clinical issues to the appropriate review function.

**Hospital roles:** U02

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Administrative and clinical grounds remain separately labeled.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-03"></a>
## UM-03 — Route and delegation interpreter

**Candidate execution form:** bounded_reasoning

**Inputs:** Task stage, product, assignment and delegated/retained functions.

**Output:** Applicable route and bounded decision envelope.

**Decision scope:** Identify permitted nonclinical alternatives, review stages and retained functions.

**Must not assume/do:** Cannot assume all nonclinical approvals are forbidden or all denials are allowed.

**Authority:** Chooses the permitted review route under program procedure and documented delegation.

**Approach:** Choose a supported operational lane while keeping retained functions and professional decision authority explicit.

**Hospital roles:** U01, U08, U17

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Route records actual delegation/applicability uncertainty.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-04"></a>
## UM-04 — Governing policy resolver

**Candidate execution form:** bounded_reasoning

**Inputs:** Product/service/setting/date and approved policy sources.

**Output:** Applicable source/version and unresolved applicability.

**Decision scope:** Select the controlling policy evidence for this task.

**Must not assume/do:** Generated summaries cannot replace or approve governing policy.

**Authority:** Selects the controlling review policy from product context and source applicability.

**Approach:** Establish which policy governs before judging the evidence and preserve unresolved version or applicability questions.

**Hospital roles:** G08, U03, U04

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Policy identity/version accompanies later analysis.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-05"></a>
## UM-05 — Criteria logic decomposer

**Candidate execution form:** bounded_reasoning

**Inputs:** Applicable policy language, exceptions and definitions.

**Output:** Structured criterion/AND/OR/exception map.

**Decision scope:** Interpret the rule structure without changing the rule.

**Must not assume/do:** Cannot add a more convenient criterion or omit an exception.

**Authority:** Interprets governing criteria with their alternatives and exceptions.

**Approach:** Apply the rule as written and expose its alternatives rather than simplify away a material exception.

**Hospital roles:** U03, U04

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** The map can be traced back to the source language.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-06"></a>
## UM-06 — Clinical fact extractor

**Candidate execution form:** bounded_reasoning

**Inputs:** Permitted chart/request evidence.

**Output:** Attributed relevant facts with unknowns and source locators.

**Decision scope:** Extract what is actually observed and relevant.

**Must not assume/do:** No invented clinical observation or cross-patient retrieval.

**Authority:** Establishes attributed clinical facts for review from observed records.

**Approach:** Read the submitted evidence carefully and keep authored findings distinct from reviewer inference.

**Hospital roles:** U03, U04

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Facts remain separable from reviewer interpretation.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-07"></a>
## UM-07 — Chronology and prior-work examiner

**Candidate execution form:** bounded_reasoning

**Inputs:** Dated records, attempted services and required temporal conditions.

**Output:** Supported timeline and date/sequence uncertainty.

**Decision scope:** Check relevant sequence/duration evidence.

**Must not assume/do:** Unknown dates cannot become assumed qualifying durations.

**Authority:** Establishes the relevant chronology from dated records and documented prior work.

**Approach:** Test duration and sequence against actual evidence and retain unknown dates as unknown.

**Hospital roles:** U03, U04

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Timeline retains source dates and unresolved temporal gaps.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-08"></a>
## UM-08 — Initial criteria matcher

**Candidate execution form:** judgment_role

**Inputs:** Rule map, facts, timeline and current initial-review scope.

**Output:** Criteria assessment, rationale and permitted recommendation/action.

**Decision scope:** Apply governing criteria to observed evidence; approve only under documented delegation when criteria and program permit, otherwise recommend or escalate within the assigned initial-review function.

**Must not assume/do:** Not an automatically authorized final denial or reconsideration.

**Authority:** Approves under documented delegation when criteria and program permit, otherwise recommends or escalates the initial clinical review.

**Approach:** Apply governing criteria to the evidence and resolve the assigned review through a supported decision or an explicit route to the responsible decision-maker.

**Hospital roles:** U03, U06, U07

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Assessment separates met/not-met/unknown with evidence.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-09"></a>
## UM-09 — Ambiguity investigator

**Candidate execution form:** bounded_reasoning

**Inputs:** Conflicts, uncertain rule terms and missing evidence.

**Output:** Specific issues, possible interpretations and clarification route.

**Decision scope:** Identify unresolved interpretation/evidence needs.

**Must not assume/do:** Cannot resolve uncertainty by confident assertion or majority vote.

**Authority:** Identifies material review uncertainty from conflicting evidence or unclear policy applicability.

**Approach:** Investigate what could change the review conclusion and explain the consequence of each unresolved question.

**Hospital roles:** U03, U04, U05

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Contradictions and alternatives remain visible to the decision function.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-10"></a>
## UM-10 — Additional-information planner

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual gaps and permitted requester/provider interface.

**Output:** Targeted information request and pending-response status.

**Decision scope:** Select appropriate additional information within the workflow.

**Must not assume/do:** Cannot request irrelevant data indefinitely or treat absent reply as an invented fact.

**Authority:** Chooses focused additional-information requirements from review gaps under permitted procedure.

**Approach:** Ask focused questions that enable the assigned review and track the response without turning missing information into an endless delay.

**Hospital roles:** U01, U03

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Request has purpose, owner and observed status.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-11"></a>
## UM-11 — Service-specific consultant

**Candidate execution form:** bounded_reasoning

**Inputs:** A bounded specialty question and scoped case/policy evidence.

**Output:** Sourced consultation with limits and proposed implications.

**Decision scope:** Analyze the assigned pharmacy/BH/specialty issue.

**Must not assume/do:** Consultation is not automatically the authorized determination.

**Authority:** Contributes the assigned specialty opinion within professional scope, with decision authority under separate assignment.

**Approach:** Contribute focused expertise with its rationale and limitations rather than imply that consultation itself settles the case.

**Hospital roles:** U05, U06, U07

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** The result names its source snapshot and unresolved limits.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-12"></a>
## UM-12 — Review assignment and authority checker

**Candidate execution form:** hybrid

**Inputs:** Actual stage, role assignment, expertise/delegation constraints and prior involvement.

**Output:** Permitted next decision function or unresolved assignment problem.

**Decision scope:** Check authority metadata/route; not self-appoint new authority.

**Must not assume/do:** A role title or fresh context does not prove required independence.

**Authority:** Establishes the review assignment's authority from documented delegation and independence requirements.

**Approach:** Verify the actual function and retained authority instead of inferring permission from seniority or a role title.

**Hospital roles:** U08, U17

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** The acting function matches the actual task/tool assignment.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-13"></a>
## UM-13 — Determination authoring role

**Candidate execution form:** judgment_role

**Inputs:** Complete applicable review record, current authority and required outcome contract.

**Output:** Authorized determination/rationale or supported unresolved disposition.

**Decision scope:** Issue or recommend the clinical coverage determination actually assigned under documented authority and governing criteria; preserve the difference between recommendation, recorded decision and finalized determination.

**Must not assume/do:** Does not derive authority from case-owner seniority or pretend a draft is finalized.

**Authority:** Issues the clinical coverage determination under assigned documented delegation, otherwise recommends it from governing criteria and observed evidence.

**Approach:** Reach the supported assigned decision and explain its rationale while preserving recommendation and final determination as distinct records.

**Hospital roles:** U04, U03

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Substantive decision and actual finalization evidence align.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-14"></a>
## UM-14 — Notice content mapper

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual determination, reason, recipient and applicable notice requirements.

**Output:** Matching notice draft and delivery obligations.

**Decision scope:** Represent the authoritative determination and applicable procedural information under notice policy; resolve missing rationale through the responsible decision source rather than changing the outcome.

**Must not assume/do:** Cannot alter the outcome to improve the letter.

**Authority:** Speaks for the recorded determination and applicable procedural rights under notice policy.

**Approach:** Explain the outcome plainly to the intended recipient and resolve missing rationale without rewriting the decision.

**Hospital roles:** U09, U10, U11

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Reason/outcome/version/recipient match the decision record.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-15"></a>
## UM-15 — Notice delivery and readback operator

**Candidate execution form:** tool_operation

**Inputs:** Permitted notice artifact, recipient/channel and action identity.

**Output:** Observed delivery receipt/failure/unknown and current state.

**Decision scope:** Execute the actual notice/delivery operation.

**Must not assume/do:** Draft, final, sent and delivered are different states.

**Authority:** Carries the assigned notice through available tools and represents observed delivery state.

**Approach:** Carry the authorized communication through its required channel and track failures or uncertain receipt explicitly.

**Hospital roles:** U09

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Outcome comes from the tool/allowed readback, not narration.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-16"></a>
## UM-16 — Appeal route intake role

**Candidate execution form:** hybrid

**Inputs:** Actual challenge, issue, representation and product/stage.

**Output:** Correct appeal/reconsideration/external route and file status.

**Decision scope:** Establish the actual review route and standing.

**Must not assume/do:** A grievance or peer exchange is not every appeal type.

**Authority:** Selects the applicable challenge route and standing from the request and governing procedure.

**Approach:** Distinguish appeal from grievance and peer exchange before routing the record and any missing material.

**Hospital roles:** U12

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Route and actual accepted/forwarded status are explicit.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-17"></a>
## UM-17 — Reconsideration role

**Candidate execution form:** judgment_role

**Inputs:** Applicable appeal record, actual assignment and independence requirements.

**Output:** Permitted reconsidered contribution/outcome with source rationale.

**Decision scope:** Affirm or reverse within assigned reconsideration authority using the disputed record and governing criteria; verify applicable review separation rather than infer independence from a changed prompt.

**Must not assume/do:** Changing the initial worker’s prompt does not prove real institutional independence; do not invent external human steps if the benchmark assigns the function.

**Authority:** Affirms or reverses the disputed decision under assigned reconsideration authority and applicable independence requirements.

**Approach:** Reconsider the disputed record and new evidence on their merits while checking that the required review separation actually exists.

**Hospital roles:** U13

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Stage, source, assignment and observed outcome remain identifiable.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="um-18"></a>
## UM-18 — Effectuation and UM closure reconciler

**Candidate execution form:** hybrid

**Inputs:** Determination/review outcome and actual implementation/notice obligations.

**Output:** Supported final/exception disposition with pending effects/owners.

**Decision scope:** Track what the actual outcome requires next.

**Must not assume/do:** Favorable review is not automatically implemented authorization, service or payment.

**Authority:** Declares the assigned review endpoint and remaining effectuation duties from the recorded outcome and observed implementation.

**Approach:** Track what the decision requires next and close only the work whose effects are actually supported.

**Hospital roles:** U01, U09, U17

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Every terminal claim has its corresponding observed evidence.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

# CM responsibilities

<a id="cm-01"></a>
## CM-01 — Chart and task orienter

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual CM task, permitted chart and current outreach/assessment state.

**Output:** Case brief, current obligations and source-linked unknowns.

**Decision scope:** Interpret the referral and current episode using observed chart context and applicable care-management intake policy; identify coordination priorities and unresolved needs.

**Must not assume/do:** Cannot assume every case needs the same assessments or starts at first contact.

**Authority:** Chooses coordination priorities from referral context and observed chart information.

**Approach:** Treat the referral as a starting point for understanding this member's needs and the program's responsibilities rather than a fixed form sequence.

**Hospital roles:** M01, M30

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Task brief matches the actual starting stage.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-02"></a>
## CM-02 — Contact and representation checker

**Candidate execution form:** hybrid

**Inputs:** Actual contact, identity, communication and representative facts.

**Output:** Permitted participant/channel and unresolved scope.

**Decision scope:** Check who is speaking and in what capacity.

**Must not assume/do:** Family relation or convenient contact is not blanket patient authority.

**Authority:** Establishes contact and representation scope from observed identity and authority records.

**Approach:** Make communication accessible and verify who is speaking for whom without substituting a representative's wishes for the member's.

**Hospital roles:** M01, P03, P05

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Participants and representation limits are separately attributed.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-03"></a>
## CM-03 — Outreach planner

**Candidate execution form:** bounded_reasoning

**Inputs:** Required outreach task, contact options and observed constraints.

**Output:** Permitted outreach step with unanswered questions.

**Decision scope:** Plan outreach from applicable care-management outreach and enrollment policy, observed contact permissions and current member questions; retain required information and exit/handoff duties.

**Must not assume/do:** Cannot invent availability, consent or a required universal contact sequence.

**Authority:** Chooses the outreach plan under care-management outreach and enrollment policy and observed contact permissions.

**Approach:** Prepare an accessible conversation that explains the program and explores priorities while preserving consent conditions and policy-specific exit duties.

**Hospital roles:** M01, M09, M13

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Plan follows actual task/supplied contact constraints.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-04"></a>
## CM-04 — Member-engagement lead

**Candidate execution form:** dialogue

**Inputs:** Actual conversation state, prior questions/answers and pending objective.

**Output:** Source-linked engagement handoff with consent status, member priorities and open questions; accurate program information and permitted post-consent interview findings.

**Decision scope:** Represent the program accurately under retrieved policy and observed eligibility conditions; learn member priorities, connect them to supported services and answer questions plainly. Invite an informed decision, respect decline and conduct a permitted interview only after actual consent.

**Must not assume/do:** Cannot use an internal patient persona to provide replies.

**Authority:** Speaks for the program to the member: may state the program's purpose, services, cost and participation terms as the retrieved policy states them, once the policy's conditions are checked against the member's records; may explain what care planning could include, ask for enrollment consent, and conduct the permitted interview after consent. It speaks as the member's health plan: the member's observed active coverage with the plan operating the program is the plan information that participation statements rely on.

**Approach:** Find what matters to the member and connect it to program services. Answer plainly from policy, invite an informed decision and respect decline without pressure or promised dates or outcomes.

**Hospital roles:** M01, M09, M13

**Status label:** executing_worker

**Model visible:** True

**Completion check:** Once questions are answered, the member was asked directly whether to enroll before any offer to end contact; an informed decision is observed or the member ended contact. Consent status, priorities and open questions are preserved.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-05"></a>
## CM-05 — Answer and speaker extractor

**Candidate execution form:** bounded_reasoning

**Inputs:** Actual patient/representative messages and relevant chart references.

**Output:** Attributed answers, quotations/locators and explicit unknown/refused items.

**Decision scope:** Extract what each person actually said.

**Must not assume/do:** Silence, translated text or caregiver opinion cannot become patient agreement.

**Authority:** Represents dialogue findings faithfully from the actual transcript.

**Approach:** Listen for the person's meaning and preserve uncertainty or refusal instead of filling a convenient answer into the record.

**Hospital roles:** M01, P05

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Answers preserve speaker, source and uncertainty.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-06"></a>
## CM-06 — Assessment obligation tracker

**Candidate execution form:** hybrid

**Inputs:** Actual required assessment contract and sourced answers.

**Output:** Complete/pending/refused/not-applicable field status where supported.

**Decision scope:** Track required information without manufacturing answers.

**Must not assume/do:** A filled form is not valid if values were inferred beyond scope.

**Authority:** Establishes assessment completeness from required fields and sourced answers under actual consent.

**Approach:** Make each assessment entry defensible and identify a missing answer without turning a completed form into a substitute for performed assessment.

**Hospital roles:** M01, C06

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each completed field has the required evidence or permitted derivation.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-07"></a>
## CM-07 — Needs and barriers analyst

**Candidate execution form:** bounded_reasoning

**Inputs:** Attributed answers, chart facts, goals and actual resource context.

**Output:** Supported needs/barriers and questions for clarification.

**Decision scope:** Identify relevant barriers and appropriate role contributions.

**Must not assume/do:** A plausible stereotype about another patient cannot inform this patient.

**Authority:** Identifies coordination needs and barriers from the member's account and observed records.

**Approach:** Understand how practical circumstances affect the member's goals and seek clarification rather than rely on assumptions about a population.

**Hospital roles:** M01, M02, M09

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each proposed need/barrier is grounded in this case.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-08"></a>
## CM-08 — Sensitive issue and scope flagger

**Candidate execution form:** bounded_reasoning

**Inputs:** Current case facts and applicable safety/privacy/escalation rules.

**Output:** Scoped concern and permitted next-action recommendation.

**Decision scope:** Flag when the assigned function lacks evidence/authority.

**Must not assume/do:** Cannot invent a diagnosis, reporting mandate or resolved protection outcome.

**Authority:** Identifies safety or scope concerns under applicable escalation and privacy rules.

**Approach:** Treat sensitive concerns respectfully and route issues to the responsible function without inventing a diagnosis or protection outcome.

**Hospital roles:** M01, M31, G10

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Flag cites actual case evidence and the relevant unresolved rule.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-09"></a>
## CM-09 — Patient goal elicitation role

**Candidate execution form:** dialogue

**Inputs:** Actual patient preferences and current plan discussion.

**Output:** Patient-authored/accepted goals with outstanding disagreement.

**Decision scope:** Elicit the member's own priorities during permitted outreach and clarify goals for care planning under the applicable consent conditions; preserve acceptance, disagreement and unknown status.

**Must not assume/do:** Staff goals or another patient’s preferences cannot substitute.

**Authority:** Represents the member's goals from their expressed priorities and agreement.

**Approach:** Elicit what useful help would mean to the member during permitted outreach and revisit proposed goals as understanding changes without assessing before consent.

**Hospital roles:** M01, M13

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Goal origin and agreement/unknown status are preserved.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-10"></a>
## CM-10 — Medication context interface

**Candidate execution form:** bounded_reasoning

**Inputs:** This case’s medication records, instructions and access concerns.

**Output:** Sourced medication question/referral or permitted contribution.

**Decision scope:** Separate adherence/access evidence from therapy decisions.

**Must not assume/do:** Availability or counselor advice is not a new medication order.

**Authority:** Owns the medication coordination question from existing instructions and observed access concerns.

**Approach:** Help resolve medication-use or access barriers through the appropriate professional contribution while preserving the prescriber's treatment authority.

**Hospital roles:** M01, M04, M05

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Existing instructions and any proposed clinical change stay distinct.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-11"></a>
## CM-11 — Psychosocial and resource analyst

**Candidate execution form:** bounded_reasoning

**Inputs:** Case-specific support needs, preferences and actual resource evidence.

**Output:** Proposed care-plan interventions linked to member goals and support needs, with responsible recipients and eligibility/availability uncertainty.

**Decision scope:** Translate supported psychosocial and resource options into proposed care-plan interventions within assigned scope.

**Must not assume/do:** A directory listing is not accepted or delivered assistance.

**Authority:** Proposes care-plan interventions for psychosocial and resource needs from observed barriers and supported options.

**Approach:** Turn relevant support options into practical proposed interventions linked to the member's goals while preserving eligibility and availability uncertainty.

**Hospital roles:** M01, M02, M09

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Options retain source, scope and unconfirmed status.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-12"></a>
## CM-12 — Care-task dependency planner

**Candidate execution form:** bounded_reasoning

**Inputs:** Patient goals, existing instructions, permitted service options and task obligations.

**Output:** Ordered/parallel next tasks and accountable recipients.

**Decision scope:** Arrange operational dependencies within actual scope.

**Must not assume/do:** Not an independent clinical triage/treatment algorithm or a universal hospital sequence.

**Authority:** Chooses care-task sequence and ownership from supported dependencies and member goals.

**Approach:** Organize feasible coordination work around the member's needs and make the next responsibility clear without imposing a universal clinical pathway.

**Hospital roles:** M01, M30, M18

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Dependencies are justified by actual requirements and current evidence.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-13"></a>
## CM-13 — Care-plan composer

**Candidate execution form:** bounded_reasoning

**Inputs:** Sourced goals, assessment, authorized clinical contributions and planned tasks.

**Output:** Versioned care plan connecting supported problems, member goals and interventions with escalation conditions, follow-up cadence, responsibilities and unresolved items.

**Decision scope:** Compose the requested plan using applicable care-plan standards; distinguish sourced problems and goals from proposed interventions and their execution status.

**Must not assume/do:** A plan is not new prescribing authority or evidence of service execution.

**Authority:** Shapes a coherent care plan from observed assessment, member goals and applicable care-plan standards.

**Approach:** Connect problems and goals to interventions, escalation conditions and follow-up cadence. Preserve ownership, uncertainty and the distinction between planned and performed work.

**Hospital roles:** M01, M18

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each section distinguishes evidence, recommendation, owner and status.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-14"></a>
## CM-14 — Referral operator

**Candidate execution form:** tool_operation

**Inputs:** Permitted referral intent, recipient, case context and action identity.

**Output:** Actual referral receipt/failure/unknown where performed, otherwise a clearly planned care-plan referral intervention.

**Decision scope:** Coordinate a permitted referral through an actual available tool; when no execution tool exists, include the proposed referral intervention and responsible recipient in the care plan.

**Must not assume/do:** Referral sent is not accepted, scheduled or completed.

**Authority:** Coordinates the consented referral through available tools, or places its proposed intervention in the care plan when execution tools are absent.

**Approach:** Pursue the supported referral connection where it can actually be performed and otherwise specify the proposed intervention and responsible recipient in the plan.

**Hospital roles:** M01, O02, M10

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Record observed receipt and next owner if executed; otherwise record the planned intervention, execution limit and responsible recipient without claiming a sent referral.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-15"></a>
## CM-15 — Receiving acknowledgement tracker

**Candidate execution form:** hybrid

**Inputs:** Actual receiver replies, referral requirements and capacity evidence.

**Output:** Sourced receiver status and next obligation, or a clearly planned acknowledgement follow-up intervention.

**Decision scope:** Track the recipient's actual acceptance or status when observable; when no receiving-status tool exists, plan the acknowledgement follow-up intervention in the care plan.

**Must not assume/do:** Cannot infer acceptance or bed/service availability from a preferred plan.

**Authority:** Represents actual receiver acceptance, or plans acknowledgement follow-up in the care plan when receiving-status tools are absent.

**Approach:** Follow the connection to its real receiving status and retain a proposed acknowledgement check when the environment cannot obtain one.

**Hospital roles:** M01, M19, M20, M26

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each claimed receiving status has a fresh actual source; an unexecuted acknowledgement check remains a planned intervention with an owner.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-16"></a>
## CM-16 — Appointment and access coordinator

**Candidate execution form:** hybrid

**Inputs:** Actual accepted/referral state, available scheduling data and patient constraints.

**Output:** Observed booking/support status where performed, otherwise a planned care-plan access intervention with unresolved barriers.

**Decision scope:** Coordinate an available permitted access step; when no execution tool exists, plan the access intervention and responsible recipient in the care plan.

**Must not assume/do:** Booked transport/visit is not attendance, care delivered or clinical clearance.

**Authority:** Coordinates access from member constraints and observed availability, or plans the intervention in the care plan when execution tools are absent.

**Approach:** Help make access feasible through available arrangements and otherwise describe the proposed access work and its owner in the care plan.

**Hospital roles:** M01, O05, M23

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Claimed bookings have supplied observations; unavailable execution is represented as planned coordination with an owner and outstanding barriers.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-17"></a>
## CM-17 — Transition handoff writer

**Candidate execution form:** bounded_reasoning

**Inputs:** Current plan, known changes, pending work and receiving participant.

**Output:** Source-linked transition/handoff artifact.

**Decision scope:** Communicate uncertainty, responsibility and next actions.

**Must not assume/do:** A sent summary does not prove comprehension, accepted responsibility or medical discharge authority.

**Authority:** Shapes supported handoff content from the current plan and unresolved responsibilities.

**Approach:** Give the receiving participant a clear account of what changed and what remains to be done while tracking acknowledgement separately from a draft.

**Hospital roles:** M01, M18

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Named receiver and actual acknowledgement are distinguished from the draft.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-18"></a>
## CM-18 — Follow-up obligation monitor

**Candidate execution form:** hybrid

**Inputs:** Current case-specific pending tasks, actual deadlines and observed replies.

**Output:** Due/pending/blocked/completed task status and next owner.

**Decision scope:** Identify what still needs a supported action.

**Must not assume/do:** A reminder sent cannot complete an assessment or service.

**Authority:** Establishes follow-up obligation status from actual deadlines and observed replies.

**Approach:** Track whether the intended connection occurred and keep the next responsible participant aware of unresolved work.

**Hospital roles:** M01, M30

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Each closure or escalation retains actual evidence.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-19"></a>
## CM-19 — New-information reconciler

**Candidate execution form:** bounded_reasoning

**Inputs:** New case observations, prior plan/source versions and active obligations.

**Output:** Changed/unchanged/conflicting facts and affected next tasks.

**Decision scope:** Re-evaluate this case after new evidence or user steering.

**Must not assume/do:** Cannot silently overwrite history or let stale helper results win.

**Authority:** Revises the case interpretation from new evidence and current member priorities.

**Approach:** Update coordination work when circumstances change while preserving the history and why an earlier interpretation was superseded.

**Hospital roles:** M01

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Changes cite sources and preserve prior superseded interpretations.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="cm-20"></a>
## CM-20 — CM closure and exception reconciler

**Candidate execution form:** hybrid

**Inputs:** Actual requested outcomes, dialogue dispositions, plan/referral/follow-up evidence.

**Output:** Source-supported episode disposition with remaining permitted documentation/communication duties, return-path information where required and unmet goals.

**Decision scope:** Choose the episode completion, decline or exception path under retrieved care-management closure policy and observed participation; distinguish an ended contact from consent or refusal.

**Must not assume/do:** A good conversation or completed plan alone is not all downstream care completed.

**Authority:** Chooses the episode closure or decline path from observed participation under care-management closure policy.

**Approach:** Respect a decline or ended contact and complete the remaining permitted documentation and return-path duties under retrieved policy while preserving any unmet assigned goal.

**Hospital roles:** M01, M30

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Disposition follows the retrieved policy and observed participation; remaining duties and unmet assigned outcomes remain explicit without claiming downstream care.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

# SH responsibilities

<a id="sh-01"></a>
## SH-01 — Task and stage router

**Candidate execution form:** hybrid

**Inputs:** Actual instruction/tool scope and current observed task stage.

**Output:** A bounded composite-job assignment.

**Decision scope:** Choose only task-relevant responsibilities.

**Must not assume/do:** Does not force PA→UM→CM or create work not requested.

**Authority:** Selects relevant responsibilities from the actual instruction and observed stage.

**Approach:** Keep the requested work central and route only the responsibilities it actually needs.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Assignment refers to actual task evidence.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-02"></a>
## SH-02 — Scoped context builder

**Candidate execution form:** deterministic

**Inputs:** Role definition, patient/case namespace, current request and permitted evidence.

**Output:** A version-linked request packet with explicit unknowns.

**Decision scope:** Select only allowed case-local and approved general content.

**Must not assume/do:** No other patient’s history, summaries or learned preferences.

**Authority:** Selects permitted context under case namespaces and source permissions.

**Approach:** Give each function the evidence it needs with explicit unknowns and traceable source versions.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** False

**Completion check:** Packet manifest records its namespace/source set.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-03"></a>
## SH-03 — Reference retrieval service

**Candidate execution form:** hybrid

**Inputs:** Current query, approved sources and case/purpose filters.

**Output:** Relevant source spans with metadata and limits.

**Decision scope:** Retrieve rather than invent policy/record evidence.

**Must not assume/do:** Search similarity is not truth, authority or patient identity.

**Authority:** Retrieves relevant evidence from approved sources and scoped queries.

**Approach:** Return relevant evidence with its provenance and limitations while leaving policy interpretation to the assigned function.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Every item passes scope and source checks before injection.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-04"></a>
## SH-04 — Evidence and contradiction ledger

**Candidate execution form:** deterministic

**Inputs:** Observed evidence IDs, origins, versions and derived interpretations.

**Output:** Traceable evidence/claim links and unresolved conflicts.

**Decision scope:** Preserve provenance and version relationships.

**Must not assume/do:** A summary cannot silently become authoritative environment state.

**Authority:** Preserves claim provenance and source version relationships.

**Approach:** Keep original evidence distinguishable from summaries and retain contradictions for explicit resolution.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** False

**Completion check:** Derived claims retain their original source references.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-05"></a>
## SH-05 — Artifact renderer

**Candidate execution form:** hybrid

**Inputs:** Approved case-local content and actual artifact contract.

**Output:** Draft/final artifacts with author/source/status metadata.

**Decision scope:** Render the required representation.

**Must not assume/do:** Draft, finalized and delivered remain separate.

**Authority:** Renders faithful artifacts from approved content under the output contract.

**Approach:** Make a clear usable artifact whose draft or final status remains visible and whose claims remain source-linked.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** True

**Completion check:** Output matches source/version/required contract.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-06"></a>
## SH-06 — Operation gate and action journal

**Candidate execution form:** deterministic

**Inputs:** Principal, operation, payload, task/version and actual tool contract.

**Output:** Permitted dispatch and observed receipt/unknown state.

**Decision scope:** Enforce the actual execution/retry envelope.

**Must not assume/do:** Valid model prose or JSON does not grant authority or exactly-once effects.

**Authority:** Enforces the execution envelope under tool contracts and journaled outcomes.

**Approach:** Treat external effects as events requiring identity and reconciliation rather than as implications of plausible model text.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** False

**Completion check:** Action identity and outcome evidence are recorded.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-07"></a>
## SH-07 — Budget and work scheduler

**Candidate execution form:** deterministic

**Inputs:** Pending case-local work, dependencies and current resource limits.

**Output:** Bounded execution/delegation plan.

**Decision scope:** Admit work and account for combined resource spend.

**Must not assume/do:** Cannot fan out every micro-role or reuse another patient’s reasoning.

**Authority:** Admits work within current budgets and dependencies.

**Approach:** Spend bounded resources on task-relevant work and keep cancellation and stopping conditions explicit.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** False

**Completion check:** Queue, budget, cancellation and stop conditions are explicit.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-08"></a>
## SH-08 — Case checkpoint and context reducer

**Candidate execution form:** hybrid

**Inputs:** Current case/request, protected obligations and coherent tool/dialogue history.

**Output:** Case-scoped checkpoint/projection with retained source references.

**Decision scope:** Reduce context under the actual provider ownership contract.

**Must not assume/do:** Does not promote patient facts into reusable staff knowledge or prove lossless semantics.

**Authority:** Preserves checkpoint obligations under the provider context contract.

**Approach:** Reduce context carefully while preserving the active request and unresolved effects and access to original sources.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** False

**Completion check:** Active request, obligations, unknown effects and source versions survive or fail explicitly.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-09"></a>
## SH-09 — Patient isolation barrier

**Candidate execution form:** deterministic

**Inputs:** Principal, organization, patient/case, source/query/cache namespaces.

**Output:** Allowed case-local views or a denied/unresolved access.

**Decision scope:** Prevent patient-derived state crossing into another patient’s work.

**Must not assume/do:** Not satisfied by merely asking the model to ignore unrelated context.

**Authority:** Denies cross-case source access under principal and patient namespaces.

**Approach:** Enforce isolation before content reaches reasoning or tools rather than relying on a request to ignore unrelated material.

**Hospital roles:** code-only safeguard

**Status label:** prompt_contract

**Model visible:** False

**Completion check:** Cross-patient source injection is rejected before inference/tool use.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning

<a id="sh-10"></a>
## SH-10 — Bounded invariant critic

**Candidate execution form:** bounded_reasoning

**Inputs:** Permitted case facts, intended action/artifact and task-visible requirements.

**Output:** Specific evidence-based defects or readiness limits.

**Decision scope:** Challenge unsupported claims and missing obligations.

**Must not assume/do:** Not hidden verifier, external reviewer or unlimited debate loop.

**Authority:** Challenges unsupported readiness and stop claims against task-visible requirements and observed effects.

**Approach:** Review both overclaiming and remaining useful permitted work with specific source-backed objections while leaving the owner responsible for the next decision.

**Hospital roles:** code-only safeguard

**Status label:** executing_worker

**Model visible:** True

**Completion check:** Feedback cites the case-visible contradiction/requirement and stays within budget.

**Activation:** Only when the current assigned task/stage and actual tool contract require this work.

**Memory:** PATIENT_CASE_ONLY; approved general procedures read-only; no patient-derived cross-patient learning
