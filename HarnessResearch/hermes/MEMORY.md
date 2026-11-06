# Memory: several stores with different lifetimes

[Index](README.md) · [Execution](EXECUTION.md) · [Context](CONTEXT.md) · [Operations](OPERATIONS.md) · [Limits](LIMITS_AND_LESSONS.md)

## Do not collapse everything into “the memory”

| Mechanism | Content/lifetime | How the model sees it | Main limitation |
|---|---|---|---|
| Active conversation | Current user/tool/assistant history | Request history | Finite window, repeated input cost and stale observations. |
| Built-in `MEMORY.md` | Curated environment/general facts | Frozen system snapshot | Very small character budget; writes do not immediately refresh prompt. |
| Built-in `USER.md` | User identity/preferences | Frozen system snapshot | Personal data needs scope/retention; inferred preference can be wrong. |
| Session database | Durable transcript/metadata, archived generations | Resumption or explicit search/read | Stored does not mean selected or semantically correct. |
| External memory provider | Provider-specific recall/retention | Static provider block plus turn prefetch/tools | Optional, separate egress/failure/retention behavior. |
| Skills | Reusable procedure/instructions/support files | Small index then explicit full load; optional pinned body | A saved procedure can encode a mistake. |
| Compaction summary | Compressed continuation state | Selected summary plus protected head/tail | Lossy, may distort temporal status and provenance. |

