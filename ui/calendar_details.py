from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QLabel, QVBoxLayout

from domain.event_limits import MAX_EVENT_TITLE_LENGTH
from domain.event_status import EVENT_STATUS_NORMAL
from ui.calendar_styles import (
    DETAILS_MESSAGE_STYLE,
    DETAILS_PANEL_STYLE,
    details_label_style,
    details_time_style,
)


class CalendarDetailsMixin:
    def setup_event_details_panel(self):
        self.event_details_panel.setFixedWidth(400)
        self.event_details_panel.setStyleSheet(DETAILS_PANEL_STYLE)
        self.month_day_open_button.clicked.connect(self.open_month_overview_day)
        self.setup_event_details_form()
        self.setup_month_day_details()
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(16, 16, 16, 16)
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.addWidget(self.current_time_label)
        panel_layout.addLayout(time_layout)
        panel_layout.addWidget(self.details_view_stack)
        self.event_details_panel.setLayout(panel_layout)

    def setup_event_details_form(self):
        self.event_details_title.setMaxLength(MAX_EVENT_TITLE_LENGTH)
        self.event_details_title.setFixedHeight(58)
        self.event_details_title.installEventFilter(self)
        self.event_details_title.textChanged.connect(self.limit_event_details_title)
        self.event_details_time.setWordWrap(True)
        self.event_details_time.setStyleSheet(
            details_time_style(self.visual_settings["time_font_size"], self.visual_settings["theme"])
        )
        self.event_details_note.installEventFilter(self)
        self.event_details_note.textChanged.connect(self.limit_event_details_note)
        self.event_details_message.setWordWrap(True)
        self.event_details_message.setStyleSheet(DETAILS_MESSAGE_STYLE)
        self.event_details_message.hide()
        self.event_details_save_button.clicked.connect(self.save_event_details)
        self.event_details_status.status_changed.connect(self.apply_event_details_status)
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        form_layout.addWidget(self.detail_caption("Event"))
        form_layout.addWidget(self.event_details_title)
        form_layout.addWidget(self.detail_caption("Time"))
        form_layout.addWidget(self.event_details_time)
        form_layout.addWidget(self.detail_caption("Status"))
        form_layout.addWidget(self.event_details_status)
        form_layout.addWidget(self.detail_caption("Note"))
        form_layout.addWidget(self.event_details_note, 1)
        form_layout.addWidget(self.event_details_message)
        form_layout.addWidget(self.event_details_save_button)
        self.event_details_form.setLayout(form_layout)
        self.details_view_stack.addWidget(self.event_details_form)

    def setup_month_day_details(self):
        overview_layout = QVBoxLayout()
        overview_layout.setContentsMargins(0, 0, 0, 0)
        overview_layout.setSpacing(10)
        self.month_day_title.setWordWrap(True)
        self.month_day_events.setSelectionMode(QAbstractItemView.NoSelection)
        overview_layout.addWidget(self.detail_caption("Selected Day"))
        overview_layout.addWidget(self.month_day_title)
        overview_layout.addWidget(self.detail_caption("Events"))
        overview_layout.addWidget(self.month_day_events, 1)
        overview_layout.addWidget(self.month_day_open_button)
        self.month_day_details.setLayout(overview_layout)
        self.details_view_stack.addWidget(self.month_day_details)

    def show_status_message(self, message, duration=3000):
        self.event_details_message.setText(message)
        self.event_details_message.show()
        if duration:
            QTimer.singleShot(duration, lambda current_message=message: self.clear_status_message(current_message))

    def clear_status_message(self, expected_message=None):
        if expected_message is not None and self.event_details_message.text() != expected_message:
            return
        self.event_details_message.clear()
        self.event_details_message.hide()

    def detail_caption(self, text):
        label = QLabel(text)
        label.setStyleSheet(details_label_style(self.visual_settings["theme"]))
        return label

    def update_event_details_panel(self):
        self.details_view_stack.setCurrentWidget(self.event_details_form)
        event = self.selected_event
        self.is_updating_event_details = True
        if event is None:
            self.update_empty_slot_details_panel()
            self.is_updating_event_details = False
            return
        current_event = self.find_event_by_id(self.events, event.id)
        if current_event is None:
            self.selected_event = None
            self.is_updating_event_details = False
            self.update_event_details_panel()
            return
        date_text = current_event.start_at.strftime("%d.%m.%Y")
        start_time_text = current_event.start_at.strftime("%H:%M")
        end_time_text = current_event.end_at.strftime("%H:%M")
        time_text = f"{date_text}\n{start_time_text} - {end_time_text}"
        self.event_details_title.setText(current_event.title)
        self.event_details_time.setText(time_text)
        self.event_details_status.setCurrentIndex(max(0, self.event_details_status.findData(current_event.status)))
        self.event_details_note.setPlainText(current_event.note)
        self.set_event_details_enabled(True)
        self.event_details_save_button.setText("Save")
        self.event_details_panel.show()
        self.is_updating_event_details = False

    def update_empty_slot_details_panel(self):
        if not self.selected_details_ranges:
            self.event_details_title.clear()
            self.event_details_time.setText("")
            self.event_details_status.setCurrentIndex(max(0, self.event_details_status.findData(EVENT_STATUS_NORMAL)))
            self.event_details_note.setPlainText("")
            self.set_event_details_enabled(False)
            self.event_details_save_button.setText("Create")
            self.event_details_panel.show()
            return
        start_at, end_at = self.selected_details_ranges[0]
        date_text = self.creation_details_date_text()
        start_time_text = start_at.strftime("%H:%M")
        end_time_text = end_at.strftime("%H:%M")
        self.event_details_title.clear()
        self.event_details_time.setText(f"{date_text}\n{start_time_text} - {end_time_text}")
        self.event_details_status.setCurrentIndex(max(0, self.event_details_status.findData(EVENT_STATUS_NORMAL)))
        self.event_details_note.setPlainText("")
        self.set_event_details_enabled(True)
        self.event_details_save_button.setText("Create")
        self.event_details_panel.show()

    def set_event_details_enabled(self, is_enabled):
        self.event_details_title.setEnabled(is_enabled)
        self.event_details_status.setEnabled(is_enabled)
        self.event_details_note.setEnabled(is_enabled)
        self.event_details_save_button.setEnabled(is_enabled)

    def eventFilter(self, watched, event):
        if (
            watched in (self.event_details_title, self.event_details_note)
            and event.type() == QEvent.KeyPress
            and event.key() in (Qt.Key_Return, Qt.Key_Enter)
        ):
            if self.event_details_save_button.isEnabled():
                self.save_event_details()
            return True
        return super().eventFilter(watched, event)
