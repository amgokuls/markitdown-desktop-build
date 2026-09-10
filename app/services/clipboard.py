"""
MarkItDown Desktop — Clipboard Service

Provides copy-to-clipboard functionality with platform-appropriate feedback.
"""
from __future__ import annotations

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication


class ClipboardService:
    """Thin wrapper around Qt clipboard."""

    @staticmethod
    def copy_text(text: str) -> None:
        """Copy text to the system clipboard."""
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(text)

    @staticmethod
    def get_text() -> str:
        """Return current clipboard text content."""
        clipboard: QClipboard = QApplication.clipboard()
        return clipboard.text()
