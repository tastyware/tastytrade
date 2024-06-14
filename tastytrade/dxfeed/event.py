from enum import Enum
from typing import List

from pydantic import BaseModel, validator

from tastytrade.utils import TastytradeError


class EventType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid subscription types
    for the data streamer.

    Information on different types of events, their uses and their properties
    can be found at the `dxfeed Knowledge Base.
    <https://kb.dxfeed.com/en/data-model/dxfeed-api-market-events.html>`_.
    """

    CANDLE = 'Candle'
    GREEKS = 'Greeks'
    PROFILE = 'Profile'
    QUOTE = 'Quote'
    SUMMARY = 'Summary'
    THEO_PRICE = 'TheoPrice'
    TIME_AND_SALE = 'TimeAndSale'
    TRADE = 'Trade'
    UNDERLYING = 'Underlying'


class Event(BaseModel):
    @validator('*', pre=True)
    def change_nan_to_none(cls, v):
        if v == 'NaN' or v == 'Infinity' or v == '-Infinity':
            return None
        return v

    @classmethod
    def from_stream(cls, data: list) -> List['Event']:  # pragma: no cover
        """
        Makes a list of event objects from a list of raw trade data fetched by
        a :class:`~tastyworks.streamer.DXFeedStreamer`.

        :param data: list of raw quote data from streamer

        :return: list of event objects from data
        """
        objs = []
        size = len(cls.model_fields)
        multiples = len(data) / size
        if not multiples.is_integer():
            msg = 'Mapper data input values are not a multiple of the key size'
            raise TastytradeError(msg)
        keys = cls.model_fields.keys()
        for i in range(int(multiples)):
            offset = i * size
            local_values = data[offset:(i + 1) * size]
            event_dict = dict(zip(keys, local_values))
            objs.append(cls(**event_dict))
        return objs
