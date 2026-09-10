"""
Test fixtures — generates sample files for conversion testing.

Run this script once to generate the fixture files:
    python tests/fixtures/generate_fixtures.py
"""
from pathlib import Path
import json
import csv
import io
import struct
import zlib

FIXTURES_DIR = Path(__file__).parent


def make_html():
    content = """<!DOCTYPE html>
<html>
<head><title>Sample HTML Document</title></head>
<body>
<h1>Sample Document</h1>
<p>This is a <strong>sample HTML</strong> document for testing MarkItDown conversion.</p>
<h2>Features</h2>
<ul>
  <li>Headings</li>
  <li>Paragraphs</li>
  <li>Lists</li>
  <li>Tables</li>
</ul>
<h2>Data Table</h2>
<table>
  <tr><th>Name</th><th>Value</th></tr>
  <tr><td>Alpha</td><td>100</td></tr>
  <tr><td>Beta</td><td>200</td></tr>
</table>
</body>
</html>"""
    (FIXTURES_DIR / "sample.html").write_text(content, encoding="utf-8")
    print("✓ sample.html")


def make_csv():
    rows = [
        ["Name", "Department", "Salary", "Start Date"],
        ["Alice Johnson", "Engineering", "95000", "2021-01-15"],
        ["Bob Smith", "Marketing", "72000", "2020-06-01"],
        ["Carol White", "Design", "80000", "2022-03-10"],
        ["Dave Brown", "Engineering", "105000", "2019-08-22"],
    ]
    with open(FIXTURES_DIR / "sample.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("✓ sample.csv")


def make_json():
    data = {
        "title": "Sample JSON Document",
        "version": "1.0.0",
        "description": "A sample JSON file for testing MarkItDown conversion",
        "metadata": {
            "author": "Test Fixture",
            "created": "2024-01-01",
            "tags": ["test", "sample", "markitdown"]
        },
        "items": [
            {"id": 1, "name": "Widget A", "price": 9.99, "in_stock": True},
            {"id": 2, "name": "Widget B", "price": 24.99, "in_stock": False},
            {"id": 3, "name": "Widget C", "price": 4.99, "in_stock": True},
        ]
    }
    (FIXTURES_DIR / "sample.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    print("✓ sample.json")


def make_xml():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
  <book id="bk001">
    <title>The Great Conversion</title>
    <author>A. Test Author</author>
    <genre>Fiction</genre>
    <price>14.99</price>
    <description>A gripping tale about document conversion.</description>
  </book>
  <book id="bk002">
    <title>Markdown Mastery</title>
    <author>B. Writer</author>
    <genre>Technical</genre>
    <price>29.99</price>
    <description>Everything you need to know about Markdown.</description>
  </book>
</catalog>"""
    (FIXTURES_DIR / "sample.xml").write_text(content, encoding="utf-8")
    print("✓ sample.xml")


def make_txt():
    content = """# Sample Text Document

This is a plain text document used for testing MarkItDown conversion.

## Section One

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section Two

- Item one
- Item two
- Item three

## Section Three

The quick brown fox jumps over the lazy dog.
Pack my box with five dozen liquor jugs.
"""
    (FIXTURES_DIR / "sample.txt").write_text(content, encoding="utf-8")
    print("✓ sample.txt")


def make_minimal_pdf():
    """Generate a minimal valid PDF with readable text for testing."""
    # This is a minimal hand-crafted PDF with a text page
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 120>>
stream
BT
/F1 18 Tf
72 720 Td
(Sample PDF Document) Tj
0 -30 Td
/F1 12 Tf
(This is a sample PDF file for testing MarkItDown conversion.) Tj
0 -20 Td
(It contains basic text content.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
489
%%EOF"""
    (FIXTURES_DIR / "sample.pdf").write_bytes(pdf_content)
    print("✓ sample.pdf")


def make_zip(tmp=FIXTURES_DIR):
    """Generate a ZIP containing a text file."""
    import zipfile
    zip_path = FIXTURES_DIR / "sample.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("readme.txt", "# ZIP Contents\n\nThis is a file inside the ZIP archive.\n")
        zf.writestr("data.csv", "Name,Value\nA,1\nB,2\n")
    print("✓ sample.zip")


if __name__ == "__main__":
    print(f"Generating fixtures in {FIXTURES_DIR}")
    make_html()
    make_csv()
    make_json()
    make_xml()
    make_txt()
    make_minimal_pdf()
    make_zip()
    print("\nAll fixtures generated.")
