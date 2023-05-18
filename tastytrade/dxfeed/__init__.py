from enum import StrEnum


class Channel(StrEnum):
    """
    This is an :class:`~enum.Enum` that contains the channels for the quote streamer.
    """
    CANDLE = '/service/timeSeriesData'
    DATA = '/service/data'
    HANDSHAKE = '/meta/handshake'
    HEARTBEAT = '/meta/connect'
    SUBSCRIPTION = '/service/sub'
