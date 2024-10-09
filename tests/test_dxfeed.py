from typing import cast

import pytest

from tastytrade.dxfeed import Quote
from tastytrade.utils import TastytradeError


def test_parse_infinities_and_nan():
    quote_data = ["SPY", 0, 0, 0, 0, "Q", 0, "Q", "-Infinity", "Infinity", "NaN", "NaN"]
    quote = Quote.from_stream(quote_data)[0]
    quote = cast(Quote, quote)
    assert quote.bidPrice is None
    assert quote.askPrice is None
    assert quote.bidSize is None


def test_malformatted_data():
    with pytest.raises(TastytradeError):
        quote_data = [
            "SPY",
            0,
            0,
            0,
            0,
            "Q",
            0,
            "Q",
            576.88,
            576.9,
            230.0,
            300.0,
            "extra",
        ]
        _ = Quote.from_stream(quote_data)
