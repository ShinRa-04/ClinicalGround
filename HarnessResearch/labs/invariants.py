"""Synthetic teaching primitives: no models, network, upstream imports or production guarantees."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import sqlite3


class BudgetError(ValueError):pass
class StaleOwner(ValueError):pass


@dataclass(frozen=True)
class Message:
    kind:str
    text:str
    call_id:str|None=None


@dataclass(frozen=True)
class Unit:
    id:str
    messages:tuple[Message,...]
    estimated_tokens:int
    protected:bool=False


def project(units:tuple[Unit,...],window:int,output_reserve:int)->tuple[Unit,...]:
    """Keep protected atomic units, then recent units that fit a synthetic budget.

    Counts are supplied estimates, not actual tokenizer/provider accounting.
    This does not summarize text or prove preservation of semantic meaning.
    """
    if window<0 or output_reserve<0 or output_reserve>window:raise BudgetError('invalid budget')
    if len({u.id for u in units})!=len(units):raise ValueError('duplicate unit')
    seen=set()
    for unit in units:
        if unit.estimated_tokens<0:raise BudgetError('negative estimate')
        calls=[m.call_id for m in unit.messages if m.kind=='call']
        results=[m.call_id for m in unit.messages if m.kind=='result']
        if None in calls or None in results or len(calls)!=len(set(calls)) or sorted(calls)!=sorted(results):
            raise ValueError('call/results must be paired within one atomic unit')
        if seen.intersection(calls):raise ValueError('duplicate call identity')
        seen.update(calls)
    available=window-output_reserve
    selected={u.id for u in units if u.protected}
    used=sum(u.estimated_tokens for u in units if u.protected)
    if used>available:raise BudgetError('protected context cannot fit; explicit recovery needed')
    for unit in reversed(units):
        if unit.id not in selected and used+unit.estimated_tokens<=available:
            selected.add(unit.id);used+=unit.estimated_tokens
    return tuple(u for u in units if u.id in selected)


class Memory:
    """Tiny exact-scope, single-parent provenance store; not an authentication system."""
    def __init__(self,path=':memory:'):
        self.db=sqlite3.connect(path);self.db.row_factory=sqlite3.Row
        self.db.execute('CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, principal TEXT, scope TEXT, text TEXT, trust TEXT, parent TEXT, version INTEGER NOT NULL DEFAULT 1, deleted INTEGER NOT NULL DEFAULT 0)')
        self.db.commit()

    def add(self,id,principal,scope,text,trust='untrusted',parent=None):
        if trust not in {'user','reviewed','untrusted'}:raise ValueError('invalid trust')
        if parent:
            row=self.db.execute('SELECT * FROM memory WHERE id=?',(parent,)).fetchone()
            if not row or row['deleted'] or (row['principal'],row['scope'])!=(principal,scope):
                raise ValueError('invalid, deleted or out-of-scope origin')
            if row['trust']=='untrusted':trust='untrusted'
        with self.db:self.db.execute('INSERT INTO memory(id,principal,scope,text,trust,parent) VALUES(?,?,?,?,?,?)',(id,principal,scope,text,trust,parent))

    def injectable(self,principal,scope):
        return [dict(r) for r in self.db.execute("SELECT * FROM memory WHERE principal=? AND scope=? AND deleted=0 AND trust!='untrusted' ORDER BY id",(principal,scope))]

    def amend(self,id,expected_version,text):
        with self.db:
            changed=self.db.execute('UPDATE memory SET text=?,version=version+1 WHERE id=? AND version=? AND deleted=0',(text,id,expected_version)).rowcount
        return changed==1

    def forget(self,id):
        with self.db:self.db.execute('WITH RECURSIVE descendants(id) AS (SELECT id FROM memory WHERE id=? UNION ALL SELECT m.id FROM memory m JOIN descendants d ON m.parent=d.id) UPDATE memory SET deleted=1,version=version+1 WHERE id IN (SELECT id FROM descendants)',(id,))

    def close(self):self.db.close()


def digest(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class SimulatedReceiver:
    """In-memory receiver that honors one same-key/same-intent contract. No real I/O."""
    def __init__(self):self.saved={};self.effects=0
    def perform(self,key,payload):
        fingerprint=digest(payload)
        if key in self.saved:
            old,result=self.saved[key]
            if old!=fingerprint:raise ValueError('same key, different intent')
            return result
        self.effects+=1;result={'receipt':f'effect-{self.effects}'}
        self.saved[key]=(fingerprint,result)
        return result


class Actions:
    """Local action journal and publication fence; does not transact with the receiver."""
    def __init__(self,path=':memory:'):
        self.db=sqlite3.connect(path);self.db.row_factory=sqlite3.Row
        self.db.executescript('CREATE TABLE IF NOT EXISTS claims(session TEXT PRIMARY KEY, epoch INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, session TEXT, fingerprint TEXT, state TEXT, result TEXT);')
        self.db.commit()

    def claim(self,session):
        with self.db:self.db.execute('INSERT INTO claims(session,epoch) VALUES(?,1) ON CONFLICT(session) DO UPDATE SET epoch=epoch+1',(session,))
        return self.db.execute('SELECT epoch FROM claims WHERE session=?',(session,)).fetchone()[0]

    def require_owner(self,session,epoch):
        row=self.db.execute('SELECT epoch FROM claims WHERE session=?',(session,)).fetchone()
        if not row or row[0]!=epoch:raise StaleOwner('result/action belongs to a superseded owner')

    def prepare(self,session,id,payload,epoch):
        self.require_owner(session,epoch);fingerprint=digest(payload)
        row=self.db.execute('SELECT * FROM actions WHERE id=?',(id,)).fetchone()
        if row:
            if row['session']!=session or row['fingerprint']!=fingerprint:raise ValueError('action identity reused with different scope/intent')
            return row['state']
        with self.db:self.db.execute('INSERT INTO actions VALUES(?,?,?,?,NULL)',(id,session,fingerprint,'prepared'))
        return 'prepared'

    def unknown(self,session,id,epoch):
        self.require_owner(session,epoch)
        with self.db:self.db.execute("UPDATE actions SET state='outcome-unknown' WHERE id=? AND session=? AND state!='confirmed'",(id,session))

    def confirm(self,session,id,result,epoch):
        self.require_owner(session,epoch)
        with self.db:
            count=self.db.execute("UPDATE actions SET state='confirmed',result=? WHERE id=? AND session=?",(json.dumps(result,sort_keys=True),id,session)).rowcount
        if count!=1:raise ValueError('unknown action')

    def state(self,id):
        row=self.db.execute('SELECT state FROM actions WHERE id=?',(id,)).fetchone()
        return row[0] if row else None

    def close(self):self.db.close()
