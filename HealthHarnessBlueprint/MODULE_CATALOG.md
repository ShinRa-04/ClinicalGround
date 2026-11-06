# Organizational modules and composite workspaces

29 logical modules organize the work. Some are composite jobs, some capabilities/services or external interfaces. This is not 29 running agents and is not the deepest decomposition: the three main jobs are built from the [66 smaller responsibility contracts](MICRO_ROLES.md). All names and boundaries are proposed, not actual benchmark API assignments.

<a id="a01"></a>
## A01 — Hospital operations coordinator

**Kind / principal:** controller / hospital

**Trigger:** A patient journey or capacity/ownership exception needs cross-department coordination.

**Responsibility:** Track queues, responsible departments, blocked obligations, capacity and service handoffs using a minimal operational view.

**Write intent:** Operational tasks, assignments and proposed scheduling changes under actual scope.

**Boundary:** Does not overrule patient consent, clinical judgment, payer decisions or external appeal bodies.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S08](SERVICE_CONTRACTS.md#s08), [S09](SERVICE_CONTRACTS.md#s09), [S10](SERVICE_CONTRACTS.md#s10), [S14](SERVICE_CONTRACTS.md#s14), [S15](SERVICE_CONTRACTS.md#s15), [S16](SERVICE_CONTRACTS.md#s16), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [O12 Practice / patient-access supervisor](../Plan/HealthcareRoles/roles/O12.md)

<a id="a02"></a>
## A02 — Provider PA case owner

**Kind / principal:** case_owner / provider

**Trigger:** An assigned provider authorization/request/dispute task needs action.

**Responsibility:** Maintain the supported request, evidence gaps, submission/receipt, payer correspondence and correct dispute route.

**Write intent:** Provider case workspace, submissions and observed status through permitted operations.

**Boundary:** Cannot invent clinical facts or treat submission, authorization, scheduling and payment as one state.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S04](SERVICE_CONTRACTS.md#s04), [S05](SERVICE_CONTRACTS.md#s05), [S07](SERVICE_CONTRACTS.md#s07), [S12](SERVICE_CONTRACTS.md#s12), [S13](SERVICE_CONTRACTS.md#s13), [S14](SERVICE_CONTRACTS.md#s14), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [O01 Provider authorization / precertification specialist](../Plan/HealthcareRoles/roles/O01.md), [O10 Provider denial / appeal specialist](../Plan/HealthcareRoles/roles/O10.md)

<a id="a03"></a>
## A03 — Payer UM case owner

**Kind / principal:** case_owner / payer

**Trigger:** An assigned payer case arrives or review/notice/implementation work remains.

**Responsibility:** Coordinate intake, benefit context, applicable review, actual authority assignment, determination and notice obligations.

**Write intent:** Payer case transitions only with the applicable operation-level task/role permission.

**Boundary:** Payer is a separate organization; operational coordination does not itself supply clinical signoff or appeals delegation.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S04](SERVICE_CONTRACTS.md#s04), [S06](SERVICE_CONTRACTS.md#s06), [S07](SERVICE_CONTRACTS.md#s07), [S12](SERVICE_CONTRACTS.md#s12), [S13](SERVICE_CONTRACTS.md#s13), [S14](SERVICE_CONTRACTS.md#s14), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [U01 Payer UM intake coordinator](../Plan/HealthcareRoles/roles/U01.md), [U08 Delegated medical-group / review-vendor reviewer](../Plan/HealthcareRoles/roles/U08.md), [U10 Member-services representative](../Plan/HealthcareRoles/roles/U10.md), [U11 Provider-services representative](../Plan/HealthcareRoles/roles/U11.md), [U17 UM manager / operational supervisor](../Plan/HealthcareRoles/roles/U17.md)

<a id="a04"></a>
## A04 — CM journey owner

**Kind / principal:** case_owner / care_program

**Trigger:** An assigned engagement, assessment, care-plan, transition or follow-up obligation is active.

**Responsibility:** Maintain actual patient responses, goals, assessments, plan contributions, referrals, barriers and observed follow-through.

**Write intent:** CM tasks, sourced assessment/plan records and permitted referral/outreach operations.

**Boundary:** Cannot infer consent, fabricate answers, alter treatment without assigned scope or mark arranged services delivered.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S07](SERVICE_CONTRACTS.md#s07), [S08](SERVICE_CONTRACTS.md#s08), [S09](SERVICE_CONTRACTS.md#s09), [S10](SERVICE_CONTRACTS.md#s10), [S12](SERVICE_CONTRACTS.md#s12), [S13](SERVICE_CONTRACTS.md#s13), [S14](SERVICE_CONTRACTS.md#s14), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [M01 Lead care manager / case manager](../Plan/HealthcareRoles/roles/M01.md), [M30 Administrative care coordinator / scheduling support](../Plan/HealthcareRoles/roles/M30.md)

<a id="a05"></a>
## A05 — Patient interaction endpoint

**Kind / principal:** external_participant_interface / patient

**Trigger:** The assigned task needs an actual supplied patient interaction or response.

**Responsibility:** Obtain and preserve separately attributed preferences, recollections, symptoms and decisions through the supplied interface.

**Write intent:** Observed patient messages and explicit preference/consent events, not internally invented answers.

**Boundary:** A harness patient persona cannot replace the supplied patient interface. Self-report is not automatically clinical ground truth.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S07](SERVICE_CONTRACTS.md#s07), [S15](SERVICE_CONTRACTS.md#s15), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [P01 Patient / insured member](../Plan/HealthcareRoles/roles/P01.md)

<a id="a06"></a>
## A06 — Caregiver and representative endpoints

**Kind / principal:** external_participant_interface / support_person

**Trigger:** A caregiver observation or specifically authorized representative contribution is required.

**Responsibility:** Provide separately attributed support/observations and exercise only recorded representation scope.

**Write intent:** Own communications and scoped representative decisions, not arbitrary patient/case facts.

**Boundary:** Different people retain separate identities, preferences and appointments; family status is not blanket authority.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S07](SERVICE_CONTRACTS.md#s07), [S15](SERVICE_CONTRACTS.md#s15), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [P02 Informal caregiver / family support person](../Plan/HealthcareRoles/roles/P02.md), [P03 Legally recognized personal representative](../Plan/HealthcareRoles/roles/P03.md)

<a id="a07"></a>
## A07 — Treating clinician role templates

**Kind / principal:** staff_role_or_service_interface / provider

**Trigger:** A clinical order, evidence author contribution, referral, specialist input or peer exchange is assigned.

**Responsibility:** Perform the actually assigned clinical-workflow function and maintain source-attributed contributions.

**Write intent:** Clinical notes/orders or peer statements only through assigned clinical-service contracts.

**Boundary:** One template is not one interchangeable credential. Perform assigned reviews/documents without inventing an examination or supplied result.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S07](SERVICE_CONTRACTS.md#s07), [S17](SERVICE_CONTRACTS.md#s17), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** [C01 Ordering / treating physician](../Plan/HealthcareRoles/roles/C01.md), [C02 Referring / primary-care clinician](../Plan/HealthcareRoles/roles/C02.md), [C03 Treating / performing specialist](../Plan/HealthcareRoles/roles/C03.md), [C04 Nurse practitioner](../Plan/HealthcareRoles/roles/C04.md), [C05 Physician assistant / associate (jurisdiction-specific title)](../Plan/HealthcareRoles/roles/C05.md), [O11 Provider physician adviser / peer-discussion clinician](../Plan/HealthcareRoles/roles/O11.md), [M06 Treating psychiatrist](../Plan/HealthcareRoles/roles/M06.md), [M27 Palliative-care clinical team member](../Plan/HealthcareRoles/roles/M27.md)

<a id="a08"></a>
## A08 — Diagnostic evidence and consultation interface

**Kind / principal:** specialist_or_adapter / assigned_organization

**Trigger:** The case needs an external result, custodian response or bounded independent specialty contribution.

**Responsibility:** Obtain attributable results or analyze a bounded question from the permitted evidence view.

**Write intent:** Source-linked consultation proposal or observed evidence receipt.

**Boundary:** A model opinion cannot create a laboratory result or binding determination. Actor author and service observation are distinct.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S07](SERVICE_CONTRACTS.md#s07), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** [O13 External diagnostic / clinical evidence author or custodian](../Plan/HealthcareRoles/roles/O13.md), [U05 Independent clinical / specialty consultant](../Plan/HealthcareRoles/roles/U05.md)

<a id="a09"></a>
## A09 — Nursing and direct-care role templates

**Kind / principal:** staff_role_or_service_interface / care_provider

**Trigger:** A scoped nursing/support/direct-care activity is assigned or observed.

**Responsibility:** Represent the specifically assigned care activity and communicate actual observations/events.

**Write intent:** Role-scoped observations/tasks; physical completion only from actual environment/service evidence.

**Boundary:** RN, LPN/LVN, clinical assistant and aide remain distinct qualifications/functions, not a merged universal scope.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S07](SERVICE_CONTRACTS.md#s07), [S08](SERVICE_CONTRACTS.md#s08), [S11](SERVICE_CONTRACTS.md#s11), [S17](SERVICE_CONTRACTS.md#s17), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** [C06 Registered nurse providing direct care](../Plan/HealthcareRoles/roles/C06.md), [C07 Licensed practical / vocational nurse](../Plan/HealthcareRoles/roles/C07.md), [C08 Medical assistant / clinical-support assistant](../Plan/HealthcareRoles/roles/C08.md), [M21 Home-health aide / personal-care worker](../Plan/HealthcareRoles/roles/M21.md)

<a id="a10"></a>
## A10 — Registration and benefits desk

**Kind / principal:** role_mode_or_tool / assigned_organization

**Trigger:** Identity, coverage, eligibility or administrative requirements must be established.

**Responsibility:** Match the correct person/case and retrieve scoped coverage/benefit facts.

**Write intent:** Verified administrative records and only explicitly delegated benefit operations.

**Boundary:** Provider and payer instances use separate principals. Benefits are not authorization or guaranteed payment.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S04](SERVICE_CONTRACTS.md#s04), [S05](SERVICE_CONTRACTS.md#s05), [S06](SERVICE_CONTRACTS.md#s06), [S14](SERVICE_CONTRACTS.md#s14), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [O03 Registration / patient-access representative](../Plan/HealthcareRoles/roles/O03.md), [O04 Provider insurance-verification / benefits specialist](../Plan/HealthcareRoles/roles/O04.md), [U02 Payer eligibility / benefit specialist](../Plan/HealthcareRoles/roles/U02.md)

<a id="a11"></a>
## A11 — Evidence and documentation auditor

**Kind / principal:** bounded_capability / caller_scope

**Trigger:** Missing, conflicting, stale or unauthorized documentation needs inspection.

**Responsibility:** Assemble provenance, identify gaps/contradictions and recommend clarification.

**Write intent:** Read-only findings/proposals by default; no silent repair of substantive clinical facts.

**Boundary:** Release purpose, source author and documentation meaning remain separate; requester cannot self-supply missing evidence.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [O06 HIM / release-of-information specialist](../Plan/HealthcareRoles/roles/O06.md), [O08 Clinical-documentation-integrity specialist](../Plan/HealthcareRoles/roles/O08.md)

<a id="a12"></a>
## A12 — Policy and criteria specialist

**Kind / principal:** bounded_capability / caller_scope

**Trigger:** Applicable policy/version or criterion-evidence mapping needs analysis.

**Responsibility:** Return sourced criteria, applicability/exception questions, evidence links and unresolved items.

**Write intent:** Version-linked interpretation proposal; controlling policy is immutable to ordinary workers.

**Boundary:** Generated policy summaries cannot approve or replace governing rules.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [G08 Policy analyst / clinical regulatory adviser](../Plan/HealthcareRoles/roles/G08.md)

<a id="a13"></a>
## A13 — Coding support

**Kind / principal:** bounded_capability / provider

**Trigger:** A supported code/documentation mapping is required by the assigned workflow.

**Responsibility:** Suggest coding from authentic source documentation and flag ambiguity.

**Write intent:** Coding proposals/queries or scoped administrative edits when assigned.

**Boundary:** A code does not create a diagnosis or replace clinician-authored facts.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S05](SERVICE_CONTRACTS.md#s05), [S12](SERVICE_CONTRACTS.md#s12), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [O07 Medical coding specialist](../Plan/HealthcareRoles/roles/O07.md)

<a id="a14"></a>
## A14 — Artifact and handoff writer

**Kind / principal:** bounded_capability / caller_scope

**Trigger:** A task requires a packet, summary, care-plan section or handoff artifact.

**Responsibility:** Render source-linked documents from approved facts/proposals with explicit unknowns and status.

**Write intent:** Draft artifacts; final publication only through the actual case/action authority.

**Boundary:** Writing convincing prose is not substantive approval, delivery or independent evidence.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S08](SERVICE_CONTRACTS.md#s08), [S12](SERVICE_CONTRACTS.md#s12), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** New technical/design responsibility; not an asserted existing healthcare occupation.

<a id="a15"></a>
## A15 — Conversation and access support

**Kind / principal:** role_mode_or_capability / caller_scope

**Trigger:** Outreach, interview, interpretation, translation or education support is needed.

**Responsibility:** Track speakers, questions, actual answers, language needs, refusals and unresolved comprehension.

**Write intent:** Attributed conversation events and education/communication artifacts.

**Boundary:** Translation, interpretation, understanding and consent are different; use actual qualification/task scope.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S07](SERVICE_CONTRACTS.md#s07), [S08](SERVICE_CONTRACTS.md#s08), [S12](SERVICE_CONTRACTS.md#s12), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [P05 Healthcare interpreter / communication-access professional](../Plan/HealthcareRoles/roles/P05.md), [P06 Healthcare translator](../Plan/HealthcareRoles/roles/P06.md), [M13 Health educator / self-management coach](../Plan/HealthcareRoles/roles/M13.md)

<a id="a16"></a>
## A16 — Navigation and transitions desk

**Kind / principal:** role_mode_or_capability / care_program

**Trigger:** Referral coordination, access assistance, transition ownership or scoped advocacy is active.

**Responsibility:** Connect the right recipient, track acceptance/obligations and retain appointment/representation limits.

**Write intent:** Referral/navigation tasks, observed replies and scoped filing assistance.

**Boundary:** This template combines reusable plumbing, not all advocacy, discharge and clinical decision powers.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S05](SERVICE_CONTRACTS.md#s05), [S07](SERVICE_CONTRACTS.md#s07), [S08](SERVICE_CONTRACTS.md#s08), [S09](SERVICE_CONTRACTS.md#s09), [S10](SERVICE_CONTRACTS.md#s10), [S12](SERVICE_CONTRACTS.md#s12), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [O02 Referral coordinator](../Plan/HealthcareRoles/roles/O02.md), [P04 Appointed appeal representative](../Plan/HealthcareRoles/roles/P04.md), [P07 Patient-relations advocate](../Plan/HealthcareRoles/roles/P07.md), [U16 SHIP / consumer-assistance / ombudsman counselor](../Plan/HealthcareRoles/roles/U16.md), [M09 Community health worker](../Plan/HealthcareRoles/roles/M09.md), [M10 Patient navigator](../Plan/HealthcareRoles/roles/M10.md), [M11 Health-care guide / nonclinical care guide](../Plan/HealthcareRoles/roles/M11.md), [M18 Discharge planner / transitions coordinator](../Plan/HealthcareRoles/roles/M18.md)

<a id="a17"></a>
## A17 — Medication expertise and access interfaces

**Kind / principal:** bounded_specialist_or_adapter / assigned_organization

**Trigger:** A medication evidence, pharmacy review or access/fulfillment question is relevant.

**Responsibility:** Separate medication expertise, existing instructions, allowed protocol activity and technician/access work.

**Write intent:** Scoped recommendations/access tasks; therapy changes only through the assigned order contract.

**Boundary:** Inventory or authorization success does not establish a new treatment order or administration.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S04](SERVICE_CONTRACTS.md#s04), [S09](SERVICE_CONTRACTS.md#s09), [S11](SERVICE_CONTRACTS.md#s11), [S17](SERVICE_CONTRACTS.md#s17), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** [M04 Clinical / community pharmacist](../Plan/HealthcareRoles/roles/M04.md), [M05 Pharmacy technician / medication-access coordinator](../Plan/HealthcareRoles/roles/M05.md)

<a id="a18"></a>
## A18 — Psychosocial, behavioral and safeguarding interfaces

**Kind / principal:** bounded_specialist_or_adapter / assigned_organization

**Trigger:** A psychosocial need, specialist input, restricted material or protection concern is present.

**Responsibility:** Identify the relevant function, credential/mandate and appropriate information/escalation pathway.

**Write intent:** Bounded specialist contribution, resource/protection routing and permitted case records.

**Boundary:** Resource support, therapy, prescribing and protection authority are distinct; sensitive evidence views remain scoped.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S07](SERVICE_CONTRACTS.md#s07), [S08](SERVICE_CONTRACTS.md#s08), [S09](SERVICE_CONTRACTS.md#s09), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [M02 Medical social worker (credential-dependent practice)](../Plan/HealthcareRoles/roles/M02.md), [M03 Licensed clinical social worker](../Plan/HealthcareRoles/roles/M03.md), [M07 Clinical psychologist](../Plan/HealthcareRoles/roles/M07.md), [M08 Licensed behavioral-health / substance-use counselor](../Plan/HealthcareRoles/roles/M08.md), [M31 Safeguarding / protection-service professional](../Plan/HealthcareRoles/roles/M31.md)

<a id="a19"></a>
## A19 — Rehabilitation, nutrition and respiratory interfaces

**Kind / principal:** bounded_specialist_or_adapter / care_provider

**Trigger:** The actual case needs discipline-specific assessment/evidence or service coordination.

**Responsibility:** Produce or obtain specifically attributed discipline contributions from permitted task evidence.

**Write intent:** Scoped recommendations/referrals and observed discipline records.

**Boundary:** A common interface does not make these professions clinically interchangeable or prove service delivery.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S08](SERVICE_CONTRACTS.md#s08), [S09](SERVICE_CONTRACTS.md#s09), [S11](SERVICE_CONTRACTS.md#s11), [S17](SERVICE_CONTRACTS.md#s17), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** [M12 Registered dietitian / qualified nutrition professional](../Plan/HealthcareRoles/roles/M12.md), [M14 Physical therapist](../Plan/HealthcareRoles/roles/M14.md), [M15 Occupational therapist](../Plan/HealthcareRoles/roles/M15.md), [M16 Speech-language pathologist](../Plan/HealthcareRoles/roles/M16.md), [M17 Respiratory therapist](../Plan/HealthcareRoles/roles/M17.md)

<a id="a20"></a>
## A20 — Access, receiving services and fulfillment network

**Kind / principal:** external_service_adapter / external_service

**Trigger:** Capacity, placement, booking, financial support, transport, equipment or receiving-service status is needed.

**Responsibility:** Coordinate requests with distinct service organizations and observe acceptance, reservations and fulfillment.

**Write intent:** Permitted reservations/requests and attributable status/financial events.

**Boundary:** Dispatch is not driving; booking is not attendance; request is not acceptance; authorization is not payment.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S07](SERVICE_CONTRACTS.md#s07), [S09](SERVICE_CONTRACTS.md#s09), [S10](SERVICE_CONTRACTS.md#s10), [S11](SERVICE_CONTRACTS.md#s11), [S12](SERVICE_CONTRACTS.md#s12), [S15](SERVICE_CONTRACTS.md#s15), [S17](SERVICE_CONTRACTS.md#s17), [S20](SERVICE_CONTRACTS.md#s20)

**Prior healthcare context:** [O05 Scheduler / procedure coordinator](../Plan/HealthcareRoles/roles/O05.md), [O09 Financial counselor / assistance specialist](../Plan/HealthcareRoles/roles/O09.md), [M19 Home-health intake / coordination clinician](../Plan/HealthcareRoles/roles/M19.md), [M20 Skilled-nursing / rehabilitation receiving-team coordinator](../Plan/HealthcareRoles/roles/M20.md), [M22 Community resource / housing / food / benefit-support worker](../Plan/HealthcareRoles/roles/M22.md), [M23 Transportation coordinator / dispatcher](../Plan/HealthcareRoles/roles/M23.md), [M24 Transport driver / service-delivery worker](../Plan/HealthcareRoles/roles/M24.md), [M25 Equipment supplier / delivery or fitting staff](../Plan/HealthcareRoles/roles/M25.md), [M26 Infusion / other receiving-service coordinator](../Plan/HealthcareRoles/roles/M26.md), [G15 Billing / patient accounts / claim-denial worker](../Plan/HealthcareRoles/roles/G15.md)

<a id="a21"></a>
## A21 — Initial UM clinical review roles

**Kind / principal:** assigned_review_role / payer

**Trigger:** Actual criteria/stage require the assigned qualified review or specialty analysis.

**Responsibility:** Apply applicable evidence and criteria; recommend/escalate or determine only under the specific assignment.

**Write intent:** Stage-scoped review contribution and authorized outcome where the task/profile permits.

**Boundary:** Initial review, consultation and reconsideration are distinct; no universal physician-only or unrestricted denial rule is invented.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S06](SERVICE_CONTRACTS.md#s06), [S07](SERVICE_CONTRACTS.md#s07), [S13](SERVICE_CONTRACTS.md#s13), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [U03 Payer nurse / licensed UM clinical reviewer](../Plan/HealthcareRoles/roles/U03.md), [U04 Payer physician reviewer / medical director acting on a case](../Plan/HealthcareRoles/roles/U04.md), [U06 Payer behavioral-health reviewer](../Plan/HealthcareRoles/roles/U06.md), [U07 Managed-care pharmacist / pharmacy reviewer](../Plan/HealthcareRoles/roles/U07.md)

<a id="a22"></a>
## A22 — Appeal administration and reconsideration roles

**Kind / principal:** separate_review_role / payer_or_review_body

**Trigger:** A proper appeal/reconsideration route is invoked and within scope.

**Responsibility:** Separate route/standing/file preparation from the required reconsidered decision and independence conditions.

**Write intent:** Scoped appeal records and observed/authorized reconsideration contributions.

**Boundary:** Independent actor assignment is more than a new prompt; a software simulation does not certify real human legal qualification.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S06](SERVICE_CONTRACTS.md#s06), [S07](SERVICE_CONTRACTS.md#s07), [S12](SERVICE_CONTRACTS.md#s12), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [U12 Internal appeal / grievance coordinator](../Plan/HealthcareRoles/roles/U12.md), [U13 Medical-necessity appeal / reconsideration physician](../Plan/HealthcareRoles/roles/U13.md)

<a id="a23"></a>
## A23 — External review, regulator and court adapters

**Kind / principal:** external_participant_adapter / external_review_body

**Trigger:** The identified product/issue/stage permits an external route.

**Responsibility:** Represent distinct eligible forums and ingest their attributable supplied outcomes.

**Write intent:** Route-specific transmission/status and outcomes only through the corresponding environment service.

**Boundary:** A local critic cannot issue a binding IRE/IRO/court result. Routes and later-stage eligibility are not automatic.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S06](SERVICE_CONTRACTS.md#s06), [S07](SERVICE_CONTRACTS.md#s07), [S12](SERVICE_CONTRACTS.md#s12), [S15](SERVICE_CONTRACTS.md#s15), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [U14 Medicare Advantage independent-review entity reviewer](../Plan/HealthcareRoles/roles/U14.md), [U15 External-review administrator](../Plan/HealthcareRoles/roles/U15.md), [U18 Applicable commercial independent-review organization reviewer](../Plan/HealthcareRoles/roles/U18.md), [G16 Regulator / oversight official](../Plan/HealthcareRoles/roles/G16.md), [J01 MA administrative law judge / applicable adjudicator](../Plan/HealthcareRoles/roles/J01.md), [J02 Medicare Appeals Council reviewer](../Plan/HealthcareRoles/roles/J02.md), [J03 Federal district court in an eligible Medicare appeal](../Plan/HealthcareRoles/roles/J03.md)

<a id="a24"></a>
## A24 — Determination notice operation

**Kind / principal:** controlled_operation / payer

**Trigger:** An actual authorized determination requires a notice/delivery action.

**Responsibility:** Generate and deliver the corresponding reason/outcome/recipient/version and preserve delivery evidence.

**Write intent:** Notice artifacts and observed delivery receipts, not the underlying decision itself.

**Boundary:** A draft notice cannot change a decision or be represented as delivered.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S06](SERVICE_CONTRACTS.md#s06), [S12](SERVICE_CONTRACTS.md#s12), [S14](SERVICE_CONTRACTS.md#s14), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [U09 Determination / notification coordinator](../Plan/HealthcareRoles/roles/U09.md)

<a id="a25"></a>
## A25 — Quality and workflow analyst

**Kind / principal:** bounded_critic_or_design_capability / permitted_audit_scope

**Trigger:** A meaningful checkpoint needs an invariant review, or permitted post-run aggregate analysis is requested.

**Responsibility:** Inspect source/state consistency, missing obligations and actual process metrics.

**Write intent:** Findings/proposals and scoped audit summaries; no automatic world truth or official grade.

**Boundary:** An internal critic is not independent reconsideration or the hidden evaluator; aggregate evidence is not a patient fact.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S03](SERVICE_CONTRACTS.md#s03), [S13](SERVICE_CONTRACTS.md#s13), [S16](SERVICE_CONTRACTS.md#s16), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [G06 Quality-improvement / audit professional](../Plan/HealthcareRoles/roles/G06.md), [G11 Health-services / population-health data analyst](../Plan/HealthcareRoles/roles/G11.md), [G12 Business / workflow analyst](../Plan/HealthcareRoles/roles/G12.md)

<a id="a26"></a>
## A26 — Governance and staffing configuration

**Kind / principal:** configuration_or_governance_interface / organization_governance

**Trigger:** Work needs approved policy, actual assignment, staffing or governance clarification.

**Responsibility:** Supply versioned mandates/approval records and distinct institutional governance actors.

**Write intent:** Design-time approved configuration or specifically authorized governance records.

**Boundary:** Ordinary task workers cannot rewrite policy, appoint themselves to every role or override other organizations.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S03](SERVICE_CONTRACTS.md#s03), [S16](SERVICE_CONTRACTS.md#s16), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [G01 Provider medical director / chief medical officer](../Plan/HealthcareRoles/roles/G01.md), [G02 Payer medical director / clinical-program leader](../Plan/HealthcareRoles/roles/G02.md), [G03 UM / medical-policy committee and specialty members](../Plan/HealthcareRoles/roles/G03.md), [G04 Care-management director / manager](../Plan/HealthcareRoles/roles/G04.md), [G05 Clinical / case-management supervisor](../Plan/HealthcareRoles/roles/G05.md), [G07 Trainer / clinical educator](../Plan/HealthcareRoles/roles/G07.md), [G09 Compliance / regulatory professional](../Plan/HealthcareRoles/roles/G09.md), [G17 Legal adviser / specialist legal representative](../Plan/HealthcareRoles/roles/G17.md)

<a id="a27"></a>
## A27 — Privacy, identity and infrastructure guard

**Kind / principal:** deterministic_service / runtime_control

**Trigger:** Every retrieval, prompt build, delegation and operation crosses a scope/resource boundary.

**Responsibility:** Enforce principal/purpose/version/tool constraints and retain diagnostic provenance.

**Write intent:** Permission/audit decisions, scoped technical state and declared exceptions.

**Boundary:** A guard is not legal certification; technical access does not establish clinical authorship or consent.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S13](SERVICE_CONTRACTS.md#s13), [S14](SERVICE_CONTRACTS.md#s14), [S16](SERVICE_CONTRACTS.md#s16), [S17](SERVICE_CONTRACTS.md#s17)

**Prior healthcare context:** [G10 Privacy officer / HIM privacy specialist](../Plan/HealthcareRoles/roles/G10.md), [G13 EHR / clinical informatics / application-support professional](../Plan/HealthcareRoles/roles/G13.md), [G14 Identity / portal-access administrator](../Plan/HealthcareRoles/roles/G14.md)

<a id="a28"></a>
## A28 — Benchmark adapter and evaluation boundary

**Kind / principal:** boundary_service / runtime_boundary

**Trigger:** A supplied task is admitted, a concrete tool is called or post-run evaluation is inspected.

**Responsibility:** Map internal work to actual task instructions and tool contracts while isolating official grading from acting inputs.

**Write intent:** Adapter/session metadata and observed response receipts; never hidden world or expected-answer state.

**Boundary:** The supplied environment owns facts and counterparties. This is an interface boundary, not a second simulator or an acting evaluator.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S14](SERVICE_CONTRACTS.md#s14), [S15](SERVICE_CONTRACTS.md#s15), [S16](SERVICE_CONTRACTS.md#s16), [S18](SERVICE_CONTRACTS.md#s18), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** New technical/design responsibility; not an asserted existing healthcare occupation.

<a id="a29"></a>
## A29 — Hospice and spiritual-care pathway

**Kind / principal:** composite_pathway / care_provider

**Trigger:** The assigned case actually includes a hospice/palliative/spiritual-support pathway.

**Responsibility:** Route distinct IDG, RN coordination, attending, certification/admission and requested spiritual-support contributions.

**Write intent:** Pathway tasks and specifically attributed role contributions under the applicable task/policy.

**Boundary:** A composite profile must not become one all-powerful hospice agent; prior hospice evidence is a dated codification.

**Instantiation:** On demand by organization, case, assignment and role; not one global persona.

**Service contracts:** [S01](SERVICE_CONTRACTS.md#s01), [S02](SERVICE_CONTRACTS.md#s02), [S07](SERVICE_CONTRACTS.md#s07), [S08](SERVICE_CONTRACTS.md#s08), [S09](SERVICE_CONTRACTS.md#s09), [S17](SERVICE_CONTRACTS.md#s17), [S19](SERVICE_CONTRACTS.md#s19)

**Prior healthcare context:** [M28 Hospice interdisciplinary group and attending functions (distinct roles)](../Plan/HealthcareRoles/roles/M28.md), [M29 Chaplain / spiritual-care professional](../Plan/HealthcareRoles/roles/M29.md)
