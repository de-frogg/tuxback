import tarfile
from datetime import datetime
from pathlib import Path

from app.config import TIME_FORMAT
from app.storage import init_storage, get_backup_path


def create_backup(source_path: str) -> str:
    """
    Создаёт резервную копию указанной директории.

    :param source_path: путь к директории для резервного копирования
    :return: имя созданного архива
    """

    init_storage()

    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    if not source.is_dir():
        raise ValueError("Backup source must be a directory")

    timestamp = datetime.now().strftime(TIME_FORMAT)

    archive_name = f"{source.name}_{timestamp}.tar.gz"

    archive_path = get_backup_path(archive_name)

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source, arcname=source.name)

    return archive_name