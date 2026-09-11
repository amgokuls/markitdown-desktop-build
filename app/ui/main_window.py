"""
Main window of MarkItDown Desktop.
Provides a clean, macOS-native workspace layout.
"""
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QToolButton, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QIcon

from app.conversion.manager import ConversionManager
from app.conversion.models import FileItem, HistoryEntry
from app.services.clipboard import ClipboardService
from app.services.filesystem import FilesystemService
from app.services.history import HistoryService

from .styles import Theme, get_stylesheet, get_colors
from .drop_zone import DropZone
from .file_list import FileListWidget
from .preview import PreviewPanel
from .history import HistoryPanel
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog
from .icons import get_icon

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MarkItDown Desktop")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        
        # Services
        self._clipboard = ClipboardService()
        self._fs = FilesystemService()
        self._history = HistoryService()
        
        self._conversion_mgr = ConversionManager()
        self._conversion_mgr.file_started.connect(self._on_file_started)
        self._conversion_mgr.file_finished.connect(self._on_file_finished)
        self._conversion_mgr.file_progress.connect(self._on_file_progress)
        self._conversion_mgr.all_finished.connect(self._on_all_finished)
        
        # Determine theme
        settings = SettingsDialog.Settings()
        theme_str = settings.get("theme", Theme.SYSTEM.value)
        try:
            self._current_theme = Theme(theme_str)
        except ValueError:
            self._current_theme = Theme.SYSTEM
            
        self._colors = get_colors(self._current_theme)
        
        self._setup_actions()
        self._setup_ui()
        self._setup_menus()
        
        self._apply_theme()
        
        # Load history
        self._history_panel.load_entries(self._history.all_entries())

    def _apply_theme(self):
        self._colors = get_colors(self._current_theme)
        self.setStyleSheet(get_stylesheet(self._current_theme))
        
        self._history_panel.update_theme(self._colors)
        self._drop_zone.update_theme(self._colors)
        self._file_list.update_theme(self._colors)
        self._preview_panel.update_theme(self._colors)
        
        self._update_toolbar_icons()

    def _update_toolbar_icons(self):
        # Update action icons for light/dark
        icon_color = self._colors.get('primary_label', '#000000')
        self.act_add.setIcon(get_icon("add", icon_color))
        self.act_convert.setIcon(get_icon("convert", self._colors.get('accent', '#007AFF')))
        self.act_cancel.setIcon(get_icon("cancel", self._colors.get('destructive', '#FF3B30')))
        self.act_settings.setIcon(get_icon("settings", icon_color))
        self.act_history.setIcon(get_icon("history", icon_color))

    def _setup_actions(self):
        self.act_add = QAction("Add Files…", self)
        self.act_add.setShortcut(QKeySequence("Ctrl+O"))
        self.act_add.triggered.connect(self._on_add_files)
        
        self.act_convert = QAction("Convert", self)
        self.act_convert.setShortcut(QKeySequence("Ctrl+Return"))
        self.act_convert.triggered.connect(self._on_convert)
        
        self.act_cancel = QAction("Cancel", self)
        self.act_cancel.triggered.connect(self._conversion_mgr.cancel_all)
        self.act_cancel.setEnabled(False)
        
        self.act_settings = QAction("Settings…", self)
        self.act_settings.setShortcut(QKeySequence("Ctrl+,"))
        self.act_settings.triggered.connect(self._show_settings)
        
        self.act_history = QAction("Toggle History", self)
        self.act_history.setShortcut(QKeySequence("Ctrl+H"))
        self.act_history.triggered.connect(self._toggle_history)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar (Unified look)
        self.toolbar = QWidget()
        self.toolbar.setObjectName("ToolbarFrame")
        self.toolbar.setFixedHeight(52)
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(16, 8, 16, 8)
        
        # We use QToolButtons to show TextBesideIcon
        def make_tb(action):
            b = QToolButton()
            b.setDefaultAction(action)
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("border: none; background: transparent; padding: 4px 8px; border-radius: 4px;")
            return b
            
        tb_layout.addWidget(make_tb(self.act_history))
        tb_layout.addSpacing(16)
        tb_layout.addWidget(make_tb(self.act_add))
        tb_layout.addStretch()
        
        self.convert_btn = make_tb(self.act_convert)
        self.convert_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {self._colors.get('accent', '#007AFF')};
                color: #FFFFFF;
                border: none;
                padding: 4px 16px;
                border-radius: 6px;
                font-weight: 600;
            }}
        """)
        tb_layout.addWidget(self.convert_btn)
        
        self.cancel_btn = make_tb(self.act_cancel)
        self.cancel_btn.hide()
        tb_layout.addWidget(self.cancel_btn)
        
        tb_layout.addStretch()
        tb_layout.addWidget(make_tb(self.act_settings))
        
        main_layout.addWidget(self.toolbar)
        
        # Splitter for Main Content
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        main_layout.addWidget(self.splitter)
        
        # 1. History Panel
        self._history_panel = HistoryPanel(self._colors)
        self._history_panel.historyItemClicked.connect(self._on_history_clicked)
        self._history_panel.clearRequested.connect(self._on_clear_history)
        self.splitter.addWidget(self._history_panel)
        
        # 2. Workspace (Drop Zone + File List stacked)
        workspace = QWidget()
        ws_layout = QVBoxLayout(workspace)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(0)

        self._drop_zone = DropZone(self._colors)
        self._drop_zone.filesDropped.connect(self._on_files_dropped)
        self._drop_zone.chooseFilesClicked.connect(self._on_add_files)
        self._drop_zone.setMinimumHeight(200)
        # stretch=0 means it won't shrink/grow — stays exactly its preferred size
        ws_layout.addWidget(self._drop_zone, stretch=0)

        self._file_list = FileListWidget(self._colors)
        self._file_list.fileRemoved.connect(self._update_convert_button)
        self._file_list.fileSelected.connect(self._on_file_selected)
        self._file_list.hide()  # Hidden until files are added
        # stretch=1 means it fills all remaining space
        ws_layout.addWidget(self._file_list, stretch=1)

        
        self.splitter.addWidget(workspace)
        
        # 3. Preview Panel
        self._preview_panel = PreviewPanel(self._colors)
        self._preview_panel.copyRequested.connect(self._on_copy_markdown)
        self._preview_panel.saveRequested.connect(self._on_save_markdown)
        self.splitter.addWidget(self._preview_panel)
        
        # Initial proportions
        self.splitter.setSizes([240, 400, 460])
        
        self._update_convert_button()

    def _setup_menus(self):
        menubar = self.menuBar()
        
        # File
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.act_add)
        file_menu.addSeparator()
        
        act_save = QAction("Save Markdown…", self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self._on_save_markdown)
        file_menu.addAction(act_save)
        
        act_close = QAction("Close Window", self)
        act_close.setShortcut(QKeySequence("Ctrl+W"))
        act_close.triggered.connect(self.close)
        file_menu.addAction(act_close)
        
        # Edit
        edit_menu = menubar.addMenu("Edit")
        act_copy = QAction("Copy Markdown", self)
        act_copy.setShortcut(QKeySequence("Ctrl+C"))
        act_copy.triggered.connect(self._on_copy_markdown)
        edit_menu.addAction(act_copy)
        
        # View
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.act_history)
        
        # Help
        help_menu = menubar.addMenu("Help")
        act_about = QAction("About MarkItDown Desktop", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _on_add_files(self):
        paths = self._fs.pick_files(self)
        if paths:
            self._on_files_dropped(paths)

    def _on_files_dropped(self, paths: list[Path]):
        items = []
        for p in paths:
            if p.is_file() and not p.name.startswith("."):
                items.append(FileItem(path=p))
        if items:
            self._drop_zone.hide()
            self._file_list.show()
            self._file_list.add_files(items)
            self._update_convert_button()

    def _update_convert_button(self):
        has_files = not self._file_list.is_empty()
        self.act_convert.setEnabled(has_files)
        
        if not has_files:
            self._file_list.hide()
            self._drop_zone.show()

    def _on_convert(self):
        items = self._file_list.all_items()
        if not items:
            return
            
        self.act_convert.setVisible(False)
        self.convert_btn.hide()
        self.act_cancel.setEnabled(True)
        self.cancel_btn.show()
        
        self.act_add.setEnabled(False)
        self._conversion_mgr.convert_files(items)

    def _on_file_started(self, path: str):
        self._file_list.update_file_status(path)

    def _on_file_progress(self, path: str, msg: str):
        pass # Optional detailed progress

    def _on_file_selected(self, path_str: str):
        item = self._file_list.get_item(path_str)
        if item and item.result and item.result.success:
            self._preview_panel.set_content(item.result.display_name, item.result.markdown)
            
    def _on_file_finished(self, result):
        path_str = str(result.input_file)

        # ── Fix 1: update the FileItem's status so the row re-renders correctly ──
        from app.conversion.models import ConversionStatus
        item = self._file_list.get_item(path_str)
        if item:
            item.status = ConversionStatus.SUCCESS if result.success else ConversionStatus.ERROR
            item.error_message = result.error_message
            item.result = result          # store result on item for click-to-preview

        self._file_list.update_file_status(path_str)

        # Build HistoryEntry
        from app.conversion.models import HistoryEntry
        entry = HistoryEntry(
            filename=result.display_name,
            path=str(result.input_file),
            success=result.success,
            duration_seconds=result.duration_seconds,
            converted_at=result.converted_at
        )

        # Update history
        self._history.add(entry)
        self._history_panel.prepend_entry(entry)

        # Show in preview if successful
        if result.success:
            self._preview_panel.set_content(result.display_name, result.markdown)


    def _on_all_finished(self, total: int, success: int):
        self.act_convert.setVisible(True)
        self.convert_btn.show()
        self.cancel_btn.hide()
        self.act_cancel.setEnabled(False)
        self.act_add.setEnabled(True)
        
        # Clean up list if auto-clear is enabled, otherwise leave for user review
        settings = SettingsDialog.Settings()
        if settings.get("auto_clear", False):
            self._file_list.clear_all()
            self._update_convert_button()

    def _toggle_history(self):
        self._history_panel.setVisible(not self._history_panel.isVisible())

    def _on_history_clicked(self, path_str: str):
        # We don't store markdown content in history to save space.
        # So clicking history doesn't auto-preview unless we re-convert.
        # But we could allow re-adding it to the queue.
        p = Path(path_str)
        if p.exists():
            self._on_files_dropped([p])
        else:
            QMessageBox.warning(self, "Not Found", f"File no longer exists:\n{path_str}")

    def _on_clear_history(self):
        reply = QMessageBox.question(self, "Clear History", "Are you sure you want to clear all history?")
        if reply == QMessageBox.StandardButton.Yes:
            self._history.clear()
            self._history_panel.clear()

    def _on_copy_markdown(self):
        md = self._preview_panel.current_markdown
        if md:
            self._clipboard.copy_text(md)
            # Flash success
            old_text = self.act_convert.text()
            self.statusBar().showMessage("Markdown copied to clipboard", 3000)

    def _on_save_markdown(self):
        """Save all successfully converted files as .md into a chosen folder."""
        # Collect all items that have been converted successfully
        converted = [
            item for item in self._file_list.all_items()
            if item.result and item.result.success
        ]

        if not converted:
            # Nothing converted yet — try the preview panel as fallback
            md = self._preview_panel.current_markdown
            if md:
                from app.conversion.models import ConversionStatus
                path, _ = __import__('PySide6.QtWidgets', fromlist=['QFileDialog']).QFileDialog.getSaveFileName(
                    self,
                    "Save Markdown",
                    str(Path.home() / (self._preview_panel.current_filename or "output.md")),
                    "Markdown Files (*.md);;All Files (*)",
                )
                if path:
                    if not path.endswith(".md"):
                        path += ".md"
                    self._fs.write_markdown(Path(path), md)
                    self.statusBar().showMessage(f"Saved: {Path(path).name}", 3000)
            return

        if len(converted) == 1:
            # Single file — show a Save As dialog with .md forced
            item = converted[0]
            default_name = item.result.suggested_output_name  # already ends in .md
            path, _ = __import__('PySide6.QtWidgets', fromlist=['QFileDialog']).QFileDialog.getSaveFileName(
                self,
                "Save Markdown",
                str(Path.home() / default_name),
                "Markdown Files (*.md);;All Files (*)",
            )
            if path:
                if not path.endswith(".md"):
                    path += ".md"
                self._fs.write_markdown(Path(path), item.result.markdown)
                self.statusBar().showMessage(f"Saved: {Path(path).name}", 3000)
        else:
            # Multiple files — pick a folder and save all as .md
            from PySide6.QtWidgets import QFileDialog
            folder = QFileDialog.getExistingDirectory(
                self,
                f"Choose folder to save {len(converted)} Markdown files",
                str(Path.home()),
                QFileDialog.Option.ShowDirsOnly,
            )
            if not folder:
                return
            folder_path = Path(folder)
            saved = 0
            for item in converted:
                out_path = folder_path / item.result.suggested_output_name
                self._fs.write_markdown(out_path, item.result.markdown)
                saved += 1
            self.statusBar().showMessage(
                f"Saved {saved} file(s) to {folder_path.name}/", 4000
            )


    def _show_settings(self):
        dlg = SettingsDialog(self)
        dlg.settingsChanged.connect(self._on_settings_changed)
        dlg.exec()

    def _on_settings_changed(self):
        settings = SettingsDialog.Settings()
        theme_str = settings.get("theme", Theme.SYSTEM.value)
        try:
            new_theme = Theme(theme_str)
        except ValueError:
            new_theme = Theme.SYSTEM
            
        if new_theme != self._current_theme:
            self._current_theme = new_theme
            self._apply_theme()

    def _show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()
