# Design questions and learning map

The objective is transferable understanding: explain a mechanism, identify its assumptions, compare alternatives, predict a failure and test the relevant property. Knowing one project's filenames or copying its defaults is not equivalent to understanding harness construction.

## Questions a builder should be able to answer

| Topic | Core question | Evidence or experiment to resolve it |
| --- | --- | --- |
| Autonomy | Which transitions need judgment rather than ordinary code? | Task variability and failure traces |
| Completion | What observable state establishes the goal? | Actual task/tool contract and outcome checks |
| Context | What exact request will the model receive? | Rendered manifest and provider-specific accounting |
| Preservation | What must survive compaction/reset/restart? | Protected obligations, retrieval references and recovery tests |
| Memory | Which facts/procedures may influence future work? | Scope/admission/provenance and transfer evaluation |
| Retrieval | Why this search method and ranking policy? | Query set, recall/disclosure errors and downstream outcomes |
| Trust | Can an untrusted observation become an instruction later? | Provenance through every derived form and adversarial tests |
| Effects | What does a timeout mean for this operation? | Actual receiver semantics and reconciliation fault injection |
| Ownership | Who may publish after cancellation or takeover? | Claim/fence/version behavior under delayed results |
| Delegation | What does a child know and own that differs from the parent? | Bounded task/result/permission/budget contract |
| Providers | Which state/protocol belongs to the service versus our process? | Adapter capability tests and actual API route |
| Performance | Which resource is constrained? | Actual aggregate tokens/cost/latency and controlled comparisons |
| Learning | What changes after an experience, and how is it validated? | Versioned procedure/memory/training pipeline with held-out evidence |
| Upgrade | Can yesterday's checkpoint still resume? | Migration/compatibility tests with retained old data |

No single product answers these for every workload. The case studies are evidence of design choices; our own requirements must determine which choices to make.

## A learning sequence

1. Trace one complete tool-using turn through request construction, model output, permitted execution, observation and termination. Explain every boundary without product-specific jargon.
2. Trace one fact from observation to storage, index, retrieval, prompt use, correction and deletion. Identify which steps are synchronous, derived, scoped and potentially stale.
3. Trace a long session across context selection, compaction, restart and provider-owned continuation. Explain what is retained exactly versus summarized or only retrievable.
4. Trace a lost acknowledgement after an external mutation. Show why a checkpoint alone cannot identify the external outcome and what the actual tool contract permits next.
5. Trace a user correction while a child or scheduled worker is still running. Identify cancellation scope, ownership, stale-result handling and unresolved effects.
6. Compare a single loop, role modes, bounded specialists and a durable workflow using the same task knowledge/resources. Explain what experimental result would change the preferred design.
7. Review an upgrade that changes a memory layout or default. Follow the effective caller/configuration path, inspect persisted data compatibility and distinguish a static source finding from a runtime test.

## Small glossary

**Harness:** runtime/control software around inference and operations. **Agent:** goal-directed acting system; term varies, so define the boundary. **Workflow:** explicit control flow, potentially containing model-driven steps. **Session:** an identified conversation/execution scope, with product-specific lifecycle. **Turn:** one input and its associated model/tool activity, not necessarily one model call.

**Context:** the model-visible input for an inference. **Projection:** a selected/transformed view of retained state. **Compaction:** a context-reduction/continuity transform with defined persistence semantics. **Pruning:** selection/removal from a view; implementations differ on whether the projection is saved. **Truncation:** bounded loss of content, not necessarily semantic summarization.

**Checkpoint:** a recovery position/state. **Episode:** a remembered interaction/experience. **Semantic memory:** maintained knowledge/facts, not synonymous with vector search. **Procedural memory:** reusable methods/instructions. **Prompt cache:** reusable model computation, not a semantic knowledge store. **Provenance:** origin/derivation information. **Tombstone:** retained deletion/exclusion marker used to prevent inappropriate reappearance.

**Idempotency:** repeated same-intent requests have the intended repeat behavior under an actual receiver contract. **Fence:** a condition that rejects stale ownership/version when publishing. **Outbox:** durable intended-delivery records coordinated with local state. **Reconciliation:** resolve an ambiguous outcome from authoritative observations. **Backpressure:** limit/adapt incoming work when capacity is constrained.

These are working definitions for this handbook, not a claim that every ecosystem uses identical terminology.

## Honest knowledge limits

This research does not audit every plugin, provider, hosted backend or product release. It does not establish universal industry standards, an optimal context policy, lossless semantics, a secure multi-tenant deployment or a winning healthcare harness. Source and documentation pins age. Semantic quality, provider behavior and production failure modes require actual evaluation.

The useful result is a reproducible conceptual and evidence map: enough structure to ask precise questions, inspect an unfamiliar implementation, construct alternatives and know what remains unverified. That knowledge can inform our later design without following any reference system's footsteps.
