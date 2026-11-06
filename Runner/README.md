# Local χ-Bench run and submission tools

This folder is for running the official benchmark, inspecting run evidence, and preparing or validating submission packets. Develop the actual agent separately and connect its packaged harness later.

The user selected Docker-contained tools. Python, Harbor, the locked dependencies, browser, Docker client, and GitHub CLI are installed inside the toolkit image. Windows needs Docker Desktop and PowerShell; it does not need a new compiler installation or a separate WSL project environment.

## Start here

Initial setup on October 16 built the toolkit and downloaded all 75 public competition tasks. Offline tests and the sample packet validator passed; handbook access/download were pending at that stage.

October 17: local environment verification PASSED. Docker/toolkit, actual-account login, restricted handbook read access/download, both host and baked data layouts, runtime HTTP/all three MCP endpoints, headless Chromium, and CLI checks passed. The startup test used external networking disabled and no provider keys; its container was removed. Real agent/judge execution and scoring remain untested. Current scope is local verification only; no real submission is requested. See [verified setup state and receipts](../Progress/LOCAL_SETUP.md).

From C:/Projects/BigData in PowerShell:

    .\Runner\toolkit.ps1 doctor
    .\Runner\toolkit.ps1 cb --help

Build or rebuild the toolkit:

    .\Runner\toolkit.ps1 build

The toolkit uses the official benchmark checkout at commit 4444a07fa68a4f1623f841a292a54e284fc8e7f7. Its image is bigdata-chi-tools:4444a07. Each command uses a temporary container that is removed afterward. The image's Python environment lives outside the mounted Windows checkout.

## Prepare task data

Downloaded datasets live in the root-level [Dataset/](../Dataset/README.md), separately from this runner. The public release is in `Dataset/chi-bench/`, with the handbook in its `skills/` subfolder. Download receipts and the relocation hash inventory are in `Dataset/receipts/`. They are local-only and ignored by Git.

Download the public release and record its exact resolved revision:

    .\Runner\toolkit.ps1 download-public

This uses the official Hugging Face download library without authentication, pins chi-bench-v1.0.0, and writes a receipt under Dataset/receipts/. It does not inspect case expectations or run an agent.

Handbook access must be approved first at https://huggingface.co/datasets/actava/managed-care-operations-handbook . After approval, sign in locally and download it:

    .\Runner\toolkit.ps1 hf auth login
    .\Runner\toolkit.ps1 download-handbook

Create a Read token at https://huggingface.co/settings/tokens using the approved account, then paste it into the PowerShell hidden prompt, preferably with right-click. The launcher validates the raw hf_ token before sending it privately through stdin to the existing container. It automatically skips Git credential storage and verifies handbook read access after login; successful access does not itself download the handbook. Website approval alone does not sign the isolated runner in. Never paste the token in chat or include it in a command argument.

This host prompt replaces the original Docker-TTY prompt after hidden paste-control characters reproduced an HTTP 400 authentication failure. Dependencies stay pinned at Hub 1.14.0; no upgrade or image rebuild is needed. See [login diagnosis and tests](../Progress/HF_LOGIN_DIAGNOSIS.md). A malformed token is rejected locally; an accepted-format but invalid token produces a normal HTTP 401.

The token is retained in this folder's ignored cache. Do not put tokens in chat or in tracked files. Protected handbook files remain local under Dataset/chi-bench/skills/; do not publish the runtime image or upload the handbook.

## Prepare the official runtime

After the handbook is present:

    .\Runner\toolkit.ps1 build-runtime

This executes the two repair/regeneration scripts required by the pinned official README against `/dataset/chi-bench` and verifies the data. It then builds from a generated local copy of the official Dockerfile with Node 22 and Claude Code 2.1.302 compatibility overrides. Data COPY instructions use the BuildKit named context `chi_data`, mapped to the separate dataset directory. The official source checkout stays unchanged. Recipe hashes/version choices are recorded under logs/. The image is tagged bigdata-chi-bench:runtime-4444a07 and aliased as chi-bench:latest because the official local flow expects that name. An existing chi-bench:latest image owned by another workspace causes an error instead of being overwritten.

