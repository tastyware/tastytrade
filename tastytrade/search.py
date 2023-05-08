import aiohttp

from tastytrade import API_URL
from tastytrade.session import Session


async def symbol_search(session: Session, symbol: str) -> list[dict[str, str]]:
    """
    Performs a symbol search using the Tastyworks API.

    This returns a list of symbols that are similar to the symbol passed in
    the parameters. This does not provide any details except the related
    symbols and their descriptions.

    :param session: active user session to use
    :param symbol: search phrase

    :return: a list of symbols and descriptions that are closely related to the passed symbol parameter

    :raises Exception: bad response code
    """

    url = f'{API_URL}/symbols/search/{symbol}'

    async with aiohttp.request('GET', url, headers=session.headers) as resp:
        data = await resp.json()
        if resp.status // 100 != 2:
            raise Exception(f'Failed to query symbols. Response status: {resp.status}; message: {data["error"]["message"]}')

    return data['data']['items']
