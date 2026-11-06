# Codex argument format and recovery repair — October 24

Implemented in `HealthHarnessCodex/`; original `HealthHarness/` unchanged.
This repairs the general failure mechanism observed in the second UM t033
attempt. No task-specific answer, expected disposition or hidden fixture was used.

## Implementation

- Codex proposals now contain `arguments` as a JSON object. Removed the inner
  `json.loads(arguments_json)` operation and the request to double-encode JSON.
- `codex_provider._reply_schema` supplies a separate branch for each permitted
  tool, pairing its name with its argument schema. Optional fields remain
  optional. Nested data, booleans, nulls, arrays, escaping and local schema
  references retain their meaning. Unknown tools and malformed proposals still
  fail before any proposal is returned for dispatch; no partial sibling dispatch.
- One decoder compatibility exception: `uniqueItems` is omitted from the
  decoding projection. Full native catalog probes repeatedly failed with it
  and passed without it. Original schemas are unchanged in the request and
  engine; duplicate array values are still rejected before dispatch. No other
  validation constraints were removed. Literal data and property names such as
  `uniqueItems` are preserved rather than mistaken for schema keywords.
- Format-correction instructions now request argument objects.
- The shared correction allowance renews after a **new successful external
  tool observation**. A successful parse, failed tool response or journal replay
  alone does not renew it. Consecutive format errors without such progress still
  stop after one correction. Existing model/tool budgets still bound all work.
  Lifetime retry counters and failed-call usage remain intact for auditing.
- Unknown write outcomes still require reconciliation; no automatic replay or
  guessed JSON/clinical-value repair was added. Case isolation, identity checks,
  policy provenance checks, fencing and completion verification remain active.

## Verification actually executed

- Final full software suite: **535 tests pass / 49.439 seconds**.
  Receipt: `HealthHarnessCodex/runs/20261024-direct-arguments-verified-tests.log`.
- Regression coverage: later malformed response after a successful write can
  recover; exactly one write executes; consecutive failures stop; failed tool
  responses do not renew correction; model budget still stops recovery; nested
  argument values survive; schemas pair tool names correctly; optional fields,
  references and literal data survive; source uniqueness validation still rejects
  duplicates; a bad sibling returns no partial proposal.
- Real Luna-high protocol checks used existing Codex sign-in, synthetic data
  and no external tool effects. Final catalog checks included all 14 internal
  tool specifications plus two synthetic specifications. Both a read proposal
  and a nested update proposal parsed and passed original schema validation.
  Reported tokens: 10712 and 10761. Receipt:
  `HealthHarnessCodex/runs/20261024-direct-arguments-final-catalog-smoke.json`.
- Final-source end-to-end synthetic engine check: injected format failures on
  calls 1 and 3, with a real Luna-generated successful in-memory update between
  them; calls 2 and 4 used actual Luna-high inference. Result **complete**,
  4 counted calls, 2 format corrections, exactly 1 tool execution, verified
  synthetic completion endpoint; 28078 reported tokens. Receipt and reproducible
  ignored script:
  `HealthHarnessCodex/runs/20261024-direct-arguments-final-engine-smoke.json`
  and adjacent `.py`.
- Earlier native compatibility probes, failed prototype checks and the earlier
  full-suite test with an incorrect expected exception-message pattern remain
  separately preserved. They are not pooled into a benchmark reliability claim.

## Remaining scope

No fresh dataset attempt or paid semantic judge was launched. UM t033's previous
failed snapshot and result are unchanged; it still needs a fresh attempt under
the new frozen source to establish task performance. This is an executed protocol
and recovery repair, not an assertion that all healthcare workflows now pass.

Context management remains pending. Tool-specific decoding schemas add schema
payload, and no reduction in model-token usage is claimed. The temporary disabled
working-context cap, separate 2 MiB request guard, timeouts and upstream limits
were not changed by this repair. Future schema deduplication must preserve the
full original validation contract rather than silently remove constraints.

Next single-task rerun directory checked unused:
`HealthHarnessCodex/runs/20261024-random-um-t033-03`.
Do not reuse the source-frozen failed `-02` attempt.
