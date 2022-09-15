import aiohttp

from tastyworks.models.session import TastyAPISession


async def symbol_search(symbol: str, session: TastyAPISession):
    """
    Performs a symbol search using Tastyworks API.

    This returns a list of symbols that are similar to the symbol passed in
    the parameters. This does not provide any details except the related
    symbols and their descriptions.

    Args:
        symbol (string): A base symbol to search for similar symbols

    Returns:
        list (dict): A list of symbols and descriptions that are closely
                     related to the passed symbol parameter
    """

    url = f'{session.API_url}/symbols/search/{symbol}'

    async with aiohttp.request('GET', url, headers=session.get_request_headers()) as resp:
        data = await resp.json()
        if resp.status != 200:
            raise Exception(f'Failed to query symbols. Response status: {resp.status}; message: {data["error"]["message"]}')

    return data['data']['items']
