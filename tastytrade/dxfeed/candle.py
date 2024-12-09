from decimal import Decimal
from typing import Optional

from pydantic import Field, computed_field

from .event import IndexedEvent

ZERO = Decimal(0)


class Candle(IndexedEvent):
    """
    A Candle event with open, high, low, close prices and other information
    for a specific period. Candles are build with a specified period using a
    specified price type with data taken from a specified exchange.
    """

    #: unique per-symbol index of this candle event
    index: int
    #: timestamp of the candle in milliseconds
    time: int
    #: sequence number of this event
    sequence: int
    #: total number of events in the candle
    count: int
    #: the total volume of the candle
    volume: Optional[Decimal] = None
    #: volume-weighted average price
    vwap: Optional[Decimal] = None
    #: bid volume in the candle
    bid_volume: Optional[Decimal] = None
    #: ask volume in the candle
    ask_volume: Optional[Decimal] = None
    #: implied volatility in the candle
    imp_volatility: Optional[Decimal] = None
    #: open interest in the candle
    open_interest: Optional[int] = None
    # these fields will not show up in serialization
    raw_open: Optional[Decimal] = Field(validation_alias="open", exclude=True)
    raw_high: Optional[Decimal] = Field(validation_alias="high", exclude=True)
    raw_low: Optional[Decimal] = Field(validation_alias="low", exclude=True)
    raw_close: Optional[Decimal] = Field(validation_alias="close", exclude=True)

    @computed_field
    @property
    def open(self) -> Decimal:
        """
        the first (open) price of the candle
        """
        return self.raw_open or ZERO

    @computed_field
    @property
    def high(self) -> Decimal:
        """
        the maximal (high) price of the candle
        """
        return self.raw_high or ZERO

    @computed_field
    @property
    def low(self) -> Decimal:
        """
        the minimal (low) price of the candle
        """
        return self.raw_low or ZERO

    @computed_field
    @property
    def close(self) -> Decimal:
        """
        the last (close) price of the candle
        """
        return self.raw_close or ZERO
