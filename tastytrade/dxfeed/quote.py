from decimal import Decimal

from .. import logger
from .event import Event

_ZERO = Decimal(0)


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
    bid_size: Decimal = _ZERO
    #: ask size as integer number (rounded toward zero)
    #: or decimal for cryptocurrencies
    ask_size: Decimal = _ZERO

    @property
    def mid_price(self) -> Decimal:
        """
        Halfway point between bid and ask prices
        """
        return (self.bid_price + self.ask_price) / 2

    @property
    def micro_price(self) -> Decimal:
        """
        Average of bid and ask price weighted by their volumes
        """
        total_size = self.bid_size + self.ask_size
        if not total_size:  # check for zero, fallback to mid
            logger.warning("Can't compute micro price without sizing!")
            return self.mid_price
        return (
            self.bid_size / total_size * self.ask_price
            + self.ask_size / total_size * self.bid_price
        )
