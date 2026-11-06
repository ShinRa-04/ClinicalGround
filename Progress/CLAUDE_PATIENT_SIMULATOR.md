# Claude CLI patient simulator

Implemented on `role-authority`, November 4, 2026. No commit, Docker operation,
trial, judge or live inference was performed for this implementation. The host
CLI's help/version commands are local checks only. The existing actor is unchanged.

## Purpose and scope

Provide an official-like patient using the user's existing Claude subscription
login and `claude-sonnet-5`, independently of the Luna actor. This addresses the
user-reported concern that the Codex patient consistently deferred. No patient
behavior improvement or benchmark comparability has been measured here.

`official` remains the default. `codex` retains its Luna/high defaults, instruction
pins and existing behavior. `claude-cli` is experimental and requires deferred
grading, no benchmark credential file and container network `none`.

## Source map and continuation

- `HealthHarnessCodex/health_harness_codex/claude_cli_patient.py`: native executable
  resolution, frozen patient settings and tool-free one-completion model adapter.
- `.../batch.py`: CLI/configuration, frozen provenance, shared spool startup and
  attempt settlement. New flags: `--simulator-backend claude-cli`,
  `--simulator-claude-model` (default `claude-sonnet-5`), and
  `--simulator-claude-executable` (default `claude`).
- `.../simulator_worker.py`: selects the patient adapter and carries its model and
  disabled-thinking identity through request hashes, receipts and responses.
- `.../simulator_bridge.py`: accepts the disabled-thinking identity. The transport
  protocol, loopback bridge, quotas, cancellation arbitration and reconciliation
  rules remain shared with Codex.
- `.../deferred_grading.py`: applies the existing experimental-backend eligibility
  guard to Claude patients too; ordinary official grading remains refused.
- `HealthHarnessCodex/tests/test_claude_cli_patient.py`: synthetic process tests;
  installed Claude is never launched by these tests. Python runs a temporary fake
  CLI script; process launch is intercepted to preserve/check the intended argv.
- Existing architecture and historical trials: [CODEX_SIMULATOR.md](CODEX_SIMULATOR.md).

Ownership: this implementation is owned by the current primary agent; no work was
delegated. Next owner reviews the diff and, when separately authorized, executes
the single fresh diagnostic below. `Progress/HANDOFF.md` is intentionally not
edited under this task's explicit constraint; it was already modified on entry.

## Invocation, isolation and provenance

Each completion starts a fresh native process with the request's system text in
`--system-prompt`, replacing the coding system prompt. The chronological history
is JSON-serialized on stdin, preserving user/assistant roles and text, with a short
instruction to emit only the next patient/counterparty response. This is a
transcript approximation: prior assistant turns are quoted inside one user prompt,
not replayed as native Anthropic message roles.

The command uses `--tools ""`, an empty explicit MCP configuration,
`--strict-mcp-config`, `--no-session-persistence`, `--output-format json`,
`--setting-sources ""`, `--disable-slash-commands`, `--safe-mode` and permission
mode `dontAsk`. It reuses `claude_code_actor.ISOLATED_SETTINGS` and
`actor_environment` without editing actor code. Settings exclude CLAUDE.md,
auto-memory, hooks and enabled plugins. Safe mode adds CLI-level suppression of
customizations while retaining login. No `--bare`: help explicitly says it excludes
OAuth login. Managed CLAUDE.md causes a fail-closed refusal, as in the actor.
Admin-managed settings still apply under safe mode; their absence/effect is not
established by fake-process tests.

The process gets an empty fresh temporary cwd within the private attempt spool,
removed after completion or timeout. The environment drops inherited
`ANTHROPIC_*` and `CLAUDE_*` customization except the actor's existing login
exceptions. The adapter does not open, print, copy or serialize login files or
token values. It creates no transcript/stderr log. The existing private spool
retains requests/responses; safe receipts contain metadata and usage only.

The default Windows `claude.cmd` dynamically chooses an installation. The new
backend instead resolves the bundled native `claude.exe` and freezes that file's
absolute path and SHA-256. Explicit `.cmd`/`.bat` launchers are refused; pass a native
binary path to override discovery. Frozen metadata also records backend, model,
thinking/effort, settings sources/settings, history strategy and output-cap
mechanism. The binary is rechecked before each request and again before launch.
Windows job ownership and Unix process groups bound process-tree cleanup.

## Thinking, output limits and deviations from official

