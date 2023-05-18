from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Optional, TypedDict

import requests

from tastytrade.session import Session
from tastytrade.utils import (datetime_from_tastydatetime, snakeify,
                              validate_response)

Deliverable = TypedDict('Deliverable', {
    'id': int,
    'root-symbol': str,
    'deliverable-type': str,
    'description': str,
    'amount': Decimal,
    'symbol': str,
    'instrument-type': str,
    'percent': str
}, total=False)
DestinationVenueSymbol = TypedDict('DestinationVenueSymbol', {
    'id': int,
    'symbol': str,
    'destination-venue': str,
    'routable': bool,
    'max-quantity-precision': int,
    'max-price-precision': int
}, total=False)
QuantityDecimalPrecision = TypedDict('QuantityDecimalPrecision', {
    'instrument-type': str,
    'symbol': str,
    'value': int,
    'minimum-increment-precision': int
}, total=False)
Strike = TypedDict('Strike', {
    'strike-price': Decimal,
    'call': str,
    'put': str
})
TickSize = TypedDict('TickSize', {
    'value': str,
    'threshold': str,
    'symbol': str
}, total=False)


class OptionType(StrEnum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of options and
    their abbreviations in the API.
    """
    #: a call option
    CALL = 'C'
    #: a put option
    PUT = 'P'


@dataclass
class Cryptocurrency:
    id: int
    symbol: str
    instrument_type: str
    short_description: str
    description: str
    is_closing_only: bool
    active: bool
    tick_size: Decimal
    destination_venue_symbols: list[DestinationVenueSymbol]
    streamer_symbol: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.tick_size, str):
            self.tick_size = Decimal(self.tick_size)

    @classmethod
    def get_cryptocurrencies(
        cls, session: Session, symbols: list[str] = []
    ) -> list['Cryptocurrency']:
        """
        Returns a list of :class:`Cryptocurrency` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the symbols to get the cryptocurrencies for.

        :return: a list of :class:`Cryptocurrency` objects.
        """
        params = {'symbol[]': symbols} if symbols else None
        response = requests.get(
            f'{session.base_url}/instruments/cryptocurrencies',
            headers=session.headers,
            params=params
        )
        validate_response(response)

        data = response.json()['data']['items']
        cryptocurrencies = [cls(**snakeify(entry)) for entry in data]

        return cryptocurrencies

    @classmethod
    def get_cryptocurrency(cls, session: Session, symbol: str) -> 'Cryptocurrency':
        """
        Returns a :class:`Cryptocurrency` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the cryptocurrency for.

        :return: a :class:`Cryptocurrency` object.
        """
        symbol = symbol.replace('/', '%2F')
        response = requests.get(
            f'{session.base_url}/instruments/cryptocurrencies/{symbol}',
            headers=session.headers,
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


@dataclass
class Equity:
    id: int
    symbol: str
    instrument_type: str
    is_index: bool
    listed_market: str
    description: str
    lendability: str
    market_time_instrument_collection: str
    is_closing_only: bool
    is_options_closing_only: bool
    active: bool
    is_illiquid: bool
    is_etf: bool
    streamer_symbol: str
    borrow_rate: Optional[Decimal] = None
    cusip: Optional[str] = None
    short_description: Optional[str] = None
    halted_at: Optional[datetime] = None
    stops_trading_at: Optional[datetime] = None
    is_fractional_quantity_eligible: Optional[bool] = None
    tick_sizes: Optional[list[TickSize]] = None
    option_tick_sizes: Optional[list[TickSize]] = None

    def __post_init__(self):
        if isinstance(self.borrow_rate, str):
            self.borrow_rate = Decimal(self.borrow_rate)
        if isinstance(self.halted_at, str):
            self.halted_at = datetime_from_tastydatetime(self.halted_at)
        if isinstance(self.stops_trading_at, str):
            self.stops_trading_at = datetime_from_tastydatetime(self.stops_trading_at)

    @classmethod
    def get_active_equities(
        cls,
        session: Session,
        per_page: int = 1000,
        page_offset: int = 0,
        lendability: Optional[str] = None
    ) -> list['Equity']:
        """
        Returns a list of actively traded :class:`Equity` objects.

        :param session: the session to use for the request.
        :param per_page: the number of equities to get per page.
        :param page_offset: the page offset to start at
        :param lendability: the lendability of the equities; 'Easy To Borrow', 'Locate Required', 'Preborrow'

        :return: a list of :class:`Equity` objects.
        """
        params: dict[str, Any] = {
            'per-page': per_page,
            'page-offset': page_offset,
            'lendability': lendability
        }

        # loop through pages and get all active equities
        equities = []
        while True:
            response = requests.get(
                f'{session.base_url}/instruments/equities/active',
                headers=session.headers,
                params=params
            )
            validate_response(response)

            json = response.json()
            equities.extend([cls(**snakeify(entry)) for entry in json['data']['items']])

            pagination = json['pagination']
            if pagination['page-offset'] >= pagination['total-pages'] - 1:
                break
            params['page-offset'] += 1  # type: ignore

        return equities

    @classmethod
    def get_equities(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        lendability: Optional[str] = None,
        is_index: Optional[bool] = None,
        is_etf: Optional[bool] = None
    ) -> list['Equity']:
        """
        Returns a list of :class:`Equity` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the symbols to get the equities for.
        :param lendability:
            the lendability of the equities; 'Easy To Borrow', 'Locate Required', 'Preborrow'
        :param is_index: whether the equities are indexes.
        :param is_etf: whether the equities are ETFs.

        :return: a list of :class:`Equity` objects.
        """
        params: dict[str, Any] = {
            'symbol[]': symbols,
            'lendability': lendability,
            'is-index': is_index,
            'is-etf': is_etf
        }
        response = requests.get(
            f'{session.base_url}/instruments/equities',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}
        )
        validate_response(response)

        data = response.json()['data']['items']
        equities = [cls(**snakeify(entry)) for entry in data]

        return equities

    @classmethod
    def get_equity(cls, session: Session, symbol: str) -> 'Equity':
        """
        Returns a :class:`Equity` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the equity for.

        :return: a :class:`Equity` object.
        """
        symbol = symbol.replace('/', '%2F')
        response = requests.get(
            f'{session.base_url}/instruments/equities/{symbol}',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


@dataclass
class Option:
    symbol: str
    instrument_type: str
    active: bool
    strike_price: Decimal
    root_symbol: str
    underlying_symbol: str
    expiration_date: date
    exercise_style: str
    shares_per_contract: int
    option_type: OptionType
    option_chain_type: str
    expiration_type: str
    settlement_type: str
    stops_trading_at: datetime
    market_time_instrument_collection: str
    days_to_expiration: int
    expires_at: datetime
    is_closing_only: bool
    listed_market: Optional[str] = None
    halted_at: Optional[datetime] = None
    old_security_number: Optional[str] = None
    streamer_symbol: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.strike_price, str):
            self.strike_price = Decimal(self.strike_price)
        if isinstance(self.expiration_date, str):
            self.expiration_date = date.fromisoformat(self.expiration_date)
        self.option_type = OptionType(self.option_type)
        if isinstance(self.stops_trading_at, str):
            self.stops_trading_at = datetime_from_tastydatetime(self.stops_trading_at)
        if isinstance(self.expires_at, str):
            self.expires_at = datetime_from_tastydatetime(self.expires_at)
        if isinstance(self.halted_at, str):
            self.halted_at = datetime_from_tastydatetime(self.halted_at)
        if not self.streamer_symbol:
            self._set_streamer_symbol()

    @classmethod
    def get_options(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        active: Optional[bool] = None,
        with_expired: Optional[bool] = None
    ) -> list['Option']:
        """
        Returns a list of :class:`Option` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the OCC symbols to get the options for.
        :param active: whether the options are active.
        :param with_expired: whether to include expired options.

        :return: a list of :class:`Option` objects.
        """
        params: dict[str, Any] = {
            'symbol[]': symbols,
            'active': active,
            'with-expired': with_expired
        }
        response = requests.get(
            f'{session.base_url}/instruments/equity-options',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}
        )
        validate_response(response)

        data = response.json()['data']['items']
        equities = [cls(**snakeify(entry)) for entry in data]

        return equities

    @classmethod
    def get_option(
        cls,
        session: Session,
        symbol: str,
        active: Optional[bool] = None
    ) -> 'Option':
        """
        Returns a :class:`Option` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, OCC format

        :return: a :class:`Option` object.
        """
        symbol = symbol.replace('/', '%2F')
        params = {'active': active} if active is not None else None
        response = requests.get(
            f'{session.base_url}/instruments/equity-options/{symbol}',
            headers=session.headers,
            params=params
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))

    def _set_streamer_symbol(self) -> None:
        if self.strike_price % 1 == 0:
            strike = '{0:.0f}'.format(self.strike_price)
        else:
            strike = '{0:.2f}'.format(self.strike_price)
            if strike[-1] == '0':
                strike = strike[:-1]

        self.streamer_symbol = \
            f".{self.underlying_symbol}{self.expiration_date.strftime('%y%m%d')}{self.option_type}{strike}"


@dataclass
class NestedOptionChainExpiration:
    expiration_type: str
    expiration_date: date
    days_to_expiration: int
    settlement_type: str
    strikes: list[Strike]

    def __post_init__(self):
        if isinstance(self.expiration_date, str):
            self.expiration_date = date.fromisoformat(self.expiration_date)


@dataclass
class NestedOptionChain:
    underlying_symbol: str
    root_symbol: str
    option_chain_type: str
    shares_per_contract: int
    tick_sizes: list[TickSize]
    deliverables: list[Deliverable]
    expirations: list[NestedOptionChainExpiration]

    def __post_init__(self):
        self.expirations = [NestedOptionChainExpiration(**snakeify(expiration)) for expiration in self.expirations]

    @classmethod
    def get_nested_option_chain(cls, session: Session, symbol: str) -> 'NestedOptionChain':
        """
        Gets the option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.

        :return: a :class:`NestedOptionChain` object.
        """
        symbol = symbol.replace('/', '%2F')
        response = requests.get(
            f'{session.base_url}/option-chains/{symbol}/nested',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']['items'][0]

        return cls(**snakeify(data))


@dataclass
class Future:
    symbol: str
    product_code: str
    tick_size: Decimal
    notional_multiplier: Decimal
    display_factor: Decimal
    last_trade_date: date
    expiration_date: date
    closing_only_date: date
    active: bool
    active_month: bool
    next_active_month: bool
    is_closing_only: bool
    stops_trading_at: datetime
    expires_at: datetime
    product_group: str
    exchange: str
    streamer_exchange_code: str
    streamer_symbol: str
    back_month_first_calendar_symbol: bool
    is_tradeable: bool
    future_product: 'FutureProduct'
    contract_size: Optional[Decimal] = None
    main_fraction: Optional[Decimal] = None
    sub_fraction: Optional[Decimal] = None
    first_notice_date: Optional[date] = None
    roll_target_symbol: Optional[str] = None
    true_underlying_symbol: Optional[str] = None
    future_etf_equivalent: Optional[dict[str, Any]] = None
    tick_sizes: Optional[list[TickSize]] = None
    option_tick_sizes: Optional[list[TickSize]] = None
    spread_tick_sizes: Optional[list[TickSize]] = None

    def __post_init__(self):
        if isinstance(self.tick_size, str):
            self.tick_size = Decimal(self.tick_size)
        if isinstance(self.notional_multiplier, str):
            self.notional_multiplier = Decimal(self.notional_multiplier)
        if isinstance(self.display_factor, str):
            self.display_factor = Decimal(self.display_factor)
        if isinstance(self.last_trade_date, str):
            self.last_trade_date = date.fromisoformat(self.last_trade_date)
        if isinstance(self.expiration_date, str):
            self.expiration_date = date.fromisoformat(self.expiration_date)
        if isinstance(self.closing_only_date, str):
            self.closing_only_date = date.fromisoformat(self.closing_only_date)
        if isinstance(self.stops_trading_at, str):
            self.stops_trading_at = datetime_from_tastydatetime(self.stops_trading_at)
        if isinstance(self.expires_at, str):
            self.expires_at = datetime_from_tastydatetime(self.expires_at)
        if not isinstance(self.future_product, FutureProduct):
            self.future_product = FutureProduct(**snakeify(self.future_product))
        if isinstance(self.contract_size, str):
            self.contract_size = Decimal(self.contract_size)
        if isinstance(self.main_fraction, str):
            self.main_fraction = Decimal(self.main_fraction)
        if isinstance(self.sub_fraction, str):
            self.sub_fraction = Decimal(self.sub_fraction)
        if isinstance(self.first_notice_date, str):
            self.first_notice_date = date.fromisoformat(self.first_notice_date)

    @classmethod
    def get_futures(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        product_codes: Optional[list[str]] = None
    ) -> list['Future']:
        """
        Returns a list of :class:`Future` objects from the given symbols or product codes.

        :param session: the session to use for the request.
        :param symbols:
            symbols of the futures, e.g. 'ESZ9'. Leading forward slash is not required.
        :param product_codes:
            the product codes of the futures, e.g. 'ES', '6A'. Ignored if symbols are provided.

        :return: a list of :class:`Future` objects.
        """
        params: dict[str, Any] = {
            'symbol[]': symbols,
            'product-code[]': product_codes
        }
        response = requests.get(
            f'{session.base_url}/instruments/futures',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}
        )
        validate_response(response)

        data = response.json()['data']['items']
        futures = [cls(**snakeify(entry)) for entry in data]

        return futures

    @classmethod
    def get_future(cls, session: Session, symbol: str) -> 'Future':
        """
        Returns a :class:`Future` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the future for.

        :return: a :class:`Future` object.
        """
        symbol = symbol.replace('/', '')
        response = requests.get(
            f'{session.base_url}/instruments/futures/{symbol}',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


@dataclass
class FutureProduct:
    root_symbol: str
    code: str
    description: str
    exchange: str
    product_type: str
    listed_months: str
    active_months: str
    notional_multiplier: Decimal
    tick_size: Decimal
    display_factor: Decimal
    streamer_exchange_code: str
    small_notional: bool
    back_month_first_calendar_symbol: bool
    first_notice: bool
    cash_settled: bool
    market_sector: str
    clearing_code: str
    clearing_exchange_code: str
    roll: dict[str, Any]
    base_tick: Optional[int] = None
    sub_tick: Optional[int] = None
    contract_limit: Optional[int] = None
    product_subtype: Optional[str] = None
    security_group: Optional[str] = None
    true_underlying_code: Optional[str] = None
    clearport_code: Optional[str] = None
    legacy_code: Optional[str] = None
    legacy_exchange_code: Optional[str] = None
    option_products: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if isinstance(self.notional_multiplier, str):
            self.notional_multiplier = Decimal(self.notional_multiplier)
        if isinstance(self.tick_size, str):
            self.tick_size = Decimal(self.tick_size)
        if isinstance(self.display_factor, str):
            self.display_factor = Decimal(self.display_factor)

    @classmethod
    def get_future_products(
        cls,
        session: Session
    ) -> list['FutureProduct']:
        """
        Returns a list of :class:`FutureProduct` objects available.

        :param session: the session to use for the request.

        :return: a list of :class:`FutureProduct` objects.
        """
        response = requests.get(
            f'{session.base_url}/instruments/future-products',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']['items']
        future_products = [cls(**snakeify(entry)) for entry in data]

        return future_products

    @classmethod
    def get_future_product(
        cls,
        session: Session,
        code: str,
        exchange: str = 'CME'
    ) -> 'FutureProduct':
        """
        Returns a :class:`FutureProduct` object from the given symbol.

        :param session: the session to use for the request.
        :param code: the product code, e.g. 'ES'
        :param exchange: the exchange to get the product from: 'CME', 'SMALLS', 'CFE', 'CBOED'

        :return: a :class:`FutureProduct` object.
        """
        code = code.replace('/', '')
        response = requests.get(
            f'{session.base_url}/instruments/future-products/{exchange}/{code}',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


@dataclass
class FutureOption:
    symbol: str
    underlying_symbol: str
    product_code: str
    expiration_date: date
    root_symbol: str
    option_root_symbol: str
    strike_price: Decimal
    exchange: str
    streamer_symbol: str
    option_type: OptionType
    exercise_style: str
    is_vanilla: bool
    is_primary_deliverable: bool
    future_price_ratio: Decimal
    multiplier: Decimal
    underlying_count: Decimal
    is_confirmed: bool
    notional_value: Decimal
    display_factor: Decimal
    settlement_type: str
    strike_factor: Decimal
    maturity_date: date
    is_exercisable_weekly: bool
    last_trade_time: str
    days_to_expiration: int
    is_closing_only: bool
    active: bool
    stops_trading_at: datetime
    expires_at: datetime
    exchange_symbol: str
    security_exchange: str
    sx_id: str
    future_option_product: 'FutureOptionProduct'

    def __post_init__(self):
        if isinstance(self.expiration_date, str):
            self.expiration_date = date.fromisoformat(self.expiration_date)
        if isinstance(self.strike_price, str):
            self.strike_price = Decimal(self.strike_price)
        self.option_type = OptionType(self.option_type)
        if isinstance(self.future_price_ratio, str):
            self.future_price_ratio = Decimal(self.future_price_ratio)
        if isinstance(self.multiplier, str):
            self.multiplier = Decimal(self.multiplier)
        if isinstance(self.underlying_count, str):
            self.underlying_count = Decimal(self.underlying_count)
        if isinstance(self.notional_value, str):
            self.notional_value = Decimal(self.notional_value)
        if isinstance(self.display_factor, str):
            self.display_factor = Decimal(self.display_factor)
        if isinstance(self.strike_factor, str):
            self.strike_factor = Decimal(self.strike_factor)
        if isinstance(self.maturity_date, str):
            self.maturity_date = date.fromisoformat(self.maturity_date)
        if isinstance(self.stops_trading_at, str):
            self.stops_trading_at = datetime_from_tastydatetime(self.stops_trading_at)
        if isinstance(self.expires_at, str):
            self.expires_at = datetime_from_tastydatetime(self.expires_at)
        if not isinstance(self.future_option_product, FutureOptionProduct):
            self.future_option_product = FutureOptionProduct(**snakeify(self.future_option_product))

    @classmethod
    def get_future_options(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        root_symbol: Optional[str] = None,
        expiration_date: Optional[date] = None,
        option_type: Optional[OptionType] = None,
        strike_price: Optional[Decimal] = None
    ) -> list['FutureOption']:
        """
        Returns a list of :class:`FutureOption` objects from the given symbols.

        NOTE: As far as I can tell, all of the parameters are bugged except for `symbols`.

        :param session: the session to use for the request.
        :param symbols: the Tastytrade symbols to filter by.
        :param root_symbol: the root symbol to get the future options for, e.g. 'EW3', 'SO'
        :param expiration_date: the expiration date for the future options.
        :param option_type: the option type to filter by.
        :param strike_price: the strike price to filter by.

        :return: a list of :class:`FutureOption` objects.
        """
        params: dict[str, Any] = {
            'symbol[]': symbols,
            'option-root-symbol': root_symbol,
            'expiration-date': expiration_date,
            'option-type': option_type,
            'strike-price': strike_price
        }
        response = requests.get(
            f'{session.base_url}/instruments/future-options',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}
        )
        validate_response(response)

        data = response.json()['data']['items']
        future_options = [cls(**snakeify(entry)) for entry in data]

        return future_options

    @classmethod
    def get_future_option(
        cls,
        session: Session,
        symbol: str
    ) -> 'FutureOption':
        """
        Returns a :class:`FutureOption` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, Tastytrade format

        :return: a :class:`FutureOption` object.
        """
        symbol = symbol.replace('/', '%2F').replace(' ', '%20')
        response = requests.get(
            f'{session.base_url}/instruments/future-options/{symbol}',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


@dataclass
class FutureOptionProduct:
    root_symbol: str
    cash_settled: bool
    code: str
    display_factor: Decimal
    exchange: str
    product_type: str
    expiration_type: str
    settlement_delay_days: int
    market_sector: str
    clearing_code: str
    clearing_exchange_code: str
    clearing_price_multiplier: Decimal
    is_rollover: bool
    future_product: Optional['FutureProduct'] = None
    product_subtype: Optional[str] = None
    legacy_code: Optional[str] = None
    clearport_code: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.display_factor, str):
            self.display_factor = Decimal(self.display_factor)
        if isinstance(self.clearing_price_multiplier, str):
            self.clearing_price_multiplier = Decimal(self.clearing_price_multiplier)
        if self.future_product is not None and not isinstance(self.future_product, FutureProduct):
            self.future_product = FutureProduct(**snakeify(self.future_product))

    @classmethod
    def get_future_option_products(
        cls,
        session: Session
    ) -> list['FutureOptionProduct']:
        """
        Returns a list of :class:`FutureOptionProduct` objects available.

        :param session: the session to use for the request.

        :return: a list of :class:`FutureOptionProduct` objects.
        """
        response = requests.get(
            f'{session.base_url}/instruments/future-option-products',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']['items']
        future_option_products = [cls(**snakeify(entry)) for entry in data]

        return future_option_products

    @classmethod
    def get_future_option_product(
        cls,
        session: Session,
        root_symbol: str,
        exchange: str = 'CME'
    ) -> 'FutureOptionProduct':
        """
        Returns a :class:`FutureOptionProduct` object from the given symbol.

        :param session: the session to use for the request.
        :param code: the root symbol of the future option
        :param exchange: the exchange to get the product from

        :return: a :class:`FutureOptionProduct` object.
        """
        root_symbol = root_symbol.replace('/', '')
        response = requests.get(
            f'{session.base_url}/instruments/future-option-products/{exchange}/{root_symbol}',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


@dataclass
class Warrant:
    symbol: str
    instrument_type: str
    listed_market: str
    description: str
    is_closing_only: bool
    active: bool
    cusip: Optional[str] = None

    @classmethod
    def get_warrants(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None
    ) -> list['Warrant']:
        """
        Returns a list of :class:`Warrant` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: symbols of the warrants, e.g. 'NKLAW'

        :return: a list of :class:`Warrant` objects.
        """
        params = {'symbol[]': symbols} if symbols is not None else {}
        response = requests.get(
            f'{session.base_url}/instruments/warrants',
            headers=session.headers,
            params=params
        )
        validate_response(response)

        data = response.json()['data']['items']
        futures = [cls(**snakeify(entry)) for entry in data]

        return futures

    @classmethod
    def get_warrant(cls, session: Session, symbol: str) -> 'Warrant':
        """
        Returns a :class:`Warrant` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the warrant for.

        :return: a :class:`Warrant` object.
        """
        response = requests.get(
            f'{session.base_url}/instruments/warrants/{symbol}',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))


def get_quantity_decimal_precisions(session: Session) -> list[QuantityDecimalPrecision]:
    response = requests.get(
        f'{session.base_url}/instruments/quantity-decimal-precisions',
        headers=session.headers
    )
    validate_response(response)

    return response.json()['data']['items']


def get_option_chain(session: Session, symbol: str) -> dict[date, list[Option]]:
    """
    Returns a mapping of expiration date to a list of :class:`Option` objects
    representing the options chain for the given symbol.

    :param session: the session to use for the request.
    :param symbol: the symbol to get the option chain for.

    :return: a dict mapping expiration date to a list of :class:`Option` objects.
    """
    symbol = symbol.replace('/', '%2F')
    response = requests.get(
        f'{session.base_url}/option-chains/{symbol}',
        headers=session.headers
    )
    validate_response(response)

    data = response.json()['data']['items']
    chain = {}
    for entry in data:
        option = Option(**snakeify(entry))
        if option.expiration_date not in chain:
            chain[option.expiration_date] = [option]
        else:
            chain[option.expiration_date].append(option)

    return chain


def get_future_option_chain(session: Session, symbol: str) -> dict[date, list[FutureOption]]:
    """
    Returns a mapping of expiration date to a list of :class:`FutureOption` objects
    representing the options chain for the given symbol.

    :param session: the session to use for the request.
    :param symbol: the symbol to get the option chain for.

    :return: a dict mapping expiration date to a list of :class:`FutureOption` objects.
    """
    symbol = symbol.replace('/', '%2F')
    response = requests.get(
        f'{session.base_url}/futures-option-chains/{symbol}',
        headers=session.headers
    )
    validate_response(response)

    data = response.json()['data']['items']
    chain = {}
    for entry in data:
        option = FutureOption(**snakeify(entry))
        if option.expiration_date not in chain:
            chain[option.expiration_date] = [option]
        else:
            chain[option.expiration_date].append(option)

    return chain
