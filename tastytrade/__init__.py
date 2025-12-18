import logging

API_URL = "https://api.tastyworks.com"
API_VERSION = "20251101"
CERT_URL = "https://api.cert.tastyworks.com"
VERSION = "11.1.0"

__version__ = VERSION
version_str: str = f"tastyware/tastytrade:v{VERSION}"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ruff: noqa: E402

from .account import Account
from .session import Session
from .streamer import AlertStreamer, DXLinkStreamer

__all__ = ["Account", "AlertStreamer", "DXLinkStreamer", "Session"]
