#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[1;33m'
plain='\033[0m'

show_menu() {
    echo -e "${green}x-ui Management Menu${plain}"
    echo "1. Start x-ui"
    echo "2. Stop x-ui"
    echo "3. Restart x-ui"
    echo "4. Status x-ui"
    echo "5. Logs x-ui"
    echo "6. Update x-ui"
    echo "7. Uninstall x-ui"
    echo "8. Reset Admin Password"
    echo "0. Exit"
    echo ""
    read -p "Enter choice [0-8]: " choice
}

start_xui() {
    systemctl start x-ui
    echo -e "${green}x-ui started${plain}"
}

stop_xui() {
    systemctl stop x-ui
    echo -e "${green}x-ui stopped${plain}"
}

restart_xui() {
    systemctl restart x-ui
    echo -e "${green}x-ui restarted${plain}"
}

status_xui() {
    systemctl status x-ui
}

logs_xui() {
    journalctl -u x-ui -f
}

update_xui() {
    bash <(curl -Ls https://raw.githubusercontent.com/anishtayin/server/main/install.sh)
}

uninstall_xui() {
    systemctl stop x-ui
    systemctl disable x-ui
    rm /etc/systemd/system/x-ui.service
    rm -rf /usr/local/x-ui
    rm -rf /etc/x-ui
    echo -e "${green}x-ui uninstalled${plain}"
}

reset_password() {
    read -p "Enter new password: " pass
    echo -e "${yellow}Password reset not implemented in demo${plain}"
}

while true; do
    show_menu
    case $choice in
        1) start_xui ;;
        2) stop_xui ;;
        3) restart_xui ;;
        4) status_xui ;;
        5) logs_xui ;;
        6) update_xui ;;
        7) uninstall_xui ;;
        8) reset_password ;;
        0) exit 0 ;;
        *) echo -e "${red}Invalid option${plain}" ;;
    esac
done
