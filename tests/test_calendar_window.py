import re
from datetime import datetime, timedelta

from PySide6.QtCore import QPoint

from tests.calendar_window_helpers import make_window


class WheelEvent:
    def __init__(self, pixel_y=0, angle_y=0):
        self.pixel_y = pixel_y
        self.angle_y = angle_y

    def pixelDelta(self):
        return QPoint(0, self.pixel_y)

    def angleDelta(self):
        return QPoint(0, self.angle_y)


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

    assert window.width() == 1600
    assert window.height() == 900


def test_window_uses_wide_details_panel(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert window.event_details_panel.width() == 400


def test_window_wheel_scrolls_active_calendar_area(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    scrollbar = window.calendar_scroll_area.verticalScrollBar()
    scrollbar.setRange(0, 1000)
    scrollbar.setValue(500)

    window.scroll_active_calendar_area(WheelEvent(angle_y=-120))

    assert scrollbar.value() == 620


def test_window_wheel_scrolls_year_overview_area(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    window.show_month_overview()
    scrollbar = window.year_overview_scroll_area.verticalScrollBar()
    scrollbar.setRange(0, 1000)
    scrollbar.setValue(500)

    window.scroll_active_calendar_area(WheelEvent(angle_y=-120))

    assert scrollbar.value() == 620


def test_window_keeps_month_event_list_wheel_scroll(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert window.should_keep_widget_wheel_scroll(window.month_day_events)
    assert window.should_keep_widget_wheel_scroll(window.month_day_events.viewport())
    assert not window.should_keep_widget_wheel_scroll(window.calendar_grid)


def test_window_has_small_settings_icon_button(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert window.settings_button.text() == "⚙"
    assert window.settings_button.width() == 32
    assert window.settings_button.height() == 32
    assert window.settings_button.toolTip() == "Settings"


def test_window_header_has_live_24_hour_clock(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", window.current_time_label.text())
    assert "font-size: 32px" in window.current_time_label.styleSheet()
    assert window.current_time_timer.isActive()
    assert window.current_time_timer.interval() == 1000


def test_window_applies_visual_settings(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)

    window.visual_settings = {
        "theme": "light",
        "slot_height": 48,
        "details_panel_width": 460,
        "time_font_size": 28,
        "event_title_font_size": 18,
        "time_axis_font_size": 14,
        "selected_border_width": 5,
        "note_marker_size": 24,
        "show_note_markers": False,
    }
    window.apply_visual_settings()

    assert window.calendar_grid.slot_height == 48
    assert window.calendar_grid.event_time_pixel_size == 28
    assert window.calendar_grid.event_title_pixel_size == 18
    assert window.calendar_grid.time_axis_pixel_size == 14
    assert window.calendar_grid.selected_border_width == 5
    assert window.calendar_grid.note_marker_size == 24
    assert not window.calendar_grid.show_note_markers
    assert window.calendar_grid.theme_colors["normal_event_background"] == "#ffffff"
    assert window.calendar_header.theme_colors["normal_event_background"] == "#ffffff"
    assert window.year_month_calendars[0].theme_colors["normal_event_background"] == "#ffffff"
    assert window.event_details_panel.width() == 460


def test_window_selects_first_slot_by_default(qt_app, tmp_path, monkeypatch):
    window = make_window(qt_app, tmp_path, monkeypatch)
    start_at = datetime.combine(window.week_start, datetime.min.time()).replace(hour=6)

    assert window.calendar_grid.selected_slots() == [start_at]
    assert window.selected_details_ranges == [(start_at, start_at + timedelta(minutes=30))]
    assert window.event_details_time.text() == f"{start_at.strftime('%d.%m.%Y')}\n06:00 - 06:30"
    assert window.event_details_save_button.text() == "Create"
