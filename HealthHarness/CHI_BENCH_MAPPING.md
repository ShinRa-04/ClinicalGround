# Pinned integration and work mapping

Engineering source review: October 18, 2026. Target checkout: `Runner/chi-bench`, commit `4444a07fa68a4f1623f841a292a54e284fc8e7f7`. This maps the public instructions and registered actor-facing tools. It is not a live schema/permission test, a benchmark score, or an audit of the protected handbook. No expected answers or verifier payloads inform the agent.

## What the supplied work actually contains

All 75 public `instruction.md` files in the three competition directories were inspected for starting stage and workspace/rule boundaries. No fixture, solution or expectation file was read for this mapping. Downloaded instructions remain local-only; this document contains aggregate workflow facts rather than reproduced cases.

| Domain | Public starting stages | Consequence for the harness |
| --- | --- | --- |
| PA / `prior_auth_provider` | 25 clinical-intake starts | Orient from the supplied request, resolve the patient/order through actual tools, then perform the required provider work. No assumption that all cases require appeals or peer-to-peer. |
| UM / `prior_auth_um` | 5 intake, 4 triage, 8 nurse-review, 4 MD-review, 4 peer-to-peer | Start at the assigned stage. An intake or nurse-review handoff is not automatically authority to perform every subsequent physician/notice operation. |
| CM / `care_management` | 25 care-management intake handoffs | Supplied instructions request intake, outreach, assessment and finalized care plan. Refusal, missing evidence and actual dialogue must remain visible. |

Instructions restrict actor namespaces and prohibit simulator source/tests/solutions/expectations inspection and fabricated evidence. CM additionally requires structured fields to be grounded in chart/transcript, and consent to follow an actual performed consent script. A general prompt or internal helper cannot manufacture that transcript.

## Actual registered surfaces

Source inspection identifies **30 provider names**, **41 payer names in the default `agent` profile**, and **16 CM names**, before runtime include/exclude filters. These counts describe code registration, not successful discovery or authorization in a running trial. Do not enable the payer `full` profile just to obtain additional capabilities.

| Supplied surface | Principal boundary | Representative tool families |
| --- | --- | --- |
| Provider MCP, default port 8020 | Provider PA work | `chart`, `cases`, `inbox`, `docs`, `forms`, `auth`, `people`, `p2p_session` |
| Payer MCP, default port 8100 | Payer UM work | `payer_intake_hub`, `triage`, `review`, `determination`, `p2p`, `p2p_session`, `payer_letter_center` |
| CM MCP, default port 8200 | Care-manager work | `cm_intake`, `cm_chart`, `cm_outreach`, `cm_assessment`, `cm_care_plan` |

Use the endpoint supplied by the actual task configuration rather than assuming a port or exposing all three endpoints to one job. Tools are discovered at runtime. Preserve exact original tool names on dispatch; an API-compatible alias is only a presentation mapping. Namespace collisions must fail rather than silently redirecting a call.

The source registrations do not supply explicit read-only annotations. Tool names are not sufficient proof of purity; some apparent reads record audit or other state. Treat unclassified calls conservatively as effects. A caller can configure reviewed annotations, but that is an engineering assertion requiring its own verification.

## Responsibility-to-surface map

These are implementation candidates and reasoning obligations, not proof that a tool enforces every role's clinical responsibility. A registered tool is not a real clinical credential. Only the actual assigned stage and environment confer the simulated operation.

