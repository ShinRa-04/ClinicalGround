## Dedicated worker preparation (2026-11-03)

Owner: Codex implementation/offline checks; reviewer/user owns review and live runs.
Branch `role-authority`; no commit. This section supersedes the earlier optional-only
worker preparation and probe implementation descriptions below. Root HANDOFF.md is
intentionally untouched under this task's explicit constraint.

User-reported rerun evidence: Luna/high, three samples per mode, local
`runs/*-conversation-probe-20261103T095*.json`. At the fee boundary, baseline and
current without a separate call each yielded 0/3 plain answers; in-reply preparation
judged the condition unknown 2/2. Separate `--prepare` yielded 3/3 plain, correctly
scoped answers and recorded the condition met. At the office-request boundary,
all modes still opened with an execution-limit disclaimer; only some added program
help. One in-reply preparation retracted an earlier fee statement as unknown;
separate preparation recorded met. These are the user's measured probe results,
not newly executed or independently rescored here. They motivate a dedicated calm
preparation step; they do not establish full-run success or fix disclaimer-first speech.

Implemented files:
- `health_harness_codex/worker_preparation.py`: shared instruction, provenance-only
  local validator, engine-shaped errors and at most one corrective completion.
- `helper_jobs.py`: optional `run_helper(..., preparation=True)` persists the job
  setting; `_work` prepares before ordinary turns. Calls, usage and proposals count
  against the existing job/case limits. One ordinary worker turn and the existing
  owner integration reserve are retained; insufficient budget/context skips
  preparation instead of blocking conversation. Request failures retain charged
  calls/usage and allow ordinary work; ownership/unknown-outcome conflicts propagate.
- `dialogue_worker.py`: CM-04 alone enables preparation by default. Selected sources
  include successful same-scope already-retrieved file/batch reads, chart, referral
  and evidence retrievals with original IDs; foreign/failed observations are excluded.
  Source bodies live in the existing observation packet, outside the bounded question.
- `conversation_probe.py`: `--prepare` calls the exact same shared routine and
  instruction, supplying boundary-limited observations. Offline `prepare_probe`
  stops prompt capture before any preparation/inference and returns the full
  current delegated inventory; ordinary probe sampling behavior remains bounded.

Only `case.record_authorized_statements` is supplied during preparation. Mixed or
other proposals are rejected as a whole with feedback; no remote dispatcher runs.
Only the existing local validator can replace the statements list. Preparation
assistant/tool feedback is persisted in the helper-owned case journal; the job
retains attempts/results. `worker_preparation` progress logs actual model calls,
recorded count, statuses and whether the local replacement succeeded. Existing
`authorized_statements.pin` carries the list into later worker contexts. Two invalid
attempts leave any prior list unchanged and conversation proceeds within its limits.

The domain-neutral instruction asks for purpose, relevant services, fees, cadence,
information sharing/use and withdrawal, with conditions decided under the existing
record-judgment rule. It includes policy-supported coordination/referrals answering
the counterparty's priorities as available after enrollment/decision, alongside
execution limits. Missing policy permits an empty list or supported unknowns;
there is no code-generated statement or semantic certification. Owner prompt text,
role authority, consent, source and execution boundaries are unchanged. No other
domain's worker is enabled by default.

Verification: see the final receipt immediately below. Tests are synthetic/fake
models only. No Docker, trial, judge, live provider call, protected handbook copy,
commit or edit under HealthHarness/, Runner/, Dataset/ or Progress/HANDOFF.md.
Pre-existing `.playwright-mcp/` remains untouched. Live behavior and benchmark
performance of this new runtime path are unverified. Next owner: review, then the
one user-only full run and native structural check below; preserve failed trials
separately from this assisted development work.

### Final offline receipt

- Full suite from `HealthHarnessCodex/`, exact requested command:
  `C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -m unittest discover -s tests -q`:
  **840 tests passed / 75.908 s**, exit 0, no failures/errors.
- Blueprint validator PASS / 0.321 s: 66 contracts, 97 mappings, 529 links,
  293 anchors. Role draft validator PASS / 0.111 s: 66 IDs, 56 mapped,
  10 code-only, no errors or authority-action-list suspects.
- Prompt metrics PASS / 0.608 s, including both offline `prepare_probe` boundaries:
  luna-03 turn 4 and luna-01 turn 7. Exact current authority present; both source
  database hashes unchanged. Each fixed worker context: system 7,884 + question
  2,633 = 10,517 characters. Separate preparation instruction is 892 characters;
  observation bodies are variable and outside these fixed counts.
