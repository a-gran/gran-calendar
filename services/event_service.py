from domain.event_index import sort_events


def add_event(events, storage, event, save=True):
    updated_events = [*events, event]
    if save:
        storage.save_event(event)
    return sort_events(updated_events)


def add_events(events, storage, new_events, save=True):
    updated_events = [*events, *new_events]
    if save:
        for event in new_events:
            storage.save_event(event)
    return sort_events(updated_events)


def delete_event(events, storage, event):
    updated_events = [stored_event for stored_event in events if stored_event.id != event.id]
    storage.delete_event(event)
    return updated_events


def delete_events(events, storage, deleted_events):
    deleted_event_ids = {event.id for event in deleted_events}
    updated_events = [event for event in events if event.id not in deleted_event_ids]
    for event in deleted_events:
        storage.delete_event(event)
    return updated_events
