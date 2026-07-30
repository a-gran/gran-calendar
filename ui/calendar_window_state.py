from datetime import date, timedelta

from domain.history_manager import HistoryManager
from storage.event_storage import EventStorage


def initialize_calendar_window_state(window, database_path):
    window.week_start = date.today() - timedelta(days=date.today().weekday())
    window.events = []
    window.events_by_id = {}
    window.events_by_date = {}
    window.copied_event = None
    window.selected_event = None
    window.selected_details_ranges = []
    window.undo_limit = 10
    window.history_manager = HistoryManager(window.undo_limit)
    window.storage = EventStorage(database_path)
    window.month_overview_date = window.week_start
    window.year_month_buttons = []
    window.year_overview_month = window.week_start.month
    window.year_overview_year = window.week_start.year
    window.overview_details_scope = "day"
    window.deleted_overview_events = {}
    window.is_updating_event_details = False
