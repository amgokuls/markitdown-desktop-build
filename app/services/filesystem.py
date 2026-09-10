"""
MarkItDown Desktop — Filesystem Service

Native file picker dialogs and save operations.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import QFileDialog, QWidget

logger = logging.getLogger(__name__)

# Supported file filter string for the open dialog
OPEN_FILTER = (
    "Supported Files ("
    "*.pdf *.docx *.doc *.pptx *.ppt *.xlsx *.xls "
    "*.html *.htm *.csv *.json *.xml *.zip *.epub "
    "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff "
    "*.mp3 *.wav *.m4a *.msg *.ipynb *.txt *.md *.rst *.rtf"
    ");;"
    "All Files (*)"
)


class FilesystemService:
    """Provides native macOS file picker and save dialogs."""

    @staticmethod
    def pick_files(parent: Optional[QWidget] = None) -> List[Path]:
        """
        Open a native file picker allowing multiple file selection.
        Returns a list of selected Paths (empty list if cancelled).
        """
        paths, _ = QFileDialog.getOpenFileNames(
            parent,
            "Select Files to Convert",
            str(Path.home()),
            OPEN_FILTER,
        )
        return [Path(p) for p in paths]

    @staticmethod
    def pick_directory(parent: Optional[QWidget] = None) -> Optional[Path]:
        """Open a directory picker. Returns None if cancelled."""
        directory = QFileDialog.getExistingDirectory(
            parent,
            "Select Output Folder",
            str(Path.home()),
            QFileDialog.ShowDirsOnly,
        )
        return Path(directory) if directory else None

    @staticmethod
    def save_markdown(
        parent: Optional[QWidget],
        default_name: str,
        default_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Show a native Save As dialog for a single Markdown file.
        Returns the chosen Path, or None if cancelled.
        """
        start_dir = str(default_dir) if default_dir else str(Path.home())
        path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save Markdown",
            str(Path(start_dir) / default_name),
            "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)",
        )
        return Path(path) if path else None

    @staticmethod
    def write_markdown(path: Path, content: str) -> None:
        """Write Markdown content to the given path."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info("Saved Markdown: %s", path)
