from dataclasses import replace

from domain.event_update import apply_event_snapshot
from services.event_service import delete_event, delete_events


class CalendarHistoryMixin:
    def remember_undo(self, undo_action, redo_action=None):
        self.history_manager.remember(undo_action, redo_action)

    def undo_last_action(self):
        action = self.history_manager.pop_undo()
        if action is None:
            self.show_status_message("Nothing to undo.", 3000)
            return
        undo_action, redo_action = action
        undo_action()
        if redo_action is not None:
            self.history_manager.remember_redo(undo_action, redo_action)
        self.refresh_calendar()

    def redo_last_action(self):
        action = self.history_manager.pop_redo()
        if action is None:
            self.show_status_message("Nothing to redo.", 3000)
            return
        undo_action, redo_action = action
        redo_action()
        self.history_manager.remember_undo(undo_action, redo_action)
        self.refresh_calendar()

    def undo_created_events(self, event_ids):
        for event_id in event_ids:
            self.undo_created_event(event_id)

    def undo_created_event(self, event_id):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            return
        self.events = delete_event(self.events, self.storage, event)
        if self.selected_event is not None and self.selected_event.id == event_id:
            self.selected_event = None

    def restore_event(self, event):
        if self.find_event_by_id(self.events, event.id) is not None:
            return
        self.store_event(event)

    def restore_events(self, events):
        missing_events = [event for event in events if self.find_event_by_id(self.events, event.id) is None]
        if not missing_events:
            return
        self.store_events(missing_events)

    def undo_edited_event(self, event_id, old_event):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            return
        apply_event_snapshot(event, old_event)
        self.storage.save_event(event)

    def redo_edited_event(self, event_id, new_event):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            return
        apply_event_snapshot(event, new_event)
        self.storage.save_event(event)

    def delete_event_with_undo(self, deleted_event):
        deleted_snapshot = replace(deleted_event)
        self.events = delete_event(self.events, self.storage, deleted_event)
        self.remember_undo(
            lambda event=deleted_snapshot: self.restore_event(event),
            lambda event_id=deleted_snapshot.id: self.redo_deleted_event(event_id),
        )
        self.select_event(None)
        self.refresh_calendar()

    def redo_deleted_event(self, event_id):
        event = self.find_event_by_id(self.events, event_id)
        if event is None:
            return
        self.events = delete_event(self.events, self.storage, event)

    def delete_events_with_undo(self, deleted_events):
        deleted_snapshots = [replace(event) for event in deleted_events]
        self.events = delete_events(self.events, self.storage, deleted_events)
        deleted_event_ids = [event.id for event in deleted_snapshots]
        self.remember_undo(
            lambda events=deleted_snapshots: self.restore_events(events),
            lambda event_ids=deleted_event_ids: self.redo_deleted_events(event_ids),
        )
        self.clear_all_selections()
        self.refresh_calendar()

    def redo_deleted_events(self, event_ids):
        for event_id in event_ids:
            event = self.find_event_by_id(self.events, event_id)
            if event is not None:
                self.events = delete_event(self.events, self.storage, event)
