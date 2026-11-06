# Observability, evaluation and maintenance

A harness needs evidence of what happened, not merely a final explanation. Record enough structure to reconstruct a run while applying the actual privacy/security policy to sensitive payloads. Logging everything indiscriminately can create a second uncontrolled data store.

## Trace the meaningful boundaries

Use correlated task/session/run/span/tool-call/action IDs. Record source/config/policy/adapter versions, model request boundaries, context selection/compaction events, permission decisions, tool outcomes, queue/ownership changes, child invocations, cancellation, errors and final status. Keep summaries distinct from exact observations and measure actual usage when the provider reports it.

A context manifest can record selected event IDs, source versions, retrieval decisions, token measurements/estimates and transform versions without duplicating full sensitive content. This helps diagnose whether a wrong answer came from missing evidence, incorrect interpretation, stale state or an execution failure. Such a manifest is a proposed engineering artifact, not a standard schema mandated by every framework.

## Evaluate at multiple layers

| Layer | What to test | What a pass does not prove |
| --- | --- | --- |
| Protocol | Valid message/tool pairing and typed adapter round trips | Correct task judgment |
| Context | Protected request/obligations survive selection; budgets respected | Perfect semantic summary fidelity |
| Memory | Scope, provenance, correction, deletion and freshness | All recalled statements are true |
| Effects | Permission gates, action identity, retries, readback | Arbitrary external exactly-once behavior |
| Recovery | Crash/interruption/replay at defined boundaries | Every platform fault is handled |
| Orchestration | Ownership, bounded fan-out, cancellation and joins | More workers improve quality |
| Task outcome | Actual valid completed work under the unchanged environment | Generalization outside the sampled tasks |
| Resource | Tokens, time, cost, tool/worker effort | Fair attribution if other variables changed |

Separate a task, one stochastic trial, the observed trace and the grader. A competent grader accepts valid alternative paths and verifies the relevant outcome rather than requiring one imagined sequence. Model-based judgments need calibration and error inspection; they are not automatically objective. [G14](../SOURCES.md#g14).

## Memory/context evaluation

Create cases where the relevant fact is old, contradicted, revoked, cross-tenant, inside a tool result, separated by several compactions or available only through retrieval. Measure recall of required facts and inappropriate recall of forbidden/stale facts. Verify source attribution and action correctness, not just lexical overlap with a summary.

A summary can look excellent while omitting an unresolved user constraint; a retrieval hit can be semantically similar but refer to the wrong case. Include adversarially duplicated/poisoned material and explicit corrections. Compare retention/retrieval policies against downstream task results under a declared resource constraint.

## Experimental controls

Pin source/environment/tool/model/config versions and record which knowledge was available. Distinguish development cases from reserved evaluation families and don't claim an untouched held-out set after using it for selection. Repeat stochastic conditions as appropriate, pair comparisons by task and report uncertainty and execution failures. More inference or better retrieval can confound an apparent architecture improvement.

The miniature offline labs in this research demonstrate selected software invariants with synthetic data. They do not measure model intelligence, semantic compaction quality, real application security or benchmark performance. Inspect their explicit limitations before transferring a result into a production claim.

## Deployment and long-lived maintenance

Version prompts, tool contracts, state schemas, memory procedures and migration code. Keep credentials out of ordinary trace/memory stores. Provide backup/restore, retention/deletion, rollout/rollback, capacity limits and a way to inspect pending/unknown operations. On upgrade, re-test persisted sessions and old checkpoints instead of only testing new empty runs.

Changing a default compression threshold, a memory backend or a tool schema can alter behavior without changing the base model. A migration must say whether old data is converted, retained read-only or no longer resumable. Documentation may lag code; preserve version-specific evidence and revalidate the effective caller/configuration path. The pinned case studies illustrate this recurring maintenance problem without implying their current choices are universal best practices.
