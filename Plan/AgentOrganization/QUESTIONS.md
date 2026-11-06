# Questions and unresolved evidence

The questions, evidence, alternatives and concise reasons are part of the research output. The [decision log](DECISION_LOG.md) records provisional answers and what would change them. Each [role profile](ROLE_ANALYSIS.md) adds a specific functional question and counterexample. These are reviewable decision rationales, not a claim of empirical proof.

Statuses: **answered in scope** means a conceptual/source distinction is documented; **proposed** means an engineering hypothesis; **unmeasured** means execution evidence is absent; **fact required** means an actual task/institution/version fact must be supplied. A question can have more than one status.

| ID | Question | Current answer / status | Evidence needed to close the uncertainty |
| --- | --- | --- | --- |
| Q01 | Are we creating χ-Bench itself? | Answered in scope: χ-Bench supplies the benchmark; we analyze our acting agent/harness. A replacement simulator has not been selected. | S06/S09/S11; any future scope change must be explicit. |
| Q02 | Does each human role need its own autonomous worker? | Proposed: retain every function, select worker boundaries by actual work and isolation needs (AD01/AD03). | Task relevance and controlled comparisons of role modes versus workers. |
| Q03 | What makes a worker unique? | Proposed: objective, knowledge view, tools, authority, state owner, output, trigger and stop rule (AD03). | Measure which distinctions affect errors/completion rather than naming alone. |
| Q04 | Which roles are actually performed in each task? | Fact required: not mapped exhaustively to the 75 public instructions/tools in this phase. | Agent-visible instruction and tool-contract inventory, without hidden expectations. |
| Q05 | Is a profile a person, group, capability or service? | Answered as a design classification for all 97 profiles; conditional on the assigned task. | Reclassify if actual instructions assign a different function; M28 remains explicitly composite. |
| Q06 | Which functions can share a job? | Proposed: W05/W08/W13 are early administrative/coordination candidates (AD04). | Actual scopes, workload/context pressure, handoff losses and matched-resource results. |
| Q07 | Does a merger preserve authority? | Proposed: implementation sharing must preserve operation-level boundaries (AD05). | Enforced tool/data scopes and actual stage/identity checks. |
| Q08 | Can one prompt satisfy independent reconsideration? | Answered in scope: no evidence of required human independence or expertise follows from a new prompt (AD06). | The actual benchmark assignment and applicable institutional conditions; fresh-context benefit is a separate experiment. |
| Q09 | Does a different model create independent reasoning? | Unmeasured: heterogeneous models may share or add errors; no guarantee. | Compare fresh same-model and heterogeneous review with evidence quality, cost and error overlap recorded. |
| Q10 | Should one worker own all case writes? | Proposed first design, not a universal rule (AD07). | Actual transaction/version/idempotency semantics and measured conflicts/latency. |
| Q11 | Which work can run in parallel? | Fact required / unmeasured: independent read-only analysis may qualify; dependent writes/dialogues may not. | Trace timing, data dependencies, context completeness and observed synchronization cost. |
| Q12 | When should a specialist be persistent? | Proposed: only when continuity and independent multi-step work justify it (AD08). | Activation frequency, sustained state use, reduced repeated work and actual benefit. |
| Q13 | How should handoffs work? | Proposed task/result contract with provenance, uncertainty, owner and acknowledgement (AD09). | Tests of dropped context, ambiguous responsibility and stale results. |
| Q14 | How is conflict resolved? | Proposed: evidence and applicable authority/clarification rather than unqualified majority vote (AD10). | Traceable conflicting sources and behavior under unresolved cases. |
| Q15 | Can a worker use information another role must not see? | Fact required: purpose, actual task scope and restrictions control the view (AD05/AD15). | Tool permissions and applicable information policy; a model prompt is not enforcement. |
| Q16 | What happens across context refresh or worker failure? | Proposed: retain case/stage, source versions, actual dialogue answers, unresolved obligations and ownership. | Recovery experiments, lost-message tests and stale-state checks. |
| Q17 | What observation establishes completion? | Proposed: task-specific terminal evidence and readback, not a worker’s confidence. | Actual tool contracts and task requirements; later official score is outside actor inputs. |
| Q18 | Do human-like biographies improve work? | Unmeasured: persona detail and functional contracts must be separate variables (AD11). | Equal-resource persona ablation beyond clearer instructions or extra compute. |
| Q19 | Can the old network choose the team size? | Answered in scope: it is an unconfirmed workflow model, not measured workload (AD12). | Trace-weighted costs and held-out validation before optimization claims. |
| Q20 | Which healthcare permissions remain ambiguous? | Fact required: prior R13 signoff tension, state/credential/delegation and dated hospice applicability remain unresolved. | Current actual program/jurisdiction documents; do not upgrade prior evidence by inference. |
| Q21 | Which integration API should be implemented? | Fact required before implementation: pin 4444a07 and live documentation differ (AD14). | Deliberately chosen runtime commit, interface inspection and compatibility checks. |
| Q22 | Does decomposition help beyond spending more tokens? | Unmeasured (AD13/AD16). | Fixed combined budgets/model/tools, reported actual usage, repetitions and ablations. |
| Q23 | How many workers are best? | Unmeasured; 23 packages are analysis categories, not a recommended worker count. | Performance/resource frontier across task families; no numeric optimum is established. |
| Q24 | What is the experiment’s held-out set? | Not selected or executed. | Define families and reserve a split before tuning; once used for selection it is no longer untouched. |
| Q25 | What is the cost of realistic organizational separation? | Unmeasured; literature does not provide our multiplier. | All worker/controller tokens, messages, tool calls, latency, retries and required environment/judge costs. |
| Q26 | Can an internal persona supply an external outcome? | Answered in scope: its generated answer is not a permitted external observation. | The actual environment response for patient answers, review outcomes, acceptance, physical delivery or payment. |

## Conditions that would reverse the provisional preference

Separate workers become more compelling if task mapping reveals sustained independent investigations, different enforceable views, distinct state ownership or measured context interference in the merged design. Merging becomes more compelling if handoffs lose evidence, repeated worker activation dominates cost, or separate workers only restate the same information. Neither finding has been observed in project trials yet.

## What remains outside this completed design study

Public-task/tool mapping, runtime construction, tool-permission enforcement, empirical worker-count/model selection and benchmark execution remain unperformed. This study supplies an explicit basis for those next activities; it does not claim they have already occurred.
