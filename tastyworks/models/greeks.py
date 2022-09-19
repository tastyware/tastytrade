from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Greeks(object):
    """
    Container class for options greeks for a specific option.
    """
    #: underlying symbol
    symbol: str
    #: identifier
    index: str
    #: time that greeks were calculated in Unix time
    datetime: datetime
    #: option price
    price: Decimal
    #: calculated volatility
    volatility: Decimal
    #: calculated delta
    delta: Decimal
    #: calculated gamma
    gamma: Decimal
    #: calculated theta
    theta: Decimal
    #: calculated rho
    rho: Decimal
    #: calculated vega
    vega: Decimal

    @classmethod
    def from_streamer_dict(cls, input_dict: dict):
        """
        Imports the Greeks data from a dictionary pulled from subscribed streamer data.

        :param input_dict: dictionary containing streamer data

        :return: :class:`Greeks` instance with the attributes from the streamer

        Example::

            session = TastyAPISession(username, password)
            streamer = await DataStreamer.create(session)
            data = await streamer.stream(SubscriptionType.GREEKS, ['.SPY220919P482'])
            greeks = Greeks.from_streamer_dict(data[0])

        """
        self = Greeks(
            symbol=input_dict.get('eventSymbol', ''),
            index=input_dict.get('index', ''),
            datetime=datetime.fromtimestamp(input_dict.get('time', 0.0) / 1000.0),  # timestamp comes in ms
            price=Decimal(str(input_dict.get('price'))),
            volatility=Decimal(str(input_dict.get('volatility'))),
            delta=Decimal(str(input_dict.get('delta'))),
            gamma=Decimal(str(input_dict.get('gamma'))),
            theta=Decimal(str(input_dict.get('theta'))),
            rho=Decimal(str(input_dict.get('rho'))),
            vega=Decimal(str(input_dict.get('vega')))
        )
        return self
