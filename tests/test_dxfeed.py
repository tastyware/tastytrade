import pytest

from tastytrade.dxfeed import Quote, Summary
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


quote_data = ["SPY", 0, 0, 0, 0, "Q", 0, "Q", 576.88, 576.9, 230.0, 300.0]


def test_wrong_number_data_fields():
    with pytest.raises(TastytradeError):
        _ = Quote.from_stream(quote_data + ["extra"])


def test_bad_extra_data():
    extra_data = ["SPY", 0, "bad", 0, 0, "Q", 0, "Q", 576.88, 576.9, 230.0, 300.0]
    _ = Quote.from_stream(quote_data + extra_data)


def test_index_quote_nan_sizes():
    """Index symbols (SPX, VIX) return NaN for bid/ask sizes since they have no order book."""
    index_data = ["SPX", 0, 0, 0, 0, "\x00", 0, "\x00", 4122.49, 4123.65, "NaN", "NaN"]
    quotes = Quote.from_stream(index_data)
    assert len(quotes) == 1
    quote = quotes[0]
    assert quote.event_symbol == "SPX"
    assert quote.bid_price is not None
    assert quote.ask_price is not None
    assert quote.bid_size is None
    assert quote.ask_size is None
