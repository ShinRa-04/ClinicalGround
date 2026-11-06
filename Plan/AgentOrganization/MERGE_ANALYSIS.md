# Merger candidates and pair screening

All 4,656 unordered pairs of 97 functions have a **mechanical planning screen** in [pair_screen.csv](data/pair_screen.csv). These are rule-derived labels, not 4,656 independently researched compatibility/permission judgments. They cannot prove safe merger, legal authority, optimal architecture or a measured benefit.

Rules run in order: preserve review accountability; preserve participant/delegation/composite boundaries; consider compatible within-package function sharing; preserve support/permission separation; otherwise record insufficient merger evidence. No numeric compatibility score is invented.

| Screen | Pairs |
| --- | --- |
| candidate_function_merger | 52 |
| no_merge_evidence_yet | 793 |
| preserve_participant_or_delegation_boundary | 2352 |
| preserve_review_accountability | 651 |
| shared_plumbing_distinct_function | 59 |
| shared_support_preserve_permissions | 749 |

## Twenty explicitly considered examples

These authored examples provide more specific reasoning. The mechanical screen is deliberately conservative and may leave a cross-package merger unclassified even where the authored example proposes it conditionally. A screen is not a decision engine.

| Pair | Judgment | Retained distinction / reason |
| --- | --- | --- |
| [O01](roles/O01.md) / [O02](roles/O02.md) | candidate | Share provider packet/referral tracking; retain referral receipt/acceptance and authorization outcome as distinct observations. |
| [O01](roles/O01.md) / [O03](roles/O03.md) | candidate | Share the case owner, but make identity matching explicit before attaching evidence. |
| [O01](roles/O01.md) / [O04](roles/O04.md) | candidate | Share benefits lookup and packet preparation; never equate verified benefits with authorization or payment. |
| [O01](roles/O01.md) / [O05](roles/O05.md) | candidate | Share administrative tracking and scheduling where permitted; booked, cleared and performed remain distinct. |
| [O06](roles/O06.md) / [O08](roles/O08.md) | conditional | Share evidence retrieval/consistency review, but use the actual release purpose and clarification/authorship process. |
| [O07](roles/O07.md) / [O08](roles/O08.md) | conditional | Common documentation support is plausible; code selection and clinical fact clarification remain different work. |
| [U01](roles/U01.md) / [U02](roles/U02.md) | candidate | Share payer intake/benefit state; apply only explicitly delegated limited nonclinical decisions. |
| [U01](roles/U01.md) / [U09](roles/U09.md) | conditional_cross_package | The payer owner may invoke notice preparation/delivery, but the notice must derive from the authorized decision and cannot create it. |
| [U03](roles/U03.md) / [U04](roles/U04.md) | conditional | Share criteria/evidence infrastructure; retain the actual initial-review stage, expertise, escalation and signoff rules. |
| [U04](roles/U04.md) / [U13](roles/U13.md) | protected | Do not rename the initial author to claim uninvolved reconsideration. Internal critic and actual reconsideration are distinct. |
| [M01](roles/M01.md) / [M10](roles/M10.md) | candidate | Navigation and coordination can share case obligations; external resource availability still needs evidence. |
| [M01](roles/M01.md) / [M18](roles/M18.md) | conditional | Shared transition coordination may improve continuity, but administrative readiness and clinical discharge authority differ. |
| [M04](roles/M04.md) / [M05](roles/M05.md) | conditional | Share medication/access information; technician/access activity must not acquire therapy-change authority. |
| [M23](roles/M23.md) / [M24](roles/M24.md) | external_boundary | Dispatcher coordination is not physical driving, pickup or attendance; only the actual environment response can establish completion. |
| [P01](roles/P01.md) / [P02](roles/P02.md) | participant_boundary | Shared family-case context must retain separate speakers, wishes and representative facts. |
| [P05](roles/P05.md) / [P06](roles/P06.md) | conditional | A language service can offer both operations while preserving oral interaction versus written fidelity and actual qualification limits. |
| [P05](roles/P05.md) / [M16](roles/M16.md) | expertise_boundary | Interpreting a conversation is not a clinical speech/swallowing assessment; similar language-related words do not make the functions equivalent. |
| [M28](roles/M28.md) / [M29](roles/M29.md) | composite_boundary | Common support coordination is possible, but hospice IDG/RN/attending/certification and spiritual support are distinct functions. |
| [G08](roles/G08.md) / [G03](roles/G03.md) | approval_boundary | A policy-analysis capability can serve governance; its draft cannot approve its own controlling policy. |
| [G06](roles/G06.md) / [U13](roles/U13.md) | review_boundary | An internal quality critic is not the applicable physician reconsiderer or official benchmark grader. |

A merger should be revisited if actual task scopes differ, context becomes unreliable, distinct information views cannot be enforced, handoff overhead changes, or a controlled trial favors separation. Conversely, common data plumbing does not require merging substantive authorities.
