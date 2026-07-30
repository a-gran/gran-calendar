from datetime import datetime

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent

from tests.calendar_grid_helpers import click_grid, mouse_event
from ui.calendar_grid import CalendarGridWidget


def test_grid_click_selects_single_slot(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    second_point = QPointF(grid.time_axis_width + 10, grid.y_for_slot_index(1) + 10)

    click_grid(grid, first_point)
    click_grid(grid, second_point)

    assert len(grid.selected_slots()) == 1
    assert grid.selected_slots()[0].time().strftime("%H:%M") == "06:30"

    click_grid(grid, second_point)

    assert len(grid.selected_slots()) == 1
    assert grid.selected_slots()[0].time().strftime("%H:%M") == "06:30"


def test_grid_ctrl_click_selects_multiple_slots(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    first_point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)
    second_point = QPointF(grid.time_axis_width + 10, grid.y_for_slot_index(1) + 10)

    click_grid(grid, first_point)
    click_grid(grid, second_point, Qt.ControlModifier)

    assert len(grid.selected_slots()) == 2

    click_grid(grid, first_point, Qt.ControlModifier)

    assert len(grid.selected_slots()) == 1

    grid.clear_selection()

    assert grid.selected_slots() == []


def test_grid_double_click_emits_slot_signal(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    emitted_slots = []
    grid.slot_double_clicked.connect(lambda slot_datetime: emitted_slots.append(slot_datetime))
    point = QPointF(grid.time_axis_width + 10, grid.header_height + 10)

    grid.mouseDoubleClickEvent(mouse_event(QMouseEvent.MouseButtonDblClick, point))

    assert len(emitted_slots) == 1
    assert emitted_slots[0].time().strftime("%H:%M") == "06:00"


def test_grid_click_selects_event(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=7)
    event = make_event(event_id="clicked", start_at=start_at)
    selected_events = []

    grid.set_events([event])
    grid.event_selected.connect(lambda selected_event: selected_events.append(selected_event))
    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    point = QPointF(event_rect.left() + 5, event_rect.top() + 5)
    click_grid(grid, point)

    assert grid.selected_event_ids_list() == ["clicked"]
    assert selected_events[-1].id == "clicked"


def test_grid_double_click_selects_event(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=7)
    event = make_event(event_id="double-clicked", start_at=start_at)
    selected_events = []

    grid.set_events([event])
    grid.event_selected.connect(lambda selected_event: selected_events.append(selected_event))
    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    point = QPointF(event_rect.left() + 5, event_rect.top() + 5)
    grid.mouseDoubleClickEvent(mouse_event(QMouseEvent.MouseButtonDblClick, point))

    assert grid.selected_event_ids_list() == ["double-clicked"]
    assert selected_events[-1].id == "double-clicked"


def test_grid_event_click_selects_single_event(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    first_start = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=7)
    second_start = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    first_event = make_event(event_id="first", start_at=first_start)
    second_event = make_event(event_id="second", start_at=second_start)

    grid.set_events([first_event, second_event])

    first_rect = grid.rect_for_range(first_event.start_at, first_event.end_at)
    second_rect = grid.rect_for_range(second_event.start_at, second_event.end_at)
    click_grid(grid, QPointF(first_rect.left() + 5, first_rect.top() + 5))
    click_grid(grid, QPointF(second_rect.left() + 5, second_rect.top() + 5))

    assert grid.selected_event_ids_list() == ["second"]
    assert grid.selected_slots() == []


def test_grid_ctrl_event_click_selects_multiple_events(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    first_start = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=7)
    second_start = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    first_event = make_event(event_id="first", start_at=first_start)
    second_event = make_event(event_id="second", start_at=second_start)

    grid.set_events([first_event, second_event])

    first_rect = grid.rect_for_range(first_event.start_at, first_event.end_at)
    second_rect = grid.rect_for_range(second_event.start_at, second_event.end_at)
    click_grid(grid, QPointF(first_rect.left() + 5, first_rect.top() + 5))
    click_grid(grid, QPointF(second_rect.left() + 5, second_rect.top() + 5), Qt.ControlModifier)

    assert grid.selected_event_ids_list() == ["first", "second"]
    assert grid.selected_slots() == []


def test_grid_set_selected_event_replaces_previous_event_selection(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    first_start = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=7)
    second_start = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=8)
    first_event = make_event(event_id="first", start_at=first_start)
    second_event = make_event(event_id="second", start_at=second_start)

    grid.set_events([first_event, second_event])
    grid.selected_event_ids = {"first", "second"}
    grid.set_selected_event_id("second")

    assert grid.selected_event_ids_list() == ["second"]


def test_grid_empty_slot_click_replaces_selected_event(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=7)
    event = make_event(event_id="kept", start_at=start_at)

    grid.set_events([event])

    event_rect = grid.rect_for_range(event.start_at, event.end_at)
    click_grid(grid, QPointF(event_rect.left() + 5, event_rect.top() + 5))
    click_grid(grid, QPointF(grid.day_column_rect(1).left() + 5, grid.header_height + 5))

    assert grid.selected_event_ids_list() == []
    assert len(grid.selected_slots()) == 1
