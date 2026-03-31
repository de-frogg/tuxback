import logging
import os
from pathlib import Path

# Корневая директория проекта, где лежит CLI.py
BASE_DIR = Path(__file__).resolve().parent.parent

# Основная информация о приложение
APP_NAME = "TuxBack"
APP_VERSION = "1.0.0"
# Имя приложения (используется для формирования директорий)
APP_DIR_NAME = "tuxback"
# Формат времени для имен файлов резервных копий
# Пример: 20260331_143500
TIME_FORMAT = "%Y%m%d_%H%M%S"

# Домашняя директория пользователя 
HOME_DIR = Path.home()
# XDG стандарты позволяют хранить данные пользователя в правильных местах
# Это избавляет от необходимости использовать sudo
# Данные (backup файлы)
XDG_DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", HOME_DIR / ".local" / "share"))
# Состояние приложения (логи)
XDG_STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", HOME_DIR / ".local" / "state"))
# Конфигурация (schedules.json)
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", HOME_DIR / ".config"))



# Пользователь может задать свои пути через переменные окружения - Например: export TUXBACK_DATA_DIR=/tmp/backups
DATA_DIR = Path(os.environ.get("TUXBACK_DATA_DIR", XDG_DATA_HOME / APP_DIR_NAME))
STATE_DIR = Path(os.environ.get("TUXBACK_STATE_DIR", XDG_STATE_HOME / APP_DIR_NAME))
CONFIG_DIR = Path(os.environ.get("TUXBACK_CONFIG_DIR", XDG_CONFIG_HOME / APP_DIR_NAME))

#Где хранится архивы
BACKUP_DIR = DATA_DIR / "backups"
#Где хранится расписания задач/расписание
SCHEDULE_FILE = CONFIG_DIR / "schedules.json"
#Где хранится сам лог файл приложение
LOG_FILE = STATE_DIR / "tuxback.log"


def ensure_directories() -> None:
  # Создаёт все необходимые директории приложения. Вызывается перед любыми операциями, чтобы гарантировать, что файловая структура существует.
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    """
    Настраивает систему логирования приложения.

    Логи пишутся:
    1. В консоль (уровень INFO)
    2. В файл tuxback.log (уровень DEBUG)

    Формат логов включает:
    - время
    - уровень
    - модуль
    - функцию и строку
    - сообщение
    """
    # Убедимся, что все директории существуют
    ensure_directories()
    #Консольный вывод (для пользователя)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s | %(message)s")
    )
    #Лог-файл (для диагностики) 
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        )
    )
    # Общая настройка логирования
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
        force=True,
    )
    # Тестовые debug-записи
    logger = logging.getLogger(__name__)
    logger.debug("Logging configured")
    logger.debug("BASE_DIR=%s", BASE_DIR)
    logger.debug("DATA_DIR=%s", DATA_DIR)
    logger.debug("STATE_DIR=%s", STATE_DIR)
    logger.debug("CONFIG_DIR=%s", CONFIG_DIR)
    logger.debug("BACKUP_DIR=%s", BACKUP_DIR)
    logger.debug("SCHEDULE_FILE=%s", SCHEDULE_FILE)
    logger.debug("LOG_FILE=%s", LOG_FILE)