import re

with open('app/ui/file_list.py', 'r') as f:
    content = f.read()

# Add signal to FileRowWidget
if 'clicked = Signal(str)' not in content:
    content = content.replace('class FileRowWidget(QWidget):', 'class FileRowWidget(QWidget):\n    clicked = Signal(str)')

# Add mouse release event to FileRowWidget
new_mouse = """    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(str(self.item.path))
        super().mouseReleaseEvent(event)"""

if 'def mouseReleaseEvent' not in content:
    content = content.replace('    def update_status(self):', new_mouse + '\n\n    def update_status(self):')

# Add signal to FileListWidget
if 'fileSelected = Signal(str)' not in content:
    content = content.replace('class FileListWidget(QWidget):', 'class FileListWidget(QWidget):\n    fileSelected = Signal(str)')

# Connect it in add_files
if 'row.clicked.connect' not in content:
    content = content.replace('row.removeRequested.connect(self._on_remove)', 'row.removeRequested.connect(self._on_remove)\n            row.clicked.connect(self.fileSelected.emit)')

with open('app/ui/file_list.py', 'w') as f:
    f.write(content)

with open('app/ui/main_window.py', 'r') as f:
    content2 = f.read()

# Connect in MainWindow._setup_ui
if 'self._file_list.fileSelected.connect' not in content2:
    content2 = content2.replace('self._file_list.fileRemoved.connect(self._update_convert_button)', 'self._file_list.fileRemoved.connect(self._update_convert_button)\n        self._file_list.fileSelected.connect(self._on_file_selected)')

# Add _on_file_selected
new_selected = """    def _on_file_selected(self, path_str: str):
        item = self._conversion_mgr._items.get(path_str)
        if item and item.result and item.result.success:
            self._preview_panel.set_content(item.result.display_name, item.result.markdown)
            
    def _on_file_finished"""
content2 = re.sub(r'    def _on_file_finished', new_selected, content2)

with open('app/ui/main_window.py', 'w') as f:
    f.write(content2)
