from typing import List

import requests

from tastytrade.session import Session
from tastytrade.utils import TastytradeJsonDataclass


class SymbolData(TastytradeJsonDataclass):
    """
    Dataclass holding search results for an individual item.
    """
    symbol: str
    description: str


def symbol_search(session: Session, symbol: str) -> List[SymbolData]:
    """
    Performs a symbol search using the Tastytrade API and returns a
    list of symbols that are similar to the given search phrase.

    :param session: active user session to use
    :param symbol: search phrase

    :return: a list of symbols and descriptions that match the search phrase
    """
    symbol = symbol.replace('/', '%2F')
    response = requests.get(
        f'{session.base_url}/symbols/search/{symbol}',
        headers=session.headers
    )
    if response.status_code // 100 != 2:
        # here it doesn't really make sense to throw an exception
        return []
    else:
        data = response.json()['data']['items']
        return [SymbolData(**entry) for entry in data]
