import calendar
from datetime import date, timedelta

import aiohttp

from tastytrade import API_URL
from tastytrade.session import Session


async def symbol_search(session: Session, symbol: str) -> list[dict[str, str]]:
    """
    Performs a symbol search using the Tastyworks API.

    This returns a list of symbols that are similar to the given query.
    This does not provide any details except the related symbols and 
    their descriptions.

    :param session: active user session to use
    :param symbol: search phrase

    :return: a list of symbols and descriptions that are closely related to the passed symbol parameter

    :raises Exception: bad response code
    """

    url = f'{API_URL}/symbols/search/{symbol}'

    async with aiohttp.request('GET', url, headers=session.get_request_headers()) as resp:
        data = await resp.json()
        if resp.status // 100 != 2:
            raise Exception(f'Failed to query symbols. Response status: {resp.status}; message: {data["error"]["message"]}')

    return data['data']['items']


def get_third_friday(d: date) -> date:
    """
    Returns the date of the monthly option in the same month as the given date, unless that date has already passed, in which case the next month's monthly will be returned.

    :param d: input date from which to calculate the date of the monthly

    :return: closest monthly to current date that hasn't already passed
    """
    s = date(d.year, d.month, 15)
    candidate = s + timedelta(days=(calendar.FRIDAY - s.weekday()) % 7)

    # This month's third friday passed
    if candidate < d:
        candidate += timedelta(weeks=4)
        if candidate.day < 15:
            candidate += timedelta(weeks=1)

    return candidate
