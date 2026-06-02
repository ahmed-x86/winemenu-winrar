# WinRAR Menu for Linux

This project is an extension for [winemenu](https://github.com/ahmed-x86/winemenu). It brings the native Windows experience to Linux by adding WinRAR's standard options (Extract and Compress) directly to your file manager's right-click context menu.

Currently, this extension supports six file managers:

* **Nautilus** (GNOME)
* **Dolphin** (KDE)
* **Nemo** (Cinnamon / Linux Mint)
* **Thunar** (XFCE)
* **Caja** (MATE)
* **PCManFM / PCManFM-Qt** (LXDE / LXQt)

## Prerequisites

If you are using **Nautilus**, **Nemo**, **Thunar**, or **Caja**, you must install the respective Python bindings for extensions before running the installation script. Install only the package(s) for the file manager(s) you use:

### For Arch Linux:
```bash
# For Nautilus:
sudo pacman -S python-nautilus
# For Nemo:
sudo pacman -S nemo-python
# For Thunar:
sudo pacman -S thunarx-python
# For Caja:
sudo pacman -S caja-python
```

### For Debian / Ubuntu / Linux Mint:

```bash
# For Nautilus:
sudo apt install python3-nautilus
# For Nemo:
sudo apt install python3-nemo
# For Thunar:
sudo apt install thunarx-python
# For Caja:
sudo apt install python3-caja
```

### For Fedora:

```bash
# For Nautilus:
sudo dnf install nautilus-python
# For Nemo:
sudo dnf install nemo-python
# For Thunar:
sudo dnf install thunarx-python
# For Caja:
sudo dnf install caja-python
```

*(Note: **Dolphin** and **PCManFM** users do not need these dependencies as they use native `.desktop` service menus/actions).*

## Installation

To install the extension, clone the repository and run the automated installation script:

```bash
git clone https://github.com/ahmed-x86/winemenu-winrar.git
cd winemenu-winrar
chmod +x install.sh
./install.sh
```

The script will automatically detect your installed file manager(s) and prompt you to choose where to install the extension.

## Terminal Commands (CLI Usage)

If you prefer to use the terminal, you can execute the exact same commands the extension uses in the background.

### 🗜️ Compression Commands

**1. Add to archive... / Add to quick archive (.rar):**
Assuming you want to compress `file1.txt` and `folder1` into `archive.rar`:

```bash
wine "$HOME/.wine/drive_c/Program Files/WinRAR/WinRAR.exe" a "archive.rar" "file1.txt" "folder1"
```

### 📂 Extraction Commands

Assuming your target archive is named `test.7z`:

**1. Extract Here:**

```bash
wine "$HOME/.wine/drive_c/Program Files/WinRAR/WinRAR.exe" x "test.7z"
```

**2. Extract to "test/" (Creates a folder with the archive name):**

```bash
wine "$HOME/.wine/drive_c/Program Files/WinRAR/WinRAR.exe" x -ad "test.7z"
```

**3. Extract files... (To a specific destination path):**

```bash
wine "$HOME/.wine/drive_c/Program Files/WinRAR/WinRAR.exe" x "test.7z" "Z:\path\to\your\destination\"
```

*(Note: WinRAR requires Windows-style paths when specifying destinations manually).*

**4. Open with WinRAR:**

```bash
wine "$HOME/.wine/drive_c/Program Files/WinRAR/WinRAR.exe" "test.7z"
```