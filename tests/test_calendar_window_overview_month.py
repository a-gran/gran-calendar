from datetime import date, datetime

from PySide6.QtCore import QDate

from tests.calendar_window_helpers import make_window, overview_event_text
from ui.calendar_dates import month_names


def test_window_overview_selects_month_and_shows_month_events(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = date(window.week_start.year, 9, 12)
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=10)
    event = make_event(event_id="month-overview", title="Month Event", start_at=event_start, duration_minutes=90)
    window.storage.load_events_between = lambda start_at, end_at: [event] if start_at <= event.start_at < end_at else []

    window.show_month_overview()
    window.year_spinbox.setValue(selected_date.year)
    window.select_month_in_year_overview(selected_date.month)

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert window.month_day_title.text() == f"{month_names()[selected_date.month - 1]} {selected_date.year}"
    assert window.month_calendar.selectedDate() == QDate(selected_date.year, selected_date.month, 1)
    assert window.month_calendar.minimumDate() == QDate(selected_date.year, selected_date.month, 1)
    assert window.month_calendar.maximumDate() == QDate(selected_date.year, selected_date.month, 30)
    assert window.year_month_buttons[selected_date.month - 1].isChecked()
    assert "10:00 - 11:30  Month Event" in overview_event_text(window, 0)
