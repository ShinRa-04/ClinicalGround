# Context and judge efficiency implementation — October 22

User authorized implementing the audited solutions. A subsequent question also
requested a separate judge-input/output analysis. Root owns coding; no delegated
agents and no increase to the existing $0.50 total paid-judge authorization.

## Implemented

- Exact MCP text/structured duplicates are normalized for model presentation;
  nonidentical text/images remain in original evidence and can be inspected in
  raw representation. Bool/integer differences are not treated as identical.
- Clinical tasks use a deterministic bounded current-case working view with
  attributed current observations, recent source index, outstanding work and
  concise completion milestones. Full evidence, full role definitions and the
  pinned completion contract remain stored/enforced independently.
- The original system safety instructions remain; responsibility cards are
  indexed concisely and available through `case.get_role`.
- Current-stage tools are presented, with `case.discover_tools` able to activate
  already-permitted tool definitions for later turns. This changes presentation,
  not actor access permissions. Helpers remain disabled in combined mode.
- `case.inspect_evidence` retrieves typed fields or exact text/list slices by
  source ID and JSON pointer. `case.find_evidence` locates older source IDs.
  Original source IDs and original char-offset retrieval still work.
- Recorder now measures the serialized engine payload, not just message content.
  The native adapter records per-pass usage and message phases, retains final
  cumulative token accounting, and explicitly requests one final proposal with
  host-managed progress. Native instructions/tool restrictions remain intact.
- Judge stops after a complete typed verdict file rather than paying for a
  trailing acknowledgment. Complete failure verdicts stop too. Partial/bad
  verdicts do not. Terminal checkpoints preserve the verdict hash and prevent
  paid replay of changed completed sessions.

## Measurements before fresh execution

- Old audited 19 prompts: 2,915,546 serialized characters.
- Re-projecting the same saved evidence with new code: 1,094,289 characters,
  **62.47% lower**. This is an offline input-size comparison, not live tokens or
  evidence of preserved clinical performance.
- Tool presentation on that projection replay: 19 initially, 26 after case
  creation, 31 for follow-up, versus the old constant 38. Includes new local
  discovery/inspection tools.
- Saved judge response replay: 3 requests instead of 4, identical verdict file;
  the omitted original request cost $0.17367 / 39.28% of the old session total.
  New paid spend: zero.
- Focused working-set, native adapter and judge tests: 27 pass. Integrated suite
  initially passed 427 tests; a subsequent 428-test suite hit an existing Windows
  PermissionError while exporting a synthetic snapshot. That isolated test passed
  immediately on recheck. Final stable-source suite: **428 tests passed in
  56.515s**. No runtime source changes followed this release suite.

## Planned verification

Freeze source after final tests. Execute one fresh t012, compare actual reported
tokens and native pass counts with the earlier fresh execution, verify actual
submission/readback and snapshot integrity, then run key-free deterministic
checks. Do not claim a fresh full semantic score without another authorized
paid evaluation. Preserve all older runs; do not pool revisions as reliability.

The detailed judge analysis is [HarnessGuide/05_JUDGE_CONTEXT_ANALYSIS.md](../HarnessGuide/05_JUDGE_CONTEXT_ANALYSIS.md).

## First live candidate: retrieval regression, stopped and preserved

Source `ef6c7ab`, `runs/20261022-context-efficient-t012-01`, reduced individual
prompt usage but did not establish acceptable workflow performance. Root stopped
the development attempt after 31 recorded model calls / 167 engine operations
because repeated field inspection was consuming the budget without finishing
form preparation. Its state backup, verifier export/hash and debug-stop receipt
were saved before its world was stopped. There were no pending/unknown writes.
The old batch manifest's running marker is historical; do not resume this trial.

The first hypothesis was that large inspection replies were being re-compacted.
Direct inspection disproved that explanation for this run: none of its 90
inspection replies exceeded the 6,500-character threshold. The confirmed
retention defect was that useful already-read fields dropped out after three
turns. Twenty-six repeated source/path/offset inspections were already observed
at call 23. The attempt is a development regression, not a passing benchmark or
a valid performance-improvement result.

