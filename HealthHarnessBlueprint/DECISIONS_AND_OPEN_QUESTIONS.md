# Decisions, rationale and remaining questions

All entries are hypothetical design decisions or user requirements, not measured runtime results. This is the reviewable rationale trail for the proposal.

| ID | Decision / requirement | Reason and alternative | What could change / remains unknown |
| --- | --- | --- | --- |
| D01 | One supplied task environment; organize our staff/work above it | User clarified χ-Bench is the day/work and we build the working organization. A second hospital-world simulator was an assistant overinterpretation and is removed. | Actual task/tool mapping still needed; no case-state mismatch was established. |
| D02 | PA, UM and CM are first-class composite workspaces | They are the problem's domains, each with outcome ownership and related functions. | Starting stage/required work varies by task; no forced PA→UM→CM pipeline. |
| D03 | Composite jobs are built from finer design roles | User explicitly wants smaller responsibilities beyond real-world professional bifurcation. | The 66-contract starting decomposition is not an optimal count or final runtime graph. |
| D04 | A role contract need not be a separate agent | Code, tools, in-context reasoning, bounded calls and workers can realize the same responsibility. | Controlled comparison and actual isolation needs determine execution form. |
| D05 | Top-level owner can delegate or perform several functions itself | Preserves a complete job outcome while allowing granularity to vary. | Context pressure, authority or sustained independent work may justify separate workers. |
| D06 | Retain actual authority/stage and participant boundaries | Shared code does not merge patient/provider/payer/review decisions. | Real benchmark assignment controls simulated function; do not invent external real-person approval steps. |
| D07 | Reuse job definitions, not patient memories | User requires one patient's data not to shape another patient's role behavior. | Patient/provider identity, scopes and actual provider-side context reset must be verified. |
| D08 | No automatic patient-derived shared learning | Prevents episodes, summaries, habits, skills or profile changes from transferring patient experience across patients. | Any separately requested/governed procedure change is outside normal runtime behavior. |
| D09 | Case working state is a projection, not alternate world truth | Actual source records/observations control; generated interpretations/artifacts retain provenance. | Actual version/readback metadata may be limited. |
| D10 | Explicit unknowns and obligations survive context changes | Avoids fabricated completeness after compaction or worker replacement. | Semantic preservation and actual provider routes need runtime evaluation. |
| D11 | Deterministic effect and isolation gates | A model title, valid JSON or persuasive summary does not enforce scope. | Actual operation permissions and transactional guarantees must be mapped. |
| D12 | Bounded helper budgets and conditional activation | Splitting every responsibility into a model call can add waste and coordination loss. | No model tier, worker count or budget is proved optimal. |
| D13 | Patient/counterparty replies come from supplied interfaces | Internal staff cannot manufacture the missing observation. | Which counterparties/tools exist depends on the actual task. |
| D14 | Separate draft, decision, delivery and fulfillment states | Prevents a packet/notice/plan from becoming an invented external outcome. | Exact official statuses/schemas are not defined by our internal labels. |
| D15 | Internal critic uses actor-visible information only | Supports checking without becoming an oracle, official grader or appeal body. | Its net benefit and false objections require measurement. |
| D16 | Broader desks activate only with supported work/interfaces | User welcomes a detailed expanded organization, not invented hospital-world events. | Unsupported bed/service/payment functions remain inactive until actually available. |
| D17 | Standards are optional interoperability references | FHIR concepts can guide structure, but actual benchmark tools govern integration. | Release/profile/security conformance not implemented or certified. |
| D18 | Structure checks are not performance/clinical validation | A hypothetical layout can be internally complete while runtime properties remain untested. | Implementation, patient-isolation tests, clinical validity and score improvements are all unestablished. |

## Questions before implementation

1. Which actual public task/tool paths require each responsibility, and which are unnecessary for that stage?
2. Which role views/tool rights can be enforced by the actual environment versus our own wrapper?
3. What patient/case/task identity and version/readback evidence are actually available?
4. How does the chosen provider own, reset and retain session/context state between patients?
5. Which responsibilities produce measurable errors when combined, and which splits only duplicate information?
6. What aggregate inference/time budget and stop policy should govern helpers?
7. Which explicit cases/families remain reserved before choosing the architecture?
8. What permitted general sources may update job procedures, without automatic patient-derived transfer?
9. Which beyond-domain supporting functions have a real interface and relevant assigned work?
10. Which clinical/policy judgments require further source/subject-matter validation before any non-benchmark use?

The user's two clarifications are incorporated rather than left pending: finer responsibilities can be invented as design roles, and patient-derived state must not cross patients. Reusable job definitions answer the earlier ambiguous phrase “persistent roles”; retained patient history does not.
