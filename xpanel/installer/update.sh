#!/bin/bash

# XPanel Update Script
# ⚠️ LEGAL WARNING: For personal and educational use only.

set -e

INSTALL_DIR="/opt/xpanel"

echo "Updating XPanel..."

if [ ! -d "$INSTALL_DIR/xpanel" ]; then
    echo "Error: XPanel not found at $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR/xpanel"

# Pull latest changes
git pull origin main || {
    echo "Warning: Could not pull from git repository"
}

# Restart services
cd "$INSTALL_DIR/xpanel/docker"
docker compose pull
docker compose up -d

echo "Update complete!"
echo "Restarting services..."
docker compose restart

echo "XPanel updated successfully!"
