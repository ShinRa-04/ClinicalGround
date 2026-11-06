# Local submission assemblies

Each dated `submission_N_YYYY-MM-DD/` directory records one assembly. Its
`packet/` holds the exact leaderboard file layout; `evidence/` preserves native
source receipts and trial records; `validation/` holds validator output.
Those payloads and archives are ignored because they can contain private case
data and protected reference responses. Only producer tools, tests and
sanitized status documentation are committed.

Creating a local packet does not publish it or establish full benchmark
coverage. Read each assembly's README for its actual scope, validation and
publication blockers.
