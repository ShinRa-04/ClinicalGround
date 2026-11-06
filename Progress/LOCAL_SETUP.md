# Isolated local setup — verified October 17, 2026

## Current result and scope

Local environment verification PASSED. This workspace contains the official controller and a tested local runtime, with dependencies inside Docker. The user explicitly wants no submission now. Agent creation remains separate from Runner/. No model-powered agent/judge run, scored trial, real packet, or public submission has occurred.

Docker is running; there are zero running or stopped containers and no iGOT images. The disposable startup-test container was removed. Only two distinct chi-bench images remain; chi-bench:latest is an alias of the runtime image.

## Verified data and authentication

- Actual-account HF login and restricted handbook read access passed at 16:11:36 IST on October 17 using the corrected local hidden prompt. See [login diagnosis](HF_LOGIN_DIAGNOSIS.md). Credentials stay in the ignored Runner/.cache/huggingface/ directory.
- Public release chi-bench-v1.0.0: commit 5ce88104df2a91e057619eb70fb51f56fc5949eb, 2,505 repository files; 25 public instruction files per domain, 75 total.
- Restricted handbook: commit f1210b294904792541116852f6074df8b84d89dd, all 1,292 repository files downloaded, now under Dataset/chi-bench/skills/. Protected content is local-only and was not copied into these documents.
- Official host data verification PASSED, including the handbook. Required official pa_t035 correction and payer-request PDF regeneration ran successfully. The public release pin remains v1.0.0, as instructed by the upstream README.

## Images, source pins, and compatibility

Official benchmark commit: 4444a07fa68a4f1623f841a292a54e284fc8e7f7. Official sparse leaderboard commit: a321b9e9603ad8431c13911729eaf213a5d3b870. The benchmark checkout has no tracked source changes.

| Artifact | Current identifier | Size |
| --- | --- | --- |
| bigdata-chi-tools:4444a07 | sha256:2ccd8c07f230b2a182f60429de8e1a2241dabd001acfb6634e837ac63d2c85e5 | 3,690,381,517 bytes |
| bigdata-chi-bench:runtime-4444a07, alias chi-bench:latest | sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66 | 4,709,409,463 bytes |

The controller uses the official frozen dependency lock: Python 3.12.15, chi-bench 1.1.0, Harbor 0.20.0, Hub 1.14.0, and 146 installed packages. Base images are pinned in Dockerfile.tools. Runtime versions actually tested: Python 3.12.15, chi-bench 1.1.0, Node v22.23.3, Claude Code CLI 2.1.302.

The upstream runtime Dockerfile installs Node 20 with Claude Code @latest. Publisher metadata for fetched CLI 2.1.302 requires Node >=22; npm emitted EBADENGINE. The agent intentionally stopped the original build (exit 143); it had not naturally failed. The tested runtime used two compatibility changes: setup_20.x -> setup_22.x and CLI @latest -> @2.1.302. After dataset relocation, Runner/toolkit.py also maps the ten data COPY instructions to named context chi_data when generating Runner/.cache/Dockerfile.runtime. The official checkout remains unchanged. Recipe hashes and versions are saved in logs/runtime-build-recipe.json. These local overrides must be reported with any future reproducibility results.

The corrected nested-client build had one context-transfer cancellation (“error from sender: context canceled”). Engine health and the exact two-change recipe were verified; no OOM event was found in the queried interval. The precise cause is unproven. The native Windows Docker client successfully built the identical recipe; this installed no host compiler, Python packages, or Node runtime. The Windows Docker CLI is already part of Docker Desktop.

## Actually executed checks

The runtime was started with a real public payer task ID, external networking disabled, no provider keys, no published ports, and limited resources. Its official entrypoint bootstrapped the stores and waited for HTTP/MCP readiness. The additional check then verified:

| Check | Result |
| --- | --- |
| HTTP /health on port 8023 | 200 |
| MCP initialize: provider 8020, payer 8100, care-management 8200 | All 200 |
| Official baked-image data-layout verification | Passed |
| Handbook SKILL.md present in runtime | Passed |
| Legacy healthverse verifier import alias | Passed |
| Node and Claude CLI version commands | Passed |
| Headless Chromium launch and local page | Passed |
| Provider keys and HF_TOKEN in runtime | All absent |
| Test-container exit and removal | Exit 0; removed |

Earlier offline verification: 54 upstream unit tests passed in 20.33s; the official sample packet validator returned 0 errors/warnings. These were infrastructure checks, not scored benchmark results. The placeholder submission schema was validated with preflight skipped; it is not a complete run configuration.

Real agent behavior, simulator/judge model calls, scoring, and task-completion quality remain UNTESTED. Provider credentials and a selected harness/model would be required for such a future local trial. Do not request them or create a submission as part of the current verification-only phase.

## Commands and local files

Run from C:/Projects/BigData:

    .\Runner\toolkit.ps1 doctor
    .\Runner\toolkit.ps1 cb data verify
    .\Runner\toolkit.ps1 cb --help

