# Candidate work packages

Twenty-three analysis categories account for all 97 functions. They are neither 23 required agents nor a national staffing plan. Even a merger candidate needs actual task/permission verification and empirical comparison. Profiles assigned to external/interface categories can still become acting role modes if actual task instructions assign them.

<a id="w01"></a>
## W01 — Patient and support participants

**Design category:** external; proposed, untested.

**Functions:** [P01 Patient / insured member](roles/P01.md), [P02 Informal caregiver / family support person](roles/P02.md), [P03 Legally recognized personal representative](roles/P03.md)

**Work to preserve:** Obtain goals, observations and applicable representation facts through permitted interaction.

**Why share some work:** Represent related participants in one case model, with separate identities and statement attribution; do not replace them with a worker that supplies convenient answers.

**What cannot silently collapse:** Patient choice, caregiver observation and lawful representation are different facts. Family relationship does not establish decision authority.

**Evidence that would favor splitting/revision:** A merged record attributes caregiver wishes to the patient or treats missing consent as agreement.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w02"></a>
## W02 — Advocacy and assistance interfaces

**Design category:** external; proposed, untested.

**Functions:** [P04 Appointed appeal representative](roles/P04.md), [P07 Patient-relations advocate](roles/P07.md), [U16 SHIP / consumer-assistance / ombudsman counselor](roles/U16.md)

**Work to preserve:** Clarify complaints, access barriers and permitted representative assistance.

**Why share some work:** Shared navigation and document-preparation capability may support several functions, while appointments and authority remain explicit.

**What cannot silently collapse:** Appeal appointment is distinct from treatment representation; assistance is not insurer or adjudicator decision power.

**Evidence that would favor splitting/revision:** One general advocate label silently grants authority over every dispute or patient decision.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w03"></a>
## W03 — Language and communication support

**Design category:** capability; proposed, untested.

**Functions:** [P05 Healthcare interpreter / communication-access professional](roles/P05.md), [P06 Healthcare translator](roles/P06.md)

**Work to preserve:** Support oral/written communication without changing the substantive author or decision owner.

**Why share some work:** One language service can expose separate interpretation and translation operations; a persistent autonomous persona is not inherently needed.

**What cannot silently collapse:** Written fidelity, oral turn-taking, participant comprehension and substantive consent must remain distinguishable. Qualification is not proved by a language prompt.

**Evidence that would favor splitting/revision:** Translation drops a negation, invents an answer, or is recorded as informed understanding without evidence.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w04"></a>
## W04 — Treating-team and clinical-evidence interfaces

**Design category:** external; proposed, untested.

**Functions:** [C01 Ordering / treating physician](roles/C01.md), [C02 Referring / primary-care clinician](roles/C02.md), [C03 Treating / performing specialist](roles/C03.md), [C04 Nurse practitioner](roles/C04.md), [C05 Physician assistant / associate (jurisdiction-specific title)](roles/C05.md), [C06 Registered nurse providing direct care](roles/C06.md), [C07 Licensed practical / vocational nurse](roles/C07.md), [C08 Medical assistant / clinical-support assistant](roles/C08.md), [O13 External diagnostic / clinical evidence author or custodian](roles/O13.md), [M06 Treating psychiatrist](roles/M06.md), [M27 Palliative-care clinical team member](roles/M27.md)

**Work to preserve:** Request and attribute existing clinical assessments, orders, referral context and externally produced evidence.

**Why share some work:** A shared evidence-request adapter may serve these contacts; that is an interface merger, not one interchangeable clinical occupation.

**What cannot silently collapse:** Credential, jurisdiction, privileges, authorship and treating relationship remain distinct; reading a chart is not performing treatment or acquiring prescribing authority.

**Evidence that would favor splitting/revision:** The harness fabricates a clinician statement or treats every clinical title as equivalent signatory permission.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w05"></a>
## W05 — Provider access and authorization operations

**Design category:** merge_candidate; proposed, untested.

**Functions:** [O01 Provider authorization / precertification specialist](roles/O01.md), [O02 Referral coordinator](roles/O02.md), [O03 Registration / patient-access representative](roles/O03.md), [O04 Provider insurance-verification / benefits specialist](roles/O04.md), [O05 Scheduler / procedure coordinator](roles/O05.md), [O09 Financial counselor / assistance specialist](roles/O09.md), [O12 Practice / patient-access supervisor](roles/O12.md)

