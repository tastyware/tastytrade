from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional, TypedDict

import requests

from tastytrade.session import Session
from tastytrade.utils import snakeify, validate_response

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
TickSize = TypedDict('TickSize', {
    'value': str,
    'threshold': str,
    'symbol': str
}, total=False)


@dataclass
class Cryptocurrency:
    id: int
    symbol: str
    instrument_type: str
    short_description: str
    description: str
    is_closing_only: bool
    active: bool
    tick_size: float
    destination_venue_symbols: list[DestinationVenueSymbol]
    streamer_symbol: Optional[str] = None

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'Cryptocurrency':
        """
        Creates a :class:`Cryptocurrency` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

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
        cryptocurrencies = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


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
    borrow_rate: Optional[float] = None
    cusip: Optional[str] = None
    short_description: Optional[str] = None
    halted_at: Optional[datetime] = None
    stops_trading_at: Optional[datetime] = None
    is_fractional_quantity_eligible: Optional[bool] = None
    tick_sizes: Optional[list[TickSize]] = None
    option_tick_sizes: Optional[list[TickSize]] = None

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'Equity':
        """
        Creates a :class:`Equity` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

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
            equities.extend([cls.from_dict(entry) for entry in json['data']['items']])

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
        equities = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


@dataclass
class EquityOption:
    symbol: str
    instrument_type: str
    active: bool
    strike_price: float
    root_symbol: str
    underlying_symbol: str
    expiration_date: date
    exercise_style: str
    shares_per_contract: int
    option_type: str
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

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'EquityOption':
        """
        Creates a :class:`EquityOption` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

    @classmethod
    def get_options(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        active: Optional[bool] = None,
        with_expired: Optional[bool] = None
    ) -> list['EquityOption']:
        """
        Returns a list of :class:`EquityOption` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the OCC symbols to get the options for.
        :param active: whether the options are active.
        :param with_expired: whether to include expired options.

        :return: a list of :class:`EquityOption` objects.
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
        equities = [cls.from_dict(entry) for entry in data]

        return equities

    @classmethod
    def get_option(
        cls,
        session: Session,
        symbol: str,
        active: Optional[bool] = None
    ) -> 'EquityOption':
        """
        Returns a :class:`EquityOption` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, OCC format

        :return: a :class:`EquityOption` object.
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

        return cls.from_dict(data)


@dataclass
class Future:
    symbol: str
    product_code: str
    tick_size: float
    notional_multiplier: float
    display_factor: float
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
    contract_size: Optional[float] = None
    main_fraction: Optional[float] = None
    sub_fraction: Optional[float] = None
    first_notice_date: Optional[date] = None
    roll_target_symbol: Optional[str] = None
    true_underlying_symbol: Optional[str] = None
    future_etf_equivalent: Optional[dict[str, Any]] = None
    tick_sizes: Optional[list[TickSize]] = None
    option_tick_sizes: Optional[list[TickSize]] = None
    spread_tick_sizes: Optional[list[TickSize]] = None

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'Future':
        """
        Creates a :class:`Equity` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

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
        futures = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


@dataclass
class FutureProduct:
    root_symbol: str
    code: str
    description: str
    exchange: str
    product_type: str
    listed_months: str
    active_months: str
    notional_multiplier: float
    tick_size: float
    display_factor: float
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

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'FutureProduct':
        """
        Creates a :class:`FutureProduct` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

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
        future_products = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


@dataclass
class FutureOption:
    symbol: str
    underlying_symbol: str
    product_code: str
    expiration_date: date
    root_symbol: str
    option_root_symbol: str
    strike_price: float
    exchange: str
    streamer_symbol: str
    option_type: str
    exercise_style: str
    is_vanilla: bool
    is_primary_deliverable: bool
    future_price_ratio: float
    multiplier: float
    underlying_count: float
    is_confirmed: bool
    notional_value: float
    display_factor: float
    settlement_type: str
    strike_factor: float
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

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'FutureOption':
        """
        Creates a :class:`FutureOption` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

    @classmethod
    def get_future_options(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        root_symbol: Optional[str] = None,
        expiration_date: Optional[date] = None,
        option_type: Optional[str] = None,
        strike_price: Optional[float] = None
    ) -> list['FutureOption']:
        """
        Returns a list of :class:`FutureOption` objects from the given symbols.

        NOTE: As far as I can tell, all of the parameters are bugged except for `symbols`.

        :param session: the session to use for the request.
        :param symbols: the Tastytrade symbols to filter by.
        :param root_symbol: the root symbol to get the future options for, e.g. 'EW3', 'SO'
        :param expiration_date: the expiration date for the future options.
        :param option_type: the option type to filter by, 'C' or 'P'
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
        future_options = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


@dataclass
class FutureOptionProduct:
    root_symbol: str
    cash_settled: bool
    code: str
    display_factor: float
    exchange: str
    product_type: str
    expiration_type: str
    settlement_delay_days: int
    market_sector: str
    clearing_code: str
    clearing_exchange_code: str
    clearing_price_multiplier: float
    is_rollover: bool
    future_product: 'FutureProduct'
    product_subtype: Optional[str] = None
    legacy_code: Optional[str] = None
    clearport_code: Optional[str] = None

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'FutureOptionProduct':
        """
        Creates a :class:`FutureOptionProduct` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

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
        future_option_products = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


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
    def from_dict(cls, json: dict[str, Any]) -> 'Warrant':
        """
        Creates a :class:`Warrant` object from the Tastytrade object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

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
        futures = [cls.from_dict(entry) for entry in data]

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

        return cls.from_dict(data)


def get_quantity_decimal_precisions(session: Session) -> list[QuantityDecimalPrecision]:
    response = requests.get(
        f'{session.base_url}/instruments/quantity-decimal-precisions',
        headers=session.headers
    )
    validate_response(response)

    return response.json()['data']['items']
