from datetime import datetime, timedelta

from PySide6.QtCore import QDate

from tests.calendar_window_helpers import make_window, overview_event_text


def test_window_overview_event_double_click_opens_week_event(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start + timedelta(days=2)
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=11)
    event = make_event(event_id="overview-open-week", title="Open Week", start_at=event_start, duration_minutes=60)
    window.storage.load_events_between = lambda start_at, end_at: [event] if start_at <= event.start_at < end_at else []

    window.show_month_overview()
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    row = window.month_day_events.itemWidget(window.month_day_events.item(0))
    row.double_clicked.emit(event.id)

    assert window.week_start == selected_date - timedelta(days=selected_date.weekday())
    assert window.calendar_view_stack.currentWidget() == window.week_view
    assert window.details_view_stack.currentWidget() == window.event_details_form
    assert window.selected_event.id == event.id


def test_window_overview_edits_event_title_inline(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=12)
    event = make_event(event_id="overview-edit-title", title="Old Title", start_at=event_start, duration_minutes=60)
    saved_events = []

    window.storage.load_events_between = lambda start_at, end_at: [event] if start_at <= event.start_at < end_at else []
    window.storage.save_event = lambda saved_event: saved_events.append(saved_event)

    window.show_month_overview()
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    row = window.month_day_events.itemWidget(window.month_day_events.item(0))
    row.edit_button.click()
    row.title_edit.setText("New Title")
    row.edit_button.click()

    assert event.title == "New Title"
    assert saved_events == [event]
    assert overview_event_text(window, 0) == "12:00 - 13:00  New Title"


def test_window_overview_deletes_and_restores_event_from_day_list(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=10)
    event = make_event(event_id="overview-delete", title="Delete Me", start_at=event_start, duration_minutes=30)
    stored_events = [event]

    def load_events_between(start_at, end_at):
        return [stored_event for stored_event in stored_events if start_at <= stored_event.start_at < end_at]

    window.storage.load_events_between = load_events_between
    window.storage.delete_event = lambda deleted_event: stored_events.remove(deleted_event)
    window.storage.save_event = lambda saved_event: stored_events.append(saved_event)

    window.show_month_overview()
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    row = window.month_day_events.itemWidget(window.month_day_events.item(0))
    row.action_button.click()

    assert stored_events == []
    assert overview_event_text(window, 0) == "10:00 - 10:30  Delete Me"
    assert row.action_button.text() == "↶"
    assert window.details_view_stack.currentWidget() == window.month_day_details

    row.action_button.click()

    assert stored_events == [event]
    assert overview_event_text(window, 0) == "10:00 - 10:30  Delete Me"
    assert window.details_view_stack.currentWidget() == window.month_day_details


def test_window_overview_hides_deleted_event_after_day_change(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start
    event_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=10)
    event = make_event(event_id="overview-delete-switch", title="Delete Me", start_at=event_start, duration_minutes=30)
    stored_events = [event]

    def load_events_between(start_at, end_at):
        return [stored_event for stored_event in stored_events if start_at <= stored_event.start_at < end_at]

    window.storage.load_events_between = load_events_between
    window.storage.delete_event = lambda deleted_event: stored_events.remove(deleted_event)
    window.storage.save_event = lambda saved_event: stored_events.append(saved_event)

    window.show_month_overview()
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    row = window.month_day_events.itemWidget(window.month_day_events.item(0))
    row.action_button.click()

    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day + 1))

    assert window.month_day_events.item(0).text() == "No events"

    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))

    assert window.month_day_events.item(0).text() == "No events"


def test_window_overview_restores_one_deleted_event_without_hiding_other_deleted_rows(
    qt_app,
    tmp_path,
    monkeypatch,
    make_event,
):
    window = make_window(qt_app, tmp_path, monkeypatch)
    selected_date = window.week_start
    first_start = datetime.combine(selected_date, datetime.min.time()).replace(hour=10)
    second_start = first_start + timedelta(hours=1)
    first_event = make_event(event_id="overview-delete-first", title="First", start_at=first_start, duration_minutes=30)
    second_event = make_event(
        event_id="overview-delete-second",
        title="Second",
        start_at=second_start,
        duration_minutes=30,
    )
    stored_events = [first_event, second_event]

    def load_events_between(start_at, end_at):
        return [stored_event for stored_event in stored_events if start_at <= stored_event.start_at < end_at]

    window.storage.load_events_between = load_events_between
    window.storage.delete_event = lambda deleted_event: stored_events.remove(deleted_event)
    window.storage.save_event = lambda saved_event: stored_events.append(saved_event)

    window.show_month_overview()
    window.select_day_in_month_overview(QDate(selected_date.year, selected_date.month, selected_date.day))
    first_row = window.month_day_events.itemWidget(window.month_day_events.item(0))
    second_row = window.month_day_events.itemWidget(window.month_day_events.item(1))

    first_row.action_button.click()
    second_row.action_button.click()
    first_row.action_button.click()

    assert stored_events == [first_event]
    assert first_row.action_button.text() == "×"
    assert second_row.action_button.text() == "↶"
    assert overview_event_text(window, 1) == "11:00 - 11:30  Second"
