# XPanel Installation Guide

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Root or sudo access
- At least 512MB RAM
- Docker and Docker Compose (will be installed automatically if missing)

## Quick Installation

### One-Command Install

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/xpanel/main/installer/install.sh | bash
```

Or download and run manually:

```bash
wget https://raw.githubusercontent.com/yourusername/xpanel/main/installer/install.sh
chmod +x install.sh
sudo ./install.sh
```

## Post-Installation

1. Access the panel at `http://YOUR_SERVER_IP:8080`
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. **IMPORTANT**: Change the default password immediately!

## Configuration Options

### Using SQLite (Default)

SQLite is perfect for single-server personal use:

```bash
# No additional configuration needed
docker compose up -d
```

### Using PostgreSQL (For Multi-Node)

For larger setups or multi-node deployments:

```bash
# Create .env file with PostgreSQL settings
cat > docker/.env << EOF
SECRET_KEY=your-secret-key-here
DATABASE_TYPE=postgresql
POSTGRES_USER=xpanel
POSTGRES_PASSWORD=secure-password-here
POSTGRES_DB=xpanel
DEFAULT_ADMIN_PASSWORD=admin123
EOF

# Start with PostgreSQL
docker compose -f docker-compose.postgres.yml up -d
```

## Management Commands

### View Logs
```bash
docker logs -f xpanel
```

### Stop Panel
```bash
cd /opt/xpanel/xpanel/docker
docker compose down
```

### Restart Panel
```bash
docker compose restart
```

### Update Panel
```bash
bash /opt/xpanel/xpanel/installer/update.sh
```

### Backup Data
```bash
bash /opt/xpanel/xpanel/installer/backup.sh
```

### Restore from Backup
```bash
bash /opt/xpanel/xpanel/installer/restore.sh 20240101_120000
```

## Firewall Configuration

Open required ports:

```bash
# Panel port
sudo ufw allow 8080/tcp

# Proxy ports (adjust based on your configuration)
sudo ufw allow 443/tcp
sudo ufw allow 8443/tcp
sudo ufw allow 51820/udp  # WireGuard
```

## Troubleshooting

### Panel Won't Start

Check logs:
```bash
docker logs xpanel
```

Check container status:
```bash
docker ps -a | grep xpanel
```

### Database Issues

For SQLite:
```bash
ls -la /var/lib/xpanel/xpanel.db
```

For PostgreSQL:
```bash
docker logs xpanel-db
```

### Permission Issues

Fix permissions:
```bash
sudo chown -R 1000:1000 /var/lib/xpanel
sudo chmod -R 755 /etc/xpanel
```

## Security Recommendations

1. **Change default password** immediately after installation
2. Use HTTPS with a reverse proxy (Nginx/Caddy)
3. Set a strong SECRET_KEY in environment
4. Regular backups of your data
5. Keep the system updated
6. Use firewall to restrict access

## Uninstallation

```bash
cd /opt/xpanel/xpanel/docker
docker compose down -v
sudo rm -rf /opt/xpanel
sudo rm -rf /var/lib/xpanel
sudo rm -rf /etc/xpanel
```

## Support

For issues and feature requests, please open an issue on GitHub.

---

⚠️ **LEGAL DISCLAIMER**: This software is provided for personal and educational use only. 
Ensure compliance with all applicable laws and regulations in your jurisdiction.
