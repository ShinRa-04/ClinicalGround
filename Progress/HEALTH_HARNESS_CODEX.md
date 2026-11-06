# Codex-backed healthcare harness fork

**Current October 20:** frozen actor source `03c845d` scored **3/3 official passes, 21/21 checks in every trial**, on the same public UM development task. Its single-task pass@1/pass@3/pass^3 are all 100%; this is not a full-dataset or held-out result. Root passed **187 software tests** (20.628 seconds) and matched all 33 original harness hashes. Two trials retained local `unresolved` because the model returned prose without the required structured completion record; the official grader independently passed their actual worlds. The third was locally complete. All three worlds are stopped after official receipts and integrity-checked SQLite backups; no inference is active. No PR or submission is authorized. See [measured pilots](HEALTH_HARNESS_PILOT_RESULTS.md) and [official evaluation](HEALTH_HARNESS_OFFICIAL_EVALUATION.md).

## Historical receipts

The following dated sections preserve earlier implementation, pause and execution states. Older pending/no-grade/no-live-run instructions are superseded by the current result and authorization above. Do not resume any old handle or replay a saved journal against a restarted world.


Current follow-through supersedes the earlier identity-blocked milestone: **119 tests pass**, late case/patient binding is implemented with provenance and isolation, and actual attempt-3 reached local completion plus independently observed final approval/provider-letter delivery. Two stricter audits retained an unresolved member-delivery requirement because no member Message send tool exists. Scope clarification is pending. Read [the latest receipt](HEALTH_HARNESS_EXECUTION_FOLLOWTHROUGH.md) for exact execution, counters, capability limits and the corrected runtime-reset finding. The runtime remains running for safe continuation; do not restart it and replay old state.

## Latest executed milestone — October 19, 05:00 IST continuation

The standalone host-to-container actor bridge and reusable evaluation recorder are implemented and exercised. **91 software tests pass**. Two genuine Luna-high attempts on one public UM case are preserved. Attempt 2 made routing changes; public actor readback is finalized/approved, but local status is blocked because routing first exposed a patient ID conflicting with the temporary case-subject namespace. No official completion, score, simulator inference or submission is claimed. The owned container is stopped and retained with changed world state. Read [the executed receipt](HEALTH_HARNESS_STANDALONE_RUN.md) and [evaluation guide](../HealthHarnessCodex/EVALUATION.md) for exact evidence, limitations and the late-identity improvement needed next. Earlier sections below describe the conversion before this later runtime milestone.

Latest ownership: Luna-high real_case_bridge implemented docker_bridge.py/standalone.py and initial tests; Luna-high run_evaluation implemented evaluation.py and tests; Luna-high identity_finish added explicit internal case-subject binding and clarified native proposal instructions. Root reviewed, added actual workspace-boundary/namespace/classifier checks, ran 91 tests and both actual attempts, preserved reports, compared provenance, verified all 33 original hashes, stopped the owned container and documented outcomes. Source/test/docs are tracked; payloads remain ignored. Current evaluation records operational behavior, not clinical correctness or an official score.

## Scope and current state

October 19, 2026: user requested duplicating HealthHarness and iterating the duplicate into a Codex connection layer, explicitly avoiding a rewrite. New root: HealthHarnessCodex/. Original HealthHarness/ stays unchanged; FORK_BASELINE.json pins all 33 copied tracked files at 0cb99c9. Ignored builds, run data, credentials and caches were not copied. Distinct Python namespace/distribution avoid import/install collisions.

Implementation is complete as a host-side Codex connection variant. The existing engine/state/role/context/tool/recovery logic is reused. New transport/provider/factory/CLI paths drive a fresh official Codex App Server process and ephemeral thread per completion and return validated proposed actions to our engine. The engine executes actual harness tools.

## Ownership and files

- GPT-6 Luna high codex_backend: codex_transport.py, codex_provider.py and new backend tests.
- GPT-6 Luna high codex_integration: copied CLI/factory/smoke/configuration, packaging metadata and explicit unsupported trial guards.
- Root: source duplication/namespacing, interface verification, native probes/smokes, review fixes, documentation, original-integrity checks and commit.
- [README](../HealthHarnessCodex/README.md), [verification](../HealthHarnessCodex/VERIFICATION.md), [fork baseline](../HealthHarnessCodex/FORK_BASELINE.json), [example config](../HealthHarnessCodex/config.example.json).

