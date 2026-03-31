import logging
from pathlib import Path
from typing import List

from app.config import (
    BACKUP_DIR,
    CONFIG_DIR,
    LOG_FILE,
    SCHEDULE_FILE,
    STATE_DIR,
    ensure_directories,
)

logger = logging.getLogger(__name__)


def init_storage() -> None:
    """
    Подготавливает файловую структуру приложения.

    Эта функция гарантирует, что:
    - директория для бэкапов существует
    - директория конфигурации существует
    - директория логов существует

    Вызывается перед любыми операциями с файлами.
    """
    ensure_directories()
    # Debug-логирование путей
    logger.debug("Storage initialized")
    logger.debug("BACKUP_DIR=%s", BACKUP_DIR)
    logger.debug("CONFIG_DIR=%s", CONFIG_DIR)
    logger.debug("STATE_DIR=%s", STATE_DIR)
    logger.debug("SCHEDULE_FILE=%s", SCHEDULE_FILE)
    logger.debug("LOG_FILE=%s", LOG_FILE)


def get_backup_path(filename: str) -> Path:
    """
    Формирует полный путь к файлу резервной копии.

    :param filename: имя архива (например backup_xxx_xxx.tar.gz)
    :return: абсолютный путь к файлу
    """
    path = BACKUP_DIR / filename
    # Логируем преобразование имени файла в путь
    logger.debug("Resolved backup path: filename=%s -> path=%s", filename, path)
    return path


def backup_exists(filename: str) -> bool:
    """
    Проверяет, существует ли архив резервной копии.

    :param filename: имя архива
    :return: True если файл существует, иначе False
    """
    exists = get_backup_path(filename).exists()
    # INFO уровень — это пользовательски значимая операция
    logger.info("Backup exists check: filename=%s exists=%s", filename, exists)
    return exists


def list_backups() -> List[str]:
    """
    Возвращает список всех доступных резервных копий.

    Фильтрация происходит по расширению `.tar.gz`,
    так как именно в этом формате создаются архивы.
    """
    # Убидится что сами директории существуют
    init_storage()

    backups = [
        file.name
        for file in BACKUP_DIR.iterdir()
        if file.is_file() and file.suffixes[-2:] == [".tar", ".gz"]
    ]
    # Сортируем список для удобства пользователя
    sorted_backups = sorted(backups)
    logger.info("Listed %d backup file(s)", len(sorted_backups))
    logger.debug("Backup files: %s", sorted_backups)
    return sorted_backups


def delete_backup(filename: str) -> bool:
    """
    Удаляет архив резервной копии по имени.

    :param filename: имя архива
    :return: True если удаление успешно, иначе False
    """
    backup_file = get_backup_path(filename)
    # Проверяем, существует ли файл
    if backup_file.exists() and backup_file.is_file():
        file_size = backup_file.stat().st_size
        # Удаляем файл
        backup_file.unlink()
        logger.info(
            "Backup deleted successfully: filename=%s size_bytes=%d",
            filename,
            file_size,
        )
        return True
    # Если файл не найден — логируем предупреждение
    logger.warning("Backup file not found for deletion: %s", filename)
    return False