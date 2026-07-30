from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

from ui.calendar_window import CalendarWindow


def overview_event_text(window, index):
    return window.month_day_events.itemWidget(window.month_day_events.item(index)).text_label.text()


def mouse_event(event_type, point, modifiers=Qt.NoModifier):
    return QMouseEvent(event_type, point, point, Qt.LeftButton, Qt.LeftButton, modifiers)


def make_window(qt_app, tmp_path, monkeypatch):
    import ui.calendar_window as calendar_window_module

    monkeypatch.setattr(calendar_window_module, "DATABASE_PATH", tmp_path / "calendar.db")
    window = CalendarWindow()
    window.storage.save_event = lambda event: None
    window.storage.delete_event = lambda event: None
    window.events = []
    window.refresh_calendar()
    return window
