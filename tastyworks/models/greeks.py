from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Greeks(object):
    symbol: str
    index: str
    datetime: datetime
    price: Decimal
    volatility: Decimal
    delta: Decimal
    gamma: Decimal
    theta: Decimal
    rho: Decimal
    vega: Decimal

    @classmethod
    def from_streamer_dict(cls, input_dict: dict):
        """
        imports the Greeks data from a dictionary pulled from subscribed streamer data
            sub_greeks = {"Greeks": [".SPY210419P410"]}
            await streamer.add_data_sub(sub_greeks)

        Args:
            input_dict (dict): dictionary from the streamer containing the greeks data for one options symbol

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
