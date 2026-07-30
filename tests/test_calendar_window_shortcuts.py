from datetime import datetime, timedelta

from PySide6.QtGui import QShortcut

from domain.event_status import EVENT_STATUS_IMPORTANT
from tests.calendar_window_helpers import make_window


def test_window_week_navigation_shortcuts(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    shortcuts = {shortcut.key().toString(): shortcut for shortcut in window.findChildren(QShortcut)}
    initial_week = window.week_start

    shortcuts["Ctrl+Left"].activated.emit()

    assert window.week_start == initial_week - timedelta(days=7)

    shortcuts["Ctrl+Right"].activated.emit()

    assert window.week_start == initial_week

    window.week_start = initial_week + timedelta(days=21)
    shortcuts["Ctrl+T"].activated.emit()

    assert window.week_start == datetime.today().date() - timedelta(days=datetime.today().date().weekday())


def test_window_creates_event_from_selected_slot_shortcut(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    shortcuts = {shortcut.key().toString(): shortcut for shortcut in window.findChildren(QShortcut)}
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=7)

    window.calendar_grid.selected_slot_datetimes = {start_at}
    shortcuts["Ctrl+N"].activated.emit()
    window.event_details_title.setText("Shortcut Event")
    window.event_details_status.setCurrentIndex(window.event_details_status.findData(EVENT_STATUS_IMPORTANT))
    window.save_event_details()

    assert len(window.events) == 1
    assert window.events[0].title == "Shortcut Event"
    assert window.events[0].status == EVENT_STATUS_IMPORTANT
    assert window.events[0].start_at == start_at
    assert window.events[0].end_at == start_at + timedelta(minutes=30)


def test_window_create_shortcut_uses_first_selected_slot(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=7)
    second_start = first_start + timedelta(days=1)

    window.calendar_grid.selected_slot_datetimes = {second_start, first_start}
    window.add_event_to_selected_slot()

    assert window.selected_details_ranges == [(first_start, first_start + timedelta(minutes=30))]
    assert window.event_details_save_button.text() == "Create"
