# t033 -16: Unicode degeneration and recovered snapshot

October25,2026. Root coding and authorized single-case execution; no judge.
Frozen actor `6c085ee`, run `20261025-random-um-t033-16`.

## Actual failure

Call8 streamed14,778 characters/40,310 UTF-8 bytes before native turn failure
`error:unknown:other` at160.2s. Neither the180s silence timeout nor600s active
cap expired. The captured tail contains9,999 consecutive U+2753 question-mark
symbols and one replacement character in its last10,000 characters. It was not
a long useful clinical explanation. No proposals from this unfinished call ran.
The underlying model/backend cause remains unconfirmed; do not call this an
account limit, context-limit failure or an error fixed by changing clinical rules.

Recorded8 model calls/21 tool proposals;599,840 reported tokens
(565,983 input/33,857 output;202,112 cached input included).

The batch then hit `PermissionError` during deferred export/snapshot capture and
correctly preserved its world for reconciliation. The original error lacked
enough filesystem detail to identify the exact cause. A later capture succeeded;
do not attribute the original failure to antivirus, file locking or permissions
configuration without evidence.

## Actual recovery

Root revalidated the owned world, captured its native HTTP export, froze and
verified213 files, stopped the container, and updated the attempt's reconciliation
receipt. No actor actions, clinical writes, model calls or judge were replayed.
The snapshot retains the original actor failure and frozen provenance. It is
ready for deferred evaluation, not a completed healthcare testcase. Operator
recovery script errors were corrected before the final receipt; data and earlier
failure logs remain preserved under ignored runs/.

Native structural checks on the recovered snapshot:3/12 applicable pass,9 fail,
15 N/A; structural binary0/fractional0.25; semantic grading disabled. Failure
names reflect the unreached nurse, MD, notice/outcome and triage-metadata stages.
The MD sign-off precommit repair was not reached or evaluated by this attempt.

## General repairs

- A4,096-character rolling window detects exact repetition of a pattern of1–8
  characters. This addresses both observed zero padding and Unicode symbol
  loops, without selecting an outcome or parsing clinical meaning. It rejects
  the unfinished response as `response_repetition` and uses the existing single
  format-correction allowance. Captured text remains private; no partial calls
  dispatch. The window is reset before every request/case, including invalid
  new input. Normal long varied replies retain the existing60k size and active
  time limits. Deliberately generating thousands of repeated characters would
  also be rejected; this is an explicit harness liveness tradeoff. More complex
  repetition beyond8-character periods is not certified as detected.
- Private stage diagnostics now save exception type, OS error codes, filename
  and stack frame locations. They exclude exception message bodies and locals,
  never overwrite a prior diagnostic, and cannot mask the original failure.
  These improve diagnosis if the Windows snapshot error recurs; they do not
  establish or claim to fix its unknown underlying cause.

Full regression658 tests pass/80.926s. Actual Codex synthetic liveness probe
`20261025-repetition-native` intercepted requested zero padding and accepted the
next finite corrected response. Two inference calls, zero actual tools, no
dataset actor or judge. This proves response-boundary recovery, not clinical
performance. The next fresh case must independently establish the workflow.

## Fresh single-case command

Root executes this after source commit; do not duplicate it while active.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-um-t033-17 `
  --domains pa_um `
  --task-id pa_t033_t033_o001_p01_triage_payer `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```