Local `claude --help` confirms the flags used above and `--effort low`; it has no
thinking-disable or output-token-cap flag. We set `MAX_THINKING_TOKENS=0` and
`CLAUDE_CODE_MAX_OUTPUT_TOKENS` to the request's `max_tokens` (1–1024; existing
P2P requests remain limited to 512). `--effort low` is a fallback effort selection,
not itself a thinking-disable mechanism. These variables are documented in the
[official environment reference](https://code.claude.com/docs/en/env-vars).
That reference says zero disables thinking on the Anthropic API with exceptions
for newer model families, and describes the output variable as applying to most
requests. Actual Sonnet 5 request parameters and cap enforcement are unverified
without a live call. We do not use the adaptive-thinking-disable variable: the
reference says it has no effect on Sonnet 5. Usage above the requested output cap
is rejected, rather than accepted as a capped completion.

`CLAUDE_CODE_MAX_RETRIES=0` disables configured API retries and terminal-title
generation is disabled to avoid auxiliary title calls. CLI-internal behavior and
service-side routing cannot be proven by fake executables. Subscription Claude
Code can still differ from the organizers' direct API patient in routing, managed
policy, wrappers, sampling and history representation. A pinned model name alone
does not establish parity with private evaluation.

JSON result text and nonnegative actual usage are required. Input usage includes
uncached, cache-read and cache-creation tokens. Invalid JSON, missing usage and
excess output use existing worker error codes. Process failure/timeout after the
durable submission marker follows the existing `submitted_outcome_unknown` rule;
no automatic replay is permitted. Existing error vocabulary retains the legacy
`codex_error`/`codex_timeout` labels internally. Unsettled requests preserve the
world for reconciliation; settled attempts still require a verified snapshot
before stopping. The existing marker-only stop correction remains a separate,
budgeted model request.

Cost: each patient turn starts one subscription CLI call and consumes subscription
usage. A marker-only stop correction adds another call. No monetary price or
private-evaluation score is asserted.

## Offline verification

Final full suite from `HealthHarnessCodex/` using the requested bundled Python
command: **873 tests passed in 74.610 seconds**, zero failures/errors. The earlier
full pass before the final integration checks was 869 tests / 80.025 seconds.
Focused new patient suite: **20 tests passed in 2.146 seconds**. These establish
software mechanics, not benchmark success. Full output is local-only at
`HealthHarnessCodex/runs/20261104-claude-patient-offline-tests.log`.

Coverage includes argv/environment/settings isolation, empty temporary cwd,
verbatim system prompt, ordered multi-turn history, JSON/usage validation,
body-free errors, process timeout cleanup, immutable request replay protection,
shared call quotas, provenance mutation, CLI/configuration validation, original
backend defaults, synthetic Docker command construction, worker wiring and
failure cleanup, and experimental grading eligibility. No actual Docker command
or model executable was used by the new tests.

The documented live command was parsed through `batch.main` with `run_batch`
mocked: model, patient, timeouts, budgets and deferred grading matched. This
check did not open the dataset or create a trial. Installed CLI reports
`2.1.309`; local help was inspected for every selected flag. `git diff --check`
passed. Branch remains `role-authority`; no commit was made. Actor source and
`HealthHarness/`, `Runner/`, `Dataset/` are untouched. The existing modified
`Progress/HANDOFF.md` was not edited during this task.

Remaining verification: actual subscription login under these isolation flags,
native Sonnet 5 request thinking/output parameters, Linux process cleanup,
container integration, patient cooperation and benchmark results. Only the
Windows fake-process cleanup path was executed here. No benchmark parity is
claimed from these tests.

## One fresh live diagnostic command (prepared, not executed)

The allowlisted configuration fields in
`runs/20261104-cm-asthma-low-coop-02/batch.manifest.json` were inspected without
reading patient content: Luna/high actor, helpers, recovery auto, 100 model calls,
500 tool calls, unlimited context, 180-second request/600-second active timeout;
patient call/character/world quotas disabled, patient request timeout 180 seconds,
one attempt and concurrency one, deferred grading. The command preserves those
settings and changes the patient backend/model. It does not run a judge.

```powershell
Set-Location C:\Projects\BigData\HealthHarnessCodex
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.batch `
  --dataset-root C:/Projects/BigData/Dataset/chi-bench `
  --run-dir runs/20261104-cm-asthma-low-coop-sonnetpatient-01 `
  --domains cm --task-id cm_asthma_low_coop_001 `
  --attempts 1 --concurrency 1 --actor-backend harness `
  --model gpt-6-luna --composition helpers --recovery-helper-policy auto `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --timeout 180 --active-timeout 600 `
  --simulator-backend claude-cli --simulator-claude-model claude-sonnet-5 `
  --simulator-claude-executable claude `
  --simulator-max-model-calls 0 --simulator-max-total-chars 0 `
  --simulator-world-deadline-seconds 0 --simulator-request-timeout-seconds 180 `
  --json-summary
```

Batch CLI always defers grading. Use the fresh directory exactly once; preserve
unknown outcomes and failed attempts. This command is supplied for later user
execution only, not authorization for implementation-time inference.
