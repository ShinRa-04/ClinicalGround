# Hugging Face login diagnosis — October 17, 2026

## Reported failure and verified scope

The user ran the original Docker-TTY login, entered a token, chose no Git credential storage, and received CloudFront HTTP 400 / Bad request. Doctor subsequently confirmed no saved HF token and no handbook. Docker Engine 29.8.2 and the toolkit are healthy; this failure is after container startup, at authentication. Current scope remains local setup verification only, with no submission or model calls.

The user's actual token/input was not inspected. Hidden terminal paste characters are a likely cause, supported by the controlled reproduction below; the exact contents of the user's failed input remain unknown. The CLI's newer-version notice alone does not establish a dependency defect. Hub 1.14.0 and all frozen dependencies remain unchanged.

## Controlled reproduction

Only deliberately invalid synthetic strings were used. Windows and container anonymous requests to /api/whoami-v2 both returned normal JSON HTTP 401. A plain invalid test token also returned 401 from both environments, confirming the authentication endpoint is reachable.

Using the installed HfApi.whoami inside the toolkit:

| Synthetic input | Response |
| --- | --- |
| Plain invalid test token | HTTP 401, HfHubHTTPError |
| Same test token prefixed with Ctrl+V (U+0016) | HTTP 400, BadRequestError |
| Test token wrapped in bracketed-paste ESC sequences | HTTP 400, BadRequestError |
| Literal printable escape notation | HTTP 401, HfHubHTTPError |

All were CloudFront responses. This reproduces the reported error class with hidden paste controls while leaving a normal invalid credential distinguishable as 401. No real token was used, saved, or logged during diagnostics.

## Implemented correction

Runner/toolkit.ps1 still accepts the same user command: .\Runner\toolkit.ps1 hf auth login. It now collects the token using PowerShell Read-Host -AsSecureString, validates the raw personal-token format locally, then passes it over Docker stdin with no TTY. Token values are not command arguments, environment variables, or task logs. Git credential storage is disabled, matching the user's chosen N.

Runner/hf_login.py runs inside the existing pinned toolkit image through the mounted Runner/ folder; no image rebuild or dependency upgrade is required. It rechecks input format, disables HTTP debug logging on this credential path, uses the official login API, and performs the official read-only auth_check for actava/managed-care-operations-handbook. Failure output contains only the phase/error class/HTTP status, without request headers or raw error bodies. Successful login/access metadata goes to ignored Runner/logs/huggingface-login.json; credentials remain in the ignored HF cache.

The active path supports the bare command and --force/--no-force/--no-add-to-git-credential. Token command-line arguments and enabling Git credential storage are rejected by this runner. Upstream CLI help describes the upstream program; its extra flags do not override this wrapper.

## Executed verification

- PowerShell parser and Python AST checks passed.
- Tested the full launcher under Windows PowerShell 5.1, matching the user's shell: a mocked secure prompt containing a hidden Ctrl+V prefix was rejected before an HTTP request; no token file was created.
- Under the same shell, a mocked secure prompt containing a well-formed deliberately invalid token reached Hugging Face and returned normal HTTP 401, exit 1; no token file was created. This checks PowerShell-to-Docker stdin handling end to end.
- hf auth login --help still works noninteractively.

The user retried successfully. The local receipt verifies real-account login and read access to the restricted handbook at 10:41:36 UTC / 16:11:36 IST on October 17. Doctor confirms a saved login. Download then completed for all 1,292 repository files at exact handbook commit f1210b294904792541116852f6074df8b84d89dd, and the official data-layout check passed. No token value or protected content was recorded in tracked documentation. This verifies authentication and retrieval, not a clinical-policy audit or a scored run.

Reference for why HF_DEBUG is unsuitable for token-handling logs: https://huggingface.co/docs/huggingface_hub/v0.30.2/package_reference/environment_variables#hfdebug . It logs requests as equivalent cURL commands; the local credential path keeps that setting disabled.
