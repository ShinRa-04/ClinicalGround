# Source-backed policy decisions — October 23, 2026

## Philosophy and user decision

Classify failures from execution/evaluation evidence and fix the general cause.
No task-specific expected outcome, patient answer or hidden scoring information
is encoded. User explicitly selected a source-backed decision record before
policy-dependent actions, allowing policy text from files or tools. The model
chooses the investigation, interprets the policy and selects the action.

Initial instruction was to prepare fixes and let the user run them. User later
authorized root to perform execution too. No additional paid judge budget was
authorized. Root implements and tests directly; no delegated agents.

## Implemented

- `case.record_policy_decision` records policy identity/applicability, exact
  code-captured source passages and field pointers, successful case evidence, the worker's
  criteria/exception analysis, unresolved questions and intended operations.
- Policy citations must point to successful same-scope observations containing
  actual text, from approved reference files or policy-returning tools/documents.
  Metadata, fabricated quotations, patient-chart opinions and authored workspace
  drafts cannot substitute. Generated decision records are not clinical evidence.
- The live standalone runner always enables the guard. The reusable generic
  engine has an operator-level opt-in for synthetic/custom callers; no live CLI
  switch or model tool disables it. Resume retains the case's persisted setting.
- Declared guarded operations include provider bundle creation, disposition and
  submission, plus UM criteria/recommendation/physician/final determination
  operations. Reads, routing and ordinary information gathering are not blocked
  by a universal clinical-review sequence. CM can record policy analysis when
  relevant; this is not a claim that every CM operation is policy-dependent.
- Writes without a valid record are rejected before journal reservation or
  dispatch. Provider final-action arguments must match the action recorded by
  the model. Long hashed MCP aliases cannot bypass known operation matching.
- One unchanged record can support its declared related actions; no duplicate
  review agent or per-action model is introduced. The working context retains
  its compact assessment and source pointers. Changed scope/action or altered
  source content invalidates the provenance check.
- Worker instructions explicitly distinguish administrative completeness from
  eligibility and service need from setting need. They call for applicable
  policy/version, relevant exclusions/footnotes/definitions, supported facts and
  unresolved ranges or exceptions. No specific policy clause or case answer is
  embedded in the prompt.
- Evaluation now reports grounding requirements, record count and refused
  operations separately from semantic correctness and official results. This
  enables grouping a general missing-grounding failure across cases.

## What the guard proves and does not prove

It checks retrieved source provenance and consistency with the declared action.
It does not establish that the model selected the correct governing policy,
read every relevant passage, interpreted it correctly, or chose a clinically
correct outcome. That remains a worker responsibility and evaluator question.
No hidden expectations are read to select a branch.

## Software verification

**454 tests passed in 48.924s**. New checks cover file/tool policy sources,
foreign/fabricated/metadata/authored evidence rejection, action/source/scope
changes, long MCP aliases, and both submission and information-gathering choices.
An actual engine/SQLite integration blocks premature bundle creation before
journaling, then reuses one recorded decision across related operations.
Native-runner tests assert that grounding is enabled.

The old failed t021 attempt is preserved. A fresh attempt follows source freeze;
its actual outcome, snapshot integrity, diagnostics and limits will be recorded
separately. No performance or benchmark-pass claim follows from these tests.

Fresh execution: `runs/20261023-policy-grounded-t021-01`, source `c599391`,
root-owned PID 24544. Same t021 task, Luna high, 48 aggregate model-call / 240
engine-operation caps, one attempt, Codex counterparty backend if required.
Docker Desktop was started for this authorized check; unrelated services were
not running. No paid judge call. Outcome pending.

## First live verification: stopped at citation interface

Source `c599391`, `20261023-policy-grounded-t021-01`, was stopped as a
development failure after 33 actor calls / 167 engine operations (plus nine
identity comparisons). The worker searched/read written references, but no
policy decision record was accepted and no policy-dependent disposition was
committed. The guard blocked an attempted unsupported disposition. This is
not a completed or scored benchmark attempt.

Confirmed interface problems, from actual saved calls:

- The schema's `path` field was interpreted as a policy filesystem path, while
  implementation required a JSON text-field pointer. Repeated attempts hit
  that mismatch. It now accepts an exact already-observed file location or an
  explicit `text_pointer`, with clear descriptions. No new path is opened.
- After addressing paths in offline replay, some quotations still failed exact
  source validation: the worker combined/paraphrased sentences or stripped
  formatting. Other quotations were verbatim. One attempt also used an invalid
  operation namespace. These are citation/operation-expression failures, not
  evidence that the model reached a correct or incorrect clinical disposition.
