# Claude Code CM actor lane — November 3 implementation handoff

## Scope, ownership and status

Codex implements; the reviewing Claude session owns review, live Docker trial
and commit. Implementer must not commit, run Docker, invoke Claude live, or
launch a dataset trial. No such operation was performed during implementation.
The retained -21 world is untouched. Read [current index](HANDOFF.md) first.

Implemented: opt-in `--actor-backend claude-code` in the existing batch runner,
restricted to one explicit CM task, one attempt, concurrency one, experimental
Codex patient, deferred grading. Default harness configuration and dispatch
remain the existing path. This is software implementation, not a CM result.

Unverified: actual Claude 2.1.309 flag/auth behavior, live MCP negotiation,
Docker execution/export and clinical outcome. The implementer's tool-session
PATH does not resolve `claude`; the reviewer previously verified their host
login. Use their native CLI path when executing the command below.

## Source findings and adaptation

### Nov 3 -02 finding: MCP output spill

Live attempt `runs/20261103-cm-anorexia-claude-sonnet55-02` spilled the roughly
53,000-character `cm_chart.get_chart_data` result into Claude Code's host
project storage. With built-in Read disabled and proxy file tools confined to
the container, the actor could not see the chart. This is a harness mechanics
defect. Implemented/offline-tested only: fix `MAX_MCP_OUTPUT_TOKENS=200000` in
the actor environment and frozen isolation provenance; after process cleanup,
move only the exact sanitized-cwd project directory into the attempt's
`claude-project.private/`. Relocation events contain status and counts only;
failure preserves the actor outcome. No clinical rules or prompt changes.
Live verification remains pending; no Docker, real Claude CLI, dataset trial
or commit was performed for this repair. Offline verification: focused suite
**22 tests / 2.974 s**, full suite **765 tests / 70.096 s**, both passed;
`git diff --check` passed.
Reviewer probe (Claude 2.1.309, synthetic 68,000 chars): the token error disappears, but results still persist to host tool-results with only a preview/path shown.
Follow-up implemented/offline-tested only: audited, read-only host spill reads for the explicitly bootstrapped Claude cwd's project/session/tool-results files, with bounded continuation and full-file SHA-256.
Follow-up verification: focused **26 tests / 3.070 s**, full **769 tests / 70.701 s**, and `git diff --check` passed; see [HANDOFF.md](HANDOFF.md). No live Claude, Docker, dataset trial or commit in this follow-up.

- `Runner/chi-bench/configs/submissions/sonnet-5-claude-code.yaml` selects stock
  Harbor `claude-code`, not the repository's separate `claude-code-cli` mcporter
  variant. Its submission model is Sonnet 5; this lane explicitly selects the
  user's Sonnet 5.5/high instead. `Runner/chi-bench/uv.lock` pins Harbor 0.20.0.
