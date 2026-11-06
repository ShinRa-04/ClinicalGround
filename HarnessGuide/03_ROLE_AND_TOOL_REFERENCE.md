# Complete responsibility and tool reference

See the [glossary](GLOSSARY.md) for role versus agent, provider versus payer,
determination, handoff and evidence terminology.

This is a source-catalog reference, not a claim that every listed function runs in every task. See [the implementation guide](02_IMPLEMENTED_HARNESS.md) before interpreting a responsibility as an agent.

## Responsibility catalog

All 66 definitions below come from the project-authored `data/micro_roles.json`. The combined owner receives its domain definitions plus the 10 shared definitions. Names identify responsibilities; they do not create independent agents, legal authority, or clinical capabilities. Optional helper calls select a definition from this catalog.

Each row preserves the catalog's stated decision scope, output, boundary and completion check. These are instruction contracts, not independently verified performance. They describe how work should be bounded; the actual operation and completion gates remain in code.

### Provider PA — 18 definitions

| Responsibility | Decision scope | Output | Boundary | Completion check |
| --- | --- | --- | --- | --- |
| PA-01 Request interpreter | Identify what this provider task asks and which obligations are actually present. | A scoped work brief with required outputs and open questions. | Cannot assume every task starts at intake or must traverse every department. | Brief refers to the real task and retains the current user request. |
| PA-02 Identity and record linker | Link only under the actual identifier evidence; otherwise request clarification. | Verified links or explicit mismatch/uncertainty. | Similar names are insufficient; cannot merge another patient’s evidence. | Each included record has a matching case/patient reference. |
| PA-03 Coverage snapshot reader | Separate known, unknown and outdated administrative facts. | Attributed coverage facts and freshness limits. | Benefit verification is not authorization, clinical necessity or payment. | Snapshot retains product/source/date and does not upgrade its meaning. |
| PA-04 Authorization requirement scout | Identify the applicable administrative requirement or unresolved requirement. | Required/not-required/unknown route with evidence. | Cannot invent a PA requirement for all services. | Route cites actual source/response and preserves uncertainty. |
| PA-05 Policy applicability resolver | Resolve applicability before using criteria. | Selected applicable policy/version and exclusions/uncertainty. | A plausible document title is not proof it governs this case. | Selection records why the source applies or why no selection is justified. |
| PA-06 Clinical evidence collector | Find relevant existing evidence and record what could not be obtained. | Authentic evidence bundle with authorship and locators. | Cannot create an examination, diagnosis or test result to fill a gap. | Every factual item points to an observed source. |
| PA-07 Criterion-to-evidence linker | Interpret the relationship between criterion and existing evidence. | Criterion table with supported/not-supported/unknown and exact evidence. | Missing evidence is not automatically an explicit negative finding. | Each criterion result preserves source, logic and uncertainty. |
| PA-08 Gap and contradiction analyst | Identify what blocks a supported packet or which discrepancy needs clarification. | Specific unresolved gaps/conflicts and next evidence need. | Cannot silently choose the convenient version or rewrite original records. | Each gap/conflict is concrete enough for an appropriate recipient to address. |
| PA-09 Clinical clarification router | Choose the right question/recipient within the assigned workflow. | A scoped question and observed response status. | Administrative staff cannot answer on behalf of the clinician. | Question, recipient and actual reply/unknown state remain distinct. |
| PA-10 Coding support role | Suggest administrative coding supported by supplied documentation. | Supported code proposal or query. | A code does not independently establish a clinical fact. | Proposal is traceable and ambiguity is retained. |
| PA-11 Packet composer | Organize permitted facts and required artifacts. | Versioned supported packet/draft. | A polished packet is not a submission, receipt or approval. | Required fields refer to sources; missing material stays explicit. |
| PA-12 Packet preflight checker | Check completeness, identity, source consistency and readiness. | Ready/not-ready findings tied to the actual contract. | Must not invent extra mandatory fields or act as the official hidden verifier. | Findings distinguish genuine contract failures from preferences. |
| PA-13 Submission operator | Execute only the authorized submission operation. | Actual submission receipt, failure or unknown outcome. | Cannot retry an uncertain external effect as a fresh intention without reconciliation. | Receipt/readback or explicit outcome-unknown is recorded. |
| PA-14 Response classifier | Classify approval, denial, information request or another supported response. | Observed response type, affected obligations and open questions. | Cannot create a new payer determination from its own interpretation. | Classification retains the actual response and does not collapse decision/notice/status. |
| PA-15 Information-request responder | Plan the supported response to the specific request. | Targeted response plan/material and outstanding needs. | Cannot fabricate clinical support or answer requests never made. | Each response item addresses a real RFI or records why it is unavailable. |
| PA-16 Peer/dispute route coordinator | Separate correction, peer exchange, appeal and external eligibility. | Proper next-route proposal, filing/interaction status and limits. | A peer discussion is not automatically a filed appeal or preserved deadline. | Standing, route and actual action evidence remain explicit. |
| PA-17 Scheduling and access handoff | Coordinate the next permitted administrative step. | A supported handoff, booking/access task or unresolved barrier. | Booked is not clinically cleared/performed; authorization is not payment. | Recipient acknowledgement/status is observed rather than assumed. |
| PA-18 PA closure and exception reconciler | Determine whether the assigned work is complete or still pending under its contract. | Evidence-backed final/exception disposition and remaining owner. | Cannot declare whole patient care complete because one packet stage ended. | Every closed obligation has its required observed evidence. |

