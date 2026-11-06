# Broader construction patterns

Checked October 18, 2026. This study widens the engineering reference beyond Hermes and OpenClaw. It compares mechanisms rather than declaring a winning framework or a universal industry standard.

Read [execution and durable state](EXECUTION_STATE.md), then [memory and context](MEMORY_CONTEXT.md), the [implementation traces](REFERENCE_TRACES.md), and [design questions and experiments](DESIGN_QUESTIONS.md). [Evidence records](evidence.json) identify the support and limits of substantive findings. [Source receipts](sources.json) record inspected artifacts and hashes; full downloaded public sources stay in the ignored research cache.

## Why these references

| Reference | Engineering question it illuminates | Evidence boundary |
| --- | --- | --- |
| LangGraph | How can an adaptive worker sit inside recoverable execution, with pauses, parallel branches and explicit state? | Official documentation plus selected Python implementation paths; not a full runtime audit |
| Pi | How can a small tool loop, message conversion and append-only session projection remain separate components? | Pinned TypeScript source and accompanying documentation; not installed or executed |
| Current Letta harness | How can editable files, shared identity, conversation context and background memory work remain distinct? | Current documentation plus selected local-backend source; cloud behavior is documentation-only |
| Historical MemGPT and RAG papers | Which memory ideas predate present products, and which questions do they actually address? | Scoped research descriptions; original experiments were not reproduced |

These are examples, not ingredients we must adopt. A narrow, bounded job may need neither multi-agent orchestration nor a vector database. A long-running shared service may need stronger durability, access controls and memory governance than a local coding session.

## Reproducible identity

- Pi: the old `badlogic/pi-mono` URL redirects to `earendil-works/pi`; source pin `c268154ca1171c2f9eefe75d3d7372a68aada2d5`.
- LangGraph: `langchain-ai/langgraph`, source pin `0eb194fe6093812243de2249e7092029c87c8820`.
- Letta harness: `letta-ai/letta-code`, source pin `6e2081fa9d7b6bb54bbaab365e24f142e7ad382b`.

These were default-branch snapshots retrieved on the checked date, not a claim that these are stable releases or the dependencies of another product. Mutable website documentation is separately identified; source pins do not pin those websites.

## Important boundaries

No packages or agents were installed, provider calls made, personal channels connected, Docker started, or benchmark content accessed for this comparison. Static source inspection establishes visible control paths, not observed production reliability. Proposed tests and engineering recommendations are explicitly synthesis. No exhaustive knowledge claim is made: deployment, model quality, privacy obligations and workload behavior require their own verification.
