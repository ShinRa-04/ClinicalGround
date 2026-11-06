# Orchestration, concurrency and sub-agents

The unit of orchestration is work with an objective, evidence view, operations, owner, budget and completion condition. A job title or persona name does not define those contracts. This general principle is compatible with a single agent, a workflow graph or several workers.

## Patterns to compare

| Pattern | Useful property | Typical engineering cost |
| --- | --- | --- |
| Single loop with role modes | Shared context and simple ownership | Context interference and self-check blind spots |
| Bounded specialist as a tool | Focused fresh context with a limited result | Handoff loss and additional inference |
| Supervisor/worker fan-out | Parallel independent investigations | Budget aggregation, joining and cancellation |
| Handoff between agents | Changes the active responsibility/context | Lost obligations and ambiguous ownership |
| Durable workflow graph | Explicit stages/checkpoints/interrupts | Rigid transitions and migration complexity |
| Peer/blackboard collaboration | Shared evolving evidence or proposals | Conflict resolution and noisy shared state |
| Hierarchical team | Decomposes large work into local scopes | Multi-level compression and coordination overhead |
| Background actor/scheduled job | Progress independent of an interactive turn | Freshness, consent/scope and delivery races |

These are design alternatives, not a required progression. Parallelism helps only where work can use a sufficiently complete snapshot without depending on another worker's unfinished action. Sometimes a deterministic search/query or a role-specific function is better than a new autonomous worker. [G09/G10](../SOURCES.md#g09).

## Admission, execution and budgets

Separate the number of child tasks accepted, queued, running and waiting for results. An admission cap, executor concurrency limit and provider rate limit need not be identical. Bound queue length, per-session concurrency, total worker fan-out, nested depth, tokens/cost and elapsed time. Backpressure should expose overload rather than allocate unbounded work.

Decide whether children share the parent's budget or have separate allocations. Independent local budgets can produce unexpectedly large aggregate spend, especially under nesting. One child timing out does not automatically stop siblings or their tools. Propagate cancellation and retain the status of any effects already dispatched.

## A handoff contract

A proposed request carries task/case, input snapshot/version, bounded question, relevant source references, allowed tools/data, expected output, deadline/budget, stop rule and destination/owner. A result distinguishes observations, interpretations, proposed actions, missing facts and actual effects. It should identify the evidence snapshot it used so the parent can reject or refresh a stale proposal.

Do not treat a brief summary as guaranteed sufficient. If a source locator or critical qualifier is missing, the parent must be able to request/read the original. Likewise, sending every raw transcript to every child defeats context isolation and may violate scope. Message design is a relevance and trust decision, not merely a serialization format.

## Shared state and competing proposals

One writer with read-only proposal workers is a useful baseline, not a universal architecture. Multiple writers can be appropriate when mutations are disjoint/transactional and the actual backend enforces consistency. A merge function must resolve conflicts according to domain rules and source versions, not arbitrary last-writer-wins or a vote over unsupported opinions.

Knowledge separation, execution separation and institutional independence are distinct. A fresh model context can diversify attention; it does not establish independent legal authority or eliminate correlated errors. A worker with a separate process but identical unrestricted credentials may not be isolated at all.

## Scheduling and interruption

An incoming user correction can replace, refine or interrupt an active intention. Preserve the latest instruction and cancel/reconcile obsolete work instead of letting stale tasks publish after a new request. Queue policy can be FIFO, per-key serialization, priority-based or explicit coalescing, but order changes can alter meaning and should be intentional.

Scheduled jobs and heartbeats need trigger identity, timezone, missed-run policy, deduplication, task scope and result-delivery ownership. A repeating schedule is not a reason to reuse stale consent, a stale task snapshot or an old session writer claim. Sleep/restart/reconnect behavior should be tested where the product relies on it.

## How to evaluate the team

Compare against a strong single-worker condition with comparable knowledge/tools and an explicit resource constraint. Count all controller/child calls, communication tokens, retries and latency. Measure completed outcomes and new failure modes, not the number of workers or how realistic their conversation sounds. Keep persona richness, context splitting, model choice, retrieval quality and tool scope as separate variables when attributing gains.

The [earlier role study](../../Plan/AgentOrganization/README.md) proposes healthcare-specific experiments. Its functional groupings remain hypotheses; this general handbook explains the engineering mechanisms needed to test them rather than confirming them by analogy.
