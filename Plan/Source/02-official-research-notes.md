# Official source research notes

Checked October 13, 2026 to support approach ideation. This is a research receipt, not another user-supplied guide. No dataset/handbook downloads, installation, paid runs, or private material access occurred.

## Sources inspected

| Source | What it supports |
| --- | --- |
| [Official repository README](https://github.com/actava-ai/chi-bench) | Harness choices, trial setup, release pinning, public workflows, current data repair instructions, submission lifecycle |
| [χ-Bench paper v1](https://arxiv.org/html/2605.16679v1) | Reported experiments and failure analysis; results describe those tested configurations, not our results or today's best possible score |
| [Agent-facing task explorer](https://www.actava.ai/benchmarks/tasks) | Public task structure and three-domain coverage |
| [Extension guide](https://github.com/actava-ai/chi-bench/blob/main/docs/extending.md) | Integration of custom models and custom agent loops |
| [Architecture guide](https://github.com/actava-ai/chi-bench/blob/main/docs/architecture.md) | Per-trial containers, domain services, workflow branches |
| [Scorecard guide](https://www.actava.ai/benchmarks/docs/scorecard) | Strict binary scoring and post-run diagnosis |
| [Experiment guide](https://www.actava.ai/benchmarks/docs/run) | Experiment/submission operations |
| [Packet contract](https://github.com/actava-ai/chi-bench/blob/main/docs/submission-packet.md) | Evidence packet structure; aggregate CSV differs from Kaggle task CSV |
| [Public dataset card](https://huggingface.co/datasets/actava/chi-bench/blob/main/README.md) | Public dataset reference inspected; task fixtures were not downloaded |
| [Kaggle overview](https://www.kaggle.com/competitions/chi-bench/overview) | Search-indexed overview corroborates several supplied details, but direct page text was unavailable |

## Observations relevant to strategy

- The paper's reported best overall pass@1 is 28.0%, with no tested configuration above 20% strict pass^3. Its analysis separates reasoning errors, incomplete workflows, policy errors, stuck runs, and dialog/consent issues. Its handbook ablation shows domain-dependent effects, so more retrieved context should not be assumed better. [Paper](https://arxiv.org/html/2605.16679v1)
- One required failed check makes binary reward zero. Use fractional completion only to diagnose failures. Post-run scorecards provide debugging information; hidden task expectations and verifier-only inputs are not acting-agent inputs. [Scorecard guide](https://www.actava.ai/benchmarks/docs/scorecard)
- The official repository allows custom harnesses/models. Its runtime architecture uses fresh trial containers. [Extension guide](https://github.com/actava-ai/chi-bench/blob/main/docs/extending.md), [architecture](https://github.com/actava-ai/chi-bench/blob/main/docs/architecture.md)

## Setup changes and verification limits

The current README includes a pa_t035 local fixture repair and regenerated payer request forms before Docker build, absent from the pasted overview. It distinguishes runtime 1.1.0 from dataset revision chi-bench-v1.0.0. Confirm organizer-approved competition setup before running; no repairs have been applied here. [README](https://github.com/actava-ai/chi-bench)

The general benchmark leaderboard permits partial domain submissions; the supplied competition requirements concern a complete final entry and 75-task public results. Follow competition-specific requirements when preparing an entry.

Direct Kaggle Rules and overview fetches returned no readable page text. Search-indexed overview text also contains a conflicting 2027 header alongside the 2026 body. The full Rules, dates, definitive package/report deadline, and multi-model details have not been verified; do not infer them from the general benchmark's capabilities. Supplied deadlines remain the planning reference pending confirmation.

The gated handbook was not accessed; its contents and retrieval quality have not been inspected. No live model endpoint availability, actual cost, or model/harness performance was tested. Claims in APPROACH_IDEAS.md about expected benefits are hypotheses to evaluate.
