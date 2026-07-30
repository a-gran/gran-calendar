from datetime import datetime, timedelta

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent

from tests.calendar_window_helpers import make_window, mouse_event


def test_window_ctrl_click_keeps_multiple_event_selection(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=7)
    second_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    first_event = make_event(event_id="first", start_at=first_start)
    second_event = make_event(event_id="second", start_at=second_start)

    window.events = [first_event, second_event]
    window.refresh_calendar()
    first_rect = window.calendar_grid.rect_for_range(first_event.start_at, first_event.end_at)
    second_rect = window.calendar_grid.rect_for_range(second_event.start_at, second_event.end_at)
    first_point = QPointF(first_rect.left() + 5, first_rect.top() + 5)
    second_point = QPointF(second_rect.left() + 5, second_rect.top() + 5)
    window.calendar_grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, first_point))
    window.calendar_grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, first_point))
    window.calendar_grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, second_point, Qt.ControlModifier))
    window.calendar_grid.mouseReleaseEvent(
        mouse_event(QMouseEvent.MouseButtonRelease, second_point, Qt.ControlModifier)
    )

    assert window.calendar_grid.selected_event_ids_list() == ["first", "second"]


def test_window_deletes_events_from_selected_slots(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=11)
    second_start = first_start + timedelta(days=1)
    first_event = make_event(event_id="first", start_at=first_start)
    second_event = make_event(event_id="second", start_at=second_start)

    window.events = [first_event, second_event]
    window.refresh_calendar()
    window.calendar_grid.selected_slot_datetimes = {first_start, second_start}
    window.delete_keyboard_selection()

    assert window.events == []

    window.undo_last_action()

    assert sorted(event.id for event in window.events) == ["first", "second"]

    window.redo_last_action()

    assert window.events == []


def test_window_gets_event_once_from_multiple_selected_slots(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=11)
    event = make_event(event_id="wide-slot-event", start_at=start_at, duration_minutes=60)
    window.events = [event]
    window.refresh_calendar()
    window.calendar_grid.selected_slot_datetimes = {start_at, start_at + timedelta(minutes=30)}

    assert window.events_for_selected_slots() == [event]


def test_window_restores_multiple_events_with_one_refresh(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_event = make_event(event_id="restore-first")
    second_event = make_event(event_id="restore-second")
    refresh_count = 0
    original_refresh_calendar = window.refresh_calendar

    def counted_refresh_calendar():
        nonlocal refresh_count
        refresh_count += 1
        original_refresh_calendar()

    window.refresh_calendar = counted_refresh_calendar

    window.restore_events([first_event, second_event])

    assert sorted(event.id for event in window.events) == ["restore-first", "restore-second"]
    assert refresh_count == 1


def test_window_deletes_multiple_selected_events(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=13)
    second_start = first_start + timedelta(days=1)
    first_event = make_event(event_id="first-selected", start_at=first_start)
    second_event = make_event(event_id="second-selected", start_at=second_start)

    window.events = [first_event, second_event]
    window.refresh_calendar()
    window.calendar_grid.selected_event_ids = {"first-selected", "second-selected"}
    window.delete_keyboard_selection()

    assert window.events == []

    window.undo_last_action()

    assert sorted(event.id for event in window.events) == ["first-selected", "second-selected"]


def test_window_limits_undo_history_to_ten(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    for index in range(11):
        window.remember_undo(lambda index=index: None, lambda index=index: None)

    assert len(window.history_manager.undo_stack) == 10
