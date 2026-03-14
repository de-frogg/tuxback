import argparse

from app.backup import create_backup
from app.restore import restore_backup
from app.storage import list_backups, delete_backup


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI service for backup and restore operations"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser(
        "backup",
        help="Create a backup of a directory"
    )
    backup_parser.add_argument(
        "source",
        help="Path to the source directory"
    )

    restore_parser = subparsers.add_parser(
        "restore",
        help="Restore a backup archive"
    )
    restore_parser.add_argument(
        "filename",
        help="Backup filename"
    )
    restore_parser.add_argument(
        "target",
        help="Path to the restore directory"
    )

    subparsers.add_parser(
        "list",
        help="List all available backups"
    )

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a backup archive"
    )
    delete_parser.add_argument(
        "filename",
        help="Backup filename to delete"
    )

    args = parser.parse_args()

    try:
        if args.command == "backup":
            archive_name = create_backup(args.source)
            print(f"Backup created: {archive_name}")

        elif args.command == "restore":
            restore_path = restore_backup(args.filename, args.target)
            print(f"Backup restored to: {restore_path}")

        elif args.command == "list":
            backups = list_backups()

            if not backups:
                print("No backups found.")
            else:
                print("Available backups:")
                for backup in backups:
                    print(f"- {backup}")

        elif args.command == "delete":
            deleted = delete_backup(args.filename)

            if deleted:
                print(f"Backup deleted: {args.filename}")
            else:
                print(f"Backup not found: {args.filename}")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()