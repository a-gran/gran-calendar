from datetime import datetime

from PySide6.QtCore import QPoint

from domain.event_limits import MAX_EVENT_TITLE_LENGTH
from ui.calendar_grid import CalendarGridWidget


def test_grid_has_expected_day_range(qt_app):
    grid = CalendarGridWidget()

    assert grid.day_start_hour == 6
    assert grid.day_end_hour == 22
    assert grid.slot_minutes == 30
    assert grid.total_slots() == 32
    assert grid.header_height == 0
    assert grid.selected_border_width == 3
    assert grid.day_names == ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def test_grid_converts_position_to_datetime(qt_app):
    grid = CalendarGridWidget()
    grid.resize(720, 600)

    position = QPoint(grid.time_axis_width + 10, grid.header_height + 10)
    slot_datetime = grid.datetime_from_position(position)

    assert slot_datetime.time().strftime("%H:%M") == "06:00"


def test_grid_expands_only_row_with_long_event(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=17, minute=30)
    title = "Very long event title for checking adaptive calendar row height"[:MAX_EVENT_TITLE_LENGTH]
    event = make_event(event_id="long", title=title, start_at=start_at)

    grid.set_events([event])

    heights = grid.slot_heights()
    target_slot = grid.slot_index_for_datetime(start_at)

    assert heights[target_slot] > grid.slot_height
    assert all(height == grid.slot_height for index, height in enumerate(heights) if index != target_slot)


def test_grid_reuses_slot_height_cache_until_invalidated(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(720, 600)
    start_at = datetime.combine(grid.week_start, datetime.min.time()).replace(hour=17, minute=30)
    event = make_event(event_id="cached", title="Cached event title", start_at=start_at)

    grid.set_events([event])

    first_heights = grid.slot_heights()
    second_heights = grid.slot_heights()

    assert first_heights is second_heights

    grid.invalidate_slot_cache()

    assert grid.slot_heights() is not first_heights
