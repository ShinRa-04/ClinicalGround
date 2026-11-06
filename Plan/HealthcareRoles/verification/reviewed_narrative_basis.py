"""Explicit review of each baseline narrative block and authored graph label."""
REVIEWS={}


def reviewed(prefix,numbers,status,evidence,reason):
    for n in numbers:
        REVIEWS[f'{prefix}:{n:03}' if prefix.startswith('NARRATIVE:') else f'{prefix}:{n:02}']=dict(
            verdict=status,evidence=[tuple(x.split('|',1)) for x in evidence.split(';;') if x],reason=reason)


P='NARRATIVE:AUTHORITY'
reviewed(P,[1,2,6,10,13,15],'DOCUMENTATION_OR_EVIDENCE_SCOPE','',
 'Reading links, source references, figure semantics and stated audit limits are documentation metadata; no independent healthcare permission is asserted.')
reviewed(P,[3,4,5],'INTERPRETIVE_AUTHORITY_FRAMEWORK','A01|informed decisions;;A02|benefits an enrollee;;A03|not involved;;V10|prohibited',
 'The framework distinguishes sourced domains and proposes facts needed for local application. It is not one universal hierarchy statute or an institution-approved command chart.')
reviewed(P,[7],'SUPPORTED_WITHIN_SCOPE','A01|request or refuse treatment;;A09|scope',
 'Hospital rights and representation limits are in the source. Exceptions and individual capacity/authority remain explicitly unresolved, not inferred.')
reviewed(P,[8],'SUPPORTED_CONTEXT_PLUS_INTERPRETATION','A01|informed decisions;;A02|benefits an enrollee;;B01|treatment plan;;R06|financial responsibility',
 'Sources separately support participation, clinical activity and benefits/cost context. The non-equivalence/hierarchy boundary is a reasoned synthesis, not a universal organizational fact.')
reviewed(P,[9,11],'SUPPORTED_SCOPED_MA_SUMMARY','A02|expects to issue;;A03|not involved;;A04|remain in dispute;;A16|Council review',
 'Core MA qualification, review and effectuation rules are supported. The integrated-plan exception is explicit, so the standard diagram must show a route check rather than assume it applies to every MA case.')
reviewed(P,[12],'SUPPORTED_CONDITIONAL_APPEAL_SUMMARY','A11|five successive levels;;A16|Council review',
 'CMS identifies the levels; eligibility and implementation exceptions matter. No numerical threshold or universal entitlement to all levels is asserted.')
reviewed(P,[14],'SUPPORTED_WITH_ADDITIONAL_ALTERNATIVE','A12|required by law to accept;;R17|non-grandfathered;;V19|same time;;R15|pre-service appeal',
 'Applicable independent review is supported, but the corresponding diagram requires an eligible urgent concurrent-review branch; a strictly linear impression would be incomplete.')
reviewed(P,[16],'SUPPORTED_FRAMEWORK_AND_JURISDICTION_LIMIT','A14|state;;V10|prohibited;;V02|103 NP;;V03|collaboration agreement',
 'General professional guidance and concrete state pathways support rejecting a universal job-rank scope rule; they do not establish actual local permission.')
reviewed(P,[17],'SUPPORTED_ORGANIZATION_EXAMPLES_WITH_GRAPH_CORRECTION','R14|supervises;;R32|Associate Director of Care Coordination;;R32|Collaborates with Supervisor',
 'The cited roles are examples, not a national chart. The manager/supervisor relationship is described as collaboration; direct direction from associate director to supervisors must not be hidden by an inferred intermediate chain.')
reviewed(P,[18],'SUPPORTED_MA_POLICY_RULE_PLUS_INTERPRETATION','A05|reviewed and approved;;A17|coverage criteria',
 'MA policy approval and governing criteria are explicit; draft-versus-approved version handling and separation from individual adjudication are interpretive controls.')
reviewed(P,[19],'SUPPORTED_HOSPITAL_RULE_AND_ROLE_BOUNDARY','A15|authenticated;;B20|assign clinical codes',
 'Hospital record/order authentication is supported. General staff boundaries are not claimed as a complete coding, correction or all-setting legal policy.')
