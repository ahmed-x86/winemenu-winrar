import os
import subprocess
import re
import gi
import urllib.parse

try:
    gi.require_version('Thunarx', '3.0')
except ValueError:
    pass

from gi.repository import GObject, Thunarx

class WinRARMenuProvider(GObject.GObject, Thunarx.MenuProvider):
    def __init__(self):
        super().__init__()
        self.valid_exts = {'.001', '.7z', '.arj', '.bz', '.bz2', '.cab', '.gz', '.iso', '.jar', '.lha', '.lz', '.lzh', '.rar', '.tar', '.taz', '.tbz', '.tbz2', '.tgz', '.tlz', '.txz', '.tzst', '.uu', '.uue', '.xxe', '.xz', '.z', '.zip', '.zipx', '.zst'}
        
        self.extract_actions = [
            {'name': 'Extract Here', 'id': 'EXTRACT_HERE'}, 
            {'name': 'Extract to...', 'id': 'EXTRACT_TO'}, 
            {'name': 'Extract files...', 'id': 'EXTRACT_DIALOG'}, 
            {'name': 'Open with WinRAR', 'id': 'OPEN'}
        ]

    def get_file_menu_items(self, window, files):
        if not files:
            return []

        has_archives = True
        for file in files:
            if file.is_directory():
                has_archives = False
                break
            
            filename = file.get_name()
            ext = os.path.splitext(filename)[1].lower()
            
            if '*' not in self.valid_exts and ext not in self.valid_exts and not re.search(r'\.(r\d+|z\d+|part\d+\.rar)$', filename.lower()):
                has_archives = False
                break

        items = []
        first_name = files[0].get_name()
        
        compress_actions = [
            {'name': f'Add to "{first_name}.rar"', 'id': 'COMPRESS_QUICK'},
            {'name': 'Add to archive...', 'id': 'COMPRESS_DIALOG'}
        ]

        # إضافة خيارات الضغط
        for action in compress_actions:
            item = Thunarx.MenuItem(
                name=f"WinRARAction::{action['id']}", 
                label=f"WinRAR: {action['name']}", 
                tooltip=f"WinRAR {action['name']}", 
                icon=""
            )
            item.connect('activate', self.execute_wine_app, files, action['id'])
            items.append(item)

        # إضافة خيارات فك الضغط إذا كانت الملفات أرشيفات فقط
        if has_archives:
            for action in self.extract_actions:
                item = Thunarx.MenuItem(
                    name=f"WinRARAction::{action['id']}", 
                    label=f"WinRAR: {action['name']}", 
                    tooltip=f"WinRAR {action['name']}", 
                    icon=""
                )
                item.connect('activate', self.execute_wine_app, files, action['id'])
                items.append(item)

        return items

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

    def execute_wine_app(self, menu, files, action_id):
        winrar_exe = os.path.expanduser('~/.wine/drive_c/Program Files/WinRAR/WinRAR.exe')

        if action_id.startswith('COMPRESS'):
            first_file = files[0]
            uri = first_file.get_uri()
            if not uri.startswith('file://'):
                return
            first_linux_filepath = urllib.parse.unquote(uri[7:])
            working_dir = os.path.dirname(first_linux_filepath)
            first_name = first_file.get_name()
            
            if action_id == 'COMPRESS_QUICK':
                archive_name = first_name + '.rar'
                archive_linux_path = os.path.join(working_dir, archive_name)
            elif action_id == 'COMPRESS_DIALOG':
                try:
                    archive_linux_path = subprocess.check_output(
                        ['zenity', '--file-selection', '--save', '--confirm-overwrite', f'--filename={os.path.join(working_dir, first_name + ".rar")}', '--title=Save Archive As...'],
                        stderr=subprocess.DEVNULL
                    ).decode('utf-8').strip()
                    if not archive_linux_path:
                        return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return

            try:
                archive_win_path = subprocess.check_output(
                    ['winepath', '-w', archive_linux_path],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
            except subprocess.CalledProcessError:
                archive_win_path = archive_linux_path

            final_cmd = ['wine', winrar_exe, 'a', archive_win_path]
            
            for file in files:
                final_cmd.append(file.get_name())

            subprocess.Popen(
                final_cmd, 
                cwd=working_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return

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
                if not dest_linux_path: return
                dest_win_path = subprocess.check_output(
                    ['winepath', '-w', dest_linux_path],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                return

        for file in files_to_process:
            uri = file.get_uri()
            if not uri.startswith('file://'): continue
            linux_filepath = urllib.parse.unquote(uri[7:])
            
            try:
                win_filepath = subprocess.check_output(
                    ['winepath', '-w', linux_filepath],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
            except subprocess.CalledProcessError:
                win_filepath = linux_filepath

            working_dir = os.path.dirname(linux_filepath)
            final_cmd = ['wine', winrar_exe]
            
            if action_id == 'EXTRACT_HERE': final_cmd.extend(['x', win_filepath])
            elif action_id == 'EXTRACT_TO': final_cmd.extend(['x', '-ad', win_filepath])
            elif action_id == 'EXTRACT_DIALOG': final_cmd.extend(['x', win_filepath, dest_win_path + '\\'])
            elif action_id == 'OPEN': final_cmd.append(win_filepath)

            subprocess.Popen(
                final_cmd, 
                cwd=working_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )