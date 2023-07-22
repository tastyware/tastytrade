from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from tastytrade import API_URL, CERT_URL
from tastytrade.dxfeed import (Candle, Event, EventType, Greeks, Profile,
                               Quote, Summary, TheoPrice, TimeAndSale, Trade,
                               Underlying)
from tastytrade.utils import TastytradeError, validate_response


class Session(ABC):
    """
    An abstract class which contains the basic functionality of a session.
    """
    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    @abstractmethod
    def headers(self) -> Dict[str, str]:
        pass

    @property
    @abstractmethod
    def user(self) -> Dict[str, str]:
        pass

    @property
    @abstractmethod
    def session_token(self) -> str:
        pass

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

        :return:
            True if the session terminated successfully and False otherwise.
        """
        response = requests.delete(
            f'{self.base_url}/sessions',
            headers=self.headers
        )

        return (response.status_code // 100 == 2)

    def get_customer(self) -> Dict[str, Any]:
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


class CertificationSession(Session):
    """
    A certification (test) session created at the developer portal which can
    be used to interact with the remote API.

    :param login: tastytrade username or email
    :param remember_me:
        whether or not to create a remember token to use instead of a password
    :param password:
        tastytrade password to login; if absent, remember token is required
    :param remember_token:
        previously generated token; if absent, password is required
    """
    def __init__(
        self,
        login: str,
        password: Optional[str] = None,
        remember_me: bool = False,
        remember_token: Optional[str] = None
    ):
        body = {
            'login': login,
            'remember-me': remember_me
        }
        if password is not None:
            body['password'] = password
        elif remember_token is not None:
            body['remember-token'] = remember_token
        else:
            raise TastytradeError('You must provide a password or remember '
                                  'token to log in.')
        #: The base url to use for API requests
        self.base_url: str = CERT_URL

        response = requests.post(f'{self.base_url}/sessions', json=body)
        validate_response(response)  # throws exception if not 200

        json = response.json()
        #: The user dict returned by the API; contains basic user information
        self.user: Dict[str, str] = json['data']['user']
        #: The session token used to authenticate requests
        self.session_token: str = json['data']['session-token']
        #: A single-use token which can be used to login without a password
        self.remember_token: Optional[str] = \
            json['data']['remember-token'] if remember_me else None
        #: The headers to use for API requests
        self.headers: Dict[str, str] = {'Authorization': self.session_token}
        self.validate()


class ProductionSession(Session):
    """
    Contains a local user login which can then be used to interact with the
    remote API.

    :param login: tastytrade username or email
    :param remember_me:
        whether or not to create a remember token to use instead of a password
    :param password:
        tastytrade password to login; if absent, remember token is required
    :param remember_token:
        previously generated token; if absent, password is required
    :param two_factor_authentication:
        if two factor authentication is enabled, this is the code sent to the
        user's device
    """
    def __init__(
        self,
        login: str,
        password: Optional[str] = None,
        remember_me: bool = False,
        remember_token: Optional[str] = None,
        two_factor_authentication: Optional[str] = None
    ):
        body = {
            'login': login,
            'remember-me': remember_me
        }
        if password is not None:
            body['password'] = password
        elif remember_token is not None:
            body['remember-token'] = remember_token
        else:
            raise TastytradeError('You must provide a password or remember '
                                  'token to log in.')
        #: The base url to use for API requests
        self.base_url: str = API_URL

        if two_factor_authentication is not None:
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
        self.user: Dict[str, str] = json['data']['user']
        #: The session token used to authenticate requests
        self.session_token: str = json['data']['session-token']
        #: A single-use token which can be used to login without a password
        self.remember_token: Optional[str] = \
            json['data']['remember-token'] if remember_me else None
        #: The headers to use for API requests
        self.headers: Dict[str, str] = {'Authorization': self.session_token}
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

    def get_candle(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        extended_trading_hours: bool = False
    ) -> List[Candle]:
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
        candle_str = f'{{={interval},tho=true}}' \
            if extended_trading_hours else f'{{={interval}}}'
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
            params=params  # type: ignore
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
        symbols: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Event]:
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
        # this shouldn't be called with candle
        if event_type == EventType.CANDLE:
            raise TastytradeError('Invalid event type for `get_event`: Use '
                                  '`get_candle` instead!')
        params: Dict[str, Any] = {
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
        symbols: List[str],
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[TimeAndSale]:
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
            params=params  # type: ignore
        )
        validate_response(response)  # throws exception if not 200

        data = response.json()[EventType.TIME_AND_SALE]
        tas = []
        for symbol in symbols:
            tas.extend([TimeAndSale(**d) for d in data[symbol]])

        return tas


def _map_event(
    event_type: str,
    event_dict: Dict[str, Any]
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
        return Underlying(**event_dict[0])  # type: ignore
    else:
        raise TastytradeError(f'Unknown event type: {event_type}')
