from datetime import datetime, timedelta

from ui.calendar_grid import CalendarGridWidget


def make_many_events(make_event, week_start, count=280):
    events = []
    day_start = datetime.combine(week_start, datetime.min.time()).replace(hour=6)
    for index in range(count):
        day_offset = index % 7
        slot_offset = index % 32
        start_at = day_start + timedelta(days=day_offset, minutes=slot_offset * 30)
        events.append(
            make_event(
                event_id=f"perf-{index}",
                title=f"Performance event {index}",
                start_at=start_at,
                duration_minutes=30,
            )
        )
    return events


def test_grid_reuses_geometry_cache_for_many_events(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(1280, 900)
    events = make_many_events(make_event, grid.week_start)

    grid.set_events(events)

    first_heights = grid.slot_heights()
    first_tops = grid.slot_tops()
    first_rects = grid.event_rects()

    for _ in range(100):
        assert grid.slot_heights() is first_heights
        assert grid.slot_tops() is first_tops
        assert grid.event_rects() is first_rects


def test_grid_calculates_many_event_rects(qt_app, make_event):
    grid = CalendarGridWidget()
    grid.resize(1280, 900)
    events = make_many_events(make_event, grid.week_start)

    grid.set_events(events)
    rects = [grid.rect_for_range(event.start_at, event.end_at) for event in events]

    assert len(rects) == len(events)
    assert all(rect is not None for rect in rects)


def test_grid_reuses_empty_event_rect_cache(qt_app):
    grid = CalendarGridWidget()
    grid.resize(1280, 900)

    first_rects = grid.event_rects()

    assert grid.event_rects() is first_rects
