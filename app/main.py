"""
MarkItDown Desktop — Application Entry Point

Sets up logging, creates the QApplication, applies the theme,
and launches the main window.
"""
from __future__ import annotations

import logging
import sys
import os
from pathlib import Path

# ------------------------------------------------------------------ #
# Logging — BEFORE any Qt imports
# ------------------------------------------------------------------ #
LOG_DIR = Path.home() / ".markitdown-desktop" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "markitdown-desktop.log", encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)

# Suppress noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> int:
    """Application entry point."""
    logger.info("Starting MarkItDown Desktop")

    # High-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

    # Must create QApplication before importing Qt widgets
    app = QApplication(sys.argv)
    app.setApplicationName("MarkItDown Desktop")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MarkItDownDesktop")
    app.setOrganizationDomain("markitdown-desktop.local")

    # macOS native look
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    # Default font
    font = QFont("-apple-system")
    font.setPointSize(13)
    app.setFont(font)

    # Import UI (after QApplication exists)
    from app.ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    logger.info("Main window shown")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
