# Why χ-Bench exists, and what the competition is trying to achieve

Updated October 15, 2026. Read this as a connected introduction before the paper. The earlier approach ideas remain proposals; we are still building background understanding.

## 1. Begin with the work that has to happen around a patient

Imagine a clinician requests a service for a patient. The clinical recommendation starts a process: someone must establish whether the patient's health plan covers the service, collect the necessary supporting records, and send a request that the insurer can review. The clinician or organization requesting care is the **provider**; the organization administering coverage is the **payer**.

For services requiring **prior authorization**, the provider seeks the payer's approval in advance. The AMA describes how this process can create administrative work and delays in access to care. That is the practical motivation for studying automation here: time and attention are spent moving information and decisions through an operational process. [AMA background](https://www.ama-assn.org/practice-management/prior-authorization/prior-authorization-research-reports)

Stay with the same imaginary case. The request reaches the payer, but the supporting record is incomplete. The reviewer asks for more information. The provider must understand what is missing, obtain it, update the request, and respond through the correct channel. The payer then needs to apply the relevant policy, obtain whichever reviews are required, record a determination, and communicate it. Each action affects what someone else can do next.

This example is deliberately simplified and is not taken from a scored task. Its purpose is to show why a case is a chain of dependent work. A useful explanation of the patient's situation is one contribution to that chain; the request still has to move through the actual records and applications.

