"""
Settings/Preferences dialog.
Uses clean, native-feeling macOS form layouts.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QCheckBox, QPushButton, QFrame,
    QFormLayout
)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QFont

class SettingsDialog(QDialog):
    settingsChanged = Signal()

    class Settings:
        def __init__(self):
            self._qs = QSettings("MarkItDownDesktop", "MarkItDown Desktop")

        def get(self, key: str, default=None):
            return self._qs.value(key, default)

        def set(self, key: str, value):
            self._qs.setValue(key, value)
            self._qs.sync()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.settings = self.Settings()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Helper to create section headers
        def make_header(text):
            lbl = QLabel(text)
            font = lbl.font()
            font.setPointSize(13)
            font.setWeight(QFont.Weight.DemiBold)
            lbl.setFont(font)
            return lbl

        def make_separator():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("background-color: palette(windowText); opacity: 0.1;")
            line.setFixedHeight(1)
            return line

        # 1. Appearance Section
        layout.addWidget(make_header("Appearance"))
        
        form_app = QFormLayout()
        form_app.setContentsMargins(12, 0, 0, 0)
        form_app.setSpacing(12)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        
        current_theme = self.settings.get("theme", "system")
        idx = {"system": 0, "light": 1, "dark": 2}.get(current_theme.lower(), 0)
        self.theme_combo.setCurrentIndex(idx)
        
        form_app.addRow("Theme:", self.theme_combo)
        layout.addLayout(form_app)
        
        layout.addWidget(make_separator())
        
        # 2. General Section
        layout.addWidget(make_header("General"))
        
        form_gen = QFormLayout()
        form_gen.setContentsMargins(12, 0, 0, 0)
        form_gen.setSpacing(12)
        
        self.auto_clear_cb = QCheckBox("Clear list automatically after successful conversion")
        self.auto_clear_cb.setChecked(self.settings.get("auto_clear", False) == "true" or self.settings.get("auto_clear", False) is True)
        
        self.auto_save_cb = QCheckBox("Automatically save Markdown to source folder")
        self.auto_save_cb.setChecked(self.settings.get("auto_save", False) == "true" or self.settings.get("auto_save", False) is True)
        
        form_gen.addRow("", self.auto_clear_cb)
        form_gen.addRow("", self.auto_save_cb)
        layout.addLayout(form_gen)
        
        layout.addStretch()
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Save")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_save)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    def _on_save(self):
        theme_val = self.theme_combo.currentText().lower()
        self.settings.set("theme", theme_val)
        self.settings.set("auto_clear", self.auto_clear_cb.isChecked())
        self.settings.set("auto_save", self.auto_save_cb.isChecked())
        self.settingsChanged.emit()
        self.accept()
