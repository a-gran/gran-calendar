from datetime import datetime, time, timedelta


class CalendarGridSelectionMixin:
    def clear_selection(self):
        self.selected_event_ids.clear()
        self.selected_slot_datetimes.clear()
        self.update()

    def selected_slots(self):
        return sorted(self.selected_slot_datetimes)

    def selected_event_ids_list(self):
        return sorted(self.selected_event_ids)

    def toggle_event_selection(self, event_id):
        if event_id in self.selected_event_ids:
            self.selected_event_ids.remove(event_id)
            self.update()
            return False
        self.selected_event_ids.add(event_id)
        self.update()
        return True

    def replace_event_selection(self, event_id):
        self.selected_event_ids = {event_id}
        self.selected_slot_datetimes.clear()
        self.update()
        return True

    def toggle_slot_selection(self, slot_datetime):
        if slot_datetime in self.selected_slot_datetimes:
            self.selected_slot_datetimes.remove(slot_datetime)
        else:
            self.selected_slot_datetimes.add(slot_datetime)
        self.update()

    def replace_slot_selection(self, slot_datetime):
        self.selected_slot_datetimes = {slot_datetime}
        self.selected_event_ids.clear()
        self.update()

    def slot_datetimes_for_ranges(self, ranges):
        slot_datetimes = []
        for start_at, end_at in ranges:
            current_slot = start_at
            while current_slot < end_at:
                slot_datetimes.append(current_slot)
                current_slot += timedelta(minutes=self.slot_minutes)
        return slot_datetimes

    def selection_ranges(self):
        if self.selection_anchor is None or self.selection_current is None:
            return []
        first_day = min(self.selection_anchor.date(), self.selection_current.date())
        last_day = max(self.selection_anchor.date(), self.selection_current.date())
        first_slot = min(
            self.slot_index_for_datetime(self.selection_anchor),
            self.slot_index_for_datetime(self.selection_current),
        )
        last_slot = max(
            self.slot_index_for_datetime(self.selection_anchor),
            self.slot_index_for_datetime(self.selection_current),
        )
        start_minutes = first_slot * self.slot_minutes
        end_minutes = (last_slot + 1) * self.slot_minutes
        ranges = []
        current_day = first_day
        while current_day <= last_day:
            start_at = datetime.combine(
                current_day,
                time(
                    hour=self.day_start_hour + start_minutes // 60,
                    minute=start_minutes % 60,
                ),
            )
            end_at = datetime.combine(
                current_day,
                time(
                    hour=self.day_start_hour + end_minutes // 60,
                    minute=end_minutes % 60,
                ),
            )
            ranges.append((start_at, end_at))
            current_day += timedelta(days=1)
        return ranges
