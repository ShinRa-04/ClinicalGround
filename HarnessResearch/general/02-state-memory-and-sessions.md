# State, memory and sessions are different resources

“Memory” is an overloaded label. To reason about construction, identify **what is stored, who owns it, how it becomes model input, what it means, and how it is invalidated**. A storage backend alone does not answer these questions.

## The main stores

| Resource | Typical contents | Durability / meaning |
| --- | --- | --- |
| Active model context | Selected instructions, conversation items, tools, retrieved excerpts | View for one inference request; not necessarily complete history |
| Event/transcript log | Inputs, assistant/tool events, outcomes and metadata | Evidence of what happened; can be append-oriented or transactionally stored |
| Execution checkpoint | State/version, pending tasks, program position, outstanding calls | A recovery point; not necessarily an external-world snapshot |
| Task/domain state | IDs, obligations, observed workflow state, versions | Operational truth according to authoritative sources |
| Working summary | Compressed continuity information and unresolved requests | Derived, potentially lossy; not a new authority |
| Episodic memory | Prior interactions/events with time/source references | Recalled experiences, often indexed on demand |
| Semantic/profile memory | Maintained facts, preferences, relationships | Claims with scope and freshness requirements |
| Procedural memory/skills | Reusable instructions, workflows, examples or executable helpers | Changes behavior; requires provenance/version control |
| Retrieval index | Chunks, embeddings, lexical postings, source pointers | Derived search structure; can lag or be rebuilt |
| Prompt/KV cache | Reusable model computation over an eligible prefix | Provider/runtime performance resource, not durable knowledge |
| Artifact/workspace | Documents, code, files, receipts, reviewed results | Output/evidence with its own lifecycle and permissions |

An event log can be long while the active context is short. A memory file can exist without being loaded. A retrieved record can be loaded without being true. A checkpoint can be durable while a remote action's status is unknown. Prompt cache reuse does not create a semantic profile or increase the model's window. These are distinct contracts, not interchangeable database names. [G04–G08](../SOURCES.md#g04).

## Canonical state versus a projection

Treat the model input as a projection constructed from authoritative and derived stores. A projection can omit irrelevant records, replace old tool output with a handle, insert a summary or retrieve a few earlier episodes. That does not require erasing the original events. Conversely, some systems persist only transformed history; inspect their actual retention and recovery behavior instead of assuming the originals survive.

State corrections should preserve whether they amend a source fact, revise an interpretation or merely change the next prompt view. A short summary that says a request was approved must not overwrite a domain record that says the decision is pending. A model's working belief is not a database constraint.

## Identity and scope

Define user/tenant, organization, workspace/project, agent, session, run, task/case, branch and tool-call identity separately where needed. A session ID is an address, not automatically an authorization token. One user may use several sessions; one case may involve several actors; a delegated child can have its own run while sharing a scoped subset of its parent's task.

Memory admission and retrieval should use explicit namespaces and principal permissions. “This agent remembers it” is not enough: should it remember across cases, projects or users? Should a child inherit the parent's profile? Can a scheduled job write the user's durable preferences? Product defaults answer particular deployment assumptions, not all these questions universally.

## Lifecycle operations need precise meanings

**Reset** can clear active history, start a new conversation identity, reset task state, or all three. **Resume** can reload an event log, restore a checkpoint or reconstruct a model projection. **Fork** can share past events while separating future state. **Archive** may preserve retrievability. **Forget** may remove a selected memory while leaving transcripts, derived summaries, vectors, caches or backups intact. Design and document these operations explicitly.

A useful deletion model tracks origins from events through chunks, summaries, profiles and generated skills. Removing one visible line is not complete deletion if later consolidation re-ingests its source. Some legal/operational retention obligations can conflict with deletion requests; this handbook does not resolve those policies. It explains the technical surfaces that a policy must address.

## Storage choices

Files are inspectable and convenient for versioned notes but need atomic replacement/locking and a consistency strategy. An append-only log makes history/replay explicit but needs indexing, schema migration and branch semantics. SQLite can provide transactions and indexes in a local application; its concurrency and filesystem assumptions matter. A network database/workflow service can coordinate distributed workers but adds operational complexity. A vector index supports a retrieval method, not the entire memory lifecycle. [G16/G17](../SOURCES.md#g16).

The general lesson is to choose storage from access, durability, isolation, deletion and recovery requirements. Do not copy a file layout because a popular harness uses it.