χ-Bench studies this kind of work from three positions. Provider Prior Authorization follows preparation and handling of the request. Payer Utilization Management follows the review and determination. Care Management follows a different coordination process: reviewing a chart, reaching a patient, carrying out assessments, and developing a care plan. The three domains are connected by their dependence on information, decisions, communication, and recorded actions. [Official domain descriptions](https://github.com/actava-ai/chi-bench)

Care management broadens the question beyond a provider-payer exchange. A patient may have concerns, practical barriers, or incomplete information that a chart does not reveal. Real care coordination involves goals, follow-up, and collaboration across services; CMS's chronic-care description provides an example of this broader setting. Its specific Medicare requirements should be studied separately from the benchmark's own task rules. [CMS background](https://www.cms.gov/medicare/payment/fee-schedules/physician-fee-schedule/chronic-care-management-complex-conditions)

## 2. Turn that operational problem into a research question

A language model can help interpret a document or draft a response. Giving it responsibility for a case introduces another requirement: it must decide what to do next as information arrives, use the relevant tools, and keep track of the consequences of its actions.

For our imaginary request, knowing that more evidence is needed does not finish the work. The system must find the right record, obtain the missing information through a permitted action, attach it to the correct case, and continue from the updated state. It must remember which parts remain unresolved after every change. This is what makes the task **long-horizon**: later actions depend on decisions and observations made earlier.

The paper asks whether current agents can sustain that responsibility. Its three central challenges are dense policies, changes of role with handoffs, and conversations with other actors. Together they make a case difficult even when the individual tools are straightforward. Some handoffs commit work irreversibly, raising the consequence of a mistake before submission. [Paper v3, introduction](https://arxiv.org/html/2605.16679v3)

Consider how those pressures interact. A policy can require several conditions, with an exception that applies only to a particular situation. The agent must establish the facts before choosing a path. Another role may then receive the agent's submitted work and make a decision from it. A conversation can introduce new information that changes the evidence. The agent has to bring that information back into the case rather than leave it in the dialog.

This explains the research interest in healthcare administration. It provides a setting where policy interpretation, information gathering, conversation, and execution have to work together. Our reading of the paper's larger question is whether an agent can maintain that coordination consistently across a complete workflow.

## 3. Build a world in which that question can be tested

To compare agents, researchers need cases that can be attempted repeatedly under controlled conditions. **χ-World** supplies the simulated environment; **χ-Bench** supplies the task and evaluation framework built around it. The IEEE challenge description lists simulated healthcare applications exposed through structured REST APIs and MCP tools. MCP is the interface through which the agent sees and invokes tools. [IEEE challenge description](https://bigdataieee.org/BigData2026/cup/)

Return to the imaginary request. In this environment, a chart-reading tool supplies evidence, a submission tool changes the case record, and a communication action leaves a trace of what was sent. A simulator can preserve those consequences and allow a fresh attempt from the same starting scenario. The runtime documentation describes a fresh container for each trial, with verification after the agent stops. [Runtime architecture](https://github.com/actava-ai/chi-bench/blob/main/docs/architecture.md)

The **Managed-Care Operations Handbook** provides the procedures, policies, and application guidance that help the agent determine how to act. It is a separate gated resource with non-commercial research and no-redistribution terms. The public tasks and shared worlds are distributed separately from the runtime code and handbook. The base task set has 75 cases, with 25 per domain. [Handbook](https://huggingface.co/datasets/actava/managed-care-operations-handbook), [task dataset](https://huggingface.co/datasets/actava/chi-bench)

The authors describe model-assisted case construction followed by human walkthroughs and healthcare-worker review. We should understand these as constructed simulation cases and study their validation before drawing conclusions about representativeness. [Paper v3, task construction](https://arxiv.org/html/2605.16679v3)

Inside this environment, the **agent** is the system that attempts the work. Its **model** supplies language reasoning, while its **harness** manages context, invokes the model and tools, controls continuation, and records execution. A reported result belongs to that whole configuration. Understanding the harness is therefore part of understanding an experiment.

## 4. Decide what would count as completing the work

Once a case has been attempted, evaluation needs to establish whether the required outcome actually exists. The official verifier uses workflow checks and rubric-based review. Every required applicable check must pass for the task to earn reward 1; a failed check produces reward 0. Partial completion is available for diagnosis. [Scoring guide](https://www.actava.ai/benchmarks/docs/scorecard)

For the imaginary request, evaluation might need to establish that the relevant record was created, the decision was supported, and the required communication occurred. These are illustrative obligations, not a hidden checklist from a real task. The important connection is that reasoning and execution both leave evidence that can be checked.

The correct stopping point also depends on the task. As an introductory principle, we should ask what outcome the case calls for rather than equate success with approval or agreement. The public dataset describes different workflow stages and outcomes. A later domain walkthrough should establish the exact duties for each kind of case. [Task dataset](https://huggingface.co/datasets/actava/chi-bench)

A single successful attempt still leaves a reliability question. **pass@1** asks how often one attempt succeeds. **pass@3** asks whether at least one of three attempts succeeds. **pass^3** asks whether all three succeed. The last metric tests consistency under repeated attempts. The original τ-bench paper introduced this reliability framing for agents interacting with users, policies, and tools. [τ-bench paper](https://arxiv.org/abs/2406.12045)

For example, a task with outcomes pass, fail, pass has an empirical single-attempt success rate of 2/3 and passes the at-least-once test. It fails the all-three test. Across tasks, the fraction passing all three is a different statistic from cubing the overall single-attempt rate. This small example shows why an impressive successful demonstration can leave substantial uncertainty about repeatability.

## 5. Read the results as evidence about the tested systems

With a simulator, task set, and success criterion in place, the researchers can compare agent configurations. The repository reports the paper's best overall pass@1 as 28.0%, strict pass^3 below 20% for every tested configuration, and 3.8% overall in the marathon experiment. These are the paper's reported results, not our reproduction or a refreshed leaderboard. [Reported results](https://github.com/actava-ai/chi-bench)

The connection to the original problem is now clear: the tested systems often failed to complete the required work, and repeated attempts exposed further inconsistency. We should examine which parts of the chain failed before proposing a fix. Missing evidence, misinterpreted policy, incomplete execution, and lost conversational information could call for different interventions.

Due diligence also means examining the measurement itself. The paper identifies language-only evaluation and use of a single judge model as limitations. Agreement among repeated votes from that judge checks its consistency; it does not establish agreement across independent evaluators. [Paper v3, limitations and judge analysis](https://arxiv.org/html/2605.16679v3)

We still need to study whether the cases cover the workflows we care about, whether the applicable policies are faithfully represented, and how runtime settings affect results. Low benchmark scores establish difficulty for the tested systems under the stated evaluation. They do not, by themselves, prove a cause or validate a proposed architecture. Transfer into live healthcare would require separate evidence.

## 6. Understand what the competition invites us to contribute

The competition turns the benchmark's research question into an engineering task: supply a runnable system and show how reliably it handles the cases. The indexed Kaggle overview describes the public leaderboard as provisional and final rankings as organizer-run private evaluation. Its ranking order is private pass@1, pass^3, inference cost, and tool calls. [Competition overview](https://www.kaggle.com/competitions/chi-bench/overview)

That gives our work a concrete purpose. We would eventually develop a method, evaluate it transparently, and supply code, configuration, evidence, and an explanation that another evaluator can use. Improvement on known public cases is development evidence; the private evaluation asks whether the method transfers to cases we did not tune against.

Our immediate task comes earlier. First, understand the workflows well enough to recognize correct progress. Then examine the paper's construction and evaluation closely enough to interpret its results. Finally, read the competition contract and establish reproduction requirements. Only after those steps should the earlier approach ideas be assessed against evidence, resources, and time.

The next reading should follow one provider authorization case from its starting instruction through evidence gathering, submission, and response. That will give the concepts above a concrete operational meaning before we compare agent designs.

---

## Paper and supporting material

The paper is *CHI-Bench: Can AI Agents Automate End-to-End, Long-Horizon, Policy-Rich Healthcare Workflows?*, by Haolin Chen and colleagues. Our reference is arXiv v3, revised September 30, 2026. [Version record](https://arxiv.org/abs/2605.16679)

- [Local research paper, v3](Source/CHI-Bench_2605.16679v3.pdf)
- [Source receipts and unresolved details](Source/03-background-source-notes.md)
- [Supplied competition requirements](Source/SUMMARY.md)
- [Earlier approach hypotheses](APPROACH_IDEAS.md)

The workflow example is explanatory. No agent has been created or benchmark run executed. Full competition Rules, definitive package/report timing, and gated handbook contents remain for the later diligence stages.