### Payer UM — 18 definitions

| Responsibility | Decision scope | Output | Boundary | Completion check |
| --- | --- | --- | --- | --- |
| UM-01 Intake record resolver | Establish what was received and which case it belongs to. | Matched intake record, missing items and duplicate/uncertain identity flags. | An intake receipt is not a substantive determination. | Request identity and observed receipt are retained. |
| UM-02 Product and benefit examiner | Identify benefit/eligibility outcome within the actual assignment. | Administrative facts and permitted route implications. | No medical-necessity conclusion from administrative mismatch alone. | Administrative and clinical grounds remain separately labeled. |
| UM-03 Route and delegation interpreter | Identify permitted nonclinical alternatives, review stages and retained functions. | Applicable route and bounded decision envelope. | Cannot assume all nonclinical approvals are forbidden or all denials are allowed. | Route records actual delegation/applicability uncertainty. |
| UM-04 Governing policy resolver | Select the controlling policy evidence for this task. | Applicable source/version and unresolved applicability. | Generated summaries cannot replace or approve governing policy. | Policy identity/version accompanies later analysis. |
| UM-05 Criteria logic decomposer | Interpret the rule structure without changing the rule. | Structured criterion/AND/OR/exception map. | Cannot add a more convenient criterion or omit an exception. | The map can be traced back to the source language. |
| UM-06 Clinical fact extractor | Extract what is actually observed and relevant. | Attributed relevant facts with unknowns and source locators. | No invented clinical observation or cross-patient retrieval. | Facts remain separable from reviewer interpretation. |
| UM-07 Chronology and prior-work examiner | Check relevant sequence/duration evidence. | Supported timeline and date/sequence uncertainty. | Unknown dates cannot become assumed qualifying durations. | Timeline retains source dates and unresolved temporal gaps. |
| UM-08 Initial criteria matcher | Apply the actual initial-review function. | Criteria assessment, rationale and permitted recommendation/action. | Not an automatically authorized final denial or reconsideration. | Assessment separates met/not-met/unknown with evidence. |
| UM-09 Ambiguity investigator | Identify unresolved interpretation/evidence needs. | Specific issues, possible interpretations and clarification route. | Cannot resolve uncertainty by confident assertion or majority vote. | Contradictions and alternatives remain visible to the decision function. |
| UM-10 Additional-information planner | Select appropriate additional information within the workflow. | Targeted information request and pending-response status. | Cannot request irrelevant data indefinitely or treat absent reply as an invented fact. | Request has purpose, owner and observed status. |
| UM-11 Service-specific consultant | Analyze the assigned pharmacy/BH/specialty issue. | Sourced consultation with limits and proposed implications. | Consultation is not automatically the authorized determination. | The result names its source snapshot and unresolved limits. |
| UM-12 Review assignment and authority checker | Check authority metadata/route; not self-appoint new authority. | Permitted next decision function or unresolved assignment problem. | A role title or fresh context does not prove required independence. | The acting function matches the actual task/tool assignment. |
| UM-13 Determination authoring role | Make the decision actually assigned by the workflow. | Authorized determination/rationale or supported unresolved disposition. | Does not derive authority from case-owner seniority or pretend a draft is finalized. | Substantive decision and actual finalization evidence align. |
| UM-14 Notice content mapper | Render required content from the authoritative decision. | Matching notice draft and delivery obligations. | Cannot alter the outcome to improve the letter. | Reason/outcome/version/recipient match the decision record. |
| UM-15 Notice delivery and readback operator | Execute the actual notice/delivery operation. | Observed delivery receipt/failure/unknown and current state. | Draft, final, sent and delivered are different states. | Outcome comes from the tool/allowed readback, not narration. |
| UM-16 Appeal route intake role | Establish the actual review route and standing. | Correct appeal/reconsideration/external route and file status. | A grievance or peer exchange is not every appeal type. | Route and actual accepted/forwarded status are explicit. |
| UM-17 Reconsideration role | Perform the task-assigned reconsideration function. | Permitted reconsidered contribution/outcome with source rationale. | Changing the initial worker’s prompt does not prove real institutional independence; do not invent external human steps if the benchmark assigns the function. | Stage, source, assignment and observed outcome remain identifiable. |
| UM-18 Effectuation and UM closure reconciler | Track what the actual outcome requires next. | Supported final/exception disposition with pending effects/owners. | Favorable review is not automatically implemented authorization, service or payment. | Every terminal claim has its corresponding observed evidence. |

