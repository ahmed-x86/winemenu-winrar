# WinRAR Menu for Linux

This project is an extension for [winemenu](https://github.com/ahmed-x86/winemenu). It brings the native Windows experience to Linux by adding WinRAR's standard options directly to your file manager's right-click context menu.

Currently, this extension supports two file managers:

* **Nautilus** (GNOME)
* **Dolphin** (KDE)

## Prerequisites

If you are using **Nautilus**, you may need to install the Python bindings for extensions before running the installation script.

* **Arch Linux:**
```bash
sudo pacman -S python-nautilus
```


* **Debian / Ubuntu:**
```bash
sudo apt install python3-nautilus
```


* **Fedora:**
```bash
sudo dnf install nautilus-python
```



*(Note: Dolphin users do not need these dependencies as it uses native `.desktop` service menus).*

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

If you prefer to use the terminal, you can execute the exact same commands the extension uses in the background. Assuming your target archive is named `test.7z`:

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