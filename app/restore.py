import tarfile
from pathlib import Path

from app.storage import backup_exists, get_backup_path


def restore_backup(filename: str, target_path: str) -> Path:
    """
    Восстанавливает резервную копию в указанную директорию.

    :param filename: имя файла резервной копии
    :param target_path: путь для восстановления
    :return: путь к директории восстановления
    """

    if not backup_exists(filename):
        raise FileNotFoundError(f"Backup file not found: {filename}")

    archive_path = get_backup_path(filename)
    target = Path(target_path)

    target.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=target)

    return target