reviewed(P,[20],'SUPPORTED_WITH_PRIVACY_COMPLEXITY','A10|treatment purposes;;V15|specific consent',
 'The HIPAA minimum-necessary exception is supported. Part 2 adds a concrete reason not to generalize it into unrestricted all-record sharing or confuse it with every consent rule.')
reviewed(P,[21,22,23],'RECOMMENDED_LOCAL_AUTHORITY_CHECKLIST','',
 'These are proposed facts/controls for local application, not a claim that a real institution supplied them or that all are identical legal mandates.')

P='NARRATIVE:WORKFLOWS'
reviewed(P,[1,2,3,6,8,10,12,15],'DOCUMENTATION_OR_MODEL_SCOPE','',
 'Links, legends and benchmark/model limitations describe the artifact and its scope, not verified institutional practice.')
reviewed(P,[4,5,9,11,13],'EXPLICIT_OPERATIONAL_MODEL','R22|Monitoring and followup;;R04|appeals',
 'These are workflow/control recommendations and conceptual state distinctions, not empirical proof of every institution\'s sequence, closure event or escalation owner.')
reviewed(P,[7],'MODEL_REQUIRING_ALTERNATIVE_BRANCHES','R13|Non-clinical personnel may;;R13|not delegated for processing;;V19|same time',
 'Keep the workflow modeled, while adding limited delegated nonclinical approvals, retained-plan appeal ownership and eligible urgent concurrent review as explicit alternatives.')
reviewed(P,[14],'SUPPORTED_PRIVACY_CONTEXT_WITH_MODEL_LIMIT','A10|treatment purposes;;V15|specific consent',
 'Purpose-dependent privacy context is supported; the conceptual arrows are not security permissions or a required API architecture.')

P='NARRATIVE:WORKFLOW_PEOPLE'
reviewed(P,[1,2,3,28,29],'DOCUMENTATION_OR_STUDY_LIMIT','',
 'Research metadata, links and unperformed validation/task mapping must remain distinct from factual confirmation of actual practice.')
reviewed(P,[4,5,9,12,16,21,23,25,26,27],'FUNCTIONAL_TAXONOMY_OR_MODEL','',
 'Role families, qualitative participation labels, typical sequences and functional analogies are explicit synthesis, not measured prevalence, mandatory staffing or an official occupational taxonomy.')
reviewed(P,[6],'SUPPORTED_BENCHMARK_DESCRIPTION','R01|prior authorization;;R02|25 tasks',
 'Official public descriptions establish domains/tasks. They do not establish that all real-world role profiles are separately simulated.')
reviewed(P,[7,10,11,15,20,24],'COMPOSITE_TABLE_TRACEABLE_TO_ROLE_REVIEWS','',
 'Every table row is mapped through COVERAGE.md to reviewed canonical roles. Read each role\'s scoped verdict; participation/combination/handoff cells remain a qualitative model, not a universal observed staffing fact.')
reviewed(P,[8],'SUPPORTED_BOUNDARY_WITH_CONDITIONS','A09|scope;;R20|appointment;;B23|interpreters',
 'Different representative/communication functions are supported; no actual family member\'s authority or additional independent credentials are inferred.')
reviewed(P,[13],'REPLACE_UNCONFIRMED_SOURCE_DEPENDENCE','R04|obtaining prior authorizations;;R05|Referral/Authorization Coordinator',
 'The Mayo job page now returns 404 and is not independently retrievable in this audit. Replace the current finance-placement example with accessible Noyes/Michigan descriptions; do not claim the historical page never existed.')
reviewed(P,[14],'SUPPORTED_DELEGATED_ROLE_EXAMPLE','R14|delegation;;R13|not delegated for processing',
 'Provider-affiliated UM is documented. Delegation may exclude appeals; do not assume one employer owns the whole review chain.')
reviewed(P,[17],'SUPPORTED_EXAMPLE_WITH_SOURCE_LIMITS','R12|Non-clinical staff;;R13|Non-clinical staff are responsible',
 'The policy examples support the statements; R12 is an earlier captured excerpt after fresh failure. Add R13\'s limited approval and appeal-ownership caveats instead of reducing all staff to a single escalation sequence.')
