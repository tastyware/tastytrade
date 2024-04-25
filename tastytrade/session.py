from abc import ABC
from typing import Any, Dict, Optional

import requests
from fake_useragent import UserAgent  # type: ignore

from tastytrade import API_URL, CERT_URL
from tastytrade.utils import (TastytradeError, TastytradeJsonDataclass,
                              validate_response)


class TwoFactorInfo(TastytradeJsonDataclass):
    is_active: bool
    type: Optional[str] = None


class Session(ABC):
    """
    An abstract class which contains the basic functionality of a session.
    """
    base_url: str
    headers: Dict[str, str]
    user: Dict[str, str]
    session_token: str

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

        # Pull streamer tokens and urls
        response = requests.get(
            f'{self.base_url}/api-quote-tokens',
            headers=self.headers
        )
        validate_response(response)
        data = response.json()['data']
        self.streamer_token = data['token']
        self.dxlink_url = data['dxlink-url']
        self.streamer_headers = {
            'Authorization': f'Bearer {self.streamer_token}'
        }


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
        #: The headers to use for API requests
        self.headers: Dict[str, str] = {'User-Agent': UserAgent().random}

        if two_factor_authentication is not None:
            headers = {
                **self.headers,
                'X-Tastyworks-OTP': two_factor_authentication
            }
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
        self.headers['Authorization'] = self.session_token
        #: A single-use token which can be used to login without a password
        self.remember_token: Optional[str] = \
            json['data']['remember-token'] if remember_me else None
        self.validate()

        # Pull streamer tokens and urls
        response = requests.get(
            f'{self.base_url}/quote-streamer-tokens',
            headers=self.headers
        )
        validate_response(response)
        data = response.json()['data']
        self.streamer_token = data['token']
        self.dxlink_url = data['dxlink-url']
        self.streamer_headers = {
            'Authorization': f'Bearer {self.streamer_token}'
        }

    def get_2fa_info(self) -> TwoFactorInfo:
        """
        Gets the 2FA info for the current user.

        :return: a dictionary containing the 2FA info.
        """
        response = requests.get(
            f'{self.base_url}/users/me/two-factor-method',
            headers=self.headers
        )
        validate_response(response)

        data = response.json()['data']

        return TwoFactorInfo(**data)
