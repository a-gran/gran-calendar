import sqlite3
from datetime import datetime

from domain.event_status import EVENT_STATUS_DONE, EVENT_STATUS_IMPORTANT, EVENT_STATUS_NORMAL
from storage.event_storage import EventStorage, get_database_path


def test_default_database_path_uses_xdg_data_home(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    assert get_database_path() == tmp_path / "gran-calendar" / "calendar.db"


def test_storage_creates_database_directory(tmp_path):
    database_path = tmp_path / "nested" / "calendar.db"

    EventStorage(database_path)

    assert database_path.exists()


def test_storage_migrates_legacy_database(tmp_path):
    legacy_database_path = tmp_path / "old" / "calendar.db"
    database_path = tmp_path / "new" / "calendar.db"
    legacy_database_path.parent.mkdir()
    with sqlite3.connect(legacy_database_path) as connection:
        connection.execute("CREATE TABLE marker (id TEXT PRIMARY KEY)")

    EventStorage(database_path, legacy_database_path=legacy_database_path)

    assert database_path.exists()
    assert not legacy_database_path.exists()


def test_storage_saves_loads_and_sorts_events(tmp_path, make_event):
    storage = EventStorage(tmp_path / "calendar.db")
    later_event = make_event(event_id="later", start_at=datetime(2026, 7, 27, 11, 0))
    earlier_event = make_event(event_id="earlier", start_at=datetime(2026, 7, 27, 9, 0))

    storage.save_event(later_event)
    storage.save_event(earlier_event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert [event.id for event in loaded_events] == ["earlier", "later"]


def test_storage_updates_event_by_id(tmp_path, make_event):
    storage = EventStorage(tmp_path / "calendar.db")
    event = make_event(event_id="same-id", title="Old")

    storage.save_event(event)
    event.title = "New"
    event.note = "New note"
    storage.save_event(event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert len(loaded_events) == 1
    assert loaded_events[0].title == "New"
    assert loaded_events[0].note == "New note"


def test_storage_saves_event_status(tmp_path, make_event):
    storage = EventStorage(tmp_path / "calendar.db")
    event = make_event(event_id="status", start_at=datetime(2026, 7, 27, 10, 0))
    event.status = EVENT_STATUS_IMPORTANT

    storage.save_event(event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert loaded_events[0].status == EVENT_STATUS_IMPORTANT


def test_storage_migrates_old_database_without_status(tmp_path, make_event):
    database_path = tmp_path / "calendar.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                note TEXT NOT NULL,
                start_at TEXT NOT NULL,
                end_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    storage = EventStorage(database_path)
    event = make_event(event_id="migrated", start_at=datetime(2026, 7, 27, 10, 0))

    storage.save_event(event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert loaded_events[0].status == EVENT_STATUS_NORMAL


def test_storage_updates_event_status(tmp_path, make_event):
    storage = EventStorage(tmp_path / "calendar.db")
    event = make_event(event_id="status-update", start_at=datetime(2026, 7, 27, 10, 0))

    storage.save_event(event)
    event.status = EVENT_STATUS_DONE
    storage.save_event(event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert loaded_events[0].status == EVENT_STATUS_DONE


def test_storage_deletes_event(tmp_path, make_event):
    storage = EventStorage(tmp_path / "calendar.db")
    event = make_event()

    storage.save_event(event)
    storage.delete_event(event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert loaded_events == []


def test_storage_loads_only_events_inside_range(tmp_path, make_event):
    storage = EventStorage(tmp_path / "calendar.db")
    inside_event = make_event(event_id="inside", start_at=datetime(2026, 7, 27, 12, 0))
    outside_event = make_event(event_id="outside", start_at=datetime(2026, 7, 28, 12, 0))

    storage.save_event(inside_event)
    storage.save_event(outside_event)

    loaded_events = storage.load_events_between(datetime(2026, 7, 27), datetime(2026, 7, 28))

    assert [event.id for event in loaded_events] == ["inside"]
