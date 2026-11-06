# CM goal-link live repair — October 25

User explicitly authorized rerunning the same CM case and repairing general
causes until the requested output is resolved. No paid judge, all-dataset run,
hidden fixture inspection or invented consent/plan is authorized.

## Attempt -05: actual result

Run `20261025-random-cm-anorexia-05`, code through `ccd8670`, frozen source
`f516a5e` (authorization documentation only added after code commit).
36 workflow model calls / 48 operations; actor unresolved. Reported workflow
usage 1,901,803 tokens (1,872,518 input + 29,285 output; 570,112 cached input
included; 12,907 reasoning-output detail). Patient simulation settled without
replaying an uncertain message. Snapshot saved and world stopped.

Native key-free checks on a copy of the actual saved export: 2/6 applicable
passed, 4 failed, 8 N/A; no assessment, care plan, target-status match or required
cross-stage audit result. No clinical/semantic judge, no full benchmark verdict.

Root announced an intended stop after observing repeated investigation of the
terminal case. However, the process lookup found no matching running batch:
the run had already ended unresolved naturally. No process was actually killed.
Do not record this as an operator-induced model error or controlled interruption.

## Confirmed new integration defect

`standalone.run_case` compiles the completion contract using raw public task
text, then passes a wrapped execution instruction to `Harness.run`. That wrapper
adds observed identifiers, workspace guidance and bootstrap context. The new
`goal_state.requested_outcome` compared the wrapped instruction's hash to the
raw task hash. It therefore returned unverified. Consequences: terminal review
and the first-stop goal review did not activate, even though feature/configuration
flags were enabled. Source-backed CM closure still executed, followed by wasteful
attempts to account for the unmet task. This is a harness integration fault.

Earlier offline tests used identical raw and execution instructions and missed
this boundary. Their mechanical results did not establish live integration.

## Repair and evidence

The host-owned completion contract now stores the exact `public_instruction`
alongside its original hash. The contract's integrity hash covers both. Goal
assessment, the compact goal view and paged task-text reads use that pinned
source; the separate execution instruction remains unchanged. No substring
guessing, integrity bypass, model-authored goal substitution or historical
artifact migration is used. Legacy contracts without the source retain the
strict fallback and cannot silently accept a mismatched wrapper.

New regression exercises the actual standalone `_profile_instruction` for PA,
UM and CM through the real Harness and SQLite state, with deterministic model
stubs. It verifies that wrapped execution text stays intact while the requested
goal is recognized as unmet rather than unverified. Another regression rejects
changed raw task text even if the outer contract is rehashed without updating
the task-source hash.

Read-only in-memory diagnosis on -05's saved state: original assessment
unverified; adding the correctly pinned public source to the diagnostic copy
gives unmet and identifies the terminal-review trigger. Database unchanged,
no actor/judge replay. Receipt: `runs/20261025-cm-05-goal-source-diagnosis.json`.

Full regression **702 tests pass / 79.389s**; 21 targeted goal tests pass.
Private log `runs/20261025-cm-raw-task-boundary-regression.log`.
This fixes the confirmed source-boundary defect, not the clinical consent issue
or the four benchmark failures. Root will commit source and run a fresh -06.

## Independent verifier inspection

Only public framework source/documentation was read, outside actor contexts.
The CM structural verifier checks assessment and plan record existence and
separately checks configured target status/audit actions. No hidden values were
read. Semantic judging cannot erase these structural failures in the documented
strict-score aggregation. No scoring code or benchmark data was modified.

## Attempt -06 and causal-boundary repairs

Source `4f1d888` fixes raw-task provenance: live goal status was correctly unmet,
and precommit reviewers ran before disenrollment. Root stopped the owned inference
process after five reviews repeated for the same case/source material. This time
the interruption was actual and operator-induced, not a provider outage.
35 model calls / 58 operations; snapshot saved and world stopped. Native
structural results remain 2/6 pass, 4 fail, 8 N/A. No paid judge.

