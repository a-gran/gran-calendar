from dataclasses import replace

from domain.clock import current_datetime
from domain.event_factory import copy_event_to_range
from services.event_service import delete_event


class CalendarClipboardMixin:
    def copy_keyboard_selection(self):
        source_event = self.event_from_keyboard_selection("copy")
        if source_event is None:
            return
        self.select_event(source_event)
        self.copied_event = replace(source_event)

    def cut_keyboard_selection(self):
        source_event = self.event_from_keyboard_selection("cut")
        if source_event is None:
            return
        self.copied_event = replace(source_event)
        self.delete_event_with_undo(source_event)

    def paste_keyboard_selection(self):
        if self.copied_event is None:
            self.show_status_message("No copied event.", 3000)
            return
        selected_slots = self.calendar_grid.selected_slots()
        if not selected_slots:
            self.show_status_message("Select a slot to paste the event.", 3000)
            return
        self.paste_copied_event_to_slots(selected_slots)

    def event_from_keyboard_selection(self, action_name):
        selected_events = self.events_for_selected_event_ids()
        if len(selected_events) == 1:
            return selected_events[0]
        if len(selected_events) > 1:
            self.show_status_message(f"Select one event by clicking it before {action_name}.", 4000)
            return None
        if self.selected_event is not None:
            return self.find_event_by_id(self.events, self.selected_event.id)
        selected_events = self.events_for_selected_slots()
        if not selected_events:
            self.show_status_message(f"No event to {action_name}.", 3000)
            return None
        if len(selected_events) > 1:
            self.show_status_message(f"Select one event by clicking it before {action_name}.", 4000)
            return None
        return selected_events[0]

    def paste_copied_event_to_slots(self, slot_datetimes):
        event_duration = self.copied_event.end_at - self.copied_event.start_at
        target_ranges = [(slot_datetime, slot_datetime + event_duration) for slot_datetime in slot_datetimes]
        overwritten_events = self.events_overlapping_ranges(target_ranges)
        overwritten_event_snapshots = [replace(event) for event in overwritten_events]
        for event in overwritten_events:
            self.events = delete_event(self.events, self.storage, event)
        current_moment = current_datetime()
        copied_events = []
        for slot_datetime in slot_datetimes:
            copied_event = copy_event_to_range(self.copied_event, slot_datetime, current_moment)
            copied_events.append(copied_event)
        self.store_events(copied_events)
        copied_event_snapshots = [replace(event) for event in copied_events]
        copied_event_ids = [event.id for event in copied_events]
        overwritten_event_ids = [event.id for event in overwritten_event_snapshots]
        self.remember_undo(
            lambda event_ids=copied_event_ids, events=overwritten_event_snapshots: self.undo_pasted_events(
                event_ids,
                events,
            ),
            lambda events=copied_event_snapshots, event_ids=overwritten_event_ids: self.redo_pasted_events(
                events,
                event_ids,
            ),
        )
        self.select_event(copied_events[-1])

    def undo_pasted_events(self, created_event_ids, overwritten_events):
        for event_id in created_event_ids:
            event = self.find_event_by_id(self.events, event_id)
            if event is not None:
                self.events = delete_event(self.events, self.storage, event)
        for event in overwritten_events:
            if self.find_event_by_id(self.events, event.id) is None:
                self.store_event(event)
        self.select_event(None)

    def redo_pasted_events(self, created_events, overwritten_event_ids):
        for event_id in overwritten_event_ids:
            event = self.find_event_by_id(self.events, event_id)
            if event is not None:
                self.events = delete_event(self.events, self.storage, event)
        for event in created_events:
            if self.find_event_by_id(self.events, event.id) is None:
                self.store_event(event)
        if created_events:
            self.select_event(created_events[-1])

    def delete_keyboard_selection(self):
        selected_events = self.events_for_selected_event_ids()
        if selected_events:
            self.delete_events_with_undo(selected_events)
            return
        deleted_events = self.events_for_selected_slots()
        if not deleted_events:
            self.show_status_message("There are no events in the selected slots.", 3000)
            return
        self.delete_events_with_undo(deleted_events)

    def events_for_selected_event_ids(self):
        selected_event_ids = self.calendar_grid.selected_event_ids_list()
        return [self.events_by_id[event_id] for event_id in selected_event_ids if event_id in self.events_by_id]

    def events_for_selected_slots(self):
        selected_slots = self.calendar_grid.selected_slots()
        result = []
        seen_ids = set()
        for slot_datetime in selected_slots:
            for event in self.get_events_for_time(slot_datetime):
                if event.id not in seen_ids:
                    result.append(event)
                    seen_ids.add(event.id)
        return result
