"""
About dialog.
Clean, native macOS-style About window.
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QCursor
import markitdown

from app.services.filesystem import FilesystemService


def open_folder(path_str):
    import sys, subprocess, os
    if sys.platform == "win32":
        os.startfile(path_str)
    elif sys.platform == "darwin":
        subprocess.run(["open", path_str])
    else:
        subprocess.run(["xdg-open", path_str])

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About MarkItDown Desktop")
        self.setFixedSize(360, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Icon
        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Try to load the actual app icon
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "AppIcon.jpg"
        if icon_path.exists():
            pix = QPixmap(str(icon_path))
            # Smooth scale to 96x96
            pix = pix.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_lbl.setPixmap(pix)
            # Make it look like a macOS icon with rounded corners if possible, but the source image is already square.
            
        layout.addWidget(icon_lbl)
        
        # Title
        title_lbl = QLabel("MarkItDown Desktop")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_lbl.font()
        font.setPointSize(18)
        font.setWeight(QFont.Weight.Bold)
        title_lbl.setFont(font)
        layout.addWidget(title_lbl)
        
        # Version
        ver_lbl = QLabel("Version 1.0.0")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_lbl.setStyleSheet("color: palette(placeholderText);")
        layout.addWidget(ver_lbl)
        
        # Description
        desc_lbl = QLabel("An independent macOS desktop interface for Microsoft's MarkItDown.")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        
        layout.addSpacing(16)
        
        # Tech stack info
        tech_lbl = QLabel(
            f"markitdown: {markitdown.__version__}\n"
            f"Python: {sys.version.split(' ')[0]}\n"
            f"License: MIT"
        )
        tech_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech_lbl.setStyleSheet("font-size: 11pt; color: palette(placeholderText);")
        layout.addWidget(tech_lbl)
        
        layout.addStretch()
        
        # Actions
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        btn_github = QPushButton("View on GitHub")
        btn_github.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # Optional: btn_github.clicked.connect(...)
        
        btn_logs = QPushButton("Open Logs")
        btn_logs.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_logs.clicked.connect(lambda: open_folder(str(Path.home() / ".markitdown-desktop" / "logs")))
        
        btn_layout.addWidget(btn_github)
        btn_layout.addWidget(btn_logs)
        
        layout.addLayout(btn_layout)
