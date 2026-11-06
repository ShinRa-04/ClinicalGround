# The hospital we are modeling

## Recommendation

I would design a **hospital operating harness**: a configurable organization of case owners, scoped clinical/administrative roles and shared capabilities, with a common execution kernel. Provider PA, payer UM and CM are its first three workflow workspaces. They share provenance, task obligations and carefully scoped services, but retain separate responsibility and decision boundaries.

“Hospital” describes the organizational model: departments, staff assignments, queues, cases, handoffs, resource dependencies, communication and oversight. A hospital also interacts with independent patients, insurers, review bodies and receiving/community services. Treating all of those as subordinate departments would create an inaccurate authority model. The proposed organization therefore includes external interfaces as well as hospital functions.

The primary execution target is **χ-Bench's existing state and tools**. Our harness models who should do the work and how its reasoning is organized. It does not replace the provided chart, patient conversation or payer/service outcome with its own generated story. The earlier research is a broader functional and engineering map; it is not a second operational world state.

## What is fact, proposal and unknown?

**Verified benchmark scope:** paper v3 names provider prior authorization, payer utilization management and care management, and emphasizes policy-rich work, multiple roles/handoffs and interactive dialogue. [B01](SOURCES.md#b01).

**Proposed here:** every module name, service boundary, memory layer, organization chart, internal task state, activation rule, scenario and roadmap. The catalogue has 29 logical modules, not 29 required simultaneous agents. Twenty service contracts are our interface decomposition, not a mapping to the benchmark's application count.

**Not established:** task-by-task coverage of all proposed capabilities, exact tool mappings, complete real-hospital clinical fidelity, institutional permissions, a best worker/model count, clinical correctness, improved score, latency or cost. Unknown mappings must remain inactive or explicit rather than implemented through fabricated observations.

## The three anchors

| Workspace | Accountable function | Main work | What completion must not imply |
| --- | --- | --- | --- |
| Provider PA | Requesting provider case owner | Supported request, evidence, submission, response/RFI and appropriate dispute work | Submitted is not approved; approved is not performed or paid |
| Payer UM | Assigned payer case/review functions | Intake, benefit/policy context, applicable review, determination, notice and proper review route | A coordinator title does not supply every signoff or appeal power |
| CM | Care-journey owner | Actual outreach/assessment, goals, plan, resource coordination and observed follow-through | A referral, scheduled service or agreeable-sounding conversation is not completed care |

One patient journey can connect these workspaces, but an individual task may start halfway through one workflow or end through refusal, ineligibility, withdrawal, missing evidence or another appropriate disposition. Do not force a full hospital tour for every case.

## Beyond the anchors

I would expose optional workspaces for patient access; referrals/scheduling; clinical evidence/diagnostics; medication access; psychosocial/community support; transitions/discharge; beds/staff/capacity; equipment/transport/receiving services; billing/assistance; quality/privacy/policy operations. Their first implementation should be evidence/coordination interfaces, not an unsupported claim to simulate every medical discipline.

Activate an extension only when the assigned task/environment supplies its relevant data/actions. A transport slot can be tracked if the service exposes it; the harness cannot infer that a car arrived because a dispatcher persona says so. This principle allows a broad architecture without pretending every capability is available today.

## What a “day in the hospital” means here

Cases arrive as work. Staff accept assignments, obtain the allowed records, perform their scoped function, produce an artifact/decision, hand off unresolved work and close only what the actual evidence establishes. Departments provide responsibility and coordination structure. We are designing that working organization, not a separate patient, physiology or hospital-world simulator.

Supporting functions beyond PA/UM/CM are useful where they help the supplied work: evidence handling, policy interpretation, coding support, communication, referrals, quality and access control. Their activation depends on real task demand and tool availability. The harness should not fabricate admissions, beds, tests, patient replies or service events merely to make its internal hospital story complete.

## First useful deliverable if implemented

A single supported case should run end to end through its actual assigned PA, UM or CM path, preserve evidence and unresolved obligations across context changes/restart, make only permitted calls, and produce an observable final or exception disposition. Additional organization is earned by measured failures and workload—not by instantiating every profile from the 97-role reference.
