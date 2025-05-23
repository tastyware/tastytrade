import logging

API_URL = "https://api.tastyworks.com"
BACKTEST_URL = "https://backtester.vast.tastyworks.com"
CERT_URL = "https://api.cert.tastyworks.com"
# SANDBOX_URL = "https://api.tastyware.dev"
SANDBOX_URL = "http://0.0.0.0:8000"
VAST_URL = "https://vast.tastyworks.com"
VERSION = "10.2.1"

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
