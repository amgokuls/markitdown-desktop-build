"""
File list and individual file rows for conversion batch.
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QScrollArea, QToolButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from app.conversion.models import FileItem, ConversionStatus
from app.ui.icons import get_icon


class FileRowWidget(QFrame):
    removeRequested = Signal(str)
    clicked = Signal(str)

    def __init__(self, item: FileItem, colors: dict):
        super().__init__()
        self.item = item
        self._colors = colors
        self.setObjectName("FileRow")
        # Fix: set a fixed height so the row never collapses
        self.setFixedHeight(72)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(f"""
            #FileRow {{
                background-color: transparent;
                border-bottom: 1px solid {colors.get('separator', '#ddd')};
            }}
            #FileRow:hover {{
                background-color: {colors.get('hover', '#eee')};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(24, 24)
        self.icon_lbl.setPixmap(get_icon("file", colors.get('secondary_label', '#666'), 24).pixmap(24, 24))
        layout.addWidget(self.icon_lbl)

        # Details layout
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)

        # Name and size
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.name_lbl = QLabel(item.display_name)
        font = self.name_lbl.font()
        font.setPointSize(13)
        self.name_lbl.setFont(font)
        self.name_lbl.setStyleSheet(f"color: {colors.get('primary_label', '#000')};")

        self.size_lbl = QLabel(item.file_size_str)
        self.size_lbl.setStyleSheet(f"color: {colors.get('secondary_label', '#666')}; font-size: 11pt;")

        header_layout.addWidget(self.name_lbl)
        header_layout.addWidget(self.size_lbl)
        header_layout.addStretch()

        details_layout.addLayout(header_layout)

        # Status / Progress
        status_layout = QHBoxLayout()
        self.status_lbl = QLabel("Pending")
        self.status_lbl.setStyleSheet(f"color: {colors.get('secondary_label', '#666')}; font-size: 11pt;")

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {colors.get('separator', '#ddd')};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {colors.get('accent', '#007AFF')};
                border-radius: 2px;
            }}
        """)
        self.progress.hide()

        status_layout.addWidget(self.status_lbl)
        status_layout.addWidget(self.progress)
        status_layout.addStretch()

        details_layout.addLayout(status_layout)
        layout.addLayout(details_layout)

        # Remove Button
        self.remove_btn = QToolButton()
        self.remove_btn.setIcon(get_icon("clear", colors.get('secondary_label', '#666'), 16))
        self.remove_btn.setStyleSheet("border: none; background: transparent;")
        self.remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.remove_btn.setToolTip("Remove File")
        self.remove_btn.clicked.connect(lambda: self.removeRequested.emit(str(self.item.path)))
        layout.addWidget(self.remove_btn)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(str(self.item.path))
        super().mouseReleaseEvent(event)

    def update_status(self):
        st = self.item.status

        if st == ConversionStatus.PENDING:
            self.status_lbl.setText("Pending")
            self.status_lbl.setStyleSheet(f"color: {self._colors.get('secondary_label', '#666')}; font-size: 11pt;")
            self.progress.hide()

        elif st == ConversionStatus.CONVERTING:
            self.status_lbl.setText("Converting…")
            self.status_lbl.setStyleSheet(f"color: {self._colors.get('accent', '#007AFF')}; font-size: 11pt;")
            self.progress.show()
            self.progress.setRange(0, 0)  # Indeterminate spinner
            self.remove_btn.setEnabled(False)

        elif st == ConversionStatus.SUCCESS:
            self.status_lbl.setText("✓ Converted")
            self.status_lbl.setStyleSheet(f"color: {self._colors.get('success', '#34C759')}; font-size: 11pt;")
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self.progress.hide()
            self.remove_btn.setEnabled(True)
            self.icon_lbl.setPixmap(get_icon("check", self._colors.get('success', '#34C759'), 24).pixmap(24, 24))

        elif st == ConversionStatus.ERROR:
            msg = self.item.error_message or "Failed"
            self.status_lbl.setText(f"✕ {msg}")
            self.status_lbl.setStyleSheet(f"color: {self._colors.get('destructive', '#FF3B30')}; font-size: 11pt;")
            self.progress.hide()
            self.remove_btn.setEnabled(True)
            self.icon_lbl.setPixmap(get_icon("warning", self._colors.get('destructive', '#FF3B30'), 24).pixmap(24, 24))


class FileListWidget(QWidget):
    fileSelected = Signal(str)
    fileRemoved = Signal(str)

    def __init__(self, colors: dict = None):
        super().__init__()
        self._colors = colors or {}
        self._rows = {}
        # Fix: always take at least a minimum height so drop zone doesn't resize
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addStretch()

        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

    def update_theme(self, colors: dict):
        self._colors = colors

    def add_files(self, items: list):
        for item in items:
            path_str = str(item.path)
            if path_str in self._rows:
                continue

            row = FileRowWidget(item, self._colors)
            row.removeRequested.connect(self._on_remove)
            row.clicked.connect(self.fileSelected.emit)

            self._rows[path_str] = row
            count = self.content_layout.count()
            self.content_layout.insertWidget(count - 1, row)
            row.show()

    def update_file_status(self, path_str: str):
        if path_str in self._rows:
            self._rows[path_str].update_status()

    def remove_file(self, path_str: str):
        self._on_remove(path_str)

    def _on_remove(self, path_str: str):
        if path_str in self._rows:
            row = self._rows.pop(path_str)
            self.content_layout.removeWidget(row)
            row.deleteLater()
            self.fileRemoved.emit(path_str)

    def clear_all(self):
        for row in self._rows.values():
            self.content_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

    def get_item(self, path_str: str):
        row = self._rows.get(path_str)
        return row.item if row else None

    def all_items(self) -> list:
        return [row.item for row in self._rows.values()]

    def all_paths(self) -> list:
        return list(self._rows.keys())

    def is_empty(self) -> bool:
        return len(self._rows) == 0
