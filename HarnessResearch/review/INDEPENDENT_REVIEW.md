# Independent harness research review

Reviewer: `/root/harness_independent_review`, October 18, 2026. The reviewer authored no handbook, case-study, comparison or lab files and made no edits to them. Authorization and review method: the applicable `iterate-until-verified` skill and the root agent's bounded research-review assignment.

## Current verdict

**PASS for the bounded reviewed scope, with R1 corrected and one small R2 diagram clarification left to the integrator.** General construction, context/memory distinctions, execution/recovery/security boundaries and the explicitly synthetic lab pass this independent sample review. Final mechanical validation and commit/publication belong to the integrator and are outside this verdict. This is not an exhaustive truth certificate for 170 research findings or any upstream deployment.

The primary deliverable remains general engineering knowledge. The general chapters explain mechanisms, alternatives, assumptions, failure scenarios and construction contracts. Hermes/OpenClaw are evidence cases. No framework, worker count, model/provider, memory backend or architecture is selected by analogy.

## Findings

**R1 [P2]: unrelated case evidence in the coverage map — FIXED AND RECHECKED.** Initial `COVERAGE.md:12,22,34,36,44` mapped K06 approval to skills disclosure H042, K16 skills to runtime/compression H035/H036, K28 scheduling partly to skill-write defaults H043, K30 evaluation to approval guardian H050 and K38 scope to delegation-iteration override H040. This made navigation appear source-backed while sending readers to unrelated evidence. The integrator corrected `tools/build_index.py` and regenerated Markdown/JSON. Independent read-back confirms K06 H048/H049/H050; K16 H042/H043/H044/H045; K28 H044/H045/H047/H060; K30 H054/H055/H056; K38 H023/H037/H038. Both `COVERAGE.md` and `verification/coverage.json` agree. Existing OpenClaw/comparative references remain present.

**R2 [P3]: recovery diagram confirmation edge — reported for integrator clarification.** `ARCHITECTURE_MAPS.md:57` initially sends reconciliation directly to confirmed success. A receiver supporting readback/idempotency can still fail or return an inconclusive observation. Label confirmation as conditional on conclusive success evidence and retain an unresolved/failed-reconciliation path. Surrounding prose already preserves uncertainty, so this is a nonblocking diagram clarification. Subsequent main-chat integration can fix it without starting another worker review round.

The following inspected limitations are real and correctly disclosed, so they are **review observations rather than failures**:

| Inspected boundary | Exact location | What this review established |
| --- | --- | --- |
| Sequential ownership fence | `labs/invariants.py:113-134`; `labs/README.md:30` | Ownership read and publication update are separate; concurrent atomic fencing is not implemented or claimed. |
| Limited tombstones | `labs/invariants.py:79-80`; `labs/README.md:28` | Known single-parent descendants are tombstoned; original text remains stored and unknown new origins can reintroduce content. Global erasure is explicitly excluded. |
| Synthetic context/protocol checks | `labs/invariants.py:28-53`; `labs/README.md:26` | Counts are supplied estimates and call/result IDs are balanced within units. This is not complete provider ordering/opaque-state validation or semantic summarization. |
| Simulated receiver | `labs/invariants.py:89-99`; `labs/README.md:30` | The receiver remains in memory across local journal reconnection. Server crashes, retention expiry and real network ambiguity are excluded. |
| Principal supplied by caller | `labs/invariants.py:71-77`; `labs/README.md:28` | Selection filters principal/scope, while amendment accepts a known record/version without authenticating a caller. The store explicitly disclaims authentication/authorization middleware. |
| Construction sequence | `general/10-construction-guide.md:26` | Security/persistence requirements influence early design; the stage table is illustrative and does not endorse postponing safety until late implementation. |

Do not remove these qualifications when reusing the examples. A future production implementation would need stronger contracts and adversarial runtime checks.

## Gates and evidence

