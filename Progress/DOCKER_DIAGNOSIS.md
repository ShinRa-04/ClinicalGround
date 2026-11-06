# Docker startup incident — October 16, 2026

## Scope and current state

Current update, October 17: the user's pagefile maximum is verified at 8,192 MiB (2,048 MiB allocated at inspection). Docker was healthy before cleanup and after successful VHDX compaction; see [Docker cleanup](DOCKER_CLEANUP.md). A later login attempt failed because Desktop/backend processes were absent and the engine unavailable. Started Docker normally and verified Engine 29.8.2 and toolkit doctor at 15:59 IST; no startup repair or new crash was observed. Zero containers are running. The incidents below are historical evidence, not proof that a stopped engine has relapsed.

October 16 at approximately 23:52 IST: a startup attempt failed with Windows virtual-memory exhaustion, a Docker UI module-load error/GPU-process crash, and a WSL-service crash (0xc00000fd). The failed session was stopped cleanly. See [Evening incident](#evening-incident--memory-pressure-and-ui-load-failure).

The user requested immediate repair and an explanation of recurring Docker Desktop crashes, initially placing χ-Bench on hold. After the update and verified restart, the user explicitly resumed χ-Bench and selected Docker-contained tools. Docker and the earlier native LiteLLM compilation failure are independent issues.

Docker Desktop officially supports Windows. WSL 2 is its normal Linux-container backend; moving a Python installation into WSL does not repair a Windows-host Docker startup failure.

The USER completed the Docker Desktop update and reported success. Live verification confirms Desktop 4.95.0.242831 and Engine/client 29.8.2. An isolated Alpine container passed, a graceful shutdown exited 0, and a subsequent normal startup and second Alpine check passed WITHOUT manually refreshing socket files. The failure reproduced under 4.50.0 did not recur in this post-update clean stop/start check.

October 16 inspection found all 16 iGOT containers stopped/restart-disabled. On October 17 they were already absent before cleanup; the user then authorized deleting its Docker images and persisted database/queue volumes. Those objects are now deleted, as recorded in DOCKER_CLEANUP.md. No host compiler was installed and no scored trial has run.

This verifies the observed startup regression after the update. Sleep/wake, Windows reboot, and long-term recurrence have not been tested; do not claim permanent immunity to every Docker failure.

## Confirmed observations

- Before update: Docker Desktop 4.50.0.209931; Engine 28.5.1 when responding. Current verified versions are 4.95.0.242831 and Engine 29.8.2.
- OS from CIM: Windows 11 Home Single Language, build 26300; registry DisplayVersion 26H2, UBR 9711. The legacy registry ProductName incorrectly says Windows 10; use CIM for the product name.
- afunix.sys file version: 10.0.26100.8972. This version relationship alone does not prove an incompatible driver.
- Startup logs report fatal failures at C:/Users/prath/AppData/Local/Docker/run/dockerInference, then at C:/Users/prath/AppData/Local/docker-secrets-engine/engine.sock.
- engine.sock retained a creation/modification timestamp of October 5, 2026, 12:55:43 IST.
- Both entries enumerate as zero-byte reparse points with attributes 1056. Those attributes alone do not establish corruption.
- With the Docker backend stopped, a read-only CreateFileW no-follow metadata probe returned error 1920 (ERROR_CANT_ACCESS_FILE) for both socket entries. The same probe on an ordinary temporary file succeeded.
- Parent directories have inherited access and grant the user's account Full Control. Socket-specific ACLs were not established; parent permissions alone do not establish socket permissions.
- A fresh AF_UNIX control using native Windows Winsock succeeded at startup, bind, listen, close, and unlink. The test used a project-cache path and cleaned up its control file/directory. Windows AF_UNIX functionality is therefore not generally absent or nonfunctional on this host.

## Explanation and uncertainty

The immediate failure chain is established: Docker initializes a host service, attempts to remove/rebind an existing Unix-domain socket, Windows rejects access, and Docker aborts startup before the Linux Engine API becomes available. Subsequent launches encounter the same persisted objects, which can sustain a startup failure loop across projects.

Similar reports exist in Docker's issue tracker, including both endpoint names and reports following normal stop/start. Docker's later release notes list a stale-socket startup fix. The installed version predates that fix. Those sources support a known failure class; they do not prove the original trigger or a specific kernel/filesystem defect on this machine.

Do not claim confirmed NTFS corruption, proven antivirus interference, a particular driver defect, universal Windows incompatibility, or a χ-Bench-specific Docker bug. Unclean shutdown/sleep is a reported possible trigger, not established from this machine's events. No relevant recent unexpected-shutdown event was established in the query.

## Actions actually taken

1. Started Docker for the requested local setup; its Windows application failed before any benchmark task or image build ran.
2. With Docker processes absent, verified Docker/run contained only runtime socket entries, preserved it as C:/Users/prath/AppData/Local/Docker/run.stale-20261016-133305, and recreated an empty run directory. No VM disk or persistent Docker data was removed by the agent.
3. Startup advanced to a second failure at the secrets-engine socket. A proposed secrets-directory refresh was blocked by process-presence checks and did not occur.
4. The user reported choosing factory reset and then Gather diagnostics. Their outcome is not independently assumed. Existing iGOT containers were subsequently observed, so do not claim all Docker data was erased.
5. A graceful docker desktop stop --timeout 20 timed out, reporting remaining processes. Later inspection showed only the diagnostic collector, and then no collector. Completion, upload, diagnostic ID, and archive location were not verified.
6. A later proposed two-directory refresh was also blocked by new running Docker processes; no second refresh occurred. Docker Engine then responded successfully. The cause of this recovery has not been isolated between user actions, queued lifecycle operations, and changed runtime state.
7. At 13:47:58 IST a normal restart reproduced the secrets-engine failure. The restart CLI eventually exited with a startup timeout. Used the official docker desktop stop --force --timeout 20 to stop the failed application; no user containers were running.
8. At 13:50:24 IST both socket-only directories were successfully renamed to preserve their previous entries: C:/Users/prath/AppData/Local/Docker/run.stale-20261016-135024 and C:/Users/prath/AppData/Local/docker-secrets-engine.stale-20261016-135024. The new secrets directory existed by recreation time, so New-Item reported an existing-item error; reinspection confirmed that BOTH old directories were preserved and BOTH active paths existed empty before startup. No persistent Docker data directories were moved.
9. Started Docker normally. Engine 28.5.1 responded; all 16 iGOT containers remained stopped with restart policy no. Ran an existing alpine:3.22 image with --rm, --pull=never, --network none, --read-only, and dropped capabilities. It printed Docker-container-check-passed and was removed automatically. No image download or project service launch was needed.
10. The next graceful docker desktop stop --timeout 30 exited 0. Verified no Docker Desktop/backend processes remained. Fresh socket entries from the recovered run were left in their ordinary active paths. Started Desktop again without refreshing them to test actual restart reliability; result pending.
11. That startup failed at dockerInference at 13:53:02 IST. This is a reproduction after successful graceful shutdown, not evidence limited to an unclean-shutdown trigger. The user also reported the same current error. Do not say Docker is currently fixed or healthy based on the earlier successful run.
12. Preparing the official Docker Desktop 4.95.0 x64 installer from https://desktop.docker.com/win/main/amd64/242831/Docker%20Desktop%20Installer.exe . Official SHA-256 from the release notes' checksum link: 73431db38491f770543880366228a23c993f84d1e8e045f56d83b8a98940cf76. Download destination: C:/Users/prath/AppData/Local/Temp/DockerRepair-20261016/Docker Desktop Installer 4.95.0.exe. Require matching checksum AND valid Docker Authenticode signature before execution. The shell is not elevated; the existing all-users installation requires a Windows administrator consent prompt for update.
13. Download completed: 636,811,696 bytes; checksum matched the official value; Authenticode status Valid, signer Docker Inc. Rechecked both before requesting the elevated installer launch. Stopped the failed Desktop with the official force-stop command.
14. The user then said they were running the update and instructed the agent to wait. The agent stopped its own control/monitor PowerShell process (PID 18444). Windows had already launched the elevated installer (PID 19040) before that cancellation completed; it was not killed mid-installation. Do not describe the elevated installer as never launched or the update as completed. No further installer launch or Docker mutation should occur until the user finishes.
15. The user reported successful update. Verified the installed executable version 4.95.0.242831 and Engine/client 29.8.2. Initial post-update Alpine execution passed; no iGOT containers were running and all 16 retained restart policy no.
16. Ran a normal docker desktop stop --timeout 30: exit 0, no Desktop/backend processes remaining. The inference and secrets sockets were removed; the old userAnalyticsOtlpHttp.sock.stale entry remained preserved. No manual socket refresh was applied.
17. Started Desktop normally with start --detach, waited for its Engine pipe and API, and confirmed Engine ready. A second isolated Alpine execution printed Clean-restart-container-check-passed. Final checks: 16 iGOT containers, 0 running, 0 restart-enabled; 0 total running containers. The clean stop/start regression test PASSED.

## iGOT lifecycle steering

The user explicitly stated that iGOT is on hold and should not run continuously, and clarified that THEY manually stopped its containers. Our pre-change inspection already showed exited states. All 16 containers whose names start with igot- were confirmed to belong to Compose project igot-skill-platform. The agent's material change was setting their runtime restart policies to no; the stop command issued afterward was a no-op for already-stopped containers. All were verified running=false. Do not attribute the initial shutdown to the agent. No containers, images, volumes, or Compose files were deleted or modified. Recreating containers from Compose in the future can restore policies declared in that project's source configuration.

## Next steps

The requested post-update checks are complete. No further Docker restart testing is necessary unless a new symptom or user request warrants it. If the fault recurs, collect the new exact error, version, timestamp, and affected socket path before choosing a repair; do not return to repeated factory resets or claim that a prior successful cycle proved every future case. Keep iGOT stopped. The user has resumed χ-Bench with Docker-contained dependencies; the unused native compiler prerequisite remains unresolved and does not block that selected approach.

## Primary references

- Windows support: https://docs.docker.com/desktop/setup/install/windows-install/
- Docker release notes: https://docs.docker.com/desktop/release-notes/
- Matching issue reports (community observations, not blanket vendor endorsement of remedies): https://github.com/docker/desktop-feedback/issues/554 and https://github.com/docker/desktop-feedback/issues/448 .

Keep raw diagnostic bundles private; do not upload or publish one as part of this project without user authorization.

## Evening incident — memory pressure and UI load failure

The user reported receiving handbook access. The toolkit first found Docker unavailable; no Desktop/backend processes were present. A normal `docker desktop start --detach` returned 0, but the application then failed. No handbook download, runtime build, model call, or task execution began.

### Verified evidence

- Windows refused a Docker CLI process launch with “The paging file is too small for this operation to complete.” A subsequent `docker desktop status` command itself failed with `fatal error: runtime: cannot allocate memory`.
- System event 2004 records low virtual memory at 23:44:08 IST (before this startup attempt) and 23:52:06 IST. These are host-wide memory-pressure events, not evidence limited to a benchmark container.
- CIM: 15.63 GiB physical RAM; 19.63 GiB total virtual-memory limit. AutomaticManagedPagefile=false, pagefile initial size 2,048 MiB, maximum 4,096 MiB, allocated size 4,096 MiB. Low pagefile usage alone does not rule out commit-limit exhaustion.
- Existing user .wslconfig caps WSL memory at 2GB, processors at 8, swap at 8GB. It was read, not edited. Linux swap does not change the verified Windows pagefile setting.
- Electron log at 23:52:17.864 IST: `dd/assets/VolumesScreen-B9wA1b8s.js` failed with `net::ERR_FAILED`. At 23:52:18.042, Electron recorded its GPU child process crashed, exitCode=34.
- Read the installed app.asar header and exact asset bytes without changing the archive. The screenshot's module exists at build/desktop-ui-build/assets/VolumesScreen-B9wA1b8s.js; all 27,163 bytes read successfully and match the archive's SHA-256 integrity entry. This specific asset is neither missing nor inconsistent with its packaged checksum. It does not verify every asset or establish the cause of Electron's request failure.
- Docker backend reports its WSL bootstrap failed with exit status 0xc00000fd. Application event 1000 at 23:52:32 IST independently records wslservice.exe 3.0.3.0 crashing in ntdll.dll with the same exception code. Do not conflate this with the earlier dockerInference stale-socket incident or claim memory pressure proves the WSL crash's exact cause.
- Stopped the failed Desktop session using `docker desktop stop --timeout 20`, exit 0. No Desktop/backend processes remained. Free physical memory increased from a preceding 2.28 GiB snapshot to 4.01 GiB; free virtual memory from 1.96 to 3.51 GiB. These are different-time snapshots, not a controlled measurement of Docker's exact memory footprint. Did not shut down Ubuntu or other WSL distributions, change pagefile settings, reboot, reset Docker, or delete data.

### Interpretation and next repair

Host commit exhaustion is confirmed. The manual 4 GiB pagefile cap limits the host's capacity under the current workload. Its role in the exact UI/GPU/WSL failures remains an inference, not a proven single cause. The specific UI module's integrity check makes a missing/corrupt copy of that file an unsupported explanation.

The proposed first correction was to restore Windows-managed paging, which can grow when commit demand rises. The agent asked for approval because this is a machine-wide administrator change that may require a reboot. The user instead said, “I'll increase it to 8gb.” The USER will apply that manual change; do not change it to automatic management or reboot on their behalf. An 8 GiB pagefile would add 4 GiB of commit headroom over the current 4 GiB allocation, but application/reboot and the resulting limit have NOT been verified. Keep Docker stopped until the user reports completion, then verify Win32_PageFileUsage/Setting and available commit before retrying. If WSL still crashes with adequate commit headroom, diagnose that independently using its new event and logs.

Source for commit limits and system-managed growth: https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file . No source establishes that the UI module error uniquely means out-of-memory.

The launcher previously continued far enough to emit a misleading image-not-built error during an unhealthy-engine response. Runner/toolkit.ps1 now also requires a valid returned server version before image checks; syntax validation passed. A stopped-engine check exited 1 with “Docker Desktop could not be checked” and the missing engine-pipe explanation, without claiming the toolkit image was absent. No image rebuild has been requested or performed.
