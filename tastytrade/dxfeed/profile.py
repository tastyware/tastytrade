from decimal import Decimal
from typing import Optional

from .event import Event


class Profile(Event):
    """
    A Profile event provides the security instrument description. It
    represents the most recent information that is available about the
    traded security on the market at any given moment of time.
    """

    #: description of the security instrument
    description: str
    #: short sale restriction of the security instrument
    #: possible values are ACTIVE | INACTIVE | UNDEFINED
    short_sale_restriction: str
    #: trading status of the security instrument
    #: possible values are ACTIVE | HALTED | UNDEFINED
    trading_status: str
    #: starting time of the trading halt interval
    halt_start_time: int
    #: ending time of the trading halt interval
    halt_end_time: int
    #: identifier of the ex-dividend date
    ex_dividend_day_id: int
    #: description of the reason that trading was halted
    status_reason: Optional[str] = None
    #: maximal (high) price in last 52 weeks
    high_52_week_price: Optional[Decimal] = None
    #: minimal (low) price in last 52 weeks
    low_52_week_price: Optional[Decimal] = None
    #: the correlation coefficient of the instrument to the S&P500 index
    beta: Optional[Decimal] = None
    #: shares outstanding
    shares: Optional[Decimal] = None
    #: maximal (high) allowed price
    high_limit_price: Optional[Decimal] = None
    #: minimal (low) allowed price
    low_limit_price: Optional[Decimal] = None
    #: earnings per share
    earnings_per_share: Optional[Decimal] = None
    #: the amount of the last paid dividend
    ex_dividend_amount: Optional[Decimal] = None
    #: frequency of cash dividends payments per year (calculated)
    dividend_frequency: Optional[Decimal] = None
    #: the number of shares that are available to the public for trade
    free_float: Optional[Decimal] = None
