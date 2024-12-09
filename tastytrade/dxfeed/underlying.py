from decimal import Decimal

from .event import IndexedEvent


class Underlying(IndexedEvent):
    """
    Underlying event is a snapshot of computed values that are available for
    an option underlying symbol based on the option prices on the market. It
    represents the most recent information that is available about the
    corresponding values on the market at any given moment of time.
    """

    #: unique per-symbol index of this event
    index: int
    #: timestamp of this event in milliseconds
    time: int
    #: sequence number of this event to distinguish events with the same time
    sequence: int
    #: 30-day implied volatility for this underlying based on VIX methodology
    volatility: Decimal
    #: front month implied volatility for the underlying using VIX methodology
    front_volatility: Decimal
    #: back month implied volatility for the underlying using VIX methodology
    back_volatility: Decimal
    #: call options traded volume for a day
    call_volume: int
    #: put options traded volume for a day
    put_volume: int
    #: options traded volume for a day
    option_volume: int
    #: ratio of put options volume to call options volume for a day
    put_call_ratio: Decimal
