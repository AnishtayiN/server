# 🚀 AnishtayiN

A modern, responsive proxy management panel with full subscription support.

## ✨ Features

- 🎨 **Modern UI** - React + TailwindCSS with dark mode
- 🔐 **JWT Auth** - Secure admin authentication
- 📡 **Multi-Protocol** - VLESS, VMess, Trojan, Shadowsocks
- 🛡️ **REALITY Support** - Bypass advanced DPI
- 📱 **QR Codes** - One-tap import for mobile clients
- 🔗 **Smart Subscription** - Auto-detect Clash/V2Ray/Sing-box
- 📊 **Traffic Monitoring** - Real-time usage tracking
- 🐳 **Docker Ready** - One-command deployment

## 🚀 Quick Start

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/anishtayin/server/main/install.sh)
```

## 🔑 Default Credentials

- **Username:** `admin`
- **Password:** `admin`

> ⚠️ Change these immediately after first login!

## 📚 Tech Stack

- **Backend:** FastAPI + SQLAlchemy + Pydantic
- **Frontend:** React 18 + Vite + TailwindCSS + Recharts
- **Agent:** Go 1.21 + gRPC + Xray-Core
- **Deployment:** Docker Compose + Nginx

## 📂 Structure

```
anishtayin/
├── backend/     # FastAPI API server
├── frontend/    # React admin panel
├── agent/       # Go proxy orchestrator
└── docker/      # Container configs
```

## 📜 License

AGPL-3.0
