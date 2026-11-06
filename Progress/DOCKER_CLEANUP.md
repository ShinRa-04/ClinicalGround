# Docker-only cleanup — October 17, 2026

## Scope and decisions

The user requested inspection of the roughly 16 GB Docker/WSL storage and deletion of everything unrelated to chi-bench, then explicitly reiterated deletion of the entirety of iGOT data. The scope remains Docker Desktop storage only. Normal Ubuntu/Debian distributions and Windows project/source folders are outside this request.

The current request authorizes removal of iGOT's persisted Docker data, superseding the earlier decision merely to keep its containers stopped. No database/queue backup was made as part of this deletion. Rebuilding iGOT later will require recreating its Docker images and persisted state.

## Before cleanup

- Docker Engine 29.8.2 was responding before any cleanup mutation. No new startup repair was needed in this session.
- Windows pagefile setting: initial 2,048 MiB, maximum 8,192 MiB. The user's maximum-size change is verified; allocated size at inspection was 2,048 MiB, not a fixed 8 GiB allocation. No pagefile change or reboot was performed by the agent.
- 14 Docker images, 0 containers, 3 volumes, 133 build-cache records. The earlier 16 iGOT containers were already absent on first inspection; the agent did not remove them in this session.
- Docker summary: images 6.726 GB, volumes 52.12 MB, build cache 10.69 GB. Image/cache accounting shares layers, so these figures must not be added as independent physical usage.
- Docker data VHDX: C:/Users/prath/AppData/Local/Docker/wsl/disk/docker_data.vhdx, 19,048,431,616 bytes. Docker's separate main/ext4.vhdx was about 100 MB.

## Deleted and verified

- 13 unrelated images: nine igot-skill-platform service images, igot/target-demo:local, igot/lab-workspace:local, rabbitmq:4-management, and postgres:16-bookworm. Exact IDs are in the ignored cleanup plan receipt.
- All 3 Docker volumes: igot-skill-platform_postgres-data (51.54 MB), igot-skill-platform_rabbitmq-data (580.5 kB), and empty anonymous volume 0e4ef32463807f41561c776717950fccfdd6e131e927d8ce717179de906b65e6. The database and queue data are deleted, not merely stopped.
- 104 old build-cache records, selected by exact cache IDs after preserving the chi-bench build graph and all its ancestors. BuildKit reported 6.817 GB reclaimed from those cache records. This is Docker accounting, not independently measured host-space recovery.
- Post-deletion inventory: exactly 1 image, 0 containers, 0 volumes, 29 cache records; all selected deletions absent and every protected cache ID still present. Only default bridge/host/none networks existed; none needed removal.

## Preserved and tested

- bigdata-chi-tools:4444a07, unchanged image ID sha256:1def01cb2eda40d029e5e1e52c4cf78379ddbfbc2ceca61d26cf9f35098a7999 (3.69 GB), plus 29 related build-cache records (3.874 GB including layers shared with the image). Generic base layers used by chi-bench remain necessary even when first pulled for an older build.
- Runner/chi-bench public release, local credentials/cache locations, planning documents, and research paper. Doctor ran successfully after deletion: chi-bench 1.1.0, Harbor 0.20.0, Engine 29.8.2, release chi-bench-v1.0.0, 25 public tasks per domain, 75 total.
- Handbook is still absent; the user reports access approved, but the runner is not logged in. Provider keys and scored-trial runtime are absent. No scored run or model call occurred.
- Normal Ubuntu and Debian registration paths were inventoried for comparison. Ubuntu remained running and Debian stopped when Docker was stopped for compaction. No global WSL shutdown or distribution unregister/delete was issued.

## Host-space reclamation

Deleting Docker objects freed internal filesystem space but did not immediately shrink the Windows VHDX. Docker's data filesystem showed approximately 7.8 GiB used after cleanup, including required Docker platform ISO cache and chi-bench layers. A targeted fstrim on /mnt/docker-desktop-disk reported 0 bytes trimmed; do not claim it reclaimed host bytes.

Stopped Docker cleanly and verified the exact Docker VHDX was not a reparse point and could be opened exclusively. First elevated compaction helper aborted before touching the disk because Docker had started again; the cause of that restart was not attributed. Rechecked zero containers, stopped Docker cleanly again, and launched the guarded helper. It uses only DiskPart select-vdisk, compact-vdisk, and exit against the exact detached Docker data disk; it never formats, deletes, or selects another disk.

Compaction completed successfully at 00:14:37 IST on October 17: DiskPart exit 0, file size 19,046,334,464 -> 9,952,034,816 bytes, a reduction of 9,094,299,648 bytes (about 9.09 decimal GB / 8.47 GiB). After normal Docker restart and toolkit checks, the disk measured 9,985,589,248 bytes (9.99 GB / 9.30 GiB), unchanged at a fresh 00:18:49 check. The user subsequently confirmed seeing it shrink. Host free space changed during other activity too; do not attribute its entire change to this operation.

Post-compaction verification passed: Engine 29.8.2, unchanged toolkit image ID, all 75 public tasks, exactly one image/29 protected cache records/zero containers/zero volumes, no iGOT image or cache-description matches. Ubuntu and Debian registration paths/versions remained unchanged and their disks remained present. An Ubuntu /bin/true control passed; Debian was not started.

At the 00:18:49 inspection, the remaining Docker layer store occupied about 6.29 GiB (approximately 5.21 GiB unpacked snapshots and 1.08 GiB compressed content), and the two current Docker platform ISOs occupied about 1.48 GiB. Total guest filesystem usage was about 7.79 GiB; the difference from the VHDX file size is filesystem/VHDX allocation overhead and unreclaimed allocated space. Do not add Docker's image-size and build-cache summary figures as if they were independent physical storage.

## Receipts and continuation

Local-only receipts live in Runner/logs/: docker-cleanup-plan-20261017.json, docker-df-before-cleanup-20261017.jsonl, docker-cache-before-cleanup-20261017.json, docker-cache-after-cleanup-20261017.json, image/volume/cache deletion logs, doctor.json, and compaction output/result files. These record metadata only and are ignored by Git.

Docker inspection used native image/volume commands and exact-ID BuildKit pruning, not broad system pruning or manual removal of internal Docker directories. The Docker data VHDX and Docker installation were preserved.

## Later chi-bench runtime build

The 9.30 GiB VHDX figure above is the 00:18 pre-runtime-build snapshot. Later legitimate chi-bench builds added a 4.71 GB private runtime image alongside the 3.69 GB controller; the runtime's two tags refer to one image. At 16:31 the VHDX was 24,321,720,320 bytes (22.65 GiB), with 75.31 GiB host free. This growth is not evidence that iGOT data returned.

After successful runtime checks, the obsolete controller image was removed. A generic shared=false cache filter reclaimed 0 bytes; selecting the 76 unused/unshared records by exact IDs then reclaimed 12.44 GB according to BuildKit. Both protected current image IDs remained unchanged. Final inventory: two distinct chi-bench images, zero containers/volumes, no iGOT images, and 13 non-reclaimable cache records (2.657 GB in Docker accounting). The existing images are marked reclaimable by Docker because no containers are running; DO NOT image-prune them indiscriminately.

No second offline compaction was performed. Docker internal free space and Windows VHDX file allocation are different measurements; do not claim the cache cleanup immediately returned 12.44 GB to Windows. See LOCAL_SETUP.md for the final functional verification and receipt paths.
