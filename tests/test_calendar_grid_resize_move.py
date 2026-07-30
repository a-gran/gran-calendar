from datetime import datetime, timedelta

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent

from tests.calendar_grid_helpers import mouse_event
from ui.calendar_grid import CalendarGridWidget


def test_grid_bottom_edge_drag_resizes_event_end(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="resize-bottom", start_at=start_at, duration_minutes=60)
    resized_events = []

    grid.set_events([event])
    grid.event_resized.connect(lambda resized_event, new_start, new_end: resized_events.append((new_start, new_end)))

    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    press_point = QPointF(event_rect.left() + 10, event_rect.bottom() - 2)
    move_point = QPointF(event_rect.left() + 10, grid.y_for_slot_index(grid.slot_index_for_datetime(event.end_at)) + 5)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, press_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, move_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, move_point))

    assert resized_events == [(event.start_at, event.end_at + timedelta(minutes=30))]


def test_grid_top_edge_drag_resizes_event_start(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="resize-top", start_at=start_at, duration_minutes=60)
    resized_events = []

    grid.set_events([event])
    grid.event_resized.connect(lambda resized_event, new_start, new_end: resized_events.append((new_start, new_end)))

    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    start_slot = grid.slot_index_for_datetime(event.start_at)
    press_point = QPointF(event_rect.left() + 10, event_rect.top() + 2)
    move_point = QPointF(event_rect.left() + 10, grid.y_for_slot_index(start_slot - 1) + 5)

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, press_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, move_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, move_point))

    assert resized_events == [(event.start_at - timedelta(minutes=30), event.end_at)]


def test_grid_hovering_event_edge_marks_resize_handle(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="hover-resize", start_at=start_at, duration_minutes=60)

    grid.set_events([event])

    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    hover_point = QPointF(event_rect.left() + 10, event_rect.bottom() - 2)

    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, hover_point))

    assert grid.hover_resize_event_id == "hover-resize"
    assert grid.hover_resize_edge == "bottom"
    assert grid.should_draw_resize_handle(event, "bottom")


def test_grid_dragging_event_body_moves_event(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="move-event", start_at=start_at, duration_minutes=60)
    moved_events = []

    grid.set_events([event])
    grid.event_moved.connect(lambda moved_event, new_start, new_end: moved_events.append((new_start, new_end)))

    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    press_point = QPointF(event_rect.left() + 20, event_rect.top() + 20)
    target_day_left = grid.day_column_rect(1).left()
    move_point = QPointF(
        target_day_left + 20, grid.y_for_slot_index(grid.slot_index_for_datetime(event.start_at) + 1) + 20
    )

    grid.mousePressEvent(mouse_event(QMouseEvent.MouseButtonPress, press_point))
    grid.mouseMoveEvent(mouse_event(QMouseEvent.MouseMove, move_point))
    grid.mouseReleaseEvent(mouse_event(QMouseEvent.MouseButtonRelease, move_point))

    expected_start = event.start_at + timedelta(days=1, minutes=30)

    assert moved_events == [(expected_start, expected_start + timedelta(minutes=60))]
