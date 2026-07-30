from datetime import timedelta

from PySide6.QtCore import Qt


class CalendarGridMouseMixin:
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return
        resize_target = self.resize_target_at_position(event.position().toPoint())
        if resize_target is not None:
            resize_event, resize_edge = resize_target
            self.start_event_resize(resize_event, resize_edge)
            return
        clicked_event = self.event_at_position(event.position().toPoint())
        slot_datetime = self.datetime_from_position(event.position().toPoint())
        is_ctrl_pressed = bool(event.modifiers() & Qt.ControlModifier)
        if clicked_event is not None:
            if is_ctrl_pressed:
                is_selected = self.toggle_event_selection(clicked_event.id)
            else:
                is_selected = self.replace_event_selection(clicked_event.id)
            self.event_selected.emit(clicked_event if is_selected else None)
            if is_selected and not is_ctrl_pressed and slot_datetime is not None:
                self.start_event_move(clicked_event, slot_datetime)
            return
        if slot_datetime is None:
            return
        if is_ctrl_pressed:
            self.toggle_slot_selection(slot_datetime)
        else:
            self.replace_slot_selection(slot_datetime)
        selected_slots = self.selected_slots()
        self.slot_selected.emit(selected_slots)
        self.is_selecting = True
        self.selection_was_dragged = False
        self.selection_start = slot_datetime
        self.selection_anchor = slot_datetime
        self.selection_current = slot_datetime
        self.selection_end = slot_datetime + timedelta(minutes=self.slot_minutes)
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_moving_event:
            self.update_event_move_preview(event.position().toPoint())
            return
        if self.is_resizing_event:
            self.update_event_resize_preview(event.position().toPoint())
            return
        if not self.is_selecting:
            self.update_resize_hover(event.position().toPoint())
            super().mouseMoveEvent(event)
            return
        slot_datetime = self.datetime_from_position(event.position().toPoint())
        if slot_datetime is None:
            return
        if slot_datetime != self.selection_anchor:
            self.selection_was_dragged = True
        self.selection_current = slot_datetime
        if slot_datetime >= self.selection_anchor:
            self.selection_start = self.selection_anchor
            self.selection_end = slot_datetime + timedelta(minutes=self.slot_minutes)
        else:
            self.selection_start = slot_datetime
            self.selection_end = self.selection_anchor + timedelta(minutes=self.slot_minutes)
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            super().mouseReleaseEvent(event)
            return
        if self.is_resizing_event:
            self.finish_event_resize()
            return
        if self.is_moving_event:
            self.finish_event_move()
            return
        if not self.is_selecting:
            return
        self.is_selecting = False
        ranges = self.selection_ranges()
        was_dragged = self.selection_was_dragged
        if was_dragged and ranges:
            self.selected_event_ids.clear()
            self.selected_slot_datetimes = set(self.slot_datetimes_for_ranges(ranges))
        self.selection_start = None
        self.selection_anchor = None
        self.selection_end = None
        self.selection_current = None
        self.selection_was_dragged = False
        self.update()
        if was_dragged and ranges:
            if len(ranges) == 1:
                start_at, end_at = ranges[0]
                self.selection_created.emit(start_at, end_at)
            else:
                self.selection_ranges_created.emit(ranges)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            clicked_event = self.event_at_position(event.position().toPoint())
            if clicked_event is not None:
                self.set_selected_event_id(clicked_event.id)
                self.event_selected.emit(clicked_event)
                return
            slot_datetime = self.datetime_from_position(event.position().toPoint())
            if slot_datetime is not None:
                self.selected_slot_datetimes = {slot_datetime}
                self.update()
                self.slot_double_clicked.emit(slot_datetime)
                return
        super().mouseDoubleClickEvent(event)
