# Project entrypoint

Read Progress/HANDOFF.md before working in this project.

## Harness development philosophy

Classify failures using preserved execution/evaluator evidence and correct the
general cause. Do not encode task IDs, patient-specific answers, or hidden
expected outcomes as behavioral rules. The model chooses investigations and
interprets policy; code checks source provenance, isolation, execution limits
and observed effects. Software tests establish mechanics, not benchmark success.
When an assistant-chosen design repeatedly causes problems, explain the evidence
and ask the user constructive questions before imposing another design. Preserve
failed trials separately from assisted development retries and evaluated results.

Downloaded benchmark data and the protected handbook live in root Dataset/;
see Dataset/README.md. Keep payloads and receipts local-only. Runner/ holds
tools and official checkouts. Use toolkit.ps1 so the separate dataset is mounted
correctly; use its build-runtime action for named-context runtime builds.

Plan/ contains competition sources and background study. Runner/ is an isolated
workspace for installing the official benchmark, testing runs, and preparing or
validating submission packets. Keep agent creation separate from Runner/.

The user selected Docker-contained run tools after the native Windows build
failure was diagnosed. Use Runner/toolkit.ps1; do not install a host compiler or
migrate this project into WSL as an automatic fallback. iGOT is on hold and its
containers must remain stopped. Scored trials require approved handbook access
and locally configured provider keys.

October 17 cleanup: the user authorized deletion of all non-chi-bench Docker
data, explicitly including iGOT's images and persisted database/queue volumes.
Those objects have been removed. Keep normal Ubuntu/Debian distributions and
Windows project folders outside this Docker-only cleanup. Read
Progress/DOCKER_CLEANUP.md for the current retained assets and verification.

Do not store credentials or protected handbook content in tracked files. The
official repositories, downloaded data, environments, caches, and run outputs
inside Runner/ are local-only. Follow the repositories' own instructions when
working in those checkouts. Record exact setup and verification state in Progress/.
