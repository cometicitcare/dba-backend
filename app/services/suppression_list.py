import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path
import json
import threading
from app.core.config import settings

logger = logging.getLogger(__name__)


class SuppressionList:
    """Persistent TTL suppression list for undeliverable email addresses.

    Stores data in app/storage/suppression.json on Railway (survives redeploys).
    Falls back to /tmp if app/storage is not writable.
    """

    def __init__(self, ttl_minutes: int = None) -> None:
        self._ttl = timedelta(minutes=ttl_minutes or settings.SUPPRESSION_TTL_MINUTES)
        self._store: Dict[str, dict] = {}
        self._lock = threading.Lock()
        
        # Railway persistent volume or fallback
        candidates = [Path("app/storage/suppression.json"), Path("/tmp/suppression.json")]
        self._file: Path = None
        for p in candidates:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch(exist_ok=True)
                self._file = p
                break
            except Exception:
                pass
        
        if not self._file:
            logger.warning("No writable suppression file; using in-memory only")
        
        self._load()

    def _load(self) -> None:
        if not self._file or not self._file.exists():
            return
        try:
            data = json.loads(self._file.read_text())
            # Deserialize ISO datetimes
            for k, v in data.items():
                v["expires_at"] = datetime.fromisoformat(v["expires_at"])
                v["created_at"] = datetime.fromisoformat(v["created_at"])
            self._store = data
            logger.info(f"Loaded {len(self._store)} suppressed emails from {self._file}")
        except Exception as e:
            logger.warning(f"Failed to load suppression list: {e}")

    def _save(self) -> None:
        if not self._file:
            return
        try:
            # Serialize datetimes to ISO
            data = {}
            for k, v in self._store.items():
                data[k] = {
                    "reason": v["reason"],
                    "expires_at": v["expires_at"].isoformat(),
                    "created_at": v["created_at"].isoformat(),
                }
            self._file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save suppression list: {e}")

    def mark(self, email: str, reason: str) -> None:
        key = (email or "").strip().lower()
        if not key:
            return
        with self._lock:
            self._store[key] = {
                "reason": reason,
                "expires_at": datetime.utcnow() + self._ttl,
                "created_at": datetime.utcnow(),
            }
            self._save()
        logger.warning(f"Suppressed email {key} for {self._ttl} due to: {reason}")

    def is_suppressed(self, email: str) -> bool:
        key = (email or "").strip().lower()
        with self._lock:
            data = self._store.get(key)
            if not data:
                return False
            if datetime.utcnow() > data.get("expires_at", datetime.utcnow()):
                # expired
                self._store.pop(key, None)
                self._save()
                return False
            return True

    def get(self, email: str) -> Optional[dict]:
        key = (email or "").strip().lower()
        with self._lock:
            data = self._store.get(key)
            if data and datetime.utcnow() <= data.get("expires_at", datetime.utcnow()):
                return data
            return None

    def prune(self) -> int:
        now = datetime.utcnow()
        with self._lock:
            to_delete = [k for k, v in self._store.items() if now > v.get("expires_at", now)]
            for k in to_delete:
                self._store.pop(k, None)
            if to_delete:
                self._save()
        return len(to_delete)


suppression_list = SuppressionList()
