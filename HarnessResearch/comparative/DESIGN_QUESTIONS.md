# Questions that determine our design

This is engineering synthesis informed by the inspected mechanisms. These are candidate experiments, not work already implemented or benchmark results. Preserve concise decision rationale, evidence and alternatives; a private model reasoning transcript is neither required nor treated as proof.

## Decide requirements before selecting mechanisms

| Decision | Questions that must be answered | Plausible alternatives |
| --- | --- | --- |
| Unit of work | Is the job bounded? Can another input alter it mid-run? How is completion observed? | Single loop; workflow with embedded loops; queued service |
| State owner | Which facts are authoritative, observations, model inferences or pending writes? | One structured case state; per-worker state with explicit merge; external system as authority |
| Persistence | Must work survive an exception, process crash, host loss or deployment? | Ephemeral process; transcript; checkpoint database; replicated durable runtime |
| Memory scope | What is allowed to cross task, user, role and organization boundaries? | No cross-task memory; curated shared procedures; scoped durable facts |
| Retrieval | Is the challenge finding text, selecting current policy or recalling an episode? | Exact references; keyword/filter search; vectors; hybrid retrieval; hierarchical files |
| Context policy | Which material is always included, retrieved, summarized, retained by identifier or excluded? | Recent window; structured state plus evidence; incremental summary; demand-loaded files |
| Parallelism | Are operations independent? Who reconciles conflicting observations and edits? | Serialized owner; bounded read specialists; transactional or versioned merge |
| Side effects | Can the tool deduplicate or report the result of a previous operation? | Idempotency key; read-back reconciliation; compensating action; explicit unknown outcome |
| Memory formation | Who may save a lesson? Does it change prompts or merely evidence retrieval? | Human-curated; foreground proposals; background proposals with validation |
| Stopping | Is there a measurable postcondition? What happens when evidence remains missing? | Verified success; justified partial result; bounded retry; explicit unresolved state |

## A compact set of discriminating experiments

1. **Stored versus visible evidence:** put one critical constraint outside the retained recent history. Compare a free summary with a structured constraint record and exact evidence pointer. Measure retrieval success and unsupported assertions, not just whether the final response sounds coherent.
2. **Unknown outcome:** use a fake mutating service which commits an operation and then drops the response. Restart before recording the tool result. Check duplicates, reconciled state and whether the harness reports uncertainty truthfully.
3. **Parallel write conflict:** have two workers read one version, propose incompatible updates and finish in reverse order. Check version handling, merge ownership and provenance.
4. **Interrupt/replay boundary:** pause after a completed task and separately inside an incomplete task. Count repeated model/tool operations and confirm the intended checkpoint semantics.
5. **Context pressure:** inject large tool outputs and growing schemas. Measure prompt size before/after reduction, required-constraint retention, tool-call/result validity and irreducible-context handling.
6. **Memory contamination:** supply a false fact for one synthetic identity and a corrected fact later. Verify scope isolation, supersession and removal from every configured retrieval path.
7. **Reconnect without replay:** disconnect a client after successful send. Reconcile history and live stream without duplicating a request or final result.
8. **Procedure promotion:** let a worker propose a reusable rule from a failed episode. Check whether it preserves prerequisites, records contrary evidence and remains a proposal until the configured promotion test passes.

Keep the model, task sample, tool contracts and resource accounting comparable when comparing designs. Include no-memory and simple-owner baselines. Report token/tool/latency budgets and failure classes; do not label a framework or multi-agent design better because it has more features.

## Unresolved by this research

No optimum context size, summarizer, memory backend, graph structure, worker count or role decomposition has been established for our task. No product has been shown here to be a formal industry standard. The current comparison does not determine whether persistent identities outperform temporary specialists, whether semantic retrieval is necessary, or whether memory learned from one benchmark task may legally or methodologically be reused for another. Those are contract and evaluation questions before they are implementation choices.
