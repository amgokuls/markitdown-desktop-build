"""
MarkItDown Desktop — User-Facing Exception Wrappers

Translates raw MarkItDown exceptions into friendly messages shown in the UI.
Technical details are preserved for the optional "Details" view.
"""
from __future__ import annotations


class ConversionError(Exception):
    """Base class for all conversion errors surfaced to the UI."""

    def __init__(self, message: str, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.detail = detail


class UnsupportedFormatError(ConversionError):
    """The file format is not supported by MarkItDown."""


class CorruptedFileError(ConversionError):
    """The file appears to be corrupted or unreadable."""


class PermissionError(ConversionError):
    """Insufficient permissions to read the file."""


class MissingDependencyError(ConversionError):
    """An optional MarkItDown dependency is not installed."""


class ConversionFailedError(ConversionError):
    """MarkItDown attempted conversion but it failed."""


class CancelledError(ConversionError):
    """The conversion was cancelled by the user."""


def wrap_markitdown_exception(exc: Exception, filename: str) -> ConversionError:
    """Convert a raw MarkItDown / system exception into a user-friendly ConversionError."""
    import traceback

    detail = traceback.format_exc()
    exc_name = type(exc).__name__
    exc_str = str(exc)

    # Map known MarkItDown exceptions
    if exc_name in ("UnsupportedFormatException",):
        return UnsupportedFormatError(
            f"This file type is not supported.\nFile: {filename}",
            detail=detail,
        )
    if exc_name in ("FileConversionException", "FailedConversionAttempt"):
        return ConversionFailedError(
            f"Unable to convert this file. The converter may not support this content.\nFile: {filename}",
            detail=detail,
        )

    # System-level errors
    if isinstance(exc, PermissionError) or isinstance(exc, OSError):
        if "Permission denied" in exc_str:
            return PermissionError(
                f"Permission denied — cannot read this file.\nFile: {filename}",
                detail=detail,
            )
        if "No such file" in exc_str:
            return ConversionFailedError(
                f"File not found.\nFile: {filename}",
                detail=detail,
            )
        return ConversionFailedError(
            f"File system error while reading the file.\nFile: {filename}",
            detail=detail,
        )

    if isinstance(exc, MemoryError):
        return ConversionFailedError(
            f"Not enough memory to convert this file. Try closing other applications.\nFile: {filename}",
            detail=detail,
        )

    # ImportError usually means an optional dependency is missing
    if isinstance(exc, ImportError) or isinstance(exc, ModuleNotFoundError):
        return MissingDependencyError(
            f"A required converter component is not available.\nFile: {filename}",
            detail=detail,
        )

    # Generic fallback
    return ConversionFailedError(
        f"Conversion failed due to an unexpected error.\nFile: {filename}",
        detail=detail,
    )
