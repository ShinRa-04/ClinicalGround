"""Case-private query results. Similarity is diagnostic, never answer equivalence."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import uuid

from .models import IsolationError


class CaseQueryCache:
    def __init__(self,namespace,encoder,path=None):
        self.namespace=namespace
        self.path=Path(path) if path else Path(__file__).resolve().parents[1]/'runs'/'case-query-cache'/(uuid.uuid4().hex+'.sqlite')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        binding=hashlib.sha256(json.dumps([namespace,encoder],sort_keys=True).encode()).hexdigest()
        with self.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS binding (slot INTEGER PRIMARY KEY CHECK(slot=1),key TEXT NOT NULL)')
            c.execute('INSERT OR IGNORE INTO binding VALUES (1,?)',(binding,))
            if c.execute('SELECT key FROM binding WHERE slot=1').fetchone()[0]!=binding:
                raise IsolationError('query cache belongs to another case or encoder')
            c.execute('CREATE TABLE IF NOT EXISTS entries (bucket TEXT,query_hash TEXT,vector BLOB,result TEXT,PRIMARY KEY(bucket,query_hash))')

    @contextmanager
    def connect(self):
        c=sqlite3.connect(self.path,timeout=30)
        try:
            with c:yield c
        finally:c.close()

    def _check(self,namespace):
        if namespace!=self.namespace:raise IsolationError('query cache belongs to another case')

    def exact(self,namespace,bucket,query):
        self._check(namespace)
        with self.connect() as c:
            row=c.execute('SELECT result FROM entries WHERE bucket=? AND query_hash=?',
                (bucket,hashlib.sha256(query.encode()).hexdigest())).fetchone()
        return json.loads(row[0]) if row else None

    def nearest(self,namespace,bucket,vector):
        self._check(namespace);scores=[]
        with self.connect() as c:
            for (blob,) in c.execute('SELECT vector FROM entries WHERE bucket=?',(bucket,)):
                v=struct.unpack('<'+'f'*(len(blob)//4),blob)
                if len(v)==len(vector):scores.append(sum(a*b for a,b in zip(vector,v)))
        return max(-1.,min(1.,max(scores))) if scores else None

    def put(self,namespace,bucket,query,vector,result):
        self._check(namespace)
        with self.connect() as c:
            # Corpus/config hashes make older answers unreachable for a changed
            # source set. Keep up to 128 entries so alternating permitted source
            # collections does not constantly evict each other's exact queries.
            c.execute('INSERT OR REPLACE INTO entries VALUES (?,?,?,?)',
                (bucket,hashlib.sha256(query.encode()).hexdigest(),
                 struct.pack('<'+'f'*len(vector),*vector),json.dumps(result,ensure_ascii=False)))
            c.execute('DELETE FROM entries WHERE rowid NOT IN (SELECT rowid FROM entries ORDER BY rowid DESC LIMIT 128)')
