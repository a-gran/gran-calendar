from datetime import datetime, time, timedelta

from PySide6.QtCore import Qt


class CalendarGridDragMixin:
    def start_event_move(self, event, anchor_datetime):
        self.is_moving_event = True
        self.moving_event = event
        self.move_anchor_datetime = anchor_datetime
        self.move_original_start = event.start_at
        self.move_original_end = event.end_at
        self.move_preview_start = event.start_at
        self.move_preview_end = event.end_at
        self.move_was_dragged = False
        self.update()

    def update_event_move_preview(self, position):
        if self.moving_event is None or self.move_anchor_datetime is None:
            return
        slot_datetime = self.datetime_from_position(position)
        if slot_datetime is None:
            return
        if slot_datetime != self.move_anchor_datetime:
            self.move_was_dragged = True
        event_duration = self.move_original_end - self.move_original_start
        move_delta = slot_datetime - self.move_anchor_datetime
        new_start = self.move_original_start + move_delta
        new_start = self.clamped_event_start(new_start, event_duration)
        self.move_preview_start = new_start
        self.move_preview_end = new_start + event_duration
        self.update()

    def clamped_event_start(self, start_at, event_duration):
        day_start = datetime.combine(start_at.date(), time(hour=self.day_start_hour))
        day_end = datetime.combine(start_at.date(), time(hour=self.day_end_hour))
        latest_start = day_end - event_duration
        if start_at < day_start:
            return day_start
        if start_at > latest_start:
            return latest_start
        return start_at

    def finish_event_move(self):
        moved_event = self.moving_event
        start_at = self.move_preview_start
        end_at = self.move_preview_end
        was_dragged = self.move_was_dragged
        self.is_moving_event = False
        self.moving_event = None
        self.move_anchor_datetime = None
        self.move_original_start = None
        self.move_original_end = None
        self.move_preview_start = None
        self.move_preview_end = None
        self.move_was_dragged = False
        self.update()
        if moved_event is None or not was_dragged:
            return
        if start_at == moved_event.start_at and end_at == moved_event.end_at:
            return
        self.event_moved.emit(moved_event, start_at, end_at)

    def resize_target_at_position(self, position):
        for event in reversed(self.events):
            event_rect = self.event_rect_for_display(event)
            if event_rect is None or not event_rect.contains(position):
                continue
            if abs(position.y() - event_rect.top()) <= self.resize_edge_margin:
                return event, "top"
            if abs(position.y() - event_rect.bottom()) <= self.resize_edge_margin:
                return event, "bottom"
        return None

    def update_resize_hover(self, position):
        resize_target = self.resize_target_at_position(position)
        if resize_target is None:
            self.hover_resize_event_id = None
            self.hover_resize_edge = None
            self.unsetCursor()
        else:
            event, edge = resize_target
            self.hover_resize_event_id = event.id
            self.hover_resize_edge = edge
            self.setCursor(Qt.SizeVerCursor)
        self.update()

    def should_draw_resize_handle(self, event, edge):
        if self.is_resizing_event and self.resizing_event is not None:
            return event.id == self.resizing_event.id and self.resizing_edge == edge
        return self.hover_resize_event_id == event.id and self.hover_resize_edge == edge

    def start_event_resize(self, event, edge):
        self.is_resizing_event = True
        self.resizing_event = event
        self.resizing_edge = edge
        self.resize_preview_start = event.start_at
        self.resize_preview_end = event.end_at
        self.hover_resize_event_id = event.id
        self.hover_resize_edge = edge
        self.selected_event_ids = {event.id}
        self.selected_slot_datetimes.clear()
        self.event_selected.emit(event)
        self.update()

    def update_event_resize_preview(self, position):
        if self.resizing_event is None:
            return
        slot_index = self.slot_index_from_y(position.y())
        event_date = self.resizing_event.start_at.date()
        if self.resizing_edge == "top":
            new_start = self.datetime_for_slot_index(event_date, slot_index)
            latest_start = self.resize_preview_end - timedelta(minutes=self.slot_minutes)
            self.resize_preview_start = min(new_start, latest_start)
        else:
            new_end = self.datetime_for_slot_index(event_date, slot_index + 1)
            earliest_end = self.resize_preview_start + timedelta(minutes=self.slot_minutes)
            self.resize_preview_end = max(new_end, earliest_end)
        self.update()

    def finish_event_resize(self):
        resized_event = self.resizing_event
        start_at = self.resize_preview_start
        end_at = self.resize_preview_end
        self.is_resizing_event = False
        self.resizing_event = None
        self.resizing_edge = None
        self.resize_preview_start = None
        self.resize_preview_end = None
        self.hover_resize_event_id = None
        self.hover_resize_edge = None
        self.unsetCursor()
        self.update()
        if resized_event is None:
            return
        if start_at == resized_event.start_at and end_at == resized_event.end_at:
            return
        self.event_resized.emit(resized_event, start_at, end_at)
