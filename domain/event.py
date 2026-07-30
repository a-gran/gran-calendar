from dataclasses import dataclass
from datetime import datetime

from domain.event_status import EVENT_STATUS_NORMAL


@dataclass
class Event:
    id: str
    title: str
    note: str
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime
    status: str = EVENT_STATUS_NORMAL
