#!/bin/bash

# XPanel Backup Script
# ⚠️ LEGAL WARNING: For personal and educational use only.

set -e

INSTALL_DIR="/opt/xpanel"
BACKUP_DIR="/var/backups/xpanel"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Creating XPanel backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup SQLite database (if using SQLite)
if [ -f "$INSTALL_DIR/xpanel/docker/xpanel_data/xpanel.db" ]; then
    echo "Backing up SQLite database..."
    cp "$INSTALL_DIR/xpanel/docker/xpanel_data/xpanel.db" "$BACKUP_DIR/xpanel_$DATE.db"
fi

# Backup environment file
if [ -f "$INSTALL_DIR/xpanel/docker/.env" ]; then
    echo "Backing up environment configuration..."
    cp "$INSTALL_DIR/xpanel/docker/.env" "$BACKUP_DIR/env_$DATE"
fi

# Backup config files
if [ -d "$INSTALL_DIR/xpanel/docker/xpanel_config" ]; then
    echo "Backing up configuration files..."
    tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$INSTALL_DIR/xpanel/docker/xpanel_config" .
fi

# Create manifest
cat > "$BACKUP_DIR/manifest_$DATE.txt" << EOF
XPanel Backup Manifest
======================
Date: $DATE
Version: $(cat $INSTALL_DIR/xpanel/README.md | grep "APP_VERSION" || echo "unknown")

Files backed up:
- Database: xpanel_$DATE.db (if exists)
- Environment: env_$DATE
- Config: config_$DATE.tar.gz

Restore instructions:
1. Stop XPanel: docker compose -C /opt/xpanel/xpanel/docker down
2. Restore database: cp $BACKUP_DIR/xpanel_$DATE.db /opt/xpanel/xpanel/docker/xpanel_data/xpanel.db
3. Restore environment: cp $BACKUP_DIR/env_$DATE /opt/xpanel/xpanel/docker/.env
4. Restore config: tar -xzf $BACKUP_DIR/config_$DATE.tar.gz -C /opt/xpanel/xpanel/docker/xpanel_config
5. Start XPanel: docker compose -C /opt/xpanel/xpanel/docker up -d
EOF

echo ""
echo "Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
echo ""
echo "To restore:"
echo "  bash $INSTALL_DIR/xpanel/installer/restore.sh $DATE"
