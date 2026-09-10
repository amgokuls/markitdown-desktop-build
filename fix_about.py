import re

with open('app/ui/about_dialog.py', 'r') as f:
    content = f.read()

new_btn_logs = """        btn_logs.clicked.connect(lambda: __import__("subprocess").run(["open", str(Path.home() / ".markitdown-desktop" / "logs")]))"""

content = re.sub(r'        btn_logs\.clicked\.connect\(lambda: FilesystemService\(self\)\.open_logs_folder\(\)\)', new_btn_logs, content)

with open('app/ui/about_dialog.py', 'w') as f:
    f.write(content)
