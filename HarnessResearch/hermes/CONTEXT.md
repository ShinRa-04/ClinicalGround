# Context management: preserve useful state inside a finite request

[Index](README.md) · [Execution](EXECUTION.md) · [Memory](MEMORY.md) · [Operations](OPERATIONS.md) · [Limits](LIMITS_AND_LESSONS.md)

## What enters a request

Hermes's source distinguishes the cached system prompt from turn-specific/API-only additions. In the inspected builder the ordered tiers are:

| Tier | Main inspected contents | Consequence |
|---|---|---|
| Stable | Identity, tool/model guidance, coding brief, explicitly pinned skill bodies | Maximizes reusable prefix when later layers change. |
| Context | Caller-supplied system text, project context files, workspace snapshot and related guidance | Project/worktree identity belongs here; instruction discovery must not import the harness's own development file accidentally. |
| Volatile | Discoverable skill index, built-in memory/profile snapshots, external memory block, plugin sections, profile/time/runtime hints | Frozen within the cached prompt even though likely to change at a rebuild. |

[H006–H007: source ordering](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/system_prompt.py#L737-L822). The guide has an inconsistent sentence calling skills stable; the code distinguishes pinned bodies from the general index. “Volatile” does **not** mean recomputed on every iteration.

A memory write can update a durable file while the conversation continues to send the older prompt snapshot. Compression is an intentional refresh boundary: invalidation clears cached prompt fields, reloads built-in memory, and permits plugin section refresh with previous-good fallback. [H010: invalidation](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/system_prompt.py#L815-L836). Changes that must be seen immediately need a deliberate turn/tool-result overlay rather than silently editing past prompt bytes.

Project context caps are **character caps**, calculated by default from 6% of the model context window times a character/token heuristic and clamped to 20,000–500,000 characters. Explicit `context_file_max_chars` overrides the dynamic choice. Truncation keeps 70% head and 20% tail plus a marker and warning. Those percentages leave room for annotation; they do not preserve the middle's semantics. [H008–H009: cap and truncation](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/prompt_builder.py#L1045-L1067), [truncation implementation](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/prompt_builder.py#L1491-L1524).

For a new harness, specify an input provenance class for each layer: operator policy, repository instructions, user input, retrieved evidence, tool observation and assistant summary. A storage location or earlier retrieval must not silently upgrade untrusted prose into new authority.

## Cache identity is an engineering concern

The default design tries to keep prior prompt bytes and tool schemas stable. Cache planning is provider-specific: Anthropic paths can decorate static system prefix, tool-array endpoint and completed transaction endpoints, with a maximum-four-marker alternative layout. The planner makes copies of decorated structures rather than mutating canonical history. [H011: copy-on-write planner](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/prompt_caching.py#L313-L377).

This is not a promise of a cache hit, a universal TTL, or measured savings for our workload. A provider can have minimum cacheable length, cache-write cost, expiry, routing and model-specific rules. Output reservation, tool schema ordering, late MCP adoption, model switching and injected runtime details can change the effective request. A construction plan must measure billed input, cache-read/write buckets, latency and correctness together; a smaller prompt may cost more if it repeatedly invalidates a long useful prefix.

## Token accounting: anchors plus local estimates

The current `UsageAnchor` captures provider-reported prompt/completion counts and fingerprints the priced transcript. It includes both the final priced message and **the whole priced prefix**. At the next request, an anchor is usable only while those fingerprints match; only appended-message deltas are estimated. The anchored reply's assistant message is skipped in delta pricing because its completion was already counted. [H012: capture/matching/delta](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/usage_anchor.py#L27-L130).

The checked guide's statement that only the boundary row is fingerprinted is stale. The code's whole-transcript-prefix hash is stronger, but it still is not a separate hash of every provider-visible system/tool/config input. A count is authoritative only for the exact request the provider priced; rough deltas remain rough. Unknown usage must not be reported as zero.

The built-in preflight policy can wait **one provider request** when an unanchored whole-context estimate crosses the trigger, including a rough estimate beyond the apparent window. Once a provider has demonstrated usage omission, heuristic fallback can act; actual over-threshold usage and provider-rejected overflow also allow recovery. This avoids premature compression due to inflation while accepting that a genuinely oversized first request can be rejected once. [Additional inspected gate](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L2981-L3003). It is a policy tradeoff, not an exact-tokenizer theorem.

## Defaults versus effective thresholds

| Setting or mechanism | Value at inspected pin | Qualification |
|---|---|---|
| Base threshold | `0.50` | Not the universal effective trigger. |
| Small-window ratio floor | At least`0.75` below 512,000 context tokens | Raise-only; other caps still apply. |
| Output reservation | Subtracted from context when usable | No explicit reservation means this function assumes the whole window. |
| Absolute threshold cap | `None` by default | Model/auxiliary constraints can change the final cap. |
| Summary target ratio | `0.20` | A sizing parameter, not measured information preservation. |
| Initial protected messages |3 non-system messages | System prompt separately protected. |
| Recent protected count |20 messages | Token ceilings and coherent transaction groups can dominate. |
| Lean tail |2.5% of context, clamped 10,000–25,000 tokens | Actual selected tail can differ for required anchors/groups. |
| Attempt budget |3, floor behavior and configured maximum 10 | Distinguish lock deferral/no-op from a spent attempt. |
| In-place compaction |True | Stable session ID; archive/generation handling remains necessary. |
| Micro-compaction |False | Opt-in repeated history rewriting breaks prefixes. |

[H013: config interpretation](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/agent_init.py#L1524-L1596), [H014: effective trigger arithmetic](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L2761-L2807), [H015: lean-tail formula](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L2233-L2247), [tail constants](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L925-L926).

There is a separate gateway hygiene policy. Its settings default to 85% token pressure and an extreme 5,000-message safety valve. It uses actual prior prompt count, then a persisted anchor, then rough history estimation; DB-backed failure cooldown and in-flight compression can defer work. It only runs with eligible history, including the minimum-four-message gate. [Gateway implementation](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/gateway/run_turn_hygiene.py#L94-L107), [pressure selection](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/gateway/run_turn_hygiene.py#L156-L228), [eligibility](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/gateway/run_turn_hygiene.py#L765-L778). The two layers do not establish that compression will occur at a fixed percentage for every session.

## Compaction is a state transition

The built-in pipeline starts from a copied history, deterministically prunes eligible large tool-result payloads, chooses protected head and token-budget tail, summarizes the middle, then assembles and sanitizes message structure. User-task anchors and tool-call/result pairing need explicit handling. [H016: pipeline](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L5526-L5668).

Lossy summarization changes what the next model knows. It can omit a failed operation, source condition, unresolved ambiguity or a recent user correction. Keeping the full transcript in storage improves recoverability but does not make the active request lossless. A new harness should preserve structured fields separately: active objective, accepted constraints, evidence/source IDs, executed-effect receipts, pending operations, unresolved questions, current task and explicit next step. Preserve conclusions and inspectable evidence/rationale rather than treating a generated summary as proof of correctness.

The inspected failure documentation describes cooldowns for failed/stalled summaries, manual retry, bounded provider-proven-overflow bypass, deterministic fallback/degradation and overload handling. The core overflow handler was traced, but every described failure class and timing ladder was not executed. [H017: bounded overflow path](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_overflow.py#L128-L180), [H058: documented failure ladder](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/context-compression-and-caching.md#L180-L238).

Do not report deterministic fallback as a successful semantic summary. Its benefit is bounded degraded continuity. A failed summary can also warrant preserving the transcript and stopping; which policy is preferable depends on task risk and whether a trustworthy checkpoint exists.

## Alternative engines and transferable choices

The `ContextEngine` interface separates `compress` from `select_context`. `compress` returns a compacted transcript; `select_context` can replace only the current request while leaving canonical storage untouched. Selection can run on every request, including retries; it must pass normal sanitizers before provider submission. `on_turn_complete` is best-effort and can be skipped by abnormal exits. [H018: interface semantics](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_engine.py#L98-L154).

That supports several legitimate designs: rolling lossy summary, retrieval over an archived transcript, topic-specific request selection, hierarchical summary nodes or explicit workflow state plus a short event tail. Installing a plugin does not demonstrate lossless semantics or automatically activate it. A useful experiment measures retrieval misses, summary drift, task accuracy, source recoverability, compaction frequency and total billed cost under the same model and task budget. No one engine is established as best here.
