from datetime import date, timedelta

from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtWidgets import QCalendarWidget, QGridLayout, QPushButton, QTableView, QVBoxLayout, QWidget

from ui.calendar_dates import end_of_month, month_names
from ui.calendar_styles import (
    CURRENT_YEAR_MONTH_TITLE_BUTTON_STYLE,
    MONTH_CALENDAR_BUTTON_TEXT,
    WEEK_CALENDAR_BUTTON_TEXT,
    YEAR_MONTH_CALENDAR_HEIGHT,
    YEAR_MONTH_TITLE_BUTTON_STYLE,
)
from ui.calendar_widgets import MonthOnlyCalendarWidget


class CalendarOverviewMixin:
    def setup_calendar_views(self):
        calendar_layout = QVBoxLayout()
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.addWidget(self.calendar_header)
        calendar_layout.addWidget(self.calendar_scroll_area)
        self.week_view.setLayout(calendar_layout)
        overview_layout = QVBoxLayout()
        overview_layout.setContentsMargins(0, 0, 0, 0)
        overview_layout.setSpacing(8)
        self.year_spinbox.setRange(1900, 3000)
        self.year_spinbox.valueChanged.connect(self.update_year_overview)
        year_calendar_widget = QWidget()
        year_calendar_layout = QGridLayout()
        year_calendar_layout.setContentsMargins(0, 0, 0, 0)
        year_calendar_layout.setSpacing(4)
        self.year_calendar_layout = year_calendar_layout
        for month_index, month_name in enumerate(month_names()):
            month_widget = QWidget()
            month_layout = QVBoxLayout()
            month_layout.setContentsMargins(0, 0, 0, 0)
            month_layout.setSpacing(1)
            month_layout.setAlignment(Qt.AlignTop)
            month_label = QPushButton(month_name)
            month_label.setFocusPolicy(Qt.NoFocus)
            month_label.clicked.connect(
                lambda _checked=False, month=month_index + 1: self.select_month_in_year_overview(month)
            )
            month_calendar = MonthOnlyCalendarWidget()
            self.setup_year_month_calendar(month_calendar)
            month_calendar.clicked.connect(self.select_day_in_month_overview)
            month_calendar.clicked.connect(lambda _qdate, calendar=month_calendar: calendar.setFocus())
            month_calendar.day_selected_from_keyboard.connect(self.select_day_in_month_overview)
            month_calendar.activated.connect(self.open_day_from_month_overview)
            self.year_month_calendars.append(month_calendar)
            self.year_month_title_buttons.append(month_label)
            month_layout.addWidget(month_label)
            month_layout.addWidget(month_calendar)
            month_widget.setLayout(month_layout)
            year_calendar_layout.addWidget(month_widget, month_index // 3, month_index % 3)
        for previous_calendar, next_calendar in zip(
            self.year_month_calendars,
            self.year_month_calendars[1:],
            strict=False,
        ):
            QWidget.setTabOrder(previous_calendar, next_calendar)
        year_calendar_widget.setLayout(year_calendar_layout)
        self.year_overview_scroll_area.setWidgetResizable(True)
        self.year_overview_scroll_area.setWidget(year_calendar_widget)
        overview_layout.addWidget(self.year_overview_scroll_area, 1)
        self.update_year_month_title_styles()
        self.month_overview.setLayout(overview_layout)
        self.calendar_view_stack.addWidget(self.week_view)
        self.calendar_view_stack.addWidget(self.month_overview)

    def setup_year_month_calendar(self, month_calendar):
        month_calendar.setGridVisible(True)
        month_calendar.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        month_calendar.setFirstDayOfWeek(Qt.Monday)
        month_calendar.setFixedHeight(YEAR_MONTH_CALENDAR_HEIGHT)
        month_calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        month_calendar.setNavigationBarVisible(False)

    def update_year_overview_calendar_sizes(self):
        if not self.year_month_calendars:
            return
        viewport_height = self.year_overview_scroll_area.viewport().height()
        if viewport_height <= 0:
            return
        grid_spacing = max(0, self.year_calendar_layout.verticalSpacing())
        row_height = max(1, (viewport_height - grid_spacing * 3) // 4)
        title_height = max(button.sizeHint().height() for button in self.year_month_title_buttons)
        month_spacing = 1
        calendar_height = max(1, row_height - title_height - month_spacing)
        first_calendar_view = self.year_month_calendars[0].findChild(QTableView, "qt_calendar_calendarview")
        if first_calendar_view is None or first_calendar_view.model() is None:
            return
        calendar_row_count = max(1, first_calendar_view.model().rowCount())
        frame_height = first_calendar_view.frameWidth() * 2
        cell_height = max(16, (calendar_height - frame_height) // (calendar_row_count + 1))
        for month_calendar in self.year_month_calendars:
            month_calendar.set_day_cell_height(cell_height)

    def toggle_calendar_overview(self):
        if self.calendar_view_stack.currentWidget() == self.month_overview:
            self.show_week_view()
            return
        self.show_month_overview()

    def show_month_overview(self):
        selected_date = date.today()
        self.year_highlighted_date = None
        self.year_spinbox.setValue(selected_date.year)
        self.year_overview_year = selected_date.year
        self.year_overview_month = selected_date.month
        self.sync_month_calendar_page(selected_date)
        self.update_year_month_details(selected_date.year, selected_date.month)
        self.calendar_view_stack.setCurrentWidget(self.month_overview)
        self.details_view_stack.setCurrentWidget(self.month_day_details)
        self.overview_toggle_button.setText(WEEK_CALENDAR_BUTTON_TEXT)
        self.year_spinbox.show()
        self.set_week_navigation_visible(False)
        self.set_week_navigation_enabled(False)
        self.update_year_overview_calendar_sizes()

    def show_week_view(self):
        self.calendar_view_stack.setCurrentWidget(self.week_view)
        self.details_view_stack.setCurrentWidget(self.event_details_form)
        self.overview_toggle_button.setText(MONTH_CALENDAR_BUTTON_TEXT)
        self.year_spinbox.hide()
        self.set_week_navigation_visible(True)
        self.set_week_navigation_enabled(True)

    def set_week_navigation_visible(self, is_visible):
        self.previous_week_button.setVisible(is_visible)
        self.current_week_button.setVisible(is_visible)
        self.next_week_button.setVisible(is_visible)

    def set_week_navigation_enabled(self, is_enabled):
        self.previous_week_button.setEnabled(is_enabled)
        self.current_week_button.setEnabled(is_enabled)
        self.next_week_button.setEnabled(is_enabled)

    def update_year_overview(self, year):
        self.year_overview_year = year
        self.year_highlighted_date = None
        self.sync_month_calendar_page(date(year, self.year_overview_month, 1))
        self.update_year_month_details(year, self.year_overview_month)

    def select_month_in_year_overview(self, month):
        self.year_highlighted_date = None
        self.year_overview_month = month
        self.year_overview_year = self.year_spinbox.value()
        self.sync_month_calendar_page(date(self.year_overview_year, month, 1))
        self.update_year_month_details(self.year_overview_year, month)

    def update_year_month_details(self, year, month):
        self.overview_details_scope = "month"
        self.details_view_stack.setCurrentWidget(self.month_day_details)
        self.month_overview_date = date(year, month, 1)
        self.month_day_title.setText(f"{month_names()[month - 1]} {year}")
        self.month_day_events.clear()
        self.update_month_buttons()
        for event in self.events_for_overview_month(year, month):
            self.add_overview_event_item(event, self.format_year_month_event(event))
        if self.month_day_events.count() == 0:
            self.month_day_events.addItem("No events")

    def update_month_buttons(self):
        self.sync_month_calendar_page(self.month_overview_date)

    def sync_month_calendar_page(self, selected_date):
        if not self.year_month_calendars:
            return
        self.update_year_month_title_styles(selected_date.year)
        for month, month_calendar in enumerate(self.year_month_calendars, start=1):
            month_start = date(selected_date.year, month, 1)
            month_end = end_of_month(selected_date.year, month)
            shown_date = selected_date if selected_date.month == month else month_start
            month_calendar.setUpdatesEnabled(False)
            month_calendar.setDateRange(
                QDate(month_start.year, month_start.month, month_start.day),
                QDate(month_end.year, month_end.month, month_end.day),
            )
            month_calendar.set_visible_month(month_start)
            month_calendar.setCurrentPage(selected_date.year, month)
            month_calendar.setSelectedDate(QDate(shown_date.year, shown_date.month, shown_date.day))
            should_highlight_date = (
                self.year_highlighted_date is not None and self.year_highlighted_date.month == month
            )
            month_calendar.set_selected_month(
                selected_date.year == self.year_overview_year and month == self.year_overview_month
            )
            month_calendar.set_highlighted_date(self.year_highlighted_date if should_highlight_date else None)
            month_calendar.setUpdatesEnabled(True)

    def sync_year_overview_selected_day(self, selected_date, previous_highlighted_date):
        self.update_year_month_title_styles(selected_date.year)
        months_to_update = {selected_date.month}
        if previous_highlighted_date is not None and previous_highlighted_date.year == selected_date.year:
            months_to_update.add(previous_highlighted_date.month)
        for month in months_to_update:
            month_calendar = self.year_month_calendars[month - 1]
            shown_date = selected_date if month == selected_date.month else date(selected_date.year, month, 1)
            month_calendar.setUpdatesEnabled(False)
            month_calendar.setSelectedDate(QDate(shown_date.year, shown_date.month, shown_date.day))
            month_calendar.set_selected_month(month == self.year_overview_month)
            month_calendar.set_highlighted_date(selected_date if month == selected_date.month else None)
            month_calendar.setUpdatesEnabled(True)

    def update_year_month_title_styles(self, overview_year=None):
        if overview_year is None:
            overview_year = self.year_overview_year
        for month, button in enumerate(self.year_month_title_buttons, start=1):
            if overview_year == self.year_overview_year and month == self.year_overview_month:
                button.setStyleSheet(CURRENT_YEAR_MONTH_TITLE_BUTTON_STYLE)
            else:
                button.setStyleSheet(YEAR_MONTH_TITLE_BUTTON_STYLE)

    def current_panel_date(self):
        if self.selected_details_ranges:
            return self.selected_details_ranges[0][0].date()
        if self.selected_event is not None:
            event = self.find_event_by_id(self.events, self.selected_event.id)
            if event is not None:
                return event.start_at.date()
        return self.week_start

    def select_day_in_month_overview(self, selected_qdate):
        selected_date = date(selected_qdate.year(), selected_qdate.month(), selected_qdate.day())
        if selected_date.year != self.year_overview_year:
            return
        previous_highlighted_date = self.year_highlighted_date
        self.year_highlighted_date = selected_date
        self.year_overview_year = selected_date.year
        self.year_overview_month = selected_date.month
        self.sync_year_overview_selected_day(selected_date, previous_highlighted_date)
        self.update_month_day_details(selected_date, should_sync_calendars=False)

    def open_day_from_month_overview(self, selected_qdate):
        self.select_day_in_month_overview(selected_qdate)
        self.open_month_overview_day()

    def open_month_overview_day(self):
        selected_date = self.month_overview_date
        self.week_start = selected_date - timedelta(days=selected_date.weekday())
        self.reload_week()
        self.select_start_slot_for_date(selected_date)
        self.show_week_view()
