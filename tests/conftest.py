import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def make_event():
    from domain.event import Event

    def _make_event(event_id="event-1", title="Event", start_at=None, duration_minutes=30):
        if start_at is None:
            start_at = datetime(2026, 7, 27, 9, 0)
        end_at = start_at + timedelta(minutes=duration_minutes)
        return Event(
            id=event_id,
            title=title,
            note="Note",
            start_at=start_at,
            end_at=end_at,
            created_at=start_at,
            updated_at=start_at,
        )

    return _make_event
