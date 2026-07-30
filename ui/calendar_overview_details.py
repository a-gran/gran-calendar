from dataclasses import replace
from datetime import datetime, time, timedelta

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QListWidgetItem

from domain.clock import current_datetime
from domain.event_index import sort_events
from services.event_service import delete_event
from ui.calendar_dates import day_name
from ui.calendar_widgets import OverviewEventRow


class CalendarOverviewDetailsMixin:
    def events_for_overview_month(self, year, month):
        month_start = datetime(year, month, 1)
        month_end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        events = self.storage.load_events_between(month_start, month_end)
        return sort_events(events)

    def format_year_month_event(self, event):
        event_date = event.start_at.date()
        return (
            f"{day_name(event_date)} {event_date.strftime('%d.%m.%Y')}\n"
            f"{event.start_at.strftime('%H:%M')} - {event.end_at.strftime('%H:%M')}  {event.title}"
        )

    def update_month_day_details(self, selected_date):
        self.overview_details_scope = "day"
        self.month_overview_date = selected_date
        self.update_month_buttons()
        self.month_day_title.setText(f"{day_name(selected_date)} {selected_date.strftime('%d.%m.%Y')}")
        self.month_day_events.clear()
        for event in self.events_for_overview_date(selected_date):
            self.add_overview_event_item(event, self.format_month_event(event))
        if self.month_day_events.count() == 0:
            self.month_day_events.addItem("No events")

    def events_for_overview_date(self, selected_date):
        day_start = datetime.combine(selected_date, time.min)
        day_end = day_start + timedelta(days=1)
        events = self.storage.load_events_between(day_start, day_end)
        return sort_events(events)

    def format_month_event(self, event):
        return f"{event.start_at.strftime('%H:%M')} - {event.end_at.strftime('%H:%M')}  {event.title}"

    def add_overview_event_item(self, event, text):
        item = QListWidgetItem()
        row = OverviewEventRow(event.id, text, event.title)
        row.delete_requested.connect(self.delete_overview_event)
        row.restore_requested.connect(self.restore_overview_event)
        row.double_clicked.connect(self.open_overview_event)
        row.title_submitted.connect(self.update_overview_event_title)
        item.setSizeHint(QSize(0, 36))
        self.month_day_events.addItem(item)
        self.month_day_events.setItemWidget(item, row)

    def update_overview_event_title(self, event_id, title):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            event = self.event_from_overview(event_id)
        if event is None:
            return
        event.title = title
        event.updated_at = current_datetime()
        self.storage.save_event(event)
        row = self.overview_row_for_event(event.id)
        if row is not None:
            row.set_display_text(self.format_overview_event(event), event.title)

    def format_overview_event(self, event):
        if self.overview_details_scope == "month":
            return self.format_year_month_event(event)
        return self.format_month_event(event)

    def open_overview_event(self, event_id):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            event = self.event_from_overview(event_id)
        if event is None:
            return
        selected_date = event.start_at.date()
        self.week_start = selected_date - timedelta(days=selected_date.weekday())
        self.reload_week()
        current_event = self.find_event_by_id(self.events, event.id)
        if current_event is not None:
            self.select_event(current_event)
        self.show_week_view()

    def delete_overview_event(self, event_id):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            event = self.event_from_overview(event_id)
        if event is None:
            return
        if self.find_event_by_id(self.events, event.id) is None:
            self.events.append(event)
        deleted_snapshot = self.delete_overview_event_with_undo(event)
        self.deleted_overview_events[event.id] = deleted_snapshot
        row = self.overview_row_for_event(event.id)
        if row is not None:
            row.show_restore_action()

    def delete_overview_event_with_undo(self, deleted_event):
        deleted_snapshot = replace(deleted_event)
        self.events = delete_event(self.events, self.storage, deleted_event)
        self.remember_undo(
            lambda event=deleted_snapshot: self.restore_event(event),
            lambda event_id=deleted_snapshot.id: self.redo_deleted_event(event_id),
        )
        self.selected_event = None
        self.selected_details_ranges = []
        self.calendar_grid.clear_selection()
        self.refresh_calendar()
        self.calendar_view_stack.setCurrentWidget(self.month_overview)
        self.details_view_stack.setCurrentWidget(self.month_day_details)
        return deleted_snapshot

    def overview_row_for_event(self, event_id):
        for index in range(self.month_day_events.count()):
            row = self.month_day_events.itemWidget(self.month_day_events.item(index))
            if row is not None and row.event_id == event_id:
                return row
        return None

    def event_from_overview(self, event_id):
        if self.overview_details_scope == "month":
            overview_events = self.events_for_overview_month(
                self.month_overview_date.year,
                self.month_overview_date.month,
            )
        else:
            overview_events = self.events_for_overview_date(self.month_overview_date)
        return self.find_event_by_id(overview_events, event_id)

    def restore_overview_event(self, event_id):
        event = self.deleted_overview_events.pop(event_id, None)
        if event is None:
            return
        self.restore_event(event)
        self.calendar_view_stack.setCurrentWidget(self.month_overview)
        self.details_view_stack.setCurrentWidget(self.month_day_details)
        row = self.overview_row_for_event(event_id)
        if row is not None:
            row.show_delete_action()

    def refresh_overview_details(self):
        if self.calendar_view_stack.currentWidget() != self.month_overview:
            return
        if self.overview_details_scope == "month":
            self.update_year_month_details(self.month_overview_date.year, self.month_overview_date.month)
            return
        self.update_month_day_details(self.month_overview_date)
