#!/bin/bash

# XPanel Restore Script
# ⚠️ LEGAL WARNING: For personal and educational use only.

set -e

INSTALL_DIR="/opt/xpanel"
BACKUP_DIR="/var/backups/xpanel"

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_date>"
    echo ""
    echo "Available backups:"
    ls -la "$BACKUP_DIR" 2>/dev/null || echo "No backups found"
    exit 1
fi

DATE=$1

echo "Restoring XPanel from backup $DATE..."

# Stop XPanel
echo "Stopping XPanel..."
cd "$INSTALL_DIR/xpanel/docker"
docker compose down

# Restore database
if [ -f "$BACKUP_DIR/xpanel_$DATE.db" ]; then
    echo "Restoring database..."
    cp "$BACKUP_DIR/xpanel_$DATE.db" "$INSTALL_DIR/xpanel/docker/xpanel_data/xpanel.db"
fi

# Restore environment
if [ -f "$BACKUP_DIR/env_$DATE" ]; then
    echo "Restoring environment configuration..."
    cp "$BACKUP_DIR/env_$DATE" "$INSTALL_DIR/xpanel/docker/.env"
fi

# Restore config
if [ -f "$BACKUP_DIR/config_$DATE.tar.gz" ]; then
    echo "Restoring configuration files..."
    mkdir -p "$INSTALL_DIR/xpanel/docker/xpanel_config"
    tar -xzf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$INSTALL_DIR/xpanel/docker/xpanel_config"
fi

# Start XPanel
echo "Starting XPanel..."
docker compose up -d

echo ""
echo "Restore completed successfully!"
echo "Access the panel at: http://YOUR_SERVER_IP:8080"
