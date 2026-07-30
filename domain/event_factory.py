from uuid import uuid4

from domain.clock import current_datetime
from domain.event import Event


def create_event(title, note, start_at, end_at, status, current_moment=None, event_id=None):
    if current_moment is None:
        current_moment = current_datetime()
    if event_id is None:
        event_id = str(uuid4())
    return Event(
        id=event_id,
        title=title,
        note=note,
        start_at=start_at,
        end_at=end_at,
        created_at=current_moment,
        updated_at=current_moment,
        status=status,
    )


def copy_event_to_range(source_event, start_at, current_moment=None, event_id=None):
    event_duration = source_event.end_at - source_event.start_at
    return create_event(
        title=source_event.title,
        note=source_event.note,
        start_at=start_at,
        end_at=start_at + event_duration,
        status=source_event.status,
        current_moment=current_moment,
        event_id=event_id,
    )