## Executed evidence

64 software tests passed independently in root with Python 3.12.14 (inherited 43 plus new connection tests, not 64 benchmark tasks). Native version0.163.0-alpha.10.2 at C:/Users/prath/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe was verified; protocol schemas generated under ignored fork runs/. Native account probe shows configured ChatGPT sign-in without exposing identity/token data.

Final wheel, offline demos, compile checks and isolated wheel import/role-data/demo checks passed. Artifact health_harness_codex-0.1.0-py3-none-any.whl is 58858 bytes, SHA-256 `3cdd8056f68b3c8f5ba8ab72da56cbf14f5877eca3033d154f34119676cad4e3`, local/ignored under fork dist/. Original 33 tracked files remain hash-identical and the role catalogue is byte-identical. The standalone trial launcher defaults to Codex and refuses unsupported trial execution; HTTP fallback requires explicit selection.

Genuine Luna-high smoke was executed using existing sign-in and synthetic tools only. Final run: two engine completion calls, one harness-executed tool, successful evidence-linked local completion. Native reported tokens: input17952/output173/total18125, reasoning-output70. An intermediate repeat was unresolved (one completion/zero tools/prose), and an initial optional-jsonrpc-field incompatibility was fixed. All attempts and their limits are recorded in VERIFICATION.md; no benchmark reliability percentage is inferred.

Native Codex reports the global user AGENTS.md despite project guidance suppression. Unknown sources fail before case input; the unchanged reviewed general preference file was explicitly hash-approved for native smoke. Shared policy is documented, not silently omitted from the claimed prompt. No automatic cross-patient memory/learning is permitted.

## Setup/run

From HealthHarnessCodex/: python -m health_harness_codex --demo; python -m unittest discover -s tests -v. README contains explicit --codex-probe and --codex-smoke commands using the official absolute executable path and optional reviewed --codex-instruction-source. Configured runs select provider.type=codex_app_server and need no provider API key. They do require a valid supported native sign-in and actual authorized MCP/task identities.

Native processes start hidden, with bounded I/O/timeouts and explicit owned-process cleanup. No login browser is opened automatically. Do not read/copy raw auth state, attach an arbitrary Python client to this desktop conversation, or treat returned Codex action events as approved harness effects.

## Limits and next steps

At the original conversion milestone, host/controller inference was connected but the host-to-container bridge was not implemented and no official case had run. That limit is superseded for the standalone actor path by the executed milestone above. Harbor launcher integration still refuses unsupported Codex execution. Late patient identity reconciliation, separate simulator/judge prerequisites and broader domain/runtime validation remain unresolved.

Output-token setting is advisory on this route; strict token caps are not verified. Source/role/policy validity, clinical quality, performance benefit, provider retention and hardened multi-tenant confidentiality remain unverified. See exact test/native scope in VERIFICATION.md before making claims.

## User-requested unrelated command cleanup

Renamed the Python comic-library codex.exe launcher to codex-comic-library.exe without removing Python's Scripts directory or uninstalling that application. Get-Command codex now resolves to the official OpenAI executable and version check passed. Prior generated comic settings remain preserved in ignored Runner cache as already documented. No credentials were printed, no original harness files changed, and no global user instruction file was edited.

## Active real-case run and evaluation work

October 19: user authorized connecting and attempting one actual standalone dataset case, then asked for reusable evaluation for future improvement. Root is starting the existing Docker runtime; Luna-high real_case_bridge owns confined Docker MCP/workspace transport and standalone runner, and Luna-high run_evaluation owns event recording, operational reports and comparison. First task is selected by public starting-stage instructions, not expected answers; all work must follow its full assigned outcome. No official grader invocation/submission is authorized. Native Codex sign-in provides actor inference; lack of separate simulator/judge credentials may block dialogue/scoring. Record exact observed progress and failures, not automatic benchmark success.
