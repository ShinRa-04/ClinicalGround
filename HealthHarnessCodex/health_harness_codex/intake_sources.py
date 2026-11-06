"""Bounded, read-only extraction of actor-listed UM intake request forms.

Only the payer-facing source metadata returned by the actor is accepted. The
actual PDF is read inside the owned trial container by a fixed Python program;
this module never opens a host path or consumes provider-side content URLs.
"""

from __future__ import annotations

import re
from typing import Any, Mapping


_MAX_PDF_BYTES = 10 * 1024 * 1024
_MAX_PAGES = 1000
_MAX_TEXT_CHARS = 20000

_READ_INTAKE_PDF_SCRIPT = r'''import hashlib,json,sys
from pathlib import Path,PurePosixPath
from pypdf import PdfReader

d=json.load(sys.stdin)
case_id=d["case_id"]
relative_path=d["relative_path"]
path=PurePosixPath(relative_path)
parts=path.parts
if (not parts or parts[0] != case_id or any(p in {"", ".", ".."} for p in parts)
    or path.is_absolute() or "\\" in relative_path or len(parts) < 3):
 raise ValueError("invalid case-local intake PDF path")
allowed=(len(parts) >= 4 and parts[1] == "payer" and parts[2] == "incoming_request") or (
 len(parts) >= 4 and parts[1] == "shared" and parts[2] in {"intake", "handoff"})
if not allowed:
 raise ValueError("intake PDF path is outside the allowed payer or shared source area")
workspace=Path("/logs/artifacts/workspaces").resolve(strict=True)
if parts[1] == "payer":
 base_path=workspace/case_id/"payer"/"incoming_request"
 tail=parts[3:]
else:
 base_path=workspace/case_id/"shared"/parts[2]
 tail=parts[3:]
base=base_path.resolve(strict=True)
if base != base_path:
 raise ValueError("allowed intake source root is redirected through a symlink")
candidate=base.joinpath(*tail).resolve(strict=True)
try:
 candidate.relative_to(base)
except ValueError:
 raise ValueError("intake PDF resolved outside its allowed case-specific source root") from None
if not candidate.is_file():
 raise ValueError("actor-listed intake form is not a regular file")
with candidate.open("rb") as f:
 raw=f.read(%d+1)
if len(raw)>%d:
 raise ValueError("intake PDF exceeds the read limit")
reader=PdfReader(__import__("io").BytesIO(raw), strict=True)
if len(reader.pages)>%d:
 raise ValueError("intake PDF exceeds the page limit")
chunks=[]
remaining=%d
for page in reader.pages:
 if remaining<=0: break
 text=page.extract_text() or ""
 separator="\n" if chunks else ""
 if len(separator)>remaining: break
 remaining-=len(separator)
 piece=text[:remaining]
 chunks.append(piece)
 remaining-=len(piece)
print(json.dumps({"text":"\n".join(chunks),"source_sha256":hashlib.sha256(raw).hexdigest(),
                  "page_count":len(reader.pages),"truncated":remaining<=0},separators=(",",":")))
''' % (_MAX_PDF_BYTES, _MAX_PDF_BYTES, _MAX_PAGES, _MAX_TEXT_CHARS)


class IntakeSourceReader:
    """Read one actor-listed intake PDF using the trial's DockerExecutor."""

    def __init__(self, executor: Any):
        if not callable(getattr(executor, "python_json", None)):
            raise TypeError("executor must provide the DockerExecutor python_json interface")
        self.executor = executor

    def __call__(self, case_id: str, document_metadata: Mapping[str, Any]) -> dict[str, Any]:
        return self.read_intake_context(case_id, document_metadata)

    def read_intake_context(self, case_id: str, document_metadata: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", case_id):
            raise ValueError("case_id must be one actor-observed identifier")
        if not isinstance(document_metadata, Mapping):
            raise TypeError("document metadata must be a mapping returned by the actor")
        if document_metadata.get("case_id") != case_id:
            raise ValueError("intake document metadata case_id does not match the selected actor case")
        if document_metadata.get("artifact_type") != "intake_request_form":
            raise ValueError("actor metadata does not identify an intake request form")
        relative_path = document_metadata.get("relative_path")
        if not isinstance(relative_path, str) or len(relative_path) > 1024:
            raise ValueError("actor metadata lacks a bounded intake form relative_path")
        parts = relative_path.split("/")
        if (parts[0] != case_id or any(part in {"", ".", ".."} for part in parts)
                or "\\" in relative_path or len(parts) < 4
                or not ((parts[1:3] == ["payer", "incoming_request"])
                        or (parts[1] == "shared" and parts[2] in {"intake", "handoff"}))):
            raise ValueError("actor metadata path is outside the allowed case-specific intake source roots")
        if not relative_path.casefold().endswith(".pdf"):
            raise ValueError("actor-listed intake request form is not a PDF")
        result = self.executor.python_json(
            _READ_INTAKE_PDF_SCRIPT,
            {"case_id": case_id, "relative_path": relative_path},
            timeout=30,
        )
        if not isinstance(result, Mapping):
            raise ValueError("intake PDF reader returned an invalid result")
        text = result.get("text")
        digest = result.get("source_sha256")
        if not isinstance(text, str) or len(text) > _MAX_TEXT_CHARS:
            raise ValueError("intake PDF reader returned text outside the configured bound")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("intake PDF reader returned an invalid source hash")
        return {
            "text": text,
            "source_sha256": digest,
            "page_count": result.get("page_count"),
            "truncated": result.get("truncated", False),
        }


def find_intake_request_form(documents_result: Any, case_id: str) -> Mapping[str, Any]:
    """Select the one source form in an actor list_documents public result."""
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("case_id must be actor-observed")
    payload = documents_result
    if isinstance(payload, Mapping) and "structuredContent" in payload:
        payload = payload.get("structuredContent")
    if isinstance(payload, Mapping):
        items = payload.get("items")
    else:
        items = None
    if not isinstance(items, list):
        raise ValueError("actor list_documents did not return an item list")
    forms = [item for item in items if isinstance(item, Mapping)
             and item.get("case_id") == case_id
             and item.get("artifact_type") == "intake_request_form"]
    if len(forms) != 1:
        raise ValueError(f"actor documents did not identify exactly one intake request form ({len(forms)} found)")
    return forms[0]
