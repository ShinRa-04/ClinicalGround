# UM t033 -06: active-generation timeout

October 24 inspection of the user-run attempt. No code changes, actor rerun,
paid judge or hidden fixture inspection occurred.

- Actor ended with `error`: request22 timed out at180.046 seconds in
  `awaiting_turn`, category `transport:timeout`, phase `transport_read`.
- This was not a JSON parse, context-character,2MiB-input or ownership-fence
  failure. Native process cleanup confirmed; snapshot213 files saved, world
  stopped. Batch is `deferred_ready` with local_status `error`, grading pending.
  That status means evidence ready for later evaluation, not completed healthcare.
- The native stream was active:28536 assistant updates, last native idle0.046s,
  last event assistant_progress. Thus this was not demonstrated silent model
  unresponsiveness. It failed to deliver a finished reply by our180-second
  deadline. Update counts are neither token nor character counts. No partial
  response text is preserved, so an output loop or the exact reason remains
  unconfirmed. The failed request reports no token usage.
- Twenty-one earlier calls completed,64 tool proposals were counted and
  1278946 reported tokens accumulated (excludes unreported failed-call usage).
- Some repeated review reads occurred, but the investigation was not wholly
  identical:6 distinct hybrid queries,7 distinct file-read requests,6 distinct
  PDF-read requests;5 nurse-review reads had3 distinct result hashes. Two last
  review repeats are recorded; no progress-recovery nudge was triggered.
- Triage route/disposition were executed. No nurse criteria save is journaled.
  The latest public plan was correcting a policy checkpoint that incorrectly
  cited a workspace observation as actor-case evidence; earlier nurse writes
  were not dispatched. The model said it would continue after correction.
- Helper composition was enabled. Actual request declarations are inspected
  separately to distinguish availability from selection; no helper job was used.

Ignored evidence: `HealthHarnessCodex/runs/20261024-random-um-t033-06/`;
attempt events, live SQLite, result, deferred snapshot and batch manifest.
No complete official score was produced or claimed. Do not label this run a
successful benchmark execution or automatically replay actions from its snapshot.

Next diagnosis should distinguish prolonged/overlong assistant generation from
ordinary latency using safe bounded streaming metrics. Do not simply increase
the deadline or call the remote cause confirmed without evidence. Policy-source
rejections and absent helper selection are separate workflow investigations.