### Care management — 20 definitions

| Responsibility | Decision scope | Output | Boundary | Completion check |
| --- | --- | --- | --- | --- |
| CM-01 Chart and task orienter | Identify what the current episode requires. | Case brief, current obligations and source-linked unknowns. | Cannot assume every case needs the same assessments or starts at first contact. | Task brief matches the actual starting stage. |
| CM-02 Contact and representation checker | Check who is speaking and in what capacity. | Permitted participant/channel and unresolved scope. | Family relation or convenient contact is not blanket patient authority. | Participants and representation limits are separately attributed. |
| CM-03 Outreach planner | Choose the next allowed channel/question opportunity. | Permitted outreach step with unanswered questions. | Cannot invent availability, consent or a required universal contact sequence. | Plan follows actual task/supplied contact constraints. |
| CM-04 Conversation turn coordinator | Manage dialogue without losing already supplied answers or refusals. | Next relevant question or truthful conversation disposition. | Cannot use an internal patient persona to provide replies. | Each next step follows observed interaction state. |
| CM-05 Answer and speaker extractor | Extract what each person actually said. | Attributed answers, quotations/locators and explicit unknown/refused items. | Silence, translated text or caregiver opinion cannot become patient agreement. | Answers preserve speaker, source and uncertainty. |
| CM-06 Assessment obligation tracker | Track required information without manufacturing answers. | Complete/pending/refused/not-applicable field status where supported. | A filled form is not valid if values were inferred beyond scope. | Each completed field has the required evidence or permitted derivation. |
| CM-07 Needs and barriers analyst | Identify relevant barriers and appropriate role contributions. | Supported needs/barriers and questions for clarification. | A plausible stereotype about another patient cannot inform this patient. | Each proposed need/barrier is grounded in this case. |
| CM-08 Sensitive issue and scope flagger | Flag when the assigned function lacks evidence/authority. | Scoped concern and permitted next-action recommendation. | Cannot invent a diagnosis, reporting mandate or resolved protection outcome. | Flag cites actual case evidence and the relevant unresolved rule. |
| CM-09 Patient goal elicitation role | Clarify the person’s expressed priorities. | Patient-authored/accepted goals with outstanding disagreement. | Staff goals or another patient’s preferences cannot substitute. | Goal origin and agreement/unknown status are preserved. |
| CM-10 Medication context interface | Separate adherence/access evidence from therapy decisions. | Sourced medication question/referral or permitted contribution. | Availability or counselor advice is not a new medication order. | Existing instructions and any proposed clinical change stay distinct. |
| CM-11 Psychosocial and resource analyst | Identify appropriate support/referral questions. | Relevant support options with eligibility/availability uncertainty. | A directory listing is not accepted or delivered assistance. | Options retain source, scope and unconfirmed status. |
| CM-12 Care-task dependency planner | Arrange operational dependencies within actual scope. | Ordered/parallel next tasks and accountable recipients. | Not an independent clinical triage/treatment algorithm or a universal hospital sequence. | Dependencies are justified by actual requirements and current evidence. |
| CM-13 Care-plan composer | Assemble the plan actually requested by the task. | Versioned care plan with responsibilities and unresolved items. | A plan is not new prescribing authority or evidence of service execution. | Each section distinguishes evidence, recommendation, owner and status. |
| CM-14 Referral operator | Send the scoped referral through the actual tool. | Actual referral receipt/failure/unknown. | Referral sent is not accepted, scheduled or completed. | Observed receipt and next owner are recorded. |
| CM-15 Receiving acknowledgement tracker | Track the actual recipient’s decision/status. | Accepted/rejected/pending state and next obligation. | Cannot infer acceptance or bed/service availability from a preferred plan. | Status has an actual source and appropriate freshness. |
| CM-16 Appointment and access coordinator | Coordinate an available next step. | Permitted booking/support task or unresolved access barrier. | Booked transport/visit is not attendance, care delivered or clinical clearance. | Each claimed booking or service status is supported by supplied observations. |
| CM-17 Transition handoff writer | Communicate uncertainty, responsibility and next actions. | Source-linked transition/handoff artifact. | A sent summary does not prove comprehension, accepted responsibility or medical discharge authority. | Named receiver and actual acknowledgement are distinguished from the draft. |
| CM-18 Follow-up obligation monitor | Identify what still needs a supported action. | Due/pending/blocked/completed task status and next owner. | A reminder sent cannot complete an assessment or service. | Each closure or escalation retains actual evidence. |
| CM-19 New-information reconciler | Re-evaluate this case after new evidence or user steering. | Changed/unchanged/conflicting facts and affected next tasks. | Cannot silently overwrite history or let stale helper results win. | Changes cite sources and preserve prior superseded interpretations. |
| CM-20 CM closure and exception reconciler | Decide whether the assigned episode has reached its permitted end. | Supported episode completion/exception and remaining responsibilities. | A good conversation or completed plan alone is not all downstream care completed. | Final claims distinguish episode scope from unobserved future care. |