**Work to preserve:** Identify the case, check administrative requirements, assemble supported materials, submit, track and coordinate scheduling/access barriers.

**Why share some work:** These operations can share a case record and an accountable workflow owner; combining them may reduce summary handoffs.

**What cannot silently collapse:** Identity, coverage verification, authorization outcome, financial estimate and service booking are different states. Management rank does not confer clinical power.

**Evidence that would favor splitting/revision:** Measured merged execution repeatedly confuses administrative states, loses obligations or lacks genuinely different access scopes.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w06"></a>
## W06 — Records, coding and documentation support

**Design category:** capability; proposed, untested.

**Functions:** [O06 HIM / release-of-information specialist](roles/O06.md), [O07 Medical coding specialist](roles/O07.md), [O08 Clinical-documentation-integrity specialist](roles/O08.md)

**Work to preserve:** Retrieve authentic records and identify coding/documentation questions with source attribution.

**Why share some work:** A bounded evidence-preparation capability can combine retrieval and consistency checks without multiple autonomous writers.

**What cannot silently collapse:** Record release, coding interpretation, clinical clarification and authentication are distinct. Staff must not create unsupported clinical facts.

**Evidence that would favor splitting/revision:** A merged evidence worker silently repairs a clinical fact instead of requesting clarification or preserving uncertainty.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w07"></a>
## W07 — Provider dispute preparation and clinical exchange

**Design category:** conditional; proposed, untested.

**Functions:** [O10 Provider denial / appeal specialist](roles/O10.md), [O11 Provider physician adviser / peer-discussion clinician](roles/O11.md)

**Work to preserve:** Assemble the correct challenge and preserve clinical contributions and process status.

**Why share some work:** Administrative filing preparation and evidence collection may share a workflow; clinical peer participation remains an explicitly authorized interface.

**What cannot silently collapse:** Peer discussion is not automatically formal appeal; filing, clinical argument, appointment, deadline and acceptance are separate.

**Evidence that would favor splitting/revision:** A merged job claims a successful appeal from a peer-discussion note or submits an unattributed clinical opinion.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w08"></a>
## W08 — Payer intake, benefits and status operations

**Design category:** merge_candidate; proposed, untested.

**Functions:** [U01 Payer UM intake coordinator](roles/U01.md), [U02 Payer eligibility / benefit specialist](roles/U02.md), [U10 Member-services representative](roles/U10.md), [U11 Provider-services representative](roles/U11.md), [U17 UM manager / operational supervisor](roles/U17.md)

**Work to preserve:** Establish administrative context, collect information, route work and communicate observed status.

**Why share some work:** A common payer case owner can combine collection and service/status functions with role-scoped operations.

**What cannot silently collapse:** Limited delegated nonclinical decisions are program-specific; medical-necessity denial and general benefits/status work remain different permissions.

**Evidence that would favor splitting/revision:** Status communication becomes an invented determination, or a clinically complete review is forced after a valid administrative terminal path.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w09"></a>
## W09 — Initial review and specialty reasoning

**Design category:** conditional; proposed, untested.

**Functions:** [U03 Payer nurse / licensed UM clinical reviewer](roles/U03.md), [U04 Payer physician reviewer / medical director acting on a case](roles/U04.md), [U05 Independent clinical / specialty consultant](roles/U05.md), [U06 Payer behavioral-health reviewer](roles/U06.md), [U07 Managed-care pharmacist / pharmacy reviewer](roles/U07.md), [U08 Delegated medical-group / review-vendor reviewer](roles/U08.md)

**Work to preserve:** Evaluate applicable criteria and evidence, request needed specialty input, and propose only authorized case actions.

**Why share some work:** Shared policy/evidence machinery can serve distinct review modes; separate bounded reasoning calls may be useful for genuinely different questions.

**What cannot silently collapse:** Professional expertise, delegation, recommendation versus determination, and actual signoff remain separate. R13 signoff tension is unresolved; delegation may exclude appeals.

