# Study publication and verification

The study publishes 97 role analyses, 23 candidate work packages, 16 design decisions, 34 authority implications, 26 cross-cutting questions, 20 proposed stress cases and 20 explicitly considered merger examples. The 4,656-pair CSV is a mechanical planning screen, not 4,656 independently verified compatibility judgments. All groupings and architecture preferences remain proposed and untested.

The prior audited healthcare reference is preserved at afb2ab9. Build checks its six baseline file hashes before generating this study. No prior healthcare data or evidence judgment was rewritten by the organizational analysis.

Structural checks **passed**. The [validation receipt](data/validation_receipt.json) records exact role/package/decision/pair/flow coverage and Markdown link/anchor counts. All three SVGs rendered using @viz-js/viz 3.31.0 with **zero warnings**; the [render receipt](data/render_receipt.json) records them. The [headless receipt](data/headless_receipt.json) records three loaded diagrams and zero JavaScript errors, without visible windows. All three final diagram screenshots were visually inspected for readable labels, arrows and stated model/proposal status. A passing structure or render does not establish factual healthcare correctness, actual task permissions or a better-performing architecture.

The initial screenshot attempt against a native SVG page timed out. The checker was corrected to embed the SVG in a controlled local HTML document; the subsequent checks passed and the browser closed in finally. Final diagrams use a vertical layout to keep labels legible. Screenshots are local-only and untracked.

## Reproduce publication

From C:/Projects/BigData with an available Python 3 and Node runtime:

```powershell
python Plan/AgentOrganization/build_study.py
node Plan/AgentOrganization/render_diagrams.mjs
python Plan/AgentOrganization/validate_study.py
```

The renderer uses the existing local-only @viz-js/viz 3.31.0 under ignored Runner/.cache/role-docs-toolchain/. It does not change the benchmark runtime or official checkout. The optional check_diagrams.mjs script uses an explicitly headless installed browser with no user profile, records image loads and saves local-only screenshots under Runner/.cache/agent-organization/qa/.

## Scope of checks

Coverage checks compare all 97 canonical IDs, unique primary package assignment, 34 authority questions, all unordered pairs, all 219 inherited dependencies and all 46 inherited handoffs. They require explicit provisional/non-executed labels, substantive decision fields, unique role questions, valid source references, Markdown paths/anchors and valid linked SVGs. They are consistency checks, not automated source-entailment or legal/clinical validation.

No runtime agent, model/provider call, scored trial, held-out split, optimal worker count or actual tool-permission implementation exists from this phase. No Docker, protected handbook, hidden verifier, visible browser, external messaging or separate research agent was used. Actual public-task/tool mapping remains pending before implementation; do not impose external human steps solely from a real-world credential analogy when the benchmark assigns the simulated function to the solver.
