# Second dataset attempt: user stop and runtime-path failure

October 21, 2026. The user launched and later resumed
`HealthHarnessCodex/runs/20261021-full-dataset-02/` with the frozen source
`6dcf5b9`. Current recorded scope is **3 deferred-ready snapshots, 3 interrupted
cases needing reconciliation, 7 setup failures, and 62 pending tasks**.
No completed full-dataset execution or new official score is established.

## User-directed stop and resume

At the user's explicit stop request root terminated the exact batch process
PID 10008 and its six child processes, then paused its three active case
containers. The saved completed snapshots were unchanged. Docker Desktop was
later unavailable and subsequently restarted. Recovery of the three paused
live worlds is not established; do not restart their containers and assume
the original clinical state survived.

The user resumed the same batch. Three attempts failed during provider
initialization, triggering the new fail-fast guard. Two already-started
workers also failed before the process exited, leaving 62 pending tasks.
The user's pasted output confirms `batch_stopped_early`. No batch process or
model worker is currently active.

## Confirmed runtime-path failure

The frozen configuration referenced:

`C:/Users/prath/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe`

That file no longer exists. The installed executable is now:

`C:/Users/prath/AppData/Local/OpenAI/Codex/bin/6257d9e8f63c0f2b/codex.exe`

The saved private exceptions say `Codex executable does not exist or is not a
file`, with stage `provider_initialization`. A desktop update is a plausible
explanation for the version-folder change, but installer logs were not checked.
The model or patient data did not migrate. The integration incorrectly relied
on a path tied to one installed version.

Root briefly copied the current executable into the ignored project cache
and successfully probed it. **The user rejected copying/moving Codex as a
workaround.** Root removed only that newly created copy and its receipt after
checking its hash, leaving the installed executable untouched. Do not recreate
the copy or move the installed program. Use the installed executable directly.

## Repair and verification

The batch default now uses the verified installed path. Before editing a
manifest or starting Docker, production execution checks that the executable
is an absolute, readable, regular file and freezes its SHA256 in configuration.
A missing or replaced executable fails before case startup. Explicit
`--codex-executable` remains available; no automatic copying or discovery was
added. The model adapter itself is unchanged.

The official installed executable directly passed the native connection and
sign-in probe: initialized, authenticated, model configured `gpt-6-luna`, and
**no inference performed**. Private probe receipts are ignored under
`HealthHarnessCodex/runs/20261021-runtime-preflight-qa/`.

Root's full suite passed **285 tests** (31.853 seconds). The final change from
the temporary cache default back to the installed path additionally passed
the focused default-path test. No inference or judge call was made during this
repair, and no retry batch was launched.

## Remaining boundaries

- The three saved snapshots can be graded later. They are saved execution
  outputs, not three established official passes.
- Two earlier provider discovery failures (before the missing-runtime failures)
  independently reported `provider patient name and chart cue did not identify
  the same roster entry`. That identity-selection issue remains unresolved and
  must not be conflated with the executable-path repair.
- Run 02's source/runtime configuration must not be silently rewritten. The
  repaired source and executable identity differ from its frozen configuration.
  Continue only through an explicit, provenance-preserving recovery plan or a
  fresh batch; do not claim a mixed-source run is one unchanged frozen trial.
- Interrupted cases are not automatically replayed. Preserve their journals
  and unknown outcomes for reconciliation. No completed full-dataset score or
  submission packet exists.

Luna-high `deferred_grading` implemented the batch preflight/hash checks and
tests. Root reviewed, verified the installed runtime, removed the rejected
copy, preserved run evidence, documented the status, and owns the commit.
