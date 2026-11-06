# Retrieval mechanism, grouped reads and semantic-search assessment

## What was actually implemented before this repair

The harness used model-directed tool retrieval, with typed JSON-field inspection
and literal case-insensitive phrase search. It had no BM25 index, embedding
model, vector database or learned relevance reranker.

- External actor tools fetch patient/case/form/document data. Code stores full
  original responses; the model receives bounded views.
- `case.inspect_evidence` selects a JSON field, with offset/limit paging.
- Legacy `case.search_evidence` searches serialized original JSON for a literal
  phrase and returns small excerpts. `case.read_evidence` opens JSON character
  ranges. JSON-envelope/escaping coordinates differ from business text fields.
- `workspace.search_files` searches permitted UTF-8 files for literal phrases.
  It skips PDFs. File/PDF readers fetch known paths and bounded text passages.
- Context projection retains source indexes and selected historical excerpts.
  Long nested fields can be omitted, requiring another model-directed inspection.

This made the model a fine-grained data navigator: decide the source, identify a
field, inspect it, guess search wording, open a chunk, ask again. In the saved
t021 run, calls 26-38 only navigated existing observations and activated a tool;
they fetched no new hospital record/reference file and used 658,183 reported
tokens. See [complete call audit](MODEL_CALL_RETRIEVAL_AUDIT.md).

Literal matching is strict about wording and weak about meaning. It can miss a
relevant passage with different wording, or find a phrase in an irrelevant or
qualified clause. A matching phrase does not establish policy applicability.
The diagnosis is evidence navigation plus representation/orchestration overhead;
the record does not establish that semantic search alone would fix the run.

## Approved grouping, now implemented

1. **Initial useful fields together:** bounded working observations now include
   attributed child fields/first excerpts with actual JSON pointers and explicit
   omissions/continuations. This improves visibility of patient, case, coverage,
   request, form and other returned fields without a model turn per child.
2. **Grouped stored-source questions:** `case.retrieve_evidence` handles up to
   twelve original-source requests, each with multiple field paths and literal
   phrases. It searches decoded business text fields, not escaped JSON copies.
   Exact passages retain original evidence IDs, text pointers and start/end
   offsets compatible with the policy-record source-capture mechanism.
3. **Bounded results and continuation:** output is capped at 4,000-24,000
   characters; unprocessed fields/queries and outer request continuation remain
   explicit. Search `next_match` resumes through `search_offset`, preventing
   repeated first-hit pages. Search traversal is bounded; partial search is not
   proof that a fact/policy is absent. Legacy inspection/read/search tools remain.
4. **Grouped documents/references:** `workspace.read_many` permits up to six
   existing `read_file`, `read_pdf` or `search_files` operations, with a shared
   output budget and existing path/reference/hidden-file restrictions. It does
   not follow discovered paths automatically or permit writes. A source must be
   located before a later request reads that source.
5. **Provenance and context:** grouped excerpts retain original source IDs across
   context projection. Policy citations can point into a batch child read;
   search snippets, error results and unauthorized files cannot become governing
   policy citations simply by being in a batch. Patient/operation decisions and
   clinical interpretation remain with the worker. Historical views do not
   establish fresh post-write state.

These are deterministic code operations, not model helpers. One model request
proposing several tool operations still counts as one model call; executing
those operations does not itself invoke another model. Every actual request to
Luna, including an independent candidate assessment or helper inference, counts
against the aggregate model-call budget. Parallel inference changes latency,
not that count. The candidate comparisons were judgment calls over records
already retrieved, rather than ten fresh hospital lookups.

## Would vector search help?

For policy/reference discovery it is worth testing semantic retrieval alongside
lexical ranking. Vector retrieval finds conceptually similar wording; lexical
ranking helps exact technical terms, identifiers and codes. Official primary
sources describe combining them as hybrid search:

- [Microsoft: hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
- [Anthropic: contextual retrieval](https://www.anthropic.com/research/contextual-retrieval)

For this harness, the proposed split is exact typed retrieval for current case
fields, and a tested hybrid candidate finder for written policy documents.
Similarity should identify candidate passages, not decide patient identity,
current case status or policy eligibility. Retrieved clauses need source/version
metadata and surrounding conditions/exclusions; contextless chunks can omit
qualifications. Patient indexes, if ever introduced, must remain case-isolated.

No embedding/vector search, BM25 index or reranker was installed in this repair.
No retrieval-quality or token-saving claim for hybrid search has been measured.
Grouped retrieval repairs round-trip granularity; it does not supply semantic
matching or prove completion of the clinical workflow.

## Verification evidence and remaining limits

Initial full suite: 477 tests passed / 48.918s. Search continuation was then
added; all nine grouped-retrieval tests passed. Final full suite: **478 tests passed / 56.422s**, log
`runs/20261023-grouped-retrieval-final-tests.log`.
Tests cover source-field types, exact Unicode spans, original source references,
same-case rejection, bounded/partial outputs, continuation, retained context,
engine model-call accounting, real workspace-program path/hidden-file boundaries
and batch-child policy citations. No protected text is tracked here.

A read-only check against the saved actual case requested four case fields and
three phrases from an already-retrieved policy source together. It returned
four fields and eight exact policy passages in 7,294 output characters, with
search continuation explicitly marked. Zero model calls, paid calls or new
external fetches. Original SQLite state hash unchanged. Private output/receipt:
`runs/20261023-policy-grounded-t021-04/grouped-retrieval-check.private.json`.
This verifies retrieval mechanics, not semantic relevance or saved model turns.

No fresh actor trial or judge run was performed for this change. The prior
8-pass/3-fail/1-N/A deterministic result is unchanged; official semantic grading
and full-dataset reliability remain unmeasured. Software tests and offline
retrieval checks do not establish benchmark success.
