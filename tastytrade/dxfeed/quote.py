from decimal import Decimal
from typing import Optional

from .event import Event


class Quote(Event):
    """
    A Quote event is a snapshot of the best bid and ask prices, and other
    fields that change with each quote.
    """

    #: sequence of this quote
    sequence: int
    #: microseconds and nanoseconds part of time of the last bid or ask change
    time_nano_part: int
    #: time of the last bid change
    bid_time: int
    #: bid exchange code
    bid_exchange_code: str
    #: time of the last ask change
    ask_time: int
    #: ask exchange code
    ask_exchange_code: str
    #: bid price
    bid_price: Decimal
    #: ask price
    ask_price: Decimal
    #: bid size as integer number (rounded toward zero)
    #: or decimal for cryptocurrencies
    bid_size: Optional[Decimal] = None
    #: ask size as integer number (rounded toward zero)
    #: or decimal for cryptocurrencies
    ask_size: Optional[Decimal] = None
