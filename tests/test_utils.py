from datetime import date

from tastytrade.utils import (get_future_fx_monthly, get_future_grain_monthly,
                              get_future_index_monthly,
                              get_future_metal_monthly, get_future_oil_monthly,
                              get_future_treasury_monthly, get_tasty_monthly,
                              get_third_friday, today_in_new_york)


def test_get_third_friday():
    assert get_third_friday(date(2024, 3, 2)) == date(2024, 3, 15)


def test_get_tasty_monthly():
    delta = (get_tasty_monthly() - today_in_new_york()).days
    assert abs(45 - delta) <= 17


def test_get_future_fx_monthly():
    exps = [
        date(2024, 2, 9),
        date(2024, 3, 8),
        date(2024, 4, 5),
        date(2024, 5, 3),
        date(2024, 6, 7),
        date(2024, 7, 5),
        date(2024, 8, 9),
        date(2024, 9, 6),
        date(2024, 10, 4),
        date(2024, 11, 8),
        date(2024, 12, 6),
        date(2025, 1, 3),
        date(2025, 2, 7),
        date(2025, 3, 7),
        date(2025, 6, 6),
        date(2025, 9, 5),
        date(2025, 12, 5)
    ]
    for exp in exps:
        assert get_future_fx_monthly(exp) == exp


def test_get_future_treasury_monthly():
    exps = [
        date(2024, 2, 23),
        date(2024, 3, 22),
        date(2024, 4, 26),
        date(2024, 5, 24),
        date(2024, 6, 21),
        date(2024, 8, 23)
    ]
    for exp in exps:
        assert get_future_treasury_monthly(exp) == exp


def test_get_future_grain_monthly():
    exps = [
        date(2024, 2, 23),
        date(2024, 3, 22),
        date(2024, 4, 26),
        date(2024, 5, 24),
        date(2024, 6, 21),
        date(2024, 8, 23),
        date(2024, 11, 22),
        date(2025, 2, 21),
        date(2025, 4, 25),
        date(2025, 6, 20),
        date(2025, 11, 21),
        date(2026, 6, 26),
        date(2026, 11, 20)
    ]
    for exp in exps:
        assert get_future_grain_monthly(exp) == exp


def test_get_future_metal_monthly():
    exps = [
        date(2024, 2, 26),
        date(2024, 3, 25),
        date(2024, 4, 25),
        date(2024, 5, 28),
        date(2024, 6, 25),
        date(2024, 7, 25),
        date(2024, 8, 27),
        date(2024, 9, 25),
        date(2024, 10, 28),
        date(2024, 11, 25),
        date(2024, 12, 26),
        date(2025, 1, 28),
        date(2025, 2, 25),
        date(2025, 3, 26),
        date(2025, 4, 24),
        date(2025, 5, 27),
        date(2025, 6, 25),
        date(2025, 7, 28),
        date(2025, 8, 26),
        date(2025, 9, 25),
        date(2025, 11, 24),
        date(2026, 5, 26),
        date(2026, 11, 24),
        date(2027, 5, 25),
        date(2027, 11, 23),
        date(2028, 5, 25),
        date(2028, 11, 27),
        date(2029, 5, 24),
        date(2029, 11, 27)
    ]
    for exp in exps:
        assert get_future_metal_monthly(exp) == exp


def test_get_future_oil_monthly():
    exps = [
        date(2024, 2, 14),
        date(2024, 3, 15),
        date(2024, 4, 17),
        date(2024, 5, 16),
        date(2024, 6, 14),
        date(2024, 7, 17),
        date(2024, 8, 15),
        date(2024, 9, 17),
        date(2024, 10, 17),
        date(2024, 11, 15),
        date(2024, 12, 16),
        date(2025, 10, 16),
        date(2026, 4, 16),
        date(2027, 7, 15),
        date(2028, 1, 14),
        date(2029, 5, 17),
        date(2030, 11, 15),
        date(2031, 8, 15),
        date(2032, 2, 17),
        date(2033, 4, 14),
        date(2034, 1, 17)
    ]
    for exp in exps:
        assert get_future_oil_monthly(exp) == exp


def test_get_future_index_monthly():
    exps = [
        date(2024, 2, 29),
        date(2024, 3, 28),
        date(2024, 4, 30),
        date(2024, 5, 31),
        date(2024, 6, 28),
        date(2024, 7, 31),
        date(2024, 9, 30),
        date(2024, 12, 31),
        date(2025, 3, 31),
        date(2025, 6, 30)
    ]
    for exp in exps:
        assert get_future_index_monthly(exp) == exp
