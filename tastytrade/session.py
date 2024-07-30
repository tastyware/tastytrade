from typing import Any, Dict, Optional

import requests
from fake_useragent import UserAgent  # type: ignore

from tastytrade import API_URL, CERT_URL
from tastytrade.utils import (TastytradeError, TastytradeJsonDataclass,
                              validate_response)


class TwoFactorInfo(TastytradeJsonDataclass):
    is_active: bool
    type: Optional[str] = None


class Session:
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
    :param is_test:
        whether to use the test API endpoints, default False
    :param two_factor_authentication:
        if two factor authentication is enabled, this is the code sent to the
        user's device
    :param dxfeed_tos_compliant:
        whether to use the dxfeed TOS-compliant API endpoint for the streamer
    """
    def __init__(
        self,
        login: str,
        password: Optional[str] = None,
        remember_me: bool = False,
        remember_token: Optional[str] = None,
        is_test: bool = False,
        two_factor_authentication: Optional[str] = None,
        dxfeed_tos_compliant: bool = False
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
        # The base url to use for API requests
        self.base_url = CERT_URL if is_test else API_URL
        #: Whether this is a cert or real session
        self.is_test = is_test
        # The headers to use for API requests
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': UserAgent().random
        }
        # Set client for requests
        self.client = requests.Session()
        self.client.headers.update(headers)
        if two_factor_authentication is not None:
            response = self.client.post(
                f'{self.base_url}/sessions',
                json=body,
                headers={'X-Tastyworks-OTP': two_factor_authentication}
            )
        else:
            response = self.client.post(
                f'{self.base_url}/sessions',
                json=body
            )
        validate_response(response)  # throws exception if not 200

        json = response.json()
        #: The user dict returned by the API; contains basic user information
        self.user = json['data']['user']
        #: The session token used to authenticate requests
        self.session_token = json['data']['session-token']
        #: A single-use token which can be used to login without a password
        self.remember_token = json['data'].get('remember-token')
        self.client.headers.update({'Authorization': self.session_token})
        self.validate()

        # Pull streamer tokens and urls
        url = ('/api-quote-tokens'
               if dxfeed_tos_compliant or is_test
               else '/quote-streamer-tokens')
        data = self.get(url)
        #: Auth token for dxfeed websocket
        self.streamer_token = data['token']
        #: URL for dxfeed websocket
        self.dxlink_url = data['dxlink-url']

    def get(self, url, **kwargs) -> Dict[str, Any]:
        response = self.client.get(self.base_url + url, timeout=30, **kwargs)
        return self._validate_and_parse(response)

    def delete(self, url, **kwargs) -> None:
        response = self.client.delete(self.base_url + url, **kwargs)
        validate_response(response)

    def post(self, url, **kwargs) -> Dict[str, Any]:
        response = self.client.post(self.base_url + url, **kwargs)
        return self._validate_and_parse(response)

    def put(self, url, **kwargs) -> Dict[str, Any]:
        response = self.client.put(self.base_url + url, **kwargs)
        return self._validate_and_parse(response)

    def _validate_and_parse(
        self,
        response: requests.Response
    ) -> Dict[str, Any]:
        validate_response(response)
        return response.json()['data']

    def validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.

        :return: True if the session is valid and False otherwise.
        """
        response = self.client.post(f'{self.base_url}/sessions/validate')
        return (response.status_code // 100 == 2)

    def destroy(self) -> None:
        """
        Sends a API request to log out of the existing session. This will
        invalidate the current session token and login.
        """
        self.delete('/sessions')

    def get_customer(self) -> Dict[str, Any]:
        """
        Gets the customer dict from the API.

        :return: a Tastytrade 'Customer' object in JSON format.
        """
        data = self.get('/customers/me')
        return data

    def get_2fa_info(self) -> TwoFactorInfo:
        """
        Gets the 2FA info for the current user.
        """
        data = self.get('/users/me/two-factor-method')
        return TwoFactorInfo(**data)
