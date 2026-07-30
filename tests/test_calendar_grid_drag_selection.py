from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent

from tests.calendar_grid_helpers import mouse_event
from ui.calendar_grid import CalendarGridWidget


def test_grid_horizontal_drag_creates_ranges_for_multiple_days(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    emitted_ranges = []
    grid.selection_ranges_created.connect(lambda ranges: emitted_ranges.extend(ranges))

    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    second_day_left = grid.day_column_rect(1).left()
    second_point = QPointF(second_day_left + 10, grid.header_height + 10)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, first_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, second_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, second_point))

    assert len(emitted_ranges) == 2
    assert [start.time().strftime("%H:%M") for start, _ in emitted_ranges] == ["06:00", "06:00"]
    assert [end.time().strftime("%H:%M") for _, end in emitted_ranges] == ["06:30", "06:30"]
    assert len(grid.selected_slots()) == 2
    assert [slot.time().strftime("%H:%M") for slot in grid.selected_slots()] == ["06:00", "06:00"]


def test_grid_diagonal_drag_keeps_all_selected_slots(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    emitted_ranges = []
    grid.selection_ranges_created.connect(lambda ranges: emitted_ranges.extend(ranges))

    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    second_day_left = grid.day_column_rect(1).left()
    third_slot_point = QPointF(second_day_left + 10, grid.y_for_slot_index(2) + 10)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, first_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, third_slot_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, third_slot_point))

    assert len(emitted_ranges) == 2
    assert [start.time().strftime("%H:%M") for start, _ in emitted_ranges] == ["06:00", "06:00"]
    assert [end.time().strftime("%H:%M") for _, end in emitted_ranges] == ["07:30", "07:30"]
    assert len(grid.selected_slots()) == 6
    assert [slot.time().strftime("%H:%M") for slot in grid.selected_slots()] == [
        "06:00",
        "06:30",
        "07:00",
        "06:00",
        "06:30",
        "07:00",
    ]


def test_grid_vertical_drag_keeps_all_selected_slots(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    emitted_ranges = []
    grid.selection_created.connect(lambda start_at, end_at: emitted_ranges.append((start_at, end_at)))

    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    third_slot_point = QPointF(grid.time_axis_width + 10, grid.y_for_slot_index(2) + 10)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, first_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, third_slot_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, third_slot_point))

    assert len(emitted_ranges) == 1
    assert [slot.time().strftime("%H:%M") for slot in grid.selected_slots()] == ["06:00", "06:30", "07:00"]
