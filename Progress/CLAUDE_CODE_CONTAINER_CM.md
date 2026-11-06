# In-world subscription Claude Code CM lane, November 3

## Ownership and current state

Codex implements; reviewer reviews, runs the one live Docker attempt and commits.
No commit, Claude inference, OAuth-file inspection, dataset trial or judge was
performed by the implementer. One read-only image-source inspection was attempted
with `docker run --rm --network none --entrypoint python bigdata-chi-tools:4444a07`;
the sandbox denied access to the Docker Desktop named pipe. No container started.
Pre-existing `.gitignore` and `.playwright-mcp/` changes remain outside this work.

Implemented: `--actor-backend claude-code-container`, exactly one explicit CM
task/attempt, concurrency one, Codex Luna/high patient, deferred grading only.
Host `claude-code` and default `harness` remain separate backends. The new backend
automatically selects bridge networking, no published ports and no provider env
file. Every other Codex-patient backend still rejects egress.

## Shipped-agent source findings

Local references:

- `Runner/chi-bench/uv.lock:1244`: Harbor 0.20.0 wheel/sdist and hashes.
- `Runner/chi-bench/configs/submissions/sonnet-5-claude-code.yaml:9`: selects
  stock `claude-code`, model `anthropic/claude-sonnet-5`, Modal, multiplier 2.0;
  no CLI version or custom prompt template.
- `Runner/chi-bench/src/chi_bench/experiment/agents/registry.py:66`: OAuth
  accepted for both Claude agents.
- `Runner/chi-bench/src/chi_bench/experiment/agents/claude_code_cli_harness.py:20`:
  the separate mcporter variant subclasses Harbor; suppresses MCP registration,
  clears `.claude.json`, writes `~/.mcporter/mcporter.json`, rewrites instructions.
  This backend follows the selected stock MCP variant instead.
- `Runner/chi-bench/scripts/export_harbor_tasks.py:238`: all three stock HTTP
  MCP endpoints: `chi-bench-provider` localhost:8020/mcp, `chi-bench-payer`
  localhost:8100/mcp, `chi-bench-cm` localhost:8200/mcp. Exported agent timeout
  comes from source task TOML; fallback 900 seconds (`:255`), submission multiplier
  2.0. The selected source task TOML was not opened.
- `Runner/chi-bench/docker/Dockerfile:28`: image build installs npm CLI `@latest`,
  keeps a `/usr/local/bin/claude` resolver and `/usr/bin/claude.real`; WORKDIR
  `/workspace`, no USER override, `IS_SANDBOX=1`. Runtime code is `/workspace/src`,
  baked task/world data `/opt/chi-bench`, mutable state `/tmp/chi-bench-runtime`,
  workspace files `/logs/artifacts/workspaces`, raw artifacts `/srv/chi-bench/raw`.

The installed Harbor source was absent from the local `.venv`; image inspection
was denied. Source fallback is the primary upstream tag, not verification of the
installed wheel's bytes:

