from decimal import Decimal

import pytest

from tastytrade.dxfeed import Quote, Summary
from tastytrade.dxfeed.quote import _ZERO
from tastytrade.utils import TastytradeError


def test_parse_infinities_and_nan():
    summary_data = [
        "SPY",
        0,
        0,
        "foo",
        0,
        "bar",
        0,
        "-Infinity",
        "Infinity",
        "NaN",
        "NaN",
        "NaN",
        "Infinity",
    ]
    summary = Summary.from_stream(summary_data)[0]
    assert summary.day_open_price is None
    assert summary.day_close_price is None
    assert summary.day_high_price is None


quote_data = ["SPY", 0, 0, 0, 0, "Q", 0, "Q", 576.88, 576.9, 200.0, 300.0]


def test_wrong_number_data_fields():
    with pytest.raises(TastytradeError):
        _ = Quote.from_stream(quote_data + ["extra"])


def test_bad_extra_data():
    extra_data = ["SPY", 0, "bad", 0, 0, "Q", 0, "Q", 576.88, 576.9, 230.0, 300.0]
    _ = Quote.from_stream(quote_data + extra_data)


def test_missing_size_data():
    missing_size_data = ["SPY", 0, 0, 0, 0, "Q", 0, "Q", 576.88, 576.9, "NaN", "NaN"]
    quotes = Quote.from_stream(quote_data + missing_size_data)
    assert quotes[0].bid_size == quote_data[-2]
    assert quotes[0].ask_size == quote_data[-1]
    assert quotes[1].bid_size == _ZERO
    assert quotes[1].ask_size == _ZERO
    assert quotes[1].micro_price == quotes[1].mid_price


def test_quote_utilities():
    quote = Quote.from_stream(quote_data)[0]
    assert quote.mid_price == Decimal("576.89")
    assert quote.micro_price == Decimal("576.888")
