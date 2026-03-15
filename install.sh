#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/tuxback"
TARGET_LINK="/usr/local/bin/tuxback"
SOURCE_SCRIPT="$PROJECT_DIR/tuxback"
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
TIMER_PATH="/etc/systemd/system/$TIMER_NAME"

echo "Installing TuxBack..."

if [[ ! -f "$SOURCE_SCRIPT" ]]; then
    echo "Error: launcher script '$SOURCE_SCRIPT' not found."
    exit 1
fi

chmod +x "$SOURCE_SCRIPT"
chmod +x "$PROJECT_DIR/uninstall.sh" 2>/dev/null || true

echo "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

echo "Copying project files..."
sudo rsync -a --delete \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'backups' \
    --exclude 'restored_data' \
    --exclude 'restored_from_cli' \
    --exclude 'test_data' \
    --exclude 'tuxback.log' \
    --exclude 'schedules.json' \
    "$PROJECT_DIR/" "$INSTALL_DIR/"

sudo chmod +x "$INSTALL_DIR/tuxback"
sudo chmod +x "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true

echo "Creating command symlink..."
sudo ln -sf "$INSTALL_DIR/tuxback" "$TARGET_LINK"

echo "Installing systemd service..."
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=TuxBack scheduled backup runner
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$INSTALL_DIR
ExecStart=$TARGET_LINK run-scheduler
EOF

echo "Installing systemd timer..."
sudo tee "$TIMER_PATH" > /dev/null <<EOF
[Unit]
Description=Run TuxBack scheduler every minute

[Timer]
OnCalendar=*-*-* *:*:00
Persistent=true
Unit=$SERVICE_NAME

[Install]
WantedBy=timers.target
EOF

echo "Enabling systemd timer..."
sudo systemctl daemon-reload
sudo systemctl enable --now "$TIMER_NAME"

echo
echo "TuxBack installed successfully."
echo
echo "Installation directory:"
echo "  $INSTALL_DIR"
echo
echo "Command available globally as:"
echo "  tuxback"
echo
echo "Systemd timer enabled as:"
echo "  $TIMER_NAME"
echo
echo "Try running:"
echo "  tuxback --help"
echo "  tuxback --version"
echo "  tuxback status"
echo "  systemctl status $TIMER_NAME"
echo "  journalctl -u $SERVICE_NAME -n 20 --no-pager"