# IEEE Big Data Cup 2026 - χ-Bench Challenge

## Source and verification status
Source 1: user-supplied overview and attached competition description, received October 13, 2026. The original text is preserved in [01-competition-description.txt](01-competition-description.txt).

Repository supplied by the user: https://github.com/actava-ai/chi-bench

The information below summarizes the supplied material. Selected official benchmark sources were inspected on October 13, 2026; see [research notes](02-official-research-notes.md). A background review on October 15 uses paper v3 and records fresh primary sources in [background receipts](03-background-source-notes.md). Full competition Rules, definitive package/report timing, and model endpoint availability remain unverified. Additional messages may refine this summary.

The [research paper, arXiv v3](CHI-Bench_2605.16679v3.pdf) is downloaded locally in this folder. Its title, version label, PDF integrity, and all 66 text-readable pages were verified; the download receipt is in the background source notes.

## Objective
Build an autonomous agent for prior authorization, utilization management, and care management in χ-World, a simulator of U.S. healthcare operations. The agent must gather evidence, apply policy, use operational tools, communicate with simulated people, and complete workflows. Healthcare applications are exposed through MCP and REST tools; decisions are grounded in the gated, 1,279-document Managed-Care Operations Handbook.

## Tracks and datasets
- Provider Prior Authorization
- Payer Utilization Management
- Care Management

The public development set has 75 tasks, 25 per track. The private set consists of unreleased clinician-validated tasks, described as approximately 75 tasks. The public leaderboard is provisional because participants control their development environments. Complete, runnable, prize-eligible final entries receive organizer-run private evaluation.

## Evaluation and awards
Each task receives a strict binary reward: 1 only if every required non-N/A verifier check passes; otherwise 0. Partial check completion is diagnostic only. Verification combines deterministic workflow checks with rubric review of policy and clinical reasoning.

Public scoring uses pass@1 over all 75 tasks. The Kaggle CSV must contain exactly one binary reward per required task, with columns task_id,reward. A reward of 1 requires corresponding official verifier output of 1.

Private evaluation runs three independent attempts. Final ranking order:
1. Higher private pass@1.
2. Higher private pass^3.
3. Lower mean agent inference cost.
4. Fewer mean agent tool calls.

Supplied simulator/judge configuration:
- Care Management patient simulator: claude-sonnet-5, adaptive thinking disabled, maximum 1,024 output tokens.
- Peer-to-peer physician counterpart: claude-sonnet-5.
- Workspace judge: claude-opus-4-7, three independent votes per rubric.

Organizers may announce an immutable replacement snapshot before launch; the frozen configuration must remain consistent between teams.

Prize pool: USD 3,000 (Gold $1,500; Silver $1,000; Bronze $500), plus a Reliability Award for the best pass^3 score.

## Setup prerequisites and supplied workflow
Requirements: Python 3.12+, Docker, uv, approved Hugging Face access/token for the handbook, ANTHROPIC_API_KEY for the official workspace judge, and the chosen agent model's provider key.

Supplied workflow, not yet executed:
1. Join Kaggle and accept the Rules.
2. Request and obtain handbook access before running the benchmark.
3. Clone χ-Bench and install with uv sync --extra dev.
4. Download actava/chi-bench pinned to chi-bench-v1.0.0 into data/ and record data/.chi-bench-version.
5. Download the approved handbook into data/skills/.
6. Configure credentials locally using .env.example; never submit credentials.
7. Run uv run cb docker build and uv run cb data verify, then a Quickstart smoke test.
8. Configure configs/submissions/my-team.yaml from configs/submission_example.yaml with team, contact, agent, model, environment, and dataset version.
9. Use cb submission validate, run, status, and prepare with the configuration file.

The prepared evidence packet includes a manifest, per-domain results, verifier evidence, provenance, and compressed trajectories. Exact supplied commands are retained in the original source; shell syntax will need adaptation for Windows before execution.

Any model, harness, prompting strategy, hardware, cloud provider, or local environment may be used subject to the Rules and licenses. No approach has been selected.

## Final submission requirements
- Public task result CSV through Kaggle.
- Short Kaggle Writeup: team name, method summary, and model name.
- Runnable package and technical report (or download link) emailed to research@actava.ai, with subject starting [Kaggle] and including team name and Writeup link.
- Package: agent source, prompts, configuration, dependencies and lock files, exact model/API details, external tools/datasets, and run instructions; include available trial evidence and cost records. Proprietary third-party weights are not required.
- Report: IEEE two-column format, at most five pages excluding references. Disclose external models, tools, and datasets in both report and package.
- Exclude credentials and protected handbook content.

Participants pay development API costs; organizers pay private-evaluation API costs. No development credits are provided. No email or submission has been sent.

## Timeline from supplied description
All deadlines are 11:59 PM UTC unless otherwise announced.

| Event | Date |
| --- | --- |
| Cup data-release program began | June 1, 2026 |
| Kaggle competition opens | August 15, 2026 |
| Entry deadline | November 7, 2026 |
| Team-merger deadline | November 7, 2026 |
| Final Kaggle submission deadline | November 15, 2026 |
| Final results announced | November 23, 2026 |
| Invited teams' camera-ready report due | December 7, 2026 |
| IEEE Big Data 2026, Phoenix, Arizona, USA | December 14-17, 2026 |

The supplied text does not separately specify an email-package/report deadline; confirm it from the complete Rules.

## Rules and data constraints from supplied description
- Accept the full Kaggle Rules and obtain handbook approval before benchmark execution.
- Public dataset: stated Apache-2.0 license. Handbook: separately gated for non-commercial research, with redistribution prohibited.
- Never upload the handbook, protected excerpts, credentials, or private evaluation material to Kaggle or public repositories.
- Evaluated tasks must be autonomous: no human task-level intervention or manual verifier-result modification.
- Agents must not access hidden expectations, private solutions, or verifier-only files.
- χ-Bench is a research benchmark, not a medical device or medical-advice source.

## Resources and unresolved questions
The supplied description names Quickstart, run/submission documentation, task explorer, leaderboard, dataset, handbook-access page, evidence repository, conference page, and Kaggle Rules/Discussion, but does not provide their exact URLs. The cited paper is https://arxiv.org/abs/2605.16679; its supplied BibTeX is preserved in the original source.

The user now wants due diligence before any official agent creation. Begin with [BACKGROUND_BRIEF.md](../BACKGROUND_BRIEF.md); its later study sequence is proposed, not completed. Earlier proposals remain in [APPROACH_IDEAS.md](../APPROACH_IDEAS.md). Before implementation, resolve the full Rules and package/report deadline, participation/team details, handbook approval, budget, model/harness choice, and environment. No solution has been selected or implemented.
