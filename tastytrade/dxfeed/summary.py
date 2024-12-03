from decimal import Decimal
from typing import Optional

from .event import Event


class Summary(Event):
    """
    Summary is an information snapshot about the trading session including
    session highs, lows, etc. This record has two goals: Transmit OHLC
    values, and provide data for charting. OHLC is required for a daily chart,
    and if an exchange does not provide it, the charting services refer to the
    Summary event.

    Before opening the bidding, the values are reset to N/A or NaN.
    """

    #: identifier of the day that this summary represents
    day_id: int
    #: the price type of the last (close) price for the day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    day_close_price_type: str
    #: identifier of the previous day that this summary represents
    prev_day_id: int
    #: the price type of the last (close) price for the previous day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    prev_day_close_price_type: str
    #: open interest of the symbol as the number of open contracts
    open_interest: int
    #: the first (open) price for the day
    day_open_price: Optional[Decimal] = None
    #: the maximal (high) price for the day
    day_high_price: Optional[Decimal] = None
    #: the minimal (low) price for the day
    day_low_price: Optional[Decimal] = None
    #: the last (close) price for the day
    day_close_price: Optional[Decimal] = None
    #: the last (close) price for the previous day
    prev_day_close_price: Optional[Decimal] = None
    #: total volume traded for the previous day
    prev_day_volume: Optional[Decimal] = None
