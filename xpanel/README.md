# XPanel - Web Control Panel for Xray Core

> **⚠️ LEGAL WARNING**: This software is provided for **personal and educational use only**. 
> You are solely responsible for ensuring compliance with all applicable laws and regulations 
> in your jurisdiction. The authors and contributors disclaim all liability for any misuse 
> of this software. Use only on networks you own or have explicit permission to manage.

## Features

- **Multi-Protocol Support**: Vmess, Vless, Trojan, ShadowSocks, WireGuard, Hysteria, HTTP, Tunnel, Mixed, Tun
- **User Management**: Create multiple users with expiry dates, traffic limits, and IP limits
- **Real-time Monitoring**: View usage statistics, connection status, and server health
- **Subscription Links**: Generate client links and subscription URLs for easy distribution
- **Inbound Management**: Configure and manage multiple inbound connections
- **Database Support**: SQLite (default) for simple setups, PostgreSQL for multi-node deployments
- **Docker Support**: Easy deployment with Docker Compose
- **One-Command Installer**: Simple installation script for quick setup

## Quick Start

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/xpanel/main/installer/install.sh | bash
```

### Docker Installation

```bash
cd xpanel/docker
docker-compose up -d
```

Access the panel at `http://localhost:8080`

Default credentials:
- Username: `admin`
- Password: `admin123` (change immediately!)

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [User Management](docs/user-management.md)
- [API Reference](docs/api.md)
- [Backup & Restore](docs/backup.md)

## Requirements

- Linux server (Ubuntu 20.04+ recommended)
- Docker & Docker Compose (for Docker deployment)
- Python 3.9+ (for native installation)
- Node.js 18+ (for frontend development)

## Project Structure

```
xpanel/
├── backend/          # Python FastAPI backend
├── frontend/         # React/Vue.js frontend
├── installer/        # Installation scripts
├── docker/           # Docker configuration
└── docs/             # Documentation
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This software is intended for legitimate network management purposes only. 
Ensure you have proper authorization before deploying and using this panel.
