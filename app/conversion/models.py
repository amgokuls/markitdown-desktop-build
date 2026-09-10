"""
MarkItDown Desktop — Conversion Data Models

Defines the core dataclasses shared between the conversion layer and UI.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional


class ConversionStatus(Enum):
    PENDING = auto()
    CONVERTING = auto()
    SUCCESS = auto()
    ERROR = auto()
    CANCELLED = auto()


@dataclass
class FileItem:
    """Represents a single file queued for conversion."""

    path: Path
    status: ConversionStatus = ConversionStatus.PENDING
    progress: float = 0.0  # 0.0 – 1.0
    error_message: Optional[str] = None
    error_detail: Optional[str] = None  # technical traceback for Details button
    result: Optional["ConversionResult"] = None

    @property
    def display_name(self) -> str:
        return self.path.name

    @property
    def file_size_str(self) -> str:
        try:
            size = self.path.stat().st_size
        except OSError:
            return "Unknown"
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def extension(self) -> str:
        return self.path.suffix.upper().lstrip(".")


@dataclass
class ConversionResult:
    """The result of a single file conversion."""

    input_file: Path
    success: bool
    markdown: str = ""
    error_message: str = ""
    error_detail: str = ""
    duration_seconds: float = 0.0
    converted_at: float = field(default_factory=time.time)

    @property
    def display_name(self) -> str:
        return self.input_file.name

    @property
    def suggested_output_name(self) -> str:
        return self.input_file.stem + ".md"


@dataclass
class HistoryEntry:
    """Lightweight history record (no document content stored)."""

    filename: str
    path: str
    success: bool
    duration_seconds: float
    converted_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "path": self.path,
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "converted_at": self.converted_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(**data)
