from datetime import datetime

from domain.event_update import apply_event_snapshot


def test_apply_event_snapshot_replaces_mutable_event_fields(make_event):
    event = make_event(event_id="event-1", title="Old")
    snapshot = make_event(event_id="event-1", title="New", start_at=datetime(2026, 7, 28, 10, 0))
    snapshot.note = "Updated note"
    snapshot.status = "done"

    apply_event_snapshot(event, snapshot)

    assert event.title == snapshot.title
    assert event.note == snapshot.note
    assert event.start_at == snapshot.start_at
    assert event.end_at == snapshot.end_at
    assert event.created_at == snapshot.created_at
    assert event.updated_at == snapshot.updated_at
    assert event.status == snapshot.status
