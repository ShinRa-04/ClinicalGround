# Proposed layout diagrams

These diagrams explain the hypothetical organization and information flow. They are not extracted program call graphs, benchmark tool mappings or proof of isolation/performance. Each SVG has editable DOT source beside it.

- [Working organization](graphs/organization.svg): χ-Bench work enters the PA/UM/CM organization; shared capabilities and kernel services support it.
- [Composite job and smaller responsibilities](graphs/composite-roles.svg): PA provides a detailed example; the full catalogue contains all PA, UM, CM and shared micro-responsibilities. Grouping is illustrative, not a required pipeline or agent count.
- [Case execution](graphs/case-execution.svg): role composition and actual effect/observation boundaries; no second world simulator.
- [Patient isolation](graphs/patient-isolation.svg): shared approved general definitions, separate patient working contexts and no patient-derived promotion into shared behavior.
- [Case memory/context](graphs/memory-context.svg): supplied records, derived case state, episode/checkpoint and bounded active context remain distinct.

The organization chart concerns work ownership. It does not mean a hospital manager controls patient consent, payer determinations or independent review. A micro-role box is a responsibility contract; the combined owner may perform it itself or delegate it under the same evidence/scope obligations.
