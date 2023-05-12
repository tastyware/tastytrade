from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

import aiohttp

from tastytrade import logger
from tastytrade.dxfeed.greeks import Greeks
from tastytrade.session import Session


class OptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of options and their abbreviations in the API.
    """
    #: a call option
    CALL = 'C'
    #: a put option
    PUT = 'P'


class UnderlyingType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of option underlyings and their abbreviations in the API.
    """
    #: an equity option
    EQUITY = 'Equity'
    #: an ETF option
    ETF = 'ETF'
    #: a futures option
    FUTURES = 'Futures'


@dataclass
class Option:
    """
    Container class for an option object in the API.
    """
    #: the underlying symbol
    ticker: str
    #: date of expiration
    expiry: date
    #: option strike
    strike: Decimal
    #: option type, either call or put
    option_type: OptionType
    #: underlying type, either equity, ETF or future
    underlying_type: UnderlyingType
    #: greeks for the option
    greeks: Optional[Greeks] = None
    #: number of contracts (for portfolio or orders)
    quantity: int = 1
    #: option symbol formatted to OCC standard
    symbol_occ: Optional[str] = None
    #: option symbol formatted to dxfeed standard
    symbol_dxf: Optional[str] = None

    def __post_init__(self):
        self.symbol_occ = self._get_occ2010_symbol()
        self.symbol_dxf = self._get_dxfeed_symbol()

    def _get_underlying_type_string(self, underlying_type: UnderlyingType):
        if underlying_type == UnderlyingType.EQUITY:
            return 'Equity Option'

    def _get_occ2010_symbol(self):
        strike_int, strike_dec = divmod(self.strike, 1)
        strike_int = int(round(strike_int, 5))
        strike_dec = int(round(strike_dec, 3) * 1000)

        res = '{ticker}{exp_date}{type}{strike_int}{strike_dec}'.format(
            ticker=self.ticker[0:6].ljust(6),
            exp_date=self.expiry.strftime('%y%m%d'),
            type=self.option_type.value,
            strike_int=str(strike_int).zfill(5),
            strike_dec=str(strike_dec).zfill(3)
        )
        return res

    def _get_dxfeed_symbol(self):
        if self.strike % 1 == 0:
            strike_str = '{0:.0f}'.format(self.strike)
        else:
            strike_str = '{0:.2f}'.format(self.strike)
            if strike_str[-1] == '0':
                strike_str = strike_str[:-1]

        res = '.{ticker}{exp_date}{type}{strike}'.format(
            ticker=self.ticker,
            exp_date=self.expiry.strftime('%y%m%d'),
            type=self.option_type.value,
            strike=strike_str
        )
        return res

    def _to_tasty_json(self):
        res = {
            'instrument-type': f'{self.underlying_type.value} Option',
            'symbol': self._get_occ2010_symbol(),
            'quantity': self.quantity
        }
        return res


class OptionChain:
    """
    A collection of call and put options, usually with the same expiration date.
    Provides filter methods based on type, strike price, expiry, etc.

    Example::

        session = Session('username', 'password')
        underlying = Underlying('SPY')
        chain = await get_option_chain(session, underlying, date(2022, 10, 21))

    """

    def __init__(self, options: list[Option]):
        #: list of all options in the chain
        self.options: list[Option] = options

    def _get_filter_strategy(self, key, unique=True):
        values = [getattr(option, key) for option in self.options]
        if not any(values):
            raise Exception(f'No values found for specified key: {key}')

        values = list(set(values)) if unique else list(values)
        return sorted(values)

    def get_all_strikes(self) -> list[Decimal]:
        """
        Get all available strikes in the chain.

        :return: list of available strikes
        """
        return self._get_filter_strategy('strike')

    def get_all_expirations(self) -> list[date]:
        """
        Get all available expirations in the chain. Usually would just be one.

        :return: list of dates present
        """
        return self._get_filter_strategy('expiry')


async def get_option_chain(session: Session, underlying: str, expiration: date = None) -> OptionChain:
    """
    Finds the option chain data for the given underlying and date.

    :param session: active user session to use
    :param underlying: underlying to fetch options for
    :expiration: date to fetch options for

    :return: :class:`OptionChain` object with retrieved data
    """
    logger.debug('Getting options chain for ticker: %s', underlying)
    data = await _get_tasty_option_chain_data(session, underlying)
    res = []

    for exp in data['expirations']:
        exp_date = datetime.strptime(exp['expiration-date'], '%Y-%m-%d').date()

        if expiration and expiration != exp_date:
            continue

        for strike in exp['strikes']:
            strike_val = Decimal(strike['strike-price'])
            for option_types in OptionType:
                new_option = Option(
                    ticker=underlying,
                    expiry=exp_date,
                    strike=strike_val,
                    option_type=option_types,
                    underlying_type=UnderlyingType.EQUITY
                )
                res.append(new_option)
    return OptionChain(res)


async def _get_tasty_option_chain_data(session, underlying) -> dict:
    async with aiohttp.request(
            'GET',
            f'{session.base_url}/option-chains/{underlying}/nested',
            headers=session.headers) as response:

        if response.status != 200:
            raise Exception(f'Could not find option chain for symbol {underlying}')
        resp = await response.json()

        # NOTE: Have not seen an example with more than 1 item. No idea what that would be.
        return resp['data']['items'][0]
