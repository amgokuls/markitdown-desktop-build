"""
Centralized macOS semantic tokens and basic stylesheet for MarkItDown Desktop.
Relies on native Qt styles for macOS, only gently guiding the appearance.
"""
from enum import Enum
from PySide6.QtGui import QPalette, QColor

class Theme(Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"

# Semantic macOS-like Colors
LIGHT_TOKENS = {
    "window_bg": "#ECECEC",
    "sidebar_bg": "#F6F6F6",
    "content_bg": "#FFFFFF",
    "primary_label": "#000000",
    "secondary_label": "#666666",
    "separator": "#D1D1D6",
    "accent": "#007AFF",
    "accent_text": "#FFFFFF",
    "hover": "#E5E5EA",
    "success": "#34C759",
    "destructive": "#FF3B30",
    "border": "#D1D1D6",
    "toolbar_bg": "#EAEAEA",
    "code_bg": "#F6F6F6",
}

DARK_TOKENS = {
    "window_bg": "#282828",
    "sidebar_bg": "#1E1E1E",
    "content_bg": "#1E1E1E",
    "primary_label": "#FFFFFF",
    "secondary_label": "#98989D",
    "separator": "#3A3A3C",
    "accent": "#0A84FF",
    "accent_text": "#FFFFFF",
    "hover": "#3A3A3C",
    "success": "#32D74B",
    "destructive": "#FF453A",
    "border": "#3A3A3C",
    "toolbar_bg": "#282828",
    "code_bg": "#1E1E1E",
}

def get_colors(theme: Theme) -> dict:
    # Basic detection for 'system' could be added, but for now
    # default SYSTEM to Light if we can't reliably detect, though PySide6
    # often handles the QPalette natively. The app Settings model passes actual Theme.
    if theme == Theme.DARK:
        return DARK_TOKENS
    elif theme == Theme.LIGHT:
        return LIGHT_TOKENS
    else:
        # Better fallback: attempt to read QPalette window color
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            lightness = app.palette().color(QPalette.ColorRole.Window).lightness()
            return DARK_TOKENS if lightness < 128 else LIGHT_TOKENS
        return LIGHT_TOKENS

def get_stylesheet(theme: Theme) -> str:
    """Returns a minimal QSS string for structural components."""
    colors = get_colors(theme)
    
    return f"""
    QMainWindow {{
        background-color: {colors['window_bg']};
    }}
    
    QSplitter::handle {{
        background-color: {colors['separator']};
    }}
    
    /* Sidebars and List Views */
    QListWidget {{
        background-color: transparent;
        border: none;
    }}
    QListWidget::item {{
        border-radius: 6px;
        margin: 2px 12px;
        padding: 4px;
        color: {colors['primary_label']};
    }}
    QListWidget::item:hover {{
        background-color: {colors['hover']};
    }}
    QListWidget::item:selected {{
        background-color: {colors['accent']};
        color: {colors['accent_text']};
    }}
    
    /* Clean Text Areas */
    QPlainTextEdit {{
        background-color: {colors['content_bg']};
        color: {colors['primary_label']};
        border: none;
        selection-background-color: {colors['accent']};
        selection-color: {colors['accent_text']};
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 13pt;
        padding: 12px;
    }}
    
    /* Scroll Areas */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {colors['separator']};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* Dialogs */
    QDialog {{
        background-color: {colors['window_bg']};
    }}
    
    /* Minimal specific overrides */
    #SidebarFrame {{
        background-color: {colors['sidebar_bg']};
        border-right: 1px solid {colors['separator']};
    }}
    
    #PreviewFrame {{
        background-color: {colors['content_bg']};
        border-left: 1px solid {colors['separator']};
    }}
    
    #ToolbarFrame {{
        background-color: {colors['toolbar_bg']};
        border-bottom: 1px solid {colors['separator']};
    }}
    """
