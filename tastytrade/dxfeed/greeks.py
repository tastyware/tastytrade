from decimal import Decimal

from .event import IndexedEvent


class Greeks(IndexedEvent):
    """
    Greek ratios, or simply Greeks, are differential values that show how the
    price of an option depends on other market parameters: on the price of the
    underlying asset, its volatility, etc. Greeks are used to assess the risks
    of customer portfolios. Greeks are derivatives of the value of securities
    in different axes. If a derivative is very far from zero, then the
    portfolio has a risky sensitivity in this parameter.
    """

    #: unique per-symbol index of this event
    index: int
    #: timestamp of this event in milliseconds
    time: int
    #: sequence number to distinguish events that have the same time
    sequence: int
    #: option market price
    price: Decimal
    #: Black-Scholes implied volatility of the option
    volatility: Decimal
    #: option delta
    delta: Decimal
    #: option gamma
    gamma: Decimal
    #: option theta
    theta: Decimal
    #: option rho
    rho: Decimal
    #: option vega
    vega: Decimal
