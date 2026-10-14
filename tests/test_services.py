from datetime import date
from app.services import calculate_days


def test_calculate_days():
    assert calculate_days(date(2026, 11, 1), date(2026, 11, 3)) == 3
