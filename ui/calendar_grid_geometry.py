from datetime import datetime, time, timedelta

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QFontMetrics

from domain.event_status import EVENT_STATUS_TEXT_BOLD


class CalendarGridGeometryMixin:
    def update_minimum_height(self):
        self.minimum_height_value = self.header_height + sum(self.slot_heights()) + 1
        self.setMinimumHeight(self.minimum_height_value)

    def invalidate_slot_cache(self):
        self.slot_heights_cache = None
        self.slot_tops_cache = None
        self.slot_cache_width = None
        self.invalidate_event_rects_cache()

    def invalidate_event_rects_cache(self):
        self.event_rects_cache = {}
        self.event_rects_cache_is_valid = False
        self.event_rects_cache_width = None
        self.event_rects_cache_week_start = None

    def slot_heights(self):
        if self.slot_heights_cache is not None and self.slot_cache_width == self.width():
            return self.slot_heights_cache
        heights = [self.slot_height for _ in range(self.total_slots())]
        for event in self.events:
            start_slot = self.slot_index_for_datetime(event.start_at)
            end_slot = self.slot_index_for_datetime(event.end_at)
            if start_slot >= end_slot:
                continue
            needed_height = self.text_height_for_event(event)
            current_height = sum(heights[start_slot:end_slot])
            if needed_height > current_height:
                heights[start_slot] += needed_height - current_height
        self.slot_heights_cache = heights
        self.slot_cache_width = self.width()
        return heights

    def slot_tops(self):
        if self.slot_tops_cache is not None and self.slot_cache_width == self.width():
            return self.slot_tops_cache
        current_y = self.header_height
        tops = [current_y]
        for slot_height in self.slot_heights():
            current_y += slot_height
            tops.append(current_y)
        self.slot_tops_cache = tops
        return tops

    def text_height_for_event(self, event):
        day_width = max(1, int((self.width() - self.time_axis_width) / 7))
        text_width = day_width - self.event_content_padding * 2
        if text_width <= 0:
            return self.slot_height
        time_height = QFontMetrics(self.event_time_font()).height()
        font_metrics = QFontMetrics(
            self.event_font(
                bold=EVENT_STATUS_TEXT_BOLD.get(event.status, False),
                pixel_size=self.event_title_pixel_size,
            )
        )
        measure_rect = QRect(0, 0, text_width, 2000)
        text_rect = font_metrics.boundingRect(
            measure_rect,
            Qt.AlignTop | Qt.AlignLeft | Qt.TextWordWrap,
            event.title,
        )
        needed_height = (
            self.event_content_padding
            + time_height
            + self.event_text_gap
            + text_rect.height()
            + self.event_content_padding
        )
        return max(self.slot_height, needed_height)

    def slot_index_for_datetime(self, value):
        minutes_from_start = (value.hour - self.day_start_hour) * 60 + value.minute
        slot_index = int(minutes_from_start / self.slot_minutes)
        return max(0, min(self.total_slots(), slot_index))

    def y_for_slot_index(self, slot_index):
        slot_index = max(0, min(self.total_slots(), slot_index))
        return self.slot_tops()[slot_index]

    def slot_index_from_y(self, y):
        current_y = self.header_height
        for slot_index, slot_height in enumerate(self.slot_heights()):
            if y < current_y + slot_height:
                return slot_index
            current_y += slot_height
        return self.total_slots() - 1

    def y_for_minutes(self, minutes_from_start):
        minutes_from_start = max(0, min(self.total_slots() * self.slot_minutes, minutes_from_start))
        slot_index = int(minutes_from_start / self.slot_minutes)
        if slot_index >= self.total_slots():
            return self.slot_tops()[-1]
        slot_offset = minutes_from_start % self.slot_minutes
        slot_top = self.y_for_slot_index(slot_index)
        slot_height = self.slot_heights()[slot_index]
        return slot_top + int(slot_offset / self.slot_minutes * slot_height)

    def total_slots(self):
        return int((self.day_end_hour - self.day_start_hour) * 60 / self.slot_minutes)

    def day_column_rect(self, day_index):
        day_width = max(1, int((self.width() - self.time_axis_width) / 7))
        left = self.time_axis_width + day_index * day_width
        right = self.width() if day_index == 6 else left + day_width
        return QRect(left, 0, right - left, self.height())

    def datetime_for_slot_index(self, selected_date, slot_index):
        slot_index = max(0, min(self.total_slots(), slot_index))
        minutes_from_start = slot_index * self.slot_minutes
        day_start = datetime.combine(selected_date, time(hour=self.day_start_hour))
        return day_start + timedelta(minutes=minutes_from_start)

    def datetime_from_position(self, position):
        if position.x() < self.time_axis_width:
            return None
        if position.y() < self.header_height:
            return None
        day_width = max(1, int((self.width() - self.time_axis_width) / 7))
        day_index = int((position.x() - self.time_axis_width) / day_width)
        day_index = max(0, min(6, day_index))
        slot_index = self.slot_index_from_y(position.y())
        slot_index = max(0, min(self.total_slots() - 1, slot_index))
        selected_date = self.week_start + timedelta(days=day_index)
        return self.datetime_for_slot_index(selected_date, slot_index)

    def rect_for_range(self, start_at, end_at):
        day_index = (start_at.date() - self.week_start).days
        if day_index < 0 or day_index > 6:
            return None
        day_start = datetime.combine(start_at.date(), time(hour=self.day_start_hour))
        start_minutes = int((start_at - day_start).total_seconds() / 60)
        end_minutes = int((end_at - day_start).total_seconds() / 60)
        if end_minutes <= 0 or start_minutes >= self.total_slots() * self.slot_minutes:
            return None
        start_minutes = max(0, start_minutes)
        end_minutes = min(self.total_slots() * self.slot_minutes, end_minutes)
        column_rect = self.day_column_rect(day_index)
        top = self.y_for_minutes(start_minutes)
        bottom = self.y_for_minutes(end_minutes)
        return QRect(
            column_rect.left(),
            top,
            column_rect.width(),
            max(self.slot_height, bottom - top),
        )

    def event_at_position(self, position):
        for event in reversed(self.events):
            event_rect = self.event_rect_for_display(event)
            if event_rect is None:
                continue
            if event_rect.contains(position):
                return event
        return None

    def event_rect_for_display(self, event):
        start_at, end_at = self.display_range_for_event(event)
        if start_at != event.start_at or end_at != event.end_at:
            return self.rect_for_range(start_at, end_at)
        return self.event_rects().get(event.id)

    def event_rects(self):
        if (
            self.event_rects_cache_is_valid
            and self.event_rects_cache_width == self.width()
            and self.event_rects_cache_week_start == self.week_start
        ):
            return self.event_rects_cache
        self.event_rects_cache = {}
        for event in self.events:
            event_rect = self.rect_for_range(event.start_at, event.end_at)
            if event_rect is not None:
                self.event_rects_cache[event.id] = event_rect
        self.event_rects_cache_width = self.width()
        self.event_rects_cache_week_start = self.week_start
        self.event_rects_cache_is_valid = True
        return self.event_rects_cache

    def display_range_for_event(self, event):
        if self.is_moving_event and self.moving_event is not None and event.id == self.moving_event.id:
            return self.move_preview_start, self.move_preview_end
        if self.is_resizing_event and self.resizing_event is not None and event.id == self.resizing_event.id:
            return self.resize_preview_start, self.resize_preview_end
        return event.start_at, event.end_at
