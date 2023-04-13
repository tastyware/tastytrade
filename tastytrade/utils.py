import calendar
from datetime import date, datetime, timedelta
import logging

import aiohttp
import requests

API_URL = 'https://api.tastyworks.com'
LOGGER = logging.getLogger(__name__)
VERSION = '1.0'


class Session:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.logged_in = False
        self.session_token = self._get_session_token()

    def _get_session_token(self):
        if self.logged_in and self.session_token:
            if (datetime.datetime.now() - self.logged_in_at).total_seconds() < 60:
                return self.session_token

        body = {
            'login': self.username,
            'password': self.password
        }
        resp = requests.post(f'{API_URL}/sessions', json=body)
        if resp.status_code != 201:
            self.logged_in = False
            self.logged_in_at = None
            self.session_token = None
            raise Exception('Failed to log in, message: {}'.format(resp.json()['error']['message']))

        self.logged_in = True
        self.logged_in_at = datetime.now()
        self.session_token = resp.json()['data']['session-token']
        self._validate_session()
        return self.session_token

    def is_active(self):
        return self._validate_session()

    def _validate_session(self):
        resp = requests.post(f'{API_URL}/sessions/validate', headers=self.get_request_headers())
        if resp.status_code != 201:
            self.logged_in = False
            self.logged_in_at = None
            self.session_token = None
            raise Exception('Could not validate the session, error message: {}'.format(
                resp.json()['error']['message']
            ))
            return False
        return True

    def get_request_headers(self):
        return {
            'Authorization': self.session_token
        }


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

    async with aiohttp.request('GET', url, headers=session.get_request_headers()) as resp:
        data = await resp.json()
        if resp.status != 200:
            raise Exception(f'Failed to query symbols. Response status: {resp.status}; message: {data["error"]["message"]}')

    return data['data']['items']
