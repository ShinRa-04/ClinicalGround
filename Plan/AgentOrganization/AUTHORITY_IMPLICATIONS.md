# Authority implications for the software design

Every one of the 34 prior questions is mapped below. The old healthcare statement retains its original scope; the software implication is a proposed design response. This is not a new legal/clinical audit or a verified task-specific permission model.

<a id="d01"></a>
## D01 — Who chooses whether to accept proposed treatment?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d01)

**Design implication:** Keep patient decision evidence external to the worker’s own proposals; merging communication and planning must not create consent.

**Retained scope:** Hospital rights under A01; capacity/minor/emergency and other exceptions require additional applicable law.

**Affected packages:** [W01](WORK_PACKAGES.md#w01), [W04](WORK_PACKAGES.md#w04)

<a id="d02"></a>
## D02 — Who establishes representative authority?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d02)

**Design implication:** Store representative identity, scope and evidence separately from informal family contact.

**Retained scope:** Healthcare personal representation and appeal standing are separate determinations.

**Affected packages:** [W01](WORK_PACKAGES.md#w01), [W02](WORK_PACKAGES.md#w02), [W20](WORK_PACKAGES.md#w20), [W22](WORK_PACKAGES.md#w22)

<a id="d03"></a>
## D03 — Who recommends/orders clinical treatment?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d03)

**Design implication:** Clinical evidence organization and clinician authorship/order permission are distinct even in one executable.

**Retained scope:** Profession/state/practice arrangement and patient consent must be established.

**Affected packages:** [W04](WORK_PACKAGES.md#w04)

<a id="d04"></a>
## D04 — Does a treating specialist automatically outrank the PCP?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d04)

**Design implication:** Route by the actual issue and mandate, not a fabricated specialty seniority ladder.

**Retained scope:** Actual episode, privileges and local responsibility assignment determine signoff.

**Affected packages:** [W04](WORK_PACKAGES.md#w04)

<a id="d05"></a>
## D05 — Can an NP act independently?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d05)

**Design implication:** Parameterize applicable NP practice/furnishing/employer conditions; do not bake a universal role hierarchy into prompts.

**Retained scope:** State and actual activity must be specified.

**Affected packages:** [W04](WORK_PACKAGES.md#w04)

<a id="d06"></a>
## D06 — Who supervises PA practice?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d06)

**Design implication:** Represent the actual PA arrangement explicitly; a generic supervisor agent is insufficient evidence.

**Retained scope:** State, privileges and agreement are unresolved until identified.

**Affected packages:** [W04](WORK_PACKAGES.md#w04)

<a id="d07"></a>
## D07 — Can an RN delegate any assigned task?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d07)

**Design implication:** Delegation needs activity/credential/competence scope; coordinator assignment cannot expand it.

**Retained scope:** No nationwide permission for a specific drug, IV task or assessment is assumed.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W17](WORK_PACKAGES.md#w17)

<a id="d08"></a>
## D08 — Who supplies the clinical facts in a request?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d08)

**Design implication:** Evidence-assembly capability must preserve substantive author identity and never manufacture clinical facts.

**Retained scope:** Hospital authentication requirement A15; other settings need their rules.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W06](WORK_PACKAGES.md#w06)

<a id="d09"></a>
## D09 — Who selects supported administrative codes?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d09)

**Design implication:** Coding suggestions should remain traceable to documentation rather than become independent proof of a clinical condition.

**Retained scope:** Code system, service and documentation must match actual context.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W06](WORK_PACKAGES.md#w06)

<a id="d10"></a>
## D10 — Is benefit verification the same as authorization?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d10)

**Design implication:** Use separate state fields for benefits, authorization and later payment.

**Retained scope:** Plan and service determine required checks.

**Affected packages:** [W05](WORK_PACKAGES.md#w05), [W08](WORK_PACKAGES.md#w08)

<a id="d11"></a>
## D11 — Can first-level UM approve a request?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d11)

**Design implication:** Allow documented limited nonclinical alternatives where applicable; do not require a clinical agent in every valid path.

**Retained scope:** R12/R13 are example programs; no universal program permission is inferred. R13 also states medical-director final responsibility and wider professional categories; exact case signoff needs clarification.

**Affected packages:** [W08](WORK_PACKAGES.md#w08), [W09](WORK_PACKAGES.md#w09)

<a id="d12"></a>
## D12 — Who reviews anticipated adverse MA medical necessity?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d12)

**Design implication:** Model the actual initial-review qualification route, including appropriate nonphysician possibilities; a title alone is inadequate.

**Retained scope:** MA initial adverse medical necessity; integrated-plan exception in 422.566(a) and different decision types must be checked.

**Affected packages:** [W09](WORK_PACKAGES.md#w09)

<a id="d13"></a>
## D13 — Who may reconsider an MA medical-necessity denial?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d13)

**Design implication:** Preserve required uninvolved reconsideration/accountability; fresh LLM context is only a software-review experiment.

**Retained scope:** Specified MA reconsideration route; not a universal rule for every product/dispute.

**Affected packages:** [W11](WORK_PACKAGES.md#w11)

<a id="d14"></a>
## D14 — Does peer-to-peer discussion replace appeal?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d14)

**Design implication:** Track peer exchange and formal filing as different transitions and outputs.

**Retained scope:** Plan/state/service process determines relationship between discussion and appeal.

**Affected packages:** [W07](WORK_PACKAGES.md#w07), [W09](WORK_PACKAGES.md#w09)

<a id="d15"></a>
## D15 — Can MA independent review reverse payer review?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d15)

**Design implication:** Observe external outcomes; do not let an internal critic manufacture IRE authority or assume instant effectuation.

**Retained scope:** 422.592 and 422.618; deadlines and further appeal rights differ by decision type.

**Affected packages:** [W10](WORK_PACKAGES.md#w10), [W11](WORK_PACKAGES.md#w11), [W12](WORK_PACKAGES.md#w12)

<a id="d16"></a>
## D16 — Can commercial independent review supersede insurer denial?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d16)

**Design implication:** Keep commercial review distinct and permit eligible urgent concurrency instead of an unconditional linear ladder.

**Retained scope:** Determine product, eligibility, issue and route first. Check the applicable ACA/non-grandfathered context and actual external-review eligibility. Eligible urgent external review may be requested concurrently with internal appeal.

**Affected packages:** [W12](WORK_PACKAGES.md#w12)

<a id="d17"></a>
## D17 — Are later MA appeal forums above the prior decision?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d17)

**Design implication:** Represent later forums as conditional external interfaces rather than an internal management hierarchy.

**Retained scope:** A16 includes a Council-review effectuation exception; further appeal can affect implementation.

**Affected packages:** [W12](WORK_PACKAGES.md#w12)

<a id="d18"></a>
## D18 — Does coverage approval order the clinician to treat?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d18)

**Design implication:** Never merge coverage outcome, clinical instruction and patient consent into one approval flag.

**Retained scope:** Functional separation; actual service and rights still apply.

**Affected packages:** [W01](WORK_PACKAGES.md#w01), [W04](WORK_PACKAGES.md#w04), [W09](WORK_PACKAGES.md#w09)

<a id="d19"></a>
## D19 — Who approves MA utilization policy?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d19)

**Design implication:** Use an approved policy/version source; policy drafting by a helper must not alter controlling rules.

**Retained scope:** MA-specific committee requirements; other products need their own governance.

**Affected packages:** [W20](WORK_PACKAGES.md#w20)

<a id="d20"></a>
## D20 — Does policy committee rank supersede every case appeal?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d20)

**Design implication:** Separate policy governance from the applicable case-appeal route.

**Retained scope:** No committee-to-IRE command edge exists in this map.

**Affected packages:** [W11](WORK_PACKAGES.md#w11), [W12](WORK_PACKAGES.md#w12), [W20](WORK_PACKAGES.md#w20)

<a id="d21"></a>
## D21 — Who owns the shared care-coordination plan?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d21)

**Design implication:** Keep a clear plan/case owner while attributing each discipline and patient contribution.

**Retained scope:** Program-specific professional background and permissions.

**Affected packages:** [W01](WORK_PACKAGES.md#w01), [W04](WORK_PACKAGES.md#w04), [W13](WORK_PACKAGES.md#w13)

<a id="d22"></a>
## D22 — Who develops hospital discharge planning?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d22)

**Design implication:** Transition coordination can share workflow state without being confused with all medical discharge authority.

**Retained scope:** Hospital discharge setting; patient goals/access and information transfer requirements also apply.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W13](WORK_PACKAGES.md#w13), [W14](WORK_PACKAGES.md#w14)

<a id="d23"></a>
## D23 — Who signs/changes the home-health medical plan?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d23)

**Design implication:** Separate service scheduling from the permitted medical-plan signature/change function.

**Retained scope:** Home-health setting; state law and agency policy apply to verbal orders and allowed activities.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W17](WORK_PACKAGES.md#w17)

<a id="d24"></a>
## D24 — Does referral acceptance mean the service happened?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d24)

**Design implication:** Require observed acceptance/delivery states; a model’s plan is not a completed service.

**Retained scope:** Operational synthesis supporting closed-loop coordination, not a universal mandated form.

**Affected packages:** [W05](WORK_PACKAGES.md#w05), [W13](WORK_PACKAGES.md#w13), [W17](WORK_PACKAGES.md#w17)

<a id="d25"></a>
## D25 — Can a technician change medication therapy?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d25)

**Design implication:** Share medication data but keep access/technician activity distinct from therapy changes.

**Retained scope:** Specific technician, pharmacist and prescribing permissions remain state/program-specific.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W15](WORK_PACKAGES.md#w15)

<a id="d26"></a>
## D26 — Does psychologist/counselor title imply prescribing?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d26)

**Design implication:** Treat actual credential/jurisdiction permissions as facts to establish, not as powers granted by a specialist prompt.

**Retained scope:** Jurisdiction and specialty qualification required.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W14](WORK_PACKAGES.md#w14)

<a id="d27"></a>
## D27 — Who can approve information sharing?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d27)

**Design implication:** Scope data views and recipients by purpose and actual permissions, preserving exceptions and special restrictions.

**Retained scope:** A10 lists minimum-necessary exceptions including specified treatment disclosures; other protections still apply. Applicable Part 2 records and separate SUD counseling notes illustrate additional consent distinctions; a HIPAA minimum-necessary exception is not blanket disclosure permission.

**Affected packages:** [W01](WORK_PACKAGES.md#w01), [W06](WORK_PACKAGES.md#w06), [W22](WORK_PACKAGES.md#w22)

<a id="d28"></a>
## D28 — Can interpreter or navigator decide for the patient?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d28)

**Design implication:** Language/navigation capability must not answer for the patient or acquire representation authority.

**Retained scope:** Additional independent license/appointment, if any, must be established separately.

**Affected packages:** [W03](WORK_PACKAGES.md#w03), [W13](WORK_PACKAGES.md#w13)

<a id="d29"></a>
## D29 — Can a manager overrule a licensed professional on any task?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d29)

**Design implication:** The orchestrator allocates work; it cannot gain every clinical permission by being called a manager.

**Retained scope:** Actual organogram and professional/practice rules required.

**Affected packages:** [W05](WORK_PACKAGES.md#w05), [W08](WORK_PACKAGES.md#w08), [W21](WORK_PACKAGES.md#w21)

<a id="d30"></a>
## D30 — Does an EHR administrator have clinical editing authority?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d30)

**Design implication:** Technical write access must not be mistaken for authorized clinical authorship.

**Retained scope:** Hospital authentication A15 and applicable access controls.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W22](WORK_PACKAGES.md#w22)

<a id="d31"></a>
## D31 — Who decides equipment or transport suitability?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d31)

**Design implication:** Logistics, clinical suitability and observed physical fulfillment need separate evidence.

**Retained scope:** Exact equipment/transport protocol not established universally; CMS device example is service-specific.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W17](WORK_PACKAGES.md#w17)

<a id="d32"></a>
## D32 — Who approves financial assistance or final payment?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d32)

**Design implication:** Track financial application/approval/payment separately from authorization and coverage.

**Retained scope:** Program and claim rules must be identified.

**Affected packages:** [W05](WORK_PACKAGES.md#w05), [W23](WORK_PACKAGES.md#w23)

<a id="d33"></a>
## D33 — Does hospice team composition create one boss over every profession?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d33)

**Design implication:** Decompose the composite hospice profile into IDG, RN, attending, certification/admission and support functions before assigning workers.

**Retained scope:** V11/V16/V17 establish that codified edition; a complete current-2026 update audit and actual hospice assignment are not established.

**Affected packages:** [W04](WORK_PACKAGES.md#w04), [W14](WORK_PACKAGES.md#w14), [W18](WORK_PACKAGES.md#w18)

<a id="d34"></a>
## D34 — Does a complaint to a regulator automatically reverse coverage?

[Prior scoped rule and passage review](../HealthcareRoles/DECISIONS.md#d34)

**Design implication:** A complaint or regulator contact is not itself a coverage reversal; preserve actual route and observed outcome.

**Retained scope:** Agency jurisdiction and program rules determine action.

**Affected packages:** [W02](WORK_PACKAGES.md#w02), [W12](WORK_PACKAGES.md#w12)
