from dataclasses import dataclass

from .event import Event


@dataclass
class Profile(Event):
    """
    A Profile event provides the security instrument description. It
    represents the most recent information that is available about the
    traded security on the market at any given moment of time.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: description of the security instrument
    description: str
    #: short sale restriction of the security instrument
    #: possible values are ACTIVE | INACTIVE | UNDEFINED
    shortSaleRestriction: str
    #: trading status of the security instrument
    #: possible values are ACTIVE | HALTED | UNDEFINED
    tradingStatus: str
    #: description of the reason that trading was halted
    statusReason: str
    #: starting time of the trading halt interval
    haltStartTime: int
    #: ending time of the trading halt interval
    haltEndTime: int
    #: maximal (high) allowed price
    highLimitPrice: float
    #: minimal (low) allowed price
    lowLimitPrice: float
    #: maximal (high) price in last 52 weeks
    high52WeekPrice: float
    #: minimal (low) price in last 52 weeks
    low52WeekPrice: float
    #: the correlation coefficient of the instrument to the S&P500 index
    beta: float
    #: earnings per share
    earningsPerShare: float
    #: frequency of cash dividends payments per year (calculated)
    dividendFrequency: float
    #: the amount of the last paid dividend
    exDividendAmount: float
    #: identifier of the ex-dividend date
    exDividendDayId: int
    #: shares outstanding
    shares: float
    #: the number of shares that are available to the public for trade
    freeFloat: float
