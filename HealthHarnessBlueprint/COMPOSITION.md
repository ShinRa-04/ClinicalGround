# Composite jobs built from smaller design roles

## The organizing unit

The main unit is a **composite job**, such as the PA specialist, UM case/review function or CM coordinator that receives assigned work. Under it are smaller responsibilities. These are proposed design roles; many need not be separate real-world professions, people or autonomous agents.

The catalogue decomposes PA into 18 responsibilities, UM into 18, CM into 20, and shared harness support into 10: **66 functional contracts**. This is a detailed starting decomposition, not an optimal count or 66 mandatory calls. Each contract identifies input, output, decision scope, forbidden inference and a completion check. It can be split, combined or omitted when the task does not need it.

## Four levels

| Level | Example | Purpose |
| --- | --- | --- |
| Organization/workspace | Provider PA desk, payer UM desk, CM desk | Responsibility, principal, queue and policy scope |
| Composite job | PA specialist assigned to this case | Own the requested outcome and unresolved obligations |
| Micro-role | Evidence collector, criterion linker, gap analyst, packet composer | Make a smaller responsibility and its output explicit |
| Execution form | Ordinary code, tool operation, in-context reasoning, bounded model call or worker | Choose the appropriate implementation, rather than equating role with process |

The 29-module organization catalogue is an upper-level map, not the deepest decomposition. A02 contains the PA family, A03/A21/A22 organize UM stages, and A04 plus relevant desks support CM. Shared capabilities and deterministic services sit underneath. The 97-role reference supplies healthcare context but does not limit which computational subroles we may invent.

## Three interchangeable execution arrangements

**Single combined agent:** the composite owner performs several or all needed reasoning responsibilities in one patient-scoped context, invoking deterministic checks/tools where required. It must still preserve the functional output/status obligations. A separate persona call for every checklist item is unnecessary.

**Owner with bounded helpers:** the owner creates a focused subtask when distinct attention or evidence analysis is useful. For example, a policy applicability question and an evidence contradiction analysis may receive different bounded contexts. Each result carries its source snapshot, unknowns and proposed implication; it does not silently mutate the case.

**Role-worker team:** selected responsibilities use separate active workers with explicit handoffs, ownership and budgets. This is useful to test when work is sustained/parallelizable or information views genuinely differ. It is not the default simply because 66 contracts exist. Workers must not all run on every case.

These arrangements should implement the same job contract. A composition policy selects a preset from actual task/stage, required scope, evidence size and measured resource/quality behavior. It must not acquire cross-patient habits through automatic patient-memory learning. No adaptive composition policy has been implemented or shown superior.

## A concrete PA example

For an assigned packet task, the owner may combine PA-01–PA-05 into an orientation/administrative pass, PA-06–PA-09 into evidence analysis, and PA-10–PA-12 into packet preparation/validation. PA-13 executes the actual supported submission. PA-14–PA-16 activate only if the real response/task calls for that work. PA-17 is conditional downstream coordination, and PA-18 checks only the assigned episode's completion.

This is a possible grouping, not a forced pipeline. A task beginning at an information request should use current records and the relevant responder rather than resubmit from scratch. If the required evidence is already available, a “collector worker” need not repeat retrieval. Micro-role completion means its needed output exists and is valid, not that a separate agent spoke.

## What can be merged, and what must survive?

Merge common reads, closely related reasoning and artifact assembly when the same scoped evidence and owner suffice. Retain identity/source checks, actual operation permissions, new-versus-existing clinical facts, policy applicability, unknowns and receipt/closure obligations. Tool effects still pass the actual operation gate even when the owner did all reasoning itself.

Preserve distinct stage/authority records for initial review and applicable reconsideration; a changed prompt cannot prove independence. In the supplied benchmark, execute the actual assigned simulated function without inventing extra real-human approval steps. An internal critic is not an external review body or official grader.

## Design method for further bifurcation

Split when a responsibility has a distinct input/output, error mode, information view, authority, latency dependency or measurable context problem. Combine when the split merely repeats facts, transfers lossy summaries or adds calls without improving the outcome. A new responsibility needs a falsifiable purpose: which failure does it prevent, and how would we know a simpler combined job is just as good?

The [micro-role catalogue](MICRO_ROLES.md) is the detailed contract reference. [Workflows](WORKFLOWS.md) show how those responsibilities process incoming work; [evaluation](EVALUATION_AND_FAILURES.md) describes how to compare the arrangements without choosing a winner by appearance.
