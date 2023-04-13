from dataclasses import dataclass
from typing import Any

N_FIELDS = 14


@dataclass
class Trade:
    #: underlying symbol
    eventSymbol: str
    eventTime: int
    #: time at which the data is sent
    time: int
    timeNanoPart: int
    sequence: int
    #: code representing the exchange traded on
    exchangeCode: str
    #: a price quote, or the IV rank if the symbol ends in .IVR
    price: float
    #: day change in price
    change: float
    size: str
    dayId: int
    #: number of units traded today
    dayVolume: int
    dayTurnover: int
    tickDirection: str
    #: whether the symbol trades during extended hours
    extendedTradingHours: bool
        
    @classmethod
    def from_stream(cls, data: list[Any]) -> list['Trade']:
        """
        Takes a list of raw trade data fetched by :class:`~tastyworks.streamer.DataStreamer`
        and returns a list of :class:`~tastyworks.dxfeed.trade.Trade` objects.

        :param data: list of raw trade data from streamer

        :return: list of :class:`~tastyworks.dxfeed.trade.Trade` objects from data
        """
        trades = []
        multiples = len(data) / N_FIELDS
        if not multiples.is_integer():
            raise Exception('Mapper data input values are not an integer multiple of the key size')
        for i in range(int(multiples)):
            offset = i * N_FIELDS
            local_values = data[offset:(i + 1) * N_FIELDS]
            trades.append(Trade(*local_values))
        return trades