from decimal import Decimal
from typing import Annotated, Any, Optional

from pydantic import (
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)

from .event import IndexedEvent

ZERO = Decimal(0)


def zero_from_none(
    v: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Decimal:
    try:
        return handler(v)
    except ValidationError:
        return ZERO


ZeroFromNone = Annotated[Decimal, WrapValidator(zero_from_none)]


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
    #: the first (open) price of the candle
    open: ZeroFromNone
    #: the maximal (high) price of the candle
    high: ZeroFromNone
    #: the minimal (low) price of the candle
    low: ZeroFromNone
    #: the last (close) price of the candle
    close: ZeroFromNone
