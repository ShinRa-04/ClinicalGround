# Agentic harness engineering research

Started October 18, 2026. User requested extensive source-backed study of modern harnesses, explicitly Hermes Agent and OpenClaw, including memory and context management, in a new root folder. This is a research/engineering handbook, not an installation of either product or an implemented healthcare harness.

The study distinguishes documentation claims, behavior traced in a pinned source commit, existing tests inspected, locally executed checks, design inferences and unresolved questions. The [38-topic coverage matrix](COVERAGE.md) makes the studied scope explicit. No claim to exhaustive knowledge of every release, plugin, deployment or proprietary system is justified.

Main questions: how a harness turns model calls into reliable execution; how context is assembled and budgeted; what survives compaction/reset/restart; how durable memory is written, retrieved, scoped and deleted; how tools, sessions, sub-agents, approvals, queues, errors and termination interact; and how to build and evaluate these mechanisms.

Local-only upstream checkouts and research caches live under ignored _sources/ and _cache/. Tracked evidence will link to exact commit/file/line ranges and record source hashes. No provider calls, Docker, visible browser windows, protected benchmark handbook or hidden verifier inspection is required. No final model/framework choice or product installation is selected by this study.

The healthcare role and organization studies remain separate under Plan/HealthcareRoles/ and Plan/AgentOrganization/. Their hypotheses can be revisited after this engineering study; they are not implementation requirements imposed on the upstream projects.

User clarification: **general harness-engineering knowledge is the primary goal**. Hermes and OpenClaw are reference implementations to learn from, not the system we are making or specifications to copy. Their adoption or status as formal industry standards has not been independently established here. General chapters must explain mechanisms, alternatives, tradeoffs and failure conditions across a wider design space. Our eventual architecture must derive from our own requirements and evidence, not follow either project by default.

## General learning path

Read the mechanism chapters first. Reference implementations then provide concrete ways to check and challenge the ideas.

| Chapter | What it teaches |
| --- | --- |
| [1. Anatomy and control](general/01-anatomy-and-control.md) | Model versus harness; logical components; turns, loops, workflows and completion |
| [2. State, memory and sessions](general/02-state-memory-and-sessions.md) | Events, task state, checkpoints, summaries, profiles, episodes, procedures, indexes and cache |
| [3. Context budgets and compaction](general/03-context-budget-and-compaction.md) | Rendered requests, effective limits, selection, atomic tool exchanges, compression alternatives and failure recovery |
| [4. Memory, retrieval and learning](general/04-memory-retrieval-and-learning.md) | Admission, scope, lexical/vector/file alternatives, ranking, consolidation, trust, correction and deletion |
| [5. Tools, execution and trust](general/05-tools-execution-and-trust.md) | Tool contracts, actual authorization, approvals, sandboxing, MCP and effect boundaries |
| [6. Durability, replay and recovery](general/06-durability-replay-and-recovery.md) | Unknown outcomes, idempotency, checkpoints, replay, ownership fences and fault injection |
| [7. Orchestration and delegation](general/07-orchestration-concurrency-and-delegation.md) | Role modes, workers, graphs, queues, admission, budgets, cancellation and schedules |
| [8. Providers and performance](general/08-providers-streaming-and-performance.md) | Typed adapters, streams, continuation ownership, retries, caching and resource tradeoffs |
| [9. Evaluation and maintenance](general/09-observability-evaluation-and-maintenance.md) | Traces, task/trial/grade distinctions, context/memory evaluation, experiments and upgrades |
| [10. Construction guide](general/10-construction-guide.md) | Deriving a design from requirements, interfaces, extension types and staged validation |
| [11. Data contracts and failure catalog](general/11-data-contracts-and-failure-catalog.md) | Proposed records/invariants and 28 failure scenarios |
| [12. Design questions and learning map](general/12-design-questions-and-learning-map.md) | Decision questions, a practical learning sequence, glossary and knowledge limits |

[General mechanism diagrams](ARCHITECTURE_MAPS.md) summarize the boundaries. The [synthetic lab](labs/README.md) makes selected invariants executable with no model/network; it is not our eventual harness.

## Reference cases and evidence

- [Hermes source study](hermes/README.md): execution, context/cache, several memory surfaces, sessions/profiles, delegation, skills and operations at a fixed source pin.
- [OpenClaw source study](openclaw/README.md): built-in/native runtime boundaries, session/state ownership, pruning/compaction, memory/provenance/consolidation, tools and operations at a fixed source pin.
- [Broader construction patterns](comparative/README.md): Pi, LangGraph and current Letta mechanisms, with historical MemGPT/RAG ideas kept separate from current implementations.
- [Primary foundations](SOURCES.md): 18 official documentation/engineering sources, including provider state, MCP, distributed retries, transactional storage and evaluation.
- [Finding index](FINDINGS_INDEX.md): 170 individually scoped implementation/comparative findings, with status, exact source locator and limits. Static traces and inspected tests are not runtime/test passes.
- [Verification and review](VERIFICATION.md): actual local checks, independent review scope and what remains untested.

The checkouts and selected source snapshots are pinned research material, not installed applications or selected dependencies of our future system. Mutable documentation has a checked date rather than a permanent behavior guarantee.

## What this study establishes

It provides a general conceptual/design map, source-level examples, practical construction contracts, failure questions and bounded executable checks. It supports explaining and comparing mechanisms instead of importing a product architecture. It does not establish an optimal worker count, the best memory backend, perfect summary fidelity, end-to-end exactly-once effects, a secure deployment or improved χ-Bench performance.

No Hermes/OpenClaw/framework runtime, provider call, personal channel, Docker environment or benchmark trial was started. The next design work should select requirements and test alternatives for our own task, not reproduce the reference defaults.

## Reproduction

The source identity checks require ignored pinned checkouts/snapshots. Reading the committed handbook does not require them. `tools/build_index.py` publishes the indexes/coverage; `tools/run_labs.py` runs only the synthetic stdlib lab; `tools/validate_research.py` checks source identities, record consistency and navigation. Details and receipts are in VERIFICATION.md. Do not automatically update source pins while claiming the original findings still apply.
