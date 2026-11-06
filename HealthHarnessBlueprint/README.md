# Hypothetical healthcare organization and agentic harness

Design proposal, October 18, 2026. The three required anchors are **provider prior authorization (PA), payer utilization management (UM), and care management (CM)**. χ-Bench supplies the day's cases and workflow conditions. We propose the working organization that processes them: staff roles, assignments, queues, decisions, documents, memory and handoffs, with shared capabilities underneath.

This is a hypothetical architecture/research deliverable, not an implemented harness, clinically validated operating system or production deployment. Proposed agents, interfaces, internal states and budgets are ours; they are not asserted benchmark APIs, legal permissions or measured improvements. Previous role/engineering research informs choices without selecting Hermes, OpenClaw or another framework as the blueprint.

**Primary design: a hospital-like organization inside our harness, operating on χ-Bench's existing environment.** The supplied environment owns case truth, tool state and counterparties. Our organizational model assigns responsibilities and coordinates work; it does not create a competing patient chart or invent supplied patient/reviewer/service outcomes.

The user explicitly clarified that a broad hospital-world simulator is **not** the intended project. There is one supplied task environment; the hospital analogy describes our operating organization, not a second patient/clinical world. No mismatch in χ-Bench case facts has been established. A detailed task-by-task tool/state mapping has not yet been executed.

The design includes an organizational layout, composite jobs and finer responsibility contracts, core/supporting workflows, source-linked working state, strict patient isolation, memory/context policy, execution boundaries, evaluation and an implementation roadmap. Exact technology/model choices remain replaceable pending evidence.

## Recommended shape

I would make each major job a **composable organization of smaller responsibilities**. A PA specialist owns the assigned outcome, but is built from request/identity/coverage/policy/evidence/gap/composition/submission/response/closure contracts. UM and CM have equivalent fine-grained decompositions. A combined owner can execute several responsibilities itself or delegate those that benefit from a separate context. Deterministic functions remain deterministic; a role contract is not a demand for another model call.

The initial catalogue has **66 micro-responsibilities**: PA 18, UM 18, CM 20 and shared support 10. It also has 29 upper-level modules, which are a different organizational layer—not a competing agent count. No optimal count or composition is claimed.

Reuse the approved job definition, not patient memories. Every patient's records, dialogue, summaries, episodes, checkpoints and helper outputs remain in the permitted patient/case/task boundary. No automatic patient-derived cross-patient learning is proposed.

## Reading path

1. [Composition model](COMPOSITION.md): the smaller roles, top-level owner, three execution arrangements and split/merge reasoning.
2. [All 66 micro-role contracts](MICRO_ROLES.md): inputs, outputs, decision scope, boundaries and completion checks.
3. [A day of work](A_DAY_OF_WORK.md) and [PA/UM/CM service blueprints](WORKFLOWS.md): how staff process incoming cases and handoffs.
4. [Architecture](ARCHITECTURE.md), [organization](ORGANIZATION.md) and [layout diagrams](DIAGRAMS.md): layers, ownership and information flow.
5. [Patient isolation](PATIENT_ISOLATION.md), [memory/context](MEMORY_AND_CONTEXT.md) and [memory layers](MEMORY_LAYERS.md): shared general knowledge versus isolated patient work.
6. [Organizational module catalogue](MODULE_CATALOG.md), [97-function context map](ROLE_COVERAGE.md), [service contracts](SERVICE_CONTRACTS.md) and [data/execution](DATA_AND_EXECUTION.md).
7. [Design decisions/questions](DECISIONS_AND_OPEN_QUESTIONS.md), [evaluation/failure cases](EVALUATION_AND_FAILURES.md) and [roadmap](ROADMAP_AND_LAYOUT.md).
8. [Sources](SOURCES.md) and [verification](VERIFICATION.md): evidence versus proposal and what has actually been checked.

Authored specifications live in catalog.py and micro_roles.py; tools/build_blueprint.py generates their catalogues/JSON. Narrative documents explain the proposal and user decisions. The code in this folder is document tooling, not an implemented healthcare agent.
