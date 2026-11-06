# Proposed layered architecture

This is the recommended hypothetical layout. All interfaces and component names are proposed; no runtime or benchmark adapter has been built.

## Layer 1 — Organizational model

Maintain an organization graph, positions/assignments, actor identities, source-role profiles, workspace responsibilities and authority domains. A person can hold several functions; several people can use one role template; a technical capability is not necessarily a person. Provider, payer, patient/representative and external review principals remain distinct.

The hospital operations coordinator sees minimal queue/capacity/ownership information. It allocates work and tracks unresolved handoffs; it does not become the treating clinician, insurer, patient or appeal authority. Governance is versioned configuration and specifically scoped actors/bodies, not a universal “chief agent” that can overrule everything.

## Layer 2 — Case and journey control

PA, UM and CM owners maintain organization-specific views and obligations. A journey registry correlates related episodes using actual identifiers without merging all chart access. Work is serialized/versioned at the affected aggregate where needed, not through one global hospital lock.

The owner is accountable for continuity, next actions and closure evidence. The substantive author/signatory is a separate attribute determined by the actual task/operation. A workflow transport owner can invoke a permitted role-specific step without claiming that its coordinator label grants real clinical credentials.

## Layer 3 — Scoped reasoning and communication

Bounded capabilities inspect policy, evidence, codes, documentation, medication, psychosocial or other relevant questions. Conversation state preserves speakers, actual questions/answers, refusals and uncertainty. Some functions can be named modes in one owner; others can use fresh contexts when there is a concrete need.

A logical role instance has: organization/principal, task/case, assignment, objective, evidence view, allowed operations, memory namespace, output contract, budget and stop rule. A shared model/runtime pool may execute several instances without sharing their private context. Conversely, different prompt names alone do not isolate tools or data.

## Layer 4 — Shared harness kernel

The kernel contains a task/session manager; context builder; model adapter; scoped retrieval/memory service; permission/tool gate; executor/action journal; worker scheduler; checkpoint/recovery manager; artifact/handoff service; and observability. Those are logical responsibilities and may initially live in one process with explicit interfaces.

Every mutation follows the actual permission and receiver contract, with stable action identity, source/task version and observable result/unknown status. Helpers return proposals by default. A model cannot update authoritative truth merely by writing a convincing note. Native provider context ownership and opaque continuation items are handled by the selected adapter rather than flattening every provider into text.

## Layer 5 — Environment adapter

**Primary adapter:** χ-Bench tools/services and actual observations. It translates our internal intent into supported operations and maps responses without inventing unsupported fields, versions, authorities or outcomes. The actual instruction, role-scoped tool interface and allowed policy material determine what an acting worker can do.

The service catalogue is an internal design map. It requires a capability-discovery/mapping table: supported operation, concrete tool/schema, required stage, response evidence, errors, replay semantics and unavailable features. This mapping has not yet been performed. Unsupported extensions must be disabled or visibly unresolved.

For software testing, bounded mocks may exercise interfaces and failure handling, but they are test fixtures rather than a second hospital environment. They must not be substituted into a scored trial or reported as equivalent to supplied case observations.

## Layer 6 — Evaluation outside acting authority

Acting agents may use a bounded quality critic based only on their permitted information. Official grading remains separate. Hidden expected facts/results must never enter owner/specialist prompts through a memory index, debug endpoint or evaluator log. A final actor statement is not the official grade.

## Deployment alternatives

For a first implementation I would favor explicit modules, a local transactional metadata/action store and a clear event interface, adding distributed workers or specialized search only when required. That is a provisional simplicity preference, not a stack selection or claim SQLite is sufficient for every deployment. Separate actor/data boundaries should remain enforceable if modules later split into processes.

Model tiers should be configurable by job risk/complexity and observed quality/cost: deterministic operations first; bounded cheaper inference for suitable extraction/navigation; stronger reasoning or independent scrutiny only where evaluated benefit justifies it. No specific model is prescribed, and high-cost models must not become the default for every desk merely because they are available.

## End-to-end control cycle

Accept task → establish actual domain/principal/stage → retrieve authoritative observations → update versioned obligations → select a relevant role/mode/capability → build a scoped evidence/context snapshot → propose/validate the next operation → execute through the real adapter → record/read back evidence or ambiguity → reconcile pending obligations → continue, hand off or close truthfully.

Current user steering and cancellation can invalidate queued work. A late helper result is a proposal against an older snapshot; it must not overwrite newer case truth. A timeout after a write remains uncertain until the real service contract supports reconciliation.
