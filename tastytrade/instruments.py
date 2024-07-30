import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from tastytrade.order import InstrumentType, TradeableTastytradeJsonDataclass
from tastytrade.session import Session
from tastytrade.utils import TastytradeJsonDataclass, validate_response


class OptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of options
    and their abbreviations in the API.
    """
    CALL = 'C'
    PUT = 'P'


class FutureMonthCode(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid month codes for
    futures.

    This is really here for reference, as the API barely uses these codes.
    """
    JAN = 'F'
    FEB = 'G'
    MAR = 'H'
    APR = 'J'
    MAY = 'K'
    JUN = 'M'
    JUL = 'N'
    AUG = 'Q'
    SEP = 'U'
    OCT = 'V'
    NOV = 'X'
    DEC = 'Z'


class Deliverable(TastytradeJsonDataclass):
    """
    Dataclass representing the deliverable for an option.
    """
    id: int
    root_symbol: str
    deliverable_type: str
    description: str
    amount: Decimal
    percent: str
    symbol: Optional[str] = None
    instrument_type: Optional[InstrumentType] = None


class DestinationVenueSymbol(TastytradeJsonDataclass):
    """
    Dataclass representing a specific destination venue symbol for a
    cryptocurrency.
    """
    id: int
    symbol: str
    destination_venue: str
    routable: bool
    max_quantity_precision: Optional[int] = None
    max_price_precision: Optional[int] = None


class QuantityDecimalPrecision(TastytradeJsonDataclass):
    """
    Dataclass representing the decimal precision (number of places) for an
    instrument.
    """
    instrument_type: InstrumentType
    value: int
    minimum_increment_precision: int
    symbol: Optional[str] = None


class Strike(TastytradeJsonDataclass):
    """
    Dataclass representing a specific strike in an options chain, containing
    the symbols for the call and put options.
    """
    strike_price: Decimal
    call: str
    put: str
    call_streamer_symbol: str
    put_streamer_symbol: str


class TickSize(TastytradeJsonDataclass):
    """
    Dataclass representing the tick size for an instrument.
    """
    value: Decimal
    threshold: Optional[Decimal] = None
    symbol: Optional[str] = None


class NestedOptionChainExpiration(TastytradeJsonDataclass):
    """
    Dataclass representing an expiration in a nested options chain.
    """
    expiration_type: str
    expiration_date: date
    days_to_expiration: int
    settlement_type: str
    strikes: List[Strike]


class NestedFutureOptionChainExpiration(TastytradeJsonDataclass):
    """
    Dataclass representing an expiration in a nested future options chain.
    """
    root_symbol: str
    notional_value: Decimal
    underlying_symbol: str
    strike_factor: Decimal
    days_to_expiration: int
    option_root_symbol: str
    expiration_date: date
    expires_at: datetime
    asset: str
    expiration_type: str
    display_factor: Decimal
    option_contract_symbol: str
    stops_trading_at: datetime
    settlement_type: str
    strikes: List[Strike]
    tick_sizes: List[TickSize]


class NestedFutureOptionFuture(TastytradeJsonDataclass):
    """
    Dataclass representing an underlying future in a nested future options
    chain.
    """
    root_symbol: str
    days_to_expiration: int
    expiration_date: date
    expires_at: datetime
    next_active_month: bool
    symbol: str
    active_month: bool
    stops_trading_at: datetime
    maturity_date: Optional[date] = None


class FutureEtfEquivalent(TastytradeJsonDataclass):
    """
    Dataclass that represents the ETF equivalent for a future (aka, the number
    of shares of the ETF that are equivalent to one future, leverage-wise).
    """
    symbol: str
    share_quantity: int


class Roll(TastytradeJsonDataclass):
    """
    Dataclass representing a roll for a future.
    """
    name: str
    active_count: int
    cash_settled: bool
    business_days_offset: int
    first_notice: bool


