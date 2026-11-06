# Evidence and verification state

The research is a general engineering handbook with scoped reference cases, not a claim to know literally every implementation detail or future release. General design contracts are synthesis/proposals; product findings carry evidence statuses and version limits.

## Evidence layers

- General foundations: 18 primary documentation/engineering pages inspected during research, with source/section/status/limit records. All 18 raw-page captures succeeded; captured hashes identify bytes, not factual entailment.
- Hermes: 60 scoped findings at e6f57427c198cfd96854522b7a9159eb007e13c2. The final checks of the originating workstream were interrupted by an account usage limit after artifacts were written; the integrator and fresh independent reviewer subsequently checked the recorded source ranges/hashes and sampled consequential claims.
- OpenClaw: 75 scoped findings at 3b3492490602f5080d3fbe7d2df9618cdb82ea9a. No upstream runtime/test execution.
- Broader comparison: 35 scoped findings, 24 captured sources, selected Pi/LangGraph/Letta pins and scoped historical abstract descriptions. No upstream runtime/test execution.
- Total implementation/comparative findings: 170. Static code inspection, documentation, ambiguity and inspected test assertions remain different statuses. No source finding is upgraded to executed because its locator/hash passes.

## Executed synthetic checks

[Lab receipt](verification/lab_receipt.json): 17 tests passed, zero failures/errors/skips, integrator Python 3.12.14. The independent reviewer separately ran the same 17 tests with Python 3.11 and reported zero failures/errors. These are two runs of the same synthetic examples, not 34 different behaviors or upstream test passes.

The lab examines explicit protected context and atomic call/result units, exact memory scope/provenance/version/tombstone examples, a supported-receiver lost-acknowledgement path and stale-publication rejection. Its README excludes semantic summary fidelity, full provider protocol validation, authentication, distributed concurrency, power-loss safety, full deletion or arbitrary external exactly-once guarantees.

## Independent review

[Independent review](review/INDEPENDENT_REVIEW.md) and [receipt](review/review_receipt.json) record the selected high-consequence semantic checks, source identity verification, lab execution, observations and explicit review limits. The reviewer authored none of the inspected general/case/comparative/lab material. This is a bounded independent agent review, not a blind study, human expert certification, production security audit or exhaustive proof of every claim.

Final integration/link/coverage verification **passed**: [validation receipt](verification/validation_receipt.json) records 177 source identity checks, 38 topic mappings, exact document/link/anchor counts and the stated synthetic test result. That checker establishes structure, source identities and honest evidence/status boundaries. It cannot decide every source claim's semantic truth. Commit completion belongs to the integrator and is checked separately in Git.

[Integrator dispositions](review/INTEGRATOR_DISPOSITIONS.md) preserve the review issues and fixes. Incorrect coverage citations were corrected and independently rechecked; the diagram was corrected to preserve an inconclusive reconciliation branch. Remaining final consolidation was performed in the main chat as the user requested, without another agent review round. The independent review receipt freezes its own earlier artifacts rather than claiming to certify all later edits.

## Scope not executed

No reference application was installed/started, upstream test suite executed, model/provider called, personal service connected, visible browser launched, Docker started, protected handbook or hidden benchmark data inspected, actual memory index benchmark run, deployment concurrency fault experiment executed, or healthcare benchmark trial performed. Proposed contracts/failure cases in the general chapters remain proposals except for the named synthetic subset.

## Commands

```powershell
python HarnessResearch/tools/build_index.py
python HarnessResearch/tools/run_labs.py
python HarnessResearch/tools/validate_research.py
```

`tools/collect_foundations.py` optionally reuses/captures raw primary pages under ignored _cache/; a refresh is new source data, not automatic revalidation of old interpretations. Hermes/OpenClaw evidence builders read the exact ignored source pins without importing/running upstream code. Preserve pins and receipts when updating this research.
