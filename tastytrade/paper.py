import math
from typing import Any

from httpx import AsyncClient
from httpx_ws import HTTPXWSException

from tastytrade import PAPER_URL
from tastytrade.session import Session
from tastytrade.streamer import AlertStreamer


class PaperSession(Session):
    """
    Contains a session which can be used to interact with the paper trading API.
    Note these sessions are only valid for endpoints in the Account class.

    :param api_key: user's paper API key from https://tastyware.dev/login
    """

    def __init__(self, api_key: str, **client_kwargs: Any):
        super().__init__("kyrie", "eleison", is_test=True)
        self.api_key = api_key
        self.session_expiration = math.inf
        # The headers to use for API requests
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
        }
        # httpx client for async requests
        self._client = AsyncClient(base_url=PAPER_URL, headers=headers, **client_kwargs)
        client_kwargs["headers"] = headers
        self.client_kwargs = client_kwargs


class PaperAlertStreamer(AlertStreamer):
    """
    Designed to mimic the behavior and API of `tastytrade.AlertStreamer`.
    Currently only supports listening to orders.
    """

    def __init__(self, session: PaperSession) -> None:
        super().__init__(session)
        self.base_url = PAPER_URL.replace("http", "ws") + "/notifications"

    def fail(self) -> None:
        """
        Raise an exception in the streamer that can be used to test retries.
        """
        raise HTTPXWSException("Something happened and the fake streamer broke, oh no!")
