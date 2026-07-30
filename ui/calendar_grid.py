from datetime import date, datetime, timedelta

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ui.calendar_grid_drag import CalendarGridDragMixin
from ui.calendar_grid_geometry import CalendarGridGeometryMixin
from ui.calendar_grid_mouse import CalendarGridMouseMixin
from ui.calendar_grid_painting import CalendarGridPaintingMixin
from ui.calendar_grid_selection import CalendarGridSelectionMixin


class CalendarGridWidget(
    CalendarGridDragMixin,
    CalendarGridGeometryMixin,
    CalendarGridMouseMixin,
    CalendarGridPaintingMixin,
    CalendarGridSelectionMixin,
    QWidget,
):
    day_names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    selection_created = Signal(datetime, datetime)
    selection_ranges_created = Signal(object)
    event_selected = Signal(object)
    event_double_clicked = Signal(object)
    event_resized = Signal(object, datetime, datetime)
    event_moved = Signal(object, datetime, datetime)
    slot_double_clicked = Signal(datetime)
    slot_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.day_start_hour = 6
        self.day_end_hour = 22
        self.slot_minutes = 30
        self.time_axis_width = 72
        self.header_height = 0
        self.slot_height = 36
        self.event_text_vertical_padding = 12
        self.event_padding = 4
        self.selected_border_width = 3
        self.week_start = date.today() - timedelta(days=date.today().weekday())
        self.events = []
        self.selected_event_ids = set()
        self.selected_slot_datetimes = set()
        self.is_selecting = False
        self.selection_start = None
        self.selection_anchor = None
        self.selection_end = None
        self.selection_current = None
        self.selection_was_dragged = False
        self.resize_edge_margin = 4
        self.is_resizing_event = False
        self.resizing_event = None
        self.resizing_edge = None
        self.resize_preview_start = None
        self.resize_preview_end = None
        self.hover_resize_event_id = None
        self.hover_resize_edge = None
        self.is_moving_event = False
        self.moving_event = None
        self.move_anchor_datetime = None
        self.move_original_start = None
        self.move_original_end = None
        self.move_preview_start = None
        self.move_preview_end = None
        self.move_was_dragged = False
        self.slot_heights_cache = None
        self.slot_tops_cache = None
        self.slot_cache_width = None
        self.event_rects_cache = {}
        self.event_rects_cache_is_valid = False
        self.event_rects_cache_width = None
        self.event_rects_cache_week_start = None
        self.minimum_height_value = 0
        self.setMouseTracking(True)
        self.update_minimum_height()

    def set_week_start(self, week_start):
        self.week_start = week_start
        self.invalidate_event_rects_cache()
        self.update()

    def set_events(self, events):
        self.events = list(events)
        available_event_ids = {event.id for event in self.events}
        self.selected_event_ids.intersection_update(available_event_ids)
        self.invalidate_slot_cache()
        self.update_minimum_height()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.invalidate_slot_cache()
        self.update_minimum_height()

    def set_selected_event_id(self, event_id):
        if event_id is None:
            self.selected_event_ids.clear()
        else:
            self.selected_event_ids = {event_id}
            self.selected_slot_datetimes.clear()
        self.update()
