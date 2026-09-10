import re

with open('app/ui/file_list.py', 'r') as f:
    content = f.read()

if 'def get_item(self, path_str: str) -> FileItem:' not in content:
    content = content.replace('    def all_items(self) -> list[FileItem]:', '    def get_item(self, path_str: str):\n        row = self._rows.get(path_str)\n        return row.item if row else None\n\n    def all_items(self) -> list[FileItem]:')

with open('app/ui/file_list.py', 'w') as f:
    f.write(content)

with open('app/ui/main_window.py', 'r') as f:
    content2 = f.read()

content2 = content2.replace('item = self._conversion_mgr._items.get(path_str)', 'item = self._file_list.get_item(path_str)')
with open('app/ui/main_window.py', 'w') as f:
    f.write(content2)
