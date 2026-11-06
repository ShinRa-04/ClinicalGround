# CM output failure and compatibility repair — October 25, 2026

Root owns code and the fresh single CM execution. Luna-high
`cm_native_schema_research` performed read-only primary-source research.
User authorized execution/fixes; no semantic judge. Latest instruction:
finish this CM test, verify/report/save its result, then stop without further
cases or research.

## Preserved failed case

`runs/20261025-random-cm-anorexia-01` ended at workflow model call14/15 tool
operations. Native error arrived before reply text in about4 seconds. The five
Codex patient-simulator requests all completed; this was not a patient simulator
timeout. The failed actor snapshot is preserved and its world stopped.

Native structural checks on that unfinished snapshot:2/6 applicable pass,
4 fail,8 N/A. Failures: assessment record, care-plan record, target status and
cross-stage audit actions. Semantic evaluation was disabled. These do not
establish a clinical failure independently of the interrupted execution.

## Confirmed upstream facts

The exact native error was `Incomplete response returned, reason: max_output_tokens`.
Previously the adapter reduced it to generic `other`. Current Codex source
constructs this error from a Responses incomplete event and maps it to Other;
that wording reports an output-limit termination, not its numeric cap.
[Codex event handling](https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/sse/responses.rs),
[protocol error](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/error.rs).

Reasoning, visible text and other generated tokens share the output allowance.
No observed source establishes the cap in this signed-in connection. The proxy's
4096-token example in [issue36180](https://github.com/openai/codex/issues/36180)
must not be treated as our measured value.
[Official reasoning guide](https://developers.openai.com/api/docs/guides/reasoning).

There is no supported explicit override for our current ChatGPT-sign-in route:
the official limitations exclude max_output_tokens, and the installed turn/start
protocol has no such parameter. Context-window/compaction settings control a
different limit. The API-key Responses route supports the parameter but changes
authorization and billing; no credentials/provider/model settings were changed.
[Sign-in limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).

## Controlled diagnosis, with zero actual actor tools

All model probes used Luna/high and saved receipts locally. They are diagnostic
inference, not dataset reliability trials or clinical scores.

| Probe | Observed result |
| --- | --- |
| Exact failed request | Same immediate output-limit failure |
| Same request plus one concise correction | Same failure |
|89-character synthetic OK/zero-tools request with full active catalogue | Same failure |
| Assessment save_section schema alone with synthetic request | Same failure |
| Active catalogue excluding assessment tools | Reply received |
| Remove discriminator annotation only | Same failure |
| Rebase discriminator mapping only | Same failure |
| Project oneOf to anyOf only | Synthetic reply received |
| Compatible production projection, exact failed request | Reply received,73265 reported tokens; no actual tool execution |
| Four synthetic assessment sections, real native generation and original schema validation | All four accepted; ambiguous untagged object rejected;10693 reported tokens; no actual tools |

The schema change is sufficient to fix these reproductions. This is evidence
of a specific integration incompatibility; it does not prove every upstream
max-output error is caused by oneOf. The documented Structured Outputs subset
lists anyOf rather than oneOf.
[Supported schemas](https://developers.openai.com/api/docs/guides/structured-outputs#supported-schemas).

## Implemented general repairs

1. The native decoding projection uses anyOf for oneOf and omits the OpenAPI
   discriminator hint. Original schemas remain unchanged in the prompt and
   execution validator. Exclusive matching, const tags, required fields,
   identity/scope checks and transactional safeguards remain authoritative.
   A native decoding candidate is not automatically an executable operation.
2. The local validator recognizes well-formed discriminator annotations without
   using them to bypass oneOf. It now validates calendar-date fields required
   by the assessment schema: exact date shape, calendar validity and nullable
   types. The first full-schema synthetic check exposed this second compatibility
   gap before another dataset run; that failed development probe is preserved.
3. The receiver recognizes only the exact observed native output-limit error.
   It reports output_token_limit and permits up to three additional generation
   requests since the last successful observation, subject to aggregate/job
   budgets. Every request is counted. Other format errors keep their existing
   one-correction allowance; unknown provider, quota and scope errors are not
   blindly retried.
4. Repeated requests use saved successful observations and request a new complete
   structured reply. No incomplete JSON is dispatched or blindly concatenated;
   completed actions are not replayed. This does not claim to resume invisible
   reasoning that the native service did not return.

Verification:669 software tests passed in76.945s. Native four-section protocol
check covered clinical, medication, behavioral-health and social-needs payloads.
These establish mechanics, not healthcare-task performance. No hidden benchmark
answers or protected handbook text were added to tracked sources.

## Fresh CM test

Root commits the source, then executes only this case. Prior attempt stays
immutable. The Codex patient simulator remains an experimental substitution;
later clinical grading/competition comparability is not established by these
key-free checks.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-cm-anorexia-02 `
  --domains cm --task-id cm_anorexia_hard_refuses_001 `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```

Final outcome: **-02 blocked on an uncertain outreach-message write; native
structural2/6 pass,4 fail,8 N/A; no model-response error in that trial.**
[Actual result and stopping boundary](CM_ANOREXIA_02_RESULT.md).
Work stopped after this test and documentation; no judge, all75 run or further
research is authorized without new user instructions.
