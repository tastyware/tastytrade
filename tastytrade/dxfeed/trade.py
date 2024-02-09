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
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: time of the last trade
    time: int
    #: microseconds and nanoseconds time part of the last trade
    timeNanoPart: int
    #: sequence of the last trade
    sequence: int
    #: exchange code of the last trade
    exchangeCode: str
    #: identifier of the current trading day
    dayId: int
    #: tick direction of the last trade
    #: possible values are DOWN | UNDEFINED | UP | ZERO | ZERO_DOWN | ZERO_UP
    tickDirection: str
    #: whether the last trade was in extended trading hours
    extendedTradingHours: bool
    #: price of the last trade
    price: Optional[Decimal] = None
    #: change of the last trade
    change: Optional[Decimal] = None
    #: size of the last trade as integer number (rounded toward zero)
    size: Optional[int] = None
    #: total vlume traded for a day as integer number (rounded toward zero)
    dayVolume: Optional[int] = None
    #: total turnover traded for a day
    dayTurnover: Optional[Decimal] = None
