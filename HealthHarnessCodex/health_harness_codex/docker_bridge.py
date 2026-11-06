"""Bounded host-to-container transport for a single owned χ-Bench trial."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from dataclasses import replace
from typing import Any, Iterable

from .models import Scope, ToolSpec, WorldUnavailableError
from .tools import MCPClient, MCPError, MCPToolError, _decode_json_or_sse, _is_relative_to


class DockerBridgeError(RuntimeError):
    """A Docker transport operation failed without exposing container output."""


class DockerExecutor:
    """Run fixed Python operations inside an already-running trial container."""

    def __init__(self, container: str, docker: str = "docker", timeout: float = 40):
        if not isinstance(container, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container):
            raise ValueError("container must be an explicit container name or ID")
        if not isinstance(docker, str) or not docker:
            raise ValueError("docker executable must be explicit")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("timeout must be positive")
        self.container = container
        self.docker = docker
        self.timeout = float(timeout)

    def assert_running(self):
        kwargs={'capture_output':True,'text':True,'encoding':'utf-8','errors':'strict',
                'timeout':min(self.timeout,5),'check':False}
        if os.name=='nt':kwargs['creationflags']=getattr(subprocess,'CREATE_NO_WINDOW',0x08000000)
        try:
            result=subprocess.run([self.docker,'inspect','--format','{{.State.Running}}',self.container],**kwargs)
        except (OSError,subprocess.TimeoutExpired,UnicodeError):
            raise WorldUnavailableError('unavailable') from None
        if result.returncode:raise WorldUnavailableError('unavailable')
        value=result.stdout.strip()
        if value=='false':raise WorldUnavailableError('stopped')
        if value!='true':raise WorldUnavailableError('unverified')

    def python_json(self, script: str, data: dict[str, Any], timeout: float | None = None) -> Any:
        if not isinstance(script, str) or not script or len(script) > 20000:
            raise ValueError("container script must be a bounded fixed program")
        if not isinstance(data, dict):
            raise TypeError("container operation data must be a JSON object")
        budget = self.timeout if timeout is None else timeout
        if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0:
            raise ValueError("timeout must be positive")
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        if len(payload.encode("utf-8")) > 2_000_000:
            raise ValueError("container operation input exceeds 2 MB")
        command = [self.docker, "exec", "-i", self.container, "/workspace/.venv/bin/python", "-c", script]
        kwargs: dict[str, Any] = {"input": payload, "capture_output": True, "text": True,
                                  "encoding": "utf-8", "errors": "strict", "timeout": float(budget),
                                  "check": False}
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        try:
            result = subprocess.run(command, **kwargs)
        except subprocess.TimeoutExpired:
            raise DockerBridgeError("container operation timed out") from None
        except OSError as exc:
            raise DockerBridgeError(f"Docker process could not start ({type(exc).__name__})") from None
        if len(result.stdout.encode("utf-8", errors="replace")) > 2_000_000:
            raise DockerBridgeError("container operation output exceeded 2 MB")
        if result.returncode:
            self.assert_running()
            raise DockerBridgeError(f"container operation failed (exit {result.returncode})")
        try:
            return json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError):
            raise DockerBridgeError("container operation returned invalid JSON") from None

    def validate_owned_trial(self, task_id: str) -> None:
        """Check running state/ownership label, then compare only the assigned task ID."""
        template = "{{json .State.Running}}|{{json .Config.Labels}}"
        command = [self.docker, "inspect", "--format", template, self.container]
        kwargs: dict[str, Any] = {"capture_output": True, "text": True, "encoding": "utf-8",
                                  "errors": "strict", "timeout": min(self.timeout, 10), "check": False}
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        try:
            result = subprocess.run(command, **kwargs)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DockerBridgeError(f"container ownership inspection failed ({type(exc).__name__})") from None
        if result.returncode:
            raise DockerBridgeError("container ownership inspection failed")
        try:
            running, raw_labels = result.stdout.strip().split("|", 1)
            labels = json.loads(raw_labels)
        except (ValueError, json.JSONDecodeError):
            raise DockerBridgeError("container ownership metadata is invalid") from None
        if running != "true" or not isinstance(labels, dict):
            raise DockerBridgeError("container is not a running owned χ-Bench trial")
        owned = any("ownedcase" in re.sub(r"[^a-z]", "", str(key).lower())
                    and str(value).strip().lower() not in {"", "0", "false", "no"}
                    for key, value in labels.items())
        root_workspace_label = labels.get("com.bigdata.workspace") == "BigData/HealthHarnessCodex"
        expected_trial_name = self.container.startswith("bigdata-health-codex-")
        owned = owned or (root_workspace_label and expected_trial_name)
        if not owned:
            raise DockerBridgeError("container lacks the explicit owned-case run label")
        script = "import json,os,sys; expected=json.load(sys.stdin)['task_id']; print(json.dumps({'task_matches':os.environ.get('CHI_BENCH_TASK_ID')==expected}))"
        try:
            status = self.python_json(script, {"task_id": task_id}, timeout=min(self.timeout, 10))
        except DockerBridgeError as exc:
            raise DockerBridgeError("container task identity could not be checked") from None
        if not isinstance(status, dict) or status.get("task_matches") is not True:
            raise DockerBridgeError("container CHI_BENCH_TASK_ID does not match the selected public task")


_MCP_SCRIPT = r'''import base64,json,sys,urllib.request,urllib.error
d=json.load(sys.stdin); raw=json.dumps(d["payload"],ensure_ascii=False,separators=(",",":" )).encode()
r=urllib.request.Request("http://127.0.0.1:"+str(d["port"])+"/mcp",data=raw,headers=d["headers"],method="POST")
try:
 with urllib.request.urlopen(r,timeout=d["timeout"]) as x:
  body=x.read(2000000); out={"status":x.status,"headers":dict(x.headers.items()),"body":base64.b64encode(body).decode()}
except urllib.error.HTTPError as x:
 out={"status":x.code,"headers":dict(x.headers.items()),"body":""}
print(json.dumps(out,separators=(",",":")))
'''


class DockerMCPClient(MCPClient):
    """Use the container's loopback MCP endpoint through `docker exec` only."""

    ALLOWED_PORTS = {8020, 8100, 8200}
    # Audited public service methods in the pinned runtime: these retrieve
    # records (and may append audit events), but do not mutate clinical cases.
    # Missing MCP annotations must not turn a readback into a clinical write.
    AUDITED_READS = frozenset({
        "chart.search_patients", "chart.get_patient_chart_by_patient", "chart.list_candidate_orders",
        "cases.get_case", "cases.list_cases", "determination.get_summary",
        "cm_chart.get_chart_data", "cm_intake.get_referral", "cm_intake.list_referral_queue", "cm_outreach.get_transcript",
        "people.list_contacts", "people.list_ordering_providers", "people.list_reviewer_contacts",
        "review.get_nurse_review_data", "review.get_md_review_data",
    })

    def list_tools(self) -> list[ToolSpec]:
        specs = super().list_tools()
        self._specs = [replace(spec, effect="read")
                       if self._actual_names.get(spec.name) in self.AUDITED_READS else spec
                       for spec in specs]
        return list(self._specs)

    def __init__(self, container: str, port: int = 8100, timeout: float = 30,
                 namespace: str = "chi-bench-real-case", executor: DockerExecutor | None = None):
        if isinstance(port, bool) or port not in self.ALLOWED_PORTS:
            raise ValueError("MCP port must be one of the official actor ports 8020, 8100, or 8200")
        super().__init__(f"http://127.0.0.1:{port}/mcp", timeout=timeout, namespace=namespace)
        self.container = container
        self.port = port
        self.executor = executor or DockerExecutor(container, timeout=max(40, timeout + 5))

    def _post(self, payload: dict[str, Any], expected_id: int | None) -> dict[str, Any]:
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": self.PROTOCOL_VERSION}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        try:
            response = self.executor.python_json(_MCP_SCRIPT, {"port": self.port, "payload": payload,
                                                               "headers": headers, "timeout": self.timeout},
                                                 timeout=self.timeout + 5)
        except DockerBridgeError as exc:
            raise MCPError(f"container MCP request failed: {exc}") from None
        if not isinstance(response, dict):
            raise MCPError("container MCP returned an invalid transport response")
        status = response.get("status")
        if not isinstance(status, int) or not 200 <= status < 300:
            raise MCPError(f"MCP endpoint returned HTTP {status if isinstance(status, int) else 'error'}")
        session = response.get("headers", {})
        if isinstance(session, dict):
            self.session_id = next((v for k, v in session.items() if k.lower() == "mcp-session-id"), self.session_id)
            content_type = next((v for k, v in session.items() if k.lower() == "content-type"), "")
        else:
            content_type = ""
        try:
            body = base64.b64decode(response.get("body", ""), validate=True)
            envelope = _decode_json_or_sse(body, content_type, expected_id) if body else {}
        except (ValueError, UnicodeError, MCPError):
            raise MCPError("MCP endpoint returned an invalid response body") from None
        if expected_id is None:
            return envelope or {}
        if envelope is None:
            raise MCPError("MCP stream ended without the matching JSON-RPC response")
        if envelope.get("id") != expected_id:
            raise MCPError("MCP returned a response with a mismatched request ID")
        return envelope


