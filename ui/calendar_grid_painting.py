from datetime import timedelta

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen

from domain.event_status import (
    EVENT_STATUS_COLORS,
    EVENT_STATUS_NORMAL,
    EVENT_STATUS_TEXT_BOLD,
    EVENT_STATUS_TEXT_COLORS,
)


class CalendarGridPaintingMixin:
    def calendar_font(self, bold=False):
        font = QFont("Sans Serif")
        font.setStyleHint(QFont.SansSerif)
        font.setPixelSize(self.time_axis_pixel_size)
        font.setBold(bold)
        return font

    def event_font(self, bold=False, pixel_size=16):
        font = QFont("Sans Serif")
        font.setStyleHint(QFont.SansSerif)
        font.setPixelSize(pixel_size)
        font.setBold(bold)
        return font

    def event_time_font(self):
        return self.event_font(bold=True, pixel_size=self.event_time_pixel_size)

    def event_note_marker_font(self):
        return self.event_font(bold=True, pixel_size=max(10, self.note_marker_size - 6))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(self.theme_colors["normal_event_background"]))
        self.draw_time_grid(painter)
        self.draw_day_column_lines(painter)
        self.draw_selection(painter)
        self.draw_selected_slots(painter)
        self.draw_events(painter)

    def draw_selected_slots(self, painter):
        for slot_datetime in sorted(self.selected_slot_datetimes):
            end_at = slot_datetime + timedelta(minutes=self.slot_minutes)
            slot_rect = self.rect_for_range(slot_datetime, end_at)
            if slot_rect is None:
                continue
            selected_color = QColor(96, 165, 250, 95)
            painter.fillRect(slot_rect, selected_color)
            painter.setPen(QPen(QColor(self.theme_colors["selection_border"]), self.selected_border_width))
            painter.drawRect(slot_rect)

    def draw_day_column_lines(self, painter):
        painter.setPen(QPen(QColor(self.theme_colors["grid_line"])))
        for day_index in range(7):
            column_rect = self.day_column_rect(day_index)
            painter.drawLine(column_rect.left(), 0, column_rect.left(), self.height())
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

    def draw_time_grid(self, painter):
        painter.setFont(self.calendar_font())
        for slot_index in range(self.total_slots() + 1):
            y = self.y_for_slot_index(slot_index)
            is_hour_line = slot_index % 2 == 0
            line_color = QColor(self.theme_colors["grid_line"] if is_hour_line else self.theme_colors["grid_half_line"])
            painter.setPen(QPen(line_color))
            painter.drawLine(self.time_axis_width, y, self.width(), y)
            if is_hour_line:
                hour = self.day_start_hour + slot_index // 2
                time_text = f"{hour:02d}:00"
                text_rect = QRect(0, y + 2, self.time_axis_width - 8, 20)
                painter.setPen(QPen(QColor(self.theme_colors["muted_text"])))
                painter.drawText(text_rect, Qt.AlignRight | Qt.AlignTop, time_text)
        painter.setPen(QPen(QColor(self.theme_colors["grid_line"])))
        painter.drawLine(self.time_axis_width, 0, self.time_axis_width, self.height())

    def draw_selection(self, painter):
        if self.selection_anchor is None or self.selection_current is None:
            return
        for start_at, end_at in self.selection_ranges():
            selection_rect = self.rect_for_range(start_at, end_at)
            if selection_rect is None:
                continue
            selection_color = QColor(59, 130, 246, 125)
            painter.fillRect(selection_rect, selection_color)
            painter.setPen(QPen(QColor(self.theme_colors["selection_border"]), self.selected_border_width))
            painter.drawRect(selection_rect)

    def draw_events(self, painter):
        for event in self.events:
            event_rect = self.event_rect_for_display(event)
            if event_rect is None:
                continue
            is_selected = event.id in self.selected_event_ids
            fill_color = self.event_fill_color(event)
            border_color = QColor(
                self.theme_colors["selected_event_border"] if is_selected else self.theme_colors["event_border"]
            )
            border_width = self.selected_border_width if is_selected else 1
            painter.fillRect(event_rect, fill_color)
            painter.setPen(QPen(border_color, border_width))
            painter.drawRect(event_rect)
            if self.should_draw_resize_handle(event, "top"):
                painter.setPen(QPen(QColor(self.theme_colors["selected_event_border"]), 3))
                painter.drawLine(event_rect.left(), event_rect.top(), event_rect.right(), event_rect.top())
            if self.should_draw_resize_handle(event, "bottom"):
                painter.setPen(QPen(QColor(self.theme_colors["selected_event_border"]), 3))
                painter.drawLine(event_rect.left(), event_rect.bottom(), event_rect.right(), event_rect.bottom())
            self.draw_event_text(painter, event, event_rect)
            if self.show_note_markers and self.event_has_note(event):
                self.draw_event_note_marker(painter, event_rect)

    def draw_event_text(self, painter, event, event_rect):
        text_color = self.event_text_color(event)
        text_rect = event_rect.adjusted(6, 4, -6, -4)
        time_text = self.format_event_time(event)
        time_height = QFontMetrics(self.event_time_font()).height()
        marker_padding = self.note_marker_size + 8 if self.show_note_markers and self.event_has_note(event) else 0
        time_rect = QRect(text_rect.left(), text_rect.top(), max(0, text_rect.width() - marker_padding), time_height)
        painter.setFont(self.event_time_font())
        painter.setPen(QPen(text_color))
        painter.drawText(time_rect, Qt.AlignTop | Qt.AlignLeft, time_text)
        title_rect = QRect(
            text_rect.left(),
            text_rect.top() + time_height + 2,
            text_rect.width(),
            max(0, text_rect.height() - time_height - 2),
        )
        painter.setFont(
            self.event_font(
                bold=EVENT_STATUS_TEXT_BOLD.get(event.status, False),
                pixel_size=self.event_title_pixel_size,
            )
        )
        painter.setPen(QPen(text_color))
        painter.drawText(
            title_rect,
            Qt.AlignTop | Qt.AlignLeft | Qt.TextWordWrap,
            event.title,
        )

    def draw_event_note_marker(self, painter, event_rect):
        marker_size = self.note_marker_size
        marker_rect = QRect(event_rect.right() - marker_size - 5, event_rect.top() + 5, marker_size, marker_size)
        painter.fillRect(marker_rect, QColor("#facc15"))
        painter.setPen(QPen(QColor("#111827"), 1))
        painter.drawRect(marker_rect)
        painter.setFont(self.event_note_marker_font())
        painter.drawText(marker_rect, Qt.AlignCenter, "N")

    def event_has_note(self, event):
        return bool(event.note.strip())

    def event_fill_color(self, event):
        if event.status == EVENT_STATUS_NORMAL:
            return QColor(self.theme_colors["normal_event_background"])
        return QColor(EVENT_STATUS_COLORS.get(event.status, EVENT_STATUS_COLORS[EVENT_STATUS_NORMAL]))

    def event_text_color(self, event):
        if event.status == EVENT_STATUS_NORMAL:
            return QColor(self.theme_colors["normal_event_text"])
        return QColor(EVENT_STATUS_TEXT_COLORS.get(event.status, self.theme_colors["text"]))

    def format_event_time(self, event):
        start_text = event.start_at.strftime("%H:%M")
        end_text = event.end_at.strftime("%H:%M")
        return f"{start_text}-{end_text}"

    def format_event(self, event):
        return f"{self.format_event_time(event)}\n{event.title}"
