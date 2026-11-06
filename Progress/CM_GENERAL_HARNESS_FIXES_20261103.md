# CM general harness fixes ? November 3, 2026

## Scope and ownership

Implemented by Codex; reviewer reviews and commits; user alone launches live attempts.
No commit, Docker command, model call, dataset trial or judge executed in this work.
No hidden fixtures/tests/solutions/expectations read. No protected handbook passages
copied into source, tests or these docs. All tests use synthetic examples.

## Evidence and diagnosis

Read ignored run `HealthHarnessCodex/runs/20261103-cm-dm-low-coop-luna-01/`:
actions in `cm/cm_dm_low_coop_001/attempt-1/state.sqlite`, `events.jsonl`,
`run.live.md`, `result.private.json`, plus its sibling launch log and manifest.
Observed: actor denied immediate clinician contact/class delivery; final patient
reply declined enrollment for now; persisted outreach remained tentative with
consent false. Ended unresolved at 48 model calls / 80 tool operations, no terminal
case mutation. Stop review began after call 44 and returned incomplete.

Reviewer diagnosis substantially supported, with qualifications:
- Dialogue's old blanket prohibition could discourage accurate descriptions of
  future program services. Behavioral causation is a prompt-design inference,
  not something the saved trajectory proves independently.
- Old progress logic compares whole business results per query or latest tool;
  changing query/rank/cache/timing metadata masks source duplication. Existing
  exact repeats produced some feedback, but no progress recovery was recorded.
- Owner context already had an absent-catalog-operation hint. It was insufficient
  in this trajectory; guidance was not entirely absent. Extend the distinction
  consistently to conversation, handoff, stage and stop reviewer.
- 23 searches total are preserved in actions, including dialogue and recovery
  helper searches; this is not 23 wholly post-call successful searches.

Policy contents were assessed only through the authorized saved observations.
No policy interpretation or CM disposition is selected by code.

## Implementation and source map

- `HealthHarnessCodex/health_harness_codex/cm_guidance.py`: common program,
  capability and stop-review guidance, quoted verbatim below.
- `roles.py`, `dialogue_worker.py`, `assignment.py`: apply program/capability
  distinction to CM owner/helpers, dialogue question and stage guidance.
  Dialogue handoff adds a metadata-only capability rule; grants remain unchanged.
- `working_set.py`: reinforce existing complete-catalog hint, preserve distinction
  between current execution and policy-supported services after enrollment.
- `retrieval_progress.py`: successful recognized hybrid-search/read-file/read-many
  shapes produce case-local source identity/version/range/text-hash coverage.
  Search scores, rank, caches, timings and query/size parameters do not establish
  new source information. Headers and qualifying passages count, too. Full-file
  SHA versions permit covered subsets; unversioned passages use exact hashes.
  New paths, new passages, extended reads and changed file versions remain new.
  Unknown shapes/errors retain old repeat behavior. No result filtering or tool
  blocking. Store hashes/ranges/receipt IDs, not another copy of source text.
- `planning.py`: integrate coverage with existing exact repeats and replanning
  feedback. Aggregate no-new-source operations across query variants.
- `recovery_audit.py`: explicit member-decision/capability distinction in helper
  question and owner feedback. Phase metadata bounded to domain/responsibility
  to avoid duplicating long stage guidance in the 4,000-character question.
  Read-only review, budgets, completion/evidence checks and owner choice retained.
- New tests `test_retrieval_progress.py` (13), `test_cm_program_guidance.py` (3).
  Existing dialogue/recovery tests assert the guidance reaches real helper inputs.

## Exact shared guidance

### Program description

> When answering the person's request, explain relevant program services supported by retrieved program or care-plan policy, clearly framed as part of enrollment and care planning: coordination with the member's clinicians, education/resource referrals and follow-up when that policy supports them. Accurately describing post-enrollment services is different from claiming an action was completed or promising it will happen immediately. Do not claim completed actions or promise immediate contact or delivery without supporting tools and observations. Do not invent schedules, names or availability, guarantee outcomes, pressure or manipulate participation, or bypass consent or privacy rules.

