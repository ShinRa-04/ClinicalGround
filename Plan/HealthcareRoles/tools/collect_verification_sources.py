"""Collect public primary evidence in ignored cache; do not publish copyrighted source text."""
from __future__ import annotations
import concurrent.futures
import hashlib
import io
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

from lxml import html
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
CACHE=ROOT/'Runner/.cache/role-verification'
CACHE.mkdir(parents=True,exist_ok=True)
SOURCES=json.loads((BASE/'data/sources.json').read_text(encoding='utf-8'))
ADDITIONAL=BASE/'verification/additional_sources.json'
if ADDITIONAL.exists():
    existing_ids={s['id'] for s in SOURCES}
    SOURCES += [s for s in json.loads(ADDITIONAL.read_text(encoding='utf-8')) if s['id'] not in existing_ids]
ROUND3=BASE/'verification/additional_sources_round3.json'
if ROUND3.exists():
    existing_ids={s['id'] for s in SOURCES}
    SOURCES += [s for s in json.loads(ROUND3.read_text(encoding='utf-8')) if s['id'] not in existing_ids]
ROUND4=BASE/'verification/additional_sources_round4.json'
if ROUND4.exists():
    existing_ids={s['id'] for s in SOURCES}
    SOURCES += [s for s in json.loads(ROUND4.read_text(encoding='utf-8')) if s['id'] not in existing_ids]
ROUND5=BASE/'verification/additional_sources_round5.json'
if ROUND5.exists():
    existing_ids={s['id'] for s in SOURCES}
    SOURCES += [s for s in json.loads(ROUND5.read_text(encoding='utf-8')) if s['id'] not in existing_ids]


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def normalize(text):
    return re.sub(r'\s+',' ',text).strip()


def tool_passages(text):
    rows=[]
    for line in text.splitlines():
        m=re.match(r'L(\d+)(?:@P(\d+)(?:-\d+)?)?:\s*(.*)',line)
        if m and normalize(m[3]):
            rows.append(dict(locator='tool line '+m[1]+(' / PDF page '+str(int(m[2])+1) if m[2] else ''),text=normalize(m[3])))
    return rows