### Shared safeguards — 10 definitions

| Responsibility | Decision scope | Output | Boundary | Completion check |
| --- | --- | --- | --- | --- |
| SH-01 Task and stage router | Choose only task-relevant responsibilities. | A bounded composite-job assignment. | Does not force PA→UM→CM or create work not requested. | Assignment refers to actual task evidence. |
| SH-02 Scoped context builder | Select only allowed case-local and approved general content. | A version-linked request packet with explicit unknowns. | No other patient’s history, summaries or learned preferences. | Packet manifest records its namespace/source set. |
| SH-03 Reference retrieval service | Retrieve rather than invent policy/record evidence. | Relevant source spans with metadata and limits. | Search similarity is not truth, authority or patient identity. | Every item passes scope and source checks before injection. |
| SH-04 Evidence and contradiction ledger | Preserve provenance and version relationships. | Traceable evidence/claim links and unresolved conflicts. | A summary cannot silently become authoritative environment state. | Derived claims retain their original source references. |
| SH-05 Artifact renderer | Render the required representation. | Draft/final artifacts with author/source/status metadata. | Draft, finalized and delivered remain separate. | Output matches source/version/required contract. |
| SH-06 Operation gate and action journal | Enforce the actual execution/retry envelope. | Permitted dispatch and observed receipt/unknown state. | Valid model prose or JSON does not grant authority or exactly-once effects. | Action identity and outcome evidence are recorded. |
| SH-07 Budget and work scheduler | Admit work and account for combined resource spend. | Bounded execution/delegation plan. | Cannot fan out every micro-role or reuse another patient’s reasoning. | Queue, budget, cancellation and stop conditions are explicit. |
| SH-08 Case checkpoint and context reducer | Reduce context under the actual provider ownership contract. | Case-scoped checkpoint/projection with retained source references. | Does not promote patient facts into reusable staff knowledge or prove lossless semantics. | Active request, obligations, unknown effects and source versions survive or fail explicitly. |
| SH-09 Patient isolation barrier | Prevent patient-derived state crossing into another patient’s work. | Allowed case-local views or a denied/unresolved access. | Not satisfied by merely asking the model to ignore unrelated context. | Cross-patient source injection is rejected before inference/tool use. |
| SH-10 Bounded invariant critic | Challenge unsupported claims and missing obligations. | Specific evidence-based defects or readiness limits. | Not hidden verifier, external reviewer or unlimited debate loop. | Feedback cites the case-visible contradiction/requirement and stays within budget. |

