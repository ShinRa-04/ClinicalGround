# Conversation probe - bounded follow-through

Owner: Codex implementation and offline verification; reviewer/user owns review and live execution.
Branch: `role-authority`; no commit. See [authorized statements](AUTHORIZED_STATEMENTS.md)
and [prompt measurements](ROLE_PROMPT_BASELINE.md).

## Dedicated preparation update (2026-11-03)

`--prepare` and runtime worker preparation now share
`health_harness_codex.worker_preparation.prepare`: identical preparation instruction,
local-only validation and one corrective call. CM-04 runtime enables it before its
first conversational completion; other workers remain opt-in. Offline context
capture stops before preparation and keeps the full delegated tool inventory.
See [current design, user-reported probe evidence and next full-run command](AUTHORIZED_STATEMENTS.md).
Owner prompts and the 3,000-character question cap are unchanged. Extra selected
policy/chart observations can increase variable preparation input size.

## Behavior and boundaries

The CLI opens the single `cm/*/attempt-1/state.sqlite` with SQLite URI `?mode=ro`,
selects its CM-04 dialogue worker, and counts successful send-message patient replies
(1-based). Simulator turn numbers count both speakers; transcript readbacks and MCP
envelope duplicates do not count. History stops immediately after the selected reply.

`baseline` uses saved system/user/history verbatim. `current` rebuilds the opening
worker context with current code in a fresh in-memory CaseStore, preserving launch
bindings/budgets and evidence through the active outreach-start receipt. It appends
saved worker history through the selected turn, excluding later history and final
state. A recorded latest statement list is restored in the opening only if its
recorded source count predates outreach start. Current code cannot replay a
preparation step that the old run never performed. Both modes retain old-prompt
history; neither simulates a new patient trajectory.

`--repeat K` defaults to 1 and accepts 1-5. Each sample starts from an independent
copy of the same context and boundary evidence. A sample proposing only
`case.record_authorized_statements` is validated with the real local validator and
applied only to that sample's in-memory state. The assistant proposal and tool result
are appended, current preparation is pinned, and ONE follow-up completion can propose
a message or correct invalid preparation. The sample stops after at most two calls,
even if that follow-up proposes preparation again. Other tool proposals, including
speaking, are reported and never dispatched; mixed batches are not applied.

Local preparation errors produce engine-shaped `{"error": type, "detail": message}`
tool feedback. Failed validation is atomic. A second invalid call is recorded and
ends that sample without preparation; a successful corrective preparation at the
second call is recorded but cannot trigger a third call to obtain a message.

`--prepare` is current-mode only. Before sampling, at most TWO shared preparation
completions see the selected context and successful same-case observations available
at that history boundary. Only the authorized-statements schema is supplied. The first
failure receives feedback and one corrective call; if both fail, samples continue
from the original context without shared preparation. A successful list is pinned
into every sample's starting context. Shared preparation is sampled once (with at
most one correction), so repeats do not measure its full variability.

JSON retains existing fields, including first-sample fields at top level. Each sample
adds `preparation` (attempts, statements/statuses, validation, usage and proposals),
`recorded_statements`, `message` (final proposed message or null) and `model_calls`.
Top-level `preparation` describes the shared `--prepare` phase; top-level `model_calls`
is the actual total. Per-sample call counts, statements/statuses and a short message
summary print to the console. No subsequent patient response is requested.

Total calls are K..2K without `--prepare`, and at most **2 + 2K** with it. Repeated
preparation cannot exhaust an unbounded loop. The probe does not generate missing
clinical facts or certify the actor's semantic condition judgment.

Tool inventory comes from the existing local public schema inventory plus current
local/workspace specs; construction/listing does not execute tools. The fake schema
provider refuses every dispatch. Native completions retain the pinned executable,
reviewed instruction source, Luna/high defaults and 180 s idle / 600 s active limits.
Baseline samples use the saved delegation; current samples use current delegation.

Outputs default to fresh timestamped JSON beside the source run, under ignored
`runs/`. Existing paths, source-run paths and any attempt-directory output are
refused. `--out` can name a fresh file outside those locations. Outputs can contain
private saved conversation/policy content: keep them local. Source databases are
never changed. A sample may propose another read or preparation instead of speaking;
only authorized-statements preparation can be applied locally, with the bounded follow-through above. Other proposals stop without dispatch. Prompt diagnosis is not
benchmark or clinical success evidence.

## Exact user-only live commands

Run from `C:\Projects\BigData\HealthHarnessCodex`. Each command below uses
`--repeat 3`: baseline/current without preparation makes 3-6 live calls; current
with preparation makes 4-8. All six commands together make at most 40 calls. These commands
were documented, **not executed** by the implementer.

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.conversation_probe --run runs/20261103-cm-dm-low-coop-luna-03 --turn 4 --mode baseline --model gpt-6-luna --effort high --repeat 3
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.conversation_probe --run runs/20261103-cm-dm-low-coop-luna-03 --turn 4 --mode current --model gpt-6-luna --effort high --repeat 3
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.conversation_probe --run runs/20261103-cm-dm-low-coop-luna-03 --turn 4 --mode current --model gpt-6-luna --effort high --repeat 3 --prepare
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.conversation_probe --run runs/20261103-cm-dm-low-coop-luna-01 --turn 7 --mode baseline --model gpt-6-luna --effort high --repeat 3
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.conversation_probe --run runs/20261103-cm-dm-low-coop-luna-01 --turn 7 --mode current --model gpt-6-luna --effort high --repeat 3
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.conversation_probe --run runs/20261103-cm-dm-low-coop-luna-01 --turn 7 --mode current --model gpt-6-luna --effort high --repeat 3 --prepare
```

## Offline verification

Full command from `HealthHarnessCodex/`:

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m unittest discover -s tests -q
```

Final results and exact timings are recorded in [follow-through verification](AUTHORIZED_STATEMENTS.md).
Tests use synthetic state and fake models: bounded one/two-call samples; shared
preparation validation and one correction; error feedback; message follow-through; identical contexts; CLI output; argument restrictions; local-only
validation; evidence cutoff; opening preparation timing; source-state immutability;
read-only SQLite and unchanged DB hash. Offline `prepare_probe` for both documented
boundaries succeeds with current authority present and databases unchanged.

Unverified: live quality/reliability, provider availability, new patient responses,
clinical/benchmark outcomes, and live preparation token volume. A preparation call
includes complete successful boundary observations; it may be larger than an ordinary
probe context and remains subject to the native provider's context capacity.
