# Evidence, design provenance and limits

The architecture is our hypothetical proposal. The sources below support benchmark scope, prior scoped healthcare knowledge, engineering mechanisms and handoff/interoperability context. They do not prove our decomposition, clinical correctness, tool compatibility or performance. No protected handbook or hidden task verifier was inspected for this design.

<a id="b01"></a>
## B01 — χ-Bench paper v3

[Paper v3](https://arxiv.org/abs/2605.16679v3), September 30, 2026 revision; abstract reopened October 18. Establishes provider prior authorization, payer utilization management and care management, plus policy-rich, multi-role and interactive workflow emphasis. Does not require one autonomous agent per profession, our 66 micro-roles or a replacement environment.

<a id="b02"></a>
## B02 — Pinned official architecture/integration

[Official docs at local pin 4444a07](https://github.com/actava-ai/chi-bench/tree/4444a07fa68a4f1623f841a292a54e284fc8e7f7/docs), previously inspected public architecture/extending docs. Distinguishes acting harness, supplied services/conversation and grading; includes an administrative failed-eligibility intake path without required clinical review. Documentation at that pin, not an executed proof of every current branch or our proposed mapping. The live integration prose differs from the pin; reconcile before implementation.

<a id="b03"></a>
## B03 — General harness engineering research

[HarnessResearch](../HarnessResearch/README.md), committed a4c5726. General mechanisms and source cases inform context/memory/effect/recovery alternatives. Synthetic lab passes do not establish this hypothetical healthcare harness's behavior. No reference implementation is selected as our blueprint.

<a id="b04"></a>
## B04 — Scoped healthcare role/authority reference

[Role research](../Plan/HealthcareRoles/README.md), evidence baseline afb2ab9. Ninety-seven functional profiles and scoped decisions supply context, not a census of separate people or verified task-specific assignments. Prior uncertainties—including program signoff, local qualifications/delegation and dated hospice applicability—remain unresolved. New computational micro-roles are explicitly design inventions, not newly discovered healthcare occupations.

<a id="b05"></a>
## B05 — Role/merger organization study

[Organization analysis](../Plan/AgentOrganization/README.md), committed a1ec02f. Provides conditional role-mode/helper/team alternatives and merger questions. Its 23 work packages are analysis categories and its pair screen is mechanical; neither proves a runtime partition or optimal agent count. The user's new finer-decomposition requirement extends this earlier work.

<a id="b06"></a>
## B06 — AHRQ TeamSTEPPS handoff guidance

[Handoff](https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/handoff.html), page reviewed May 2023, reopened October 18, 2026. Discusses uncertainty, accountability, appropriate information, acknowledgement and clarification in human care handoffs. Our task/result fields and staff handoffs are software design synthesis, not mandatory API fields or proof of professional authority transfer.

<a id="b07"></a>
## B07 — HL7 FHIR R5 overview

[FHIR overview](https://www.hl7.org/fhir/overview.html), displayed v5.0.0/R5, reopened October 18. Explains composable healthcare information resources and exchange. Resource-inspired concepts here are optional modeling references; actual mappings/profiles and benchmark integration are not implemented.

<a id="b08"></a>
## B08 — HL7 FHIR R5 security context

[FHIR security](https://www.hl7.org/fhir/security.html), displayed v5.0.0/R5, reopened October 18. Security/privacy considerations require implementation-specific controls. This design neither implements a FHIR security system nor certifies privacy/regulatory compliance. The immediate hard isolation requirement comes directly from the user.

## Design provenance

User requirements: χ-Bench supplies the work; create the hospital's working organization, not broad hospital/world simulation; decompose composite jobs into smaller design roles even where no corresponding profession exists; allow combined execution when useful; prevent patient-derived influence across patients. The proposal's module/service/memory/micro-role counts, fields, activation/composition patterns and acceptance tests are authored design choices, not source-established facts.

[Baseline hashes](baseline.json) preserve the prior inputs. The new design is unimplemented and not a clinically validated operational system. Sources and prior findings remain version/scoped; detailed public-task/tool mapping and real execution/evaluation remain future work.
