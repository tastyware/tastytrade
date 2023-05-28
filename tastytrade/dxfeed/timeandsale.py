from dataclasses import dataclass

from .event import Event


@dataclass
class TimeAndSale(Event):
    """
    A Quote event is a snapshot of the best bid and ask prices, and other fields that change with each quote.
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
    #: the current bid price on the market when this time and sale event had occured
    bidPrice: float
    #: the current ask price on the market when this time and sale event had occured
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
