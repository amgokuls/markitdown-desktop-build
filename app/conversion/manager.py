"""
MarkItDown Desktop — Conversion Manager

Manages a queue of file conversions running on background QThreadPool workers.
Emits Qt signals for progress, completion, and error — the UI connects to these.

Architecture:
    ConversionManager (QObject)
        └── QThreadPool
                └── ConversionWorker (QRunnable) per file
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot, QMutex, QMutexLocker

from .converter import MarkItDownConverter
from .models import ConversionResult, ConversionStatus, FileItem

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Signals emitted by ConversionWorker (QRunnable can't emit signals directly)."""

    started = Signal(str)           # file path
    progress = Signal(str, float)   # file path, 0.0–1.0
    finished = Signal(object)       # ConversionResult
    error = Signal(str, str, str)   # file path, message, detail


class ConversionWorker(QRunnable):
    """Runs a single file conversion on the thread pool."""

    def __init__(self, file_item: FileItem, converter: MarkItDownConverter):
        super().__init__()
        self.file_item = file_item
        self.converter = converter
        self.signals = WorkerSignals()
        self._cancelled = False
        self.setAutoDelete(True)

    def cancel(self) -> None:
        self._cancelled = True

    @Slot()
    def run(self) -> None:
        path = self.file_item.path

        if self._cancelled:
            return

        self.signals.started.emit(str(path))
        self.signals.progress.emit(str(path), 0.1)

        try:
            if self._cancelled:
                return

            result = self.converter.convert_file(path)
            self.signals.progress.emit(str(path), 1.0)
            self.signals.finished.emit(result)

        except Exception as exc:
            logger.exception("Unexpected worker error for %s", path)
            self.signals.error.emit(
                str(path),
                f"Unexpected error converting {path.name}",
                str(exc),
            )


class ConversionManager(QObject):
    """
    Central manager for file conversion jobs.

    Signals:
        file_started(path_str)                  — conversion began
        file_progress(path_str, fraction)       — progress 0.0–1.0
        file_finished(ConversionResult)         — conversion done (success or fail)
        all_finished(completed, total)          — batch complete
    """

    file_started = Signal(str)
    file_progress = Signal(str, float)
    file_finished = Signal(object)  # ConversionResult
    all_finished = Signal(int, int)  # completed, total

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._converter = MarkItDownConverter()
        self._pool = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(4)

        self._active_workers: Dict[str, ConversionWorker] = {}
        self._mutex = QMutex()

        self._total = 0
        self._completed = 0

    def update_converter_settings(self, enable_plugins: bool, preserve_structure: bool) -> None:
        self._converter.update_settings(enable_plugins, preserve_structure)

    def convert_files(self, file_items: List[FileItem]) -> None:
        """Submit a list of FileItems for background conversion."""
        if not file_items:
            return

        with QMutexLocker(self._mutex):
            self._total += len(file_items)

        for item in file_items:
            item.status = ConversionStatus.CONVERTING
            worker = ConversionWorker(item, self._converter)
            worker.signals.started.connect(self._on_started)
            worker.signals.progress.connect(self._on_progress)
            worker.signals.finished.connect(self._on_finished)
            worker.signals.error.connect(self._on_error)

            with QMutexLocker(self._mutex):
                self._active_workers[str(item.path)] = worker

            self._pool.start(worker)

    def cancel_all(self) -> None:
        """Cancel all pending and running conversions."""
        with QMutexLocker(self._mutex):
            for worker in self._active_workers.values():
                worker.cancel()
            self._active_workers.clear()
        self._pool.clear()
        logger.info("All conversions cancelled")

    def cancel_file(self, path: Path) -> None:
        """Cancel conversion for a specific file."""
        key = str(path)
        with QMutexLocker(self._mutex):
            worker = self._active_workers.pop(key, None)
        if worker:
            worker.cancel()

    @property
    def markitdown_version(self) -> str:
        return self._converter.markitdown_version

    # ------------------------------------------------------------------ #
    # Internal slots
    # ------------------------------------------------------------------ #

    @Slot(str)
    def _on_started(self, path_str: str) -> None:
        logger.debug("Started: %s", path_str)
        self.file_started.emit(path_str)

    @Slot(str, float)
    def _on_progress(self, path_str: str, fraction: float) -> None:
        self.file_progress.emit(path_str, fraction)

    @Slot(object)
    def _on_finished(self, result: ConversionResult) -> None:
        key = str(result.input_file)
        with QMutexLocker(self._mutex):
            self._active_workers.pop(key, None)
            self._completed += 1
            completed = self._completed
            total = self._total

        self.file_finished.emit(result)
        logger.debug("Finished: %s (success=%s)", result.input_file.name, result.success)

        if completed >= total:
            self.all_finished.emit(completed, total)
            with QMutexLocker(self._mutex):
                self._total = 0
                self._completed = 0

    @Slot(str, str, str)
    def _on_error(self, path_str: str, message: str, detail: str) -> None:
        key = path_str
        with QMutexLocker(self._mutex):
            self._active_workers.pop(key, None)
            self._completed += 1
            completed = self._completed
            total = self._total

        result = ConversionResult(
            input_file=Path(path_str),
            success=False,
            error_message=message,
            error_detail=detail,
        )
        self.file_finished.emit(result)

        if completed >= total:
            self.all_finished.emit(completed, total)
            with QMutexLocker(self._mutex):
                self._total = 0
                self._completed = 0
