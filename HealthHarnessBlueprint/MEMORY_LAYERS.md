# Proposed memory layers

Ten logical surfaces with separate ownership and meaning. They are not ten databases or a selected storage stack. Patient-derived material remains in the current permitted patient/case/task boundary; shared job/procedure knowledge is approved and read-only.

| ID | Layer | Scope / owner | Contents | Boundary |
| --- | --- | --- | --- | --- |
| M01 | Authoritative supplied environment state | Environment services; never replaced by a summary | Supplied domain records under actual write contracts | No global actor read; no direct acting-worker access to hidden truth |
| M02 | Case/journey working state | Per organization and patient/task | Goals, observed stage, obligations, unknowns and source/version links | Separate hospital/payer/CM views even when correlated by journey |
| M03 | Conversation episodes | Per participant/conversation with scope | Exact observed messages, asked questions, answers, refusal and channel status | Do not merge speakers or assume a silence/translation is consent |
| M04 | Reusable job definition and assignment | Approved role definition plus case-local assignment | Mandate, allowed scope, specialty, organization and output contract; no patient-derived profile | Shared job definition does not retain patient memories or acquire authority from its title |
| M05 | Policy/reference knowledge | Versioned scoped registry | Approved rules, terminology and source documents | Applicability/effective version checked; summaries remain derived |
| M06 | Approved general procedures | Read-only approved shared versions | General methods, prerequisites and tool/version assumptions | No patient-derived automatic learning or procedure/skill promotion across patients |
| M07 | Case-local episodic history | Current permitted patient/case/task namespace only | This case’s observations, attempts, outcomes and uncertainty | No cross-patient recall, learned habits, summaries or patient-derived procedural transfer |
| M08 | Execution checkpoints/actions | Runtime owner/aggregate | Program position, source/task version, pending actions and unknown receipts | Local checkpoint does not guarantee external exactly-once effects |
| M09 | Active model context | One scoped inference request | Protected request, role, relevant evidence, recent coherent exchanges and bounded recall | Budget reserves and complete call/result units; fail explicitly if essentials cannot fit |
| M10 | Retrieval and computation caches | Versioned derived scope | Lexical/vector indexes, tool-result caches and provider prompt cache where available | Different invalidation/retention; cache does not create new knowledge or permission |
