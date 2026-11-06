"""SQLite-backed, scope-isolated case state and durable action journal."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .models import ConflictError, IsolationError, Scope, UnknownOutcomeError

_DEFAULT_BUDGETS = {
    "max_model_calls": 30,
    "max_tool_calls": 100,
    "max_context_chars": 0,
    "max_output_tokens": 4000,
}


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _load(value: str) -> Any:
    return json.loads(value)


class CaseStore:
    """Persist a separate versioned working set and action journal per Scope."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path, timeout=30, isolation_level=None, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        with self._lock:
            self._db.execute("PRAGMA foreign_keys=ON")
            self._db.execute("PRAGMA busy_timeout=30000")
            if self.path != ":memory:":
                self._db.execute("PRAGMA journal_mode=WAL")
                self._db.execute("PRAGMA synchronous=FULL")
            self._db.executescript("""
                CREATE TABLE IF NOT EXISTS cases (
                    scope_key TEXT PRIMARY KEY,
                    scope_json TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    version INTEGER NOT NULL CHECK(version >= 0),
                    lease_owner TEXT,
                    lease_expires REAL,
                    fence INTEGER NOT NULL DEFAULT 0 CHECK(fence >= 0)
                );
                CREATE TABLE IF NOT EXISTS actions (
                    scope_key TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    arguments_json TEXT NOT NULL,
                    effect TEXT NOT NULL CHECK(effect IN ('read','write')),
                    status TEXT NOT NULL CHECK(status IN ('pending','completed','unknown')),
                    result_json TEXT,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY(scope_key, action_id),
                    FOREIGN KEY(scope_key) REFERENCES cases(scope_key) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS actions_scope_status ON actions(scope_key, status);
            """)

    def open_case(self, scope: Scope, instruction: str, domain: str) -> dict[str, Any]:
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError("instruction must be a non-empty string")
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain must be a non-empty string")
        key = scope.key
        with self._transaction() as db:
            row = db.execute("SELECT * FROM cases WHERE scope_key=?", (key,)).fetchone()
            if row:
                if row["scope_json"] != _dump(scope.to_dict()):
                    raise IsolationError("scope digest collision or mismatched scope record")
                if row["instruction"] != instruction or row["domain"] != domain:
                    raise ConflictError("scope already opened with a different instruction or domain")
                return self._case_from_row(row)
            state = {
                "scope": scope.to_dict(),
                "instruction": instruction,
                "domain": domain,
                "version": 0,
                "messages": [],
                "obligations": [],
                "evidence": [],
                "model_calls": 0,
                "tool_calls": 0,
                "usage": {},
                "status": "ready",
                "budgets": dict(_DEFAULT_BUDGETS),
            }
            db.execute(
                "INSERT INTO cases(scope_key,scope_json,instruction,domain,state_json,version) VALUES(?,?,?,?,?,0)",
                (key, _dump(scope.to_dict()), instruction, domain, _dump(state)),
            )
            return state

    def load_case(self, scope: Scope) -> dict[str, Any]:
        with self._lock:
            row = self._db.execute("SELECT * FROM cases WHERE scope_key=?", (scope.key,)).fetchone()
        if row is None:
            raise KeyError("case has not been opened")
        self._check_scope(row, scope)
        return self._case_from_row(row)

    def save_case(self, scope: Scope, state: dict[str, Any], expected_version: int, *, owner: str | None = None, fence: int | None = None) -> int:
        if not isinstance(state, dict):
            raise TypeError("case state must be a dict")
        with self._transaction() as db:
            row = db.execute("SELECT * FROM cases WHERE scope_key=?", (scope.key,)).fetchone()
            if row is None:
                raise KeyError("case has not been opened")
            self._check_scope(row, scope)
            self._enforce_mutation_claim(row, owner, fence)
            if row["version"] != expected_version:
                raise ConflictError(f"stale case version: expected {expected_version}, current {row['version']}")
            if state.get("scope") != scope.to_dict() or state.get("instruction") != row["instruction"] or state.get("domain") != row["domain"]:
                raise IsolationError("scope, instruction, and domain are immutable case attributes")
            proposed = dict(state)
            proposed["version"] = expected_version + 1
            encoded = _dump(proposed)
            cur = db.execute(
                "UPDATE cases SET state_json=?,version=? WHERE scope_key=? AND version=?",
                (encoded, expected_version + 1, scope.key, expected_version),
            )
            if cur.rowcount != 1:
                raise ConflictError("case changed during save")
            return expected_version + 1

    def claim(self, scope: Scope, owner: str, ttl_seconds: float = 60) -> int:
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("owner must be a non-empty string")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        now = time.time()
        with self._transaction() as db:
            row = db.execute("SELECT * FROM cases WHERE scope_key=?", (scope.key,)).fetchone()
            if row is None:
                raise KeyError("case has not been opened")
            self._check_scope(row, scope)
            active = row["lease_owner"] is not None and (row["lease_expires"] or 0) > now
            if active and row["lease_owner"] != owner:
                raise ConflictError("case is leased by another owner")
            fence = row["fence"] if active else row["fence"] + 1
            db.execute("UPDATE cases SET lease_owner=?,lease_expires=?,fence=? WHERE scope_key=?",
                       (owner, now + float(ttl_seconds), fence, scope.key))
            return fence

    def release(self, scope: Scope, owner: str, fence: int) -> None:
        with self._transaction() as db:
            row = db.execute("SELECT * FROM cases WHERE scope_key=?", (scope.key,)).fetchone()
            if row is None:
                raise KeyError("case has not been opened")
            self._check_scope(row, scope)
            self._check_lease_row(row, owner, fence, require_live=False)
            db.execute("UPDATE cases SET lease_owner=NULL,lease_expires=NULL WHERE scope_key=?", (scope.key,))

    def renew(self, scope: Scope, owner: str, fence: int, ttl_seconds: float = 120) -> None:
        """Extend only this live fencing token; never reacquire expired ownership."""
        if type(ttl_seconds) not in (int,float) or not 0<ttl_seconds<86400:
            raise ValueError('invalid lease renewal duration')
        with self._transaction() as db:
            row=self._require_case(db,scope)
            self._check_scope(row,scope)
            self._check_lease_row(row,owner,fence,require_live=True)
            db.execute('UPDATE cases SET lease_expires=? WHERE scope_key=?',
                       (time.time()+ttl_seconds,scope.key))

    @contextmanager
    def maintained_claim(self,scope: Scope,owner: str,fence: int,*,ttl_seconds=120,interval_seconds=20):
        """Keep ownership during a bounded model wait, without changing the fence."""
        if not 0<interval_seconds<ttl_seconds:raise ValueError('lease interval must be shorter than duration')
        self.assert_claim(scope,owner,fence)
        stop=threading.Event();errors=[]
        def heartbeat():
            while not stop.wait(interval_seconds):
                try:self.renew(scope,owner,fence,ttl_seconds)
                except Exception as exc:
                    errors.append(exc);return
        worker=threading.Thread(target=heartbeat,daemon=True);worker.start()
        body_failed=False
        try:yield
        except BaseException:
            body_failed=True;raise
        finally:
            stop.set();worker.join()
            if not body_failed:
                if errors:raise ConflictError('case ownership renewal failed') from errors[0]
                self.assert_claim(scope,owner,fence)

    def assert_claim(self, scope: Scope, owner: str, fence: int) -> None:
        with self._lock:
            row = self._db.execute("SELECT * FROM cases WHERE scope_key=?", (scope.key,)).fetchone()
        if row is None:
            raise KeyError("case has not been opened")
        self._check_scope(row, scope)
        self._check_lease_row(row, owner, fence, require_live=True)

    def reserve_action(self, scope: Scope, action_id: str, tool: str, arguments: Any, effect: str, *, owner: str | None = None, fence: int | None = None) -> dict[str, Any]:
        if not action_id or not tool:
            raise ValueError("action_id and tool must be non-empty")
        if effect not in ("read", "write"):
            raise ValueError("effect must be 'read' or 'write'")
        args_json = _dump(arguments)
        now = time.time()
        with self._transaction() as db:
            case = self._require_case(db, scope)
            self._enforce_mutation_claim(case, owner, fence)
            row = db.execute("SELECT * FROM actions WHERE scope_key=? AND action_id=?", (scope.key, action_id)).fetchone()
            if row:
                if row["tool"] != tool or row["arguments_json"] != args_json or row["effect"] != effect:
                    raise ConflictError("action ID was already reserved with a different payload")
                record = self._action_from_row(row)
                if record["status"] == "unknown" and effect == "write":
                    raise UnknownOutcomeError(f"write action {action_id!r} has an unknown outcome and needs reconciliation")
                return record
            db.execute("INSERT INTO actions VALUES(?,?,?,?,?,'pending',NULL,?)",
                       (scope.key, action_id, tool, args_json, effect, now))
            return {"id": action_id, "tool": tool, "arguments": _load(args_json), "effect": effect,
                    "status": "pending", "result": None, "updated_at": now}

    def finish_action(self, scope: Scope, action_id: str, result: Any, *, owner: str | None = None, fence: int | None = None) -> dict[str, Any]:
        result_json = _dump(result)
        with self._transaction() as db:
            row = db.execute("SELECT * FROM actions WHERE scope_key=? AND action_id=?", (scope.key, action_id)).fetchone()
            if row is None:
                raise KeyError("action has not been reserved")
            self._check_action_scope(db, row, scope)
            self._enforce_mutation_claim(self._require_case(db, scope), owner, fence)
            if row["status"] == "unknown":
                raise UnknownOutcomeError("an unknown action outcome must be reconciled before recording completion")
            if row["status"] == "completed":
                if row["result_json"] != result_json:
                    raise ConflictError("completed action result is immutable")
                return self._action_from_row(row)
            db.execute("UPDATE actions SET status='completed',result_json=?,updated_at=? WHERE scope_key=? AND action_id=?",
                       (result_json, time.time(), scope.key, action_id))
            return self._action_from_row(db.execute("SELECT * FROM actions WHERE scope_key=? AND action_id=?",
                                                    (scope.key, action_id)).fetchone())

    def unknown_action(self, scope: Scope, action_id: str, reason: str, *, owner: str | None = None, fence: int | None = None) -> dict[str, Any]:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        with self._transaction() as db:
            row = db.execute("SELECT * FROM actions WHERE scope_key=? AND action_id=?", (scope.key, action_id)).fetchone()
            if row is None:
                raise KeyError("action has not been reserved")
            self._check_action_scope(db, row, scope)
            self._enforce_mutation_claim(self._require_case(db, scope), owner, fence)
            if row["status"] == "completed":
                raise ConflictError("completed action cannot become unknown")
            result = {"unknown_reason": reason}
            db.execute("UPDATE actions SET status='unknown',result_json=?,updated_at=? WHERE scope_key=? AND action_id=?",
                       (_dump(result), time.time(), scope.key, action_id))
            return self._action_from_row(db.execute("SELECT * FROM actions WHERE scope_key=? AND action_id=?",
                                                    (scope.key, action_id)).fetchone())

    def actions(self, scope: Scope) -> list[dict[str, Any]]:
        with self._lock:
            self._require_case(self._db, scope)
            rows = self._db.execute("SELECT * FROM actions WHERE scope_key=? ORDER BY updated_at,action_id", (scope.key,)).fetchall()
        return [self._action_from_row(row) for row in rows]

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def _transaction(self):
        store = self

        class Transaction:
            def __enter__(self):
                store._lock.acquire()
                try:
                    store._db.execute("BEGIN IMMEDIATE")
                except BaseException:
                    store._lock.release()
                    raise
                return store._db

            def __exit__(self, exc_type, exc, tb):
                try:
                    store._db.execute("ROLLBACK" if exc_type else "COMMIT")
                finally:
                    store._lock.release()
                return False
        return Transaction()

    @staticmethod
    def _case_from_row(row: sqlite3.Row) -> dict[str, Any]:
        state = _load(row["state_json"])
        state["version"] = row["version"]
        return state

    @staticmethod
    def _check_scope(row: sqlite3.Row, scope: Scope) -> None:
        if row["scope_key"] != scope.key or row["scope_json"] != _dump(scope.to_dict()):
            raise IsolationError("case scope does not match stored namespace")

    @staticmethod
    def _check_lease_row(row: sqlite3.Row, owner: str, fence: int, require_live: bool) -> None:
        if row["lease_owner"] != owner or row["fence"] != fence:
            raise ConflictError("lease owner or fencing token is stale")
        if require_live and (row["lease_expires"] or 0) <= time.time():
            raise ConflictError("lease has expired")

    @staticmethod
    def _enforce_mutation_claim(row: sqlite3.Row, owner: str | None, fence: int | None) -> None:
        # Unleased calls are useful for offline setup/tests. Once a worker owns
        # the case, every durable mutation must present its live fencing token.
        if row["lease_owner"] is not None:
            if owner is None or fence is None:
                raise ConflictError("a live case lease requires its owner and fencing token")
            CaseStore._check_lease_row(row, owner, fence, require_live=True)
        elif owner is not None or fence is not None:
            raise ConflictError("lease is no longer active")

    def _require_case(self, db: sqlite3.Connection, scope: Scope) -> sqlite3.Row:
        row = db.execute("SELECT * FROM cases WHERE scope_key=?", (scope.key,)).fetchone()
        if row is None:
            raise KeyError("case has not been opened")
        self._check_scope(row, scope)
        return row

    def _check_action_scope(self, db: sqlite3.Connection, action: sqlite3.Row, scope: Scope) -> None:
        case = self._require_case(db, scope)
        if action["scope_key"] != case["scope_key"]:
            raise IsolationError("action belongs to another case")

    @staticmethod
    def _action_from_row(row: sqlite3.Row) -> dict[str, Any]:
        return {"id": row["action_id"], "tool": row["tool"], "arguments": _load(row["arguments_json"]),
                "effect": row["effect"], "status": row["status"],
                "result": _load(row["result_json"]) if row["result_json"] is not None else None,
                "updated_at": row["updated_at"]}
