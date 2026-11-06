# Anatomy of an agentic harness

This chapter is a general engineering model, not the architecture of one product. The reference systems demonstrate implementations; they do not determine our design. Source-backed mechanisms are distinguished from proposed engineering contracts throughout this handbook.

## The model is one component

A model produces outputs from supplied inputs. An agentic system adds a goal, observations, tools and a repeated opportunity to act. The **harness** is the software that makes those opportunities controlled, stateful, observable and recoverable. It constructs each request, interprets responses, mediates operations, maintains continuity and decides whether execution can continue. An SDK can implement part of this; a gateway or managed service can implement more. Owning a model endpoint is not the same as owning these runtime responsibilities. [G03/G07](../SOURCES.md#g03).

Separate a product's user experience from its execution kernel. Chat channels, a CLI, a web UI and scheduled tasks are entrypoints. They may share one kernel or have different loops. A code path used by an interactive CLI is not proof that the gateway, cron worker or delegated child uses identical policy.

## Components and contracts

| Component | Responsibility | Failure if conflated |
| --- | --- | --- |
| Ingress | Authenticate/identify an input and place it in the correct session | Cross-user/case contamination |
| Task state | Track requested work, obligations and observed progress | “Conversation ended” becomes “task complete” |
| Session manager | Identify a conversation/run and manage ownership/lifecycle | Concurrent writers or reset confusion |
| Context builder | Select/render what the next model call sees | Hidden omissions or runaway prompts |
| Model adapter | Normalize supported request/response semantics | Broken tool blocks or incompatible state |
| Tool registry | Describe and discover available operations | Overlapping or stale capabilities |
| Policy/execution gate | Validate scope, arguments and required approvals before effects | A model request becomes unrestricted execution |
| Executor | Run permitted calls, capture outcomes and handle cancellation/timeouts | Duplicate or unobserved effects |
| Persistence | Preserve events/checkpoints/artifacts with clear commit boundaries | Restart loses obligations or repeats work |
| Memory service | Admit, retrieve, revise and delete cross-run knowledge | Stale or poisoned recollections |
| Scheduler/orchestrator | Route work, join results and control concurrency/budgets | Unbounded fan-out or deadlock |
| Observability | Attribute actions, versions, usage and errors | A failure cannot be reproduced or explained |
| Evaluator | Measure valid outcomes and failure modes | Fluent narration substitutes for success |

These are logical responsibilities, not a demand for thirteen services. A small harness can implement several in one process. Splitting into processes becomes useful when deployment, isolation, concurrency or ownership demands it—not merely because a diagram contains separate boxes.

## A turn as a state machine

A proposed lifecycle is: accept input → claim the appropriate session/run → load authoritative state → construct the model view → check budget → request inference → validate/assemble output → execute permitted effects → record observations → evaluate stop/continue conditions. Tool results may trigger another inference step within the same user turn. Streaming output may occur before all work finishes, so delivery and task completion need separate events.

The transition conditions matter more than the loop syntax. A partial streamed tool argument is not an executable call. A successful HTTP response is not proof the intended business state exists. An assistant final message is not necessarily a complete task. An exhausted budget should produce a truthful unresolved/checkpoint state, not an invented success. [G03](../SOURCES.md#g03), [G14](../SOURCES.md#g14).

Keep control decisions inspectable: why a worker was invoked, which evidence/version it used, what action it proposed, what gate accepted it and what observation established the result. Observable decisions and actions are sufficient engineering records; the system must not depend on access to a model's private reasoning transcript.

## Two useful architectural families

An **open agent loop** lets the model choose steps within permissions. It handles variable paths but needs strong termination and effect controls. A **workflow/state graph** constrains transitions and calls models inside bounded steps. It offers explicit recovery points but can reject valid exceptions if the graph is too rigid. A hybrid may use a graph for durable stages and an agent loop inside an investigative stage. These are alternatives to evaluate, not a maturity ranking.

The construction question is therefore: which state and transitions must software guarantee, and where should model judgment remain flexible? Do not ask the model to simulate a transaction manager or ask a fixed graph to anticipate every information-gathering path.

## Questions to answer before coding

Who is the principal? What can change externally? What evidence defines completion? What survives a crash? Who can cancel or redirect? Which operations can be retried? What can another worker observe? Which instructions outrank retrieved material? What is the maximum resource spend? If these answers are vague, a framework choice will conceal rather than resolve the design problem.
