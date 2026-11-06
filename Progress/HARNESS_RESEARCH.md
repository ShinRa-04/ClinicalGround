# Harness engineering research

## Authorized request

October 18, 2026: extensively research how contemporary agentic harnesses are built, explicitly Hermes Agent and OpenClaw, including memory and context management, in a new root folder. Create a durable, navigable source-backed engineering reference and preserve uncertainty/version boundaries. Existing authorization to commit project research/continuity changes applies.

## Scope and definition of done

Study pinned official sources, not search snippets or third-party summaries alone. Cover execution/control loop, model/provider boundary, prompt/context construction, token budgets, caching, pruning/compaction, durable/episodic/procedural memory, retrieval/indexing, provenance/deletion, sessions/concurrency, tool execution, sandbox/permissions, sub-agents, schedules/gateways, recovery, observability, evaluation, extensibility and a practical construction/testing roadmap.

Acceptance gates: (1) official repository identities and pins recorded; (2) both deep dives trace core memory/context/control paths with durable locators; (3) cross-system comparison distinguishes defaults, optional backends, documentation drift and untested assumptions; (4) construction guide includes state/data contracts, failure recovery and verification; (5) substantial findings have evidence/status/limits; (6) independent review and local consistency checks recorded; (7) reading index/handoff updated and all research changes committed. Breadth is explicit, not a promise of literally knowing every implementation detail.

## Constraints and ownership

Keep Docker closed, all browser work non-visible, source repositories local-only/ignored, and credentials/protected data out of tracked files. Do not install or start Hermes/OpenClaw, connect personal messaging accounts, execute provider calls, inspect hidden benchmark expectations or change benchmark setup. Static code inspection and bounded isolated non-network tests are allowed where dependencies permit.

The iterate-until-verified skill explicitly calls for independent workstreams/review when useful and permitted. Main agent integrates; research workstreams and reviewer ownership will be recorded here. No external messages or separately created user chats are authorized.

## Initial state and user steering

Prior organization study is committed as a1ec02f. New root HarnessResearch/ created. Official identities being verified: NousResearch/hermes-agent and openclaw/openclaw. Checkouts/pins, subsystem traces and review are in progress. No coverage/implementation/runtime claim is complete yet.

User steering: the PRIMARY objective is GENERAL engineering knowledge, not importing two products' designs. Learn from reference implementations without following them as the blueprint for our project. Do not claim they are formal standards or universally dominant without evidence. Build a wider mechanism/design-space reference and derive any future design from our own requirements.

Ownership: /root integrates the general handbook, source/coverage registry and construction guide; /root/hermes_source_audit owns Hermes reports; /root/openclaw_source_audit owns OpenClaw reports. Both were informed of the general-learning priority. Each agent edits only its own report directory and leaves upstream sources unchanged. Independent review will follow integration.

## Completed research publication

The defined general engineering study is complete. It lives in root HarnessResearch/ with **12 general chapters** and a **38-topic coverage map**, plus source case studies and practical construction/failure contracts. Read the general learning path before the product examples. No architecture, provider, framework, memory backend or agent count is selected by this study.

Published evidence: 18 general primary sources with captured-page hashes; 60 scoped Hermes findings; 75 scoped OpenClaw findings; 35 broader comparative findings and 24 source receipts covering Pi/LangGraph/current Letta plus scoped historical research. The 170 implementation/comparative findings separate code traces, documentation, inspected tests and one documentation ambiguity. Reference source pins remain unchanged and clean; selected comparative snapshots record their own pins. No source inspection is represented as an upstream runtime pass.

General content covers the execution kernel; distinct memory/state/context/checkpoint/cache resources; provider and streaming semantics; context budgets/projections/compaction; retrieval/admission/consolidation/provenance/deletion; tool contracts/permissions/sandbox; ownership/replay/unknown effects; queues/delegation/schedules; observability/evaluation/migration; and independent construction choices/data contracts. Twenty-eight proposed failure scenarios support future testing. The skill-selected independent reviewer found and reported real integration issues instead of providing a blanket correctness claim.

## Executed checks

- Integrator synthetic lab: **17 tests passed**, zero failures/errors/skips, Python 3.12.14. Reviewer separately ran the same 17 tests with Python 3.11. These are repeated runs of the same bounded fixtures, not upstream tests or 34 unique behaviors.
- Independent identity check: 135 Hermes/OpenClaw source ranges/hashes plus 24 comparative cache hashes = 159 checks, zero failures. The semantic review sampled consequential memory/context/recovery/security/default claims and reopened selected official foundations; it was not exhaustive.
- Final integrated validator: **177 source identities**, **538 Markdown links**, **410 anchor targets**, 41 authored Markdown documents, 38 known-ID topic mappings; passed. Both complete source checkouts stayed clean. The checker prunes ignored source/cache trees to avoid needlessly scanning tens of thousands of upstream files.
- Independent R1 incorrect coverage citations were corrected and rechecked. R2 diagram confirmation was made conditional, with an explicit inconclusive branch and bounded-attempt prose. Integrator dispositions preserve both findings and corrections without rewriting the review history.

Receipts: HarnessResearch/verification/; independent review and integrator responses: HarnessResearch/review/. All remaining final integration was performed by the main chat, with no additional agent review round.

## Cost and execution steering

User noted all research agents inherited 6.1 Sol/High and requested cheaper Luna agents for information collection, with review/consolidation in the main chat after existing agents finished. All agents have finished. Future delegated collection for this work should use Luna if needed; do not repeat broad High-agent review loops. The main chat owns final organization/checks. User instructions override the earlier skill's generic delegation suggestions.

The Hermes worker wrote its artifacts before an account usage limit interrupted final workstream checks; a fresh independent reviewer and the integrator completed the recorded source checks. This is documented rather than attributing a successful final worker run that did not occur.

## Limits and continuation

No reference application was installed/started, provider/model called, personal service connected, Docker or visible browser launched, protected handbook/hidden verifier inspected, upstream test suite executed or healthcare benchmark trial run. The sequential synthetic lab does not prove semantic summary fidelity, real tokenizer accuracy, authentication, global erasure, concurrent/distributed fencing, power-loss safety or exactly-once external effects. Every such boundary is explicit in the lab and verification guide.

This is extensive bounded knowledge, not a promise of literally knowing every release/plugin/deployment. Future design should start from our own actual requirements and failure modes, then select and test mechanisms; it should not reproduce Hermes/OpenClaw defaults by analogy. Public-task/tool mapping and empirical harness implementation/evaluation remain separate unperformed work. Preserve source pins and revalidate changed evidence on a refresh.

All research/continuity files are recorded in the dedicated final research commit; consult git log. Local source checkouts, raw page caches and unrelated dataset archives are excluded.
