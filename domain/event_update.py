from domain.event import Event


def apply_event_snapshot(event: Event, snapshot: Event) -> None:
    event.title = snapshot.title
    event.note = snapshot.note
    event.start_at = snapshot.start_at
    event.end_at = snapshot.end_at
    event.created_at = snapshot.created_at
    event.updated_at = snapshot.updated_at
    event.status = snapshot.status
