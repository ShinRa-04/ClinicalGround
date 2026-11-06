# Open harness corrections - October 23

**Update:** both items below are implemented and verified at software,
synthetic live-recovery and real-reference GPU levels. The query cache is also
implemented. See [release evidence and remaining limits](RECOVERY_AND_CACHE_REPAIR.md).
The following diagnosis/proposal sections preserve the pre-repair state. No
fresh full t021 result or official score has been measured since these fixes.

User explicitly requested recording the handbook indexing delay for improvement
and reviewing t021-05 before starting corrections. This is an open-work record,
not a claim that either item is implemented or verified fixed.

## 1. Bootstrap response-format recovery

Observed in `runs/20261023-hybrid-t021-05`: candidate comparisons1-9 validated;
two positive candidates triggered investigation. Calls10-11 produced four
successful candidate inspections, two for each candidate. Call12 failed in
`CodexSessionModel._parse_reply`: nested tool `arguments_json` was not valid JSON.
The raw rejected response was not retained, so its exact malformed characters
and whether the cause was escaping/truncation/another syntax issue are unknown.

`identity_investigation.investigate_identity` invokes its completion callback
without handling `ModelResponseFormatError`. The callback accounts aggregate
model calls but propagates the exception. Main `Harness` workflow already has
bounded format recovery; bootstrap does not share that handling. Consequently
the whole setup failed before case binding or healthcare-workflow retrieval.

No budget exhaustion or clinical policy failure is established. Twelve calls
were started, eleven finished successfully; zero workflow tools and zero
retrieval events. No official judge ran. The batch marks needs_reconciliation:
world is preserved, no verified deferred snapshot exists, and retrying this
same settled directory is not a fresh attempt.

Correction direction, not yet implemented: consistent bounded response-format
recovery at every model boundary, including bootstrap, preserving successful
read provenance and aggregate budgets. A malformed proposal must execute
nothing; a correction must not repeat completed actions or introduce another
patient's context. Test malformed first/middle/later calls, correction failure,
budget exhaustion and accounting. Do not claim success from a single fake-model
test; verify actual recovery behavior within the explicitly selected one-case
scope. Evaluate the fragility of nested JSON encoding separately rather than
silently guessing or repairing invalid model arguments.

## 2. Broad handbook indexing and static cache reuse

Run -03 searched the entire permitted handbook:1289 files/39601 chunks.
Fixed-reference disk caching was disabled because eligibility requires the
entire corpus to be trusted references, while handbook-root searches include
other files. Narrow policy search correctly reused21199 cached vectors. The
unintended all-case batch also showed simultaneous workers independently
building substantially the same broad corpus. These are handbook chunks, not
other patients or the 75 test cases.

Correction direction, not yet implemented:

- Decide static-cache eligibility for each verified document, not all-or-nothing
  for a mixed corpus. Only approved static references may share vectors.
- Coordinate concurrent builders by encoder/content identity; wait/recheck
  completed batches instead of embedding identical missing chunks independently.
- Preserve complete coverage and explicit resource errors; do not restore the
  alphabetical-prefix truncation that previously hid relevant policies.
- Retain current-case isolation and source hashes. Patient/query vectors must
  never enter the shared reference cache.
- Show tool name, corpus scope, cache hits/misses and current work in logs without
  exposing patient/query text. Measure cold/warm and concurrent execution.

Similar-query caching is still deferred as previously requested; it is a
separate optimization and does not fix duplicate document embedding.