**Evidence that would favor splitting/revision:** A shared review mode crosses product/delegation limits, hides conflicting evidence or requires more independent expertise than its input supports.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w10"></a>
## W10 — Notice preparation and delivery

**Design category:** capability; proposed, untested.

**Functions:** [U09 Determination / notification coordinator](roles/U09.md)

**Work to preserve:** Render and deliver the observed authorized decision with the appropriate reason and review information.

**Why share some work:** This can be a controlled operation of the payer workflow owner rather than another open-ended agent.

**What cannot silently collapse:** The notice must derive from the authoritative decision/version; drafting or delivery must not change the substantive decision.

**Evidence that would favor splitting/revision:** Notice text contradicts the stored decision, wrong recipient is used, or draft is recorded as delivered.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w11"></a>
## W11 — Internal appeal administration and reconsideration

**Design category:** protected_review; proposed, untested.

**Functions:** [U12 Internal appeal / grievance coordinator](roles/U12.md), [U13 Medical-necessity appeal / reconsideration physician](roles/U13.md)

**Work to preserve:** Establish standing/route, assemble the appeal record and obtain the applicable reconsideration outcome.

**Why share some work:** Filing support may share software, but do not collapse initial-decision ownership and a required uninvolved reconsideration function.

**What cannot silently collapse:** For the cited MA rule, actual uninvolved persons and appropriate physician expertise are requirements; a fresh LLM context is not proof of those human qualifications.

**Evidence that would favor splitting/revision:** The initial author self-certifies independent reconsideration merely by changing its role label.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w12"></a>
## W12 — External review and adjudication interfaces

**Design category:** external_review; proposed, untested.

**Functions:** [U14 Medicare Advantage independent-review entity reviewer](roles/U14.md), [U15 External-review administrator](roles/U15.md), [U18 Applicable commercial independent-review organization reviewer](roles/U18.md), [G16 Regulator / oversight official](roles/G16.md), [J01 MA administrative law judge / applicable adjudicator](roles/J01.md), [J02 Medicare Appeals Council reviewer](roles/J02.md), [J03 Federal district court in an eligible Medicare appeal](roles/J03.md)

**Work to preserve:** Identify the applicable external route, transmit authorized material, and observe externally issued outcomes.

**Why share some work:** A routing adapter can share transport/record plumbing, while preserving distinct institutions, jurisdiction, eligibility and decision authority.

**What cannot silently collapse:** MA IRE, commercial IRO, regulator, ALJ, Council and court are not one escalating internal worker. External decisions cannot be invented by a local reviewer persona.

**Evidence that would favor splitting/revision:** A harness creates a binding external reversal or moves automatically through every forum without eligibility.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w13"></a>
## W13 — Care coordination and follow-through

**Design category:** merge_candidate; proposed, untested.

**Functions:** [M01 Lead care manager / case manager](roles/M01.md), [M09 Community health worker](roles/M09.md), [M10 Patient navigator](roles/M10.md), [M11 Health-care guide / nonclinical care guide](roles/M11.md), [M13 Health educator / self-management coach](roles/M13.md), [M18 Discharge planner / transitions coordinator](roles/M18.md), [M30 Administrative care coordinator / scheduling support](roles/M30.md)

**Work to preserve:** Maintain goals, assessment context, referrals, outreach, barriers and observed follow-through across care transitions.

**Why share some work:** A case owner can combine administrative coordination, navigation and general education support while invoking specific expertise when needed.

**What cannot silently collapse:** Clinical assessment permissions, patient statements, discharge authority and professional education scope remain explicit; coordination is not physical service delivery.

**Evidence that would favor splitting/revision:** A merged worker loses patient dialogue state, invents assessment answers, or marks a referral as completed care.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w14"></a>
## W14 — Psychosocial and behavioral-health interfaces

**Design category:** conditional; proposed, untested.

**Functions:** [M02 Medical social worker (credential-dependent practice)](roles/M02.md), [M03 Licensed clinical social worker](roles/M03.md), [M07 Clinical psychologist](roles/M07.md), [M08 Licensed behavioral-health / substance-use counselor](roles/M08.md)

**Work to preserve:** Identify psychosocial needs and interpret or request appropriate specialist contributions.

**Why share some work:** Common intake/resource-finding support can be shared; separate expertise and restricted information views may be necessary for specialist reasoning.

