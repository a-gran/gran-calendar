from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QCalendarWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QWidget,
)

from domain.event_limits import MAX_EVENT_TITLE_LENGTH
from ui.calendar_styles import OVERVIEW_EVENT_ROW_STYLE


class MultilineTitleEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.max_length = None

    def setMaxLength(self, max_length):
        self.max_length = max_length

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)


class OverviewEventRow(QWidget):
    delete_requested = Signal(str)
    restore_requested = Signal(str)
    double_clicked = Signal(str)
    title_submitted = Signal(str, str)

    def __init__(self, event_id, text, title):
        super().__init__()
        self.event_id = event_id
        self.is_deleted = False
        self.is_editing = False
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.title_edit = QLineEdit(title)
        self.title_edit.setMaxLength(MAX_EVENT_TITLE_LENGTH)
        self.title_edit.hide()
        self.title_edit.returnPressed.connect(self.submit_title)
        self.edit_button = QPushButton("✎")
        self.edit_button.setFixedSize(24, 24)
        self.edit_button.clicked.connect(self.toggle_title_edit)
        self.action_button = QPushButton("×")
        self.action_button.setFixedSize(24, 24)
        self.action_button.clicked.connect(self.emit_action)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.title_edit, 1)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.action_button)
        self.setLayout(layout)
        self.setStyleSheet(OVERVIEW_EVENT_ROW_STYLE)

    def emit_action(self):
        if self.is_deleted:
            self.restore_requested.emit(self.event_id)
            return
        self.delete_requested.emit(self.event_id)

    def show_restore_action(self):
        self.is_deleted = True
        self.action_button.setText("↶")
        self.edit_button.setEnabled(False)

    def show_delete_action(self):
        self.is_deleted = False
        self.action_button.setText("×")
        self.edit_button.setEnabled(True)

    def set_display_text(self, text, title):
        self.text_label.setText(text)
        self.title_edit.setText(title)
        self.show_display()

    def toggle_title_edit(self):
        if self.is_editing:
            self.submit_title()
            return
        self.is_editing = True
        self.text_label.hide()
        self.title_edit.show()
        self.edit_button.setText("✓")
        self.title_edit.setFocus()
        self.title_edit.setCursorPosition(len(self.title_edit.text()))

    def submit_title(self):
        title = self.title_edit.text().strip()
        if not title:
            self.show_display()
            return
        self.title_submitted.emit(self.event_id, title)

    def show_display(self):
        self.is_editing = False
        self.title_edit.hide()
        self.text_label.show()
        self.edit_button.setText("✎")

    def mouseDoubleClickEvent(self, event):
        if not self.is_deleted and not self.is_editing:
            self.double_clicked.emit(self.event_id)
        super().mouseDoubleClickEvent(event)


class MonthOnlyCalendarWidget(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.visible_year = date.today().year
        self.visible_month = date.today().month

    def set_visible_month(self, selected_date):
        self.visible_year = selected_date.year
        self.visible_month = selected_date.month
        self.updateCells()

    def paintCell(self, painter, rect, qdate):
        if qdate.year() == self.visible_year and qdate.month() == self.visible_month:
            super().paintCell(painter, rect, qdate)
            return
        painter.save()
        painter.fillRect(rect, QColor("#111827"))
        painter.setPen(QPen(QColor("#1f2937")))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
        painter.restore()
