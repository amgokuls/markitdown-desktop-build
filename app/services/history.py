"""
MarkItDown Desktop — History Service

Persists lightweight conversion history to disk.
Only metadata (filename, path, success, duration, timestamp) is stored.
Document content is NEVER stored in history.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from ..conversion.models import HistoryEntry

logger = logging.getLogger(__name__)

APP_DATA_DIR = Path.home() / ".markitdown-desktop"
HISTORY_FILE = APP_DATA_DIR / "history.json"
MAX_HISTORY_ENTRIES = 200


class HistoryService:
    """Read/write conversion history. Thread-safe for single-thread UI use."""

    def __init__(self):
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._entries: List[HistoryEntry] = self._load()

    # ------------------------------------------------------------------ #

    def add(self, entry: HistoryEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > MAX_HISTORY_ENTRIES:
            self._entries = self._entries[:MAX_HISTORY_ENTRIES]
        self._save()

    def all_entries(self) -> List[HistoryEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries = []
        self._save()

    # ------------------------------------------------------------------ #

    def _load(self) -> List[HistoryEntry]:
        if not HISTORY_FILE.exists():
            return []
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return [HistoryEntry.from_dict(d) for d in data]
        except Exception as exc:
            logger.warning("Could not load history: %s", exc)
            return []

    def _save(self) -> None:
        try:
            HISTORY_FILE.write_text(
                json.dumps([e.to_dict() for e in self._entries], indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("Could not save history: %s", exc)
