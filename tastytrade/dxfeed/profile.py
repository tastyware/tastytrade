from decimal import Decimal
from typing import Optional

from .event import Event


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
    #: starting time of the trading halt interval
    haltStartTime: int
    #: ending time of the trading halt interval
    haltEndTime: int
    #: identifier of the ex-dividend date
    exDividendDayId: int
    #: description of the reason that trading was halted
    statusReason: Optional[str] = None
    #: maximal (high) price in last 52 weeks
    high52WeekPrice: Optional[Decimal] = None
    #: minimal (low) price in last 52 weeks
    low52WeekPrice: Optional[Decimal] = None
    #: the correlation coefficient of the instrument to the S&P500 index
    beta: Optional[Decimal] = None
    #: shares outstanding
    shares: Optional[Decimal] = None
    #: maximal (high) allowed price
    highLimitPrice: Optional[Decimal] = None
    #: minimal (low) allowed price
    lowLimitPrice: Optional[Decimal] = None
    #: earnings per share
    earningsPerShare: Optional[Decimal] = None
    #: the amount of the last paid dividend
    exDividendAmount: Optional[Decimal] = None
    #: frequency of cash dividends payments per year (calculated)
    dividendFrequency: Optional[Decimal] = None
    #: the number of shares that are available to the public for trade
    freeFloat: Optional[Decimal] = None
