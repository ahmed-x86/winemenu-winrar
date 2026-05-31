import os
import subprocess
import re
import gi

try:
    gi.require_version('Nautilus', '4.0')
except ValueError:
    gi.require_version('Nautilus', '4.1')

from gi.repository import GObject, Nautilus

class WinRARMenuProvider(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        self.valid_exts = {'.001', '.7z', '.arj', '.bz', '.bz2', '.cab', '.gz', '.iso', '.jar', '.lha', '.lz', '.lzh', '.rar', '.tar', '.taz', '.tbz', '.tbz2', '.tgz', '.tlz', '.txz', '.tzst', '.uu', '.uue', '.xxe', '.xz', '.z', '.zip', '.zipx', '.zst'}
        
        self.actions = [
            {'name': 'Extract Here', 'id': 'EXTRACT_HERE'}, 
            {'name': 'Extract to...', 'id': 'EXTRACT_TO'}, 
            {'name': 'Extract files...', 'id': 'EXTRACT_DIALOG'}, 
            {'name': 'Open with WinRAR', 'id': 'OPEN'}
        ]

    def get_file_items(self, *args):
        files = args[-1]
        if not files:
            return []

        for file in files:
            if file.is_directory():
                return []
            
            filename = file.get_name()
            ext = os.path.splitext(filename)[1].lower()
            
            if '*' not in self.valid_exts and ext not in self.valid_exts and not re.search(r'\.(r\d+|z\d+|part\d+\.rar)$', filename.lower()):
                return []

        main_item = Nautilus.MenuItem(name='WineMenu::WinRAR', label='WinRAR')
        main_submenu = Nautilus.Menu()
        main_item.set_submenu(main_submenu)

        for idx, action in enumerate(self.actions):
            item = Nautilus.MenuItem(name=f"WinRARAction::{action['id']}", label=action['name'])
            item.connect('activate', self.execute_wine_app, files, action['id'])
            main_submenu.append_item(item)

        return [main_item]

    def get_base_archive_name(self, filename):
        name = re.sub(r'\.part\d+\.rar$', '.rar', filename, flags=re.IGNORECASE)
        if name != filename: return name
        
        name = re.sub(r'\.\d{3}$', '', filename)
        if name != filename: return name
        
        name = re.sub(r'\.r\d+$', '.rar', filename, flags=re.IGNORECASE)
        if name != filename: return name
        
        name = re.sub(r'\.z\d+$', '.zip', filename, flags=re.IGNORECASE)
        if name != filename: return name

        return filename

    def sort_files_priority(self, file):
        name = file.get_name().lower()
        if name.endswith('.rar') and not re.search(r'\.part\d+\.rar$', name):
            return 0
        if re.search(r'\.(001|part0*1\.rar)$', name):
            return 1
        return 2

    # التنفيذ المباشر (مثل الكود القديم) بدون Threading
    def execute_wine_app(self, menu, files, action_id):
        processed_bases = set()
        files_to_process = []
        
        sorted_files = sorted(files, key=self.sort_files_priority)
        
        for file in sorted_files:
            filename = file.get_name()
            base_name = self.get_base_archive_name(filename)
            
            if base_name not in processed_bases:
                processed_bases.add(base_name)
                files_to_process.append(file)

        dest_win_path = ""
        if action_id == 'EXTRACT_DIALOG':
            try:
                dest_linux_path = subprocess.check_output(
                    ['zenity', '--file-selection', '--directory', '--title=Select Extraction Destination'],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
                
                if not dest_linux_path:
                    return
                
                dest_win_path = subprocess.check_output(
                    ['winepath', '-w', dest_linux_path],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                return

        for file in files_to_process:
            linux_filepath = file.get_location().get_path()
            if not linux_filepath:
                continue
            
            try:
                win_filepath = subprocess.check_output(
                    ['winepath', '-w', linux_filepath],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
            except subprocess.CalledProcessError:
                win_filepath = linux_filepath

            working_dir = os.path.dirname(linux_filepath)
            winrar_exe = os.path.expanduser('~/.wine/drive_c/Program Files/WinRAR/WinRAR.exe')
            
            final_cmd = ['wine', winrar_exe]
            
            if action_id == 'EXTRACT_HERE':
                final_cmd.extend(['x', win_filepath])
            elif action_id == 'EXTRACT_TO':
                final_cmd.extend(['x', '-ad', win_filepath])
            elif action_id == 'EXTRACT_DIALOG':
                final_cmd.extend(['x', win_filepath, dest_win_path + '\\'])
            elif action_id == 'OPEN':
                final_cmd.append(win_filepath)

            subprocess.Popen(
                final_cmd, 
                cwd=working_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )