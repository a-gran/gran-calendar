from datetime import datetime, timedelta

from domain.event_index import (
    build_event_date_index,
    build_event_id_index,
    events_for_range,
    find_event_by_id,
    sort_events,
)


def test_event_index_finds_event_by_id(make_event):
    event = make_event(event_id="event-1")

    events_by_id = build_event_id_index([event])

    assert find_event_by_id([event], events_by_id, "event-1") == event


def test_event_index_falls_back_to_supplied_event_list(make_event):
    event = make_event(event_id="event-1")

    assert find_event_by_id([event], {}, "event-1") == event


def test_event_date_index_tracks_multi_day_events(make_event):
    start_at = datetime(2026, 7, 27, 23, 30)
    event = make_event(start_at=start_at, duration_minutes=120)

    events_by_date = build_event_date_index([event])

    assert event in events_by_date[start_at.date()]
    assert event in events_by_date[(start_at + timedelta(days=1)).date()]


def test_events_for_range_returns_overlapping_events_once(make_event):
    event = make_event(start_at=datetime(2026, 7, 27, 23, 30), duration_minutes=120)
    events_by_date = build_event_date_index([event])

    result = events_for_range(events_by_date, datetime(2026, 7, 27, 23, 45), datetime(2026, 7, 28, 0, 15))

    assert result == [event]


def test_sort_events_uses_start_then_creation_time(make_event):
    later_created = make_event(event_id="later", start_at=datetime(2026, 7, 27, 9, 0))
    earlier_created = make_event(event_id="earlier", start_at=datetime(2026, 7, 27, 9, 0))
    earlier_created.created_at = earlier_created.created_at - timedelta(minutes=5)

    result = sort_events([later_created, earlier_created])

    assert result == [earlier_created, later_created]
