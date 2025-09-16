"""SQLite storage adapter (simple, synchronous wrapped in async signatures)."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from ui_testing_framework_v3.ports.storage import IStorage


class SQLiteStorage(IStorage):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._path = (config or {}).get("path", ":memory:")
        self._ensure()

    def _ensure(self) -> None:
        con = sqlite3.connect(self._path)
        try:
            con.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
            con.commit()
        finally:
            con.close()

    async def save(self, key: str, data: Any) -> bool:
        con = sqlite3.connect(self._path)
        try:
            con.execute("INSERT OR REPLACE INTO kv(k, v) VALUES (?, ?)", (key, json.dumps(data)))
            con.commit()
            return True
        finally:
            con.close()

    async def load(self, key: str) -> Any | None:
        con = sqlite3.connect(self._path)
        try:
            cur = con.execute("SELECT v FROM kv WHERE k = ?", (key,))
            row = cur.fetchone()
            return json.loads(row[0]) if row else None
        finally:
            con.close()

    async def delete(self, key: str) -> bool:
        con = sqlite3.connect(self._path)
        try:
            cur = con.execute("DELETE FROM kv WHERE k = ?", (key,))
            con.commit()
            return cur.rowcount > 0
        finally:
            con.close()

    async def exists(self, key: str) -> bool:
        con = sqlite3.connect(self._path)
        try:
            cur = con.execute("SELECT 1 FROM kv WHERE k = ?", (key,))
            return cur.fetchone() is not None
        finally:
            con.close()


def register(registry: Any) -> None:
    registry.register("storage", SQLiteStorage, name="sqlite")
