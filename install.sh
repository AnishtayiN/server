#!/bin/bash
set -Eeuo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[AnishtayiN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

[[ $EUID -ne 0 ]] && error "Run as root"

log "Installing dependencies..."
apt-get update -qq
apt-get install -y -qq curl git docker.io docker-compose-v2 ufw > /dev/null

log "Configuring firewall..."
ufw allow 22/tcp > /dev/null
ufw allow 80/tcp > /dev/null
ufw allow 443/tcp > /dev/null
ufw allow 443/udp > /dev/null
ufw --force enable > /dev/null

log "Starting Docker services..."
docker compose up -d --build

log "Installation complete!"
log "Panel: http://$(curl -s ifconfig.me)"
log "Default login: admin / admin"
