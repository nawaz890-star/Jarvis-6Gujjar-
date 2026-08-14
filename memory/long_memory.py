import sqlite3
from pathlib import Path
from core.config import Config

DB_PATH = Path(Config.DATA_DIR) / "long_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

def store(key, value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def find(key):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, key, value, created_at FROM memory WHERE key = ? ORDER BY id DESC", (key,))
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
