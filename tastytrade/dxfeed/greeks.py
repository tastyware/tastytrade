from dataclasses import dataclass

from .event import Event


@dataclass
class Greeks(Event):
    """
    Greek ratios, or simply Greeks, are differential values that show how the
    price of an option depends on other market parameters: on the price of the
    underlying asset, its volatility, etc. Greeks are used to assess the risks
    of customer portfolios. Greeks are derivatives of the value of securities
    in different axes. If a derivative is very far from zero, then the
    portfolio has a risky sensitivity in this parameter.
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
    #: option market price
    price: float
    #: Black-Scholes implied volatility of the option
    volatility: float
    #: option delta
    delta: float
    #: option gamma
    gamma: float
    #: option theta
    theta: float
    #: option rho
    rho: float
    #: option vega
    vega: float
