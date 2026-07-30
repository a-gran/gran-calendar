from datetime import datetime, timedelta

from tests.calendar_window_helpers import make_window


def test_window_detects_event_overlap(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=9)
    event = make_event(start_at=start_at, duration_minutes=60)

    window.events = [event]
    window.refresh_calendar()

    assert window.has_event_overlap(start_at + timedelta(minutes=30), start_at + timedelta(minutes=90))
    assert not window.has_event_overlap(start_at + timedelta(hours=1), start_at + timedelta(hours=2))


def test_window_rebuilds_event_index_on_refresh(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    event = make_event(event_id="indexed")
    window.events = [event]
    window.refresh_calendar()

    assert window.find_event_by_id(window.events, "indexed") is event


def test_window_gets_selected_events_from_event_index(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    first_event = make_event(event_id="selected-first")
    second_event = make_event(event_id="selected-second")
    window.events = [first_event, second_event]
    window.refresh_calendar()
    window.calendar_grid.selected_event_ids = {"selected-first", "selected-second"}

    assert window.events_for_selected_event_ids() == [first_event, second_event]


def test_window_rebuilds_event_date_index_on_refresh(qt_app, tmp_path, monkeypatch, make_event):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=21, minute=30)
    event = make_event(event_id="overnight", start_at=start_at, duration_minutes=180)
    window.events = [event]
    window.refresh_calendar()

    assert window.events_for_range(start_at, start_at + timedelta(minutes=30)) == [event]
    assert window.events_for_range(event.end_at - timedelta(minutes=30), event.end_at) == [event]


def test_window_syncs_calendar_header_week(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    initial_week = window.week_start

    window.show_next_week()

    assert window.calendar_header.week_start == initial_week + timedelta(days=7)


def test_window_uses_large_start_size(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert window.width() == 1400
    assert window.height() == 900


def test_window_uses_wide_details_panel(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert window.event_details_panel.width() == 400


def test_window_selects_first_slot_by_default(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=6)

    assert window.calendar_grid.selected_slots() == [start_at]
    assert window.selected_details_ranges == [(start_at, start_at + timedelta(minutes=30))]
    assert window.event_details_time.text() == f"{start_at.strftime('%d.%m.%Y')}\n06:00 - 06:30"
    assert window.event_details_save_button.text() == "Create"
