# Glossary: healthcare, benchmark and harness terms

This glossary explains the terms used in this project's guides and code. It
describes the benchmark and our implementation, rather than establishing a
universal hospital organization chart or legal decision authority. Actual duties
and permitted decisions depend on the assigned task and organization.

Start with the first section, then use these as lookup references:

- [The terms most easily confused](#1-the-terms-most-easily-confused)
- [Healthcare workflows and people](#2-healthcare-workflows-and-people)
- [Records and workflow states](#3-records-and-workflow-states)
- [Benchmark execution](#4-benchmark-execution)
- [Harness components and tools](#5-harness-components-and-tools)
- [Identity and evidence](#6-identity-and-evidence)
- [Memory, context and token usage](#7-memory-context-and-token-usage)
- [Evaluation and results](#8-evaluation-and-results)
- [Files and technical notation](#9-files-and-technical-notation)

## 1. The terms most easily confused

### Provider, payer and model provider

**Healthcare provider:** the clinician or organization requesting/providing a
healthcare service. In a provider PA task, this is the requesting side of the
authorization workflow. It is not the AI company.

**Payer:** the organization responsible for the coverage/authorization review
represented in the task. It is the reviewing side of the provider–payer
relationship. The task determines the institutional arrangement; the term does
not imply every decision is personally made by an insurance-company doctor.

**Model provider:** the service supplying AI inference. In code,
`codex_provider.py` is an adapter to Codex model inference, not a healthcare
provider. OpenRouter is the API routing service used for the configured judge;
it is not the payer.

### What “provider actor” actually means

An **actor** is the participant whose permitted work is being performed in the
benchmark. A **provider actor** is the participant acting on the requesting
healthcare provider's side, using the provider-side tools. It does **not** mean
one specific doctor, the AI vendor, or the patient.

In our normal runner, one model-driven **case owner** performs that actor's
assigned work. It may cover several administrative responsibilities through
multiple model calls. Python executes its allowed tool proposals.

| Phrase | Read it as |
| --- | --- |
| Provider actor | The participant doing the requesting provider's assigned work |
| Payer actor / UM actor | The participant doing the payer's assigned utilization-review work |
| CM actor | The participant doing the assigned care-management work |
| Actor-visible data | Information that participant can obtain through its allowed inputs and tools |
| Actor tool | An operation available to that participant, such as reading a case or submitting a request |
| Actor port / actor surface | The software endpoint exposing that participant's tools; not a physical hospital department |
| Actor model | The AI model reasoning about the assigned work |
| Model provider | The software service supplying AI inference |

### Actor, agent, role and person

| Term | Meaning here | What it does not establish |
| --- | --- | --- |
| Person / staff member | A real human professional in an organization | That the code launches a matching independent worker |
| Responsibility / micro-role | A named set of duties and boundaries in our instructions | A separate agent, conversation, license or institutional authority |
| Agent | Model reasoning connected to instructions, state and an execution loop | A real person or permission to perform every duty |
| Combined owner / case owner | The logical agent responsible for progressing one case in the normal runner | A hospital executive who can override clinical or payer decisions |
| Helper | An optional model call analyzing selected evidence under one responsibility definition | An independent witness or authority to execute actor tools |
| Simulator / counterparty | The benchmark participant responding as the patient or other side of a discussion | A helper secretly supplying the owner's answers |
| Judge | A separate evaluator assessing the recorded outcome | A worker who repairs the case |

There are **66 responsibility definitions**, not 66 independently running staff
agents. The normal runner uses one combined owner per case. Three concurrent
cases mean three separate attempts, not three specialists sharing one patient.

For example, **“the provider actor submitted the packet”** should mean: the
owner proposed the permitted submission operation, the dispatcher executed it,
and the benchmark returned/stored submission evidence. The owner's final
sentence alone cannot establish that it happened.

## 2. Healthcare workflows and people

| Term | Plain meaning in this project |
| --- | --- |
| PA — prior authorization | The workflow for determining whether a proposed service requires authorization and preparing/requesting it when appropriate. Provider PA is the requesting side; it does not itself confer payer approval. |
| UM — utilization management | The payer-side workflow represented by `pa_um`: intake, routing, assessment and an assigned determination/communication stage. The task may start partway through it. |
| CM — care management | Coordination of a person's needs, engagement, assessment, goals and care plan. In these guides CM means care management, not context management. |
| Domain | One category of benchmark work: provider PA, payer UM or CM. It is not a website domain. |
| Ordering practitioner / ordering provider | The clinician identified as requesting the service. A directory record and the task's evidence establish the relevant identity. |
| Requesting provider | The provider asking for authorization. May refer to a clinician or organization; the actual record determines which. |
| Member | The person described from the health-plan side. Commonly the patient in the case, but identifiers must be verified rather than assumed interchangeable. |
| Care manager / coordinator | The function conducting assigned coordination work. The title alone does not prove a particular license or prescribing authority. |
| Nurse reviewer | The review function recording criteria assessments/recommendations where assigned. A recommendation and a final determination are separate records. |
| Physician reviewer / MD reviewer | The physician-level review function represented in the task. MD means medical doctor; a simulated role title does not create real-world licensure. |
| Intake | Receiving, identifying and organizing a request or referral before later work. |
| Triage / routing / review lane | Choosing the next permitted review stage or owner. Here this is a workflow decision, not automatically emergency medical triage or a treatment decision. |
| Coverage / benefit / eligibility | Administrative information about the represented plan and person. Its presence alone does not prove authorization, medical necessity or payment. |
| Medical necessity | Whether the requested service meets the applicable clinical requirements in the represented review. A plausible clinical story alone does not establish that those requirements are met. |
| Policy / criteria | The applicable source rules and individual review requirements. “Policy” can also mean a software restriction elsewhere; specify which kind. |
| P2P — peer-to-peer | A clinician-to-clinician discussion in the review workflow, where assigned. It is not computer peer-to-peer networking or automatically an appeal. |
| RFI — request for information | A request for specific missing/additional material. It is not approval or denial by itself. |
| Appeal / reconsideration | A review route for an earlier decision. Not interchangeable with every correction, grievance or P2P conversation; the task defines the route. |
| Outreach | Contacting the patient or another permitted participant through the available workflow. |
| Consent | The agreement required by the assigned workflow. A completed form or staff assumption cannot replace the required actual interaction. |
| Assessment | A structured account of needs and relevant findings based on permitted sources. |
| Care plan | Documented goals, actions, responsibilities and follow-up. Writing a plan does not prove its actions happened. |
| Intervention | An action proposed/recorded in a care plan to address a need. Actual performance requires separate evidence. |
| Referral | A request directing a person/service need to another function. In provider PA it may initiate authorization work; in CM it may initiate coordination. |
| Handoff | Passing work and relevant information to the next responsible function. Sending and receiving acknowledgment are separate events. |
| Effectuation | Implementing the consequences of a decision, such as updating applicable authorization records. A favorable decision is not automatically its implementation. |
| SLA / timeliness | SLA means service-level agreement: an expected operational turnaround or response commitment. The task/policy determines the applicable deadline; the acronym implies no universal time limit. |
| BH / psychosocial / social needs | BH means behavioral health; the other terms concern relevant personal/social circumstances and barriers. These labels do not independently establish a diagnosis. |

## 3. Records and workflow states

| Term | Plain meaning in this project |
| --- | --- |
| Chart | The patient record available through allowed chart tools. A read is limited to what the operation actually returns. |
| Order / ServiceRequest | A record describing the requested clinical service, separate from the administrative authorization case. An existing order is not required for every supported case-creation route. |
| Case / work item | The record grouping assigned work for a person/request. Patient ID and case ID are not synonyms. |
| PriorAuthCase / PA case | The authorization workflow record linked to the patient and service request. |
| Case line / line item | One requested item within a case. A case summary does not necessarily capture every item's outcome. |
| CMReferral / CMCase / CMAssessment | Separate records for referral, the CM workflow episode and structured assessment, linked to keep information in the correct episode. |
| Form / questionnaire response | Structured answers linked to the required case/form. Filled fields still need appropriate evidence and validation. |
| Artifact / document | A file or saved work product. Existence on disk does not mean attached, sent, accepted or graded. |
| Bundle / draft packet | A prepared collection of material. Preparation is distinct from submission. |
| SubmissionPacket | The benchmark's persisted healthcare submission record. Different from our competition submission folder. |
| Provider determination / disposition | The provider-side decision about proceeding, such as submitting or gathering information. Not a payer coverage determination. |
| Payer determination | The decision made through the assigned payer review workflow. A draft/recommendation may precede finalization. |
| Finalize / commit | Making a particular record/state final. Finalizing one record does not finish every downstream obligation. |
| Notice / letter | Correspondence about an outcome or information request. Generated, finalized, sent and delivered are distinct claims. |
| Receipt | Recorded acknowledgment/outcome of an operation. Transmission does not necessarily establish delivery or acceptance. |
| Readback | Reading the environment after an operation to confirm its resulting state. Fresh readback means a later actual read, not reopening an old answer. |
| Milestone / endpoint / terminal state | An intermediate event / the assigned stopping target / an accepted endpoint for that task and branch. There is no universal endpoint for every healthcare task. |

Read each status with the **record and workflow branch** it belongs to:

| Status or phrase | What it supports | What it does not support by itself |
| --- | --- | --- |
| `draft` | A record is being prepared | Submitted, approved or task complete |
| `docs_needed` | A recorded evidence/document need | That the task is unsolvable or that this is an acceptable final endpoint |
| `ready_to_submit` | Preparation reached readiness | Actual submission |
| `submitted` | The submission stage occurred as represented | Payer approval or payment |
| Approved | A particular decision is favorable | Every notice delivered or service performed |
| Local `complete` | Our completion logic accepted its observed endpoint | Official benchmark success |
| `unresolved` | The harness did not establish its required endpoint | A proven dataset defect or impossible task |

## 4. Benchmark execution

| Term | Plain meaning in this project |
| --- | --- |
| χ-Bench / chi-bench | The benchmark providing tasks, simulated services and evaluation machinery. Not the agent we are building. χ is the Greek letter chi. |
| Dataset / core tasks | Supplied task material. Our current core selection has 25 tasks per domain, 75 total. An attempt executes one task. |
| Public instruction | The description available to the actor, as distinct from hidden evaluation material. “Public” here does not authorize publishing protected reference content. |
| Handbook | Approved reference material available through its allowed path. Separate from our shareable explanation documents. |
| World / environment | The benchmark records, services and conversation state in which an attempt operates. World state is the actual records, not the model's belief about them. |
| Fresh world / fresh attempt | A newly initialized supplied environment for a new execution, rather than continuing the previous mutated world. |
| Run | An ambiguous execution label. Reports should specify a task attempt or a 75-task batch. |
| Batch / suite | A selected collection of attempts/tests. A software test suite checks code mechanics; a dataset batch performs benchmark tasks. |
| Concurrency | Independent attempts running at once, not staff roles collaborating on one case. |
| Preflight | Checks before later work, such as validating the executable or waiting for tools. Passing preflight does not mean clinical work has passed. |
| Bootstrap / setup | Establishing runtime, tools, identities and starting context. |
| Simulator backend | The connection supplying counterparty replies when a task needs patient/P2P conversation. Separate from actor and judge connections. |
| Snapshot / exported state | Saved world state and required evidence for later evaluation, not merely the owner's final answer. |
| Deferred grading | Saving execution evidence first and evaluating later. No final score exists yet. |
| Resume / retry / replay | Continue eligible saved progress / start another attempt / reuse recorded inputs or actions. They have different safety and measurement implications. |
| Frozen configuration / provenance | The recorded source, binary hash, task, model and settings identifying an experiment. Changed inputs can invalidate a resume/comparison. |

## 5. Harness components and tools

| Term | Plain meaning in this project |
| --- | --- |
| Agentic harness | Software supplying instructions/state, calling the model, executing permitted proposals and checking progress. More than selecting a strong model. |
| Runner | Code managing executions. Root `Runner/` holds benchmark/tooling assets; `HealthHarnessCodex/` holds our Codex-connected harness. Neither is the dataset folder. |
| Controller / engine | Python code owning the reasoning–proposal–execution loop and its limits. |
| Dispatcher | Code validating a tool proposal and invoking the allowed operation. Proposal is not execution. |
| Tool / operation | A callable capability, such as reading a chart or submitting authorization. One model reply can propose several operations. |
| Tool schema | Argument names, types and requirements. It defines how to call an operation, not clinical correctness. |
| Tool catalog / registry | Operations known for a participant. The model may see a stage-relevant subset plus discovery. |
| Discovery / activation | Finding permitted operations / exposing their schemas in context. Activation does not grant permission outside the registry. |
| MCP — Model Context Protocol | The software protocol exposing benchmark tools/results here. Not another model or medical record. |
| Namespace | A grouping of names/identities. `auth` groups operations; a patient namespace separates case data. The purpose depends on context. |
| Canonical name / alias | The standard operation name / an alternate exposed name mapped to it. An alias does not create a new operation. |
| Bridge / adapter / backend | Carries requests between components / translates interfaces / supplies the selected implementation behind an interface. |
| `CodexSessionModel` / App Server | Our model adapter / the Codex process interface it uses. It does not attach the actor to this desktop chat's conversation. |
| Logical model call / turn | One harness request for a model reply. It can involve multiple native inference passes and is not one healthcare action. |
| Guard / gate | A code check permitting/blocking an action or completion claim. The local gate is not the official evaluator. |
| Completion contract | Our rules for evidence needed to accept the assigned endpoint, distinguishing preparation from actual effects. |
| Obligation / deferred work | Required unfinished work tracked in the case ledger, not an independently running worker. |
| Action journal / idempotency | The journal records attempted actions/outcomes; idempotency handling avoids repeated intended effects where supported. Not every external retry is harmless. |
| Reconciliation / unknown outcome | Investigating what happened when an operation's result is uncertain. A timeout does not prove a write failed; blindly repeating it may duplicate effects. |
| Workspace | Approved case/reference files and directories, separate from arbitrary host filesystem access. |
| Read / write / side effect | A read obtains information; a write changes a record/artifact; a side effect is a change outside the model reply, such as submitting a request. A tool's read classification does not prove its implementation is infallible. |
| Tool-free / read-only helper | Tool-free means the model receives no executable tools. Our helper analyzes supplied evidence; it does not independently read arbitrary records or modify them. |
| Structured output / envelope | A model reply constrained to defined fields, such as proposed calls and a final message. Valid formatting does not prove the proposed work is correct. |

## 6. Identity and evidence

| Term | Plain meaning in this project |
| --- | --- |
| ID / identifier | A value identifying a record. `patient_id`, `case_id`, `service_request_id` and `document_id` identify different things. |
| Principal / organization | The acting identity and organizational context represented by the harness. |
| Scope / case isolation | The boundary combining environment, task, organization, principal, patient and case identities. Another case's information must not become this case's evidence. |
| Identity reconsideration / context reset | A model-requested clean investigation after rejecting its patient/case selection. Old working information is quarantined, not carried into the new patient context; budgets and audit persist. Existing external effects require reconciliation. |
| Binding / identity resolution | Linking bookkeeping to an identity actually observed through trusted tools. A guessed ID or similar name is insufficient. |
| Evidence / observation | Information returned by a tool/permitted source. It does not guarantee source accuracy or that an inferred conclusion follows. |
| Evidence ID / source locator / citation | Reference to a saved observation / position inside a source / reference supporting a claim. Valid citations alone do not prove task completion. |
| Grounding / attribution | Linking a claim to its source and speaker/author while separating interpretation from observed fact. |
| Raw evidence / working view | The full saved response / the representation shown to the model. A full response does not include data/pages the tool never returned. |
| Historical observation / fresh evidence | A saved earlier result / a new environment observation. Reopening an old result does not refresh its state. |
| `structuredContent` / structured result | Machine-readable tool fields. Some MCP replies repeat the same information as text; exact duplicate presentation can be removed while preserving the original. |
| JSON pointer | A field locator such as `/case/status`, allowing precise retrieval from nested data. |
| Hidden fixture / expected answer | Material withheld from the actor for evaluation. Only the isolated evaluator should consume it; it is not an actor retrieval source or solving shortcut. |

## 7. Memory, context and token usage

| Term | Plain meaning in this project |
| --- | --- |
| Durable case memory / CaseStore | Saved SQLite case state: observations, messages, bindings, obligations, counters and journal. Saved does not mean all of it is sent next turn. |
| Context / prompt | Instructions, task, tools and selected history/evidence supplied for a model call. Judge calls have separate context. |
| Working set / projection | The bounded representation selected for the model now. This is our harness design, not a χ-Bench requirement. |
| Context window / context budget | Model/runtime capacity / our local selection limit. Character limits are not native token limits. |
| Context bloat | Repeated, duplicated or poorly selected input consuming space/tokens without proportionate usefulness. Smaller context must still retain what correct execution needs. |
| Compaction / truncation | Reducing/reorganizing context / cutting content. Both can lose needed information without proper retention and retrieval. |
| Retrieval / rehydration | Finding relevant stored material / reopening detailed content while preserving scope and source identity. |
| Retention window / inspected-field cache | Keeping recent turns / retaining exact already-read fields in a bounded case cache. Historical cached content is not fresh readback proof. |
| Token | A model encoding/accounting unit, not reliably a word or a fixed character count. |
| Input / output tokens | Material processed / tokens generated. Repeated input can dominate cost despite short answers. |
| Cached input / cache hit | Input the model service reports as reused. Different from our SQLite/evidence cache, which does not guarantee provider caching. |
| Reasoning tokens | Internal model reasoning usage when reported, not a visible explanation or clinical record. |
| Native inference pass | A processing pass inside Codex. One logical call can have multiple passes, so call count alone does not establish total input usage. |
| Payload / serialization / telemetry | Data sent / encoding that data for transport / recording execution and usage. Measurement boundaries affect reported sizes. |
| OCR — optical character recognition | Extracting text from image pixels. Reading a PDF's existing text layer is different; our verified PDF path uses text extraction, not DeepSeek OCR. |

## 8. Evaluation and results

| Term | Plain meaning in this project |
| --- | --- |
| Verifier | Benchmark code applying checks to the recorded world/evidence. Some checks invoke a semantic judge. |
| Deterministic check | A code-based check, such as resulting status or presence of a record. Does not itself need a model judgment. |
| Semantic judge / rubric | Model evaluator assessing meaning/quality / the specified criteria. Separate from the actor performing the task. |
| Verdict | A check's recorded outcome, with explanations/references where required. A local completion flag is not an official verdict. |
| Scorecard / strict score | Recorded check results / task-level result under the strict aggregation rule. Many passed checks can still accompany a failed strict score. |
| Not applicable / N/A | Normally the check's condition does not apply under the verifier's rules. Inspect its reason: some official degraded-judge paths also use this marker for unevaluated semantic checks. Our grading layer rejects those degraded evaluations as valid scored results. N/A alone does not establish why a check was excluded. |
| Ungraded / deferred-ready | No final evaluation yet / saved evidence eligible for later grading under recorded checks. Neither establishes success. |
| Successful benchmark run | Requires actual strict-score evidence, evaluated scope and failed/unmeasured checks stated. Process exit, saved packet and local completion are different claims. |
| Partial diagnostic | A limited evaluation, such as deterministic checks with semantic judging disabled. Useful debugging evidence, not a full verdict. |
| Software regression test | Automated code-behavior check. Passing does not establish AI performance on real tasks. |
| Development regression | A change making observed behavior worse. A smaller prompt is still a regression if needed evidence is lost. |
| Baseline / comparison | Reference implementation/run / later measured result. Model, CLI, settings and assisted retries limit causal conclusions when changed. |
| pass@1 / pass@3 / pass^3 | Single-attempt success / at least one success in three attempts / success in all three. State the task scope and complete graded attempts used. Assisted revisions are not interchangeable reliability trials. |
| Cost estimate / actual spend / cap | Forecast / recorded billed usage / authorized spending ceiling. An estimate is not a guaranteed charge; optimization does not refund earlier spending. |
| Competition submission packet | Packaged run evidence/results for the competition, separate from the healthcare `SubmissionPacket` inside a case. |

For example, a conditional appeal check can be legitimately inapplicable when
the assigned path contains no appeal. A semantic check omitted because a judge
was unavailable is an evaluation limitation. Both can appear as N/A in some
verifier paths, so the reason and judge-availability metadata matter. Neither
should be silently described as a passed check.

## 9. Files and technical notation

| Term | Plain meaning in this project |
| --- | --- |
| API / endpoint | Application programming interface / exposed address or operation. “Endpoint” can also mean a workflow stopping target; context matters. |
| HTTP / POST | The web request protocol / a request method used to send data to an API operation. A successful network response does not necessarily mean the requested clinical workflow reached its endpoint. |
| PDF / UTF-8 | A document format / a text encoding. A PDF can contain actual text, scanned page images, or both; its extension alone does not tell us whether OCR is needed. |
| Diagram LR / TD / TB | Mermaid layout directions: left-to-right / top-down / top-to-bottom. These control the drawing, not workflow permissions or priority. |
| Docker / container / image | Runtime system / isolated instance / template used to create it. A new container can initialize a new world rather than continue an old one. |
| CLI / executable | Command-line interface / program file. Updates can replace a version-specific installation directory. |
| SHA-256 / fingerprint / integrity check | Content-derived identifier / recorded identifier / checking for changes. Matching hashes establish byte identity, not clinical correctness. |
| Manifest | File listing tasks, frozen configuration, attempt states and artifact references. |
| SQLite / JSON / JSONL / Markdown | Local database / structured data / one JSON record per line / this guide's readable document format. |
| Mermaid | Text notation for diagrams. Rendering a diagram does not execute the harness. |
| `pa_provider` / `pa_um` / `cm` | Runner labels corresponding to dataset folders `prior_auth_provider`, `prior_auth_um` and `care_management`. |
| `run.result.json` / `evaluation.json` | Local execution result / harness telemetry and observations. Neither filename establishes an official scorecard. |
| `scope_key` / internal case subject | Harness bookkeeping identity, not necessarily the actual benchmark `case_id` observed after creation. |
| `auth.submit_authorization` | Namespace `auth`, method `submit_authorization`. The name identifies an operation, not proof it ran. |

## Where these definitions come from

This is a reading aid checked against the existing guides and implementation.
It introduces no new clinical guidance or claim that each responsibility maps
to a separate real employee.

- [Dataset workflows](01_DATASET_WORKFLOWS.md): records and actor viewpoints.
- [Implemented harness](02_IMPLEMENTED_HARNESS.md): execution, memory,
  model participants, permissions and output boundaries.
- [Responsibility/tool reference](03_ROLE_AND_TOOL_REFERENCE.md): named duties.
- [Judge analysis](05_JUDGE_CONTEXT_ANALYSIS.md): separate judge measurements.
- Implementation: [domain profiles](../HealthHarnessCodex/health_harness_codex/domain_profiles.py),
  [controller](../HealthHarnessCodex/health_harness_codex/engine.py),
  [working context](../HealthHarnessCodex/health_harness_codex/working_set.py),
  [batch results](../HealthHarnessCodex/health_harness_codex/batch.py).
