# Logical service contracts

These 20 internal contracts are proposed boundaries, not verified MCP names/endpoints or a one-to-one copy of the benchmark’s apps. Actual task/tool mapping is unperformed. No service is implemented by this document. Unavailable operations must be disabled or remain explicit gaps; there is no second world engine supplying convenient outcomes.

<a id="s01"></a>
## S01 — Identity, representation and scope

Principal, organization, patient/case IDs, purpose, representation, resource permissions.

**Contract:** Authorization checks and scoped identity matches; no role prompt can bypass the gate.

**Actual mapping:** not performed; implementation absent.

<a id="s02"></a>
## S02 — Clinical record and evidence

Versioned source notes, orders, observations, diagnostic reports and document provenance.

**Contract:** Reads and attributed writes follow assigned operation scope; agents cannot create unobserved test results.

**Actual mapping:** not performed; implementation absent.

<a id="s03"></a>
## S03 — Policy and criteria registry

Product/jurisdiction/setting/version/effective-date rules and approval history.

**Contract:** Ordinary workers read; approved governance controls change versions.

**Actual mapping:** not performed; implementation absent.

<a id="s04"></a>
## S04 — Coverage and benefit facts

Enrollment/benefit snapshots, requirements and administrative determinations.

**Contract:** Product-specific administrative scope; not clinical necessity or payment assurance.

**Actual mapping:** not performed; implementation absent.

<a id="s05"></a>
## S05 — Provider authorization workspace

Requests, packet versions, submissions, RFIs and provider disputes.

**Contract:** Versioned mutation, stable action identity and observable submission/receipt.

**Actual mapping:** not performed; implementation absent.

<a id="s06"></a>
## S06 — Payer review and appeal workspace

Intake/review episodes, qualification/assignment, determination and appeal state.

**Contract:** Actual stage/route and signoff envelope; no universal forced stage sequence.

**Actual mapping:** not performed; implementation absent.

<a id="s07"></a>
## S07 — Conversation and correspondence

Patient, representative, clinician and interorganization exchanges.

**Contract:** Preserve speaker, actual observed answer, scope, channel, status and reply correlation.

**Actual mapping:** not performed; implementation absent.

<a id="s08"></a>
## S08 — Care journey and obligations

Assessments, goals, plan contributions, outreach and follow-up ownership.

**Contract:** Attributed updates with unknowns, refusal and pending/exception dispositions.

**Actual mapping:** not performed; implementation absent.

<a id="s09"></a>
## S09 — Referrals and resource directory

Receiving providers, community supports, service eligibility and acceptance.

**Contract:** Resource listing, referral, acceptance and actual fulfillment remain distinct.

**Actual mapping:** not performed; implementation absent.

<a id="s10"></a>
## S10 — Capacity, staffing and scheduling

Beds, slots, shifts, resources, reservations and waitlists.

**Contract:** No double allocation; reservations/expiry follow only exposed authoritative version/time semantics.

**Actual mapping:** not performed; implementation absent.

<a id="s11"></a>
## S11 — Service fulfillment and delivery

Visits, transport, supplies, placement, administration and no-shows.

**Contract:** Only environment/service events establish delivery; a plan or actor narration alone cannot.

**Actual mapping:** not performed; implementation absent.

<a id="s12"></a>
## S12 — Artifacts, notices and delivery

Draft/final packet, note, plan, handoff, notice and delivery receipt.

**Contract:** Author/source/decision/version link; draft, final and delivered are separate.

**Actual mapping:** not performed; implementation absent.

<a id="s13"></a>
## S13 — Scoped memory and retrieval

Per-actor/case working context, episodes, policy/procedure knowledge and indexes.

**Contract:** Scope/trust/provenance filters before injection and delegation; index freshness explicit.

**Actual mapping:** not performed; implementation absent.

<a id="s14"></a>
## S14 — Action journal and recovery

Intents, canonical payload hashes, attempts, receipts, unknown outcomes and replay.

**Contract:** Stable intent keys, actual receiver contract, fenced publication and reconciliation.

**Actual mapping:** not performed; implementation absent.

<a id="s15"></a>
## S15 — Work events, queues and task clock

Observed task events, internal timers, deadlines and waiting obligations.

**Contract:** Use actual task/environment time where exposed; do not advance a fictional hospital clock.

**Actual mapping:** not performed; implementation absent.

<a id="s16"></a>
## S16 — Audit and observability

Permitted action/source/context/usage trace and aggregate operational metrics.

**Contract:** Separate actor-visible diagnostics from hidden oracle/debug data; retention/purpose apply.

**Actual mapping:** not performed; implementation absent.

<a id="s17"></a>
## S17 — Actor assignments and authority

People/positions, recorded role/task scope, delegation, scope, ownership and conflicts.

**Contract:** Distinct organization/decision domains; policy-configured independence and actual assignment checks.

**Actual mapping:** not performed; implementation absent.

<a id="s18"></a>
## S18 — Benchmark boundary and evaluation output

Supplied task input/tool contracts and separate post-run result receipts.

**Contract:** No acting prompt/tool may query hidden expected answers; official grading remains outside our acting organization.

**Actual mapping:** not performed; implementation absent.

<a id="s19"></a>
## S19 — Clinical evidence and diagnostic interfaces

Supplied clinical observations, orders, diagnostic evidence and exposed service results.

**Contract:** No physiology/world engine: accept actual observations and distinguish a new review judgment from an invented test result.

**Actual mapping:** not performed; implementation absent.

<a id="s20"></a>
## S20 — Billing, assistance and payment

Estimates, assistance applications, claims, adjudication and observed payment.

**Contract:** Not inferred from authorization; financial outcomes require their own service evidence.

**Actual mapping:** not performed; implementation absent.
