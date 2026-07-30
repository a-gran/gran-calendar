from datetime import date, timedelta

from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtWidgets import QCalendarWidget, QHBoxLayout, QVBoxLayout

from ui.calendar_dates import end_of_month, month_names
from ui.calendar_styles import (
    MONTH_BUTTON_STYLE,
    MONTH_CALENDAR_BUTTON_TEXT,
    MONTH_OVERVIEW_CALENDAR_HEIGHT,
    WEEK_CALENDAR_BUTTON_TEXT,
)
from ui.year_selector import YearMonthButton


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
        month_strip_layout = QHBoxLayout()
        month_strip_layout.setContentsMargins(0, 0, 0, 0)
        month_strip_layout.setSpacing(6)
        self.year_spinbox.setRange(1900, 3000)
        self.year_spinbox.valueChanged.connect(self.update_year_overview)
        month_strip_layout.addWidget(self.year_spinbox)
        for month_index, month_name in enumerate(month_names()):
            button = YearMonthButton(month_index + 1, month_name[:3])
            button.setCheckable(True)
            button.setStyleSheet(MONTH_BUTTON_STYLE)
            button.clicked.connect(
                lambda _checked=False, month=month_index + 1: self.select_month_in_year_overview(month)
            )
            button.double_clicked.connect(self.select_month_in_year_overview)
            self.year_month_buttons.append(button)
            month_strip_layout.addWidget(button)
        overview_layout.addLayout(month_strip_layout)
        self.month_calendar.setGridVisible(True)
        self.month_calendar.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.month_calendar.setFirstDayOfWeek(Qt.Monday)
        self.month_calendar.setFixedHeight(MONTH_OVERVIEW_CALENDAR_HEIGHT)
        self.month_calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.month_calendar.setNavigationBarVisible(False)
        self.month_calendar.clicked.connect(self.select_day_in_month_overview)
        self.month_calendar.activated.connect(self.open_day_from_month_overview)
        overview_layout.addWidget(self.month_calendar)
        overview_layout.addStretch()
        self.month_overview.setLayout(overview_layout)
        self.calendar_view_stack.addWidget(self.week_view)
        self.calendar_view_stack.addWidget(self.month_overview)

    def toggle_calendar_overview(self):
        if self.calendar_view_stack.currentWidget() == self.month_overview:
            self.show_week_view()
            return
        self.show_month_overview()

    def show_month_overview(self):
        selected_date = self.current_panel_date()
        self.year_spinbox.setValue(selected_date.year)
        self.year_overview_year = selected_date.year
        self.year_overview_month = selected_date.month
        self.sync_month_calendar_page(selected_date)
        self.update_month_day_details(selected_date)
        self.calendar_view_stack.setCurrentWidget(self.month_overview)
        self.details_view_stack.setCurrentWidget(self.month_day_details)
        self.overview_toggle_button.setText(WEEK_CALENDAR_BUTTON_TEXT)
        self.set_week_navigation_enabled(False)

    def show_week_view(self):
        self.calendar_view_stack.setCurrentWidget(self.week_view)
        self.details_view_stack.setCurrentWidget(self.event_details_form)
        self.overview_toggle_button.setText(MONTH_CALENDAR_BUTTON_TEXT)
        self.set_week_navigation_enabled(True)

    def set_week_navigation_enabled(self, is_enabled):
        self.previous_week_button.setEnabled(is_enabled)
        self.current_week_button.setEnabled(is_enabled)
        self.next_week_button.setEnabled(is_enabled)

    def update_year_overview(self, year):
        self.year_overview_year = year
        self.sync_month_calendar_page(date(year, self.year_overview_month, 1))
        self.update_year_month_details(year, self.year_overview_month)

    def select_month_in_year_overview(self, month):
        self.year_overview_month = month
        self.year_overview_year = self.year_spinbox.value()
        self.sync_month_calendar_page(date(self.year_overview_year, month, 1))
        self.update_year_month_details(self.year_overview_year, month)

    def update_year_month_details(self, year, month):
        self.overview_details_scope = "month"
        self.month_overview_date = date(year, month, 1)
        self.month_day_title.setText(f"{month_names()[month - 1]} {year}")
        self.month_day_events.clear()
        self.update_month_buttons()
        for event in self.events_for_overview_month(year, month):
            self.add_overview_event_item(event, self.format_year_month_event(event))
        if self.month_day_events.count() == 0:
            self.month_day_events.addItem("No events")

    def update_month_buttons(self):
        for button in self.year_month_buttons:
            button.setChecked(button.month == self.year_overview_month)

    def sync_month_calendar_page(self, selected_date):
        month_start = date(selected_date.year, selected_date.month, 1)
        month_end = end_of_month(selected_date.year, selected_date.month)
        self.month_calendar.setUpdatesEnabled(False)
        self.month_calendar.setDateRange(
            QDate(month_start.year, month_start.month, month_start.day),
            QDate(month_end.year, month_end.month, month_end.day),
        )
        self.month_calendar.set_visible_month(selected_date)
        self.month_calendar.setCurrentPage(selected_date.year, selected_date.month)
        self.month_calendar.setSelectedDate(QDate(selected_date.year, selected_date.month, selected_date.day))
        self.month_calendar.setUpdatesEnabled(True)

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
        if selected_date.year != self.year_overview_year or selected_date.month != self.year_overview_month:
            return
        self.year_overview_year = selected_date.year
        self.year_overview_month = selected_date.month
        self.sync_month_calendar_page(selected_date)
        self.update_month_day_details(selected_date)

    def open_day_from_month_overview(self, selected_qdate):
        self.select_day_in_month_overview(selected_qdate)
        self.open_month_overview_day()

    def open_month_overview_day(self):
        selected_date = self.month_overview_date
        self.week_start = selected_date - timedelta(days=selected_date.weekday())
        self.reload_week()
        self.select_start_slot_for_date(selected_date)
        self.show_week_view()
