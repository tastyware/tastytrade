from dataclasses import dataclass

from .event import Event


@dataclass
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
    #: bid price
    bidPrice: float
    #: bid size as integer number (rounded toward zero)
    bidSize: int
    #: time of the last ask change
    askTime: int
    #: ask exchange code
    askExchangeCode: str
    #: ask price
    askPrice: float
    #: ask size as integer number (rounded toward zero)
    askSize: int
