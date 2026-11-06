# Data contracts and failure catalog

The following contracts are design proposals. They name distinctions a builder should resolve; they are not universal schemas, official APIs or a mandate to store every field. Choose fields and retention according to actual correctness, privacy and operational requirements.

## Proposed records

| Record | Typical fields | Invariant to decide |
| --- | --- | --- |
| Principal/scope | tenant/user, allowed purpose, workspace/task, credentials reference | Resource identity is not authorization by itself |
| Input event | event ID, source/speaker, time, session/task, content reference, trust label | Observations remain attributable through transforms |
| Task state | version, goal, active request, obligations, observed outcomes, unknowns | A summary cannot silently override domain truth |
| Run/session claim | owner/run, epoch, lease, cancellation scope | Stale owners cannot publish current mutations |
| Model request manifest | model/adapter, context source IDs/versions, token measurement/estimate | Counts and projections match the actual request scope |
| Tool intent | stable action ID, principal, operation/version, canonical argument digest | Retry identity expresses the same intended effect |
| Approval | bound action/resource/payload, policy version, approver, expiry | Changed intent is re-evaluated by actual policy |
| Tool observation | call/action ID, outcome, receipt/readback, error/ambiguity, time | Timeout is not automatically proven failure |
| Checkpoint | task/session version, program position, pending actions, schema version | Recovery semantics and repeated work are explicit |
| Memory entry | entity/scope, text/value, origin chain, trust, version, validity/tombstone | Recall and rewrite do not promote untrusted origins |
| Retrieval result | source/version, score/method, permissions, excerpt/handle | Similarity does not establish truth or current access |
| Compaction artifact | source range/version, summary/opaque state, retained references, transform version | The new view corresponds to the state being replaced |
| Worker task/result | objective, snapshot, allowed tools, budget, source-linked result/unknowns | Responsibility and actual effects remain explicit |
| Completion receipt | requested goal, observed terminal evidence, remaining work, checks | A fluent final message is not the only success criterion |

No record should casually embed provider secrets, sensitive identifiers in retry keys or full private content in every trace. References can preserve auditability while keeping payloads in an appropriately controlled store.

## Failure scenarios to test

| ID | Failure | Expected property to examine |
| --- | --- | --- |
| F01 | Current user correction disappears during compaction | Active request/obligations remain protected or recoverable |
| F02 | Tool result retained without its call | Request protocol rejects/repairs the orphan under actual adapter rules |
| F03 | Mandatory context exceeds the available budget | Explicit failure/retrieval/restructure path instead of silent omission |
| F04 | Native provider thread grows while local mirror shrinks | Budget/compaction applies to the actual context owner |
| F05 | A summary turns missing evidence into a positive fact | Unknown/source status survives and can be checked |
| F06 | Same fact is copied repeatedly and gains rank | Derivative frequency does not become independent corroboration |
| F07 | External instructions enter durable profile memory | Trust/provenance survives rewriting; no automatic authority promotion |
| F08 | Cross-user/case result retrieved | Scope/permission filters prevent inappropriate disclosure/use |
| F09 | Source deleted but derived memories return | Tombstone/lineage and ingestion policy prevent regeneration |
| F10 | Index trails a source update | Freshness is explicit; callers don't silently combine versions |
| F11 | A timed-out remote action actually completed | Readback/idempotent reconciliation preserves uncertainty and avoids unsafe duplicate intent |
| F12 | Reused action key carries changed arguments | Receiver rejects mismatch according to its actual contract |
| F13 | Old worker returns after owner replacement | Publication is fenced or reconciled as a late observation |
| F14 | Approval resumes after relevant state changes | Scope/payload/version conditions are revalidated |
| F15 | Cancellation arrives during tool execution | Further work stops where possible; prior effects are not falsely undone |
| F16 | Parallel writes race on the same domain record | Actual transactional/version/ownership policy handles conflicts |
| F17 | Child nesting exhausts aggregate resources | Parent/child accounting and admission limits apply |
| F18 | Provider response contains partial tool arguments | Executor waits for complete validated call under actual protocol |
| F19 | Rate limit mistaken for context overflow | Correct bounded recovery class is selected |
| F20 | Compaction summary request cannot fit | Alternative policy/failure path; no repeated impossible request loop |
| F21 | Plugin changes tool/schema semantics mid-session | Version compatibility or explicit migration/failure |
| F22 | Database restart succeeds but remote effects are ambiguous | Storage recovery and world reconciliation remain distinct |
| F23 | A remembered workflow overfits a development case | Transfer evaluation and procedure scope expose the limitation |
| F24 | UI receives text before final effect persistence | Delivery and task/effect completion are separately recorded |
| F25 | Disk-full/partial-write prevents checkpoint publication | No false success; previous valid state/recovery path remains inspectable |
| F26 | Prompt-cache hit is treated as remembered user facts | Application memory and compute cache remain distinct |
| F27 | Scheduled retry reuses stale task permission | Actual current principal/scope and intent are checked |
| F28 | A grading helper sees hidden expected answers | Acting inputs and post-run evaluation remain separated |

These are proposed tests, not a claim that all were executed or that every upstream system has the defect. The lab receipt identifies the small synthetic subset actually exercised. Real provider semantics, semantic summary fidelity, concurrency, filesystem faults and application deployment need separate experiments.

## Operational tradeoffs

Retaining every event helps investigation but increases data/retention burden. Aggressive forgetting reduces storage and disclosure surface but can undermine recovery or permitted auditability. A strict one-writer design simplifies ownership but can limit throughput; multiwriter systems need stronger consistency contracts. A detailed context manifest aids debugging but can leak sensitive data if it records full payloads everywhere.

Choose explicit guarantees and document tradeoffs rather than asserting perfect durability, perfect memory and unrestricted autonomous speed simultaneously. Versioned evidence and failure tests make disagreements resolvable.
