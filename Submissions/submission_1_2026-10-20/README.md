# Submission 1 — October 20, 2026

**Assembled locally for Executioners.** The provided contact is set in the ignored manifest. This is a one-task UM development packet: three fresh trials of frozen actor `03c845d`, each officially graded **1, 21/21 checks**. It is not a full-domain or full-benchmark result.

## Files

- `packet/2026-10-20-submission_1/`: the 17-file packet, with manifest, CSV, derived run descriptor, provenance, README, three native result records, original official scorecards/rewards and compressed trajectories.
- `submission_1_2026-10-20.zip`: a ZIP of that packet directory only. Extract before using the leaderboard validator; ZIPs are not allowed inside the actual packet. Supporting private evidence is deliberately outside this archive.
- `evidence/`: original run/evaluation/event records, SQLite snapshots, official receipts and selected exports, prior development history, Git source snapshot, exact runtime source bytes and producer source.
- `validation/`: official validator reports, independent integrity audit, per-file/source hashes, archive verification and contract/schema/validator identities.

## Actual validation

The unchanged official leaderboard validator at `a321b9e9603ad8431c13911729eaf213a5d3b870` exited **0**, reporting **0 errors and 3 warnings** (`needs-review`). All three native `result.json` files exceed the 200 KiB soft limit (389,387 / 267,664 / 364,608 bytes), while remaining below the 2 MiB hard limit. They are preserved verbatim, not truncated to suppress the warnings.

The independent audit verified all 17 packet files, three exact native result copies, exact receipt-selected official scorecard/reward copies, and every decompressed transcript message against its read-only SQLite source. Transcript message counts: **91 / 52 / 69**. The manifest and CSV report **1 task, 3 trials**, not 3 tasks. Unknown cost is omitted. Two original local statuses remain unresolved; official scores are kept separate. Original operational result fields still say the official score was unknown when those files were written; the later unchanged official reward/scorecard and receipt contain the actual grades.

The packet is **1,205,590 bytes**; its ZIP is **314,246 bytes**, with all 17 members matching the packet byte-for-byte. ZIP integrity passed. Archive SHA-256:

```text
0ae7281659ce68e47dd5f35830e7b7fcbeb030fae56cdb322a8880c0f8d0939f
```

Root independently passed the **3 packet producer tests**. The actor package was not changed or rerun. Its archived runtime bytes match the exact frozen trial source fingerprint. No model inference, provider credentials or external publication were used to assemble this packet.

## Format and publication limits

The original execution was the standalone HealthHarnessCodex runner, not Harbor. Each packet `result.json` is the real native result, unchanged. Trajectories contain faithful native engine messages under `health-harness/native-transcript/v1`; the header's session ID is a declared SQLite-content hash, not a fabricated model/Harbor session. `sub.yaml` is explicitly a derived native configuration export because these trials did not originate from a `cb submission` YAML.

Schema/file validation does not establish maintainer acceptance of this native producer format or a one-task subset within a domain. Those points remain **unconfirmed**. The [published workflow](https://www.actava.ai/benchmarks/submit) documents domain-level partial submissions; it does not explicitly resolve these two cases. The packet therefore retains `publication_ready: false`. No PR, upload, push or public submission has occurred. Raw transcripts/supporting evidence can contain private case and protected reference responses and remain ignored/local-only.

## Reproduce

Producer: `../tools/assemble_native_packet.py`. It first invokes the existing pilot integrity/comparability validator, refuses to overwrite an existing packet, preserves actual scores/statuses and checks the exact file allowlist. It uses the existing Docker runtime's upstream zstd-19 packer; no host installation is required. It is deliberately scoped to this frozen three-trial pilot, not a generic full-benchmark producer.

Use a **new output directory** for any rebuild. Supply `--pilot-root`, `--output-root`, `--submission-id submission_1`, `--date 2026-10-20`, `--team Executioners` and the user-provided `--contact`. Never modify generated packet files to hide validator warnings; change/review the producer and preserve the previous assembly.

Run the official local validator with the packet DIRECTORY, not this wrapper folder or ZIP: `python Runner/leaderboard/scripts/validate.py Submissions/submission_1_2026-10-20/packet/2026-10-20-submission_1`. Its existing Docker runtime has the required dependencies. Tests use bundled Python: `python -X utf8 -m unittest discover -s Submissions/tests -v`.
