# CM harness state and attempt -21 incident

Updated November 3, 2026. This is the current handoff; earlier run receipts remain
historical evidence. Root owns the unfinished implementation.

## Current scope

The latest user instruction is **documentation updates only**. No implementation,
tests, Docker restart/inspection, dataset execution, paid judge or new delegated
work is authorized by this document. Future work requires a new explicit user
instruction. No harness/test Python process was found during the documentation
status check; Docker/container state was not refreshed in this pass.

The intended CM result remains an evidence-grounded assessment and finalized care
plan on the same case, with all applicable native key-free checks passing. That
result has **not** been achieved. Do not change patient behavior, inject private
persona/expected answers, weaken verification or merge failed trials into a pass.

## What is committed and verified

- Last tested code commit: `d77870c` — scoped chart pointers and detection of
  interleaved unchanged investigations.
- Release verification: **743 software tests passed in 68.310 seconds**. The
  earlier release attempt had one artifact-tamper-test failure that did not
  reproduce in isolation. The strengthened test verifies its initial graded
  receipt before tampering. The first failure's cause remains unconfirmed.
- Offline replay of -20: the new metadata handoff indexed all six observed chart
  documents in 4,151 characters; five unchanged reads were detected among ten
  working-record reads. The old snapshot was unchanged. This was not a new case
  execution or clinical score.
- The last available CM native result is **attempt -20: 2/6 applicable checks
  passed, 4 failed, 8 N/A**, structural binary reward 0. No paid judge ran.
  That result must not be attributed to -21.

The 743-test result predates the unfinished runtime-guard edits described below.
The current working tree is not a verified release.

## What actually happened in attempt -21

| Item | Saved evidence |
|---|---|
| Run directory | `HealthHarnessCodex/runs/20261101-random-cm-anorexia-21` |
| Source used throughout execution | `d77870c` |
| Selected work | One CM case, `cm_anorexia_hard_refuses_001`; one attempt |
| Models | Worker `gpt-6.1-sol/high`; experimental patient `gpt-6-luna/high` |
| Configuration | Helpers/auto; 100 shared model calls; 500 tool operations; context-character cap disabled; patient cumulative quotas disabled |
| Provider/judge boundary | Existing Codex sign-in; no benchmark provider keys; grading deferred; no paid judge |
| Observed counters | 16 workflow model calls, 30 tool operations, **0 patient model calls** |
| Reported workflow usage | 444,636 tokens: 436,053 input + 8,583 output; 8,704 cached input included |
| Harness outcome | `error`; requested outcome unmet |
| Batch outcome | `needs_reconciliation` |
| Deferred snapshot | None; export failed because the world was unavailable |
| Native/semantic evaluation | Not performed; unavailable, not a synthetic zero |

The actor therefore did **not** test the new chart handoff in a patient
conversation. No conclusion about patient refusal or improved clinical performance
can be drawn from this attempt.

### Timeline and confidence

Times below are recorded November 1, Asia/Kolkata (UTC+05:30).

1. **21:58:47** — batch started. **21:58:49** — world startup returned;
   preflight became ready at **21:59:21**.
2. Docker metadata recorded world start at `2026-11-01T16:28:48.156627988Z` and
   exit at `2026-11-01T16:31:22.705545856Z` (**22:01:22 IST**).
3. The last operator inspection reported `Running=false`, `ExitCode=255`,
   `OOMKilled=false`, no Docker state error text, and no restart policy.
   Container memory/swap limits were both 0. These facts do **not** establish
   why Docker/the world exited; neither an OOM nor a daemon restart was proved.
4. Subsequent workspace reads failed with the generic message
   `container operation failed (exit 1)`. The model continued using cached
   evidence. Batched workspace reads could return an outer result containing
   per-item `workspace_read_failed` errors, concealing the infrastructure failure
   behind ordinary retrieval feedback.
5. After confirming that the world was stopped, root **manually stopped this
   attempt's owned Codex inference process**. The model error on call 16 reflects
   that operator intervention; it is not evidence of a new quota failure or
   spontaneous model unresponsiveness.
6. **22:07:08** — actor settled, simulator worker reported 0 calls and settled,
   deferred export failed, and the batch preserved the world for reconciliation.

