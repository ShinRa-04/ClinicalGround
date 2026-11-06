**Correction after the real-reference check:** the initial corpus/index caps
excluded needed policies. Complete collection/global ranking and user-approved
fixed-reference vector caching now replace prefix ranking. Final-logic checks
retrieve 9/9 expected sources in the top five, with qualifications verified on
four relevant queries. See [candidate audit and limits](RETRIEVAL_CANDIDATE_CHECK.md).
The earlier two-document GPU smoke was insufficient for coverage validation.

# Hybrid retrieval implementation - October 23, 2026

## Authorized goal and current scope

The user approved exact structured retrieval for patient identifiers, codes,
forms and current status; hybrid lexical/semantic discovery for policies and
narrative documents; and original text with surrounding qualifications and
metadata. The user then requested GPU use and said they will execute the next
benchmark test. Root implemented directly. No delegated agents, fresh benchmark
actor run, provider API call or paid judge call was used for this work.

## Implemented

- `case.retrieve_evidence` and existing actor reads remain the exact structured
  path. Semantic results cannot establish identity, code equality or fresh state.
- `case.search_narrative` ranks text fields from explicitly named successful
  original observations in this exact case. Results carry original evidence ID,
  text pointer and text hash. Identifier/status/code fields are excluded. Its
  index is in memory and discarded on namespace change. A private SQLite query
  cache now binds its case/encoder and source/config hashes; patient/query data
  is never learned across patients or shared between them.
- `workspace.hybrid_search` collects only files permitted by the existing
  current-case/reference path guard, then ranks their text using BM25 and dense
  cosine similarity, combined through reciprocal-rank fusion. No vector server
  or hosted embedding API is used. A full manifest is rechecked on each search; cached source text is reused
  only while that complete manifest is unchanged. PDF handling uses text layers, not OCR.
- Results retain exact original character spans, file hashes/PDF page metadata,
  document headers, neighboring text and bounded exclusion/exception/definition
  sections. Markdown links remain visible but are not followed automatically.
  Qualifier context is explicitly incomplete; rankings are not eligibility
  decisions. Policy records can cite original search evidence and exact nested
  text pointers. Case-authored opinions cannot become policy merely by ranking.
- Source excerpts survive working-context projection. Chunk hashes permit
  reuse of unchanged embeddings within the same index; changed/removed source
  chunks are evicted. No patient-derived vector cache is persisted globally.
- Hybrid search does not silently degrade to lexical-only search. If the local
  embedding backend fails, tools report `semantic_backend_unavailable` and
  `semantic_executed=false`; exact/literal tools remain available explicitly.

Source: `HealthHarnessCodex/health_harness_codex/hybrid_search.py`,
`docker_bridge.py`, `engine.py`, `working_set.py`, `policy_grounding.py`.

## GPU runtime and provenance

Verified hardware: NVIDIA GeForce RTX 4050 Laptop GPU, 6,141 MiB VRAM.
Initial CPU choice was a portability assumption, not a model capacity limit.

- Local encoder: `BAAI/bge-small-en-v1.5`, 384-dimensional vectors.
- FastEmbed GPU 0.9.0; ONNX Runtime GPU **1.23.2**, CUDA 12.8.1/cuDNN runtime.
- Latest unconstrained ONNX wheel initially expected CUDA 13 and failed the
  smoke check. Pinned 1.23.2 resolves that mismatch. No silent CPU fallback.
- Pinned image:
  `sha256:7511bbf140ee9f29937cce74e002f140762f39bb24f4abbea65bae26ede7c1c7`.
- Public model-file manifest hash:
  `dec6361296a7075c148f94f899b3345cca70956be40bed593ddea795578b285f`.
- Model/runtime selection is saved in ignored `HealthHarnessCodex/retrieval.local.json`.
  It is included in batch source identity, frozen configuration and native
  evaluation provenance. A changed runtime invalidates an in-flight source pin.

Setup downloads public model weights. Actual inference uses short-lived Docker
containers with GPU access, `--network none`, read-only root filesystem and no
host data/credential mounts. Text enters via stdin. The 3 GB Docker memory cap
is host RAM, not GPU VRAM. The separate benchmark runtime image was not changed.
No unrelated container was started.

Generative actor/helper calls still count against the 48-call budget. Embedding
inference is real local model computation, recorded separately in tool results
as inference requests, embedded texts/query requests and elapsed time. It is not
an extra Codex/Opus request and incurs no provider API token charge. Do not call
embedding inference free computation or hide it in performance reporting.

## Current bounds and limitations

