# Basic relevance filtering and retrieval progress

## Responsibility and method

The user requested a relevance floor derived from ambiguous relevant queries,
with routine calibration delegated to a Luna-high agent. Root owns production
code and review; `/root/relevance_calibration` collected local GPU scores and
ran read-only validation. No benchmark actor or paid judge was called.

This screens query relevance, not clinical applicability. The worker still
decides which policy governs the person, plan, procedure, setting and date.
Cosine is not a probability, and increasing ambiguity does not necessarily
decrease cosine. An empty result means no indexed passage cleared this screen;
the model can refine its query or use permitted exact reads. It is not proof
that information does not exist.

The frozen calibration used three ambiguous relevant queries per corpus. The
policy set targeted hospital versus ambulatory surgery location and shoulder
surgery prerequisites. The independent synthetic narrative set targeted scan
findings, facility rationale and prior treatment. Synthetic notes were newly
invented, not derived from a patient. A shared narrative floor was not tuned
from saved patient data.

| Corpus | Minimum expected-target cosine | Configured floor |
|---|---:|---:|
| Fixed reference policies | 0.6651826 | 0.665 |
| Independent synthetic narratives | 0.5870627 | 0.587 |

Floors round down to three decimals to avoid rejecting calibration-boundary
positives through float serialization differences. They are minima of the
**expected source's best chunk**, not maxima over arbitrary candidates. The
validation negatives did not determine the floors. The small probe set is
development calibration, not a universal relevance guarantee or held-out
benchmark measurement.

Pre-filter diagnostics: two additional policy positives and five saved-chart
positive queries exceeded their respective floors. Four unrelated controls
(spacecraft pump maintenance, Python debugging, parking fees, banana bread)
were below the floor in each calibration corpus. Closest negative policy
query scored 0.6549, only about 0.0103 below the unrounded policy floor.
Before filtering, one ambiguous policy target was dense rank 1 but outside
the hybrid top 5; this is why actual filtered returned results must also be
checked rather than inferring retrieval quality from cosine alone.

Private receipts, frozen synthetic/query sets, full source spans and source
hashes remain ignored under
`HealthHarnessCodex/runs/20261023-relevance-floor-calibration-01/`.
Saved-case databases remained unchanged. This is a read-only retrieval check,
not evidence that the healthcare workflow is now successful.

Actual gated validation (`-02`, same frozen inputs): policy targets retained
4/5, synthetic narrative targets 3/3, saved-chart validation targets 5/5;
all eight negative controls returned empty. These 12/13 source hits combine
calibration and validation examples, not a held-out estimate. The omitted
policy target was from the broad query "When is the hospital location
justified?". Its best cosine was 0.6755, above the cutoff; its dense source
rank was 9. Ambulance and imaging site policies ranked ahead, and bounded
output returned only two matches with `output_partial=true`. The cutoff did
not discard the expected policy; the complete corpus was indexed. Do not
claim this broad-query ranking limitation solved. The more specific policy
validation queries retained their expected sources. The -02 receipt has null
source hashes due to its script's path-resolution error; keep it preserved
and use a separately captured final-source receipt for provenance.

Final-source confirmation `-03` repeated all 21 frozen queries with the same
results: 4/5 policy, 3/3 synthetic and 5/5 saved-chart source hits; 8/8 empty
negative controls. Pre/post hashes for retrieval code, calibration JSON and
local runtime configuration are non-null and identical. Input hashes match
the earlier runs. All source spans verify, both saved databases are unchanged,
21,199 reference vectors were reused and the exact owned read-only/network-none
container was removed. Zero actor, paid or judge calls. Private receipt:
`HealthHarnessCodex/runs/20261023-relevance-floor-calibration-03/summary.private.json`.

Software verification: 502 tests passed in 51.146 seconds, log
`HealthHarnessCodex/runs/20261023-relevance-release-tests-02.log`.
The first full check failed because two standalone test doubles lacked the
new optional progress parameter; their signatures were updated. No production
exception was suppressed to make those tests pass. These checks establish
mechanics, not healthcare-task performance.

## Implementation

`health_harness_codex/data/relevance_floors.json` pins the model and runtime
image used for calibration. A configured encoder/image change requires
recalibration. Source fingerprints include all data JSON so the operator's
floor configuration is part of a frozen run.

Native `workspace.hybrid_search` and `case.search_narrative` supply these
floors to `HybridIndex`. Chunks below the applicable cosine floor are removed
**before** BM25/dense reciprocal-rank fusion; rejected candidate text and
metadata are not returned. Original context/qualifiers from retained sources
remain available. The result reports the cutoff, best cosine and counts.
The generic index can explicitly remain ungated for diagnostics; native tools
do not offer the model an argument to disable or change the floor.

## Tool lifecycle and progress

Yes, vector retrieval is a tool capability. Within a single invocation:

1. `checking_corpus`: validate the current permitted source manifest.
2. `collecting_corpus`: read all sources if its manifest changed.
3. `checking_vector_cache`: reuse unchanged in-memory/static reference vectors.
4. `indexing`: embed missing chunks in bounded GPU batches, reporting counts.
5. `indexed_retrieving`: embed the query, score, filter and rank passages.
6. `retrieval_finished`: return bounded original passages with provenance.

Warm searches report `indexed` and skip document embedding when nothing is
missing. Progress goes to run events and console/live logs, not another model
completion. The generative model receives the final tool response when the
call returns; it does not have an active status conversation while waiting.
Embedding queries/chunks still incur local GPU computation, recorded
separately from the actor's generative-call limit. Logs contain stages/counts,
not patient text, query text or source passages.

Follow-up logging repair: retrieval stages now include `tool_name` to distinguish
`workspace.hybrid_search` from `case.search_narrative`. Internal `case.*` calls
also emit `LOCAL_TOOL_START` and `LOCAL_TOOL_END`, with the tool name, duration
and success/error outcome. Previously they bypassed the external-tool logging
wrapper. Separate event kinds preserve existing external dispatch accounting.
No arguments or result text are added to console messages. These are visibility
changes; they do not solve the separately observed context-budget exhaustion.

## Case-query cache update

The user subsequently authorized implementation. Case-private SQLite query
vectors and results now support exact reuse on unchanged sources/config and
similarity comparison for new queries. Approximate answer reuse remains disabled;
new queries are independently ranked. See [implementation and measured checks](RECOVERY_AND_CACHE_REPAIR.md).

### Historical proposal

The user proposed embedding a query and comparing it against queries in a
case-local SQLite cache. This was originally deferred until the later authorization above.
It could reduce repeated scoring/retrieval, but semantic similarity alone is
not enough to reuse an answer. A change in negation, date, setting, status or
evidence scope can change the result despite high similarity.

A future design must bind entries to exact case namespace, permitted source
IDs and content hashes, corpus version, encoder, filter configuration and
retrieval parameters; invalidate on changed evidence/reselection; preserve
original source provenance; and never share patient/query vectors across
cases. Prefer an exact-query cache first, measure duplicate frequency and
latency, then evaluate whether approximate reuse adds useful savings. Cache
retrieved passages, not clinical decisions or claims about fresh mutable state.
