# CM tool failure recovery — October 25

User resumed work after the previous stop and authorized diagnosis, repairs and
single-case execution. No paid judge or full-dataset run is authorized.

## Evidence before repair

- CM -02: `cm_outreach.send_message` returned MCP `isError=true`; the adapter
  discarded the response and raised a generic exception. Its write was fenced
  as unknown. Original artifacts remain unchanged.
- Read-only inspection of the saved public transcript projection: session still
  active, twelve messages; attempted last message absent. This narrows the
  effect but does not identify the service rejection or authorize blind replay.
- Recovered `/tmp/chi-bench-server.log` from stopped container into ignored runs.
  It contains request metadata, no service exception detail. No old world was
  restarted and no old write replayed.
- Public `send_message` service has multiple failure paths, including session
  preconditions and simulator errors. None is yet established for this failure.

## Implemented diagnostic repair

`MCPToolError` retains the returned response as a private attribute while its
public exception text remains generic. `RecordingTools` saves bounded,
credential-redacted error evidence in that case's ignored `tool-failures/`
directory, with exclusive creation and no console/event payload. Oversized
responses retain a redacted hash instead. Capture failure preserves the
original exception. Unknown-write fencing and absence of automatic retries are
unchanged. A returned tool error is not proof of no side effects.

Root owns implementation and execution. Tests cover error preservation,
private/redacted capture, no duplicate dispatch and no overwrite. Full regression
verification: **671 tests pass in 68.140s**. All 33 original harness baseline
hashes match. Plan-only selects exactly one CM case. Initial targeted invocation used a wrong unittest import
path for engine fixtures; use discovery as documented, not that invocation.

Next: commit frozen code after tests; run fresh CM -03 with existing Luna/high
sign-in, helpers/auto, 100 model/500 tool calls, 180s silence/600s active timeout,
Codex patient simulator (8 calls). If the error recurs, inspect the private
response and public contract before deciding recovery. No task-specific outcome
or hidden fixture inspection. Evaluate actual saved export with native structural
checks, semantic judge disabled.

## CM -03 execution and second repair

Frozen source `4ed289a`. Root stopped its owned inference after confirmed
irreversible premature closure and repeated investigation of unavailable reopening.
The process interruption is operator-induced, not a spontaneous provider failure.
25 model calls / 50 operations; 6-file snapshot saved and world stopped. Native
structural verification on the copied export: 2/6 pass, 4 fail, 8 N/A; same missing
assessment/plan/target-status/audit checks as -02. No judge. Original artifacts
remain unchanged. The earlier MCP error did not recur in this attempt.

The actual outreach record says **tentative**, with no consent and willingness
to hear more. The worker then called terminal `cm_intake.disenroll_case` despite
its own correct distinction from definitive refusal. Subsequent investigation
could not reopen the terminal case. Root initially summarized this as refusal;
checking original observations disproved that summary and it was corrected.

User approved checking this direct contradiction. CM disenrollment now requires
the existing source-backed policy decision, exact bound case/reason, and current
outreach evidence. Refusal-based closure requires recorded refusal with no consent.
Other policy-supported reasons remain model decisions; this is not a rule to
force consent or produce a predetermined outcome. Approved fixed CM workflow
references can support this CM-only decision without expanding provider-policy
source acceptance. New outreach invalidates an older closure decision.

The workspace-listing error was an empty relative path (`.`) indexed as a
nonempty tuple when current-case reference roots were configured. Guarding that
path fixes listing/search of an uncreated workspace without widening access.

## Marker-only simulator stop

The original -02 seventh simulator output was exactly `###STOP###`, while the
saved public session still held only the preceding twelve messages. Its exact
MCP error text was lost. A synthetic protocol check in the pinned runtime (no
dataset/task/persona/keys/network) establishes that an empty stopped response
raises `ConversationMessage` validation and leaves the original session active;
a nonempty stopped response persists the ended session. This reproduces a
mechanism consistent with -02, not recovery of its discarded exception text.

