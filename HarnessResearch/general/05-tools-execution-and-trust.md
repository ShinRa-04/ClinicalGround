# Tools, execution boundaries and trust

A tool call is a proposal by a model to invoke an operation. A robust executor separately establishes the caller, permitted scope, valid arguments, execution identity and observed outcome. Valid JSON is a syntax property; it is not proof of authorization or correctness. [G03](../SOURCES.md#g03).

## Design the contract for the decision

Every tool needs a clear purpose, stable name/version, parameter schema, effect classification, permission requirement, timeout/cancellation behavior, output/error contract and retry semantics. Useful effect classes include read-only observation, local reversible mutation, external side effect and an action requiring a particular approval. This classification is a design aid; each actual operation needs its own semantics.

Make identifiers and versions explicit where correctness depends on them. A response can carry concise evidence, a status, source references and a handle for a larger artifact. Tool ergonomics should not erase the exact record ID needed to act safely. The goal is high-signal context, not removing metadata indiscriminately. Namespacing and good descriptions can reduce ambiguity, but measure behavior on actual tasks. [G11](../SOURCES.md#g11).

Avoid exposing thousands of overlapping endpoints without discovery or scope. Alternatives include a small task-relevant toolset, lazy schema retrieval, capability routing or a code-execution layer that filters intermediates. A higher-level tool can reduce repeated reasoning but also hide several effects behind one call. Its permission, atomicity and partial-failure contract must remain inspectable. [G12/G13](../SOURCES.md#g12).

## A proposed execution pipeline

1. Assemble the complete typed request; reject incomplete streamed arguments.
2. Resolve the principal, session/run and current task/version.
3. Validate schema and domain constraints; normalize without silently changing intent.
4. Apply actual permission/purpose/approval policy to that operation and resource.
5. Assign a durable action identity and record intent before relevant side effects.
6. Execute with a bounded timeout/cancellation scope and the correct credentials/runtime.
7. Record observed result or explicit ambiguity; verify authoritative state where needed.
8. Return a bounded observation to the model with provenance and next-action implications.

The exact ordering of persistence and authorization depends on the operation; do not log secrets or a full sensitive payload just to satisfy a generic template. The important property is that effects cannot bypass the applicable gate and ambiguity cannot be reported as success.

## Permission is not a prompt

Instructions can guide behavior; access controls should be enforced outside the model where a boundary matters. Scope files to resolved permitted paths, credentials to the intended service/audience, and tools to the actual principal. Validate remote targets, redirects and network egress according to the deployment's requirements. Avoid treating a remembered approval as permission for a different payload or version.

An approval record should bind principal, action, resource, arguments or canonical digest, policy/version, expiry and approver identity as needed. If arguments change after approval, re-evaluate according to the actual policy. Durable approvals need restart-safe pending state and a clear cancellation/rejection path. This is an engineering contract proposal, not a universal claim that every harmless action requires user confirmation.

## The sandbox boundary

Separate “can the process do it?” from “should this user/task be allowed to do it?” A filesystem/process sandbox can constrain execution, but it does not by itself establish the right customer record, clinical authority, external side-effect intent or confidentiality policy. Conversely, an authorization check without process/network confinement may leave broad ambient capabilities exposed.

Choose isolation from threat model: trusted local operator, trusted team, untrusted users/tenants, hostile tool servers and arbitrary code are different settings. A tool/runtime useful for a trusted personal assistant may be unsuitable as a shared public service without further boundaries. Case-study defaults must be read in that context rather than copied.

## MCP is an interface layer

MCP offers an interoperability architecture for host/client/server interactions and capabilities. It does not replace the harness's execution loop, memory admission, task state or permission policy. The host remains responsible for controlling context sharing and cross-server boundaries. [G01](../SOURCES.md#g01).

The protocol's security guidance addresses concrete transport/authorization risks such as token audience mistakes, token passthrough and SSRF. Read the actual revision and transport requirements. Tool descriptions/results can still contain untrusted material; interoperability does not make them trusted instructions. [G02](../SOURCES.md#g02).

## Learn from failures

Test wrong IDs, stale approvals, schema-valid but invalid values, output truncation that removes a critical qualifier, malicious retrieved instructions, late results after cancellation, partial external completion and a timeout after a successful effect. A tool system that only passes the happy-path function call has not demonstrated these properties.
