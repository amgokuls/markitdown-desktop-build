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
    win._conversion_mgr.file_finished.connect(lambda r: print(f"FINISHED: {r.input_file}, success={r.success}, md_len={len(r.markdown_content) if r.markdown_content else 'None'} error={r.error_message}"))
    
    win._on_convert()
    
    # Run event loop with a timeout to prevent hanging
    import threading
    def timeout():
        print("TIMEOUT")
        app.quit()
    
    t = threading.Timer(10.0, timeout)
    t.start()
    
    app.exec()
    t.cancel()
    print("Finished event loop.")

test_pipeline()
