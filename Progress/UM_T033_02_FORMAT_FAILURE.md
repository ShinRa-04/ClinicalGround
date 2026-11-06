# UM t033 second October 24 attempt: format failure

Inspected user-run `HealthHarnessCodex/runs/20261024-random-um-t033-02`.
No actor rerun or paid judge was launched during inspection.

## Execution evidence

- Local status `error`, classification `inference_failure`.
- Six model requests: calls 1, 2, 4 and 5 returned parsed responses; calls 3
  and 6 raised `ModelResponseFormatError` at `arguments_json` parsing.
- Call 3 consumed the single format correction; call 4 succeeded. Call 6
  encountered the same parser category and ended the attempt because the
  correction allowance was already used. This allowance is shared across
  response format, final format and pre-dispatch validation corrections.
- 19 counted tool proposals; 16 completed journal entries, plus local tool
  activity. These counts are different measures, not 19 clinical actions.
- Reported aggregate usage: 297904 input, 5709 output, 303613 total tokens.
  Cached input is a subset of reported input, not an additional amount.
- Both failed native turns completed normally, with process cleanup confirmed:
  call 3 took 11.844 seconds; call 6 took 19.265 seconds. Neither timed out.
- No context-character, 2 MiB request-byte, model-call or tool-call cap caused
  this stop. The attempt had 100 model calls available and stopped at 6.
- Snapshot saved: 213 files; batch reports its world stopped.

## Confirmed mechanism and limits

`codex_provider.py::_parse_reply` first parses the outer response, then calls
`json.loads` on every tool call's `arguments_json` string. Both errors arose
in this second parse. The outer output schema constrains that field as a
string, not as the actual tool-specific argument object. Outer schema validity
therefore does not establish valid embedded JSON.

`engine.py` currently permits one correction across the whole workflow, rather
than a new bounded correction opportunity after later successful progress.
This explains why the second malformed proposal was fatal despite remaining
execution budget. It does not establish that unlimited retries are appropriate.

The malformed raw reply is not retained in these artifacts. The exact syntax
error, affected proposed tool and reason the model generated it cannot be
reconstructed. Do not invent a missing quote, truncation or context-size cause.
No proposal from either unparsable response was dispatched by the provider.

## Native snapshot diagnostic

Ran the existing native verifier against a copy of the frozen exported state,
with networking disabled and no credentials supplied. Original snapshot
integrity was verified before and after; diagnostic container removed.

Evidence: `HealthHarnessCodex/runs/20261024-um-t033-02-native-diagnostic/`.

- 3 applicable checks passed, 9 failed; diagnostic binary reward 0.
- Failures: `md.decision_exists`, `md.audit`, `nurse.reviews_exist`,
  `nurse.recommendation_exists`, `nurse.audit`, `outcome.target_status`,
  `outcome.letter_types`, `triage.record_exists`, `triage.audit`.
- Full grading status remains `ungraded`: `official_judge_unavailable`.
  These are partial structural diagnostics, not a complete official score.
- The run is operationally incomplete; it did not reach a verified task endpoint.

## Next design decision

Repair the generic model-to-tool argument contract and bounded format recovery.
Avoid guessing or repairing clinical argument values. Preserve validation and
ensure invalid proposals execute nothing. Discuss replacing the repeated
assistant-chosen nested-string/recovery design before imposing another rule.
Context management remains separate pending work.