User chose an **additional budgeted model generation**, rejecting a coded event
substitution. For marker-only CM output the receiver makes exactly one separate,
journaled request asking for a brief farewell that retains the stop decision,
adds no medical facts/preferences/consent/refusal, and includes the marker. A
second unusable answer fails closed. Both generations share model-call,
character, original request deadline and world budgets; fresh native contexts
and per-world isolation remain. Independent claim/receipt records survive
restart; no completed external message is replayed. Raw marker output/usage is
saved privately before correction. Normal patient text is untouched. Wire usage
sums both calls; individual receipts/events retain each call separately.

Verification: full regression **680 tests pass in 63.423s**, then final retention
and shared-budget tests **27 simulator tests pass in 1.560s**. Synthetic native
service stop check preserved in ignored runs. Next is fresh single CM -04;
source frozen/committed first. No paid judge or full dataset.

## CM -04 actual result

Frozen source **29b941c**; normal actor finish at **19 model calls / 23 operations**,
275.2s actor / 325.5s world duration. **Local status complete is not benchmark
success.** Native structural verification still **2/6 pass, 4 fail, 8 N/A**;
assessment record, care-plan record, target status and cross-stage audit checks
failed. Structural binary reward 0, fractional 1/3; no semantic judge or full
competition verdict. Source-backed refusal/disenrollment was the accepted local
branch. No assessment or finalized care plan was created.

The model actually retrieved governing outreach guidance before closure. The
retrieved guidance prohibits starting assessment without clear consent and
provides a terminal decline path after limited clarification without consent.
The actual patient conversation ended without enrollment consent. This supports
the chosen workflow stop; it does **not** fulfill the public task's requested
finalized plan or remove the verifier failures. Code must not manufacture
consent, force assessment, weaken native checks or prescribe a hidden answer to
make that score pass. Full clinical/semantic judgment remains unmeasured. The
remaining task-versus-observed-policy/simulator limitation is explicit.

Before actual closure, the new decision record rejected missing current outreach
evidence and missing closure basis. The worker corrected both, then cited
retrieved policy, bound the exact reason and case, and recorded refusal/no consent
before the actual terminal write. This trial exercised evidence requirements;
the direct tentative/refusal contradiction is separately covered by regression
tests. Its semantic interpretation is not certified by the Python guard.

All 7 actual patient-simulator calls completed, 0 failed/unknown. No marker-only
reply occurred in -04, so the additional-generation branch was not exercised by
this dataset trial. It was verified separately by an explicit synthetic trigger
and **one real native Luna/high correction call**: nonempty farewell and stop
signal preserved; reported actual usage 6,753 input + 52 output = 6,805 tokens.
The initial marker was synthetic with zero usage; do not present that probe as
two real inferences or another benchmark trial. No actor tools or judge ran.
Local evidence: `runs/20261025-cm-real-farewell-probe/summary.json`.

Workflow reported usage: **848,507** tokens (839,243 input + 9,264 output;
205,696 cached input included; 4,194 reasoning-output detail). Patient simulator
usage is separate. This remains inefficient; no efficiency improvement claim.

The 6-file snapshot was integrity-verified; world stopped; no owned task worlds
remain running. Snapshot manifest SHA-256:
`351e78e26949b8fa7259f53414018f45e5ea3f36395405dbac0abb659d6a1874`.
All 33 original harness baseline hashes match. Raw payloads stay ignored.
Final source regression: **681 tests pass in 65.010s**
(`runs/20261025-cm-final-regression.log`).

Root stops further trials here: the remaining structural failure is not evidence
that consent may be bypassed. Do not claim full CM capability or generalize one
normal decline branch across the dataset. Preserve the stopped -03 and failed
-02 independently; no pooling assisted development retries into reliability.

### Explicit repeat command (no judge)

This creates a fresh development attempt, not a guarantee of a finalized plan.
Do not reuse an old run directory after source/configuration changes.

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261025-random-cm-anorexia-05 `
  --domains cm `
  --task-id cm_anorexia_hard_refuses_001 `
  --composition helpers --recovery-helper-policy auto `
  --concurrency 1 --attempts 1 `
  --timeout 180 --active-timeout 600 `
  --max-model-calls 100 --max-tool-calls 500 --max-context-chars 0 `
  --simulator-backend codex --simulator-max-model-calls 8
```
