from decimal import Decimal
from typing import Optional

from .event import Event


class Trade(Event):
    """
    A Trade event provides prices and the volume of the last transaction in
    regular trading hours, as well as the total amount per day in the number
    of securities and in their value. This event does not contain information
    about all transactions, but only about the last transaction for a single
    instrument.
    """

    #: time of the last trade
    time: int
    #: microseconds and nanoseconds time part of the last trade
    time_nano_part: int
    #: sequence of the last trade
    sequence: int
    #: exchange code of the last trade
    exchange_code: str
    #: identifier of the current trading day
    day_id: int
    #: tick direction of the last trade
    #: possible values are DOWN | UNDEFINED | UP | ZERO | ZERO_DOWN | ZERO_UP
    tick_direction: str
    #: whether the last trade was in extended trading hours
    extended_trading_hours: bool
    #: price of the last trade
    price: Decimal
    #: change of the last trade
    change: Optional[Decimal] = None
    #: size of the last trade as integer number (rounded toward zero)
    size: Optional[int] = None
    #: total vlume traded for a day as integer number (rounded toward zero)
    day_volume: Optional[int] = None
    #: total turnover traded for a day
    day_turnover: Optional[Decimal] = None