Preparation commands, already completed:

    .\Runner\toolkit.ps1 download-public
    .\Runner\toolkit.ps1 hf auth login
    .\Runner\toolkit.ps1 download-handbook
    .\Runner\toolkit.ps1 build-runtime

The last command prepares/repairs data and generates the compatibility recipe, then invokes a container-side Docker client. On the earlier context-transfer cancellation, the Windows Docker CLI built the runtime successfully. After the October 17 dataset relocation, the equivalent host-client command must include the named data context:

    docker build --file .\Runner\.cache\Dockerfile.runtime --build-context chi_data=.\Dataset\chi-bench --target runtime --label com.bigdata.workspace=BigData/Runner --tag bigdata-chi-bench:runtime-4444a07 .\Runner\chi-bench
    docker tag bigdata-chi-bench:runtime-4444a07 chi-bench:latest

Use the host command only after preparation has succeeded and the alias is confirmed runner-owned. The generated recipe and downloaded handbook are required. The runtime image includes protected handbook content and must stay private. No image was pushed.

Runner/ maps to /runner/ and Dataset/ maps to /dataset/ inside the controller. Dependencies live in its image, outside the mounted source checkout. The current toolkit.py is mounted over the image's helper, so the separate dataset paths work without a controller rebuild. The controller uses the existing Docker Desktop socket; this is dependency/project separation, not a separate daemon or host security boundary. Its own build context excludes credentials, downloaded data, handbook, caches, and logs.

Local-only receipts under Runner/logs/ include doctor.json, huggingface-login.json, toolkit-image.json, runtime-image.json, runtime-build-recipe.json, local-verification-final-20261017.json, and runtime-smoke-20261017/runtime-check.json. Original public-data-download.json and handbook-download.json now live in Dataset/receipts/, alongside relocation-20261017.json. Their original destinations remain historical provenance. Startup invocation records network=none and no forwarded model keys. Build/console/server logs are ignored. Never store credentials or protected handbook text in tracked files.

## October 17 dataset relocation

The user requested a root Dataset/ folder, root tmp/ removal, and a commit of all project changes. The entire former Runner/chi-bench/data/ tree was moved to Dataset/chi-bench/, including public tasks, fixtures, shared worlds, metadata, assets, release pin, handbook, and download caches. All 11,396 local files retained identical SHA-256 hashes; the count includes cache metadata and is not the upstream repository-file count. Download receipts were moved to Dataset/receipts/. Root tmp/ contained only an empty pdfs/ directory; both empty directories were removed.

Executed after relocation: toolkit doctor PASSED with 25 tasks in each core domain and handbook present; official cb data verify PASSED; prepare-runtime PASSED with zero request PDFs updated; placeholder submission schema validation PASSED with preflight skipped. The generated recipe maps all ten data COPY instructions to BuildKit context chi_data. Docker build --check with the real Windows dataset context PASSED with no warnings. This is a static recipe check, not a complete post-relocation runtime rebuild. Existing controller/runtime image IDs are unchanged. No provider/model call, scored trial, or submission was performed.

The official source checkout has no tracked source changes. The runner's documented default data commands now supply --data-dir /dataset/chi-bench, and the submission example uses the same root. Future runtime builds must use the wrapper's build-runtime action or the named-context host command above; the unmodified upstream cb docker build assumes a repository-local data folder.

## Historical issues and cleanup

- Windows native dependency install failed because chi-bench[dev] -> Harbor 0.20.0 -> LiteLLM 1.93.0 selected a source build without a Windows wheel; Rust/MSVC required link.exe and a Windows SDK, neither installed. The user chose Docker-contained tools. The failed native .venv remains unused; no host compiler/SDK or WSL project migration occurred.
- That failed build auto-downloaded Rust into C:/Users/prath/AppData/Local/puccinialin/puccinialin/Cache. It was not deleted. A Linux uv binary under Runner/.bin/ is also unused.
- Windows shell files were restored to exact upstream LF bytes after checkout conversion; clone-local LF policy was set. A local ignored .dockerignore excludes native environments/caches from runtime context.
- Docker startup incidents and uncertainty: [DOCKER_DIAGNOSIS.md](DOCKER_DIAGNOSIS.md). The user's pagefile maximum is verified at 8,192 MiB; allocated size at that inspection was 2,048 MiB. The agent did not change it or reboot Windows.
- User-authorized removal of iGOT images/database/queue data and Docker VHDX compaction: [DOCKER_CLEANUP.md](DOCKER_CLEANUP.md). Ubuntu/Debian and Windows project folders were preserved. New chi-bench builds legitimately add runtime layers after the earlier compaction baseline.
- The obsolete prior controller image was removed after the replacement and runtime passed checks. Current images are the two identifiers above.
- Temporary build cleanup selected 76 reclaimable, unshared cache records by exact IDs and BuildKit reported 12.44 GB reclaimed internally. Both working image IDs remained unchanged. Thirteen non-reclaimable cache records remain. Host VHDX allocation can stay larger until another compaction; this is not a claim that Windows recovered 12.44 GB. No second compaction or Docker restart was done after the successful startup check.

No required local environment-verification work remains. Continue background study or future agent work only within the user's next requested scope.
