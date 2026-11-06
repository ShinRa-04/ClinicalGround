# Durable execution, replay and uncertain outcomes

An agent can restart with a fluent summary yet still repeat a payment, lose a pending operation or overwrite newer state. Durable execution is about recoverable control and effect semantics, not merely remembering the topic.

## Distinguish recovery surfaces

An event log records what was observed; a checkpoint records a restart position/state; an outbox records intended delivery; a result ledger records known action outcomes; an artifact records a produced work product. They may share a database but have different meanings. SQLite transactions can atomically update related local records under its documented assumptions. They cannot atomically include an arbitrary remote API. [G16/G17](../SOURCES.md#g16).

Consider this failure trace: record a request locally → remote service performs it → response is lost → process crashes before storing success. The checkpoint cannot tell whether the remote effect occurred. Blind replay risks duplication; assuming failure may be false. The correct state is often **outcome unknown**, followed by a permitted readback/reconciliation or idempotent retry supported by that service.

## Idempotency is an agreement

A durable request identity expresses the same intended operation across retries. The receiving service needs a contract for matching that identity, validating unchanged intent, deduplicating the effect and retaining/replaying a result. A local random key has no power if the remote tool ignores it. Key retention, scope and parameter mismatch rules matter. [G15](../SOURCES.md#g15), [G18](../SOURCES.md#g18).

Do not infer end-to-end exactly-once execution from one local transaction or workflow checkpoint. At-most-once attempts can lose work; at-least-once delivery can duplicate effects; an idempotent receiving operation can make retries safe within its actual scope/retention. Where no such contract exists, expose uncertainty and reconcile instead of claiming an impossible guarantee.

## Proposed action states

Use an explicit lifecycle such as planned, permitted, dispatching, observed-success, observed-failure, outcome-unknown and reconciled. Names are illustrative, not a standard or upstream API. A timeout transitions to the state justified by available evidence, not automatically failure. Cancellation means stop further work where possible; it cannot undo an already completed external effect.

Retain action IDs, canonical request digest, task/source version, principal, attempt/epoch and observation references. Separate retries of one intention from a new intention. Reusing a key for changed parameters should not silently produce an old outcome. A child worker or transport retry must not create a new business intent merely because it has a new process/run ID.

## Replay boundaries

Checkpoint replay may rerun code from the last committed boundary. Keep nondeterministic computation and effects inside replay-aware tasks/activities or use durable result records. A stored model output can be replayed as an observation; calling the model again is a new stochastic event and may choose different actions. An interrupted approval step can also replay its surrounding code unless the framework's semantics prevent it. See [broader comparisons](../comparative/README.md) for checkpoint-based alternatives.

Resume should validate schema/config/tool/model versions and still-applicable authorization. Replaying an old approval against a changed record can be incorrect even if the original request was valid. Migration is part of persistence design: old checkpoints and transcripts need a supported reader, a conversion path or an explicit non-resumable status.

## Ownership and stale workers

A per-session lock can prevent concurrent work in one process. A distributed worker needs stronger ownership: a durable claim/lease, a monotonically changing epoch or other fence, and checks before publishing mutations/results. A timed-out worker can return after a replacement has taken over; without a fence, the old result may overwrite the newer one.

Leases alone do not revoke remote authority already in flight. Fencing must be applied at the relevant mutation receiver where feasible, or late outcomes must be reconciled explicitly. The general invariant is that only the current authorized owner may publish current state; raw late observations may still need to be retained without adopting them.

## Recovery tests

Inject failure before intent commit, after intent/before dispatch, after remote success/before local result, during compaction publication, after lease loss, during approval wait and during final artifact persistence. Restart and inspect actual records. A test that merely restarts a process and obtains another answer is not proof of correct effect recovery.

Backups, WAL/checkpoint behavior, disk-full errors, torn file writes and schema migrations belong in the same test plan. No set of unit tests proves all platform failure modes, so state the tested filesystem/runtime assumptions and remaining gaps. [G16/G17](../SOURCES.md#g16).
