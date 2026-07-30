from datetime import datetime

from domain.clock import current_datetime


def test_current_datetime_returns_datetime():
    assert isinstance(current_datetime(), datetime)
