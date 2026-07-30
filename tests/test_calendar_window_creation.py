from datetime import datetime, timedelta

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent

from domain.event_status import EVENT_STATUS_IMPORTANT
from tests.calendar_window_helpers import make_window, mouse_event


def test_window_creates_event_from_selection(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    end_at = start_at + timedelta(minutes=60)

    window.add_event_from_selection(start_at, end_at)
    window.event_details_title.setText("Panel Event")
    window.event_details_note.setPlainText("Panel Note")
    window.event_details_status.setCurrentIndex(window.event_details_status.findData(EVENT_STATUS_IMPORTANT))
    window.save_event_details()

    assert len(window.events) == 1
    assert window.events[0].title == "Panel Event"
    assert window.events[0].note == "Panel Note"
    assert window.events[0].status == EVENT_STATUS_IMPORTANT
    assert window.events[0].start_at == start_at
    assert window.events[0].end_at == end_at


def test_window_drag_selection_prepares_side_panel_creation(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    grid = window.calendar_grid
    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    third_slot_point = QPointF(grid.time_axis_width + 10, grid.y_for_slot_index(2) + 10)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, first_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, third_slot_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, third_slot_point))

    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=6)
    end_at = start_at + timedelta(minutes=90)

    assert window.event_details_save_button.text() == "Create"
    assert window.selected_details_ranges == [(start_at, end_at)]
    assert [slot.time().strftime("%H:%M") for slot in grid.selected_slots()] == ["06:00", "06:30", "07:00"]


def test_window_diagonal_drag_selection_prepares_multiple_side_panel_ranges(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    grid = window.calendar_grid
    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    second_day_left = grid.day_column_rect(1).left()
    third_slot_point = QPointF(second_day_left + 10, grid.y_for_slot_index(2) + 10)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, first_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, third_slot_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, third_slot_point))

    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=6)
    first_end = first_start + timedelta(minutes=90)
    second_start = first_start + timedelta(days=1)
    second_end = second_start + timedelta(minutes=90)

    assert window.event_details_save_button.text() == "Create"
    assert window.selected_details_ranges == [(first_start, first_end), (second_start, second_end)]
    assert len(grid.selected_slots()) == 6


def test_window_creates_same_event_for_multiple_ranges(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=9)
    ranges = [
        (first_start, first_start + timedelta(minutes=30)),
        (first_start + timedelta(days=1), first_start + timedelta(days=1, minutes=30)),
    ]

    window.add_events_from_ranges(ranges)
    window.event_details_title.setText("Repeat")
    window.event_details_status.setCurrentIndex(window.event_details_status.findData(EVENT_STATUS_IMPORTANT))
    window.save_event_details()

    assert len(window.events) == 2
    assert [event.title for event in window.events] == ["Repeat", "Repeat"]
    assert [event.status for event in window.events] == [EVENT_STATUS_IMPORTANT, EVENT_STATUS_IMPORTANT]
    assert [event.start_at for event in window.events] == [ranges[0][0], ranges[1][0]]

    window.undo_last_action()

    assert window.events == []

    window.redo_last_action()

    assert len(window.events) == 2
