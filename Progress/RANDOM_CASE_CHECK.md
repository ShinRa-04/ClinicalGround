# Random single-case check — October 22, 2026

User requested a completely random additional task. Root performs the check;
no delegation, task-specific source changes or assisted retries are planned.

## Selection and frozen execution

- Enumerated the 75 core tasks using public instruction files only.
- Excluded only the immediately preceding provider t012 case, leaving 74.
- Selected once with Python `secrets.choice`; no redraw, domain preference,
  filtering by difficulty, or hidden answer inspection.
- Selected `pa_provider/pa_t021_t021_o003_p01_new_referral_provider`.
- Source: `8c668febbcf20574bb63cbc9f762be6e22b66f6b`.
- Run: ignored `HealthHarnessCodex/runs/20261022-random-case-223642/`.
- Selection/launch receipt: adjacent `.launch.json`; root-owned PID 6344.
- Model: `gpt-6-luna`, high; one attempt, concurrency one.
- Limits: 48 actor calls, 240 engine operations; experimental Codex counterparty
  backend with its separate 8-call limit if a conversation is required.
- Fresh Docker world; no provider credentials or benchmark network egress.
- No additional paid judge budget authorized. Preserve an evaluable snapshot,
  then perform isolated deterministic checks without semantic judging.

## Executed outcome: incomplete workflow and deterministic failures

Finished at 22:44 IST, approximately 7 minutes 52 seconds after batch startup.
No source changes, corrective operator instructions, retries or redraws were
used during the attempt.

| Measurement | Actual result |
| --- | --- |
| Local status | `unresolved`, classification `incomplete_workflow` |
| Stop reason | `stop_recovery_limit_reached`; two recovery prompts recorded |
| Model calls / engine operations | 31 / 60 |
| Observed case status | `docs_needed` |
| Overall form completeness | False |
| SubmissionPacket count | 0 |
| Reported input / output tokens | 1,230,530 / 20,234 |
| Reported total tokens | 1,250,764 |
| Cached input, included in input | 381,824 |
| Model errors / unknown actions | 0 / 0 |
| Open obligations | 2 |
| Snapshot | Saved; integrity validation passed |
| Attempt world / diagnostic container | Stopped / removed |
| Paid judge calls | 0 |

Isolated official deterministic verifier logic, with semantic judging explicitly
disabled and network unavailable: **1 passed / 10 failed / 1 N/A**. This is a
partial diagnostic, not a full official semantic evaluation. The deterministic
failures already rule out calling this a successful benchmark attempt.

| Check | Result |
| --- | --- |
| `new_referral.service_request_created` | Failed |
| `new_referral.procedure_code` | Failed |
| `new_referral.required_diagnosis_codes` | Failed |
| `new_referral.service_type` | Failed |
| `new_referral.site_of_service` | Failed |
| `new_referral.case_created` | Failed |
| `new_referral.case_status` | Failed |
| `provider_pre_submission.provider_determination_present` | Failed |
| `provider_pre_submission.final_action` | Failed |
| `provider_pre_submission.packet_absent` | Passed |
| `provider_pre_submission.required_documents_present` | N/A |
| `cross.forward_transitions` | Failed |

## What is established and what remains uncertain

The actor did execute case creation and a provider determination, but the
verifier's safe resolution diagnostics report **zero matching service-request
candidates**, resolution `missing`; case resolution is
`unresolved_service_request`. Several downstream checks are failed by that
missing-target condition, so ten failed checks are not proof of ten independent
field-level mistakes.

This exposes a likely identity/linking issue, but its exact cause has not been
established. Do not assert that the tool failed, the wrong patient was selected,
or the dataset is defective without further evidence. Hidden target values and
expected answers were not read or fed back to the actor. Only generic verifier
code and the evaluator's resolution/count diagnostics were inspected.

The actor additionally reported unresolved clinical-intent clarification and
a required access-attestation field. It chose a gather-more-evidence
disposition, left forms incomplete and did not submit. Its report is an actor
claim, not independent confirmation that no permitted route could resolve those
issues. It also reported that a reference read exposed metadata rather than
substantive text; the retrieval path needs examination before calling that
reference unavailable.

## Artifacts and next investigation

### Follow-up cause audit: same domain, identity confidence and reference loss

Both recent tasks, t012 and t021, are **provider PA**. The random draw did not
select a different domain. Their different outcomes therefore do not establish
that cross-domain differences caused this failure.

Inspected actor observations, the public t021 instruction and implementation;
no expected identities or hidden answers were opened. Findings:

1. **Weak identity admission.** Discovery recorded
   `public_instruction_unique_chart_phrase`, with no explicit patient name
   match. The selected chart and task share a nine-token standardized diagnosis
   phrase. The algorithm selects the strongest unique exact phrase and only
   uses age/sex to resolve some ties. Here age/sex agree, but that does not
   independently establish identity. The patient is then bound and other
   roster discovery is hidden from the case worker. This is a structural
   confidence problem. Combined with the verifier's zero target matches, it
   makes incorrect identity/linking a strong hypothesis, but the exact target
   mismatch has not been independently resolved.
2. **Confirmed reference-text omission.** Two successful `workspace.read_file`
   observations saved 3,279 and 7,520 text characters respectively. The latter
   response occupies 7,835 serialized characters and crosses the 6,500-character
   recent-turn compaction threshold. Reproducing the current 3,000-character
   preview shows metadata retained and `/text` omitted. Unlike explicit local
   evidence inspection, `workspace.read_file` is not exempted. Thus the later
   model context can hide text that the actual read successfully retrieved.
   The original observation is intact and typed retrieval exists, but the
   actor did not recover that text before claiming it had not observed the
   reference instructions. This is our context/retrieval usability defect,
   not proof of missing benchmark documentation.
3. **Ineffective recovery.** Recovery prompts followed calls 25 and 30. The
   engine stopped at call 31 for `stop_recovery_limit_reached`, despite a
   48-call cap. It did not establish a corrected identity, recover the omitted
   reference text or resolve the form gap. Stopping an unsupported submission
   is appropriate; the preceding investigation/replanning was inadequate.

Ten failed checks are partly a cascade: generic verifier code marks dependent
request/case/field checks false when it cannot resolve the target request.
They should not be presented as ten independent coding or medical mistakes.
No semantic judge is needed to establish these observed execution failures;
semantic quality and a full official evaluation remain unmeasured.

Expected corrections require stronger evidence-based identity admission,
preserving bounded reference text or reliably retrieving it, and targeted
recovery tied to the actual unresolved dependency. These findings are not yet
implemented fixes and do not change the recorded random attempt.

### Preserved artifacts

All private outputs remain ignored in the recorded run folder:
`batch.manifest.json`, the attempt's `run.result.json`, `evaluation.json`,
`state.sqlite`, events and immutable snapshot; `deterministic-diagnostic/receipt.json`
records the key-free checks and cleanup. The adjacent launch receipt preserves
the one-draw selection and frozen command.

Next investigation, if authorized: reconcile the public instruction's identity
with the actor-visible discovery/creation links, then inspect the unresolved
form/reference retrieval path. Preserve this failed attempt. Do not use hidden
target identifiers to repair the actor or combine future assisted fixes with
this run's performance record.
