# t033 -08: optional audit actor rejection and recovery repair

October 24, 2026. Root diagnosis/coding; Luna-high provided an initial finding
before hitting the account usage limit. Its investigation was incomplete. Root
independently verified the saved result, source contracts and validation path.

## Actual saved execution

Run: `HealthHarnessCodex/runs/20261024-random-um-t033-08`,
`pa_um/pa_t033_t033_o001_p01_triage_payer/attempt-1`.

- Actor ended `error` after 372.812 seconds, 20 completed model calls and
  43 counted tool proposals. Reported usage: 1,328,244 tokens. These are
  observed usage counts, not a dollar estimate or efficiency achievement.
- Triage, nurse criteria/recommendation and an MD request_info write have
  successful observed records. Stage guidance reached `information_handoff`.
  No helper ran and no stagnation recovery was triggered. This was a validation
  stop, not evidence of the earlier repeated-investigation loop.
- Call 20 completed normally and proposed `payer_letter_center.generate_pend`
  with `actor: "SYSTEM"`. Saved tool feedback is
  `arguments_rejected_before_dispatch`, category `identity_scope`, path `$.actor`.
  No such letter-generation call was dispatched. The prior MD service response
  already contained a generated-letter reference; generation and delivery must
  not be conflated. The owner did not deliver the notice before stopping.
- `principal_bindings` is empty and `model_failure` is null. Zero pre-dispatch
  corrections were offered. The stop did not exhaust 100 model/500 tool budgets
  and was not a response-format error, timeout or provider usage-limit failure.
- Snapshot saved 215 files and world stopped. The later Luna diagnostic agent's
  account limit is a separate event; it did not cause the saved actor failure.
  No paid judge was run and clinical correctness remains ungraded.

## Confirmed cause

`schema.py` treats an explicitly supplied `actor` as a principal identity and
requires it to match the trusted current principal. That rejected SYSTEM.
The same-case MD result exposed SYSTEM as reviewer attribution, but it did not
establish the trusted principal binding used by the harness. Reusing a string
from one output is not sufficient to create authentication/role authority.

The error was in recovery: `_has_observed_identity_for_rejection` allowed a
principal correction only when `principal_bindings` existed. It overlooked an
alternative requiring no replacement identity: **omitting an optional actor**.

The public service defines `generate_pend_letter(..., actor: str | None = None)`;
the HTTP `GenerateLetterBody` also makes it optional, and the service applies
its own audit attribution fallback. Source locations:

- `Runner/chi-bench/src/chi_bench/services/letters.py`, generate_pend_letter,
  _generate_letter and audit fallback.
- `Runner/chi-bench/src/chi_bench/server/routers/models.py`, GenerateLetterBody.
- `HealthHarnessCodex/health_harness_codex/engine.py`, pre-dispatch rejection and
  bounded correction path.

The historical evaluation classified this generic harness error as
`inference_failure`; that label alone does not prove a provider/model failure.
The concrete rejection and completed model event establish this cause.

## Implemented correction

The original identity validation remains unchanged. A new narrow recovery check
handles a rejected top-level `actor` by testing a copy with that field omitted.
The **entire remaining proposal** must pass the actual tool schema, explicit
identity_fields and normal isolation validation before omission can be offered.
The worker gets one bounded correction to the same tool, explicitly instructing
it to omit actor rather than guess another identity or send null.

The code neither dispatches the rejected proposal nor rewrites the model's
arguments automatically. It adds no SYSTEM allowlist, accepts no arbitrary
principal, changes no patient scope, and preserves stable action IDs. Required
actor fields, conditional requirements and other identity/schema violations
remain rejected. Another bad proposal stops after the existing correction cap.

## Verification

- Four new offline regression tests pass: optional actor correction executes
  once, explicit/conditional required identities cannot be omitted, other scope
  or schema errors cannot be masked, and repeated bad actors stop boundedly.
- Full **600 tests pass in 82.310 seconds**. Local receipt:
  `HealthHarnessCodex/runs/20261024-optional-actor-regression.log`.
- Initial new-test failures were test scaffolding: CaseStore requires closing()
  rather than a context-manager protocol; corrected calls retain the original
  stable action evidence ID. Those tests were corrected before final acceptance.
- No fresh dataset actor, real-model check or paid judge ran during this repair.
  The real-model path is unverified after the account limit. A subsequent
  single-case execution is still required to observe actual model correction.

Preserve -08. Next fresh run directory: `runs/20261024-random-um-t033-09`.
Use the same explicit single-case command documented in
[the stage repair](UM_ASSIGNMENT_STAGE_REPAIR.md), replacing -08 with -09.
Wait for usable Codex account capacity before launching inference. Grading
remains deferred; no benchmark-success claim follows from software tests.
