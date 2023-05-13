from datetime import date
from typing import Any

import requests

from tastytrade.session import Session
from tastytrade.utils import validate_response


def get_market_metrics(session: Session, symbols: list[str]) -> dict[str, Any]:
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


def get_dividends(session: Session, symbol: str) -> dict[str, Any]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for

    :return: a list of Tastytrade 'DividendInfo' objects in JSON format.
    """
    response = requests.get(
        f'{session.base_url}/market-metrics/historic-corporate-events/dividends/{symbol}',
        headers=session.headers
    )
    validate_response(response)

    return response.json()['data']['items']


def get_earnings(session: Session, symbol: str, start_date: date) -> dict[str, Any]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date

    :return: a list of Tastytrade 'EarningsInfo' objects in JSON format.
    """
    response = requests.get(
        f'{session.base_url}/market-metrics/historic-corporate-events/earnings-reports/{symbol}',
        headers=session.headers,
        params={'start-date': start_date}  # type: ignore
    )
    validate_response(response)

    return response.json()['data']['items']
