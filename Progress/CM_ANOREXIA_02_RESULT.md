# CM test -02 result — October 25, 2026

**The test did not complete successfully. It ended blocked on an uncertain
outreach-message write. Native structural verifier:2/6 applicable pass,4 fail,
8 N/A. No semantic judge was run. Work stopped after this test as requested.**

## Actual execution

- Single selected task: `cm_anorexia_hard_refuses_001`.
- Run: `HealthHarnessCodex/runs/20261025-random-cm-anorexia-02/`.
- Frozen source: `aa7e6c8`; GPT-6 Luna/high; helpers enabled; Codex patient simulator.
- Workflow:15 model calls,17 harness-counted tool operations.
- Model-response errors/format retries:0. This does not prove the assessment
  stage completed: this trial remained in outreach when it stopped.
- Patient simulator:7 submitted/7 completed,0 failed/unknown, settled.
- Workflow reported usage:720,588 total tokens (711,329 input/9,259 output;
  265,984 cached input included;5,831 reasoning-output detail). Patient-simulator
  usage is separate and is not included in this workflow subtotal.
- Actor duration211.7s; total world duration257.4s.
- Snapshot:6 files, integrity verified, container stopped. This CM snapshot has
  no generated workspace artifacts; file count is not a completion score.

## Exact stopping mechanism

Workflow call15 proposed `cm_outreach.send_message`. The MCP tool layer returned
`MCPToolError`. Its current error text withholds the underlying service details:
`MCP tool reported an error; outcome details were withheld`.

The action journal therefore records the write outcome as unknown, and the
controller blocks further execution rather than replaying a possibly executed
message. The stop is consistent with the existing transactional safety rule.
The precise service-side cause is **not confirmed**. Do not label it a model
output limit, simulator quota, consent decision, conversation-turn limit or
network timeout without additional evidence. No blind retry/reconciliation
write was performed after the user's stop instruction.

The batch's `deferred_ready` means the failed trial's saved export is available
for later evaluation; it does not mean the healthcare workflow succeeded.
Its final `failed=0` counter concerns batch scheduling/snapshot failures and is
not a count of successful actors. The actor itself is blocked. The console's
actor-end unknown label does not override the saved blocked result.

## Native key-free verification

The pinned χ-Bench native verifier ran against a copy of the actual saved export,
with semantic judging disabled and network off. Original snapshot integrity
was rechecked. Passed2/6 applicable, failed4,8 N/A; structural binary0 and
fractional1/3. These are not full competition scores.

Failed checks:

- `cm.assessment.record_exists`
- `cm.care_plan.record_exists`
- `cm.cross_stage.target_status`
- `cm.cross_stage.audit_actions`

Those stages/effects were not reached. Their failure does not independently
establish which clinical disposition was appropriate. The experimental Codex
patient simulator also limits comparability with official simulator trials.

Local evidence remains ignored/private:

- Actor `run.result.json`, `events.jsonl`, `state.snapshot.sqlite` and batch manifest.
- `runs/20261025-random-cm-anorexia-02-structural-only/summary.json` and
  `original-snapshot-verified.json`.
- Snapshot manifest SHA-256:
  `18f51ff8a7138881a67396c39bf35d4f15f69a60077fe232e9374e105b1e1df6`.

## Repairs completed before this test

[Full diagnosis/research and actual command](CM_NATIVE_OUTPUT_COMPATIBILITY_REPAIR.md).
Native oneOf-to-anyOf decoding compatibility, original exclusive execution
validation, discriminator/date support, exact output-limit classification and
up to3 additional budgeted generation requests were implemented and tested.
669 regression tests passed/76.945s. Controlled native replays and four synthetic
assessment payloads passed, with no actual clinical tool operations.

The failed -01 model-output reproduction was corrected in those diagnostics.
This -02 trial had no model-output errors but stopped on a different tool error
before reaching the assessment stage. Do not call the whole CM workflow fixed.
No further case, judge, software change or research was started after this test.