Diagnosis compares five decision records: cited source business-content hashes
were identical. Owner rationale and audit-reason wording changed. The review
fingerprint incorrectly treated those edits as new material and spawned more
reviews. It now uses operation/effect arguments, pinned contract and a canonical
set of source-content hashes. For CM disenrollment, its public service contract
defines reason as audit text; that field is excluded from review identity while
the exact current proposed reason must still match the owner's decision record.
Other operation arguments remain part of the effect signature. Current wording
is not falsely labeled independently reviewed. New source content still triggers
a review; identical sources under new IDs or a different order do not.

Another confirmed sequencing defect: the owner batched a conversational message
and an outreach-summary write in one proposal. The summary was authored before
the patient reply was available. In this trial the reply happened to agree with
the summary, but a changed reply would not have been considered before persistence.
The dispatcher now records a case-local conversation observation fence for public
`cm_outreach.send_message` / `p2p_session.send_turn` operations. Later writes from
that same host-owned proposal round are not dispatched; independent reads can
continue. A new model turn can propose a write after observing the reply. The
fence is durable across interruption/resume; completed writes are not replayed.
This is a causal execution constraint, not a rule about consent or a task answer.

Regression adds an unexpected affirmative response followed by a stale negative
summary proposal: the stale write never reaches the tool, while a subsequent
owner turn can submit its own corrected summary. Both CM and P2P dialects,
independent reads, resume fencing, review reuse after rewording, and genuine
source changes are covered. **704 tests pass / 83.407s**; targeted goal tests23.
Private log `runs/20261025-cm-review-reuse-regression.log`.

No expected values, simulator persona or reference solution were read. Public
release documentation was checked for version context; it does not establish
that this particular task is defective. Source/runtime/policy conflict remains
an investigation, not a confirmed benchmark bug. Root commits then attempts -07.

## Attempt -07 and interface/data-flow repairs

Source `7adbf53`: 26 calls / 45 operations, 1,355,522 workflow tokens
(1,329,269 input + 26,253 output; 300,160 cached input included; 12,844
reasoning-output detail). Natural unresolved finish; one terminal helper, so
the repeat-review defect no longer reproduced. Snapshot/world stop preserved.
Native structural checks still 2/6 pass, 4 fail, 8 N/A; no paid judge.

The final model report honestly left the care-plan goal unmet and acknowledged
an unfinished refusal-closure obligation. It cited both reads and writes as
investigations. The stop validator rejected the list: it incorrectly treated
all write-effect tools as non-investigative, including actual counterparty
dialogue responses. It now separately recognizes original reads and public
CM/P2P dialogue responses as information gathering; authored summaries and
terminal writes remain ineligible as investigations. Supporting effect evidence
may still cite those writes. Incomplete finals now receive the same bounded,
precise tool-free source correction as complete finals. Its one-attempt budget
is separate from an earlier tool-argument correction; global budgets still apply.

Other real frictions repaired:

- The owner had to copy long bound audit reasons into a second tool call; a
  wording change caused `policy_decision_action_changed`. The optional
  `case.execute_recorded_action(record_id, operation)` resolves the exact stored
  payload before the normal dispatcher. Original schemas, identity/policy checks,
  terminal reviews and write journal still apply. A stable case/record/operation
  journal key prevents repeating a completed commit. Helper permissions cannot be
  expanded by delegating this local command without the actual remote write tool.
  Model-authored choices/arguments are not replaced or invented by code.
- Reviewers lacked some required input handles, notably the session ID from an
  earlier actual start result. `observed_resource_handles` supplies only exact
  same-case actor-returned IDs required by delegated tool schemas, with source
  IDs/pointers. It is not permission or proof that a session remains active.
  Read-only evidence discovery is also delegated; no ID guessing or new API.
