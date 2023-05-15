from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

import requests

from tastytrade.session import Session
from tastytrade.utils import validate_response


@dataclass
class DestinationVenueSymbol:
    id: int
    symbol: str
    destination_venue: str
    routable: bool
    max_quantity_precision: Optional[int] = None
    max_price_precision: Optional[int] = None


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
    streamer_symbol: str
    destination_venue_symbols: list[DestinationVenueSymbol]

    @classmethod
    def get_cryptocurrencies(
        self, session: Session, symbols: list[str] = None
    ) -> list['Cryptocurrency']:
        url = f'{session.base_url}/instruments/cryptocurrencies'
        params = None
        if symbols:
            params = {'symbol[]': symbols}

        response = requests.get(url, headers=session.headers, params=params)
        validate_response(response)

        data = response.json()['data']['items']
        cryptocurrencies = []
        for crypto in data:
            crypto = {
                k.replace('-', '_'): v for k, v in data.items()
            }  # replace hyphens with underscores in keys
            destination_venue_symbols = [
                DestinationVenueSymbol(
                    **{k.replace('-', '_'): v for k, v in dvs.items()}
                )
                for dvs in crypto.pop('destination_venue_symbols')
            ]
            cryptocurrencies.append(
                Cryptocurrency(destination_venue_symbols=destination_venue_symbols, **crypto)
            )
        return cryptocurrencies


@dataclass
class Equity:
    symbol: str
    instrument_type: str
    short_description: str
    is_index: bool
    listed_market: str
    description: str
    lendability: str
    borrow_rate: float
    halted_at: str
    stops_trading_at: str
    market_time_instrument_collection: str
    is_closing_only: bool
    is_options_closing_only: bool
    active: bool
    is_fractional_quantity_eligible: bool
    is_illiquid: bool
    is_etf: bool
    streamer_symbol: str
    tick_sizes: dict[str, Any]
    option_tick_sizes: dict[str, Any]


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
