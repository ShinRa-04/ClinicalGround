# Model-call grouping and retrieval batching audit

Analyzed run: `HealthHarnessCodex/runs/20261023-policy-grounded-t021-04`,
frozen source `4b49b93`. This is a retrospective analysis, not a new execution
or implemented retrieval redesign. All 48 model-call start events, 47 completed
responses and the final failed response were examined. Tool-purpose categories
come from recorded proposals and dispatch events, not hidden benchmark targets.

## What "retrieve at once" means

One model turn can request several tool operations. A retrieval service can
also gather several already-authorized fields/passages without asking the model
to choose each JSON pointer or chunk in a separate turn. These are different
from merging all APIs into one endpoint or putting all records into the model
context. Existing responses must retain original source references and unknowns.

Batching does not remove dependencies. Patient identity must be established
before patient work; a newly created case ID must exist before case-specific
reads; a located policy/document must be identified before its contents can be
read. Some apparent reads materialize artifacts and are declared writes: one
proposal batch is not authorization to execute all operations concurrently.

## Complete categorization

| Global calls | Count | Actual purpose | What can be retrieved together? | What must remain separate? |
|---|---:|---|---|---|
| 1-10 | 10 | Nine independent candidate assessments plus one source-validation correction | Candidate records had already been acquired through permitted discovery. Assessment requests could run in parallel in isolated contexts. | These are model judgments, not ten fresh record-fetches. Do not merge all patients into a clinical worker context or treat a correction as retrieval. |
| 11-13 | 3 | Six record inspections across two competing candidates | A bounded, source-attributed set of relevant passages per candidate could be prepared together. | Actual trace used root-field discovery followed by paged summaries; later requested pointers/pages depended on earlier views. Multi-candidate evidence belongs only in pre-binding investigation. |
| 14 | 1 | Source-backed identity resolution | No new retrieval in this call. | Keep the model's selection/unresolved judgment after the investigation. |
| 15 | 1 | Selected-patient chart, candidate orders, provider directory; two obligations | The three known patient/provider reads were already proposed together. | Preserve each operation's actual effect and identity permissions. |
| 16-18 | 3 | Eight stored-field inspections, one reference search, one tool-discovery step | Relevant patient/order/provider fields could accompany a bounded initial retrieval result; known independent reference searches could be grouped. | Unknown schema fields/search targets may require a preceding result. This is an opportunity, not proof all three calls are removable. |
| 19 | 1 | Create service request and draft case | Not a retrieval call. | Depends on supported intake/identity fields; later case reads depend on the returned identifier. |
| 20 | 1 | Case details, documents, required forms, inbox | Already proposed as one four-operation batch. | Requires the created case. Artifact-materializing operations still obey write sequencing. |
| 21-25 | 5 | Case/document inspection; policy searches; two policy-file reads | Known case/form fields, document metadata and independent policy queries can be gathered together. Once sources are found, read the relevant passages together. | Policy discovery and reading newly discovered files are separate dependency stages. Do not assume correct policy applicability from a search hit. |
| 26-38 | 13 | Only stored-evidence inspection/search plus one tool-discovery operation | Strongest batching opportunity: 35 field inspections, 43 text searches and two stored-text reads could be handled as a few bounded information requests rather than repeated model navigation. | Some later questions may depend on earlier findings. No evidence supports promising that all 13 become exactly one call. No new hospital record or reference file was fetched in this block. |
| 39-46 | 8 | More stored searches/inspection, five file searches, a PDF read, repeated provider listing, tool discovery and obligations | Group independent case questions and source searches; retrieve the identified PDF and policy passages together where permissions/effects allow. | Identifying a PDF/policy precedes reading it. Whether the repeated provider read was unnecessary needs an argument/state comparison; its repetition alone does not prove waste. |
| 47 | 1 | Two policy-file reads and refreshed case/forms | Already proposed together. Static policy passages can share retrieval; current case state may require a fresh read. | Do not replace necessary post-write confirmation with stale cached state. |
| 48 | 1 | Failed response with malformed `arguments_json` | No valid tools could be recovered/dispatched from the response. | This is a model-format failure, not retrieval. The final model-call slot was consumed and no correction budget remained. |

Counts total 48. Calls 15-48 are the 34 owner-workflow calls; 32 are retrieval-
oriented or mix retrieval with local bookkeeping. Call 19 performs creation;
call 48 fails parsing. This does **not** classify all 32 as unnecessary calls.

## Measured concentration

Calls 26-38 alone reported 645,622 input and 12,561 output tokens: **658,183
tokens**, approximately 34.1% of the complete run's 1,930,078 reported tokens.
They proposed no new actor record or workspace-file retrieval. A major burden
is repeated model-mediated navigation over data already stored by the harness,
not solely the number of external records or network round trips.

Calls 15 and 20 demonstrate that proposing several operations in one model turn
already works. Missing capabilities are richer bounded retrieval results and
grouped source questions, rather than a universal inability to batch tool calls.

## General opportunities, not an implementation decision

1. Return useful typed fields and a source index with initial results, reducing
   model turns spent learning field paths. Preserve omission/partial markers.
2. Let one retrieval request contain several questions about already-observed
   sources. Code can collect exact attributed passages and deduplicate them.
3. Search references in groups, then retrieve the identified sources in a
   second stage. Keep policy applicability/interpretation with the worker.
4. Preserve sequential mutation, dependent identifier binding and necessary
   final readback. Avoid oversized all-record dumps and cross-patient leakage.
5. Keep correction capacity within the aggregate budget; its amount is a design
   choice, not established by this audit. More calls alone do not fix navigation.

No reduced call count, token saving, completion-rate gain or semantic correctness
has been measured for these proposed changes. No source behavior, judge prompt,
dataset, credential, running service or recorded attempt was changed here.

Private evidence: the attempt's `events.jsonl`, `evaluation.json`,
`identity-investigation.private.json`, final state and preserved snapshot.
No patient data or protected policy text is copied into this document.