## Complete declared actor catalogs

The following names are extracted from the pinned benchmark's **public MCP registration source**, without reading fixture/expectation/solution data. Provider allowlist: 30 methods. Default payer agent catalog: 41 methods. CM catalog: 16 methods.

These are catalog counts, not live per-task discovery counts or performance claims. Runtime filters can remove methods. The payer server also has a separate broader `full` profile; the table below documents its default agent profile. Our selected-domain namespace gate still applies after discovery. A method's presence does not establish that its preconditions are met.

### Provider PA

| Namespace | Declared operations |
| --- | --- |
| `auth` | `check_status`, `file_appeal`, `file_external_appeal`, `finalize_provider_determination`, `request_peer_to_peer`, `respond_to_peer_to_peer`, `respond_to_pend`, `submit_authorization` |
| `cases` | `create_from_order`, `get_case`, `list_cases` |
| `chart` | `get_patient_chart_by_patient`, `list_candidate_orders`, `search_patients` |
| `docs` | `create_submission_bundle`, `get_document`, `list_case_documents`, `upload_evidence`, `upload_evidence_file` |
| `forms` | `list_required_forms`, `save_form_response`, `validate_form` |
| `inbox` | `list_messages`, `read_message` |
| `p2p_session` | `get_context`, `send_turn`, `submit_summary` |
| `people` | `list_contacts`, `list_ordering_providers`, `list_reviewer_contacts` |

### Payer UM

| Namespace | Declared operations |
| --- | --- |
| `payer_intake_hub` | `list_intake_queue`, `get_intake_case`, `create_intake_case`, `save_auth_header`, `save_diagnoses`, `save_requesting_provider`, `add_line_item`, `update_line_item`, `remove_line_item`, `list_documents`, `confirm_decisions` |
| `triage` | `get`, `calculate_sla`, `check_gold_card`, `set_disposition`, `route_case` |
| `review` | `get_nurse_review_data`, `save_criteria_evaluation`, `submit_nurse_case_recommendation`, `get_md_review_data`, `save_md_review`, `submit_md_case_decision` |
| `determination` | `get_summary`, `finalize` |
| `p2p` | `list`, `offer_slots`, `schedule`, `record_outcome` |
| `p2p_session` | `get_context`, `send_turn`, `submit_summary` |
| `payer_letter_center` | `list`, `get`, `generate_approval`, `generate_partial_approval`, `generate_denial`, `generate_pend`, `generate_notification`, `deliver`, `reissue`, `audit_completeness` |

