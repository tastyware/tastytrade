import requests

from tastytrade import API_URL, CERT_URL


class Session:
    """
    Contains a local user login which can then be used to interact with the remote API.
    """
    def __init__(self, username: str, password: str, TwoFA: str = None):
        body = {
            'login': username,
            'password': password,
            'remember-me': True
        }
        
        if TwoFA: 
            headers = {
                'X-Tastyworks-OTP': TwoFA
            }
            resp = requests.post(f'{CERT_URL}/sessions', json=body, headers=headers)
        else:
            resp = requests.post(f'{API_URL}/sessions', json=body)

        if resp.status_code // 100 != 2:
            raise Exception('Failed to log in, message: {}'.format(resp.json()['error']['message']))

        self.session_token = resp.json()['data']['session-token']
        self.remember_token = resp.json()['data']['remember-token']
        self.is_valid()

    def is_valid(self) -> bool:
        """
        Performs a check to see if the session is legitimate.

        :return: True if the session is valid and False otherwise.
        """
        resp = requests.post(f'{API_URL}/sessions/validate', headers=self.get_request_headers())
        if resp.status_code // 100 == 2:
            return True
        return False

    def terminate_session(self) -> bool:
        """
        Sends a API request to delete the existing session. This will invalidate the
        current session token and login.

        :return: True if the session was terminated and False otherwise.
        """
        resp = requests.delete(f'{API_URL}/sessions', headers=self.get_request_headers())
        if resp.status_code // 100 == 2:
            self.session_token = None
            return True
        return False

    def get_request_headers(self) -> dict[str, str]:
        """
        Gets the session authentication data to be used with API requests.

        :return: The request header containing session authorization data
        """
        return {'Authorization token': self.session_token, 'Remember token': self.remember_token}