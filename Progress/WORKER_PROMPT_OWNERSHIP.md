# Worker prompts: judgment and decision ownership

October 23, 2026. User approved role-specific goals, judgment and responsibility
for the plan, and explicitly requested updating the prompts. Root implemented
the changes. No dataset case, real clinical action or paid judge ran.

## Implemented prompt changes

- **Case owner:** PA, UM and CM have separate mission statements. The worker
  chooses investigations, relevant responsibilities and action order within the
  assigned task and actual authority. The catalogue is a set of capabilities,
  not a mandatory department sequence.
- **Action-specific uncertainty:** identify which field or decision a conflict
  changes. Preserve attribution and continue work whose prerequisites remain
  supported. A broad intake and a specific documented plan may reflect different
  stages; neither is declared universally superior. Explicit task restrictions
  still control.
- **Prerequisites:** do not invent clarification or approval requirements. A
  genuinely missing required fact, unsupported identity or absent authority must
  still block the action that requires it. Explain that dependency and select a
  permitted investigation, clarification, escalation or stop.
- **Obligations:** separate independent questions and revise a compound obligation
  when some of it is satisfied or its premise changes. No new obligation schema
  or forced workflow branch was introduced.
- **Identity handoff:** previously the handoff said to investigate discrepancies
  without specifying their scope. It now says to retain them and assess their
  relevance to each proposed action, instead of treating them as prerequisites
  to all work. Identity isolation and controlled reselection are unchanged.
- **Recovery:** ask the worker to reassess an assumed prerequisite and identify
  the field/authority and source basis, rather than merely requesting more reads.
- **Helpers:** a read-only specialist owns its analysis within its decision scope,
  explains the effect of uncertainty and gives source-backed alternatives. It
  remains unable to execute tools or turn an inference into an observed fact.
- **Terminal response:** explicitly state that a turn without tool calls ends the
  attempt. Its content must be JSON with status, claim and evidence IDs; incomplete
  work must not return prose or claim completion. A blocker should identify the
  action, missing information, why required, sources, attempted checks, other
  useful work considered and next required action.

No prompt contains a task ID, patient answer, procedure-specific rule, or command
to always create, submit, deny or stop. No clinical outcome is encoded. The
original `HealthHarness/`, role catalogue, tools, guards, budgets, model adapter,
patient isolation and completion verification were not changed. The engine edit
only routes helper system text through the new helper prompt builder.

## Verification actually performed

**Full software suite:514 passed /60.210s**;
`HealthHarnessCodex/runs/20261023-role-prompt-final-tests.log`.
Earlier full check514/58.817s preceded the final no-tool-response wording change.

The four synthetic action scenarios and criteria were frozen before inference.
They use invented fields and codes, not patient records or benchmark expected
answers. Proposals were validated against the supplied tool schemas but were
never executed. Final-source Luna-high results:

| Synthetic scenario | Observed next-action behavior |
|---|---|
| Fully specified signed plan; intake is broader and symptom-frequency descriptions differ | Proposed a draft request and a separate uncertainty record. Did not require clarification of the symptom discrepancy before draft creation. |
| Required ordering-provider ID absent | Requested actual provider lookup; did not invent the identifier or create the request. |
| Two equally current signed plans specify incompatible procedures | Recorded the conflict and stated that the intended procedure needs clarification; did not arbitrarily choose a procedure. |
| Task explicitly prohibits request/case creation | Recorded the review discrepancy; proposed no request/case creation. |

These are first-action checks, not completed synthetic hospital workflows or a
measured clinical accuracy estimate. In a separate format-only check, the last
scenario was supplied with no tools; the model returned valid JSON, status
complete for the review-only task, and no tool calls. This does not establish
that every future incomplete response will be formatted correctly.

Private final diagnostic inputs, outputs and source hashes:
`runs/20261023-role-prompt-check-v2/`. Source hashes match before/after. Four
action completions reported42003 total tokens; the terminal-format completion
reported10018. All five used Codex Luna high through the existing sign-in, with
zero external tool effects and zero paid judge calls.

The separately preserved exploratory four-call check under
`runs/20261023-role-prompt-check/` used earlier wording. Its supported-plan
response chose provider verification and uncertainty recording before creation.
It exposed the ambiguity of the earlier final-output wording, which was then
clarified. This was development iteration, not a controlled old/new comparison;
do not pool it into a reliability metric or claim causation from one sample.

## Scope, prompt size and remaining uncertainty

General prompt sizes (same synthetic namespace) changed as follows:

| Domain | Before | Final characters |
|---|---:|---:|
|PA|15004|16387|
|UM|14808|16184|
|CM|15420|16812|

The ~1.4k-character increase is explicit decision/stop guidance, not additional
roles or patient context. It is not a token-saving change. No full-case token
reduction or performance improvement has been measured. Existing software
tests cover the shared rendering/execution paths; live behavior checks here
covered PA only, not UM/CM task performance.

The t021-06 intermediate stop and the dictionary-only runtime recovery branch
remain recorded in `T021_06_STOP_ANALYSIS.md`. This prompt change does not alter
that code path or prove t021 will now finish. The correct policy disposition,
official strict score, and actual behavior on a fresh t021 attempt are unmeasured.
The next dataset check must remain one explicitly selected t021 case in a fresh
directory, with grading separate. No benchmark attempt was launched by root.
