# x-ui Panel

A lightweight and powerful proxy panel written in Go, similar to 3x-ui.

## Features

- **Lightweight**: Written in Go, single binary deployment
- **Web UI**: Modern and responsive web interface
- **Multi-protocol**: Support for VMess, VLESS, Trojan
- **Easy Installation**: One-command installation script
- **Systemd Service**: Runs as a system service
- **SQLite Database**: No external database required

## Quick Installation

```bash
bash <(curl -Ls https://raw.githubusercontent.com/anishtayin/server/main/install.sh)
```

## Management Commands

```bash
x-ui start      # Start the panel
x-ui stop       # Stop the panel
x-ui restart    # Restart the panel
x-ui status     # Check panel status
x-ui log        # View panel logs
x-ui update     # Update to latest version
x-ui uninstall  # Uninstall the panel
```

## Default Credentials

- **Username**: admin
- **Password**: admin
- **Port**: 2053

## Access Panel

After installation, access the panel at:
```
http://YOUR_SERVER_IP:2053
```

## Build from Source

```bash
go mod download
go build -o x-ui main.go
```

## Supported Architectures

- amd64 (x86_64)
- arm64 (aarch64)
- arm (armv7l)

## License

MIT License
