# Implementation verification and limits

Implementation: October 18–19, 2026. Final local checks: October 19 IST. Runtime target: Python 3.11+. Executed local interpreter: **Python 3.12.14**, using the bundled dependency runtime. Python 3.11 was not separately tested. Tests use synthetic records and fake endpoints; they do not measure clinical quality or benchmark performance.

## Executed checks

The final integrated suite passed **43 tests**, independently executed in the main chat after the Luna implementation handoff. Author and reviewer reruns are the same 43 tests, not separate unique coverage. Expected rejection messages from negative CLI tests are not suite failures.

Covered behaviors:

- Full-scope state/action separation and immutable scope/task identity.
- Optimistic state versions, transactional mutation fencing, stale-owner rejection and expired/released leases.
- Unknown write outcomes rejected on resume without automatic redispatch.
- Schema/argument identity validation, inactive unsupported-schema branches, local Pydantic references, NaN rejection and boolean/number enum distinction.
- Detached general responsibility definitions and correct domain/shared counts.
- Scoped local completion requiring observed support; known failures cannot support completion.
- Foreign patient/case results quarantined before the next model request.
- Stable journal IDs across a helper and mutation in the same owner response.
- Context/request bounds including tool schemas, evidence pointers and whole tool-call exchanges.
- Provider-safe tool aliases, conservative MCP effect defaults, session headers, JSON-text normalization, duplicate names and SSE matching.
- Separate case workspaces, reference allowlists, path escape rejection and registry collisions.
- Reassignment of an existing workspace/MCP client to a different full scope is rejected before discovery/inference. Overlapping runs on one Harness instance are rejected; separate case instances are required for concurrency.
- Changing A's saved records leaves B's constructed context unchanged, and sequential reuse of a stateless model does not carry A's conversation into B's request.
- A stored completed effect receipt is consumed after a simulated crash boundary without redispatch. A pending write is quarantined. A transient model failure can be resumed with retained budgets and one effect.
- Four real localhost HTTP tests exercise client encoding/session headers/SSE matching, PA/UM/CM loops, CLI-configured execution, usage reporting, foreign JSON-text rejection and uncertain-effect recovery. All model/MCP responses are synthetic; no external endpoint is contacted.
- Harbor adapter packaging/configuration is checked using fake controller/environment objects: bounded source chunks, packaged role data, explicit failure propagation, private state/artifact paths and no key in shell command text.
- Launcher defaults to a plan and includes the external agent class, pinned Docker environment class, controller import path and scoped output location. Execution is mocked in tests; credential values stay out of argv.

Additional executed checks:

- `compileall` passed for the package and launcher.
- Default/module CLI, `--demo`, and launcher `--help` passed. PA, UM and CM each returned a local synthetic completion using two scripted model turns and one synthetic observation.
- Built `dist/health_harness-0.1.0-py3-none-any.whl` with bundled setuptools, without installing new dependencies. After removing surplus source-file EOF blank lines, the final wheel is **44,807 bytes**, SHA-256 `5cf8987a48253252055876c2fee3b91a1a66b925d9b0a03a224d0277c9565008`.
- Imported that wheel from an isolated Python process, checked its packaged role data (PA/shared 28, UM/shared 28, CM/shared 30), and ran the three-domain demo from the wheel. This is an isolated archive import, not a `pip install` or a production deployment.
- PowerShell AST parsing of the changed Runner launcher passed without invoking Docker. The official benchmark checkout remains clean at `4444a07fa68a4f1623f841a292a54e284fc8e7f7`.

Build outputs, bytecode and runtime data remain ignored. The initial root-directory test invocation failed because the package was not on that invocation's import path; running the documented command from `HealthHarness/` passed. This was not a missing dependency installation.

These are specific tested properties. They do not establish that arbitrary returned free text or opaque resource identifiers always have the correct patient provenance.

## Boundaries that remain unverified

No live provider call, official MCP server connection from this new package, Docker trial, conversation simulator/judge run, official score, model/architecture comparison or submission has been executed. Synthetic adapter doubles cannot establish actual installed Harbor execution. The official checkout remains pinned and unmodified. Harbor environment-template resolution is a pinned integration dependency still requiring a real environment check.

No protected handbook content, verifier expectations, solutions or real patient records are embedded in the package or tests. Runtime reference access is an explicit configuration input. Prior public role/policy research retains its original evidence limits; putting a role in a prompt is not medical validation.

Explicit scope configuration remains required. Automatic patient resolution and safe binding of newly created PA/CM resource IDs are not assumed. The known-identity guard can conservatively reject an observation containing a different historical case ID even when it belongs to the same patient; broadening that requires an explicit, tested ownership rule.

## Important engineering limitations

- SQLite fencing applies to trusted code using the store API. It is not a multi-tenant authentication service or a guarantee against direct file/database tampering.
- The external server owns its access policy. Input schemas, annotations and configured IDs do not prove authorization of every opaque document/session/referral handle.
- Remote outcomes can remain uncertain. Local transactions cannot prove exactly-once effects on an unrelated server. Reconciliation requires actual environment readback; there is no blanket “clear the error and retry” operation.
- Schema support is intentionally bounded. Unsupported assertions and recursive/external references must fail explicitly. A live server's full schema set still needs compatibility testing.
- Character limits are not exact token counts or monetary caps. Reported usage is evidence only for fields actually supplied by the endpoint; no price/usage number is inferred when absent.
- The provider adapter implements a Chat Completions request subset (`max_tokens`, optional `reasoning_effort`, function tools). The configured endpoint/model must accept those parameters. Responses API, native Anthropic/Gemini protocols and persistent provider threads are not implemented by this adapter.
- Stateless request assembly prevents application-level conversation reuse across patients. Provider-side retention, training and infrastructure policies are not tested by this package.
- Path resolution rejects ordinary traversal and pre-existing escapes; it is not an OS sandbox against an adversarial process changing paths concurrently.
- A local completion claim checks source membership, recorded outcomes and open obligations. It does not semantically prove a clinical conclusion or substitute for the official grader.
- The 66 contracts describe responsibilities. Broader scheduling, referrals, asynchronous fulfillment, independent appeal bodies and autonomous hospital staffing are not fabricated when the supplied tools do not expose them.

## Reproducing local checks

From `HealthHarness/`:

```powershell
python -m unittest discover -s tests -v
```

Use the existing Runner toolkit for any future official dependency/runtime work. Do not install host compilers or migrate to WSL. No new external dependency is required for the standard-library package tests.
