from decimal import Decimal
from typing import Annotated, Any, cast

from pydantic import (
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)

from .event import IndexedEvent


def zero_from_none(
    v: Any, handler: ValidatorFunctionWrapHandler, _: ValidationInfo
) -> Decimal:
    try:
        return cast(Decimal, handler(v))
    except ValidationError:
        return Decimal(0)


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
    volume: Decimal | None = None
    #: volume-weighted average price
    vwap: Decimal | None = None
    #: bid volume in the candle
    bid_volume: Decimal | None = None
    #: ask volume in the candle
    ask_volume: Decimal | None = None
    #: implied volatility in the candle
    imp_volatility: Decimal | None = None
    #: open interest in the candle
    open_interest: int | None = None
    #: the first (open) price of the candle
    open: ZeroFromNone
    #: the maximal (high) price of the candle
    high: ZeroFromNone
    #: the minimal (low) price of the candle
    low: ZeroFromNone
    #: the last (close) price of the candle
    close: ZeroFromNone
