# Response-to-execution audit and t033 -11 failure

October 24, 2026. Root inspected and repaired the response boundary rather than
changing a task-specific answer. User subsequently authorized root to execute
the entire single t033 case, diagnose and retry. **No judge is authorized** for
that continuation; actor and non-LLM checks only. Do not run all 75 tasks.

## Confirmed failure and severity

User run `HealthHarnessCodex/runs/20261024-random-um-t033-11` ended with an actor
error after 12 model calls/29 proposals, before the new final stopping path.
Call 12 completed generation (5,243 reply characters), then parsing raised
ProviderError: invalid or duplicate tool-call ID. No proposals from that reply
were dispatched. Eighteen earlier journal actions were completed; this is a
partial execution, not successful testcase completion. No MD decision was reached.

**Severity: execution-blocking adapter failure.** An internal tracking-label
validation killed the entire testcase; no bounded repair was offered.

The error combined empty ID, wrong type, excessive length and duplicate-within-
reply conditions. The saved database has 11 accepted assistant replies; the
12th text was never persisted, and its temporary ephemeral native session was
cleaned. Its exact ID defect **cannot be reconstructed from the preserved run**.
Do not report a duplicate as confirmed. The old schema required uniqueness only
within a reply, not a global model counter. The fatal code path and evidence
retention gap are confirmed independently of that missing subcause.

Original deferred snapshot (213 files/131 directories) inventory/provenance was
verified after diagnosis. No original payload or run result was changed.

## Findings and implemented repairs

| Finding | Consequence | Repair |
| --- | --- | --- |
| Model authored internal request labels | Empty/repeated/invalid labels could reject an otherwise completed reply | Codex proposals contain only tool name and argument object. Code assigns deterministic labels from request SHA256 plus proposal ordinal; domain IDs inside arguments remain untouched |
| Only outer JSON decoding was a correctable response error | Valid JSON with malformed proposal shapes ended execution immediately | Typed response-format stages, one budget-charged correction under existing limits, exact safe stage/index diagnostics |
| Parser exceptions discarded completed-call usage | Result token totals omitted known usage for failed replies | Provider errors carry allowlisted reported usage; owner, helper and recorder retain it without inventing unreported usage |
| Other backend ModelReply batches lacked whole-envelope validation | A malformed later sibling could be detected only after an earlier proposal ran | Owner/helper validate the entire proposal envelope before dispatch; argument schemas and identity remain checked per action against current state |
| Simulator inbox became visible during direct O_EXCL writes | Consumer could parse incomplete JSON and reject a valid request | Stage and fsync a private sibling, then publish with atomic no-overwrite hard link. Existing claim/output partial-marker guards remain |

Original -11 reported 677,772 tokens is a known subtotal. Failed-call telemetry
reports 1,790 output tokens but its usage object was empty; do not present the
saved subtotal as an exact full-call total or invent the missing input count.

Internal request labels are bookkeeping, not patient, case, reviewer or policy
identifiers. Legacy proposal id fields are discarded for compatibility; no
model-authored value determines the journal label. The same request/proposal
position has a stable code label, and separate proposals have distinct labels.

Unique labels alone do **not** prevent the model from asking for the same
clinical action twice with different intent/requests. Journal replay protection
and unknown-write fencing remain separate, and were tested with generated IDs.
Do not globally suppress repeated identical arguments: repeat reads and
intentional later updates can be legitimate. Full semantic duplicate-work
prevention is not established by this audit.

## Safety boundaries preserved

- No partial ModelReply is returned from malformed parsing. A bad proposal
  envelope causes no sibling proposal to dispatch. This is not a claim that
  multiple valid clinical writes form one rollback-capable transaction.
- Unknown tool names remain rejected; correction can propose only permitted
  operations and all original argument/identity/policy guards still run.
- Native action items, foreign thread/turn messages, unapproved instruction
  sources, malformed transport and uncertain writes remain hard failures or
  reconciliation cases. They are not made into general automatic retries.
- The response-shape repair cannot replay a clinical write from the rejected
  reply because no such proposal was returned/dispatched. Retries share existing
  budgets and stop after the bounded allowance. Precise diagnostics contain
  enum stages/counts, not raw clinical text or model-supplied secret values.
- Simulator race was an independent finding from the full suite. The -11
  simulator made zero model calls; this race did not cause its actor ID error.

## Executed verification

- **628 regression tests pass in 79.195s**, including a new malformed-response
  matrix, generated ID properties, batch-envelope rejection, usage retention,
  bounded correction, other-backend duplicate labels and unknown-write fencing.
  Receipt: `runs/20261024-response-boundary-final-tests.log`.
- First broad 626-test run exposed the actual inbox publication race through
  the submitted-claim timeout test. This was investigated and fixed in the
  publisher, not hidden by increasing sleeps or weakening the assertion.
- Deterministic tests verify invisibility before publication finishes, complete
  JSON afterward, concurrent single-winner publication and no overwriting.
  Ten bridge tests and 27 Codex provider tests passed independently.
- Synthetic platform probe ran in the pinned Docker runtime, network disabled,
  using both Linux /tmp and the actual Windows bind-mounted run folder. First
  publication succeeded, a second publication could not overwrite it, complete
  JSON remained, temporary siblings were cleaned. Container removed (--rm).
  Receipt: `runs/20261024-publication-platform-audit/receipt.json`.
- Actual GPT-6 Luna high, synthetic in-memory workflow only: complete in eight
  calls/nine proposals, with four actor effects, a deferred external obligation
  and valid no-further-action record. All original source IDs use code-generated
  labels; zero response-format or final-reference corrections. Reported usage
  199,141 input + 4,110 output = 203,251 tokens (46,848 cached input included).
  Receipt: `runs/20261024-response-boundary-native-01/receipt.json`.

This measures the repaired response boundary and synthetic workflow, not all
healthcare reasoning, all 75 cases or an official benchmark score. The original
-11 is preserved separately. No judge was run during the audit.

## Authorized next execution

Root will launch fresh `runs/20261024-random-um-t033-12`, exactly one UM task,
Luna high, helpers/auto, 100 model/500 tool calls, 180-second request timeout,
Codex simulator backend and deferred grading. Freeze and commit source before
the actor starts; do not modify source mid-run. Inspect actual saved effects
and stopping record. If another defect appears, preserve that attempt and
correct the general cause before a fresh retry. No paid or semantic judge.
