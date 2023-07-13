from datetime import datetime
from typing import Any, Optional

import requests

from tastytrade import API_URL, CERT_URL
from tastytrade.dxfeed import (Candle, Event, EventType, Greeks, Profile,
                               Quote, Summary, TheoPrice, TimeAndSale, Trade,
                               Underlying)
from tastytrade.utils import TastytradeError, validate_response


class Session:
    """
    Contains a local user login which can then be used to interact with the
    remote API.

    :param login: tastytrade username or email
    :param password:
        tastytrade password or a remember token obtained previously
    :param remember_me:
        whether or not to create a single-use remember token to use in place
        of a password; currently appears to be bugged.
    :param two_factor_authentication:
        if two factor authentication is enabled, this is the code sent to the
        user's device
    :param is_certification: whether or not to use the certification API
    """
    def __init__(
        self,
        login: str,
        password: str,
        remember_me: bool = False,
        two_factor_authentication: str = '',
        is_certification: bool = False
    ):
        body = {
            'login': login,
            'password': password,
            'remember-me': remember_me
        }
        #: The base url to use for API requests
        self.base_url: str = CERT_URL if is_certification else API_URL
        #: Whether or not this session is using the certification API
        self.is_certification: bool = is_certification

        if two_factor_authentication:
            headers = {'X-Tastyworks-OTP': two_factor_authentication}
            response = requests.post(
                f'{self.base_url}/sessions',
                json=body,
                headers=headers
            )
        else:
            response = requests.post(f'{self.base_url}/sessions', json=body)
        validate_response(response)  # throws exception if not 200

        json = response.json()
        #: The user dict returned by the API; contains basic user information
        self.user: dict[str, str] = json['data']['user']
        #: The session token used to authenticate requests
        self.session_token: str = json['data']['session-token']
        #: A single-use token which can be used to login without a password
        self.remember_token: Optional[str] = \
            json['data']['remember-token'] if remember_me else None
        #: The headers to use for API requests
        self.headers: dict[str, str] = {'Authorization': self.session_token}
        self.validate()

        #: Pull streamer tokens and urls
        response = requests.get(
            f'{self.base_url}/quote-streamer-tokens',
            headers=self.headers
        )
        validate_response(response)
        data = response.json()['data']
        self.streamer_token = data['token']
        url = data['websocket-url'] + '/cometd'
        self.streamer_url = url.replace('https', 'wss')
        self.rest_url = data['websocket-url'] + '/rest/events.json'
        self.streamer_headers = {
            'Authorization': f'Bearer {self.streamer_token}'
        }

    def validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.

        :return: True if the session is valid and False otherwise.
        """
        response = requests.post(
            f'{self.base_url}/sessions/validate',
            headers=self.headers
        )
        return (response.status_code // 100 == 2)

    def destroy(self) -> bool:
        """
        Sends a API request to log out of the existing session. This will
        invalidate the current session token and login.

        :return: True if the session was terminated successfully and
        False otherwise.
        """
        response = requests.delete(
            f'{self.base_url}/sessions',
            headers=self.headers
        )
        return (response.status_code // 100 == 2)

    def get_customer(self) -> dict[str, Any]:
        """
        Gets the customer dict from the API.

        :return: a Tastytrade 'Customer' object in JSON format.
        """
        response = requests.get(
            f'{self.base_url}/customers/me',
            headers=self.headers
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']

    def get_candle(
        self,
        symbols: list[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        extended_trading_hours: bool = False
    ) -> list[Candle]:
        """
        Using the dxfeed REST API, fetchs Candle events for the given list of
        symbols.

        This is meant for single-use requests. If you need a fast, recurring
        datastream, use :class:`tastytrade.streamer.Streamer` instead.

        :param symbols: the list of symbols to fetch the event for
        :param interval:
            the width of each candle in time, e.g. '15s', '5m', '1h', '3d',
            '1w', '1mo'
        :param start_time: starting time for the data range
        :param end_time: ending time for the data range
        :param extended_trading_hours: whether to include extended trading

        :return: a list of Candle events
        """
        candle_str = (f'{{={interval},tho=true}}'
        if extended_trading_hours else f'{{={interval}}}')
        params = {
            'events': EventType.CANDLE,
            'symbols': (candle_str + ',').join(symbols) + candle_str,
            'fromTime': int(start_time.timestamp() * 1000)
        }
        if end_time is not None:
            params['toTime'] = int(end_time.timestamp() * 1000)
        response = requests.get(
            self.rest_url,
            headers=self.streamer_headers,
            params=params
        )
        validate_response(response)  # throws exception if not 200

        data = response.json()[EventType.CANDLE]
        candles = []
        for _, v in data.items():
            candles.extend([Candle(**d) for d in v])

        return candles

    def get_event(
        self,
        event_type: EventType,
        symbols: list[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list[Event]:
        """
        Using the dxfeed REST API, fetches an event for the given list of
        symbols. For `EventType.CANDLE`, use :meth:`get_candle` instead, and
        :meth:`get_time_and_sale` for `EventType.TIME_AND_SALE`.

        This is meant for single-use requests. If you need a fast, recurring
        datastream, use :class:`tastytrade.streamer.Streamer` instead.

        :param event_type: the type of event to fetch
        :param symbols: the list of symbols to fetch the event for
        :param start_time: the start time of the event
        :param end_time: the end time of the event

        :return: a list of events
        """
        params: dict[str, Any] = {
            'events': event_type,
            'symbols': ','.join(symbols)
        }
        if start_time is not None:
            params['fromTime'] = int(start_time.timestamp() * 1000)
        if end_time is not None:
            params['toTime'] = int(end_time.timestamp() * 1000)
        response = requests.get(
            self.rest_url,
            headers=self.streamer_headers,
            params=params
        )
        validate_response(response)  # throws exception if not 200

        data = response.json()[event_type]

        return [_map_event(event_type, v) for _, v in data.items()]

    def get_time_and_sale(
        self,
        symbols: list[str],
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> list[TimeAndSale]:
        """
        Using the dxfeed REST API, fetchs TimeAndSale events for the given
        list of symbols.

        This is meant for single-use requests. If you need a fast, recurring
        datastream, use :class:`tastytrade.streamer.Streamer` instead.

        :param symbols: the list of symbols to fetch the event for
        :param start_time: the start time of the event
        :param end_time: the end time of the event

        :return: a list of TimeAndSale events
        """
        params = {
            'events': EventType.TIME_AND_SALE,
            'symbols': ','.join(symbols),
            'fromTime': int(start_time.timestamp() * 1000)
        }
        if end_time is not None:
            params['toTime'] = int(end_time.timestamp() * 1000)
        response = requests.get(
            self.rest_url,
            headers=self.streamer_headers,
            params=params
        )
        validate_response(response)  # throws exception if not 200

        data = response.json()[EventType.TIME_AND_SALE]
        tas = []
        for symbol in symbols:
            tas.extend([TimeAndSale(**d) for d in data[symbol]])

        return tas


def _map_event(
    event_type: str,
    event_dict: dict[str, Any]
) -> Event:
    """
    Parses the raw JSON data from the dxfeed REST API into event objects.

    :param event_type: the type of event to map to
    :param event_dict: the raw JSON data from the dxfeed REST API
    """
    if event_type == EventType.GREEKS:
        return Greeks(**event_dict)
    elif event_type == EventType.PROFILE:
        return Profile(**event_dict)
    elif event_type == EventType.QUOTE:
        return Quote(**event_dict)
    elif event_type == EventType.SUMMARY:
        return Summary(**event_dict)
    elif event_type == EventType.THEO_PRICE:
        return TheoPrice(**event_dict)
    elif event_type == EventType.TRADE:
        return Trade(**event_dict)
    elif event_type == EventType.UNDERLYING:
        return Underlying(**event_dict[0])
    else:
        raise TastytradeError(f'Unknown event type: {event_type}')
