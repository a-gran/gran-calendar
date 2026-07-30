from datetime import date, datetime, time, timedelta

from PySide6.QtWidgets import QHBoxLayout

from domain.event_index import sort_events


class CalendarWeekMixin:
    def setup_week_navigation(self, parent_layout):
        navigation_layout = QHBoxLayout()
        self.previous_week_button.clicked.connect(self.show_previous_week)
        self.current_week_button.clicked.connect(self.show_current_week)
        self.next_week_button.clicked.connect(self.show_next_week)
        self.overview_toggle_button.clicked.connect(self.toggle_calendar_overview)
        navigation_layout.addWidget(self.previous_week_button)
        navigation_layout.addWidget(self.week_label)
        navigation_layout.addStretch()
        navigation_layout.addWidget(self.overview_toggle_button)
        navigation_layout.addWidget(self.current_week_button)
        navigation_layout.addWidget(self.next_week_button)
        parent_layout.addLayout(navigation_layout)
        self.update_week_label()

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
