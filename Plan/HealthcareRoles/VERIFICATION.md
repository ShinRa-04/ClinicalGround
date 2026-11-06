# Verification state

The **defined evidence review is complete**: 2,218 frozen assertion units each have a verdict/reason, including composite narrative blocks, title classifications and explicit models. Zero units remain without a disposition. This does **not** mean every finding is confirmed true. The review is research-agent-authored, not independent human clinical/legal certification. [Evidence register](EVIDENCE_REGISTER.md), [assertion audit](verification/README.md), [corrections](FINDINGS.md).

## Evidence review and revision reconciliation

- Original inventory: 811 role assertion units, 136 decision units, 1,031 explicit model units, 82 narrative blocks and 61 authored graph labels; supplemented with 97 title units. Generated repetitions are not counted as new findings.
- Authored role/decision/narrative judgments bind 495 selected passage anchors to captured paragraph/page/tool-line locations; zero unresolved selectors. Binding confirms location presence, not automatic truth or entailment. Sources support general descriptions, dated rules and named program examples under different limits.
- Fifteen correction/clarification groups were applied to role/decision data, earlier overviews and diagram semantics. The original ledger retains frozen wording/hashes; changed canonical wording is recorded separately.
- Revision reconciliation accounts for all 157 current narrative/graph units: 132 unchanged, 25 revised/added, zero pending dispositions. These overlap the frozen inventory; they are not 157 additional independent findings. [Revision review](verification/revisions.md) records explicit revised judgments. Eight normalized UTF-8 artifact hashes detect stale reconciliation.
- Catalogue: 95 entries over 94 URLs, including four failed source attempts. R09/R12 retain earlier excerpts after fresh-access failure; R19 aliases A09. [Provenance](SOURCE_PROVENANCE.md) distinguishes access from assertion support. Full public-source captures stay ignored/local; tracked hashes and locators identify what was reviewed.
- Unresolved signatory scope, prospective pathway wording, unprovided local authority and incomplete current-2026 hospice update checking remain explicit. A completed disposition can be conditional, model, corrected or unresolved; it is not automatically a positive confirmation.

## Executed structural and rendering checks

- Generated 97 role dossiers/interfaces, 34 decision questions, 46 handoff contracts and 219 conditional dependencies; all 86 earlier participant rows map to canonical functions.
- All 112 DOT diagrams rendered using @viz-js/viz 3.31.0 with **zero warnings**. These are 15 overview views and 97 neighborhoods.
- Validator passed frozen ID/hash coverage, verdict/evidence presence, current canonical correction application, source references, earlier-map coverage, model labels, local Markdown links and SVG parsing/node links. The current receipt records **3,443 local Markdown links** and **949 SVG node instances**.
- Consistency sentinels preserve nonclinical delegated alternatives, dated hospice distinctions, urgent commercial concurrency, MA route qualification and collaboration versus reporting. These checks verify the representation, not the underlying healthcare truth.
- No institution-specific permission, clinical appropriateness, observed workflow, provider/model execution or benchmark scoring was tested.

## Executed headless and visual checks

`tools/check_headless.mjs` used a task-owned loopback reference server and `headless:true`, with no user browser profile or Docker. Checks passed for 97 profiles, ID search, domain filtering, hash navigation/reset and zero JavaScript errors. Seven SVGs loaded: authority domains, MA appeals, commercial appeals, reporting examples, M28, U13 and provider information.

Screenshots of the changed MA, commercial, reporting and M28 views were visually inspected after regeneration; their labels and alternative connections were readable. Earlier authority/U13 screenshots had also been inspected. The large provider-information panorama needs zoom/per-role views; this does not claim manual inspection of every SVG. Screenshots remain ignored under Runner/.cache/role-docs-toolchain/qa/.

The earlier visible blank preview window was unwanted and closed. No subsequent verification requested a visible browser window. Keep all future checks non-visible for this task.

## Reproduction and limits

From the root: run `tools/build_reference.py`, `tools/render_graphs.mjs` and `tools/validate_reference.py` under Plan/HealthcareRoles/. Build applies the authored corrections, reconciles revised narrative/graph units and publishes review files. Bind/adjudicate first only when intentionally changing review judgments; source rebinding requires the ignored local corpus. Do not regenerate the frozen original inventory from corrected data.

Machine-readable receipts are in data/ and verification/. Passing software checks does not establish zero hallucinations. Actual jurisdiction/product/license/privileges/delegation, patient representation, organogram and case stage require the missing local facts listed in AUTHORITY.md. No interviews, institutional signoff, all-state legal audit, full current hospice amendment audit or task-by-task benchmark mapping occurred.
