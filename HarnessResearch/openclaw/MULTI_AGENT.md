# Delegation, session boundaries and resource ownership

OpenClaw distinguishes background child runs, persistent visible sessions, external ACP/native sessions, and configured agents/personas. Those surfaces can share models and tools while differing in lifecycle, authority and history. A role name alone does not establish a process, context or permission boundary. The documented subagent unit runs in its own session and normally announces results to a requester. [Subagent overview](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents.md).

## What crosses a spawn boundary

At the implementation level, the persisted policy envelope records the child session key, spawning parent, optional completion owner, inherited allow/deny policy and delegated policy. These are actual state fields, separate from the child system prompt. [OC-059](EVIDENCE.md#oc-059).

Context can be narrow task input or a fork where supported; full transcript inheritance costs tokens and may include irrelevant or audience-sensitive data. The subagent guide documents independent contexts/token usage and conditional fork behavior. That is a contract description, not a measured comparison of architectures. [Pinned overview](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents.md).

The child representation has several independent dimensions:

| Dimension | Questions an implementer must answer |
| --- | --- |
| Identity | Which configured agent and session owns this work? |
| Task | What result, evidence and stopping condition are required? |
| Context | Fresh task, selected evidence, forked transcript or shared structured state? |
| Tools | Which effective tools survived all restrictions? |
| Credentials | Which owner supplies them; can they be forwarded? |
| Storage | Separate conversation, shared workspace, isolated worktree or sandbox? |
| Completion | Who receives results and who decides the main task is complete? |
| Lifetime | One run, resumable session or recurring worker? |
| Budget | Child admission, running capacity, deadline, tokens and downstream cost? |

This table is a general analytical decomposition. It should not be read as a claim that all dimensions are configurable for every OpenClaw adapter.

## Tool policy and current authority

The normal policy pipeline applies profile/provider/global/agent/group/sender restrictions. The subagent layer adds hard-denied surfaces and persisted-envelope restrictions. Hidden helpers lack `message`; visible spawned dashboard sessions have a scoped delivery exception. At the depth cap, leaf workers lose further spawn/session-control surfaces. Ordinary allow/alsoAllow entries cannot override documented hard denies. [OC-060](EVIDENCE.md#oc-060), [OC-062](EVIDENCE.md#oc-062), [OC-063](EVIDENCE.md#oc-063).

The host also issues run authority with a live assertion, abort/revocation state and current assignment readers. Neither a model saying “I am the supervisor” nor a session key authorizes an effect. [OC-064](EVIDENCE.md#oc-064), [OC-067](EVIDENCE.md#oc-067).

General lesson: if one role must be allowed to recommend and another to apply a change, enforce the write capability in code/tool credentials. Two different natural-language role prompts are not sufficient enforcement.

## Concurrency is not one number

At this pin:

| Bound | Default/source scope | Interpretation |
| --- | --- | --- |
| Top-level agent execution capacity | `max(8, 4 * availableParallelism())` | Shared resource capacity unless configured |
| Ordinary child execution capacity | 8 per immediate controller session | Accepted work above capacity can queue |
| Active child admission | 5 per controller | Raising execution capacity alone does not authorize more active children |
| Recursive spawn depth | 5 | A depth-capped child is a leaf |
| Archive delay | 60 minutes | Retention/lifecycle control, not runtime timeout |

These constants and resolvers are code-traced; they are not recommended values for a new harness. [OC-057](EVIDENCE.md#oc-057).

Pending child starts reserve admission slots before the asynchronous launch completes. Release is idempotent. That prevents several simultaneous requests from each observing spare capacity and oversubscribing admission. Depth and active/total caps are separate checks. [OC-058](EVIDENCE.md#oc-058).

Ordinary subagent execution lanes belong to the immediate parent. A nested orchestrator's descendants use its capacity, avoiding a simple “parent holds all slots while waiting for its children” deadlock. A different completion recipient does not move the execution budget. Special collectors/swarm and native runtime schedulers have their own contracts; do not assume ordinary limits apply to them. [OC-005](EVIDENCE.md#oc-005), [operations contract](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents/operations.md).

## What a child completion means

A child's successful execution, result persistence, announcement delivery and main-task completion are different events. The documented lifecycle permits delivery backlog/failure without converting a successful child computation into a failed computation. Equally, a finished child does not imply its parent's dependencies are satisfied. [Subagent operations](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents/operations.md).

For general harness engineering, a result envelope should make task identity, outcome, artifacts, evidence, incomplete work, errors and cost visible. Whether that envelope is typed JSON or a constrained text format is a design choice; the need to distinguish those facts follows from the lifecycle split.

## Restart and interrupted work

The current operations guide says interrupted children are finalized with an interrupted result instead of automatically relaunched after Gateway restart. The parent receives settled results and decides remaining work. Current operator authority must be revalidated; saved metadata alone does not mint a new execution grant. This is a documented recovery protocol, not a crash test performed in this research. [OC-061](EVIDENCE.md#oc-061).

Why this matters: a child may have changed an external system before its completion record was saved. Blind replay risks repeating that effect. A safe recovery policy needs tool-level receipts/idempotency or explicit inspection, not only “retry the agent.” The exact recovery tradeoff depends on the external tool contract.

## Session isolation is weaker than security isolation

Independent contexts help focus and cost accounting. They do not, by themselves, isolate credentials, host files or other agents' transcripts. The documented Gateway model is one mutually trusted boundary with broad default session reach; sandbox configuration is separate and defaults off. [OC-065](EVIDENCE.md#oc-065), [OC-067](EVIDENCE.md#oc-067).

Therefore, using subagents to model different people is a representation decision. Actual separation of authority, data audience or tenant trust needs additional enforced boundaries. Conversely, functions with the same authority and shared state can sometimes remain modes/tools inside one worker. This is a general design inference, not an OpenClaw performance result or a selection for our project.
