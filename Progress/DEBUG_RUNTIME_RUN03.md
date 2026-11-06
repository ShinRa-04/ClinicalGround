# Run 03 runtime and model diagnosis

**Updated:** October 21, 2026
**Scope:** shared Codex provider, transport, model-error handling and context/runtime lane.
**Evidence:** immutable actor records in `HealthHarnessCodex/runs/20261021-full-dataset-03/`; sanitized per-case index in the ignored `HealthHarnessCodex/runs/20261021-debug-run03/runtime/findings.json`.

## Run coverage and classification

All 75 selected attempts settled. The batch recorded 69 deferred snapshots, 3 setup failures without a snapshot, and 3 reconciliation cases. Local actor outcomes were 5 `complete`, 24 `unresolved`, 32 `error`, 8 `blocked`, and 6 `setup_failure`. There was no official judge run, so no strict score is available. A local completion is not an official pass.

The shared runtime lane found 20 `inference_failure` errors. All are CM cases. Their persisted error is the same sanitized `ProviderError` outcome, “Codex turn reported a failure.” Eighteen failed on their first model call (event 12 in each case, before any tool result). Two failed after prior settled activity: `cm_complex_parkinson_dep_moderate_tentative_001` on call 4 (event 24, after 3 successful model calls and 3 tool results) and `cm_complex_hf_afib_ckd_hard_refuses_001` on call 7 (event 51, after 6 successful model calls and 13 tool results). The other 18 public task IDs are:

- `cm_copd_hard_refuses_002`, `cm_dementia_hard_refuses_001`, `cm_dm_hard_refuses_002`, `cm_dm_low_coop_001`, `cm_dm_moderate_anxious_001`, `cm_hf_hard_refuses_002`, `cm_htn_low_tentative_001`, `cm_mdd_hard_refuses_002`, `cm_mdd_moderate_reluctant_001`
- `cm_metabolic_syndrome_hard_refuses_001`, `cm_parkinson_hard_refuses_001`, `cm_post_hip_moderate_anxious_001`, `cm_post_mi_hard_refuses_002`, `cm_post_pna_moderate_tentative_001`, `cm_post_stroke_hard_refuses_001`, `cm_ptsd_hard_refuses_001`, `cm_schizo_hard_refuses_001`, `cm_sud_hard_refuses_001`

The historical actor logs do not preserve the terminal Codex error code or status, and the runtime discarded the structured turn error. The exact remote cause for these 20 failures therefore cannot be recovered from run 03; current account usage cannot establish their historical cause. No run 03 attempt was replayed.

Thirteen other cases were classified `schema_or_scope_rejection`: 12 ended `error`, and one (`pa_t024_t024_o001_p01_nurse_review_payer`) ended `blocked`. Seven UM proposals used an `actor` value that exactly matched a successful same-case MD or nurse review result at `structuredContent.triage.actor`, while the run scope still used fallback principal `payer-actor`. The engine now binds that principal only from the exact configured tool alias and path, requires `triage.case_id` to equal the selected case, records the source evidence, and rejects a conflicting later binding. Five candidates came from nurse review results (`pa_t022_t022_o001_p01_nurse_review_payer`, `pa_t026_t026_o003_p01_nurse_review_payer`, `pa_t027_t027_o002_p01_nurse_review_payer`, `pa_t028_t028_o001_p01_nurse_review_payer`, `pa_t032_t032_o002_p01_nurse_review_payer`); two came from MD review results (`pa_t017_t017_o001_p01_mdreview_payer`, `pa_t018_t018_o001_p01_mdreview_payer`). Two UM cases (`pa_t030_t030_o002_p01_triage_payer`, `pa_t035_t035_o001_p01_intake_payer`) had no prior same-case actor observation and remain rejected. Three provider cases (`pa_t016_t016_o001_p01_new_referral_provider`, `pa_t030_t030_o002_p01_new_referral_provider`, `pa_t032_t032_o002_p01_new_referral_provider`) attempted a case identity before a real provider case was bound; those values remain rejected. The separate blocked case quarantined returned identity content. No identity gate was weakened.

Seven cases ended `unknown_effect` after a write outcome could not be confirmed: `cm_afib_moderate_anxious_001` (event 42), `cm_anorexia_hard_refuses_001` (58), `cm_asthma_low_coop_001` (45), `cm_ckd_moderate_anxious_001` (47), `cm_complex_esrd_dm_hard_refuses_001` (54), `pa_t031_t031_o001_p01_p2p_payer` (26), and `pa_t036_t036_o002_p01_p2p_payer` (46). Each has exactly one journal entry marked `unknown` and a matching failed tool event. All seven surfaced as `MCPToolError`; the adapter withheld the MCP error details. Five are `mcp_cm_outreach_send_message`, one is `mcp_p2p_schedule`, and one is `mcp_p2p_session_send_turn`. Earlier actions completed, and no post-error readback is recorded. The same redacted error hash appears in all seven. No stable tool error code is available, and `isError=true` does not prove whether a write took effect. Keep these actions unknown; no write was replayed.

