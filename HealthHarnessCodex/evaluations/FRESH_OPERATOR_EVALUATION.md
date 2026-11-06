> Codex fork note: this document was copied from the original HealthHarness baseline. The current connection, session boundaries and verified Codex behavior are documented in [the fork README](../README.md) and [verification](../VERIFICATION.md). Inherited claims of no Codex connection describe the original at its stated commit. The Codex host-to-Docker trial bridge is not implemented.

# Fresh operator evaluation without a separate API key

Date: October 19, 2026. Evaluated implementation: commit `b3ce3db`. This is a fresh operator/readiness check, not a dataset trial or a benchmark score.

## Requested experiment

The user requested a GPT-6 Luna agent with high reasoning, no inherited project conversation, given the created harness as an unfamiliar package and asked to do its dataset workload without a separate provider API key.

Dispatched `fresh_operator_evaluation` with `fork_turns="none"`, model `gpt-6-luna`, reasoning effort `high`. It received the package and dataset locations, the requested task and execution/data-access constraints. It was told not to consult Progress/, prior research, blueprint, Codex memory or previous agent outputs. It could inspect the delivered package normally. Thus this is no inherited conversation/history, not a claim of no pretrained benchmark knowledge or an information-isolated operating system. Package documentation itself is visible to an ordinary recipient.

The evaluator was told to attempt legitimate entrypoints and determine whether its inference could be driven through the delivered package. It could not replace the package with a separate Codex solver, patch the implementation, start services, extract credentials or inspect hidden answers. The parent supplied no known implementation failure list or expected evaluation result.

## Observed result

The evaluator independently ran, from HealthHarness/ with bundled Python 3.12.14:

```powershell
python -m health_harness_codex --demo
python -m unittest discover -s tests -v
python launch_chi_bench.py --help
```

- PA, UM and CM demonstrations returned local synthetic completion, each with two scripted model turns and one synthetic observation.
- All **43 existing tests passed**. This rerun is not 43 new tests or 43 dataset cases.
- Launcher help worked; no trial was launched.
- It found no included bridge from this Codex session's Luna inference into the package's model interface.
- It performed no dataset workflow, official MCP interaction, provider call, Docker trial, patient/P2P conversation or official judging. No clinical/task-completion quality was measured.

The evaluator returned: “The delivered package cannot run this workload using this session’s Luna inference without an additional adapter or provider key.” This is a conclusion about the shipped integration, not a universal claim that an API key is required for every possible implementation.

Evidence in the shipped code:

- [cli.py](../health_harness_codex/cli.py): configured execution requires the named key environment variable and constructs `OpenAICompatibleModel`; the default/demo constructs `ScriptedModel`.
- [providers.py](../health_harness_codex/providers.py): its external adapter sends explicitly authenticated Chat Completions requests. The scripted alternative is a deterministic fake.
- [engine.py](../health_harness_codex/engine.py): accepts an injected model object with `complete(messages, tools, max_output_tokens=...)`; this is an extension point, not an implemented Codex transport.
- [chi_bench.py](../health_harness_codex/chi_bench.py): the optional trial adapter requires explicit provider configuration/key, independent of the surrounding Codex app session.

## What the proposed method can establish

| Method | Valid interpretation | Limit |
| --- | --- | --- |
| Fresh Codex agent inspects/starts/tests the delivered package | Operator usability, reproducible software checks and integration gaps | Does not measure actual dataset completion if the acting model is never connected. |
| Codex solves cases directly using its own shell/MCP tools | Evaluation of that documented Codex-driven system | Cannot attribute success to our engine's memory, context reducer, budgets, role composition or effect gates when bypassed. |
| Our engine requests model replies through a supported, controlled inference adapter | A functional model-in-the-loop test of our actual orchestration, with adapter/backend disclosed | Requires implementation and evidence that all effects/context boundaries actually remain controlled by our engine. It is not automatically an official scored trial. |
| A model follows copied role prompts manually | Prompt/procedure exploration | Does not validate SQLite recovery, actual context construction, isolation gates or automatic orchestration. |

A Codex wrapper also has its own context and tools. If it remembers earlier content after our engine drops it, it can bypass the very context-management behavior being evaluated. An adapter must deliver the exact current scoped request, prevent out-of-band dataset tools/effects, handle helper requests, record actual decisions and usage, and avoid unrelated patient/session history. A supported stateless request route is a cleaner experiment than an unconstrained long-running coding conversation.

The official environment's patient/P2P simulator and judge are separate inference consumers. Connecting the acting model through a subscription does not establish their authentication, availability or scoring compatibility. The existing runner guide documents native judge credentials; local public source constructs an Anthropic patient-simulator client. None of those services was started here.

## Supported no-separate-key options: documentation, not implementation

Official OpenAI documentation checked October 19:

- [Authentication](https://learn.chatgpt.com/docs/auth): Codex supports ChatGPT subscription sign-in as well as API-key sign-in for local work.
- [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode): `codex exec` supports automation/structured outputs and reuses saved CLI authentication. This does not make arbitrary Python code inherit the app's authenticated model interface.
- [Sign in with ChatGPT quickstart](https://developers.openai.com/siwc/quickstart): eligible plan-backed requests in participating applications can avoid a separate developer API key through the documented registration/sign-in flow.
- [Codex app-server integration](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server) and [preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations): the documented plan-backed route uses Responses API and has specific request/state/tool constraints.

These routes mean a no-separate-API-key integration is possible in principle. Eligibility, exact Luna model availability, request limits and successful inference on a chosen route remain unverified for this account. The current harness implements Chat Completions, not that plan-backed Responses adapter. No OAuth registration/login, token reading/copying, API-key creation or new authentication was attempted.

## Local command collision and preserved diagnostics

The parent's PATH check resolved `codex.exe` to an unrelated Python comic-library application under Python311/Scripts. Invoking its version/help imported that application, generated a root config directory and failed on the missing Unix `resource` module. It is not evidence of an OpenAI CLI installation or authentication state. Do not use this executable for a proposed model adapter.

The generated directory was identified by its creation times and installed application source (`Path.cwd()/config`). No generated secret value was read or printed. Automatic command review blocked deletion, giving only “blocked by policy.” The confirmed generated files were instead preserved by moving the whole directory to ignored `Runner/.cache/codex-name-collision-20261019/`. No unrelated installation or user data was removed. The evaluator itself intentionally changed no source files.

## Conclusion and next step

The requested fresh operator check was performed. It is valid for usability/integration assessment and demonstrated a missing inference connection. It did not do the dataset. A supported no-key adapter plus actual authorized environment access would be required for a genuine harness-driven trial; official scoring has its own prerequisites. Preserve that distinction when comparing this work with another agent repository.
