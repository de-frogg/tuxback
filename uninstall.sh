#!/usr/bin/env bash

set -euo pipefail

INSTALL_DIR="/opt/tuxback"
TARGET_LINK="/usr/local/bin/tuxback"
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
TIMER_PATH="/etc/systemd/system/$TIMER_NAME"

echo "Removing TuxBack..."

echo "Stopping and disabling systemd timer..."
sudo systemctl disable --now "$TIMER_NAME" 2>/dev/null || true

echo "Removing systemd unit files..."
sudo rm -f "$SERVICE_PATH" "$TIMER_PATH"
sudo systemctl daemon-reload
sudo systemctl reset-failed 2>/dev/null || true

if [[ -L "$TARGET_LINK" || -f "$TARGET_LINK" ]]; then
    sudo rm -f "$TARGET_LINK"
    echo "Removed symlink:"
    echo "  $TARGET_LINK"
else
    echo "Symlink not found:"
    echo "  $TARGET_LINK"
fi

if [[ -d "$INSTALL_DIR" ]]; then
    sudo rm -rf "$INSTALL_DIR"
    echo "Removed installation directory:"
    echo "  $INSTALL_DIR"
else
    echo "Installation directory not found:"
    echo "  $INSTALL_DIR"
fi

echo
echo "TuxBack removed successfully."
echo "Run 'hash -r' or open a new shell if your shell still remembers the old command path."

# очищаем кэш bash команд
hash -r 2>/dev/null || true