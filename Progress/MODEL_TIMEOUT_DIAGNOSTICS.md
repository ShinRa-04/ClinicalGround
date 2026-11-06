# Safe model timeout diagnostics

User requested checks for a repeat of UM t033's unexplained180-second timeout,
before rerunning that one task. No actor or paid judge was launched for this
change. The previous run's underlying service/transport cause remains unknown;
new diagnostics cannot reconstruct its missing historical events.

## What is now recorded

Each model request tracks these fixed stages: input validation, process startup,
initialization, preflight, thread startup, turn startup, waiting for the turn,
reply parsing and completion. A preflight stall can additionally be identified
by the last safe RPC method, such as account/read versus config/read.

While waiting, console/live logs can show the stage, last safe event category,
notification count, time since a native event and whether the process is running.
Failure events in events.jsonl retain a sanitized request_diagnostics object:

- Stage, configured timeout, request elapsed time and timeout phase
  (stdin write, transport read or already-expired deadline).
- Last event category, idle time and counts of reasoning/assistant progress.
- Last known RPC method, sent-request/received-message counts and stderr byte
  count, without stderr contents.
- Whether the child process was running before cleanup, its exit code and
  whether cleanup completed.
- Input/message/tool-schema sizes, so payload pressure can be assessed without
  retaining request text.

Transport timeouts have the explicit category transport:timeout. Their diagnostic
object is also included in the engine's persisted model_failure when ownership
is still valid. The previously fixed ownership heartbeat keeps long model waits
from expiring the case's fence. The recorder can retain a failure diagnostic
even if later controller persistence fails.

Example of the intended console shape (illustrative values, not a new trial):

```text
MODEL_WAIT ... stage=awaiting_turn notifications_received=3 last_event=reasoning_progress native_idle_seconds=12.0s process_running=true
MODEL_ERROR ... stage=awaiting_turn timeout_seconds=180.0s request_timed_out=true last_event=reasoning_progress cleanup_confirmed=true
```

## Boundaries

No raw prompt, patient text, tool arguments, response text, reasoning contents,
account identity, credential, server-supplied arbitrary method name or stderr
text is added. Diagnostic fields use an explicit enum/numeric/boolean allowlist.
Unknown event names are reduced to other. Optional diagnostic getters failing
cannot replace an original model error or break a valid reply.

These signals narrow the cause; they do not prove whether a remote server or
network caused a turn wait. Reasoning updates show that progress was observed,
not that an answer is guaranteed. Silence does not prove the model is dead.
Cleanup flags describe the owned local process, not an unverifiable claim about
remote computation. Stage timings include local request lifecycle work and
cleanup; they are not a remote inference-time measurement.

The180-second deadline, retry policy, model settings, task scopes, clinical
guards and official evaluation rules are unchanged. A timeout is identified,
not silently retried. No new dataset task starts automatically.

## Tests

Tests inject timeouts during initialization, account preflight, thread startup,
turn startup and after a reasoning-progress notification. They verify stage,
timeout category, no implicit retry and cleanup confirmation. A real local
stdio child process completes setup, emits a synthetic private reasoning marker
and stderr marker, then stalls; it is terminated, and neither marker appears
in the diagnostics. Recorder tests verify diagnostics survive error handling
without exposing private data or replacing the original exception. A valid
reply still succeeds if its optional transport diagnostic getter raises.

Focused provider suite17 tests passed/2.063s; recorder24 passed/0.559s.
These are synthetic protocol/software tests, with no Codex account inference
or paid provider calls. They are not a new UM t033 benchmark run.

Final full suite: **524 passed /62.454s**,
`runs/20261023-timeout-diagnostics-verified-tests.log`. Earlier full checks
caught an empty diagnostic field changing the existing failure-record shape;
the field is now emitted only when useful safe metadata exists. Existing
non-diagnostic provider errors retain their previous shape. No test was skipped.

Next user rerun should use the single UM t033 command with fresh directory
`runs/20261023-random-um-t033-02`, preserving the failed -01 attempt. If it stops
again, inspect the failed event's request_diagnostics first, then the native
evaluation artifacts; do not classify the cause as a fluke without evidence.
