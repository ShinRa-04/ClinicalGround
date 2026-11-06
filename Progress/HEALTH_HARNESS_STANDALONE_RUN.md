# Executed standalone dataset attempt — October 19, 2026

Historical first attempts. [Later execution follow-through](HEALTH_HARNESS_EXECUTION_FOLLOWTHROUGH.md) fixes the identity defect, records actual local completion and stricter audits, and corrects the assumption that a stopped container retains its clinical world across entrypoint restart. Do not treat this earlier blocked result as the current code state.

## Outcome

The Codex-backed harness actually ran against one real public UM task using GPT-6 Luna/high and the existing native account sign-in. The second attempt reached payer routing; the actor determination readback reported `case_status=approved` and `workflow_stage=determination`, `stage_detail=finalized`, `outcome=approved`, `action_owner=none`.

The local harness result is **blocked**, not complete. Routing returned an explicit patient ID after initial actor views had exposed only the case ID. That new identity differed from the internal `case-subject:` namespace, so the existing response guard quarantined the response and stopped. No routing replay was attempted. The recorded final state is an actor observation, not independent clinical validation or an official benchmark success. No judge, simulator inference or submission was invoked; no score exists.

## Executed attempts

| Attempt | Model calls | Engine tool operations | External/workspace returns | Native reported tokens | Elapsed | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 3 | 12 | 6 | 117,007 | 31.359 s | Incomplete; adapter wording was interpreted as prohibiting effects |
| 2 | 6 | 31 | 13 | 301,722 | 57.766 s | Blocked on newly exposed patient identity after routing; final actor readback approved |

Engine operations include local obligation/evidence operations. Proxy dispatch counters cover external/workspace calls only. Returned calls do not establish clinical success; attempt 2 has 12 successful evidence records and one quarantined failure. Both attempts recorded zero unknown journal actions. The actor's `check_gold_card`, `calculate_sla`, `get_nurse_review_data`, `set_disposition` and `route_case` tools were used in attempt 2. Tool execution and readback are verified; no claim is made that all policy analysis or clinical decisions were correct.

Attempt 1 used reads only and left the public case in intake/triage with no determination or MD decision. A conflicting provider instruction, “never call them or perform their effects,” was clarified to explicitly permit JSON proposals for reads and authorized mutations while retaining the prohibition on native execution. Attempt 2 started in a fresh local run directory. Its initial observed actor-payload fingerprint matches attempt 1; task/model/effort/budgets/general instruction hash/composition match, while the source fingerprint differs. This is an exploratory debugging comparison, not a controlled quality study or a full hidden-world reset audit.

The first report's original substring classifier incorrectly treated “scoped completion” as a scope rejection. The classifier and regression test were corrected. Original attempt 1 artifacts are preserved, with a separate `evaluation.review.json` correcting its operational classification to incomplete workflow. Attempt 2's schema/scope classification is an actual guard rejection.

## Reproducibility and local artifacts

- Public task: `pa_t012_t012_o001_p01_triage_payer`. It requires the full assigned work through final determination, not routing alone.
- Container: `bigdata-health-codex-um-20261019-first`, ID `1582436d0d52dc5ee0b5a991ad3263e974c4f1b75b22efa7b213728cb98da1c7`.
- Runtime image: `sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66` (`bigdata-chi-bench:runtime-4444a07`). Network `none`, no published ports, no provider keys passed.
- The owned container was stopped and retained after execution. Do not replay its effects. Its world is changed by attempt 2.
- Ignored artifact root: `HealthHarnessCodex/runs/20261019-um-triage-first/`, including `attempt-1/`, `attempt-2/`, `comparison.json`, bootstrap records and mounted `container_logs/`.
- Each attempt has `events.jsonl`, `run.live.md`, `state.sqlite`, `run.result.json`, `evaluation.json` and `result.private.json`. Source/instruction fingerprints and actual native reported usage are retained there. Clinical/tool bodies and handbook content must remain ignored.
- Python 3.12.14; native Codex executable/version and unchanged approved global instruction hash are recorded in [connection handoff](HEALTH_HARNESS_CODEX.md). No raw auth files were read or copied.

The actual run used the standalone command in [README](../HealthHarnessCodex/README.md), the public task above, actor-observed case ID from the private bootstrap receipt, `--allow-case-subject-namespace`, and `--codex-instruction-source C:/Users/prath/.codex/AGENTS.md`. Defaults: 12 model calls, 50 engine tool operations, 180,000 context characters, 180 s per model call. The native output-token setting remains advisory.

## Implemented and tested

Docker MCP transport, restricted case filesystem, explicit queue case selection, strict default patient binding, opt-in internal case-subject namespace, namespace-to-remote-patient-argument prohibition, same-case review identity verification, run recording, operational comparison and safe live summaries are implemented. No hidden fixtures, expectations, solutions or verifier content were read. Protected handbook reads occurred through the acting harness's approved reference tool as part of the public task.

Root independently ran **91 software tests: all passed**. Tests cover transport/session handling, actual fixed-program filesystem boundaries, strict/optional identity setup, cross-case rejection, exception recording, native proposal contract and evaluation classification/comparability. All 33 original HealthHarness files remain hash-identical to FORK_BASELINE.json. These tests do not prove clinical quality or benchmark performance.

After the actual attempts, a final tested guard was added to reject reuse of a directory containing prior attempt artifacts before any actor/model call. The executed source fingerprints in each report describe their respective code at startup; the final committed tree additionally contains this guard. No further inference was run merely to verify directory rejection.

## Next improvement

Resolve late patient identity explicitly before treating this configuration as a complete workflow harness. Prefer acquiring a case-bound identity through an actor-visible read before mutations, where available. Otherwise design and test a provenance-bound distinction between immutable internal case namespace and later observed patient identity, including contradictory identities, nested responses, journal recovery and cross-case rejection. Do not simply accept any patient ID in a response, change the scope silently, disable the guard, or repeat the already executed route action.

The reusable [evaluation guide](../HealthHarnessCodex/EVALUATION.md) is implemented and exercised by these two attempts. It measures operational behavior and failure modes. Official quality evaluation, repeated fresh-world studies, reliable final completion across domains, clinical validity, separate simulator credentials and Harbor integration remain unverified or unimplemented.
