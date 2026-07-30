from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from domain.event_status import (
    EVENT_STATUS_COLORS,
    EVENT_STATUS_LABELS,
    EVENT_STATUS_NORMAL,
    EVENT_STATUS_TEXT_COLORS,
)
from ui.calendar_styles import theme_colors


class StatusSelector(QWidget):
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.statuses = list(EVENT_STATUS_LABELS.items())
        self.theme_colors = theme_colors("dark")
        self.buttons = {}
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        for index, (status, label) in enumerate(self.statuses):
            button = QPushButton(label.upper())
            button.setCheckable(True)
            button.setStyleSheet(self.button_style(status))
            self.button_group.addButton(button, index)
            self.buttons[status] = button
            layout.addWidget(button)
        self.setLayout(layout)
        self.button_group.idClicked.connect(self.emit_status_changed)
        self.setCurrentStatus(EVENT_STATUS_NORMAL)

    def emit_status_changed(self, button_id):
        if button_id < 0 or button_id >= len(self.statuses):
            return
        self.status_changed.emit(self.statuses[button_id][0])

    def button_style(self, status):
        if status == EVENT_STATUS_NORMAL:
            background_color = self.theme_colors["normal_event_background"]
            text_color = self.theme_colors["normal_event_text"]
        else:
            background_color = EVENT_STATUS_COLORS.get(status, EVENT_STATUS_COLORS[EVENT_STATUS_NORMAL])
            text_color = EVENT_STATUS_TEXT_COLORS.get(status, self.theme_colors["text"])
        return (
            f"QPushButton {{ background-color: {background_color}; color: {text_color}; "
            f"border: 1px solid {self.theme_colors['button_border']}; border-radius: 4px; padding: 5px 8px; "
            "font-size: 14px; font-weight: bold; }"
            f"QPushButton:checked {{ border: 2px solid {self.theme_colors['selected_event_border']}; "
            "padding: 4px 7px; }"
            f"QPushButton:disabled {{ background-color: {self.theme_colors['disabled_background']}; "
            f"color: {self.theme_colors['disabled_text']}; border: 1px solid {self.theme_colors['grid_half_line']}; }}"
        )

    def set_theme(self, theme_name):
        self.theme_colors = theme_colors(theme_name)
        for status, button in self.buttons.items():
            button.setStyleSheet(self.button_style(status))

    def findData(self, status):
        for index, (candidate_status, _label) in enumerate(self.statuses):
            if candidate_status == status:
                return index
        return -1

    def setCurrentIndex(self, index):
        if index < 0 or index >= len(self.statuses):
            index = self.findData(EVENT_STATUS_NORMAL)
        self.buttons[self.statuses[index][0]].setChecked(True)

    def setCurrentStatus(self, status):
        self.setCurrentIndex(self.findData(status))

    def currentData(self):
        checked_id = self.button_group.checkedId()
        if checked_id < 0:
            return EVENT_STATUS_NORMAL
        return self.statuses[checked_id][0]

    def currentText(self):
        return EVENT_STATUS_LABELS[self.currentData()]
