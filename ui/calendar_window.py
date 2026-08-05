from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from storage.event_storage import DATABASE_PATH
from ui.calendar_clipboard import CalendarClipboardMixin
from ui.calendar_details import CalendarDetailsMixin
from ui.calendar_details_actions import CalendarDetailsActionsMixin
from ui.calendar_events import CalendarEventsMixin
from ui.calendar_history import CalendarHistoryMixin
from ui.calendar_overview import CalendarOverviewMixin
from ui.calendar_overview_details import CalendarOverviewDetailsMixin
from ui.calendar_settings import CalendarSettingsMixin
from ui.calendar_shortcuts import setup_window_shortcuts
from ui.calendar_week import CalendarWeekMixin
from ui.calendar_window_connections import connect_calendar_window_signals
from ui.calendar_window_layout import setup_calendar_window_layout
from ui.calendar_window_state import initialize_calendar_window_state
from ui.calendar_window_widgets import initialize_calendar_window_widgets


class CalendarWindow(
    CalendarClipboardMixin,
    CalendarDetailsMixin,
    CalendarDetailsActionsMixin,
    CalendarOverviewMixin,
    CalendarOverviewDetailsMixin,
    CalendarSettingsMixin,
    CalendarHistoryMixin,
    CalendarEventsMixin,
    CalendarWeekMixin,
    QMainWindow,
):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gran-calendar")
        self.resize(1600, 900)
        initialize_calendar_window_state(self, DATABASE_PATH)
        initialize_calendar_window_widgets(self)
        self.calendar_scroll_area.setWidgetResizable(True)
        self.calendar_scroll_area.setWidget(self.calendar_grid)
        self.calendar_grid.set_week_start(self.week_start)
        self.calendar_header.set_week_start(self.week_start)
        connect_calendar_window_signals(self)
        setup_calendar_window_layout(self)
        self.statusBar().hide()
        self.load_events_from_storage()
        self.setup_shortcuts()
        self.update_calendar_header_padding()
        self.select_default_start_slot()
        QApplication.instance().installEventFilter(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_calendar_header_padding()
        if hasattr(self, "calendar_view_stack") and self.calendar_view_stack.currentWidget() == self.month_overview:
            self.update_year_overview_calendar_sizes()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Wheel and self.should_scroll_window_from_wheel(watched):
            if self.should_keep_widget_wheel_scroll(watched):
                return super().eventFilter(watched, event)
            self.scroll_active_calendar_area(event)
            return True
        return super().eventFilter(watched, event)

    def should_keep_widget_wheel_scroll(self, watched):
        if not hasattr(self, "month_day_events"):
            return False
        return watched is self.month_day_events or self.month_day_events.isAncestorOf(watched)

    def should_scroll_window_from_wheel(self, watched):
        if not isinstance(watched, QWidget):
            return False
        return watched is self or self.isAncestorOf(watched)

    def scroll_active_calendar_area(self, event):
        scroll_area = self.year_overview_scroll_area
        if self.calendar_view_stack.currentWidget() != self.month_overview:
            scroll_area = self.calendar_scroll_area
        scrollbar = scroll_area.verticalScrollBar()
        pixel_delta = event.pixelDelta().y()
        angle_delta = event.angleDelta().y()
        scroll_delta = pixel_delta if pixel_delta else angle_delta
        scrollbar.setValue(scrollbar.value() - scroll_delta)

    def update_calendar_header_padding(self):
        scrollbar = self.calendar_scroll_area.verticalScrollBar()
        right_padding = scrollbar.sizeHint().width() if scrollbar.isVisible() else 0
        self.calendar_header.set_right_padding(right_padding)

    def setup_shortcuts(self):
        setup_window_shortcuts(self)

    def clear_all_selections(self):
        self.selected_event = None
        self.selected_details_ranges = []
        self.calendar_grid.clear_selection()
        if self.calendar_view_stack.currentWidget() == self.month_overview:
            self.details_view_stack.setCurrentWidget(self.month_day_details)
            return
        self.update_event_details_panel()
