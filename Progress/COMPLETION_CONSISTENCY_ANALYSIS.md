# Completion processing: competing authorities and incomplete handoff integration

The later [completion repair](COMPLETION_REPAIR.md) implements and verifies the
general correction. The analysis below preserves the pre-repair diagnosis.

October 24, 2026. This is a verified code-path diagnosis and proposed general
repair, not an implemented behavior change. No actor or paid judge was run.

## Verified processing path

1. Before each owner call, `assignment.completion_audit` checks the pinned
   branch requirements against successful scoped evidence. The working context
   also includes model-created obligations and current-stage guidance.
2. The final reply uses a single complete/incomplete field. In
   `engine.Harness._accept_final`, any non-complete reply returns unresolved
   **before** executing the final completion validator. The assignment audit
   may already accept a handoff, but that result does not reconcile this exit.
3. The outer loop treats incomplete as requiring stop recovery. The prompt
   starts by asserting that the worker returned before finishing its workflow,
   then directs it to return incomplete if no permitted action remains. This
   can reinforce the same completion/scope disagreement instead of resolving it.
4. Even a complete reply is subject to an older finalization condition:
   deferred obligations are allowed only when branch_id is literally
   provider_more_evidence_required and each obligation names that branch.
   The newer UM MD handoff operation legitimately records
   um_md_information_handoff. Audit and finalization therefore disagree.

The last condition is a confirmed integration bug. It does not follow from
clinical uncertainty, benchmark task diversity, or an API failure. The owner
reply was an immediate exit condition in the saved run; the provider-only
restriction is an additional latent rejection, not the executed cause of its
incomplete final. Do not collapse these two causal claims.

## Offline causal probe

Read the saved state.snapshot.sqlite via a read-only connection, copied its
JSON into memory, retained the standalone runner's trusted review-principal
path configuration, and invoked only local final-processing code. No model,
Docker actor, tool dispatch, patient mutation or original-state write occurred.
Snapshot hash was unchanged afterward.

| In-memory diagnostic variant | Observed result |
| --- | --- |
| Actual incomplete final | unresolved before final gate evaluation |
| Same final/evidence with only status changed to complete | handoff branch found, then rejected as deferred_work_requires_matching_handoff |
| Diagnostic control: same complete variant without deferred ledger entries | complete; handoff gate accepted |

The control is a counterfactual to isolate the finalization condition. It is
**not** a proposed fix, a changed patient record, an assisted actor retry or a
new benchmark result. Removing real deferred work would conceal responsibilities.

An initial diagnostic harness omitted trusted principal-path configuration and
thus did not faithfully reconstruct final identity validation. That probe was
corrected before interpreting branch-level results. The accepted receipt uses
the same declared review paths as standalone.py.

Ignored script/receipt:
`HealthHarnessCodex/runs/20261024-t033-10-closure-analysis.py` and `.json`.

## General repair direction (not implemented here)

- Use one closure assessment for both the assignment audit and finalization.
  Represent permission for an evidenced external handoff as explicit branch
  semantics, not a provider branch-name exception embedded in engine.py.
  Every deferred obligation still needs matching branch authority, original
  evidence and next action. Missing internal work remains blocking.
- Distinguish assignment execution, external case state and evaluation status.
  A completed permitted handoff can coexist with a pending clinical case and
  unscored semantic review. None implies approval or correct clinical reasoning.
- Evaluate and persist the closure assessment even when the model reports
  incomplete. Treat the model's report as meaningful input requiring a scoped
  explanation when it conflicts with the evidence. Do not auto-pass the case
  simply because our structural interpretation accepted it.
- Recovery should resolve that specific disagreement: identify an unmet
  responsibility, fresh contradictory evidence, or a permitted external wait.
  It should not assume work is unfinished or repeatedly solicit an identical
  investigation. A claimed conflict with the contract must remain expressible.
- Test the entire path: handoff tool -> deferred obligation -> final response ->
  finalization -> reporting. Earlier tests checked MD handoff with no deferred
  ledger and checked the deferral operation separately. The missing composition
  test let individually passing components retain incompatible final semantics.

Use synthetic cross-domain branches and negative variants: missing notice,
wrong identity/stale readback, unmatched deferral, open internal work, explicit
task prohibition of handoff, and model-reported evidence contradicting apparent
completion. No task ID, policy answer, patient details or expected disposition
belongs in a behavioral fix. Semantic grading remains separate.
