# Context construction, budgets and compaction

The context builder is a policy-controlled compiler from stored state into a provider-specific request. Its job is to include enough relevant evidence and instructions to act correctly while respecting a finite input/output budget and preserving message protocol structure.

## Measure the rendered request

A planning inequality is:

`rendered_input + reserved_output + provider_required_overhead <= effective_context_limit`

This is a budgeting model, not a universal tokenizer formula. Rendered input includes instructions, tool schemas, conversation, retrieved material, attachments and serialization wrappers. Reasoning/output accounting and hidden overhead differ by model/API. A provider's input cap, per-request/token-rate cap and model context limit are different constraints. A request can fail even when a nominal window calculation seems valid.

Count or estimate **after** relevant transforms and tool discovery. Preserve measured provider usage with its request/model/configuration fingerprint; a count for an earlier prefix is not necessarily valid after editing tools, changing models or injecting new memory. Where exact counting is unavailable, use conservative estimates and a bounded recovery policy, while labeling the uncertainty.

A fixed “compact at 80%” rule is a design choice, not a law. Trigger policy should account for output reserve, incoming tool-result size, summarizer capacity, minimum protected tail and the required next action. The pinned case studies show why nominal defaults and effective thresholds can differ.

## Selection before summarization

Before asking a model to summarize everything, consider filtering irrelevant records, limiting tool results, retrieving precise file spans, deferring unused schemas, resolving large attachments through handles, and dropping expendable intermediate views. These transforms are not equivalent to forgetting facts or deleting event history. [G09/G11/G13](../SOURCES.md#g09).

Keep stable instructions and tool identity consistent where possible for cache reuse, but prioritize correctness. Cache behavior depends on matching eligible rendered prefixes; moving a changing memory block into an early prefix can invalidate reuse. Compaction itself can change the prefix. A lower cache-hit rate after compaction can coexist with lower total input work; evaluate cost/latency rather than optimizing a single cache percentage. [G06](../SOURCES.md#g06).

## Preserve protocol units

Treat a tool call and its matching results as an atomic conversation unit when selecting a cut point. Also preserve valid assistant/user boundaries and provider-specific continuation items. Partial JSON from a stream, an orphan result, an omitted required opaque item or reordered calls can break the next request independently of summary quality.

Create a normalized internal event model, but do not assume all provider content can be losslessly flattened into role/text pairs. Multimodal parts, refusals, tool errors and opaque continuation state can need typed retention. Standalone and server-managed compaction may have different rules for which returned items to preserve. [G03/G05](../SOURCES.md#g03).

## Compaction strategies and their costs

| Strategy | What it gains | What can fail |
| --- | --- | --- |
| Keep recent turns only | Simple bounded input | Old constraints and unresolved obligations disappear |
| Rolling natural-language summary | Broad continuity at low token volume | Accumulated omission, ambiguity and false certainty |
| Hierarchical summaries | Limits each summarization request | Additional latency and errors at multiple levels |
| Structured task checkpoint plus selective episodes | Explicit goals/obligations with evidence retrieval | Schema omissions and retrieval misses |
| Provider-native opaque compaction | Continuation integrated with a provider | Portability, inspection and backend-ownership limits |
| External retained history plus lazy references | Original evidence remains recoverable | Handles can go stale or retrieval may not occur |
| Fresh context with durable handoff artifacts | Clean working window | Reorientation cost and incomplete handoff |

No row guarantees semantic losslessness. Keeping the originals makes a lossy summary recoverable; it does not make the summary itself lossless. Preservation of exact events and preservation of all decision-relevant meaning are different properties.

## A proposed compaction contract

Snapshot the current state/version; identify protected instruction, active user request, unresolved obligations, recent atomic exchanges and authoritative identifiers; select admissible older material; checkpoint any required durable state; summarize or transform with enough capacity; validate the resulting protocol/required fields; publish the new projection only if its source version is still current; retain rollback/retrieval references.

If the summary fails, do not silently mark the operation successful or rotate away the unresolved task. If a provider-native backend owns the actual thread, changing a local mirrored transcript may not shrink that backing context. If the selected summarizer has a smaller window, batching, retrieval or a different policy may be needed. Repeatedly invoking a summarizer that cannot fit its input is not recovery.

Tests should include delayed tool results, a giant tool response, contradictory evidence, pending approvals, mid-turn steering, opaque provider items, repeated compactions, model changes and restart during publication. The desired outcome is valid continuation with traceable uncertainty, not merely fewer tokens. [G05/G08/G09](../SOURCES.md#g05).
