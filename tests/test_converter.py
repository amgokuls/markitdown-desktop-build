"""
Tests for the MarkItDown conversion layer.

Tests the converter adapter and manager in isolation.
"""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Use fixtures directory relative to this file
FIXTURES = Path(__file__).parent / "fixtures"


# ================================================================== #
# MarkItDownConverter tests
# ================================================================== #

class TestMarkItDownConverter:

    def test_convert_file_success(self, tmp_path):
        """Converter returns success result for a plain text file."""
        from app.conversion.converter import MarkItDownConverter

        test_file = tmp_path / "hello.txt"
        test_file.write_text("# Hello\nThis is a test.", encoding="utf-8")

        converter = MarkItDownConverter()
        result = converter.convert_file(test_file)

        assert result.success is True
        assert result.input_file == test_file
        assert isinstance(result.markdown, str)
        assert len(result.markdown) > 0
        assert result.duration_seconds >= 0

    def test_convert_nonexistent_file(self, tmp_path):
        """Converter returns failure for a file that does not exist."""
        from app.conversion.converter import MarkItDownConverter

        converter = MarkItDownConverter()
        result = converter.convert_file(tmp_path / "ghost.pdf")

        assert result.success is False
        assert "not found" in result.error_message.lower() or "file" in result.error_message.lower()

    def test_convert_directory_path(self, tmp_path):
        """Converter returns failure for a directory path."""
        from app.conversion.converter import MarkItDownConverter

        converter = MarkItDownConverter()
        result = converter.convert_file(tmp_path)

        assert result.success is False

    def test_convert_html_file(self, tmp_path):
        """HTML files can be converted."""
        from app.conversion.converter import MarkItDownConverter

        html_file = tmp_path / "page.html"
        html_file.write_text(
            "<html><body><h1>Title</h1><p>Body text.</p></body></html>",
            encoding="utf-8",
        )

        converter = MarkItDownConverter()
        result = converter.convert_file(html_file)

        assert result.success is True
        assert "Title" in result.markdown

    def test_convert_csv_file(self, tmp_path):
        """CSV files can be converted to Markdown tables."""
        from app.conversion.converter import MarkItDownConverter

        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Name,Value\nAlice,100\nBob,200\n", encoding="utf-8")

        converter = MarkItDownConverter()
        result = converter.convert_file(csv_file)

        assert result.success is True
        assert "Name" in result.markdown or "Alice" in result.markdown

    def test_convert_json_file(self, tmp_path):
        """JSON files can be converted."""
        from app.conversion.converter import MarkItDownConverter

        json_file = tmp_path / "data.json"
        json_file.write_text('{"key": "value", "number": 42}', encoding="utf-8")

        converter = MarkItDownConverter()
        result = converter.convert_file(json_file)

        assert result.success is True
        assert len(result.markdown) > 0

    def test_convert_xml_file(self, tmp_path):
        """XML files can be converted."""
        from app.conversion.converter import MarkItDownConverter

        xml_file = tmp_path / "data.xml"
        xml_file.write_text(
            "<?xml version='1.0'?><root><item>Hello</item></root>",
            encoding="utf-8",
        )

        converter = MarkItDownConverter()
        result = converter.convert_file(xml_file)

        assert result.success is True

    def test_markitdown_version(self):
        """Version string is available."""
        from app.conversion.converter import MarkItDownConverter

        converter = MarkItDownConverter()
        version = converter.markitdown_version
        assert isinstance(version, str)
        assert len(version) > 0

    def test_convert_fixtures_pdf(self):
        """Convert sample PDF fixture (if available)."""
        from app.conversion.converter import MarkItDownConverter

        pdf = FIXTURES / "sample.pdf"
        if not pdf.exists():
            pytest.skip("sample.pdf fixture not found")

        converter = MarkItDownConverter()
        result = converter.convert_file(pdf)
        assert result.success is True
        assert len(result.markdown) > 0

    def test_convert_fixtures_docx(self):
        """Convert sample DOCX fixture (if available)."""
        from app.conversion.converter import MarkItDownConverter

        docx = FIXTURES / "sample.docx"
        if not docx.exists():
            pytest.skip("sample.docx fixture not found")

        converter = MarkItDownConverter()
        result = converter.convert_file(docx)
        assert result.success is True

    def test_convert_fixtures_xlsx(self):
        """Convert sample XLSX fixture (if available)."""
        from app.conversion.converter import MarkItDownConverter

        xlsx = FIXTURES / "sample.xlsx"
        if not xlsx.exists():
            pytest.skip("sample.xlsx fixture not found")

        converter = MarkItDownConverter()
        result = converter.convert_file(xlsx)
        assert result.success is True

    def test_convert_fixtures_pptx(self):
        """Convert sample PPTX fixture (if available)."""
        from app.conversion.converter import MarkItDownConverter

        pptx = FIXTURES / "sample.pptx"
        if not pptx.exists():
            pytest.skip("sample.pptx fixture not found")

        converter = MarkItDownConverter()
        result = converter.convert_file(pptx)
        assert result.success is True


# ================================================================== #
# ConversionResult tests
# ================================================================== #

class TestConversionResult:

    def test_display_name(self, tmp_path):
        from app.conversion.models import ConversionResult

        result = ConversionResult(
            input_file=tmp_path / "report.pdf",
            success=True,
            markdown="# Report",
        )
        assert result.display_name == "report.pdf"

    def test_suggested_output_name(self, tmp_path):
        from app.conversion.models import ConversionResult

        result = ConversionResult(
            input_file=tmp_path / "my document.docx",
            success=True,
            markdown="# Doc",
        )
        assert result.suggested_output_name == "my document.md"


# ================================================================== #
# Exception wrapper tests
# ================================================================== #

class TestExceptionWrapper:

    def test_wraps_import_error(self):
        from app.conversion.exceptions import wrap_markitdown_exception, MissingDependencyError

        exc = ImportError("No module named 'some_dep'")
        wrapped = wrap_markitdown_exception(exc, "test.docx")
        assert isinstance(wrapped, MissingDependencyError)

    def test_wraps_permission_error(self):
        from app.conversion.exceptions import wrap_markitdown_exception

        exc = PermissionError("Permission denied")
        wrapped = wrap_markitdown_exception(exc, "secret.pdf")
        assert "permission" in wrapped.message.lower() or "secret.pdf" in wrapped.message

    def test_wraps_generic_exception(self):
        from app.conversion.exceptions import wrap_markitdown_exception, ConversionFailedError

        exc = RuntimeError("Something broke")
        wrapped = wrap_markitdown_exception(exc, "file.pdf")
        assert isinstance(wrapped, ConversionFailedError)
        assert "file.pdf" in wrapped.message


# ================================================================== #
# FileItem tests
# ================================================================== #

class TestFileItem:

    def test_display_name(self, tmp_path):
        from app.conversion.models import FileItem

        path = tmp_path / "my_document.pdf"
        path.touch()
        item = FileItem(path=path)
        assert item.display_name == "my_document.pdf"

    def test_extension(self, tmp_path):
        from app.conversion.models import FileItem

        path = tmp_path / "report.PDF"
        path.touch()
        item = FileItem(path=path)
        assert item.extension == "PDF"

    def test_file_size_str(self, tmp_path):
        from app.conversion.models import FileItem

        path = tmp_path / "test.txt"
        path.write_bytes(b"x" * 1024)
        item = FileItem(path=path)
        assert "KB" in item.file_size_str or "B" in item.file_size_str
