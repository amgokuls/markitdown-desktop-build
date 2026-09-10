"""
Document preview workspace.
Provides raw Markdown editing and rendered HTML preview in a clean macOS style.
"""
import markdown
from pygments.formatters import HtmlFormatter

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QPlainTextEdit,
    QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

from app.ui.icons import get_icon

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False


class PreviewPanel(QWidget):
    copyRequested = Signal()
    saveRequested = Signal()

    def __init__(self, colors: dict = None):
        super().__init__()
        self._colors = colors or {}
        self.setObjectName("PreviewFrame")
        self.current_markdown = ""
        self.current_filename = ""
        self._setup_ui()

    def update_theme(self, colors: dict):
        self._colors = colors
        self.setStyleSheet(f"""
            #PreviewFrame {{
                background-color: {colors['content_bg']};
                border-left: 1px solid {colors['separator']};
            }}
        """)
        self._update_web_preview()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"border-bottom: 1px solid {self._colors.get('separator', '#ddd')};")
        
        t_layout = QHBoxLayout(toolbar)
        t_layout.setContentsMargins(16, 0, 16, 0)
        
        self.title_lbl = QLabel("No document selected")
        font = self.title_lbl.font()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.DemiBold)
        self.title_lbl.setFont(font)
        self.title_lbl.setStyleSheet(f"color: {self._colors.get('primary_label', '#000')}; border: none;")
        
        # Segmented Control
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        seg_widget = QWidget()
        seg_layout = QHBoxLayout(seg_widget)
        seg_layout.setContentsMargins(0, 0, 0, 0)
        seg_layout.setSpacing(0)
        
        self.btn_md = QPushButton("Markdown")
        self.btn_md.setCheckable(True)
        self.btn_md.setChecked(True)
        self.btn_md.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.btn_prev = QPushButton("Preview")
        self.btn_prev.setCheckable(True)
        self.btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.btn_group.addButton(self.btn_md, 0)
        self.btn_group.addButton(self.btn_prev, 1)
        
        # For a truly native segmented control, Qt needs heavy QSS or Mac-specific calls.
        # We will use simple buttons for now, Mac styling makes them look okay.
        seg_layout.addWidget(self.btn_md)
        seg_layout.addWidget(self.btn_prev)
        
        self.btn_group.idClicked.connect(self._on_tab_changed)
        
        # Actions
        self.btn_copy = QPushButton("Copy")
        self.btn_copy.setIcon(get_icon("copy", self._colors.get('accent', '#007AFF'), 16))
        self.btn_copy.clicked.connect(self.copyRequested.emit)
        
        self.btn_save = QPushButton("Save…")
        self.btn_save.setIcon(get_icon("save", self._colors.get('accent', '#007AFF'), 16))
        self.btn_save.clicked.connect(self.saveRequested.emit)
        
        t_layout.addWidget(self.title_lbl)
        t_layout.addStretch()
        t_layout.addWidget(seg_widget)
        t_layout.addStretch()
        t_layout.addWidget(self.btn_copy)
        t_layout.addWidget(self.btn_save)
        
        layout.addWidget(toolbar)
        
        # Stack
        self.stack = QStackedWidget()
        
        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        
        self.stack.addWidget(self.editor)
        
        if HAS_WEBENGINE:
            self.web_view = QWebEngineView()
            self.stack.addWidget(self.web_view)
        else:
            fallback = QLabel("HTML Preview requires QtWebEngineWidgets.")
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack.addWidget(fallback)
            self.btn_prev.setEnabled(False)
            
        layout.addWidget(self.stack)

    def _on_tab_changed(self, idx: int):
        self.stack.setCurrentIndex(idx)
        if idx == 1:
            self._update_web_preview()

    def set_content(self, filename: str, md_text: str):
        self.current_filename = filename
        self.current_markdown = md_text
        self.title_lbl.setText(filename)
        self.editor.setPlainText(md_text)
        if self.stack.currentIndex() == 1:
            self._update_web_preview()

    def clear(self):
        self.current_filename = ""
        self.current_markdown = ""
        self.title_lbl.setText("No document selected")
        self.editor.clear()
        if HAS_WEBENGINE:
            self.web_view.setHtml("")

    def _update_web_preview(self):
        if not HAS_WEBENGINE or not self.current_markdown:
            return
            
        html_body = markdown.markdown(
            self.current_markdown,
            extensions=[
                "markdown.extensions.tables",
                "markdown.extensions.fenced_code",
                "markdown.extensions.nl2br",
                "markdown.extensions.sane_lists",
            ]
        )
        
        is_dark = self._colors.get('window_bg', '#FFF').upper() < '#AAA'
        bg_color = self._colors.get('content_bg', '#FFFFFF')
        text_color = self._colors.get('primary_label', '#000000')
        link_color = self._colors.get('accent', '#007AFF')
        border_color = self._colors.get('separator', '#E5E5EA')
        code_bg = self._colors.get('code_bg', '#F6F6F6')
        
        css = f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 15px;
            line-height: 1.6;
            color: {text_color};
            background-color: {bg_color};
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        a {{ color: {link_color}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid {border_color}; padding-bottom: .3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid {border_color}; padding-bottom: .3em; }}
        code {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            background-color: {code_bg};
            padding: 0.2em 0.4em;
            border-radius: 6px;
            font-size: 85%;
        }}
        pre {{
            background-color: {code_bg};
            padding: 16px;
            border-radius: 8px;
            overflow: auto;
        }}
        pre code {{ background-color: transparent; padding: 0; }}
        blockquote {{
            margin: 0;
            padding-left: 1em;
            color: {self._colors.get('secondary_label', '#666')};
            border-left: 4px solid {border_color};
        }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
        th, td {{ border: 1px solid {border_color}; padding: 8px 12px; }}
        th {{ background-color: {code_bg}; font-weight: 600; }}
        """
        
        full_html = f"<!DOCTYPE html><html><head><style>{css}</style></head><body>{html_body}</body></html>"
        self.web_view.setHtml(full_html)
