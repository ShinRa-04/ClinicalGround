# Decision and rationale log

Sixteen provisional design judgments record the question, evidence, conclusion, concise reason, alternatives, uncertainty and reconsideration condition. These are reviewable reasoning summaries, not measured outcomes. The main objective is our harness inside χ-Bench; an independently built simulator remains a separate alternative.

<a id="ad01"></a>
## AD01 — Should each of the 97 profiles become a running agent?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Preserve all functions in the design inventory, but do not select 97 running agents from the count of profiles.

**Rationale:** Profiles include people, composite groups, infrastructure, governance and physical services. Running-worker boundaries need a task-specific purpose beyond a title.

**Alternatives:** One agent per profile for a controlled ecosystem simulation; A single worker with explicit role modes; A small team with capability workers.

**Evidence/context:** [S01](SOURCES.md#s01), [S03](SOURCES.md#s03), [Prior audited reference](../HealthcareRoles/README.md)

**Uncertainty:** No chi-Bench comparison of these organizations has been run.

**Reconsider if:** A role-per-worker design demonstrably improves the chosen objective under comparable resources without compromising allowed environment boundaries.

<a id="ad02"></a>
## AD02 — Are realistic simulation and benchmark solving the same design problem?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Maintain two explicitly separate designs and success criteria.

**Rationale:** A world simulation may model independent parties; a solver must interact with the supplied environment. Internal synthetic consent or external outcomes would not be observations.

**Alternatives:** A full organizational simulator as a separate research environment; A task-scoped solver with external interfaces.

**Evidence/context:** [S06](SOURCES.md#s06), [S09](SOURCES.md#s09), [Prior audited reference](../HealthcareRoles/README.md)

**Uncertainty:** The 75 public instruction files have not been mapped to every proposed capability in this phase.

**Reconsider if:** A documented benchmark contract actually delegates simulation ownership or the project objective changes to constructing a new simulator.

<a id="ad03"></a>
## AD03 — What makes two software workers substantively different?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Specify objective, input view, tools, authority envelope, state ownership, output contract, trigger and stop condition.

**Rationale:** Two prompts with different job titles can still have identical information and correlated failure. A distinct output or isolation requirement is a stronger reason to separate.

**Alternatives:** Role prompt only; Isolated context with common permissions; Separate tool/data scope and state ownership.

**Evidence/context:** [S01](SOURCES.md#s01), [S02](SOURCES.md#s02), [S04](SOURCES.md#s04)

**Uncertainty:** Which dimension matters most for this benchmark is unmeasured.

**Reconsider if:** A controlled prompt-only condition provides the same benefit more simply than stronger worker separation.

<a id="ad04"></a>
## AD04 — Which functions are plausible early merger candidates?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Investigate provider access (W05), payer administrative operations (W08), and care coordination (W13), with explicit state and permission distinctions.

**Rationale:** These work packages can share a case record and continuity obligation. This is a design hypothesis informed by role overlap, not a legal permission to combine all activities.

**Alternatives:** Separate workers for every function; One case owner with named modes; Case owner plus specialist calls.

**Evidence/context:** [Prior audited reference](../HealthcareRoles/README.md), [S01](SOURCES.md#s01), [S03](SOURCES.md#s03)

**Uncertainty:** Actual tool scopes, task frequency, workload and local assignments remain unresolved.

**Reconsider if:** Merged trials repeatedly lose required distinctions or separate workers gain repeatably at matched task/model/resource settings.

<a id="ad05"></a>
## AD05 — Can merging preserve different authorities?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Merge implementation only where it preserves explicit operation-level permissions, author identity and decision stage.

**Rationale:** Shared computation and shared authority are different properties. One executable can enforce separate scopes, and many prompts can still expose unrestricted access.

**Alternatives:** Separate processes; One process with scoped adapters and state transitions; A role-mode prompt without enforceable separation.

**Evidence/context:** [S07](SOURCES.md#s07), [S08](SOURCES.md#s08), [Prior audited reference](../HealthcareRoles/README.md)

**Uncertainty:** No permission-enforcement implementation has been built or tested.

**Reconsider if:** The actual tool contract cannot preserve required isolation inside one process, or scoped operations prove ineffective in execution tests.

<a id="ad06"></a>
## AD06 — Does a fresh model call provide independent reconsideration?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Treat a fresh reviewer context as an error-checking experiment, never as proof of required human institutional independence or qualification.

**Rationale:** The cited MA reconsideration rule concerns uninvolved persons and appropriate physician expertise. Naming a model physician does not establish either. Models can also share failure biases.

**Alternatives:** Same-context self-check; Fresh context with the same model; Different model or human/institutional review where actually required.

**Evidence/context:** [S07](SOURCES.md#s07), [S03](SOURCES.md#s03), [Prior audited reference](../HealthcareRoles/README.md)

**Uncertainty:** Error correlation and the value of context isolation have not been measured here.

**Reconsider if:** Actual policy/tool requirements and measured outcomes establish the permitted software role; real human qualification claims still require actual evidence.

<a id="ad07"></a>
## AD07 — Who should write mutable case state?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Use one accountable case-write owner as the first design to test; let helpers return proposals with source/version references.

**Rationale:** This makes conflicting or duplicate writes easier to control. It is a local engineering preference, not a claim that all real institutions have one writer.

**Alternatives:** One serialized case owner; Several transactional writers with conflict control; Uncoordinated agent writers.

**Evidence/context:** [S04](SOURCES.md#s04), [S05](SOURCES.md#s05), [S09](SOURCES.md#s09)

**Uncertainty:** The benchmark’s observed concurrency/version/idempotency semantics have not been tested in this study.

**Reconsider if:** Disjoint transactional writes are supported and measured parallel execution gains outweigh coordination failures.

<a id="ad08"></a>
## AD08 — When should a specialist be a sub-agent rather than a capability call?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Use a bounded call for a specific evidence or interpretation question; consider autonomous specialists only when independent multi-step exploration and context isolation add measurable value.

**Rationale:** Many functions need focused reasoning without a new persistent identity, memory or right to mutate the case.

**Alternatives:** Reusable prompt/tool function; Fresh read-only specialist context; Persistent autonomous worker.

**Evidence/context:** [S01](SOURCES.md#s01), [S02](SOURCES.md#s02), [S03](SOURCES.md#s03)

**Uncertainty:** No activation thresholds or profitable call budget have been established.

**Reconsider if:** Trace evidence shows repeated independent multi-step specialist work and controlled trials show net improvement.

<a id="ad09"></a>
## AD09 — Should workers communicate in free-form conversation?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Prefer a small structured task/result contract plus a concise explanation; retain source references and explicit unknowns.

**Rationale:** A handoff must preserve what is needed for the recipient’s action. More dialogue alone is not proof of transfer, understanding or accepted responsibility.

**Alternatives:** Free-form chat; Shared structured record; Structured messages with acknowledgement and clarification.

**Evidence/context:** [S04](SOURCES.md#s04), [S05](SOURCES.md#s05), [S10](SOURCES.md#s10)

**Uncertainty:** The smallest sufficient message for each function is not yet measured.

**Reconsider if:** Structured compression loses necessary context or a richer format reduces observed handoff failures at acceptable cost.

<a id="ad10"></a>
## AD10 — What should happen when specialists disagree?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Preserve the conflicting evidence and applicable rule; route to the authorized decision function or an unresolved/clarification state.

**Rationale:** A majority of model opinions cannot create missing patient facts, professional authority or a binding external outcome.

**Alternatives:** Majority vote; Evidence/rule-based resolution; Escalation or unresolved state under the actual workflow.

**Evidence/context:** [Prior audited reference](../HealthcareRoles/README.md), [S04](SOURCES.md#s04)

**Uncertainty:** Not every clinical conflict has a deterministic answer from the available information.

**Reconsider if:** A validated aggregation rule improves a bounded reasoning task without being confused with clinical or institutional authorization.

<a id="ad11"></a>
## AD11 — How much organizational realism is useful?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Retain realistic accountability, information limits and observable handoffs; test conversational personas separately from these mechanisms.

**Rationale:** Realistic names, simulated shifts or internal politics can add cost without improving completion. They may still be useful if the research objective is simulation fidelity.

**Alternatives:** Rich human-like personas; Minimal function contracts; Separate realism and operational-mechanism experiments.

**Evidence/context:** [S01](SOURCES.md#s01), [S03](SOURCES.md#s03), [Prior audited reference](../HealthcareRoles/README.md)

**Uncertainty:** No effect of persona richness on this benchmark has been measured.

**Reconsider if:** An ablation isolates a repeatable benefit from persona detail beyond extra tokens and clearer functional instructions.

<a id="ad12"></a>
## AD12 — Can the existing dependency graph determine the optimal organization?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Use it to enumerate modeled interactions and stress cases; do not treat graph clustering as proof of an optimal worker count.

**Rationale:** Its 219 edges are explicit proposed dependencies, not measured interaction frequencies, token costs or observed workload.

**Alternatives:** Cluster the modeled graph as a hypothesis generator; Measure trace-weighted interactions before optimizing; Start with functional packages and revise from trials.

**Evidence/context:** [Prior audited reference](../HealthcareRoles/README.md), [S03](SOURCES.md#s03)

**Uncertainty:** No empirical edge weights or workload distribution exist in this study.

**Reconsider if:** Measured traces establish meaningful weights and held-out evaluation validates a graph-derived partition.

<a id="ad13"></a>
## AD13 — What evidence would justify the extra agents?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Require complete-task outcomes and process validity alongside resource accounting; compare against a strong mode-based single-agent baseline.

**Rationale:** Additional calls, tokens, context and tools can confound an apparent architectural improvement. Literature outside chi-Bench motivates controls, not a predicted score gain.

**Alternatives:** Equal-resource causal comparisons; Equal-wall-time practical comparisons; Best-effort frontier with full cost disclosure.

**Evidence/context:** [S02](SOURCES.md#s02), [S03](SOURCES.md#s03), [S04](SOURCES.md#s04)

**Uncertainty:** Models, task subsets, repetitions, exact budgets and scoring runs remain unselected/unexecuted.

**Reconsider if:** Results reproduce across appropriately separated evaluation cases and stochastic trials with a practically meaningful cost/quality tradeoff.

<a id="ad14"></a>
## AD14 — Which harness integration description should future code follow?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Use the tested pinned checkout interface as the initial implementation target and explicitly reconcile any upgrade; do not splice the live guide’s API into the old checkout.

**Rationale:** The live guide describes AgentHarness/constructor/run/trajectory wiring, while local commit 4444a07 uses a Harbor BaseInstalledAgent integration. These are different interface descriptions.

**Alternatives:** Keep the tested pin; Intentionally update and reverify; Guess compatibility from similar names.

**Evidence/context:** [S06](SOURCES.md#s06), [S09](SOURCES.md#s09)

**Uncertainty:** Cause of live-versus-pinned documentation divergence and current remote compatibility are unconfirmed.

**Reconsider if:** An intentional version update with actual interface/runtime checks establishes the new contract.

<a id="ad15"></a>
## AD15 — Should governance and infrastructure be runtime personas?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Model most approval/version/access rules as explicit configuration or tools; use bounded analysis where interpretation is actually needed.

**Rationale:** A policy committee, EHR administrator or quality role does not need to hold an open-ended conversation on every case to preserve its function.

**Alternatives:** Autonomous governance agents; Versioned configuration and scoped tools; Tools plus a bounded interpretation/escalation capability.

**Evidence/context:** [S01](SOURCES.md#s01), [S08](SOURCES.md#s08), [Prior audited reference](../HealthcareRoles/README.md)

**Uncertainty:** Some tasks could explicitly require policy analysis or unusual escalation; invocation must follow real task demand.

**Reconsider if:** Runtime traces reveal unresolved governance work that cannot be represented adequately by the simpler approach.

<a id="ad16"></a>
## AD16 — What is the provisional experimental starting point?

**Status:** PROVISIONAL_DESIGN_JUDGMENT_NOT_RUNTIME_VALIDATED

**Conclusion:** Compare one case owner with explicit role modes against that same owner plus a small number of on-demand bounded specialists; retain a role-per-worker variant as a separate hypothesis.

**Rationale:** This separates benefits of functional instructions and state tracking from benefits of worker/context separation. It does not select a final framework or prove the smaller team wins.

**Alternatives:** Mode-rich single worker; Case owner plus bounded specialists; Persistent role team; Full organization simulator outside the official solver environment.

**Evidence/context:** [S01](SOURCES.md#s01), [S02](SOURCES.md#s02), [S03](SOURCES.md#s03), [S04](SOURCES.md#s04)

**Uncertainty:** Task-level relevance and all runtime effects are pending; 23 work packages are analysis categories, not a recommended agent count.

**Reconsider if:** Controlled results favor a different structure for the chosen objective and satisfy task-boundary constraints.
