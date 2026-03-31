# Установка TuxBack

Данный документ описывает процесс установки и первоначальной настройки утилиты **TuxBack**.

TuxBack — это CLI‑приложение для Linux, предназначенное для создания, хранения и восстановления резервных копий директорий. Также поддерживается автоматическое выполнение задач по расписанию.

---

# Системные требования

Перед установкой убедитесь, что в системе установлены:

- Linux (Ubuntu, Debian, CentOS и др.)
- Python **3.10+**
- Git
- systemd (для планировщика)

---

# Получение проекта

Скачайте репозиторий:

```bash
git clone https://github.com/de-frogg/tuxback
cd tuxback
```

---

# Подготовка

Сделайте файлы исполняемыми:

```bash
chmod +x tuxback install.sh uninstall.sh
```

---

# Установка

Запустите установку:

```bash
./install.sh
```

Во время установки происходит:

- копирование файлов в `/opt/tuxback`
- создание команды `/usr/local/bin/tuxback`
- настройка **user-level systemd** (без root runtime)
- активация таймера планировщика

После установки приложение работает **без sudo**.

---

# Проверка установки

```bash
tuxback --help
tuxback status
```

Пример:

```
TuxBack status:
- Version: 1.0.0
- Total backups: 0
- Total schedules: 0
- Enabled schedules: 0
```

---

# Проверка планировщика

TuxBack использует **user-level systemd timer**.

Проверка статуса:

```bash
systemctl --user status tuxback-scheduler.timer
```

Список таймеров:

```bash
systemctl --user list-timers
```

Логи:

```bash
journalctl --user -u tuxback-scheduler.service
```

---

# Где хранятся данные

TuxBack использует XDG-стандарт:

Бэкапы:
```
~/.local/share/tuxback/backups
```

Расписание:
```
~/.config/tuxback/schedules.json
```

Логи:
```
~/.local/state/tuxback/tuxback.log
```

---

# Удаление

```bash
/opt/tuxback/uninstall.sh
```

Удаляется:

- systemd timer и service
- команда tuxback
- директория `/opt/tuxback`

---

# Очистка кеша shell

```bash
hash -r
```

Или перезапустите терминал.