#!/bin/bash
# DAIOPH Edge Uninstallation Script
set -e

INSTALL_DIR="/opt/daioph"
SERVICE_USER="daioph"

echo "Uninstalling DAIOPH Edge..."

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Stop and disable service
if systemctl is-active --quiet daioph; then
    systemctl stop daioph
fi
systemctl disable daioph 2>/dev/null || true

# Remove systemd service
rm -f /etc/systemd/system/daioph.service
systemctl daemon-reload

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

# Remove service user
if id -u "$SERVICE_USER" >/dev/null 2>&1; then
    userdel -r "$SERVICE_USER" 2>/dev/null || true
fi

echo "DAIOPH Edge uninstalled successfully."