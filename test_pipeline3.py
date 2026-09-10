import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def test_pipeline():
    app = QApplication(sys.argv)
    win = MainWindow()

    test_file = Path("tests/fixtures/sample.md")
    test_file.write_text("Hello World")
    
    print("Simulating drop...")
    win._on_files_dropped([test_file])
    
    print("Simulating convert...")
    win._conversion_mgr.all_finished.connect(lambda t, c: print(f"ALL FINISHED EVENT! {t}/{c}") or app.quit())
    win._conversion_mgr.file_finished.connect(lambda r: print(f"FINISHED: {r.input_file}, success={r.success}"))
    
    win._on_convert()
    
    import threading
    t = threading.Timer(10.0, lambda: print("TIMEOUT") or app.quit())
    t.start()
    
    app.exec()
    t.cancel()
    print("Finished event loop.")

test_pipeline()
