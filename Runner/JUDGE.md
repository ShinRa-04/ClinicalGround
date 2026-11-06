# Running one official judge — October 21, 2026

The user requested the command before each paid judge run and a cost estimate.
Show the actual container/task/output directory for each invocation. Do not
paste keys into chat or include key values in shell commands or tracked files.

## Current provider choice and integration boundary

The user selected OpenRouter Batch for judge inference. OpenRouter currently
lists `anthropic/claude-opus-4.7:batch` at **$2.50/M input and $12.50/M output**:
[model pricing](https://openrouter.ai/anthropic/claude-opus-4.7:batch).
Its [Batch API documentation](https://github.com/OpenRouterTeam/docs/blob/main/batch-quickstart.mdx)
describes asynchronous submission and result retrieval with a 24-hour window.

**Live testing status:** an experimental Batch adapter and bounded tool runner
are implemented with 14 focused offline tests. All five controlled Opus 4.7
submissions were rejected by OpenRouter with HTTP 400 before a batch ID or model
response, despite the Batch endpoint appearing in its public catalog. Final
authenticated key check reports **$0.00 used / $0.50 remaining**. No real judge
verdict was obtained. See [full test evidence](../Progress/DEFERRED_JUDGING.md).

This remains **an unverified live judge connection**. The pinned
official `claude_runner.py` explicitly removes `ANTHROPIC_BASE_URL` and runs the
judge through the direct Anthropic endpoint. An OpenRouter key cannot simply
replace the Anthropic key in the command below. No OpenRouter judge call has
been made; an adapter preserving the tool-driven judge session would require
live verification. Acceptance of that alternate transport for
official competition scores is not established. Keep the original judge and
its direct command intact; do not silently route or relabel alternate scores.

At the quoted uncached token rates, the same hypothetical sessions cost:

| Total input | Total output | OpenRouter Batch token cost |
|---:|---:|---:|
| 20,000 | 2,000 | $0.075 |
| 50,000 | 5,000 | $0.1875 |
| 100,000 | 10,000 | $0.375 |

The middle scenario is $14.06 for 75 case evaluations, judge tokens only.
These are calculations, not measured workloads or spending caps; caching,
extra turns, reasoning, retries and other applicable charges can change them.

The judge normally runs **after the actor finishes**. It needs the preserved
final workspace/environment, not a simultaneously active Codex worker. Our
manual live-world command below requires the original trial container to remain
running after the actor stops. Restarting it resets the world. The new default
batch CLI instead saves final-state snapshots before stopping worlds; its
offline verifier replay passed a real Docker transport check with model calls
disabled. Use the [deferred grading commands](../Progress/DEFERRED_JUDGING.md)
for that workflow. No paid late judge has yet completed.

## Set the key locally

From PowerShell:

```powershell
notepad C:\Projects\BigData\Runner\.env
```

Set `ANTHROPIC_API_KEY` in that ignored file, without quotes or inline comments.
Do not change the Codex agent's model connection. The key is for benchmark-owned
inference, including the official judge; patient/P2P models may need their own
configured provider access separately.

## Direct Anthropic judge only, after the agent stops

This template requires the SAME still-running owned trial world, with outbound
network access. Do not restart a stopped trial: that resets the benchmark state.
Use a new output directory each time; do not overwrite an earlier grade.
The assistant will supply the actual container and task values before a run.

```powershell
$judgeContainer = 'RUNNING_TRIAL_CONTAINER'
$judgeTask = 'PUBLIC_TASK_ID'
$judgeOutput = '/logs/manual_judge_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss')

docker exec --env-file C:\Projects\BigData\Runner\.env `
  --env CHI_BENCH_JUDGE_MODEL=claude-opus-4-7 `
  --env CHI_BENCH_JUDGE_NUM_VOTES=1 `
  $judgeContainer /workspace/.venv/bin/python -m chi_bench.verifier.task_runtime verify `
  --expectations-path "/opt/chi-bench/tasks/$judgeTask/fixtures/expectations.json" `
  --verifier-host 127.0.0.1 --verifier-port 8023 `
  --reward-path "$judgeOutput/reward.json" `
  --scorecard-path "$judgeOutput/scorecard.json" `
  --exported-state-path "$judgeOutput/exported_state.json" `
  --verifier-context-path "$judgeOutput/verifier_context.json"
```

Passing the baked fixture PATH to the unchanged grader is permitted; do not
open its contents or provide it to the acting model. A fresh actor world can
be started with the existing batch runner's explicit `--benchmark-env-file
C:/Projects/BigData/Runner/.env --allow-benchmark-network` options. That batch
command executes the agent AND judge; the command above executes only grading.
No paid judge was invoked while preparing these instructions. Current earlier
trial worlds are stopped, so their names must not be substituted into this
template as if their original live state were still present.

## Cost estimate, not measured usage

Anthropic's standard direct API list price for Claude Opus 4.7 was checked on
October 21: **$5 per million uncached input tokens, $25 per million output
tokens**. The following are calculated scenarios for one total judge session,
not observed token volumes or guaranteed limits:

| Total input tokens | Total output tokens | Calculated standard cost |
|---:|---:|---:|
| 20,000 | 2,000 | $0.15 |
| 50,000 | 5,000 | $0.375 |
| 100,000 | 10,000 | $0.75 |

Formula: `(input_tokens * 5 + output_tokens * 25) / 1,000,000` USD.
At the middle scenario, 75 one-vote case evaluations would be about **$28.13**
for the judge alone. The benchmark documentation's own rough estimate is
$0.05–$0.30 per trial; it has not been measured for this harness. Tool-driven
turns, reasoning output, retries and cache-write/read pricing can change the
bill. The pinned runner allows large outputs, so these examples are not a
spending cap. Extra votes or repeated grading cost more. Deterministic tasks
that never invoke an LLM judge have no judge model-token charge.

Sources: [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[official judge documentation](https://github.com/actava-ai/chi-bench/blob/main/docs/judge.md).
No paid judge usage has been measured yet. Capture the Claude CLI's actual
reported usage/cost after the first authenticated evaluation before treating
any per-case estimate as representative of all tasks.
