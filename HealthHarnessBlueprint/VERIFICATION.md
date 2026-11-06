# Design status and verification

This deliverable is a hypothetical working-organization layout, **not a running agentic harness**. The source/catalogue generation and diagram tooling publish a specification; they do not instantiate healthcare workers or demonstrate patient isolation.

## Scope of the proposal

- Three composite domain jobs: provider PA, payer UM and CM.
- Sixty-six proposed smaller responsibility contracts: PA 18, UM 18, CM 20 and shared support 10. They may be combined in one agent, delegated selectively or realized partly as deterministic functions/tools.
- Twenty-nine upper-level organizational/capability/interface modules, 20 logical service contracts, 10 memory layers and three composition arrangements. These are not benchmark app/tool names or a recommended runtime-agent count.
- All 97 prior functional profiles receive a primary context mapping without limiting the new computational decomposition to existing professions.
- Strict patient separation is a user requirement: shared approved job/procedure definitions, but no patient-derived context, notes, episodes, summaries, learned habits or automatic procedure updates crossing to another patient.

## Structural and diagram checks

The builder checks five prior baseline hashes and generates the linked catalogues/data. The validator checks unique IDs, required functional contract fields, exact family/role coverage, source/module/service references, proposed/unimplemented flags, the user's environment/isolation requirements, local Markdown links/anchors and SVG parsing/link integrity. Receipts under verification/ distinguish passed document checks from unimplemented runtime properties.

Five SVGs have editable DOT sources. Headless loading/visual inspection records which diagrams were actually checked. A diagram can illustrate a patient barrier; it cannot prove the barrier has been implemented. All reviews/integration for this deliverable are in the main chat; no extra research/review agents were spawned.

Executed publication checks passed: all 66 responsibility contracts and family counts, 29 modules, 20 service contracts, 10 memory layers, all 97 prior-function mappings, three composition variants, 18 design decisions and 20 proposed acceptance cases. The [validation receipt](verification/validation_receipt.json) records exact link/anchor counts and false/unimplemented runtime flags. Five diagrams rendered with @viz-js/viz 3.31.0, zero warnings; all five loaded headlessly with zero JavaScript errors and their screenshots were visually inspected. Raw screenshots remain ignored.

The main-chat scope review removed the assistant's initial broad-world-simulator interpretation, replaced the coarse-role-only design with composite jobs and finer contracts, and made cross-patient independence a direct user requirement. The execution diagram also permits already-sufficient evidence and explicit unresolved/exception reporting without requiring a gratuitous write or an endless clarification loop. A font-width warning was corrected by using ASCII equivalents in diagram labels; source documents retain the normal benchmark spelling.

## Not executed or established

Detailed public-task/tool mapping, a new runtime, model/provider calls, actual session/context reset, isolation/noninterference tests, replay/concurrency fault tests, clinical validation and benchmark outcomes are unperformed. No second hospital-world environment, patient simulator, real-world integration, protected handbook inspection, hidden verifier access, Docker or visible browser was used for this design.

Proposed failure/acceptance cases are not passing runtime tests. The official environment remains authoritative; no mismatch in its actual case facts was established by the previous research. Existing privacy/credential/delegation/hospice source limits remain unchanged.

## Reproduce publication

```powershell
python HealthHarnessBlueprint/tools/build_blueprint.py
node HealthHarnessBlueprint/tools/render_diagrams.mjs
python HealthHarnessBlueprint/tools/validate_blueprint.py
```

The renderer uses the existing ignored @viz-js/viz 3.31.0 document toolchain. The optional check_diagrams.mjs uses an explicitly headless local browser and stores screenshots under ignored _cache/qa/. No deployment/runtime environment is created by these commands.
