from datetime import datetime, timedelta

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent

from domain.event_status import EVENT_STATUS_IMPORTANT, EVENT_STATUS_KAIROS
from tests.calendar_window_helpers import make_window, mouse_event


def test_window_shows_panel_message_when_title_is_missing(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.save_event_details()

    assert window.event_details_message.text() == "Event title is required."
    assert not window.statusBar().isVisible()


def test_window_clears_panel_message_when_selection_changes(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="details", start_at=start_at)

    window.show_status_message("Old message", 3000)
    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)

    assert window.event_details_message.text() == ""
    assert window.event_details_message.isHidden()


def test_window_shows_selected_event_details(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="details", title="Details Event", start_at=start_at, duration_minutes=90)
    event.note = "Details note"
    event.status = EVENT_STATUS_IMPORTANT

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)

    assert window.event_details_title.text() == "Details Event"
    assert window.event_details_time.text() == f"{start_at.strftime('%d.%m.%Y')}\n08:00 - 09:30"
    assert window.event_details_status.currentText() == "Important"
    assert window.event_details_note.toPlainText() == "Details note"


def test_window_double_click_event_shows_side_panel_details(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="double-details", title="Double Details", start_at=start_at)

    window.events = [event]
    window.refresh_calendar()
    event_rect = window.calendar_grid.rect_for_range(event.start_at, event.end_at)
    point = QPointF(event_rect.left() + 5, event_rect.top() + 5)
    window.calendar_grid.mouseDoubleClickEvent(mouse_event(QMouseEvent.MouseButtonDblClick, point))

    assert window.selected_event.id == "double-details"
    assert window.event_details_title.text() == "Double Details"


def test_window_saves_event_details_with_undo_and_redo(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="details-save", title="Old Title", start_at=start_at)
    event.note = "Old note"

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.event_details_title.setText("New Title")
    window.event_details_status.setCurrentIndex(window.event_details_status.findData(EVENT_STATUS_KAIROS))
    window.event_details_note.setPlainText("New note")
    window.save_event_details()

    assert event.title == "New Title"
    assert event.status == EVENT_STATUS_KAIROS
    assert event.note == "New note"

    window.undo_last_action()

    assert event.title == "Old Title"
    assert event.note == "Old note"

    window.redo_last_action()

    assert event.title == "New Title"
    assert event.status == EVENT_STATUS_KAIROS
    assert event.note == "New note"


def test_window_clears_event_details(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=8)
    event = make_event(event_id="details-clear", title="Clear Details", start_at=start_at)

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.calendar_grid.selected_slot_datetimes = {start_at + timedelta(minutes=30)}
    window.clear_all_selections()

    assert not window.event_details_panel.isHidden()
    assert not window.event_details_save_button.isEnabled()
    assert window.calendar_grid.selected_event_ids_list() == []
    assert window.calendar_grid.selected_slots() == []
    assert window.event_details_title.text() == ""
    assert window.event_details_time.text() == ""
    assert window.event_details_status.currentText() == "Normal"
    assert window.event_details_note.toPlainText() == ""


def test_window_creates_event_from_selected_slot_details(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=10)

    window.select_slot_for_details(start_at)

    assert not window.event_details_panel.isHidden()
    assert window.event_details_time.text() == f"{start_at.strftime('%d.%m.%Y')}\n10:00 - 10:30"
    assert window.event_details_save_button.text() == "Create"

    window.event_details_title.setText("Panel Event")
    window.event_details_status.setCurrentIndex(window.event_details_status.findData(EVENT_STATUS_KAIROS))
    window.event_details_note.setPlainText("Panel note")
    window.save_event_details()

    assert len(window.events) == 1
    assert window.events[0].title == "Panel Event"
    assert window.events[0].status == EVENT_STATUS_KAIROS
    assert window.events[0].note == "Panel note"
    assert window.events[0].start_at == start_at
    assert window.events[0].end_at == start_at + timedelta(minutes=30)

    window.undo_last_action()

    assert window.events == []


def test_window_creates_events_from_selected_slot_list_details(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_start = datetime.combine(window.week_start, datetime.min.time()).replace(hour=10)
    second_start = first_start + timedelta(days=1, minutes=30)

    window.select_slot_for_details([first_start, second_start])

    assert not window.event_details_panel.isHidden()
    assert window.event_details_save_button.text() == "Create"
    assert window.selected_details_ranges == [
        (first_start, first_start + timedelta(minutes=30)),
        (second_start, second_start + timedelta(minutes=30)),
    ]

    window.event_details_title.setText("Multi Slot Event")
    window.save_event_details()

    assert len(window.events) == 2
    assert [event.start_at for event in window.events] == [first_start, second_start]
    assert window.calendar_grid.selected_slots() == []
    assert window.calendar_grid.selected_event_ids_list() == [window.events[-1].id]


def test_window_deletes_selected_event_from_details_panel(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=11)
    event = make_event(event_id="panel-delete", start_at=start_at)

    window.events = [event]
    window.refresh_calendar()
    window.select_event(event)
    window.event_details_delete_button.click()

    assert window.events == []
    assert window.event_details_message.text() == ""

    window.undo_last_action()

    assert len(window.events) == 1


def test_window_disables_details_delete_button_for_creation(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert not window.event_details_delete_button.isEnabled()
