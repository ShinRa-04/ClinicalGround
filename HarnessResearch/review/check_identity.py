"""Independent mechanical source checks; never imports reference applications."""
from pathlib import Path
import datetime
import hashlib
import json

root = Path(__file__).resolve().parents[1]
checks = []
for system in ("hermes", "openclaw"):
    entries = json.loads((root / system / "evidence.json").read_text(encoding="utf-8-sig"))
    for entry in entries:
        source = root / "_sources" / system / entry["source_path"]
        raw = source.read_bytes()
        lines = raw.decode("utf-8-sig").splitlines()
        bounds = 1 <= entry["line_start"] <= entry["line_end"] <= len(lines)
        key = "selected_lines_sha256" if system == "hermes" else "source_sha256"
        payload = "\n".join(lines[entry["line_start"] - 1:entry["line_end"]]).encode() if system == "hermes" else raw
        checks.append({"id": entry["id"], "line_bounds_valid": bounds,
                       "hash_matches": hashlib.sha256(payload).hexdigest() == entry[key]})
sources = json.loads((root / "comparative/sources.json").read_text(encoding="utf-8-sig"))
for source in sources["sources"]:
    path = root / source["cache_relative_path"]
    checks.append({"id": source["id"], "hash_matches": hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]})
result = {"checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "checks": checks, "limits": "Mechanical identity and line bounds only; not semantic claim validation."}
(root / "review/identity_checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"checks": len(checks), "failed": [check for check in checks if not all(value for key, value in check.items() if key != "id")]}))
