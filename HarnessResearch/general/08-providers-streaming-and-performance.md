# Model adapters, streaming and performance

Provider integration is more than swapping a model-name string. A harness needs an explicit capability contract for messages, tools, structured output, multimodal data, continuation state, streaming, usage, cancellation and context ownership. Supported semantics must be checked for the actual model/API/version. [G03–G07](../SOURCES.md#g03).

## A normalized internal boundary

Represent text, tool calls/results, errors, attachments, refusals, opaque provider items and usage as typed events. An adapter maps these into the chosen provider's request and back. Unsupported content should fail explicitly or use a declared transformation; silently flattening everything into strings can discard protocol state or change meaning.

Version the adapter and record which capabilities were active. A model may support JSON output without supporting a given parallel-tool policy, reasoning setting, native compaction route or persistent conversation API. Model aliases and provider limits can change; a pinned run receipt should retain the resolved identity/configuration where available.

## Streaming is an event protocol

Text deltas, tool-name/argument fragments, usage updates, completion markers and errors can arrive separately. Accumulate/validate a complete tool call before dispatch unless the provider explicitly defines another safe protocol. Distinguish a transport disconnect from a model-level stop and from application task completion.

Associate events with request/run/call IDs and preserve order within the required scope. If a stream disconnects after a tool intent or partial response, restarting inference may produce a different action. Resume/retry policy must account for already observed effects and any server-owned continuation state.

## Rate limits and retry classes

Transient transport failure, overload, authentication rejection, unsupported parameter, context overflow, malformed tool arguments and a tool-domain refusal require different handling. Retrying every error with the same request can spend budget indefinitely. Compacting a prompt cannot fix invalid credentials or every per-minute request-size ceiling.

Use bounded retry/backoff where appropriate, preserve the same action identity for an idempotent external retry, and stop/reconcile when the outcome is ambiguous. A model request retry and a business-operation retry are different layers. [G15/G18](../SOURCES.md#g15).

## Cache, compute and context economics

Prompt caching can reuse eligible prefix computation; it does not save the application from storing events or selecting valid context. Retrieval caches, tool-result caches, embedding caches and model KV/prompt caches have different invalidation and scope requirements. A cached tool result may be stale even if its text is cheap to re-inject.

Keep stable reference content and schemas stable where useful, while preserving correct policy/tool versions. Changing an earlier prefix can affect later reuse. Compaction trades fewer input tokens against summarization work and potential cache changes. Provider retention/pricing differs, so report actual usage/cost rather than copying a fixed multiplier from another system. [G06](../SOURCES.md#g06).

Useful measurements include time to first token, time to first useful action, total task latency, model/tool time, queue wait, cached/uncached usage, summarization/retrieval overhead, cost per valid completed task and failure/retry rate. A faster first token can coexist with slower or incorrect completion. Parallel workers can reduce elapsed time while increasing aggregate cost.

## Local, hosted and managed choices

A local/self-hosted model gives control over serving/storage but adds capacity, batching, tokenizer and operational responsibilities. A hosted model delegates serving but leaves application state/effects largely with the caller unless a managed harness API is used. A managed runtime can own sessions/tools/compaction under its contract; its state resources, retention and sandbox lifecycle must not be confused with an SDK session in our process. [G07](../SOURCES.md#g07).

Portability is a tradeoff: a lowest-common-denominator adapter simplifies switching but may forgo useful native features; a feature-rich adapter needs more route-specific tests. Preserve opaque native state where required rather than pretending it is portable text memory. Neither approach is selected for our eventual system by this study.
