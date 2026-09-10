import re

with open('app/ui/main_window.py', 'r') as f:
    content = f.read()

if 'from app.conversion.models import HistoryEntry' not in content:
    content = content.replace('from app.conversion.models import FileItem', 'from app.conversion.models import FileItem, HistoryEntry')

new_finished = """    def _on_file_finished(self, result):
        path_str = str(result.input_file)
        self._file_list.update_file_status(path_str)
        
        # Update history
        entry = HistoryEntry(
            filename=result.display_name,
            path=str(result.input_file),
            success=result.success,
            duration_seconds=result.duration_seconds,
            converted_at=result.converted_at
        )
        self._history.add(entry)
        self._history_panel.prepend_entry(entry)
        
        # If this is the currently selected file in the UI, update preview
        if self._file_list.selected_path == path_str:
            self._on_file_selected(path_str)"""

content = re.sub(r'    def _on_file_finished\(self, result\):\n.*?self\._on_file_selected\(path_str\)', new_finished, content, flags=re.DOTALL)

with open('app/ui/main_window.py', 'w') as f:
    f.write(content)
