from dataclasses import dataclass
from typing import Any

N_FIELDS = 12


@dataclass
class Quote:
    #: underlying symbol
    eventSymbol: str
    eventTime: int
    sequence: int
    timeNanoPart: int
    #: time at which bid was fetched
    bidTime: int
    #: exchange from which bid was sourced
    bidExchangeCode: str
    #: bid value
    bidPrice: float
    #: size of bid offer
    bidSize: float
    #: time at which ask was fetched
    askTime: int
    #: exchange from which ask was sourced
    askExchangeCode: str
    #: ask value
    askPrice: float
    #: size of ask offer
    askSize: float
    
    @classmethod
    def from_stream(cls, data: list[Any]) -> list['Quote']:
        """
        Takes a list of raw trade data fetched by :class:`~tastyworks.streamer.DataStreamer`
        and returns a list of :class:`~tastyworks.dxfeed.quote.Quote` objects.

        :param data: list of raw quote data from streamer

        :return: list of :class:`~tastyworks.dxfeed.quote.Quote` objects from data
        """
        quotes = []
        multiples = len(data) / N_FIELDS
        if not multiples.is_integer():
            raise Exception('Mapper data input values are not an integer multiple of the key size')
        for i in range(int(multiples)):
            offset = i * N_FIELDS
            local_values = data[offset:(i + 1) * N_FIELDS]
            quotes.append(Quote(*local_values))
        return quotes