from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests

from tastytrade.session import Session
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
    implied_volatility_index: Decimal
    implied_volatility_index_5_day_change: Decimal
    implied_volatility_index_rank: Decimal
    tos_implied_volatility_index_rank: Decimal
    tw_implied_volatility_index_rank: Decimal
    tos_implied_volatility_index_rank_updated_at: datetime
    implied_volatility_index_rank_source: str
    implied_volatility_percentile: Decimal
    implied_volatility_updated_at: datetime
    liquidity_value: Decimal
    liquidity_rank: Decimal
    liquidity_rating: int
    updated_at: datetime
    option_expiration_implied_volatilities: List[OptionExpirationImpliedVolatility]  # noqa: E501
    liquidity_running_state: Liquidity
    beta: Decimal
    beta_updated_at: datetime
    corr_spy_3month: Decimal
    dividend_rate_per_share: Decimal
    dividend_yield: Decimal
    listed_market: str
    lendability: str
    borrow_rate: Decimal
    market_cap: Decimal
    implied_volatility_30_day: Decimal
    historical_volatility_30_day: Decimal
    historical_volatility_60_day: Decimal
    historical_volatility_90_day: Decimal
    iv_hv_30_day_difference: Decimal
    price_earnings_ratio: Decimal
    earnings_per_share: Decimal
    created_at: Optional[datetime] = None
    dividend_ex_date: Optional[date] = None
    dividend_next_date: Optional[date] = None
    dividend_pay_date: Optional[date] = None
    dividend_updated_at: Optional[datetime] = None


def get_market_metrics(
    session: Session,
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


def get_dividends(session: Session, symbol: str) -> List[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for

    :return: a list of Tastytrade 'DividendInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    response = requests.get(
        f'{session.base_url}/market-metrics/historic-corporate-events/dividends/{symbol}',  # noqa: E501
        headers=session.headers
    )
    validate_response(response)

    data = response.json()['data']['items']

    return [DividendInfo(**entry) for entry in data]


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

    :return: a list of Tastytrade 'EarningsInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    params: Dict[str, Any] = {'start-date': start_date}
    response = requests.get(
        f'{session.base_url}/market-metrics/historic-corporate-events/earnings-reports/{symbol}',  # noqa: E501
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
