# Experimental Codex simulator: implementation and execution

**State:** synthetic SDK bridge QA passed and one fresh CM case reached local completion on October 22, 2026. Frozen source: `771286236e65146d3dfce3c286afbb45c23b23f0`. The Codex simulator remains experimental; no judge or official grade ran. This note is separate from the run-03 integration handoff and records simulator QA evidence and limits.

## Intended proof

The one-call check in `HealthHarnessCodex/runs/20261022-codex-simulator-qa-02/run_synthetic_native_qa.py` sends a synthetic Anthropic Messages request from the benchmark runtime image to a loopback bridge inside the container. The container uses Docker `--network none` and mounts only the per-run spool plus the bridge source. A host-side `SimulatorWorker` reads the private spool and invokes the installed native Codex executable with `gpt-6-luna`, high effort, and a one-call cap. The passing receipt requires a settled completed Codex reply, actual usage fields, and exact `PATIENT_OK` text.

The system and user messages contain only a synthetic transport phrase. No task directory, fixture, patient data, handbook file, provider credential, benchmark `.env`, or network egress is supplied to the check. The local bridge key is a fixed loopback sentinel, not a provider credential. The result receipt keeps only success, model identity, usage counts, and safe worker status; it does not keep the response text or request body. A failure after submission remains a single-call result and is not retried.

This demonstrates one synthetic transport and usage-envelope exchange on the installed Codex path. It does not test Anthropic's remote service, nor does it establish benchmark comparability with the official Sonnet 5 simulator. Codex is an experimental simulator replacement; no official judge or benchmark score was used.

## Execution evidence

The first invocation stopped before worker startup because Docker Desktop's Linux engine pipe was unavailable. The runner reported a generic digest mismatch, but a safe follow-up confirmed the actual cause was the unavailable daemon; no inference was submitted. That receipt is preserved as `HealthHarnessCodex/runs/20261021-debug-run03/simulator-qa/qa.preflight.20261022T1.json`.

After Docker became ready, version 29.8.2 was available and the pinned image digest matched `sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66`. The initial synthetic attempt then recorded one worker submission marker but ended `submitted_outcome_unknown`; it had zero completed replies and no usage envelope. The body-free events show 3,375 ms from the local submission marker to the unknown outcome. That receipt remains unchanged. A later read-only reproduction showed that omitting the reviewed instruction-source allowlist can fail local thread startup; this identifies a setup failure mode but does not establish the original attempt's terminal cause.

The revised QA supplied the reviewed instruction source `C:/Users/prath/.codex/AGENTS.md` with pinned SHA-256 `1c683adadd4bffe13c4ff0700dc824fd3f3f35c024ffc3b6c68959f887318f96`. Its pre-call receipt records source commit, script/bridge/worker/provider/config code hashes, native executable hash, and runtime image digest in `HealthHarnessCodex/runs/20261022-codex-simulator-qa-02/qa.preflight.json`. The body-free result at `qa.result.json` records one worker submission, one completed Codex call, `settled=true`, exact `PATIENT_OK`, backend `gpt-6-luna`/high, and actual SDK usage of 6,543 input plus 72 output tokens. It records no clinical task, judge, or official score. The local package-root correction that preceded this call is separately recorded in `qa.local-preflight-error.01.json`; that attempt submitted no request. The first unknown-attempt spool and receipts were not copied, overwritten, or replayed.

The standalone synthetic check passed. This does not establish any official score, clinical workflow behavior, or model comparability with the pinned simulator.

## Fresh CM diagnostic

One fresh attempt ran for `cm_copd_hard_refuses_002` in `HealthHarnessCodex/runs/20261022-codex-simulator-cm-01/`, under the same frozen source commit. The actor used `gpt-6-luna` high with 48 model-call and 240 tool-call budgets. The experimental Codex patient simulator used its standard cap of 8 calls, 180,000 input characters, 900-second world deadline, and 180-second request timeout. Concurrency was one, grading was deferred, and no benchmark environment file or benchmark network was supplied.

The attempt settled as `deferred_ready`, with local status `complete` and grading `pending`. Its snapshot was saved and the world stopped. Safe actor logs record 23 completed workflow calls, 31 tool calls, 1,211,939 input tokens, and 9,819 output tokens. The simulator's body-free spool receipts show four completed `cm_patient` responses, zero unknown outcomes, 37,990 input tokens, and 867 output tokens. These are functional local observations from one experimental case, not an official judge result or benchmark pass. No PHI, task payload, patient transcript, or model reply was read for this report; output is stored only in the ignored local run.

## Combined 75-task follow-up status

The original run-03 baseline remains 5 local-complete and 70 needing follow-up. The separate later six-case run adds the locally complete `pa_t036_t036_o002_p01_new_referral_provider`; the newer CM case adds `cm_copd_hard_refuses_002`. Across observed attempts, 7 distinct task IDs now have a local-complete result and 68 still have a non-complete local status requiring follow-up. The generated [75-task JSON ledger](../HealthHarnessCodex/runs/20261022-followup-status/latest-followup.json), [CSV ledger](../HealthHarnessCodex/runs/20261022-followup-status/latest-followup.csv), and [counts](../HealthHarnessCodex/runs/20261022-followup-status/counts.json) use only task ID, local status, source commit, backend, and follow-up flag. Each row uses the newest observed attempt for that task.

