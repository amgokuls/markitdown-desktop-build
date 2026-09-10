"""
Minimal UI smoke tests using pytest-qt.
Validates widget creation and basic interactions without a real display.
"""
from __future__ import annotations

from pathlib import Path

import pytest

try:
    from PySide6.QtWidgets import QApplication
    HAS_QT = True
except ImportError:
    HAS_QT = False

pytestmark = pytest.mark.skipif(not HAS_QT, reason="PySide6 not available")


@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for the test session."""
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


class TestDropZone:

    def test_instantiation(self, qapp):
        from app.ui.drop_zone import DropZone
        zone = DropZone()
        assert zone is not None
        assert zone.minimumHeight() > 0

    def test_accepts_drops(self, qapp):
        from app.ui.drop_zone import DropZone
        zone = DropZone()
        assert zone.acceptDrops()


class TestFileListWidget:

    def test_instantiation(self, qapp):
        from app.ui.file_list import FileListWidget
        widget = FileListWidget()
        assert widget is not None
        assert widget.is_empty()

    def test_add_files(self, qapp, tmp_path):
        from app.ui.file_list import FileListWidget
        from app.conversion.models import FileItem

        widget = FileListWidget()
        path = tmp_path / "test.pdf"
        path.touch()
        items = [FileItem(path=path)]
        widget.add_files(items)

        assert not widget.is_empty()
        assert str(path) in widget.all_paths()

    def test_remove_file(self, qapp, tmp_path):
        from app.ui.file_list import FileListWidget
        from app.conversion.models import FileItem

        widget = FileListWidget()
        path = tmp_path / "test.csv"
        path.touch()
        item = FileItem(path=path)
        widget.add_files([item])
        widget.remove_file(str(path))

        assert widget.is_empty()

    def test_clear_all(self, qapp, tmp_path):
        from app.ui.file_list import FileListWidget
        from app.conversion.models import FileItem

        widget = FileListWidget()
        for name in ["a.pdf", "b.docx", "c.xlsx"]:
            p = tmp_path / name
            p.touch()
            widget.add_files([FileItem(path=p)])

        widget.clear_all()
        assert widget.is_empty()


class TestPreviewPanel:

    def test_instantiation(self, qapp):
        from app.ui.preview import PreviewPanel
        panel = PreviewPanel()
        assert panel is not None

    def test_set_content(self, qapp):
        from app.ui.preview import PreviewPanel
        panel = PreviewPanel()
        panel.set_content("test.pdf", "# Hello\n\nWorld")
        assert panel.current_markdown == "# Hello\n\nWorld"
        assert panel.current_filename == "test.pdf"

    def test_clear(self, qapp):
        from app.ui.preview import PreviewPanel
        panel = PreviewPanel()
        panel.set_content("f.md", "content")
        panel.clear()
        assert panel.current_markdown == ""


class TestStylesheet:

    def test_dark_stylesheet_generation(self):
        from app.ui.styles import get_stylesheet, Theme
        css = get_stylesheet(Theme.DARK)
        assert "background-color" in css
        assert len(css) > 100

    def test_light_stylesheet_generation(self):
        from app.ui.styles import get_stylesheet, Theme
        css = get_stylesheet(Theme.LIGHT)
        assert "background-color" in css
        assert len(css) > 100
