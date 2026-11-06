# Data, tools and execution contracts

## Three separate representations

1. **Supplied environment records and observations:** the actual source of case/tool state.
2. **Our case-working view:** a versioned, source-linked projection for obligations, conversations, drafts, pending actions and unknowns.
3. **Our organizational configuration:** composite jobs, micro-role contracts, permissions/routing and approved general procedures.

The working view is not a second clinical chart with authority to contradict the environment. A generated assessment, plan or review artifact may be an actual required new work product; it must remain distinct from an invented prior clinical observation or externally issued outcome.

## Proposed records

| Record | Content / purpose | Key invariant |
| --- | --- | --- |
| Work assignment | Environment/task/domain, principal, patient/case, actual stage and required outputs | No assignment inferred from an unrestricted hospital persona |
| Composite job | Outcome contract, activated responsibilities, current owner and pending obligations | One named owner for continuity; substantive authority still follows actual task/operation |
| Micro-role result | Question, case/source snapshot, facts versus interpretations, proposed actions and unknowns | A helper result cannot silently become environment truth |
| Evidence reference | Source/tool/document, author/speaker, locator, observed time and available version | Exact patient/case and provenance survive summaries |
| Criterion assessment | Governing source, logical condition, evidence and met/not-met/unknown rationale | Missing record is not automatically an explicit negative |
| Conversation state | Participants, actual messages, asked questions, answers/refusals and pending next question | No internally manufactured patient/clinician reply |
| Work product | Draft/final packet, review, plan, notice or handoff with source/version links | Draft, finalized, submitted and delivered stay different |
| Action journal | Intent ID, scope, payload digest, actual operation, attempts, result/unknown | Retries follow receiver semantics rather than assume exactly-once effects |
| Closure receipt | Assigned outcome, observed evidence, checks and remaining owner | Completion narration cannot replace required effects |

## Logical services versus real tools

[Service contracts](SERVICE_CONTRACTS.md) describe 20 internal boundaries. They are not verified MCP tool names, endpoints or a one-to-one match to χ-Bench's apps. Before implementation, each operation needs an explicit mapping: actual tool/schema, task/stage scope, input source, effect class, observable output, error handling, retry/readback contract and unavailable features.

If an exact environment version/ETag is unavailable, retain what can actually be observed—a response identifier, fetch time, canonical content digest or documented freshness limit. Do not invent optimistic-concurrency guarantees the tool does not expose. If a desired hospital extension has no supported interface, leave it inactive or unresolved; don't let an agent narrate the missing result into existence.

## Execution cycle

Resolve actual task/principal/patient → obtain allowed records → update case-local obligations → select needed responsibilities → construct a scoped request → propose action → validate actual permission/arguments/current scope → record intended action → dispatch to supplied tool → record outcome/readback or uncertainty → reconcile obligations.

Reasoning roles can be combined; effect gates remain explicit. Parallel read-only work may be possible on a coherent snapshot, but dependent writes, current dialogue and case finalization need an intentional ordering/ownership policy. The prototype should test per-case serialization first and expand only where actual tool semantics and measurements justify it.

## Retry and recovery

A timeout can follow a successful remote effect. Use actual idempotency/readback/reconciliation support where present; otherwise retain outcome-unknown instead of assuming failure or success. A stable local action ID alone does not make the external tool idempotent. A replaced worker's result must be checked against current owner/case/source state before publication.

## Interoperability option

Patient, coverage, service request, task, care-plan, observation, document, provenance and audit concepts can guide a future canonical data model. FHIR is a useful healthcare information-exchange reference, but this proposal does not implement a FHIR server or claim profile/security conformance. Actual mappings would require a chosen release/profile and validation; χ-Bench's real tool contracts remain the immediate integration target. [B07](SOURCES.md#b07), [B08](SOURCES.md#b08).

## Illustrative future repository layout

```text
health_harness/
  organization/         # job definitions, responsibility graph, assignments
  micro_roles/          # PA / UM / CM / shared functional contracts
  runtime/              # context, adapters, scheduling, action gates, recovery
  knowledge/approved/   # shared general policy/procedure versions
  cases/<scoped-key>/   # patient/task-local state, episodes, drafts, receipts
  adapters/chibench/    # explicit mappings to supplied tools; no shadow world
  audit/restricted/    # controlled traces, excluded from cross-patient memory
  evaluation/          # separate post-run evidence and comparison tooling
```

This tree is a hypothetical implementation layout, not a claim that these runtime folders or capabilities have been built in this repository.
