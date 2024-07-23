from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from tastytrade.session import Session
from tastytrade.utils import TastytradeJsonDataclass


class DividendInfo(TastytradeJsonDataclass):
    """
    Dataclass representing dividend information for a given symbol.
    """
    occurred_date: date
    amount: Decimal


class EarningsInfo(TastytradeJsonDataclass):
    """
    Dataclass representing earnings information for a given symbol.
    """
    occurred_date: date
    eps: Decimal


class EarningsReport(TastytradeJsonDataclass):
    """
    Dataclass containing information about a recent earnings report, or the
    expected date of the next one.
    """
    estimated: bool
    late_flag: int
    visible: bool
    actual_eps: Optional[Decimal] = None
    consensus_estimate: Optional[Decimal] = None
    expected_report_date: Optional[date] = None
    quarter_end_date: Optional[date] = None
    time_of_day: Optional[str] = None
    updated_at: Optional[datetime] = None


class Liquidity(TastytradeJsonDataclass):
    """
    Dataclass representing liquidity information for a given symbol.
    """
    sum: Decimal
    count: int
    started_at: datetime
    updated_at: Optional[datetime] = None


class OptionExpirationImpliedVolatility(TastytradeJsonDataclass):
    """
    Dataclass containing implied volatility information for a given symbol
    and expiration date.
    """
    expiration_date: date
    settlement_type: str
    option_chain_type: str
    implied_volatility: Optional[Decimal] = None


class MarketMetricInfo(TastytradeJsonDataclass):
    """
    Dataclass representing market metrics for a given symbol.

    Contains lots of useful information, like IV rank, IV percentile and beta.
    """
    symbol: str
    implied_volatility_index: Optional[Decimal] = None
    implied_volatility_index_5_day_change: Optional[Decimal] = None
    implied_volatility_index_rank: Optional[str] = None
    tos_implied_volatility_index_rank: Optional[Decimal] = None
    tw_implied_volatility_index_rank: Optional[Decimal] = None
    tos_implied_volatility_index_rank_updated_at: Optional[datetime] = None
    implied_volatility_index_rank_source: Optional[str] = None
    implied_volatility_percentile: Optional[str] = None
    implied_volatility_updated_at: Optional[datetime] = None
    liquidity_rating: Optional[int] = None
    updated_at: datetime
    option_expiration_implied_volatilities: Optional[List[OptionExpirationImpliedVolatility]] = None  # noqa: E501
    beta: Optional[Decimal] = None
    corr_spy_3month: Optional[Decimal] = None
    market_cap: Decimal
    earnings: Optional[EarningsReport] = None
    price_earnings_ratio: Optional[Decimal] = None
    earnings_per_share: Optional[Decimal] = None
    dividend_rate_per_share: Optional[Decimal] = None
    implied_volatility_30_day: Optional[Decimal] = None
    historical_volatility_30_day: Optional[Decimal] = None
    historical_volatility_60_day: Optional[Decimal] = None
    historical_volatility_90_day: Optional[Decimal] = None
    iv_hv_30_day_difference: Optional[Decimal] = None
    beta_updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    dividend_ex_date: Optional[date] = None
    dividend_next_date: Optional[date] = None
    dividend_pay_date: Optional[date] = None
    dividend_updated_at: Optional[datetime] = None
    liquidity_value: Optional[Decimal] = None
    liquidity_rank: Optional[Decimal] = None
    liquidity_running_state: Optional[Liquidity] = None
    dividend_yield: Optional[Decimal] = None
    listed_market: Optional[str] = None
    lendability: Optional[str] = None
    borrow_rate: Optional[Decimal] = None


def get_market_metrics(
    session: Session,
    symbols: List[str]
) -> List[MarketMetricInfo]:
    """
    Retrieves market metrics for the given symbols.

    :param session: active user session to use
    :param symbols: list of symbols to retrieve metrics for
    """
    data = session.get(
        '/market-metrics',
        params={'symbols': ','.join(symbols)}
    )
    return [MarketMetricInfo(**i) for i in data['items']]


def get_dividends(
    session: Session,
    symbol: str
) -> List[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for
    """
    symbol = symbol.replace('/', '%2F')
    data = session.get(f'/market-metrics/historic-corporate-events/'
                       f'dividends/{symbol}')
    return [DividendInfo(**i) for i in data['items']]


def get_earnings(
    session: Session,
    symbol: str,
    start_date: date
) -> List[EarningsInfo]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date
    """
    symbol = symbol.replace('/', '%2F')
    params = {'start-date': start_date}
    data = session.get(
        (f'/market-metrics/historic-corporate-events/'
         f'earnings-reports/{symbol}'),
        params=params
    )
    return [EarningsInfo(**i) for i in data['items']]


def get_risk_free_rate(session: Session) -> Decimal:
    """
    Retrieves the current risk-free rate.

    :param session: active user session to use
    """
    data = session.get('/margin-requirements-public-configuration')
    return Decimal(data['risk-free-rate'])
