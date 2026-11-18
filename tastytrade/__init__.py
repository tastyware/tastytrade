import logging

API_URL = "https://api.tastyworks.com"
API_VERSION = "20251101"
#: Version sent on order endpoints. Order endpoints stop accepting versions before
#: 20261012 on or after 2027-04-12; other endpoints keep ``API_VERSION``.
ORDER_API_VERSION = "20261012"
CERT_URL = "https://api.cert.tastyworks.com"
PAPER_URL = "https://tastyware.dev/api"
VERSION = "13.2.3"

__version__ = VERSION
version_str: str = f"tastyware/tastytrade:v{VERSION}"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ruff: noqa: E402

from .account import Account
from .session import Session
from .streamer import AlertStreamer, DXLinkStreamer

__all__ = ["Account", "AlertStreamer", "DXLinkStreamer", "Session"]