- Owner prompts unchanged: PA combined 23,284 (+4.91%), helpers 18,742 (+13.39%);
  UM combined 23,313 (+6.01%), helpers 18,776 (+14.97%);
  CM combined 30,196 (+9.35%), helpers 24,107 (+12.29%). All within +15%.
- Original FORK_BASELINE **33/33 hashes match / 0.004 s**; `git diff --check`
  passes. Branch remains `role-authority`; prohibited paths have no diff.
- Added 7 regressions (6 shared/runtime preparation tests and one CM source-selection
  test); updated existing dialogue/statement tests for the restricted first call.
  Coverage includes fake-model call order, local-only/mixed proposal rejection,
  citation failure/correction, two-invalid fallback, shared/job charging, later pin,
  source isolation, CM enablement, non-CM default and shared probe routine.
  Earlier full run: 840 tests / 101.114 s with one outdated first-call permission
  assertion; corrected to verify preparation-only first and normal permissions later.
  This failed check is not represented as a passing run.

### One user-only full run, then native key-free check

Run from a normal PowerShell window. Settings checked against the saved luna-03
frozen manifest: actor Luna/high, helpers/recovery auto, 100/500, no context cap,
180/600, Codex Luna/high patient, both simulator quotas zero, 180 s request timeout.
The commands are documented, not executed in this turn. The check uses Docker but
no semantic judge, live model or provider key; run it only after the attempt settles
and saves its snapshot.

```powershell
Set-Location C:/Projects/BigData/HealthHarnessCodex
& C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -m health_harness_codex.batch `
  --dataset-root ../Dataset/chi-bench `
  --run-dir runs/20261103-cm-dm-low-coop-luna-04 `
  --domains cm --task-id cm_dm_low_coop_001 --attempts 1 --concurrency 1 `
  --actor-backend harness --model gpt-6-luna `
  --composition helpers --recovery-helper-policy auto `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --timeout 180 --active-timeout 600 `
  --simulator-backend codex --simulator-max-model-calls 0 --simulator-max-total-chars 0 `
  --simulator-request-timeout-seconds 180 `
  --codex-executable C:/Users/prath/AppData/Local/OpenAI/Codex/bin/22cfb1d302613eae/codex.exe

