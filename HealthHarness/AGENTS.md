# Implementation entrypoint

Read `../Progress/HANDOFF.md` and `../Progress/HEALTH_HARNESS_IMPLEMENTATION.md` before resuming. `README.md` contains runnable commands; `VERIFICATION.md` separates executed checks from untested live integration. The broader proposal remains in `../HealthHarnessBlueprint/`.

Keep patient-derived messages, observations, summaries, artifacts, caches and budgets within their full execution scope. General role definitions remain read-only. Do not add cross-patient learning, invented counterpart replies or a second clinical-world simulator.

Preserve transactional fencing, stable action IDs, pending/unknown effect handling and explicit failure states. A local completion claim is not official benchmark success. Do not turn conservative errors into silent retries.

Use synthetic tests by default. Do not read fixtures, expectations, solutions or protected handbook contents as development shortcuts. No secrets/payloads/logs in tracked files; use ignored `runs/` and `*.local.json`. Live provider calls, Docker trials and submissions require their own explicit invocation and accurate execution receipts.