The rest of the local outcomes were 24 `incomplete_workflow`, 5 `locally_complete_ungraded`, and 6 `setup_failure`. Read-only final inspection split the 24 incomplete outcomes into 14 plain-prose finals, 6 structured pending/incomplete finals, 3 completion claims blocked by open obligations, and 1 unobserved evidence citation. The fresh-runtime prose correction below does not change the historical outcomes. The per-case index retains the raw coverage categories without actor content.

## Runtime change

The provider now extracts only an allowlisted `codexErrorInfo` code and bounded turn status from terminal App Server errors. It discards the free-form server message. The structured failure category and two separate facts are carried into the local run result: whether the failed model call returned no proposal to dispatch, and whether its recognized error code is transient-retry eligible.

The runtime does not automatically retry. A future retry must be bounded and charged as another model call; this change makes no such call and does not alter prior usage accounting. The `proposal_dispatch_safe` flag concerns only the failed completion: the harness received no `ModelReply` from it, so it dispatched no proposal from that completion. It does not certify earlier writes or resolve an unknown effect.

The new metadata supports future turn-error diagnosis without storing error prose or protected actor content. It cannot retroactively recover run 03's missing error code. Reproduction of the historical failure remains unverified until the coordinator permits a bounded fresh synthetic/public CM probe after the source freeze.

The engine also supports an observed principal binding from explicitly configured source tools and paths. It requires the exact review record to bind the selected case ID and a non-empty actor string, records the source evidence ID, and checks later proposals against that principal. A cross-case record, malformed actor, or conflicting later actor is quarantined. The UM launcher configures only the MD and nurse review tool aliases with `structuredContent.triage`; cases without that evidence keep the fallback scope and rejected actor values.

For a plain-prose final, the engine may make one format-only correction call if the shared correction allowance remains. The retry is separately counted against the model budget, uses the same case transcript and evidence, declares no tools, and rejects any proposed tool call without dispatch. It shares the single correction allowance with the existing JSON-response retry. Structured incomplete status, open obligations, and invalid evidence do not trigger it.

## Verification

- `test_codex_provider.py`: 12 tests passed, including allowlisted error-code extraction, rejection of unknown error details, no retention of free-form error text, and separate retry-safety flags.
- `test_codex_transport.py`: 7 tests passed.
- `test_engine.py`: 29 tests passed, including principal source binding/conflict/cross-case/malformed-path checks, bounded format correction, retry-budget sharing, and tool-proposal rejection.
- Domain-path integration: `test_context.py` 8, `test_domain_profiles.py` 24, `test_identity_integration.py` 11, and `test_standalone.py` 28 passed.
- `git diff --check` passed for the runtime lane files.
- No clinical task was rerun, no native inference was issued, and no OpenRouter or judge call was made during this lane.

The error-code allowlist follows the Codex App Server `TurnError` / `CodexErrorInfo` shape and preserves only recognized machine-readable categories. See the [official Codex error schema](https://github.com/openai/codex/blob/main/codex-rs/app-server-protocol/schema/typescript/v2/TurnError.ts) and [official error-info schema](https://github.com/openai/codex/blob/main/codex-rs/app-server-protocol/schema/typescript/v2/CodexErrorInfo.ts). The schema is current upstream documentation; run 03's installed CLI version and the absent error payload were not independently verified against it.

## Remaining limits and handoff

- Do not claim the 20 historical failures are repaired; their remote cause is absent from the retained actor evidence.
- Do not treat identity rejections as permission to weaken identity gates. Domain review owns the model/tool instruction path for those cases.
- Do not replay any `unknown_effect` case or restart any retained recovery world.
- Recovery coordinator owns the source freeze and any bounded fresh reproduction. If a reproduction is authorized, use a fresh isolated thread and public/synthetic context, preserve exact model-call accounting, and stop after the first useful diagnostic category.
- A generic read-only reconciliation path for unknown writes needs an action-specific proof contract. The current engine stops after an unknown write, continuation rejects unknown journal entries, and the store has no audited transition out of `unknown`. A read-only query alone cannot prove delivery or non-delivery across all action types. Keep each action unknown until a domain verifier or operator ties actual readback evidence to that exact write; a separately designed audited reconciliation step is then required.
