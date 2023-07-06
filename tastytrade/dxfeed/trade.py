from dataclasses import dataclass

from .event import Event


@dataclass
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
    #: price of the last trade
    price: float
    #: change of the last trade
    change: float
    #: size of the last trade as integer number (rounded toward zero)
    size: int
    #: identifier of the current trading day
    dayId: int
    #: total vlume traded for a day as integer number (rounded toward zero)
    dayVolume: int
    #: total turnover traded for a day
    dayTurnover: float
    #: tick direction of the last trade
    #: possible values are DOWN | UNDEFINED | UP | ZERO | ZERO_DOWN | ZERO_UP
    tickDirection: str
    #: whether the last trade was in extended trading hours
    extendedTradingHours: bool
