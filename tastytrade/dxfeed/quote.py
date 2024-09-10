from decimal import Decimal
from typing import Optional

from .event import Event


class Quote(Event):
    """
    A Quote event is a snapshot of the best bid and ask prices, and other
    fields that change with each quote.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: sequence of this quote
    sequence: int
    #: microseconds and nanoseconds part of time of the last bid or ask change
    timeNanoPart: int
    #: time of the last bid change
    bidTime: int
    #: bid exchange code
    bidExchangeCode: str
    #: time of the last ask change
    askTime: int
    #: ask exchange code
    askExchangeCode: str
    #: bid price
    bidPrice: Optional[Decimal] = None
    #: ask price
    askPrice: Optional[Decimal] = None
    #: bid size as integer number (rounded toward zero)
    #: or decimal for cryptocurrencies
    bidSize: Optional[Decimal] = None
    #: ask size as integer number (rounded toward zero)
    #: or decimal for cryptocurrencies
    askSize: Optional[Decimal] = None
