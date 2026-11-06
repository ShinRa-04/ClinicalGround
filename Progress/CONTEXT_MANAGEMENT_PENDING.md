# Context management: pending; hard cap temporarily disabled

October24,2026. The user explicitly requested recording this unfinished work,
removing the assistant-set working-context limit for now, and a command to
rerun only UM t033. This change is an interim configuration capability, not a
claim that context management has been solved.

## What changed now

`--max-context-chars 0` means no harness working-context character cap. It is
now the default in the core limits/store and real standalone/batch entrypoints.
The projector interprets zero as unbounded rather than an empty allowance.
Existing deterministic working-set/history projection still operates, but it
cannot return exhausted merely because a preserved newest turn exceeds180k
characters. Bootstrap comparisons/investigation also recognize zero. Positive
caps still work when explicitly selected. Calls/tools/output budgets remain
positive and enforced; zero does not disable them.

Continuation comparisons understand that zero context is unbounded: changing
a finite context budget to zero is an increase, while imposing a finite budget
on a previously unbounded continuation is a reduction. Existing frozen failed
trials are preserved; the user rerun uses a fresh directory.

**Still present:** the adapter's2MiB serialized-input guard, transport bounds,
document/file limits, timeout and upstream model/service limits. Disabling the
working-context cap does not provide literally unlimited model capacity or
remove these separate limits. Larger requests may consume more tokens/time.

## Actual failure and verification

The Oct24 t033 attempt stopped before call4 after a large explicit policy read.
Our character-size replay uses an inert schema placeholder with the same58733
character cost recorded for the last tool set; it is not a model invocation or
a semantic replay of the tool definitions. The preserved context requires202671
characters:112826 prefix/schema plus89845 newest-turn contribution. The finite
180000 setting returns no projection; zero successfully projects that same
state. Receipt:
`runs/20261024-um-t033-context-inspection/disabled-cap-replay.json`.

Tests cover large explicit reads under finite versus disabled caps, continued
identity investigation with zero, negative/boolean rejection, independent call
limits and finite/unbounded continuation ordering. No actor or paid judge was
launched. No memory/evidence was deleted to force a test to pass.

## Work that still needs to be done

- Make oversized new tool groups fit an explicitly chosen working budget using
  source references and bounded original passages; retain complete evidence in
  case-local storage. Current explicit file/PDF reads bypass normal shortening.
- Preserve qualifications, exclusions, source IDs, hashes and continuation
  markers. An unseen part of a policy must remain explicitly unseen, not be
  presented as having been reasoned over or silently summarized into certainty.
- Budget instructions, tool schemas, source views and recent history together;
  diagnose their separate costs before stopping or requesting another model call.
- Reduce repeated tool-schema and reference material; measure actual actor token
  counts and latency rather than claiming that caching alone reduces context.
- Test real large-file/PDF batches and multiple domains with complete snapshot
  integrity and native outcome checks. Keep patient contexts isolated and do not
  replace this with a task-specific answer or forced workflow sequence.
- Revisit the default only with an explicit, documented configuration decision;
  do not silently restore the old180k stop while these issues remain unresolved.

Next user-run folder: `runs/20261024-random-um-t033-02`. Select only
`pa_t033_t033_o001_p01_triage_payer`, domain pa_um, concurrency1. The old run
remains separate and exhausted. No complete benchmark score or successful new
execution is claimed by this cap change.

Final full software suite: **527 passed /50.628s**,
`runs/20261024-context-cap-final-tests.log`. This validates the disabled-cap
configuration and existing checks, not a new dataset outcome.