reviewed(P,[18],'SUPPORTED_DISTINCTIONS_PLUS_INTERPRETATION','R13|benefit only;;R15|pre-service appeal;;A04|independent',
 'The distinctions are grounded in scoped sources; no uniform professional permission or appeal process is certified for all programs.')
reviewed(P,[19],'REPLACE_UNVERIFIABLE_GENERAL_GUIDE_CLAIM','R24|social worker/nurse practitioner;;R25|registered nurses;;R32|Nurse Case Manager',
 'Full text of R23 was not recovered. Replace dependence on its broad background statement with accessible program examples and remove any implication of measured national prevalence.')
reviewed(P,[22],'SUPPORTED_MULTIPLE_PROGRAM_EXAMPLES','R25|integrated model;;R26|Administrative Staff;;R24|support team',
 'These public sources describe different specific teams, not a required composition for every program or evidence of present staffing headcounts.')

P='NARRATIVE:MEDICAL_WORKFLOW'
reviewed(P,[1,2,3],'DOCUMENTATION_AND_STUDY_SCOPE','',
 'Research scope and links do not certify every statement; examples explicitly identified as invented remain illustrations.')
reviewed(P,[4,10,14,15],'SOURCE_INFORMED_INTERPRETATION_OR_HYPOTHESIS','R01|workflow;;R22|care coordination',
 'The classification, clinical/operational interpretation and proposed harness mechanisms are synthesis/hypotheses, not measured improvements or an official occupational classification.')
reviewed(P,[5,9,11],'SUPPORTED_PUBLIC_BENCHMARK_DESCRIPTION','R01|Care Management;;R02|25 tasks',
 'Official domains and task descriptions support the limited benchmark statements; not all tasks start at the same stage or contain every actor.')
reviewed(P,[6],'SOURCE_CONTEXT_WITH_ILLUSTRATIVE_WORKFLOW','R04|obtaining prior authorizations;;R13|medical necessity',
 'Provider request preparation is documented, but the generalized sequence is illustrative and conditional on the actual request.')
reviewed(P,[7,12],'EXPLICIT_INVENTED_ILLUSTRATION','',
 'These are expressly invented explanatory cases, not sourced clinical cases, benchmark solutions or observations. No empirical verification is claimed.')
reviewed(P,[8],'SUPPORTED_PRIOR_AUTHORIZATION_CONTEXT','V21|before services are rendered;;R11|Prior Authorization Request',
 'The CMS overview establishes pre-service authorization and contrasts pre-claim review, which may occur after service. This does not establish that all care requires authorization.')
reviewed(P,[13],'SUPPORTED_COORDINATION_DESCRIPTION','R22|proactive care plan;;R22|Monitoring and followup',
 'The AHRQ definition/activities support the role of organized assessment, planning, monitoring and resources; exact local workflow remains unconfirmed.')

# Authored graph labels: every line/edge is reviewed, not silently promoted from graph rendering.
P='GRAPH:authority-domains'
reviewed(P,[1,9],'CONCEPTUAL_AUTHORITY_FRAMEWORK','',
 'This is an interpretive domain map and its legend, not an empirically verified institution hierarchy.')
reviewed(P,[2,10],'SUPPORTED_PATIENT_DOMAIN_WITH_SCOPE','A01|informed decisions;;A09|scope',
 'Patient/representative domain is supported within stated law; no actual capacity or appointment is established.')
reviewed(P,[3,11],'SUPPORTED_CLINICAL_CONTEXT_CONDITIONAL','B01|treatment plan;;B03|scope of practice varies;;A15|ordering practitioner',
 'Authorized clinical function is supported; specific credential, privileges and jurisdiction remain conditions.')
reviewed(P,[4,12,15],'SUPPORTED_COVERAGE_CONTEXT_CONDITIONAL','A02|expects to issue;;A17|medical necessity',
 'Scoped professional review and benefit context are supported; this is not approval authority for every listed person in a real case.')
reviewed(P,[5,13],'SUPPORTED_REVIEW_ROUTES_WITH_CONDITIONS','A04|independent;;A12|required by law to accept;;A11|five successive levels',
 'Applicable review may supersede the challenged coverage decision, only under its actual route and conditions.')
reviewed(P,[6,14],'PROFESSIONAL_SCOPE_FRAMEWORK_NOT_UNIVERSAL_CHAIN','V10|prohibited;;A14|state',
 'Scope constraints are supported; the diagram does not establish every profession\'s permission or one doctor-over-all hierarchy.')
