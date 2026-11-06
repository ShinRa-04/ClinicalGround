# Completed t033 no-judge execution — October 25, 2026

**The fresh actor completed normally. χ-Bench's native structural verifier
passed18/18 applicable checks, with0 failures and10 N/A. The semantic judge was
not run. This is not a full official benchmark verdict.**

Root executed one explicitly selected UM task, not all75. Run directory:
`HealthHarnessCodex/runs/20261025-random-um-t033-18/`. Actor source commit:
`2e8a0335c718ee8f5bcf80251aa6814b2fcf5cef` (code repairs through `56f748b`).
Model GPT-6 Luna/high, helpers enabled, recovery policy auto,180s setup/silence
timeout,600s active total cap,100 model/500 tool budgets, context cap disabled.
No case-specific expected answers, hidden-fixture inspection by the acting model,
paid provider calls, submission or remote publishing were used.

## What actually ran

| Measurement | Observed result |
| --- | --- |
| Harness endpoint | complete; no further permitted action reported with source references |
| Supported branch | MD information-request handoff |
| Nurse work |9 actual criterion evaluations and submitted case recommendation |
| MD case decision |request_info, signed_off=true |
| Notice | Pend notice actually delivered |
| External dependency | One provider-information obligation recorded and deferred |
| Readback/closure | Fresh scoped records, accepted assignment audit and accepted stopping record |
| Model calls |34, all finished;0 failed calls/format corrections |
| Tool operations |74 harness-counted proposals, including internal operations and any validation feedback |
| Helper/counterparty inference |0 helper jobs;0 simulator model calls |
| Actor duration |720.5 seconds;771.9 seconds including world startup/snapshot/shutdown |
| Reported usage |2,602,412 total:2,566,069 input +36,343 output |
| Cache detail |916,352 cached input tokens, included in input total |
| Reasoning detail |16,362 reported reasoning-output tokens |
| Attachment provenance |12 actor-listed case-attachment receipts across policy records |
| Snapshot |216 files/134 directories, integrity verified; container stopped |
| Judge | Disabled; no semantic/clinical score or cost |

The worker used the word incomplete for the broader healthcare case: external
records and a plan-policy scope question remain unresolved. It separately
provided the required source-backed no-further-action assessment. The controller
accepted the completed assigned review-round handoff, retained the deferred
dependency and preserved the original wording. It did not invent an approval,
erase missing information or equate a pending case with a final determination.
Semantic correctness of that actionability assessment is explicitly unverified.

## Are these results from the actual verifier?

Yes. The diagnostic ran the pinned χ-Bench runtime's own
`chi_bench.verifier.task_runtime.collect_all_verifier_checks` against a copy of
the actual saved export, with the native expected-check loader and
`include_semantic_judge=False`. It then called the native `build_scorecard`.
The official checker consumes its expectations opaquely; the actor did not see
expected answers. No custom replacement checks produced the18/18 number.

The measured structural binary and fractional rewards are both1.0. These rewards
apply only to the selected structural checks; they are not the full competition
strict score, reliability metrics, or evidence that every clinical explanation
is correct. The10 N/A checks are excluded by the native checker's applicability
rules; the semantic judge checks were intentionally not executed.

Local evidence:

- `runs/20261025-random-um-t033-18-structural-only/summary.json`
- Same directory: `scorecard.private.json` and `original-snapshot-verified.json`
- `runs/check_structural_no_judge.py` contains the exact native invocation.
- Actor `run.result.json`, `events.jsonl`, `state.snapshot.sqlite` and the
  batch's `deferred_snapshot/snapshot.manifest.json` remain ignored/private.

Original snapshot manifest SHA-256:
`144d2bd8bd5a9394e4e04e9dac5000884c352bbccaab34a6d564ce977ec6d8f5`.
The stored packet is ready for later deferred evaluation without replaying the
actor. Full clinical grading remains subject to the user's future authorization.

## Decisions and repairs made during continuation

