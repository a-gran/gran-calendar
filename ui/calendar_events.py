from dataclasses import replace
from datetime import timedelta

from domain.clock import current_datetime
from domain.event_index import build_event_date_index, build_event_id_index, events_for_range
from services.event_service import add_event, add_events


class CalendarEventsMixin:
    def add_event_to_selected_slot(self):
        selected_slots = self.calendar_grid.selected_slots()
        if not selected_slots:
            self.show_status_message("Select a slot to create an event.", 3000)
            return
        start_at = selected_slots[0]
        end_at = start_at + timedelta(minutes=self.calendar_grid.slot_minutes)
        self.add_event_from_selection(start_at, end_at)

    def add_event_from_selection(self, start_at, end_at):
        self.begin_event_creation_details([(start_at, end_at)])

    def add_events_from_ranges(self, ranges):
        self.begin_event_creation_details(ranges)

    def begin_event_creation_details(self, ranges):
        if not ranges:
            return
        if any(self.has_event_overlap(start_at, end_at) for start_at, end_at in ranges):
            self.show_status_message("One of the selected days already has an event.", 4000)
            return
        self.clear_status_message()
        self.selected_event = None
        self.selected_details_ranges = list(ranges)
        self.update_event_details_panel()

    def add_event_to_slot(self, slot_datetime):
        end_at = slot_datetime + timedelta(minutes=self.calendar_grid.slot_minutes)
        self.add_event_from_selection(slot_datetime, end_at)

    def store_event(self, event, save=True):
        self.events = add_event(self.events, self.storage, event, save)
        self.refresh_calendar()

    def store_events(self, events, save=True):
        self.events = add_events(self.events, self.storage, events, save)
        self.refresh_calendar()

    def refresh_calendar(self):
        self.rebuild_event_index()
        self.calendar_grid.set_events(self.events)
        if self.selected_event is not None:
            self.calendar_grid.set_selected_event_id(self.selected_event.id)
        self.update_event_details_panel()

    def rebuild_event_index(self):
        self.events_by_id = build_event_id_index(self.events)
        self.events_by_date = build_event_date_index(self.events)

    def events_for_range(self, start_at, end_at):
        return events_for_range(self.events_by_date, start_at, end_at)

    def select_event(self, event):
        self.clear_status_message()
        self.selected_event = event
        self.selected_details_ranges = []
        if event is not None and event.id not in self.calendar_grid.selected_event_ids:
            self.calendar_grid.set_selected_event_id(event.id)
        self.update_event_details_panel()

    def select_slot_for_details(self, slot_datetime):
        self.clear_status_message()
        self.selected_event = None
        if slot_datetime is None:
            self.selected_details_ranges = []
        elif isinstance(slot_datetime, list):
            self.selected_details_ranges = [
                (selected_slot, selected_slot + timedelta(minutes=self.calendar_grid.slot_minutes))
                for selected_slot in slot_datetime
            ]
        else:
            end_at = slot_datetime + timedelta(minutes=self.calendar_grid.slot_minutes)
            self.selected_details_ranges = [(slot_datetime, end_at)]
        self.update_event_details_panel()

    def get_events_for_time(self, slot_datetime):
        return self.events_for_range(slot_datetime, slot_datetime + timedelta(microseconds=1))

    def has_event_overlap(self, start_at, end_at):
        return bool(self.events_for_range(start_at, end_at))

    def has_event_overlap_excluding(self, event_id, start_at, end_at):
        return any(event.id != event_id for event in self.events_for_range(start_at, end_at))

    def events_overlapping_ranges(self, ranges):
        overlapping_events = []
        overlapping_ids = set()
        for start_at, end_at in ranges:
            for event in self.events_for_range(start_at, end_at):
                if event.id in overlapping_ids:
                    continue
                overlapping_events.append(event)
                overlapping_ids.add(event.id)
        return overlapping_events

    def find_event_by_id(self, events, event_id):
        if events is self.events:
            return self.events_by_id.get(event_id)
        for event in events:
            if event.id == event_id:
                return event
        return None

    def resize_event_from_grid(self, event, start_at, end_at):
        event = self.find_event_by_id(self.events, event.id)
        if event is None:
            return
        if self.has_event_overlap_excluding(event.id, start_at, end_at):
            self.show_status_message("There is already an event in the selected time.", 4000)
            self.refresh_calendar()
            return
        old_event = replace(event)
        event.start_at = start_at
        event.end_at = end_at
        event.updated_at = current_datetime()
        self.storage.save_event(event)
        new_event = replace(event)
        self.remember_undo(
            lambda event_id=event.id, old_event=old_event: self.undo_edited_event(event_id, old_event),
            lambda event_id=event.id, new_event=new_event: self.redo_edited_event(event_id, new_event),
        )
        self.refresh_calendar()
