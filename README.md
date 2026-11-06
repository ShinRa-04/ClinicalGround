# ClinicalGround

A research harness for long-horizon healthcare-administration agents, built for the CHI-Bench
(χ-Bench, [arXiv:2605.16679](https://arxiv.org/abs/2605.16679)) benchmark and the IEEE Big Data Cup 2026
competition around it.

**Status: abandoned (November 2026). Archived as-is. Runnable with your own API key and CHI-Bench access, but untested that way.**

The competition this project targeted was abandoned, so the work stopped. This repository is a research
record: the design, the reasoning, and unusually detailed run-by-run evidence. It is not a ready-to-run
system, and it does not report an official benchmark score.

## Disclaimer: how this was run, and what changed for publication

Read this before judging the results or trying to reproduce anything.

- **No paid API keys were used.** The author had no Anthropic or OpenAI API keys. Subscription tools were
  used as a low-cost workaround to develop and test.
- **Actor model.** OpenAI's `gpt-6-luna`, driven through the locally installed Codex app (its App Server)
  on the author's own ChatGPT subscription. Every model call started a fresh Codex session. The model
  only proposed tool calls; the harness executed them inside the benchmark's offline Docker world.
- **Simulated patient (care management).** Claude Sonnet 5, run through the locally installed Claude Code
  CLI on the author's Claude subscription. This approximates, and is not identical to, the benchmark's
  official patient simulator. Earlier runs used a Codex-model patient.
- **Official judge.** The semantic judge (Claude Opus 4.7) was run exactly once, through OpenRouter. Every
  other result below is from native structural checks only.
- **The subscription connection layer was replaced.** `HealthHarnessCodex/`, the main harness where most
  of the October and November 2026 work happened, is included, but the modules that connected it to the
  subscription tools were deliberately removed because they were a workaround, not a product design:
  - Codex App Server on the ChatGPT subscription (the actor connection): the original `codex_provider.py`,
    `codex_transport.py`, `codex_smoke.py`. In their place, `codex_provider.py` is now a small **API-key
    adapter** with the same interface, which sends each turn to any OpenAI-compatible Chat Completions API
    (see [Running it yourself](#running-it-yourself)).
  - Claude Code CLI on the Claude subscription (the Sonnet patient and Claude-actor experiments):
    `claude_cli_patient.py`, `claude_code_actor.py`, `claude_code_container_actor.py`,
    `claude_container_runtime.py`.
  - Their tests: `test_codex_provider.py`, `test_codex_transport.py`, `test_codex_integration.py`,
    `test_claude_cli_patient.py`, `test_claude_code_actor.py`, `test_claude_code_container_actor.py`.
  The OpenRouter judge modules (`openrouter_judge.py`, `openrouter_batch.py`) remain; they use an
  ordinary API key.
- **Consequence.** The harness imports and its offline tests pass, but it has **never been run end to end
  with the API-key adapter**; every recorded result came from the subscription setup above. The Claude
  CLI patient backend and Claude actor backends are not available. The gated CHI-Bench dataset and
  handbook are not included: you need your own access. The recorded runs cannot be reproduced exactly.
- **Official task limits were not met.** Core tasks allow an agent timeout of 900 s (doubled by the
  multiplier in the submission example) on 2 CPUs, 4 GB and no GPU. Runs here took roughly 28 to 65
  minutes, and document search used local GPU embeddings. A result from this harness would not have been
  valid under the official limits.

## The idea

The model proposes structured decisions. The harness executes the real tools. Code checks provenance,
isolation, execution limits and observed effects. It never decides which clinical answer is right.

Main mechanisms:

- **Completion contracts** built from the public task text, so "done" means no further useful permitted
  action remains, supported by recorded effects, not just a status flag.
- **Policy-grounded decisions.** Consequential actions must cite retrieved policy text and case evidence.
  Provider case creation binds every requested field to a documented or inferred basis, and inferred
  fields must cite a reference.
- **Role catalog.** 66 micro-roles derived from a 97-role hospital study, each with an authority field
  (a mandate, never an allow-list) and an approach field. Roles are design responsibilities, not 66
  mandatory agents.
- **Care-management conversation worker.** A separate worker with consent gates, a decision-invitation
  gate, awareness of the simulator's turn cap, and breadth-first "information needs" for the assessment
  interview.
- **Permitted declines** are recorded as outcomes, and **final reports are honest**, listing outstanding
  duties instead of claiming completion.
- **Offline testing and replay.** 925 offline unit tests passed in the main harness on 6 November 2026,
  before the removals above, plus replay of saved runs against new logic. Tests establish mechanics, not
  benchmark success.

## Status and results

Tracks: provider prior authorization (PA), payer utilization management (UM), care management (CM).

| Measure | Result |
|---|---|
| Executed attempts | About 200, covering all 75 public tasks |
| Attempts ever judged | 1 (PA provider t012, Oct 22: strict reward 0, 9/11 checks, both semantic checks passed) |
| Full native structural pass | 4 of 75 tasks: CM `cm_asthma_low_coop_001`; UM `pa_t012_…_triage_payer`; UM `pa_t033_…_triage_payer`; PA provider `pa_t012_…_new_referral_provider` |
| Best near-miss | PA provider t008 reached 10/11; site of service was the only failure |
| Last run | PA provider t011, 6/11, exhausted its model-call budget after 65 minutes |

Everything except the single judged attempt is native structural checks only, with no judge. Most other
tasks were last run on older harness versions, so their results do not reflect the final code. Not an
official score.

### Open findings for anyone resuming

1. Official time and no-GPU limits are not respected (see the disclaimer).
2. Provider request-field choice, mainly site of service and procedure code, is the main PA provider gap.
3. Codex reasoning output can overflow on long contexts; the output cap is only advisory.
4. CM conversations are constrained by the simulator's turn cap of about 20 turns.

## Repository layout

| Path | Contents |
|---|---|
| `HealthHarnessCodex/` | The main harness: actor loop, batch runner, simulator bridge, role and completion logic, tests. Its subscription connection was replaced by an API-key adapter (see the disclaimer and [Running it yourself](#running-it-yourself)). |
| `HealthHarness/` | The original harness the Codex-based work started from, pinned. Standard-library Python core; see its own README. |
| `HealthHarnessBlueprint/` | Design proposal: hospital-style organization, role catalog (66 micro-roles) and generators. |
| `Progress/` | Handoff and design notes with every run's evidence and decisions. Start at `Progress/HANDOFF.md`. |
| `Plan/` | Background study, competition research, organization and healthcare-role research. |
| `Runner/`, `Submissions/` | Docker-based toolkit and submission tooling. Official benchmark checkouts are not included. |
| `HarnessResearch/` | Source-backed study of modern agent harnesses (memory, context, tools, sessions). |
| `HarnessGuide/` | Guide to the dataset workflows and the implemented harness, with glossary. |

Not included: the removed subscription connection modules in `HealthHarnessCodex/`, the protected Managed-Care Operations
Handbook, downloaded benchmark data, run outputs and credentials.

## Where to start reading

1. `Progress/HANDOFF.md`, the top section, for the final state.
2. `HealthHarnessCodex/ARCHITECTURE.md`, `HealthHarness/ARCHITECTURE.md` and `HealthHarnessBlueprint/README.md` for the design.
3. `HarnessGuide/README.md` for how the pieces fit together.

## Running it yourself

Untested end to end with the API-key adapter. Expect to debug. Developed on Windows 11 with Docker
Desktop and PowerShell; other platforms were not tried.

**You need:** Docker Desktop; Python 3.12; an OpenAI-compatible API key for a model that supports tool
calling; a Hugging Face account approved for the
[Managed-Care Operations Handbook](https://huggingface.co/datasets/actava/managed-care-operations-handbook);
optionally an NVIDIA GPU for the semantic search tool.

1. **Get the official benchmark** (the toolkit builds from this exact commit):

   ```powershell
   git clone https://github.com/actava-ai/chi-bench Runner/chi-bench
   git -C Runner/chi-bench checkout 4444a07fa68a4f1623f841a292a54e284fc8e7f7
   ```

2. **Build the toolkit and download the data** (from the repository root):

   ```powershell
   .\Runner\toolkit.ps1 build
   .\Runner\toolkit.ps1 download-public
   .\Runner\toolkit.ps1 hf auth login        # after your handbook access is approved
   .\Runner\toolkit.ps1 download-handbook
   ```

3. **Build the benchmark runtime image and pin it.** Your build has its own image ID, so tell the harness:

   ```powershell
   .\Runner\toolkit.ps1 build-runtime
   $env:CLINICALGROUND_RUNTIME_IMAGE_ID = (docker image inspect bigdata-chi-bench:runtime-4444a07 --format '{{.Id}}')
   ```

4. **Optional semantic search** (GPU): `.\Runner\toolkit.ps1 build-retrieval`. Without it, the
   `workspace.hybrid_search` tool reports itself unavailable; file search and reads still work.

5. **Configure the model:**

   ```powershell
   $env:CLINICALGROUND_API_KEY  = '<your key>'                 # never commit it
   $env:CLINICALGROUND_BASE_URL = 'https://api.openai.com/v1'  # or any OpenAI-compatible endpoint
   $env:CLINICALGROUND_MODEL    = '<model id>'                 # overrides --model
   # optional: $env:CLINICALGROUND_REASONING_EFFORT = 'none'   # if your endpoint rejects reasoning_effort
   ```

6. **Run one task** (a payer triage task needs no simulated counterpart):

   ```powershell
   cd HealthHarnessCodex
   python -X utf8 -m health_harness_codex.batch --dataset-root ..\Dataset\chi-bench `
     --run-dir runs\first-run --domains pa_um --task-id pa_t012_t012_o001_p01_triage_payer `
     --attempts 1 --concurrency 1 --actor-backend harness --composition helpers `
     --recovery-helper-policy auto --max-model-calls 100 --max-tool-calls 500 --json-summary
   ```

   For care-management tasks add `--simulator-backend codex`; the simulated patient then also uses your
   API model through the same adapter (the official patient is Claude Sonnet 5, so results will differ).
   Grading is deferred and no paid judge is called. Run output stays in `HealthHarnessCodex/runs/`,
   which is git-ignored.

## Tests

`HealthHarnessCodex/tests/` is the main offline suite (no network, no Docker, no keys). From a fresh clone
of this repository it passes: 791 tests, 2 skipped (Codex-app behaviour replaced by the adapter).

```bash
cd HealthHarnessCodex
python -X utf8 -m unittest discover -s tests -q
```

The original `HealthHarness/` has its own suite and demo (`python -m health_harness --demo`,
`python -m unittest discover -s tests -v` from inside it); not re-run for this publication.

## Licensing and third-party material

No licence file is included for this repository's own code. The paper PDF in `Plan/Source/` is
CC BY-SA 4.0; see [Plan/Source/NOTICE.md](Plan/Source/NOTICE.md). The CHI-Bench handbook, datasets, run
outputs and credentials are not included.