def fetch(source):
    id,url=source['id'],source['url']
    target=CACHE/(id+'.json')
    if target.exists():
        return json.loads(target.read_text(encoding='utf-8'))
    record=dict(id=id,url=url,retrieved_utc=datetime.now(timezone.utc).isoformat(),kind=source['kind'])
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Healthcare-role-public-source-research/1.0','Accept':'text/html,application/pdf,application/xml;q=0.9,*/*;q=0.8'})
        with urllib.request.urlopen(request,timeout=25) as response:
            content=response.read(24_000_000); record.update(final_url=response.url,status=response.status,content_type=response.headers.get('Content-Type',''),byte_sha256=hashlib.sha256(content).hexdigest())
        if content.startswith(b'%PDF'):
            reader=PdfReader(io.BytesIO(content)); rows=[]
            for page_number,page in enumerate(reader.pages,1):
                for paragraph_number,paragraph in enumerate(re.split(r'\n\s*\n',page.extract_text() or ''),1):
                    if normalize(paragraph): rows.append(dict(locator=f'PDF page {page_number}, block {paragraph_number}',text=normalize(paragraph)))
            record['format']='pdf'
        else:
            tree=html.fromstring(content)
            for element in tree.xpath('//script|//style|//nav|//footer|//header|//noscript'):
                element.drop_tree()
            bodies=tree.xpath('//main|//article|//*[@id="content"]|//*[@id="main-content"]')
            body=max(bodies,key=lambda e:len(e.text_content())) if bodies else tree
            rows=[]; seen=set()
            for number,element in enumerate(body.xpath('.//h1|.//h2|.//h3|.//h4|.//p|.//li|.//td|.//dd'),1):
                text=normalize(element.text_content())
                if len(text)>=20 and text not in seen:
                    seen.add(text); rows.append(dict(locator=f'HTML {element.tag} block {number}',text=text))
            record['format']='html'
        record['paragraphs']=rows
        joined='\n'.join(p['text'] for p in rows)
        record['text_sha256']=sha(joined)
        record['retrieval_status']='retrieved' if len(joined)>150 else 'insufficient_body'
        if any(t in joined.lower() for t in ['your request has been flagged','access denied','captcha','request access']) and len(joined)<5000:
            record['retrieval_status']='access_blocked'
    except Exception as exc:
        record.update(retrieval_status='failed',error=type(exc).__name__+': '+str(exc),paragraphs=[])
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return record


def main():
    previous_path=CACHE/'previous_tool_excerpts.json'
    previous=json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
    fresh_path=CACHE/'fresh_tool_excerpts.json'
    fresh=json.loads(fresh_path.read_text(encoding='utf-8')) if fresh_path.exists() else {}
    additional_tool=CACHE/'additional_tool_excerpts.json'
    if additional_tool.exists():
        fresh.update(json.loads(additional_tool.read_text(encoding='utf-8')))
    additional_tool_2=CACHE/'additional_tool_excerpts_2.json'
    if additional_tool_2.exists():
        fresh.update(json.loads(additional_tool_2.read_text(encoding='utf-8')))
    additional_tool_3=CACHE/'additional_tool_excerpts_3.json'
    if additional_tool_3.exists():
        fresh.update(json.loads(additional_tool_3.read_text(encoding='utf-8')))
    additional_tool_4=CACHE/'additional_tool_excerpts_4.json'
    if additional_tool_4.exists():
        fresh.update(json.loads(additional_tool_4.read_text(encoding='utf-8')))
    additional_tool_5=CACHE/'additional_tool_excerpts_5.json'
    if additional_tool_5.exists():
        fresh.update(json.loads(additional_tool_5.read_text(encoding='utf-8')))
    archived_path=CACHE/'earlier_archived_excerpts.json'
    archived=json.loads(archived_path.read_text(encoding='utf-8')) if archived_path.exists() else {}
    keymap={**{f'B{i:02}':f'B{i:02}' for i in range(1,24)},**{f'A{i:02}':f'A{i:02}' for i in range(1,18)}}
    keymap.update(A02='audit_D12',A03='audit_D13',A06='audit_D22',A07='audit_D23',A08='A08_fallback')
    for source in SOURCES:
        key=keymap.get(source['id'])
        if key in previous:
            paragraphs=tool_passages(previous[key])
            record=dict(id=source['id'],url=source['url'],retrieval_status='tool_excerpt',format='tool_lines',
                retrieval_note='Primary page/tool excerpt retrieved earlier in this conversation; not necessarily the entire page. Original source access/edition limits remain.',
                text_sha256=sha('\n'.join(p['text'] for p in paragraphs)),paragraphs=paragraphs)
            (CACHE/(source['id']+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for source in SOURCES:
        text=fresh.get(source['id'])
        if not text: continue
        paragraphs=tool_passages(text)
        if len(paragraphs)<5 or 'Your request has been flagged' in text:
            continue
        record=dict(id=source['id'],url=source['url'],retrieval_status='tool_excerpt',format='tool_lines',
            retrieval_note='Primary page excerpt re-opened during deep verification; not necessarily entire page.',
            text_sha256=sha('\n'.join(p['text'] for p in paragraphs)),paragraphs=paragraphs)
        (CACHE/(source['id']+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for source in SOURCES:
        text=archived.get(source['id'])
        if not text: continue
        paragraphs=tool_passages(text)
        if len(paragraphs)<5: continue
        target=CACHE/(source['id']+'.json')
        existing=json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
        if existing.get('retrieval_status') in ['retrieved','tool_excerpt']: continue
        record=dict(id=source['id'],url=source['url'],retrieval_status='earlier_tool_excerpt',format='tool_lines',
            retrieval_note='Earlier primary-source tool result archived from this conversation. Fresh retrieval failed; not evidence of current availability.',
            fresh_failure=existing.get('error',existing.get('retrieval_status')),
            text_sha256=sha('\n'.join(p['text'] for p in paragraphs)),paragraphs=paragraphs)
        target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for source in SOURCES:
        target=CACHE/(source['id']+'.json')
        existing=json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
        if existing.get('retrieval_status') in ['retrieved','tool_excerpt','earlier_tool_excerpt','alias_excerpt']: continue
        for other in SOURCES:
            if other['id']==source['id'] or other['url']!=source['url']: continue
            alias_path=CACHE/(other['id']+'.json')
            if not alias_path.exists():continue
            alias=json.loads(alias_path.read_text(encoding='utf-8'))
            if alias.get('retrieval_status') not in ['retrieved','tool_excerpt','earlier_tool_excerpt']:continue
            alias=dict(alias,id=source['id'],retrieval_status='alias_excerpt',alias_of=other['id'],direct_failure=existing.get('error'))
            target.write_text(json.dumps(alias,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');break
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(fetch,SOURCES))
    manifest=[{k:r.get(k) for k in ['id','url','retrieval_status','format','byte_sha256','text_sha256','error']}|{'paragraphs':len(r['paragraphs'])} for r in records]
    (CACHE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    counts={status:sum(r['retrieval_status']==status for r in records) for status in sorted({r['retrieval_status'] for r in records})}
    print(json.dumps(dict(sources=len(records),retrieval_status=counts,failures=[dict(id=r['id'],error=r.get('error',r['retrieval_status'])) for r in records if r['retrieval_status'] not in ['retrieved','tool_excerpt']]),indent=2))


if __name__=='__main__':main()
