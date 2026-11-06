# Which healthcare functions should become agents?

Design study, October 18, 2026. [Decision records](DECISION_LOG.md) · [Role index](ROLE_ANALYSIS.md) · [Work packages](WORK_PACKAGES.md) · [Sources and limits](SOURCES.md). Authored inputs are in definitions.py, decision_basis.py and sources.json. Architecture preferences are provisional; no runtime or performance evaluation has been executed. Current structural/publication status is recorded in [verification](VERIFICATION.md).

## The research question

The useful question is: **what separation improves the work, and which separations preserve necessary accountability or information limits?** The earlier reference describes functions in healthcare organizations. It does not establish an efficient software organization. Ninety-seven profiles are not 97 unique people, and neither number implies 97 model workers. M28, for example, explicitly combines a hospice group and several distinct functions; P01 is a patient, M24 a physical transport worker, and G14 an access-administration function.

This study retains every function, but separates four design units: a real-world actor, a responsibility, a reusable capability and a running worker. A single person can hold several responsibilities; several people can hold the same profession; one capability can serve multiple workers. The correct runtime identity may depend on organization, case, task and permitted information—not only profession.

The provisional conclusion is to **test functional organization before treating every profession as an autonomous persona**. This is a hypothesis and experimental ordering, not a finding that a small team will win. The proposed 23 work packages are a navigable grouping of the 97 functions, not an optimized partition, institutional staffing chart or recommended agent count. See AD01, AD03, AD04 and AD16.

## Two systems with different objectives

| Design | What it controls | What success means | Main error to avoid |
| --- | --- | --- | --- |
| Healthcare ecosystem simulation | Separate synthetic parties, observations, local policies, incentives and interactions in a newly designed environment | Fidelity, plausible independent knowledge, correct authority boundaries and useful experimental behavior | Assuming realistic names or dialogue establish valid clinical/institutional behavior |
| Solver inside the supplied benchmark | Its permitted reasoning, memory, orchestration and tool calls; supplied services/counterparties remain outside its authorship | Complete assigned tasks through the actual tools and permitted observations | Generating its own patient agreement, outside review outcome or completed-service evidence |

