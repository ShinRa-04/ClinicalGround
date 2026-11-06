# HealthHarnessCodex

> **Published copy:** the modules that used Codex as the model (`codex_provider.py`, `codex_transport.py`,
> `codex_smoke.py`) and the Claude Code CLI adapters were removed before publication because they were a
> subscription workaround, not part of the harness design. `codex_provider.py` here is a small API-key
> adapter with the same interface (OpenAI-compatible endpoint, `CLINICALGROUND_API_KEY`); it is untested
> end to end. See the [root README](../README.md#running-it-yourself) for setup and the disclaimer.

**Current status, November 3: documentation only.** The latest tested code is
`d77870c` (743 software tests). Current runtime-guard edits are unfinished and
untested; do not treat the working tree as a verified release. Attempt -21 lost
its Docker world, has no valid deferred snapshot, and requires reconciliation.
No CM assessment/finalized-plan success is claimed. See
[current state and restrictions](../Progress/CM_RUNTIME_FAILURE_20261101.md).

**November 1 chart handoff and repeat detection:** CM dialogue receives a scoped
index of the already-observed chart, with original source IDs and document/field
pointers; bodies remain retrievable through the existing guarded tools. Existing
record review and formal assessment are distinct; consent, privacy and stop rules
remain intact. The worker checks the whole relevant communication protocol,
including duties that cannot be performed after a counterparty ends contact.
Unchanged-read feedback now tracks individual queries as well as latest tool
results, so alternating work/blocker views cannot masquerade as new information.

**October 30 CM handoff and stop-record repair:** the conversation worker receives
a small map of the case owner's actual assessment/care-plan tools and scoped
receipt references. This describes the wider workflow without granting the
worker those tools. Support is explained as potentially complementary to the
patient's own actions, with policy and consent still required.
Explicit worker-authored waiting/blocked lists placed at the final JSON's top
level can be relocated into `stop_assessment` without changing their values.
Original submissions and normalization receipts remain available. Missing,
incorrect or conflicting work acknowledgment still rejects; it never completes
unfinished clinical work. See [repair evidence](../Progress/CM_RESEARCH_REPAIR_PLAN.md).

**October 28 response recovery:** a JSON whitespace loop now stops before tool
dispatch. If this occurs on a tool-proposal request, the next budgeted generation
omits Codex's native output schema and requests the same JSON envelope in text.
The original tool contracts remain in the input. Host parsing, argument-schema
validation, undeclared-parameter rejection, identity, provenance and write guards
remain authoritative. Partial replies never execute. The patient simulator is
unchanged. `argument_decoding_mode=host_validated` identifies this recovery mode.
See [actual trials and verification](../Progress/CM_RESEARCH_REPAIR_PLAN.md).

**Native stream interruption:** owner and delegated workers retry a classified
`responseStreamDisconnected` once after confirmed process cleanup and no proposal
dispatch. Both generations count toward existing budgets. A second consecutive
disconnect stops; quota/authentication failures and uncertain writes do not use
this recovery. `MODEL_RETRY` and the recorded call numbers make recovery visible.

**October 24 response-boundary audit:** Codex proposes only tool names/arguments;
code assigns internal request labels. Malformed proposal envelopes cannot partly
dispatch and get bounded correction; failure stages and reported usage survive
rejection. Simulator requests publish complete JSON without overwriting a winner.
628 tests and native synthetic/platform probes passed. See
[findings, severity and execution limits](../Progress/RESPONSE_BOUNDARY_AUDIT.md).

**October 24 completion correction:** audit and finalization share one assessment
of the pinned contract and obligations. Pending-information endpoints require
an explicit, source-backed explanation that no useful permitted action remains;
ambiguity or a pending status alone cannot close the testcase. External waiting
permission is declared in the contract. Original clinical sources remain required;
local audits create no evidence IDs. See [implementation and verification](../Progress/COMPLETION_REPAIR.md).

**October 24 stage and assignment repair:** the owner now receives observed-stage
guidance and a readonly structural assignment audit each call. A nurse pend does
not waive an assigned MD decision; a verified MD information-request handoff is
supported without forcing approval/denial. Provider deferral is restricted to PA.
`--recovery-helper-policy auto` (batch default) permits one bounded readonly
blocker audit in helper mode, sharing case budgets; `off` disables it. Domain
and clinical decisions remain with the model. 596 regression tests and actual
Luna synthetic probes passed; no new dataset score is claimed. See
[design, evidence, limits and single-case command](../Progress/UM_ASSIGNMENT_STAGE_REPAIR.md).

**October 24 recovery and delegation:** the batch runner now defaults to
`--composition helpers` and freezes the selected mode. Owners can delegate
scoped tool-using jobs, with separate contexts, shared budgets and explicit
write permissions. Source-backed prerequisite records, case working notes,
clear absence feedback and unchanged-result replanning are implemented.
Real Luna synthetic delegation completed with the long document confined to
the helper context; no new dataset score is claimed. See
[implementation, graph and verification](../Progress/IMPLEMENTATION_RECOVERY_HELPERS.md).

**October 24 parameter repair:** undeclared top-level names are rejected before
dispatch for named tool parameters, with valid-name correction feedback.
Explicit open maps and nested data maps remain supported. This fixes the
confirmed silent-empty-save loop in the interrupted UM t033 attempt; 542 tests
pass and real Luna synthetic correction saves once. See
[cause, user decision and verification](../Progress/T033_03_SAVE_PARAMETER_REPAIR.md).

**October 24 protocol repair:** Codex tool proposals use direct JSON argument
objects constrained by tool-specific schemas. Bounded format correction renews
after new successful tool observations. Full 535-test suite passes; real
Luna-high synthetic engine validation recovers two injected format errors while
executing its update once. A fresh dataset rerun is still needed. See
[implementation and verification](../Progress/CODEX_ARGUMENT_FORMAT_REPAIR.md).

**Current checkpoint, October 22:** a fresh t012 execution at `9fd27cd`
actually submitted its authorization and saved one packet. Its key-free
deterministic check passed 8 checks with 0 failures and 1 not applicable;
semantic judging was not rerun. The earlier separately evaluated t012 failed
case status (strict score 0), which exposed the readiness-vs-submission bug.
Ordinary referrals can no longer complete at readiness alone. Scoped document
path resolution and application-error reporting are repaired. Context efficiency
remains unresolved. All full-dataset runs remain stopped; historical container
state and exact evidence are in [the handoff](../Progress/HANDOFF.md) and
[the latest repair](../Progress/POST_JUDGE_REPAIR.md).

For a source-grounded explanation of the dataset and actual implementation,
including agent/tool graphs and the complete role/tool reference, start with
[the shareable HarnessGuide](../HarnessGuide/README.md).
Custom configured CLI runs now require a scope-matched,
operator-authored `completion_contract`; the offline demo supplies its own
synthetic contract. Do not auto-resume the stopped run after source changes.
Read [current handoff](../Progress/HANDOFF.md) and
[completion-validation audit](../Progress/COMPLETION_VALIDATION_DEBUG.md).
The dated execution/evaluation notes below are historical.

**Latest execution logging:** terminal lines now identify task/domain/attempt,
setup versus actual model/tool work, waiting times, snapshots and batch counts.
The default final output is concise; `--json-summary` restores the final full
JSON. The user selected a fresh **75-task** attempt in
`runs/20261021-full-dataset-03/`. See [logging and exact command](LOGGING.md).
That run has not been launched by root. Earlier cases and scores remain separate.

**October 21:** normal batch CLI execution now saves immutable final-state
snapshots and stops each world, so grading can start after all selected actor
tasks finish. Root passed **278 software tests** and a real key-free
snapshot/stop/offline-verifier replay check. OpenRouter Batch remains blocked:
five tiny Opus 4.7 submissions were rejected with HTTP 400 before inference;
the key still reports **$0.00 used / $0.50 remaining**. See
[deferred grading and exact evidence](../Progress/DEFERRED_JUDGING.md).
These checks do not establish a new benchmark score or full-dataset execution.

**All-domain integration, October 20:** the shared Codex model adapter now has
PA/provider, UM and CM execution profiles plus a 75-task batch runner. Root
passed 232 harness tests and 7 packet producer tests; actual fresh all-domain
execution is the next verification stage. The previous one-UM-task scores
below remain historical evidence, not a new full-dataset result. See the
[all-domain handoff](../Progress/HEALTH_HARNESS_ALL_DOMAINS.md) for commands,
case-binding behavior, coverage and benchmark inference requirements.

This is a **copy of HealthHarness**, iterated into a Codex-backed variant. The original folder is unchanged. The package is independently named `health_harness_codex`, and the installable distribution/command is `health-harness-codex`.

The existing PA/UM/CM owner loop, case memory, role catalogue, context reduction, evidence/obligation tracking, operation gates and recovery journal are reused. The new adapter obtains structured decisions from an application-owned Codex App Server session; our engine executes proposed harness tools. It does not attach to this desktop conversation.

**Current evaluation:** **187 software tests pass**. Frozen source `03c845d` passed the unchanged official verifier in **3/3 fresh trials, 21/21 checks each**, on one public UM development task. Its single-task pass@1/pass@3/pass^3 are all 100%; no benchmark-wide or held-out rate is established. Two runs retained local `unresolved` because the model omitted the required structured completion record; one was locally complete. Official results and local status remain separate. Earlier failed versions are preserved. Read [measured pilots](../Progress/HEALTH_HARNESS_PILOT_RESULTS.md), [evaluation procedure](EVALUATION.md) and [software verification](VERIFICATION.md). No submission packet or PR has been produced.

## Quick start

Python 3.11+ is the target; checks here used bundled Python 3.12.14. From this folder:

```powershell
python -m health_harness_codex --demo
python -m unittest discover -s tests -v
```

The default/demo is offline and scripted. Live Codex checks are separate opt-in commands. On this machine the verified official binary is:

```powershell
$codexExe = 'C:/Users/prath/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe'
python -m health_harness_codex --codex-probe --codex-executable $codexExe
python -m health_harness_codex --codex-smoke --codex-executable $codexExe --codex-instruction-source 'C:/Users/prath/.codex/AGENTS.md'
```

Use `C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` in place of `python` on this workspace if needed. Other machines need their own verified official executable path and supported sign-in. A binary may move after an app update; no installation-specific path is silently discovered or assumed by the adapter.

`--codex-probe` initializes the native server and reports sanitized configured-account status, without a generation turn. It does not prove model entitlement or complete isolation. `--codex-smoke` performs real account-backed inference against one synthetic observation tool. It consumes account usage and defaults to two harness completion calls. It cannot access official task tools. A non-complete result exits nonzero; it is never relabelled as success.

## Instruction and session boundaries

Every completion, including helper analysis, gets a new owned process, temporary working directory and ephemeral thread. The adapter does not resume an old chat or copy/read authentication files. It disables known shell, agent, plugin, connector, web, skill and memory capabilities, explicitly disables discovered inherited MCP/plugin/skill entries, and rejects server requests or action-capable response items.

Native Codex still reports the user's global AGENTS.md even with project guidance disabled. Unknown instruction sources are rejected **before case input is sent**. The repeated `--codex-instruction-source FILE` option approves only explicitly named general instruction files by their current SHA-256 for that invocation. In a persisted run config, pin the exact path and SHA-256 under `allowed_instruction_sources`; changed or unknown sources fail. Never approve patient notes, credentials or episode summaries as shared instructions.

The verified local approved file contains general project-continuity and progress-reporting preferences, not patient records. It was retained unchanged as a known shared instruction prefix. This is a controlled **Codex-backed harness**, not a claim of raw-model prompt equivalence or a proof against malicious local filesystem/process interference. See [architecture](ARCHITECTURE.md).

## Configured case execution

Copy [config.example.json](config.example.json) to ignored `run.local.json` and replace the actual task, scope, paths and authorized MCP endpoint. The important new configuration is:

```json
{
  "provider": {
    "type": "codex_app_server",
    "executable": "<absolute path to the official Codex executable>",
    "model": "gpt-6-luna",
    "reasoning_effort": "high",
    "timeout": 120,
    "allowed_instruction_sources": {}
  }
}
```

No `key_env` or API key is required by this backend. An existing supported native account sign-in is required; the code never launches a login browser automatically. Replace the empty instruction map only with reviewed ordinary instruction-file paths and their approved hashes where the native session reports them.

```powershell
python -m health_harness_codex --config .\run.local.json --live
python -m health_harness_codex --config .\run.local.json --live --resume
```

These run the copied harness on the host/controller against the authorized MCP endpoints in the config. They require real task scope and tool availability. All normal patient isolation, action journal and case recovery gates remain in use. The compatible HTTP provider remains available with `type: openai_compatible` for inherited tests or separately configured usage; it still requires its own provider credentials.

## Resource limits and errors

With CM `--composition helpers` (or `team`) and `--recovery-helper-policy auto`,
the first proposed patient message after an observed active session starts the
CM-04 conversation worker. It has a separate context and uses only selected
reads and the ordinary guarded `send_message` tool. The owner's original draft
is explicitly not sent; delegated messages have their own journal entries.
The worker handles the permitted conversation/interview, returns original
source references, and cannot save outreach/assessment/plan/closure records.
The owner must verify the transcript and complete the remaining work. Old
owner writes from before delegation are fenced until a new owner turn.
Combined mode retains the single-owner path. This is presentation/responsibility
separation, not another patient model or a modification of the benchmark.

Patient dialogue has no harness-specific cumulative call, input-character or
world-duration quota by default. For the experimental Codex simulator, zero in
`--simulator-max-model-calls`, `--simulator-max-total-chars` and
`--simulator-world-deadline-seconds` means disabled. Per-request timeouts and
payload bounds, overall owner/helper budgets, and the benchmark's own session
limits still apply independently. The benchmark environment is not modified.

`--model` selects the case worker and its responsibility workers. The experimental
Codex patient remains independently pinned to Luna/high; changing the case-worker
model does not change the patient. Both selections are recorded separately in the
frozen manifest. Codex sign-in/model availability and account usage still apply.

For CM dialogue, three consecutive identical completed care-manager/patient
exchanges stop further patient dialogue in that attempt. Matching ignores case
and whitespace, preserves punctuation/numbers and does not detect paraphrases.
Different questions with the same reply are not identical exchanges. Cached
tool readbacks do not count again. `DIALOGUE_REPEAT_STOP` records original source
IDs; the stop survives resume and blocks reopening another outreach session as
a workaround. It is a harness stop, not patient refusal, consent, or a patient
stop signal. Other permitted documentation/investigation can continue, and the
requested outcome is still checked separately.

The existing engine counts owner/helper completion requests and harness tool operations. The Codex adapter adds operation deadlines, bounded JSON/queues/output characters, owned-process cleanup and strict response parsing. It reports usage fields actually emitted by Codex. **A strict model output-token cap is not verified for this Codex route**: `max_output_tokens` is advisory to the model, while returned characters are bounded. It is not a hard dollar cap or an exact count of Codex-internal retries/requests.

Timeouts, malformed output, unapproved instructions, changed source hashes, wrong thread/turn IDs and unexpected Codex actions fail explicitly. Unknown outcomes of harness effects continue to require real readback/reconciliation; the adapter cannot bypass that journal.

## Benchmark boundary

The standalone path now connects the host harness to the official actor MCP inside an explicitly owned runtime container using `docker exec`. The Windows Codex process stays on the host. No host port exposure or API-key transfer is needed. This path is distinct from Harbor integration: the copied Harbor launcher continues to reject unsupported Codex execution.

Only explicit public PA/UM task selection and payer case binding are supported by this standalone runner. It checks the case against the observed queue, preserves the original task's entire scope, and records an actual determination readback separately from the harness claim. Patient/P2P simulators may still need their own credentials; account-backed actor inference does not provide those. The standalone command does not grade or submit. Local official grading is a separate operator stage documented in EVALUATION.md; public submission remains unauthorized.

```powershell
python -m health_harness_codex.standalone --container <owned-running-container> --task-dir <public-task-directory> --allow-case-subject-namespace --run-dir <absolute-path-under-this-folder/runs/new-attempt> --codex-executable $codexExe --codex-instruction-source 'C:/Users/prath/.codex/AGENTS.md'
```

Without `--case-id`, the runner selects a unique matching live queue case from the public task's provider and procedure; missing or ambiguous matches fail closed. This matching is implemented, not validated across every benchmark task format. An explicit `--case-id` is available for operator-directed development and is recorded separately.

When the actor exposes a case ID but no patient ID, the default is to stop. `--allow-case-subject-namespace` explicitly permits a case-derived internal isolation key. It is labeled as a namespace, never asserted or passed to tools as an actual patient ID. Case-bound tools and the existing response identity checks remain required. Use a fresh attempt directory; the runner never starts/stops containers or automatically retries uncertain writes.

A patient ID exposed later may be bound separately only by selected actor tools that explicitly associate it with the same case. The binding and evidence source are persisted without changing the namespace/key. Contradictory IDs and model-authored workspace data cannot establish a binding. Approved reference directories can now be listed within the same read-only roots.

Scoped `workspace.read_pdf` extracts text-layer pages using the existing container parser; it reports source hashes, page/offset continuation and extraction limits. It does not perform OCR or validate visual layout. `workspace.search_files` finds approved text references; `case.search_evidence` searches already-observed case results by their original evidence ID. `case.read_evidence` rehydrates those same sources without creating new evidence. Context projection preserves raw observations when they fit and uses partial previews only under budget pressure. DeepSeek OCR is not installed or required for the verified text-layer PDFs.

For an explicit audit continuation, use `python -m health_harness_codex.continuation --help`. It copies a settled source run through read-only SQLite backup into a fresh run directory and verifies that the live public determination still matches. Supply an ignored `--note-file`, explicit cumulative non-reducing budgets, source/destination run directories and the same task/container/native connection options. It archives previous completion and counters; it does not overwrite the source or silently reopen a completed case. Completed routing/disposition actions are unavailable during the audit. Restarting the observed runtime resets its actor world; continuation refuses a mismatched determination.

Read [evaluation and improvement](EVALUATION.md) for run artifacts, failure categories, comparisons, reproducibility limits, and the distinction between operational metrics and clinical/benchmark quality. The static [actor/workflow map](CHI_BENCH_MAPPING.md) remains useful, but its inherited HTTP-provider packaging notes are not evidence of a Codex Harbor trial.

## Code and provenance

- `codex_transport.py`: hidden stdio process, JSON-RPC correlation, bounded I/O and process cleanup.
- `codex_provider.py`: fresh session policy, instruction-source pinning, strict proposed-action replies and usage.
- `provider_factory.py`, `cli.py`: backend selection, key-free Codex configuration and explicit live modes.
- `codex_smoke.py`: small genuine-inference check with a synthetic tool.
- Existing engine/store/context/roles/tools: copied rather than rewritten. Role data remains identical.
- [FORK_BASELINE.json](FORK_BASELINE.json): hashes of all 33 original tracked source/document files at duplication.
- [Progress handoff](../Progress/HEALTH_HARNESS_CODEX.md): implementation ownership, commands and actual execution evidence.

Build artifacts, protocol schemas, private configs, bytecode and run data remain ignored. Historical copied evaluation/contract documents describe the original baseline at their stated commit; this README and VERIFICATION.md describe the Codex variant.
