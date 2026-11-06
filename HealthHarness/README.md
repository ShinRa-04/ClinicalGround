# HealthHarness

An independent healthcare workflow agent harness for provider prior authorization (PA), payer utilization management (UM) and care management (CM). It organizes responsibility, evidence, obligations, tools and handoffs over a supplied environment. χ-Bench remains the environment and evaluator.

The first implementation uses a composite case owner, optional bounded analysis helpers, a packaged catalogue of 66 design responsibilities, case-scoped SQLite state, transactional worker fencing, an action journal, configurable stateless model requests and an MCP/tool boundary. Responsibility contracts are not 66 mandatory agents or independently validated clinical capabilities.

Start with [architecture](ARCHITECTURE.md), [actual χ-Bench work/interface mapping](CHI_BENCH_MAPPING.md), and [executed checks and limits](VERIFICATION.md). Project continuity lives in [Progress/HEALTH_HARNESS_IMPLEMENTATION.md](../Progress/HEALTH_HARNESS_IMPLEMENTATION.md). The [larger blueprint](../HealthHarnessBlueprint/README.md) remains a design reference.

## Local development

Python target: 3.11 or later. The core uses the standard library; no Docker or model credential is needed for synthetic tests. From this directory:

```powershell
python -m health_harness --demo
python -m unittest discover -s tests -v
```

On this workspace, the bundled executable is `C:/Users/prath/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; the verified version is 3.12.14. Selecting Luna for code writing does not select a model for live harness execution.

Runtime files, private configs and logs belong in ignored `runs/` or `*.local.json`. Never commit credentials, patient payloads or protected handbook content. Optional Harbor integration requires the existing benchmark tool environment; do not install its compiler dependencies on the host.

The default `python -m health_harness` invocation also runs only the offline synthetic demo. Its PA/UM/CM examples demonstrate software contracts using scripted observations; they are not completed χ-Bench cases or clinical evaluations.

## Configured execution

Copy [config.example.json](config.example.json) to `run.local.json` and replace every placeholder locally. Keep the secret itself in the named environment variable; the example is a format template, not a runnable trial configuration.

Use the local JSON configuration format with these fields:

| Field | Meaning |
| --- | --- |
| `scope` | Explicit `environment`, `task`, `organization`, `principal`, `patient`, `case` identities. No identity is inferred from a disease or filename. |
| `domain` / `instruction` | Assigned PA, UM or CM work and the actual actor-visible instruction. |
| `provider` | Explicit `model`, compatible `/v1` `base_url` and `key_env` naming a locally configured environment variable. Optional timeout/reasoning effort depend on endpoint support. |
| `mcp_servers` | Actual actor-authorized endpoint(s), optionally with stable namespace labels/timeouts. Do not expose unrelated principals' servers to the job. |
| `storage` / `workspace` / `output_dir` | SQLite file, workspace parent and private receipt directory. Relative paths resolve from the config file. Artifacts and receipts are partitioned by full scope. |
| `read_roots` | Explicit approved read-only reference files/directories. Do not point at a dataset/fixture/source checkout root. |
| `composition` | `combined`, `helpers`, or `team`. `team` uses separate sequential bounded role prompts; no concurrent worker-process pool is implemented. |
| `limits` | Positive `max_model_calls`, `max_tool_calls`, `max_context_chars`, `max_output_tokens`. Aggregate model limits include helpers; persisted case limits survive resume. |

Once a private config has actual identifiers/endpoints and the configured key environment variable exists:

```powershell
python -m health_harness --config .\run.local.json --live
python -m health_harness --config .\run.local.json --live --resume
```

These commands can incur model and environment costs. They are documentation for an explicit future invocation, not commands executed during implementation. Configured execution without `--live` is rejected. A zero exit denotes an accepted **local** completion claim; non-complete states have a nonzero exit and a scoped JSON receipt. Exceptions/preflight failures are nonzero as well.

Resume does not grant permission to resend an uncertain effect. A pending/unknown submission or message remains blocked until its real outcome is reconciled. Do not edit the database to bypass that protection. A new case requires a fresh full scope and case workspace; general role instructions are the reusable part.

## Pinned χ-Bench bridge

The external adapter is `health_harness.chi_bench:HealthHarnessAgent`, targeting checkout `4444a07`. The pinned `cb` runner does not resolve this class merely because `submission.agent` contains a new name; [the integration map](CHI_BENCH_MAPPING.md) explains the dispatch limit.

[launch_chi_bench.py](launch_chi_bench.py) assembles a direct single-trial Harbor command. Its default is **plan only**; `--execute` is required to launch. The existing `Runner/toolkit.ps1` conditionally mounts this folder read-only at `/health-harness` so the controller can import the external package without modifying the official checkout or installing host dependencies.

From the repository root, inspect the launcher help through the existing toolkit when Docker is deliberately available:

```powershell
.\Runner\toolkit.ps1 python /health-harness/launch_chi_bench.py --help
```

Local help needs no Docker: from this folder, `python launch_chi_bench.py --help`. A plan requires an actual single task folder, an ignored scope-only JSON file containing the six IDs, domain, runtime model, provider base URL and supplied MCP URL. Paths passed inside the toolkit use `/dataset/chi-bench/...` and `/runner/...`; they are not Windows host paths. Use `--key-env` to name a locally configured provider variable. Native judge/simulator credentials remain separate inputs to the official environment.

The plan includes both the external agent import and χ-Bench's custom Docker environment class. The adapter packages this code into the trial container; the controller mount alone does not make host files available inside a child container. Private state/receipts and actor artifacts have separate locations. This bridge is covered by offline command/configuration tests; an actual Docker/Harbor/scored trial has not been executed.

## Main code locations

| File | Responsibility |
| --- | --- |
| `health_harness/models.py`, `store.py` | Scope, limits, transactional case state, leases/fences and action journal. |
| `health_harness/roles.py`, `data/micro_roles.json` | Packaged general responsibility groups and immutable patient-independent definitions. |
| `health_harness/engine.py` | Owner loop, local obligations, source-linked observations, helpers and completion/failure states. |
| `health_harness/context.py` | Deterministic bounded context projection and evidence pointers. |
| `health_harness/providers.py` | Stateless compatible API requests, tool aliases and reported usage. |
| `health_harness/schema.py`, `tools.py` | Argument/known-identity gates, MCP transport, tool routing and confined file operations. |
| `health_harness/cli.py`, `__main__.py` | Offline default and explicit configured execution. |
| `health_harness/chi_bench.py` | Optional direct Harbor adapter for the pinned integration contract; actual official execution remains untested. |

## Scope of the first version

This is a benchmark-oriented implementation, not a clinical deployment or a proven improvement in task completion. Local evidence-linked completion is distinct from official benchmark success. No live model-driven trial or score is established by the offline tests.

Patient/case identifiers are explicit inputs. Fully automatic entity discovery and safe binding of newly created case/resource IDs are not implied by the initial package. The current tool/schema/known-identity checks complement the supplied environment's access controls; they cannot authenticate every arbitrary note or opaque resource identifier.

Unknown outcomes of effects require reconciliation with the actual environment. The package does not silently replay a possible submission/message/update. A context bound must stop unresolved work explicitly if the required context cannot fit. General role definitions can be reused; patient-derived behavior, summaries and history are not shared across cases.
