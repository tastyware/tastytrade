from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import re
from typing import Optional

import aiohttp

from tastytrade import API_URL, log
from tastytrade.option import OptionType
from tastytrade.session import Session


@dataclass
class Futures:
    pass


@dataclass
class FuturesOption:
    """
    Container class for an option object in the API.
    This is agnostic to long/short or quantities, because
    technically those are only pertinent to orders.
    """
    #: the underlying symbol
    underlying: str
    #: date of expiration
    expiry: date
    #: option strike
    strike: Decimal
    #: option type, either call or put
    option_type: OptionType
    #: option symbol formatted to OCC standard
    symbol_occ: Optional[str] = None
    #: option symbol formatted to dxfeed standard
    symbol_dxf: Optional[str] = None

    def __post_init__(self):
        self.symbol_occ = self._get_occ2010_symbol()
        self.symbol_dxf = self._get_dxfeed_symbol()

    @classmethod
    def from_occ2010(cls, symbol: str) -> 'Option':
        """
        Creates an option given a symbol in the OCC 2010 format.
        
        :param symbol: the symbol in OCC format
        
        :return: an :class:`~tastytrade.option.Option` object
        """
        return Option(
            underlying=symbol[:6].strip(),
            expiry=datetime.strptime(symbol[6:12], '%y%m%d'),
            strike=int(symbol[13:18]) + int(symbol[18:]) / 1000.0,
            option_type=OptionType(symbol[12])
        )
    
    @classmethod
    def from_dxfeed(cls, symbol: str) -> 'Option':
        """
        Creates an option given a symbol in the dxfeed format.
        
        :param symbol: the symbol in dxfeed format
        
        :return: an :class:`~tastytrade.option.Option` object
        """
        match = re.split(r'([A-Z]+)|([\d\.]+)', symbol[1:])  # remove leading '.'
        match[:] = [x for x in match if x]  # remove Nones and empty strings
        return Option(
            underlying=match[0],
            expiry=datetime.strptime(match[1], '%y%m%d'),
            strike=Decimal(match[3]),
            option_type=OptionType(match[2])
        )

    def _get_occ2010_symbol(self):
        strike_int, strike_dec = divmod(self.strike, 1)
        strike_int = int(round(strike_int, 5))
        strike_dec = int(round(strike_dec, 3) * 1000)

        return '{underlying}{exp_date}{option_type}{strike_int}{strike_dec}'.format(
            underlying=self.underlying[0:6].ljust(6),
            exp_date=self.expiry.strftime('%y%m%d'),
            option_type=self.option_type.value,
            strike_int=str(strike_int).zfill(5),
            strike_dec=str(strike_dec).zfill(3)
        )

    def _get_dxfeed_symbol(self):
        if self.strike % 1 == 0:  # a whole number
            strike_str = '{0:.0f}'.format(self.strike)
        else:
            strike_str = '{0:.2f}'.format(self.strike)
            if strike_str[-1] == '0':
                strike_str = strike_str[:-1]

        return '.{underlying}{exp_date}{option_type}{strike}'.format(
            underlying=self.underlying,
            exp_date=self.expiry.strftime('%y%m%d'),
            option_type=self.option_type.value,
            strike=strike_str
        )

    def _to_tasty_json(self):
        return {
            'instrument-type': 'Equity Option',  # apparently this applies to ETFs as well
            'symbol': self.symbol_occ
        }


class FuturesOptionChain:
    """
    Object containing all available strikes for all expirations for a specific symbol.
    Provides easy access to a list of expirations or all strikes for a given expiration.

    Example::

        session = Session('username', 'password')
        chain = await OptionChain.fetch(session, 'SPY')

    """
    def __init__(self, chains: dict[date, list[Option]]):
        self.all_chains = chains

    def get_expirations(self) -> list[date]:
        """
        Get all available expirations in the chain.

        :return: list of dates present
        """
        return list(self.all_chains.keys())
    
    def get_chain_at(self, expiration: date) -> list[Option]:
        """
        Get all strikes at the given date.
        
        :param expiration: the desired date

        :return: list of strikes at given date
        """
        return self.all_chains[expiration]

    @classmethod
    async def fetch(cls, session: Session, underlying: str) -> 'OptionChain':
        """
        Finds the option chain data for the given underlying and date.

        :param session: active user session to use
        :param underlying: underlying to fetch options for
        :param expiration: date to fetch options for; if not provided, all dates will be fetched.

        :return: :class:`~tastytrade.option.OptionChain` object with retrieved data
        """
        log.debug('Getting options chain for ticker: %s', underlying)
        # fetch chains for every date
        async with aiohttp.request(
            'GET',
            f'{API_URL}/futures-option-chains/{underlying}/nested',
            headers=session.get_request_headers()
        ) as response:
            if response.status // 100 != 2:
                raise Exception(f'Could not find option chain for symbol {underlying}')

            resp = await response.json()
            all_dates = resp['data']['items'][0]
        
        res = {}
        for exp in all_dates['expirations']:
            exp_date = datetime.strptime(exp['expiration-date'], '%Y-%m-%d').date()
            res[exp_date] = []

            for strike in exp['strikes']:
                strike_val = Decimal(strike['strike-price'])
                for option_type in OptionType:
                    new_option = Option(
                        underlying=underlying,
                        expiry=exp_date,
                        strike=strike_val,
                        option_type=option_type
                    )
                    res[exp_date].append(new_option)
        return cls(res)