& C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 runs/check_structural_no_judge.py 20261103-cm-dm-low-coop-luna-04
```

# Authorized statements - Phase 4

Owner: Codex implementation/offline verification. Reviewer/user owns review and live execution.
Branch `role-authority`; no commit. User-authorized Phase 4 of the approved plan.
Root `Progress/HANDOFF.md` is intentionally unchanged under the explicit task limit.
See [role authority](ROLE_AUTHORITY.md), [probe commands and semantics](CONVERSATION_PROBE.md),
and [prompt measurements](ROLE_PROMPT_BASELINE.md).

## Goal and design

Give an actor a place to decide whether observed records satisfy a conditional policy
statement before speaking for a program or decision. This is general preparation,
not a case-specific answer, a code-generated fact, a semantic policy verifier or a
new permission gate. No task IDs, patient facts, answers or handbook text were added
to implementation prompts/code. All new tests use synthetic observations/fake models.

`health_harness_codex/authorized_statements.py` declares the shared schema and real
validator. `engine._LOCAL_SPECS` includes `case.record_authorized_statements` with
`effect='write'`. Engine local dispatch validates and persists it through the existing
case-scoped local-write path; assistant proposals and tool results stay in the case
message journal like other local writes. No remote action/tool is generated or dispatched.
The helper channel continues to mark its messages with job ownership. No guard is weakened.

Arguments replace the entire latest list atomically. Each entry requires `text`,
`source_evidence_id`, nullable `policy_condition`, `condition_status`, and
`condition_evidence_ids`; `scope_note` is optional. Schema rejects undeclared keys.
Limits: 0-6 entries (empty clears); text 1-600 characters; condition null or 1-300;
scope note up to 300; at most 8 condition IDs, each/source ID 1-160 characters.
Statuses are `met`, `not_met`, `not_applicable`, `unknown`.

Validation checks only shape and provenance: every cited ID is a successful
observation in this exact case scope; `met` requires at least one condition ID.
The actor chooses text/status and applicability. Code stores deep copies without
editing text, generating facts, checking semantic entailment, or certifying the
policy condition. Failed validation leaves the previous list untouched. Stored
`authorized_statements_source_count` permits conservative opening-context restoration
in the probe; it grants no authority. The latest state list and existing message
journal provide continuity; no cross-case memory is used.

`working_set.py` pins the compact full latest list into the owner ledger for CM,
PA and UM. `context.py` also includes it in the fallback owner ledger without a
mapped clinical contract. `helper_jobs.py` pins current preparation into the fresh
system context before each worker completion, so worker-recorded updates appear
on the next call. The label is `actor_source_linked_preparation_not_policy`, with
`interpretation_verified: false`. Re-pinning replaces stale context preparation.
The bounded entries are serialized intact, not truncated or rewritten.

`dialogue_worker.py` delegates exactly one additional local write to CM-04:
`case.record_authorized_statements`. Its remote speaking permission is unchanged;
no other local writes are added. Owners in all domains can select the local tool.
Role guidance adjacent to precedence is short and domain-neutral, explicitly
optional, and asks the actor to decide conditions from observed records, state
`met` statements plainly, and explain unknowns once with a resolution path.
The outreach question reinforces preparation. Skipping it never blocks speaking.
Authority, consent, identity, observed-effects and capability limits remain in force.

## Probe implementation and limits

See [probe documentation](CONVERSATION_PROBE.md) for the six exact `--repeat 3`
commands, with and without `--prepare`. Each sample starts independently and may
apply only authorized-statements preparation in memory, append its tool result and
make one follow-up call for a message or correction. Max two calls per sample.
Shared `--prepare` makes at most two calls: engine-shaped validation feedback allows
one correction; persistent failure is recorded and samples proceed without shared
preparation. Other tool proposals never dispatch. Total <= 2K without shared
preparation, <= 2 + 2K with it. Saved SQLite remains read-only. Per-sample output
includes preparation attempts, recorded statements/statuses, message and call count.
Preparation is shared across repeats; full boundary observations may enlarge its
context. Live provider capacity/usage remains unverified.

Condition guidance now judges records according to what they can show: consistent
records of the kind a condition refers to support `met`, without demanding record
types the system lacks. `unknown` is reserved for missing/conflicting settling
records and accompanied once by what would settle it. This domain-neutral guidance
appears once per owner/helper prompt. It does not change provenance validation or
make code determine a condition's truth. Existing ownership, precedence and blocker
wording was shortened without removing role, source, consent or execution boundaries.

A current probe rebuilds the opening context, then appends real saved old-prompt
history. It restores a latest list only when recorded before outreach start; it
cannot reconstruct unperformed preparation or generate counterfactual patient turns.
`--prepare` is the explicit diagnostic way to add that missing step. First-sample
top-level JSON fields are retained for compatibility; all outputs are in `samples`.

## Follow-through verification (2026-11-03)

Latest implementation: `conversation_probe.py`, `roles.py`; synthetic regressions:
`tests/test_conversation_probe.py` (18 tests) and `tests/test_authorized_statements.py`
(6 tests). Existing fields remain; preparation failure is recoverable, and samples
now follow preparation with one bounded completion. A valid correction on the second
sample call can record statements but cannot produce a third call; its message may
remain null. This is intentional call-limit enforcement, not a claimed actor success.

Final full-suite result: **833 tests passed / 73.506 s**, process exit 0, no failures
or errors. Exact command is below in the historical verification section. The preceding 833-test run passed in 76.328 s, before a final
wording-only adjustment preserving original-source-link guidance.
Blueprint validator: PASS, 66 contracts, 97 mappings, 529 links, 293 anchors / 0.304 s.
Role draft validator: PASS, 66 IDs, 56 mapped + 10 code-only / 0.102 s.
Prompt metrics: PASS / 0.568 s, including budget assertions and offline `prepare_probe`
for luna-03 turn 4 and luna-01 turn 7. Both source database hashes remain unchanged;
exact current authority is present. Each worker is 7,884 system + 2,633 question =
10,517 chars. All 33 FORK_BASELINE source hashes match. `git diff --check` passes.

| Domain / composition | Before | Current | Growth |
| --- | ---: | ---: | ---: |
| PA / combined | 22195 | 23284 | +4.91% |
| PA / helpers | 16529 | 18742 | +13.39% |
| UM / combined | 21992 | 23313 | +6.01% |
| UM / helpers | 16331 | 18776 | +14.97% |
| CM / combined | 27613 | 30196 | +9.35% |
| CM / helpers | 21469 | 24107 | +12.29% |

All checks are offline; fake models only. No commit, Docker, trial, judge or live
model call. No protected path was edited, and root HANDOFF.md remains untouched by
explicit task instruction. The pre-existing untracked `.playwright-mcp/` is unrelated
and untouched. Next owner is reviewer/user: inspect the diff, then execute the six
commands in CONVERSATION_PROBE.md if desired. Live condition judgment consistency,
message quality, clinical correctness and benchmark performance remain unverified.
The initial development budget overflow and test-only helper lookup error were
corrected before final verification; neither is represented as a passing check.

## Historical Phase 4 verification

Final exact unpiped command from `HealthHarnessCodex/`:

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m unittest discover -s tests -q
```