Both are legitimate research directions, but they are different projects. A model patient could be a separate actor in our own simulator; the solver cannot use an internal patient agent’s fabricated response instead of the benchmark’s supplied interaction. A model judge might help a separate simulation study; it is not the actual court or official grader. Official documentation distinguishes the acting harness, conversation/service environment and grading components. [S06](https://www.actava.ai/benchmarks/docs/extending), [S09](https://github.com/actava-ai/chi-bench/tree/4444a07fa68a4f1623f841a292a54e284fc8e7f7/docs).

Following the clarification, the main subject here is **our agentic harness operating in χ-Bench**. The separate-simulator alternative is retained only to clarify the boundary; the user has not selected a replacement simulator. The paper explicitly motivates multi-role composition and evaluates harness/model combinations. That makes role organization a relevant research hypothesis, not a mandate to create a new harness or 97 agents. [S11](https://arxiv.org/abs/2605.16679v3).

The labels in the role profiles are conditional design defaults, **not verified assignments for every benchmark task**. If a task explicitly assigns the solver a review or documentation function, the solver may perform that simulated function through its permitted tools; we must not invent an extra real-person approval requirement merely because the analogous human job requires credentials. Conversely, a tool result or patient statement supplied by the environment cannot be replaced with an internal persona’s answer. Detailed public-task and tool mapping remains a separate unexecuted step before implementation.

## Define a role by its work and constraints

For a candidate worker, record these independently:

| Dimension | Question to answer | Why it changes the design |
| --- | --- | --- |
| Trigger | What actual case condition creates this work? | Prevents invoking all roles on every case |
| Objective | What bounded output must be produced? | Makes delegation and completion reviewable |
| Knowledge | What can the worker observe, and which facts are unknown? | Prevents invented source facts and unnecessary sharing |
| Expertise | Does it need a distinct interpretation or merely another title? | Distinguishes specialist reasoning from persona decoration |
| Permission | Which tools/operations are actually allowed for this task? | Role text alone does not enforce authority |
| Responsibility | Who owns the next action and unresolved obligations? | Prevents gaps after a handoff |
| State ownership | Which record can it propose, write or finalize? | Makes conflicts and retries manageable |
| Independence | Is separation an actual institutional requirement or only a software error check? | Avoids false claims about independence |
| Interface | Which input/output fields and source references must survive? | Reduces ambiguity at merge/split boundaries |
| Timing | Does work need parallelism, an external wait, or ordered actions? | Sequential dependencies can make many agents expensive |
| Stop condition | What observation establishes done, blocked or clarification needed? | Avoids endless committees and premature completion |
| Measurement | Which failure should separation fix, and what would disprove the benefit? | Prevents selecting an organization by appearance |

These are proposed engineering criteria, not empirically calibrated weights. Do not sum arbitrary scores and call the result an optimal team. Existing dependency arrows identify possible context/service relationships; they are not measured frequencies, workload weights or independent observations. See AD12.

## When a function deserves separation

Separation can be justified by a distinct knowledge view, genuinely different specialized work, a sustained independent subtask, required accountability, incompatible objectives, separate organization, or enforceable tool isolation. These are reasons to examine separation, not automatic proof that another autonomous process is required.

Different kinds of separation can solve different problems. A new context can limit irrelevant material; a scoped adapter can limit operations; an external interface preserves a real counterparty; an independent institution supplies a real review decision. One does not substitute for the others. Two worker prompts in one unrestricted environment are not necessarily isolated. Conversely, one application can preserve several operation-level scopes without pretending they are the same authority. See AD05–AD08.

A particularly consequential example is MA reconsideration. The cited rule addresses actual uninvolved persons and physician expertise for the specified medical-necessity issue. A new model call is an optional internal critic, not proof of compliance with that human institutional requirement. Software independence, factual independence and legal/institutional independence need separate evidence. [S07](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590). Whether a benchmark task assigns an abstract review function is determined by its actual instructions/tools; do not add real-world staffing steps that the simulated workflow does not require.

## When several functions can share a job

Provider registration, benefits checking, packet assembly, tracking and scheduling are plausible functions for one provider workflow owner with explicit modes. Care outreach, navigation, general education support and follow-up may similarly share a case owner. Payer intake, administrative eligibility and status communication can share state while respecting delegated decision scope. These are W05, W13 and W08 respectively.

The rationale is continuity: identifiers, evidence versions, outstanding requests and the next observable action can remain in one maintained case record. The risk is silent authority/state collapse. A combined worker must retain distinctions such as benefit fact versus authorization, authorization versus payment, request versus receipt, referral versus acceptance, scheduled versus delivered, and clinical suggestion versus authorized decision.

Merger is therefore conditional: same relevant task principal and permitted purpose; compatible data access; explicit operations; retained author/decision identity; manageable context/workload; and complete output obligations. Combining software functions never establishes that a real employee is licensed, privileged or delegated to perform all of them. The detailed healthcare audit remains the source for those unresolved facts.

Some source examples support combined human assignments, but actual institutional patterns differ. The new grouping extends that context into a design proposal; it does not claim the source institution deploys this AI architecture. For every package, WORK_PACKAGES.md states a split trigger and retained boundary rather than a blanket safe-to-merge verdict.

## Make a unique worker useful rather than theatrical

A useful clinical-evidence worker might receive a bounded question, the permitted chart view and relevant policy excerpts; return supported facts, missing evidence and contradictions; and lack case-finalization tools. A notice capability might render an already authorized determination and verify the recipient/status, with no ability to change the outcome. A conversation owner might preserve speaker attribution, asked questions, actual answers and explicit refusals.

These examples are conceptual contracts. We have not implemented tools or verified their runtime enforceability. Specialized vocabulary, a biography, a professional title or a simulated personality alone does not establish expertise, accuracy or permission. For an ecosystem simulator, individual goals, uncertainty and information asymmetry may be important experimental variables; they should be specified and evaluated separately from solver performance.

Persistent identity is justified only if continuity across that worker’s work matters. Otherwise, a capability call or fresh specialist context may suffice. Also consider the reverse failure: pooling unrelated cases into one persistent persona can leak facts or preferences across patients. Case identifiers, scope and evidence references must accompany any reuse.

## Keep one accountable owner without inventing a universal boss

The first proposed solver design has one owner for mutable case actions, with helpers proposing findings rather than silently writing competing outcomes. This is an engineering hypothesis to simplify state changes, retries and conflict handling. It is not an organizational claim that all real care has one global manager or one record writer. A richer multiwriter design remains an alternative if the actual tool semantics support transactional or disjoint writes and measurement justifies it.

The coordinator owns workflow continuity, not every substantive authority. It can route to an authorized function, preserve disagreement and track an external response. It cannot manufacture missing consent, clinical expertise, policy approval, external review or service fulfillment because it is called a director.

When helpers disagree, preserve sources, versions, missing facts and the contested criterion. Use the applicable policy/authority or clarification pathway. A majority vote may be studied as a bounded reasoning technique; it does not turn unsupported opinions into an institutional decision. A failed review loop needs a declared stop condition, not indefinite discussion. See AD07 and AD10.

## Information flow needs more than a summary

A proposed handoff includes case identity, task/stage, evidence/source versions, objective, allowed operations, requested output, unresolved questions, deadline/budget and a clear recipient. The result distinguishes facts, interpretations, proposals and observed tool outcomes. The receiver acknowledges what was accepted and which obligation remains with whom.

AHRQ describes accountability and acknowledgement as important in human handoffs and separately describes closed-loop feedback. Those ideas motivate the design; they do not prove the exact software fields are mandatory or that a worker message transfers a professional license. [S05](https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/handoff.html), [S10](https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/loop.html).

Shared memory can reduce copying but cannot make every reader entitled to every record. Proposed worker views should follow the actual task/purpose and restrictions. HHS guidance has explicit exceptions; the earlier Part 2 review also prevents reducing privacy to one simplistic rule. No general legal claim that every treatment exchange requires authorization or that all treatment-related sharing is unrestricted is made here. [S08](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html).

## What the multi-agent literature does and does not establish

Engineering guidance describes workflows, routing and workers as alternatives; a vendor’s research-system account reports gains on parallel research while warning about resources and coordination. These support investigating bounded separation, not importing a fixed agent count or token multiplier. [S01](https://www.anthropic.com/engineering/building-effective-agents), [S02](https://www.anthropic.com/engineering/multi-agent-research-system).

The scaling paper compares several architectures across six other agentic benchmarks and finds task-dependent outcomes. Its robustness and limitations sections constrain how strongly to generalize; no chi-Bench result or universally useful team size follows. The MAST study provides failure categories spanning design, alignment and verification, with methodology and task-domain limits. Our stress cases borrow the diagnostic idea; we have not measured those failure rates here. [S03](https://arxiv.org/html/2512.08296v3), [S04](https://arxiv.org/html/2503.13657v3).

The current literature therefore makes a comparison necessary, not redundant. Extra workers can add context capacity, compute, retrieval and clearer instructions simultaneously. A win without those controls would not isolate the value of organizational separation.

## Architecture alternatives to compare

| Variant | Organization | What it tests | Key risk |
| --- | --- | --- | --- |
| V0 | Existing strong permitted harness | Reference performance and cost | Weak baseline can exaggerate proposed gains |
| V1 | One worker with explicit role/function modes | Value of domain instructions and tracked obligations | Context interference and self-check blind spots |
| V2 | Same owner plus on-demand bounded read-only specialists | Additional context/specialization beyond V1 | Extra tokens and stale/incomplete handoffs |
| V3 | Persistent task-relevant role workers | Value of sustained separation/identity | Coordination overhead, duplicate work and conflicting writes |
| V4 | Independently scoped ecosystem actors in a separate simulator | Fidelity and information/authority asymmetry | Conflating a new simulator with the supplied benchmark |

The useful first comparison is V1 against V2, alongside V0; V3 remains a serious alternative rather than an assumed mistake. Persona richness should be an orthogonal ablation. V4 needs a separate objective and environment, so it should not be mixed into the official solver experiment. None of these variants has been implemented or run in this phase.

## Current conclusion and what would change it

Preserve the 97-function knowledge base, but compose execution according to task demand and actual permission. Start experimental design with one accountable case owner, explicit role modes, and separately test bounded specialist contexts. Preserve patient/counterparty identity, independent review, policy approval, information restrictions and physical fulfillment as real boundaries in the model.

This proposed conclusion would change if task mapping exposes sustained independent work or enforceable information/authority separation that a merged owner cannot support, or if controlled trials show persistent role workers produce better complete-task outcomes at an acceptable resource cost. The decision records state reconsideration conditions. Completion of the documented design study must remain separate from empirical architecture selection and detailed public-task/tool mapping, which have not been executed. The [verification receipt](VERIFICATION.md) records what was actually published and checked.