| Gate | Verdict | Evidence and limit |
| --- | --- | --- |
| General knowledge remains primary | PASS | Read general 01–12, root index draft, both lessons documents and comparison chapters; mechanisms and conditional alternatives remain separate from selected architecture. |
| Memory/context correctness | PASS, sampled | Frozen snapshots, priced-prefix usage anchors, effective resolver defaults, projection persistence, provenance/taint and deletion limits independently checked below. |
| Execution/recovery correctness | PASS, sampled | Pre-effect canonical persistence refusal, unknown prior-owner work, replay boundaries, provider-specific state and external-effect uncertainty are separated. |
| Security/trust correctness | PASS, sampled | Host enforcement, sandbox/threat model, caller-supplied scope and provenance are not equated with model obedience or factual truth. |
| Effective defaults and documentation drift | PASS, sampled | OpenClaw pruning contradiction and resolved memory defaults checked against implementation and docs; Letta local memory layout scoped to local implementation. |
| Source identity and citation bounds | PASS, mechanical | Independent `check_identity.py`: all 60 Hermes + 75 OpenClaw ranges/hashes and 24 comparative cached hashes, 159 checks, zero failures; git HEADs equal recorded pins and both checkout statuses were clean. Hashes are not semantic verification. |
| Construction/data contracts/failure coverage | PASS | Read general 10–12 plus the preceding chapters; explicit contracts, unknown outcomes, state/version ownership, migration, deletion, evaluation and proposed failure catalog present. |
| Lab logic versus declared claims | PASS, bounded | Read all lab code/tests/README and runner. Independently executed 17 tests with Python 3.11. No upstream program imported or run; no provider/model/network call. |
| Hidden runtime/security/performance claims | PASS | Case studies distinguish source/test inspection from execution. Lab limitations restrict the executed claims to fixtures. No production or benchmark success inferred. |
| Index/source/coverage read-back | PASS, targeted | Read completed root README, SOURCES, COVERAGE, VERIFICATION and architecture maps; corrected R1 mappings agree in Markdown/JSON. R2 is disclosed above. |
| Final mechanical validator | INTEGRATOR-OWNED, outside verdict | The main chat performs and assesses the final structural/link checks; no worker claim that an unfinished validator passed. |
| Commit/publication completion | INTEGRATOR-OWNED, outside verdict | Reviewer did not commit. Root must confirm final files and publication state. |

## Independent semantic source sample

These IDs were selected for consequence and likely misinterpretation, rather than accepted because an author labeled them correct. The receipt freezes reviewed authored-file hashes. Source identities and ranges are recoverable from the matching evidence ledgers.

- **Hermes:** H002, H006, H010, H012, H014, H029, H034, H038, H048, H049. Read the selected implementation/documentation spans for persistence refusal, prompt tiers and refresh, whole-priced-prefix fingerprinting, effective budget arithmetic, required checkpoint handling, owner-loss recovery, fresh delegated context, whole-process isolation distinction and approval configuration.
- **OpenClaw:** OC-018, OC-023, OC-024, OC-025, OC-035, OC-036, OC-038, OC-043, OC-044, OC-045, OC-058, OC-063, OC-064, OC-065, OC-066, OC-067. Read fence checks, saved projection markers versus unchanged result rows, the conflicting pruning table/guide, normal resolver values, query/index-source distinction, declared network taint, origin promotion filters, child admission, policy composition, admitted authority, sandbox defaults, exec constants and documented gateway trust boundary.
- **Broader cases:** C05, C12, C13, C14, C16, C17, C22, C23, C27, C34. Read selected cached official Pi persistence/tool paths, LangGraph SQLite writes/interrupt contracts and Letta session/memory documentation/local layout and compaction code. The limited local-vs-hosted scope is preserved.
- **General foundations:** G01, G05, G06, G15. Independently reopened official [MCP architecture](https://modelcontextprotocol.io/specification/2026-07-28/architecture), [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction), [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) and [AWS idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). Reviewed host responsibilities, route-specific opaque compaction continuation, matching eligible rendered prefixes and receiver-side same-intent/parameter-mismatch rules. These are checked-date documentation, not permanently pinned service behavior.

## Actual review execution and limits

Independent test command: `python -B -m unittest discover -s HarnessResearch/labs -p 'test_*.py' -v`. Result: **17 tests, zero failures/errors**, host Python 3.11, 0.092 seconds reported by unittest. This does not replace or alter the root's separate Python 3.12.14 lab receipt.

The independent identity script only reads local public sources and authored ledgers and writes review-owned JSON. An initial stdin-pipeline invocation stalled and was interrupted without a result; the saved-file invocation subsequently completed successfully. No result is attributed to the interrupted attempt.

No Docker, visible browser, application installation/startup, personal account/service, protected benchmark data, provider call, upstream mutation, benchmark run, concurrency fault injection, semantic summary/retrieval evaluation or production security audit occurred. Live foundation checks used the non-visible web retrieval tool. The reviewer did not verify every branch/caller/plugin or every substantive claim. General conceptual coverage and selected high-consequence support can pass while remaining empirical questions stay unresolved.
