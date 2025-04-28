import logging

API_URL = "https://api.tastyworks.com"
BACKTEST_URL = "https://backtester.vast.tastyworks.com"
CERT_URL = "https://api.cert.tastyworks.com"
VAST_URL = "https://vast.tastyworks.com"
VERSION = "10.1.0"

__version__ = VERSION
version_str = f"tastyware/tastytrade:v{VERSION}"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ruff: noqa: E402

from .account import Account
from .session import Session
from .streamer import AlertStreamer, DXLinkStreamer

__all__ = [
    "Account",
    "AlertStreamer",
    "DXLinkStreamer",
    "Session",
]