| Failure mechanism | General repair and reason |
| --- | --- |
| Hard180s deadline interrupted active output | User-approved explicit180s silence/600s active cap, refreshed only by scoped generation deltas; keepalives cannot extend it |
| Entire workspace class rejected as clinical evidence | User-approved exact actor-listed attachment linkage with case/path/type/text/hash checks; generated drafts, unrelated files and filename guesses remain excluded |
| Tool accepted empty review despite prose claiming to save content | Report omitted collection inputs and returned empty collections; preserve the original result and let the model correct its payload |
| Unsigned MD decision accepted by runtime but failed native verification, then could not be amended | Enforce the public conditional sign-off contract before dispatch; never auto-sign or choose a medical outcome; retain unsigned P2P reservation |
| Tens of thousands of repeated zeros/question marks | Early size enforcement and4,096-character short-period repetition detection; no partial dispatch, existing single format-correction allowance |
| Windows snapshot PermissionError | Preserve/reconcile the actual world before stopping; add private OS/frame diagnostics. Exact original cause remains unknown; do not claim it was fixed |

The final trial supplied a signed decision directly and had no generation errors;
the negative guard/correction paths were verified separately by regression and
synthetic native/service tests. Do not attribute all differences between fresh
model samples solely to these repairs.

Root briefly suspected the local MD sign-off check was too strict because the
runtime accepted an unsigned request-info decision. Native verification then
failed `md.signed_off`, disproving that conclusion for this benchmark. The check
was retained and the validation moved before the one-time write. Detailed cause,
public-contract conflict and evidence are in [the -15 report](T033_15_MD_PRECOMMIT_REPAIR.md).

## Preserved development attempts

| Attempt | Actual outcome | Native structural scope |
| --- | --- | --- |
| -13 | Account limit at call2; preserved | Not evaluated in this continuation |
| -14 | Operator stopped oversized zero-generation at call49; snapshot saved |7/16 pass,9 fail,11 N/A |
| -15 | Reviews/notice performed; unsigned immutable MD decision blocked closure; operator stopped at call63 |17/18 pass,1 fail,10 N/A |
| -16 | Native turn failed during Unicode repetition at call8; snapshot manually reconciled |3/12 pass,9 fail,15 N/A |
| -17 | Account limit at call1, zero tools; snapshot saved | Not evaluated |
| -18 | Fresh actor completed normally at call34 |18/18 pass,0 fail,10 N/A |

Different reached stages change which checks are applicable. These development
revisions are not independent reliability trials or a pass@1 estimate. They all
concern the same development task and must not be counted as broader75-task
coverage. Links: [-14](T033_14_OUTPUT_AND_PAYLOAD_REPAIR.md),
[-15](T033_15_MD_PRECOMMIT_REPAIR.md), [-16](T033_16_REPETITION_AND_SNAPSHOT_RECOVERY.md),
[timeout policy](STREAMING_TIMEOUT_REPAIR.md).

## Remaining limits and next work

- Clinical/policy reasoning, plan applicability and information-request adequacy
  remain unscored without the semantic judge.
- Efficiency remains poor:2.6 million reported tokens for this one actor trial.
  The worker made additional policy searches after recording its handoff. This
  execution checkpoint does not establish that context/retrieval efficiency is
  solved.
- Current repaired source has one completed structural development-case check;
  broader PA/UM/CM and75-task performance is unmeasured.
- Native generation's underlying degeneration cause and the intermittent
  Windows permission failure remain unconfirmed. Recovery/diagnostics improve
  handling; they do not prove these underlying problems disappeared.
-658 software tests pass in80.926 seconds. All33 original `HealthHarness/`
  baseline hashes match. Software tests establish mechanics, not benchmark quality.

## Reproduce a fresh single case

The completed -18 directory is immutable evidence. Use a new directory:

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-um-t033-19 `
  --domains pa_um `
  --task-id pa_t033_t033_o001_p01_triage_payer `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```

No new actor or judge run was launched after -18 completed and its structural
checks passed. No benchmark data, credentials or private receipts were committed.
