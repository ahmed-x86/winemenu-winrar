#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

uninstall_nautilus() {
    echo -e "${YELLOW}[-] Uninstalling for Nautilus...${NC}"
    rm -f ~/.local/share/nautilus-python/extensions/winrar.py
    echo -e "${GREEN}[+] Restarting Nautilus...${NC}"
    nautilus -q || true
    echo -e "${GREEN}[✔] Uninstallation for Nautilus completed.${NC}"
}

uninstall_dolphin() {
    echo -e "${YELLOW}[-] Uninstalling for Dolphin...${NC}"
    rm -f ~/.local/bin/winrar_dolphin.py
    rm -f ~/.local/share/kio/servicemenus/winrar.desktop
    echo -e "${GREEN}[✔] Uninstallation for Dolphin completed.${NC}"
}

uninstall_nemo() {
    echo -e "${YELLOW}[-] Uninstalling for Nemo...${NC}"
    rm -f ~/.local/share/nemo-python/extensions/winrar.py
    echo -e "${GREEN}[+] Restarting Nemo...${NC}"
    nemo -q || true
    echo -e "${GREEN}[✔] Uninstallation for Nemo completed.${NC}"
}

uninstall_thunar() {
    echo -e "${YELLOW}[-] Uninstalling for Thunar...${NC}"
    rm -f ~/.local/share/thunarx-python/extensions/winrar.py
    echo -e "${GREEN}[+] Restarting Thunar...${NC}"
    thunar -q || true
    echo -e "${GREEN}[✔] Uninstallation for Thunar completed.${NC}"
}

uninstall_caja() {
    echo -e "${YELLOW}[-] Uninstalling for Caja...${NC}"
    rm -f ~/.local/share/caja-python/extensions/winrar.py
    echo -e "${GREEN}[+] Restarting Caja...${NC}"
    caja -q || true
    echo -e "${GREEN}[✔] Uninstallation for Caja completed.${NC}"
}

uninstall_pcmanfm() {
    echo -e "${YELLOW}[-] Uninstalling for PCManFM / PCManFM-Qt...${NC}"
    rm -f ~/.local/bin/winrar_pcmanfm.py
    rm -f ~/.local/share/file-manager/actions/winrar_*.desktop
    echo -e "${YELLOW}[!] Please restart PCManFM manually to see the changes.${NC}"
    echo -e "${GREEN}[✔] Uninstallation for PCManFM completed.${NC}"
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
    echo "From where would you like to uninstall the WinRAR extension?"
    [ "$HAS_NAUTILUS" = true ] && echo "1. Nautilus"
    [ "$HAS_DOLPHIN" = true ] && echo "2. Dolphin"
    [ "$HAS_NEMO" = true ] && echo "3. Nemo"
    [ "$HAS_THUNAR" = true ] && echo "4. Thunar"
    [ "$HAS_CAJA" = true ] && echo "5. Caja"
    [ "$HAS_PCMANFM" = true ] && echo "6. PCManFM / PCManFM-Qt"
    
    echo -e "${YELLOW}(You can type multiple numbers like '1 3 6')${NC}"
    read -p "Enter your choice: " choice

    VALID_CHOICE=false
    
    if [[ "$choice" == *"1"* ]] && [ "$HAS_NAUTILUS" = true ]; then
        uninstall_nautilus; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"2"* ]] && [ "$HAS_DOLPHIN" = true ]; then
        uninstall_dolphin; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"3"* ]] && [ "$HAS_NEMO" = true ]; then
        uninstall_nemo; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"4"* ]] && [ "$HAS_THUNAR" = true ]; then
        uninstall_thunar; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"5"* ]] && [ "$HAS_CAJA" = true ]; then
        uninstall_caja; VALID_CHOICE=true
    fi
    if [[ "$choice" == *"6"* ]] && [ "$HAS_PCMANFM" = true ]; then
        uninstall_pcmanfm; VALID_CHOICE=true
    fi

    if [ "$VALID_CHOICE" = false ]; then
        echo -e "${RED}Invalid choice. Uninstallation cancelled.${NC}"
        exit 1
    fi

elif [ "$HAS_NAUTILUS" = true ]; then uninstall_nautilus
elif [ "$HAS_DOLPHIN" = true ]; then uninstall_dolphin
elif [ "$HAS_NEMO" = true ]; then uninstall_nemo
elif [ "$HAS_THUNAR" = true ]; then uninstall_thunar
elif [ "$HAS_CAJA" = true ]; then uninstall_caja
elif [ "$HAS_PCMANFM" = true ]; then uninstall_pcmanfm
else
    echo -e "${RED}No supported file managers were found on this system.${NC}"
    exit 1
fi

echo -e "${GREEN}Uninstallation finished successfully!${NC}"