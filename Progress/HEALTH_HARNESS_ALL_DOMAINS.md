# All-domain execution integration — October 20, 2026

**October 21 live dataset attempt:** the user's first 75-task run encountered
a real provider discovery defect: a 25-record request truncated a 65-patient
roster. Root stopped the repeated zero-model setup failures, preserved exports
and stopped all nine started worlds. The corrected bounded roster, private
diagnostics and fail-fast scheduler pass **282 tests**; read-only discovery
against the real 65-patient world passed. The fresh retry is not started and no
full-dataset score exists. See [run receipt and next command](FULL_DATASET_RUN_01.md).

## October 21 checkpoint

The two Luna-high coding agents completed the UM intake selection connection.
When requester/procedure headers do not give a unique match, discovery reads
the actor-listed original intake request form in the owned container and
compares candidates individually through the same shared Codex adapter. These
calls count against the aggregate model-call budget. Multiple or zero positive
matches fail closed. Generic form boilerplate cannot automatically select a
case. Other candidate bodies never enter the clinical worker context.

The reader accepts only metadata for the same case and approved original
intake input roots; file size, page count and extracted text are bounded.
Truncation is explicit in candidate context. Root's actual read-only actor QA
extracted a two-page, 1,779-character PDF without OCR, with an unchanged source
hash on the repeat check. Private evidence stays under ignored
`HealthHarnessCodex/runs/20261021-domain-contracts/um-intake/`.

Root independently passed the final 253 harness tests (29.506 seconds) and
7 packet tests (26.761 seconds). All 33 original harness file hashes match the
fork baseline. Final same-case symlink containment tests and the repeat live
PDF readback passed. The read-only QA world is stopped. Both coding agents are
finished; root owns the next source checkpoint and fresh clinical trials.
No new clinical actor trial or paid judge was executed in this checkpoint.
The full 75-task batch and full graded packet remain outstanding.

The user's current judge-command and cost-estimate request is documented in
[Runner/JUDGE.md](../Runner/JUDGE.md). Show the actual command, case scope and
estimate before each paid evaluation; collect measured token/cost evidence
from the first authenticated call. The saved dollar scenarios are not bills
or spending caps. Do not paste a key into chat or tracked files.

The user requested the entire integration, not a single-case pilot. The Codex
provider/transport/factory remain the single shared model boundary. New work is
benchmark execution, identity, case workspace routing, batching and export.

## Implemented and tested

- `domain_profiles.py`: canonical PA/provider, payer/UM and CM profiles using
  actual dataset boundaries, actor ports/namespaces and public tool schemas.
  No patient/case identity is inferred from task filenames or hidden data.
- `standalone.py`: shared backend for all profiles. CM selects a uniquely
  supported referral. Provider starts from a patient, then binds the actual
  case only from a trusted same-patient creation result. Its durable namespace
  stays immutable; workspace writes wait for the actual case binding.
- Provider exact-match selector QA: 19/25 unique, six ambiguous. A fresh,
  read-only comparison through the same model adapter handles ambiguous
  candidates individually, requiring one positive and literal source quotes.
  Comparison calls consume the same overall model-call budget. Rejected
  candidate data never enters the clinical worker context. CM exact public
  referral selection QA: 25/25 unique. These are selection checks, not scores.
- `engine.py`, `identity.py`, `context.py`: separately persisted trusted case
  binding alongside the existing late-patient binding. Foreign identities
  remain quarantined. Provider inbox calls require its bound case ID; chart
  reads require its selected patient. Actual actor date-time/binary schemas
  are supported without disabling unknown-schema rejection.
- `batch.py`: inventories all 75 public tasks (25 per domain), creates fresh
  owned worlds, checks image and public instruction hashes, reuses standalone,
  invokes the unchanged official verifier, backs up state and records exact
  settled grades. A valid reward-0/exit-1 result stays a real graded failure.
  Missing or unavailable grading stays ungraded. Resume never replays an
  interrupted write/attempt. Full/selected coverage are distinct.