**828 tests passed in 81.829 seconds, process exit 0.** This includes 5 new
statement-tool tests and 14 probe tests (8 existing + 6 new). Existing caution,
precedence, capability, isolation and dialogue regressions pass. Final receipt:
`HealthHarnessCodex/runs/phase4-verification.local.json` (ignored). The redirected
`phase4-unittest-final.local.log` is the preceding 827-test/82.542 s passing run,
not the final source verification; PowerShell returned an inconsistent exit status
for that stderr-redirection invocation. The final unpiped invocation above is the
completion evidence.

Executed validators: blueprint PASS (0.297 s): 66 contracts, 97 mappings, 529 links,
293 anchors. Role draft PASS (0.109 s): 66 IDs, 56 mapped, 10 code-only, no errors
or authority-action-list suspects. These are structural checks, not clinical validation.
All 33 original `HealthHarness/` hashes match `FORK_BASELINE.json`.
`git diff --check` passes. Prohibited paths have no diff; branch remains `role-authority`.

Prompt metrics executed offline (exit 0 / 0.547 s), including its budget assertions, and refreshed
the after-numbers in `ROLE_PROMPT_BASELINE.md`. All six owner prompts are within
+15% of Phase 0; CM-04 question remains under 3,000 characters. Fixed system/question
budgets do not measure the variable statement list, saved conversation, tool schemas,
or full observations added for an actual preparation call.

| Domain / composition | Before | Phase 4 | Growth |
| --- | ---: | ---: | ---: |
| PA / combined | 22195 | 23274 | +4.86% |
| PA / helpers | 16529 | 18732 | +13.33% |
| UM / combined | 21992 | 23303 | +5.96% |
| UM / helpers | 16331 | 18766 | +14.91% |
| CM / combined | 27613 | 30186 | +9.32% |
| CM / helpers | 21469 | 24097 | +12.24% |

Both current offline probes have system 7,792 + question 2,633 = 10,425 characters,
versus Phase 0 system+question 10,980. Exact CM-04 authority is present.
The requested saved boundaries prepare without inference: turn 4 has 23 messages,
turn 7 has 34; baseline 11 specs/current 12. Boundary preparation has 18/22
observations respectively. Both database hashes remain unchanged. Baseline/current
preparation took 0.078/0.063 s total per source run in the explicit offline check.

Tests cover shape/bounds/status, unknown/foreign/failed provenance, met-without-support,
atomic replacement and exact text retention, PA/UM synthetic contracts, both owner
ledger paths, actual local dispatcher persistence, worker next-turn pinning and write
allowlist, stale-pin replacement, optional preparation before speaking, repeat counts,
identical contexts, CLI JSON, early flag rejection, preparation tool restriction,
future-evidence cutoff and pre-outreach restoration. Existing caution, precedence,
question cap and prompt-budget regressions remain included in the full suite.

Earlier verification: 824 tests passed / 73.524 s. A subsequent 827-test run caught
a five-character owner prompt overflow (+15% threshold), which was corrected by
shortening blocker guidance without changing its rules. Final wording has +14.91%
UM/helpers growth. One validator invocation initially used the wrong repository path;
rerunning the correct blueprint path passed. No failed run is claimed as a pass.

## Continuation and unverified work

Implementation and offline verification are complete; reviewer review remains.
User can run the commands in `CONVERSATION_PROBE.md` to compare baseline/current
repeats and one shared preparation plus repeats. Review semantic accuracy as well
as plain wording. No live model, Docker, trial, judge, commit, protected handbook
extraction or saved-run mutation was performed. Software verification does not
establish improved live behavior, clinical correctness or benchmark success.
