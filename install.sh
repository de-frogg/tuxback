##!/usr/bin/env bash
# Включаем строгий режим bash: -e  → завершение при ошибке, -u  → ошибка при неинициализированных переменных, -o pipefail → ошибка если падает любая команда в цепочке
set -euo pipefail
# Директория проекта (где лежит install.sh)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Куда будет установлен проект
INSTALL_DIR="/opt/tuxback"
# Глобальная команда (симлинк)
TARGET_LINK="/usr/local/bin/tuxback"
# Основной исполняемый файл
SOURCE_SCRIPT="$PROJECT_DIR/tuxback"
# Названия systemd unit-файлов
SERVICE_NAME="tuxback-scheduler.service"
TIMER_NAME="tuxback-scheduler.timer"
# Пользовательская systemd директория (важно: без sudo)
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_PATH="$USER_SYSTEMD_DIR/$SERVICE_NAME"
TIMER_PATH="$USER_SYSTEMD_DIR/$TIMER_NAME"

echo "Installing TuxBack..."
# Проверяет наличие launcher-скрипта
if [[ ! -f "$SOURCE_SCRIPT" ]]; then
    echo "Error: launcher script '$SOURCE_SCRIPT' not found."
    exit 1
fi
# Делаем скрипты исполняемыми
chmod +x "$SOURCE_SCRIPT"
chmod +x "$PROJECT_DIR/uninstall.sh" 2>/dev/null || true

echo "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

echo "Copying project files..."
# rsync вместо cp:
# 1. быстрее
# 2. умеет удалять лишние файлы (--delete)
# 3. удобно исключать ненужные файлы
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
# Делает исполняемыми установленные файлы
sudo chmod +x "$INSTALL_DIR/tuxback"
sudo chmod +x "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true
# Создаёт симлинк → tuxback становится доступен глобально
sudo ln -sf "$INSTALL_DIR/tuxback" "$TARGET_LINK"
# Создаёт директорию для user systemd
mkdir -p "$USER_SYSTEMD_DIR"
# SERVICE
echo "Installing user-level systemd service..."
cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=TuxBack scheduled backup runner
After=default.target

[Service]
Type=oneshot
WorkingDirectory=$INSTALL_DIR
ExecStart=$TARGET_LINK run-scheduler
EOF
# TIMER
echo "Installing user-level systemd timer..."
cat > "$TIMER_PATH" <<EOF
[Unit]
Description=Run TuxBack scheduler every minute

[Timer]
OnCalendar=*-*-* *:*:00
Persistent=true
Unit=$SERVICE_NAME

[Install]
WantedBy=timers.target
EOF
# Позволяет таймеру работать даже после выхода пользователя
sudo loginctl enable-linger "$USER" 2>/dev/null || true
# Перезапускает user systemd
systemctl --user daemon-reload
# Включает таймер
systemctl --user enable --now "$TIMER_NAME"

echo
echo "TuxBack installed successfully."
echo
echo "Program files installed to:"
echo "  $INSTALL_DIR"
echo
echo "Global command available as:"
echo "  tuxback"
echo
echo "User data, schedules and logs are now stored in your home directory."
echo "This means TuxBack can be used without sudo after installation."
echo
echo "User systemd timer enabled as:"
echo "  $TIMER_NAME"
echo
echo "Try running:"
echo "  tuxback --help"
echo "  tuxback --version"
echo "  tuxback status"
echo "  systemctl --user status $TIMER_NAME"
echo "  journalctl --user -u $SERVICE_NAME -n 20 --no-pager"