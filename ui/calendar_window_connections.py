def connect_calendar_window_signals(window):
    window.calendar_scroll_area.verticalScrollBar().rangeChanged.connect(
        lambda _minimum, _maximum: window.update_calendar_header_padding()
    )
    window.calendar_grid.selection_created.connect(window.add_event_from_selection)
    window.calendar_grid.selection_ranges_created.connect(window.add_events_from_ranges)
    window.calendar_grid.event_selected.connect(window.select_event)
    window.calendar_grid.event_double_clicked.connect(window.mark_event_done_from_grid)
    window.calendar_grid.event_resized.connect(window.resize_event_from_grid)
    window.calendar_grid.event_moved.connect(window.resize_event_from_grid)
    window.calendar_grid.slot_double_clicked.connect(window.add_event_to_slot)
    window.calendar_grid.slot_selected.connect(window.select_slot_for_details)
