import requests

from tastytrade import API_URL
from tastytrade.utils import validate_response


class Session:
    """
    Contains a local user login which can then be used to interact with the remote API.
    """
    def __init__(self, login: str, password: str, remember_me: bool = False,
                 two_factor_authentication: str = ''):
        body = {
            'login': login,
            'password': password,
            'remember-me': remember_me
        }

        if two_factor_authentication:
            headers = {'X-Tastyworks-OTP': two_factor_authentication}
            response = requests.post(f'{API_URL}/sessions', json=body, headers=headers)
        else:
            response = requests.post(f'{API_URL}/sessions', json=body)
        validate_response(response)  # throws exception if not 200

        json = response.json()
        self.user = json['data']['user']
        self.session_token = json['data']['session-token']
        self.remember_token = json['data']['remember-token'] if remember_me else None
        self.headers = {'Authorization': self.session_token}
        self.validate()

    def validate(self) -> None:
        """
        Validates the current session by sending a request to the API. If the session is
        invalid, an exception will be thrown.
        """
        response = requests.post(f'{API_URL}/sessions/validate', headers=self.headers)
        validate_response(response)  # throws exception if not 200

    def destroy(self) -> bool:
        """
        Sends a API request to log out of the existing session. This will invalidate the
        current session token and login.

        :return: True if the session was terminated and False otherwise.
        """
        response = requests.delete(f'{API_URL}/sessions', headers=self.headers)
        if response.status_code // 100 == 2:
            return True
        return False
