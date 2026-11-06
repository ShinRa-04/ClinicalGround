# OpenClaw scoped evidence registry

Pinned official repository: `3b3492490602f5080d3fbe7d2df9618cdb82ea9a`. Review date: 2026-10-18 (Asia/Calcutta).

Statuses describe evidence strength, not correctness percentages. `code-traced` means the named static path/branch was inspected; `docs-only` means the pinned contract was read without full implementation proof; `test-inspected` means assertions were read without running them. No OpenClaw runtime or upstream test was executed.

The companion JSON includes source-file hashes, exact line ranges and immutable GitHub permalinks. The local checker only establishes pin/locator integrity; it cannot prove runtime behavior or security.

## OC-001

**code-traced** — The pinned checkout declares package version 2026.10.4, MIT licensing, and SQLite/Postgres database capabilities; this is a moving-main source snapshot, not a verified installed release.

[Pinned source: package.json:3-24](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/package.json#L3-L24)

Limit: Static source inspection; not executed in this research.

## OC-002

**code-traced** — The pinned package requires Node >=24.16.0 <25 or >=26.1.0; historical Node 22 guidance must not be substituted for this revision.

[Pinned source: package.json:2465-2469](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/package.json#L2465-L2469)

Limit: Static source inspection; not executed in this research.

## OC-003

**docs-only** — Provider, model, runtime/harness, and messaging channel are separate layers; embedded and external CLI/native backends have different ownership.

[Pinned source: docs/concepts/agent-runtimes.md:10-46](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-runtimes.md#L10-L46)

Limit: Pinned documentation contract; parity of every native adapter was not tested.

## OC-004

**code-traced** — runEmbeddedAgent creates a session lane and global lane, waits for deferred maintenance/projection, then admits work through the global queue.

[Pinned source: src/agents/embedded-agent-runner/run-orchestrator.ts:162-246](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/run-orchestrator.ts#L162-L246)

Limit: Static source inspection; not executed in this research.

## OC-005

**code-traced** — Ordinary child execution lanes are keyed by immediate spawning/controller session; cron nested work receives a distinct lane to avoid a held-lane deadlock.

[Pinned source: src/agents/embedded-agent-runner/lanes.ts:15-46](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/lanes.ts#L15-L46)

Limit: Static source inspection; not executed in this research.

## OC-006

**code-traced** — The built-in loop handles queued messages, continuation preparation, streamed responses, admitted tool batches, provider errors, taint, stop/continuation signals and abort; a text response with endTurn=false can continue.

[Pinned source: packages/agent-core/src/agent-loop.ts:229-403](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/agent-loop.ts#L229-L403)

Limit: Static source inspection; not executed in this research.

## OC-007

**code-traced** — Tool calls are resolved/validated before batch admission; configured sequential execution or a sequential tool constrains a batch, while other calls can use grouped parallel/asynchronous execution.

[Pinned source: packages/agent-core/src/agent-loop.ts:475-554](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/agent-loop.ts#L475-L554)

Limit: Static source inspection; not executed in this research.

## OC-008

**code-traced** — Attempt preparation constructs core/plugin tools and a prepared system prompt, then refreshes the effective prompt tool policy; the model prompt is an assembled runtime product.

[Pinned source: src/agents/embedded-agent-runner/run/attempt.ts:327-441](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/run/attempt.ts#L327-L441)

Limit: Static source inspection; not executed in this research.

## OC-009

**code-traced** — System prompt construction distinguishes full/minimal/none modes and derives sections from runtime capability context; a subagent prompt is not simply a full parent prompt with a new name.

[Pinned source: src/agents/system-prompt.ts:354-438](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/system-prompt.ts#L354-L438)

Limit: Static source inspection; not executed in this research.

## OC-010

**code-traced** — Prompt preparation gates skills and memory sections on callable capabilities and prepares ordered context files/bootstrap sections.

[Pinned source: src/agents/system-prompt.ts:517-613](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/system-prompt.ts#L517-L613)

Limit: Static source inspection; not executed in this research.

## OC-011

**code-traced** — Bootstrap defaults are 20,000 characters per ordinary file and 60,000 total, with a separate 4,000-character USER.md cap; these are character limits, not exact model token counts.

[Pinned source: src/agents/embedded-agent-helpers/bootstrap.ts:87-106](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-helpers/bootstrap.ts#L87-L106)

Limit: Static source inspection; not executed in this research.

## OC-012

**code-traced** — Bootstrap diagnostics distinguish per-file/total truncation and near-limit pressure, using an 85% warning threshold.

[Pinned source: src/agents/bootstrap-budget.ts:122-183](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/bootstrap-budget.ts#L122-L183)

Limit: Static source inspection; not executed in this research.

## OC-013

**code-traced** — System prompt reports account for rendered prompt inputs, context-file injection, tool schema/summary sizes and hashes; a report is observability, not proof the model followed instructions.

[Pinned source: src/agents/system-prompt-report.ts:124-181](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/system-prompt-report.ts#L124-L181)

Limit: Static source inspection; not executed in this research.

## OC-014

**code-traced** — An engine returns ordered messages and an estimated token count, but its estimate does not control host request admission; per-turn and persistent-thread projection are distinct contracts.

[Pinned source: src/context-engine/types.ts:8-50](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/context-engine/types.ts#L8-L50)

Limit: Static source inspection; not executed in this research.

## OC-015

**code-traced** — The implicit memory plugin slot is memory-core and the implicit context-engine slot is legacy; these are distinct replaceable ownership slots.

[Pinned source: src/plugins/slots.ts:17-22](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/plugins/slots.ts#L17-L22)

Limit: Static source inspection; not executed in this research.

## OC-016

**code-traced** — The default legacy engine does not itself persist ingested messages; assembly is pass-through and compaction delegates to the built-in runtime, with existing sanitization/limit/repair downstream.

[Pinned source: src/context-engine/legacy.ts:14-38](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/context-engine/legacy.ts#L14-L38)

Limit: Static source inspection; not executed in this research.

## OC-017

**code-traced** — The context engine contract includes bootstrap, maintenance, ingest/batch-ingest, after-turn, assemble, compact and dispose hooks; host compatibility and lifecycle are part of extension correctness.

[Pinned source: src/context-engine/types.ts:362-548](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/context-engine/types.ts#L362-L548)

Limit: Static source inspection; not executed in this research.

## OC-018

**code-traced** — Transcript mutation scope checks current session ID, lifecycle revision and active writer run ID when the corresponding expected fence is supplied.

[Pinned source: src/config/sessions/session-accessor.sqlite-scope.ts:84-111](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/config/sessions/session-accessor.sqlite-scope.ts#L84-L111)

Limit: Static source inspection; not executed in this research.

## OC-019

**code-traced** — The locked SQLite transcript write guard reads fresh session identity and refuses a rebound/stale fenced writer before committing a protected mutation.

[Pinned source: src/config/sessions/session-accessor.sqlite-transcript-write-guard.ts:54-79](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/config/sessions/session-accessor.sqlite-transcript-write-guard.ts#L54-L79)

Limit: Static source inspection; not executed in this research.

## OC-020

**docs-only** — The documented active store uses durable writer claims and per-agent SQLite writes; the Gateway state-directory lock excludes another owner.

[Pinned source: docs/concepts/agent-loop.md:58-65](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-loop.md#L58-L65)

Limit: Write-guard mechanism separately traced; full cross-process fault behavior was not executed.

## OC-021

**code-traced** — Client cache-TTL pruning is opt-in via mode=cache-ttl; its local resolver defaults TTL to five minutes, hard clear to enabled, and deny/allow tool filters are applied.

[Pinned source: src/agents/embedded-agent-runner/tool-result-truncation.ts:64-98](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/tool-result-truncation.ts#L64-L98)

Limit: Static source inspection; not executed in this research.

## OC-022

**code-traced** — Client soft pruning replaces a large eligible tool result with its first/last 1,500 characters and a trim marker; the operation constructs a projected message.

[Pinned source: src/agents/embedded-agent-runner/tool-result-truncation.ts:154-190](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/tool-result-truncation.ts#L154-L190)

Limit: Static source inspection; not executed in this research.

## OC-023

**code-traced** — Tool-result projections are serialized as hidden openclaw.cache-ttl transcript markers; successful marker commit updates the cached checkpoint, while original tool-result rows are distinct.

[Pinned source: src/agents/embedded-agent-runner/session-prompt-state.ts:348-381](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/session-prompt-state.ts#L348-L381)

Limit: Static source inspection; not executed in this research.

## OC-024

**docs-only** — The pinned pruning guide documents TTL/context thresholds, protected recent assistant turns, persistent projection replay across restart, and unchanged raw tool-result history.

[Pinned source: docs/concepts/session-pruning.md:67-108](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/session-pruning.md#L67-L108)

Limit: Detailed threshold branches not all independently executed; projection persistence separately code-traced.

## OC-025

**docs-only** — The compaction guide still calls pruning in-memory-only, conflicting with the current pruning guide and marker-persistence implementation.

[Pinned source: docs/concepts/compaction.md:407-409](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L407-L409)

Limit: This records a documentation contradiction; use OC-023 and OC-024 for the precise current distinction.

## OC-026

**code-traced** — The low-level library defaults compaction on, reserveTokens=16,384, keepRecentTokens=20,000; these are not necessarily the final host-effective settings.

[Pinned source: packages/agent-core/src/harness/compaction/compaction.ts:163-169](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/harness/compaction/compaction.ts#L163-L169)

Limit: Library defaults inspected; host configuration, reserves, output limits and runtime/provider ownership can override them.

## OC-027

**code-traced** — Compaction planning uses an estimation safety margin of 1.2 and excludes runtime-only context and private tool-result details before message token estimation.

[Pinned source: src/agents/compaction-planning.ts:7-19](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/compaction-planning.ts#L7-L19)

Limit: Static source inspection; not executed in this research.

## OC-028

**docs-only** — Prepared request budgeting considers system instructions, schemas, pending input and output reserve; a larger summarizer does not enlarge the foreground model window.

[Pinned source: docs/concepts/compaction.md:160-184](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L160-L184)

Limit: No live provider tokenization or overflow trial executed.

## OC-029

**docs-only** — History hydration independently bounds serialized replay bytes (8 times context-token budget, at least 1 KiB and at most 64 MiB); omitted stored history is not deleted or summarized.

[Pinned source: docs/concepts/compaction.md:261-282](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L261-L282)

Limit: Hydration implementation not independently exercised; dense events and byte/token mismatch remain relevant limits.

## OC-030

**docs-only** — An opt-in active-transcript byte guard triggers semantic compaction; if it fails or remains oversized, bounded recent history can be used without rewriting/deleting the saved messages.

[Pinned source: docs/concepts/compaction.md:228-258](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L228-L258)

Limit: Byte cap applies to selected active SQLite history, not a universal disk-retention cap.

## OC-031

**code-traced** — Memory Core flush defaults use a 4,000-token soft threshold and 2 MiB transcript-byte pressure; the prompt targets append-only daily notes and treats curated/bootstrap files as read-only.

[Pinned source: extensions/memory-core/src/flush-plan.ts:12-34](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/flush-plan.ts#L12-L34)

Limit: Static source inspection; not executed in this research.

## OC-032

**code-traced** — Memory flush can be disabled; its plan computes effective reserves/soft threshold, optional exact model override and a timezone-resolved daily memory path.

[Pinned source: extensions/memory-core/src/flush-plan.ts:63-108](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/flush-plan.ts#L63-L108)

Limit: Static source inspection; not executed in this research.

## OC-033

**code-traced** — The flush gate records at most one flush per compaction cycle by comparing memoryFlush.compactionCount to the current compactionCount.

[Pinned source: src/auto-reply/reply/memory-flush.ts:169-174](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/auto-reply/reply/memory-flush.ts#L169-L174)

Limit: Static source inspection; not executed in this research.

## OC-034

**docs-only** — Flush failure is documented as nonfatal maintenance; required compaction failure preserves the conversation and reports failure rather than automatically starting over.

[Pinned source: docs/concepts/compaction.md:325-333](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L325-L333)

Limit: No injected flush or compaction failure executed.

## OC-035

**code-traced** — Memory search resolves enabled=true by default; the normal query resolver uses maxResults=6/minScore=.35 with .7/.3 vector/text weights, 4x candidates, enabled MMR lambda=.7, enabled temporal decay half-life 30 days.

[Pinned source: src/agents/memory-search.ts:88-149](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts#L88-L149)

Limit: Static source inspection; not executed in this research.

## OC-036

**code-traced** — Unset or auto memory embedding provider resolves to openai; provider=none is the built-in FTS-only sentinel and avoids semantic provider discovery.

[Pinned source: src/agents/memory-search.ts:71-88](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts#L71-L88)

Limit: Configuration resolution is not credential readiness, a network request, or proof a model was downloaded.

## OC-037

**code-traced** — Built-in memory chunking resolves to 400 tokens with 80 overlap; the embedding cache is enabled by default and bounded to 50,000 entries in this resolver.

[Pinned source: src/agents/memory-search.ts:209-217](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts#L209-L217)

Limit: Static source inspection; not executed in this research.

## OC-038

**code-traced** — Default memory query sources are memory files; session sources depend on session-memory/remember-across-conversations policy, and indexed sources can differ from explicit query sources.

[Pinned source: src/agents/memory-search-source-policy.ts:3-41](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search-source-policy.ts#L3-L41)

Limit: Static source inspection; not executed in this research.

## OC-039

**code-traced** — Hybrid retrieval merges by chunk identity, combines vector/lexical signals, handles path-specific ranking, project affinity and recency; final ranking is more nuanced than one cosine score.

[Pinned source: extensions/memory-core/src/memory/hybrid.ts:137-226](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory/hybrid.ts#L137-L226)

Limit: Static source inspection; not executed in this research.

## OC-040

**code-traced** — MMR reorders candidates using normalized relevance and token-set Jaccard redundancy, controlled by lambda; it is diversity ranking, not a truth verifier.

[Pinned source: extensions/memory-core/src/memory/mmr.ts:28-91](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory/mmr.ts#L28-L91)

Limit: Static source inspection; not executed in this research.

## OC-041

**code-traced** — Recency applies exponential half-life decay to dated/dated-source entries; evergreen root/topic memory paths are exempt. Helper defaults are disabled, but the normal resolver explicitly enables decay.

[Pinned source: extensions/memory-core/src/memory/temporal-decay.ts:15-84](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory/temporal-decay.ts#L15-L84)

Limit: Static source inspection; not executed in this research.

## OC-042

**docs-only** — Memory Core distinguishes instructions, curated core, episodic notes/transcripts, prospective intents/cron and human-only review output; storage and injection policies differ.

[Pinned source: docs/concepts/memory-architecture.md:53-87](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-architecture.md#L53-L87)

Limit: File-oriented memory does not imply all harness state is plain text: index, provenance, sessions and scheduling include database state.

## OC-043

**code-traced** — Origin classification uses host metadata: tainted assistant content is untrusted, assistant derivation of owner content is agent, internal system input is system, explicit owner input is owner, and other input is untrusted.

[Pinned source: packages/memory-host-sdk/src/host/session-provenance.ts:4-24](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/memory-host-sdk/src/host/session-provenance.ts#L4-L24)

Limit: Static source inspection; not executed in this research.

## OC-044

**code-traced** — A tool result declared network-sourced taints later assistant derivations until a new user turn; this mechanism depends on accurate result-source declarations.

[Pinned source: packages/agent-core/src/turn-taint.ts:24-66](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/turn-taint.ts#L24-L66)

Limit: Static source inspection; not executed in this research.

## OC-045

**code-traced** — Promotion rejects untrusted/system provenance; consolidation requires owner/agent origin and interactive kind for session-derived candidates.

[Pinned source: extensions/memory-core/src/dreaming-consolidation-candidates.ts:11-25](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/dreaming-consolidation-candidates.ts#L11-L25)

Limit: Static source inspection; not executed in this research.

## OC-046

**code-traced** — Dreaming default frequency is 03:00 daily; deep defaults include limit=10, minScore=.75, minRecallCount=3, minUniqueQueries=3, 14-day recency half-life and bounded prior-entry loss.

[Pinned source: src/memory-host-sdk/dreaming.ts:21-42](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/memory-host-sdk/dreaming.ts#L21-L42)

Limit: Static source inspection; not executed in this research.

## OC-047

**code-traced** — The dreaming config resolver defaults its sweep and light/deep/REM phases enabled; this still depends on selected memory plugin, running Gateway/cron and eligible candidates.

[Pinned source: src/memory-host-sdk/dreaming.ts:381-445](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/memory-host-sdk/dreaming.ts#L381-L445)

Limit: Static source inspection; not executed in this research.

## OC-048

**code-traced** — Dreaming registration/reconciliation checks scheduler availability/enabled state and warns when cron is unavailable rather than pretending a configured sweep executed.

[Pinned source: extensions/memory-core/src/dreaming.ts:414-444](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/dreaming.ts#L414-L444)

Limit: Static source inspection; not executed in this research.

## OC-049

**docs-only** — Consolidation is documented to compare the memory content hash before atomic replacement, preserve preimages and append a readable review diary; concurrent external edits can cause rewrite abort/fallback.

[Pinned source: docs/concepts/memory-architecture.md:212-227](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-architecture.md#L212-L227)

Limit: Accepted residual filesystem race and recovery are documented; no concurrent-writer stress test executed.

## OC-050

**code-traced** — Memory forget requires session/hook/participant selectors, resolves current source sessions and origin rows, and serializes mutating cleanup with a workspace lock; dry-run follows a nonmutating branch.

[Pinned source: extensions/memory-core/src/memory-forget.ts:81-142](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory-forget.ts#L81-L142)

Limit: Static source inspection; not executed in this research.

## OC-051

**docs-only** — Admission exclusion and retrospective forget are different: forget removes identifiable memory artifacts, not original transcripts, all freeform writes or every retained copy.

[Pinned source: docs/concepts/memory-provenance.md:17-36](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-provenance.md#L17-L36)

Limit: Not a compliance-grade erasure guarantee; no deletion command executed.

## OC-052

**docs-only** — Memory ingestion/backfill exclusions do not govern raw transcript indexing or direct file writes; effective write prevention requires actual tool/file/host restrictions.

[Pinned source: docs/concepts/memory-provenance.md:161-184](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-provenance.md#L161-L184)

Limit: Scope limitation described in source documentation; not a full authorization proof.

## OC-053

**code-traced** — Active Memory defines a 15-second normal recall budget, 45-second CLI recall default, 220-character summary target, 15-second cache, recent-query/escalate mode, and timeout circuit-breaker defaults.

[Pinned source: extensions/active-memory/types.ts:4-32](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/types.ts#L4-L32)

Limit: Static source inspection; not executed in this research.

## OC-054

**code-traced** — Active Memory is a separate configured plugin: its resolved settings enable it unless disabled, default eligible chat type is direct, and it narrows callable recall tools and budgets.

[Pinned source: extensions/active-memory/config.ts:151-212](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/config.ts#L151-L212)

Limit: Static source inspection; not executed in this research.

## OC-055

**code-traced** — The recall helper invokes a distinct embedded run with a bounded deadline, explicit recall tool allowlist and inherited memory audience; storage uses a SQLite runtime session, with optional JSONL diagnostic artifact export.

[Pinned source: extensions/active-memory/recall-run.ts:267-311](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/recall-run.ts#L267-L311)

Limit: Static source inspection; not executed in this research.

## OC-056

**code-traced** — Active Memory hooks before prompt building, filters recall tools through current authority and arms a bounded deadline that skips failed/timed-out recall instead of blocking the conversational reply forever.

[Pinned source: extensions/active-memory/index.ts:212-271](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/index.ts#L212-L271)

Limit: Static source inspection; not executed in this research.

## OC-057

**code-traced** — Top-level default concurrency is max(8,4*availableParallelism); ordinary subagent execution limit defaults to 8 per controller, active-child admission cap 5, spawn depth cap 5 and archive delay 60 minutes.

[Pinned source: src/config/agent-limits.ts:5-46](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/config/agent-limits.ts#L5-L46)

Limit: Static source inspection; not executed in this research.

## OC-058

**code-traced** — Child admission includes pending reservations, checks depth and active/total caps, and makes slot release idempotent; launch acceptance and execution concurrency are separate limits.

[Pinned source: src/agents/child-admission.ts:43-106](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/child-admission.ts#L43-L106)

Limit: Static source inspection; not executed in this research.

## OC-059

**code-traced** — Spawned sessions persist parent/completion-owner identities and inherited allow/deny/delegated tool policy; the restrictions are state, not only role prose.

[Pinned source: src/agents/subagents/spawn/subagent-capabilities.ts:43-52](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/subagents/spawn/subagent-capabilities.ts#L43-L52)

Limit: Static source inspection; not executed in this research.

## OC-060

**docs-only** — Subagents get the normal policy pipeline plus a hard-deny layer; hidden helpers lack direct message delivery, visible sessions have a scoped exception, and depth-capped leaves lose spawn/session-control tools.

[Pinned source: docs/tools/subagents/tool-policy.md:41-62](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents/tool-policy.md#L41-L62)

Limit: The complete every-tool policy composition was not executed; persisted envelope and layered policy mechanisms separately traced.

## OC-061

**docs-only** — Restart recovery does not blindly relaunch interrupted subagents: it settles interrupted outcomes and returns continuation responsibility to the parent; saved operator evidence is revalidated.

[Pinned source: docs/tools/subagents/operations.md:82-103](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents/operations.md#L82-L103)

Limit: Fault recovery protocol documented, not crash-tested in this research.

## OC-062

**code-traced** — Tool policy composes profile/provider/global/agent/group/sender layers, preserving layer provenance for diagnostics.

[Pinned source: src/agents/tool-policy-pipeline.ts:72-141](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/tool-policy-pipeline.ts#L72-L141)

Limit: Static source inspection; not executed in this research.

## OC-063

**code-traced** — Policy layers successively filter the current effective tools; later allow entries do not independently recreate tools filtered out by an earlier layer.

[Pinned source: src/agents/tool-policy-pipeline.ts:156-243](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/tool-policy-pipeline.ts#L156-L243)

Limit: Static source inspection; not executed in this research.

## OC-064

**code-traced** — Run authority is host-issued, captures a live assertion and revocation/abort checks, and wraps access to current assignments; a model-provided label is not authority.

[Pinned source: src/agents/admitted-run-context.ts:86-140](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/admitted-run-context.ts#L86-L140)

Limit: Static source inspection; not executed in this research.

## OC-065

**code-traced** — Sandbox config defaults mode=off, backend=docker and workspaceAccess=none when enabled; backend choice does not mean Docker is required for every run.

[Pinned source: src/agents/sandbox/config.ts:221-233](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/sandbox/config.ts#L221-L233)

Limit: Static source inspection; not executed in this research.

## OC-066

**code-traced** — Host exec approval defaults are security=full and ask=off, with deny fallback when an approval prompt cannot be resolved; this is a trusted-operator design choice.

[Pinned source: src/infra/exec-approvals-config.ts:95-100](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/infra/exec-approvals-config.ts#L95-L100)

Limit: Static source inspection; not executed in this research.

## OC-067

**docs-only** — One Gateway is intended for one operator or mutually trusting team; default session reach is broad, routing session IDs are not authorization tokens, and hostile tenants require separate isolation.

[Pinned source: docs/gateway/security/trust-model.md:11-25](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/gateway/security/trust-model.md#L11-L25)

Limit: No security audit or exploit testing performed; configuration and host boundaries matter.

## OC-068

**code-traced** — The generic run-timeout resolver defaults to 48 hours and treats explicit zero as a timer-safe unlimited sentinel; caller/runtime/scheduler deadlines can be tighter.

[Pinned source: src/agents/timeout.ts:13-38](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/timeout.ts#L13-L38)

Limit: Static source inspection; not executed in this research.

## OC-069

**docs-only** — Gateway scheduling owns durable job/run state and an independent watchdog; interrupted effects are not automatically replayed when the outcome is unknown.

[Pinned source: docs/automation/cron-jobs/how-it-works.md:14-71](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/automation/cron-jobs/how-it-works.md#L14-L71)

Limit: Cron recovery not executed; documented default budgets are isolated-agent 60 min, command 10 min and script 5 min.

## OC-070

**code-traced** — The base heartbeat interval constant is 30 minutes; provider defaults and agent configuration may alter eligibility/cadence.

[Pinned source: src/auto-reply/heartbeat.ts:26-29](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/auto-reply/heartbeat.ts#L26-L29)

Limit: Static source inspection; not executed in this research.

## OC-071

**docs-only** — OTel content capture is documented off by default; enabling it adds bounded redacted prompts/results/tool data while excluding system prompts and private thinking. External runtime tool spans do not guarantee content parity.

[Pinned source: docs/gateway/opentelemetry/privacy-and-trace-context.md:45-82](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/gateway/opentelemetry/privacy-and-trace-context.md#L45-L82)

Limit: Exporter behavior across every runtime was not tested; local transcripts/logs have separate retention policies.

## OC-072

**docs-only** — Native runtime model-loop/thread/compaction ownership differs from built-in ownership; OpenClaw projects or mirrors context and cannot claim universal hook parity.

[Pinned source: docs/concepts/agent-runtimes.md:110-130](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-runtimes.md#L110-L130)

Limit: Native adapters were not installed, authenticated or executed.

## OC-073

**test-inspected** — A targeted writer-claim test fixture supplies expected run ownership; test source covers supersession/stale-write scenarios.

[Pinned source: src/agents/embedded-agent-runner/run/lane-controller.writer-claim.test.ts:109-134](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/run/lane-controller.writer-claim.test.ts#L109-L134)

Limit: Test file inspected, not run; existence is not a passing result.

## OC-074

**test-inspected** — A provenance test models declared network tool output and expects assistant derivation to downgrade while owner input stays trusted.

[Pinned source: packages/memory-host-sdk/src/host/session-files.provenance.test.ts:115-150](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/memory-host-sdk/src/host/session-files.provenance.test.ts#L115-L150)

Limit: Inspected test assertions, not executed.

## OC-075

**test-inspected** — Pruning tests assert invalid TTL fallback to 300,000 ms and explicit 1h parsing to 3,600,000 ms.

[Pinned source: src/agents/embedded-agent-runner/tool-result-truncation.cache-ttl.test.ts:309-314](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/tool-result-truncation.cache-ttl.test.ts#L309-L314)

Limit: Test source inspected, not executed.
