from dataclasses import dataclass

from .event import Event


@dataclass
class Summary(Event):
    """
    Summary is an information snapshot about the trading session including
    session highs, lows, etc. This record has two goals:

    1. Transmit OHLC values.
    2. Provide data for charting. OHLC is required for a daily chart, and
    if an exchange does not provide it, the charting services refer to the
    Summary event.

    Before opening the bidding, the values are reset to N/A or NaN.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: identifier of the day that this summary represents
    dayId: int
    #: the first (open) price for the day
    dayOpenPrice: float
    #: the maximal (high) price for the day
    dayHighPrice: float
    #: the minimal (low) price for the day
    dayLowPrice: float
    #: the last (close) price for the day
    dayClosePrice: float
    #: the price type of the last (close) price for the day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    dayClosePriceType: str
    #: identifier of the previous day that this summary represents
    prevDayId: int
    #: the last (close) price for the previous day
    prevDayClosePrice: float
    #: the price type of the last (close) price for the previous day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    prevDayClosePriceType: str
    #: total volume traded for the previous day
    prevDayVolume: float
    #: open interest of the symbol as the number of open contracts
    openInterest: int
