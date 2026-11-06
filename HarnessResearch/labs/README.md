# Executable design-invariant lab

This is a small **synthetic teaching lab**, written for this research. It does not import, install or execute Hermes, OpenClaw, Pi, LangGraph, Letta or a model SDK. It makes no network/provider calls. It is not our production harness, an application security system, a retrieval/semantic-quality benchmark or a proof of an optimal architecture.

Run from the project root with Python 3.10+:

```powershell
python -m unittest discover -s HarnessResearch/labs -p "test_*.py" -v
```

The test runner below records a receipt without retaining temporary databases:

```powershell
python HarnessResearch/tools/run_labs.py
```

## What it exercises

- Context projection protects an explicit unresolved request, reserves a supplied output budget, keeps whole tool-call/result units, rejects orphans/duplicate call IDs and leaves the canonical input intact.
- A small SQLite memory store demonstrates exact principal/scope filtering, untrusted-origin propagation, single-parent tombstone propagation, rejection of a known deleted/out-of-scope origin, optimistic version checking and connection-restart persistence.
- A local action journal plus simulated idempotent receiver demonstrates a lost-acknowledgement/restart path, same-key/different-intent rejection and a publication fence for superseded owners.
- An intentional counterexample shows that a local journal/checkpoint does not deduplicate a receiver that ignores request identity.

## Important limits

Token costs are supplied synthetic estimates, not real tokenizer/model-window accounting. The lab does not produce or grade natural-language summaries, validate every provider's message protocol or preserve opaque provider state. “Protected” means explicitly flagged in these fixtures, not automatically discovered from real instructions.

The memory store is not authentication/authorization middleware: callers supply the principal. It supports one parent per entry, exact scope matches and known-ID tombstones, not arbitrary provenance DAGs, semantic deduplication, an embedding index, retention law, physical erasure, backups or prevention of unrecognized re-ingestion under a new origin ID.

The action lab is sequential. Its simulated receiver has an in-memory idempotency contract, no network, no retention expiry and no independent server crash. The local ownership check illustrates publication fencing but is not a distributed/atomic check-and-update protocol under concurrent writers. A stale in-flight external effect is not revoked by that fence. Power-loss, thread/process races, real permissions and every external API's retry semantics are outside the tested scope.

The receipt states which tests ran and passed. It must not be described as upstream tests passing, production crash safety or end-to-end exactly-once execution.
