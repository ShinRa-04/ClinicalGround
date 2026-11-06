"""Source-preserving BM25 + local dense-vector retrieval, never an adjudicator."""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sqlite3
import struct
import time
import uuid

from .models import IsolationError


class CorpusCoverageError(ValueError):
    """Resource-limited prefixes must not masquerade as full-corpus search."""


class ReferenceVectorCache:
    """Fixed-reference chunk vectors only, never patient/query text or vectors."""
    def __init__(self,identity,path=None):
        key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        self.path=Path(path) if path else Path(__file__).resolve().parents[1]/'runs'/'reference-cache'/(key+'.sqlite')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            current=c.execute("SELECT value FROM metadata WHERE key='encoder'").fetchone()
            if current and current[0]!=key:raise ValueError('reference cache encoder mismatch')
            c.execute("INSERT OR IGNORE INTO metadata VALUES ('encoder',?)",(key,))
            if c.execute("SELECT value FROM metadata WHERE key='encoder'").fetchone()[0]!=key:
                raise ValueError('reference cache encoder mismatch')
            c.execute('CREATE TABLE IF NOT EXISTS vectors (key TEXT PRIMARY KEY,vector BLOB NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS leases (key TEXT PRIMARY KEY,owner TEXT,expires REAL)')

    @contextmanager
    def _connect(self):
        connection=sqlite3.connect(self.path,timeout=30)
        try:
            with connection:yield connection
        finally:connection.close()

    def get(self,keys):
        values={}
        with self._connect() as c:
            for start in range(0,len(keys),400):
                part=keys[start:start+400]
                for key,blob in c.execute('SELECT key,vector FROM vectors WHERE key IN ('+','.join('?' for _ in part)+')',part):
                    if blob and len(blob)%4==0:values[key]=list(struct.unpack('<'+'f'*(len(blob)//4),blob))
        return values

    def put(self,values):
        with self._connect() as c:
            c.executemany('INSERT OR REPLACE INTO vectors VALUES (?,?)',[
                (key,struct.pack('<'+'f'*len(v),*v)) for key,v in values.items()])

    def claim(self,keys,owner,seconds=180):
        claimed=[]
        with self._connect() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('DELETE FROM leases WHERE expires<?',(time.time(),))
            for key in keys:
                if c.execute('SELECT 1 FROM vectors WHERE key=?',(key,)).fetchone():continue
                c.execute('INSERT OR IGNORE INTO leases VALUES (?,?,?)',(key,owner,time.time()+seconds))
                row=c.execute('SELECT owner FROM leases WHERE key=?',(key,)).fetchone()
                if row and row[0]==owner:claimed.append(key)
        return claimed

    def release(self,owner):
        with self._connect() as c:c.execute('DELETE FROM leases WHERE owner=?',(owner,))


def runtime_config():
    path=Path(__file__).resolve().parents[1]/'retrieval.local.json'
    if not path.exists():return {'configured':False}
    d=json.loads(path.read_text(encoding='utf-8-sig'))
    if d.get('schema_version')!=1 or not re.fullmatch(r'sha256:[a-f0-9]{64}',d.get('image','')):
        raise ValueError('invalid pinned embedding runtime configuration')
    if d.get('device')!='gpu' or d.get('model')!='BAAI/bge-small-en-v1.5':
        raise ValueError('unsupported embedding runtime identity')
    return {'configured':True,'image':d['image'],'model':d['model'],'device':'gpu'}


def relevance_settings(kind):
    """Operator-owned calibration, never a tool/model-selected clinical rule."""
    path=Path(__file__).resolve().parent/'data'/'relevance_floors.json'
    raw=path.read_bytes();policy=json.loads(raw)
    if policy.get('schema_version')!=1 or kind not in policy.get('floors',{}):
        raise ValueError('relevance floor is not calibrated for this corpus')
    expected=policy['encoder'];actual=runtime_config()
    if actual.get('configured') and (actual.get('model')!=expected.get('model') or actual.get('image')!=expected.get('runtime_image')):
        raise ValueError('relevance floor requires recalibration for this embedding runtime')
    value=policy['floors'][kind]['minimum_cosine']
    if type(value) not in (float,int) or not math.isfinite(value) or not -1<=value<=1:
        raise ValueError('invalid calibrated relevance floor')
    return {'minimum_cosine':value,'corpus_kind':kind,'calibration_sha256':hashlib.sha256(raw).hexdigest(),
            'basis':policy['floors'][kind]['basis']}


class DockerEmbedder:
    def __init__(self,config=None,docker='docker',timeout=120):
        self.config=config or runtime_config();self.docker=docker;self.timeout=timeout
        self.identity={'model':self.config.get('model'),'runtime_image':self.config.get('image'),'device':'gpu'}
        self.stats={'inference_requests':0,'embedded_texts':0,'query_requests':0,'elapsed_seconds':0.0}

    def embed(self,texts,*,query=False):
        if not self.config.get('configured'):raise RuntimeError('embedding runtime not configured; run Runner/toolkit.ps1 build-retrieval')
        output=[]
        for offset in range(0,len(texts),512):
            name='bigdata-health-embed-'+uuid.uuid4().hex[:16]
            command=[self.docker,'run','--rm','--name',name,'--init','-i','--gpus','all','--network','none',
                '--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=64m','--cap-drop','ALL',
                '--security-opt','no-new-privileges','--cpus','2','--memory','3g',self.config['image']]
            try:
                started=time.monotonic();self.stats['inference_requests']+=1
                self.stats['embedded_texts']+=len(texts[offset:offset+512])
                self.stats['query_requests']+=int(query)
                result=subprocess.run(command,input=json.dumps({'texts':texts[offset:offset+512],'query':query}),
                    text=True,encoding='utf-8',capture_output=True,timeout=self.timeout,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if result.returncode:raise RuntimeError('local GPU embedding failed; no lexical-only result was mislabeled hybrid')
                value=json.loads(result.stdout)
                vectors=value['vectors'];encoder=value['encoder']
                if encoder.get('device')!='gpu' or 'CUDAExecutionProvider' not in encoder.get('providers',[]):
                    raise RuntimeError('embedding runtime did not confirm CUDA execution')
                if len(vectors)!=len(texts[offset:offset+512]):raise RuntimeError('embedding response count mismatch')
                output.extend(vectors);self.identity={**encoder,'runtime_image':self.config['image']}
            except (ValueError,KeyError):raise RuntimeError('embedding response invalid') from None
            except (OSError,subprocess.TimeoutExpired):raise RuntimeError('local GPU embedding runtime unavailable') from None
            finally:
                self.stats['elapsed_seconds']+=time.monotonic()-started
                # Exact ephemeral container only. No host files or credentials
                # are mounted; no other service/container is touched.
                try:
                    cleanup=subprocess.run([self.docker,'rm','--force',name],capture_output=True,timeout=30,
                                           creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                    self.stats['cleanup_confirmed']=(cleanup.returncode==0 or 'no such container' in str(cleanup.stderr).lower())
                except (OSError,subprocess.TimeoutExpired):self.stats['cleanup_confirmed']=False
        return output


def _tokens(text):return re.findall(r'[^\W_]+(?:[-.][^\W_]+)*',text.casefold())


def _sections(text):
    headings=list(re.finditer(r'(?m)^#{1,6}\s+(.+)$',text))
    return [{'heading':m.group(1),'start':m.start(),'end':headings[i+1].start() if i+1<len(headings) else len(text)}
            for i,m in enumerate(headings)]


def _chunks(doc):
    text=doc['text'];sections=_sections(text);start=0
    while start<len(text):
        end=min(len(text),start+1100)
        if end<len(text):
            cut=text.rfind('\n',start+400,end)
            if cut>start:end=cut+1
        heading=next((s['heading'] for s in reversed(sections) if s['start']<=start),'')
        yield {'doc':doc,'start':start,'end':end,'text':text[start:end],'heading':heading,
               'embedding_text':doc.get('title','')[:180]+'\n'+heading[:180]+'\n'+text[start:end]}
        if end==len(text):break
        start=max(start+1,end-160)


def _unit(vector):
    if not isinstance(vector,(list,tuple)) or not vector or any(not isinstance(x,(float,int)) or not math.isfinite(x) for x in vector):
        raise ValueError('invalid embedding vector')
    norm=math.sqrt(sum(x*x for x in vector))
    if norm==0:raise ValueError('zero embedding vector')
    return [x/norm for x in vector]


class HybridIndex:
    """In-memory cache owned by ONE case namespace, discarded at scope reset."""
    def __init__(self,namespace,embedder,reference_cache=False,cache_path=None,relevance_floor=None,progress=None,
                 query_cache=False,query_cache_path=None):
        self.namespace=namespace;self.embedder=embedder;self.cache={}
        self.reference_cache_enabled=reference_cache;self.reference_cache_path=cache_path;self._reference_cache=None
        self._encoder_cache_identity=dict(getattr(embedder,'identity',{}))
        if relevance_floor is not None and (type(relevance_floor) not in (int,float) or not math.isfinite(relevance_floor) or not -1<=relevance_floor<=1):
            raise ValueError('invalid relevance floor')
        self.relevance_floor=relevance_floor
        self.progress=progress
        self._query_cache=None
        if query_cache:
            from .retrieval_cache import CaseQueryCache
            self._query_cache=CaseQueryCache(namespace,self._encoder_cache_identity,query_cache_path)

    def _progress(self,stage,**fields):
        if self.progress is not None:self.progress("retrieval_progress",stage=stage,**fields)

    def search(self,documents,query,*,namespace,limit=5,max_chars=16000):
        if namespace!=self.namespace:raise IsolationError('hybrid index belongs to another case namespace')
        if not isinstance(query,str) or not query.strip() or len(query)>1000:raise ValueError('bounded nonempty query required')
        if not 1<=limit<=8 or not 4000<=max_chars<=24000:raise ValueError('invalid hybrid result budget')
        if len(documents)>10000 or sum(len(d.get('text','')) for d in documents)>50000000:
            raise CorpusCoverageError('complete hybrid corpus exceeds resource budget')
        # Hash current text AND source metadata: identical wording in another
        # source must never return the old evidence ID, path or patient scope.
        bucket=hashlib.sha256(json.dumps([documents,self.relevance_floor,limit,max_chars,'hybrid-v2'],
            ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if self._query_cache:
            cached=self._query_cache.exact(namespace,bucket,query)
            if cached is not None:
                cached['query_cache']={'status':'exact_hit','inference_executed_this_call':False}
                cached['semantic_executed']=False
                cached['semantic_result_cached']=True
                cached['reference_cache']['disk_hits']=0
                cached['embedding_metrics']=dict(getattr(self.embedder,'stats',{}))
                self._progress('query_cache_hit',count=len(cached['matches']))
                return cached
        chunks=[]
        for d in documents:
            if not isinstance(d.get('text'),str) or not isinstance(d.get('id'),str):raise ValueError('source document invalid')
            for chunk in _chunks(d):
                if len(chunks)>=60000:raise CorpusCoverageError('complete hybrid chunk budget exceeded')
                chunks.append(chunk)
        result={'mode':'hybrid_bm25_dense_rrf','matches':[],'documents':[],
                'corpus_partial':False,'coverage_complete':True,'output_partial':False,'source_documents':len(documents),
                'indexed_chunks':len(chunks),'creates_evidence':False,
                'instruction':'Ranked candidate passages, not identity, eligibility or current-state conclusions. '
                 'Read applicable versions and linked conditions/exclusions; bounded context may omit qualifications.'}
        if not chunks:
            result.update(encoder=getattr(self.embedder,'identity',{}),semantic_executed=False)
            return result
        keys=[hashlib.sha256(c['embedding_text'].encode()).hexdigest() for c in chunks]
        # Evict removed/changed documents. No patient-derived vector cache is
        # persisted to disk or reused by another namespace.
        current_keys=set(keys);self.cache={k:v for k,v in self.cache.items() if k in current_keys}
        self._progress("checking_vector_cache",total=len(current_keys),file_count=len(documents))
        eligible_keys={k for k,c in zip(keys,chunks) if self.reference_cache_enabled and
            c['doc'].get('source',{}).get('trusted_fixed_reference') is True and
            c['doc']['source'].get('path','').startswith('/workspace/skills/managed-care-operations-handbook/references/')}
        eligible=bool(eligible_keys)
        cache_hits=0
        if eligible:
            if self._reference_cache is None:self._reference_cache=ReferenceVectorCache(self._encoder_cache_identity,self.reference_cache_path)
            saved=self._reference_cache.get(list(eligible_keys-self.cache.keys()));cache_hits=len(saved)
            self.cache.update({k:_unit(v) for k,v in saved.items()})
        missing=list(dict.fromkeys(k for k in keys if k not in self.cache))
        texts={k:c['embedding_text'] for k,c in zip(keys,chunks)}
        self._progress('cache_ready',cache_hits=len(current_keys)-len(missing),cache_misses=len(missing),total=len(current_keys))
        self._progress("indexing" if missing else "indexed",current=len(current_keys)-len(missing),total=len(current_keys))
        if missing:
            owner=uuid.uuid4().hex;deadline=time.monotonic()+360;pending=missing[:];last_wait_log=0
            try:
                while pending:
                    proposed=pending[:512];fixed=[k for k in proposed if k in eligible_keys]
                    if fixed:
                        saved=self._reference_cache.get(fixed);cache_hits+=len(saved)
                        self.cache.update({k:_unit(v) for k,v in saved.items()})
                        owned=self._reference_cache.claim([k for k in fixed if k not in self.cache],owner)
                    else:owned=[]
                    batch=[k for k in proposed if k not in eligible_keys and k not in self.cache]+owned
                    if batch:
                        vectors=self.embedder.embed([texts[k] for k in batch])
                        if len(vectors)!=len(batch):raise ValueError('embedding document count mismatch')
                        normalized={k:_unit(v) for k,v in zip(batch,vectors)};self.cache.update(normalized)
                        if eligible:self._reference_cache.put({k:v for k,v in normalized.items() if k in eligible_keys})
                        if eligible:self._reference_cache.release(owner)
                    pending=[k for k in pending if k not in self.cache]
                    if not batch and pending:
                        if time.monotonic()>deadline:raise RuntimeError('reference indexing wait budget exhausted')
                        if time.monotonic()-last_wait_log>=2:
                            self._progress('waiting_for_reference_index',current=len(current_keys)-len(pending),total=len(current_keys))
                            last_wait_log=time.monotonic()
                        time.sleep(.2)
                    else:self._progress('indexing',current=len(current_keys)-len(pending),total=len(current_keys))
            finally:
                if eligible:self._reference_cache.release(owner)
        self._progress("indexed_retrieving",total=len(chunks))
        q=_unit(self.embedder.embed([query],query=True)[0]);vectors=[self.cache[k] for k in keys]
        neighbor=self._query_cache.nearest(namespace,bucket,q) if self._query_cache else None
        if any(len(v)!=len(q) for v in vectors):raise ValueError('embedding dimensions differ')
        dense=[sum(a*b for a,b in zip(q,v)) for v in vectors]
        passed=[i for i in range(len(chunks)) if self.relevance_floor is None or dense[i]>=self.relevance_floor]
        result['relevance_gate']={'enabled':self.relevance_floor is not None,'minimum_cosine':self.relevance_floor,
            'best_cosine':max(dense),'passed_chunks':len(passed),'rejected_chunks':len(chunks)-len(passed),
            'status':'candidates_above_floor' if passed else 'no_candidate_above_floor',
            'instruction':'This is a basic relevance screen, not a probability, clinical applicability decision or proof that no policy exists.'}
        counts=[Counter(_tokens(c['text'])) for c in chunks];terms=set(_tokens(query));n=len(chunks)
        avg=sum(sum(c.values()) for c in counts)/n or 1
        df={t:sum(t in c for c in counts) for t in terms}
        lexical=[]
        for count in counts:
            length=sum(count.values());score=0
            for t in terms:
                f=count[t]
                if f:score+=math.log(1+(n-df[t]+.5)/(df[t]+.5))*f*2.2/(f+1.2*(.25+.75*length/avg))
            lexical.append(score)
        dense_order=sorted(passed,key=lambda i:(-dense[i],i))
        lexical_order=sorted((i for i in passed if lexical[i]>0),key=lambda i:(-lexical[i],i))
        fused={i:1/(60+rank) for rank,i in enumerate(dense_order,1)}
        for rank,i in enumerate(lexical_order,1):fused[i]+=1/(60+rank)
        order=sorted(fused,key=lambda i:(-fused[i],i));used=[];metadata={}
        for i in order:
            c=chunks[i];doc=c['doc'];text=doc['text']
            if any(d==doc['id'] and max(a,c['start'])<min(b,c['end']) for d,a,b in used):continue
            start=max(0,c['start']-350);end=min(len(text),c['end']+350)
            hit={'document_id':doc['id'],'source':doc['source'],'start':start,'end':end,
                 'text':text[start:end],'heading':c['heading'],'scores':{'bm25':lexical[i],'cosine':dense[i],'rrf':fused[i]}}
            meta={'document_id':doc['id'],'source':doc['source'],'header':{'start':0,'end':min(1200,len(text)),
                  'text':text[:1200]},'qualifying_sections':[],
                  'qualifications_complete':False,
                  'linked_references':re.findall(r'\[[^\]]+\]\(([^)]+)\)',text)[:16]}
            for section in _sections(text):
                if re.search(r'exclu|exception|limitation|definition|footnote|effective|applicab',section['heading'],re.I):
                    a=section['start'];b=min(section['end'],a+1200)
                    meta['qualifying_sections'].append({'heading':section['heading'],'start':a,'end':b,
                        'text':text[a:b],'partial':b<section['end']})
                    if len(meta['qualifying_sections'])>=4:break
            candidate={**result,'matches':[*result['matches'],hit],
                       'documents':list({**metadata,doc['id']:meta}.values()),
                       'encoder':getattr(self.embedder,'identity',{}),'semantic_executed':True}
            if not result['matches'] and len(json.dumps(candidate,ensure_ascii=False,separators=(',',':')))>max_chars-400:
                # Preserve a useful exact hit even at the smallest output
                # budget. Mark the reduced qualifier context explicitly.
                meta['header']['end']=min(350,len(text));meta['header']['text']=text[:350]
                meta['qualifying_sections']=meta['qualifying_sections'][:1]
                for s in meta['qualifying_sections']:
                    s['end']=min(s['end'],s['start']+350);s['text']=text[s['start']:s['end']];s['partial']=True
                meta['context_partial']=True
                candidate['documents']=list({**metadata,doc['id']:meta}.values())
            if len(json.dumps(candidate,ensure_ascii=False,separators=(',',':')))>max_chars-400:
                # Output is a ranked prefix. Do not scan/repack the entire
                # corpus looking for a lower-ranked result that happens to fit.
                result['output_partial']=True;break
            metadata[doc['id']]=meta;result=candidate;used.append((doc['id'],start,end))
            if len(used)>=limit:break
        result.update(encoder=getattr(self.embedder,'identity',{}),semantic_executed=True,
                      embedding_metrics=dict(getattr(self.embedder,'stats',{})),
                      reference_cache={'eligible':eligible,'eligible_chunks':len(eligible_keys),'disk_hits':cache_hits,'query_vectors_persisted':False})
        if self._query_cache:
            result['query_cache']={'status':'miss','nearest_similarity':neighbor,'similar_result_reused':False,
                'inference_executed_this_call':True}
            self._query_cache.put(namespace,bucket,query,q,result)
        self._progress("retrieval_finished",count=len(result["matches"]))
        return result
