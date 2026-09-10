import re

with open('app/ui/main_window.py', 'r') as f:
    content = f.read()

# Replace the whole _on_file_finished function
def replace_func():
    lines = content.split('\n')
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('    def _on_file_finished(self, result):') or line.startswith('    def _on_file_finished(self, result: ConversionResult):'):
            start_idx = i
            break
            
    if start_idx == -1: return content
    
    end_idx = start_idx + 1
    while end_idx < len(lines) and (lines[end_idx].startswith('        ') or lines[end_idx].strip() == ''):
        end_idx += 1
        
    new_func = """    def _on_file_finished(self, result):
        path_str = str(result.input_file)
        self._file_list.update_file_status(path_str)
        
        # Build HistoryEntry
        from app.conversion.models import HistoryEntry
        entry = HistoryEntry(
            filename=result.display_name,
            path=str(result.input_file),
            success=result.success,
            duration_seconds=result.duration_seconds,
            converted_at=result.converted_at
        )
        
        # Update history
        self._history.add(entry)
        self._history_panel.prepend_entry(entry)
        
        # Update preview if selected
        if self._file_list.selected_path == path_str:
            self._on_file_selected(path_str)
"""
    return '\n'.join(lines[:start_idx]) + '\n' + new_func + '\n' + '\n'.join(lines[end_idx:])

content = replace_func()

with open('app/ui/main_window.py', 'w') as f:
    f.write(content)
