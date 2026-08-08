#!/bin/bash

# XPanel One-Command Installer
# ⚠️ LEGAL WARNING: For personal and educational use only.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
XPANEL_VERSION="1.0.0"
INSTALL_DIR="/opt/xpanel"
DATA_DIR="/var/lib/xpanel"
CONFIG_DIR="/etc/xpanel"
LOG_DIR="/var/log/xpanel"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    XPanel Installer                      ║${NC}"
echo -e "${BLUE}║              Web Control Panel for Xray Core             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${RED}⚠️  LEGAL WARNING: This software is for personal and educational${NC}"
echo -e "${RED}   use only. Ensure compliance with all applicable laws.${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run as root (use sudo)${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    print_status "Detected OS: $OS $VER"
}

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found. Installing Docker..."
        install_docker
    else
        print_success "Docker is already installed ($(docker --version))"
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_warning "Docker Compose not found. Installing..."
        install_docker_compose
    else
        print_success "Docker Compose is available"
    fi
}

install_docker() {
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    print_success "Docker installed successfully"
}

install_docker_compose() {
    print_status "Installing Docker Compose..."
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    ln -s $DOCKER_CONFIG/cli-plugins/docker-compose /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
}

# Create directories
create_directories() {
    print_status "Creating directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    print_success "Directories created"
}

# Download XPanel
download_xpanel() {
    print_status "Downloading XPanel..."
    
    # Clone or update repository
    if [ -d "$INSTALL_DIR/xpanel" ]; then
        cd "$INSTALL_DIR/xpanel"
        git pull origin main 2>/dev/null || print_warning "Could not pull updates"
    else
        cd "$INSTALL_DIR"
        git clone https://github.com/yourusername/xpanel.git 2>/dev/null || {
            print_warning "Could not clone from GitHub. Using local files..."
            # For development/testing, copy from workspace
            cp -r /workspace/xpanel "$INSTALL_DIR/"
        }
    fi
    
    print_success "XPanel downloaded"
}

# Generate environment file
generate_env() {
    print_status "Generating environment configuration..."
    
    ENV_FILE="$INSTALL_DIR/xpanel/docker/.env"
    
    # Generate secure random key
    SECRET_KEY=$(openssl rand -hex 32)
    
    cat > "$ENV_FILE" << EOF
# XPanel Environment Configuration
# Generated on $(date)

# Security
SECRET_KEY=$SECRET_KEY

# Database Settings (sqlite or postgresql)
DATABASE_TYPE=sqlite

# PostgreSQL Settings (only used if DATABASE_TYPE=postgresql)
POSTGRES_USER=xpanel
POSTGRES_PASSWORD=$(openssl rand -base64 24)
POSTGRES_DB=xpanel

# Admin Credentials
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123

# Server Settings
SUBSCRIPTION_HOST=
SUBSCRIPTION_PORT=8080
EOF
    
    chmod 600 "$ENV_FILE"
    print_success "Environment configuration generated"
    print_warning "Default admin password is 'admin123' - Change it after first login!"
}

# Install XPanel
install_xpanel() {
    print_status "Installing XPanel with Docker..."
    
    cd "$INSTALL_DIR/xpanel/docker"
    
    # Pull images
    docker compose pull || print_warning "Could not pull images"
    
    # Start services
    docker compose up -d
    
    print_success "XPanel installed successfully"
}

# Show installation summary
show_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  Installation Complete!                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Access the panel:${NC} http://YOUR_SERVER_IP:8080"
    echo -e "${BLUE}Username:${NC} admin"
    echo -e "${BLUE}Password:${NC} admin123 ${RED}(CHANGE IMMEDIATELY!)${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  View logs:     docker logs -f xpanel"
    echo "  Stop panel:    docker compose -C $INSTALL_DIR/xpanel/docker down"
    echo "  Restart:       docker compose -C $INSTALL_DIR/xpanel/docker restart"
    echo "  Update:        bash $INSTALL_DIR/xpanel/installer/update.sh"
    echo "  Backup:        bash $INSTALL_DIR/xpanel/installer/backup.sh"
    echo ""
    echo -e "${RED}⚠️  REMINDER: Use responsibly and legally!${NC}"
    echo ""
}

# Main installation function
main() {
    detect_os
    check_docker
    create_directories
    download_xpanel
    generate_env
    install_xpanel
    show_summary
}

# Run installation
main "$@"
