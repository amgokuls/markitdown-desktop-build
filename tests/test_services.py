"""
Tests for the History and Filesystem services.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from app.conversion.models import HistoryEntry


class TestHistoryService:

    def test_add_and_retrieve(self, tmp_path, monkeypatch):
        """History service persists entries."""
        import app.services.history as hs_module
        monkeypatch.setattr(hs_module, "APP_DATA_DIR", tmp_path)
        monkeypatch.setattr(hs_module, "HISTORY_FILE", tmp_path / "history.json")

        from app.services.history import HistoryService
        svc = HistoryService()

        entry = HistoryEntry(
            filename="report.pdf",
            path="/Users/test/report.pdf",
            success=True,
            duration_seconds=1.23,
        )
        svc.add(entry)

        entries = svc.all_entries()
        assert len(entries) == 1
        assert entries[0].filename == "report.pdf"
        assert entries[0].success is True

    def test_clear(self, tmp_path, monkeypatch):
        """Clear removes all history."""
        import app.services.history as hs_module
        monkeypatch.setattr(hs_module, "APP_DATA_DIR", tmp_path)
        monkeypatch.setattr(hs_module, "HISTORY_FILE", tmp_path / "history.json")

        from app.services.history import HistoryService
        svc = HistoryService()
        svc.add(HistoryEntry("f.pdf", "/f.pdf", True, 1.0))
        svc.clear()
        assert svc.all_entries() == []

    def test_persistence(self, tmp_path, monkeypatch):
        """History persists across service restarts."""
        import app.services.history as hs_module
        monkeypatch.setattr(hs_module, "APP_DATA_DIR", tmp_path)
        hist_file = tmp_path / "history.json"
        monkeypatch.setattr(hs_module, "HISTORY_FILE", hist_file)

        from app.services.history import HistoryService
        svc1 = HistoryService()
        svc1.add(HistoryEntry("doc.docx", "/doc.docx", True, 0.5))

        # Simulate restart
        svc2 = HistoryService()
        entries = svc2.all_entries()
        assert len(entries) == 1
        assert entries[0].filename == "doc.docx"

    def test_max_entries(self, tmp_path, monkeypatch):
        """History is capped at MAX_HISTORY_ENTRIES."""
        import app.services.history as hs_module
        monkeypatch.setattr(hs_module, "APP_DATA_DIR", tmp_path)
        monkeypatch.setattr(hs_module, "HISTORY_FILE", tmp_path / "history.json")
        monkeypatch.setattr(hs_module, "MAX_HISTORY_ENTRIES", 5)

        from app.services.history import HistoryService
        svc = HistoryService()
        for i in range(10):
            svc.add(HistoryEntry(f"f{i}.pdf", f"/f{i}.pdf", True, 1.0))

        assert len(svc.all_entries()) == 5


class TestHistoryEntryModel:

    def test_to_dict_and_back(self):
        entry = HistoryEntry(
            filename="test.pdf",
            path="/some/path/test.pdf",
            success=True,
            duration_seconds=2.5,
            converted_at=1234567890.0,
        )
        d = entry.to_dict()
        restored = HistoryEntry.from_dict(d)
        assert restored.filename == entry.filename
        assert restored.success == entry.success
        assert restored.duration_seconds == entry.duration_seconds
        assert restored.converted_at == entry.converted_at
