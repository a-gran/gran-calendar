from datetime import timedelta

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

from domain.event_status import (
    CALENDAR_EMPTY_CELL_COLOR,
    EVENT_STATUS_COLORS,
    EVENT_STATUS_TEXT_BOLD,
    EVENT_STATUS_TEXT_COLORS,
)


class CalendarGridPaintingMixin:
    def calendar_font(self, bold=False):
        font = QFont("Sans Serif")
        font.setStyleHint(QFont.SansSerif)
        font.setPixelSize(16)
        font.setBold(bold)
        return font

    def event_font(self, bold=False):
        font = QFont("Sans Serif")
        font.setStyleHint(QFont.SansSerif)
        font.setPixelSize(16)
        font.setBold(bold)
        return font

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(CALENDAR_EMPTY_CELL_COLOR))
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
            painter.setPen(QPen(QColor("#93c5fd"), self.selected_border_width))
            painter.drawRect(slot_rect)

    def draw_day_column_lines(self, painter):
        painter.setPen(QPen(QColor("#334155")))
        for day_index in range(7):
            column_rect = self.day_column_rect(day_index)
            painter.drawLine(column_rect.left(), 0, column_rect.left(), self.height())
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

    def draw_time_grid(self, painter):
        painter.setFont(self.calendar_font())
        for slot_index in range(self.total_slots() + 1):
            y = self.y_for_slot_index(slot_index)
            is_hour_line = slot_index % 2 == 0
            line_color = QColor("#334155") if is_hour_line else QColor("#1e293b")
            painter.setPen(QPen(line_color))
            painter.drawLine(self.time_axis_width, y, self.width(), y)
            if is_hour_line:
                hour = self.day_start_hour + slot_index // 2
                time_text = f"{hour:02d}:00"
                text_rect = QRect(0, y + 2, self.time_axis_width - 8, 20)
                painter.setPen(QPen(QColor("#94a3b8")))
                painter.drawText(text_rect, Qt.AlignRight | Qt.AlignTop, time_text)
        painter.setPen(QPen(QColor("#334155")))
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
            painter.setPen(QPen(QColor("#93c5fd"), self.selected_border_width))
            painter.drawRect(selection_rect)

    def draw_events(self, painter):
        for event in self.events:
            event_rect = self.event_rect_for_display(event)
            if event_rect is None:
                continue
            is_selected = event.id in self.selected_event_ids
            fill_color = QColor(EVENT_STATUS_COLORS.get(event.status, EVENT_STATUS_COLORS["normal"]))
            border_color = QColor("#ffffff") if is_selected else QColor("#60a5fa")
            border_width = self.selected_border_width if is_selected else 1
            painter.fillRect(event_rect, fill_color)
            painter.setPen(QPen(border_color, border_width))
            painter.drawRect(event_rect)
            if self.should_draw_resize_handle(event, "top"):
                painter.setPen(QPen(QColor("#ffffff"), 3))
                painter.drawLine(event_rect.left(), event_rect.top(), event_rect.right(), event_rect.top())
            if self.should_draw_resize_handle(event, "bottom"):
                painter.setPen(QPen(QColor("#ffffff"), 3))
                painter.drawLine(event_rect.left(), event_rect.bottom(), event_rect.right(), event_rect.bottom())
            event_text = self.format_event(event)
            painter.setFont(self.event_font(bold=EVENT_STATUS_TEXT_BOLD.get(event.status, False)))
            painter.setPen(QPen(QColor(EVENT_STATUS_TEXT_COLORS.get(event.status, "#ffffff"))))
            painter.drawText(
                event_rect.adjusted(6, 4, -6, -4),
                Qt.AlignTop | Qt.AlignLeft | Qt.TextWordWrap,
                event_text,
            )

    def format_event(self, event):
        start_text = event.start_at.strftime("%H:%M")
        end_text = event.end_at.strftime("%H:%M")
        return f"{start_text}-{end_text}\n{event.title}"
