# Selected implementation traces

These are bounded static traces at the pins in [source receipts](sources.json). They are navigation aids for construction, not executed integration tests or complete security reviews.

## Pi: request preparation is an explicit boundary

The selected `runLoop` path polls steering, prepares the next turn/request, streams a response, handles tools and decides whether to continue. Error/abort ends the loop. A length-truncated response with tool calls produces failures instead of executing potentially incomplete arguments. Steering and follow-up inputs are polled at different scheduling points. `streamAssistantResponse` performs `transformContext` before `convertToLlm`, then normalizes the provider request. [Pinned `agent-loop.ts`, lines 175–320 and 387–407](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent-loop.ts#L175). Evidence C30–C31.

The `Agent` wrapper passes the hooks and separate queue-drain callbacks into the loop; its configured default tool execution is parallel. Those facts concern this wrapper and snapshot. [Pinned `agent.ts`, lines 253 and 475–503](https://github.com/earendil-works/pi/blob/c268154ca1171c2f9eefe75d3d7372a68aada2d5/packages/agent/src/agent.ts#L475). Evidence C32.

**Design inference:** keep the domain's canonical state independent of provider message format. Make request construction inspectable. A correction arriving during compaction needs a defined scheduling rule; cancellation needs explicit behavior for already-running tools. A clean “no more tool calls” response is an execution stop signal, not proof the user's objective succeeded.

## LangGraph: primitive contracts are narrower than product guarantees

The pinned task wrapper forwards retry, cache and timeout policies into runtime calls. Its source documentation requires serializable checkpointed values and notes that synchronous tasks cannot safely be cancelled in-process by the supported timeout mechanism. A retry policy therefore needs operation-specific reasoning. [Pinned `func/__init__.py`, lines 59–94 and 144–169](https://github.com/langchain-ai/langgraph/blob/0eb194fe6093812243de2249e7092029c87c8820/libs/langgraph/langgraph/func/__init__.py#L59). Evidence C33.

`interrupt` explicitly documents restarting a node and matching multiple resume values by encounter order; the implementation uses task scratchpad state to track the interrupt index. Reordering interrupt calls after deployment can therefore invalidate assumptions about a paused execution. This is a source-backed compatibility concern, not an observed migration failure in this repository. [Pinned `types.py`, lines 903–925 and 1019–1021](https://github.com/langchain-ai/langgraph/blob/0eb194fe6093812243de2249e7092029c87c8820/libs/langgraph/langgraph/types.py#L903). Evidence C34.

**Design inference:** retain the policy/schema/code version with recoverable work, and define whether to finish, migrate or abandon paused old-version runs. A database row surviving a restart is insufficient if the new code interprets it differently.

## Letta: local context reduction is distinct from memory promotion

The pinned local compaction planner selects a retained suffix and a prefix to summarize, with cutoffs chosen around valid assistant boundaries and pending-tool constraints. Its full-compaction plan also keeps a pending assistant tool-call tail. [Pinned `compaction.ts`, lines 625–707](https://github.com/letta-ai/letta-code/blob/6e2081fa9d7b6bb54bbaab365e24f142e7ad382b/src/backend/local/compaction.ts#L625). Evidence C35.

This is a conversation-buffer transformation. It does not establish that every omitted fact was promoted to durable memory, that a summary preserved all evidence, or that all memory workers merged successfully. The Git/memory lifecycle and cloud services are different paths. Current documentation and the selected local code should not be flattened into one backend-independent promise.

## Reuse the seams, question the choices

The transferable lesson is modularity: request preparation, context projection, tool policy, side-effect recovery, memory promotion and client reconnection can each have an explicit contract. We need not copy any reference's queue policy, default token reserve, file layout or agent count. Our own job requirements and measured failures determine those choices.
