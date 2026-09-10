"""
Elegant, native-feeling macOS drag-and-drop zone.
"""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

from app.ui.icons import get_icon

class DropZone(QWidget):
    filesDropped = Signal(list)
    chooseFilesClicked = Signal()

    def __init__(self, colors: dict = None):
        super().__init__()
        self._colors = colors or {}
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setObjectName("DropZone")
        self._is_drag_active = False
        self._setup_ui()

    def update_theme(self, colors: dict):
        self._colors = colors
        self._update_style()
        self._icon_lbl.setPixmap(get_icon("file", colors['secondary_label'], 48).pixmap(48, 48))

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 40, 24, 40)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._icon_lbl = QLabel()
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # We'll set the pixmap in update_theme or manually here
        layout.addWidget(self._icon_lbl)
        
        title_lbl = QLabel("Drop files to convert")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_lbl.font()
        font.setPointSize(15)
        font.setWeight(QFont.Weight.DemiBold)
        title_lbl.setFont(font)
        self._title_lbl = title_lbl
        layout.addWidget(title_lbl)
        
        sub_lbl = QLabel("or choose files from your Mac")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_sub = sub_lbl.font()
        font_sub.setPointSize(13)
        sub_lbl.setFont(font_sub)
        self._sub_lbl = sub_lbl
        layout.addWidget(sub_lbl)
        
        layout.addSpacing(16)
        
        self.choose_btn = QPushButton("Choose Files…")
        self.choose_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # Use native macOS button appearance
        self.choose_btn.setMinimumWidth(140)
        self.choose_btn.clicked.connect(self.chooseFilesClicked.emit)
        
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(self.choose_btn)
        layout.addLayout(btn_layout)
        
        self._update_style()

    def _update_style(self):
        bg = self._colors.get('hover', '#E5E5EA') if self._is_drag_active else "transparent"
        border = self._colors.get('accent', '#007AFF') if self._is_drag_active else "transparent"
        
        self.setStyleSheet(f"""
            #DropZone {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 12px;
            }}
        """)
        self._title_lbl.setStyleSheet(f"color: {self._colors.get('primary_label', '#000')};")
        self._sub_lbl.setStyleSheet(f"color: {self._colors.get('secondary_label', '#666')};")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._is_drag_active = True
            self._update_style()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._is_drag_active = False
        self._update_style()
        event.accept()

    def dropEvent(self, event):
        self._is_drag_active = False
        self._update_style()
        
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                p = Path(url.toLocalFile())
                if p.is_dir():
                    paths.extend(self._collect_directory(p))
                else:
                    paths.append(p)
                    
        if paths:
            self.filesDropped.emit(paths)
        
        event.acceptProposedAction()

    def _collect_directory(self, d: Path) -> list[Path]:
        collected = []
        for p in d.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                collected.append(p)
        return collected
