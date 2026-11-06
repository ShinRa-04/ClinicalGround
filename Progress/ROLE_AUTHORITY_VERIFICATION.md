# Role authority Phase 2 verification

2026-11-03. Phase 1 revision and Phase 2 implemented and verified offline on
`role-authority`, based on `514a890f7d1f03537de7c1b5f87ec149ceba9306`. No commit.
The user's delegated Claude decisions are the binding review record; see
[approved roles and reasons](ROLE_AUTHORITY.md) and
[before/after prompt measurements](ROLE_PROMPT_BASELINE.md).

## Scope and decisions

All 66 roles have affirmative authority, a short professional approach, hospital
mapping, status_label and model_visible. CM-04 uses the exact delegated text;
CM-02/05 composites, UM-04/05 split and CM-14/15/16 redefinitions are retained.
CM-17/18/19 prior substantive contracts and all 66 boundary strings are unchanged.
The only executing_worker labels are CM-04 and SH-10. Six specified SH safeguards
remain cataloged but are excluded from model prompts and delegation; case.get_role
can still retrieve their current-domain/shared contracts.

The blueprint is the source of truth. Runtime-only overrides are explicit in
`HealthHarnessBlueprint/runtime_overrides.py`, currently empty. The former
CM-04 runtime status difference is superseded by the shared status_label.
No deviation from the delegated decisions was needed.

## Architecture and changed files

- Catalog source/generation: `HealthHarnessBlueprint/micro_roles.py`,
  `runtime_overrides.py`, `tools/build_blueprint.py`, `tools/validate_blueprint.py`;
  generated `data/micro_roles.json`, `MICRO_ROLES.md` and
  `HealthHarnessCodex/health_harness_codex/data/micro_roles.json`.
- Runtime, under `HealthHarnessCodex/health_harness_codex/`: `roles.py` delivers
  authority in visible owner summaries and full substantive helper contracts;
  `helper_jobs.py` rejects hidden safeguard delegation; `assignment.py` adds
  scope/authority/approach to CM packets and CM-09 to outreach; `cm_guidance.py`,
  `working_set.py`, `planning.py`, `recovery_audit.py` consolidate shared caution
  and remove CM language from shared paths; `dialogue_worker.py` caps the rendered
  stage question at 3,000 characters by trimming only the assignment excerpt.
- Offline evaluation tools: `evaluations/build_role_draft.py` exports the final
  approved record from the blueprint while retaining mapping provenance;
  `validate_role_draft.py` validates final fields and pinned original/new
  redefinitions; `prompt_metrics.py` adds current offline prepare measurements
  and appends after-numbers without replacing Phase 0 data.
- Tests: new `tests/test_role_authority.py` (11 tests); updated
  `test_cm_program_guidance.py`, `test_dialogue_worker.py`,
  `test_conversation_probe.py`, `test_goal_planning.py`,
  `test_recovery_audit.py`, `test_retrieval_progress.py`.
- Documentation: `ROLE_AUTHORITY_DRAFT.md` converted to `ROLE_AUTHORITY.md`;
  `role_authority_draft.json` retains the historical filename with final fields;
  `ROLE_PROMPT_BASELINE.md` preserves Phase 0 and adds the Phase 2 table;
  this file is the implementation handoff.

The pre-existing conversation probe implementation and its prior documentation
were reused, not rewritten. The existing dirty `Progress/HANDOFF.md` and
unrelated `.playwright-mcp/` files were left untouched. No changes to
`HealthHarness/`, `Runner/` or `Dataset/`.

## Executed verification

| Check | Result | Duration |
| --- | --- | ---: |
| Full offline unittest discovery | 817 tests, OK | 72.025 s |
| Focused authority tests | 11 tests, OK | 0.135 s |
| Blueprint validator | 66 roles; 97 hospital-role mappings; 529 local links and 293 anchors; passed | 0.299 s wall |
| Final role record validator | 66 IDs; 56 mapped and 10 code safeguards; 18 redefinitions; zero errors or action-list suspects | 0.109 s wall |
| Prompt metrics plus two current offline prepares | All six owner budgets passed; both prepares passed | 0.541 s wall |
| FORK_BASELINE verification | All 33 original HealthHarness SHA-256 values match | not timed |
| Git whitespace check | passed | not timed |

The role validator's maximum authority length is 342 (CM-04's explicit exception);
maximum approach length is 191. Every other authority is at most 160 characters.
Authority tests also compare boundaries byte-for-byte with the HEAD catalog,
check generated blueprint/runtime equality after only documented overrides,
exercise hidden-role retrieval versus delegation, check required field rejection,
enumerate all five caution protection families and check precedence/caution once
per owner/helper system message. Existing consent/privacy/identity, provenance,
fencing, repeat detection, isolation and closure mechanics remain covered by the
full suite. Lexical/pattern checks cannot prove absence of every imaginable name
or semantic patient reference; the text also received direct implementation review.

Initial full discovery: 816 tests in 67.243 s, two failures from old assertions
(the outreach packet now includes CM-09; the retrieval nudge now references the
central system capability rule). Those assertions were corrected without changing
guard behavior. Initial and successful final logs are preserved separately:
`HealthHarnessCodex/runs/role-authority-full-tests.local.log` and
`HealthHarnessCodex/runs/role-authority-full-tests-final.local.log`.
No failed benchmark trial or evaluated result was created.

## Offline probe evidence and limits

`conversation_probe.prepare_probe`, mode `current`, successfully rebuilt:

- `runs/20261103-cm-dm-low-coop-luna-03`, patient reply turn 4.
- `runs/20261103-cm-dm-low-coop-luna-01`, patient reply turn 7.

Each has a 7,361-character CM-04 system message and 2,493-character question,
total **9,854**, versus the Phase 0 saved system/question total **10,980**
(6,572 + 4,408). Both contain the exact new CM-04 authority in the system message.
Saved database SHA-256 values remained unchanged. These prepares use an in-memory
store and capture model, with a tool inventory that refuses dispatch. Only sizes
and booleans were exported; no dialogue, patient facts or protected policy text
was copied into tracked files. Full sanitized metrics remain local in
`HealthHarnessCodex/runs/role-authority-metrics-final.local.txt`.

The largest owner growth is UM/helpers at +14.44%; all six combinations pass the
+15% budget. See the linked baseline for every before/after value. The capped
question test also uses long and escaping-heavy synthetic inputs, rather than
depending on a short fixture's accidental margin.

Not executed: Docker, a live model, a dataset trial, a judge, a deployment or a
commit. No clinical or benchmark success claim follows from these software checks.

## Reproduce and continue

Bundled interpreter:
`C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
From the repository root, run the blueprint generator, approved record exporter,
blueprint validator, role record validator and prompt metrics script with `-X utf8`.
For prompt metrics, use `--after-report Progress/ROLE_PROMPT_BASELINE.md` to retain
the before-numbers. The metrics script performs the two offline prepares only;
it does not call the live probe CLI.

From `HealthHarnessCodex/`, the full test command is:

```powershell
& 'C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -m unittest discover -s tests -q
```

Implementation owner: Codex, without sub-agent delegation. Next owner: Claude
reviews the concrete diff and verification evidence and handles any later commit;
the user owns live probe/trial execution under separate authorization. No active
implementation blocker remains. Live behavior, PA/UM behavioral regression and
benchmark outcomes remain unverified. Root HANDOFF.md remains reviewer-owned.