**What cannot silently collapse:** Job title, independent clinical licensure and additional prescribing certification differ. Do not collapse social support, therapy and prescribing.

**Evidence that would favor splitting/revision:** A generic behavioral-health persona acts beyond its assigned function or exposes protected material to unrelated work.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w15"></a>
## W15 — Medication review and access

**Design category:** conditional; proposed, untested.

**Functions:** [M04 Clinical / community pharmacist](roles/M04.md), [M05 Pharmacy technician / medication-access coordinator](roles/M05.md)

**Work to preserve:** Distinguish medication expertise, existing therapy instructions and administrative access/fulfillment work.

**Why share some work:** Share a medication evidence record and access workflow, while separating clinical proposals from technician/access operations.

**What cannot silently collapse:** Protocol-authorized pharmacist activity, general prescribing and technician tasks are not equivalent; local authority is unresolved.

**Evidence that would favor splitting/revision:** Medication availability is treated as a treatment order or access staff alter therapy.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w16"></a>
## W16 — Rehabilitation, nutrition and respiratory interfaces

**Design category:** conditional; proposed, untested.

**Functions:** [M12 Registered dietitian / qualified nutrition professional](roles/M12.md), [M14 Physical therapist](roles/M14.md), [M15 Occupational therapist](roles/M15.md), [M16 Speech-language pathologist](roles/M16.md), [M17 Respiratory therapist](roles/M17.md)

**Work to preserve:** Request or summarize discipline-specific assessments and service needs.

**Why share some work:** Use a common referral/evidence adapter with discipline-specific capability selection; persistent workers only if workload and errors justify them.

**What cannot silently collapse:** Different disciplines assess different functions and have different scope; one capability catalogue is not interchangeable clinical expertise.

**Evidence that would favor splitting/revision:** A general specialist output substitutes nutrition, mobility, daily-function, communication or respiratory evidence for one another.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w17"></a>
## W17 — Receiving services and real-world fulfillment

**Design category:** external_service; proposed, untested.

**Functions:** [M19 Home-health intake / coordination clinician](roles/M19.md), [M20 Skilled-nursing / rehabilitation receiving-team coordinator](roles/M20.md), [M21 Home-health aide / personal-care worker](roles/M21.md), [M22 Community resource / housing / food / benefit-support worker](roles/M22.md), [M23 Transportation coordinator / dispatcher](roles/M23.md), [M24 Transport driver / service-delivery worker](roles/M24.md), [M25 Equipment supplier / delivery or fitting staff](roles/M25.md), [M26 Infusion / other receiving-service coordinator](roles/M26.md)

**Work to preserve:** Coordinate service acceptance, availability, scheduling and observed delivery/attendance evidence.

**Why share some work:** A shared logistics coordinator can manage requests; providers, workers and actual delivery remain distinct external parties/events.

**What cannot silently collapse:** Referral sent, accepted, scheduled, delivered and completed are separate states. Capacity and actual attendance must come from allowed observations.

**Evidence that would favor splitting/revision:** A dispatcher persona or optimistic plan is used as evidence that a person received care, transport, food or equipment.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w18"></a>
## W18 — Hospice and spiritual-care interfaces

**Design category:** external; proposed, untested.

**Functions:** [M28 Hospice interdisciplinary group and attending functions (distinct roles)](roles/M28.md), [M29 Chaplain / spiritual-care professional](roles/M29.md)

**Work to preserve:** Coordinate the appropriate hospice group/attending and spiritual support contributions.

**Why share some work:** Common communication plumbing may connect participants; the composite hospice profile must be decomposed into functions before creating worker identities.

**What cannot silently collapse:** IDG planning, designated RN coordination, attending, certification/admission and spiritual support are distinct; the cited hospice evidence is the 2025 edition.

**Evidence that would favor splitting/revision:** One hospice agent is assigned all professional decisions or spiritual support is treated as clinical certification.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w19"></a>
## W19 — Safeguarding and protection interface

**Design category:** external; proposed, untested.

**Functions:** [M31 Safeguarding / protection-service professional](roles/M31.md)

**Work to preserve:** Recognize a potential protection concern and follow an actually applicable reporting/escalation pathway.

