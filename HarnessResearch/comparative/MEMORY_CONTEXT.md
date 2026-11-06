# Memory and context as separate engineering mechanisms

## A useful vocabulary

The semantic/episodic/procedural taxonomy describes remembered facts, experiences and methods. It does not prescribe a database. Semantic memory is also distinct from semantic search: storing a preference is a memory decision; using embeddings to retrieve it is a search decision. LangChain's official memory overview uses this distinction and contrasts a consolidated profile with a document collection, and foreground with background writes. These are useful design axes, not a complete scientific theory of machine memory. [Official memory overview](https://docs.langchain.com/oss/python/concepts/memory). Evidence C15.

| Mechanism | Question it answers | Failure a designer should examine |
| --- | --- | --- |
| Active context | What does this model request contain? | Omitted constraint, contradictory versions, tool-pair corruption |
| Working/task state | What is currently known, pending or completed? | Lost status, stale observation, concurrent overwrite |
| Execution checkpoint | Where can this computation recover? | Unsaved effect, repeated task, incompatible code migration |
| Durable facts | What may carry across tasks? | Wrong entity, stale fact, missing provenance |
| Episodes | Which past attempts are useful examples? | Leakage, misleading similarity, success-only selection |
| Procedures/skills | What method should a worker follow? | Outdated rule, unsafe generated procedure, unreviewed promotion |
| Retrieval index | How can stored material be found? | Missing permission filter, stale index, weak recall |
| Provider prompt cache | Which request work may the provider reuse? | Mistaking cache lifetime for application persistence |

This table is engineering synthesis. These categories can share storage but need separate contracts and tests. Provider caching details require provider-specific documentation; this comparison does not infer them from an agent's memory files.

## File memory is a legitimate alternative to a mandatory vector database

Current Letta MemFS documentation describes a Git-backed repository projected onto the execution computer. Core files enter the system prompt; indexed subdirectories are read on demand. It explicitly says no semantic/vector index is included by default. Optional search and conversation-history search are separate features, with cloud/local differences. Git also provides history and synchronization; local-only backups remain the operator's responsibility. [MemFS, Memory structure, Semantic and vector search, Versioning](https://docs.letta.com/concepts/memfs/index.md). Evidence C16–C17.

**Construction inference:** choose retrieval from access patterns. A small curated fact file can be cheaper to inspect and update than an embedding pipeline. A large heterogeneous corpus may need filtering, keyword search, embeddings or hybrid retrieval. An index does not decide whether a retrieved statement is true, current or authorized for the current job.

RAG's original paper combines a parametric generator with an external non-parametric retrieval component for knowledge-intensive tasks. That is a retrieval-generation architecture, not by itself a session recovery or memory-write policy. Its reported experiments do not establish the right retrieval method for our workload. [RAG paper](https://arxiv.org/abs/2005.11401). Evidence C18.

## Historical ideas and current implementation should remain separate

MemGPT v2 proposes managing multiple memory tiers and moving information into limited model context, borrowing an operating-system analogy. Its abstract reports document-analysis and multi-session-conversation evaluations. This motivates explicit context movement; it does not prove current Letta behaves exactly like that research implementation, or that any product has unlimited model attention. [MemGPT v2](https://arxiv.org/abs/2310.08560v2). Evidence C19.

Current Letta conversations share the agent's durable identity/memory but retain their own message contexts. The documentation says compaction can omit exact wording and provenance, while history remains searchable. A long-lived conversation is therefore not a claim that every historical token is simultaneously in the model request. [Conversations, Conversation context and agent memory](https://docs.letta.com/concepts/conversations/index.md). Evidence C20.

## Concrete documentation drift: what is always in context?

The current SDK memory page says creation entries land under `system/` and those files are always in context. The current MemFS page describes root files as core memory, with `system/` for older agents. The pinned local implementation resolves a specific part of this mismatch: `detectMemoryFormat` distinguishes v2 using root `MEMORY.md`; `isCoreMemoryPath` chooses root Markdown for v2 and `system/` for v1. The local initializer explicitly creates v2 root files and rejects path collisions. [SDK memory](https://docs.letta.com/agent-sdk/memory/index.md), [pinned format logic, lines 4–20](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/agent/memory-format.ts#L4), [pinned local initializer, lines 78–115](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/backend/local/initial-memory.ts#L78). Evidence C21–C23.

**Limit:** this verifies the selected local path, not all hosted agent migrations or every SDK creation route. Preserve both version/layout facts; do not silently generalize one page to every deployment. The lesson is to test actual prompt assembly after upgrades, not to trust a filename convention.

## Budgeting and compaction need protocol-aware policies

Pi's pinned defaults enable compaction with a 16,384-token reserve and a 20,000-token recent-history target. `shouldCompact` compares estimated usage with the model window minus reserve. The estimator uses valid provider usage where appropriate, estimates trailing messages, and invalidates stale accounting after context edits/compaction. Cut selection avoids beginning at a tool result. These are this snapshot's choices, not universal recommended values. [Pinned compaction source, lines 120–269 and 390–437](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/compaction/compaction.ts#L120). Evidence C24–C26.

Letta's inspected local compaction module has full and sliding-window modes, a sliding-window default, summary limits, overflow fallback handling and a progress check that rejects compaction which reduces neither message count nor estimated tokens. These are local implementation paths, not measured summary quality or every hosted backend's policy. [Pinned local compaction, lines 22–92](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/backend/local/compaction.ts#L22). Evidence C27.

**Construction inference:** reserve space for completion and likely tool output before the hard limit. Keep unresolved constraints, evidence identifiers, authorization scope and unfinished actions structured outside a free-form summary. Test summaries for omission and false certainty. After compaction, check actual prompt size again; a huge system prompt or tool schema can remain irreducible even after discarding conversation text.

## Memory writes are changes to future behavior

Letta's dreaming documentation describes background agents that consolidate recent conversations into memory and an optional second agent review of proposed updates. That review consumes model work and is not human approval. Current SDK options distinguish trigger, interval and behavior. [Memory and dreaming](https://docs.letta.com/configuration/memory/index.md), [SDK memory, Dreaming](https://docs.letta.com/agent-sdk/memory/index.md). Evidence C28–C29.

**Construction inference:** background work trades foreground latency against delayed freshness, additional cost and concurrent writes. A reviewed proposal is still fallible. Use provenance, entity/task scope, timestamps, conflict handling and revocation. Deleting one live memory file may leave history, indexes, summaries, logs or replicas: define and verify the intended deletion scope separately. Git history is useful for rollback and may also retain material the live view no longer shows.
