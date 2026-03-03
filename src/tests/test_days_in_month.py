import pytest
from src.utils.days_in_month import days_in_month


# ---------------------------------------------------------------------------
# Обычные месяцы
# ---------------------------------------------------------------------------

class TestDaysInMonthBasic:
    def test_january_has_31_days(self):
        assert days_in_month(1, 2026) == 31

    def test_march_has_31_days(self):
        assert days_in_month(3, 2026) == 31

    def test_april_has_30_days(self):
        assert days_in_month(4, 2026) == 30

    def test_june_has_30_days(self):
        assert days_in_month(6, 2026) == 30

    def test_december_has_31_days(self):
        assert days_in_month(12, 2026) == 31


# ---------------------------------------------------------------------------
# Февраль и високосные годы
# ---------------------------------------------------------------------------

class TestFebruary:
    def test_february_non_leap_year(self):
        assert days_in_month(2, 2026) == 28

    def test_february_leap_year(self):
        assert days_in_month(2, 2024) == 29

    def test_february_divisible_by_100_not_leap(self):
        # делится на 100, но не на 400 — не високосный
        assert days_in_month(2, 1900) == 28

    def test_february_divisible_by_400_is_leap(self):
        # делится на 400 — високосный
        assert days_in_month(2, 2000) == 29


# ---------------------------------------------------------------------------
# Граничные значения
# ---------------------------------------------------------------------------

class TestBoundaryValues:
    def test_first_month(self):
        assert days_in_month(1, 2026) == 31

    def test_last_month(self):
        assert days_in_month(12, 2026) == 31


# ---------------------------------------------------------------------------
# Валидация входных данных
# ---------------------------------------------------------------------------

class TestValidation:
    def test_month_zero_raises(self):
        with pytest.raises(ValueError):
            days_in_month(0, 2026)

    def test_month_13_raises(self):
        with pytest.raises(ValueError):
            days_in_month(13, 2026)

    def test_negative_month_raises(self):
        with pytest.raises(ValueError):
            days_in_month(-1, 2026)

    def test_year_zero_raises(self):
        with pytest.raises(ValueError):
            days_in_month(1, 0)

    def test_negative_year_raises(self):
        with pytest.raises(ValueError):
            days_in_month(1, -2026)
