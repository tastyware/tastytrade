from dataclasses import dataclass

from .event import Event


@dataclass
class Underlying(Event):
    """
    Underlying event is a snapshot of computed values that are available for
    an option underlying symbol based on the option prices on the market. It
    represents the most recent information that is available about the
    corresponding values on the market at any given moment of time.
    """
    #: symbol of this event
    eventSymbol: str
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this event
    index: int
    #: timestamp of this event in milliseconds
    time: int
    #: sequence number of this event to distinguish events with the same time
    sequence: int
    #: 30-day implied volatility for this underlying based on VIX methodology
    volatility: float
    #: front month implied volatility for the underlying using VIX methodology
    frontVolatility: float
    #: back month implied volatility for the underlying using VIX methodology
    backVolatility: float
    #: call options traded volume for a day
    callVolume: int
    #: put options traded volume for a day
    putVolume: int
    #: options traded volume for a day
    optionVolume: int
    #: ratio of put options volume to call options volume for a day
    putCallRatio: float
