import json
from pathlib import Path
from typing import Any, Dict, List

from app.config import SCHEDULE_FILE


def load_schedules() -> List[Dict[str, Any]]:
    """
    Загружает список задач расписания из JSON-файла.
    Если файл не существует, возвращает пустой список.
    """
    if not SCHEDULE_FILE.exists():
        return []

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_schedules(schedules: List[Dict[str, Any]]) -> None: #  Сохраняет список задач расписания в JSON-файл.
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedules, file, indent=4, ensure_ascii=False)


def add_schedule(source: str, interval_minutes: int) -> Dict[str, Any]:
    """
    Добавляет новую задачу резервного копирования в расписание.
    :param source: путь к исходной директории
    :param interval_minutes: интервал запуска в минутах
    :return: созданная задача
    """
    schedules = load_schedules()

    new_schedule = {
        "id": len(schedules) + 1,
        "source": source,
        "interval_minutes": interval_minutes,
        "enabled": True
    }

    schedules.append(new_schedule)
    save_schedules(schedules)

    return new_schedule


def list_schedules() -> List[Dict[str, Any]]:
    """
    Возвращает список всех задач расписания.
    """
    return load_schedules()


def delete_schedule(schedule_id: int) -> bool:
    """
    Удаляет задачу расписания по идентификатору.
    :param schedule_id: ID задачи
    :return: True, если задача удалена, иначе False
    """
    schedules = load_schedules()
    updated_schedules = [
        schedule for schedule in schedules
        if schedule["id"] != schedule_id
    ]

    if len(updated_schedules) == len(schedules):
        return False

    save_schedules(updated_schedules)
    return True