- Only a complete, graded first attempt for all 75 tasks produces
  `kaggle_submission.csv`; partial output is named explicitly and never fills
  missing grades with fabricated zeros. Three-attempt metrics require fully
  graded groups.
- `Submissions/tools/assemble_batch_packet.py`: separate full-batch exporter;
  requires all 75 hash-verified first attempts, including failures. It refuses
  incomplete results. The earlier submission_1 pilot remains unchanged.

Root independently passed **232 harness tests** (22.348 seconds) and **7 packet
producer tests** (12.117 seconds). Actual public task inventory is 75 and its
release pin is chi-bench-v1.0.0. The Codex backend files were not changed.
Native all-domain trials and full-dataset scores are **not yet established**.

## Run

From HealthHarnessCodex with the bundled host Python:

```powershell
python -X utf8 -m health_harness_codex.batch --dataset-root C:/Projects/BigData/Dataset/chi-bench --run-dir runs/NEW_BATCH --concurrency 3 --attempts 1
```

Add `--plan-only` to hash/enumerate public instructions without Docker or
inference. `--task-id` selects exact public task IDs for development checks;
selected-scope completion must not be called full-dataset coverage. Defaults:
GPT-6 Luna high, 48 total model calls, 240 engine operations, 180,000 context
characters, 180 seconds per model request. Root freezes source before actual
execution. Do not modify actor code or commit a new revision mid-batch.

Default worlds have network none and empty provider keys. Our model uses the
existing host Codex sign-in. Benchmark-owned patient/P2P simulators or judges
may have separate inference requirements; these must be observed per task.
Optional `--benchmark-env-file C:/Projects/BigData/Runner/.env` requires an
explicit `--allow-benchmark-network`; it uses only that existing ignored file
and records no values. It does not extract Codex auth or substitute a judge.
No public ports, publication or unrelated services are introduced.

## Active execution and ownership

Luna-high domain_connections implemented profiles/discovery and its tests;
triage_commit_guard implemented standalone and trusted binding/schema changes;
identity_finish implemented batch, full-batch export and tests. Root reviewed,
obtained public actor contracts in fresh PA/CM QA worlds, independently tested
and owns native runs, official grading, handoff updates and commits. QA worlds
were stopped. Payloads and all evaluation data stay ignored.

Next: freeze this source, run fresh PA/UM/CM development cases, resolve actual
integration failures without guessing hidden answers, then execute the full
75-task first-attempt batch. Report all failures and unavailable grades. No
full packet or full-benchmark number may be claimed before those artifacts
exist. Audit continuation remains explicitly UM-only; fresh normal execution
is the all-domain path.

## First live integration check — frozen 53ac56d

Three fresh worlds were attempted in `HealthHarnessCodex/runs/20261020-three-domain-smoke/`:

| Domain | Actual result | Official score |
|---|---|---|
| Provider PA | Setup stopped before model/actions: lazy actor tool catalogue was not initialized | Unavailable |
| CM | Same setup catalogue initialization error | Unavailable |
| UM (different MD-review task) | 12 model calls, 56 engine operations; stopped on a late patient-identity response from MD decision | Ungraded: official Claude judge authentication unavailable |

All worlds stopped; original results, receipts, SQLite snapshots and grader
outputs remain preserved. No full-coverage score exists. The public runtime
error explicitly reported absent Claude authentication and ANTHROPIC_API_KEY.
The earlier deterministic pilot's key-free grading does not generalize. The
published standard judge documentation specifies Anthropic/Opus 4.7; the
runtime additionally advertises Claude CLI login, which has not been tested
here. No alternate judge acceptance is confirmed and no judge is substituted.

The catalogue fix has 15 focused profile tests. Root also identified that the
old UM provider/procedure selector uniquely matched only 14 of 25 public
instructions against the observed queue; five intake entries lack completed
provider/header information. Broader public-case bootstrap is being checked
using the fresh, read-only `bigdata-health-codex-contract-20261020-um-intake`
QA world and allowed intake/review/document APIs. No hidden targets or expected
clinical answers are read. Root has requested local judge authentication while
continuing independent implementation and key-free execution checks.