This classification is analysis of implementation roles, not a claim that Hermes labels all stores with these exact names. The strongest code links are [store snapshots H020–H022](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L175-L255), [search H030](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/session_search_tool.py#L1-L52) and [skills H042](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/skills_tool.py#L1-L45).

## Small built-in fact/profile stores

Default configuration enables both stores, with 2,200 characters for memory and 1,375 for profile, a nudge interval of 10, no external provider selected and `write_approval: false`. These are small curated text stores; no default built-in vector database is implied. Character-to-token comments are approximations. Existing installations/config migrations can differ. [H019: defaults](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1310-L1328).

The store is profile-scoped under `memories/`. Loading reads entries and captures rendered prompt snapshots. Strict threat-pattern scanning can replace suspicious entries with a blocked placeholder in the snapshot, while preserving original disk entries. Existing over-limit files generate a warning and prevent further additions until reduced; they are not silently truncated on load. The `memory` tool exposes mutations such as add, patch, remove and supported batch operations. [H020: store load](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L175-L255), [tool contract](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool.py#L222-L290).

The mutation sequence matters more than the Markdown format: acquire a lock on a separate lockfile, reread current content under that lock, identify the intended entry, refuse ambiguous/destructive drift when needed, enforce constraints, then atomically replace the file. A drift backup helps avoid clobbering foreign/manual text. Writes update store/disk state while `format_for_system_prompt` still returns the frozen load-time snapshot. [H021–H022: mutation and snapshot](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L257-L367), [render/write/drift](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L618-L700).

For a new harness, a memory record often deserves more than prose: record subject/scope, statement, source, observation time, confidence/status, expiry, supersession and deletion state. Hermes's bounded files show that a simple baseline can be useful; they do not establish that every durable healthcare/organizational fact belongs in a universal system prompt. Memory persistence is not model-weight training.

## External memory: optional provider behavior

Initialization can add **one configured external provider alongside built-in stores**. The manager intentionally rejects a second external provider even though its internal API uses lists. Reserved core tool names cannot be hijacked by provider tools. The checked source tree contains `retaindb` and `byterover` directories, while configuration comments name additional catalog-installed integrations. Their backend implementations were not audited in this workstream; directory presence is not activation or an installed service. [H023–H024: init and manager](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/agent_init.py#L1299-L1383), [provider registration](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L288-L348).

The `MemoryProvider` contract separates static prompt block, prefetch, queued prefetch, completed-turn synchronization, tool dispatch, actual session boundaries, pre-compress checkpoint and memory-write notifications. A provider may implement only part of that surface or use a compatibility signature. Interface presence does not tell us whether it uses embeddings, a graph, extraction, raw transcript storage, a remote model or local storage. [H059: lifecycle interface](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_provider.py#L121-L225).

The inspected main flow is:

1. At turn start, flatten semantic user text, notify author/turn context and skip trivial-query prefetch.
2. Invoke provider prefetch once before the tool loop. External prefetch gets a bounded waiting thread; if stuck, later turns skip that provider until its thread returns.
3. Fence returned recall as memory context, emit a deterministic recall indicator, and compose it into the user request variant.
4. Persist an `api_content` sidecar where necessary so replay can reproduce model-visible bytes while keeping clean display/transcript text separately.
5. At completion, queue redacted turn synchronization on a single context-bound background worker so turn N's write precedes N+1's.

[H025–H028: bounded prefetch](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L365-L421), [turn admission/sidecar](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_context.py#L908-L968), [serialized sync](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L453-L533).

The returned recall wrapper explicitly tells the model that recalled context is reference data rather than new user input, but also calls it authoritative. That is a prompt instruction, **not a factual verification guarantee**. A stale or poisoned memory remains possible; a new harness should preserve evidence strength and authority scope explicitly. [Inspected wrapper](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_context.py#L169-L185).

Timeout also does not kill a blocked Python thread or cancel a remote operation. Redaction reduces exposure but is not a general proof that all sensitive information was removed. A background queue hides latency from the user but creates flush/shutdown/retry concerns. Those are separate responsibilities to design, instrument and test.

## Before context is lost

The manager supports a versioned pre-compress checkpoint contract. When `require_checkpoint` is requested, a capable provider must successfully complete the checkpoint hook or an exception keeps the caller from accepting unsafe loss of the uncompressed transcript. Normal best-effort provider hooks do not automatically satisfy this requirement. [H029: checkpoint handling](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L673-L716).

This is an important construction pattern: an optional learning side effect and a mandatory durable checkpoint need different failure policies. It is not proof that all Hermes compaction uses checkpoint-required mode or that every provider implements a durable write. The operator must select the mode and the integration must honor the promise.

## Transcript recall is not the same as semantic memory

At this pin, built-in `session_search` explicitly performs **no LLM calls** and returns actual database messages. It infers discovery, read, anchored scroll or browse mode from supplied arguments. Discovery deduplicates lineage, hides internal kanban/subagent/tool sessions and demotes repetitive cron sessions so they do not dominate interactive history. Read results cap per-message content at 2,000 characters; discovery can scan 300 FTS rows before deduplication, and the excluded-session list is capped at 20. [H030–H031: tool contract and caps](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/session_search_tool.py#L1-L52).

The DB search implementation includes FTS, CJK/trigram routes and canonical-row fallbacks for stale/corrupt derived indexes. This establishes lexical retrieval machinery, not default embedding-based semantic recall, perfect rankings or complete multilingual recall. [H032: search routes](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_state_search.py#L1088-L1191).

Raw messages provide provenance but can contain outdated assumptions or an assistant's own earlier error. A new harness should display timestamp, role, source session and message/operation ID; distinguish user confirmation from assistant speculation; and allow widening a bounded retrieval when the evidence is insufficient. A search hit is evidence of what was said, not evidence that it was true.

## Procedural memory through skills

Skills are directory-based instructions plus optional scripts/references/templates/assets. The default list/index stays small, and `skill_view` loads selected full content. This is progressive disclosure: the harness does not need to place the complete library into every request. Pinned auto-loaded bodies are the explicit exception. [H042: skill tool](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/skills_tool.py#L1-L45).

Relevant defaults are deliberately separate: trusted project discovery enabled but with an empty trusted-root list; inline skill shell snippets off; approval for skill mutation off; agent-created scanning guard off; provenance ledger on with a 5MiB cap. Hub-install scanning is a different path. [H043: default controls](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1450-L1490).

Curator maintenance defaults enabled with weekly interval,2h idle prerequisite,14-day stale and 30-day archive thresholds. LLM consolidation and built-in pruning default off; backup keep count is 2. Archiving and explicit purge are distinct. These settings demonstrate a lifecycle for procedural knowledge rather than indefinite accumulation. They do not show that learned rules improve performance. [H044: curator defaults](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1492-L1529).

## Background learning has costs and failure modes

The finalizer may fork a memory/skill review after response delivery when review is due and a usable final response exists, unless interrupted or explicitly skipped. It is not an unconditional fork after every turn. Review configuration defaults enabled; a safe-worker or finite-turn policy suppresses it, while configuration read failure otherwise leaves it enabled with a warning. [H045–H046: finalizer](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_finalizer.py#L763-L803), [review gate](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/background_review.py#L228-L251).

The same word `on_session_end` appears in different extension layers. The general plugin hook is called at the normal finalizer seam, while the comments explicitly reserve memory-provider `on_session_end`/shutdown for actual session owners. An integration must trace which hook contract it implements; matching names do not guarantee matching lifetime.

Research questions for our own harness remain open: Should learning occur only after explicit user confirmation or independently verified task success? Should failed episodes yield candidate lessons requiring review? What evidence invalidates a learned procedure? How are deletions propagated to summaries, archives, indexes, backups and remote providers? This Hermes review does not establish an end-to-end forgetting guarantee for every optional backend, and it should not be used to claim one.
