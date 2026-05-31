#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$(dirname "$0")" || exit

install_nautilus() {
    echo -e "${GREEN}[+] Installing for Nautilus...${NC}"
    
    mkdir -p ~/.local/share/nautilus-python/extensions
    cp nautilus/winrar.py ~/.local/share/nautilus-python/extensions/
    
    echo -e "${GREEN}[+] Restarting Nautilus to apply changes...${NC}"
    nautilus -q || true
    
    echo -e "${GREEN}[✔] Installation for Nautilus completed.${NC}"
}

install_dolphin() {
    echo -e "${GREEN}[+] Installing for Dolphin...${NC}"
    
    mkdir -p ~/.local/bin
    mkdir -p ~/.local/share/kio/servicemenus
    
    cp dolphin/winrar_dolphin.py ~/.local/bin/
    chmod +x ~/.local/bin/winrar_dolphin.py
    
    cp dolphin/winrar.desktop ~/.local/share/kio/servicemenus/
    sed -i "s|~|$HOME|g" ~/.local/share/kio/servicemenus/winrar.desktop
    chmod +x ~/.local/share/kio/servicemenus/winrar.desktop
    
    echo -e "${YELLOW}[!] You may need to close and reopen Dolphin to see the context menu.${NC}"
    echo -e "${GREEN}[✔] Installation for Dolphin completed.${NC}"
}

HAS_NAUTILUS=false
HAS_DOLPHIN=false

if command -v nautilus &> /dev/null; then HAS_NAUTILUS=true; fi
if command -v dolphin &> /dev/null; then HAS_DOLPHIN=true; fi

if [ "$HAS_NAUTILUS" = true ] && [ "$HAS_DOLPHIN" = true ]; then
    echo -e "${YELLOW}Found both Nautilus and Dolphin on your system.${NC}"
    echo "Where would you like to install the WinRAR extension?"
    echo "1. Nautilus"
    echo "2. Dolphin"
    echo -e "${YELLOW}(You can type '1 2' to install for both)${NC}"
    
    read -p "Enter your choice: " choice

    if [[ "$choice" == *"1"* && "$choice" == *"2"* ]]; then
        install_nautilus
        install_dolphin
    elif [[ "$choice" == *"1"* ]]; then
        install_nautilus
    elif [[ "$choice" == *"2"* ]]; then
        install_dolphin
    else
        echo -e "${RED}Invalid choice. Installation cancelled.${NC}"
        exit 1
    fi

elif [ "$HAS_NAUTILUS" = true ]; then
    echo -e "${GREEN}Found only Nautilus file manager.${NC}"
    install_nautilus

elif [ "$HAS_DOLPHIN" = true ]; then
    echo -e "${GREEN}Found only Dolphin file manager.${NC}"
    install_dolphin

else
    echo -e "${RED}Neither Nautilus nor Dolphin was found on this system.${NC}"
    exit 1
fi

echo -e "${GREEN}Installation finished successfully!${NC}"