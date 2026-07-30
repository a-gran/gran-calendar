from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtWidgets import QAbstractItemView, QCalendarWidget

from tests.calendar_window_helpers import make_window
from ui.calendar_styles import MONTH_OVERVIEW_CALENDAR_HEIGHT
from ui.calendar_widgets import MonthOnlyCalendarWidget


def test_window_toggles_month_overview(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.toggle_calendar_overview()

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert window.overview_toggle_button.text() == "Week Calendar"
    assert isinstance(window.month_calendar, MonthOnlyCalendarWidget)
    assert window.month_calendar.height() == MONTH_OVERVIEW_CALENDAR_HEIGHT
    assert window.month_calendar.locale().language() == QLocale.English
    assert window.month_calendar.firstDayOfWeek() == Qt.Monday
    assert window.month_calendar.verticalHeaderFormat() == QCalendarWidget.NoVerticalHeader
    assert window.month_day_events.selectionMode() == QAbstractItemView.NoSelection
    assert window.year_spinbox.value() == window.week_start.year
    assert window.year_month_buttons[window.week_start.month - 1].isChecked()
    assert not window.previous_week_button.isEnabled()
    assert not window.current_week_button.isEnabled()
    assert not window.next_week_button.isEnabled()

    window.toggle_calendar_overview()

    assert window.calendar_view_stack.currentWidget() == window.week_view
    assert window.details_view_stack.currentWidget() == window.event_details_form
    assert window.overview_toggle_button.text() == "Month Calendar"
    assert window.previous_week_button.isEnabled()
    assert window.current_week_button.isEnabled()
    assert window.next_week_button.isEnabled()


def test_window_disables_week_navigation_in_month_overview(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.show_month_overview()

    assert not window.previous_week_button.isEnabled()
    assert not window.current_week_button.isEnabled()
    assert not window.next_week_button.isEnabled()


def test_window_overview_changes_year_and_keeps_month_selected(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.select_month_in_year_overview(9)
    window.year_spinbox.setValue(2027)

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert window.month_calendar.selectedDate() == QDate(2027, 9, 1)
    assert window.month_day_title.text() == "September 2027"


def test_window_overview_double_click_month_selects_month(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.year_month_buttons[9].double_clicked.emit(10)

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert window.month_calendar.selectedDate() == QDate(2026, 10, 1)
    assert window.month_day_title.text() == "October 2026"
