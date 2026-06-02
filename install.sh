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

install_thunar() {
    echo -e "${GREEN}[+] Installing for Thunar...${NC}"
    mkdir -p ~/.local/share/thunarx-python/extensions
    cp thunar/winrar.py ~/.local/share/thunarx-python/extensions/
    echo -e "${GREEN}[+] Restarting Thunar to apply changes...${NC}"
    thunar -q || true
    echo -e "${GREEN}[✔] Installation for Thunar completed.${NC}"
}

install_caja() {
    echo -e "${GREEN}[+] Installing for Caja...${NC}"
    mkdir -p ~/.local/share/caja-python/extensions
    cp caja/winrar.py ~/.local/share/caja-python/extensions/
    echo -e "${GREEN}[+] Restarting Caja to apply changes...${NC}"
    caja -q || true
    echo -e "${GREEN}[✔] Installation for Caja completed.${NC}"
}

install_pcmanfm() {
    echo -e "${GREEN}[+] Installing for PCManFM / PCManFM-Qt...${NC}"
    mkdir -p ~/.local/bin
    mkdir -p ~/.local/share/file-manager/actions
    
    cp pcmanfm/winrar_pcmanfm.py ~/.local/bin/
    chmod +x ~/.local/bin/winrar_pcmanfm.py

    local ACTIONS_DIR="$HOME/.local/share/file-manager/actions"

    cp pcmanfm/actions/*.desktop "$ACTIONS_DIR/"
    
    sed -i "s|~|$HOME|g" "$ACTIONS_DIR"/winrar_*.desktop
    chmod +x "$ACTIONS_DIR"/winrar_*.desktop

    echo -e "${YELLOW}[!] Restart PCManFM to see the changes.${NC}"
    echo -e "${GREEN}[✔] Installation for PCManFM completed.${NC}"
}


HAS_NAUTILUS=false
HAS_DOLPHIN=false
HAS_NEMO=false
HAS_THUNAR=false
HAS_CAJA=false
HAS_PCMANFM=false

if command -v nautilus &> /dev/null; then HAS_NAUTILUS=true; fi
if command -v dolphin &> /dev/null; then HAS_DOLPHIN=true; fi
if command -v nemo &> /dev/null; then HAS_NEMO=true; fi
if command -v thunar &> /dev/null; then HAS_THUNAR=true; fi
if command -v caja &> /dev/null; then HAS_CAJA=true; fi
if command -v pcmanfm &> /dev/null || command -v pcmanfm-qt &> /dev/null; then HAS_PCMANFM=true; fi

MANAGER_COUNT=0
[ "$HAS_NAUTILUS" = true ] && ((MANAGER_COUNT++))
[ "$HAS_DOLPHIN" = true ] && ((MANAGER_COUNT++))
[ "$HAS_NEMO" = true ] && ((MANAGER_COUNT++))
[ "$HAS_THUNAR" = true ] && ((MANAGER_COUNT++))
[ "$HAS_CAJA" = true ] && ((MANAGER_COUNT++))
[ "$HAS_PCMANFM" = true ] && ((MANAGER_COUNT++))

if [ "$MANAGER_COUNT" -gt 1 ]; then
    echo -e "${YELLOW}Found multiple supported file managers on your system.${NC}"
    echo "Where would you like to install the WinRAR extension?"
    [ "$HAS_NAUTILUS" = true ] && echo "1. Nautilus"
    [ "$HAS_DOLPHIN" = true ] && echo "2. Dolphin"
    [ "$HAS_NEMO" = true ] && echo "3. Nemo"
    [ "$HAS_THUNAR" = true ] && echo "4. Thunar"
    [ "$HAS_CAJA" = true ] && echo "5. Caja"
    [ "$HAS_PCMANFM" = true ] && echo "6. PCManFM / PCManFM-Qt"
    
    echo -e "${YELLOW}(You can type multiple numbers like '1 3 6' to install for multiple)${NC}"
    read -p "Enter your choice: " choice

    VALID_CHOICE=false
    
    if [[ "$choice" == *"1"* ]] && [ "$HAS_NAUTILUS" = true ]; then
        install_nautilus; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"2"* ]] && [ "$HAS_DOLPHIN" = true ]; then
        install_dolphin; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"3"* ]] && [ "$HAS_NEMO" = true ]; then
        install_nemo; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"4"* ]] && [ "$HAS_THUNAR" = true ]; then
        install_thunar; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"5"* ]] && [ "$HAS_CAJA" = true ]; then
        install_caja; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"6"* ]] && [ "$HAS_PCMANFM" = true ]; then
        install_pcmanfm; VALID_CHOICE=true
    fi

    if [ "$VALID_CHOICE" = false ]; then
        echo -e "${RED}Invalid choice. Installation cancelled.${NC}"
        exit 1
    fi

elif [ "$HAS_NAUTILUS" = true ]; then install_nautilus
elif [ "$HAS_DOLPHIN" = true ]; then install_dolphin
elif [ "$HAS_NEMO" = true ]; then install_nemo
elif [ "$HAS_THUNAR" = true ]; then install_thunar
elif [ "$HAS_CAJA" = true ]; then install_caja
elif [ "$HAS_PCMANFM" = true ]; then install_pcmanfm
else
    echo -e "${RED}No supported file managers were found on this system.${NC}"
    exit 1
fi

echo -e "${GREEN}Installation finished successfully!${NC}"