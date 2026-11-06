# Healthcare roles, responsibilities, decisions and graphs

Research reference for the US healthcare workflows relevant to chi-Bench. Built October 17, 2026. This extends the [earlier participant map](../WORKFLOW_PEOPLE.md), with individual role dossiers and separately typed authority/relationship models.

**Defined evidence review completed: 2,218 inventoried assertion units, each with a verdict and reason.** This includes composite narrative blocks, interpretations and explicit models; it does not mean every assertion is confirmed true. Dependencies, handoff fields, modeled contacts and escalation routes remain **synthesis, not confirmed institutional practice**. Actual local authority is **not confirmed**. Start with the [corrections and complexities](FINDINGS.md), [evidence review](EVIDENCE_REGISTER.md) and [assertion ledger](verification/README.md).

## Start here

- [Searchable offline reference](index.html): search by role ID/title or filter by domain. Opening is optional; all substantive work is also in Markdown.
- [Role index](ROLE_INDEX.md): 97 role/function profiles with responsibilities, permitted decisions, limits, inputs, outputs, dependencies, escalation, local conditions and evidence.
- [Authority and hierarchy](AUTHORITY.md): distinguishes clinical treatment, consent, professional scope, management, coverage, policy, privacy and appeals.
- [Decision matrix](DECISIONS.md): 34 questions stating the rule, scope, exclusions and review route.
- [Workflow and exception guide](WORKFLOWS.md): how the three use cases connect, including failure ownership.
- [219-edge dependency register](DEPENDENCIES.md): decodes every DEP arrow with sender work products and recipient context needs.
- [46 detailed information handoffs](INFORMATION_FLOWS.md): suggested artifact fields, acknowledgement and missing/rejected-information handling.
- [97 illustrative service interfaces](SERVICE_INTERFACES.md): a request/response boundary for every role, with a modeled primary contact; not an asserted local protocol.
- [Earlier-map coverage](COVERAGE.md): all 86 non-header rows mapped to current dossiers; rows are not unique people.
- [Source catalogue](SOURCES.md): 95 entries covering 94 distinct URLs, including failed attempts; [capture provenance](SOURCE_PROVENANCE.md) distinguishes access failures, earlier excerpts and aliases. R19/A09 identify the same HHS guidance.
- [Verification](VERIFICATION.md): exact executed checks and limits, separate from clinical/institutional validation.

## Graph library

| Question | Graph |
| --- | --- |
| Which authority controls which kind of decision? | [Separate authority domains](graphs/authority-domains.svg) |
| What can review/supersede an MA coverage determination? | [Scoped MA appeal hierarchy](graphs/ma-appeals.svg) |
| How does eligible commercial independent review differ? | [Commercial review route](graphs/commercial-appeals.svg) |
| What reporting lines have actual organizational examples? | [Documented reporting examples](graphs/reporting-examples.svg) |
| Who provides context/services to whom in provider authorization? | [Provider dependencies](graphs/provider-dependencies.svg) |
| Who provides context/services to whom in payer review? | [Payer dependencies](graphs/payer-dependencies.svg) |
| Who provides context/services to whom in care management? | [Care dependencies](graphs/care-dependencies.svg) |
| What information moves in provider authorization? | [Provider information](graphs/provider-information.svg) |
| What information moves in review/appeal? | [Payer and appeal information](graphs/payer-appeal-information.svg) |
| What information moves through care coordination? | [Care information](graphs/care-information.svg) |
| How do program support roles connect? | [Governance dependencies](graphs/governance-dependencies.svg), [governance information](graphs/governance-information.svg) |
| What is the complete role dependency network? | [All 97 roles / 219 conditional dependencies](graphs/all-role-dependencies.svg) |
| What request/response examples cover every role? | [All-role information interfaces](graphs/all-role-information.svg) |

There are 112 rendered SVGs: 15 overview/workflow/authority graphs and 97 individual dependency neighborhoods linked from the dossiers. Full networks are large reference maps; use the per-workflow and per-role views to read individual relationships. Each SVG has its editable `.dot` source alongside it. Arrows identify their meaning; a dependency arrow is not a boss, universal prerequisite or compulsory approval.

## What is established and what is modeled

**Scoped evidence judgments:** every frozen assertion unit has an authored disposition, source locations where supporting context exists, alternatives and unresolved facts. Scripts resolved 495 authored passage selectors; a match is not a truth judgment. The review is agent-authored, not independent human legal/clinical certification. Government occupational descriptions, source-specific programs and professional frameworks establish different kinds of support. Direct eCFR pages displayed Title 42 through October 15, 2026; source editions and access limits remain explicit.

**Operational synthesis:** artifact/input/output contracts, primary modeled contacts, dependency connections and generalized workflow/exception views. These make responsibilities explicit without pretending an institution supplied its internal procedures. Every role has a scope condition and authority limits.

**Not established by this study:** all states' professional permissions; an institution's actual organogram, privileges, delegation or procedures; every product's deadlines/appeal route; a complete current-2026 hospice update review (V11/V16/V17 establish the official 2025 codification); observed staffing, interviews or clinical validation; task-by-task benchmark role coverage. R13's mixed professional-category/final-responsibility wording and V02's prospective pathway timing are explicitly unresolved rather than guessed.

The correct way to eliminate local ambiguity is to fill the required authority record in AUTHORITY.md. If a permission is not established, the reference states that boundary explicitly rather than assigning invented seniority. No clinical or insurer outcomes were tested, and no agent architecture was selected.

## Reusable data and reproducible generation

`data/roles.json`, `decisions.json`, `information_flows.json`, `service_interfaces.json`, `relations.json`, `sources.json` and `coverage.json` are the reusable records. They preserve role IDs and evidence references. `build_receipt.json` and `render_receipt.json` describe generation, not clinical validation.

Authored definitions live in `tools/role_definitions.py`, `decision_definitions.py`, `custom_graphs.py` and `data/additional_sources.json`. Reviewed corrections are applied from `verification/apply_reviewed_corrections.py`; authored review bases, additional sources and the immutable original inventory live in `verification/`. Do not edit generated dossiers alone. Narrative guides are authored Markdown. Raw public-source captures stay local-only under ignored Runner/.cache/role-verification/; tracked locators/hashes let future work identify the reviewed captures without publishing full source text.

From the project root, using an available Python 3 interpreter and Node.js:

```powershell
python Plan/HealthcareRoles/tools/build_reference.py
node Plan/HealthcareRoles/tools/render_graphs.mjs
python Plan/HealthcareRoles/tools/validate_reference.py
```

The committed bindings and ledger support offline regeneration. Build also reconciles current narrative/graph units against their explicit review assignments and publishes the [revision delta](verification/revisions.md). To rebind after intentionally editing authored judgments, run `tools/bind_verification_evidence.py` (requires the local captured corpus), then `tools/adjudicate_reference.py`, then build/render/validate. Do not overwrite the frozen baseline with revised generated output. A future source refresh is a new review, not an automatic truth upgrade.

The render command uses local-only `@viz-js/viz` **3.31.0** at `Runner/.cache/role-docs-toolchain/`. To recreate that optional document toolchain:

```powershell
npm install --prefix Runner/.cache/role-docs-toolchain --no-audit --no-fund @viz-js/viz@3.31.0
```

No Docker, model/provider key, host compiler, benchmark execution or WSL migration is required. The reference remains readable without the renderer or any network access. Browser appearance/interaction checks are performed headlessly only; do not open visible automated browser windows for this task.
