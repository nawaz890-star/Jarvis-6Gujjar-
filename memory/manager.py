import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class LongTermMemory:
    def __init__(self, db_path: Optional[Path] = None):
        from core.config import Config
        if db_path is None:
            self.db_path = Path(Config.DATA_DIR) / "long_memory.db"
        else:
            self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

    def add(self, key: str, value: str) -> int:
        if not key or not isinstance(key, str):
            raise ValueError("key must be a non-empty string")
        if value is None:
            raise ValueError("value must not be None")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO memory (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        rowid = cur.lastrowid
        conn.close()
        logger.debug("Stored memory id=%s key=%s", rowid, key)
        return rowid

    def get(self, key: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, key, value, created_at FROM memory WHERE key = ? ORDER BY id DESC LIMIT ?", (key, limit))
        rows = cur.fetchall()
        conn.close()
        return [ {"id": r[0], "key": r[1], "value": r[2], "created_at": r[3]} for r in rows ]

    def list_keys(self, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, key, value, created_at FROM memory ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [ {"id": r[0], "key": r[1], "value": r[2], "created_at": r[3]} for r in rows ]

    def delete(self, entry_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM memory WHERE id = ?", (entry_id,))
        changed = cur.rowcount
        conn.commit()
        conn.close()
        return changed > 0

    def clear_all(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM memory")
        conn.commit()
        conn.close()

    def export_json(self, path: Path):
        data = self.list_keys(limit=10_000)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def import_json(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        count = 0
        for it in items:
            k = it.get("key")
            v = it.get("value")
            if k and v is not None:
                self.add(k, v)
                count += 1
        return count