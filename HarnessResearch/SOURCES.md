# Primary foundations and source status

General chapters are engineering analysis grounded in these primary sources; proposed contracts and tests are our synthesis. Product-specific behavior is recorded separately in the pinned case-study ledgers. Documentation support, static code traces, inspected tests and executed synthetic tests are different evidence categories. No exhaustive runtime or security audit is claimed.

<a id="g01"></a>
## G01 — MCP architecture

[MCP architecture](https://modelcontextprotocol.io/specification/2026-07-28/architecture)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Host/client/server responsibilities; security boundaries

**Supported mechanism:** MCP separates host, client and server responsibilities; the host controls cross-server context and security boundaries.

**Limit:** Protocol architecture does not implement an entire harness, workflow policy or safe deployment.

<a id="g02"></a>
## G02 — MCP security best practices

[MCP security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Confused deputy; token passthrough; SSRF; session/security considerations

**Supported mechanism:** The guidance identifies audience-validation/token-passthrough and network/session attack risks in MCP deployments.

**Limit:** Guidance and protocol rules are not evidence that a particular deployment enforces them; authorization details depend on the transport/version.

<a id="g03"></a>
## G03 — OpenAI function calling

[OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Function-calling flow; tool calls and tool outputs

**Supported mechanism:** Function calling separates model-requested operations from application execution and subsequent tool-result input.

**Limit:** A generated call or schema-valid argument is not authorization, successful execution or an observed business outcome.

<a id="g04"></a>
## G04 — OpenAI conversation state

[OpenAI conversation state](https://developers.openai.com/api/docs/guides/conversation-state)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Manual state; Responses state/conversation patterns

**Supported mechanism:** Applications can carry conversation state explicitly or use supported service-managed state mechanisms.

**Limit:** Specific chaining/retention behavior is provider/API-specific; saved history is not automatically a task database or universal context guarantee.

<a id="g05"></a>
## G05 — OpenAI compaction

[OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Server-side compaction; standalone output handling

**Supported mechanism:** The current guide distinguishes server-side and standalone compaction and describes opaque encrypted carry-forward items with route-specific continuation handling.

**Limit:** Opaque items are not editable semantic-memory notes. Follow the chosen API's output/chaining contract; do not generalize manual pruning across routes.

<a id="g06"></a>
## G06 — OpenAI prompt caching

[OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Reusable rendered prefix; cache location; compaction/cache interaction

**Supported mechanism:** Prompt caching reuses eligible model computation for a matching rendered prefix. Compaction may change that prefix.

**Limit:** Caching is not durable knowledge storage or a larger context window. Rates, thresholds, retention and support are model/account/version-dependent and are not fixed recommendations here.

<a id="g07"></a>
## G07 — OpenAI agents overview

[OpenAI agents overview](https://developers.openai.com/api/docs/guides/agents)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Agents API / Agents SDK / Responses comparison

**Supported mechanism:** The guide distinguishes managed harness infrastructure, an application-controlled SDK runner and lower-level model/tool integration.

**Limit:** The guide describes specific OpenAI products; these layers are comparison examples, not a selection of our provider or runtime.

<a id="g08"></a>
## G08 — OpenAI: Building Reliable Agents with Memory and Compaction

[OpenAI: Building Reliable Agents with Memory and Compaction](https://developers.openai.com/cookbook/examples/agents_sdk/building_reliable_agents_memory_compaction)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Compaction versus memory; reviewed investigation artifacts

**Supported mechanism:** The synthetic cookbook separates current-run continuity, cross-run workflow memory and reviewed output artifacts.

**Limit:** A teaching example does not prove every summarized fact is preserved or establish healthcare validity/our project performance.

<a id="g09"></a>
## G09 — Anthropic: Effective context engineering for AI agents

[Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Context curation; compaction; structured notes; sub-agent architectures

**Supported mechanism:** Describes selective context assembly, compaction, external notes and focused sub-agent contexts as techniques for finite-context work.

**Limit:** Engineering guidance is not a universal optimal context policy; tradeoffs must be evaluated on actual tasks.

<a id="g10"></a>
## G10 — Anthropic: Effective harnesses for long-running agents

[Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Initializer/incremental worker; progress artifacts; testing; future work

**Supported mechanism:** Reports a long-running coding workflow using durable progress/requirements artifacts and incremental verified work across sessions.

**Limit:** The article presents one coding-oriented approach and explicitly leaves broader generalization and team structure open. Its filenames/architecture are not requirements for our system.

<a id="g11"></a>
## G11 — Anthropic: Writing effective tools for agents

[Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Purpose/namespacing; meaningful bounded responses; tool evaluation

**Supported mechanism:** Discusses agent-facing tool purpose, descriptions, response content and evaluation instead of merely exposing every low-level endpoint.

**Limit:** Reported ergonomic/performance observations are task/model-dependent; preserve required identifiers and authoritative state in our own contracts.

<a id="g12"></a>
## G12 — Anthropic: Code execution with MCP

[Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Programmatic tool access; filtering intermediate results; execution environment

**Supported mechanism:** Describes executing orchestration code to discover/call tools and filter intermediate data before it enters model context.

**Limit:** A code-execution design adds a runtime/security boundary and is an alternative to direct tool calls, not a required harness ingredient.

<a id="g13"></a>
## G13 — Anthropic: Advanced tool use

[Anthropic: Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Tool search; programmatic tool calling; usage examples

**Supported mechanism:** Describes tool discovery and programmatic use patterns that reduce the need to load every schema/intermediate result into active context.

**Limit:** Feature availability and provider API details are product-specific; a generic harness needs adapter/capability negotiation rather than assuming all providers support them.

<a id="g14"></a>
## G14 — Anthropic: Demystifying evals for AI agents

[Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Trials, tasks, graders and traces; agent evaluation practices

**Supported mechanism:** Distinguishes evaluating task outcomes from inspecting trajectories and discusses the practical difficulty of evaluating stochastic tool-using systems.

**Limit:** It does not supply our evaluation set or establish any local pass rate. Our test proposals and executed synthetic checks must remain separate.

<a id="g15"></a>
## G15 — AWS Builders' Library: Making retries safe with idempotent APIs

[AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

**Status:** PRIMARY_ENGINEERING_ACCOUNT_READ; checked 2026-10-18

**Inspected location:** Unique caller-provided request identifier; atomic mutation/dedupe; same key/different intent; retention

**Supported mechanism:** Describes request-identity contracts and atomic deduplication with the associated mutation, including parameter mismatch and retention considerations.

**Limit:** This applies where the actual receiving service supports the contract. A local checkpoint cannot make an arbitrary external service execute exactly once.

<a id="g16"></a>
## G16 — SQLite transactional guarantees

[SQLite transactional guarantees](https://www.sqlite.org/transactional.html)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Atomic, consistent, isolated and durable transactions

**Supported mechanism:** Documents transactional behavior for SQLite storage.

**Limit:** Storage guarantees depend on the documented platform/filesystem/settings assumptions and do not atomically include unrelated remote services.

<a id="g17"></a>
## G17 — SQLite write-ahead logging

[SQLite write-ahead logging](https://www.sqlite.org/wal.html)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Concurrency; checkpointing; same-host assumptions; disadvantages

**Supported mechanism:** Describes WAL readers/writer concurrency, checkpoints and deployment restrictions.

**Limit:** WAL is not a guarantee of unlimited concurrent writers or a substitute for application-level ownership, supported filesystem behavior and backups.

<a id="g18"></a>
## G18 — Stripe idempotent requests

[Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)

**Status:** OFFICIAL_DOCUMENTATION_READ; checked 2026-10-18

**Inspected location:** Idempotency keys; v1/v2 response semantics; retention and parameter validation

**Supported mechanism:** Provides a concrete service-specific example of request keys, response replay and version-sensitive retry behavior.

**Limit:** Do not assume every tool uses Stripe's rules, retention period or semantics; this research does not perform any Stripe call.

## Versioned implementation evidence

[Hermes registry](hermes/evidence.json) and [OpenClaw registry](openclaw/EVIDENCE.md) link to exact commits, paths and line ranges. [Broader comparison](comparative/README.md) adds Pi, LangGraph and Letta plus scoped historical research; its [24 source receipts](comparative/sources.json) preserve hashes and current-versus-historical boundaries. [Pinned identities](source_versions.json) identify the two complete local checkouts; comparative source snapshots record their own repository pins.

Full source checkouts/public-page snapshots remain ignored. Hashes identify captured material; they do not prove factual entailment. General-source cache capture status is in verification/foundation_capture_receipt.json when run and is distinct from official web pages actually inspected during research.
