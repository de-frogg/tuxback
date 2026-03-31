#!/usr/bin/env bash

# Включаем строгий режим bash:
# -e - завершение при любой ошибке
# -u - ошибка при использовании неинициализированных переменных
# -o pipefail - ошибка, если любая команда в pipeline завершится неуспешно
set -euo pipefail

# Директория, в которую был установлен проект
INSTALL_DIR="/opt/tuxback"
# Глобальная команда приложения (символическая ссылка)
TARGET_LINK="/usr/local/bin/tuxback"
# Названия пользовательских systemd unit-файлов
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"
# Пользовательская директория systemd, где хранятся service/timer для текущего пользователя
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
# Полные пути к unit-файлам
SERVICE_PATH="$USER_SYSTEMD_DIR/$SERVICE_NAME"
TIMER_PATH="$USER_SYSTEMD_DIR/$TIMER_NAME"

echo "Removing TuxBack..."

# Отключает и останавливаем пользовательский timer. 2>/dev/null || true используется для того, чтобы скрипт не завершался ошибкой, если timer уже удалён или никогда не был создан.
echo "Stopping and disabling user-level systemd timer..."
systemctl --user disable --now "$TIMER_NAME" 2>/dev/null || true

# Удаляет service и timer из пользовательской директории systemd.
echo "Removing user-level systemd unit files..."
rm -f "$SERVICE_PATH" "$TIMER_PATH"
systemctl --user daemon-reload 2>/dev/null || true

# Удаляет симлинк /usr/local/bin/tuxback, если он существует.
if [[ -L "$TARGET_LINK" || -f "$TARGET_LINK" ]]; then
    sudo rm -f "$TARGET_LINK"
    echo "Removed symlink:"
    echo "  $TARGET_LINK"
else
    echo "Symlink not found:"
    echo "  $TARGET_LINK"
fi

# Удаляет директорию установки /opt/tuxback, где находятся исходные файлы программы после install.sh.
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
# Очищаем кэш команд оболочки. Это нужно, чтобы shell "забыл" старый путь к команде tuxback.
hash -r 2>/dev/null || true