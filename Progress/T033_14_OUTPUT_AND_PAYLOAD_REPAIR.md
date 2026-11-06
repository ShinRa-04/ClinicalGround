# t033 -14 diagnosis and general repairs — October 25

Root owns coding/execution. The user authorized autonomous remaining decisions,
with an explanatory summary at the end. **No judge** remains the explicit limit.

## Actual attempt, not a successful completed testcase

Frozen actor source `962a559`, `20261025-random-um-t033-14`, one UM case,
Luna high, helpers enabled, 180s silence/600s active cap. Recorded49 model calls,
84 tool proposals, 3,538,962 reported tokens (3,492,446 input/46,516 output;
1,124,864 cached input is included, not additional). Final interrupted generation
did not report complete usage, so this is a known subtotal.

Call49 generated73,675 public reply characters before root stopped only its owned
native child after it had exceeded the existing60,000-character response bound.
The batch completed its normal readback/export/213-file snapshot and stopped the
world. The operator stop is recorded separately in ignored run data; this was
not the600s deadline, a provider outage or a naturally completed actor attempt.
No proposal from call49 was dispatched.

The private bounded capture establishes what the previous -12 capture could not:
the first60,000 characters contain59,792 consecutive zeroes inside `reviewer_id`
in a criteria-save proposal. It is an unterminated JSON string, not a clinical
essay or a token count. The reason the model entered this degeneracy is unknown.
Do not generalize this observed content to the uncaptured -12 output.

## Native key-free checks on a copy

Pinned native structural checker only, `include_semantic_judge=False`, no network,
no credentials, original snapshot integrity reverified. Passed7/16 applicable;
failed9;11 N/A. Structural binary0, fractional0.4375. Semantic criteria unmeasured.

Failed names: `md.decision_exists`, `md.audit`, `nurse.recommendation_exists`,
`nurse.audit`, `outcome.target_status`, `outcome.letter_types`,
`triage.disposition_matches`, `triage.urgency_matches`, `triage.gold_card_matches`.
The missing reviews/outcomes reflect unfinished work. The three triage failures
also need improvement; do not explain all nine solely by the interrupted call.
No hidden expected values were read or encoded. Clinical correctness is not
established by this diagnostic.

## Repairs and decisions

1. **Enforce the existing response bound during streaming.** Previously only
   completed text was checked. Endless output could consume the entire active
   allowance despite already being too large to accept. Both streaming and
   completed excess now return `response_size`, using the existing single
   correction allowance since the last successful observation. The correction
   asks for finite concise JSON, real identifiers and documented optional
   defaults. No partial writes, new retry budget or arbitrary new size cutoff.

2. **Accept verified actor-listed case attachments.** The user explicitly
   approved this. Previously every workspace source was rejected as authored.
   Read-file/PDF/batch excerpts can now support a policy-decision record when
   their exact normalized same-case path matches original successful actor
   document metadata, document kind is an incoming clinical/intake type, text
   and SHA-256 were actually returned, any supplied patient/hash matches, and
   the path is not observed as authored by workspace writes. Filenames alone,
   copied aliases, foreign listings, fixed reference documents and typed drafts
   do not qualify as patient attachments. Mixed batches retain per-child
   pointers. Source/listing hashes are rechecked before the decision is reused.
   This verifies reported provenance, not the clinical truth or human authorship
   of an external document. It does not open new files or perform hidden reads.

3. **Explain empty accepted writes.** Eight real criteria saves omitted the
   `evaluations` input entirely; all returned zero criteria. The model's public
   operational text said it intended to save assessments. Synthetic native
   tests with the isolated contract and the saved active catalogue both emitted
   an explicit evaluations array, so there is no evidence that this adapter
   stripped that field. Added factual feedback lists unsent collection inputs
   and empty output collections, linked to the original evidence. An empty draft
   remains permitted; code does not supply criteria or choose clinical values.
   Original responses remain unchanged, and recent feedback survives projection.

4. **Clarify execution semantics.** Prose does not fill argument fields; a
   conservative `write` classification is a dispatch safety label, not proof
   that a lookup/calculation saved a decision. Use actual tool contracts and
   readback. Triage-stage guidance distinguishes calculated inputs from a
   recorded disposition before immutable routing, while respecting valid
   existing decisions. This is not a prescribed t033 answer or outcome.

## Verification and limits

Full regression650 tests pass/73.666s, including early stream rejection,
bounded correction, attachment/case/draft/path/hash rejection and source mutation,
   and a real engine test where omitted payload feedback lets a model send content
on its next operation. A final native-wrapper sentence clarifies effect labels.
Native protocol probes made two inference-only calls, no actual actor tools:
7,755 and25,398 reported tokens. Both serialized the requested synthetic
evaluation successfully. They are not healthcare-case performance results.

Private captures, snapshots, model requests and clinical data remain ignored.
Original HealthHarness is unchanged. A fresh single-case attempt is required
after this source change; -14 must not be resumed under changed frozen settings.
Final targeted provider28 tests pass/2.158s and assignment10 pass/0.053s after
the final wrapper/triage guidance edits.

## Fresh root-owned single-case command

Root executes this after committing source. Do not launch another copy while active.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-um-t033-15 `
  --domains pa_um `
  --task-id pa_t033_t033_o001_p01_triage_payer `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```
