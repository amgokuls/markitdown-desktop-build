with open('app/ui/file_list.py', 'r') as f:
    content = f.read()

content = content.replace('class FileRowWidget(QFrame):\n    removeRequested = Signal(str)', 'class FileRowWidget(QFrame):\n    removeRequested = Signal(str)\n    clicked = Signal(str)')

with open('app/ui/file_list.py', 'w') as f:
    f.write(content)