- Exact duplicate MCP text/structured representations are removed from helper
  input views without altering original source records or dropping facts.
  Helpers are explicitly told not to claim absence from selected snippets.
- Current CM function inputs, outputs and boundaries are projected from the
  existing responsibility catalogue. Outreach guidance identifies source-required
  information and exit obligations before contact can end. Actual terminal
  effects move presentation to closure consistently; no tool is made a clinical
  permission by these design-role descriptions.
- Owner/reviewer guidance distinguishes performing care, documenting its
  refusal/non-performance and finalizing a record. Applicability must come from
  actual policy/tool scope; this does not authorize bypassing consent or making
  up clinical fields. Whether this distinction helps this case is unmeasured.

**710 offline tests pass / 73.426s**, including 25 goal/stopping tests and 4 new
prepared-action/helper-boundary tests. Actual MCP alias resolution, exact payload
dispatch once, repeat commit caching, source/case isolation, helper permission
fencing, original-record preservation and session handles are covered.
All 33 original harness baseline hashes match. Source/task/scoring/simulator
personas are unchanged. No hidden fixture/reference solution was read. Root
commits and executes fresh -08, then checks its actual output. The requested
finalized-care-plan outcome is still not established; do not claim it fixed.

## Attempt -08 result and October 26 diagnosis

Frozen source `dcd92d8`, run `20261025-random-cm-anorexia-08`. The actor finished
operationally with a supported stopping report, while the requested finalized
care plan remained unmet. There were **24 shared workflow/helper model calls,
35 operations, one terminal review**, and 5 patient-model calls. Reported
workflow/helper usage: **1,218,178 tokens** = 1,203,878 input + 14,300 output;
331,136 cached input is included in input; 5,707 reasoning output is included
in output. These totals exclude the separately recorded patient-model usage.

The existing native structural diagnostic returned **2/6 applicable checks
passed, 4 failed, 8 N/A**, structural binary reward 0 and diagnostic fractional
reward 1/3. Failures:

- `cm.assessment.record_exists`
- `cm.care_plan.record_exists`
- `cm.cross_stage.target_status`
- `cm.cross_stage.audit_actions`

The first two names identify tests, not statements that the records exist:
both failed because the records were missing. The result is not an expected
passing output. No paid/semantic judge ran; a full official score remains
unmeasured. Structural failure already prevents a strict all-checks pass.

An isolated dispatch-only probe of the official entrypoint confirmed
`stage_contract_path`. That agrees with the diagnostic's stage-check route.
The earlier concern about legacy-versus-stage routing was not substantiated.
The probe used sentinels instead of grading functions and is not itself a score.
Private receipt: `runs/20261025-cm-official-route-08/route.json`.

The actual transcript records declined enrollment and callback, limited accepted
program information, then an ended conversation. The reviewer retrieved the
complete transcript through its observed session handle. Prepared commit and
review reuse worked; this attempt did not reproduce the repeated-review loop.
The owner documented refusal and disenrolled, leaving assessment/plan absent.
Its source-linked stop is operational evidence, not evidence of benchmark success.

There was a narrower investigation gap: owner/reviewer read workflow/outreach
policy but did not open assessment/care-plan standards. Root subsequently read
only those two permitted reference files, outside any acting model context.
That read found no documented alternative allowing the requested output after
this refusal. It does not prove that every possible permitted path was exhausted
or that a different earlier conversation could not have changed the outcome.
No protected source content is reproduced here. Hashes/read scope are retained
only in ignored `runs/20261026-cm08-diagnosis.json`. These extra reads must not be
misrepresented as evidence available to the -08 actor or as a new actor trial.

Confirmed chain: observed refusal prevented consent-dependent assessment; no
assessment/plan was produced; native checks failed. Unresolved causes: worker
conversation quality versus intended difficult-patient behavior versus behavior
of the experimental Codex replacement for the original simulator. The verifier
checks effects and cannot resolve that attribution. The bridge code passes the
simulator's supplied system/messages and adds no instruction to refuse; model
equivalence is still not established. No persona, hidden fixture, expected field
value, or reference solution was inspected. Do not infer behavior from task names.