### Capability limits

> Use the complete actor tool catalog, including discoverable tools and explicit owner/delegate boundaries, to determine executable capabilities. If a needed capability is absent, state that execution limit once; do not search policy to manufacture an unavailable capability. This limit does not negate policy-supported program services after enrollment. Use already retrieved policy, or retrieve a genuinely unread applicable passage, to choose and cite the permitted policy path and remaining duties. Do not invent delivery or contact receipts.

### Stop review

> Distinguish a member decision limiting participation from missing information or an unavailable execution capability. Do not treat a member decision as a reason to search for unavailable capabilities or seek consent through pressure. Review applicable policy and observed permissions for remaining documentation, communication and closure duties; the owner chooses and cites the policy path. A permitted exit does not establish that the requested goal was met. Preserve unmet requirements and all completion and evidence checks.

## Executed offline verification

From `C:/Projects/BigData/HealthHarnessCodex`:

```powershell
& C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -m unittest discover -s tests -q
```

**798 tests passed, 95.946 s, zero failures/errors.** Includes 16 new tests.
Ignored log: `HealthHarnessCodex/runs/20261103-cm-general-fixes-unittest.log`.
Initial focused retrieval test had one test-isolation failure: it reused the same
state for separate exact-repeat scenarios. Resetting each scenario fixed it;
the full final suite passes. `git diff --check` passed (line-ending notices only).

Read-only offline replay of 53 saved actions in SQLite row insertion order,
matched to original evidence IDs/model-call numbers; comparison against HEAD's
unmodified detector, not a resumed world or a new model trajectory:

```powershell
& C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 runs/replay_cm_retrieval_progress.py
```

Replay script and result are ignored, local only. Result:
`runs/20261103-cm-general-fixes-replay.json`. Old feedback: 1 search, 2 file reads.
New: 15 searches, 5 file reads. First newly flagged file read at call 8 (action 13);
first newly flagged search at call 13 (action 18). The search totals include one
preexisting exact-repeat error response; source-coverage detection adds feedback
on 14 successful searches. No source text printed or copied to the report.

## User-only fresh attempt and native key-free check (NOT executed)

The commands below start exactly one attempt with the default harness backend,
Luna/high, helpers/recovery auto, 100/500, no context cap, 180/600 timeouts,
Codex Luna/high patient, network none and grading deferred. Native executable is
pinned to the same existing path recorded in -01. Batch CLI fixes high effort
and defers grading; simulator defaults match the saved manifest. Existing
retrieval runtime configuration is reused. Do not launch a second attempt on
failure automatically. Fresh target directory did not exist at verification.

Run in a normal PowerShell window after review:

```powershell
Set-Location C:/Projects/BigData/HealthHarnessCodex
& C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -m health_harness_codex.batch `
  --dataset-root ../Dataset/chi-bench `
  --run-dir runs/20261103-cm-dm-low-coop-luna-02 `
  --domains cm --task-id cm_dm_low_coop_001 --attempts 1 --concurrency 1 `
  --actor-backend harness --model gpt-6-luna `
  --composition helpers --recovery-helper-policy auto `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --timeout 180 --active-timeout 600 `
  --simulator-backend codex --simulator-request-timeout-seconds 180 `
  --codex-executable C:/Users/prath/AppData/Local/OpenAI/Codex/bin/22cfb1d302613eae/codex.exe
```

After that attempt is settled with a saved snapshot, native key-free structural
check (it uses Docker with network none; no semantic judge/model/keys):

```powershell
& C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 runs/check_structural_no_judge.py 20261103-cm-dm-low-coop-luna-02
```

## Unverified and next steps

Reviewer reviews changes and commits if accepted. User launches the one fresh
attempt and native check above. No evidence yet that the actor responds to the
new feedback, reaches a policy-supported disposition or meets the requested goal.
Offline tests establish harness mechanics only; replay establishes warning
locations, not counterfactual clinical success. Actual Docker/runtime/auth and
native check remain unverified this session. Preserve -01 unchanged and keep any
new evaluated result separate from these assisted development checks.