Container retained by the batch:
`bigdata-health-codex-2089be7382cd-cm-4eb9e681-a1`.

The manifest's `container_stopped=false` means the runner did not confirm its own
normal cleanup. It does **not** mean the world was running: the operator's Docker
inspection had already confirmed an exited container. Do not restart the old
world, remove it, claim a valid export, or replay its actions automatically.

## Unfinished runtime-guard implementation

These existing edits are **uncommitted and untested**. No tests or code changes
were made during the November 3 documentation-only pass.

| File under `HealthHarnessCodex/health_harness_codex/` | Existing partial implementation |
|---|---|
| `models.py` | Adds `WorldUnavailableError` with bounded reasons: stopped, unavailable, unverified. |
| `docker_bridge.py` | Adds `DockerExecutor.assert_running()` using a bounded Docker state inspection; invokes it after nonzero container-command exit. |
| `engine.py` | Accepts an optional runtime guard; checks before owner inference; records a runtime failure; preserves uncertain writes as unknown and requires reconciliation. |
| `helper_jobs.py` | Checks the guard before a delegated model call. |
| `standalone.py` | Passes the executor's guard to the harness through the new constructor keyword. |
| `console_logs.py` | Adds a `WORLD_UNAVAILABLE` event and safe runtime-status field. |

This is not a completed fix. In particular:

- No regression suite or real stopped-world protocol check has run against these
  edits. The previous 743 passing tests do not validate them.
- Existing standalone constructor fakes/spies do not all accept the new
  `runtime_guard` keyword. Compatibility and actual callback wiring need review;
  no execution has established the resulting failures or fixes.
- Pre-dispatch and final-acceptance runtime checks were discussed but **not added**.
  Do not describe the current edits as guarding every action boundary.
- Fatal-state propagation through MCP, individual workspace operations, batched
  reads, and helper jobs still needs explicit regression coverage. Ordinary
  missing-file errors must remain distinct from an unavailable runtime.
- Dedicated evaluation/reporting integration and tests for the new error path
  remain unfinished. The new error/event names alone do not prove correct handling.
- Docker exit cause remains unknown. No host resource configuration was changed,
  and this assistant launched no replacement case after -21 stopped.

## Conditional next steps — only after a new user instruction

1. Preserve -21 and inspect its retained evidence before any restart or cleanup.
   Diagnose the world exit without assuming memory pressure or altering patient
   fixtures. If state recovery is possible, distinguish forensic recovery from a
   valid official deferred snapshot.
2. Finish the general infrastructure guard. A stopped/unavailable world must stop
   inference rather than become a clinical-information blocker. Keep uncertain
   writes fenced; never restart a world or repeat a write automatically.
3. Add meaningful regressions: stopped before inference produces zero model calls;
   runtime loss stops sibling dispatch; unknown writes remain unreplayed; batched
   reads preserve fatal errors; normal file-not-found remains recoverable; owner
   and helper guard wiring works; logs expose no raw container output or secrets.
4. Run the appropriate tests, then the release suite. Record actual results,
   including failures. Commit source only after review and verification.
5. If a fresh dataset attempt is then authorized, use a new run directory, freeze
   source/configuration, keep patient data isolated, and collect the real result.
   No all-75 run or paid judge is authorized by this handoff.

## Local-only evidence

Payloads, protected material and receipts remain ignored/local-only. Useful paths:

- `HealthHarnessCodex/runs/20261101-cm-anorexia-21-launch.log`
- `HealthHarnessCodex/runs/20261101-random-cm-anorexia-21/batch.manifest.json`
- That run's `cm/cm_anorexia_hard_refuses_001/attempt-1/result.private.json`,
  `state.sqlite`, model/tool failure captures and stage diagnostic.
- `HealthHarnessCodex/runs/20261101-cm20-native-check.log` — **-20**, not -21.
- `HealthHarnessCodex/runs/20261101-chart-handoff-progress-release-02.log`
- `HealthHarnessCodex/runs/20261101-cm21-handoff-progress-replay.json`

See [the research/repair chronology](CM_RESEARCH_REPAIR_PLAN.md) and
[external research with source links](EXTERNAL_HARNESS_RESEARCH_20261028.md).