MAX_WORKSPACE_FILE_BYTES = 1_000_000
DEFAULT_WORKSPACE_READ_BYTES = 30_000

_WORKSPACE_SCRIPT = (f'MAX_FILE={MAX_WORKSPACE_FILE_BYTES}; DEFAULT_READ={DEFAULT_WORKSPACE_READ_BYTES}\n' + r'''import hashlib,json,os,pathlib,sys,tempfile
d=json.load(sys.stdin); root=pathlib.Path(d["case_root"]).resolve(); roots=[pathlib.Path(x).resolve() for x in d["read_roots"]]
if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
blocked={"hidden","fixture","fixtures","test","tests","verifier","verification","expectation","expectations","solution","solutions","source","sources"}
MAX_SEARCH_FILES=2000; MAX_SEARCH_BYTES=20000000; MAX_RESULTS=10
class Fault(Exception):
 def __init__(self,code):self.code=code
def safe(p):
 parts={x.lower().replace("-","_") for x in p.parts}
 for part in p.parts:
  if part.startswith("."):return False
  stem=part.lower().split(".",1)[0].replace("-","_")
  if stem in blocked or any(stem.startswith(x) for x in ("fixture","test","verifier","expectation","solution","source")):return False
 return not any(x in blocked for x in parts)
def inside(p,r):
 try:p.relative_to(r);return True
 except ValueError:return False
def permitted(p):return inside(p,root) or any(inside(p,r) for r in roots)
def resolve(text,require_exists=True):
 if not isinstance(text,str) or not text:raise Fault("access_denied")
 p=pathlib.Path(text)
 if not p.is_absolute():
  relative=p
  p=root/relative
  # Actor document paths can be relative to the workspaces root (CASE/shared)
  # or the current case (shared/...). Resolve only against explicitly granted
  # roots of this bound case; never search other case directories. Writes keep
  # their existing private workspace semantics.
  if d['operation']!='write' and relative.parts and '..' not in relative.parts:
   cases={a for r in roots for a in (r,*r.parents) if a.parent.name=='workspaces'}
   for case in cases:
    candidate=(case.parent/relative if relative.parts[0]==case.name else case/relative)
    candidate=candidate.resolve()
    if safe(candidate) and permitted(candidate) and candidate.exists():
     p=candidate
     break
 p=p.resolve()
 if not safe(p) or not permitted(p):raise Fault("access_denied")
 if require_exists and not p.exists():raise Fault("file_not_found")
 return p
op=d["operation"]
if op=="write":
 p=resolve(d["path"],False)
 if not inside(p,root):raise PermissionError("writes are confined to this case workspace")
 b=d["content"].encode("utf-8")
 if len(b)>1000000:raise ValueError("workspace artifact exceeds size limit")
 p.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=".hh-write-",dir=str(p.parent))
 try:
  with os.fdopen(fd,"wb") as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 out={"path":str(p),"bytes_written":len(b)}
elif op in {"read","list","search","read_pdf"}:
 try:
  p=resolve(d.get("path","."),op in {"read","read_pdf"})
  if not p.exists() and p!=root:raise Fault("file_not_found")
  if op=="read":
   if not p.is_file():raise Fault("file_not_found")
   if p.is_symlink():raise Fault("access_denied")
   cap=min(int(d.get("max_file_bytes",MAX_FILE)),MAX_FILE)
   with p.open("rb") as f:b=f.read(cap+1)
   if len(b)>cap:raise Fault("file_too_large")
   if b"\0" in b:raise Fault("binary_or_invalid_utf8")
   try:text=b.decode("utf-8")
   except UnicodeDecodeError:raise Fault("binary_or_invalid_utf8")
   chunk_cap=min(max(4,int(d.get("max_bytes",DEFAULT_READ))),MAX_FILE)
   offset=max(0,int(d.get("offset_chars",0))); offset=min(offset,len(text)); end=offset; used=0
   while end<len(text):
    width=len(text[end].encode("utf-8"))
    if used+width>chunk_cap:break
    used+=width;end+=1
   out={"path":str(p),"text":text[offset:end],"bytes":len(b),"total_chars":len(text),
        "offset_chars":offset,"next_offset":end,"has_more":end<len(text),"sha256":hashlib.sha256(b).hexdigest()}
  elif op=="read_pdf":
   MAX_PDF_BYTES=10000000;MAX_PDF_PAGES=1000;MAX_PDF_PAGES_PER_CALL=10;MAX_PDF_CHARS=20000
   if not p.is_file():raise Fault("file_not_found")
   if p.is_symlink():raise Fault("access_denied")
   try:size=p.stat().st_size
   except OSError:raise Fault("access_denied")
   if size>MAX_PDF_BYTES:raise Fault("file_too_large")
   try:import pypdf
   except ImportError:raise Fault("parser_unavailable")
   import io,logging,warnings
   logging.getLogger("pypdf").setLevel(logging.CRITICAL)
   try:
    with p.open("rb") as f:pdf_bytes=f.read(MAX_PDF_BYTES+1)
   except OSError:raise Fault("access_denied")
   if len(pdf_bytes)>MAX_PDF_BYTES:raise Fault("file_too_large")
   digest=hashlib.sha256(pdf_bytes).hexdigest()
   try:
    with warnings.catch_warnings():
     warnings.simplefilter("ignore")
     reader=pypdf.PdfReader(io.BytesIO(pdf_bytes),strict=False)
     if reader.is_encrypted:raise Fault("encrypted_pdf")
     total_pages=len(reader.pages)
     if total_pages<1:raise Fault("invalid_pdf")
     if total_pages>MAX_PDF_PAGES:raise Fault("parser_budget_exceeded")
   except Fault:raise
   except Exception:raise Fault("invalid_pdf")
   page_start=max(1,int(d.get("page_start",1)));page_count=max(1,min(int(d.get("page_count",3)),MAX_PDF_PAGES_PER_CALL))
   if page_start>total_pages:raise Fault("page_out_of_range")
   max_chars=max(1,min(int(d.get("max_chars",MAX_PDF_CHARS)),MAX_PDF_CHARS))
   page_offset=max(0,int(d.get("page_char_offset",0)));page_end=min(total_pages,page_start+page_count-1)
   pages=[];chars_used=0;truncated=False;next_page=page_end+1;next_char_offset=0;extractable_pages=0
   for page_number in range(page_start,page_end+1):
    try:
     with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      extracted=reader.pages[page_number-1].extract_text()
    except Exception:raise Fault("invalid_pdf")
    text=extracted if isinstance(extracted,str) else ""
    if not text.strip():
     pages.append({"page":page_number,"text":"","char_offset":0,"total_chars":0,
                   "has_more_text":False,"text_status":"text_unavailable_needs_ocr"})
     continue
    extractable_pages+=1
    offset=page_offset if page_number==page_start else 0
    if offset>len(text):raise Fault("page_char_offset_out_of_range")
    available=max_chars-chars_used
    if available<=0:
     truncated=True;next_page=page_number;next_char_offset=offset;break
    end=min(len(text),offset+available);piece=text[offset:end]
    chars_used+=len(piece);has_more_text=end<len(text)
    pages.append({"page":page_number,"text":piece,"char_offset":offset,"total_chars":len(text),
                  "has_more_text":has_more_text,
                  "text_status":"text_available" if piece.strip() else "text_unavailable_needs_ocr"})
    if has_more_text:
     truncated=True;next_page=page_number;next_char_offset=end;break
   if extractable_pages==0:raise Fault("text_unavailable")
   has_more=truncated or page_end<total_pages
   if not truncated and page_end<total_pages:next_page=page_end+1;next_char_offset=0
   out={"path":str(p),"sha256":digest,"total_pages":total_pages,"page_start":page_start,
        "pages":pages,"extraction_method":"pypdf text-layer extraction",
        "pypdf_version":pypdf.__version__,"text_layer_only":True,"ocr_performed":False,
        "no_layout_validation":True,"max_chars":max_chars,"truncated":truncated,
        "next_page":next_page if has_more else None,"next_char_offset":next_char_offset if has_more else None,
        "has_more":has_more,"parser_budget":{"max_pdf_bytes":MAX_PDF_BYTES,
        "max_total_pages":MAX_PDF_PAGES,"max_pages_per_call":MAX_PDF_PAGES_PER_CALL,
        "max_output_chars":MAX_PDF_CHARS}}
  elif op=="list":
   if not p.is_dir() and p.exists():raise Fault("file_not_found")
   files=[];truncated=False
   for current,dirs,names in os.walk(p,followlinks=False):
    here=pathlib.Path(current)
    try:real_here=here.resolve(strict=True)
    except OSError:dirs[:]=[];continue
    if here.is_symlink() or not safe(here) or not safe(real_here) or not permitted(real_here):dirs[:]=[];continue
    dirs.sort();kept=[]
    for name in dirs:
     child=here/name
     if child.is_symlink() or not safe(child):continue
     try:real_child=child.resolve(strict=True)
     except OSError:continue
     if safe(real_child) and permitted(real_child):kept.append(name)
    dirs[:]=kept
    for name in sorted(names):
     child=here/name
     if child.is_symlink() or not safe(child):continue
     try:real_child=child.resolve(strict=True)
     except OSError:continue
     if not safe(real_child) or not real_child.is_file() or not permitted(real_child):continue
     label=str(real_child.relative_to(root)) if inside(real_child,root) else str(real_child)
     if len(files)>=1000:truncated=True;break
     files.append(label)
    if truncated:break
   out={"files":files,"truncated":truncated}
  else:
   query=d.get("query");
   if not isinstance(query,str) or not query:raise Fault("access_denied")
   limit=max(1,min(int(d.get("max_results",3)),MAX_RESULTS));q=query.casefold()
   matches=[];scanned_files=0;scanned_bytes=0;skipped_large=0;skipped_binary=0;truncated=False;limits_hit=[]
   def label_for(file):return str(file.relative_to(root)) if inside(file,root) else str(file)
   def iter_files(base):
    if base.is_file():
     yield base;return
    for current,dirs,names in os.walk(base,followlinks=False):
     here=pathlib.Path(current)
     try:real_here=here.resolve(strict=True)
     except OSError:dirs[:]=[];continue
     if here.is_symlink() or not safe(here) or not safe(real_here) or not permitted(real_here):dirs[:]=[];continue
     dirs.sort();kept=[]
     for name in dirs:
      child=here/name
      if child.is_symlink() or not safe(child):continue
      try:real_child=child.resolve(strict=True)
      except OSError:continue
      if safe(real_child) and permitted(real_child):kept.append(name)
     dirs[:]=kept
     for name in sorted(names):
      child=here/name
      if child.is_symlink() or not safe(child):continue
      try:real_child=child.resolve(strict=True)
      except OSError:continue
      if safe(real_child) and real_child.is_file() and permitted(real_child):yield real_child
   for file in iter_files(p):
    if scanned_files>=MAX_SEARCH_FILES:truncated=True;limits_hit.append("files");break
    scanned_files+=1
    try:size=file.stat().st_size
    except OSError:continue
    if size>MAX_FILE:
     skipped_large+=1;truncated=True
     if "per_file_bytes" not in limits_hit:limits_hit.append("per_file_bytes")
     continue
    if scanned_bytes+size>MAX_SEARCH_BYTES:truncated=True;limits_hit.append("bytes");break
    try:
     with file.open("rb") as f:b=f.read(MAX_FILE+1)
    except OSError:continue
    if len(b)>MAX_FILE:
     skipped_large+=1;truncated=True
     if "per_file_bytes" not in limits_hit:limits_hit.append("per_file_bytes")
     continue
    if scanned_bytes+len(b)>MAX_SEARCH_BYTES:
     truncated=True
     if "bytes" not in limits_hit:limits_hit.append("bytes")
     break
    scanned_bytes+=len(b)
    if b"\0" in b:skipped_binary+=1;continue
    try:text=b.decode("utf-8")
    except UnicodeDecodeError:skipped_binary+=1;continue
    folded=[];origin=[]
    for index,char in enumerate(text):
     for part in char.casefold():folded.append(part);origin.append(index)
    folded_text="".join(folded);at=0;digest=hashlib.sha256(b).hexdigest()
    while True:
     found=folded_text.find(q,at)
     if found<0:break
     if len(matches)>=limit:truncated=True;limits_hit.append("results");break
     start=origin[found];end=origin[found+len(q)-1]+1
     snippet_start=max(0,start-120);snippet_end=min(len(text),snippet_start+400)
     if end>snippet_end:snippet_start=max(0,end-400);snippet_end=min(len(text),snippet_start+400)
     matches.append({"path":label_for(file),"line":text.count("\n",0,start)+1,"char_offset":start,
                     "snippet":text[snippet_start:snippet_end],"sha256":digest})
     at=found+max(1,len(q))
    if truncated and "results" in limits_hit:break
   out={"matches":matches,"scanned_files":scanned_files,"scanned_bytes":scanned_bytes,
        "skipped_large_files":skipped_large,"skipped_binary_files":skipped_binary,
        "truncated":truncated,"limits_hit":limits_hit,
        "limits":{"files":MAX_SEARCH_FILES,"total_bytes":MAX_SEARCH_BYTES,"per_file_bytes":MAX_FILE,"results":limit}}
 except Fault as exc:
  messages={"text_unavailable":"No extractable text layer was found; OCR is required.",
            "parser_budget_exceeded":"PDF exceeds the configured parser page budget.",
            "page_out_of_range":"Requested PDF page is outside the document.",
            "page_char_offset_out_of_range":"Requested text offset is outside the page.",
            "parser_unavailable":"PDF text parser is unavailable in this runtime."}
  out={"error":{"code":exc.code,"message":messages.get(exc.code,exc.code.replace("_"," "))}}
  if exc.code in {'access_denied','file_not_found'}:
   out['error']['allowed_read_roots']=[str(root),*[str(r) for r in roots]]
   out['error']['recovery']='List an allowed case directory, or read/search the exact approved reference path. A reference file does not grant its parent directory.'
 except PermissionError:out={"error":{"code":"access_denied","message":"access denied"}}
 except FileNotFoundError:out={"error":{"code":"file_not_found","message":"file not found"}}
 except (OSError,ValueError,UnicodeError):out={"error":{"code":"access_denied","message":"operation failed safely"}}
else:raise ValueError("unsupported workspace operation")
print(json.dumps(out,ensure_ascii=False,separators=(",",":")))
''')


