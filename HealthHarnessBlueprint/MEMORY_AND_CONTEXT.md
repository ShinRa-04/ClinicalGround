# Memory and context for the proposed harness

The design separates authoritative state from what any worker remembers or believes. The [memory-layer catalogue](MEMORY_LAYERS.md) defines ten logical surfaces; they can share storage infrastructure while retaining different contracts.

## Case truth versus working memory

In the primary χ-Bench mode, supplied records and actual tool responses establish environment observations. Our case state is a versioned derived working view: current task, known source IDs, actual observed stage, pending obligations, unresolved questions, actions/receipts and next owners. If it conflicts with a fresh authoritative observation, the conflict is recorded and reconciled rather than hidden by a summary.

Keep provider, payer, patient conversation and CM namespaces distinct. A journey ID can correlate episodes without making all records visible to all participants. Retrieval must carry principal, purpose, organization, patient/case, source version and sensitivity scope as appropriate. Exact real tool metadata is not assumed to exist; the adapter must document what can actually be verified.

## A proposed model-request packet

1. Stable role/assignment, operation limits and actual task instructions.
2. Protected active user request, current scope and unresolved obligations.
3. A compact case/journey snapshot with authoritative evidence references and explicit unknowns.
4. Applicable policy identity/version and only the relevant criteria/exceptions.
5. Coherent recent interaction/tool exchanges with speaker and call/result identity.
6. Bounded task-relevant recall or specialist proposals, each labeled by source/trust/version.
7. Requested output/action format, remaining budget and stop/clarification conditions.

The builder measures the actual rendered request where possible and reserves output/recovery capacity under the chosen provider contract. A universal token threshold or one summarizer model is not prescribed. If protected essentials cannot fit, retrieval/restructuring/explicit failure is preferable to silently dropping them.

## Compaction checkpoint

Before replacing old context, preserve goal, case/principal/role identity, outstanding obligations, actual patient answers/refusals, relevant representation facts, policy/source versions, unresolved contradictions, in-flight action IDs and outcome-unknown states. Preserve complete tool units and provider-native opaque state where required. Retain references to original evidence so a summary omission can be investigated.

A summary is a derived continuity aid, not a new chart entry. “No record found” must not become “condition absent,” a submitted packet must not become approved, and a scheduled visit must not become completed. A new user instruction or source update during compaction invalidates the older publication snapshot and requires reconciliation.

## Long-term knowledge

Keep approved policy documents separate from generated policy interpretations. Reusable workflow procedures contain prerequisites, applicable versions and validation evidence; they do not contain patient-specific answer keys. Role profiles contain the job definition, not patient-derived personal memories. Episodic memory is restricted to the current permitted patient/case/task; it cannot teach another patient's worker how to behave.

The user explicitly requires cross-patient independence. No automatic consolidation of patient experience into shared role prompts, skills, preferences, workflow habits or model weights is proposed. [Patient isolation](PATIENT_ISOLATION.md) defines the hard boundary and the proposed verification property. Reusable roles mean reusable job definitions with fresh/scoped execution state, not carrying patient context between jobs.

Start retrieval with exact IDs, structured filters and lexical search where adequate; add semantic/hybrid retrieval only if query/task evaluation justifies it. Ranking similarity, recency or frequency cannot promote an untrusted statement into authority. User corrections and revoked sources need version/tombstone behavior across derived notes/indexes.

## Delegation

A specialist receives a bounded question, scoped evidence references/versions, permitted tools, output contract, budget and stop rule. It returns observations versus interpretations, criterion mapping, missing evidence, contradictions and proposed actions. It does not receive hidden scenario/evaluator truth or unrelated patient memory.

The owner checks case/version/scope before using the result. Independent worker contexts are an attention/engineering choice, not proof of professional authority or uncorrelated error. Shared model serving can remain possible while sessions/principals and data permissions stay separate.

## Cache and deletion

Prompt/KV cache is an inference-performance resource; a retrieval index is a derived search resource; neither substitutes for the case store. Tool-result cache freshness depends on actual record/version semantics. Do not reuse stale coverage, consent or availability merely because the text is cached.

Provenance should identify where facts/notes/summaries came from. Forget/correction policy must consider stored episodes, derived profiles/procedures, indexes and future re-ingestion—not just one visible memory line. Retention/legal obligations and production deletion guarantees are not established by this hypothetical design.

The design follows the mechanisms learned in [HarnessResearch](../HarnessResearch/README.md), not a copied Hermes/OpenClaw file layout or threshold configuration.
