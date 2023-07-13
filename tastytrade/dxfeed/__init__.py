from enum import Enum

from .candle import Candle
from .event import Event, EventType
from .greeks import Greeks
from .profile import Profile
from .quote import Quote
from .summary import Summary
from .theoprice import TheoPrice
from .timeandsale import TimeAndSale
from .trade import Trade
from .underlying import Underlying

__all__ = [
    'Candle',
    'Event',
    'EventType',
    'Greeks',
    'Profile',
    'Quote',
    'Summary',
    'TheoPrice',
    'TimeAndSale',
    'Trade',
    'Underlying'
]


class Channel(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the channels for the quote
    streamer.
    """
    DATA = '/service/data'
    HANDSHAKE = '/meta/handshake'
    HEARTBEAT = '/meta/connect'
    SUBSCRIPTION = '/service/sub'
    TIME_SERIES = '/service/timeSeriesData'
