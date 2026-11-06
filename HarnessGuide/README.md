# Dataset workflows and the implemented healthcare harness

**Latest completion correction:** testcase completion means no further useful
permitted action remains, supported by recorded effects and original sources.
The audit, finalizer and reporting now use consistent contract semantics;
pending case status alone is insufficient. Read the
[completion implementation and verification](../Progress/COMPLETION_REPAIR.md)
alongside older diagrams below.

**Latest stage-responsibility update:** the case owner's work guidance changes
with observed stage and assigned obligations. Assignment audit, a verified MD
information-request handoff and one bounded automatic readonly blocker review
are implemented. See [current design and execution evidence](../Progress/UM_ASSIGNMENT_STAGE_REPAIR.md).
The audit checks structural effects; it does not decide clinical correctness.

**October 24 implementation update:** operational helpers now support delegated
tools and separate contexts, and the batch runner defaults to helper mode.
The older architectural explanation below predates this change. Read the
[current delegation/recovery design and diagram](../Progress/IMPLEMENTATION_RECOVERY_HELPERS.md)
alongside it for actual capabilities, configuration and executed verification.

Prepared October 22, 2026, from implementation source at `9fd27cd` and the
subsequent verification notes. This is a shareable explanation of structure and
behavior. It contains no patient-record values, credentials, protected handbook
extracts, hidden expectations, or private run payloads.

Read in this order:

**Terminology:** keep the [plain-language glossary](GLOSSARY.md) alongside the
guides. Start there for provider actor, payer, role versus agent, case versus
patient, context, packet, verdict and the different meanings of complete.

1. [One example from each dataset domain](01_DATASET_WORKFLOWS.md): what the
   records represent, how they connect, which operations move work forward, and
   what the output means.
2. [How the actual harness works](02_IMPLEMENTED_HARNESS.md): model roles,
   execution control, tools, memory, inputs, outputs, diagrams, and reasons for
   each major design choice.
3. [Complete responsibility and tool reference](03_ROLE_AND_TOOL_REFERENCE.md):
   all 66 responsibility definitions and the declared domain tool catalogs.
4. [Measured context-bloat analysis](04_CONTEXT_BLOAT_ANALYSIS.md): exact prompt
   reconstruction, repeated/duplicated material, native-inference telemetry,
   uncertainties and proposed repair priorities.
5. [Judge API input/output analysis](05_JUDGE_CONTEXT_ANALYSIS.md): its separate
   token/cost breakdown, large evidence input and redundant acknowledgment call.

The important distinction throughout is **a responsibility, a model call, an
environment operation, and a verifier check are different things**. The current
normal runner has one combined workflow actor per case. It does not deploy 66
independent staff agents.

The Markdown and Mermaid diagrams can be shared together as this folder. A
Mermaid-capable viewer renders the graphs; otherwise their source remains
readable. Relative code links require the corresponding project checkout; the
explanations themselves do not require private dataset files to understand.

Current measured limits are in the implementation guide's verification section.
Operational continuation details remain in [Progress/HANDOFF.md](../Progress/HANDOFF.md).
