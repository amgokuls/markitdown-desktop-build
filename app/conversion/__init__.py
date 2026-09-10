"""Conversion package — public API."""
from .converter import MarkItDownConverter, is_likely_supported, SUPPORTED_EXTENSIONS
from .manager import ConversionManager
from .models import ConversionResult, ConversionStatus, FileItem, HistoryEntry
from .exceptions import (
    ConversionError,
    UnsupportedFormatError,
    CorruptedFileError,
    MissingDependencyError,
    ConversionFailedError,
    CancelledError,
)

__all__ = [
    "MarkItDownConverter",
    "ConversionManager",
    "ConversionResult",
    "ConversionStatus",
    "FileItem",
    "HistoryEntry",
    "is_likely_supported",
    "SUPPORTED_EXTENSIONS",
    "ConversionError",
    "UnsupportedFormatError",
    "CorruptedFileError",
    "MissingDependencyError",
    "ConversionFailedError",
    "CancelledError",
]