| Contracts | Relevant supplied interface or input | Implementation boundary |
| --- | --- | --- |
| PA-01 | Instruction/current stage | Owner interpretation; no forced whole-hospital pipeline. |
| PA-02 | `chart.search_patients`, `cases.get_case`, returned patient/order links | Identifier equality alone cannot verify that a free-form clinical note belongs to a patient. |
| PA-03 | Chart's returned coverage snapshot | Dedicated `coverage` namespace is not in the allowed provider surface. Preserve missing benefit facts. |
| PA-04–PA-05 | Allowed handbook/reference documents, returned request/form requirements | Policy applicability is reasoning over sourced material; no invented policy API. |
| PA-06 | `chart.get_patient_chart_by_patient`, `chart.list_candidate_orders`, `docs.get_document` | Keep returned evidence distinct from agent-authored summaries. |
| PA-07–PA-08 | Existing chart/reference observations | Criteria links and contradictions are case-local interpretations. |
| PA-09 | `people` contact lookups; actual supplied communication operations where applicable | No general clinician-chat service has been established. An internal role cannot invent an answer. |
| PA-10 | Actual order/diagnosis fields and references | Coding support is a reasoning role, not code-change authority. |
| PA-11–PA-12 | `forms.list_required_forms`, `forms.save_form_response`, `forms.validate_form`, document/bundle tools | Artifact content must use observed evidence; validation is not submission. |
| PA-13 | `auth.submit_authorization` | Persist intent before effect; use actual result, no simulated acceptance. |
| PA-14–PA-15 | `auth.check_status`, `inbox` observations, `auth.respond_to_pend` | Activate only if actual assigned work/current response requires it. |
| PA-16 | `auth.request_peer_to_peer`, `auth.respond_to_peer_to_peer`, `p2p_session`, appeal tools | Counterparty replies come from the supplied interface. |
| PA-17 | No dedicated appointment/receiving-service interface established in this surface | Produce a supported handoff if requested; do not book fictional appointments. |
| PA-18 | Scoped task obligations, actual status/receipt and requested finalization | Local completeness is distinct from external receipt and official grade. |
| UM-01 | `payer_intake_hub` queue/case/document tools | Intake and case IDs come from supplied observations. |
| UM-02 | Returned intake/benefit facts and approved references | No separate general benefit service established for default actor. |
| UM-03 | `triage.get`, SLA/gold-card checks, disposition and routing tools | Do not silently upgrade routing to a clinical determination. |
| UM-04–UM-05 | Handbook and permitted references | The default payer surface does not expose the expanded policy-library family. |
| UM-06–UM-08 | `review.get_nurse_review_data`, `review.get_md_review_data`, intake documents | Extract/compare facts with source attribution; preserve assigned review stage. |
| UM-09–UM-10 | Actual document gaps, information-request/notice operations where supported | An internal reviewer is not a provider response. |
| UM-11 | Evidence/reference reasoning or supplied P2P | No universal service-specific consultant tool established. |
| UM-12 | Instruction stage, routing data, actual reviewer fields | Persona separation is not independent review or legal authority. |
| UM-13 | `review.save_criteria_evaluation`, `review.submit_nurse_case_recommendation`, `review.save_md_review`, `review.submit_md_case_decision`, `determination.finalize` | Select operations required by actual stage; recommendation, decision and final determination are different records. |
| UM-14–UM-15 | `payer_letter_center` generation, audit, delivery/readback | Generated text is not delivered correspondence. |
| UM-16–UM-17 | No `payer_appeals` tools in the default `agent` profile | Inactive as external appeals workflow unless actual tool configuration explicitly supplies it. Existing provider appeal tools do not grant payer authority. |
| UM-18 | `determination.get_summary`, actual notice/status observations | Effectuation/payment/fulfillment must not be invented. |
| CM-01 | `cm_intake.list_referral_queue`, `get_referral`, `open_case`, `cm_chart.get_chart_data`, `submit_chart_review` | Case creation/recording are effects, not reads. |
| CM-02–CM-03 | Referral/chart participant facts and outreach planning | Representation/contact facts need supplied evidence. |
| CM-04–CM-05 | `cm_outreach.start_outreach_call`, `send_message`, `get_transcript`, `end_outreach_call` | Patient answers and consent require actual dialogue. |
| CM-06 | `cm_assessment.start_assessment`, `save_section`, `complete_assessment` | Saving an assessment does not prove unsupported field content true. |
| CM-07–CM-12 | Chart/transcript plus case-local analysis | Needs, sensitive issues, goals, medication/psychosocial context and dependency planning do not confer prescribing authority. |
| CM-13 | `cm_care_plan.create_draft`, `save_care_plan`, `finalize` | Preserve draft/final distinctions and sourced claims. |
| CM-14–CM-18 | No independent referral fulfillment, appointment booking, receiving acknowledgment or asynchronous follow-up service established | Care-plan actions/handoff drafts may be supported; external fulfillment remains unconfirmed. |
| CM-19–CM-20 | New actual transcript/tool observations, case obligations and final plan | Reconcile new evidence; report unresolved work instead of claiming universal completion. |
| SH-01–SH-02 | Domain configuration, scope gate and context builder | Local engineering responsibilities, not remote hospital personnel. |
| SH-03–SH-05 | Allowlisted references, source/obligation ledger, confined artifact tools | No arbitrary host filesystem, simulator internals or protected-content exports. |
| SH-06–SH-09 | Local journal, budgets, case checkpoint, namespace checks | Local enforcement does not prove remote authorization or provider retention policies. |
| SH-10 | Optional bounded read-only analysis of actor-visible context | It is neither an external medical reviewer nor the official judge. |

## Integration contract and an important runner limit

The pinned checkout uses Harbor `BaseInstalledAgent`. The adapter belongs to this separate package and must install/package our code in each trial container. It cannot assume a host-only Python package exists inside Docker.

**The pinned `cb` runner does not route an arbitrary import path from `submission.agent`.** It checks its in-tree registry; an unknown name is passed as Harbor's built-in `-a` name. The submission validator's soft warning therefore does not prove a custom class is runnable. For an unmodified checkout, the external class is supplied to Harbor with `--agent-import-path`; a future convenience integration would need an explicit launcher or reviewed registry/config change. No registry modification or scored trial has been executed here.

Identities must be resolved from permitted runtime inputs. Do not derive patient/case IDs from disease names or read fixtures to prepopulate them. This first package's explicit scope configuration is an integration precondition; automatic discovery and safe binding of a newly created PA/CM case must be treated as separate supported behavior only where implemented and tested. Configured ID equality is not a proof of every returned record's provenance.

## Sources and reproducibility

Local source code at the pin is the integration target, rather than later live documentation. Primary source permalinks:

- [Actor tool catalog](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/mcp/catalog.py)
- [Provider registration](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/mcp/server.py)
- [Payer registration and agent/full profiles](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/mcp/payer_server.py)
- [CM registration](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/mcp/cm_server.py)
- [Runner dispatch](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/src/chi_bench/experiment/runner.py)
- [Extension instructions](https://github.com/actava-ai/chi-bench/blob/4444a07fa68a4f1623f841a292a54e284fc8e7f7/docs/extending.md)

Reviewed local SHA-256: catalog `f7972c5314b54f8dc435059a85ac445409390c5bab0688b13859d2c5e70468a8`; CM registration `3dd5e1f5cae9b3e4eeb4327da2d8f4141451938cfd87b0d96f83a3170b157031`; runner `58f82fe4ec4f2bab949cba31be1583cf7d85e952f5de94dcc4c06f4757647261`. These are public implementation-source identities, not downloaded patient-data receipts.
