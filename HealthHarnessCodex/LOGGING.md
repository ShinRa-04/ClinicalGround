# Execution logs

The terminal output is produced by our harness. Every case line carries an IST
timestamp, public task ID, domain and attempt number, so three concurrent
cases can be followed independently. Batch-wide messages use `[BATCH]`.

The stages are deliberately separate:

| Label | Meaning |
|---|---|
| `TASK_START` | A batch worker has picked this task; model execution has not necessarily started. |
| `WORLD_START`, `WORLD_WAIT`, `WORLD_READY` | Docker startup and health/tool readiness checks. Waiting here does not mean the model is working. |
| `ACTOR_SETUP`, `SETUP_STAGE` | Model adapter setup, ownership validation and case discovery. |
| `DISCOVERY_ROSTER`, `DISCOVERY_PROGRESS`, `DISCOVERY_SOURCE` | Bounded public roster, chart and intake-source retrieval, with actual counters. |
| `MODEL_START`, `MODEL_WAIT`, `MODEL_RECEIVING`, `MODEL_END`, `MODEL_ERROR` | A model call, call number, role, stream activity, duration and reported usage when available. Identity, owner and helper calls are distinguished. |
| `TOOL_REQUEST`, `TOOL_WAIT`, `TOOL_END` | The requested capability, declared effect, dispatch outcome and duration. A returned tool error is distinguished from a completed transport call. |
| `WORKFLOW_END` | The worker's local outcome. This is not an official benchmark pass. |
| `SNAPSHOT_START`, `SNAPSHOT_SAVED` | The final world export and files are being preserved for later grading. |
| `WORLD_STOPPED`, `WORLD_PRESERVED` | Teardown succeeded, or the world is retained for reconciliation. |
| `TASK_END` | The task attempt has settled, including snapshot/teardown state. Saved snapshots remain ungraded. |
| `BATCH_PROGRESS`, `BATCH_END`, `BATCH_STOPPED` | Actual saved, failed, active, pending and reconciliation counts. |

Model calls sample progress about every 5 seconds. `MODEL_WAIT` means no new
assistant reply text arrived since the preceding update; `MODEL_RECEIVING`
means the reply-character count increased. Tool waits retain their 15-second
interval. Progress messages stop on return or error. Tool names use their declared actor names
instead of opaque hashed aliases when the mapping is available. Failed setup
shows the stage, exception type and a safe error code; the complete exception
remains in its ignored private receipt.

Console output excludes patient identifiers, clinical text, prompts, model
answers, tool arguments/results, credentials and raw exception messages. Model
reasoning is not printed. Counts and saved artifacts do not establish clinical
correctness or an official score. No token-spend estimate is invented when
usage is unavailable. The display-only reply-token approximation below is
explicitly labelled and is never used for spend, usage totals or budgets.

## Receiving versus waiting

For an active Codex assistant-text stream, progress looks like:

```text
MODEL_RECEIVING Receiving model reply ... reply_chars_received=1200 estimated_reply_tokens=300 token_estimate_method=characters_div4
```

`reply_chars_received` counts actual canonical assistant-text deltas. It excludes
reasoning summaries, metadata notifications, mirrored raw events and completed
message copies. A fragment is not treated as a token. `reply_bytes_received`
counts UTF-8 bytes of that decoded text, not JSON transport overhead.

The current route does not provide a token count per text fragment. Therefore
`estimated_reply_tokens` is a **coarse characters/4 estimate**, rounded up; it is
not a tokenizer measurement and can differ substantially for JSON, code or
non-English text. It remains separate from actual provider usage. When native
usage snapshots arrive, `reported_output_tokens` and `reported_reasoning_tokens`
show those provider counts; repeated cumulative snapshots are not summed. The
usual `MODEL_END output_tokens` remains actual provider-reported accounting.

If the stream pauses, `MODEL_WAIT` retains the received counters and exposes
`reply_idle_seconds` when available. Native metadata or reasoning activity alone
does not count as new assistant reply text. Counts reset for every request and
are retained in safe timeout diagnostics without storing the streamed content.
The existing hard request timeout is unchanged: active streaming can still reach
that deadline. These logging changes do not retry requests or replay tools.

## Saved logs

- `batch.events.jsonl` in the run root: safe structured batch lifecycle events.
- Per-attempt `events.jsonl`: the existing local execution event stream.
- Per-attempt `run.live.md`: readable case progress.
- `batch.manifest.json`: authoritative attempt and snapshot status.
- `.setup-exception.private.json`: local setup diagnostic, when setup fails.

All of these are ignored run outputs. No new logging package or tqdm dependency
is required. Progress is printed as explicit counters; it is not an ETA or a
guarantee that a case passed. The default CLI finishes with a concise summary
and manifest location. Add `--json-summary` for the final full JSON summary;
`--plan-only` continues to produce its machine-readable plan without execution.

## Verification and next fresh run

Root independently passed the full **295-test** suite (29.492 seconds) and the
final **4 formatter tests** after the last small formatting adjustment. Checks
cover event order, three-way task correlation, heartbeat lifecycle, error and
snapshot labels, private-field exclusion and concise/machine summary behavior.
An ignored synthetic log preview was generated; no model, Docker case or paid
API request was executed for the logging change. All 33 original harness file
hashes still match the fork baseline.

The user chose a fresh attempt of every public task, rather than continuation
of the earlier pending subset. From `C:/Projects/BigData/HealthHarnessCodex`:

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.batch --dataset-root C:/Projects/BigData/Dataset/chi-bench --run-dir runs/20261021-full-dataset-03 --concurrency 3 --attempts 1
```

The plan was checked: 75 tasks, 25 per domain, installed Codex executable
present and hashable, grading deferred. This run has not been started by root.
Keep Docker running and keep source/runtime unchanged after starting. The two
earlier provider identity-selection failures remain a known issue; logging
does not change their behavior or prove that all workflows will complete.
