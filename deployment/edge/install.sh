#!/bin/bash
# DAIOPH Edge Installation Script
set -e

DAIOPH_VERSION="${DAIOPH_VERSION:-latest}"
INSTALL_DIR="/opt/daioph"
SERVICE_USER="daioph"

echo "Installing DAIOPH Edge v${DAIOPH_VERSION}..."

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Create service user
if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
    useradd --system --create-home --shell /bin/bash "$SERVICE_USER"
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Download and extract DAIOPH
curl -sSL "https://github.com/shadowkingaftab/DAIOPH/releases/download/${DAIOPH_VERSION}/daioph-edge.tar.gz" \
    | tar -xz -C "$INSTALL_DIR" --strip-components=1

# Set permissions
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/bin/daioph"

# Install Python dependencies
pip3 install --no-cache-dir -r "$INSTALL_DIR/requirements.txt"

# Install systemd service
cp "$INSTALL_DIR/deployment/edge/daioph.service" /etc/systemd/system/
systemctl daemon-reload

# Enable and start service
systemctl enable daioph
systemctl start daioph

echo "DAIOPH Edge installed successfully."
echo "Service status: $(systemctl is-active daioph)"