from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Greeks(object):
    symbol: str = None
    index: str = None
    datetime: datetime = None
    price: Decimal = None
    volatility: Decimal = None
    delta: Decimal = None
    gamma: Decimal = None
    theta: Decimal = None
    rho: Decimal = None
    vega: Decimal = None

    def from_streamer_dict(self, input_dict: dict):
        """
        imports the Greeks data from a dictionary pulled from subscribed streamer data
            sub_greeks = {"Greeks": [".SPY210419P410"]}
            await streamer.add_data_sub(sub_greeks)

        Args:
            input_dict (dict): dictionary from the streamer containing the greeks data for one options symbol

        """
        self.symbol = input_dict.get('eventSymbol')
        self.index = input_dict.get('index')
        self.datetime = datetime.fromtimestamp(input_dict.get('time') / 1000.0)  # timestamp comes in ms
        self.price = Decimal(str(input_dict.get('price')))
        self.volatility = Decimal(str(input_dict.get('volatility')))
        self.delta = Decimal(str(input_dict.get('delta')))
        self.gamma = Decimal(str(input_dict.get('gamma')))
        self.theta = Decimal(str(input_dict.get('theta')))
        self.rho = Decimal(str(input_dict.get('rho')))
        self.vega = Decimal(str(input_dict.get('vega')))

        return self
