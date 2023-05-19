from typing import Any, Optional

import requests

from tastytrade import API_URL, CERT_URL
from tastytrade.utils import validate_response


class Session:
    """
    Contains a local user login which can then be used to interact with the remote API.

    :param login: tastytrade username or email
    :param password: tastytrade password or a remember token obtained previously
    :param remember_me:
        whether or not to generate a token which can be used to login without a password;
        appears to be bugged currently.
    :param two_factor_authentication:
        if two factor authentication is enabled, this is the code sent to the user's device
    :param is_certification: whether or not to use the certification API
    """
    def __init__(self, login: str, password: str, remember_me: bool = False,
                 two_factor_authentication: str = '', is_certification: bool = False):
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
            response = requests.post(f'{self.base_url}/sessions', json=body, headers=headers)
        else:
            response = requests.post(f'{self.base_url}/sessions', json=body)
        validate_response(response)  # throws exception if not 200

        json = response.json()
        #: The user dict returned by the API; contains basic user information
        self.user: dict[str, str] = json['data']['user']
        #: The session token used to authenticate requests
        self.session_token: str = json['data']['session-token']
        #: An alternate token which can be used to login without a password
        self.remember_token: Optional[str] = json['data']['remember-token'] if remember_me else None
        #: The headers to use for API requests
        self.headers: dict[str, str] = {'Authorization': self.session_token}
        self.validate()

    def validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.

        :return: True if the session is valid and False otherwise.
        """
        response = requests.post(f'{self.base_url}/sessions/validate', headers=self.headers)
        return (response.status_code // 100 == 2)

    def destroy(self) -> bool:
        """
        Sends a API request to log out of the existing session. This will invalidate the
        current session token and login.

        :return: True if the session was terminated successfully and False otherwise.
        """
        response = requests.delete(f'{self.base_url}/sessions', headers=self.headers)
        return (response.status_code // 100 == 2)

    def get_customer(self) -> dict[str, Any]:
        """
        Gets the customer dict from the API.

        :return: a Tastytrade 'Customer' object in JSON format.
        """
        response = requests.get(f'{self.base_url}/customers/me', headers=self.headers)
        validate_response(response)  # throws exception if not 200

        return response.json()['data']