Complete collection follows internal transport pages; those pages are not
independent ranked corpora. Ceilings: 5,000 files, 50 MB raw bytes, 10 MB per
file, 1,000 PDF pages; index ceilings: 10,000 source/page documents, 50 million
text characters and 60,000 chunks. Unsupported sources or exceeded limits
produce explicit coverage errors, not partial-prefix search results. Output
remains bounded to 4,000-24,000 characters; returned qualifier context can be
partial and does not establish clinical applicability.

The user approved sharing fixed reference embeddings across cases. Only trusted
static-handbook chunks use the ignored SQLite reference-vector cache. Patient
records, queries and decisions never enter it; patient narrative indexes remain
case-local. Cold builds embed bounded GPU batches and cache each completed batch.
The encoder/image identity and source content determine reuse. No controlled
GPU-versus-CPU speedup or clinical-performance improvement is claimed.

The original unrelated-query control returned candidate policies before the
subsequent [calibrated relevance screen](RETRIEVAL_RELEVANCE.md). That screen
now rejects the tested controls; it is not a universal no-match guarantee.
See the candidate audit for historical ranking results and cache confirmation.

## Verification actually executed

Software: full suite initially 487 passed / 60.313s, then 490 / 45.821s and
491 / 60.643s with PDF/provenance/continuation tests. Expected embedding-failure
feedback was subsequently checked by 31 focused tests. Final full suite:
**491 passed / 51.051s**, `runs/20261023-hybrid-release-repeat.log`.
One preceding full run failed an existing deferred-grading test because a
synthetic snapshot hit PermissionError; that test passed isolated, then the
full repeat passed. Preserve this intermittent issue as open. No unrelated
simulator or snapshot implementation was changed.
Tests use synthetic vectors for algorithm mechanics, not as evidence of real
embedding relevance. Existing exact retrieval and case guards remain covered.

Actual local GPU hybrid smoke: two synthetic documents, query "cardiac
evaluation", top result the heart-clinic document. Its BM25 score was zero;
cosine was approximately 0.768. This demonstrates meaning-based retrieval on
that example only. CUDA provider confirmed; complete cold smoke 21.843 seconds,
zero actor/paid calls, no benchmark case. Receipt:
`HealthHarnessCodex/runs/20261023-hybrid-gpu-smoke.private.json`.

Separate ONNX execution profiling verified **95 CUDA node executions**, including
Attention and MatMul, with two CPU node executions (Gather/Unsqueeze). This
confirms actual GPU work, not merely an installed CUDA provider. Node counts
are not percentages of runtime or a VRAM measurement. Receipt:
`HealthHarnessCodex/runs/20261023-gpu-node-profile.json`.

The user will run the fresh benchmark attempt. Prior t021 8-pass/3-fail/1-N/A
partial results remain unchanged. No official strict/semantic score is claimed.

## Setup and next user-run test

The GPU image is already built/pinned on this PC. Rebuild when intentionally
updating runtime/model dependencies:

```powershell
cd C:\Projects\BigData
.\Runner\toolkit.ps1 build-retrieval
```

With Docker Desktop running, launch a fresh one-case run (not a resume):

```powershell
cd C:\Projects\BigData\HealthHarnessCodex
& 'C:\Users\prath\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -u -X utf8 -m health_harness_codex.batch `
  --dataset-root C:\Projects\BigData\Dataset\chi-bench `
  --run-dir runs/20261023-hybrid-t021-06 `
  --domains pa_provider `
  --task-id pa_t021_t021_o003_p01_new_referral_provider `
  --concurrency 1 --attempts 1 `
  --max-model-calls 100 --max-tool-calls 500 `
  --simulator-backend codex --simulator-max-model-calls 8
```

Grading is deferred by default. This command starts no paid judge. Do not reuse
the run directory for a fresh attempt after execution; preserve old evidence.

Primary dependency references:
[FastEmbed](https://qdrant.tech/documentation/embeddings/fastembed/),
[ONNX CUDA provider requirements](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html),
[ONNX Runtime GPU 1.23.2](https://pypi.org/project/onnxruntime-gpu/1.23.2/).
# Relevance screen and lifecycle update

The native retrieval tools now apply calibrated basic-relevance cosine floors
before fusion and report indexing/cache/retrieval progress in run logs. This
does not decide clinical applicability. See [calibration and its remaining
broad-query limitation](RETRIEVAL_RELEVANCE.md). The subsequent
[recovery/cache repair](RECOVERY_AND_CACHE_REPAIR.md) adds per-document static
reuse, coordinated indexing and a private case-query cache. Only identical
queries can reuse results; similarity scores alone do not replace retrieval.
