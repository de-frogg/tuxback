from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
SCHEDULE_FILE = BASE_DIR / "schedules.json"
TIME_FORMAT = "%Y%m%d_%H%M%S"


def ensure_directories() -> None:
    """
    Создаёт необходимые директории для работы приложения,
    если они ещё не существуют.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)