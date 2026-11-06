# UM t033 -03 stop, confirmed cause and parameter repair

October 24, 2026. The user requested stopping the live run and investigating,
then selected rejection of undeclared top-level tool parameter names.

## Stop and preservation actually executed

- Terminated the verified batch PID 20644 and its owned child PIDs 21988/16656.
  Confirmed those processes absent and exact owned Docker world stopped.
- Run: `HealthHarnessCodex/runs/20261024-random-um-t033-03`.
- Stop counts: 80 completed model calls, 140 counted tool proposals,
  **4,920,350 reported tokens**; no model-format errors.
- Preserved actual verifier `/export`, SQLite backup, published save-tool schemas,
  actor container logs and original manifest under the attempt's
  `operator_stop_capture/`. Verified all 211 initially captured file hashes.
- Batch manifest now records operator-requested interruption, not completion or
  grading. The preserved SQLite retains the original interrupted `running`
  status. No manufactured normal actor result or official deferred-ready packet.
- One pending nurse-review readback remains in the journal, labeled write by
  the existing tool classification. It was not replayed or silently cleared.
  The original world remains stopped and preserved; do not resume this attempt
  under changed source.

## Confirmed failure chain

All 14 journaled nurse-criteria save actions omitted the declared `evaluations`
parameter. They instead supplied undeclared names such as `evaluations_defer`,
`evaluations data` or a spelling ending with a curly quotation mark. These were
syntactically valid JSON keys, so eliminating double-encoded JSON alone could
not catch them.

The published tool schema declared `evaluations` optional and did not explicitly
forbid additional top-level fields. Our validator followed JSON Schema's open
default. The benchmark's MCP argument model silently ignored unknown fields;
the service received the default absent list and saved an empty evaluation list.
The worker noticed the empty result but kept changing invalid parameter names
and retrying. More document retrieval could not make those requests persist
criteria.

Reproduced against the pinned benchmark runtime, using the actual public
`ReviewService` and MCP SDK, with a synthetic in-memory context, no network,
credentials, hidden fixture or real patient data:

- `evaluations_defer` -> zero criteria saved.
- `evaluations` -> one synthetic criterion saved.

Receipt/source: `HealthHarnessCodex/runs/20261024-named-parameters-native-reproduction-02/`.
The first diagnostic used the wrong SDK import path and is preserved separately;
it did not exercise the service.

## Implemented general correction

- Added an explicit **tool-parameter adapter rule**, approved by the user:
  when a tool declares named root properties and omits `additionalProperties`,
  its root parameter map is treated as closed. This is intentionally stricter
  than JSON Schema's default, not a claim that the original schema forbade extras.
- Codex prompt schema, per-tool decoding schema, HTTP model-provider schema and
  pre-dispatch validation use the same parameter policy. Published source
  dictionaries are not mutated. Root local references are handled as well.
- Unknown top-level names fail before tool dispatch. Structured correction
  feedback gives the valid declared names without echoing the unknown key or
  patient-derived values. The model chooses and supplies the correction; code
  does not rename keys or infer evaluation contents.
- Explicitly open `additionalProperties: true`/typed maps, unstructured maps and
  nested data maps retain their intended behavior. Optional parameters remain
  optional; the rule does not invent a requirement to fill every field.
- Existing bounded correction, stable journal IDs, identity/provenance checks,
  call budgets and uncertain-write protections remain active.

## Verification actually executed

- **542 tests pass / 49.914 seconds**:
  `HealthHarnessCodex/runs/20261024-named-parameters-tests.log`.
- New regression tests cover misspelled parameter names including spaces/Unicode,
  safe valid-name feedback, nested/explicit open maps, optional values,
  non-mutating decoder projection, referenced roots and correction before first
  dispatch with exactly one saved evaluation/tool execution.
- Read-only retrospective check: **14/14** preserved invalid save proposals are
  rejected by the new validator before dispatch. No original action was replayed.
- Actual Luna-high proposal using the published UM save schema plus all internal
  tool specs produced the correct parameter names and one evaluation, passing
  validation. No real tool executed. Reported tokens: 11742. Receipt:
  `HealthHarnessCodex/runs/20261024-named-parameters-final-luna-smoke.json`.
- Final real-Luna synthetic engine test injected an invalid parameter proposal;
  engine rejected it, supplied valid names, Luna corrected it, and the in-memory
  tool saved one evaluation exactly once. Verified synthetic completion in three
  counted calls: one injected proposal plus two actual native calls; one schema
  correction; 38716 reported tokens. Receipt/script:
  `HealthHarnessCodex/runs/20261024-named-parameters-final-engine-smoke.json` and `.py`.

No new dataset actor or paid judge was launched. These checks establish the
specific protocol/validation fix, not UM clinical performance or benchmark
success. Broader repeated-retrieval and context-management work remains pending;
no blanket progress-stop rule or task-specific clinical outcome was imposed.

Next fresh single-case directory, checked unused:
`HealthHarnessCodex/runs/20261024-random-um-t033-04`.
