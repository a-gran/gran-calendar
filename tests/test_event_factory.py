from datetime import datetime

from domain.event_factory import copy_event_to_range, create_event


def test_create_event_fills_identity_and_timestamps():
    current_moment = datetime(2026, 7, 27, 9, 0)

    event = create_event(
        title="Title",
        note="Note",
        start_at=datetime(2026, 7, 27, 10, 0),
        end_at=datetime(2026, 7, 27, 10, 30),
        status="normal",
        current_moment=current_moment,
        event_id="event-1",
    )

    assert event.id == "event-1"
    assert event.created_at == current_moment
    assert event.updated_at == current_moment


def test_copy_event_to_range_keeps_duration_and_content(make_event):
    source_event = make_event(title="Copied", duration_minutes=90)
    start_at = datetime(2026, 7, 28, 12, 0)

    event = copy_event_to_range(source_event, start_at, current_moment=start_at, event_id="event-2")

    assert event.id == "event-2"
    assert event.title == source_event.title
    assert event.note == source_event.note
    assert event.start_at == start_at
    assert event.end_at == datetime(2026, 7, 28, 13, 30)
