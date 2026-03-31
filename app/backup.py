import logging
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Tuple

from app.config import TIME_FORMAT
from app.storage import get_backup_path, init_storage
# Инициализация логгера для текущего модуля.
# Через него записываются события создания резервных копий.
logger = logging.getLogger(__name__)


def _collect_source_stats(source: Path) -> Tuple[int, int, int]:
    """
    Подсчитывает статистику по исходной директории.

    Функция проходит по всем вложенным объектам и определяет:
    - количество файлов
    - количество директорий
    - суммарный размер файлов в байтах

    Эти данные используются для:
    - детального логирования
    - диагностики
    - понимания объёма резервной копии

    :param source: путь к исходной директории
    :return: кортеж (количество_файлов, количество_директорий, общий_размер_в_байтах)
    """
    file_count = 0
    dir_count = 0
    total_bytes = 0
    # Обходим все вложенные элементы в исходной директории
    for path in source.rglob("*"):
        if path.is_dir():
            dir_count += 1
        elif path.is_file():
            file_count += 1
            try:
                total_bytes += path.stat().st_size
            except OSError:
        # В редких случаях размер файла может быть недоступен.
        # Не прерываем выполнение, а просто логируем ситуацию.
                logger.debug("Could not read file size: %s", path, exc_info=True)

    return file_count, dir_count, total_bytes


def create_backup(source_path: str) -> str:
    """
    Создаёт архив резервной копии для указанной директории.

    Алгоритм работы:
    1. Инициализация структуры хранения
    2. Проверка существования исходной директории
    3. Подсчёт статистики по исходным данным
    4. Генерация имени архива с меткой времени
    5. Создание .tar.gz архива
    6. Логирование результата

    :param source_path: путь к директории, которую нужно архивировать
    :return: имя созданного архива
    """
    # Убедится, что все директории приложения существуют.
    # К примеру, каталог для хранения бэкапов должен быть создан заранее.
    init_storage()
    # Преобразует путь в абсолютный и разворачиваем ~ если он был передан.
    source = Path(source_path).expanduser().resolve()
    logger.info("Starting backup: source=%s", source)
    # Проверяет, существует ли исходный путь.
    if not source.exists():
        logger.error("Backup source path does not exist: %s", source)
        raise FileNotFoundError(f"Source path does not exist: {source}")
    # Проверяет, что пользователь передал именно директорию.
    if not source.is_dir():
        logger.error("Backup source is not a directory: %s", source)
        raise ValueError("Backup source must be a directory")
    # Собирает статистику для логов.
    file_count, dir_count, total_bytes = _collect_source_stats(source)
    logger.debug(
        "Backup source stats: files=%d dirs=%d size_bytes=%d",
        file_count,
        dir_count,
        total_bytes,
    )
    # Формируем имя архива на основе имени директории и текущего времени.
    # Например: data_20260331_154501.tar.gz
    timestamp = datetime.now().strftime(TIME_FORMAT)
    archive_name = f"{source.name}_{timestamp}.tar.gz"
    # Получает  полный путь, куда будет сохранён архив.
    archive_path = get_backup_path(archive_name)

    logger.debug("Archive name generated: %s", archive_name)
    logger.debug("Archive path resolved: %s", archive_path)

    # Создаём архив в формате tar.gz.
    # arcname=source.name позволяет сохранить в архиве красивое имя директории, а не полный абсолютный путь.
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source, arcname=source.name)
    # После создания получаем фактический размер архива.
    archive_size = archive_path.stat().st_size if archive_path.exists() else 0
    # Логируем итог операции.
    logger.info(
        "Backup created successfully: archive=%s size_bytes=%d source_files=%d source_dirs=%d",
        archive_path,
        archive_size,
        file_count,
        dir_count,
    )
    return archive_name