### Care management

| Namespace | Declared operations |
| --- | --- |
| `cm_intake` | `list_referral_queue`, `get_referral`, `open_case`, `disenroll_case` |
| `cm_chart` | `get_chart_data`, `submit_chart_review` |
| `cm_outreach` | `start_outreach_call`, `send_message`, `get_transcript`, `end_outreach_call` |
| `cm_assessment` | `start_assessment`, `save_section`, `complete_assessment` |
| `cm_care_plan` | `create_draft`, `save_care_plan`, `finalize` |

## All local case tools

| Tool | Connection and effect |
| --- | --- |
| `case.inspect_evidence` | Retrieves typed fields or exact list/text slices from the original successful source by JSON pointer; supports business and raw MCP representations. |
| `case.record_policy_decision` | Saves a source-backed policy assessment and intended operations. The live runner checks quotation provenance before policy-dependent effects; the model retains policy interpretation and decision responsibility. |
| `case.request_identity_reselection` | Requests a clean identity investigation after rejecting the current binding. Stops the current batch; retains audit/budgets and blocks automatic reset after external or uncertain writes. |
| `case.find_evidence` | Finds older current-case source IDs by tool name/ID with pagination. |
| `case.discover_tools` | Activates selected tools already allowed by the domain registry for presentation next turn; changes no environment permission. |
| `case.get_role` | Retrieves a complete domain/shared responsibility definition from the general catalog; does not invoke another model. |
| `case.add_obligation` | Adds a scoped unfinished requirement, optionally with dependencies on existing obligations. |
| `case.close_obligation` | Closes work only with same-case observed support and satisfied dependencies. |
| `case.defer_obligation` | Preserves outstanding external-document work at an accepted, verified information-gathering handoff; sends no message and does not close the work. |
| `case.read_evidence` | Reads a bounded range from an existing observation by original source ID; creates no new source fact. |
| `case.search_evidence` | Searches one successful observation and returns bounded excerpts/offsets; it does not search the entire outside world. |
| `case.request_helper` | Optional read-only analysis over selected current-case evidence; unavailable in combined mode. |

## All workspace tools

| Tool | Connection and effect |
| --- | --- |
| `workspace.read_file` | Bounded UTF-8 source excerpt with continuation metadata and file hash. |
| `workspace.search_files` | Bounded literal search within an approved case directory or exact reference root; not unrestricted host search. |
| `workspace.read_pdf` | Selected PDF text-layer pages using pypdf; no OCR or visual layout proof. |
| `workspace.list_files` | Lists accessible case/reference paths; does not create a document or attach it to a case. |
| `workspace.write_file` | Writes an explicitly authored artifact beneath the scoped writable root; does not make that file an independent source record or send it. |

## Judge tools are a separate tool set

`Read`, `Glob`, `Grep`, `Write`, and `Edit` belong to the alternate judge runner's confined evaluation workspace. They are not actor tools. In particular, judge `Write` creates evaluation material such as a verdict file; it cannot call `auth.submit_authorization` or change the actor world.

## Where to verify this reference

- [Responsibility definitions](../HealthHarnessCodex/health_harness_codex/data/micro_roles.json) and [prompt composition](../HealthHarnessCodex/health_harness_codex/roles.py).
- [Provider/default payer registration](../Runner/chi-bench/src/chi_bench/mcp/catalog.py), [payer profile choice](../Runner/chi-bench/src/chi_bench/mcp/payer_server.py), and [CM registration](../Runner/chi-bench/src/chi_bench/mcp/cm_server.py).
- [Local case tool definitions](../HealthHarnessCodex/health_harness_codex/engine.py) and [workspace tool definitions](../HealthHarnessCodex/health_harness_codex/docker_bridge.py).
- [Judge tool implementation](../HealthHarnessCodex/health_harness_codex/openrouter_batch.py) reused by [the synchronous judge runner](../HealthHarnessCodex/health_harness_codex/openrouter_judge.py).
