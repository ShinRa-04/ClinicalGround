# Goal and constraint planning — original proposal and implementation scope

October 25, 2026. User requested a detailed general repair proposal after CM -04.
This was the original design proposal. A targeted implementation is now verified
offline: [implemented goal links, benefits and limits](GOAL_LINK_IMPLEMENTATION.md).
The full hospital-template importer and broader evaluation plan remain deferred.
This document does not itself authorize a new trial or judge.

**User feedback received:** graphical current/proposed explanation, persistent
primary-goal importance markers, and concrete prerequisite examples requested.
The earlier hospital dependency/data-flow research must feed the runtime graph;
it must not remain background role descriptions. Bounded helper review and
separate execution/outcome/evaluation reporting accepted. Keep clear cases simple.
**Broader verification experiments are ON HOLD** while the design/implementation
work is addressed. See [execution diagrams and concrete example](EXECUTION_FLOW_CURRENT_AND_PROPOSED.md).

## Concrete gap

CM -04 ended normally with a source-backed decline/disenrollment. The requested
finalized care plan was not produced; native structural checks passed 2/6, with
4 failures and 8 N/A. Semantic judgment remains unmeasured. The retrieved policy
and observed non-consent support a stopping interpretation, but do not prove the
preceding outreach was optimal, the goal impossible, or simulator equivalence.

Current code already has source-linked blockers, obligations, working notes,
progress recovery, policy decisions, and a shared closure assessment. Reuse them.
`closure.assess_closure` requires a stop assessment for branches declaring external
waiting; a terminal decline branch can be accepted without that mandatory review.
The CM contract also treats a permissible alternative endpoint as local completion
even when the public instruction explicitly requested a finalized plan. This
conflates a justified stop with achievement of the original requested outcome.

## Central change

Connect original goals, proposed prerequisites, observations, unresolved questions,
investigations and action effects in one evolving case-local dependency record.
Use it during planning and before an irreversible action, rather than merely
checking whether records exist afterward. The graph describes the model's current
understanding; it is not a fixed menu or hospital sequence.

### Preserve the assignment

Keep the public requested outcome and source immutable. Separately record actual
progress and any supported alternative stopping endpoint. A permissible decline
can end execution while leaving the requested outcome unmet. Do not relabel it
as a finalized plan, force consent, or alter native scoring.

### Represent dependencies with their epistemic status

For each material blocker record: which goal/action it affects; the claimed
prerequisite; its source; whether it is an explicit tool requirement, the model's
policy interpretation, an observed state or an unverified assumption; what remains
unknown; and what investigation could change the plan. Code verifies exact source
and tool-schema claims. Policy necessity and applicability remain interpretations.

Example: assessment depends on consent under the retrieved policy; the patient
has not consented; a question about information use remains unanswered. That
blocks assessment, not necessarily answering the patient's question. In another
domain, missing documents may block a final approval without blocking an assigned
physician review or an information request. Neither example becomes a hardcoded
workflow rule.

### Make uncertainty actionable

The owner selects investigations using available permitted tools. It explains
what question an action could answer and which goal or decision that would affect.
Reuse existing observations before retrieving them again. No invented numerical
confidence score, compulsory number of alternatives, or extra planning call for
every operation. Update the existing compact record when a relevant fact, goal,
interpretation or plan changes; derive tool effects in code.

### Review irreversible actions before execution

For an action known from public contracts to close a case or make an immutable
decision, add to the existing decision record: expected effect, impact on unfinished
goals, supporting observations/policy, relevant remaining alternatives and why
the chosen action is justified now. Bind the record to the actual proposal and
material source state. A changed relevant source invalidates stale justification.

Code checks provenance, identities, explicit constraints and direct structured
contradictions. It cannot prove a natural-language policy interpretation correct
or prove that all useful actions have been exhausted. The model retains that
judgment. Another policy-supported exit remains available; do not mandate enrollment,
approval, denial, repeated persuasion or a task-specific answer.

When a terminal proposal abandons an unfinished explicit goal or conflicts with
observed evidence, a bounded read-only helper can challenge its premise using
selected original sources and permitted reads. Ask what evidence would change
the decision and whether a useful action remains. The owner makes the final
decision; the helper is not a clinical judge and may also be wrong. Reuse the
existing helper machinery. At most one critique for a materially unchanged
decision; no recursive review loops or separate model on every ordinary action.

### Stop honestly

Keep three separate outputs: execution state, requested-outcome achievement,
and evaluation result. The user's stopping criterion remains no further useful
permitted action, not mere ambiguity. A supported decline can be
`execution=finished`, `requested_outcome=unmet`, with benchmark checks still failed.
An unknown write, exhausted budget or model failure must remain a distinct stop
reason. Do not claim Python has semantically certified that no action remains.

## Implementation scope

- `planning.py`: extend existing blockers/working record with goal and prerequisite
  links, epistemic status, next investigation and material revisions.
- `completion_contracts.py`: preserve requested outcome separately from permissible
  stop branches; alternative stops cannot silently satisfy a different outcome.
- `policy_grounding.py` and `engine.py`: extend existing precommit decision checks
  with goal impact and source-state binding; retain transactional fencing.
- `helper_jobs.py`: reuse scoped read-only critique for consequential goal/constraint
  conflicts, with shared budgets and no write authority by default.
- `closure.py`: consistent stopping review across pending and alternative terminal
  endpoints; retain model judgments as judgments.
- `context.py` and `working_set.py`: project a concise current goal/dependency view
  with original source pointers, not duplicate the full transcript.
- `evaluation.py`, batch and console reporting: expose finished/goal-unmet separately
  from verified goal achievement and actual benchmark grades.

No new vector database, broad provider migration, hospital-role expansion, hidden
fixture access, simulator-persona tuning or benchmark modification is part of this
proposal. Tool discovery remains available; the graph does not restrict the owner
to a prescribed list of next actions.

## Verification

**Deferred at the user's October 25 instruction.** The plan below is retained for
later; do not launch this experiment matrix or new dataset evaluations now.

First test mechanics and actual model behavior separately. Use synthetic paired
scenarios with the same tools but changed evidence: unresolved question versus
explicit refusal; missing final-decision evidence with other assigned work still
possible; real service prohibition versus an assumed prerequisite; new information
after a blocker; irrelevant repeated reads; and an uncertain write. Expected
behavior concerns provenance, investigation and respecting actual boundaries,
not one mandatory clinical answer.

Then execute a small predeclared set across PA, UM and CM, keeping source/configuration
frozen and every failed development attempt separate. Report achieved goals,
supported stops with goals unmet, errors, native check results and unmeasured
semantic quality independently. Include owner/helper calls, reported input/output
tokens, repeat reads and premature terminal actions. A few passing cases establish
limited evidence, not broad reliability. No paid judge without authorization.

The main trade-off is additional reasoning at consequential decisions. Keep it
selective and measure its cost. A more elaborate record or an agreeing helper does
not itself establish better judgment. If varied executions do not improve, revisit
the design rather than add mandatory prompts and more agents.
