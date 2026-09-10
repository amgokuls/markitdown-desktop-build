import re

with open('app/ui/history.py', 'r') as f:
    content = f.read()

new_prepend = """    def prepend_entry(self, entry: HistoryEntry):
        self._add_row(entry, append=False)"""

content = re.sub(r'    def prepend_entry\(self, result\):\n.*?(?=\n\n|\Z)', new_prepend, content, flags=re.DOTALL)

with open('app/ui/history.py', 'w') as f:
    f.write(content)
