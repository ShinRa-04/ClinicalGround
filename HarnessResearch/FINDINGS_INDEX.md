# Implementation and comparative finding index

170 individually scoped findings across two deep source studies and the broader comparison. These are not 170 executed tests or verified deployment guarantees. General construction recommendations remain engineering synthesis in the handbook.

| System | Evidence status | Findings |
| --- | --- | --- |
| comparative | ambiguous_documentation | 1 |
| comparative | code_inspected | 17 |
| comparative | documented | 17 |
| hermes | code-traced | 49 |
| hermes | docs-only | 8 |
| hermes | test-inspected | 3 |
| openclaw | code-traced | 54 |
| openclaw | docs-only | 18 |
| openclaw | test-inspected | 3 |

<a id="h001"></a>
## H001 — hermes

**code-traced** — The turn loop assembles context, supports a separate Codex app-server turn path, then iterates preflight, request/retry, normalized tool-or-text response and finalization phases.

[Source: agent/conversation_loop.py:1555-1715](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/conversation_loop.py#L1555-L1715)

**Limit:** Static call-path trace; provider success, cancellation timing and all early-return paths were not exercised.

<a id="h002"></a>
## H002 — hermes

**code-traced** — A model tool-call turn is persisted before dispatch; failed canonical persistence ends the turn before side effects.

[Source: agent/turn_tool_round.py:109-178](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_tool_round.py#L109-L178)

**Limit:** Persist-before-dispatch is not atomicity between a remote side effect and its later result receipt; no exactly-once external-effect claim.

<a id="h003"></a>
## H003 — hermes

**code-traced** — Session turn leases use a 300 second TTL, a default 60 second refresh interval, and separate liveness activity checks.

[Source: agent/turn_facade_lease.py:22-106](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_facade_lease.py#L22-L106)

**Limit:** A lease is concurrency ownership, not proof a model/tool is making useful progress; alternate configured timings may apply.

<a id="h004"></a>
## H004 — hermes

**code-traced** — Provider response-normalization transports are registry-based, discovering Anthropic, Codex, chat-completions and Bedrock modules; registered plugin API modes can be recognized.

[Source: agent/transports/__init__.py:17-56](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/transports/__init__.py#L17-L56)

**Limit:** Normalization registry is only one part of execution; Codex app-server has its separate turn implementation; not every backend audited.

<a id="h005"></a>
## H005 — hermes

**docs-only** — Provider runtime documentation describes one shared resolver across CLI, gateway, cron, ACP and auxiliary calls, with explicit requests before saved config, environment and defaults.

[Source: website/docs/developer-guide/provider-runtime.md:8-54](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/provider-runtime.md#L8-L54)

**Limit:** High-level documentation precedence; all credential refresh/fallback/custom-endpoint branches were not individually traced.

<a id="h006"></a>
## H006 — hermes

**code-traced** — System prompt construction orders stable, context and volatile tiers; skill index and memory occupy the volatile tier while pinned auto-loaded skill bodies enter stable prefix.

[Source: agent/system_prompt.py:737-822](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/system_prompt.py#L737-L822)

**Limit:** Volatile means likely to change at rebuild, not rewritten every API request; the concrete ordering controls over contradictory guide prose.

<a id="h007"></a>
## H007 — hermes

**code-traced** — Built-in memory and external provider system blocks are assembled together; exposure of external provider tools gates its advertised block.

[Source: agent/system_prompt.py:522-549](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/system_prompt.py#L522-L549)

**Limit:** No claim that this scans or semantically validates every provider's retrieved fact.

<a id="h008"></a>
## H008 — hermes

**code-traced** — Project context character cap defaults dynamically to 6% of model window times a character estimate, clamped from 20,000 to 500,000 characters; explicit config overrides.

[Source: agent/prompt_builder.py:1045-1067](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/prompt_builder.py#L1045-L1067)

**Limit:** Characters are not exact tokens; caps are context-file limits, not the entire request or the subdirectory hint cap.

<a id="h009"></a>
## H009 — hermes

**code-traced** — Context-file truncation preserves 70% head and 20% tail plus a marker, with warnings and a path for reading omitted content.

[Source: agent/prompt_builder.py:1491-1524](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/prompt_builder.py#L1491-L1524)

**Limit:** A retained heading or marker does not preserve omitted instruction semantics; warning does not guarantee later reread.

<a id="h010"></a>
## H010 — hermes

**code-traced** — Memory prompt invalidation at compression clears cached state and reloads snapshots for a rebuild boundary.

[Source: agent/system_prompt.py:815-862](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/system_prompt.py#L815-L862)

**Limit:** Inspect the full function for other cache fields; mutation is not a refresh on every memory write.

<a id="h011"></a>
## H011 — hermes

**code-traced** — Anthropic cache planning is copy-on-write and supports a native tool-array breakpoint plus static prefix and two completed-transaction endpoints, or a maximum-four-marker message layout.

[Source: agent/prompt_caching.py:313-377](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/prompt_caching.py#L313-L377)

**Limit:** Provider-specific optimization; markers do not promise cache hits or measured savings, and other providers use other semantics.

<a id="h012"></a>
## H012 — hermes

**code-traced** — Usage anchors capture provider prompt/completion counts plus transcript fingerprints, including the whole priced prefix, and estimate only appended-message deltas.

[Source: agent/usage_anchor.py:27-130](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/usage_anchor.py#L27-L130)

**Limit:** Not a vendor tokenizer or full request fingerprint: external tool definitions and separately assembled system prompt are not independently fingerprinted here.

<a id="h013"></a>
## H013 — hermes

**code-traced** — Compression config base defaults: threshold .50, target ratio .20, protect first 3, recent count 20, max attempts 3 capped at10, in-place true, micro-compaction false.

[Source: agent/agent_init.py:1524-1596](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/agent_init.py#L1524-L1596)

**Limit:** Effective trigger is adjusted by model overrides, output reservation, small-window floor and optional caps; recent count is opportunistic against token ceilings.

<a id="h014"></a>
## H014 — hermes

**code-traced** — For context windows below512,000, built-in compression raises threshold ratio to at least .75; effective input subtracts output reservation, with minimum-floor and .85 guard behavior.

[Source: agent/context_compressor.py:2761-2807](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L2761-L2807)

**Limit:** No universal .50 trigger. Explicit absolute/auxiliary caps can lower final threshold; model-specific auto-raise may raise ratio.

<a id="h015"></a>
## H015 — hermes

**code-traced** — Lean verbatim tail uses 2.5% of context clamped by lean floor/cap constants; legacy uses threshold times summary target ratio.

[Source: agent/context_compressor.py:2233-2247](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L2233-L2247)

**Limit:** Tail selection must preserve coherent tool groups/user anchors and may adjust actual retained size; not a fixed count of turns.

<a id="h016"></a>
## H016 — hermes

**code-traced** — Compression pipeline prunes a copied tool-result history, finds a compression window and summary path, then assembles the compressed transcript.

[Source: agent/context_compressor.py:5526-5668](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L5526-L5668)

**Limit:** Lossy compaction: preservation of full archived transcript does not make the model-visible summary lossless.

<a id="h017"></a>
## H017 — hermes

**code-traced** — Overflow recovery tracks bounded compression attempts; provider-proven overflow requests a cooldown-bypassing pass and distinguishes transient lock refusal from exhaustion.

[Source: agent/turn_overflow.py:128-180](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_overflow.py#L128-L180)

**Limit:** HTTP payload bytes and context tokens are different error classes. This is not proof every provider's error string is classified correctly.

<a id="h018"></a>
## H018 — hermes

**code-traced** — Context-engine API separates destructive/persisted compression from request-only select_context replacement and best-effort on_turn_complete observation.

[Source: agent/context_engine.py:98-154](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_engine.py#L98-L154)

**Limit:** Custom engines may change cache prefix and have optional hooks; terminal failures can skip on_turn_complete.

<a id="h019"></a>
## H019 — hermes

**code-traced** — Memory config defaults enable two built-in stores, cap them at2200 and1375 characters, leave write approval off, nudge interval10 and no external provider selected.

[Source: hermes_cli/config_defaults.py:1310-1328](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1310-L1328)

**Limit:** Character limits are not measured token guarantees; existing user config/migrations can differ. These defaults do not imply permission for this project to auto-write research memory.

<a id="h020"></a>
## H020 — hermes

**code-traced** — MemoryStore loads a frozen system-prompt snapshot; writes mutate disk state separately; strict threat scanning can substitute blocked-entry placeholders in the snapshot.

[Source: tools/memory_tool_store.py:175-255](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L175-L255)

**Limit:** Pattern scanning is a heuristic, not proof a memory is true/safe; preexisting oversized files are warned and loaded, not silently clipped.

<a id="h021"></a>
## H021 — hermes

**code-traced** — Memory mutations lock a separate lockfile, reread current disk state, detect destructive-edit drift and atomically write updated entries.

[Source: tools/memory_tool_store.py:257-367](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L257-L367)

**Limit:** Protects supported cooperating file writers; external manual edits can still create drift. Approval behavior and remote provider stores are separate.

<a id="h022"></a>
## H022 — hermes

**code-traced** — Memory prompt rendering returns the frozen load snapshot; disk writes use atomic_write_text and preserve foreign-content drift backups.

[Source: tools/memory_tool_store.py:618-700](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/memory_tool_store.py#L618-L700)

**Limit:** Atomic local file replacement does not provide a multi-store or cross-service distributed transaction.

<a id="h023"></a>
## H023 — hermes

**code-traced** — Agent initialization loads built-in memory unless skipped or safe-worker gated, and optionally loads one configured external provider alongside it.

[Source: agent/agent_init.py:1299-1383](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/agent_init.py#L1299-L1383)

**Limit:** An explicitly requested memory toolset can still load the built-in store when skip_memory is true; safe-worker and disabled-toolset gates matter.

<a id="h024"></a>
## H024 — hermes

**code-traced** — MemoryManager rejects a second external provider, protects reserved core tool names and snapshots recall spill policy when registering.

[Source: agent/memory_manager.py:288-348](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L288-L348)

**Limit:** The orchestrator's list-shaped API is not proof unlimited simultaneous external stores are supported.

<a id="h025"></a>
## H025 — hermes

**code-traced** — External prefetch runs on a context-propagating daemon thread with bounded wait; a stuck provider is skipped on later turns until it returns.

[Source: agent/memory_manager.py:365-421](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L365-L421)

**Limit:** Timeout does not forcibly terminate Python thread or undo remote work. No unbounded new thread per later turn for the same stuck provider.

<a id="h026"></a>
## H026 — hermes

**code-traced** — Turn start prefetch uses semantic user text, skips trivial prompts, notifies turn author and emits a deterministic recall indicator when context is injected.

[Source: agent/turn_context.py:908-935](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_context.py#L908-L935)

**Limit:** Whether recall was relevant/correct still depends on provider and task; image-only text may be trivial.

<a id="h027"></a>
## H027 — hermes

**code-traced** — Injected user context is stamped into api_content sidecar for exact replay while clean transcript content can remain separately stored.

[Source: agent/turn_context.py:938-968](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_context.py#L938-L968)

**Limit:** Sidecar semantics require the matching persistence path; this is not an assertion that no sensitive content is stored.

<a id="h028"></a>
## H028 — hermes

**code-traced** — Provider sync_turn sends redacted turn text and optional transcript through one serialized background worker, preserving ordering and bounded user-facing completion.

[Source: agent/memory_manager.py:453-533](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L453-L533)

**Limit:** Redaction patterns do not guarantee removal of all sensitive information. Queue completion and remote durability need explicit flush/provider semantics.

<a id="h029"></a>
## H029 — hermes

**code-traced** — Checkpoint-required pre-compress mode requires a capable provider to succeed or raises so caller can retain uncompressed transcript.

[Source: agent/memory_manager.py:673-716](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_manager.py#L673-L716)

**Limit:** Opt-in checkpoint contract, not universal default or transactional proof of every provider's storage.

<a id="h030"></a>
## H030 — hermes

**code-traced** — Current session_search returns actual stored messages with discovery/read/scroll/browse modes and makes no LLM calls.

[Source: tools/session_search_tool.py:1-52](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/session_search_tool.py#L1-L52)

**Limit:** Built-in tool only; external memory providers can call models. Search ranking does not establish factual correctness.

<a id="h031"></a>
## H031 — hermes

**code-traced** — Search hides kanban/subagent/tool sources, demotes cron matches, caps raw discovery scan300, read-message content2000 and exclusion IDs20.

[Source: tools/session_search_tool.py:20-49](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/session_search_tool.py#L20-L49)

**Limit:** These are implementation defaults at pin, not complete semantic recall guarantees; hidden sources are not deleted.

<a id="h032"></a>
## H032 — hermes

**code-traced** — SessionDB search uses FTS with canonical-row fallback routes for stale/corrupt indexes, including CJK/trigram handling.

[Source: hermes_state_search.py:1088-1191](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_state_search.py#L1088-L1191)

**Limit:** Runtime indexing availability/platform extension behavior was not executed; not default vector search.

<a id="h033"></a>
## H033 — hermes

**code-traced** — State schema includes canonical messages, model usage, runtime epoch, durable session admissions, managed-worker executions and receipts.

[Source: hermes_state_common.py:477-586](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_state_common.py#L477-L586)

**Limit:** Schema existence alone does not prove every legacy writer goes through all revision fences.

<a id="h034"></a>
## H034 — hermes

**code-traced** — Started admissions/workers from a prior owner epoch become unknown; started external effects are not blindly replayed.

[Source: hermes_state_runtime.py:390-404](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_state_runtime.py#L390-L404)

**Limit:** Unknown requires reconciliation. This sacrifices automatic liveness rather than claiming exactly-once external actions.

<a id="h035"></a>
## H035 — hermes

**code-traced** — Claiming new input refuses while unknown input or worker execution blocks the session.

[Source: hermes_state_runtime.py:193-223](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_state_runtime.py#L193-L223)

**Limit:** Core admission store path only; all other platform delivery semantics are not thereby proven.

<a id="h036"></a>
## H036 — hermes

**code-traced** — Managed compression mutates archive/publication and generation on the supplied connection and returns its result projection for the enclosing receipt transaction.

[Source: hermes_state_mutation_compress.py:1-27](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_state_mutation_compress.py#L1-L27)

**Limit:** Enclosing mutate_runtime_session stores its exact-retry receipt on the same connection; no universal legacy-writer claim.

<a id="h037"></a>
## H037 — hermes

**code-traced** — Hermes home resolves context-local override before environment and platform default; named profile state must retain that identity through child work.

[Source: hermes_constants.py:161-176](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_constants.py#L161-L176)

**Limit:** Profile configuration isolation is not an OS security boundary or an audited medical data-access policy.

<a id="h038"></a>
## H038 — hermes

**code-traced** — Delegate child construction makes fresh isolated conversation with supplied goal/context, derived depth role, skipped project/default memory and a fresh iteration budget.

[Source: tools/delegate_tool.py:229-313](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/delegate_tool.py#L229-L313)

**Limit:** skip_memory exception for explicit memory toolsets exists in init; child context/terminal session isolation does not imply separate filesystem or tenant sandbox.

<a id="h039"></a>
## H039 — hermes

**code-traced** — Delegation defaults are250 iterations per child,24,000 summary characters, no child idle timeout,10 concurrent children and inherited MCP toolsets.

[Source: hermes_cli/config_defaults.py:1355-1378](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1355-L1378)

**Limit:** Operator overrides apply; dynamic parent-headroom limit also bounds summaries, and actual supported child tools are filtered separately.

<a id="h040"></a>
## H040 — hermes

**code-traced** — Delegate max_iterations argument from caller is ignored when it differs from authoritative delegation configuration.

[Source: tools/delegate_tool.py:520-540](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/delegate_tool.py#L520-L540)

**Limit:** No shared-parent-budget inference; aggregate spend across independently budgeted children still needs policy.

<a id="h041"></a>
## H041 — hermes

**docs-only** — Public lifecycle API documents capability handles, cooperative cancel, immutable bounded result/hash and unavailable reconnect after process restart.

[Source: website/docs/developer-guide/subagent-lifecycle-api.md:27-68](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/subagent-lifecycle-api.md#L27-L68)

**Limit:** Documentation contract inspected, not full API exercise; Python threads do not survive host exit.

<a id="h042"></a>
## H042 — hermes

**code-traced** — Skills use progressive disclosure: lightweight index/list and full skill_view content plus support files.

[Source: tools/skills_tool.py:1-45](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/skills_tool.py#L1-L45)

**Limit:** A selected skill can still load substantial content; its mere presence does not prove correct procedural learning.

<a id="h043"></a>
## H043 — hermes

**code-traced** — Default skill writes need no approval; inline shell snippets are off; agent-created guard off; ledger on with5MiB cap; project discovery requires trusted root.

[Source: hermes_cli/config_defaults.py:1450-1490](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1450-L1490)

**Limit:** Hub install scanning and operator trust are distinct; a ledger is provenance/rollback support, not validation of skill correctness.

<a id="h044"></a>
## H044 — hermes

**code-traced** — Curator defaults enabled, weekly interval,2h idle,14day stale,30day archive, LLM consolidation off, built-in prune off and backup keep2.

[Source: hermes_cli/config_defaults.py:1492-1529](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1492-L1529)

**Limit:** Defaults describe maintenance policy, not measured learning; archive TTL default0 and explicit purge differ from automatic deletion.

<a id="h045"></a>
## H045 — hermes

**code-traced** — Post-turn finalizer can spawn a background memory/skill review only when due, noninterrupted, final response exists and background review not skipped.

[Source: agent/turn_finalizer.py:763-803](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/turn_finalizer.py#L763-L803)

**Limit:** Not every turn forks. General plugin on_session_end hook is called here but memory-provider session-end cleanup is explicitly elsewhere.

<a id="h046"></a>
## H046 — hermes

**code-traced** — Background review defaults enabled unless finite-turn or safe-worker policy suppresses it; config-read failure leaves review enabled with warning.

[Source: agent/background_review.py:228-251](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/background_review.py#L228-L251)

**Limit:** This is fail-open for optional learning behavior/cost, not a security recommendation; no review-model calls were executed.

<a id="h047"></a>
## H047 — hermes

**code-traced** — Cron constructs agents with skip_memory=False, load_soul_identity=True and skip_background_review=True; project context depends on configured workdir.

[Source: cron/scheduler.py:2515-2530](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/cron/scheduler.py#L2515-L2530)

**Limit:** Contradicts stale agent AGENTS.md cron skip_memory=True claim; actual selected toolsets and provider gates still apply.

<a id="h048"></a>
## H048 — hermes

**docs-only** — Security policy treats OS-level whole-process isolation as containment and distinguishes it from terminal-backend sandbox and in-process heuristic checks.

[Source: SECURITY.md:59-116](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/SECURITY.md#L59-L116)

**Limit:** Published trust model, not penetration-test result or security certification. No sandbox/runtime was launched.

<a id="h049"></a>
## H049 — hermes

**code-traced** — Approval default is smart, while cron/single-query/unattended modes default deny.

[Source: hermes_cli/config_defaults.py:1657-1686](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L1657-L1686)

**Limit:** Actual guard participation depends on tool path/config; not all possible host effects are thereby contained.

<a id="h050"></a>
## H050 — hermes

**code-traced** — Approval module has per-session state and a default three-consecutive-smart-denial breaker; frozen launch YOLO state cannot be changed by a later environment read.

[Source: tools/approval.py:40-119](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/approval.py#L40-L119)

**Limit:** An in-process heuristic, not a sandbox; user-configured bypass/floors have separate semantics.

<a id="h051"></a>
## H051 — hermes

**docs-only** — Plugin architecture documents different discovery precedence for general, memory and model-provider plugins; context engines are separate kind-specific extensions.

[Source: plugins/AGENTS.md:70-77](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/plugins/AGENTS.md#L70-L77)

**Limit:** Documentation design contract inspected; installer/package compatibility and all plugin execution isolation paths not audited.

<a id="h052"></a>
## H052 — hermes

**docs-only** — Context-engine selection documentation requires explicit config and falls back to built-in compressor; engines are not activated simply because installed.

[Source: website/docs/developer-guide/context-compression-and-caching.md:40-68](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/context-compression-and-caching.md#L40-L68)

**Limit:** Plugin implementation such as LCM not audited here; fallback and selection wiring statically inspected in agent_init1904 onward.

<a id="h053"></a>
## H053 — hermes

**code-traced** — Gateway health monitoring defaults off and OTLP export off; typed events are intended content-free operational health/diagnostics rather than transcript export.

[Source: hermes_cli/config_defaults.py:2074-2098](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/hermes_cli/config_defaults.py#L2074-L2098)

**Limit:** Separate logs, usage auditing, traces and plugin telemetry may carry different content and retention; no global privacy guarantee.

<a id="h054"></a>
## H054 — hermes

**test-inspected** — Upstream test contracts inspect frozen memory snapshots, roundtrip storage and oversized file loading.

[Source: tests/tools/test_memory_tool.py:405-463](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tests/tools/test_memory_tool.py#L405-L463)

**Limit:** Tests inspected only, not executed; selected range covers roundtrip/oversize/frozen snapshot, not all test claims elsewhere.

<a id="h055"></a>
## H055 — hermes

**test-inspected** — Usage-anchor tests explicitly exercise prefix rewrites preserving the final priced row and matching reloaded transcript content.

[Source: tests/agent/test_usage_anchor.py:118-160](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tests/agent/test_usage_anchor.py#L118-L160)

**Limit:** Tests inspected, not executed; no vendor-tokenizer comparison.

<a id="h056"></a>
## H056 — hermes

**test-inspected** — Runtime admission tests cover durable request identity/conflict and claim/recovery behavior.

[Source: tests/hermes_state/test_runtime_admission.py:1-94](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tests/hermes_state/test_runtime_admission.py#L1-L94)

**Limit:** Tests inspected, not executed. Assertions are evidence of intended contract, not measured production reliability.

<a id="h057"></a>
## H057 — hermes

**docs-only** — Gateway hygiene documentation describes separate85% safety threshold using prior real usage, persisted anchor then rough fallback.

[Source: website/docs/developer-guide/context-compression-and-caching.md:78-106](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/context-compression-and-caching.md#L78-L106)

**Limit:** Docs-only here: actual gateway/run_turn_hygiene.py is additional implementation to audit for changed guards; built-in main compressor does not always fire at50%.

<a id="h058"></a>
## H058 — hermes

**docs-only** — Compression guide explains failed-summary cooldowns, deterministic degradation, overload escalation and manual/provider-overflow bypasses.

[Source: website/docs/developer-guide/context-compression-and-caching.md:180-238](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/context-compression-and-caching.md#L180-L238)

**Limit:** Documentation-only detailed failure ladder; core compress/overflow call path traced but every failure class not dynamically tested.

<a id="h059"></a>
## H059 — hermes

**code-traced** — MemoryProvider ABC exposes prefetch, sync_turn, session lifecycle, pre-compress checkpoint and memory-write notification seams.

[Source: agent/memory_provider.py:121-225](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/memory_provider.py#L121-L225)

**Limit:** An interface contract does not prove provider-specific privacy, deletion, embeddings or durable implementation.

<a id="h060"></a>
## H060 — hermes

**docs-only** — Session-storage guide describes canonical gateway ownership, separate runtime workers and archive generations rather than treating all clients as independent transcript writers.

[Source: website/docs/developer-guide/session-storage.md:5-15](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/session-storage.md#L5-L15)

**Limit:** Architecture documentation; direct AIAgent/batch/legacy modes have scope caveats, so not every process universally gateway-only.

<a id="oc-001"></a>
## OC-001 — openclaw

**code-traced** — The pinned checkout declares package version 2026.10.4, MIT licensing, and SQLite/Postgres database capabilities; this is a moving-main source snapshot, not a verified installed release.

[Source: package.json:3-24](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/package.json#L3-L24)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-002"></a>
## OC-002 — openclaw

**code-traced** — The pinned package requires Node >=24.16.0 <25 or >=26.1.0; historical Node 22 guidance must not be substituted for this revision.

[Source: package.json:2465-2469](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/package.json#L2465-L2469)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-003"></a>
## OC-003 — openclaw

**docs-only** — Provider, model, runtime/harness, and messaging channel are separate layers; embedded and external CLI/native backends have different ownership.

[Source: docs/concepts/agent-runtimes.md:10-46](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-runtimes.md#L10-L46)

**Limit:** Pinned documentation contract; parity of every native adapter was not tested.

<a id="oc-004"></a>
## OC-004 — openclaw

**code-traced** — runEmbeddedAgent creates a session lane and global lane, waits for deferred maintenance/projection, then admits work through the global queue.

[Source: src/agents/embedded-agent-runner/run-orchestrator.ts:162-246](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/run-orchestrator.ts#L162-L246)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-005"></a>
## OC-005 — openclaw

**code-traced** — Ordinary child execution lanes are keyed by immediate spawning/controller session; cron nested work receives a distinct lane to avoid a held-lane deadlock.

[Source: src/agents/embedded-agent-runner/lanes.ts:15-46](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/lanes.ts#L15-L46)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-006"></a>
## OC-006 — openclaw

**code-traced** — The built-in loop handles queued messages, continuation preparation, streamed responses, admitted tool batches, provider errors, taint, stop/continuation signals and abort; a text response with endTurn=false can continue.

[Source: packages/agent-core/src/agent-loop.ts:229-403](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/agent-loop.ts#L229-L403)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-007"></a>
## OC-007 — openclaw

**code-traced** — Tool calls are resolved/validated before batch admission; configured sequential execution or a sequential tool constrains a batch, while other calls can use grouped parallel/asynchronous execution.

[Source: packages/agent-core/src/agent-loop.ts:475-554](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/agent-loop.ts#L475-L554)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-008"></a>
## OC-008 — openclaw

**code-traced** — Attempt preparation constructs core/plugin tools and a prepared system prompt, then refreshes the effective prompt tool policy; the model prompt is an assembled runtime product.

[Source: src/agents/embedded-agent-runner/run/attempt.ts:327-441](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/run/attempt.ts#L327-L441)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-009"></a>
## OC-009 — openclaw

**code-traced** — System prompt construction distinguishes full/minimal/none modes and derives sections from runtime capability context; a subagent prompt is not simply a full parent prompt with a new name.

[Source: src/agents/system-prompt.ts:354-438](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/system-prompt.ts#L354-L438)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-010"></a>
## OC-010 — openclaw

**code-traced** — Prompt preparation gates skills and memory sections on callable capabilities and prepares ordered context files/bootstrap sections.

[Source: src/agents/system-prompt.ts:517-613](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/system-prompt.ts#L517-L613)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-011"></a>
## OC-011 — openclaw

**code-traced** — Bootstrap defaults are 20,000 characters per ordinary file and 60,000 total, with a separate 4,000-character USER.md cap; these are character limits, not exact model token counts.

[Source: src/agents/embedded-agent-helpers/bootstrap.ts:87-106](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-helpers/bootstrap.ts#L87-L106)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-012"></a>
## OC-012 — openclaw

**code-traced** — Bootstrap diagnostics distinguish per-file/total truncation and near-limit pressure, using an 85% warning threshold.

[Source: src/agents/bootstrap-budget.ts:122-183](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/bootstrap-budget.ts#L122-L183)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-013"></a>
## OC-013 — openclaw

**code-traced** — System prompt reports account for rendered prompt inputs, context-file injection, tool schema/summary sizes and hashes; a report is observability, not proof the model followed instructions.

[Source: src/agents/system-prompt-report.ts:124-181](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/system-prompt-report.ts#L124-L181)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-014"></a>
## OC-014 — openclaw

**code-traced** — An engine returns ordered messages and an estimated token count, but its estimate does not control host request admission; per-turn and persistent-thread projection are distinct contracts.

[Source: src/context-engine/types.ts:8-50](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/context-engine/types.ts#L8-L50)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-015"></a>
## OC-015 — openclaw

**code-traced** — The implicit memory plugin slot is memory-core and the implicit context-engine slot is legacy; these are distinct replaceable ownership slots.

[Source: src/plugins/slots.ts:17-22](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/plugins/slots.ts#L17-L22)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-016"></a>
## OC-016 — openclaw

**code-traced** — The default legacy engine does not itself persist ingested messages; assembly is pass-through and compaction delegates to the built-in runtime, with existing sanitization/limit/repair downstream.

[Source: src/context-engine/legacy.ts:14-38](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/context-engine/legacy.ts#L14-L38)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-017"></a>
## OC-017 — openclaw

**code-traced** — The context engine contract includes bootstrap, maintenance, ingest/batch-ingest, after-turn, assemble, compact and dispose hooks; host compatibility and lifecycle are part of extension correctness.

[Source: src/context-engine/types.ts:362-548](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/context-engine/types.ts#L362-L548)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-018"></a>
## OC-018 — openclaw

**code-traced** — Transcript mutation scope checks current session ID, lifecycle revision and active writer run ID when the corresponding expected fence is supplied.

[Source: src/config/sessions/session-accessor.sqlite-scope.ts:84-111](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/config/sessions/session-accessor.sqlite-scope.ts#L84-L111)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-019"></a>
## OC-019 — openclaw

**code-traced** — The locked SQLite transcript write guard reads fresh session identity and refuses a rebound/stale fenced writer before committing a protected mutation.

[Source: src/config/sessions/session-accessor.sqlite-transcript-write-guard.ts:54-79](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/config/sessions/session-accessor.sqlite-transcript-write-guard.ts#L54-L79)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-020"></a>
## OC-020 — openclaw

**docs-only** — The documented active store uses durable writer claims and per-agent SQLite writes; the Gateway state-directory lock excludes another owner.

[Source: docs/concepts/agent-loop.md:58-65](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-loop.md#L58-L65)

**Limit:** Write-guard mechanism separately traced; full cross-process fault behavior was not executed.

<a id="oc-021"></a>
## OC-021 — openclaw

**code-traced** — Client cache-TTL pruning is opt-in via mode=cache-ttl; its local resolver defaults TTL to five minutes, hard clear to enabled, and deny/allow tool filters are applied.

[Source: src/agents/embedded-agent-runner/tool-result-truncation.ts:64-98](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/tool-result-truncation.ts#L64-L98)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-022"></a>
## OC-022 — openclaw

**code-traced** — Client soft pruning replaces a large eligible tool result with its first/last 1,500 characters and a trim marker; the operation constructs a projected message.

[Source: src/agents/embedded-agent-runner/tool-result-truncation.ts:154-190](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/tool-result-truncation.ts#L154-L190)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-023"></a>
## OC-023 — openclaw

**code-traced** — Tool-result projections are serialized as hidden openclaw.cache-ttl transcript markers; successful marker commit updates the cached checkpoint, while original tool-result rows are distinct.

[Source: src/agents/embedded-agent-runner/session-prompt-state.ts:348-381](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/session-prompt-state.ts#L348-L381)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-024"></a>
## OC-024 — openclaw

**docs-only** — The pinned pruning guide documents TTL/context thresholds, protected recent assistant turns, persistent projection replay across restart, and unchanged raw tool-result history.

[Source: docs/concepts/session-pruning.md:67-108](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/session-pruning.md#L67-L108)

**Limit:** Detailed threshold branches not all independently executed; projection persistence separately code-traced.

<a id="oc-025"></a>
## OC-025 — openclaw

**docs-only** — The compaction guide still calls pruning in-memory-only, conflicting with the current pruning guide and marker-persistence implementation.

[Source: docs/concepts/compaction.md:407-409](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L407-L409)

**Limit:** This records a documentation contradiction; use OC-023 and OC-024 for the precise current distinction.

<a id="oc-026"></a>
## OC-026 — openclaw

**code-traced** — The low-level library defaults compaction on, reserveTokens=16,384, keepRecentTokens=20,000; these are not necessarily the final host-effective settings.

[Source: packages/agent-core/src/harness/compaction/compaction.ts:163-169](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/harness/compaction/compaction.ts#L163-L169)

**Limit:** Library defaults inspected; host configuration, reserves, output limits and runtime/provider ownership can override them.

<a id="oc-027"></a>
## OC-027 — openclaw

**code-traced** — Compaction planning uses an estimation safety margin of 1.2 and excludes runtime-only context and private tool-result details before message token estimation.

[Source: src/agents/compaction-planning.ts:7-19](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/compaction-planning.ts#L7-L19)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-028"></a>
## OC-028 — openclaw

**docs-only** — Prepared request budgeting considers system instructions, schemas, pending input and output reserve; a larger summarizer does not enlarge the foreground model window.

[Source: docs/concepts/compaction.md:160-184](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L160-L184)

**Limit:** No live provider tokenization or overflow trial executed.

<a id="oc-029"></a>
## OC-029 — openclaw

**docs-only** — History hydration independently bounds serialized replay bytes (8 times context-token budget, at least 1 KiB and at most 64 MiB); omitted stored history is not deleted or summarized.

[Source: docs/concepts/compaction.md:261-282](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L261-L282)

**Limit:** Hydration implementation not independently exercised; dense events and byte/token mismatch remain relevant limits.

<a id="oc-030"></a>
## OC-030 — openclaw

**docs-only** — An opt-in active-transcript byte guard triggers semantic compaction; if it fails or remains oversized, bounded recent history can be used without rewriting/deleting the saved messages.

[Source: docs/concepts/compaction.md:228-258](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L228-L258)

**Limit:** Byte cap applies to selected active SQLite history, not a universal disk-retention cap.

<a id="oc-031"></a>
## OC-031 — openclaw

**code-traced** — Memory Core flush defaults use a 4,000-token soft threshold and 2 MiB transcript-byte pressure; the prompt targets append-only daily notes and treats curated/bootstrap files as read-only.

[Source: extensions/memory-core/src/flush-plan.ts:12-34](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/flush-plan.ts#L12-L34)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-032"></a>
## OC-032 — openclaw

**code-traced** — Memory flush can be disabled; its plan computes effective reserves/soft threshold, optional exact model override and a timezone-resolved daily memory path.

[Source: extensions/memory-core/src/flush-plan.ts:63-108](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/flush-plan.ts#L63-L108)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-033"></a>
## OC-033 — openclaw

**code-traced** — The flush gate records at most one flush per compaction cycle by comparing memoryFlush.compactionCount to the current compactionCount.

[Source: src/auto-reply/reply/memory-flush.ts:169-174](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/auto-reply/reply/memory-flush.ts#L169-L174)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-034"></a>
## OC-034 — openclaw

**docs-only** — Flush failure is documented as nonfatal maintenance; required compaction failure preserves the conversation and reports failure rather than automatically starting over.

[Source: docs/concepts/compaction.md:325-333](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/compaction.md#L325-L333)

**Limit:** No injected flush or compaction failure executed.

<a id="oc-035"></a>
## OC-035 — openclaw

**code-traced** — Memory search resolves enabled=true by default; the normal query resolver uses maxResults=6/minScore=.35 with .7/.3 vector/text weights, 4x candidates, enabled MMR lambda=.7, enabled temporal decay half-life 30 days.

[Source: src/agents/memory-search.ts:88-149](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts#L88-L149)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-036"></a>
## OC-036 — openclaw

**code-traced** — Unset or auto memory embedding provider resolves to openai; provider=none is the built-in FTS-only sentinel and avoids semantic provider discovery.

[Source: src/agents/memory-search.ts:71-88](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts#L71-L88)

**Limit:** Configuration resolution is not credential readiness, a network request, or proof a model was downloaded.

<a id="oc-037"></a>
## OC-037 — openclaw

**code-traced** — Built-in memory chunking resolves to 400 tokens with 80 overlap; the embedding cache is enabled by default and bounded to 50,000 entries in this resolver.

[Source: src/agents/memory-search.ts:209-217](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts#L209-L217)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-038"></a>
## OC-038 — openclaw

**code-traced** — Default memory query sources are memory files; session sources depend on session-memory/remember-across-conversations policy, and indexed sources can differ from explicit query sources.

[Source: src/agents/memory-search-source-policy.ts:3-41](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search-source-policy.ts#L3-L41)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-039"></a>
## OC-039 — openclaw

**code-traced** — Hybrid retrieval merges by chunk identity, combines vector/lexical signals, handles path-specific ranking, project affinity and recency; final ranking is more nuanced than one cosine score.

[Source: extensions/memory-core/src/memory/hybrid.ts:137-226](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory/hybrid.ts#L137-L226)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-040"></a>
## OC-040 — openclaw

**code-traced** — MMR reorders candidates using normalized relevance and token-set Jaccard redundancy, controlled by lambda; it is diversity ranking, not a truth verifier.

[Source: extensions/memory-core/src/memory/mmr.ts:28-91](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory/mmr.ts#L28-L91)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-041"></a>
## OC-041 — openclaw

**code-traced** — Recency applies exponential half-life decay to dated/dated-source entries; evergreen root/topic memory paths are exempt. Helper defaults are disabled, but the normal resolver explicitly enables decay.

[Source: extensions/memory-core/src/memory/temporal-decay.ts:15-84](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory/temporal-decay.ts#L15-L84)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-042"></a>
## OC-042 — openclaw

**docs-only** — Memory Core distinguishes instructions, curated core, episodic notes/transcripts, prospective intents/cron and human-only review output; storage and injection policies differ.

[Source: docs/concepts/memory-architecture.md:53-87](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-architecture.md#L53-L87)

**Limit:** File-oriented memory does not imply all harness state is plain text: index, provenance, sessions and scheduling include database state.

<a id="oc-043"></a>
## OC-043 — openclaw

**code-traced** — Origin classification uses host metadata: tainted assistant content is untrusted, assistant derivation of owner content is agent, internal system input is system, explicit owner input is owner, and other input is untrusted.

[Source: packages/memory-host-sdk/src/host/session-provenance.ts:4-24](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/memory-host-sdk/src/host/session-provenance.ts#L4-L24)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-044"></a>
## OC-044 — openclaw

**code-traced** — A tool result declared network-sourced taints later assistant derivations until a new user turn; this mechanism depends on accurate result-source declarations.

[Source: packages/agent-core/src/turn-taint.ts:24-66](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/agent-core/src/turn-taint.ts#L24-L66)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-045"></a>
## OC-045 — openclaw

**code-traced** — Promotion rejects untrusted/system provenance; consolidation requires owner/agent origin and interactive kind for session-derived candidates.

[Source: extensions/memory-core/src/dreaming-consolidation-candidates.ts:11-25](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/dreaming-consolidation-candidates.ts#L11-L25)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-046"></a>
## OC-046 — openclaw

**code-traced** — Dreaming default frequency is 03:00 daily; deep defaults include limit=10, minScore=.75, minRecallCount=3, minUniqueQueries=3, 14-day recency half-life and bounded prior-entry loss.

[Source: src/memory-host-sdk/dreaming.ts:21-42](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/memory-host-sdk/dreaming.ts#L21-L42)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-047"></a>
## OC-047 — openclaw

**code-traced** — The dreaming config resolver defaults its sweep and light/deep/REM phases enabled; this still depends on selected memory plugin, running Gateway/cron and eligible candidates.

[Source: src/memory-host-sdk/dreaming.ts:381-445](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/memory-host-sdk/dreaming.ts#L381-L445)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-048"></a>
## OC-048 — openclaw

**code-traced** — Dreaming registration/reconciliation checks scheduler availability/enabled state and warns when cron is unavailable rather than pretending a configured sweep executed.

[Source: extensions/memory-core/src/dreaming.ts:414-444](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/dreaming.ts#L414-L444)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-049"></a>
## OC-049 — openclaw

**docs-only** — Consolidation is documented to compare the memory content hash before atomic replacement, preserve preimages and append a readable review diary; concurrent external edits can cause rewrite abort/fallback.

[Source: docs/concepts/memory-architecture.md:212-227](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-architecture.md#L212-L227)

**Limit:** Accepted residual filesystem race and recovery are documented; no concurrent-writer stress test executed.

<a id="oc-050"></a>
## OC-050 — openclaw

**code-traced** — Memory forget requires session/hook/participant selectors, resolves current source sessions and origin rows, and serializes mutating cleanup with a workspace lock; dry-run follows a nonmutating branch.

[Source: extensions/memory-core/src/memory-forget.ts:81-142](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/memory-core/src/memory-forget.ts#L81-L142)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-051"></a>
## OC-051 — openclaw

**docs-only** — Admission exclusion and retrospective forget are different: forget removes identifiable memory artifacts, not original transcripts, all freeform writes or every retained copy.

[Source: docs/concepts/memory-provenance.md:17-36](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-provenance.md#L17-L36)

**Limit:** Not a compliance-grade erasure guarantee; no deletion command executed.

<a id="oc-052"></a>
## OC-052 — openclaw

**docs-only** — Memory ingestion/backfill exclusions do not govern raw transcript indexing or direct file writes; effective write prevention requires actual tool/file/host restrictions.

[Source: docs/concepts/memory-provenance.md:161-184](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/memory-provenance.md#L161-L184)

**Limit:** Scope limitation described in source documentation; not a full authorization proof.

<a id="oc-053"></a>
## OC-053 — openclaw

**code-traced** — Active Memory defines a 15-second normal recall budget, 45-second CLI recall default, 220-character summary target, 15-second cache, recent-query/escalate mode, and timeout circuit-breaker defaults.

[Source: extensions/active-memory/types.ts:4-32](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/types.ts#L4-L32)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-054"></a>
## OC-054 — openclaw

**code-traced** — Active Memory is a separate configured plugin: its resolved settings enable it unless disabled, default eligible chat type is direct, and it narrows callable recall tools and budgets.

[Source: extensions/active-memory/config.ts:151-212](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/config.ts#L151-L212)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-055"></a>
## OC-055 — openclaw

**code-traced** — The recall helper invokes a distinct embedded run with a bounded deadline, explicit recall tool allowlist and inherited memory audience; storage uses a SQLite runtime session, with optional JSONL diagnostic artifact export.

[Source: extensions/active-memory/recall-run.ts:267-311](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/recall-run.ts#L267-L311)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-056"></a>
## OC-056 — openclaw

**code-traced** — Active Memory hooks before prompt building, filters recall tools through current authority and arms a bounded deadline that skips failed/timed-out recall instead of blocking the conversational reply forever.

[Source: extensions/active-memory/index.ts:212-271](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/active-memory/index.ts#L212-L271)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-057"></a>
## OC-057 — openclaw

**code-traced** — Top-level default concurrency is max(8,4*availableParallelism); ordinary subagent execution limit defaults to 8 per controller, active-child admission cap 5, spawn depth cap 5 and archive delay 60 minutes.

[Source: src/config/agent-limits.ts:5-46](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/config/agent-limits.ts#L5-L46)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-058"></a>
## OC-058 — openclaw

**code-traced** — Child admission includes pending reservations, checks depth and active/total caps, and makes slot release idempotent; launch acceptance and execution concurrency are separate limits.

[Source: src/agents/child-admission.ts:43-106](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/child-admission.ts#L43-L106)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-059"></a>
## OC-059 — openclaw

**code-traced** — Spawned sessions persist parent/completion-owner identities and inherited allow/deny/delegated tool policy; the restrictions are state, not only role prose.

[Source: src/agents/subagents/spawn/subagent-capabilities.ts:43-52](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/subagents/spawn/subagent-capabilities.ts#L43-L52)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-060"></a>
## OC-060 — openclaw

**docs-only** — Subagents get the normal policy pipeline plus a hard-deny layer; hidden helpers lack direct message delivery, visible sessions have a scoped exception, and depth-capped leaves lose spawn/session-control tools.

[Source: docs/tools/subagents/tool-policy.md:41-62](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents/tool-policy.md#L41-L62)

**Limit:** The complete every-tool policy composition was not executed; persisted envelope and layered policy mechanisms separately traced.

<a id="oc-061"></a>
## OC-061 — openclaw

**docs-only** — Restart recovery does not blindly relaunch interrupted subagents: it settles interrupted outcomes and returns continuation responsibility to the parent; saved operator evidence is revalidated.

[Source: docs/tools/subagents/operations.md:82-103](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/tools/subagents/operations.md#L82-L103)

**Limit:** Fault recovery protocol documented, not crash-tested in this research.

<a id="oc-062"></a>
## OC-062 — openclaw

**code-traced** — Tool policy composes profile/provider/global/agent/group/sender layers, preserving layer provenance for diagnostics.

[Source: src/agents/tool-policy-pipeline.ts:72-141](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/tool-policy-pipeline.ts#L72-L141)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-063"></a>
## OC-063 — openclaw

**code-traced** — Policy layers successively filter the current effective tools; later allow entries do not independently recreate tools filtered out by an earlier layer.

[Source: src/agents/tool-policy-pipeline.ts:156-243](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/tool-policy-pipeline.ts#L156-L243)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-064"></a>
## OC-064 — openclaw

**code-traced** — Run authority is host-issued, captures a live assertion and revocation/abort checks, and wraps access to current assignments; a model-provided label is not authority.

[Source: src/agents/admitted-run-context.ts:86-140](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/admitted-run-context.ts#L86-L140)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-065"></a>
## OC-065 — openclaw

**code-traced** — Sandbox config defaults mode=off, backend=docker and workspaceAccess=none when enabled; backend choice does not mean Docker is required for every run.

[Source: src/agents/sandbox/config.ts:221-233](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/sandbox/config.ts#L221-L233)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-066"></a>
## OC-066 — openclaw

**code-traced** — Host exec approval defaults are security=full and ask=off, with deny fallback when an approval prompt cannot be resolved; this is a trusted-operator design choice.

[Source: src/infra/exec-approvals-config.ts:95-100](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/infra/exec-approvals-config.ts#L95-L100)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-067"></a>
## OC-067 — openclaw

**docs-only** — One Gateway is intended for one operator or mutually trusting team; default session reach is broad, routing session IDs are not authorization tokens, and hostile tenants require separate isolation.

[Source: docs/gateway/security/trust-model.md:11-25](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/gateway/security/trust-model.md#L11-L25)

**Limit:** No security audit or exploit testing performed; configuration and host boundaries matter.

<a id="oc-068"></a>
## OC-068 — openclaw

**code-traced** — The generic run-timeout resolver defaults to 48 hours and treats explicit zero as a timer-safe unlimited sentinel; caller/runtime/scheduler deadlines can be tighter.

[Source: src/agents/timeout.ts:13-38](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/timeout.ts#L13-L38)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-069"></a>
## OC-069 — openclaw

**docs-only** — Gateway scheduling owns durable job/run state and an independent watchdog; interrupted effects are not automatically replayed when the outcome is unknown.

[Source: docs/automation/cron-jobs/how-it-works.md:14-71](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/automation/cron-jobs/how-it-works.md#L14-L71)

**Limit:** Cron recovery not executed; documented default budgets are isolated-agent 60 min, command 10 min and script 5 min.

<a id="oc-070"></a>
## OC-070 — openclaw

**code-traced** — The base heartbeat interval constant is 30 minutes; provider defaults and agent configuration may alter eligibility/cadence.

[Source: src/auto-reply/heartbeat.ts:26-29](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/auto-reply/heartbeat.ts#L26-L29)

**Limit:** Static source inspection; not executed in this research.

<a id="oc-071"></a>
## OC-071 — openclaw

**docs-only** — OTel content capture is documented off by default; enabling it adds bounded redacted prompts/results/tool data while excluding system prompts and private thinking. External runtime tool spans do not guarantee content parity.

[Source: docs/gateway/opentelemetry/privacy-and-trace-context.md:45-82](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/gateway/opentelemetry/privacy-and-trace-context.md#L45-L82)

**Limit:** Exporter behavior across every runtime was not tested; local transcripts/logs have separate retention policies.

<a id="oc-072"></a>
## OC-072 — openclaw

**docs-only** — Native runtime model-loop/thread/compaction ownership differs from built-in ownership; OpenClaw projects or mirrors context and cannot claim universal hook parity.

[Source: docs/concepts/agent-runtimes.md:110-130](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/docs/concepts/agent-runtimes.md#L110-L130)

**Limit:** Native adapters were not installed, authenticated or executed.

<a id="oc-073"></a>
## OC-073 — openclaw

**test-inspected** — A targeted writer-claim test fixture supplies expected run ownership; test source covers supersession/stale-write scenarios.

[Source: src/agents/embedded-agent-runner/run/lane-controller.writer-claim.test.ts:109-134](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/run/lane-controller.writer-claim.test.ts#L109-L134)

**Limit:** Test file inspected, not run; existence is not a passing result.

<a id="oc-074"></a>
## OC-074 — openclaw

**test-inspected** — A provenance test models declared network tool output and expects assistant derivation to downgrade while owner input stays trusted.

[Source: packages/memory-host-sdk/src/host/session-files.provenance.test.ts:115-150](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/packages/memory-host-sdk/src/host/session-files.provenance.test.ts#L115-L150)

**Limit:** Inspected test assertions, not executed.

<a id="oc-075"></a>
## OC-075 — openclaw

**test-inspected** — Pruning tests assert invalid TTL fallback to 300,000 ms and explicit 1h parsing to 3,600,000 ms.

[Source: src/agents/embedded-agent-runner/tool-result-truncation.cache-ttl.test.ts:309-314](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/embedded-agent-runner/tool-result-truncation.cache-ttl.test.ts#L309-L314)

**Limit:** Test source inspected, not executed.

<a id="c01"></a>
## C01 — comparative

**documented** — The official guide distinguishes predetermined workflows from agents that dynamically direct their tool/process use.

[Source: Overview](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c02"></a>
## C02 — comparative

**documented** — Graph and Functional APIs are alternative control-flow interfaces to the same LangGraph runtime.

[Source: Choosing an API; Control flow](https://docs.langchain.com/oss/python/langgraph/choosing-apis)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c03"></a>
## C03 — comparative

**code_inspected** — Pi stores parent-linked session entries and a selected leaf in an append-only JSONL tree.

[Source: lines 976-998](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/session-manager.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c04"></a>
## C04 — comparative

**code_inspected** — Pi builds a compaction-aware session projection which retains source-entry associations and applies context edits.

[Source: buildContextEntries/buildSessionProjection/buildSessionContext, lines 473-582](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/session-manager.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c05"></a>
## C05 — comparative

**code_inspected** — Pi persists through synchronous initial writes and appends when persistence is enabled.

[Source: _persist, lines 1160-1195](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/session-manager.ts)

**Limit:** No claim of fsync, power-loss safety, cross-service transactions or multi-writer consistency.

<a id="c06"></a>
## C06 — comparative

**documented** — Checkpointers persist thread state; stores hold cross-thread application data, and memory-backed savers lose state on restart.

[Source: Checkpointer vs. store; MemorySaver does not persist between restarts](https://docs.langchain.com/oss/python/langgraph/persistence)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c07"></a>
## C07 — comparative

**documented** — Graph checkpoints occur at super-step boundaries, with per-task writes supporting successful-sibling recovery.

[Source: Super-steps; Pending writes](https://docs.langchain.com/oss/python/langgraph/checkpointers)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c08"></a>
## C08 — comparative

**documented** — Historical replay re-executes nodes after the selected checkpoint, including model and API calls.

[Source: Replay](https://docs.langchain.com/oss/python/langgraph/checkpointers)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c09"></a>
## C09 — comparative

**documented** — sync, async and exit modes offer different persistence timing and crash-recovery tradeoffs.

[Source: Durability modes](https://docs.langchain.com/oss/python/langgraph/checkpointers)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c10"></a>
## C10 — comparative

**documented** — Resuming an interrupt restarts its node, including code before the interrupt.

[Source: Resuming interrupts; Side effects called before interrupt must be idempotent](https://docs.langchain.com/oss/python/langgraph/interrupts)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c11"></a>
## C11 — comparative

**documented** — A functional entrypoint replays from its beginning using saved task outputs; incomplete tasks may execute again, requiring idempotent side effects.

[Source: Determinism; Idempotency](https://docs.langchain.com/oss/python/langgraph/functional-api)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c12"></a>
## C12 — comparative

**code_inspected** — SqliteSaver loads checkpoint pending writes and stores intermediate writes using thread/namespace/checkpoint/task identifiers.

[Source: get_tuple, lines 238-308; put_writes, lines 458-495](https://github.com/langchain-ai/langgraph/blob/0eb194fe6093812243de2249e7092029c87c8820/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py)

**Limit:** No external service transaction or exactly-once execution guarantee inferred.

<a id="c13"></a>
## C13 — comparative

**documented** — Letta SDK documentation warns against blindly resending after an uncertain connection failure and says missed stream events are not replayed automatically.

[Source: Guarantees and non-guarantees](https://docs.letta.com/agent-sdk/sessions/index.md)

**Limit:** Official documentation description; runtime behavior not tested.

<a id="c14"></a>
## C14 — comparative

**code_inspected** — Pi supports sequential preflight and concurrent tool execution while emitting final tool-result messages in assistant source order; sequential tools can force the batch sequential.

[Source: executeToolCalls/executeToolCallsParallel, lines 508-658](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent-loop.ts)

**Limit:** Ordering visible in this loop does not make arbitrary side effects independent or transactionally safe.

<a id="c15"></a>
## C15 — comparative

**documented** — Semantic, episodic and procedural memory describe remembered content; semantic memory differs from semantic search; memory writes can be foreground or background.

[Source: Long-term memory; Semantic memory; Writing memories](https://docs.langchain.com/oss/python/concepts/memory)

**Limit:** Useful taxonomy and documented patterns, not universal cognitive categories or measured gains here.

<a id="c16"></a>
## C16 — comparative

**documented** — Current MemFS docs describe Git-backed memory with core context files and demand-loaded indexed subdirectories.

[Source: Memory structure; Versioning and synchronization](https://docs.letta.com/concepts/memfs/index.md)

**Limit:** Mutable documentation; core layout differs between v1/v2; cloud behavior not tested.

<a id="c17"></a>
## C17 — comparative

**documented** — MemFS has no default semantic/vector index; optional search and conversation-history search have separate setup and backend scope.

[Source: Semantic and vector search](https://docs.letta.com/concepts/memfs/index.md)

**Limit:** Checked-date documentation; optional mod and hosted search not installed or evaluated.

<a id="c18"></a>
## C18 — comparative

**documented** — The original RAG research combines a generator with external retrieved non-parametric knowledge for knowledge-intensive tasks.

[Source: Abstract](https://arxiv.org/abs/2005.11401)

**Limit:** Abstract-level research framing only; experiments not reproduced and not an agent persistence contract.

<a id="c19"></a>
## C19 — comparative

**documented** — MemGPT v2 proposes virtual context management over memory tiers and reports document-analysis and multi-session-chat evaluations.

[Source: Abstract; version v2, revised 2024-02-12](https://arxiv.org/abs/2310.08560v2)

**Limit:** Historical research framing; not a current Letta implementation specification or evidence of unlimited model context.

<a id="c20"></a>
## C20 — comparative

**documented** — Current Letta docs distinguish shared agent memory from conversation context, and note compaction summaries can omit exact wording or provenance.

[Source: Conversation context and agent memory](https://docs.letta.com/concepts/conversations/index.md)

**Limit:** Documentation-only; no empirical retention-quality guarantee.

<a id="c21"></a>
## C21 — comparative

**ambiguous_documentation** — The SDK memory page still describes system/ as core memory, differing from the current MemFS page root-layout description.

[Source: MemFS bullet list](https://docs.letta.com/agent-sdk/memory/index.md)

**Limit:** Documentation discrepancy preserved; selected local code resolves only the local v1/v2 path.

<a id="c22"></a>
## C22 — comparative

**code_inspected** — The local memory format detector uses root MEMORY.md for v2; v2 core files are root Markdown and v1 core files are under system/.

[Source: detectMemoryFormat/isCoreMemoryPath, lines 4-20](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/agent/memory-format.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c23"></a>
## C23 — comparative

**code_inspected** — The selected local initializer creates v2 root files and rejects case-insensitive path collisions.

[Source: initialMemoryFilesFromCreateBody, lines 78-115](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/backend/local/initial-memory.ts)

**Limit:** Local creation path only; hosted migrations and every SDK path not audited.

<a id="c24"></a>
## C24 — comparative

**code_inspected** — Pi snapshot compaction defaults enable reduction with reserveTokens=16384 and keepRecentTokens=20000.

[Source: DEFAULT_COMPACTION_SETTINGS, lines 120-130](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/compaction/compaction.ts)

**Limit:** Snapshot defaults, not universal tuning recommendations or necessarily inherited by every embedding product.

<a id="c25"></a>
## C25 — comparative

**code_inspected** — Pi estimates context from valid provider usage plus trailing estimates and invalidates stale usage after relevant context changes.

[Source: estimateContextTokens/estimateProjectedContextTokens, lines 194-269](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/compaction/compaction.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c26"></a>
## C26 — comparative

**code_inspected** — Pi compaction cut-point selection avoids starting with tool-result messages.

[Source: findValidCutPoints/findCutPoint, lines 390-437](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/compaction/compaction.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c27"></a>
## C27 — comparative

**code_inspected** — The local module supports all/sliding_window modes and rejects reductions that make no count/token progress.

[Source: constants and assertLocalCompactionProgress, lines 22-92](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/backend/local/compaction.ts)

**Limit:** Local compaction implementation only; summary accuracy and hosted defaults not established.

<a id="c28"></a>
## C28 — comparative

**documented** — Dreaming consolidates conversations in background agents; optional agent review is not human approval and consumes additional model work.

[Source: Dreaming](https://docs.letta.com/configuration/memory/index.md)

**Limit:** Documentation-only; no performance/quality improvement measured.

<a id="c29"></a>
## C29 — comparative

**documented** — SDK dreaming configuration separates trigger, step interval and behavior, with session-level overrides narrower than creation options.

[Source: Dreaming](https://docs.letta.com/agent-sdk/memory/index.md)

**Limit:** SDK configuration description, not proof all backends implement identical scheduling.

<a id="c30"></a>
## C30 — comparative

**code_inspected** — The loop treats error/abort as termination and fails tool calls from a length-truncated assistant message rather than executing them.

[Source: runLoop, lines 241-270](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent-loop.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c31"></a>
## C31 — comparative

**code_inspected** — Request preparation applies transformContext before convertToLlm, with steering and follow-up polled at different loop stages.

[Source: runLoop lines 175-320; streamAssistantResponse lines 387-407](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent-loop.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c32"></a>
## C32 — comparative

**code_inspected** — The Agent wrapper defaults to parallel tool execution and supplies separate steering/follow-up queue-drain callbacks.

[Source: line 253; _buildConfig lines 475-503](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c33"></a>
## C33 — comparative

**code_inspected** — The task wrapper forwards retry/cache/timeout policies, and its source notes sync tasks cannot safely be cancelled in-process by the supported timeout mechanism.

[Source: _TaskFunction lines 59-94; task documentation lines 144-169](https://github.com/langchain-ai/langgraph/blob/0eb194fe6093812243de2249e7092029c87c8820/libs/langgraph/langgraph/func/__init__.py)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c34"></a>
## C34 — comparative

**code_inspected** — The interrupt contract re-executes node logic and matches repeated interrupts by encounter order using task-scoped state.

[Source: interrupt lines 903-925, 1019-1021](https://github.com/langchain-ai/langgraph/blob/0eb194fe6093812243de2249e7092029c87c8820/libs/langgraph/langgraph/types.py)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.

<a id="c35"></a>
## C35 — comparative

**code_inspected** — The local compaction planner splits summarized prefix from retained suffix and handles a pending assistant tool-call tail.

[Source: planLocalSlidingWindowCompaction/planLocalAllCompaction, lines 625-707](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/backend/local/compaction.ts)

**Limit:** Selected pinned source path statically inspected; no runtime or integration execution.
