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
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: identifier of the day that this summary represents
    dayId: int
    #: the price type of the last (close) price for the day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    dayClosePriceType: str
    #: identifier of the previous day that this summary represents
    prevDayId: int
    #: the price type of the last (close) price for the previous day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    prevDayClosePriceType: str
    #: open interest of the symbol as the number of open contracts
    openInterest: int
    #: the first (open) price for the day
    dayOpenPrice: Optional[Decimal] = None
    #: the maximal (high) price for the day
    dayHighPrice: Optional[Decimal] = None
    #: the minimal (low) price for the day
    dayLowPrice: Optional[Decimal] = None
    #: the last (close) price for the day
    dayClosePrice: Optional[Decimal] = None
    #: the last (close) price for the previous day
    prevDayClosePrice: Optional[Decimal] = None
    #: total volume traded for the previous day
    prevDayVolume: Optional[Decimal] = None