**Why share some work:** Detection and routing can be a capability of a case owner; legal investigation/protection authority remains external.

**What cannot silently collapse:** Applicable mandate, jurisdiction, urgency and APS phase-in facts cannot be inferred from a generic concern. Child/adult pathways are not identical.

**Evidence that would favor splitting/revision:** A model resolves a safeguarding case by assertion or invents a universal reporting rule.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w20"></a>
## W20 — Policy, legal and clinical governance

**Design category:** governance; proposed, untested.

**Functions:** [G01 Provider medical director / chief medical officer](roles/G01.md), [G02 Payer medical director / clinical-program leader](roles/G02.md), [G03 UM / medical-policy committee and specialty members](roles/G03.md), [G08 Policy analyst / clinical regulatory adviser](roles/G08.md), [G09 Compliance / regulatory professional](roles/G09.md), [G17 Legal adviser / specialist legal representative](roles/G17.md)

**Work to preserve:** Establish applicable policies, approved versions and unresolved governance/legal questions.

**Why share some work:** Share policy retrieval and change tracking; proposal, clinical governance, committee approval and legal advice remain separately attributed functions.

**What cannot silently collapse:** An analyst draft or agent-generated rule is not approved policy. Provider and payer leaders have different mandates; hierarchy is not global authority.

**Evidence that would favor splitting/revision:** A task worker rewrites the controlling rule or approves its own policy revision to make a case pass.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w21"></a>
## W21 — Management, quality, analytics and learning

**Design category:** governance; proposed, untested.

**Functions:** [G04 Care-management director / manager](roles/G04.md), [G05 Clinical / case-management supervisor](roles/G05.md), [G06 Quality-improvement / audit professional](roles/G06.md), [G07 Trainer / clinical educator](roles/G07.md), [G11 Health-services / population-health data analyst](roles/G11.md), [G12 Business / workflow analyst](roles/G12.md)

**Work to preserve:** Manage process design, training, workload and aggregate quality analysis outside ordinary case execution.

**Why share some work:** A design-time analysis service may cover several functions, while runtime checks remain bounded and separate from official grading.

**What cannot silently collapse:** Operational management is not clinical or appeal authority; internal diagnostics must not read hidden verifier answers or masquerade as official scores.

**Evidence that would favor splitting/revision:** Training feedback contaminates held-out evaluation, or a self-audit is reported as independent official success.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w22"></a>
## W22 — Privacy and system-access controls

**Design category:** infrastructure; proposed, untested.

**Functions:** [G10 Privacy officer / HIM privacy specialist](roles/G10.md), [G13 EHR / clinical informatics / application-support professional](roles/G13.md), [G14 Identity / portal-access administrator](roles/G14.md)

**Work to preserve:** Constrain record access, authorized operations and technical identity/support.

**Why share some work:** Prefer explicit permission/configuration machinery plus escalation where uncertain; a persona alone cannot enforce access.

**What cannot silently collapse:** Technical access is not consent, clinical permission or substantive authorship; privacy purpose and special restrictions remain explicit.

**Evidence that would favor splitting/revision:** Every worker receives all tools/data because one shared model is assumed to have global authority.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.

<a id="w23"></a>
## W23 — Billing and post-service account interface

**Design category:** external_service; proposed, untested.

**Functions:** [G15 Billing / patient accounts / claim-denial worker](roles/G15.md)

**Work to preserve:** Track account/claim status and administrative payment questions when actually in scope.

**Why share some work:** Share identifiers and authorized documents with access/dispute workflows; invoke payment reasoning only where needed.

**What cannot silently collapse:** Prior authorization, benefit verification, claim acceptance, adjudication and payment are different states.

**Evidence that would favor splitting/revision:** Authorization success is reported as a paid claim or a completed financial outcome without evidence.

**Alternative implementations:** a shared adapter/tool, a named mode within a case owner, bounded specialist contexts, or persistent workers where justified. Which functions are actually assigned is unresolved until task/tool mapping.

**Evidence trail:** healthcare context is in each linked audited dossier; the grouping and split trigger are authored engineering hypotheses. [Decision framework](DECISION_LOG.md) and [experiment plan](EXPERIMENT_PLAN.md) describe how to challenge them.
