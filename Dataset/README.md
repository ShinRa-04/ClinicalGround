# Local benchmark datasets

The downloaded data lives here, separately from the official benchmark code and run tools in `Runner/`.

| Location | Contents |
| --- | --- |
| `chi-bench/` | Complete public release, task instructions, fixtures, shared worlds, assets, metadata, download caches, and release pin |
| `chi-bench/skills/` | Separately downloaded restricted Managed-Care Operations Handbook and its download cache |
| `receipts/` | Original download receipts and the SHA-256 relocation inventory |

All contents except this README are local-only and ignored by the parent repository. Credentials remain in the ignored runner authentication cache, separately from dataset files. Never redistribute the handbook or publish the runtime image containing it.

Public release: `chi-bench-v1.0.0`, resolved commit `5ce88104df2a91e057619eb70fb51f56fc5949eb` (2,505 repository files). It includes the 75 core competition tasks, 23 additional provider-payer tasks, and marathon material. Handbook commit: `f1210b294904792541116852f6074df8b84d89dd` (1,292 repository files). Local official repairs are described in [setup state](../Progress/LOCAL_SETUP.md).

October 17 relocation moved 11,396 local files, including caches, from `Runner/chi-bench/data/` to `Dataset/chi-bench/`. Every file's SHA-256 matched before and after. Original download receipts retain their historical destinations; `receipts/relocation-20261017.json` records the current location and inventory.

Use the root-level launcher:

```powershell
.\Runner\toolkit.ps1 doctor
.\Runner\toolkit.ps1 cb data verify
.\Runner\toolkit.ps1 download-public
.\Runner\toolkit.ps1 download-handbook
```

The launcher mounts this folder at `/dataset` inside Docker. Commands use `/dataset/chi-bench` as the data root; the original benchmark checkout has no data copy or link. For a future individual trial, pass its task path under `/dataset/chi-bench/<domain>/tasks/<id>`. No model-driven trial has been executed.

Sources: [public dataset](https://huggingface.co/datasets/actava/chi-bench), [gated handbook](https://huggingface.co/datasets/actava/managed-care-operations-handbook).
