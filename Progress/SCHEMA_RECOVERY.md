# t021 rerun: nested schema feedback was discarded

## Observed execution

`HealthHarnessCodex/runs/20261023-hybrid-t021-02` finished with an error after
12 bootstrap identity calls and 3 workflow calls (15 total), 4 counted workflow
tool proposals. Identity comparisons validated and the ambiguity investigation
selected a candidate. The workflow read the chart, candidate orders and
ordering-provider roster. It then proposed `case.retrieve_evidence` with nine
queries in its first request and one query in its second request. The first
request exceeded its declared maximum of eight queries. No retrieval request
was dispatched. The single correction repeated the exact invalid list.

This is different from -01's identity-quote failure, but both expose insufficient
correction feedback. Neither result establishes retrieval quality. The -02 world
was snapshotted and stopped; batch status is deferred_ready. No judge ran and
there is no official score. A saved snapshot of a failed workflow is not a
successful benchmark result.

## Root cause

The schema validator correctly raised `array length at $.requests[0].queries
is out of bounds`. `_safe_validation_feedback` had no array-length category.
Its path filters also omitted array indexes in several categories, and its
schema-path checker only looked at top-level properties. It discarded the
specific error and gave the model only `arguments_rejected`. The retry had no
identified failing field or bound. The terminal message incorrectly conflated
an exhausted single correction with missing identity or aggregate call budget.

## General repair

Code now traverses declared object properties and array item schemas to validate
feedback paths, recognizes array/string/numeric bounds and indexed paths,
and returns the declared constraints without copying argument values or unknown
field names into feedback. Example:

```json
{"category":"schema_array_bounds","path":"$.requests[0].queries","constraints":{"maxItems":8}}
```

The correction instruction explains that investigation items can be grouped
within valid entries of the same tool request when the schema permits. It does
not silently drop searches, dispatch invalid requests, increase retry budgets,
select a patient or prescribe a clinical result. Failed-correction terminal
text now reports that specific condition.

## Verification and boundaries

44 focused engine tests passed in 3.174 seconds. Regression tests cover the
actual nine-versus-eight structure, indexed path visibility, no disclosure of
query/source strings or unknown keys, and recovery through real engine/local
retrieval dispatch with a synthetic model. The regrouped request preserves all
searches and does not repeat the original source read. A first test development
failure used the wrong synthetic tool name; production validation was retained.
Full suite: **506 passed in 46.909 seconds**;
`HealthHarnessCodex/runs/20261023-schema-release-tests.log`.

One actual Luna-high diagnostic completion was also run against the saved case
conversation, replacing the discarded error with structured feedback and an
explicit instruction to preserve searches by valid grouping. It returned one
schema-valid `case.retrieve_evidence` proposal preserving all ten original
source/query pairs across both source IDs. No proposal was executed. Input
56,274/output276 tokens, one generative call, zero paid judge calls; saved SQLite
hash unchanged. This diagnostic added correction guidance as well as replacing
feedback; it is not a controlled causal comparison or a full healthcare run.
Private receipt: `HealthHarnessCodex/runs/20261023-schema-live-replay.private.json`.

The previous identity-feedback fix was never sufficient evidence that a fresh
full workflow would work. Do not ask the user to treat software tests or this
correction diagnostic as a passed t021 case. Preserve -01 and -02 separately;
do not resume either under changed source. No fresh benchmark case was launched.
