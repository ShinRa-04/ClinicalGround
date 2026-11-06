# UM t033: model timeout masked by expired case ownership

## Observed failure

`runs/20261023-random-um-t033-01` stopped on model call6. The first five calls
finished. Recorded latency for the sixth was180.047 seconds, matching the
configured180-second model timeout. It emitted ProviderError. The engine renews
its case claim before each request with a120-second lifetime, so by the time
the provider failure was being saved that claim had expired.

`CaseStore.save_case` correctly requires a live owner/fencing token. The attempt
to save the model failure therefore raised ConflictError, masking the provider
timeout. The fallback runtime result did not retain durable model/tool counters,
so result.private.json misleadingly reported0 total observed model calls. Saved
SQLite state and events establish6 started calls,5 successful replies,28 counted
tool proposals and361140 reported tokens before the failed request.

This is an orchestration/timeout-lease mismatch, not evidence that the medical
model chose an incorrect endpoint. No quota/clinical-reasoning diagnosis should
be inferred from this error. The original request exceeded its deadline; its
missing stage telemetry does not identify whether startup, transport or remote
inference caused the delay. The secondary ConflictError is a harness defect.

## Native diagnostic before judging task success

The integrity-verified frozen snapshot was copied into a separate key-free,
network-none native-verifier diagnostic. It produced diagnostic reward0,
3 passing and9 failing structural/applicable checks. Required triage, nurse/MD
review and outcome records were not completed. Semantic judge checks were not
evaluated; the grade helper correctly classifies the result **ungraded** because
the judge is unavailable. Do not advertise this as a complete official score.
The structural failures nevertheless establish that this is not another t021
case where a valid recorded endpoint merely received a misleading local label.

Original snapshot integrity verified again; no actor replay, credentials or
paid judge calls. Diagnostic container removed. Local-only evidence:
`runs/20261023-um-t033-native-diagnostic/`.

## Implemented correction

- `CaseStore.renew` extends only the existing live owner and exact fence. It
  cannot revive expired ownership, steal another lease or change the fence.
- A context-managed heartbeat maintains that claim throughout main/helper
  model waits. It stops and joins before the result is processed. Ownership is
  rechecked before a successful result can be used. The model's180-second
  timeout itself is unchanged.
- If a model result arrives after ownership changed, it cannot be dispatched
  under the old fence. The system does not silently reacquire ownership.
- Standalone runtime-exception reporting reads durable counters, usage, evidence
  and bindings without an unfenced mutation. A genuine runtime failure remains
  a failure, but already executed work no longer disappears from reporting.

This prevents the lease expiry from obscuring a slow provider failure; it does
not guarantee that the model service will answer within180 seconds. No automatic
clinical replay or new task run was added.

## Verification

Focused engine suite45 tests passed/4.495s, including a real delayed synthetic
provider failure lasting longer than a deliberately shortened lease. It retained
the ProviderError and correct counters instead of raising ConflictError.
Focused standalone suite33 tests passed/1.434s, including durable-counter
recovery after a forced runtime exception. Store tests cover renewal beyond the
original expiry, exclusion of another owner, rejecting stale/expired fences and
ownership changes during the wait.

The first full test run found a new test missing its explicit synthetic domain;
the test was corrected rather than changing domain validation. These are
software checks, not a fresh UM benchmark result. The original failed run is
preserved and must not be resumed under changed source.

Final full suite: **519 passed /61.705s**,
`runs/20261023-lease-fix-final-tests.log`. No fresh actor or paid judge was
launched. Why the remote model failed to return inside180 seconds remains
unverified; renewing ownership prevents the secondary error, not the original
service timeout.
