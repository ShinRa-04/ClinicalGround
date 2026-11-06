"""Freeze the independently reviewed authored artifacts, excluding mutable integration files."""
from pathlib import Path
import datetime
import hashlib
import json
import platform

root = Path(__file__).resolve().parents[1]
paths = []
for directory in ("general", "hermes", "openclaw", "comparative", "labs"):
    paths.extend(path for path in (root / directory).glob("*") if path.suffix in (".md", ".json", ".py"))
paths += [root / name for name in ("foundation_sources.json", "source_versions.json", "tools/run_labs.py",
                                  "README.md", "SOURCES.md", "COVERAGE.md", "FINDINGS_INDEX.md",
                                  "VERIFICATION.md", "ARCHITECTURE_MAPS.md", "verification/coverage.json")]
receipt = {
    "schema_version": 1,
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "reviewer": "/root/harness_independent_review",
    "independent_of_authors": True,
    "verdict": "pass_for_bounded_reviewed_scope_with_nonblocking_diagram_clarification",
    "issues": [{"id": "R1", "severity": "P2", "status": "fixed_and_independently_rechecked",
                "file": "COVERAGE.md", "lines": [12, 22, 34, 36, 44],
                "title": "Unrelated Hermes evidence IDs in coverage-topic mappings",
                "detail": "Integrator fixed generator and regenerated Markdown/JSON; independent readback confirmed all five corrected mappings."},
               {"id": "R2", "severity": "P3", "status": "reported_to_integrator_nonblocking",
                "file": "ARCHITECTURE_MAPS.md", "lines": [57],
                "title": "Diagram reconciliation-to-confirmed edge needs an inconclusive-outcome branch",
                "detail": "Surrounding prose already preserves uncertainty. Integrator can clarify without another worker review round."}],
    "gates": [
        {"id": name, "status": "pass"} for name in (
            "general_learning_priority", "sampled_memory_context_correctness", "sampled_execution_recovery_correctness",
            "sampled_security_trust_correctness", "sampled_defaults_documentation_drift", "source_identity_line_bounds",
            "construction_contract_failure_coverage", "synthetic_lab_logic_and_execution", "truthful_execution_claims")
    ] + [
        {"id": "targeted_final_index_source_coverage_readback", "status": "pass"},
        {"id": "final_mechanical_validator", "status": "integrator_owned_outside_review_verdict", "owner": "integrator"},
        {"id": "commit_publication_completion", "status": "integrator_owned_outside_review_verdict", "owner": "integrator"}
    ],
    "semantic_samples": {
        "hermes": ["H002", "H006", "H010", "H012", "H014", "H029", "H034", "H038", "H048", "H049"],
        "openclaw": ["OC-018", "OC-023", "OC-024", "OC-025", "OC-035", "OC-036", "OC-038", "OC-043", "OC-044", "OC-045", "OC-058", "OC-063", "OC-064", "OC-065", "OC-066", "OC-067"],
        "comparative": ["C05", "C12", "C13", "C14", "C16", "C17", "C22", "C23", "C27", "C34"],
        "foundation": ["G01", "G05", "G06", "G15"]
    },
    "mechanical_identity_checks": {"count": 159, "failures": 0, "artifact": "identity_checks.json"},
    "independent_lab_execution": {
        "command": "python -B -m unittest discover -s HarnessResearch/labs -p 'test_*.py' -v",
        "python": platform.python_version(), "tests": 17, "failures": 0, "errors": 0,
        "reported_test_seconds": 0.092, "scope": "Synthetic fixture invariants only; no upstream/runtime/model/provider validation."
    },
    "reviewed_artifacts": [
        {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted(set(paths))
    ],
    "limits": [
        "Semantic verification samples selected high-consequence claims; not exhaustive review of all 170 findings.",
        "General foundations reopened through non-visible web retrieval and remain mutable checked-date docs.",
        "No upstream app installed, imported or run; source/test inspection differs from runtime execution.",
        "No Docker, visible browser, protected benchmark data, personal services, provider/model calls or upstream mutations.",
        "Lab is sequential and synthetic: no atomic distributed fencing, real tokenizer/semantic compaction, global erasure or external exactly-once proof.",
        "R1 navigation corrections independently rechecked. R2 low-severity diagram clarification is integrator-owned.",
        "Final mechanical validator and commit/publication are outside reviewer verdict; reviewer made no commit."
    ]
}
(root / "review/review_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"reviewed_artifacts": len(receipt["reviewed_artifacts"]), "verdict": receipt["verdict"]}))
