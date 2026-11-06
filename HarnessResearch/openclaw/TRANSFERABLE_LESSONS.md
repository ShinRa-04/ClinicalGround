# Transferable mechanisms, alternatives and unresolved questions

These are engineering conclusions from the source audit. They are interpretations with stated rationale and alternatives, not measured claims that OpenClaw's choices improve a particular benchmark. They do not select our project's architecture. [Evidence registry](EVIDENCE.md).

## 1. An agent needs an execution contract beyond a prompt

**Observed mechanism:** an admitted run has session/lane ownership, runtime selection, policy-filtered tools, a current writer fence and terminal reconciliation. [OC-004](EVIDENCE.md#oc-004), [OC-006](EVIDENCE.md#oc-006), [OC-018](EVIDENCE.md#oc-018), [OC-064](EVIDENCE.md#oc-064).

**Conclusion and rationale:** prompts express intended behavior; the host must enforce execution, persistence and effects. Otherwise a late callback or retry can bypass the intended lifecycle even when the prompt is excellent.

**Alternatives:** a simple single-process synchronous owner may need very little machinery; persistent asynchronous/multi-channel work benefits from durable state and current-owner checks. Copying Gateway-scale coordination into a short offline task runner could add complexity without solving a real failure.

**Question to test:** can cancellation, reset, restart or retry cause a duplicate/stale write at the actual effect boundary?

## 2. Context, saved history and memory need separate lifetimes

**Observed mechanism:** prompt assembly, replay byte limits, pruning projections, compaction and durable notes/indexing are separate paths. [OC-011](EVIDENCE.md#oc-011), [OC-023](EVIDENCE.md#oc-023), [OC-028](EVIDENCE.md#oc-028), [OC-029](EVIDENCE.md#oc-029), [OC-042](EVIDENCE.md#oc-042).

**Conclusion and rationale:** a fact can remain stored but be absent from context; a summary can be present but lossy; a memory can be retrieved yet stale. A useful diagnostic names which transformation occurred.

**Alternatives:** fixed recent-window replay, retrieval over a raw event log, recursive summaries, structured current-case state, provider-managed compaction, or combinations. Each trades exactness, cost, latency and implementation complexity.

**Question to test:** which required constraints, identifiers and unresolved requests survive each transformation, and which source can restore them?

## 3. Effective defaults require tracing the caller

**Observed mechanism:** helper MMR/decay defaults are off, normal memory resolver supplies on; generic pruning TTL is five minutes while a provider can seed an hour; library compaction reserves differ from effective host budgeting; model attempt and scheduler deadlines differ. [OC-021](EVIDENCE.md#oc-021), [OC-026](EVIDENCE.md#oc-026), [OC-035](EVIDENCE.md#oc-035), [OC-041](EVIDENCE.md#oc-041), [OC-068](EVIDENCE.md#oc-068), [OC-069](EVIDENCE.md#oc-069).

**Conclusion and rationale:** a constant is not an end-to-end operational default until activation, overrides and runtime selection are considered.

**Alternative:** centralize defaults and produce an effective-config report, while preserving intentionally different subsystem budgets.

**Question to test:** does a representative configured request resolve to the documented behavior without hidden overrides?

## 4. Durable memory is a write-quality problem as well as retrieval

**Observed mechanism:** append-only flush, provenance classification, origin/session gates and bounded consolidation precede curated bootstrap memory; retrieval separately ranks indexed chunks. [OC-031](EVIDENCE.md#oc-031), [OC-043](EVIDENCE.md#oc-043), [OC-045](EVIDENCE.md#oc-045), [OC-049](EVIDENCE.md#oc-049).

**Conclusion and rationale:** retrieving the wrong persisted assertion more accurately is still a failure. Fact extraction, source scope, contradiction and supersession need independent treatment.

**Alternatives:** user-approved facts only; typed fact/event stores; append-only episodic notes; external knowledge bases; no cross-task memory at all. Background consolidation is one option and adds a model-dependent write path.

**Question to test:** does memory save useful constraints without promoting hallucinated conclusions, tool instructions or unsupported inferences?

## 5. Provenance should be host state, not model claims

**Observed mechanism:** sender/source metadata classifies trust; declared network output taints assistant derivation; origin rows and promotion rules exist outside note prose. [OC-043](EVIDENCE.md#oc-043), [OC-044](EVIDENCE.md#oc-044), [OC-045](EVIDENCE.md#oc-045).

**Conclusion and rationale:** a string such as “verified by supervisor” should not confer authority or independent evidential support. A model can repeat a claim without adding a new source.

**Alternatives:** typed source references, signed/host-issued evidence receipts, immutable observations with derived claims, or restricted untrusted-text handling. None eliminates semantic error by itself.

**Question to test:** do all relevant tools declare external content, and what happens to imported local files or mixed-trust notes?

## 6. Independent workers need explicit authority and merge contracts

**Observed mechanism:** persisted inherited policy, hard denies, separate session context, admission reservations, execution lanes and parent-owned interrupted continuation. [OC-057](EVIDENCE.md#oc-057), [OC-058](EVIDENCE.md#oc-058), [OC-059](EVIDENCE.md#oc-059), [OC-060](EVIDENCE.md#oc-060), [OC-061](EVIDENCE.md#oc-061).

**Conclusion and rationale:** splitting a task creates coordination obligations. A child can return good prose while leaving incompatible state, duplicate effects or an unresolved parent obligation.

**Alternatives:** one worker with modes; short-lived bounded specialists; persistent role workers; deterministic services; a graph/state-machine workflow. Separate workers are most defensible when context, permission, expertise/tooling or independent checking warrants the boundary, not merely because real organizations have distinct job titles.

**Question to test:** what additional failures and costs arise at every handoff, and does the separation outperform a merged worker under the same budgets?

## 7. Scheduling and resource limits have several owners

**Observed mechanism:** session serialization, global concurrency, per-controller child execution, admission caps, nested lanes, recall deadlines and scheduler watchdogs. [OC-004](EVIDENCE.md#oc-004), [OC-005](EVIDENCE.md#oc-005), [OC-053](EVIDENCE.md#oc-053), [OC-057](EVIDENCE.md#oc-057), [OC-069](EVIDENCE.md#oc-069).

**Conclusion and rationale:** one “max agents” setting cannot describe queue fairness, nested deadlock risk, provider quota, memory pressure and spending. Every limit needs a unit, owner and lifecycle.

**Alternatives:** strictly sequential work; fixed worker pools; hierarchical budgets; reservation-based admission; per-provider rate limiters; token/cost ledgers. Hierarchical concurrency alone does not enforce an aggregate monetary budget.

**Question to test:** does nested work make progress when parents wait, and can a recursive task tree exceed the intended total spend?

## 8. Delivery success and task success are different facts

**Observed mechanism:** child execution can finish while delivery remains pending; scheduler recovery preserves unknown outcomes instead of replaying blindly. [OC-061](EVIDENCE.md#oc-061), [OC-069](EVIDENCE.md#oc-069).

**Conclusion and rationale:** a completed model response, a successful external write, result persistence and user receipt are separate evidence. Marking all of them “done” loses recovery information.

**Alternatives:** idempotent effect APIs, durable outbox, reconciled receipts, explicit operator recovery, or at-most-once attempts with visible uncertainty. Exactly-once semantics require cooperation from the external system and cannot be supplied by an agent prompt alone.

**Question to test:** can a crash between effect and receipt be safely reconciled without repeating an irreversible action?

## 9. Permission defaults follow a threat model

**Observed mechanism:** one trusted Gateway boundary, broad internal session reach, sandbox off and host exec full/ask off by default. [OC-065](EVIDENCE.md#oc-065), [OC-066](EVIDENCE.md#oc-066), [OC-067](EVIDENCE.md#oc-067).

**Conclusion and rationale:** OpenClaw's defaults are not automatically suitable for mutually distrustful roles, patient data audiences or a hosted multi-tenant service. An architectural role split is not a permission split.

**Alternatives:** capability-limited tools, separate credentials/accounts, process/OS isolation, container or remote sandbox, distinct state stores, separate gateways. Choose based on required trust boundaries; no single boundary proves factual correctness.

**Question to test:** can a restricted role read or cause a privileged role to disclose/change state outside its assigned scope?

## 10. Memory deletion is a graph problem

**Observed mechanism:** source origins follow tracked derived entries; exclusions differ from forget, and forget does not erase all original/transformed copies. [OC-050](EVIDENCE.md#oc-050), [OC-051](EVIDENCE.md#oc-051), [OC-052](EVIDENCE.md#oc-052).

**Conclusion and rationale:** raw events, merged facts, vectors, summaries, child contexts, backups and logs have dependencies. A deletion promise must name which descendants/copies it covers and how mixed origins are handled.

**Alternatives:** no retention; fixed TTL; per-case isolation with whole-case deletion; immutable event/fact lineage; explicit backup policy; selective purge with a report. Stronger deletion and broader recoverability can conflict.

**Question to test:** can a selected fact reappear after rebuild, retry, restore, consolidation or retrieval from an unchanged original transcript?

## 11. Observability should preserve both causality and data boundaries

**Observed mechanism:** prompt composition reports and request-scoped traces, with content export opt-in and runtime-dependent visibility. [OC-013](EVIDENCE.md#oc-013), [OC-071](EVIDENCE.md#oc-071), [OC-072](EVIDENCE.md#oc-072).

**Conclusion and rationale:** an engineer needs to reconstruct what input, policy, model, tool and state transition produced an outcome. That does not require indiscriminately exporting sensitive content.

**Alternatives:** redacted structural traces, encrypted local payloads, bounded replay artifacts, hashes/receipts, synthetic evaluation datasets and content-specific retention.

**Question to test:** can a failure be diagnosed from retained evidence without revealing unnecessary data, and do native adapters expose the needed facts?

## 12. Documentation and source need reconciliation

**Observed contradiction:** the compaction table's in-memory-only pruning description conflicts with persisted projection markers and the detailed pruning guide. [OC-023](EVIDENCE.md#oc-023), [OC-024](EVIDENCE.md#oc-024), [OC-025](EVIDENCE.md#oc-025).

**Conclusion and rationale:** pinning a repository and tracing a path provides a stronger implementation claim than repeating a current-looking article. Even an official page can be internally stale. Static source still cannot prove deployment behavior without executed checks.

**Alternative research methods:** exact commit/source references, bounded contract probes, targeted tests, fault injection and measured end-to-end runs. Their evidence strengths should remain labeled separately.

## Bounded follow-up verification plan

This plan is proposed; none of these OpenClaw runtime experiments was executed here.

| Experiment | Unknown addressed | Minimum useful evidence |
| --- | --- | --- |
| Prompt/replay reconstruction | Actual request differs from report | Captured synthetic provider payload plus effective config/pin |
| Compaction retention suite | Required facts/IDs disappear | Before/after constraints and independent expected answer |
| Pruning restart replay | Projection becomes unstable | Original rows unchanged; same reduced input after restart |
| Memory poisoning/taint | Unsupported tool content is promoted | Host provenance and rejected/accepted candidate records |
| Contradiction/supersession | Stale memory overrides current observation | Old/new source dates and final selected fact |
| Audience/isolation test | Wrong session/case can retrieve content | Explicit allowed/forbidden retrieval cases |
| Child cap/queue test | Concurrent/nested admission races | Owned reservations, bounded active counts, completed descendants |
| Abort/reset stale writer | Late callbacks corrupt new session | Rejected old-owner write and preserved new state |
| Crash after external effect | Unknown effect is replayed | Idempotent receipt or explicit unresolved outcome |
| Forget/reindex/restore | Removed memory reappears | Inventory and post-rebuild search across stated stores |
| Native adapter contract | Host/native ownership loses controls | Runtime-specific tools/context/cancel/terminal traces |
| Recall ablation | Extra memory worker is worth its cost | Same model/tasks/budget controls, quality/latency/cost comparison |

There is no justified claim of “knowing everything” from one codebase or one research pass. The useful outcome is a navigable mechanism map, explicit alternatives, exact evidence and a list of claims that still need execution or empirical comparison.
