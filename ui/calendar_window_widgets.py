from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QWidget,
)

from ui.calendar_grid import CalendarGridWidget
from ui.calendar_header import CalendarHeaderWidget
from ui.calendar_styles import MONTH_CALENDAR_BUTTON_TEXT
from ui.calendar_widgets import MonthOnlyCalendarWidget, MultilineTitleEdit
from ui.status_selector import StatusSelector
from ui.year_selector import YearSelector


def initialize_calendar_window_widgets(window):
    window.week_label = QLabel()
    window.week_label.setStyleSheet("font-size: 20px; font-weight: bold;")
    window.previous_week_button = QPushButton("Previous")
    window.current_week_button = QPushButton("Current")
    window.next_week_button = QPushButton("Next")
    window.settings_button = QPushButton("⚙")
    window.settings_button.setFixedSize(32, 32)
    window.settings_button.setToolTip("Settings")
    window.overview_toggle_button = QPushButton(MONTH_CALENDAR_BUTTON_TEXT)
    window.calendar_grid = CalendarGridWidget()
    window.calendar_header = CalendarHeaderWidget()
    window.calendar_view_stack = QStackedWidget()
    window.week_view = QWidget()
    window.month_overview = QWidget()
    window.month_calendar = MonthOnlyCalendarWidget()
    window.year_spinbox = YearSelector()
    window.calendar_scroll_area = QScrollArea()
    window.event_details_panel = QFrame()
    window.details_view_stack = QStackedWidget()
    window.event_details_form = QWidget()
    window.month_day_details = QWidget()
    window.month_day_title = QLabel()
    window.month_day_events = QListWidget()
    window.month_day_open_button = QPushButton("Open Day")
    window.event_details_title = MultilineTitleEdit()
    window.event_details_time = QLabel()
    window.event_details_status = StatusSelector()
    window.event_details_note = QPlainTextEdit()
    window.event_details_message = QLabel()
    window.event_details_save_button = QPushButton("Save")
