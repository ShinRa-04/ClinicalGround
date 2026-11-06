# Policy grounding: operational procedures for operational decisions

2026-11-03, branch `role-authority`. Implemented by Claude (Codex account was at its usage limit).

## Failure

UM triage task `pa_t012_t012_o001_p01_triage_payer` passed 3/3 officially on Oct 20, before the
policy-grounding requirement existed (added Oct 23). On Nov 3 (`runs/20261103-eval-ra-pa_t012…`)
it ran 20 model calls without creating a triage record. At call 18 the actor voluntarily recorded a
`case.record_policy_decision` for `triage.route_case`, citing the governing routing procedure
(`references/payer-um/operational/02-triage-routing.md`, via `workspace.read_many`) and the
clinical medical policy. The validator rejected the whole decision with a generic
"must identify retrieved policy text" error and no citation index or reason.

Cause: `policy_grounding._policy_text_source` accepted handbook files only under
`/medical-library/` or `/pa-requirements/` unless `allow_workflow`, and `allow_workflow` was true
only for CM operations (Oct 28 CM fix). An operational decision outside CM could not cite its own
operational procedure. Earlier calls show the actor re-searching and re-reading policy text,
consistent with hunting for citable text; the run then ended on a provider idle timeout.

## Fix (general, all domains)

- `DETERMINATION_ACTIONS` = `POLICY_ACTIONS` minus `cm_intake.disenroll_case` (provider
  submission/finalization, nurse/MD review decisions, determination finalize).
- Each citation must be real retrieved handbook text (unchanged rules: file/batch-child/search
  document text, not metadata, chart opinions or drafts). Operational/workflow references anywhere
  under the handbook's `references/` are now accepted for any operation.
- Any determination operation must additionally cite at least one clinical source
  (`medical-library` / `pa-requirements`); otherwise `PolicyGroundingError` with
  `reason=clinical_source_required_for_determination`. CM behavior is unchanged.
- Rejections now report `reason=not_retrieved_policy_text`, `citation_index`, `evidence_id`,
  `text_pointer`, `source_tool`, `source_path`.

## Verification

- New tests in `tests/test_policy_grounding.py` (synthetic text; real path shapes): routing
  procedure accepted for `triage.route_case`; determination with only a procedure rejected with the
  new reason and accepted once a clinical source is added; rejection feedback names index and path.
  `tests.test_policy_grounding`: 22 OK.
- Offline replay of the exact rejected t012 arguments against the saved state: **accepted**,
  `provenance_verified=True`.
- Full suite: 843 tests OK / 149.4 s.
- Not yet executed live: a fresh t012 run is next (after the Codex/Luna account limit resets 19:21 IST).

## Follow-up the same afternoon: CM decision invitation and unknown-condition consistency

Evidence from `runs/20261103-cm-dm-low-coop-luna-04`: the CM-04 worker never invited enrollment
and closed with "anything else… or stop here?"; its preparation judged the no-separate-fee
condition `unknown` because no fee-specific record exists (probe preparations judged it `met` 3/3).

- **Decision-invitation gate (general option, CM-04 on):** `run_helper(conversation_tools=…)`
  gives the worker a required `conversation_move` field on the counterparty message tool
  (`answer`, `ask_priority`, `invite_decision`, `confirm_consent`, `respect_decline`, `close`),
  stripped before dispatch. A `close` before any `invite_decision`/`respect_decline` is not sent and
  gets one feedback; it never blocks twice. CM-04 completion check now requires a direct enrollment
  question before any offer to end contact.
- **Unknown conditions:** `case.record_authorized_statements` items marked `unknown` must name
  `settling_record_type` and `settling_record_available`; an `unknown` resting on a record type the
  system does not hold is rejected with a re-judge instruction (one preparation retry). Code never
  sets statuses.
- Tests: `ConversationMoveTests`, `UnknownConditionTests`; full suite 848 OK / 70.5 s; blueprint and
  role validators pass; 33 FORK_BASELINE hashes match. Not yet executed live.

## Nov 3–4 night: t012 live reruns and two more general causes

- `runs/20261103-um-t012-grounding-01` (source `b9bfd01`): ended at model call 8 —
  `case.record_policy_decision` bound `"actor": "agent"` inside `bound_arguments`; identity check
  rightly rejected it, but no correction was allowed (no bound principal in UM triage). Structural
  2/15. **Fix `89aeacc`:** the optional-actor omission proof also strips `actor` from bound-argument
  objects; the one correction is offered only if the stripped call fully validates.
- `runs/20261103-um-t012-grounding-02` (source `89aeacc`): routed, reviewed, ran out of the 100-call
  budget (2,137 s, 315 tool ops). Structural **17/21** (was 2/15); failed `outcome.letter_types`,
  `triage.disposition_matches`, `triage.urgency_matches`, `triage.gold_card_matches`.
  Cause (compared with the Oct 20 pilot that passed 21/21 in 12 calls): `triage.route_case`
  returned a lane that finalized the case (`case.status=approved`, no review task); the pilot then
  recorded the disposition and delivered the approval letter. Today's actor instead pursued
  nurse/MD review for ~60 calls because the completion contract (`completion_contracts._um_contract`)
  had a single final-determination branch requiring nurse + MD + `determination.finalize`.
- **Fix:** new general branch `um_route_finalized_determination` for UM routing/intake tasks:
  intake stage (if any) + route + route result with a terminal case status + triage disposition +
  delivered notice + terminal readback. Offline: the pilot's real evidence (with read tools tagged
  as reads — the Oct 20 harness tagged every MCP call as a write) is accepted by the new branch.
  New test `test_um_route_that_finalizes_the_case_is_a_distinct_supported_branch`; full suite 850 OK.
- **Executed:** `runs/20261104-um-t012-route-01` (source `4899b6c`, Luna/high): harness `complete`
  (terminal condition verified), 24 model calls, 70 tool ops, 478 s; route → `set_disposition
  auto_approval` → approval letter generated + delivered. Native key-free structural **21/21,
  binary 1.0** (`runs/20261104-um-t012-route-01-native-check.log`). The Nov 3 UM regression is fixed.
