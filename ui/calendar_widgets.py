from datetime import date, timedelta

from PySide6.QtCore import QDate, QEvent, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPen
from PySide6.QtWidgets import (
    QCalendarWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTableView,
    QWidget,
)

from domain.event_limits import MAX_EVENT_TITLE_LENGTH
from ui.calendar_styles import OVERVIEW_EVENT_ROW_STYLE, theme_colors


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

    def overview_size_hint(self, available_width):
        layout_spacing = self.layout().spacing()
        buttons_width = self.edit_button.width() + self.action_button.width()
        text_width = max(1, available_width - buttons_width - layout_spacing * 3)
        text_height = QFontMetrics(self.text_label.font()).boundingRect(
            QRect(0, 0, text_width, 2000),
            Qt.AlignTop | Qt.AlignLeft | Qt.TextWordWrap,
            self.text_label.text(),
        ).height()
        row_height = max(text_height, self.edit_button.height(), self.action_button.height()) + 10
        return QSize(0, row_height)

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
    day_selected_from_keyboard = Signal(QDate)

    def __init__(self):
        super().__init__()
        self.visible_year = date.today().year
        self.visible_month = date.today().month
        self.highlighted_date = None
        self.theme_colors = theme_colors("dark")
        self.day_cell_height = 16
        self.day_number_pixel_size = 12
        self.day_number_is_bold = True
        self.month_table_border_color = "#ffffff"
        self.month_table_border_width = 3
        self.is_selected_month = False
        self.calendar_view = None
        self.setFocusPolicy(Qt.StrongFocus)

    def set_visible_month(self, selected_date):
        if self.visible_year == selected_date.year and self.visible_month == selected_date.month:
            return
        self.visible_year = selected_date.year
        self.visible_month = selected_date.month
        self.apply_square_day_cells()
        self.updateCells()

    def set_theme(self, theme_name):
        self.theme_colors = theme_colors(theme_name)
        self.apply_square_day_cells()
        self.updateCells()

    def set_highlighted_date(self, selected_date):
        if self.highlighted_date == selected_date:
            return
        self.highlighted_date = selected_date
        self.apply_square_day_cells()
        self.updateCells()

    def set_day_cell_height(self, cell_height):
        if self.day_cell_height == cell_height:
            return
        self.day_cell_height = cell_height
        self.apply_square_day_cells()
        self.updateCells()

    def set_selected_month(self, is_selected):
        if self.is_selected_month == is_selected:
            return
        self.is_selected_month = is_selected
        self.apply_square_day_cells()
        self.updateCells()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_square_day_cells()

    def wheelEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        if self.handle_calendar_key_press(event):
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched, event):
        if (
            watched == self.calendar_view
            and event.type() == QEvent.KeyPress
            and self.handle_calendar_key_press(event)
        ):
            return True
        return super().eventFilter(watched, event)

    def handle_calendar_key_press(self, event):
        if event.key() == Qt.Key_Left:
            self.move_keyboard_selection(-1)
            return True
        if event.key() == Qt.Key_Right:
            self.move_keyboard_selection(1)
            return True
        if event.key() == Qt.Key_Up:
            self.move_keyboard_selection(-7)
            return True
        if event.key() == Qt.Key_Down:
            self.move_keyboard_selection(7)
            return True
        return False

    def move_keyboard_selection(self, day_delta):
        current_qdate = self.selectedDate()
        current_date = date(current_qdate.year(), current_qdate.month(), current_qdate.day())
        next_date = current_date + timedelta(days=day_delta)
        if next_date.year != self.visible_year or next_date.month != self.visible_month:
            return
        next_qdate = QDate(next_date.year, next_date.month, next_date.day)
        self.setSelectedDate(next_qdate)
        self.day_selected_from_keyboard.emit(next_qdate)

    def apply_square_day_cells(self):
        calendar_view = self.findChild(QTableView, "qt_calendar_calendarview")
        if calendar_view is None:
            return
        if self.calendar_view is None:
            self.calendar_view = calendar_view
            self.calendar_view.installEventFilter(self)
        border_color = "#facc15" if self.is_selected_month else self.month_table_border_color
        calendar_view.setStyleSheet(
            f"QTableView {{ border: {self.month_table_border_width}px solid {border_color}; }}"
        )
        if calendar_view.model() is None:
            return
        row_count = max(1, calendar_view.model().rowCount())
        cell_height = self.day_cell_height
        header_font = calendar_view.horizontalHeader().font()
        header_font.setPixelSize(self.day_number_pixel_size)
        calendar_view.horizontalHeader().setFont(header_font)
        calendar_view.verticalHeader().setMinimumSectionSize(1)
        calendar_view.verticalHeader().setDefaultSectionSize(cell_height)
        calendar_view.horizontalHeader().setFixedHeight(cell_height)
        header_height = calendar_view.horizontalHeader().height()
        frame_height = calendar_view.frameWidth() * 2
        self.setFixedHeight(header_height + cell_height * row_count + frame_height)

    def paintCell(self, painter, rect, qdate):
        cell_date = date(qdate.year(), qdate.month(), qdate.day())
        painter.save()
        day_font = painter.font()
        day_font.setPixelSize(self.day_number_pixel_size)
        day_font.setBold(self.day_number_is_bold)
        painter.setFont(day_font)
        if cell_date == self.highlighted_date:
            painter.fillRect(rect, QColor(self.theme_colors["button_checked"]))
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawText(rect, Qt.AlignCenter, str(qdate.day()))
            painter.restore()
            return
        if qdate.year() == self.visible_year and qdate.month() == self.visible_month:
            painter.fillRect(rect, QColor(self.theme_colors["field_background"]))
            painter.setPen(QPen(QColor(self.theme_colors["grid_half_line"])))
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
            text_color = QColor("#ef4444") if qdate.dayOfWeek() in (6, 7) else QColor(self.theme_colors["text"])
            painter.setPen(QPen(text_color))
            painter.drawText(rect, Qt.AlignCenter, str(qdate.day()))
            painter.restore()
            return
        painter.fillRect(rect, QColor(self.theme_colors["field_background"]))
        painter.setPen(QPen(QColor(self.theme_colors["grid_half_line"])))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
        painter.restore()