Use `prepare-runtime` to execute the repair/verification and generate the recipe without building an image. Use the wrapper's `build-runtime` action for future builds, rather than the upstream `cb docker build` command that assumes a repository-local data folder. The new named-context recipe passed Docker's static build check; a full rebuild after relocation has not been executed. The existing tested runtime already contains its own baked dataset and remains usable.

The toolkit image and scored-trial runtime image have different purposes. A successful toolkit build does not establish that a scored trial or runtime build has occurred.

The runtime build is now verified, including its startup. A nested-client build had one context-transfer cancellation; the identical recipe succeeded using the Windows Docker CLI. The tested host-client fallback and exact current image IDs are recorded in LOCAL_SETUP.md. Both image tags for the runtime refer to one image. Keep it private because it includes the protected handbook.

## Configure a run

The local .env file starts with empty keys. Fill ANTHROPIC_API_KEY for the official judge and the provider key required by the agent you select. Use plain KEY=value lines without surrounding quotes or inline comments. The launcher passes the env file directly to Docker; it never treats the file as executable shell commands.

Copy submission.example.yaml to submission.local.yaml and replace the team, contact, harness, and model placeholders. The example uses local Docker, one attempt, concurrency one, and all three public domains. It makes no agent or model choice for you.

    Copy-Item .\Runner\submission.example.yaml .\Runner\submission.local.yaml
    .\Runner\toolkit.ps1 cb submission validate -f /runner/submission.local.yaml

When credentials, handbook, model selection, and runtime are ready, the official lifecycle is:

    .\Runner\toolkit.ps1 cb submission run -f /runner/submission.local.yaml
    .\Runner\toolkit.ps1 cb submission status -f /runner/submission.local.yaml
    .\Runner\toolkit.ps1 cb submission prepare -f /runner/submission.local.yaml

The run command can incur provider, simulator, and judge API costs. It is not executed during environment preparation. No public submission is made by these commands.

Paths passed after the action are paths inside the toolkit. Windows Runner/ is /runner/, so a file at Runner/submission.local.yaml is /runner/submission.local.yaml inside the command. Windows Dataset/ is /dataset/; the submission template uses /dataset/chi-bench. The wrapper supplies this root automatically for `cb data verify` and `cb data download` unless an explicit `--data-dir` is given.

## Validate a prepared packet

    .\Runner\toolkit.ps1 validate-packet /runner/logs/submissions/local-test/packet/DATE-SLUG

This invokes the official leaderboard validator. It does not publish, push, create a fork, or open a PR. Actual publication requires a real completed packet and GitHub authentication, following the official leaderboard submission skill. The separate Kaggle competition may have additional delivery requirements.

## Isolation and files

- chi-bench/ and leaderboard/: separate official Git checkouts, excluded from the parent project's Git history.
- ../Dataset/: downloaded public data, protected handbook, caches, and data receipts; see its README.
- Dockerfile.tools, toolkit.py, toolkit.ps1, hf_login.py: the local environment, launchers, and stdin-based authentication helper, with no custom agent implementation.
- .cache/: runner-only Hugging Face/GitHub state and command caches, ignored by Git.
- .env and submission.local.yaml: local credentials and selected run settings, ignored by Git.
- logs/: readiness reports, runtime-build records, and trial outputs, ignored by Git. Dataset download receipts live under ../Dataset/receipts/.
- ../Progress/LOCAL_SETUP.md: authoritative record of completed work, checks, and remaining prerequisites.

The toolkit talks to the existing Docker Desktop engine through its socket. This isolates dependencies and project files; it is not a separate Docker daemon or a security boundary against the host. Scored agent trials use the official fresh task containers. No host ports are published by the toolkit launcher, and iGOT services are not started.

The Docker build context uses an allowlist: public package manifests, official source code, and the toolkit helper. Local credentials, task data, handbook files, and logs are excluded from the toolkit build. The official scored-trial image includes task data and the handbook as required by its Dockerfile and must stay private.

The launcher mounts the current toolkit.py over the image's helper so path updates take effect without rebuilding its dependency image. This mount does not change the installed official benchmark package or its dependency lock.
