import sys
import os
import subprocess
import re

def get_base_archive_name(filename):
    name = re.sub(r'\.part\d+\.rar$', '.rar', filename, flags=re.IGNORECASE)
    if name != filename: return name
    name = re.sub(r'\.\d{3}$', '', filename)
    if name != filename: return name
    name = re.sub(r'\.r\d+$', '.rar', filename, flags=re.IGNORECASE)
    if name != filename: return name
    name = re.sub(r'\.z\d+$', '.zip', filename, flags=re.IGNORECASE)
    if name != filename: return name
    return filename

def sort_files_priority(filepath):
    name = os.path.basename(filepath).lower()
    if name.endswith('.rar') and not re.search(r'\.part\d+\.rar$', name):
        return 0
    if re.search(r'\.(001|part0*1\.rar)$', name):
        return 1
    return 2

def main():
    if len(sys.argv) < 3:
        return

    action_id = sys.argv[1]
    file_paths = sys.argv[2:]
    winrar_exe = os.path.expanduser('~/.wine/drive_c/Program Files/WinRAR/WinRAR.exe')

    if action_id.startswith('COMPRESS'):
        first_linux_path = file_paths[0]
        working_dir = os.path.dirname(first_linux_path)
        first_name = os.path.basename(first_linux_path)
        
        files_to_compress = []
        for linux_path in file_paths:
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
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return

    processed_bases = set()
    files_to_process = []
    
    sorted_files = sorted(file_paths, key=sort_files_priority)
    
    for filepath in sorted_files:
        filename = os.path.basename(filepath)
        base_name = get_base_archive_name(filename)
        
        if base_name not in processed_bases:
            processed_bases.add(base_name)
            files_to_process.append(filepath)

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

    for linux_filepath in files_to_process:
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
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

if __name__ == "__main__":
    main()