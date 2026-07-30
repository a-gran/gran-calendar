from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from domain.event_status import (
    EVENT_STATUS_COLORS,
    EVENT_STATUS_LABELS,
    EVENT_STATUS_NORMAL,
    EVENT_STATUS_TEXT_COLORS,
)


class StatusSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.statuses = list(EVENT_STATUS_LABELS.items())
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
        self.setCurrentStatus(EVENT_STATUS_NORMAL)

    def button_style(self, status):
        background_color = EVENT_STATUS_COLORS.get(status, EVENT_STATUS_COLORS[EVENT_STATUS_NORMAL])
        text_color = EVENT_STATUS_TEXT_COLORS.get(status, "#ffffff")
        return (
            f"QPushButton {{ background-color: {background_color}; color: {text_color}; "
            "border: 1px solid #475569; border-radius: 4px; padding: 5px 8px; "
            "font-size: 14px; font-weight: bold; }"
            "QPushButton:checked { border: 2px solid #ffffff; padding: 4px 7px; }"
            "QPushButton:disabled { background-color: #111827; color: #64748b; border: 1px solid #1e293b; }"
        )

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
