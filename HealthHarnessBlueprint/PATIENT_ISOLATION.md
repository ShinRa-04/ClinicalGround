# Patient isolation is a hard design requirement

The user's requirement is that one patient's data must not influence how a role/agent works with another patient. The proposed design therefore reuses **job definitions and approved general knowledge**, not patient-derived memories, summaries, habits or learned procedures across patients.

## Reusable role does not mean reusable patient context

A role definition is a versioned job description: responsibilities, allowed tools, output contract and approved general procedures. The same PA role definition can be used for two patients. Its patient working context, evidence, conversations, checkpoint and action history must not carry from one to the other.

A process/model-serving pool may be reused only through a stateless or verified-reset execution boundary. A provider-owned persistent thread must not be reassigned to another patient merely because a local mirror was cleared. Begin the new patient run with a new correctly scoped provider/session state, or demonstrate the actual reset contract before reuse.

Do not batch unrelated patients' working records into one model prompt or allow one role's running conversation to switch patients while retaining its history. Provider infrastructure may batch independent requests internally under its own contract; that does not justify mixing their application contexts. Provider-side retention/training/isolation controls require separate verification and are not established by this hypothetical layout.

## Scope key

An illustrative working namespace is `(environment, task/episode, organization, principal, patient, case)`. These are proposed logical fields, not assumed benchmark API fields. Resolve actual identities from the task/observations; fail or clarify ambiguous matches rather than using another patient's record.

Role instances, retrieved evidence, conversations, summaries, tool handles, caches and helper outputs carry the relevant namespace/version. The barrier is enforced before retrieval disclosure, context assembly, delegation and mutation—not merely by asking the model to ignore irrelevant data after it has already seen it.

## Sharing policy

| Surface | Proposed rule |
| --- | --- |
| Job definitions and approved general procedures | Read-only shared versions; no patient-derived automatic edits |
| Approved policies/reference documents | Shared where applicable; determine current product/setting/version per case |
| Patient chart/evidence and derived facts | Current patient/case and actual permission only |
| Conversation answers, consent/refusal and representation facts | Current participant/patient/episode scope; never a staff preference profile |
| Summaries, checkpoints and episodic recall | Same permitted patient/case/task scope; excluded from cross-patient recall |
| Patient-derived procedures/“lessons learned” | No automatic promotion into another patient's workflow or shared role prompt |
| Tool-result/retrieval cache | Partition or verify resource/namespace/version; no wrong-case reuse |
| Model prompt cache | Share only eligible stable general prefixes as permitted; never concatenate another patient's context |
| Audit/operational logs | Controlled storage, not an acting agent's cross-patient memory corpus |
| Model training/fine-tuning | No patient-driven weight update in this design; provider retention/training controls require separate verification before any real deployment |

Even de-identification is not treated here as automatic permission to teach one patient's specific experience into another patient's role behavior. General procedure updates would be a separately governed, explicitly requested activity, outside this per-case harness behavior.

## Same patient, another episode

Do not implicitly carry a previous task's hidden working notes into a new episode. Re-obtain allowed patient information from the current environment/task or an explicitly authorized continuity source. Same identity alone does not prove every earlier record, organization or purpose is in scope.

## Operational state is a different input

Actual available appointment slots, current tool capacity or a task's permitted queue status can affect scheduling. Those are supplied operational facts, not the agent learning a clinical habit from another patient's data. The design should keep such inputs minimal and separately sourced; it must not inject another patient's chart or reasons into the current case. If a proposed operational view cannot preserve that distinction, disable or narrow it.

## Verification property

Hold patient B's allowed inputs, general procedures, supplied operational facts, model configuration and relevant randomness constant. Change patient A's records, dialogue, summaries and case memories. B's **constructed context, retrieved source set and permitted operation scope** should remain unchanged. Stochastic output need not be byte-identical without a real deterministic provider contract; test the data/control independence rather than inventing determinism.

Test namespace collisions, stale worker objects, reused provider threads, cross-case cache keys, retrieval-filter failures, contaminated skill/profile writes, mislabeled helper results, context compaction and restart. These are proposed acceptance tests; isolation has not been implemented or demonstrated by this document.
