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
TickSizes = TypedDict('TickSizes', {
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
    destination_venue_symbols: list[dict[str, Any]]
    streamer_symbol: Optional[str] = None

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'Cryptocurrency':
        """
        Creates a :class:`Cryptocurrency` object from the Tastytrade 'Cryptocurrency' object in JSON format.
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
            params=params,
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
    tick_sizes: Optional[list[TickSizes]] = None
    option_tick_sizes: Optional[list[TickSizes]] = None

    @classmethod
    def from_dict(cls, json: dict[str, Any]) -> 'Equity':
        """
        Creates a :class:`Equity` object from the Tastytrade 'Equity' object in JSON format.
        """
        snake_json = snakeify(json)
        return cls(**snake_json)

    @classmethod
    def get_active_equities(
        cls,
        session: Session,
        per_page: int = 1000,
        page_offset: int = 0,
        lendability: Optional[str] = None,
    ) -> list['Equity']:
        url = f'{session.base_url}/instruments/equities/active'
        equities = []
        while True:
            params = {
                'per-page': per_page,
                'page-offset': page_offset,
                'lendability': lendability,
            }
            response = requests.get(url, headers=session.headers, params=params)
            validate_response(response)
            response_data = response.json()
            equities.extend([cls.from_dict(entry) for entry in response_data['data']['items']])
            total_items = response_data['pagination']['total-items']
            if page_offset * per_page >= total_items:
                break
            else:
                page_offset += 1

        return equities

    @classmethod
    def get_equities(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        lendability: Optional[str] = None,
        is_index: Optional[bool] = None,
        is_etf: Optional[bool] = None,
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
            'is-etf': is_etf,
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
            f'{session.base_url}/instruments/equities/{symbol}', headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return cls.from_dict(data)


@dataclass
class EquityOption:
    symbol: str
    instrument_type: str
    active: bool
    listed_market: str
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
    halted_at: str
    stops_trading_at: str
    market_time_instrument_collection: str
    days_to_expiration: int
    expires_at: str
    is_closing_only: bool
    old_security_number: str
    streamer_symbol: str


@dataclass
class Future:
    symbol: str
    product_code: str
    contract_size: float
    tick_size: float
    notional_multiplier: float
    main_fraction: float
    sub_fraction: float
    display_factor: float
    last_trade_date: date
    expiration_date: date
    closing_only_date: date
    active: bool
    active_month: bool
    next_active_month: bool
    is_closing_only: bool
    first_notice_date: date
    stops_trading_at: datetime
    expires_at: datetime
    product_group: str
    exchange: str
    roll_target_symbol: str
    streamer_exchange_code: str
    streamer_symbol: str
    back_month_first_calendar_symbol: bool
    is_tradeable: bool
    true_underlying_symbol: str
    future_etf_equivalent: dict[str, Any]
    future_product: 'FutureProduct'
    tick_sizes: dict[str, Any]
    option_tick_sizes: dict[str, Any]
    spread_tick_sizes: dict[str, Any]


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
    base_tick: int
    sub_tick: int
    streamer_exchange_code: str
    small_notional: bool
    back_month_first_calendar_symbol: bool
    first_notice: bool
    cash_settled: bool
    contract_limit: int
    security_group: str
    product_subtype: str
    true_underlying_code: str
    market_sector: str


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
    future_option_product: 'FutureOptionProduct'


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
    product_subtype: str
    market_sector: str


@dataclass
class Warrant:
    symbol: str
    instrument_type: str
    cusip: str
    listed_market: str
    description: str
    is_closing_only: bool
    active: bool
