import re

with open('app/ui/main_window.py', 'r') as f:
    content = f.read()

new_save_method = """    def _on_save_markdown(self):
        md = self._preview_panel.current_markdown
        if md:
            path = self._fs.save_markdown(self, self._preview_panel.current_filename)
            if path:
                self._fs.write_markdown(path, md)"""

content = re.sub(r'    def _on_save_markdown\(self\):\n.*?self\._fs\.save_markdown\(.*?\)', new_save_method, content, flags=re.DOTALL)

with open('app/ui/main_window.py', 'w') as f:
    f.write(content)
