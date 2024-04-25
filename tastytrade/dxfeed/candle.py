from decimal import Decimal
from typing import Optional

from .event import Event


class Candle(Event):
    """
    A Candle event with open, high, low, close prices and other information
    for a specific period. Candles are build with a specified period using a
    specified price type with data taken from a specified exchange.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this candle event
    index: int
    #: timestamp of the candle in milliseconds
    time: int
    #: sequence number of this event
    sequence: int
    #: total number of events in the candle
    count: int
    #: the first (open) price of the candle
    open: Optional[Decimal] = None
    #: the maximal (high) price of the candle
    high: Optional[Decimal] = None
    #: the minimal (low) price of the candle
    low: Optional[Decimal] = None
    #: the last (close) price of the candle
    close: Optional[Decimal] = None
    #: the total volume of the candle
    volume: Optional[Decimal] = None
    #: volume-weighted average price
    vwap: Optional[Decimal] = None
    #: bid volume in the candle
    bidVolume: Optional[Decimal] = None
    #: ask volume in the candle
    askVolume: Optional[Decimal] = None
    #: implied volatility in the candle
    impVolatility: Optional[Decimal] = None
    #: open interest in the candle
    openInterest: Optional[int] = None
