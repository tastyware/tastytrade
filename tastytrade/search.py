import requests

from tastytrade.session import Session


def symbol_search(session: Session, symbol: str) -> list[dict[str, str]]:
    """
    Performs a symbol search using the Tastytrade API and returns a list of symbols that
    are similar to the given search phrase.

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
        # here it doesn't really make sense to throw an exception; we'll just return nothing
        return []
    else:
        data = response.json()
        return data['data']['items']
