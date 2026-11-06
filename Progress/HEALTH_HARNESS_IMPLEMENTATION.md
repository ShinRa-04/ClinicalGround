# Healthcare harness implementation

## Scope and authorization

October 18, 2026: user requested code writing using GPT-6 Luna with high reasoning and a new root folder. Root `HealthHarness/` is the implementation; `HealthHarnessBlueprint/` remains the published design. Prior request to commit changes remains applicable. No push or submission is authorized.

Implement an independent composable PA/UM/CM work organization over supplied χ-Bench observations, with patient-scoped memory, tools, bounded inference and recovery. No separate clinical-world simulator, invented counterparty, automatic patient-derived cross-patient learning or claim of legal/clinical certification.

## Ownership and implemented work

- GPT-6 Luna high `core_implementation` wrote the core/runtime/tool/CLI/package code; `implementation_finish` completed adapter/launcher/isolation/recovery corrections after continuation. Root reviewed/integrated, inspected public interfaces, added localhost HTTP validation, documented evidence and committed. No high-cost review agents were spawned. Additional initial Luna dispatches hit a team-slot limit and did not run.
- Shared code interfaces and deliverable boundaries: [implementation contract](../HealthHarness/IMPLEMENTATION_CONTRACT.md).
- [Pinned source/task mapping](../HealthHarness/CHI_BENCH_MAPPING.md) inspected all 75 public instruction files for stage/rules and static actor registration (PA 30, UM default agent profile 41, CM 16 names). No fixtures, expectations or protected handbook content were read for this mapping.
- The pinned runner uses Harbor BaseInstalledAgent, and does not dispatch an arbitrary external import path merely from submission.agent. Use an external Harbor import path for the separate package; convenience runner integration remains distinct work.
- Implemented: PA/UM/CM combined owner; optional sequential bounded read-only role analyses; packaged 66 responsibility contracts; source-linked observations and obligation/closure records; full-scope SQLite state, optimistic versions and transactional lease fencing; stable action journal with unknown-effect blocking; deterministic context projection and evidence rehydration; stateless configurable Chat Completions adapter; MCP JSON/SSE/session transport; scope-bound tool clients and confined artifacts; offline-default CLI; optional Harbor packaging adapter and planned-by-default direct-trial launcher.
- Runner/toolkit.ps1 only gains a conditional read-only mount for the sibling implementation folder. The official source checkout, dataset, protected handbook, research catalogues and previous Docker assets remain unchanged. Docker was not started.
- Start at [HealthHarness/README.md](../HealthHarness/README.md). [Architecture](../HealthHarness/ARCHITECTURE.md), [verification](../HealthHarness/VERIFICATION.md) and [example configuration](../HealthHarness/config.example.json) document supported behavior and actual limits.

## Verification/status boundaries

The first working software version is implemented and offline-tested. Final root checks on October 19 IST: **43 tests passed** using bundled Python **3.12.14**, plus compileall, three-domain module/demo CLI, launcher help, pure-Python wheel build, isolated wheel import/packaged-role/demo checks and Runner PowerShell parse. The same suite's author/reviewer reruns are not additional unique tests. The localhost protocol tests use synthetic model/MCP responses only.

Important review fixes were implemented and tested: transactional mutation fencing; unsupported-schema branches; stable action IDs across helper calls; observed identity quarantine before inference; whole-group context reduction; known-failed evidence rejected for closure; bound workspace/MCP reassignment rejected; concurrent same-instance runs rejected; state reloaded after lease acquisition; interrupted completed effects recovered without replay; transient model failures resumable with retained budgets; controller import path and pinned Docker environment routing; bounded source upload and command failure propagation. Details/test scope: VERIFICATION.md.

Final wheel after EOF whitespace cleanup: HealthHarness/dist/health_harness-0.1.0-py3-none-any.whl, 44,807 bytes, SHA-256 `5cf8987a48253252055876c2fee3b91a1a66b925d9b0a03a224d0277c9565008`; local ignored build artifact. Core has no runtime dependencies. No new host dependency/compiler installation.

No live provider/model request, Docker startup, benchmark trial, official judge run, public submission or non-benchmark clinical use has occurred. Credentials are not read or printed. Runtime model/provider choice remains explicit local configuration; coding-agent model selection does not select the eventual benchmark model.

## Commands and next steps

From HealthHarness/: `python -m health_harness --demo`; `python -m unittest discover -s tests -v`. Use the bundled Python path in README.md on this machine. Runtime config is an ignored local JSON file; live invocations require explicit --live. The optional direct Harbor launcher requires --execute; default is a command plan. Do not invoke trials merely to recheck code publication.

Before an actual benchmark trial: obtain the permitted actual patient/case scope without fixture shortcuts, choose runtime model/endpoint and local provider/judge credentials, validate the live tool/schema set and actor-specific file paths, and test the adapter against installed Harbor via the existing toolkit. Automatic creation/discovery/binding of new PA/CM case IDs is not implemented. Unknown effects require real environment reconciliation; there is no generic safe reset/retry shortcut. Actual benchmark performance, clinical validity, provider retention, broad multi-tenant security and optimal role composition are unverified.

Implementation deliverable is ready for local use and review; live integration/benchmark work remains a separate execution stage. Keep receipts/payloads local, preserve user constraints, and commit tracked source/tests/docs only. No push or submission.

## October 19 fresh operator check

At the user's request, spawned GPT-6 Luna high with no inherited conversation (`fork_turns=none`), excluded earlier project research/handoff/memory, and gave it the delivered package plus task/dataset locations. It independently reran the 43-test suite, three-domain scripted demo and launcher help. It confirmed the shipped package has no connection to its in-session Luna inference; no actual dataset case or official score was produced. [Full evaluation record](../HealthHarness/evaluations/FRESH_OPERATOR_EVALUATION.md) separates operator usability, a Codex solver outside our loop, and a genuine adapter-driven harness trial.

Official OpenAI documentation supports account-sign-in/no-separate-key integration options in principle; no such adapter, account entitlement or exact model access was implemented/verified here. The official simulator/judge have separate prerequisites. No credentials were extracted/read. A PATH `codex` collision with an unrelated Python comic application generated settings before failing; automatic deletion was blocked and the generated directory was preserved in ignored Runner/.cache/codex-name-collision-20261019/. No source change or Docker/service startup during evaluation.
