# Where chi-Bench fits in healthcare work

This is a study explanation, checked against public benchmark documentation, CMS, and AHRQ on October 17, 2026. It contains no protected handbook excerpts. Examples below are invented explanations, not benchmark solutions or clinical advice.

## Main classification

**Evidence caution:** this explanation is an interpretation of cited public material. Its substantive blocks now have explicit dispositions in the [defined assertion audit](HealthcareRoles/verification/README.md); invented examples and candidate mechanisms remain illustrations/hypotheses. The [evidence register](HealthcareRoles/EVIDENCE_REGISTER.md) records scope and unresolved local authority rather than certifying every possible case.

For the extensive real-world participant map, responsibilities and handoffs, see [WORKFLOW_PEOPLE.md](WORKFLOW_PEOPLE.md) and its [source ledger](Source/04-workflow-people-sources.md).

The closest description is **healthcare operations and care coordination, with policy-grounded clinical reasoning**. The benchmark covers work performed across a healthcare provider, an insurance payer, and a care-management team. Documentation is one output; operational decisions, communication, escalation, and changes to application records are also part of the work. This classification is an interpretation of the benchmark's published task descriptions.

The official three domains are provider prior authorization, payer utilization management, and care management, with 25 core public tasks each. Agents work through simulated applications using tools. Tasks have specified starting points and completion requirements; an individual task need not cover every stage of a patient's entire journey. See the [official domain descriptions](https://github.com/actava-ai/chi-bench#what-this-benchmark-measures) and [public task explorer](https://www.actava.ai/benchmarks/tasks).

## Provider side: arranging authorization for proposed care

Think of a clinic or hospital trying to obtain the required insurer authorization for a proposed service. Its authorization staff may gather existing records, check coverage, assemble a request, and handle requests for more evidence. Clinicians may contribute the medical justification and participate in escalation or appeals. The benchmark's provider tasks represent parts of this work.

For an invented example, a clinician recommends a procedure. The operational task becomes connecting the proposed procedure to the right patient's records, assembling the relevant evidence, submitting the required request, and recording or responding to its outcome. Writing a persuasive paragraph alone does not complete those steps.

CMS describes prior authorization as a process in which the provider submits a request and receives a decision before services are rendered. That general background explains the administrative purpose; the exact benchmark workflow follows its own task and policy materials. [CMS overview](https://www.cms.gov/data-research/monitoring-programs/medicare-fee-service-compliance-programs/prior-authorization-and-pre-claim-review-initiatives).

## Payer side: reviewing the request

The second domain represents the receiving insurance organization. The benchmark describes intake, checking policy, nurse and physician review, and issuing a determination. This is utilization management: reviewing whether a requested service meets the applicable requirements and routing the case through the appropriate review stages.

There is real reasoning in this category: identifying which evidence matters, noticing that a criterion is unsupported, and identifying when another review stage is needed. But the operational question is about a request under a particular policy, rather than an unrestricted attempt to diagnose a patient from scratch. CMS's coverage material helps distinguish coverage determinations from the treating clinician's broader clinical assessment. [CMS coverage background](https://www.cms.gov/medicare/coverage/determination-process).

## Care-management side: coordinating ongoing support

The third domain moves closer to patient communication and care coordination. The benchmark describes chart review, contact with a simulated patient, assessments, and preparation of a care plan. Real-world analogues include nurse case managers and care coordinators; actual staffing and responsibilities vary by organization.

An invented example is a patient who has difficulty following an existing care plan. A coordinator needs to learn what is preventing follow-through, record what the patient actually says, and organize appropriate support and follow-up. The central difficulty can involve missing information, communication, and continuity across records, as well as clinical knowledge.

AHRQ describes care coordination in terms of organizing care activities and sharing information. It identifies needs assessment, proactive care planning, monitoring, follow-up, and links to community resources as examples. These explain why this domain is broader than writing hospital notes. [AHRQ care coordination](https://www.ahrq.gov/ncepcr/care/coordination.html).

## Relationship to documentation and a doctor's reasoning

| Aspect | Relationship to these tasks |
| --- | --- |
| Documentation | Necessary evidence and outputs: requests, reviews, assessments, case notes, or plans, depending on the task |
| Clinical reasoning | Interpreting existing medical evidence and using it within the assigned role and policy |
| Operational execution | Using tools, updating records, communicating, routing/escalating cases, and satisfying task completion requirements |
| Diagnosis and treatment | Clinical context can be relevant, but this is not primarily a bedside diagnostic or treatment-selection benchmark |
| Organization | Spans providers, insurers, and care-management teams; it is broader than one hospital department |

For harness research, this suggests studying case-state tracking, evidence provenance, policy retrieval, unresolved requirements, communication state, and confirmation that intended actions were actually saved. These are candidate mechanisms, not a selected architecture or demonstrated improvements. A useful controlled comparison holds the model fixed and measures the effect of harness changes with comparable task and inference budgets.
