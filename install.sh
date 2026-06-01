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

install_nemo() {
    echo -e "${GREEN}[+] Installing for Nemo...${NC}"
    
    mkdir -p ~/.local/share/nemo-python/extensions
    cp nemo/winrar.py ~/.local/share/nemo-python/extensions/
    
    echo -e "${GREEN}[+] Restarting Nemo to apply changes...${NC}"
    nemo -q || true
    
    echo -e "${GREEN}[✔] Installation for Nemo completed.${NC}"
}

HAS_NAUTILUS=false
HAS_DOLPHIN=false
HAS_NEMO=false

if command -v nautilus &> /dev/null; then HAS_NAUTILUS=true; fi
if command -v dolphin &> /dev/null; then HAS_DOLPHIN=true; fi
if command -v nemo &> /dev/null; then HAS_NEMO=true; fi

# حساب عدد مديري الملفات المتوفرة
MANAGER_COUNT=0
[ "$HAS_NAUTILUS" = true ] && ((MANAGER_COUNT++))
[ "$HAS_DOLPHIN" = true ] && ((MANAGER_COUNT++))
[ "$HAS_NEMO" = true ] && ((MANAGER_COUNT++))

if [ "$MANAGER_COUNT" -gt 1 ]; then
    echo -e "${YELLOW}Found multiple supported file managers on your system.${NC}"
    echo "Where would you like to install the WinRAR extension?"
    [ "$HAS_NAUTILUS" = true ] && echo "1. Nautilus"
    [ "$HAS_DOLPHIN" = true ] && echo "2. Dolphin"
    [ "$HAS_NEMO" = true ] && echo "3. Nemo"
    
    echo -e "${YELLOW}(You can type multiple numbers like '1 3' to install for both)${NC}"
    read -p "Enter your choice: " choice

    VALID_CHOICE=false
    
    if [[ "$choice" == *"1"* ]] && [ "$HAS_NAUTILUS" = true ]; then
        install_nautilus
        VALID_CHOICE=true
    fi
    if [[ "$choice" == *"2"* ]] && [ "$HAS_DOLPHIN" = true ]; then
        install_dolphin
        VALID_CHOICE=true
    fi
    if [[ "$choice" == *"3"* ]] && [ "$HAS_NEMO" = true ]; then
        install_nemo
        VALID_CHOICE=true
    fi

    if [ "$VALID_CHOICE" = false ]; then
        echo -e "${RED}Invalid choice. Installation cancelled.${NC}"
        exit 1
    fi

elif [ "$HAS_NAUTILUS" = true ]; then
    echo -e "${GREEN}Found only Nautilus file manager.${NC}"
    install_nautilus

elif [ "$HAS_DOLPHIN" = true ]; then
    echo -e "${GREEN}Found only Dolphin file manager.${NC}"
    install_dolphin

elif [ "$HAS_NEMO" = true ]; then
    echo -e "${GREEN}Found only Nemo file manager.${NC}"
    install_nemo

else
    echo -e "${RED}Neither Nautilus, Dolphin, nor Nemo was found on this system.${NC}"
    exit 1
fi

echo -e "${GREEN}Installation finished successfully!${NC}"