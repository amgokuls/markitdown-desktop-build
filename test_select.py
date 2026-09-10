import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

app = QApplication(sys.argv)
win = MainWindow()

test_file = Path("tests/fixtures/sample.md")
test_file.touch()
print("Simulating drop...")
win._on_files_dropped([test_file])
print(f"File list visible: {win._file_list.isVisible()}")
print(f"Number of rows: {len(win._file_list._rows)}")

print("Simulating convert...")
win._on_convert()
print("Conversion triggered.")
sys.exit(0)
