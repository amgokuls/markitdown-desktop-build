"""
MarkItDown Desktop — MarkItDown Adapter (Converter)

Clean abstraction layer around Microsoft's MarkItDown package.
All MarkItDown interactions happen here. UI components never import markitdown directly.

Security:
  - Uses convert_local() (narrowest API) for all local file conversions.
  - Validates that the path is an actual local file before passing to MarkItDown.
  - Never executes document content as code.
  - Never passes unsanitized remote URLs.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from .exceptions import ConversionError, wrap_markitdown_exception
from .models import ConversionResult

logger = logging.getLogger(__name__)


class MarkItDownConverter:
    """
    Singleton-safe wrapper around MarkItDown.

    Creating a MarkItDown() instance is inexpensive; we keep one per
    converter instance so settings (plugins, llm_client) can be swapped later.
    """

    def __init__(self, enable_plugins: bool = False, preserve_structure: bool = True):
        self._enable_plugins = enable_plugins
        self._preserve_structure = preserve_structure
        self._md_instance = self._create_instance()

    def _create_instance(self):
        """Lazily create the MarkItDown instance."""
        try:
            from markitdown import MarkItDown

            return MarkItDown(enable_plugins=self._enable_plugins)
        except ImportError as exc:
            raise RuntimeError(
                "MarkItDown is not installed. "
                "Please run: pip install 'markitdown[all]'"
            ) from exc

    def update_settings(self, enable_plugins: bool, preserve_structure: bool) -> None:
        """Recreate the MarkItDown instance if settings changed."""
        changed = (
            self._enable_plugins != enable_plugins
            or self._preserve_structure != preserve_structure
        )
        if changed:
            self._enable_plugins = enable_plugins
            self._preserve_structure = preserve_structure
            self._md_instance = self._create_instance()

    def convert_file(self, path: Path) -> ConversionResult:
        """
        Convert a local file to Markdown.

        Args:
            path: Absolute path to the local file.

        Returns:
            ConversionResult with success=True and populated markdown, or
            success=False with user-friendly error messages.

        Security:
            Validates path is local and readable before calling MarkItDown.
        """
        start = time.monotonic()

        # --- Input validation ---
        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_absolute():
            path = path.resolve()

        if not path.exists():
            return ConversionResult(
                input_file=path,
                success=False,
                error_message=f"File not found.\nFile: {path.name}",
                error_detail=f"Path does not exist: {path}",
                duration_seconds=0.0,
            )

        if not path.is_file():
            return ConversionResult(
                input_file=path,
                success=False,
                error_message=f"Not a file.\nPath: {path.name}",
                error_detail=f"Path is not a regular file: {path}",
                duration_seconds=0.0,
            )

        if not _is_readable(path):
            return ConversionResult(
                input_file=path,
                success=False,
                error_message=f"Permission denied — cannot read this file.\nFile: {path.name}",
                error_detail=f"File not readable: {path}",
                duration_seconds=0.0,
            )

        # --- Conversion ---
        logger.info("Converting: %s", path)
        try:
            # Use convert_local() — the narrowest/safest API for local files
            result = self._md_instance.convert_local(str(path))
            duration = time.monotonic() - start
            markdown = result.markdown or ""
            logger.info("Converted %s in %.2fs (%d chars)", path.name, duration, len(markdown))
            return ConversionResult(
                input_file=path,
                success=True,
                markdown=markdown,
                duration_seconds=duration,
            )
        except Exception as exc:
            duration = time.monotonic() - start
            logger.warning("Conversion failed for %s: %s", path.name, exc, exc_info=True)
            friendly = wrap_markitdown_exception(exc, path.name)
            return ConversionResult(
                input_file=path,
                success=False,
                error_message=friendly.message,
                error_detail=friendly.detail,
                duration_seconds=duration,
            )

    @property
    def markitdown_version(self) -> str:
        """Return installed MarkItDown version string."""
        try:
            from importlib.metadata import version

            return version("markitdown")
        except Exception:
            return "unknown"


def _is_readable(path: Path) -> bool:
    """Check if a file is readable without raising."""
    try:
        with open(path, "rb") as f:
            f.read(1)
        return True
    except OSError:
        return False


# --- Supported extensions (informational; MarkItDown uses magika for detection) ---
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
    ".html", ".htm", ".csv", ".json", ".xml", ".zip", ".epub",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff",
    ".mp3", ".wav", ".m4a",
    ".msg",  # Outlook
    ".ipynb",  # Jupyter
    ".txt", ".md", ".rst", ".rtf",
}


def is_likely_supported(path: Path) -> bool:
    """
    Return True if the file extension is in the known-supported set.
    MarkItDown may still attempt conversion even for unknown extensions
    (it uses magika for MIME detection).
    """
    return path.suffix.lower() in SUPPORTED_EXTENSIONS
