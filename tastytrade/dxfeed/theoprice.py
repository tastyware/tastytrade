from dataclasses import dataclass

from .event import Event


@dataclass
class TheoPrice(Event):
    """
    Theo price is a snapshot of the theoretical option price computation that
    is periodically performed by dxPrice model-free computation. dxFeed does
    not send recalculations for all options at the same time, so we provide
    you with a formula so you can perform calculations based on values from
    this event.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this event
    index: int
    #: timestamp of this event in milliseconds
    time: int
    #: sequence number to distinguish events that have the same time
    sequence: int
    #: theoretical price
    price: float
    #: underlying price at the time of theo price computation
    underlyingPrice: float
    #: delta of the theoretical price
    delta: float
    #: gamma of the theoretical price
    gamma: float
    #: implied simple dividend return of the corresponding option series
    dividend: float
    #: implied simple interest return of the corresponding option series
    interest: float
