# Contradictions, transferable choices and remaining verification

[Index](README.md) · [Execution](EXECUTION.md) · [Context](CONTEXT.md) · [Memory](MEMORY.md) · [Operations](OPERATIONS.md)

## How conclusions were reached

This workstream used official repository/docs, a frozen Git commit, selected call-path inspection and selected upstream tests. The ledger records claim, status, source lines, hash and limitations; readers can reproduce the cited source selection without trusting a prose summary. Conflicts were resolved by distinguishing maintained intent from the current code path, not by assuming a newer-sounding phrase is correct. Our engineering recommendations are explicitly synthesis rather than claims that upstream measured them.

The transparent record is a **decision/evidence trail**: question, inspected alternatives, decisive source, conclusion and uncertainty. It is not a claim to publish a model's private internal reasoning or that verbose reasoning itself is factual evidence.

## Material documentation drift found at the pinned commit

| Question | Conflicting source text | Scoped conclusion |
|---|---|---|
| Where do skills sit in the cached prompt? | Prompt guide first describes volatile index, then says skills are stable. | Code puts general index in volatile; explicit pinned skill bodies are stable. Use [builder](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/system_prompt.py#L737-L822), not the contradictory sentence in [guide](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/prompt-assembly.md#L25-L43). |
| Does compression always fire at 50%? | Many overview diagrams say 50%. | Base config is 50%, effective ratio floor is 75% below 512k, plus output reservation, minimum floor, overrides and caps. See [effective trigger](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/context_compressor.py#L2761-L2807). |
| Does anchor identity cover only a boundary row? | Compression guide warns that it does not fingerprint the entire prefix. | Code captures and checks `base_prefix_fp` over every priced message as well as final-row fingerprint. It still is not a complete independent hash of external system/tool/config inputs. See [anchor](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/usage_anchor.py#L42-L108) and [guide](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/website/docs/developer-guide/context-compression-and-caching.md#L136-L145). |
| Do children share the parent's iteration budget? | Agent guide says default 500 shared with children. | Current child constructor passes `iteration_budget=None`; delegation config defaults 250 independently per child. See [construction](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/delegate_tool.py#L277-L292), [agent guide](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/AGENTS.md#L8-L17). |
| Does cron skip memory? | Agent guide says `skip_memory=True` by default. | Actual scheduler passes false and separately skips background review. See [scheduler](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/cron/scheduler.py#L2515-L2530). |
| Does session recall require an auxiliary model? | Some older provider-oriented descriptions group session search with auxiliary work. | Current built-in tool says no LLM calls and returns actual DB messages. Do not extend that conclusion to optional external providers. See [tool](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tools/session_search_tool.py#L1-L8). |
| Is the whole current API limited to three modes? | Agent-loop guide enumerates three API modes. | Transport registry includes Bedrock and plugin-registered modes, while loop supports whole-turn Codex app-server path. Three-mode overview is incomplete for this pin. See [registry](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/transports/__init__.py#L17-L56) and [route](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/agent/conversation_loop.py#L1645-L1651). |

These are research qualifications, not a claim that all documentation is obsolete or that each mismatch causes a runtime bug. Existing user configuration and migration history also mean defaults alone cannot reconstruct an actual installation's behavior.

## Mechanisms worth understanding, with legitimate alternatives

| Hermes mechanism | Problem it addresses | Alternative to investigate | New failure introduced or left open |
|---|---|---|---|
| Frozen prompt plus append-only history | Prefix-cache reuse and reproducible replay | Rebuild minimal request from structured state each step | Frozen stale facts versus rebuilt prefix cost. |
| Real usage anchors plus estimated delta | Estimator inflation and provider accounting | Provider count endpoint, local exact tokenizer, request budget reservation | Counts can be missing or stale; extra count calls add latency/cost. |
| Lossy middle summary plus verbatim tail | Window pressure while retaining recent detail | Retrieval/archive tree, branch selection, domain state machine | Summary drift, retrieval misses or state-model omissions. |
| Tiny curated fact/profile files | Stable cross-session facts cheaply visible | Scoped record DB with TTL/provenance, explicit per-project memory | Incorrect preference/generalization can contaminate unrelated work. |
| FTS transcript recall | Recover past evidence without model synthesis | Hybrid lexical/vector search plus reranking | Rank bias, outdated claims, private-data scope. |
| Progressive-disclosure skills | Reuse procedures without loading whole library | Typed workflows, scripts, deterministic services | Procedures can be stale or unsafe, and maintenance can cost model calls. |
| Durable input FIFO and owner epochs | Crash recovery and concurrent writers | Workflow engine/event log with transactional outbox | External side effect can remain unknown; automatic replay may be unsafe. |
| Fresh bounded child agents | Parallel focused work without parent-context flood | Single owner switching modes; persistent role workers | Missing handoff context, duplicated effort, aggregate spend and result loss. |
| Versioned provider/context/memory seams | Extend without multiplying core branches | A deliberately small closed implementation | Plugin compatibility and trust become separate responsibilities. |

The alternatives are engineering hypotheses to test. This comparison does not establish Hermes, OpenClaw or another framework as the best basis for our benchmark harness.

## Upstream tests inspected, not run

| Test source | Intended contract visible in assertions | What was established here |
|---|---|---|
| [Memory tool tests](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tests/tools/test_memory_tool.py#L405-L463) | Save/load roundtrip, oversized-load warning and frozen snapshot after mutation | Test implementation read; no pass/fail execution result. |
| [Usage-anchor tests](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tests/agent/test_usage_anchor.py#L118-L160) | Rewrite invalidates anchor even if final priced row survives; identical reload remains usable | Supports intended fingerprint contract, not vendor-tokenizer accuracy. |
| [Runtime admission tests](https://github.com/NousResearch/hermes-agent/blob/e6f57427c198cfd96854522b7a9159eb007e13c2/tests/hermes_state/test_runtime_admission.py#L1-L94) | Retry identity, conflicting payload refusal, FIFO, epoch/generation fences, unknown after restart, transactional failure | Asserted test coverage inspected, not proof of production reliability. |

Installing dependencies or running the application was unnecessary and outside this source-review scope. Upstream instructions require their isolated test runner/environment; those were respected by not launching a partial improvised application test suite. Our local evidence script only reads text, verifies line ranges and hashes, and writes the authored ledger. Such structural checks validate our citations, not Hermes runtime behavior.

## Questions a real implementation study must still answer

1. Does a chosen provider report usage consistently through cache hits, images, tool schemas, hidden reasoning and native compaction? Can our harness reproduce billed totals without double counting?
2. What is retained in an actual provider request before/after compression, tool spill, native response replay and fallback? Does our task-critical evidence survive?
3. Which external actions expose stable operation IDs and safe readbacks? How will an unknown effect be reconciled after owner loss?
4. Can every background write, callback, child process and remote retrieval be attributed to the owning profile/run/task?
5. Does a memory provider's acknowledged checkpoint mean durable storage? How are extraction retries, duplicates, cross-session scope, conflict resolution and deletions implemented?
6. How are memory/skill candidates promoted only after adequate evidence, and how do we revoke a false lesson propagated to summaries and later sessions?
7. Do separate role workers improve task success enough to justify duplicated context, coordination and aggregate budget? Which functions need independent review versus ordinary tool/service calls?
8. Is the selected deployment a trusted single-user process, a benchmark sandbox or a multi-tenant service? Does isolation cover the entire process tree and network rather than just terminal commands?
9. Can we collect useful diagnostics without protected content, provider credentials or sensitive task material in logs and external telemetry?
10. Which advanced features should be absent from a minimal first harness? A gateway, scheduler, desktop UI or auto-learning loop is not a prerequisite for reliable autonomous task execution.

No optional memory backend, platform adapter, credential flow, whole-process sandbox, native compaction API or complete plugin catalog received an exhaustive audit. No network-provider experiment, application launch, performance benchmark or medical/compliance assessment was performed. The root handbook should retain these omissions when reusing this case study.
