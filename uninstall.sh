#!/usr/bin/env bash

set -euo pipefail

INSTALL_DIR="/opt/tuxback"
TARGET_LINK="/usr/local/bin/tuxback"

echo "Removing TuxBack..."

# Удаляем симлинк
if [[ -L "$TARGET_LINK" || -f "$TARGET_LINK" ]]; then
    sudo rm -f "$TARGET_LINK"
    echo "Removed symlink:"
    echo "  $TARGET_LINK"
else
    echo "Symlink not found:"
    echo "  $TARGET_LINK"
fi

# Удаляем директорию установки
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