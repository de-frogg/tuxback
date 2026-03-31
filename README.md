# TuxBack

TuxBack — это CLI‑утилита для резервного копирования и восстановления данных в Linux, разработанная на Python.

Проект создан как дипломная работа и демонстрирует:
- разработку CLI-приложения
- работу с файловой системой
- автоматизацию через systemd
- контейнеризацию (Docker)
- практики CI/CD

Основная цель — предоставить простую, удобную и расширяемую утилиту для автоматизации резервного копирования.

---

# Основные возможности

- создание резервных копий директорий
- восстановление из архивов
- просмотр и удаление бэкапов
- планирование задач
- автоматический запуск через systemd
- подробное логирование
- установка как системной утилиты
- работа без sudo после установки
- поддержка Docker

Формат архивов:

```
.tar.gz
```

---

# Быстрый старт

```bash
git clone https://github.com/de-frogg/tuxback
cd tuxback
chmod +x tuxback install.sh uninstall.sh
./install.sh
```

Проверка:

```bash
tuxback --help
tuxback status
```

---

# Команды

Создание бэкапа:

```bash
tuxback backup <directory>
```

Список бэкапов:

```bash
tuxback list
```

Восстановление:

```bash
tuxback restore <archive> <target>
```

Удаление:

```bash
tuxback delete <archive>
```

Статус:

```bash
tuxback status
```

Версия:

```bash
tuxback --version
```

---

# Планировщик

Добавление задачи:

```bash
tuxback schedule-add <directory> <interval_minutes>
```

Просмотр задач:

```bash
tuxback schedule-list
```

Удаление:

```bash
tuxback schedule-delete <id>
```

Ручной запуск:

```bash
tuxback run-scheduler
```

---

# Установка

Во время установки:

- файлы копируются в `/opt/tuxback`
- создаётся команда `/usr/local/bin/tuxback`
- настраивается **user-level systemd timer**

После установки приложение работает **без sudo**.

---

# Автозапуск (systemd)

Планировщик запускается каждую минуту:

```bash
systemctl --user status tuxback-scheduler.timer
```

Логи systemd:

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

# Логирование

Логи записываются:
- в консоль
- в файл

Пример:

```bash
tail -n 20 ~/.local/state/tuxback/tuxback.log
```

---

# Docker

Сборка:

```bash
docker build -t tuxback .
```

Запуск:

```bash
docker run --rm tuxback
```

С volume:

```bash
docker run --rm -v "$(pwd):/data" tuxback backup /data
```

---

# CI/CD

Используется GitHub Actions:

```
.github/workflows/ci.yml
```

Pipeline выполняет:
- тест CLI
- проверку логов
- сборку Docker

---

# Документация

```
docs/
 ├ installation.md
 ├ usage.md
 └ development.md
```

Архитектура:

```
architect.md
```

---

# Технологии

- Python 3.12
- argparse
- tarfile
- pathlib
- logging
- json
- datetime
- Docker
- systemd
- GitHub Actions

---

# Makefile

```bash
make install
make uninstall
make status
make docker-build
```

---

# Возможные улучшения

- Шифрование бэкапов
- Удалённое хранилище
- web-интерфейс
- Конфиг файл
- Тесты