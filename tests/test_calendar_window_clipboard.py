from datetime import datetime, timedelta

from domain.event_status import EVENT_STATUS_DONE
from tests.calendar_window_helpers import make_window


def test_window_copies_and_pastes_event(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=9)
    event = make_event(event_id="source", start_at=start_at, duration_minutes=60)

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.copy_keyboard_selection()

    assert window.copied_event.id == "source"

    window.paste_copied_event_to_slots([start_at + timedelta(days=1)])

    assert len(window.events) == 2

    window.paste_copied_event_to_slots([start_at])

    assert len(window.events) == 2


def test_window_cut_undo_and_redo(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=10)
    event = make_event(event_id="cut", start_at=start_at)

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.cut_keyboard_selection()

    assert window.events == []
    assert window.copied_event.id == "cut"

    window.undo_last_action()

    assert len(window.events) == 1

    window.redo_last_action()

    assert window.events == []


def test_window_copies_single_event_from_selected_slot(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=12)
    event = make_event(event_id="slot-copy", start_at=start_at)

    window.events = [event]
    window.refresh_calendar()
    window.calendar_grid.selected_slot_datetimes = {start_at}
    window.copy_keyboard_selection()

    assert window.copied_event.id == "slot-copy"


def test_window_pastes_copied_event_to_selected_slots(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=14)
    first_target = start_at + timedelta(days=1)
    second_target = start_at + timedelta(days=2)
    event = make_event(event_id="keyboard-copy", start_at=start_at, duration_minutes=60)
    event.status = EVENT_STATUS_DONE

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.copy_keyboard_selection()
    window.calendar_grid.selected_slot_datetimes = {first_target, second_target}
    window.paste_keyboard_selection()

    assert len(window.events) == 3
    assert sorted(copied.start_at for copied in window.events if copied.id != "keyboard-copy") == [
        first_target,
        second_target,
    ]
    assert {copied.status for copied in window.events if copied.id != "keyboard-copy"} == {EVENT_STATUS_DONE}

    window.undo_last_action()

    assert window.events == [event]


def test_window_keyboard_paste_overwrites_busy_selected_slots(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=15)
    first_target = start_at + timedelta(days=1)
    second_target = start_at + timedelta(days=2)
    event = make_event(event_id="busy-source", start_at=start_at, duration_minutes=30)

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.copy_keyboard_selection()
    window.calendar_grid.selected_slot_datetimes = {start_at, first_target, second_target}
    window.paste_keyboard_selection()

    assert len(window.events) == 3
    assert window.find_event_by_id(window.events, "busy-source") is None
    assert sorted(copied.start_at for copied in window.events) == [
        start_at,
        first_target,
        second_target,
    ]

    window.undo_last_action()

    assert window.events == [event]

    window.redo_last_action()

    assert len(window.events) == 3
    assert window.find_event_by_id(window.events, "busy-source") is None
