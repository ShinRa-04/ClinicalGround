# Durable memory, retrieval and learning

General design analysis. Retrieval and memory are policies over stored evidence, not magic extensions of model weights. Writing a note does not retrain a model; loading it later changes the inference input. Reusable skills change future procedure through instructions/tools unless a separate training process is actually run.

## A full lifecycle

Define: **observe → admit → store → index → retrieve → rank → inject → use → correct/consolidate → expire/delete**. Each transition can fail independently. A memory system is incomplete if it specifies only an embedding function or only a file where an agent can write.

Observation needs source, timestamp, principal and confidence/status. Admission decides whether content belongs in a temporary episode, task record, durable fact, profile preference, reusable procedure or nowhere. The caller's current goal can justify using a fact without granting it permanent influence over all future sessions.

Maintain the distinction between user-stated instructions, observed external facts, model interpretations and quoted untrusted material. A malicious web page summarized by an agent does not acquire instruction authority merely because an internal process rewrites it. Trust, permissions and source lineage should survive transformation rather than reset at each summary.

## Retrieval alternatives

| Method | Useful for | Important limit |
| --- | --- | --- |
| Exact IDs/structured queries | Case/record lookup and explicit filters | Requires reliable metadata |
| Lexical/FTS search | Exact names, error strings, known terms | Synonyms and paraphrases can be missed |
| Dense semantic retrieval | Conceptual similarity | Similarity is not correctness or authorization |
| Hybrid lexical+dense | Complementary candidate discovery | Fusion weights need evaluation |
| Reranking | Refines a candidate set | Cannot recover omitted candidates by itself |
| Graph/relationship traversal | Explicit links and dependencies | Maintenance/error propagation costs |
| File navigation/lazy loading | Small inspectable workspaces | Needs useful indexes and disciplined retrieval |
| Model-guided search | Multi-step ambiguous questions | More inference, variable paths and unverifiable summaries |

No vector database is mandatory. A well-scoped lexical or structured lookup may outperform a complex retrieval stack for identifiers. A retrieval system should be judged on the actual queries and downstream actions, not the presence of fashionable components. See the [broader-system comparison](../comparative/README.md) for contrasting implementations.

## Candidate ranking is not admission or truth

Relevance, recency, diversity, frequency and user affinity are ranking signals. None alone proves a fact true or safe to inject. Repeated retrieval can amplify an initially wrong statement if frequency is allowed to promote trust. Distinguish corroboration by independent evidence from many derivative records copied from one source.

Filter by principal/scope before disclosure, and recheck authorization on source reads rather than assuming an old index result still grants access. Preserve exact source locators and timestamps so a recipient can inspect evidence. A search hit's score is not a probability that a clinical or business claim is valid.

## Consolidation and contradictions

Background consolidation can merge duplicates, organize episodes, supersede stale facts and maintain compact profiles. It can also erase qualification, fuse different people/cases, import malicious instructions or overgeneralize a one-off preference. An implementation should expose what was proposed, what source supported it, which scope changed, which version was replaced and how to undo it.

Store contradictions when they are genuinely unresolved. “Latest statement wins” is a policy that may suit some user preferences but fail for authoritative records or conflicting sources. “Most frequently mentioned wins” can be vulnerable to duplication or poisoning. A bounded review/approval process is an alternative for high-consequence durable changes; whether approval is required follows actual product/user policy, not a universal rule invented here.

## Consistency and deletion

An asynchronous index can lag behind a write. Record source/index versions or readiness where freshness matters. Updating a source file, embeddings and profile summary in separate operations can leave mixed versions. Choose whether to fail closed, serve the older committed snapshot, or expose partial freshness explicitly.

Deletion must consider raw events, daily notes, consolidated profiles, indexes, caches, derived skills and future ingestion. Source-based tombstones can prevent regeneration from a retained episode. Backups and audit retention need their own policy. Revoking one result in the UI is not proof that all derived forms have been removed.

## Learn procedures without teaching the wrong lesson

A procedural memory entry should describe the task class, prerequisites, evidence of success, applicable tool/version assumptions, limits and a revision history. Do not turn an unverified run narration into a global instruction. Do not store a task-ID answer key as a “general skill” and claim improved generalization. Evaluate transfer on cases not used to choose the procedure. [G08/G10/G14](../SOURCES.md#g08).

For our future harness, memory selection should follow the actual problem: preserve authoritative case facts in case state, reusable workflow knowledge in reviewed procedures, user preferences in scoped profiles, and recoverable experiences in a searchable log. That is a design principle, not a selection of Hermes, OpenClaw or any particular database.
