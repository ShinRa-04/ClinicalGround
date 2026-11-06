# Background study source receipts

Checked October 15, 2026 for the user's requested due diligence before agent creation. Earlier October 13 ideation and v1 notes remain historical. Current learning entrypoint: [BACKGROUND_BRIEF.md](../BACKGROUND_BRIEF.md).

## Downloaded research paper

- Local file: [CHI-Bench_2605.16679v3.pdf](CHI-Bench_2605.16679v3.pdf).
- Download source: https://arxiv.org/pdf/2605.16679v3 (resolved to the same URL; no login required).
- Version: arXiv:2605.16679v3, September 30, 2026; confirmed both against the arXiv record and the first-page version label.
- Integrity: PDF signature confirmed; 10,382,153 bytes; all 66 pages parsed and yielded readable text.
- Identity: first page matches the paper title and Haolin Chen/author list. First and last pages rendered and visually inspected.
- SHA-256: ca03eb2e9dae45dfceedd75b76f92f35c476353b8070da80e624176f7403e119.
- Status: authoritative arXiv copy, including appendices; not independently verified as a final publisher/proceedings edition.

The background brief was rewritten after reader feedback to explain one continuous progression: healthcare work, the agent research problem, the simulated test environment, evaluation, reported evidence, and the competition's goal. Source metadata and unresolved details sit outside the main narrative.

## Primary sources and verification boundaries

| Source | Use / status |
| --- | --- |
| [arXiv record](https://arxiv.org/abs/2605.16679) | Verified version history: first submission May 15, 2026; latest v3 September 30, 2026 |
| [Paper v3](https://arxiv.org/html/2605.16679v3) | Reviewed main benchmark construction and experiments, plus relevant metrics/judge and validation sections; methodology is author-reported, not independently audited |
| [Repository](https://github.com/actava-ai/chi-bench) | Official runtime reference and headline experimental results; venue acceptance is a repository claim |
| [IEEE Cup](https://bigdataieee.org/BigData2026/cup/) | Independently confirms χ-Bench in the 2026 Cup program as Challenge 07 |
| [Actava overview](https://www.actava.ai/benchmarks) | Organizer framing and simulator background |
| [Dataset card](https://huggingface.co/datasets/actava/chi-bench) | Separation of fixtures/runtime/handbook; base, arena, and marathon task families; public fixtures under Apache-2.0 |
| [Handbook public card](https://huggingface.co/datasets/actava/managed-care-operations-handbook) | Manual access approval, non-commercial/no-redistribution terms, and public description; gated contents were not accessed |
| [Architecture](https://github.com/actava-ai/chi-bench/blob/main/docs/architecture.md) | Trial lifecycle and runtime responsibilities |
| [Scorecard](https://www.actava.ai/benchmarks/docs/scorecard) | Strict reward versus diagnostic partial completion |
| [AMA background](https://www.ama-assn.org/practice-management/prior-authorization/prior-authorization-research-reports) | Prior authorization's real-world purpose and reported burdens; no causal AI-benefit claim inferred |
| [CMS chronic-care background](https://www.cms.gov/medicare/payment/fee-schedules/physician-fee-schedule/chronic-care-management-complex-conditions) | Illustrative care-coordination background, not competition-specific policy |
| [τ-bench paper](https://arxiv.org/abs/2406.12045) | Earlier tool/user/policy interaction benchmark and reliability metric |
| [HealthAdminBench paper](https://arxiv.org/abs/2604.09937) | Related healthcare administrative benchmark using graphical interfaces |
| [Kaggle overview](https://www.kaggle.com/competitions/chi-bench/overview) | Read through search-indexed text; direct page fetch still returned no readable text |

## Open details retained for later diligence

- The publicly listed handbook contains approximately 1,279 Markdown pages plus 11 PDFs; the paper abstract says 1,290+ documents. No downloaded manifest was inspected, so release-level counts remain unverified.
- The repository reports NeurIPS acceptance, but a separate official acceptance/proceedings record was not established during this review. Do not describe the checked arXiv version as a verified final proceedings edition.
- Current indexed Kaggle text still has a 2027 header above a 2026 overview; IEEE's official page lists the 2026 challenge. The cause has not been established.
- Indexed Kaggle overview text now labels December 7 as finalist-materials due, while the earlier pasted source called it invited teams' camera-ready report due. Preserve both descriptions rather than silently treating them as identical. Final package/report timing and the complete Rules remain unresolved.
- General IEEE Cup material contains broader recommended report/timing guidance. That is not sufficient to override competition-specific requirements.
- Experimental results are literature results, not our reproduction or a live leaderboard ranking. Agent provider availability, current prices, runtime equivalence, and private evaluation construction were not tested.
- Public narrative examples in the paper are study material. No hidden task files, private evaluation materials, or scored-case solutions have been downloaded or added to agent inputs.

The diagrams and example in BACKGROUND_BRIEF.md are explanatory constructions. They are not executed trajectories. No architecture choice, handbook request, registration, repository clone, dependency installation, benchmark trial, API spend, or submission occurred.
