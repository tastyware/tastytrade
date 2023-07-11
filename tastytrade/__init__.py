import logging

API_URL = 'https://api.tastyworks.com'
CERT_URL = 'https://api.cert.tastyworks.com'
VERSION = '5.7'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .account import *
from .instruments import *
from .metrics import *
from .search import *
from .streamer import *
