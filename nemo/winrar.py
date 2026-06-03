import os
import subprocess
import re
import gi
import urllib.parse

try:
    gi.require_version('Nemo', '3.0')
except ValueError:
    pass

from gi.repository import GObject, Nemo

class WinRARMenuProvider(GObject.GObject, Nemo.MenuProvider):
    def __init__(self):
        super().__init__()
        self.valid_exts = {'.001', '.7z', '.arj', '.bz', '.bz2', '.cab', '.gz', '.iso', '.jar', '.lha', '.lz', '.lzh', '.rar', '.tar', '.taz', '.tbz', '.tbz2', '.tgz', '.tlz', '.txz', '.tzst', '.uu', '.uue', '.xxe', '.xz', '.z', '.zip', '.zipx', '.zst'}
        
        self.extract_actions = [
            {'name': 'Extract Here', 'id': 'EXTRACT_HERE'}, 
            {'name': 'Extract to...', 'id': 'EXTRACT_TO'}, 
            {'name': 'Extract files...', 'id': 'EXTRACT_DIALOG'}, 
            {'name': 'Open with WinRAR', 'id': 'OPEN'}
        ]

    def get_file_items(self, window, files):
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
        main_item = Nemo.MenuItem(name='NemoMenu::WinRAR', label='WinRAR', tip='WinRAR Options', icon='')
        main_submenu = Nemo.Menu()
        main_item.set_submenu(main_submenu)

        first_name = files[0].get_name()
        compress_actions = [
            {'name': f'Add to "{first_name}.rar"', 'id': 'COMPRESS_QUICK'},
            {'name': 'Add to archive...', 'id': 'COMPRESS_DIALOG'}
        ]

        for action in compress_actions:
            item = Nemo.MenuItem(name=f"WinRARAction::{action['id']}", label=action['name'], tip='', icon='')
            item.connect('activate', self.execute_wine_app, files, action['id'])
            main_submenu.append_item(item)

        if has_archives:
            for action in self.extract_actions:
                item = Nemo.MenuItem(name=f"WinRARAction::{action['id']}", label=action['name'], tip='', icon='')
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

    def get_linux_path(self, file):
        uri = file.get_uri()
        if uri.startswith('file://'):
            return urllib.parse.unquote(uri[7:])
        return file.get_location().get_path()

    def execute_wine_app(self, menu, files, action_id):
        winrar_exe = os.path.expanduser('~/.wine/drive_c/Program Files/WinRAR/WinRAR.exe')

        if action_id.startswith('COMPRESS'):
            first_linux_path = self.get_linux_path(files[0])
            working_dir = os.path.dirname(first_linux_path)
            first_name = files[0].get_name()
            
            files_to_compress = []
            for file in files:
                linux_path = self.get_linux_path(file)
                try:
                    win_path = subprocess.check_output(['winepath', '-w', linux_path], stderr=subprocess.DEVNULL).decode('utf-8').strip()
                    files_to_compress.append(win_path)
                except subprocess.CalledProcessError:
                    files_to_compress.append(linux_path)

            if action_id == 'COMPRESS_QUICK':
                archive_name = first_name + '.rar'
                win_archive_path = os.path.join(os.path.dirname(files_to_compress[0]), archive_name)
                final_cmd = ['wine', winrar_exe, 'a', '-ep1', win_archive_path] + files_to_compress
            
            elif action_id == 'COMPRESS_DIALOG':
                try:
                    yad_cmd = [
                        'yad', '--title=WinRAR Settings',
                        '--form', '--width=500', '--center',
                        '--text=<b>Configure Archive Settings:</b>',
                        '--separator=|||',
                        '--field=Archive Name', first_name,
                        '--field=Save Location:DIR', working_dir,
                        '--field=Archive Type:CB', '^rar!zip',
                        '--field=Password:H', '',
                        '--field=Split Size (e.g., 100M, 1G)', '',
                        '--field=Compression Level:CB', '0 (Store)!1 (Fastest)!2 (Fast)!^3 (Normal)!4 (Good)!5 (Best)',
                        '--field=Delete original files after archiving:CHK', 'FALSE',
                        '--field=Create Solid Archive:CHK', 'FALSE',
                        '--field=Dictionary Size (e.g., 32m, 128m)', ''
                    ]
                    
                    result = subprocess.check_output(yad_cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
                    if not result:
                        return
                    
                    parts = result.split('|||')
                    archive_base_name = parts[0].strip()
                    save_location = parts[1].strip()
                    archive_type = parts[2].strip()
                    password = parts[3].strip()
                    split_size = parts[4].strip()
                    
                    comp_level_raw = parts[5].strip()
                    comp_level = ""
                    if comp_level_raw:
                        match = re.search(r'\d', comp_level_raw)
                        if match:
                            comp_level = match.group()
                    
                    del_files = parts[6].strip()
                    solid_arch = parts[7].strip()
                    dict_size = parts[8].strip()

                    if not archive_base_name.lower().endswith(f'.{archive_type}'):
                        archive_name = f"{archive_base_name}.{archive_type}"
                    else:
                        archive_name = archive_base_name

                    archive_linux_path = os.path.join(save_location, archive_name)
                    
                    try:
                        archive_win_path = subprocess.check_output(['winepath', '-w', archive_linux_path], stderr=subprocess.DEVNULL).decode('utf-8').strip()
                    except subprocess.CalledProcessError:
                        archive_win_path = archive_linux_path

                    final_cmd = ['wine', winrar_exe, 'a']
                    
                    if password:
                        final_cmd.append(f'-hp{password}')
                    if split_size:
                        final_cmd.append(f'-v{split_size}')
                    if comp_level in ['0', '1', '2', '3', '4', '5']:
                        final_cmd.append(f'-m{comp_level}')
                    if del_files == 'TRUE':
                        final_cmd.append('-df')
                    if solid_arch == 'TRUE':
                        final_cmd.append('-s')
                    if dict_size:
                        final_cmd.append(f'-md{dict_size}')
                    
                    final_cmd.append(archive_win_path)
                    final_cmd.extend(files_to_compress)

                except subprocess.CalledProcessError:
                    return

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
                    ['yad', '--file-selection', '--directory', '--title=Select Extraction Destination'],
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
            linux_filepath = self.get_linux_path(file)
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