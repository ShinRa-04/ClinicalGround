# Evaluating changes to this harness

The standalone runner records the operational trial; a separate authorized invocation of the unchanged official verifier scores its final world. The recorder establishes which tools ran, where execution stopped, and which observations support a local completion claim. It does not itself certify clinical correctness or calculate an official reward. Software tests are a separate layer. [Measured pilots](../Progress/HEALTH_HARNESS_PILOT_RESULTS.md) contains the current numbers and retained failures.

## Competition target

The user clarified that competition evaluation defines the target. The [official scoring contract](https://github.com/actava-ai/chi-bench#reading-the-verifier-output), checked October 19, publishes a strict binary reward only when every applicable verifier check passes. Fractional progress is diagnostic. Therefore `local complete`, terminal actor state, valid citations and software tests must never be substituted for an official reward. Local official grading is authorized; public submission is not. Standard workspace-judge inference has separate credential requirements, but the pinned UM fixture actually exercised here completes its deterministic checks without judge inference or a key. Verify the emitted checks and judge availability for each task; Codex actor sign-in does not provide another provider's credentials.

Derive operational requirements from the public assignment, applicable retrieved policy and tool contracts. Preserve distinctions such as generating versus sending a message. A stronger action absent from those sources must not become an invented mandatory obligation. Conversely, missing tool capability does not justify pretending an actual required action happened. Review cited source passages and validate evidence IDs before trusting either a completion claim or an incomplete audit. `case.read_evidence` rehydrates an original source; it creates no new evidence ID.

Debugging continuations with operator notes are development evidence, not an autonomous competition trial. A final clean check uses a fresh actor world, the original public task, no operator follow-ups and no manually supplied case ID. The runner may select a unique case by matching public provider/procedure text to actor queue metadata; ambiguity fails closed and other queue records never enter the working model's prompt. This bounded selection rule has not been validated on all 75 tasks.

## What gets saved

Every attempt must use a fresh directory under ignored `HealthHarnessCodex/runs/`. Do not commit these files: they can contain protected references and patient information.

| Artifact | Purpose |
| --- | --- |
| `run.live.md` | Progress using model-call ordinals and tool names, without request/result bodies |
| `events.jsonl` | Request timing, context fingerprints, reported usage and tool dispatch outcomes |
| `state.sqlite` | Full case-local conversation, evidence, obligations and action journal |
| `result.private.json` | Local harness result, including unresolved work |
| `evaluation.json` | Operational metrics, version/configuration provenance and public determination readback |
| `run.result.json` | Standalone execution receipt and observed final-state response |

`evaluation.json` distinguishes attempted tool dispatches, returned calls, successful/failed evidence, and unknown journal outcomes. A returned call is not proof of a successful clinical effect. Usage is whatever Codex reports; missing usage is not a measured zero. Context character metrics cover message contents, not an exact tokenizer measurement or all native instruction overhead.

The engine's total tool count also includes local obligation/evidence operations. Proxy dispatch and latency maps cover external/workspace tools; local errors are retained in the case conversation rather than comprehensively broken out by this first report schema. See the [first executed comparison](../Progress/HEALTH_HARNESS_STANDALONE_RUN.md) for the actual outcomes and an original-classification correction retained separately from its raw report.

Failures are grouped as setup, inference, schema/scope rejection, unknown effect, exhausted budget, or incomplete workflow. `locally_complete_ungraded` means only that the local completion gate accepted the model's evidence-linked claim. An explicit nonterminal determination readback overrides that classification to incomplete workflow; missing terminal information remains unknown. `official_success` and `official_score` remain null. No judge is invoked.

## Compare two attempts

From this folder:

```powershell
python -m health_harness_codex.evaluation compare .\runs\baseline\evaluation.json .\runs\candidate\evaluation.json
```

The report compares calls, elapsed time, observed usage, evidence, open obligations and unknown effects. It also checks task instruction, model/effort, budgets, initial actor-payload fingerprint, shared instruction hashes, code version/fingerprint and composition. A matching initial fingerprint covers observed bootstrap payloads only; it is not a complete hidden-world snapshot. The same task or container name does not prove equal starting state. Code/composition changes are experimental factors; other mismatches must be explained before interpreting a delta.

For useful improvement experiments, reset to equivalent fresh environments, change one declared factor, retain failed cases, and repeat across cases and model variability. Compare task completion using an independently permitted evaluator when available. Smaller tool counts or cheaper runs alone do not establish better task performance. Do not tune against hidden expectations or report this one exploratory case as a benchmark estimate.

## Isolation and recovery

Bootstrap selects a unique case from the actor-visible queue. After binding, the case worker's catalogue excludes the all-case queue; direct calls are refused before dispatch. Other-case response quarantine remains enforced. Missing patient identifiers fail by default. The optional case-subject namespace mode uses the observed case ID solely as an internal isolation key; it asserts no physical patient identifier and must never be sent to tools as one. Organization/principal fallback labels are execution namespaces rather than verified human identities.

Late patient identity is stored as a separate case-local binding, backed by a successful observation from an explicitly selected actor tool. One returned object must bind the patient ID to the active case, and contradictory identities reject the entire response. Workspace files cannot establish this binding. Subsequent arguments and responses are checked against the observed patient ID while the durable scope key, workspace and journal retain their original namespace. The context manifest carries the binding and source evidence so it survives context reduction and recovery.

**Runtime lifecycle matters:** in the observed official container, stopping and restarting the entrypoint reset the case to initial intake. Retaining a container is not a saved clinical-world checkpoint. Verify actor-visible state after restart and use a fresh attempt if it reset; never replay an old journal against a different world merely because its container name matches.

An uncertain write remains blocked for real readback/reconciliation. Reports do not authorize retrying it. Preserve an attempt before fixing code or starting another world, and use a new run directory so versions, counts and outcomes cannot silently mix. The comparison utility does not reset environments, run a study, certify medical decisions, or calculate a competition score.

Explicit audit continuation uses `python -m health_harness_codex.continuation --help`. It requires a settled source result, unchanged task/container/scope, a matching live public determination signature, a fresh destination, a written audit note and explicit cumulative budgets. Source SQLite is backed up read-only; previous final claims and counters remain in history. Completed routing/disposition mutations are hidden and rejected. `model_calls`/`tool_calls` and accumulated usage in the final case result are lifetime values; `model_calls_observed_this_segment`, `reported_usage_this_segment`, dispatch maps and `starting_counts` identify the new segment. Audit conclusions can remain unresolved even when the actor reports final approval, as the [executed follow-through](../Progress/HEALTH_HARNESS_EXECUTION_FOLLOWTHROUGH.md) demonstrates. Do not erase that distinction to make a dashboard green.


## Observed development failures and next experiments

The [execution history](../Progress/HEALTH_HARNESS_COMPETITION_EXECUTION.md) preserves actual autonomous failures separately from operator-assisted continuations. Confirmed defects included oversized reference reads, inability to read PDF clinical contents, unconditional compaction of large observations, and confusion between task-authorized simulated roles and real professional credentials. Their fixes have software checks; a clinical/competition pass must not be inferred from those checks.

Repeated source searches and rehydration remain an observed efficiency limitation. A useful next controlled experiment would compare the current owner context with an explicit case-local fact/criterion ledger carrying source IDs, offsets, unknowns and required next actions. Such a ledger is **planned, not implemented here**; it must not introduce patient-derived cross-case learning or replace source evidence with unsupported summaries. Conditional catalog availability and source-derived criterion labels also deserve failure classification instead of repeated blind searches.

One development case cannot establish general reliability, clinical correctness, superior architecture, or live coverage of PA/CM. Compare additional tasks and repeated runs under recorded model/budget/source versions, then use genuinely held-out tasks. Preserve strict official reward and diagnostic fractions separately. This recorder supplies operational evidence; official grading is the separate stage below, and submission-format integration remains unverified.


## Separate official verifier execution

The user subsequently authorized local official evaluation. Invoke the unchanged pinned runtime verifier only after the actor run stops, against the same retained actor world; do not restart it first. Pass the public task's baked fixture path to the verifier as an opaque path without opening fixture/test/solution contents. Direct reward, scorecard, export and context files to a new directory outside the acting tool read roots. Keep the original unscored recorder output unchanged, and store a separate official receipt referencing its source version and hashes of official output artifacts.

The [official evaluation procedure](../Progress/HEALTH_HARNESS_OFFICIAL_EVALUATION.md) records the invocation and launch limitations; [pilot results](../Progress/HEALTH_HARNESS_PILOT_RESULTS.md) retains each fixed-version batch. This particular fixture completed deterministic checks without an LLM judge call; the standard published all-domain judge pipeline still has its own Anthropic authentication requirements. Do not equate missing keys, degraded/skipped judge checks or diagnostic fractional completion with a valid strict pass. Verify actual emitted checks and judge status per execution instead of assuming one authentication rule covers every released fixture.

For the three aggregate metrics, freeze the harness/model/budgets and use independent fresh worlds. pass@1 estimates single-attempt success; pass@3 measures at least one success in three; pass^3 requires all three to succeed. Different development revisions and assisted continuations cannot form a comparable three-attempt batch. Official local verification is distinct from a Harbor-compatible submission packet and from public leaderboard publication.

Run `python -X utf8 evaluations/aggregate_official_pilot.py --pilot-root runs/<batch>` from this folder. Each `trial-1/2/3` must contain its settled `attempt-1/evaluation.json` and `run.result.json`, plus an `official-evaluation-receipt.json` naming a contained `container_logs/verifier_official_attempt_N` directory and hashing all official artifacts. The aggregator validates hashes, binary reward/check consistency, N/A accounting, semantic availability and matching source/task/model/budget/initial-observation metadata. It rejects incomplete inputs; it never supplies a missing score. Timestamped JSON and Markdown reports preserve earlier results. Counts distinguish engine operations, actor capability attempts, known local refusals and remote dispatch attempts. Usage is reported only when supplied; dollar cost remains unknown.
