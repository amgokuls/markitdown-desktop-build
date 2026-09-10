import re

with open('app/ui/main_window.py', 'r') as f:
    content = f.read()

# Add FileItem import if missing
if 'from app.conversion.models import FileItem' not in content:
    content = content.replace('from app.conversion.manager import ConversionManager', 'from app.conversion.manager import ConversionManager\nfrom app.conversion.models import FileItem')

# Fix _on_files_dropped
new_dropped = """    def _on_files_dropped(self, paths: list[Path]):
        items = []
        for p in paths:
            if p.is_file() and not p.name.startswith("."):
                items.append(FileItem(path=p))
        if items:
            self._drop_zone.hide()
            self._file_list.show()
            self._file_list.add_files(items)
            self._update_convert_button()"""

content = re.sub(r'    def _on_files_dropped\(self, paths: list\[Path\]\):\n.*?self\._update_convert_button\(\)', new_dropped, content, flags=re.DOTALL)

# Fix _on_convert
new_convert = """    def _on_convert(self):
        items = self._file_list.all_items()
        if not items:
            return
            
        self.act_convert.setVisible(False)
        self.convert_btn.hide()
        self.act_cancel.setEnabled(True)
        self.cancel_btn.show()
        
        self.act_add.setEnabled(False)
        self._conversion_mgr.convert_files(items)"""

content = re.sub(r'    def _on_convert\(self\):\n.*?self\._conversion_mgr\.convert_files\(.*?_str\)', new_convert, content, flags=re.DOTALL)

with open('app/ui/main_window.py', 'w') as f:
    f.write(content)