- The local registry and CLI variant import Harbor's installed `ClaudeCode`.
  That dependency's source was not present in the local Runner directories;
  inspected upstream [ClaudeCode v0.20.0](https://github.com/laude-institute/harbor/blob/v0.20.0/src/harbor/agents/installed/claude_code.py)
  and [BaseInstalledAgent v0.20.0](https://github.com/laude-institute/harbor/blob/v0.20.0/src/harbor/agents/installed/base.py).
  `run()` sends the instruction via stdin to print mode, with verbose
  stream-json. `render_instruction()` leaves it unchanged unless a prompt
  template is configured; the supplied submission has none. There is no
  benchmark-specific wrapper to copy. This implementation passes the UTF-8
  instruction bytes decoded verbatim as the `-p` argument, preserving CRLF too.
- Stock registers task MCP servers and keeps Claude's ordinary local tools.
  `Runner/chi-bench/scripts/export_harbor_tasks.py` declares provider, payer and
  CM endpoints. The public CM instruction authorizes only `cm_intake`,
  `cm_chart`, `cm_outreach`, `cm_assessment`, `cm_care_plan`; therefore this lane
  exposes **only the CM endpoint :8200**, with the raw upstream tool names,
  descriptions, schemas and MCP result/error envelopes. Default upstream tool
  separator is `.`, also accepted by the stock Claude lane. Other namespaces
  are filtered even if returned by the endpoint. No clinical behavior rules or
  expected answers are added.
- Stock uses the environment's working directory (`/workspace` in the runtime
  Dockerfile), and can read local handbook/skills and write working files.
  Harbor copies configured skills into its Claude config directory. In this
  host adaptation, cwd is a newly created empty `attempt-1/claude-cwd/` and all
  built-in tools are off. Five MCP file operations replace local file/shell
  access: read, write, list, literal search, PDF text read. Relative paths use
  the selected case's `care-manager/`; absolute shared handoff writes also work.
  Read/write boundaries are that case's `care-manager/` and `shared/` only;
  handbook and tool-reference paths in the public instruction are read-only.
  Existing DockerWorkspaceTools path, symlink, hidden-material and size checks
  remain in force. No shell/interpreter, broad `/workspace` or `/logs`, fixtures,
  tests, solutions, evaluator, other cases or host files are exposed.
- Before file tools are offered, the proxy uses the existing public referral
  queue/readback discovery to bind the case/patient boundary. These additional
  read-only bootstrap calls are an adaptation for confinement; the selected
  identity/readback is **not injected into the prompt**. This is not a byte-
  identical stock trajectory or an official stock-Harbor execution. Skill
  auto-discovery is disabled; the actor can read the handbook at its documented
  path. The implementer did not read protected handbook contents.

## CLI isolation and process ownership

The [Claude headless documentation](https://code.claude.com/docs/en/headless)
states that `--bare` skips OAuth credentials/keychain and cannot use subscription
login. Accordingly, this lane does **not** use bare mode or copy auth files.
It uses `--setting-sources ""`, explicit `claudeMdExcludes: ["**"]`, disabled
auto-memory/hooks/plugins, disabled slash commands, no session persistence,
strict MCP config and `--tools ""`. `--allowedTools mcp__chi-bench-cm__*` plus
`--permission-mode dontAsk` permits the proxy without prompting. Existing home
login storage remains available. Inherited Claude customizations and Anthropic
provider routing/API-key variables are removed from the child environment;
an existing OAuth-token environment variable and configured login-store directory,
if supplied, are preserved only in memory. No credential values are logged. Managed CLAUDE.md files cause a launch
refusal because exclude globs cannot suppress them. Managed settings policy
still applies; runtime isolation remains subject to the reviewer's live check.
See [CLI reference](https://code.claude.com/docs/en/cli-reference) and
[instruction exclusion documentation](https://code.claude.com/docs/en/memory).

On Windows the actor starts suspended, is assigned to a kill-on-close kernel Job
Object, then resumes. Timeout kills the owned process tree including the proxy;
normal cleanup also closes the job. This avoids taskkill/WMI permissions and
prevents a child spawning before ownership is installed. POSIX uses a new
process session/group. Full-attempt actor wall time defaults to 1800 seconds,
independent of the existing patient's 180-second request timeout. No actor
retry or fallback model is launched automatically.

## Files and artifacts

- `HealthHarnessCodex/health_harness_codex/claude_code_actor.py`: stdlib stdio
  MCP proxy, confined file adapter, CLI runner, stream parsing, tree cleanup.
- `.../batch.py`: optional dispatch and CLI flags; freeze model/effort/executable
  path/hash/timeout/isolation settings; include private actor artifacts in the
  existing immutable snapshot. Existing simulator model/effort and approved
  Codex instruction pins still govern the patient, independently of Claude.
- `.../console_logs.py`: allow numeric reported turns/observed assistant-message
  counts. The reviewer's existing runtime-guard changes in this file and the
  other five files are preserved.
- `HealthHarnessCodex/tests/test_claude_code_actor.py`: offline fake process,
  stdio, MCP/docker-layer and full fake batch lifecycle tests.
- `HealthHarnessCodex/tests/test_standalone.py`: two fake harness constructors
  now accept the reviewer's optional `runtime_guard` keyword. No production
  guard was removed or bypassed to make these tests pass.

Private artifacts under ignored attempt directories:
`claude-stream.private.jsonl`, `claude-stderr.private.log`,
`claude-mcp.private.jsonl`, `claude-progress.json`, `claude-mcp.json`, plus the
usual result/evaluation/SQLite snapshot files. The SQLite ledger is empty for
this actor; it is retained for batch-format compatibility, not evidence that
the Python harness executed Claude's actions. MCP audit and exported world are
the execution evidence. Raw upstream tool errors are MCP tool errors; transport
and validation exceptions become generic tool errors with no raw container
stdout/arguments/exception bodies. No automatic write retry occurs.

Stream tool-use IDs and assistant-message IDs are deduplicated. Counts are
observations, not proof that a tool dispatched or succeeded. `num_turns` is
reported only when Claude supplies it, separately from model calls (unknown).
Usage, duration and total_cost_usd are the CLI's reports, not independently
measured cost or subscription billing. Stage/count events and a 15-second
heartbeat enter batch.events.jsonl and terminal logging; status JSON updates
atomically. A successful CLI exit maps to `claude_finished`/local `incomplete`,
an error to `claude_error`/local `error`, timeout to local `exhausted`. Clinical
goal stays unverified until evaluated. The batch may be deferred-ready after
any settled actor outcome if a valid export/snapshot is saved.

## Offline verification

From `C:/Projects/BigData/HealthHarnessCodex`:

```powershell
$python = 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $python -X utf8 -m unittest discover -s tests -p test_claude_code_actor.py -q
& $python -X utf8 -m unittest discover -s tests -q
```

Final focused run: **18 tests passed in 2.697 s**.
Final integrated run after all source changes: **761 tests passed in 69.584 s**.
`git diff --check` passed. Final private log:
`HealthHarnessCodex/runs/20261103-claude-lane-acceptance.log`.
Initial full suite: 757 tests / 65.196 s, 2 failures + 8 errors, all attributable
to the two old fake harness constructors rejecting `runtime_guard`. After the
minimal fake compatibility fix: 760 tests / 69.282 s, all passed. The initial
new timeout tests also caught taskkill cleanup failure in this sandbox; replaced
with Job Object ownership, then tested actual fake descendants stopping.
Logs remain ignored under `HealthHarnessCodex/runs/20261103-claude-lane-*.log`.

## Reviewer: exactly one live attempt (not executed by implementer)

Check for an existing completed run before launching. Review/commit the diff and
freeze source first; do not modify source while the batch is running.

```powershell
Set-Location C:/Projects/BigData/HealthHarnessCodex
$python = 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $python -X utf8 -m health_harness_codex.batch `
  --dataset-root ../Dataset/chi-bench `
  --run-dir runs/20261103-cm-anorexia-claude-sonnet55-01 `
  --domains cm --task-id cm_anorexia_hard_refuses_001 `
  --attempts 1 --concurrency 1 --actor-backend claude-code `
  --claude-executable (Get-Command claude -ErrorAction Stop).Source `
  --claude-model claude-sonnet-5-5 --claude-effort high `
  --claude-timeout-seconds 1800 --simulator-backend codex `
  --simulator-max-model-calls 0 --simulator-max-total-chars 0 `
  --simulator-world-deadline-seconds 0 --simulator-request-timeout-seconds 180
```

CLI batch execution already always defers grading; no grading enable flag,
provider key or paid judge is used here. Patient remains fixed Luna/high.
Harness helper/composition/model/tool budgets do not govern Claude and are
explicitly marked unapplied in provenance; the wall-clock deadline governs it.

Once the attempt is deferred-ready and its world stopped, run the existing local
key-free native structural diagnostic separately:

```powershell
& $python -X utf8 ./runs/check_structural_no_judge.py 20261103-cm-anorexia-claude-sonnet55-01
```

That existing ignored operator script verifies the immutable snapshot, copies
its export into a fresh `*-structural-only` directory and runs native checks in
a separate read-only/network-none pinned-runtime container, with
`include_semantic_judge=False`. It verifies the original snapshot again and
does not replay the actor. The private scorecard is not an official semantic
benchmark score. Preserve failed trials and all receipts. Only the reviewer
may decide the previously authorized conditional Opus attempt after assessing
the first result; the lane never launches it automatically.

## Live results (Nov 3)

Sonnet 5.5/high `-02` and Opus 5.5/medium `-01` were both executed. Both failed
native structural checks with 2/6 and binary 0. The spill read path was verified live
in the Opus run. See the [HANDOFF.md](HANDOFF.md) results table.
