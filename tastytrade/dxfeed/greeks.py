from dataclasses import dataclass
from typing import Any

N_FIELDS = 13


@dataclass
class Greeks:
    #: options symbol in dxfeed format
    eventSymbol: str
    eventTime: int
    eventFlags: int
    index: int
    time: int
    sequence: int
    #: last traded price of the option
    price: float
    #: implied volatility (IV) computed from price
    volatility: float
    #: delta computed from price
    delta: float
    #: gamma computed from price
    gamma: float
    #: theta computed from price
    theta: float
    #: rho computed from price
    rho: float
    #: vega computed from price
    vega: float

    @classmethod
    def from_stream(cls, data: list[Any]) -> list['Greeks']:
        """
        Takes a list of raw trade data fetched by :class:`~tastyworks.streamer.DataStreamer`
        and returns a list of :class:`~tastyworks.dxfeed.greeks.Greeks` objects.

        :param data: list of raw quote data from streamer

        :return: list of :class:`~tastyworks.dxfeed.greeks.Greeks` objects from data
        """
        greeks = []
        multiples = len(data) / N_FIELDS
        if not multiples.is_integer():
            raise Exception('Mapper data input values are not an integer multiple of the key size')
        for i in range(int(multiples)):
            offset = i * N_FIELDS
            local_values = data[offset:(i + 1) * N_FIELDS]
            greeks.append(Greeks(*local_values))
        return greeks