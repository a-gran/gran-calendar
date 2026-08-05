from datetime import date, datetime, time, timedelta

from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QWidget

from domain.event_index import sort_events


class CalendarWeekMixin:
    def setup_week_navigation(self, parent_layout):
        navigation_layout = QGridLayout()
        left_navigation = QWidget()
        left_navigation_layout = QHBoxLayout()
        left_navigation_layout.setContentsMargins(0, 0, 0, 0)
        left_navigation_layout.addWidget(self.previous_week_button)
        left_navigation_layout.addWidget(self.current_week_button)
        left_navigation_layout.addWidget(self.next_week_button)
        self.year_spinbox.hide()
        left_navigation_layout.addWidget(self.year_spinbox)
        left_navigation_layout.addStretch()
        left_navigation.setLayout(left_navigation_layout)
        self.left_navigation = left_navigation
        right_navigation = QWidget()
        right_navigation_layout = QHBoxLayout()
        right_navigation_layout.setContentsMargins(0, 0, 0, 0)
        right_navigation_layout.addStretch()
        right_navigation_layout.addWidget(self.overview_toggle_button)
        right_navigation_layout.addWidget(self.settings_button)
        right_navigation.setLayout(right_navigation_layout)
        self.previous_week_button.clicked.connect(self.show_previous_week)
        self.current_week_button.clicked.connect(self.show_current_week)
        self.next_week_button.clicked.connect(self.show_next_week)
        self.settings_button.clicked.connect(self.open_visual_settings_dialog)
        self.overview_toggle_button.clicked.connect(self.toggle_calendar_overview)
        navigation_layout.addWidget(left_navigation, 0, 0)
        navigation_layout.addWidget(self.week_label, 0, 1, alignment=Qt.AlignCenter)
        navigation_layout.addWidget(right_navigation, 0, 2)
        navigation_layout.setColumnStretch(0, 1)
        navigation_layout.setColumnStretch(1, 1)
        navigation_layout.setColumnStretch(2, 1)
        parent_layout.addLayout(navigation_layout)
        self.update_week_label()
        self.setup_current_time_clock()

    def setup_current_time_clock(self):
        self.current_time_timer = QTimer(self)
        self.current_time_timer.timeout.connect(self.update_current_time_label)
        self.update_current_time_label()
        self.current_time_timer.start(1000)

    def update_current_time_label(self):
        self.current_time_label.setText(QTime.currentTime().toString("HH:mm:ss"))
        self.calendar_grid.update()

    def update_week_label(self):
        week_end = self.week_start + timedelta(days=6)
        label_text = f"{self.week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}"
        self.week_label.setText(label_text)

    def clear_calendar_view(self):
        self.events = []
        self.selected_event = None
        self.selected_details_ranges = []
        self.calendar_grid.set_events(self.events)
        self.calendar_grid.clear_selection()
        self.update_event_details_panel()

    def reload_week(self):
        self.clear_calendar_view()
        self.calendar_grid.set_week_start(self.week_start)
        self.calendar_header.set_week_start(self.week_start)
        self.update_week_label()
        self.load_events_from_storage()
        self.sync_month_calendar_page(self.week_start)

    def show_previous_week(self):
        self.week_start = self.week_start - timedelta(days=7)
        self.reload_week()

    def show_next_week(self):
        self.week_start = self.week_start + timedelta(days=7)
        self.reload_week()

    def show_current_week(self):
        self.week_start = date.today() - timedelta(days=date.today().weekday())
        self.reload_week()

    def load_events_from_storage(self):
        week_start_datetime = datetime.combine(self.week_start, time.min)
        week_end_datetime = week_start_datetime + timedelta(days=7)
        self.events = sort_events(self.storage.load_events_between(week_start_datetime, week_end_datetime))
        self.refresh_calendar()

    def select_default_start_slot(self):
        self.select_start_slot_for_date(self.week_start)

    def select_start_slot_for_date(self, selected_date):
        start_at = datetime.combine(selected_date, time(hour=self.calendar_grid.day_start_hour))
        self.calendar_grid.replace_slot_selection(start_at)
        self.select_slot_for_details(start_at)
