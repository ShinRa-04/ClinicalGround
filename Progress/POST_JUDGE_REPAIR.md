# Completion, retrieval and reporting repair — October 22

The user asked to defer context-management work, fix the other problems, and
ask for explanation instructions before explaining the harness. Root owns the
coding; no delegated agents. Do not start another whole-dataset batch or spend
beyond the existing cumulative $0.50 judge authorization ($0.44215 already used).

## Changes

- Ordinary provider Clinical Intake contracts no longer accept
  `provider_record_ready_for_submission` as completion. It remains supported
  only when the public task explicitly assigns preparation/readiness alone.
  Legitimate no-authorization and evidence-gathering dispositions remain
  available; the repair does not force submission regardless of policy.
- Generic provider instructions and early-stop recovery now distinguish
  readiness from actual authorization submission and packet readback. No
  task-ID-specific answer or hidden expected status is inserted into the actor.
- Workspace reads resolve `CASE-ID/shared/...` and `shared/...` paths using
  only the bound case's explicitly allowed directories. Writes retain private
  workspace semantics. Cross-case and protected-root restrictions remain.
- Missing-file/access-denied results identify already-approved read roots and
  advise listing those directories or reading the exact approved reference.
  A permitted reference file does not grant access to its parent directory.
- RecordingTools now logs a plain `error` response as an error, consistently
  with the engine evidence ledger; normal transport return is not evidence of
  successful retrieval.
- The normal deferred-grading CLI exposes `--budget-mode key-limit`; with
  `--judge-transport openrouter --max-budget-usd 0.50`, this uses the verified
  non-resetting provider-side key cap used in the completed judge continuation.
  The default conservative reservation mode remains available. No paid call
  was made to test the CLI change.

## Verification

- Full integrated suite: **419 tests passed in 49.006s**.
- After adding the judge CLI option, its focused runner/deferred-grader suite:
  **14 tests passed in 2.201s**.
- Replaying only the new completion validator against both saved t012 evidence
  sets rejects their previous readiness-only completion. Both source result
  hashes remain unchanged. Body-free receipt:
  `HealthHarnessCodex/runs/20261022-completion-retrieval-replay.json`.
- Regressions preserve explicitly preparation-only tasks, require real
  submission for referral completion, resolve bound-case shared paths, block
  cross-case paths, and distinguish application errors from transport return.

## Fresh executed verification

At source `9fd27cd`, fresh isolated t012 finished at 15:51:01 IST. It made
**19 model calls / 57 engine operations**, actually called
`auth.submit_authorization` once, and read back **`submitted` with one
SubmissionPacket** and complete required fields. The gate accepted
`provider_packet_submitted`. There were no model errors, unknown actions,
active obligations or deferred obligations. One premature action was refused
until its required fresh case read was obtained.

One actor response was an application failure: an attempted workspace directory
listing before actual case binding was denied. The response listed only the
already-approved roots and the actor continued through permitted tools. This
is an enforced boundary, not a reason to grant the parent workspace or another
patient's files. The new case-relative path regression passes, but this native
attempt alone does not establish every possible document format is supported.

The finished snapshot passed the same integrity validation and its world was
stopped. A separate disposable, **network-disabled, key-free** verifier replay
ran with semantic judging explicitly disabled. It resolved all **9 deterministic
checks: 8 pass / 0 fail / 1 not applicable**. In particular,
`new_referral.case_status` now passes. All seven new-referral checks and the
forward-transition check passed. The original snapshot still passed hash
verification afterward; the temporary diagnostic container was removed.

Private evidence is under
`HealthHarnessCodex/runs/20261022-post-judge-repair-t012-01/`:
`verification.receipt.json`, immutable deferred snapshot, and
`deterministic-diagnostic/receipt.json`. The key-free diagnostic script is
`check_deterministic.py`; it cannot be called a new full judge evaluation or
official score. Today's previous full semantic evaluation remains a separate
failed trial; its passing semantic checks must not be copied into this attempt.
No paid provider-key call occurred in this repair. Existing judge spending
remains $0.44215 under the user's $0.50 cumulative cap.

All 33 original HealthHarness baseline hashes still match. Final inspection
found zero currently paused worlds: the six previously paused containers now
report `Exited (255)` approximately 33 minutes before inspection. No operation
in this repair restarted or unpaused those worlds; the cause of their state
change is unconfirmed. Preserve the containers and recorded attempt evidence;
do not restart them or replay their journals. Context efficiency remains
deliberately untouched. Full
multi-case performance and the new trial's semantic correctness are unverified.

## Next user interaction

The user asked to provide instructions before a harness explanation. A question
was sent asking for their preferred structure and technical depth. Wait for that
answer before explaining. State actual implemented behavior separately from
unvalidated design ambitions and outstanding context-management work.
