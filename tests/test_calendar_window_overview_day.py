from datetime import datetime, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QTableView

from tests.calendar_window_helpers import make_window, overview_event_text
from ui.calendar_dates import day_name


def key_press(widget, key):
    QApplication.sendEvent(widget, QKeyEvent(QKeyEvent.KeyPress, key, Qt.NoModifier))


def calendar_table(month_calendar):
    return month_calendar.findChild(QTableView, "qt_calendar_calendarview")


def test_window_month_overview_selects_day_and_shows_events(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start + timedelta(days=16)
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=13)
    event = make_event(event_id="overview", title="Overview Event", start_at=event_start, duration_minutes=60)
    window.storage.load_events_between = lambda start_at, end_at: [event] if start_at <= event.start_at < end_at else []

    window.show_month_overview()
    window.select_month_in_year_overview(selected_date.month)
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.month_day_title.text() == f"{day_name(selected_date)} {selected_date.strftime('%d.%m.%Y')}"
    assert window.year_highlighted_date == selected_date
    assert window.year_month_calendars[selected_date.month - 1].highlighted_date == selected_date
    assert all(
        calendar.highlighted_date is None
        for index, calendar in enumerate(window.year_month_calendars, start=1)
        if index != selected_date.month
    )
    assert overview_event_text(window, 0) == "13:00 - 14:00  Overview Event"
    assert window.month_day_events.item(0).sizeHint().height() >= 34


def test_window_month_overview_event_row_height_grows_for_wrapped_text(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start + timedelta(days=16)
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=18)
    event = make_event(
        event_id="overview-wrapped",
        title="ItGen: интенсив, тесты по блочному Python",
        start_at=event_start,
        duration_minutes=180,
    )
    window.storage.load_events_between = lambda start_at, end_at: [event] if start_at <= event.start_at < end_at else []
    window.month_day_events.setFixedWidth(220)

    window.show_month_overview()
    window.select_month_in_year_overview(selected_date.month)
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))

    assert window.month_day_events.item(0).sizeHint().height() > 34


def test_window_month_overview_escape_keeps_day_events_panel(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start + timedelta(days=16)
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=13)
    event = make_event(event_id="overview-escape", title="Escape Event", start_at=event_start, duration_minutes=60)
    window.storage.load_events_between = lambda start_at, end_at: [event] if start_at <= event.start_at < end_at else []

    window.show_month_overview()
    window.select_month_in_year_overview(selected_date.month)
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    window.clear_all_selections()
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert overview_event_text(window, 0) == "13:00 - 14:00  Escape Event"


def test_window_year_overview_selects_day_from_another_month(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = datetime(2026, 5, 31).date()

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.select_month_in_year_overview(6)
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))

    assert window.year_overview_month == selected_date.month
    assert window.month_day_title.text() == f"{day_name(selected_date)} {selected_date.strftime('%d.%m.%Y')}"


def test_window_year_overview_moves_selected_day_with_arrow_keys(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    month_calendar = window.year_month_calendars[4]

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.select_month_in_year_overview(5)
    window.select_day_in_month_overview(QDate(2026, 5, 12))
    month_calendar.setFocus()

    key_press(calendar_table(month_calendar), Qt.Key_Right)
    key_press(calendar_table(month_calendar), Qt.Key_Down)

    assert month_calendar.selectedDate() == QDate(2026, 5, 20)
    assert window.year_highlighted_date == datetime(2026, 5, 20).date()
    assert window.month_day_title.text() == "Wednesday 20.05.2026"


def test_window_year_overview_keeps_arrow_selection_inside_month(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    month_calendar = window.year_month_calendars[4]

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.select_month_in_year_overview(5)
    window.select_day_in_month_overview(QDate(2026, 5, 1))
    month_calendar.setFocus()

    key_press(calendar_table(month_calendar), Qt.Key_Left)

    assert month_calendar.selectedDate() == QDate(2026, 5, 1)
    assert window.year_highlighted_date == datetime(2026, 5, 1).date()


def test_window_month_overview_open_day_switches_to_week(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start + timedelta(days=16)

    window.show_month_overview()
    window.select_month_in_year_overview(selected_date.month)
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    window.open_month_overview_day()

    expected_week_start = selected_date - timedelta(days=selected_date.weekday())
    expected_start = datetime.combine(selected_date, datetime.min.time()).replace(
        hour=window.calendar_grid.day_start_hour
    )
    assert window.week_start == expected_week_start
    assert window.calendar_grid.week_start == expected_week_start
    assert window.calendar_view_stack.currentWidget() == window.week_view
    assert window.selected_details_ranges == [(expected_start, expected_start + timedelta(minutes=30))]


def test_window_month_overview_double_click_opens_day(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start + timedelta(days=16)

    window.show_month_overview()
    window.select_month_in_year_overview(selected_date.month)
    window.open_day_from_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))

    expected_week_start = selected_date - timedelta(days=selected_date.weekday())
    expected_start = datetime.combine(selected_date, datetime.min.time()).replace(
        hour=window.calendar_grid.day_start_hour
    )
    assert window.week_start == expected_week_start
    assert window.calendar_view_stack.currentWidget() == window.week_view
    assert window.selected_details_ranges == [(expected_start, expected_start + timedelta(minutes=30))]
