"""
History sidebar panel.
Uses native macOS styling and icons.
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QSizePolicy, QScrollArea, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

from app.conversion.models import HistoryEntry
from app.ui.icons import get_icon

class HistoryRowWidget(QFrame):
    clicked = Signal(str)

    def __init__(self, entry: HistoryEntry, colors: dict):
        super().__init__()
        self.entry = entry
        self._colors = colors
        self.setObjectName("HistoryRow")
        
        # We handle styling in styles.py generally, but for hover effects we can use QWidget events or specific CSS
        self.setStyleSheet(f"""
            #HistoryRow {{
                background: transparent;
                border-radius: 6px;
                border-bottom: 1px solid {colors.get('separator', '#ddd')};
            }}
            #HistoryRow:hover {{
                background-color: {colors.get('hover', '#eee')};
            }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        icon_lbl = QLabel()
        icon_color = colors.get('success', '#34C759') if entry.success else colors.get('destructive', '#FF3B30')
        icon_name = "check" if entry.success else "warning"
        icon_lbl.setPixmap(get_icon(icon_name, icon_color, 16).pixmap(16, 16))
        layout.addWidget(icon_lbl)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        name_lbl = QLabel(entry.filename)
        font = name_lbl.font()
        font.setPointSize(13)
        name_lbl.setFont(font)
        name_lbl.setStyleSheet(f"color: {colors.get('primary_label', '#000')};")
        
        dt = datetime.fromtimestamp(entry.converted_at)
        time_str = dt.strftime("%I:%M %p").lstrip("0")
        if not entry.success:
            time_str += " • Failed"
            
        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet(f"color: {colors.get('secondary_label', '#666')}; font-size: 11pt;")
        
        text_layout.addWidget(name_lbl)
        text_layout.addWidget(time_lbl)
        layout.addLayout(text_layout)
        layout.addStretch()
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.entry.path)
        super().mouseReleaseEvent(event)


class HistoryPanel(QWidget):
    historyItemClicked = Signal(str)
    clearRequested = Signal()

    def __init__(self, colors: dict = None):
        super().__init__()
        self._colors = colors or {}
        self.setObjectName("SidebarFrame")
        self._setup_ui()

    def update_theme(self, colors: dict):
        self._colors = colors
        self.setStyleSheet(f"""
            #SidebarFrame {{
                background-color: {colors['sidebar_bg']};
                border-right: 1px solid {colors.get('separator', '#ddd')};
            }}
        """)
        # We would normally update child widgets here too, but for simplicity we rely on the main window applying the global stylesheet.

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 16, 16, 12)
        
        title = QLabel("History")
        title_font = title.font()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self._colors.get('secondary_label', '#666')};")
        
        clear_btn = QToolButton()
        clear_btn.setIcon(get_icon("trash", self._colors.get('secondary_label', '#666'), 14))
        clear_btn.setToolTip("Clear History")
        clear_btn.setStyleSheet("border: none; background: transparent;")
        clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_btn.clicked.connect(self.clearRequested.emit)
        
        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(clear_btn)
        
        layout.addWidget(header)
        
        # Scroll area for items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addStretch() # Push items to top
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)

    def load_entries(self, entries: list[HistoryEntry]):
        self.clear()
        for entry in reversed(entries):
            self._add_row(entry, append=True)

    def prepend_entry(self, entry: HistoryEntry):
        self._add_row(entry, append=False)

    def _add_row(self, entry: HistoryEntry, append: bool = False):
        row = HistoryRowWidget(entry, self._colors)
        row.clicked.connect(self.historyItemClicked.emit)
        
        if append:
            # insert before the stretch
            count = self.content_layout.count()
            self.content_layout.insertWidget(count - 1, row)
        else:
            self.content_layout.insertWidget(0, row)
        
        row.show() # CRITICAL FIX: Ensure the row is visible when dynamically added

    def clear(self):
        # Remove all widgets except the bottom stretch
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
