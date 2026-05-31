import sys
import os
import subprocess
import re
import shutil

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
            if shutil.which('kdialog'):
                dest_linux_path = subprocess.check_output(
                    ['kdialog', '--getexistingdirectory', 'Select Extraction Destination'],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8').strip()
            else:
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

    winrar_exe = os.path.expanduser('~/.wine/drive_c/Program Files/WinRAR/WinRAR.exe')

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