reviewed(P,[7,16],'SUPPORTED_MA_POLICY_CONTEXT','A05|reviewed and approved;;A17|coverage criteria',
 'The MA policy context is supported; a universal policy committee design for every product is not established.')
reviewed(P,[8,17],'SUPPORTED_MANAGEMENT_CONTEXT_PLUS_BOUNDARY','B22|supervise staff;;A03|not involved',
 'Operational management is described; separation from required independent/licensed decisions is a bounded interpretation, not proof of an actual organogram.')

P='GRAPH:ma-appeals'
reviewed(P,[1],'SCOPED_ROUTE_LEGEND','',
 'Legend correctly limits the process; add an explicit integrated-plan route check to prevent an overly broad visual interpretation.')
reviewed(P,[2],'SUPPORTED_WITHIN_SCOPE','A02|expects to issue',
 'Initial anticipated adverse medical-necessity qualification rule directly supported; not every initial denial or every MA integrated route.')
reviewed(P,[3,9],'SUPPORTED_WITHIN_SCOPE','A03|not involved;;A03|made by a physician',
 'Proper reconsideration and independent expert physician requirement are supported for the specified case.')
reviewed(P,[4,10],'SUPPORTED_WITHIN_SCOPE','A03|send the case file;;A04|remain in dispute',
 'Remaining adverse issues proceed to the CMS-contracted independent route under applicable MA conditions.')
reviewed(P,[5,6,7,11,12,13],'SUPPORTED_CONDITIONAL_LATER_REVIEW','A11|five successive levels',
 'The named subsequent stages are supported; the graph preserves conditional eligibility rather than automatic access.')
reviewed(P,[8,14,15,16,17,18],'SUPPORTED_EFFECTUATION_WITH_EXCEPTIONS','A16|Reversals;;A16|Council review',
 'Reversal effectuation is scoped by decision type and includes an exception for applicable Council review; no universal instant implementation is established.')

P='GRAPH:commercial-appeals'
reviewed(P,[1],'SCOPED_PROCESS_LEGEND','',
 'The legend is a scope statement, not independent legal verification of all products.')
reviewed(P,[2,3,6],'SUPPORTED_STANDARD_ROUTE_CONDITIONAL','R17|non-grandfathered;;A12|internal appeal',
 'Standard internal review context is supported within applicable plan/process conditions.')
reviewed(P,[4,5,8],'SUPPORTED_APPLICABLE_EXTERNAL_REVIEW','A12|required by law to accept;;R17|final',
 'Independent external review and applicable binding outcome are supported; eligibility/other remedies still matter.')
reviewed(P,[7],'INCOMPLETE_LINEAR_MODEL_CORRECTED','V19|same time',
 'Eligible urgent external review can be requested alongside internal appeal; replace a solely linear impression with an explicit concurrent branch.')

P='GRAPH:reporting-examples'
reviewed(P,[1,2,3,4,5,6,7],'SUPPORTED_ORGANIZATION_DESCRIPTION_NOT_ACTUAL_STAFF_CENSUS','R14|supervises',
 'The UCSD job description states supervision of nurse case managers and referral coordinators. It does not establish other institutions or actual current named employee assignments.')
reviewed(P,[8,9,10,11,12,13,14,15,17],'SUPPORTED_ORGANIZATION_DESCRIPTION_WITH_SCOPE','R32|Associate Director of Care Coordination;;R32|Supervisor of Case Management',
 'The source describes direction of managers and supervisors plus assigned staff oversight, with different qualifications. This is not a national license hierarchy.')
reviewed(P,[16],'RELATIONSHIP_OVERGENERALIZATION_CORRECTED','R32|Collaborates with Supervisor;;R32|Associate Director of Care Coordination',
 'Manager/supervisor collaboration is not proof of a direct reporting line. Use a dashed collaboration edge and separately show the documented associate-director direction to supervisors.')
reviewed(P,[18],'MODEL_BOUNDARY_AND_REQUIRED_LOCAL_FACTS','',
 'This is an explicit conservative limitation of the diagram, not a claim to have verified all institutions\' bylaws or arrangements.')
