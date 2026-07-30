from dataclasses import replace

from domain.clock import current_datetime
from domain.event_factory import create_event
from domain.event_limits import MAX_EVENT_NOTE_LENGTH, MAX_EVENT_TITLE_LENGTH


class CalendarDetailsActionsMixin:
    def delete_selected_event_from_details(self):
        if self.selected_event is None:
            self.show_status_message("Select an event to delete.", 3000)
            return
        event = self.find_event_by_id(self.events, self.selected_event.id)
        if event is None:
            self.show_status_message("Selected event was already deleted.", 3000)
            self.select_event(None)
            return
        self.delete_event_with_undo(event)

    def limit_event_details_note(self):
        if self.is_updating_event_details:
            return
        note = self.event_details_note.toPlainText()
        if len(note) <= MAX_EVENT_NOTE_LENGTH:
            return
        cursor = self.event_details_note.textCursor()
        position = min(cursor.position(), MAX_EVENT_NOTE_LENGTH)
        self.event_details_note.blockSignals(True)
        self.event_details_note.setPlainText(note[:MAX_EVENT_NOTE_LENGTH])
        cursor = self.event_details_note.textCursor()
        cursor.setPosition(position)
        self.event_details_note.setTextCursor(cursor)
        self.event_details_note.blockSignals(False)

    def limit_event_details_title(self):
        if self.is_updating_event_details:
            return
        title = self.event_details_title.toPlainText()
        if len(title) <= MAX_EVENT_TITLE_LENGTH:
            return
        cursor = self.event_details_title.textCursor()
        position = min(cursor.position(), MAX_EVENT_TITLE_LENGTH)
        self.event_details_title.blockSignals(True)
        self.event_details_title.setPlainText(title[:MAX_EVENT_TITLE_LENGTH])
        cursor = self.event_details_title.textCursor()
        cursor.setPosition(position)
        self.event_details_title.setTextCursor(cursor)
        self.event_details_title.blockSignals(False)

    def save_event_details(self):
        if self.selected_event is None:
            self.create_events_from_details_ranges()
            return
        self.update_selected_event_from_details()

    def creation_details_date_text(self):
        dates = {start_at.date() for start_at, _end_at in self.selected_details_ranges}
        if len(dates) == 1:
            return self.selected_details_ranges[0][0].strftime("%d.%m.%Y")
        first_date = self.selected_details_ranges[0][0].strftime("%d.%m.%Y")
        last_date = self.selected_details_ranges[-1][0].strftime("%d.%m.%Y")
        return f"{first_date} - {last_date}"

    def create_events_from_details_ranges(self):
        if not self.selected_details_ranges:
            return
        if any(self.has_event_overlap(start_at, end_at) for start_at, end_at in self.selected_details_ranges):
            self.show_status_message("There is already an event in the selected time.", 4000)
            return
        title = self.event_details_title.text().strip()
        if not title:
            self.show_status_message("Event title is required.", 3000)
            return
        current_moment = current_datetime()
        created_events = []
        for start_at, end_at in self.selected_details_ranges:
            event = create_event(
                title=title,
                note=self.event_details_note.toPlainText(),
                start_at=start_at,
                end_at=end_at,
                status=self.event_details_status.currentData(),
                current_moment=current_moment,
            )
            created_events.append(event)
        event_snapshots = [replace(event) for event in created_events]
        event_ids = [event.id for event in created_events]
        self.remember_undo(
            lambda event_ids=event_ids: self.undo_created_events(event_ids),
            lambda events=event_snapshots: self.restore_events(events),
        )
        self.selected_details_ranges = []
        self.store_events(created_events)
        self.select_event(created_events[-1])

    def update_selected_event_from_details(self):
        if self.selected_event is None:
            return
        event = self.find_event_by_id(self.events, self.selected_event.id)
        if event is None:
            self.selected_event = None
            self.update_event_details_panel()
            return
        title = self.event_details_title.text().strip()
        if not title:
            self.show_status_message("Event title is required.", 3000)
            return
        old_event = replace(event)
        event.title = title
        event.note = self.event_details_note.toPlainText()
        event.status = self.event_details_status.currentData()
        event.updated_at = current_datetime()
        self.storage.save_event(event)
        new_event = replace(event)
        self.remember_undo(
            lambda event_id=event.id, old_event=old_event: self.undo_edited_event(event_id, old_event),
            lambda event_id=event.id, new_event=new_event: self.redo_edited_event(event_id, new_event),
        )
        self.refresh_calendar()
