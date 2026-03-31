import argparse
import logging
# Импорт основных функций приложения. Каждый модуль отвечает за отдельную часть.
from app.backup import create_backup
from app.config import (
    APP_NAME,
    APP_VERSION,
    BACKUP_DIR,
    LOG_FILE,
    SCHEDULE_FILE,
    setup_logging,
)
from app.restore import restore_backup
from app.scheduler import (
    add_schedule,
    delete_schedule,
    list_schedules,
    run_due_schedules,
)
from app.storage import delete_backup, list_backups
# Инициализация логгера для CLI-модуля. Через него будут записываться все действия пользователя, выполненные через командную строку.
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Главная точка входа CLI-приложения.

    Здесь происходит:
    1. настройка логирования
    2. создание CLI-интерфейса через argparse
    3. регистрация всех доступных команд
    4. разбор аргументов командной строки
    5. вызов нужной функции в зависимости от команды пользователя
    6. обработка возможных ошибок
    """

    # Настраиваем логирование до выполнения любых действий. Это позволяет фиксировать весь жизненный цикл вызова команды.
    setup_logging()
    # Создаём основной parser командной строки. Через него будут регистрироваться все подкоманды приложения.
    parser = argparse.ArgumentParser(
        description="CLI service for backup and restore operations"
    )

    # Глобальный флаг версии приложения. Позволяет вывести номер версии без выполнения команды.
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    # Создаём контейнер для подкоманд CLI. Например: tuxback backup, tuxback restore, tuxback status
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Create a backup of a directory")
    backup_parser.add_argument("source", help="Path to the source directory")

    restore_parser = subparsers.add_parser("restore", help="Restore a backup archive")
    restore_parser.add_argument("filename", help="Backup filename")
    restore_parser.add_argument("target", help="Path to the restore directory")

    subparsers.add_parser("list", help="List all available backups")
    subparsers.add_parser("status", help="Show project status summary")

    delete_parser = subparsers.add_parser("delete", help="Delete a backup archive")
    delete_parser.add_argument("filename", help="Backup filename to delete")

    schedule_add_parser = subparsers.add_parser(
        "schedule-add", help="Add a scheduled backup task"
    )
    schedule_add_parser.add_argument("source", help="Path to the source directory")
    schedule_add_parser.add_argument(
        "interval", type=int, help="Backup interval in minutes"
    )

    subparsers.add_parser("schedule-list", help="List all scheduled backup tasks")

    schedule_delete_parser = subparsers.add_parser(
        "schedule-delete", help="Delete a scheduled backup task"
    )
    schedule_delete_parser.add_argument("schedule_id", type=int, help="Scheduled task ID")

    subparsers.add_parser(
        "run-scheduler", help="Run all due scheduled backup tasks"
    )

    args = parser.parse_args()
    logger.info("CLI command started: %s", args.command)
    logger.debug("CLI arguments namespace: %s", vars(args))

    try:
        if args.command == "backup":
            logger.debug("Executing backup command for source=%s", args.source)
            archive_name = create_backup(args.source)
            print(f"Backup created: {archive_name}")

        elif args.command == "restore":
            logger.debug(
                "Executing restore command for filename=%s target=%s",
                args.filename,
                args.target,
            )
            restore_path = restore_backup(args.filename, args.target)
            print(f"Backup restored to: {restore_path}")

        elif args.command == "list":
            logger.debug("Executing list command")
            backups = list_backups()

            if not backups:
                print("No backups found.")
            else:
                print("Available backups:")
                for backup in backups:
                    print(f"- {backup}")

        elif args.command == "status":
            logger.debug("Executing status command")
            backups = list_backups()
            schedules = list_schedules()
            enabled_schedules = [
                schedule for schedule in schedules if schedule.get("enabled", True)
            ]

            print(f"{APP_NAME} status:")
            print(f"- Version: {APP_VERSION}")
            print(f"- Total backups: {len(backups)}")
            print(f"- Total schedules: {len(schedules)}")
            print(f"- Enabled schedules: {len(enabled_schedules)}")
            print(f"- Backup directory: {BACKUP_DIR}")
            print(f"- Schedule file: {SCHEDULE_FILE}")
            print(f"- Log file: {LOG_FILE}")

        elif args.command == "delete":
            logger.debug("Executing delete command for filename=%s", args.filename)
            deleted = delete_backup(args.filename)

            if deleted:
                print(f"Backup deleted: {args.filename}")
            else:
                print(f"Backup not found: {args.filename}")

        elif args.command == "schedule-add":
            logger.debug(
                "Executing schedule-add command for source=%s interval=%s",
                args.source,
                args.interval,
            )
            schedule = add_schedule(args.source, args.interval)
            print(f"Schedule added: {schedule}")

        elif args.command == "schedule-list":
            logger.debug("Executing schedule-list command")
            schedules = list_schedules()

            if not schedules:
                print("No scheduled tasks found.")
            else:
                print("Scheduled backup tasks:")
                for schedule in schedules:
                    print(
                        f"- ID: {schedule['id']}, "
                        f"Source: {schedule['source']}, "
                        f"Interval: {schedule['interval_minutes']} min, "
                        f"Enabled: {schedule['enabled']}, "
                        f"Last run: {schedule.get('last_run')}"
                    )

        elif args.command == "schedule-delete":
            logger.debug(
                "Executing schedule-delete command for schedule_id=%s",
                args.schedule_id,
            )
            deleted = delete_schedule(args.schedule_id)

            if deleted:
                print(f"Schedule deleted: {args.schedule_id}")
            else:
                print(f"Schedule not found: {args.schedule_id}")

        elif args.command == "run-scheduler":
            logger.debug("Executing run-scheduler command")
            results = run_due_schedules()

            if not results:
                print("No scheduled tasks are due right now.")
            else:
                print("Executed scheduled backup tasks:")
                for result in results:
                    print(
                        f"- ID: {result['id']}, "
                        f"Source: {result['source']}, "
                        f"Archive: {result['archive']}, "
                        f"Run at: {result['run_at']}"
                    )

    except Exception as error:
    # Ошибки CLI пишем в лог. Для пользователя выводим короткое сообщение.
        logger.error("CLI command failed: %s", error)
        logger.debug("CLI traceback details", exc_info=True)
        print(f"Error: {error}")

    # Ошибки CLI пишем в лог. Для пользователя выводим короткое сообщение.
if __name__ == "__main__":
    main()