# Testing role separation versus merged work

**Proposed, not executed.** No model/provider calls, trial allocation, held-out split, runtime or score improvement has been established. The objective is our agentic harness operating inside the supplied benchmark. The real-world organization is an inspiration and source of boundary questions, not a replacement grading system.

## Compare mechanisms separately

| ID | Condition | Main comparison | Interpretation limit |
| --- | --- | --- | --- |
| V0 | Existing permitted strong harness | Reference outcome/resource behavior | A deliberately weak baseline would exaggerate gains. |
| V1 | One worker with explicit role modes and case obligations | V0 → V1: domain instructions/state discipline | More detailed instructions may explain improvement without multiple agents. |
| V2 | Same owner and role knowledge as V1, plus bounded specialist contexts | V1 → V2: context/worker separation | Count all extra inference and communication; keep tools/retrieval resources controlled. |
| V3 | Persistent task-relevant role workers | V2 → V3: continuity, identity and autonomy | Compare relevant activated roles, not all 97 on every case; record coordination failures. |
| V4 | Separate healthcare organization simulator | Different experiment: simulation fidelity | Do not substitute this environment’s outcomes for χ-Bench observations or compare its scores as the same benchmark. |

V1 versus V2 is the provisional first decomposition comparison, not a final architecture choice. V3 must be implemented competently if evaluated: clear role contracts, permitted data views, bounded budgets and explicit completion ownership. A poorly coordinated role team would be an unfair comparison. The paper supports multi-role composition as a task property; it does not predetermine the winning arrangement.

## Preserve a fair comparison

Use the same task instances, pinned environment/data/handbook versions and available agent-visible tools across solver conditions. Start with the same underlying model configuration so model quality is not mistaken for an architecture effect. Keep substantive role instructions and retrieval access comparable; a role team should not win merely because it alone receives better policy evidence.

For the primary architectural comparison, predeclare a **combined inference budget** across the owner, specialists, routing and critic calls, including communication context. Record actual usage rather than assuming each condition spends its cap. Token caps, billed cost and wall-clock caps cannot generally all be matched simultaneously, especially with different models or parallelism; state which resource is controlled and report the others. Missing provider usage fields stay missing, with any estimates labeled as estimates.

Use a separate practical comparison for equal wall time or equal cost, if useful, without calling it the same causal test. A best-effort performance/resource frontier is another valid analysis when labeled clearly. Changing model families, retrieval, context size, autonomy and worker number simultaneously would not isolate the benefit of separation.

## Task selection and stochastic variation

First inventory the public task instructions and actual tool contracts; this mapping is not yet performed. Group meaningful workflow families before selecting a development/evaluation split. Reserve whole families where feasible, and record any limited family count or distribution imbalance. No split is claimed to exist now.

Do not inspect hidden expectations or private solutions to decide a role structure. A selected held-out set must remain unused for prompt/architecture tuning; if it is used, relabel it honestly. Keep the earlier studied public cases and development feedback distinct from genuinely reserved evaluation data.

Predeclare repeats and record every stochastic source: model sampling, routing, subtask sampling, environment conversations and retry behavior where applicable. A repeated numeric seed does not guarantee provider or environment determinism. Randomize/interleave condition order where appropriate; record provider failures and execution exclusions before looking at favorable results. Use paired task comparisons with uncertainty that accounts for repeated trials belonging to the same task/family. Choose sample size and analysis after considering the available cases and budget, rather than inventing a precision guarantee.

## Outcomes and diagnostic measurements

| Level | Measurement | What it can establish |
| --- | --- | --- |
| Primary | Official complete-task/binary outcome under the unchanged benchmark | Success at the official criterion, within the sampled scope |
| Process | Required actions/artifacts and permitted-operation compliance from actual traces | Whether apparent completion omitted steps or invented observations |
| Diagnostic | Official partial/check-level feedback, used only after acting | Where a run failed; partial credit is not a binary pass |
| Resource | All owner/helper model usage, tool calls, worker activations, message volume, latency, retries and failures | Actual cost/coordination tradeoff |
| State integrity | Wrong-case evidence, stale proposals, duplicate mutations, conflicting persisted outcomes | Whether ownership/synchronization breaks |
| Dialogue fidelity | Actual answers versus inferences, refusals, unanswered questions, duplicates after refresh | Whether a dialogue-aware split helps or harms |
| Review behavior | Errors caught, valid outcomes blocked, new errors introduced, unresolved disagreements | A critic’s net effect rather than its number of objections |
| Generalization | Reserved family/case outcomes with selection history | Transfer beyond cases used to choose prompts/structure |

Required benchmark simulation/judge costs should be reported separately from acting-agent costs where the tooling permits attribution. An internal completion critic must not inspect the official hidden verifier or feed post-run expected answers into the acting process. Its output is a proposal/check, not the official score.

## Ablations

1. Hold functional instructions constant and vary shared versus separate reasoning contexts.
2. Hold case-state schema constant and vary one writer versus coordinated disjoint writers only if the tool contract supports it.
3. Compare no critic, same-context self-check and a fresh-context critic at the same declared resource constraint; record correlated/new errors.
4. Remove persona biographies while retaining objective, authority and output contracts; test the reverse only as a separately labeled condition.
5. Vary on-demand activation versus persistent workers; count idle/repeated activity and lost continuity.
6. Vary message structure and provenance fields without changing the available facts.
7. Vary worker count only within justified task scope; do not claim every profile is represented in every task.

These are experiment proposals. No ablation, provider expense or environment change has been run.

## Failure diagnosis and decision rule

Use the [20 stress cases](STRESS_CASES.md) to challenge the design before claiming a benefit. Their conceptual expected behavior must first be translated into actual supported tasks/tool semantics; none is claimed to be an official benchmark case or a passed test. The taxonomy is informed by MAST, but project failure frequencies must be measured independently.

Prefer the simplest configuration on a documented performance/resource frontier that meets the chosen task/process requirements. Predeclare what magnitude and uncertainty would count as a meaningful benefit, then inspect regressions as well as recovered cases. A single good demonstration, a higher partial score or more convincing role dialogue is insufficient to establish a superior harness.

## Implementation gate, not an approval gate

Before code: map actual public task functions/tools, choose and inspect a pinned integration contract, and specify budgets/state/output rules. When implementation is authorized, those are concrete engineering prerequisites, not a reason to repeatedly ask for permission. This study does not itself implement or execute them. The live guide and local 4444a07 interface differ; reconcile deliberately before copying either API into code.
