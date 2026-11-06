# What I would build, and in what order

This roadmap is a proposal. Only the design documents/catalogues and their structural checks belong to the current deliverable; no listed runtime phase has been implemented.

## P0 — Explicit responsibility specification

Define the organizational desks, composite job outcomes, smaller responsibility contracts, actual environment boundary, patient isolation and completion evidence. This proposal supplies the starting catalogue and design decisions. It does not select a final framework/model or prove an optimal decomposition.

## P1 — Map real work before choosing a runtime

Read allowed public instructions and concrete tool contracts for representative PA, UM and CM work. Map each required action/evidence/artifact to actual supported operations, stage/role scope, errors and readback/retry semantics. Identify starting stages and valid exceptions. Leave unsupported extensions inactive. This mapping remains unperformed in this study.

## P2 — First composite jobs

Implement one minimally sufficient combined owner for each assigned domain, using explicit micro-responsibility outputs and deterministic identity/scope/action checks. Start with the smallest actual vertical tasks, not a global master brain or every possible specialist. General role/procedure definitions are reusable; patient execution state is new/scoped.

## P3 — Continuity and isolation before expansion

Implement source-linked case state, dialogue/obligation tracking, checkpoints, actual provider context ownership, context budgeting, action journal, unknown-outcome reconciliation and strict patient boundaries. Test wrong-case retrieval, stale workers, context reduction, restart and cross-case worker reuse. Do not call the system safe simply because a prompt says so.

## P4 — Decompose where it helps

Add bounded policy/evidence/contradiction/documentation helpers or a dedicated conversation responsibility where measured failures justify them. Compare against the same combined job with comparable information/resources. Keep a role-worker-team alternative; do not assume either maximal subdivision or maximal merger is best. Deterministic responsibilities should not incur model calls just for theatrical staff realism.

## P5 — A fuller working organization

Add relevant referral, access, medication, psychosocial, transition, quality and operations desks as task demand and real tools support them. Maintain named ownership and clear handoffs. Hospital-like organization can become richer without constructing a second world, physiology engine or fake receiving-service actor.

## P6 — Controlled comparison

Execute the predeclared variants on development/reserved cases with repeated trials as appropriate. Measure complete outcomes, data/control integrity and total resource costs. Keep private expected answers outside the acting system. Record failures and limits, including whether context isolation or extra compute explains any gain.

## Longer-term ideas I would investigate

- A responsibility graph that activates only the contract outputs needed for the current stage.
- Pluggable single-agent, helper and role-worker execution arrangements under the same job contract.
- A case-local evidence/obligation ledger that remains readable after compaction or worker replacement.
- Structured handoffs with exact source references, unknowns and recipient acknowledgement.
- Composition budgets that account for all helpers and stop repeated low-value review loops.
- An isolation audit that can explain every included record and reject wrong-patient context before inference.
- Human-readable operational boards that expose work ownership without sharing everyone’s patient chart.

These ideas require tests. The system must not automatically learn patient-derived behavioral rules for use on other patients; published general knowledge and approved procedure versions remain separate inputs.

## Replaceable technology choices

An explicit module boundary and a transactional local metadata/action store may be a useful first implementation, but exact storage, search, scheduling, provider and deployment choices remain open. A vector database, many processes, heavyweight graph framework or native provider compaction is not automatically required. Choose according to actual workload, data isolation, persistence and adapter constraints.

The earlier harness engineering study contains the general alternatives. This blueprint applies that understanding to the work organization and does not follow any reference product's footsteps.
