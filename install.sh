#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[1;33m'
plain='\033[0m'

cur_dir=$(pwd)
ARCH=$(uname -m)

case $ARCH in
    x86_64) ARCH="amd64" ;;
    aarch64) ARCH="arm64" ;;
    armv7l) ARCH="arm" ;;
    *) echo -e "${red}Unsupported architecture${plain}"; exit 1 ;;
esac

echo -e "${green}Installing x-ui panel...${plain}"

mkdir -p /etc/x-ui
mkdir -p /var/log/x-ui
mkdir -p /usr/local/x-ui

cd /tmp || exit
curl -L -o x-ui-linux-${ARCH}.tar.gz "https://github.com/anishtayin/server/releases/latest/download/x-ui-linux-${ARCH}.tar.gz"

if [ ! -f x-ui-linux-${ARCH}.tar.gz ]; then
    echo -e "${red}Failed to download x-ui${plain}"
    exit 1
fi

tar zxvf x-ui-linux-${ARCH}.tar.gz
chmod +x x-ui

cp x-ui /usr/local/x-ui/x-ui
cp -r web /usr/local/x-ui/

cat > /etc/systemd/system/x-ui.service << EOF
[Unit]
Description=x-ui Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/x-ui/x-ui
Restart=on-failure
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable x-ui
systemctl start x-ui

echo -e "${green}Installation completed!${plain}"
echo -e "Panel URL: ${yellow}http://\$(hostname -I | awk '{print \$1}'):2053${plain}"
echo -e "Default username: ${yellow}admin${plain}"
echo -e "Default password: ${yellow}admin${plain}"

cd "$cur_dir" || exit
