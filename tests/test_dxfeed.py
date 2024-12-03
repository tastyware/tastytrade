from typing import cast

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
    summary = cast(Summary, summary)
    assert summary.day_open_price is None
    assert summary.day_close_price is None
    assert summary.day_high_price is None


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
