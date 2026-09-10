import sys, re

# Fix about_dialog.py
with open('app/ui/about_dialog.py', 'r') as f:
    content = f.read()

helper = """
def open_folder(path_str):
    import sys, subprocess, os
    if sys.platform == "win32":
        os.startfile(path_str)
    elif sys.platform == "darwin":
        subprocess.run(["open", path_str])
    else:
        subprocess.run(["xdg-open", path_str])
"""
if "def open_folder" not in content:
    content = content.replace("class AboutDialog(QDialog):", helper + "\nclass AboutDialog(QDialog):")

content = re.sub(r'__import__\("subprocess"\)\.run\(\["open", str\(Path\.home\(\) / "\.markitdown-desktop" / "logs"\)\]\)', 'open_folder(str(Path.home() / ".markitdown-desktop" / "logs"))', content)

with open('app/ui/about_dialog.py', 'w') as f:
    f.write(content)