class Cryptocurrency(TradeableTastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade cryptocurrency object. Contains
    information about the cryptocurrency and methods to populate that data
    using cryptocurrency symbol(s).
    """
    id: int
    short_description: str
    description: str
    is_closing_only: bool
    active: bool
    tick_size: Decimal
    destination_venue_symbols: List[DestinationVenueSymbol]
    streamer_symbol: Optional[str] = None

    @classmethod
    def get_cryptocurrencies(
        cls,
        session: Session,
        symbols: List[str] = []
    ) -> List['Cryptocurrency']:
        """
        Returns a list of cryptocurrency objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the symbols to get the cryptocurrencies for.
        """
        params = {'symbol[]': symbols} if symbols else None
        data = session.get('/instruments/cryptocurrencies', params=params)
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_cryptocurrency(
        cls,
        session: Session,
        symbol: str
    ) -> 'Cryptocurrency':
        """
        Returns a Cryptocurrency object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the cryptocurrency for.
        """
        symbol = symbol.replace('/', '%2F')
        data = session.get(f'/instruments/cryptocurrencies/{symbol}')
        return cls(**data)


class Equity(TradeableTastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade equity object. Contains information
    about the equity and methods to populate that data using equity symbol(s).
    """
    id: int
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
    tick_sizes: Optional[List[TickSize]] = None
    option_tick_sizes: Optional[List[TickSize]] = None

    @classmethod
    def get_active_equities(
        cls,
        session: Session,
        per_page: int = 1000,
        page_offset: Optional[int] = None,
        lendability: Optional[str] = None
    ) -> List['Equity']:
        """
        Returns a list of actively traded Equity objects.

        :param session: the session to use for the request.
        :param per_page: the number of equities to get per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
        :param lendability:
            the lendability of the equities; e.g. 'Easy To Borrow',
            'Locate Required', 'Preborrow'
        """
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
        params = {
            'per-page': per_page,
            'page-offset': page_offset,
            'lendability': lendability
        }
        # loop through pages and get all active equities
        equities = []
        while True:
            response = session.client.get(
                f'{session.base_url}/instruments/equities/active',
                params={k: v for k, v in params.items() if v is not None}
            )
            validate_response(response)
            json = response.json()
            equities.extend([cls(**i) for i in json['data']['items']])
            # handle pagination
            pagination = json['pagination']
            if (
                pagination['page-offset'] >= pagination['total-pages'] - 1 or
                not paginate
            ):
                break
            params['page-offset'] += 1  # type: ignore

        return equities

    @classmethod
    def get_equities(
        cls,
        session: Session,
        symbols: Optional[List[str]] = None,
        lendability: Optional[str] = None,
        is_index: Optional[bool] = None,
        is_etf: Optional[bool] = None
    ) -> List['Equity']:
        """
        Returns a list of Equity objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the symbols to get the equities for.
        :param lendability:
            the lendability of the equities; e.g. 'Easy To Borrow',
            'Locate Required', 'Preborrow'
        :param is_index: whether the equities are indexes.
        :param is_etf: whether the equities are ETFs.
        """
        params = {
            'symbol[]': symbols,
            'lendability': lendability,
            'is-index': is_index,
            'is-etf': is_etf
        }
        data = session.get(
            '/instruments/equities',
            params={k: v for k, v in params.items() if v is not None}
        )
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_equity(cls, session: Session, symbol: str) -> 'Equity':
        """
        Returns a Equity object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the equity for.
        """
        symbol = symbol.replace('/', '%2F')
        data = session.get(f'/instruments/equities/{symbol}')
        return cls(**data)


class Option(TradeableTastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade option object. Contains information
    about the option and methods to populate that data using option symbol(s).
    """
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.streamer_symbol:
            self._set_streamer_symbol()

    @classmethod
    def get_options(
        cls,
        session: Session,
        symbols: Optional[List[str]] = None,
        active: Optional[bool] = None,
        with_expired: Optional[bool] = None
    ) -> List['Option']:
        """
        Returns a list of Option objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the OCC symbols to get the options for.
        :param active: whether the options are active.
        :param with_expired: whether to include expired options.
        """
        params = {
            'symbol[]': symbols,
            'active': active,
            'with-expired': with_expired
        }
        data = session.get(
            '/instruments/equity-options',
            params={k: v for k, v in params.items() if v is not None}
        )
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_option(
        cls,
        session: Session,
        symbol: str,
        active: Optional[bool] = None
    ) -> 'Option':
        """
        Returns a Option object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, OCC format
        """
        symbol = symbol.replace('/', '%2F')
        params = {'active': active} if active is not None else None
        data = session.get(
            f'/instruments/equity-options/{symbol}',
            params=params
        )
        return cls(**data)

    def _set_streamer_symbol(self) -> None:
        if self.strike_price % 1 == 0:
            strike = '{0:.0f}'.format(self.strike_price)
        else:
            strike = '{0:.2f}'.format(self.strike_price)
            if strike[-1] == '0':
                strike = strike[:-1]

        exp = self.expiration_date.strftime('%y%m%d')
        self.streamer_symbol = \
            f'.{self.underlying_symbol}{exp}{self.option_type.value}{strike}'

    @classmethod
    def streamer_symbol_to_occ(cls, streamer_symbol) -> str:
        """
        Returns the OCC 2010 symbol equivalent to the given streamer symbol.

        :param streamer_symbol: the streamer symbol to convert
        """
        match = re.match(
            r'\.([A-Z]+)(\d{6})([CP])(\d+)(\.(\d+))?',
            streamer_symbol
        )
        if match is None:
            return ''
        symbol = match.group(1)[:6].ljust(6)
        exp = match.group(2)
        option_type = match.group(3)
        strike = match.group(4).zfill(5)
        if match.group(6) is not None:
            decimal = str(100 * int(match.group(6))).zfill(3)
        else:
            decimal = '000'

        return f'{symbol}{exp}{option_type}{strike}{decimal}'

    @classmethod
    def occ_to_streamer_symbol(cls, occ) -> str:
        """
        Returns the dxfeed symbol for use in the streamer from the given OCC
        2010 symbol.

        :param occ: the OCC symbol to convert
        """
        match = re.match(
            r'([A-Z]+)\s+(\d{6})([CP])(\d{5})(\d{3})',
            occ
        )
        if match is None:
            return ''
        symbol = match.group(1)
        exp = match.group(2)
        option_type = match.group(3)
        strike = int(match.group(4))
        decimal = int(match.group(5))

        res = f'.{symbol}{exp}{option_type}{strike}'
        if decimal != 0:
            decimal_str = str(decimal / 1000.0)
            res += decimal_str[1:]
        return res


class NestedOptionChain(TastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade nested option chain object.
    Contains information about the option chain and a method to fetch one for
    a symbol.

    This is cleaner than calling :meth:`get_option_chain` but if you want to
    create actual :class:`Option` objects you'll need to make an extra API
    request or two.
    """
    underlying_symbol: str
    root_symbol: str
    option_chain_type: str
    shares_per_contract: int
    tick_sizes: List[TickSize]
    deliverables: List[Deliverable]
    expirations: List[NestedOptionChainExpiration]

    @classmethod
    def get_chain(cls, session: Session, symbol: str) -> 'NestedOptionChain':
        """
        Gets the option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.
        """
        symbol = symbol.replace('/', '%2F')
        data = session.get(f'/option-chains/{symbol}/nested')
        return cls(**data['items'][0])


class FutureProduct(TastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade future product object. Contains
    information about the future product and a method to fetch one for a
    symbol.

    Useful for fetching general information about a family of futures, without
    knowing the specific expirations or symbols.
    """
    root_symbol: str
    code: str
    description: str
    exchange: str
    product_type: str
    listed_months: List[FutureMonthCode]
    active_months: List[FutureMonthCode]
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
    roll: Roll
    base_tick: Optional[int] = None
    sub_tick: Optional[int] = None
    contract_limit: Optional[int] = None
    product_subtype: Optional[str] = None
    security_group: Optional[str] = None
    true_underlying_code: Optional[str] = None
    clearport_code: Optional[str] = None
    legacy_code: Optional[str] = None
    legacy_exchange_code: Optional[str] = None
    option_products: Optional[List['FutureOptionProduct']] = None

    @classmethod
    def get_future_products(
        cls,
        session: Session
    ) -> List['FutureProduct']:
        """
        Returns a list of FutureProduct objects available.

        :param session: the session to use for the request.
        """
        data = session.get('/instruments/future-products')
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_future_product(
        cls,
        session: Session,
        code: str,
        exchange: str = 'CME'
    ) -> 'FutureProduct':
        """
        Returns a FutureProduct object from the given symbol.

        :param session: the session to use for the request.
        :param code: the product code, e.g. 'ES'
        :param exchange:
            the exchange to fetch from: 'CME', 'SMALLS', 'CFE', 'CBOED'
        """
        code = code.replace('/', '')
        data = session.get(f'/instruments/future-products/{exchange}/{code}')
        return cls(**data)


class Future(TradeableTastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade future object. Contains information
    about the future and methods to fetch futures for symbol(s).
    """
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
    back_month_first_calendar_symbol: bool
    instrument_type: InstrumentType = InstrumentType.FUTURE
    streamer_symbol: Optional[str] = None
    is_tradeable: Optional[bool] = None
    future_product: Optional['FutureProduct'] = None
    contract_size: Optional[Decimal] = None
    main_fraction: Optional[Decimal] = None
    sub_fraction: Optional[Decimal] = None
    first_notice_date: Optional[date] = None
    roll_target_symbol: Optional[str] = None
    true_underlying_symbol: Optional[str] = None
    future_etf_equivalent: Optional[FutureEtfEquivalent] = None
    tick_sizes: Optional[List[TickSize]] = None
    option_tick_sizes: Optional[List[TickSize]] = None
    spread_tick_sizes: Optional[List[TickSize]] = None

    @classmethod
    def get_futures(
        cls,
        session: Session,
        symbols: Optional[List[str]] = None,
        product_codes: Optional[List[str]] = None
    ) -> List['Future']:
        """
        Returns a list of Future objects from the given symbols
        or product codes.

        :param session: the session to use for the request.
        :param symbols:
            symbols of the futures, e.g. 'ESZ9', '/ESZ9'.
        :param product_codes:
            the product codes of the futures, e.g. 'ES', '6A'. Ignored if
            symbols are provided.
        """
        params = {
            'symbol[]': symbols,
            'product-code[]': product_codes
        }
        data = session.get(
            '/instruments/futures',
            params={k: v for k, v in params.items() if v is not None}
        )
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_future(cls, session: Session, symbol: str) -> 'Future':
        """
        Returns a Future object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the future for.
        """
        symbol = symbol.replace('/', '')
        data = session.get(f'/instruments/futures/{symbol}')
        return cls(**data)


class FutureOptionProduct(TastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade future option product object.
    Contains information about the future option product (deliverable for
    the future option).
    """
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

    @classmethod
    def get_future_option_products(
        cls,
        session: Session
    ) -> List['FutureOptionProduct']:
        """
        Returns a list of FutureOptionProduct objects available.

        :param session: the session to use for the request.
        """
        data = session.get('/instruments/future-option-products')
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_future_option_product(
        cls,
        session: Session,
        root_symbol: str,
        exchange: str = 'CME'
    ) -> 'FutureOptionProduct':
        """
        Returns a FutureOptionProduct object from the given symbol.

        :param session: the session to use for the request.
        :param code: the root symbol of the future option
        :param exchange: the exchange to get the product from
        """
        root_symbol = root_symbol.replace('/', '')
        data = session.get(f'/instruments/future-option-products/'
                           f'{exchange}/{root_symbol}')
        return cls(**data)


class FutureOption(TradeableTastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade future option object. Contains
    information about the future option, and methods to get future options.
    """
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
    instrument_type: InstrumentType = InstrumentType.FUTURE_OPTION
    future_option_product: Optional['FutureOptionProduct'] = None

    @classmethod
    def get_future_options(
        cls,
        session: Session,
        symbols: Optional[List[str]] = None,
        root_symbol: Optional[str] = None,
        expiration_date: Optional[date] = None,
        option_type: Optional[OptionType] = None,
        strike_price: Optional[Decimal] = None
    ) -> List['FutureOption']:
        """
        Returns a list of FutureOption objects from the given symbols.

        NOTE: Last I checked, all of the parameters are bugged except
        for `symbols`.

        :param session: the session to use for the request.
        :param symbols: the Tastytrade symbols to filter by.
        :param root_symbol:
            the root symbol to get the future options for, e.g. 'EW3', 'SO'
        :param expiration_date: the expiration date for the future options.
        :param option_type: the option type to filter by.
        :param strike_price: the strike price to filter by.
        """
        params = {
            'symbol[]': symbols,
            'option-root-symbol': root_symbol,
            'expiration-date': expiration_date,
            'option-type': option_type,
            'strike-price': strike_price
        }
        data = session.get(
            '/instruments/future-options',
            params={k: v for k, v in params.items() if v is not None}
        )
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_future_option(
        cls,
        session: Session,
        symbol: str
    ) -> 'FutureOption':
        """
        Returns a FutureOption object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, Tastytrade format
        """
        symbol = symbol.replace('/', '%2F').replace(' ', '%20')
        data = session.get(f'/instruments/future-options/{symbol}')
        return cls(**data)


class NestedFutureOptionSubchain(TastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade nested future option chain for a
    specific futures underlying symbol.
    """
    underlying_symbol: str
    root_symbol: str
    exercise_style: str
    expirations: List[NestedFutureOptionChainExpiration]


class NestedFutureOptionChain(TastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade nested option chain object. Contains
    information about the option chain and a method to fetch one for a symbol.

    This is cleaner than calling :meth:`get_future_option_chain` but if you
    want to create actual :class:`FutureOption` objects you'll need to make an
    extra API request or two.
    """
    futures: List[NestedFutureOptionFuture]
    option_chains: List[NestedFutureOptionSubchain]

    @classmethod
    def get_chain(
        cls,
        session: Session,
        symbol: str
    ) -> 'NestedFutureOptionChain':
        """
        Gets the futures option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.
        """
        symbol = symbol.replace('/', '')
        data = session.get(f'/futures-option-chains/{symbol}/nested')
        return cls(**data)


class Warrant(TastytradeJsonDataclass):
    """
    Dataclass that represents a Tastytrade warrant object. Contains
    information about the warrant, and methods to get warrants.
    """
    symbol: str
    instrument_type: InstrumentType
    listed_market: str
    description: str
    is_closing_only: bool
    active: bool
    cusip: Optional[str] = None

    @classmethod
    def get_warrants(
        cls,
        session: Session,
        symbols: Optional[List[str]] = None
    ) -> List['Warrant']:
        """
        Returns a list of Warrant objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: symbols of the warrants, e.g. 'NKLAW'
        """
        params = {'symbol[]': symbols} if symbols else None
        data = session.get('/instruments/warrants', params=params)
        return [cls(**i) for i in data['items']]

    @classmethod
    def get_warrant(cls, session: Session, symbol: str) -> 'Warrant':
        """
        Returns a Warrant object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the warrant for.
        """
        data = session.get(f'/instruments/warrants/{symbol}')
        return cls(**data)


# fix pydantic forward references
FutureProduct.update_forward_refs()


def get_quantity_decimal_precisions(
    session: Session
) -> List[QuantityDecimalPrecision]:
    """
    Returns a list of QuantityDecimalPrecision objects for different
    types of instruments.

    :param session: the session to use for the request.
    """
    data = session.get('/instruments/quantity-decimal-precisions')
    return [QuantityDecimalPrecision(**i) for i in data['items']]


def get_option_chain(
    session: Session,
    symbol: str
) -> Dict[date, List[Option]]:
    """
    Returns a mapping of expiration date to a list of option objects
    representing the options chain for the given symbol.

    In the case that there are two expiries on the same day (e.g. SPXW
    and SPX AM options), both will be returned in the same list. If you
    just want one expiry, you'll need to filter the list yourself, or use
    :class:`NestedOptionChain` instead.

    :param session: the session to use for the request.
    :param symbol: the symbol to get the option chain for.
    """
    symbol = symbol.replace('/', '%2F')
    data = session.get(f'/option-chains/{symbol}')
    chain = defaultdict(list)
    for i in data['items']:
        option = Option(**i)
        chain[option.expiration_date].append(option)

    return chain


def get_future_option_chain(
    session: Session,
    symbol: str
) -> Dict[date, List[FutureOption]]:
    """
    Returns a mapping of expiration date to a list of futures options
    objects representing the options chain for the given symbol.

    In the case that there are two expiries on the same day (e.g. EW
    and ES options), both will be returned in the same list. If you
    just want one expiry, you'll need to filter the list yourself, or
    use :class:`NestedFutureOptionChain` instead.

    :param session: the session to use for the request.
    :param symbol: the symbol to get the option chain for.
    """
    symbol = symbol.replace('/', '')
    data = session.get(f'/futures-option-chains/{symbol}')
    chain = defaultdict(list)
    for i in data['items']:
        option = FutureOption(**i)
        chain[option.expiration_date].append(option)

    return chain
