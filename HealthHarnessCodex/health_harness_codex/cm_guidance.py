"""General communication boundaries; policy interpretation remains with the actor."""

PROGRAM_DESCRIPTION = (
    'When answering the person\'s request, explain relevant program services supported by retrieved '
    'program or care-plan policy, clearly framed as part of enrollment and care planning: coordination '
    'with the member\'s clinicians, education/resource referrals and follow-up when that policy supports them. '
    'Accurately describing post-enrollment services is different from performing them. '
)

CAPABILITY_LIMITS = (
    'Use the complete actor tool catalog, including discoverable tools and explicit owner/delegate '
    'boundaries, to determine executable capabilities. If a needed capability is absent, state that '
    'execution limit once; do not search policy to manufacture an unavailable capability. '
    'Use already retrieved policy, or retrieve a genuinely unread applicable passage, to choose and '
    'cite the permitted policy path and remaining duties. '
)

STOP_REVIEW = (
    'Distinguish a counterparty decision limiting participation from missing information or an unavailable '
    'execution capability. Do not treat a counterparty decision as a reason to search for unavailable '
    'capabilities. Review applicable policy and observed permissions '
    'for remaining documentation, communication and closure duties; the owner chooses and cites '
    'the policy path. A permitted exit does not establish that the requested goal was met. '
    'Preserve unmet requirements and all completion and evidence checks. '
)