Original snapshot integrity reverified offline on October 26. Saved manifest
records the world stopped; Docker is currently unavailable. No actor replay,
patient modification, scoring change or new source change was made during this
diagnosis. Preserve all failed development trials separately. A further trial
needs a meaningful new hypothesis; do not rerun merely to obtain a lucky consent
response or manufacture records. User is discussing whether the patient model
is the bottleneck; direction on a separate case remains unconfirmed.

## Operator-only patient-instruction audit, October 26

The user explicitly requested checking whether the patient LLM is instructed
to refuse always, then asked about using the instructions to understand the
conversation. This authorized a narrowly scoped operator audit of the current
task's `persona_contract.patient_profile`. It did not authorize feeding private
instructions into the care-manager actor, modifying the patient, reading separate
expected outcomes/solutions, or changing scoring. Root inspected the patient
narrative only; it also contains private assessment facts, so root can no longer
claim to be blind to this task's patient information. Actor contexts were not
changed. Preserve this exposure in future development/evaluation provenance.

Finding: the configured patient is **conditionally willing**, not unconditionally
refusing. The narrative defines both a route to consent and conversational
boundary violations that prevent consent for the remainder of the current call.
The saved -08 transcript contains a qualifying violation: the worker introduced
sensitive diagnostic labeling before permission. The local configured rule thus
explains why later clarifications did not obtain consent. This is stronger
evidence than the earlier speculation that the replacement patient might simply
be too unwilling. It does not establish equivalence between Codex and the
original simulator, nor guarantee success with a different conversation.

No patient narrative, private checklist, assessment answers or special consent
recipe is reproduced in tracked documentation. The run itself remains unchanged
and failed. Future general repairs must derive their worker-facing instructions
from permitted workflow guidance and observable dialogue, without embedding the
private persona's particular conditions. Later same-case root-assisted trials
must be labeled development attempts rather than blind evaluation.

Private audit receipt `HealthHarnessCodex/runs/20261026-cm-patient-instruction-audit.json`
records the selected field, source digest, scope and exposure. No model call,
dataset actor, paid judge, data edit or behavioral source change occurred.

## General communication repair and retry -09 preparation

The user emphasized that care management needs a kind, responsive conversation
and that patient concerns must be addressed rather than dismissed. Root updated
the general CM owner mission, CM specialist guidance and outreach-stage reminder
in `roles.py` and `assignment.py`. They require responding to the patient's actual
questions/priorities, checking understanding, using supported information,
explaining sensitive topics before asking permission, pacing the dialogue and
respecting declined topics or a stop. The model still chooses the wording and
next investigation; there is no automatic consent decision or compulsory script.
The same general practices are already supported by permitted workflow/outreach
guidance. The code includes no patient-specific label list, private trigger
checklist, case identifier, hidden assessment answer or numerical consent recipe.

Initial full regression: 710 executed, one existing timing-sensitive test failed.
Its fake model sometimes returned within the same monotonic clock tick, leaving
the entire one-second allowance available instead of the assumed elapsed time.
The test now advances an explicit fake clock during inference. No production
deadline or simulator behavior changed. All 27 simulator tests pass after that
test repair. Final full regression: **710 tests pass / 85.740s**. Private log:
`runs/20261026-cm-communication-regression-final.log`. These checks verify
mechanics, not patient engagement or benchmark success.

After the user restarted Docker, Linux engine availability was verified. The
authorized fresh single-case retry is `20261026-random-cm-anorexia-09`, helpers
with automatic recovery, Luna/high, actor 100 model calls/500 operations, 180s
silence/600s active deadline, no actor context-character cap. Patient-call
allowance is raised from 8 to 32 to permit a longer outreach/assessment dialogue;
the existing 180,000 cumulative simulator input-character and 900s world bounds
remain. It remains an experimental Codex patient, with no paid judge. No claim
of simulator equivalence or blind evaluation: root inspected the private persona
under explicit user instruction; that material is not supplied to the worker.

