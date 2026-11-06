# First full-dataset attempt: startup failure and repair

October 21, 2026. The user launched the 75-task CLI batch themselves in
`HealthHarnessCodex/runs/20261021-full-dataset-01/`, one attempt per task,
concurrency three, Luna high, deferred grading. This is an attempted dataset
run, not a completed or scored full-dataset result.

## Actual execution and stop

The first six provider attempts reached the standalone setup path and failed
before model execution. Their evaluations report `setup_failure`, zero model
calls, zero engine tool calls, and no case-state SQLite database. Bootstrap
public tool reads did occur. Three further worlds had started preflight when
root stopped the exact matching batch process, PID 10500, to prevent repeating
the failure through the dataset. The original manifest is preserved unchanged:
six `needs_reconciliation`, three `running` entries left by the interrupted
process, and 66 `pending`. Those labels are historical snapshot state, not
evidence of a currently running process.

Root subsequently saved the actual verifier `/export` for all nine worlds
under their ignored container log directories, recorded SHA256 receipts and
confirmed all nine stopped. No model inference, clinical write or judge call
was made in this failed batch or its read-only diagnosis. The operator stop
and world preservation receipts are local-only in the original run directory.
Do not resume this batch with the repaired source or overwrite its evidence.

## Confirmed cause

The provider bootstrap requested `chart.search_patients` with `limit:25` and
required a complete roster. The live public tool returned 25 entries with
`total:65`. Discovery therefore raised:

`provider public patient roster is not complete within the bounded discovery limit`

There are 25 provider tasks, but that does not mean the world contains only
25 patients. Earlier selection QA on the first 25 records did not establish
roster completeness. Unit tests and inventory checks also did not detect this
live-world mismatch. The incomplete-roster rejection was appropriate; the
hard-coded discovery bound was the integration defect.

## Changes and verification

- Provider discovery now requests a bounded complete roster of up to 256,
  validates the actual total, rejects truncation and malformed/duplicate IDs,
  and preserves existing single-candidate model isolation and budgets.
- Private setup diagnostics preserve stage, exception type/message and traceback
  frame locations without locals. Console/evaluation output exposes only safe
  stage/type information. Setup failure no longer appears only as `run finished`.
- Three consecutive verified zero-model/no-action setup failures stop new task
  scheduling. Unstarted tasks stay pending. Unknown or post-action failures
  retain their reconciliation/preservation rules.

Root independently passed **282 software tests** in **28.752 seconds**. A
read-only check against the actual retained provider world completed discovery
using all 65 patients and uniquely selected the public task's patient by a
chart phrase, with zero semantic model calls or clinical writes (29.03 seconds).
This verifies the discovery repair; it does not verify a completed provider
workflow or new official score.

Luna-high `provider_roster_fix` owned profiles/tests, `all_domain_runtime` owned
private setup diagnostics/tests, and `deferred_grading` owned fail-fast
scheduling/tests. All are finished. Root owned diagnosis, process stop,
actual-world read-only QA, preservation, independent verification and commits.

## Next run

The repaired source needs a new frozen batch directory. From
`C:/Projects/BigData/HealthHarnessCodex`:

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.batch --dataset-root C:/Projects/BigData/Dataset/chi-bench --run-dir runs/20261021-full-dataset-02 --concurrency 3 --attempts 1
```

Keep Docker running and do not edit source or commit while the batch runs.
Judging remains deferred. No retry batch was started automatically during this
repair. Task completion, simulator credentials, late grading and all 75 scores
remain to be established by actual execution. Provider semantic fallback over
a larger roster can exhaust the fixed 48-call budget; no budget was silently
expanded in this repair.

See [deferred grading](DEFERRED_JUDGING.md) and
[all-domain execution](HEALTH_HARNESS_ALL_DOMAINS.md).
