# Healthcare harness continuation

**Current November 3: documentation only.** The user has not authorized resuming
implementation, tests or runs. Read [HANDOFF.md](HANDOFF.md) and
[the current -21 incident/state](CM_RUNTIME_FAILURE_20261101.md). Last tested code
is `d77870c`; current runtime-guard edits are unfinished and untested. The CM goal
is still unmet. Do not execute historical commands or recreate past automations.

**Historical October 20 checkpoint:** frozen actor source `03c845d` scored **3/3 official passes, 21/21 checks in every trial**, on the same public UM development task. Its single-task pass@1/pass@3/pass^3 are all 100%; this is not a full-dataset or held-out result. Root passed **187 software tests** (20.628 seconds) and matched all 33 original harness hashes. Two trials retained local `unresolved` because the model returned prose without the required structured completion record; the official grader independently passed their actual worlds. The third was locally complete. All three worlds were stopped after official receipts and integrity-checked SQLite backups. This dated result does not describe today's CM state. See [measured pilots](HEALTH_HARNESS_PILOT_RESULTS.md) and [official evaluation](HEALTH_HARNESS_OFFICIAL_EVALUATION.md).

## Historical receipts

The following dated sections preserve earlier implementation, pause and execution states. Their execution authorizations and automation receipts are historical; the latest user restriction and current HANDOFF take precedence. Do not resume any old handle or replay a saved journal against a restarted world.


**Historical pause snapshot.** The 05:00 scheduled continuation executed. Current outcome, retained artifacts and next steps are in [the standalone run receipt](HEALTH_HARNESS_STANDALONE_RUN.md). Do not rerun the commands below against the retained changed world as if it were untouched.

The user explicitly requested stopping everything because their usage limit was ending, and scheduling continuation for 05:00 today (October 19, Asia/Calcutta). Work stopped around 01:05 IST. The real_case_bridge agent was interrupted; other agents had completed. The owned runtime container was gracefully stopped and inspected as `exited`; it was not removed. No actual model-driven dataset case has run yet. Do not interpret runtime bootstrap as task completion.

An ACTIVE one-time thread automation was created: `resume-healthcare-harness-at-5-am`, daily at 05:00 with COUNT=1. Resume in this chat, not a separate project/task. Do not create a duplicate schedule.

## Authorized objective

Complete one genuine, unscored standalone dataset attempt through HealthHarnessCodex using the existing native Codex account sign-in, GPT-6 Luna/high. User also requested a reusable evaluation method for improvement. No API key is available. Do not invoke an official judge or submit anything. Original HealthHarness stays unchanged. Commit authorized source/test/documentation changes when reviewed; current work is saved but uncommitted.

## Saved source and verification state

Baseline commit: cc7b786. New files under HealthHarnessCodex/health_harness_codex/: docker_bridge.py, standalone.py, evaluation.py. New tests: test_docker_bridge.py, test_standalone.py, test_evaluation.py. Progress/HEALTH_HARNESS_CODEX.md also modified.

Luna-high bridge agent reports 7 bridge + 5 standalone synthetic tests and py_compile passing. Evaluation agent reports 8 focused tests passing. These are agent-reported checks; root still needs to review the final edits and run appropriate integration/software checks. Previous committed duplicate had 64 tests. Do not claim a benchmark success rate from software tests.

Bridge uses fixed Python scripts via docker exec with JSON stdin, no model-written shell; actor MCP is internal localhost:8100. Workspace tools restrict writes to current case/payer/scope-key and reads to approved handbook/tool reference/current-case incoming/shared handoff. Agent added container ownership/task preflight, source and initial actor-payload hashes, recording before discovery, setup-failure reports, explicit case selection, and journal status counts. Review final source before use.

Evaluation records safe event names/timing, reported usage, context hashes/sizes, tool attempts versus returns, failure classes, journal outcomes, private results, and public-tool terminal readbacks. `official_success`/`official_score` remain null. Comparison reports operational changes and comparability limits, not clinical correctness. Unknown action effects must come from authoritative journal status when available. Scope/schema rejection is separate from unknown effects. Payloads stay in ignored runs; no patient bodies in live Markdown.

## Runtime and exact run

- Container: bigdata-health-codex-um-20261019-first; label com.bigdata.workspace=BigData/HealthHarnessCodex. Stopped, retained.
- Image: bigdata-chi-bench:runtime-4444a07, ID sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66.
- Network none, no provider keys passed. Bootstrap and internal HTTP health 200 passed. All actor tools discovered (41 payer tools). No clinical workflow effects executed.
- Task: Dataset/chi-bench/prior_auth_um/tasks/pa_t012_t012_o001_p01_triage_payer. Its public instruction requires triage THROUGH clinical review, MD decision, necessary P2P and final determination. Routing alone is not completion.
- Current case observed in live actor queue: CASE-E33A4F82; intake INTAKE-0F15FDC2. Exact public provider/procedure match selected the case; no fixture/answer inspection.
- Ignored run directory: HealthHarnessCodex/runs/20261019-um-triage-first/. Contains setup.json, initial run.live.md, container_logs/, bootstrap-queue.private.json and bootstrap-current-case.private.json. Queue holds other cases; do not send unrelated records to the model.

## Immediate unresolved blocker: patient identity

The queue, get_intake_case, and permitted review.get_nurse_review_data response for this case do NOT expose a patient ID. Root searched only current-case actor document text for Patient ID/Member ID labels; no match. The bridge currently requires patient identity and tries nurse/MD readbacks; this may still fail. Do not inspect hidden fixtures, source clinical semantics, expected answers, provider endpoints or world DB to manufacture one.

Possible explicit design resolution: support a documented, opt-in case-subject namespace such as case-subject:CASE-E33A4F82 for case-bound UM tools. This would be an isolation namespace, NOT an asserted real/FHIR patient ID. Record missing physical identity, observed case provenance and scope limits; guard against explicit contradictory identities. Root has NOT implemented or validated this yet. Determine the sound design on resume, add meaningful tests, and document it. Organization/principal fallback labels likewise represent execution namespaces, not verified staff identities.

## Run commands and limits

Python: C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe (3.12.14), use -X utf8. Run from HealthHarnessCodex with `-m health_harness_codex.standalone`, --container above, --task-dir and --run-dir above as absolute paths, --case-id CASE-E33A4F82, --codex-executable C:/Users/prath/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe, --codex-instruction-source C:/Users/prath/.codex/AGENTS.md. Review CLI for any new option needed for identity handling before running.

Approved user AGENTS SHA256: 1c683adadd4bffe13c4ff0700dc824fd3f3f35c024ffc3b6c68959f887318f96. It contains general preferences; don't edit it or approve unknown instruction sources blindly. Fresh native process/ephemeral thread per completion; own engine executes proposed tools. Output token setting is advisory, not a verified hard cap.

Restart only this owned container when ready. Do not start iGOT, install host compilers, migrate to WSL, expose ports or launch a visible browser. Separate patient/P2P simulator credentials may be required despite account-backed actor inference; if missing, preserve the actual blocker rather than fake the counterpart. No automatic replay of unknown writes. Preserve failed attempts and exact code/version receipts. Save run artifacts before stopping this container again. Update HANDOFF and HEALTH_HARNESS_CODEX with executed evidence and commit tracked changes, never protected content or run payloads.
