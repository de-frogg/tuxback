import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from app.backup import create_backup
from app.config import SCHEDULE_FILE

logger = logging.getLogger(__name__)


def load_schedules() -> List[Dict[str, Any]]:
    """
    Загружает список задач планировщика из JSON-файла.

    Если файл расписаний ещё не существует,
    функция возвращает пустой список.

    :return: список задач планировщика
    """
    # Если файл ещё не создан, значит задач пока нет.
    if not SCHEDULE_FILE.exists():
        logger.info("Schedule file does not exist yet: %s", SCHEDULE_FILE)
        return []
    # Открывает JSON-файл и загружает его содержимое в память.
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
        schedules = json.load(file)

    logger.info("Loaded %d scheduled task(s)", len(schedules))
    logger.debug("Schedule payload: %s", schedules)
    return schedules


def save_schedules(schedules: List[Dict[str, Any]]) -> None:
    """
    Сохраняет список задач планировщика в JSON-файл.

    :param schedules: список задач, который нужно сохранить
    """
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedules, file, indent=4, ensure_ascii=False)

    logger.info("Saved %d scheduled task(s)", len(schedules))
    logger.debug("Schedule file updated at: %s", SCHEDULE_FILE)


def add_schedule(source: str, interval_minutes: int) -> Dict[str, Any]:
    """
    Добавляет новую задачу резервного копирования.

    Перед добавлением выполняются проверки:
    1. существует ли исходная директория
    2. является ли путь директорией
    3. больше ли интервал нуля
    4. нет ли уже аналогичной активной задачи

    :param source: директория, которую нужно архивировать
    :param interval_minutes: интервал запуска в минутах
    :return: созданная задача планировщика
    """
    # Преобразует путь к стандартному абсолютному виду.
    source_path = Path(source).expanduser().resolve()
    logger.info(
        "Adding schedule: source=%s interval_minutes=%s",
        source_path,
        interval_minutes,
    )
    # Проверяет, существует ли директория-источник.
    if not source_path.exists():
        logger.error("Schedule source path does not exist: %s", source_path)
        raise FileNotFoundError(f"Source path does not exist: {source_path}")
    # Проверяет, что пользователь передал директорию, а не файл.
    if not source_path.is_dir():
        logger.error("Schedule source path is not a directory: %s", source_path)
        raise ValueError("Schedule source must be a directory")
    # Интервал должен быть положительным числом.
    if interval_minutes <= 0:
        logger.error("Invalid schedule interval: %s", interval_minutes)
        raise ValueError("Interval must be greater than 0 minutes")
    # Загружаем текущий список задач.
    schedules = load_schedules()
    # Проверяет, не существует ли уже активная задача с тем же источником и тем же интервалом.
    for schedule in schedules:
        if (
            schedule["source"] == str(source_path)
            and schedule["interval_minutes"] == interval_minutes
            and schedule.get("enabled", True)
        ):
            logger.warning(
                "Duplicate schedule detected: source=%s interval=%s existing_id=%s",
                source_path,
                interval_minutes,
                schedule["id"],
            )
            raise ValueError(
                "An active schedule with the same source and interval already exists"
            )

    next_id = max((schedule["id"] for schedule in schedules), default=0) + 1
    # Формирует новую задачу.
    new_schedule = {
        "id": next_id,
        "source": str(source_path),
        "interval_minutes": interval_minutes,
        "enabled": True,
        "last_run": None,
    }
    # Добавляет задачу в список и сохраняем его.
    schedules.append(new_schedule)
    save_schedules(schedules)
    logger.info("Added new schedule: %s", new_schedule)
    return new_schedule


def list_schedules() -> List[Dict[str, Any]]:
    """
    Возвращает список всех задач планировщика.

    :return: список задач
    """
    schedules = load_schedules()
    logger.info("Returning %d scheduled task(s)", len(schedules))
    return schedules


def delete_schedule(schedule_id: int) -> bool:
    """
    Удаляет задачу по её идентификатору.

    :param schedule_id: ID задачи
    :return: True если задача удалена, иначе False
    """
    schedules = load_schedules()
    # Оставляет только те задачи, чей ID не совпадает с удаляемым.
    updated_schedules = [
        schedule for schedule in schedules if schedule["id"] != schedule_id
    ]
    # Если длина списка не изменилась, значит задача не была найдена.
    if len(updated_schedules) == len(schedules):
        logger.warning("Schedule not found for deletion: %s", schedule_id)
        return False
    # Сохраняет обновлённый список задач.
    save_schedules(updated_schedules)
    logger.info("Deleted schedule with ID: %s", schedule_id)
    return True

def run_due_schedules() -> List[Dict[str, Any]]:
    """
    Запускает все активные задачи, срок выполнения которых уже наступил.

    Логика работы:
    1. загрузить список задач
    2. проверить, какие задачи активны
    3. определить, наступило ли время их запуска
    4. создать резервные копии для задач, которые нужно выполнить
    5. обновить поле last_run
    6. сохранить изменения в schedules.json

    :return: список результатов выполненных задач
    """
    schedules = load_schedules()
    results: List[Dict[str, Any]] = []
    now = datetime.now()
    updated = False

    logger.info("Scheduler run started at %s", now.isoformat(timespec="seconds"))
    logger.debug("Evaluating %d schedule(s)", len(schedules))
    # Последовательно проверяем каждую задачу.
    for schedule in schedules:
        # Если задача отключена — пропускаем её.
        if not schedule.get("enabled", True):
            logger.info("Skipping disabled schedule ID: %s", schedule["id"])
            continue

        last_run_raw = schedule.get("last_run")
        interval_minutes = schedule["interval_minutes"]
        should_run = False
        next_run_iso = None
    # Если задача никогда не запускалась, значит её нужно выполнить сразу.
        if last_run_raw is None:
            should_run = True
        else:
    # Иначе вычисляем время следующего запуска.
            last_run = datetime.fromisoformat(last_run_raw)
            next_run = last_run + timedelta(minutes=interval_minutes)
            next_run_iso = next_run.isoformat(timespec="seconds")
            should_run = now >= next_run

        logger.debug(
            "Schedule evaluation: id=%s source=%s interval=%s last_run=%s next_run=%s should_run=%s",
            schedule["id"],
            schedule["source"],
            interval_minutes,
            last_run_raw,
            next_run_iso,
            should_run,
        )
        # Если время ещё не пришло — пропускаем задачу.
        if not should_run:
            continue
        # Выполняет резервное копирование для задачи.
        archive_name = create_backup(schedule["source"])
        # Обновляет время последнего запуска.
        schedule["last_run"] = now.isoformat(timespec="seconds")
        updated = True
        # Формирует результат выполнения.
        result = {
            "id": schedule["id"],
            "source": schedule["source"],
            "archive": archive_name,
            "run_at": schedule["last_run"],
        }
        results.append(result)
        logger.info("Executed scheduled backup: %s", result)
    # Если были изменения — сохраняем обновлённое расписание.
    if updated:
        save_schedules(schedules)

    logger.info("Scheduler run completed: executed=%d", len(results))
    return results