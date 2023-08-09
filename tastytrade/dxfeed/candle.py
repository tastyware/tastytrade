from dataclasses import dataclass

from .event import Event


@dataclass
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
    open: float
    #: the maximal (high) price of the candle
    high: float
    #: the minimal (low) price of the candle
    low: float
    #: the last (close) price of the candle
    close: float
    #: the total volume of the candle
    volume: int
    #: volume-weighted average price
    vwap: float
    #: bid volume in the candle
    bidVolume: int
    #: ask volume in the candle
    askVolume: int
    #: implied volatility in the candle
    impVolatility: float
    #: open interest in the candle
    openInterest: int
