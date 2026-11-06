# Execution, state and recovery

## Three decisions that should not be conflated

An agent loop chooses another model/tool step. A workflow determines which units may run and how their results join. A durable runtime determines what survives failure and what is repeated. These can coexist in one harness. LangGraph's workflow/agent distinction is about predetermined versus dynamically selected execution; its Functional API also permits ordinary language control flow over the same runtime as its Graph API. A visible DAG is therefore optional even in a graph-oriented framework. [Official workflows guide](https://docs.langchain.com/oss/python/langgraph/workflows-agents), [API comparison](https://docs.langchain.com/oss/python/langgraph/choosing-apis). Evidence C01–C02.

**Construction inference:** place model judgment where the next action is genuinely uncertain; retain ordinary code for known validation, accounting, routing and termination rules. “Agentic” does not require asking a model to decide every transition.

## A transcript is one projection of execution

Pi's session manager keeps parent-linked entries in append-only JSONL. A leaf selects the active branch. `buildContextEntries` selects the relevant compaction entry and retained range; `buildSessionProjection` associates projected messages with source entries and applies context edits. Older entries can remain on disk while being absent from the next request. Branch navigation changes the selected history rather than rewriting all previous alternatives. [Pinned session implementation, lines 473–582 and 976–985](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/session-manager.ts#L473). Evidence C03–C04.

**Construction inference:** an event record, current materialized state and model-visible prompt have different jobs. Retaining an event allows later reconstruction; selecting it for a prompt gives the model current access. Neither implies the other. This is an event-log-inspired design lesson, not a claim Pi implements every guarantee of a transactional event-sourcing platform.

The source's `_persist` uses synchronous file writes/appends and can be disabled for ephemeral sessions. Static inspection here does not establish crash-atomic records, filesystem durability after power loss, transactional integration with external APIs or a multi-writer protocol. [Pinned write path, lines 1160–1195](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/coding-agent/src/core/session-manager.ts#L1160). Evidence C05.

## Checkpoints, successful tasks and historical replay

LangGraph's checkpointer saves thread state. A separate store holds application-defined cross-thread information. A memory-backed implementation loses data at process exit even though its interface is a checkpointer or store. The word “persistent” is consequently insufficient without the selected backend and durability mode. [Official persistence guide](https://docs.langchain.com/oss/python/langgraph/persistence). Evidence C06.

Graph checkpoints occur at super-step boundaries; completed task writes within a failing step support recovery without rerunning successful siblings. Historical replay is different: nodes after the selected historical checkpoint execute again, including model calls and external requests. `sync`, `async` and `exit` persistence modes make different crash-recovery/performance tradeoffs. [Official checkpointer guide, Super-steps, Replay and Durability modes](https://docs.langchain.com/oss/python/langgraph/checkpointers). Evidence C07–C09.

An interrupt resumes by restarting its node, so code before the interrupt can run again. In the Functional API an entrypoint restarts while saved task results are restored. A task that failed before its result was recorded can still execute again. Thus tasks do not create universal exactly-once external side effects. [Interrupt rules](https://docs.langchain.com/oss/python/langgraph/interrupts), [Functional API, Determinism and Idempotency](https://docs.langchain.com/oss/python/langgraph/functional-api). Evidence C10–C11.

The inspected SQLite saver retrieves pending writes alongside a checkpoint and records intermediate writes by thread, namespace, checkpoint and task identifiers. These are concrete storage mechanics, not proof the external application transaction committed with that checkpoint. [Pinned SQLite implementation, lines 238–308 and 458–495](https://github.com/langchain-ai/langgraph/blob/0eb194fe6093812243de2249e7092029c87c8820/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L238). Evidence C12.

## The uncertain-outcome problem

**Illustrative design problem, not an executed test:** a tool sends an update; the server commits it; the network fails before the harness records success. A checkpoint only knows that success is unrecorded. Blind retry may duplicate the update; assuming failure may omit completed work from the agent's state.

**Construction inference:** give a mutating request a stable operation identifier; use downstream idempotency when available; otherwise read back authoritative state or route the unresolved outcome for reconciliation. Record “intent”, “attempted”, “confirmed” and “outcome unknown” separately. An approval decision, a tool response and an observed business state should also remain distinct. The precise protocol depends on the tool's real contract.

Letta's current SDK explicitly warns against blindly retrying after a successful send followed by connection failure. It also says disconnected events are not replayed automatically: clients reconcile from history or a bootstrap snapshot. Persisting the conversation is different from guaranteeing event delivery to every client. [Sessions, turns and durability, Guarantees and non-guarantees](https://docs.letta.com/agent-sdk/sessions/index.md). Evidence C13.

## Concurrency is an ordering contract

Pi's loop can execute allowed calls concurrently after sequential preflight. Completion events follow completion timing, but final tool-result messages preserve assistant call order. A per-tool sequential designation can force the whole batch onto the sequential path. This is visible in `executeToolCalls` and `executeToolCallsParallel`, not a blanket guarantee that arbitrary concurrent tools are safe. [Pinned tool-loop implementation, lines 508–658](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent-loop.ts#L508). Evidence C14.

**Construction inference:** separately define scheduling order, approval order, execution order, visible event order and commit order. Two tools updating one record may need serialization even if the model requested them together. Conversely, independent reads may safely run concurrently. Schema validity is insufficient to decide independence.