This is operational coverage only across multiple source commits and simulator backends. It is not a pass rate or official score. A clean same-version 75-case regression run has not been performed.

## Offline inspection completed

- Read the prepared runner and confirmed it has `max_calls=1`, a 170-second world deadline, a 150-second request timeout, no fixture or dataset mount, and Docker network mode `none`.
- Parsed the runner with Python `ast.parse`; result: `syntax_ok`. This was a syntax-only check and made no network or model call.
- Read only the allowlisted run-03 machine ledger and the six-case representative machine ledger for counts. No clinical payloads, task instructions, actor prose, tool arguments, or verifier expectations were read for this summary.
- The original 75-task run-03 ledger reports 75 attempts: 5 local `complete`, 24 `unresolved`, 32 `error`, 8 `blocked`, and 6 `setup_failure`. Its five local-complete IDs are:
  - `pa_t012_t012_o001_p01_new_referral_provider`
  - `pa_t013_t013_o002_p01_new_referral_provider`
  - `pa_t021_t021_o003_p01_new_referral_provider`
  - `pa_t024_t024_o001_p01_new_referral_provider`
  - `pa_t034_t034_o002_p01_new_referral_provider`
- Follow-up counts from the sanitized run-03 report are 70/75 with issues: 62 fresh-world rerun candidates and 8 cases gated for issue-specific reconciliation or scope review. The 8 gated cases comprise 7 unknown writes and 1 quarantined out-of-scope result. The 24 unresolved workflows are summarized as 14 prose finals, 6 pending/incomplete finals, 3 open-obligation claims, and 1 unobserved evidence citation.
- The separate six-case representative ledger at source `56afb4e1a83557721bb66d6817980a18192afa8d` records 6 saved attempts: 1 local `complete`, 2 `unresolved`, 2 `blocked` due to unknown effects, and 1 `error` classified as a schema/scope rejection. It records 0 official grades. These six diagnostics remain separate from run 03 and are not a cross-version pass rate.

The source ledgers are `HealthHarnessCodex/runs/20261021-full-dataset-03/debug-report/all-cases.json` and `HealthHarnessCodex/runs/20261021-debug-run03-representative-01/debug-report/all-cases.json`. The original run-03 artifacts were not modified.

## Commands and execution status

The original dated script produced a daemon-unavailable preflight receipt and then one ambiguous submission; both receipts remain immutable and were not replayed. A separate private script was prepared and run after root froze commit `771286236e65146d3dfce3c286afbb45c23b23f0`.

A local package-root error in that fresh script copy was fixed before worker startup; its zero-submission receipt is preserved. The corrected script passes the reviewed `DEFAULT_INSTRUCTION` path and pinned SHA-256 to `SimulatorWorker`, verifies that instruction file before use, and writes `qa.preflight.json` with the frozen commit and code hashes before worker startup. Its result distinguishes worker submission markers from completed Codex calls and records real token usage only when a completed reply and SDK envelope are present.

```powershell
python .\HealthHarnessCodex\runs\20261022-codex-simulator-qa-02\run_synthetic_native_qa.py
```

After that synthetic check passed, the following isolated CM command ran for `cm_copd_hard_refuses_002`. It used no benchmark credential file, one attempt, one worker, deferred grading, actor budgets of 48 model calls and 240 tool calls, and the standard experimental Codex simulator defaults: 8 calls, 180,000 input characters, a 900-second world deadline, and a 180-second request timeout. The local status is `complete`; the official grade remains pending because no judge ran.

```powershell
Set-Location C:\Projects\BigData\HealthHarnessCodex
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m health_harness_codex.batch `
  --dataset-root C:/Projects/BigData/Dataset/chi-bench `
  --run-dir runs/20261022-codex-simulator-cm-01 `
  --domains cm `
  --task-id cm_copd_hard_refuses_002 `
  --attempts 1 `
  --concurrency 1 `
  --max-model-calls 48 `
  --max-tool-calls 240 `
  --simulator-backend codex `
  --simulator-max-model-calls 8 `
  --json-summary
```

The CM attempt is one experimental local diagnostic, not an official benchmark pass. Preserve its raw attempt and local safe diagnostics; do not replay an uncertain write. Do not run a judge, infer a benchmark grade from local completion, copy or move Codex, modify global Codex policy, or combine this pilot with another version's counts. The official simulator remains pinned Sonnet 5; the Codex lane is experimental.

## Ownership and continuation

The simulator QA preparer owns this document and offline preparation. The integration peer owns `Progress/HANDOFF.md` and the run-03 main debug report. Do not edit batch/runtime modules as part of this QA-preparation task. Root owns final review, source freeze, approval of any call, execution, and any integrated handoff update.
