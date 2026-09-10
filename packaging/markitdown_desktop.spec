# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for MarkItDown Desktop.

Build with:
    pyinstaller packaging/markitdown_desktop.spec --noconfirm --clean
"""
import sys
from pathlib import Path

PROJECT_DIR = Path(SPECPATH).parent
APP_DIR = PROJECT_DIR / "app"
RESOURCES_DIR = PROJECT_DIR / "resources"
ICON_PATH = str(RESOURCES_DIR / "icons" / "AppIcon.icns")

# ------------------------------------------------------------------ #
# Data files to include
# ------------------------------------------------------------------ #
datas = [
    # Include resources directory
    (str(RESOURCES_DIR), "resources"),
]

# ------------------------------------------------------------------ #
# Hidden imports — MarkItDown uses entry_points / importlib for converters
# ------------------------------------------------------------------ #
hidden_imports = [
    # MarkItDown core
    "markitdown",
    "markitdown._markitdown",
    "markitdown.converters",
    "markitdown._base_converter",
    "markitdown._stream_info",
    "markitdown._uri_utils",
    "markitdown._exceptions",

    # MarkItDown converter dependencies
    "pdfminer",
    "pdfminer.high_level",
    "pdfminer.layout",
    "pdfminer.pdfpage",
    "pdfplumber",
    "mammoth",
    "python_pptx",
    "pptx",
    "openpyxl",
    "xlrd",
    "pandas",
    "pandas.io.formats.style",
    "lxml",
    "lxml.etree",
    "lxml._elementpath",
    "beautifulsoup4",
    "bs4",
    "bs4.builder._html5lib",
    "bs4.builder._lxml",
    "bs4.builder._htmlparser",
    "markdownify",
    "magika",
    "charset_normalizer",
    "defusedxml",
    "defusedxml.ElementTree",
    "olefile",
    "pydub",
    "speech_recognition",
    "youtube_transcript_api",
    "requests",
    "urllib3",
    "certifi",

    # PySide6
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtNetwork",

    # Markdown rendering
    "markdown",
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
    "markdown.extensions.toc",
    "pygments",
    "pygments.formatters.html",
    "pygments.lexers",

    # Standard library
    "importlib.metadata",
    "importlib.resources",
    "email.message",
    "zipfile",
    "csv",
    "json",
    "xml.etree.ElementTree",
]

# ------------------------------------------------------------------ #
# Excludes — reduce app size
# ------------------------------------------------------------------ #
excludes = [
    "tkinter",
    "test",
    "unittest",
    "PyQt5",
    "PyQt6",
    "wx",
    "gtk",
]

# ------------------------------------------------------------------ #
# Analysis
# ------------------------------------------------------------------ #
a = Analysis(
    [str(PROJECT_DIR / "app" / "main.py")],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=["packaging/hooks"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MarkItDown Desktop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,       # None = current arch; use "universal2" for fat binary
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="MarkItDown Desktop",
)

app = BUNDLE(
    coll,
    name="MarkItDown Desktop.app",
    icon=ICON_PATH if Path(ICON_PATH).exists() else None,
    bundle_identifier="com.markitdown-desktop.app",
    version="1.0.0",
    info_plist={
        "CFBundleDisplayName": "MarkItDown Desktop",
        "CFBundleName": "MarkItDown Desktop",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "CFBundleIdentifier": "com.markitdown-desktop.app",
        "CFBundleExecutable": "MarkItDown Desktop",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,  # Supports dark mode
        "NSHumanReadableCopyright": "© 2024 MarkItDown Desktop Contributors. MIT License.",
        # Drag-and-drop file support
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "PDF Document",
                "CFBundleTypeExtensions": ["pdf"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "Word Document",
                "CFBundleTypeExtensions": ["docx", "doc"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "PowerPoint Presentation",
                "CFBundleTypeExtensions": ["pptx", "ppt"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "Excel Spreadsheet",
                "CFBundleTypeExtensions": ["xlsx", "xls"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "HTML Document",
                "CFBundleTypeExtensions": ["html", "htm"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "CSV File",
                "CFBundleTypeExtensions": ["csv"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "JSON File",
                "CFBundleTypeExtensions": ["json"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "XML File",
                "CFBundleTypeExtensions": ["xml"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "ZIP Archive",
                "CFBundleTypeExtensions": ["zip"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "EPUB Book",
                "CFBundleTypeExtensions": ["epub"],
                "CFBundleTypeRole": "Viewer",
            },
        ],
        # Privacy (no network for local conversions)
        "NSAppTransportSecurity": {
            "NSAllowsArbitraryLoads": False,
        },
    },
)
