from datetime import date, timedelta

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.calendar_styles import theme_colors


class CalendarHeaderWidget(QWidget):
    day_names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_axis_width = 72
        self.header_height = 36
        self.right_padding = 0
        self.week_start = date.today() - timedelta(days=date.today().weekday())
        self.theme_colors = theme_colors("dark")
        self.setFixedHeight(self.header_height)

    def calendar_font(self):
        font = QFont("Sans Serif")
        font.setStyleHint(QFont.SansSerif)
        font.setPixelSize(16)
        font.setBold(True)
        return font

    def set_week_start(self, week_start):
        self.week_start = week_start
        self.update()

    def set_right_padding(self, right_padding):
        self.right_padding = right_padding
        self.update()

    def set_theme(self, theme_name):
        self.theme_colors = theme_colors(theme_name)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(self.theme_colors["normal_event_background"]))
        painter.setFont(self.calendar_font())
        for day_index in range(7):
            column_rect = self.day_column_rect(day_index)
            current_day = self.week_start + timedelta(days=day_index)
            day_text = f"{self.day_names[day_index]} {current_day.strftime('%d.%m')}"
            painter.setPen(QPen(QColor(self.theme_colors["text"])))
            painter.drawText(column_rect, Qt.AlignCenter, day_text)

    def day_column_rect(self, day_index):
        content_width = max(self.time_axis_width + 1, self.width() - self.right_padding)
        day_width = max(1, int((content_width - self.time_axis_width) / 7))
        left = self.time_axis_width + day_index * day_width
        right = content_width if day_index == 6 else left + day_width
        return QRect(left, 0, right - left, self.header_height)
