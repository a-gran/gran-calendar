from datetime import date

from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtWidgets import QAbstractItemView, QCalendarWidget, QTableView

from tests.calendar_window_helpers import make_window
from ui.calendar_styles import CURRENT_YEAR_MONTH_TITLE_BUTTON_STYLE, YEAR_MONTH_CALENDAR_HEIGHT
from ui.calendar_widgets import MonthOnlyCalendarWidget


def test_window_toggles_month_overview(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.toggle_calendar_overview()
    window.show()
    qt_app.processEvents()

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert window.overview_toggle_button.text() == "Week"
    assert len(window.year_month_calendars) == 12
    assert len(window.year_month_title_buttons) == 12
    assert window.year_month_title_buttons[date.today().month - 1].styleSheet() == CURRENT_YEAR_MONTH_TITLE_BUTTON_STYLE
    assert "font-size: 18px" in window.year_month_title_buttons[0].styleSheet()
    assert all(isinstance(calendar, MonthOnlyCalendarWidget) for calendar in window.year_month_calendars)
    assert window.year_month_calendars[0].day_cell_height == 16
    assert window.year_month_calendars[0].day_number_pixel_size == 12
    assert window.year_month_calendars[0].day_number_is_bold
    assert window.year_month_calendars[0].month_table_border_color == "#ffffff"
    assert window.year_month_calendars[0].month_table_border_width == 3
    assert window.year_month_calendars[0].height() < YEAR_MONTH_CALENDAR_HEIGHT
    assert window.year_month_calendars[0].locale().language() == QLocale.English
    assert window.year_month_calendars[0].firstDayOfWeek() == Qt.Monday
    assert window.year_month_calendars[0].verticalHeaderFormat() == QCalendarWidget.NoVerticalHeader
    unselected_month_index = 1 if date.today().month == 1 else 0
    calendar_view = window.year_month_calendars[unselected_month_index].findChild(
        QTableView,
        "qt_calendar_calendarview",
    )
    selected_calendar_view = window.year_month_calendars[date.today().month - 1].findChild(
        QTableView,
        "qt_calendar_calendarview",
    )
    assert "border: 3px solid #ffffff" in calendar_view.styleSheet()
    assert "border: 3px solid #facc15" in selected_calendar_view.styleSheet()
    assert calendar_view.verticalHeader().defaultSectionSize() == 16
    assert calendar_view.horizontalHeader().height() == calendar_view.verticalHeader().defaultSectionSize()
    month_block_height = window.year_month_title_buttons[0].height() + window.year_month_calendars[0].height()
    assert month_block_height * 4 + 12 <= window.year_overview_scroll_area.viewport().height()
    assert window.year_overview_scroll_area.verticalScrollBar().maximum() == 0
    assert window.month_day_events.selectionMode() == QAbstractItemView.NoSelection
    assert window.year_spinbox.value() == window.week_start.year
    assert not window.year_spinbox.isHidden()
    assert window.year_spinbox.parentWidget() == window.left_navigation
    today = date.today()
    assert window.month_day_title.text().endswith(str(today.year))
    assert window.year_overview_month == today.month
    assert all(
        calendar.highlighted_date is None
        for calendar in window.year_month_calendars
    )
    assert not window.previous_week_button.isEnabled()
    assert not window.current_week_button.isEnabled()
    assert not window.next_week_button.isEnabled()
    assert window.previous_week_button.isHidden()
    assert window.current_week_button.isHidden()
    assert window.next_week_button.isHidden()

    window.toggle_calendar_overview()

    assert window.calendar_view_stack.currentWidget() == window.week_view
    assert window.details_view_stack.currentWidget() == window.event_details_form
    assert window.overview_toggle_button.text() == "Year"
    assert window.year_spinbox.isHidden()
    assert window.previous_week_button.isEnabled()
    assert window.current_week_button.isEnabled()
    assert window.next_week_button.isEnabled()
    assert not window.previous_week_button.isHidden()
    assert not window.current_week_button.isHidden()
    assert not window.next_week_button.isHidden()


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
    assert window.year_month_calendars[8].selectedDate() == QDate(2027, 9, 1)
    assert window.month_day_title.text() == "September 2027"


def test_window_overview_selects_month(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.select_month_in_year_overview(10)

    assert window.calendar_view_stack.currentWidget() == window.month_overview
    assert window.details_view_stack.currentWidget() == window.month_day_details
    assert window.year_month_calendars[9].selectedDate() == QDate(2026, 10, 1)
    assert window.month_day_title.text() == "October 2026"


def test_window_overview_month_title_button_selects_month(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.show_month_overview()
    window.year_spinbox.setValue(2026)
    window.year_month_title_buttons[5].click()

    assert window.year_overview_month == 6
    assert window.year_highlighted_date is None
    assert window.month_day_title.text() == "June 2026"
    assert window.year_month_title_buttons[5].styleSheet() == CURRENT_YEAR_MONTH_TITLE_BUTTON_STYLE
    assert window.year_month_title_buttons[date.today().month - 1].styleSheet() != CURRENT_YEAR_MONTH_TITLE_BUTTON_STYLE
    selected_calendar_view = window.year_month_calendars[5].findChild(QTableView, "qt_calendar_calendarview")
    unselected_month_index = 0 if date.today().month != 6 else 1
    current_calendar_view = window.year_month_calendars[unselected_month_index].findChild(
        QTableView,
        "qt_calendar_calendarview",
    )
    assert "border: 3px solid #facc15" in selected_calendar_view.styleSheet()
    assert "border: 3px solid #ffffff" in current_calendar_view.styleSheet()
