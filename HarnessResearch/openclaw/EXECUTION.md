# Execution and runtime boundaries

The useful unit to study is an admitted run with an owner, a session, policy, resources and a terminal outcome. A model request is one operation inside that unit. This distinction explains why a production harness has much more code than `while tool_calls: execute()`.

## The layers that should not be confused

The pinned runtime guide separates **provider** (authentication, model discovery and transport identity), **model** (selected model reference), **runtime/harness** (the prepared execution loop) and **channel** (where messages arrive and leave). It also distinguishes embedded runtimes from CLI backends. An OpenAI-named model reference alone does not prove a particular billing route, transport or native runtime. [OC-003](EVIDENCE.md#oc-003).

For the built-in runtime, OpenClaw owns the loop and transcript. A native app-server runtime can own its primary thread and compaction while OpenClaw owns channel routing/delivery and a mirror. The host projects context into that runtime through an adapter; it cannot infer access to native internals or identical hooks merely because both expose a chat interface. This is a documented ownership contract, not an executed adapter-parity result. [OC-072](EVIDENCE.md#oc-072).

Engineering implication: provider compatibility and harness compatibility are separate questions. An adapter may support text inference yet fail to preserve tool policy, cancellation, persistent thread identity, context replacement or terminal delivery semantics. This is an inference from the ownership split, not a claim that a particular adapter failed.

## The built-in execution path

The thin `src/agents/embedded-agent-runner/run.ts` entrypoint exports the orchestration implementation. In `run-orchestrator.ts`, a run resolves a session lane and a global/resource lane. It waits for deferred maintenance and transcript projection before consuming a global execution slot. This preserves same-session ordering without making unrelated sessions wait behind that session's maintenance. [OC-004](EVIDENCE.md#oc-004).

The ordinary child resource lane is keyed by immediate controller session; nested cron work has another lane so an outer scheduled job does not consume the exact slot its own inner work must acquire. A scheduler has to model nested ownership, not simply put every operation into one global semaphore. [OC-005](EVIDENCE.md#oc-005).

The attempt builds the effective tool bundle and system prompt, then uses a prompt tool-policy object that can be refreshed. The model-visible capability surface is assembled from current policy/capabilities rather than assumed from all tools compiled into the application. [OC-008](EVIDENCE.md#oc-008).

The actual built-in loop is present in the repository's `packages/agent-core/src/agent-loop.ts`. At this pin it is insufficient to describe OpenClaw only through older articles about an external Pi dependency. The inspected path:

1. Checks abort state and admits pending user/steering messages.
2. Refreshes continuation instructions/tools when an owner supplies a continuation preparer.
3. Streams a model response and permits streamed tool scheduling.
4. Executes remaining eligible calls not already executed by streaming.
5. Distinguishes provider failure from normal tool continuation.
6. Appends results and emits turn events.
7. Continues when tools or provider `endTurn=false` require it, unless a host termination/intervention wins.
8. Produces a terminal outcome on completion, abort or a fatal/intervention path.

These are source-traced branches, not measured claims about task quality. [OC-006](EVIDENCE.md#oc-006).

## Tool calls are a protocol boundary

`executeToolCalls()` first creates batch state, resolves/validates calls for optional `beforeToolBatch` admission, then determines sequential requirements. A configured sequential batch or a tool marked sequential changes scheduling; otherwise the grouped executor can overlap appropriate calls. The host must still preserve tool-call IDs, ordered result association, cancellation and side-effect ownership. [OC-007](EVIDENCE.md#oc-007).

This yields three distinct statements:

| Statement | What it establishes |
| --- | --- |
| The model emitted a valid schema-shaped call | Parameters can be parsed; it does not establish authority or usefulness. |
| The host admitted a call | Current execution policy permits that effect through this surface. |
| The tool produced a confirmed result | That operation completed to the extent its tool contract can prove. |

The separation is an engineering interpretation supported by the admission pipeline, not a universal proof that all downstream integrations expose equally strong receipts.

## Terminal output, continuation and delivery

An assistant text chunk is not necessarily a completed turn. The built-in loop handles `endTurn=false`, tool work and explicit host termination separately. The documented host then reconciles the completed result, required final reply and source delivery. A network delivery request, a progress message and a confirmed terminal delivery are different facts. [OC-006](EVIDENCE.md#oc-006), [agent-loop contract](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-loop.md).

Why this matters generally: retrying a final answer before checking whether it was already delivered can duplicate an external action. Conversely, treating any text as completion can abandon pending tool/child work. Delivery reconciliation is relevant to any harness with an external output channel, even if that channel is an evaluation API rather than chat.

## Persistence and current writer ownership

Current session/transcript state uses SQLite-backed accessors. A fenced write checks that the stored session ID, lifecycle revision and active writer run match the expected scope. The locked write guard reads fresh state before a protected mutation and raises a rebound error when the owner changed. [OC-018](EVIDENCE.md#oc-018), [OC-019](EVIDENCE.md#oc-019).

This solves a different problem from a queue. A queue controls normal scheduling; a current-owner check rejects a late callback from an old run after reset, replacement or cancellation. The source documentation additionally describes a state-directory lock against competing Gateway/local owners. That full multi-process behavior is documentation-backed here, not crash-tested. [OC-020](EVIDENCE.md#oc-020).

A focused writer-claim test file contains supersession/stale-owner fixtures. We inspected its assertions without running it; no passing test count is claimed. [OC-073](EVIDENCE.md#oc-073).

## What a new harness author can take from this example

These are design options, not a prescription to clone this architecture:

- Name who owns the run, session, provider request, tool effect, child and delivery.
- Make lifecycle state explicit enough to distinguish accepted, queued, running, interrupted, terminal and delivered.
- Keep cancellation and write authority current after waits.
- Decide whether an external runtime or the host owns history/context, and test that seam explicitly.
- Prefer a small loop with replaceable provider/tool contracts until actual product requirements justify a multi-channel Gateway and its operational complexity.

The last point is a design judgment: OpenClaw's scope explains its breadth, but breadth is not evidence that every task runner needs the same subsystems.
