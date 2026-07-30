from services.event_service import add_event, add_events, delete_event, delete_events


class FakeStorage:
    def __init__(self):
        self.saved_events = []
        self.deleted_events = []

    def save_event(self, event):
        self.saved_events.append(event)

    def delete_event(self, event):
        self.deleted_events.append(event)


def test_add_event_saves_and_sorts_events(make_event):
    storage = FakeStorage()
    later_event = make_event(event_id="later")
    earlier_event = make_event(event_id="earlier")
    earlier_event.start_at = later_event.start_at.replace(hour=8)

    events = add_event([later_event], storage, earlier_event)

    assert events == [earlier_event, later_event]
    assert storage.saved_events == [earlier_event]


def test_add_events_can_skip_storage_save(make_event):
    storage = FakeStorage()
    event = make_event(event_id="event")

    events = add_events([], storage, [event], save=False)

    assert events == [event]
    assert storage.saved_events == []


def test_delete_event_removes_by_id_and_deletes_from_storage(make_event):
    storage = FakeStorage()
    event = make_event(event_id="event")

    events = delete_event([event], storage, event)

    assert events == []
    assert storage.deleted_events == [event]


def test_delete_events_removes_multiple_events(make_event):
    storage = FakeStorage()
    first_event = make_event(event_id="first")
    second_event = make_event(event_id="second")

    events = delete_events([first_event, second_event], storage, [first_event, second_event])

    assert events == []
    assert storage.deleted_events == [first_event, second_event]
