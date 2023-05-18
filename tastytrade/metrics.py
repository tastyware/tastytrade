from datetime import date
from decimal import Decimal
from typing import Any, TypedDict

import requests

from tastytrade.session import Session
from tastytrade.utils import validate_response

DividendInfo = TypedDict('DividendInfo', {
    'occurred-date': date,
    'amount': Decimal
}, total=False)
EarningsInfo = TypedDict('EarningsInfo', {
    'occurred-date': date,
    'eps': Decimal
}, total=False)
MarketMetricInfo = TypedDict('MarketMetricInfo', {
    'symbol': str,
    'implied-volatility-index': Decimal,
    'implied-volatility-index-5-day-change': Decimal,
    'implied-volatility-rank': Decimal,
    'implied-volatility-percentile': Decimal,
    'liquidity': Decimal,
    'liquidity-rank': Decimal,
    'liquidity-rating': int,
    'option-expiration-implied-volatilities': list[dict[str, Any]]
}, total=False)


def get_market_metrics(session: Session, symbols: list[str]) -> list[MarketMetricInfo]:
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

    return response.json()['data']['items']


def get_dividends(session: Session, symbol: str) -> list[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for

    :return: a list of Tastytrade 'DividendInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    response = requests.get(
        f'{session.base_url}/market-metrics/historic-corporate-events/dividends/{symbol}',
        headers=session.headers
    )
    validate_response(response)

    return response.json()['data']['items']


def get_earnings(session: Session, symbol: str, start_date: date) -> list[EarningsInfo]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date

    :return: a list of Tastytrade 'EarningsInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    params: dict[str, Any] = {'start-date': start_date}
    response = requests.get(
        f'{session.base_url}/market-metrics/historic-corporate-events/earnings-reports/{symbol}',
        headers=session.headers,
        params=params
    )
    validate_response(response)

    return response.json()['data']['items']
