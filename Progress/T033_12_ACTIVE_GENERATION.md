# Root t033 -12: active generation interrupted by the request deadline

October 24, 2026. User authorized root to run/fix/retry one entire testcase,
without the judge. Root ran only t033. No paid or semantic judge ran.

## Actual failure

`HealthHarnessCodex/runs/20261024-random-um-t033-12` used source `47e4c38`.
Actor ended error after five model calls and fifteen proposals. Call 5 exceeded
the configured 180-second request deadline while still producing assistant
output: 46,845 characters, 19,702 stream updates, 0.11 seconds of output/native
idle time at expiry. Cleanup was confirmed. No proposal from that unfinished
reply was dispatched. This is not a duplicate-ID error, JSON parse rejection,
silent unresponsiveness, context-character cap or exhausted model/tool budget.

**Severity: execution-blocking timeout.** Earlier permitted reads/observations
are preserved, but the testcase did not reach a valid execution endpoint. A
transport_read timeout phase here identifies the local deadline wait; it does
not establish a remote network outage. Do not execute partial JSON to recover.

The current role was triage; investigation had retrieved policy and clinical
document excerpts. Four replies completed before call 5. The input for call 5
was 134,295 characters including 65,447 characters of tool declarations and
63,827 message characters. This is far below the adapter's input byte bound.
The output was below the 60,000-character completed-reply bound when interrupted.
The model's exact partial output was not saved in that old run. Therefore,
whether it was lengthy useful arguments, excess narrative or repetition remains
**unconfirmed**; do not label it an infinite loop or valid finished work.

Snapshot (213 files) provenance/inventory verified after the attempt; world
stopped. Do not modify/reclassify the original -12 as completed. Reported usage
189,615 covers the reported data; no finished-call usage was available for the
interrupted generation. Character/4 output estimates are not actual usage.

## Verified interface facts

The installed App Server generated TurnStartParams has outputSchema but no
max-output-token RPC field. The wrapper's max_output_tokens remains advisory.
Official documentation explains that App Server takes its RPC inputs rather
than arbitrary Responses parameters, and the ChatGPT-plan preview omits
max_output_tokens. Do not claim an invented hard token cap.

Sources: [App Server documentation](https://learn.chatgpt.com/docs/app-server),
[ChatGPT-plan preview limits](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
Local generated protocol schema is under ignored
`runs/20261024-codex-request-schema/`.

The installed configuration schema supports model_verbosity. A real native
ephemeral thread accepted model_verbosity=low without an inference call. The
change is thread-local; no user/global settings, model ID or high reasoning
effort changed. Lower verbosity is expected to discourage excessive public
output; it does not prove the original long reply's cause or impose a token cap.

## Implemented diagnostics

CodexSessionModel now keeps a bounded public-assistant-text capture for the
active thread/turn only. Reasoning events and foreign thread/turn text are
excluded. Capture resets before every request, including invalid next inputs.
If generation completes but parsing fails, the exact completed parser input
is retained instead of a possibly mixed delta stream.

RecordingModel writes failed request messages/tool schemas and up to 60,000
characters of public reply to `model-failures/call-NNNN.private.json` inside the
ignored case run folder. These are sensitive private debugging artifacts and
must not be tracked, printed or uploaded. Normal events/logs contain only a
capture-success boolean. A capture IO failure never replaces the original
exception; files are exclusive and linked directories are refused. Oversized
requests are represented by their hash/omission marker instead of unbounded
diagnostic output. No reasoning, auth configuration or RPC envelope is captured.

## Verification and next step

631 regression tests pass in 80.490 seconds. Targeted tests verify capture
privacy/bounds/foreign-event exclusion, unchanged original failure on capture IO
error and existing parser/streaming behavior. Native thread configuration was
accepted without inference. No judge used.

Root asked whether active output should be allowed up to ten minutes while
retaining a three-minute silence timeout. That preference was unanswered when
preparing the next attempt, so the existing 180-second hard deadline remains.
Do not interpret elapsed time as approval. Next fresh single-case attempt is
`runs/20261024-random-um-t033-13`, with low public verbosity and private failure
capture. Root continues execution and diagnosis; no full-dataset run or judge.
