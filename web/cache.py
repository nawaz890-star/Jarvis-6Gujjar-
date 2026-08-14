"""
Simple file-backed TTL cache used by web modules to provide offline fallback.

Cache entries are stored as JSON files named by sanitized keys under data/cache/.
This is intentionally simple and safe (no external dependencies).
"""
from pathlib import Path
import json
import time
import hashlib
from typing import Any, Optional
from core.config import Config

CACHE_DIR = Path(Config.DATA_DIR) / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key_to_path(key: str) -> Path:
    h = hashlib.sha256(key.encode('utf-8')).hexdigest()
    return CACHE_DIR / f"{h}.json"


def set_cache(key: str, value: Any, ttl: int = 300) -> None:
    path = _key_to_path(key)
    payload = {
        "ts": int(time.time()),
        "ttl": int(ttl),
        "value": value
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def get_cache(key: str) -> Optional[Any]:
    path = _key_to_path(key)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        ts = int(payload.get("ts", 0))
        ttl = int(payload.get("ttl", 0))
        if int(time.time()) - ts > ttl:
            # expired
            path.unlink(missing_ok=True)
            return None
        return payload.get("value")
    except Exception:
        # any error -> treat as cache miss
        return None
