import shutil
import sqlite3
from datetime import datetime
from os import environ
from pathlib import Path

from domain.event import Event
from domain.event_status import EVENT_STATUS_NORMAL

APPLICATION_DIRECTORY_NAME = "calendar-planner"
DATABASE_FILE_NAME = "calendar.db"
LEGACY_DATABASE_PATH = Path(__file__).resolve().parent.parent / DATABASE_FILE_NAME


def get_application_data_directory():
    xdg_data_home = environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / APPLICATION_DIRECTORY_NAME
    return Path.home() / ".local" / "share" / APPLICATION_DIRECTORY_NAME


def get_database_path():
    return get_application_data_directory() / DATABASE_FILE_NAME


DATABASE_PATH = get_database_path()


def ensure_database_directory(database_path):
    Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def migrate_legacy_database(database_path, legacy_database_path):
    database_path = Path(database_path).expanduser()
    legacy_database_path = Path(legacy_database_path).expanduser()
    if database_path.exists() or not legacy_database_path.exists():
        return
    ensure_database_directory(database_path)
    shutil.move(str(legacy_database_path), str(database_path))


class EventStorage:
    def __init__(self, database_path, legacy_database_path=None):
        self.database_path = Path(database_path).expanduser()
        if legacy_database_path is None and self.database_path == DATABASE_PATH:
            legacy_database_path = LEGACY_DATABASE_PATH
        if legacy_database_path is not None:
            migrate_legacy_database(self.database_path, legacy_database_path)
        ensure_database_directory(self.database_path)
        self.initialize_database()

    def connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_database(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    note TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'normal'
                )
                """
            )
            columns = connection.execute("PRAGMA table_info(events)").fetchall()
            column_names = {column["name"] for column in columns}
            if "status" not in column_names:
                connection.execute(
                    "ALTER TABLE events ADD COLUMN status TEXT NOT NULL DEFAULT 'normal'",
                )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at)")

    def save_event(self, event):
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO events (
                    id,
                    title,
                    note,
                    start_at,
                    end_at,
                    created_at,
                    updated_at,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    note = excluded.note,
                    start_at = excluded.start_at,
                    end_at = excluded.end_at,
                    updated_at = excluded.updated_at,
                    status = excluded.status
                """,
                (
                    event.id,
                    event.title,
                    event.note,
                    event.start_at.isoformat(),
                    event.end_at.isoformat(),
                    event.created_at.isoformat(),
                    event.updated_at.isoformat(),
                    event.status,
                ),
            )

    def load_events_between(self, start_at, end_at):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    note,
                    start_at,
                    end_at,
                    created_at,
                    updated_at,
                    status
                FROM events
                WHERE start_at < ? AND end_at > ?
                ORDER BY start_at, created_at
                """,
                (end_at.isoformat(), start_at.isoformat()),
            ).fetchall()
        return [self.event_from_row(row) for row in rows]

    def delete_event(self, event):
        with self.connect() as connection:
            connection.execute("DELETE FROM events WHERE id = ?", (event.id,))

    def event_from_row(self, row):
        return Event(
            id=row["id"],
            title=row["title"],
            note=row["note"],
            start_at=datetime.fromisoformat(row["start_at"]),
            end_at=datetime.fromisoformat(row["end_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            status=row["status"] or EVENT_STATUS_NORMAL,
        )
