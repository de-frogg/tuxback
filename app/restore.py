import logging
import tarfile
from pathlib import Path
from app.storage import backup_exists, get_backup_path

logger = logging.getLogger(__name__)

def _is_within_directory(base: Path, target: Path) -> bool:
    """
    Проверяет, что путь target находится внутри base.

    Это критически важная функция безопасности.
    Она защищает от атак типа:
    - Path Traversal
    - попыток распаковки файлов вне целевой директории

    Пример атаки:
    ../../../etc/passwd

    :param base: базовая директория (куда распаковываем)
    :param target: путь файла из архива
    :return: True если безопасно, иначе False
    """
    try:
        # Проверяем, что target лежит внутри base
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def restore_backup(filename: str, target_path: str) -> Path:
    """
    Восстанавливает резервную копию из архива.

    Алгоритм работы:
    1. Проверка существования архива
    2. Определение целевой директории
    3. Проверка безопасности всех файлов в архиве
    4. Распаковка архива
    5. Логирование результата

    :param filename: имя архива (например backup_20260315.tar.gz)
    :param target_path: путь, куда нужно восстановить данные
    :return: путь к директории восстановления
    """

    logger.info("Starting restore: filename=%s target=%s", filename, target_path)
    # Проверяем, существует ли архив
    if not backup_exists(filename):
        logger.error("Backup file not found: %s", filename)
        raise FileNotFoundError(f"Backup file not found: {filename}")

    archive_path = get_backup_path(filename)
    # Преобразуем путь назначения
    target = Path(target_path).expanduser().resolve()
    # Создаёт директорию, если её нет
    target.mkdir(parents=True, exist_ok=True)

    logger.debug("Restore archive path: %s", archive_path)
    logger.debug("Restore target path: %s", target)
    # Открывает архив
    with tarfile.open(archive_path, "r:gz") as tar:
    # Получаем список файлов внутри архива
        members = tar.getmembers()
        logger.debug("Archive contains %d member(s)", len(members))

        for member in members:
            destination = target / member.name
        # Проверяет, что файл не выходит за пределы target
            if not _is_within_directory(target, destination):
                logger.error("Unsafe archive member detected: %s", member.name)
                raise ValueError(f"Unsafe archive member detected: {member.name}")

        tar.extractall(path=target, members=members)
    # Логирует  успешное восстановление
    logger.info(
        "Backup restored successfully: filename=%s target=%s extracted_members=%d",
        filename,
        target,
        len(members),
    )
    return target