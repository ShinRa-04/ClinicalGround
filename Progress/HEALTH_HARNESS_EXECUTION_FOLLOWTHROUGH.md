# Proper execution follow-through — October 19, 2026

## Current execution

The late patient identity defect is fixed in HealthHarnessCodex. A new actual run (`attempt-3`) reached local completion: 18 Luna-high model calls, 77 engine tool operations, 216.235 seconds, no open obligations or unknown actions. Actor readback reports finalized/approved. It used the actor's `triage_auto_approve` path; its final claim explicitly says that no nurse, MD or P2P review occurred. The actor records an approval letter delivery and completeness audit, and a generated member notification. This is not an official benchmark score or proof of clinical correctness.

Because the task mentions clinical/MD work and the harness included required communications, local completion alone was not accepted as sufficient. Two explicit audit continuations ran on read-only SQLite backups in fresh ignored directories, with completed routing/disposition tools removed and blocked. The original results and journals remain untouched.

The audits supported bypass of manual clinical/MD/P2P review for this automatic approval path, but left `audit_member_notice_delivery` open. The actor's public `payer_letter_center.generate_notification` contract explicitly creates a Message record without sending/delivering it. `payer_letter_center.deliver` operates on provider-facing Letter records, not those member Messages. No member-message send operation is exposed by the supplied payer tools. The generated notification therefore must not be described as delivered. The scope audit retained this limitation rather than returning a false completion claim.

| Segment | Result | New model calls | Lifetime engine operations | Seconds | Native reported tokens this segment |
| --- | --- | ---: | ---: | ---: | ---: |
| attempt-3 | local complete | 18 | 77 | 216.235 | 1,435,581 |
| attempt-3-audit | unresolved member delivery | 10 | 125 | 130.609 | 793,416 |
| attempt-3-scope-audit | same capability limit | 2 | 126 | 26.984 | 142,174 |

All three segments recorded zero unknown journal actions. Reference/path errors remain in their evidence; this is not an error-free or independent benchmark success claim. Budgets and code changed during debugging, so no performance gain is inferred. Continuations preserve lifetime counters; per-segment observed model calls/usage and starting counts are separately recorded.

Independent final live readbacks confirmed `case_status=approved`, current workflow `determination/finalized`, `action_owner=none`, source `triage_auto_approve`, and an approval Letter with recorded API delivery. `final-execution-verification.json` records these observations separately from the still-unresolved broader communication audit. Official success/score remain null. A clarification is pending on whether the user's completion target is the available benchmark operations or the full handbook workflow including an unavailable send step. No audit obligation was forcibly closed.

## Implemented corrections and tested boundaries

- The immutable internal case-subject namespace remains the SQLite/workspace key. A separate patient binding can be adopted only from selected actor tools returning an object that binds that ID to the same case. Conflicting cases/patients and unrelated sibling IDs reject the entire response; workspace files cannot supply the binding. The evidence source is persisted and projected into the context ledger. Arguments/results use the observed patient ID without changing the namespace or rewriting raw evidence.
- Approved read-only reference directories can be listed, with a 1,000-name bound, blocked-file filtering, traversal/root checks and symlink non-leak. This fixes the reference-discovery failures observed during attempt 3. Broader task-asset directory listing remains forbidden; only the named public tool reference file is approved there.
- Explicit continuation archives the previous final/completion/status and counters, appends an audited new instruction and allows only explicitly non-reducing budgets. Plain resume cannot silently reopen a completed case. Unknown/pending writes and blocked cases cannot be bypassed.
- The continuation runner verifies task/container/scope/instruction hashes and a matching public case/determination/workflow signature before model input. It refuses a reset world. Source SQLite is copied through read-only backup; source files are hash-checked. Result/evaluation reports distinguish lifetime counters from model calls/usage observed during the new segment.
- Terminal observation now uses the current actor's explicit flags or finalized determination/workflow fields; nested historical flags cannot declare the current case terminal. This is an environment-state interpretation, not a judge result.

Root ran all **119 software tests successfully** after integrating these changes. Unit/integration checks cover trusted late binding, conflicting/unbound IDs, cross-case isolation, persistent recovery, approved reference discovery, continuation snapshots, world mismatch refusal and completed-route filtering. All 33 original HealthHarness files were independently rehashed and match FORK_BASELINE.json.

## Corrected runtime-lifecycle finding

The prior receipt assumed the stopped container retained its finalized clinical world. That was incorrect. After restarting, actor-visible get_intake_case and get_summary returned intake/triage with no determination, and nurse/MD views exposed no patient ID again. Therefore the entrypoint reset the task world on the observed restart. Attempt 3 started from this independently observed initial state in a new local directory; attempt 2's journal was not replayed against it.

Do not confuse a retained container/image/filesystem with a recoverable active actor world. Keep the runtime running while continuing a case and verify actual actor state before every continuation. Do not restart it to resolve a workflow problem.

## Artifacts and provenance

All private artifacts remain under ignored `HealthHarnessCodex/runs/20261019-um-triage-first/`: previous attempts, `attempt-3/`, the explicit audit note, public readback receipts and `attempt-3-audit/`. Neither protected reference contents nor patient/tool bodies belong in Git. Each segment records the source tree fingerprint at startup; fixes implemented during execution are separately tested and may have a later fingerprint. Prior exploratory failures remain preserved rather than relabeled as successes.

No simulator/judge inference, official grade, public submission, external provider API key, host compiler installation, WSL migration or unrelated service startup is part of this execution.