- Validation now identifies the bad citation, actual source field and retrieval
  coordinates, or the available operation names. It does not invent a source
  or weaken quote verification.

SQLite backup, world export/hash and debug-stop receipt are preserved in the
ignored run root; world stopped. Journal contained 46 completed actions and
no pending/unknown actions. The manifest's running marker is historical. Do
not resume the stopped world or count this as a reliability trial.

Following the user's cross-project preference, a design question is pending:
use source/passage references with code capturing exact text, or retain manually
supplied verbatim quotes with improved feedback. Do not silently choose another
citation design or start another native trial before incorporating the answer.
Path normalization alone passed a 455-test suite (51.256s); subsequent richer
feedback passed 39 focused tests. No additional paid API call occurred.
Final interface/feedback source: **456 tests passed in 46.781s**. Native retry
is still pending the user's citation-interface choice, not implied by green tests.


## Approved passage-reference interface

User selected source and passage references with code capturing exact text.
The worker now supplies the original successful evidence ID and text-field
pointer (file reads infer `/text`). Optional `start` and exclusive `end` are
zero-based character positions within that stored field, as returned by source
inspection/search. They are not absolute offsets in the original file. Omit
both to cite the entire already-returned passage; no verbatim copying or range
guessing is required. No new file or unread tail is opened.

Code captures exact text and coordinates plus the complete field hash. These
are checked again before dispatch. The compact working context keeps pointers
and analysis without repeating captured policy text. Legacy exact quotation
callers remain compatible, but cannot mix quote and range selectors. Source
identity, same-case scope and policy-content checks remain unchanged. Semantic
applicability and the selected outcome still belong to the model.

Focused verification: 13 tests passed, including engine dispatch with a
source-only citation, Unicode slicing, excerpt-relative coordinates, invalid
ranges and foreign/metadata/authored source rejection. Full suite and fresh
native trial results follow separately. No paid judge call.


Release verification: all 13 policy tests pass; a combined 16-test run including
the three intermittently failing existing checks passes (2.463s). Full-suite
attempts were not clean: 459/460 passed with a simulator timeout assertion
failure (61.882s); repeat 458/460 passed with deferred-plan and simulator cached
response errors (99.418s). No policy test failed. Logs are ignored
`runs/20261023-policy-passage-release-tests*.log`. These are open intermittent
suite issues, not an all-green claim; simulator marker publication/read timing
is a suspected cause for the bridge failures, not established here. Simulator
and deferred-grading implementations were not changed by this citation repair.
Proceed with the authorized one-case development verification and report its
actual outcome independently. No paid judge call.


## Fresh native execution of passage-reference source

Source `6a25c13`; run `20261023-policy-grounded-t021-02`; Luna high with the
existing Codex sign-in, 48 aggregate calls / 240 engine operations, one attempt.
World started and passed preflight. Public roster discovery and nine isolated
candidate comparisons ran. Two candidates were accepted, and the existing
exactly-one-positive selector raised at actor discovery. Thus no patient was
bound, no actor workflow or policy record ran, and no valid judge packet exists.
Do not claim a fresh policy-guard pass or that t021's three checks are fixed.

Actual evidence: positive comparison 003 relied on broad symptom-duration and
injection-response similarities despite several discrepancies; comparison 007
contained more specific clinician/imaging anchors. These receipts establish a
weak-positive/ambiguity-handling problem, not a broken retrieval endpoint or a
hidden-fixture diagnosis. Protected details stay in ignored comparison receipts.
Current code requires multiple categories but cannot establish whether anchors
are sufficiently distinguishing. The controller then stops without offering
additional model-led investigation. No target ID, category weight, preferred
clinician or expected outcome was forced into code.

Reported usage: 123,004 input / 4,339 output = 127,343 tokens; nine setup calls,
zero actor workflow calls, zero model errors and zero unknown actions. No paid
judge call, no deterministic check or official score. After batch exit root
captured an actual private world export and stopped the exact owned container.
`setup-failure.receipt.json` records export SHA
`cb3dc8213cfac9772fdaf56380a092d0fbb6a07d00d63bb881090b4e02f36c4d`.
The manifest retains historical `needs_reconciliation`/world-preserved status;
the separate receipt records the later stop, not a normal verified snapshot.

Root asked for the user's design feedback before changing identity handling
again: allow model-led investigation of competing matches with justified
selection or unresolved ambiguity, rather than automatic setup termination.
No decision yet; do not silently rerun until the approved design is incorporated.
Open suite intermittency is separate: the repeated deferred-plan test's synthetic
snapshot logged a PermissionError; simulator failures may involve concurrent
marker publication/reads. These causes remain incompletely diagnosed.
