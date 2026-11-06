# Streaming timeout and t033 continuation — October 25, 2026

Root owns this implementation and single-case execution. User authorized fresh
t033 attempts and deterministic/native structural checks, **no semantic judge**.
Original failed attempts remain separate and immutable.

## Confirmed prior failure

`20261024-random-um-t033-13` used frozen source `5dd7b08` and the old
180-second hard timeout. It stopped at model call 2 with native
`error:unknown:usageLimitExceeded`, before any reply text on that call.
This was the signed-in account limit, not a retrieval failure or a timeout.
Two model calls and five tool proposals were recorded. Snapshot receipt saved
213 files; world stopped. No judge was invoked. The account tool subsequently
reported ordinary usage allowed; only a new inference can establish usable
capacity for this model.

## Approved timeout behavior

The user selected up to ten minutes for an actively streaming call, with a
three-minute silence timeout. New explicit options:

```text
--timeout 180 --active-timeout 600
```

- Startup RPCs keep the existing setup timeout.
- Once the turn starts, only nonempty assistant or reasoning text deltas with
  the active thread/turn identifiers refresh the silence deadline. Reasoning
  text is not captured in failure artifacts.
- Keepalives, usage updates, empty deltas and item metadata do not refresh it.
- The request always stops at the total cap measured from request start,
  regardless of continued generation. No partial proposals are dispatched.
- Logs record the configured cap and whether silence or the total cap expired.
- Omitting the new option preserves the old hard-timeout behavior. Batch freezes
  and forwards the option; standalone and audit continuation expose it as well.
  Helpers share the owner's configured model. The separately bounded counterparty
  simulator retains its own request limits.

This changes latency tolerance, not the clinical workflow, inference model,
reasoning effort, response validation, source isolation or completion rules.
It does not solve excessive output or guarantee that the case finishes.

## Verification and live execution

Deterministic timelines cover a valid response after the old hard deadline,
silence after progress, metadata/empty-delta non-extension, reasoning progress,
foreign-thread rejection, hard total cap and legacy behavior. A real subprocess
stall test checks owned-process cleanup with the new silence policy. Batch
integration checks forwarding and frozen configuration.

Full regression:639 tests pass in85.429s. After expanding real subprocess and
batch assertions, final targeted provider28 tests pass in2.188s and batch38
tests pass in29.962s. These establish software mechanics, not healthcare-task
performance. Suite output is local in `runs/20261025-streaming-timeout-tests.log`.
Private failure requests/public assistant prefixes stay in ignored per-case
`model-failures/`; never commit these payloads.

## Explicit fresh single-case command

Root executes this after committing source. Do not launch a duplicate while it
is active. Use a new directory after changing frozen source/configuration.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-um-t033-14 `
  --domains pa_um `
  --task-id pa_t033_t033_o001_p01_triage_payer `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```

No judge or full-dataset execution is selected. Fresh execution outcome follows
in the handoff after the actor and permitted structural diagnostic settle.