The revised projection retains a bounded 20k-character cache of exact, already-
inspected source readouts, linked to successful same-case evidence. These remain
historical observations and cannot establish fresh-readback completion. It keeps
up to ten complete recent turns, uses a 100k-character target, and preserves
explicit bounded retrieval results. Full responsibility contracts remain in
the system instructions; their earlier compaction was rolled back. A regression
checks that a read field survives beyond the recent-turn window without changing
the original evidence. The judge optimization is unchanged.

A second fresh execution will verify this revision. Record its actual counters,
effects and deterministic checks before claiming an efficiency gain.

## Second candidate: discovery search bug, stopped and preserved

Source `c23dd80`, `runs/20261022-context-efficient-t012-02`, was stopped at
22 model calls / 111 operations. Natural-language multiword tool queries returned
zero matches because discovery required the entire phrase literally. Relevant
permitted tools existed. No pending/unknown writes remained; state backup,
verifier export/hash and debug-stop receipt were saved before stopping the world.
Its manifest's running marker is historical; do not resume this development run.

Discovery now ranks word overlap, gives explicit exact-name status, and the
working set always includes the complete permitted canonical operation index.
The model can see when a handbook operation is not exposed by this actor rather
than assuming more searches will find it. Schemas still activate only from the
existing allowed registry. A regression covers the real multiword provider-
directory query that previously returned nothing. Full suite: **430 tests passed
in 51.741s**. A third fresh execution follows source freeze.

## Official desktop update and executable discovery

The third launch stopped before world creation or inference because the old
version-specific Codex directory disappeared. User reports an official app
update; that causal explanation is plausible but update history was not read.
The currently installed official CLI reports `0.163.0-alpha.11.1`.
Fresh batch defaults now discover the newest installed official desktop binary
by modification time. Explicit executable overrides remain supported. Existing
batch path/hash freezing still rejects resuming with a changed binary; this
does not silently migrate an earlier experiment. No executable was moved,
copied or installed. A synthetic regression covers directory replacement,
removal and missing installations. A new live trial will use a different CLI
from the baseline, which limits causal before/after token comparisons.
Verification after discovery correction: **431 software tests passed in
57.143s**, including binary replacement and existing resume hash rejection.

## Fresh submitted case: lower per-call context, higher total usage

Source `c05d265`, `runs/20261022-context-efficient-t012-05`, finished after
33 model calls / 71 engine operations. Its actual readback is `submitted`,
forms complete, with one SubmissionPacket. The immutable snapshot passed
integrity validation; world stopped. An isolated network-disabled deterministic
verifier diagnostic returned **8 pass / 0 fail / 1 N/A**. No semantic judge ran;
official strict score remains unknown. Do not combine old semantic verdicts
with this attempt's deterministic results.

| Measurement | Older source `9fd27cd` | Candidate `c05d265` |
| --- | ---: | ---: |
| Model calls | 19 | 33 |
| Engine operations | 57 | 71 |
| Reported input tokens | 1,270,858 | 1,379,381 |
| Reported output tokens | 8,842 | 15,618 |
| Reported total tokens | 1,279,700 | 1,394,999 |
| Cached input tokens, included in input | 359,424 | 445,440 |
| Serialized engine payload characters across calls | 2,915,546 | 3,080,612 |

Mean input per call decreased **37.51%**, but total input increased **8.54%**.
Therefore this is **not a verified total-usage improvement**. More turns offset
smaller working inputs. The CLI changed between runs, so this descriptive
comparison cannot isolate the harness change's causal effect. Fifteen of the
33 candidate calls had two native input passes; 18 had one. The native-pass
multiplier remains unresolved. There were zero model errors or unknown actions.

Local numeric receipt: `efficiency.numeric.json`; deterministic diagnostic:
`deterministic-check.log` and `deterministic-diagnostic/`. These stay ignored.
No paid API call occurred and the existing judge cap was not increased.
Launch 03 failed before inference because the old executable was gone; launch
04 failed before inference because Docker Desktop was closed. Neither is a
completed clinical attempt. Docker was started before trial 05; unrelated
containers were not started. All 33 preserved original-harness hashes match.

Next: inspect the extra decision/retrieval turns in the saved candidate and
reduce total work without losing sources or submission proof. Do not rerun
the full dataset or declare context management solved from per-call savings.
