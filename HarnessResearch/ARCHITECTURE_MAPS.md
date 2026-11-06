# General mechanism maps

These are explanatory engineering models, not extracted complete call graphs or a selected architecture. They show boundaries to reason about. Particular runtimes may combine components or delegate them to a provider. The [general chapters](README.md) explain alternatives and evidence limits.

## A tool-using execution cycle

```mermaid
flowchart TD
    I[Input and authenticated principal] --> T[Task/session state and current owner]
    T --> C[Select and render context]
    M[Scoped memory and retrieved evidence] --> C
    C --> B[Budget and adapter validation]
    B --> L[Model request and typed response]
    L --> P{Proposed operation or finish?}
    P -->|operation| G[Actual permission and argument gate]
    G --> E[Execute with action identity and limits]
    E --> O[Observed outcome or explicit uncertainty]
    O --> T
    P -->|finish| V[Check requested outcome and remaining obligations]
    V --> R[Truthful result / checkpoint / unresolved status]
```

The model chooses a proposal; host software mediates effects. A stop signal, delivered message and verified task result are distinct events. This does not imply every step needs another model call.

## Storage and model-visible context

```mermaid
flowchart LR
    E[Canonical events / observations] --> S[Scoped admission and source lineage]
    S --> N[Episodes / maintained facts / procedures]
    N --> X[Derived search indexes]
    X --> Q[Permission-filtered retrieval]
    E --> P[Context projection]
    D[Task state and unresolved obligations] --> P
    Q --> P
    P --> A[Provider request]
    A -. eligible prefix computation .-> K[Prompt / KV cache]
    P -. bounded transform .-> C[Compaction artifact / retained references]
    C --> P
    N -. correction / tombstones .-> S
```

Stored, indexed, selected, trusted and currently authorized are different properties. Compaction can change the model view without erasing retained events. A cache is not a semantic knowledge store. Whether a real implementation persists a pruning projection must be checked rather than assumed.

## A lost-acknowledgement recovery problem

```mermaid
flowchart TD
    A[Persist intended action identity] --> B[Dispatch to external receiver]
    B --> C[Receiver may commit effect]
    C --> D{Receipt durably observed?}
    D -->|yes| E[Record confirmed outcome]
    D -->|no / disconnected| U[Outcome unknown]
    U --> R{Receiver supports same-intent idempotency or readback?}
    R -->|yes| F[Reconcile using actual receiver contract]
    R -->|no| H[Retain uncertainty / permitted escalation]
    F -->|conclusive outcome evidence| E
    F -->|still ambiguous / lookup failed| U
```

A local checkpoint does not atomically include that receiver's effect. Reconciliation can remain inconclusive; attempts need a bounded policy and must retain uncertainty when that budget is exhausted. A stale worker can also return after takeover, so result publication needs an ownership/version policy. The synthetic lab demonstrates a narrow supported-receiver example and an explicit duplicate-effect counterexample; it does not implement a distributed guarantee.
