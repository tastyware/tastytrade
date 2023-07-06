from dataclasses import dataclass

from .event import Event


@dataclass
class TimeAndSale(Event):
    """
    TimeAndSale event represents a trade or other market event with a price,
    like market open/close price. TimeAndSale events are intended to provide
    information about trades in a continuous-time slice (unlike Trade events
    which are supposed to provide snapshots about the most recent trade).
    TimeAndSale events have a unique index that can be used for later
    correction/cancellation processing.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this time and sale event
    index: int
    #: timestamp of the original event
    time: int
    #: microseconds and nanoseconds part of time of the last bid or ask change
    timeNanoPart: int
    #: sequence of this quote
    sequence: int
    #: exchange code of this time and sale event
    exchangeCode: str
    #: price of this time and sale event
    price: float
    #: size of this time and sale event as integer number (rounded toward zero)
    size: int
    #: the bid price on the market when this time and sale event occured
    bidPrice: float
    #: the ask price on the market when this time and sale event occured
    askPrice: float
    #: sale conditions provided for this event by data feed
    exchangeSaleConditions: str
    #: transaction is concluded by exempting from compliance with some rule
    tradeThroughExempt: str
    #: initiator of the trade
    aggressorSide: str
    #: whether this transaction is a part of a multi-leg order
    spreadLeg: bool
    #: whether this transaction is completed during extended trading hours
    extendedTradingHours: bool
    #: normalized SaleCondition flag
    validTick: bool
    #: type of event - 0: new, 1: correction, 2: cancellation
    type: str
    #: Undocumented; always None
    buyer: None
    #: Undocumented; always None
    seller: None
