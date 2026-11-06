# Operations, security and observability

The operational lesson from OpenClaw is that permission, execution, storage, recovery and delivery are related but separate responsibilities. This report describes the pinned design and its declared trust boundary. It is not a recommendation to deploy these defaults for an unrelated system and is not a security audit.

## The declared trust model

The security guide supports one Gateway for a single operator or mutually trusting team. It explicitly does not promise isolation among hostile/adversarial users sharing one agent/Gateway. It documents broad default session visibility and agent-to-agent reach; `sessionKey` is a routing selector, not a bearer authorization token. Separate gateways and ideally OS/host boundaries are the prescribed stronger isolation for hostile tenants. [OC-067](EVIDENCE.md#oc-067).

The sandbox resolver defaults `mode` to off. When sandboxing is enabled, the default backend is Docker and workspace access is none; configurable other backends exist. Docker is therefore not an inherent requirement for the reasoning loop or for reading this code. We did not start it. [OC-065](EVIDENCE.md#oc-065).

Host exec approval constants default to `security="full"`, `ask="off"`. The fallback when an approval cannot be resolved is deny, but that does not turn the default trusted-host mode into a mandatory approval flow. Those choices fit the upstream declared operator model; a harness with different threat assumptions must choose its own policy. [OC-066](EVIDENCE.md#oc-066).

## Three controls with different jobs

| Control | Question it answers | What it cannot establish on its own |
| --- | --- | --- |
| Tool policy | Is this callable capability in the effective surface for this caller? | Host filesystem/process isolation |
| Approval/exec mode | Does this effect require a current operator decision under this policy? | Semantic safety of arbitrary interpreter behavior |
| Sandbox/OS/network boundary | Where can the admitted process reach? | Correctness of the model's reasoning or facts |

The layering is an interpretation of the traced policy and configuration surfaces. It avoids treating a role prompt, approved tool schema or container as a complete security solution.

## Policy composition and provenance

The tool pipeline constructs profile, provider profile, global, provider-global, agent, provider-agent, group and sender layers. Each layer retains its origin for diagnostics. It filters the currently remaining tool set, so a later allowlist cannot independently recreate an already-removed tool. Plugin group expansion and unknown/unavailable-tool diagnostics happen within this pipeline. [OC-062](EVIDENCE.md#oc-062), [OC-063](EVIDENCE.md#oc-063).

Run authority is host-issued and includes a live assertion, abort/revocation state and captured operator scope. Its current-role readers recheck that assertion. This demonstrates a capability-lifetime mechanism; it does not prove every provider/tool/plugin integration invokes it correctly at every effect. [OC-064](EVIDENCE.md#oc-064).

General failure case: a long tool preparation starts while permission exists, waits on I/O, then publishes after the permission or session changed. Correct admission is necessary but not sufficient; the current capability must be checked at the effect boundary. The inspected run-authority and transcript-write fences address those classes at named paths. [OC-018](EVIDENCE.md#oc-018), [OC-019](EVIDENCE.md#oc-019), [OC-064](EVIDENCE.md#oc-064).

## Sessions, transcripts and database ownership

The current active path stores session and transcript state in SQLite and guards protected writes against lifecycle/writer rebound. The package also advertises database-engine families including Postgres; that does not establish that every Memory Core operation uses Postgres. This audit's traced memory search/store resolver is SQLite-specific. [OC-001](EVIDENCE.md#oc-001), [OC-018](EVIDENCE.md#oc-018), [OC-019](EVIDENCE.md#oc-019), [memory resolver](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/src/agents/memory-search.ts).

The architecture documentation describes per-agent writer ordering and Gateway state-directory ownership. A history export or legacy JSONL artifact should not be edited as if it were the authoritative current SQLite record. Exact migration/restore procedures depend on the pinned version and deployment. No migration or database repair was executed. [OC-020](EVIDENCE.md#oc-020).

## Deadlines at different levels

The generic resolver defaults to 48 hours for the agent/model-attempt timeout; zero maps to a timer-safe unlimited sentinel. This is a surprisingly large general default, so quoting old “ten-minute agent timeout” summaries would be wrong for this revision. It is not the deadline of every operation. [OC-068](EVIDENCE.md#oc-068).

The scheduling guide describes independent defaults: isolated/detached agent jobs have a 60-minute scheduler watchdog; command jobs ten minutes; script payloads five minutes. A fallback model attempt does not restart the scheduler deadline. Active Memory has much shorter recall-specific budgets. [OC-069](EVIDENCE.md#oc-069), [OC-053](EVIDENCE.md#oc-053).

General lesson: distinguish request timeout, model-attempt timeout, tool timeout, child deadline, queue wait, scheduler watchdog and cancellation-drain grace. A single `timeout` configuration key rarely describes the complete execution budget.

## Cron and heartbeat are host behavior

The base heartbeat constant is 30 minutes, with provider/config overrides and eligibility conditions. A heartbeat is a scheduled trigger that can invoke agent work; the model is not independently watching wall-clock time. [OC-070](EVIDENCE.md#oc-070).

Cron/automation jobs run through the Gateway scheduler, with job definitions, state and history persisted in the shared state database. The Gateway must be running. On restart, recorded terminal results are reconciled rather than blindly replayed; uncertain active runs become interrupted and required delivery can remain unknown. These are pinned documented contracts, not executed fault-injection results here. [OC-069](EVIDENCE.md#oc-069).

This is distinct from durable memory: a note saying “remind me tomorrow” is not itself a scheduled job. Prospective intent, time/event trigger, admitted run and delivery receipt are separate pieces. An implementation must connect them deliberately.

## Side effects, retries and recovery

The scheduler guide explicitly accepts a tradeoff: after a crash with an unknown effect outcome, it may miss an occurrence rather than replay uncertain command/script/tool/delivery effects. The subagent guide similarly lets the parent assess interrupted work rather than relaunching every child. [OC-061](EVIDENCE.md#oc-061), [OC-069](EVIDENCE.md#oc-069).

This is not a universal “exactly once” guarantee. For any external operation, a reliable harness needs an effect identity, a tool receipt or reconciliation query, and a policy for ambiguous outcomes. Idempotent API keys, transactional writes, retries and human review are alternatives whose usefulness depends on the application.

## Observability and privacy

The pinned OTel guide describes request-scoped W3C trace context and bounded identifiers spanning agent/harness/model/provider/tool activity. It documents content capture off by default. Enabling it adds bounded redacted input/output/tool material while excluding system prompts and private thinking. External runtime tool events do not necessarily include the same content as built-in tool calls. [OC-071](EVIDENCE.md#oc-071).

This provides an important distinction for research logs:

- A trace ID correlates work; it does not establish that a tool succeeded.
- Token/latency/cost metadata can be retained separately from patient/task content.
- Turning off exported content does not automatically erase local transcripts, notes, diagnostic artifacts or backups.
- A native runtime may expose weaker/different visibility than the built-in loop.

The first three are implications of separate storage/export responsibilities; no deployment-level privacy certification is claimed.

## Extension boundaries

OpenClaw exposes distinct provider, channel, runtime/harness, context-engine, memory and tool/plugin contracts. Bundled plugins follow public SDK boundaries; registration metadata is intentionally separable from runtime execution. Hooks can narrow tool surfaces or observe lifecycle, but support depends on runtime ownership. [OC-003](EVIDENCE.md#oc-003), [OC-014](EVIDENCE.md#oc-014), [OC-015](EVIDENCE.md#oc-015), [OC-017](EVIDENCE.md#oc-017), [OC-072](EVIDENCE.md#oc-072), [extension boundary source](https://github.com/openclaw/openclaw/blob/3b3492490602f5080d3fbe7d2df9618cdb82ea9a/extensions/AGENTS.md).

For a new harness, extension points should follow stable responsibility boundaries. Adding a second provider does not automatically require a new core memory system; adding an external runtime does require an explicit account of which owner controls tools, context, auth, cancellation and completion.
