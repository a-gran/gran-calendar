from datetime import datetime, timedelta

from tests.calendar_window_helpers import make_window


def test_window_resizes_event_with_undo_and_redo(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=16)
    event = make_event(event_id="resize-window", start_at=start_at, duration_minutes=60)

    window.events = [event]
    window.refresh_calendar()
    window.resize_event_from_grid(event, event.start_at, event.end_at + timedelta(minutes=30))

    assert event.end_at == start_at + timedelta(minutes=90)

    window.undo_last_action()

    assert event.end_at == start_at + timedelta(minutes=60)

    window.redo_last_action()

    assert event.end_at == start_at + timedelta(minutes=90)


def test_window_rejects_resize_overlapping_another_event(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=17)
    event = make_event(event_id="blocked-resize", start_at=start_at, duration_minutes=60)
    blocker = make_event(event_id="blocker", start_at=start_at + timedelta(hours=1), duration_minutes=30)

    window.events = [event, blocker]
    window.refresh_calendar()
    window.resize_event_from_grid(event, event.start_at, blocker.end_at)

    assert event.end_at == start_at + timedelta(minutes=60)


def test_window_moves_event_with_undo_and_redo(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=18)
    event = make_event(event_id="move-window", start_at=start_at, duration_minutes=60)
    moved_start = start_at + timedelta(days=1, minutes=30)

    window.events = [event]
    window.refresh_calendar()
    window.resize_event_from_grid(event, moved_start, moved_start + timedelta(minutes=60))

    assert event.start_at == moved_start
    assert event.end_at == moved_start + timedelta(minutes=60)

    window.undo_last_action()

    assert event.start_at == start_at
    assert event.end_at == start_at + timedelta(minutes=60)

    window.redo_last_action()

    assert event.start_at == moved_start
    assert event.end_at == moved_start + timedelta(minutes=60)


def test_window_rejects_move_overlapping_another_event(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=18)
    target_start = start_at + timedelta(days=1)
    event = make_event(event_id="blocked-move", start_at=start_at, duration_minutes=60)
    blocker = make_event(event_id="move-blocker", start_at=target_start, duration_minutes=60)

    window.events = [event, blocker]
    window.refresh_calendar()
    window.resize_event_from_grid(event, target_start, target_start + timedelta(minutes=60))

    assert event.start_at == start_at
    assert event.end_at == start_at + timedelta(minutes=60)
