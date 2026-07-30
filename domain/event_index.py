from datetime import timedelta


def sort_events(events):
    return sorted(events, key=lambda event: (event.start_at, event.created_at))


def build_event_id_index(events):
    return {event.id: event for event in events}


def build_event_date_index(events):
    events_by_date = {}
    for event in events:
        current_date = event.start_at.date()
        last_date = (event.end_at - timedelta(microseconds=1)).date()
        while current_date <= last_date:
            events_by_date.setdefault(current_date, []).append(event)
            current_date += timedelta(days=1)
    return events_by_date


def events_for_range(events_by_date, start_at, end_at):
    if end_at <= start_at:
        return []
    current_date = start_at.date()
    last_date = (end_at - timedelta(microseconds=1)).date()
    result = []
    seen_ids = set()
    while current_date <= last_date:
        for event in events_by_date.get(current_date, []):
            if event.id in seen_ids:
                continue
            if start_at < event.end_at and end_at > event.start_at:
                result.append(event)
                seen_ids.add(event.id)
        current_date += timedelta(days=1)
    return result


def find_event_by_id(events, events_by_id, event_id):
    if events_by_id is not None:
        event = events_by_id.get(event_id)
        if event is not None:
            return event
    for event in events:
        if event.id == event_id:
            return event
    return None
