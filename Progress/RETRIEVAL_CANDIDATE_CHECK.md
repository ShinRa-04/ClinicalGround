# Real-reference candidate check and coverage repair - October 23, 2026

## Scope and relevance labels

The user requested checking retrieval before their benchmark run. Root used
permitted policy references and original actor-visible notes from the saved
t021 execution, not hidden benchmark expectations or judge answers. Nine
positive queries and one unrelated control were frozen before ranking. Policy
targets came from the prior permitted policy review; narrative targets came
from note kinds/titles. These are development source-retrieval labels, not
clinical decision ground truth, a held-out set, or a complete relevance pool.
Other returned notes can also contain useful overlapping information.

All three private query-set files have SHA-256
`25d603a3605966e17ac22d4d052c5860a3260ae7dab48c3b2b858550ad612b2f`.
Labels were used only to evaluate results; they were not inputs to the encoder,
ranker, production filters or policy decisions. No patient-specific answer or
expected disposition was inserted into production behavior.

## Confirmed original defect

The first check collected only 42 policy documents and indexed an alphabetical
prefix capped at 1,024 chunks. The relevant site-of-service and shoulder files
were not indexed. All six policy queries therefore missed their preselected
target. All three narrative targets were already in the top five. This was a
real collection/coverage defect, not proof that embeddings failed semantically.
The earlier two-document smoke check had not established real-corpus coverage.

The permitted medical-policy directory contains 256 files, 17,049,231 bytes;
one file exceeds the old 1 MB file cutoff. Keeping a partial flag did not make
prefix ranking adequate for this task.

## General repair, including the user's cache decision

- Collection now follows bounded internal transport cursors until every
  permitted source fragment/page is assembled. Full manifest hashes before,
  during and after collection prevent mixed source versions. Transport pages
  are not separate search corpora. No source-prefix rank is returned.
- Indexing covers the whole collected corpus; GPU embedding still uses bounded
  512-chunk requests. Resource limits fail explicitly instead of silently
  truncating the search domain. No target filenames or query-specific rules
  determine indexing order or ranking.
- The user approved cross-case caching of fixed reference embeddings. Only
  reader-verified fixed-handbook sources qualify. SQLite stores chunk hashes
  and vector blobs keyed by encoder identity; no patient text, query text,
  patient/query vectors or decisions enter that shared cache. Patient narrative
  indexes remain case-local. Changed text/model identities cannot reuse stale
  vectors; connections are explicitly closed on Windows.
- Working source text is reused only after its full manifest is revalidated.
  Candidate packing stops at the output budget rather than repeatedly rebuilding
  context for every lower-ranked chunk in the corpus. Partial output remains
  explicit and is different from incomplete source coverage.

Hard collection ceilings: 5,000 files, 50 MB total source bytes, 10 MB per file,
1,000 PDF pages; index ceilings: 10,000 source/page documents, 50 million text
characters and 60,000 chunks. Unsupported/encrypted/non-text sources or an
incomplete collection return an explicit error, not a prefix ranking. No OCR
was added. Source path/hidden-file restrictions remain unchanged.

## Actual final-logic results

Complete corpus: **256 policies / 21,199 chunks**, plus 11 saved narrative text
sources in their separate namespace. GPU model/image unchanged from the prior
implementation. Results from the fresh-context confirmation:

| Query category | Expected source rank in returned hybrid candidates | Vector-only first target-chunk rank |
|---|---:|---:|
| Site of service, direct wording | 1 | 1 |
| Site of service, paraphrased wording | 2 | 1 |
| Equipment access requirements | 1 | 1 |
| Equipment-preference qualification | 1 | 1 |
| Shoulder surgery criteria, direct wording | 1 | 1 |
| Shoulder surgery criteria, paraphrased wording | 1 | 1 |
| Imaging narrative | 1 | 1 |
| Surgical planning narrative | 1 | 1 |
| Prior conservative-treatment narrative | 4 | 4 |

Expected source present in top five: **9/9**; first returned source: **7/9**.
Vector-only target chunk first: **8/9**, top five: **9/9**. These are different
metrics: raw chunk ranks precede deduplication and output-budget packing.
The previously reviewed exclusion line appeared verbatim in returned original
context for **4/4** relevant site-of-service queries. This verifies text presence,
not correct clinical interpretation or that every qualification was returned.

The fresh-context policy check reused **21,199 cached reference vectors**.
Only seven policy query embeddings ran; no reference-document embeddings were
repeated. Narrative data was separately re-embedded and not shared. Returned
character spans were checked against original sources; the saved case SQLite
hash was unchanged. Zero generative actor calls, paid calls or benchmark tasks.
All disposable audit/embedding containers were removed.

Cold development run: 522.453s. Final-logic warm confirmation: 89.250s, including
diagnostic ranking recomputation and all ten queries. Do not attribute this
entire difference to caching: candidate-packing code also changed between these
development runs. No controlled speedup or full-task token reduction is claimed.

## Unrelated-query control: ranking is not applicability certification

Historical ungated check (superseded for relevance filtering by
[the calibrated screen](RETRIEVAL_RELEVANCE.md)): the control asked about a spacecraft liquid-oxygen pump. Medical policies were
still returned as the closest available candidates. They were genuine source
text but did not answer the question. That version had no validated no-match
rejection; similarity/rank is not a probability of correctness.

The worker must assess procedure/plan/setting/version applicability and relevant
conditions/exclusions, and can determine that no returned source applies. A
separate rejection/evidence-sufficiency mechanism would require testing; no
arbitrary cutoff was tuned on this single unrelated example. Positive target
hit rates do not establish absence detection or certify the first result.

## Evidence and verification boundaries

Private artifacts, all under ignored `HealthHarnessCodex/runs/`:

- `20261023-hybrid-candidate-audit-01/`: original incomplete-index failure.
- `20261023-hybrid-candidate-audit-02/`: complete-corpus cold development check.
- `20261023-hybrid-candidate-audit-03/`: final-logic warm-cache confirmation,
  frozen queries, exact results, summary and cleanup receipt.
- `reference-cache/`: fixed-reference vectors only.

Final-logic source fingerprint at audit launch and afterward:
`277db8229f93df8cbf914c0076941786a6d47c75c31ebbfdf54d897bbd61680c`.
Software suite: 496 passed / 68.741s; an additional real-reader regression with
300 files confirms a late alphabetical target is collected and ranked. Final
full suite: **497 passed / 42.987s**,
`runs/20261023-coverage-candidate-release-tests.log`. The first full late-file
regression exposed a Windows drive-letter case mismatch in its assertion; the
test now compares canonical paths. No production source change was needed
for that assertion. No new official score exists; the previous case's
8-pass/3-fail/1-N/A diagnostic is unchanged. The user will run the next case.
