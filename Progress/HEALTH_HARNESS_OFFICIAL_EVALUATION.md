# Official local evaluation — October 20, 2026

Read [measured fixed-version pilots](HEALTH_HARNESS_PILOT_RESULTS.md) for current scores, failures and active execution. This page describes the official grading boundary and reproducible procedure. No PR or public submission is authorized.

## What actually supplies a score

The user authorized local official grading after the original operational demonstration. The unchanged pinned runtime verifier evaluates the actor's settled final world. Binary reward 1 requires every applicable check to pass. Diagnostic fractional reward, model completion, finalized approval, valid evidence IDs and passing software tests are different claims.

The original `20261020-um-roles-autonomous/attempt-1` reached functional completion but officially scored **0/1, 19/21 checks**. `triage.disposition_matches` and `triage.route_matches` failed. The subsequent generic policy-clarification run also scored 0/1, 19/21. Those separate development runs cannot be pooled as a reliability batch. The later fixed-version three-trial batches are fully retained in the pilot report, including genuine 21/21 passes and failures.

This pinned fixture emits deterministic checks without `judge.*` checks and has completed without an API key or external judge inference. The earlier blanket request for an Anthropic key was premature for this case. The [published standard submission process](https://www.actava.ai/benchmarks/submit) describes a broader workspace-judge pipeline with Anthropic authentication. Account-backed Codex actor inference supplies neither those credentials nor a substitute judge. Check actual task/verifier requirements rather than generalizing this key-free observation to every domain.

A leaderboard PR publishes an already evaluated packet. It requires result/reward/scorecard, compressed trajectories, manifest and provenance; CI validation is not a replacement for executing and grading the benchmark. The standalone Codex route has not produced or validated a Harbor-compatible submission packet. No packet, PR or leaderboard result is claimed.

## Exact procedure

1. Create an independent fresh owned runtime world from the pinned image, with network disabled, no published ports or provider keys. Bind only this task's public `instruction.md` and actual actor observations; never inspect its fixture/test/solution contents.
2. Freeze actor source/model/budgets and run the original task through the native Codex adapter. Preserve every outcome, including errors and blocked runs. Do not insert task-specific hints or manually supplied case identifiers.
3. Wait for the actor process to settle. Do not stop/restart the world before grading: the runtime resets on restart. Invoke the unchanged official module below using the baked fixture path as an opaque grader input.
4. Preserve raw official files in a NEW verifier directory outside acting read roots. If the upstream export times out before creating a scorecard, retain the log and retry read-only grading into another fresh output directory. Never rerun the actor or replace a completed scorecard to obtain a better result.
5. Check emitted binary reward, native checks/N/A counts and judge availability. Write a separate receipt hashing all official artifacts and recording actor commit/runtime image. Keep original operational recorder files unchanged. Back up SQLite read-only and verify integrity, then stop the owned world.
6. For a pilot, repeat in exactly three independent worlds under the same frozen configuration, then aggregate. Keep different versions separate. Full benchmark performance requires substantially more than this one development task.

```text
docker exec <owned-container> python -m chi_bench.verifier.task_runtime verify
  --expectations-path /opt/chi-bench/tasks/pa_t012_t012_o001_p01_triage_payer/fixtures/expectations.json
  --verifier-host 127.0.0.1 --verifier-port 8023
  --reward-path /logs/verifier_official_attempt_1/reward.json
  --scorecard-path /logs/verifier_official_attempt_1/scorecard.json
  --exported-state-path /logs/verifier_official_attempt_1/exported_state.json
  --verifier-context-path /logs/verifier_official_attempt_1/verifier_context.json
```

The default `/fixtures/expectations.json` alias was absent in this image; supplying the standard baked path resolved that launch failure. The upstream state-export request has a five-second timeout and occasionally needed a read-only retry. An exit code alone cannot distinguish failed grading startup from binary reward 0: inspect whether complete official artifacts exist. No fixture/solution/hidden expectation content is opened by the operator or fed to the actor. The grader consumes its own fixture; operator receipt parsing reads only judge availability from its generated context.

## Metrics and accounting

For one task's three trials: pass@1 is successes/3, pass@3 is 1 if any trial passes, and pass^3 is 1 only if all three pass. Thus 1,1,0 gives 66.7%, 100%, 0%. These are one-task pilot observations, not benchmark-wide estimates or clinical certification. Use independent held-out tasks to evaluate generalization after development.

The reusable operator aggregator is `HealthHarnessCodex/evaluations/aggregate_official_pilot.py`; see [evaluation guide](../HealthHarnessCodex/EVALUATION.md) for inputs and CLI. It verifies comparable settled trials, artifact hashes, binary/check consistency, native N/A accounting and judge availability, then writes new timestamped reports. It rejects incomplete grading rather than inventing a failure or pass. Remote dispatch attempts, local refusals, engine operations, model calls, elapsed time and actually supplied usage are distinct. Cost is unknown. Receipts are local integrity records, not independent third-party attestations.

All protected material and outputs remain ignored under `HealthHarnessCodex/runs/`; only source/tests and sanitized documentation are committed. The original HealthHarness, official grader and hidden fixtures remain unchanged. The latest original-harness check matched all 33 baseline hashes.
