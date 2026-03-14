from pathlib import Path
from typing import List

from app.config import BACKUP_DIR, ensure_directories


def init_storage() -> None: # Инициализирует хранилище резервных копий.
  
    ensure_directories()


def get_backup_path(filename: str) -> Path: # Возвращает полный путь к файлу резервной копии.

    return BACKUP_DIR / filename


def backup_exists(filename: str) -> bool: #  Проверяет, существует ли файл резервной копии.

    return get_backup_path(filename).exists()


def list_backups() -> List[str]: # Возвращает список всех резервных копий в директории backups.

    init_storage()

    backups = [
        file.name
        for file in BACKUP_DIR.iterdir()
        if file.is_file() and file.suffixes[-2:] == [".tar", ".gz"]
    ]

    return sorted(backups)


def delete_backup(filename: str) -> bool: # Удаляет резервную копию по имени файла. Возвращает True, если удаление прошло успешно, иначе False.

    backup_file = get_backup_path(filename)

    if backup_file.exists() and backup_file.is_file():
        backup_file.unlink()
        return True

    return False