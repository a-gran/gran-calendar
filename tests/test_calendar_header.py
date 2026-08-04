from datetime import date, timedelta

from ui.calendar_header import CalendarHeaderWidget


def test_header_has_english_day_names(qt_app):
    header = CalendarHeaderWidget()

    assert header.day_names == ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def test_header_updates_week_start(qt_app):
    header = CalendarHeaderWidget()
    week_start = date(2026, 7, 27)

    header.set_week_start(week_start)

    assert header.week_start == week_start


def test_header_reserves_right_padding_for_scrollbar(qt_app):
    header = CalendarHeaderWidget()
    header.resize(772, 36)

    header.set_right_padding(20)

    assert header.day_column_rect(6).right() == 751


def test_header_highlights_current_day(qt_app):
    header = CalendarHeaderWidget()

    assert header.day_text_color(date.today()).name() == "#facc15"
    assert header.day_text_color(date.today() + timedelta(days=8)).name() == header.theme_colors["text"]
