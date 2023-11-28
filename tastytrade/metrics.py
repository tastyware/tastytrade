from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests

from tastytrade.session import ProductionSession, Session
from tastytrade.utils import TastytradeJsonDataclass, validate_response


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


class Liquidity(TastytradeJsonDataclass):
    """
    Dataclass representing liquidity information for a given symbol.
    """
    sum: Decimal
    count: int
    started_at: datetime
    updated_at: datetime


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
    session: ProductionSession,
    symbols: List[str]
) -> List[MarketMetricInfo]:
    """
    Retrieves market metrics for the given symbols.

    :param session: active user session to use
    :param symbols: list of symbols to retrieve metrics for

    :return: a list of Tastytrade 'MarketMetricInfo' objects in JSON format.
    """
    response = requests.get(
        f'{session.base_url}/market-metrics',
        headers=session.headers,
        params={'symbols': ','.join(symbols)}
    )
    validate_response(response)

    data = response.json()['data']['items']

    return [MarketMetricInfo(**entry) for entry in data]


def get_dividends(
    session: ProductionSession,
    symbol: str
) -> List[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for

    :return: a list of Tastytrade 'DividendInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    response = requests.get(
        (f'{session.base_url}/market-metrics/historic-corporate-events/'
         f'dividends/{symbol}'),
        headers=session.headers
    )
    validate_response(response)

    data = response.json()['data']['items']

    return [DividendInfo(**entry) for entry in data]


def get_earnings(
    session: ProductionSession,
    symbol: str,
    start_date: date
) -> List[EarningsInfo]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date

    :return: a list of Tastytrade 'EarningsInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    params: Dict[str, Any] = {'start-date': start_date}
    response = requests.get(
        (f'{session.base_url}/market-metrics/historic-corporate-events/'
         f'earnings-reports/{symbol}'),
        headers=session.headers,
        params=params
    )
    validate_response(response)

    data = response.json()['data']['items']

    return [EarningsInfo(**entry) for entry in data]


def get_risk_free_rate(session: Session) -> Decimal:
    """
    Retrieves the current risk-free rate.

    :param session: active user session to use

    :return: the current risk-free rate
    """
    response = requests.get(
        f'{session.base_url}/margin-requirements-public-configuration',
        headers=session.headers
    )
    validate_response(response)

    data = response.json()['data']['risk-free-rate']
    return Decimal(data)
