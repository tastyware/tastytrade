import logging

API_URL = 'https://api.tastyworks.com'
CERT_URL = 'https://api.cert.tastyworks.com'
VERSION = '7.5'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .account import Account  # noqa: E402
from .search import symbol_search  # noqa: E402
from .session import CertificationSession, ProductionSession  # noqa: E402
from .streamer import AlertStreamer, DXLinkStreamer  # noqa: E402
from .watchlists import PairsWatchlist, Watchlist  # noqa: E402

__all__ = [
    'Account',
    'AlertStreamer',
    'CertificationSession',
    'DXLinkStreamer',
    'PairsWatchlist',
    'ProductionSession',
    'Watchlist',
    'symbol_search'
]
