# Bootstrap recovery and retrieval caching repair

October 23, 2026. Root implemented and reviewed the changes; no delegation.
This repairs the recorded integration failures and adds the user's case-query
cache. It does not claim a new t021 workflow result or official benchmark score.

## Bootstrap recovery

The provider still rejects malformed JSON before executing any proposal. A
shared formatting-correction instruction now serves the main workflow,
isolated candidate comparisons and identity investigation. Candidate comparisons
use their existing two-attempt bound, shared with quote correction. Investigation
allows one format correction inside its existing six-attempt maximum, not an
extra invisible call. The standalone callback counts failed calls against the
aggregate budget and retains the workflow reserve. Usage accounting includes
provider-format failures through the existing recorder.

Successful candidate reads and source IDs survive correction. Malformed replies
are not inserted as successful messages or executed, and no code guesses how to
repair their argument JSON. A repeated format failure, exhausted context/calls,
unsupported identity or actual provider quota error still stops safely. The
audit records failed-attempt number/stage. It does not retain malformed patient
text. The nested JSON transport itself remains unchanged.

Verification: first/middle/last failures, repeated failure, non-format exception,
successful-read retention, comparison retry/aggregate accounting, and the
existing patient/isolation/provenance suite. A live Luna-high **synthetic fault
injection** used two actual completions plus one deliberately injected format
exception. It selected the supported synthetic candidate after retaining two
successful read references. No real case or external clinical tool was involved.
Reported usage:14261 input/346 output,14607 total. Receipt:
`HealthHarnessCodex/runs/20261023-bootstrap-live-smoke.private.json`.

## Fixed-reference vector reuse and concurrent builders

Eligibility is now decided per verified chunk/document, not all-or-nothing for
the selected directory. A mixed handbook corpus can load and populate approved
reference vectors while keeping other material in the current index only.
Neither patient-derived chunks nor query vectors enter the shared cache.

SQLite leases coordinate missing chunk keys per encoder/content identity. A
worker claims a bounded batch, rechecks completed vectors and waits for another
builder rather than duplicating its embeddings. Writes are transactional; leases
are released on success/error, expire after a crashed worker and have a bounded
wait. No SQLite transaction is held open during GPU inference. Encoder and
case bindings are checked after atomic initialization as well as on reuse.

The complete permitted corpus is still collected and ranked; no alphabetical
prefix limit was restored. Up to four manifest-validated source collections
within a 50-million-character aggregate budget can remain in memory when the
worker alternates policy/requirements directories. Logs name the tool and show
cache hits/misses, unique chunk counts, indexing and waiting work without
printing patient/query text.

Tests used two actual spawned processes and independent SQLite connections:
both obtained valid results while their shared chunk was embedded only once.
Other tests verify mixed-corpus privacy, stale-lease recovery, exception cleanup,
source changes, full coverage, source spans and output bounds.

## Case-private query cache

Native file and case-narrative search now create a private SQLite cache for the
index instance. Its metadata binds exact case namespace and encoder. Entries
contain a query hash, embedding and bounded retrieval result; they are not a
cross-patient or cross-case store. Files are ignored under
`HealthHarnessCodex/runs/case-query-cache/`. They are private run artifacts,
not transferable role memory. An index reset creates a new cache instance.

An identical query can reuse a result only with identical source text, document
IDs, source metadata, relevance floor, retrieval options and index revision.
Current filesystem access/manifest checks still precede cache lookup. Altered
records, evidence IDs, source scopes or options cause misses. Up to128 entries
allow repeated queries across alternating source collections. Cached result
metrics explicitly show that inference did not execute on that call.

For a new query, the code embeds it and compares it with stored vectors from
the same source/configuration bucket. It reports nearest cosine, then performs
fresh ranking. **Similarity alone does not reuse an answer**: dates, negation,
setting and clinical conditions can change the question. Only exact reuse is
enabled. This implements vector comparison without inventing an unvalidated
approximate-answer threshold. It caches passages, not clinical decisions.

## Actual full-handbook GPU checks

Read-only/network-none disposable containers, pinned existing GPU image/model.
1289 handbook files produced1293 text/page records,39601 chunk occurrences and
39567 unique embedding keys. This is reference material, not75 patient cases.

| Check | Time | Embedding work |
|---|---:|---|
| Initial broad build with partial cache |300.890s|22665 disk hits;16902 missing document chunks plus1 query|
| Final-source fresh case with built cache |28.375s|39563 disk hits;4 nonshared chunks plus1 query|
| Identical query repeated in that case |0.969s|No embedding call or reranking|
| Similar query in that case |6.953s|One new query embedding; no document embedding|

These are observed development timings, not a controlled speedup benchmark or
measured full-workflow token reduction. The four nonshared chunks remain outside
the approved reference subtree. The similar-query cosine was0.93958; it did not
cause answer reuse. Every returned passage was checked against original text.
Complete coverage remained true. Disposable audit/embedding containers were
removed; preserved failed benchmark worlds were not altered.

The first development audit overlapped small metadata-only code edits and has
only a post-run source hash. Final verification used a fresh process/container
and confirmed all source/configuration hashes identical before and after.
Receipts (local-only):

- `runs/20261023-cache-real-audit/` initial build, separately preserved.
- `runs/20261023-cache-real-audit-warm/` final-source confirmation, exact spans,
  source hashes, cache/inference counts and cleanup receipt.

## Release verification and remaining scope

Full final software suite: **514 passed /55.304s**,
`HealthHarnessCodex/runs/20261023-recovery-cache-final-tests.log`.
Earlier full check511/55.113s preceded additional binding/lease/cache tests.
One initial test cleanup failed because its own inspection connection remained
open on Windows; the test now closes it explicitly. Production cache connections
already use explicit closure. No test failure was bypassed or masked.

No new dataset actor run, paid judge call, official score, reliability rate or
submission is claimed. Prior t021 failures remain preserved. This does not
resolve account-side quota errors, prove every policy ranking clinically
applicable, or establish that the still-configured context limit is sufficient.
The user should next run **one explicit t021 case** in a fresh directory, then
inspect actual completion and its evaluation packet before broadening the run.
