# Judge API input and output: separate from Codex actor context

See the [glossary](GLOSSARY.md#8-evaluation-and-results) for verifier, judge,
rubric, verdict and evaluation-status terminology.

Measured from the completed t012 evaluation's saved OpenRouter Opus 4.7 requests.
No additional paid API call was made for this analysis. The actor's 1.27-million
input-token figure is a different execution scope and must not be attributed to
this judge session.

## Actual requests

| Request | Input tokens | Output tokens | Cost | Work performed |
| --- | ---: | ---: | ---: | --- |
| 1 | 4,339 | 122 | $0.024745 | Requested rubric and canonical-case files |
| 2 | 7,699 | 83 | $0.040570 | Requested the actor's stage-output file |
| 3 | 33,213 | 1,484 | $0.203165 | Wrote the two rubric verdicts with explanations and evidence references |
| 4 | 34,719 | 3 | $0.173670 | Finished the conversation after the verdict file was already written |
| **Total** | **79,970** | **1,692** | **$0.442150** | Completed evaluation |

At the actual $5/M input and $25/M output rates, input cost was **$0.399850**
(90.43%) and output cost **$0.042300** (9.57%). Reported cached input was zero
for these four requests. No separate reasoning tokens were reported.

These are actual response usage/cost records, including the first two requests
from the interrupted invocation and the two requests from its continuation.
They are not two independent judge sessions added together.

## Where input growth came from

The first prompt was 8,781 characters. The judge's five file-tool definitions
occupied about 1,592 JSON characters under the audit's serialization.
Both remained present in subsequent requests.

Reading the rubric file added 1,841 characters; reading the canonical record
added 7,021. The actor stage-output file then added **57,778 characters**.
HTTP request bodies grew from 10,674 to 20,770 to 83,257 to 87,562 UTF-8 bytes.

The normal chat API expects the conversation history on subsequent calls, so
read tool outputs are replayed. The last request therefore sent the large
evidence file again, together with the written verdict and the tool receipt,
despite having no remaining evaluation work.

The case-output file is benchmark-generated judge evidence. Large size alone
does not prove its contents are unnecessary. Pruning clinical/evaluation fields
could change what the judge can assess. No such pruning was performed here.
The actor's exact duplicated MCP text/structured-result problem should not be
assumed to exist in the same form in this judge workspace.

## Were the API answers bloated?

The first two outputs were short file-read requests. The substantial third
output contained a 3,633-character Write-tool argument with the verdict file
and a 62-character accompanying message. It used 1,484 output tokens to record
two rubric judgments, explanations and evidence references.

This audit does not establish that those explanations should be shortened.
They are the actual evaluation product and support review of the verdict.
Output length was not the dominant cost.

The waste was the **fourth request**: 34,719 input tokens were processed to
produce only 3 output tokens after the useful verdict file already existed.

## Implemented correction

The runner now stops after a successful Write/Edit of `verdicts.json` when all
expected rubric IDs have typed verdicts, explanations and reference lists.
The benchmark's own verdict parser remains authoritative. Partial files,
malformed verdicts, unrelated file writes and failed tool operations do not
trigger early completion. Valid failure verdicts also terminate correctly;
this is not a stop-only-when-passing shortcut.

A durable completion checkpoint records the verdict hash. Re-entering the same
unchanged completed session sends no extra request. A changed verdict is rejected
instead of automatically starting more paid work.

A network-free replay of the actual saved responses now uses **3 POST-shaped
steps instead of 4**, and writes a **semantically identical verdict file**.
On that preserved sequence, the omitted request originally cost **$0.173670**,
or **39.28% of the session's cost**. This is a saved-response replay measurement,
not a newly billed live-session saving. No money was spent by the replay.

The next live judge evaluation should measure its own cost rather than assume
every case will save the same amount. The existing cumulative $0.50 authorization
has not been expanded.

## Relationship to the eleven scorecard checks

The final scorecard contained nine deterministic checks and two semantic
WorkspaceJudge checks. The Opus session supplied the two semantic verdicts;
it did not independently generate all eleven checks. The failed case-status
check was deterministic. The model verdicts passed, but the combined strict
reward was zero because the case status failed.

Sources: saved request/cost receipts under ignored
`HealthHarnessCodex/runs/20261022-single-case-judged-01/late_grades/judge-continuation-c2c5bb39/`,
[`openrouter_judge.py`](../HealthHarnessCodex/health_harness_codex/openrouter_judge.py),
and [benchmark WorkspaceJudge](../Runner/chi-bench/src/chi_bench/verifier/judge/workspace_judge.py).
