# From healthcare functions to agent organization

Started October 18, 2026. This is a new analysis phase requested by the user: examine distinct role-like sub-agents, merged jobs and alternatives, while preserving the questions, evidence, conclusions and decision rationale. It is a design study, not an implementation or measured architecture result.

The prior healthcare evidence reference is preserved at Git commit **afb2ab9**. [Baseline receipt](baseline.json) records input hashes. [Prior reference](../HealthcareRoles/README.md) contains scoped healthcare findings and unresolved facts; this study must not silently upgrade them into universal permissions.

The central question is which distinctions need separate reasoning context, state ownership, permissions, objectives or review, and which only need explicit functions within one worker. A real-world profession, a software capability and a running agent are different units. Following the clarification, the main subject is **our agentic harness operating in χ-Bench**; a separate ecosystem simulator is an alternative boundary example, not the selected project.

For each decision, record the question, supporting evidence, alternative designs, conclusion, concise rationale, uncertainty and what result would change the conclusion. This is an auditable decision record, not a claim of complete empirical validation.

Scope: all 97 existing functional profiles, all 34 decision questions, merged work-package candidates, boundaries that merging must preserve, representative workflow stress cases and a controlled evaluation plan. Public internet research may inform the analysis. No agent runtime, model calls, scored trials, Docker, visible browsers, protected handbook access, hidden verifier inspection or final stack selection is authorized by this research phase.

Owner: main agent. Actual research delegation has not been requested; the proposed sub-agents are the subject of analysis.

Current status: **documented design study completed and structurally checked**. Baseline checkpoint: 3c28c4d; the intermediate draft/clarification checkpoint is 73c7b10. All 97 role analyses, 23 candidate packages, 16 provisional decisions, 34 authority implications, 26 cross-cutting questions, 20 stress cases and 20 merger examples are published. The 4,656-pair screen is explicitly mechanical, not independently researched permission judgments. Three diagrams render with zero warnings and were checked headlessly and visually. See [verification](VERIFICATION.md) for executed checks and limits.

The provisional experimental starting point is a case owner with explicit functional modes, compared against the same owner plus bounded specialists and a competent persistent role-worker alternative. **No optimal agent count, winning architecture or runtime benefit has been established.** Detailed public-task/tool mapping and experimental implementation/execution remain unperformed.

## Reading path

- [Main analysis](ANALYSIS.md): the question, separation/merger criteria, scope distinctions and provisional conclusion.
- [Three worked job designs](JOB_DESIGNS.md): provider authorization, payer operations/review and care-management coordination, each with alternatives and failure conditions.
- [All 97 role analyses](ROLE_ANALYSIS.md): unique question, function, proposed representation, merger conditions, counterexample and unresolved facts for each profile.
- [Twenty-three work packages](WORK_PACKAGES.md): candidate groupings, retained boundaries and split triggers; not a recommended agent count.
- [Merger analysis](MERGE_ANALYSIS.md): 20 explicitly considered pairs plus the labeled mechanical screen for all pairs.
- [Decision/rationale log](DECISION_LOG.md): evidence, alternatives, conclusions, uncertainty and reconsideration conditions.
- [Authority implications](AUTHORITY_IMPLICATIONS.md): all 34 prior decision questions mapped to proposed software boundaries.
- [Information design](INFORMATION_DESIGN.md) and [diagrams](DIAGRAMS.md): all 46 inherited handoffs, the package crosswalk for all 219 modeled dependencies, and proposed ownership/message contracts.
- [Questions](QUESTIONS.md), [20 proposed stress cases](STRESS_CASES.md), and [experiment plan](EXPERIMENT_PLAN.md): what remains unknown and how to test it without invented results.
- [Source ledger](SOURCES.md): 11 primary-source entries with access, edition, inspected sections and limits. The prior healthcare audit remains a separate evidence baseline.

## Reproduction and editing

Edit definitions.py, decision_basis.py and sources.json for authored structured content; edit ANALYSIS.md, JOB_DESIGNS.md, QUESTIONS.md and EXPERIMENT_PLAN.md for narrative work. Generated role/report/data views come from build_study.py. From the project root:

```powershell
python Plan/AgentOrganization/build_study.py
node Plan/AgentOrganization/render_diagrams.mjs
python Plan/AgentOrganization/validate_study.py
```

All prior baseline file hashes must remain unchanged. The local-only document renderer and optional headless screenshot checker are described in VERIFICATION.md. This publication tooling is not an implemented healthcare agent or benchmark harness.

Clarification verified against [paper v3](https://arxiv.org/abs/2605.16679v3) and [official extension guide](https://www.actava.ai/benchmarks/docs/extending): χ-Bench is the benchmark/environment/evaluation system. The paper introduces and studies that benchmark and compares agent/harness-model configurations; it is not merely a description of healthcare facilities. Our agent is the acting system; its model supplies inference and its harness manages execution, tools, memory, routing and optional sub-agents. Role composition is part of the challenge, but separate autonomous agents for each human role are an architectural hypothesis, not a benchmark requirement. Existing agent harnesses are also supported, so creating a new harness is our possible method, not a mandatory deliverable imposed by that paper.
