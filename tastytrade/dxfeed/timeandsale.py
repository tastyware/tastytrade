from decimal import Decimal

from .event import IndexedEvent


class TimeAndSale(IndexedEvent):
    """
    TimeAndSale event represents a trade or other market event with a price,
    like market open/close price. TimeAndSale events are intended to provide
    information about trades in a continuous-time slice (unlike Trade events
    which are supposed to provide snapshots about the most recent trade).
    TimeAndSale events have a unique index that can be used for later
    correction/cancellation processing.
    """

    #: unique per-symbol index of this time and sale event
    index: int
    #: timestamp of the original event
    time: int
    #: microseconds and nanoseconds part of time of the last bid or ask change
    time_nano_part: int
    #: sequence of this quote
    sequence: int
    #: exchange code of this time and sale event
    exchange_code: str
    #: price of this time and sale event
    price: Decimal
    #: size of this time and sale event as integer number (rounded toward zero)
    size: int
    #: the bid price on the market when this time and sale event occured
    bid_price: Decimal
    #: the ask price on the market when this time and sale event occured
    ask_price: Decimal
    #: sale conditions provided for this event by data feed
    exchange_sale_conditions: str
    #: transaction is concluded by exempting from compliance with some rule
    trade_through_exempt: str
    #: initiator of the trade
    aggressor_side: str
    #: whether this transaction is a part of a multi-leg order
    spread_leg: bool
    #: whether this transaction is completed during extended trading hours
    extended_trading_hours: bool
    #: normalized SaleCondition flag
    valid_tick: bool
    #: type of event - 0: new, 1: correction, 2: cancellation
    type: str
    #: Undocumented; always None
    buyer: None
    #: Undocumented; always None
    seller: None
