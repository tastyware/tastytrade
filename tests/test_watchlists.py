import asyncio

from tastytrade.models.watchlists import WatchlistGroup
from tastytrade.tastyworks_api import tasty_session


class TestWatchlists(object):
    """Test Watchlists

    Class to test watchlist groups and watchlists.

    Args:
        username (string): Tastyworks username
        password (string): Tastyworks password
    """

    def __init__(self, username: str, password: str, public: bool = True):
        self.session = tasty_session.create_new_session(
            username, password
        )
        self.watchlists = asyncio.run(
            WatchlistGroup.get_watchlists(self.session, public=public)  # NOQA: E501
        )
