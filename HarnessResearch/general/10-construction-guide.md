# Constructing a harness from requirements

This is a general construction method, not a prescription to reproduce Hermes, OpenClaw or any framework. Every stage below is conditional on the intended workload. The source studies provide examples and counterexamples; the application requirements determine the design.

## Start with the work, not the framework

Write down the task principal, observable goal, input/output evidence, permitted effects, uncertainty, interruption/restart needs, expected duration, trust boundary and resource constraint. Classify representative tasks: single bounded inference, deterministic workflow with model steps, open-ended tool loop, recoverable long-running job, or collaborative work with independent subtasks.

Some jobs need no autonomous loop. Others need flexible exploration within a durable workflow. A personal local assistant, a public multi-tenant service, a batch analyst and a clinical workflow solver do not have interchangeable access, memory or recovery requirements. This is why a reference implementation's default should be studied in its own deployment context.

## A useful construction sequence

| Stage | Build or choose | Evidence required before expanding |
| --- | --- | --- |
| 1. Domain contract | Task state and terminal/exception conditions | A real outcome can be checked independently of narration |
| 2. Observation layer | A small relevant read-only tool surface | Correct IDs, provenance, bounded responses and meaningful errors |
| 3. Model boundary | Typed request/response adapter | Supported tools/content/streaming and accurate stop/error interpretation |
| 4. Minimal loop | Goal → observation → proposal → permitted action → observation | Bounded steps/budget and truthful unresolved completion |
| 5. Effect boundary | Permission, action identity, execution/result ledger | Fault/retry tests don't silently create duplicate or falsely confirmed effects |
| 6. Persistence | Session/events/checkpoints/artifacts with selected backend | Restart, migration and ownership behavior are demonstrated |
| 7. Context policy | Prompt composition, measurement, selection and compaction | Required instructions/obligations and protocol units survive |
| 8. Memory | Admission, scope, retrieval, correction and deletion | Wrong/stale/untrusted memories do not silently gain authority |
| 9. Orchestration | Modes, bounded helpers or durable graph if justified | A controlled comparison shows what extra machinery contributes |
| 10. Operations | Tracing, capacity, upgrades, backup/restore and evaluation | Actual deployment assumptions and remaining failure modes are documented |

The ordering is illustrative, not a waterfall rule. Security and persistence requirements must influence early contracts even if their full implementation comes later. For an existing framework, inspect which responsibilities it actually owns and which still belong to the application.

## Interfaces that keep choices replaceable

Prefer explicit boundaries such as `ContextBuilder`, `ModelAdapter`, `ToolPolicy`, `Executor`, `SessionStore`, `MemoryStore`, `CheckpointStore`, `Scheduler` and `Observer`. These are proposed logical interfaces, not a required class hierarchy. A compact local program may combine them; a hosted system may delegate several to a service.

Context construction should accept a versioned state snapshot and return a request plus a manifest of selected evidence/transform versions. Execution should accept a fully resolved permitted operation and return an observation or explicit ambiguity. Memory retrieval should accept principal/scope/query/freshness constraints and return source-linked records, not an unqualified answer that overwrites authoritative state.

An adapter should expose capabilities and unsupported routes rather than silently pretend every provider is identical. A storage interface should disclose whether it is ephemeral, local durable or remotely coordinated. A checkpoint interface should state its replay boundary and whether external effects can repeat.

## Choose representations by invariants

Structured state is useful when a field has an operational meaning: current case ID, pending action, source version, unresolved request or approval digest. Free text is useful for explanations and contextual notes. Neither should replace the other universally. An excessively rigid schema can discard nuance; free-form prose can conceal missing obligations.

Use immutable observations and versioned derived interpretations where feasible. Keep authoritative domain state separate from a model-generated working summary. Event logs and materialized views can coexist, but event sourcing is not compulsory. Files, SQLite, a transactional database or a workflow service are alternatives with different operating assumptions.

## Extend deliberately

| Extension | What it changes | What still needs verification |
| --- | --- | --- |
| Prompt/role template | Guidance and model attention | It does not grant credentials or enforce access |
| Skill/procedure | Reusable method/context, sometimes helpers | Provenance, version, prerequisites and transfer validity |
| Tool | Available operation and observation contract | Authorization, side effects, errors and retry semantics |
| Plugin | Code or provider/backend integration | Supply chain, lifecycle, compatibility and trust boundary |
| Memory provider | Storage/retrieval/admission implementation | Isolation, deletion, freshness and injection behavior |
| Context engine | Selection/compression/projection policy | Budget correctness, protocol validity and recoverable omissions |
| Worker/sub-agent | Separate reasoning/execution responsibility | Input/output scope, ownership, budget and net value |

These categories overlap in actual products. Inspect the interface, caller and effective configuration before relying on a name. A plugin that replaces a memory tool may not replace automatic prompt injection or pre-compaction flushing unless the caller routes those through it.

## Learning and self-modification

Saving a useful procedure, editing a prompt, adding a plugin and updating model weights are different changes. Each needs its own version/evaluation/rollback boundary. A successful-looking run can teach the wrong procedure if success wasn't independently observed. A local fix can overfit a task family. Training on traces introduces an additional data/training/evaluation pipeline; it is not implied by writing a memory file.

Constrain automated proposals to the allowed scope, retain evidence and test against reserved cases before making broad claims. Product-specific “self-improvement” terminology should be decomposed into the concrete operation: what was changed, who approved it if required, what evidence supported it, and which future runs consume it.

## Preserve the ability to say unknown

An honest harness can report a pending external outcome, missing evidence, incompatible provider state, failed memory write, expired scope or exhausted budget. The alternative is often fabricated completion. Design the unresolved states and reconciliation paths before the happy path becomes entrenched.

The [data contracts](11-data-contracts-and-failure-catalog.md) and [synthetic labs](../labs/README.md) make selected invariants concrete. They are teaching/verification artifacts, not our eventual production harness. No framework, worker count or provider is selected by their existence.
