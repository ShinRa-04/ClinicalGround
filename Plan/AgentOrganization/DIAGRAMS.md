# Design diagrams

These are proposed software structures and inherited workflow-model groupings, not observed hospital organization charts or tested architectures. Arrows say what they carry; they do not grant clinical, patient, insurer or external-review authority.

- [Owner and bounded specialists](graphs/owner-specialists.svg): one proposed mutable-case owner; specialist proposals and external observations remain different.
- [Proposed handoff acceptance](graphs/handoff-acceptance.svg): case/version/scope checks, clarification and ownership acknowledgement before applying a result.
- [Selected package dependencies](graphs/package-dependencies.svg): a subset of cross-package links derived from the earlier 219 modeled dependencies. Labels count inherited model edges, not measured frequency, workload or required stages. The full crosswalk is [package_dependencies.csv](data/package_dependencies.csv).

Each SVG has editable DOT beside it. The dependency view deliberately omits packages outside the selected core view; all 23 packages and all 219 original dependencies remain represented in the CSV. These pictures cannot establish the best agent count.
