"""Capture already-inspected public reference URLs in ignored cache; never execute content."""
import concurrent.futures
import datetime
import hashlib
import json
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
sources=json.loads((BASE/'foundation_sources.json').read_text(encoding='utf-8'))
cache=BASE/'_cache/foundations';cache.mkdir(parents=True,exist_ok=True)


def capture(source):
    id=source['id'];file=cache/(id+'.bin');receipt=cache/(id+'.json')
    if file.exists() and receipt.exists():return json.loads(receipt.read_text(encoding='utf-8'))
    result=dict(id=id,url=source['url'],captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Raw snapshot identity only; selected passages were separately read in official web sources.')
    try:
        req=urllib.request.Request(source['url'],headers={'User-Agent':'Harness-Engineering-Public-Research/1.0'})
        with urllib.request.urlopen(req,timeout=25) as response:
            raw=response.read(12000000)
            result.update(status='captured',final_url=response.url,content_type=response.headers.get('Content-Type',''),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        file.write_bytes(raw)
    except Exception as error:result.update(status='capture_failed',error=f'{type(error).__name__}: {error}')
    receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    return result


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(capture,sources))
target=BASE/'verification/foundation_capture_receipt.json';target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(entries=len(rows),captured=sum(r['status']=='captured' for r in rows),capture_failures=[r['id'] for r in rows if r['status']!='captured']),indent=2))