_CORPUS_SCRIPT = _WORKSPACE_SCRIPT.split('op=d["operation"]',1)[0] + r'''
try:
 p=resolve(d.get('path','.'));documents=[];entries=[];total=0
 def files(base):
  if base.is_file():yield base;return
  for here,dirs,names in os.walk(base,followlinks=False):
   here=pathlib.Path(here)
   dirs[:]=sorted(x for x in dirs if not (here/x).is_symlink() and safe(here/x) and permitted((here/x).resolve()))
   for name in sorted(names):
    file=here/name
    if file.is_symlink() or not safe(file) or not permitted(file.resolve()):continue
    if file.is_file():yield file
 for file in files(p):
  size=file.stat().st_size;total+=size
  if len(entries)>=5000 or total>50000000 or size>10000000:raise Fault('complete_corpus_budget_exceeded')
  raw=file.read_bytes();entries.append((file,raw,hashlib.sha256(raw).hexdigest()))
 manifest=[{'path':str(f),'bytes':len(raw),'sha256':digest} for f,raw,digest in entries]
 fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 if d.get('manifest_only'):
  out={'manifest_sha256':fingerprint,'files':len(entries),'bytes':total,'coverage_complete':True}
 else:
  cursor=d.get('cursor') or {'file_index':int(d.get('file_offset',0)),'page_index':0,'text_offset':0}
  next_cursor=None;used=0;stop=False;excluded=[]
  for file_index,(file,raw,digest) in enumerate(entries):
   if file_index<cursor['file_index']:continue
   texts=[]
   if file.suffix.lower()=='.pdf':
    try:
     import pypdf,io,warnings,logging
     logging.getLogger('pypdf').setLevel(logging.CRITICAL)
     with warnings.catch_warnings():
      warnings.simplefilter('ignore');reader=pypdf.PdfReader(io.BytesIO(raw),strict=False)
      if reader.is_encrypted or len(reader.pages)>1000:raise ValueError('unsupported PDF')
      for i,page in enumerate(reader.pages):texts.append((i+1,page.extract_text() or ''))
      if not any(t.strip() for _,t in texts):raise ValueError('no text layer')
    except Exception:excluded.append({'path':str(file),'reason':'pdf_text_unavailable'});continue
   else:
    if b'\0' in raw:excluded.append({'path':str(file),'reason':'binary'});continue
    try:texts=[(None,raw.decode('utf-8'))]
    except UnicodeDecodeError:excluded.append({'path':str(file),'reason':'invalid_utf8'});continue
   for page_index,(page,text) in enumerate(texts):
    if file_index==cursor['file_index'] and page_index<cursor['page_index']:continue
    at=cursor['text_offset'] if file_index==cursor['file_index'] and page_index==cursor['page_index'] else 0
    while at<len(text):
     part=text[at:at+50000]
     source={'path':str(file),'sha256':digest,'page':page,'offset_chars':at,'file_index':file_index,
             'has_more':at+len(part)<len(text),'total_chars':len(text),'text_layer_only':page is not None,
             'trusted_fixed_reference':str(file).startswith('/workspace/skills/managed-care-operations-handbook/references/')}
     item={'id':str(file)+(('#page='+str(page)) if page else ''),'title':file.name,'text':part,'source':source}
     length=len(json.dumps(item,ensure_ascii=False).encode())
     if used+length>1500000 or len(documents)>=256:
      next_cursor={'file_index':file_index,'page_index':page_index,'text_offset':at};stop=True;break
     documents.append(item);used+=length;at+=len(part)
    if stop:break
   if stop:break
  out={'documents':documents,'corpus_partial':next_cursor is not None or bool(excluded),
       'manifest_sha256':fingerprint,'scanned_files':len(entries),'source_bytes':total,
       'next_cursor':next_cursor,'next_file_offset':next_cursor['file_index'] if next_cursor else None,
       'excluded_sources':excluded,'coverage_complete':next_cursor is None and not excluded}
except (Fault,OSError,ValueError) as exc:
 out={'error':{'code':getattr(exc,'code','corpus_access_failed'),'allowed_read_roots':[str(root),*[str(r) for r in roots]]}}
print(json.dumps(out,ensure_ascii=False))
'''