- [Harbor ClaudeCode v0.20.0](https://github.com/laude-institute/harbor/blob/v0.20.0/src/harbor/agents/installed/claude_code.py),
  lines 128-181, 1210-1235, 1256-1413: checks existing CLI; otherwise installs
  curl/procps as root, native bootstrap on Debian/RPM, npm on Alpine. No version
  pin unless explicitly configured. Runs as environment default user, with
  `IS_SANDBOX=1`, background-task toggles, nonessential traffic disabled,
  model in `ANTHROPIC_MODEL`, and sessions under `/logs/agent/sessions`.
  HTTP MCP registration maps streamable-http to Claude's `http` type.
- [Harbor BaseInstalledAgent v0.20.0](https://github.com/laude-institute/harbor/blob/v0.20.0/src/harbor/agents/installed/base.py),
  lines 480-555: default-user exec, optional timeout, verbatim instruction when
  no template is configured. Stock feeds instruction via stdin to verbose
  stream-json print mode, default bypassPermissions, and tees combined output.

Upstream filesystem access follows the container user's ordinary permissions;
there is no actor filesystem allowlist in those methods. This image defaults
to root, so reproducing that unrestricted access would expose baked hidden data.

## Implemented command, boundaries and all deviations

The fixed bootstrap source is supplied directly to `docker exec -i -e
CLAUDE_CODE_OAUTH_TOKEN <owned-world> /usr/local/bin/python -I -c <source>`.
Only the public instruction, model/effort, HTTP MCP config and a public-MCP-bound
workspace path travel on stdin. No fixture/test/solution/verifier input is read.

The actual Claude argv is:

```text
<resolved-in-container-claude> --verbose --output-format=stream-json --permission-mode=bypassPermissions --print --model claude-sonnet-5-5 --effort high --no-session-persistence
```

1. Uses the batch Docker lifecycle, not Harbor orchestration/Modal. Reuses the
   pinned runtime digest, worker, spool, world export, deferred snapshot and
   manifests. No judge. This is not an official stock-Harbor score.
2. Sonnet 5.5/high are explicit CLI flags, replacing the submission's Sonnet 5
   model environment setting. No added clinical prompt, helper or behavioral
   rules. Public instruction bytes, including CRLF, go through stdin.
3. Token comes only from ignored `Runner/claude-oauth.env`, validated in memory
   before world start. Only its variable name appears in docker exec argv; the
   client subprocess environment supplies its value. Installer, cleanup,
   docker run and patient server receive no OAuth token. No host home mount or
   credential-file copy. No provider key/base URL is passed to Claude.
4. Installation follows upstream's check/reuse/bootstrap approach with no CLI
   pin. A failed existing `claude --version` triggers repair installation, and
   install output goes to private stderr. No `.bashrc` modification is needed
   because PATH is explicit. The runtime Dockerfile already installs a CLI,
   but its actual installed version is unverified; version output is retained
   in the private stderr artifact. Native installer resolution needs egress if
   the baked CLI is unavailable. A pinned prebuilt CLI/image could avoid install
   egress; no proxy or artifact mirroring was added.
5. Docker bridge is automatic only here. The existing patient's dummy marker
   `ANTHROPIC_API_KEY=codex-local-bridge` and loopback base URL remain on the world
   server; they are not provider credentials. A fresh whitelist environment
   strips them from Claude. `patient_simulator.py:61` constructs
   `anthropic.AsyncAnthropic()` with default environment routing, so it retains
   the spool endpoint regardless of bridge networking. Live routing remains to
   be verified by the reviewer; no patient implementation changed.
6. Native built-in tools remain available, with root/IS_SANDBOX and cwd
   `/workspace`, but [Landlock](https://docs.kernel.org/userspace-api/landlock.html)
   restricts the actor's filesystem. Requires ABI >=3, x86_64/aarch64, permitted
   syscalls; fails closed if unavailable. Read grants: `/usr`, `/bin`, `/lib`,
   `/lib64`, `/etc`, `/root/.local`, the public handbook and tool-reference file,
   null/random devices and four public proc status files. Read/write grants:
   only the discovered case's `care-manager/` and `shared/`, private actor temp,
   and `/dev/null`. No broad workspace, runtime source, dataset, logs, spool,
   raw-store or Docker-socket grant. Existing workspace symlinks are rejected.
   Kernel enforcement/CLI compatibility have not been live-tested here.
7. Config/HOME/temp are fresh under `/tmp/chi-claude-actor`, not Harbor's mounted
   sessions directory. Sessions are disabled and private config/spills removed
   after execution; no stock skill-copy/auto-memory seeding or ATIF conversion.
   Handbook stays readable at its original public path. Persistent evidence is
   the redacted private CLI stream, stderr, progress, config and world snapshot.
8. No tee in the container: the host drains both pipes, replaces the exact
   secret before parsing/writing, deduplicates tool/message IDs, records only
   observed counts, and emits stage/15-second heartbeat/progress JSON. Read-only
   public referral binding before Claude starts is an extra confinement step;
   its results are not injected into the prompt. Counts describe CLI stream
   observations, not successful MCP dispatches or clinical success.
9. Default 1800-second actor budget includes public binding, installation and
   inference; cleanup has a separate bounded allowance. Host timeout also issues
   an in-container process-group SIGKILL, waits for it to settle and removes
   private config. A persistent cancellation marker prevents a delayed Docker
   exec from starting installation/inference after timeout cleanup checked for
   its PID. Cleanup failure is an error. No automatic attempt/model retry.

Files: `HealthHarnessCodex/health_harness_codex/{batch.py,claude_code_actor.py,
claude_code_container_actor.py,claude_container_runtime.py}` and
`HealthHarnessCodex/tests/test_claude_code_container_actor.py`. Existing source
fingerprinting includes both new Python modules. New container CLI artifacts
are copied and hashed into deferred snapshots through the existing machinery.

## Offline validation

From `HealthHarnessCodex/`, using
`C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`:

```powershell
& $python -X utf8 -m unittest discover -s tests -p 'test_claude_code*actor.py' -q
& $python -X utf8 -m unittest discover -s tests -q
```

Focused final: 39 tests passed / 4.109 s. First full suite: 781 passed / 79.420 s,
log `HealthHarnessCodex/runs/20261103-claude-container-suite.log`. Final integrated
verification, including the cancellation race fix: **782 tests passed / 74.215 s**,
log `HealthHarnessCodex/runs/20261103-claude-container-suite-final.log`.
`git diff --check` passed. No source changes followed this final suite.
Fakes cover token parsing/missing-before-start; no token in argv, stream,
stderr, progress, SQLite, snapshots or manifest; network boundaries; stock MCP
and launch config; distinct patient/actor environments; stream counts/timeouts;
cleanup failure; batch patient/snapshot/no-judge lifecycle. Real Linux kernel
filesystem enforcement and real in-container process cleanup are unverified.
The final added test covers timeout cancellation before/after process-group
publication. An intermediate full rerun also passed 781 tests / 71.722 s before
this final race regression was added.

## Reviewer: exactly one live attempt, then separate key-free check

Review/freeze source first and ensure this fresh run directory does not already
contain an attempt. The implementer did not execute these commands.

```powershell
Set-Location C:/Projects/BigData/HealthHarnessCodex
$python = 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $python -X utf8 -m health_harness_codex.batch `
  --dataset-root ../Dataset/chi-bench `
  --run-dir runs/20261103-cm-anorexia-claude-container-sonnet55-01 `
  --domains cm --task-id cm_anorexia_hard_refuses_001 `
  --attempts 1 --concurrency 1 --actor-backend claude-code-container `
  --claude-model claude-sonnet-5-5 --claude-effort high `
  --claude-timeout-seconds 1800 --simulator-backend codex `
  --simulator-max-model-calls 0 --simulator-max-total-chars 0 `
  --simulator-world-deadline-seconds 0 --simulator-request-timeout-seconds 180

& $python -X utf8 ./runs/check_structural_no_judge.py `
  20261103-cm-anorexia-claude-container-sonnet55-01
```

Batch CLI always defers grading. The second command is only for a verified
deferred snapshot after the world stopped; it is the existing key-free native
structural diagnostic, not a semantic judge or official grade. Do not retry the
actor automatically on any failure. Preserve logs/snapshot and report the exact
setup/actor/patient/cleanup result. Clinical performance remains unverified.
