# Source ledger and interpretation limits

Eleven primary-source entries read during this study/clarification. These establish background and scoped rules, not validation of our proposed software architecture. The prior 97-role evidence audit remains a separate baseline. No source is interpreted as proving that every profession needs an agent.

<a id="s01"></a>
## S01 — Anthropic: Building effective agents

[Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

**Edition:** December 19, 2024; live page warns tooling has changed

**Checked:** 2026-10-18; Primary engineering article opened through web tool

**Locator:** What are agents; When and when not; Routing; Orchestrator-workers; Evaluator-optimizer

**Finding:** Distinguishes fixed workflows from model-directed loops and describes composable patterns. Supports comparing simpler mechanisms before adding coordination.

**Limit:** Practitioner guidance, not controlled evidence that any architecture wins chi-Bench. Historical tooling examples are not current integration instructions.

<a id="s02"></a>
## S02 — Anthropic: How we built our multi-agent research system

[Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

**Edition:** Engineering account, June 2025

**Checked:** 2026-10-18; Primary engineering article opened; architecture, costs and evaluation sections inspected

**Locator:** Why multi-agent systems; Architecture overview; Effective evaluation; Production reliability

**Finding:** Describes a research system using parallel workers and explicit task boundaries; reports benefits for breadth-first work alongside substantial resource and coordination costs.

**Limit:** Vendor-reported research-system results. Its reported token multipliers and performance gains are not estimates for this project or a universal multi-agent tax.

<a id="s03"></a>
## S03 — Towards a Science of Scaling Agent Systems

[Towards a Science of Scaling Agent Systems](https://arxiv.org/html/2512.08296v3)

**Edition:** arXiv v3, April 8, 2026

**Checked:** 2026-10-18; Abstract, full HTML introduction/setup and limitations/robustness passages inspected

**Locator:** Sections 3, 4.1, 4.5 and 5

**Finding:** Compares coordination architectures under controlled configurations across six agentic benchmarks; reports task-dependent outcomes and coordination overhead.

**Limit:** No chi-Bench evaluation. Strong cross-domain prediction is limited; some comparisons use small subsets, and limitations discuss prompt sensitivity and exploratory agent-count scaling. No universal worker-count threshold is imported here.

<a id="s04"></a>
## S04 — Why Do Multi-Agent LLM Systems Fail?

[Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/html/2503.13657v3)

**Edition:** arXiv v3, October 26, 2025

**Checked:** 2026-10-18; Abstract and full HTML methodology/taxonomy passages inspected

**Locator:** Sections 3.1–3.3, 4 and 5

**Finding:** MAST organizes observed failures around system design, inter-agent misalignment and task verification. Useful as a diagnostic vocabulary for proposed stress cases.

**Limit:** The initial qualitative sampling focused on programming/math frameworks; broader traces and model-based annotation are not a healthcare validation study. Our scenario labels are adaptations, not reproduced MAST measurements.

<a id="s05"></a>
## S05 — AHRQ TeamSTEPPS: Handoff

[AHRQ TeamSTEPPS: Handoff](https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/handoff.html)

**Edition:** Last reviewed May 2023

**Checked:** 2026-10-18; Primary guidance opened and handoff components inspected

**Locator:** Definition; How To Use a Handoff Effectively

**Finding:** Discusses responsibility/accountability transfer, appropriate information, receiver acknowledgement and an opportunity for questions during care handoffs.

**Limit:** Healthcare training guidance, not a mandatory universal software protocol. Its translation into worker-message fields is our proposed design, not proof of an AI performance gain.

<a id="s06"></a>
## S06 — Actava: Bring your own agent

[Actava: Bring your own agent](https://www.actava.ai/benchmarks/docs/extending)

**Edition:** Live page checked October 18, 2026

**Checked:** 2026-10-18; Official public page opened; harness contract and authoritative-doc links inspected

**Locator:** What an agent harness needs to provide; Wiring a new harness

**Finding:** Describes task instructions, role-scoped tools and trajectory-producing custom-agent integration.

**Limit:** Its AgentHarness description differs from the tested pinned checkout’s Harbor BaseInstalledAgent interface. Do not mix APIs or treat the live prose as proof of compatibility with local commit 4444a07.

<a id="s07"></a>
## S07 — 42 CFR 422.590: MA reconsideration responsibility

[42 CFR 422.590: MA reconsideration responsibility](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-422/subpart-M/section-422.590)

**Edition:** Page displayed Title 42 through October 15, 2026

**Checked:** 2026-10-18; Primary eCFR page opened; subsection (h) directly inspected

**Locator:** 422.590(h)(1)–(2)

**Finding:** The specified reconsideration uses persons uninvolved in the initial determination; medical-necessity denial reconsideration has an appropriate physician-expertise requirement.

**Limit:** Specified MA route and issue, not a blanket rule for every payer. Human qualifications and involvement are not established by changing a model prompt or opening a fresh context.

<a id="s08"></a>
## S08 — HHS: Minimum Necessary Requirement

[HHS: Minimum Necessary Requirement](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html)

**Edition:** Guidance revised 2003; page reviewed July 2013

**Checked:** 2026-10-18; Primary HHS guidance opened; exceptions and workforce-access paragraphs inspected

**Locator:** How the Rule Works; Uses and Disclosures; persons/classes/categories/conditions paragraph

**Finding:** Describes purpose-sensitive information access and exceptions, including specified provider treatment disclosures/requests.

**Limit:** Not a complete present privacy-law review. Applicable Part 2 and other restrictions remain in the earlier audit. A scoped software-view proposal is an engineering inference, not a legal conclusion for every exchange.

<a id="s09"></a>
## S09 — Pinned official chi-Bench integration and architecture documentation

[Pinned official chi-Bench integration and architecture documentation](https://github.com/actava-ai/chi-bench/tree/4444a07fa68a4f1623f841a292a54e284fc8e7f7/docs)

**Edition:** Local official checkout commit 4444a07fa68a4f1623f841a292a54e284fc8e7f7

**Checked:** 2026-10-18; Read docs/extending.md and docs/architecture.md only; no hidden verifier or task fixtures inspected

**Locator:** extending §2 New agent harness; architecture Components and Trial lifecycle

**Finding:** Pinned integration uses Harbor BaseInstalledAgent; architecture distinguishes harness, services, conversation and grading. It documents an administrative failed-eligibility intake terminal route without clinical review.

**Limit:** Documentation describes that pin; this study did not execute a trial or prove every code path. Live integration prose differs. Runtime tool contracts and all public task instructions still need focused mapping before implementation.

<a id="s10"></a>
## S10 — AHRQ TeamSTEPPS: Closed-Loop Communication

[AHRQ TeamSTEPPS: Closed-Loop Communication](https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/loop.html)

**Edition:** Last reviewed May 2023

**Checked:** 2026-10-18; Primary guidance opened and communication sequence inspected

**Locator:** Closed-loop definition and three-element illustration

**Finding:** Describes sender initiation, receiver feedback and sender confirmation of receipt/understanding.

**Limit:** Human communication guidance. Our proposed acknowledgements distinguish message receipt from substantive task completion and are not a universal legally mandated API.

<a id="s11"></a>
## S11 — CHI-Bench paper v3

[CHI-Bench paper v3](https://arxiv.org/abs/2605.16679v3)

**Edition:** September 30, 2026 revision

**Checked:** 2026-10-18; Primary abstract reopened during the benchmark/agent clarification

**Locator:** Abstract: policy density, multi-role composition, multilateral interaction and three workflow domains

**Finding:** Introduces a simulated healthcare-workflow benchmark and reports agent/harness-model evaluations. Multi-role work is part of the task, but separate autonomous workers for each role are not required by that description.

**Limit:** This is a benchmark description and reported evaluation, not evidence for our proposed organization or a claim that all 97 researched functions are represented in the tasks.

## Local provenance

The AHRQ communication overview was also extracted headlessly with shared Crawl4AI 0.9.5: HTTP 200, 37,901 Markdown characters. Its raw text/receipt remain local-only under ignored Runner/.cache/agent-organization/sources/. That extraction is not an additional independent source or factual validation.

S09 was inspected in the actual local official checkout at commit 4444a07fa68a4f1623f841a292a54e284fc8e7f7. No source fetch changed that checkout. Its interface and the live S06 description differ; AD14 records the unresolved compatibility issue. Full paper methods were not reproduced, no all-state/current-law re-audit occurred, and inherited healthcare ambiguities remain explicit.