class DockerWorkspaceTools:
    """Case-scoped Linux workspace with explicit read roots and no shell tool."""

    _BLOCKED = {"hidden", "fixture", "fixtures", "test", "tests", "verifier", "verification",
                "expectation", "expectations", "solution", "solutions", "source", "sources"}

    def __init__(self, container: str, root: str, scope: Scope, read_roots: Iterable[str] = (),
                 max_read_bytes: int = 1_000_000, executor: DockerExecutor | None = None, progress=None):
        self.progress=progress
        if not isinstance(root, str) or not root.startswith("/"):
            raise ValueError("workspace root must be an absolute Linux path")
        if not isinstance(max_read_bytes, int) or isinstance(max_read_bytes, bool) or not 4 <= max_read_bytes <= 1_000_000:
            raise ValueError("max_read_bytes must be between 4 and 1000000")
        if any(not isinstance(p, str) or not p.startswith("/") for p in read_roots):
            raise ValueError("read roots must be explicit absolute Linux paths")
        self.container, self.root, self.scope = container, PurePosixPath(root), scope
        self.case_root = self.root / scope.key
        self.read_roots = tuple(PurePosixPath(p) for p in read_roots)
        self.max_read_bytes = max_read_bytes
        self.executor = executor or DockerExecutor(container)
        self._hybrid_index = None
        self._hybrid_corpus_cache = {}
        self._specs = [
            ToolSpec("workspace.read_file", "Read a bounded UTF-8 excerpt from a current-case or configured reference file. Large files require offset_chars continuation; use workspace.search_files before reading large references. Use workspace.read_pdf for PDF text layers. The response includes total size, offsets, has_more, and the full-file SHA-256.", {
                "type": "object", "required": ["path"], "additionalProperties": False,
                "properties": {"path": {"type": "string", "minLength": 1},
                               "max_bytes": {"type": "integer", "minimum": 4, "maximum": max_read_bytes},
                               "offset_chars": {"type": "integer", "minimum": 0}},
            }, effect="read"),
            ToolSpec("workspace.write_file", "Write a UTF-8 artifact only inside this case workspace.", {
                "type": "object", "required": ["path", "content"], "additionalProperties": False,
                "properties": {"path": {"type": "string", "minLength": 1}, "content": {"type": "string"}},
            }, effect="write"),
            ToolSpec("workspace.list_files", "List files within this case workspace or configured read-only references; workspace paths are relative and reference paths are absolute.", {
                "type": "object", "required": [], "additionalProperties": False,
                "properties": {"path": {"type": "string"}},
            }, effect="read"),
            ToolSpec("workspace.search_files", "Search case workspace files, or a selected configured read-only reference root, for a literal case-insensitive UTF-8 text phrase. Defaults to the case workspace; pass an approved reference root path to search it. PDFs are skipped; use workspace.read_pdf for PDF text layers. Bounded to 2,000 files, 20 MB scanned, 1 MB per file and 10 snippets; snippets carry path, line, character offset and full-file SHA-256. Binary and invalid UTF-8 files are skipped.", {
                "type": "object", "required": ["query"], "additionalProperties": False,
                "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 500},
                               "path": {"type": "string", "minLength": 1},
                               "max_results": {"type": "integer", "minimum": 1, "maximum": 10}},
            }, effect="read"),
            ToolSpec("workspace.read_pdf", "Read selected pages from an approved current-case or configured-reference PDF using pypdf text-layer extraction only. No OCR or layout validation. Page selection is 1-based; use next_page and page_char_offset to continue truncated output. Enforced limits: 10 MB PDF, 1,000 total pages, 10 pages per call and 20,000 output characters.", {
                "type": "object", "required": ["path"], "additionalProperties": False,
                "properties": {"path": {"type": "string", "minLength": 1},
                               "page_start": {"type": "integer", "minimum": 1},
                               "page_count": {"type": "integer", "minimum": 1, "maximum": 10},
                               "page_char_offset": {"type": "integer", "minimum": 0},
                               "max_chars": {"type": "integer", "minimum": 1, "maximum": 20000}},
            }, effect="read"),
        ]
        variants=[]
        for spec in self._specs:
            if spec.name not in {'workspace.read_file','workspace.read_pdf','workspace.search_files'}:continue
            variants.append({'type':'object','required':['operation','arguments'],'additionalProperties':False,
                'properties':{'operation':{'const':spec.name.split('.',1)[1]},'arguments':spec.input_schema}})
        self._specs.append(ToolSpec('workspace.read_many',
            'Group up to six independent approved file/PDF reads or literal file searches in one model turn. '
            'Use read_file/read_pdf only for known locations; search for unknown sources first, then read found locations. '
            'Every item uses the existing same-case/reference path checks. No writes, hidden files, model calls or automatic '
            'following of search hits. Combined output is bounded; errors/continuations remain explicit. '
            'Policy citations use this original evidence ID and /items/N/result/text (or the returned PDF page text pointer).',
            {'type':'object','required':['requests'],'additionalProperties':False,'properties':{
                'requests':{'type':'array','minItems':1,'maxItems':6,'items':{'oneOf':variants}},
                'max_chars':{'type':'integer','minimum':4000,'maximum':24000}}},effect='read'))
        self._specs.append(ToolSpec('workspace.hybrid_search',
            'Find relevant policy/narrative passages using BM25 plus LOCAL GPU semantic embeddings. '
            'Choose an approved reference directory or the current case workspace. Actual reader path restrictions apply. '
            'Results contain exact text, source hashes, neighboring context, headers and qualifying sections. '
            'A calibrated cosine floor screens basic relevance before ranking. Empty results mean no passage cleared '
            'that screen, not proof the information is absent; refine the query or use permitted exact reads. '
            'Ranks do not prove policy applicability or eligibility. Read linked conditions and effective versions. '
            'Cite this tool evidence ID with /matches/N/text or /documents/N/qualifying_sections/M/text. '
            'No OCR, provider API, patient selection, state query or clinical write. A missing embedding runtime is an error, not silent lexical fallback.',
            {'type':'object','required':['query'],'additionalProperties':False,'properties':{
                'query':{'type':'string','minLength':1,'maxLength':1000},
                'path':{'type':'string','minLength':1},
                'max_results':{'type':'integer','minimum':1,'maximum':8},
                'max_chars':{'type':'integer','minimum':4000,'maximum':24000}}},effect='read'))

    def bind_scope(self, scope: Scope) -> None:
        if scope != self.scope:
            raise ValueError("DockerWorkspaceTools is bound to a different case scope")

    def list_tools(self) -> list[ToolSpec]:
        return list(self._specs)

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name=='workspace.hybrid_search':
            from .hybrid_search import HybridIndex,DockerEmbedder,CorpusCoverageError,relevance_settings
            self._retrieval_progress("retrieval_progress",stage="checking_corpus")
            corpus=self._collect_hybrid_corpus(arguments.get('path','.'))
            if 'error' in corpus:return corpus
            calibration=relevance_settings('policy' if all(d['source'].get('trusted_fixed_reference') for d in corpus['documents']) else 'narrative')
            if self._hybrid_index is None:
                self._hybrid_index=HybridIndex(self.scope.key,DockerEmbedder(),reference_cache=True,
                    relevance_floor=calibration['minimum_cosine'],progress=self._retrieval_progress,query_cache=True)
            else:
                self._hybrid_index.relevance_floor=calibration['minimum_cosine']
            try:
                result=self._hybrid_index.search(corpus['documents'],arguments['query'],namespace=self.scope.key,
                    limit=arguments.get('max_results',5),max_chars=arguments.get('max_chars',16000))
            except CorpusCoverageError:
                return {'error':{'code':'corpus_coverage_incomplete','message':'The entire selected corpus could not be indexed within resource limits. No prefix ranking was returned.'}}
            except RuntimeError:
                return {'error':{'code':'semantic_backend_unavailable','message':'Local GPU embeddings are unavailable; no semantic search result was produced.'},
                        'semantic_executed':False}
            result['coverage_complete']=True
            result['relevance_calibration']=calibration
            result['scanned_files']=corpus.get('scanned_files')
            result['creates_evidence']=True
            return result
        if name=='workspace.read_many':
            from .schema import validate_arguments
            from .working_set import packed
            spec=next(s for s in self._specs if s.name==name)
            validate_arguments(spec,arguments,self.scope)
            budget=arguments.get('max_chars',20000);requests=arguments['requests']
            share=max(500,(budget-1200)//len(requests));items=[]
            for index,request in enumerate(requests):
                operation=request['operation'];args=dict(request['arguments'])
                if operation=='read_file':args['max_bytes']=min(args.get('max_bytes',self.max_read_bytes),max(4,(share-450)//3))
                elif operation=='read_pdf':args['max_chars']=min(args.get('max_chars',20000),max(1,(share-450)//3))
                elif operation=='search_files':args['max_results']=min(args.get('max_results',3),max(1,share//1400))
                try:result=self.call('workspace.'+operation,args)
                except (RuntimeError,ValueError,KeyError):result={'error':'workspace_read_failed','instruction':'The original path/reader checks still apply; inspect this request separately if needed.'}
                item={'request_index':index,'operation':operation,'result':result}
                if len(packed(item))>share:
                    item={'request_index':index,'operation':operation,'result':{'error':'batch_item_output_budget',
                          'instruction':'Read this source separately with a narrower passage/page selection.'}}
                items.append(item)
            return {'items':items,'scope':'current_case_and_approved_references',
                    'instruction':'Original observed excerpts, not semantic answers. Each reader retains its continuation and hash metadata; errors are not evidence of absence.'}
        if name == "workspace.read_file":
            data = {"operation": "read", "case_root": str(self.case_root), "read_roots": list(map(str, self.read_roots)),
                    "path": arguments["path"], "max_bytes": min(arguments.get("max_bytes", 30_000), self.max_read_bytes),
                    "offset_chars": arguments.get("offset_chars", 0), "max_file_bytes": self.max_read_bytes}
        elif name == "workspace.write_file":
            data = {"operation": "write", "case_root": str(self.case_root), "read_roots": list(map(str, self.read_roots)),
                    "path": arguments["path"], "content": arguments["content"]}
        elif name == "workspace.list_files":
            data = {"operation": "list", "case_root": str(self.case_root), "read_roots": list(map(str, self.read_roots)),
                    "path": arguments.get("path", ".")}
        elif name == "workspace.search_files":
            data = {"operation": "search", "case_root": str(self.case_root), "read_roots": list(map(str, self.read_roots)),
                    "path": arguments.get("path", "."), "query": arguments["query"],
                    "max_results": min(arguments.get("max_results", 3), 10)}
        elif name == "workspace.read_pdf":
            data = {"operation": "read_pdf", "case_root": str(self.case_root), "read_roots": list(map(str, self.read_roots)),
                    "path": arguments["path"], "page_start": arguments.get("page_start", 1),
                    "page_count": min(arguments.get("page_count", 3), 10),
                    "page_char_offset": arguments.get("page_char_offset", 0),
                    "max_chars": min(arguments.get("max_chars", 20_000), 20_000)}
        else:
            raise KeyError(f"unknown workspace tool: {name}")
        try:
            return self.executor.python_json(_WORKSPACE_SCRIPT, data)
        except DockerBridgeError as exc:
            raise RuntimeError(str(exc)) from None

    def _retrieval_progress(self,event,**fields):
        if self.progress:self.progress(event,tool_name='workspace.hybrid_search',**fields)

    def _collect_hybrid_corpus(self,path):
        """Transport pages are bounded; source coverage is not an alphabetical sample."""
        data={'operation':'corpus','case_root':str(self.case_root),'read_roots':list(map(str,self.read_roots)),'path':path}
        manifest=self.executor.python_json(_CORPUS_SCRIPT,{**data,'manifest_only':True})
        if 'error' in manifest:return manifest
        prior=self._hybrid_corpus_cache.get(path)
        if prior and prior['manifest_sha256']==manifest['manifest_sha256']:return prior
        self._retrieval_progress("retrieval_progress",stage="collecting_corpus",file_count=manifest["files"])
        assembled={};cursor=None;seen=set()
        for _ in range(256):
            part=self.executor.python_json(_CORPUS_SCRIPT,{**data,'cursor':cursor})
            if 'error' in part:return part
            if part.get('manifest_sha256')!=manifest['manifest_sha256']:
                return {'error':{'code':'corpus_changed_during_collection'}}
            if part.get('excluded_sources'):
                return {'error':{'code':'corpus_coverage_incomplete','excluded_sources':part['excluded_sources'],
                    'message':'Some permitted sources could not be indexed; no partial ranking was returned.'}}
            for doc in part['documents']:
                previous=assembled.get(doc['id']);offset=doc['source']['offset_chars']
                if previous:
                    if previous['source']['sha256']!=doc['source']['sha256'] or len(previous['text'])!=offset:
                        return {'error':{'code':'corpus_fragment_mismatch'}}
                    previous['text']+=doc['text'];previous['source']['has_more']=doc['source']['has_more']
                else:
                    if offset!=0:return {'error':{'code':'corpus_fragment_missing_prefix'}}
                    assembled[doc['id']]={**doc,'source':dict(doc['source'])}
            cursor=part.get('next_cursor')
            if cursor is None:break
            key=(cursor['file_index'],cursor['page_index'],cursor['text_offset'])
            if key in seen:return {'error':{'code':'corpus_cursor_did_not_advance'}}
            seen.add(key)
        else:return {'error':{'code':'complete_corpus_budget_exceeded'}}
        if any(d['source']['has_more'] for d in assembled.values()):return {'error':{'code':'corpus_fragment_incomplete'}}
        final=self.executor.python_json(_CORPUS_SCRIPT,{**data,'manifest_only':True})
        if final.get('manifest_sha256')!=manifest['manifest_sha256']:return {'error':{'code':'corpus_changed_during_collection'}}
        result={'documents':list(assembled.values()),'manifest_sha256':manifest['manifest_sha256'],
                'corpus_partial':False,'coverage_complete':True,'scanned_files':manifest['files']}
        self._hybrid_corpus_cache[path]=result
        # Keep a few source collections when alternating policy and requirements
        # directories. Every reuse still rechecks its manifest above.
        while len(self._hybrid_corpus_cache)>4 or sum(
            len(d['text']) for v in self._hybrid_corpus_cache.values() for d in v['documents'])>50000000:
            self._hybrid_corpus_cache.pop(next(iter(self._hybrid_corpus_cache)))
        return result