## Retry -09 interrupted; patient quotas and exact repetition guard

Source `620e533`; root stopped the owned Codex inference after the user requested
no fixed patient-conversation quota and a repetition-based stop. Actor settled
at 4 model calls/5 operations, with snapshot saved and world stopped. This was
operator-induced interruption, not a new model outage or a clinical result.
No patient exchange had occurred. Do not grade or pool it as a natural outcome.

User explicitly chose three repeated exchanges, rather than paraphrase analysis.
`dialogue_guard.py` records hashes and original evidence IDs for completed CM
send-message exchanges. Three consecutive identical pairs (NFKC, case and spacing
normalized; punctuation/numbers retained) stop further dialogue for the attempt.
Only successful original exchanges count, not cached action readbacks. State
survives resume; starting another session cannot bypass the stop. The external
patient reply/session is not altered and no synthetic STOP/refusal/consent is
introduced. Other permitted tasks can continue and goal verification is separate.
The console event is `DIALOGUE_REPEAT_STOP`. Paraphrased loops remain outside
this exact-match check; other existing progress/recovery controls still apply.

Patient simulator defaults now use zero to disable cumulative call/input-character
and world-duration quotas. Explicit positive limits retain their previous checks.
Per-request validation/deadlines, overall actor/helper100/500 budgets and official
benchmark session limits remain. No official runtime source/data is changed.
New synthetic coverage checks repeated-pair detection, changing questions,
independent sessions, cached readbacks, actual guarded dispatch after resume,
continued non-dialogue reads, and 12 fake patient calls exceeding the former
180,000-character/900s quotas with quotas disabled. **714 tests pass / 77.793s**;
private log `runs/20261026-dialogue-guard-regression.log`. Mechanics only.

Next authorized same-case trial: fresh `20261026-random-cm-anorexia-10`, with
explicit simulator flags all zero, existing Luna/high helpers/auto and actor
100/500. No paid judge/all75; source must be committed/frozen before launch.

## Retry -10 and explicit stop

Source `f8dd276`, run `20261026-random-cm-anorexia-10`. The run ended naturally
at 14:08:37 IST on October 26, before root's process lookup in response to the
user's explicit "Stop the work." No matching process remained; none was killed.
42 shared workflow/helper model calls, 78 operations, 6 patient-model calls.
Actor unresolved, requested goal unmet. Snapshot saved and task world stopped;
`docker ps` returned no running containers. No structural diagnostic or paid
judge was launched for this trial before the stop. Do not infer a new score
from earlier trials. All source changes through f8dd276 were committed; the
prelaunch regression was 714 tests passed / 77.793s.

The observed conversation improved its initial listening and respected the
patient's wording, but became passive: it repeatedly explained limitations and
offered to stop rather than translating the patient's request into a supported
next step. The patient ended contact without enrollment consent. No cumulative
patient quota or exact-repetition guard caused this stop. Later owner/helper
work repeatedly investigated records needed for final stopping; the precise
controller failure path remains unconfirmed and needs saved-state diagnosis.

Root also found a case-evidence-use weakness: a previously observed chart source
contained clinician follow-up planning, while the worker told the patient it
lacked the doctor's follow-up instructions. Historical instructions still need
current-applicability verification; their existence should not be conflated with
an available live clinician response or a promise of delivered coordination.

The user approved a proposed general correction: make replies responsive AND
purposeful, connecting them to concrete source-supported next steps, explaining
participation and inviting consent when appropriate without pressure or promises
of unavailable services. This correction has NOT been implemented. No new source
change, test or trial should occur until the user resumes work. Original private
persona exposure remains an operator-only development limitation.
