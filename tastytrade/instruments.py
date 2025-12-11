import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, overload

from pydantic import field_validator, model_validator
from typing_extensions import Self

from tastytrade.order import InstrumentType, TradeableTastytradeData
from tastytrade.session import Session
from tastytrade.utils import TastytradeData, a_paginate, paginate


class OptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of options
    and their abbreviations in the API.
    """

    CALL = "C"
    PUT = "P"


class FutureMonthCode(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid month codes for
    futures.

    This is really here for reference, as the API barely uses these codes.
    """

    JAN = "F"
    FEB = "G"
    MAR = "H"
    APR = "J"
    MAY = "K"
    JUN = "M"
    JUL = "N"
    AUG = "Q"
    SEP = "U"
    OCT = "V"
    NOV = "X"
    DEC = "Z"


class Deliverable(TastytradeData):
    """
    Dataclass representing the deliverable for an option.
    """

    id: int
    root_symbol: str
    deliverable_type: str
    description: str
    amount: Decimal
    percent: str
    symbol: str | None = None
    instrument_type: InstrumentType | None = None


class DestinationVenueSymbol(TastytradeData):
    """
    Dataclass representing a specific destination venue symbol for a
    cryptocurrency.
    """

    id: int
    symbol: str
    destination_venue: str
    routable: bool
    max_quantity_precision: int | None = None
    max_price_precision: int | None = None


class QuantityDecimalPrecision(TastytradeData):
    """
    Dataclass representing the decimal precision (number of places) for an
    instrument.
    """

    instrument_type: InstrumentType
    value: int
    minimum_increment_precision: int
    symbol: str | None = None


class Strike(TastytradeData):
    """
    Dataclass representing a specific strike in an options chain, containing
    the symbols for the call and put options.
    """

    strike_price: Decimal
    call: str
    put: str
    call_streamer_symbol: str
    put_streamer_symbol: str


class TickSize(TastytradeData):
    """
    Dataclass representing the tick size for an instrument.
    """

    value: Decimal
    threshold: Decimal | None = None
    symbol: str | None = None


class NestedOptionChainExpiration(TastytradeData):
    """
    Dataclass representing an expiration in a nested options chain.
    """

    expiration_type: str
    expiration_date: date
    days_to_expiration: int
    settlement_type: str
    strikes: list[Strike]


class NestedFutureOptionChainExpiration(TastytradeData):
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
    strikes: list[Strike]
    tick_sizes: list[TickSize]


class NestedFutureOptionFuture(TastytradeData):
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
    maturity_date: date | None = None

    @field_validator("maturity_date", mode="before")
    @classmethod
    def parse_date_with_utc(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.split(" ")[0]
        return value


class FutureEtfEquivalent(TastytradeData):
    """
    Dataclass that represents the ETF equivalent for a future (aka, the number
    of shares of the ETF that are equivalent to one future, leverage-wise).
    """

    symbol: str
    share_quantity: int


class Roll(TastytradeData):
    """
    Dataclass representing a roll for a future.
    """

    name: str
    active_count: int
    cash_settled: bool
    business_days_offset: int
    first_notice: bool


class Cryptocurrency(TradeableTastytradeData):
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
    destination_venue_symbols: list[DestinationVenueSymbol]
    streamer_symbol: str | None = None

    @overload
    @classmethod
    async def a_get(
        cls, session: Session, symbols: list[str] | None = None
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: str | list[str] | None = None,
    ) -> Self | list[Self]:
        """
        Returns a list of cryptocurrency objects from the given symbols,
        or a single cryptocurrency if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: the symbol(s) to get the cryptocurrencies for.
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F")
            data = await session._a_get(f"/instruments/cryptocurrencies/{symbol}")
            return cls(**data)
        params = {"symbol[]": symbols} if symbols else None
        data = await session._a_get("/instruments/cryptocurrencies", params=params)
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session, symbols: list[str] | None = None) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        symbols: str | list[str] | None = None,
    ) -> Self | list[Self]:
        """
        Returns a list of cryptocurrency objects from the given symbols,
        or a single cryptocurrency if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: the symbol(s) to get the cryptocurrencies for.
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F")
            data = session._get(f"/instruments/cryptocurrencies/{symbol}")
            return cls(**data)
        params = {"symbol[]": symbols} if symbols else None
        data = session._get("/instruments/cryptocurrencies", params=params)
        return [cls(**i) for i in data["items"]]


class Equity(TradeableTastytradeData):
    """
    Dataclass that represents a Tastytrade equity object. Contains information
    about the equity and methods to populate that data using equity symbol(s).
    """

    id: int
    is_index: bool
    description: str
    lendability: str
    market_time_instrument_collection: str
    is_closing_only: bool
    is_options_closing_only: bool
    active: bool
    is_illiquid: bool
    is_etf: bool
    streamer_symbol: str
    borrow_rate: Decimal | None = None
    cusip: str | None = None
    short_description: str | None = None
    halted_at: datetime | None = None
    stops_trading_at: datetime | None = None
    is_fractional_quantity_eligible: bool | None = None
    tick_sizes: list[TickSize] | None = None
    listed_market: str | None = None
    option_tick_sizes: list[TickSize] | None = None

    @classmethod
    async def a_get_active_equities(
        cls,
        session: Session,
        per_page: int = 1000,
        page_offset: int | None = 0,
        lendability: str | None = None,
    ) -> list[Self]:
        """
        Returns a list of actively traded Equity objects.

        :param session: the session to use for the request.
        :param per_page: the number of equities to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param lendability:
            the lendability of the equities; e.g. 'Easy To Borrow',
            'Locate Required', 'Preborrow'
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "lendability": lendability,
        }
        return await a_paginate(
            session.async_client, cls, "/instruments/equities/active", params
        )

    @classmethod
    def get_active_equities(
        cls,
        session: Session,
        per_page: int = 1000,
        page_offset: int | None = 0,
        lendability: str | None = None,
    ) -> list[Self]:
        """
        Returns a list of actively traded Equity objects.

        :param session: the session to use for the request.
        :param per_page: the number of equities to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param lendability:
            the lendability of the equities; e.g. 'Easy To Borrow',
            'Locate Required', 'Preborrow'
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "lendability": lendability,
        }
        return paginate(
            session.sync_client, cls, "/instruments/equities/active", params
        )

    @overload
    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: list[str],
        *,
        per_page: int = 250,
        page_offset: int | None = 0,
        lendability: str | None = None,
        is_index: bool | None = None,
        is_etf: bool | None = None,
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: str | list[str],
        per_page: int = 250,
        page_offset: int | None = 0,
        lendability: str | None = None,
        is_index: bool | None = None,
        is_etf: bool | None = None,
    ) -> Self | list[Self]:
        """
        Returns a list of Equity objects from the given symbols, or a single
        Equity object if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: the symbol(s) to get the equities for.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param lendability:
            the lendability of the equities; e.g. 'Easy To Borrow',
            'Locate Required', 'Preborrow'
        :param is_index: whether the equities are indexes.
        :param is_etf: whether the equities are ETFs.
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F")
            data = await session._a_get(f"/instruments/equities/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "lendability": lendability,
            "is-index": is_index,
            "is-etf": is_etf,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return await a_paginate(
            session.async_client, cls, "/instruments/equities", params
        )

    @overload
    @classmethod
    def get(
        cls,
        session: Session,
        symbols: list[str],
        *,
        per_page: int = 250,
        page_offset: int | None = 0,
        lendability: str | None = None,
        is_index: bool | None = None,
        is_etf: bool | None = None,
    ) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        symbols: str | list[str],
        *,
        per_page: int = 250,
        page_offset: int | None = 0,
        lendability: str | None = None,
        is_index: bool | None = None,
        is_etf: bool | None = None,
    ) -> Self | list[Self]:
        """
        Returns a list of Equity objects from the given symbols, or a single
        Equity object if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: the symbol(s) to get the equities for.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param lendability:
            the lendability of the equities; e.g. 'Easy To Borrow',
            'Locate Required', 'Preborrow'
        :param is_index: whether the equities are indexes.
        :param is_etf: whether the equities are ETFs.
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F")
            data = session._get(f"/instruments/equities/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "lendability": lendability,
            "is-index": is_index,
            "is-etf": is_etf,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return paginate(session.sync_client, cls, "/instruments/equities", params)


class Option(TradeableTastytradeData):
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
    is_closing_only: bool
    expires_at: datetime | None = None
    streamer_symbol: str = ""
    listed_market: str | None = None
    halted_at: datetime | None = None
    old_security_number: str | None = None

    @model_validator(mode="after")
    def set_streamer_symbol(self) -> Self:
        if self.streamer_symbol == "":
            self._set_streamer_symbol()
        return self

    @overload
    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: list[str],
        *,
        active: bool | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
        with_expired: bool | None = None,
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: str | list[str],
        *,
        active: bool | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
        with_expired: bool | None = None,
    ) -> Self | list[Self]:
        """
        Returns a list of Option objects from the given symbols, or a single
        Option object if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: the OCC symbol(s) to get the options for.
        :param active: whether the options are active.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param with_expired: whether to include expired options.
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F")
            data = await session._a_get(f"/instruments/equity-options/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "active": active,
            "with-expired": with_expired,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return await a_paginate(
            session.async_client, cls, "/instruments/equity-options", params
        )

    @overload
    @classmethod
    def get(
        cls,
        session: Session,
        symbols: list[str],
        *,
        per_page: int = 250,
        page_offset: int | None = 0,
        active: bool | None = None,
        with_expired: bool | None = None,
    ) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        symbols: str | list[str],
        *,
        active: bool | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
        with_expired: bool | None = None,
    ) -> Self | list[Self]:
        """
        Returns a list of Option objects from the given symbols, or a single
        Option object if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: the OCC symbol(s) to get the options for.
        :param active: whether the options are active.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param with_expired: whether to include expired options.
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F")
            data = session._get(f"/instruments/equity-options/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "active": active,
            "with-expired": with_expired,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return paginate(session.sync_client, cls, "/instruments/equity-options", params)

    def _set_streamer_symbol(self) -> None:
        if self.strike_price % 1 == 0:
            strike = "{0:.0f}".format(self.strike_price)
        else:
            strike = "{0:.2f}".format(self.strike_price)
            if strike[-1] == "0":
                strike = strike[:-1]

        exp = self.expiration_date.strftime("%y%m%d")
        self.streamer_symbol = (
            f".{self.underlying_symbol}{exp}{self.option_type.value}{strike}"
        )

    @classmethod
    def streamer_symbol_to_occ(cls, streamer_symbol: str) -> str:
        """
        Returns the OCC 2010 symbol equivalent to the given streamer symbol.

        :param streamer_symbol: the streamer symbol to convert
        """
        match = re.match(r"\.([A-Z]+)(\d{6})([CP])(\d+)(\.(\d+))?", streamer_symbol)
        if match is None:
            return ""
        symbol = match.group(1)[:6].ljust(6)
        exp = match.group(2)
        option_type = match.group(3)
        strike = match.group(4).zfill(5)
        if match.group(6) is not None:
            decimal = str(100 * int(match.group(6))).zfill(3)
        else:
            decimal = "000"

        return f"{symbol}{exp}{option_type}{strike}{decimal}"

    @classmethod
    def occ_to_streamer_symbol(cls, occ: str) -> str:
        """
        Returns the dxfeed symbol for use in the streamer from the given OCC
        2010 symbol.

        :param occ: the OCC symbol to convert
        """
        symbol = occ[:6].split()[0]
        info = occ[6:]
        match = re.match(r"(\d{6})([CP])(\d{5})(\d{3})", info)
        if match is None:
            return ""
        exp = match.group(1)
        option_type = match.group(2)
        strike = int(match.group(3))
        decimal = int(match.group(4))

        res = f".{symbol}{exp}{option_type}{strike}"
        if decimal != 0:
            decimal_str = str(decimal / 1000.0)
            res += decimal_str[1:]
        return res


class NestedOptionChain(TastytradeData):
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
    tick_sizes: list[TickSize]
    expirations: list[NestedOptionChainExpiration]
    deliverables: list[Deliverable] | None = None

    @classmethod
    async def a_get(cls, session: Session, symbol: str) -> list[Self]:
        """
        Gets the option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.
        """
        symbol = symbol.replace("/", "%2F")
        data = await session._a_get(f"/option-chains/{symbol}/nested")
        return [cls(**item) for item in data["items"]]

    @classmethod
    def get(cls, session: Session, symbol: str) -> list[Self]:
        """
        Gets the option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.
        """
        symbol = symbol.replace("/", "%2F")
        data = session._get(f"/option-chains/{symbol}/nested")
        return [cls(**item) for item in data["items"]]


class FutureProduct(TastytradeData):
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
    listed_months: list[FutureMonthCode]
    active_months: list[FutureMonthCode]
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
    base_tick: int | None = None
    sub_tick: int | None = None
    contract_limit: int | None = None
    product_subtype: str | None = None
    security_group: str | None = None
    true_underlying_code: str | None = None
    clearport_code: str | None = None
    legacy_code: str | None = None
    legacy_exchange_code: str | None = None
    option_products: list["FutureOptionProduct"] | None = None

    @overload
    @classmethod
    async def a_get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(
        cls, session: Session, code: str, exchange: str = "CME"
    ) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        code: str | None = None,
        exchange: str = "CME",
    ) -> Self | list[Self]:
        """
        Returns a list of FutureProduct objects available, or a single
        FutureProduct object if a code is provided.

        :param session: the session to use for the request.
        :param code: the product code, e.g. 'ES'
        :param exchange:
            the exchange to fetch from: 'CME', 'SMALLS', 'CFE', 'CBOED'
        """
        if code:
            code = code.replace("/", "")
            data = await session._a_get(
                f"/instruments/future-products/{exchange}/{code}"
            )
            return cls(**data)
        data = await session._a_get("/instruments/future-products")
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, code: str, exchange: str = "CME") -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        code: str | None = None,
        exchange: str = "CME",
    ) -> Self | list[Self]:
        """
        Returns a list of FutureProduct objects available, or a single
        FutureProduct object if a code is provided.

        :param session: the session to use for the request.
        :param code: the product code, e.g. 'ES'
        :param exchange:
            the exchange to fetch from: 'CME', 'SMALLS', 'CFE', 'CBOED'
        """
        if code:
            code = code.replace("/", "")
            data = session._get(f"/instruments/future-products/{exchange}/{code}")
            return cls(**data)
        data = session._get("/instruments/future-products")
        return [cls(**i) for i in data["items"]]


class Future(TradeableTastytradeData):
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
    streamer_symbol: str = ""
    closing_only_date: date | None = None
    is_tradeable: bool | None = None
    future_product: "FutureProduct | None" = None
    contract_size: Decimal | None = None
    main_fraction: Decimal | None = None
    sub_fraction: Decimal | None = None
    first_notice_date: date | None = None
    roll_target_symbol: str | None = None
    true_underlying_symbol: str | None = None
    future_etf_equivalent: FutureEtfEquivalent | None = None
    tick_sizes: list[TickSize] | None = None
    option_tick_sizes: list[TickSize] | None = None
    spread_tick_sizes: list[TickSize] | None = None

    @overload
    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: list[str] | None = None,
        *,
        product_codes: list[str] | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: str | list[str] | None = None,
        *,
        product_codes: list[str] | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> Self | list[Self]:
        """
        Returns a list of Future objects from the given symbols
        or product codes.

        :param session: the session to use for the request.
        :param symbols:
            symbol(s) of the futures, e.g. 'ESZ9', '/ESZ9'.
        :param product_codes:
            the product codes of the futures, e.g. 'ES', '6A'. Ignored if
            symbols are provided.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "")
            data = await session._a_get(f"/instruments/futures/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "product-code[]": product_codes,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return await a_paginate(
            session.async_client, cls, "/instruments/futures", params
        )

    @overload
    @classmethod
    def get(
        cls,
        session: Session,
        symbols: list[str] | None = None,
        *,
        product_codes: list[str] | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        symbols: str | list[str] | None = None,
        *,
        product_codes: list[str] | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> Self | list[Self]:
        """
        Returns a list of Future objects from the given symbols
        or product codes.

        :param session: the session to use for the request.
        :param symbols:
            symbol(s) of the futures, e.g. 'ESZ9', '/ESZ9'.
        :param product_codes:
            the product codes of the futures, e.g. 'ES', '6A'. Ignored if
            symbols are provided.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "")
            data = session._get(f"/instruments/futures/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "product-code[]": product_codes,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return paginate(session.sync_client, cls, "/instruments/futures", params)


class FutureOptionProduct(TastytradeData):
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
    future_product: "FutureProduct | None" = None
    product_subtype: str | None = None
    legacy_code: str | None = None
    clearport_code: str | None = None

    @overload
    @classmethod
    async def a_get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(
        cls, session: Session, root_symbol: str, exchange: str = "CME"
    ) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        root_symbol: str | None = None,
        exchange: str = "CME",
    ) -> Self | list[Self]:
        """
        Returns a list of FutureOptionProduct objects available, or a single
        FutureOptionProduct object if a root symbol is provided.

        :param session: the session to use for the request.
        :param root_symbol: the root symbol of the future option
        :param exchange: the exchange to get the product from
        """
        if root_symbol:
            root_symbol = root_symbol.replace("/", "")
            data = await session._a_get(
                f"/instruments/future-option-products/{exchange}/{root_symbol}"
            )
            return cls(**data)
        data = await session._a_get("/instruments/future-option-products")
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, root_symbol: str, exchange: str = "CME") -> Self: ...

    @classmethod
    def get(
        cls, session: Session, root_symbol: str | None = None, exchange: str = "CME"
    ) -> Self | list[Self]:
        """
        Returns a list of FutureOptionProduct objects available, or a single
        FutureOptionProduct object if a root symbol is provided.

        :param session: the session to use for the request.
        :param root_symbol: the root symbol of the future option
        :param exchange: the exchange to get the product from
        """
        if root_symbol:
            root_symbol = root_symbol.replace("/", "")
            data = session._get(
                f"/instruments/future-option-products/{exchange}/{root_symbol}"
            )
            return cls(**data)
        data = session._get("/instruments/future-option-products")
        return [cls(**i) for i in data["items"]]


class FutureOption(TradeableTastytradeData):
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
    future_option_product: "FutureOptionProduct | None" = None

    @field_validator("maturity_date", mode="before")
    @classmethod
    def parse_date_with_utc(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.split(" ")[0]
        return value

    @overload
    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: list[str],
        *,
        root_symbol: str | None = None,
        expiration_date: date | None = None,
        option_type: OptionType | None = None,
        strike_price: Decimal | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        symbols: str | list[str],
        *,
        root_symbol: str | None = None,
        expiration_date: date | None = None,
        option_type: OptionType | None = None,
        strike_price: Decimal | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> Self | list[Self]:
        """
        Returns a list of FutureOption objects from the given symbols.

        NOTE: many of the parameters are bugged, maybe Tasty will fix?

        :param session: the session to use for the request.
        :param symbols: the Tastytrade symbol(s) to filter by.
        :param root_symbol:
            the root symbol to get the future options for, e.g. 'EW3', 'SO'
        :param expiration_date: the expiration date for the future options.
        :param option_type: the option type to filter by.
        :param strike_price: the strike price to filter by.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F").replace(" ", "%20")
            data = await session._a_get(f"/instruments/future-options/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "option-root-symbol": root_symbol,
            "expiration-date": expiration_date,
            "option-type": option_type.value if option_type else None,
            "strike-price": strike_price,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return await a_paginate(
            session.async_client, cls, "/instruments/future-options", params
        )

    @overload
    @classmethod
    def get(
        cls,
        session: Session,
        symbols: list[str],
        *,
        root_symbol: str | None = None,
        expiration_date: date | None = None,
        option_type: OptionType | None = None,
        strike_price: Decimal | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        symbols: str | list[str],
        *,
        root_symbol: str | None = None,
        expiration_date: date | None = None,
        option_type: OptionType | None = None,
        strike_price: Decimal | None = None,
        per_page: int = 250,
        page_offset: int | None = 0,
    ) -> Self | list[Self]:
        """
        Returns a list of FutureOption objects from the given symbols.

        NOTE: many of the parameters are bugged, maybe Tasty will fix?

        :param session: the session to use for the request.
        :param symbols: the Tastytrade symbol(s) to filter by.
        :param root_symbol:
            the root symbol to get the future options for, e.g. 'EW3', 'SO'
        :param expiration_date: the expiration date for the future options.
        :param option_type: the option type to filter by.
        :param strike_price: the strike price to filter by.
        :param per_page: the number of options to get per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        """
        if isinstance(symbols, str):
            symbol = symbols.replace("/", "%2F").replace(" ", "%20")
            data = session._get(f"/instruments/future-options/{symbol}")
            return cls(**data)
        params = {
            "symbol[]": symbols,
            "option-root-symbol": root_symbol,
            "expiration-date": expiration_date,
            "option-type": option_type.value if option_type else None,
            "strike-price": strike_price,
            "per-page": per_page,
            "page-offset": page_offset,
        }
        return paginate(session.sync_client, cls, "/instruments/future-options", params)


class NestedFutureOptionSubchain(TastytradeData):
    """
    Dataclass that represents a Tastytrade nested future option chain for a
    specific futures underlying symbol.
    """

    underlying_symbol: str
    root_symbol: str
    exercise_style: str
    expirations: list[NestedFutureOptionChainExpiration]


class NestedFutureOptionChain(TastytradeData):
    """
    Dataclass that represents a Tastytrade nested option chain object. Contains
    information about the option chain and a method to fetch one for a symbol.

    This is cleaner than calling :meth:`get_future_option_chain` but if you
    want to create actual :class:`FutureOption` objects you'll need to make an
    extra API request or two.
    """

    futures: list[NestedFutureOptionFuture]
    option_chains: list[NestedFutureOptionSubchain]

    @classmethod
    async def a_get(cls, session: Session, symbol: str) -> Self:
        """
        Gets the futures option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.
        """
        symbol = symbol.replace("/", "")
        data = await session._a_get(f"/futures-option-chains/{symbol}/nested")
        return cls(**data)

    @classmethod
    def get(cls, session: Session, symbol: str) -> Self:
        """
        Gets the futures option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.
        """
        symbol = symbol.replace("/", "")
        data = session._get(f"/futures-option-chains/{symbol}/nested")
        return cls(**data)


class Warrant(TastytradeData):
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
    cusip: str | None = None

    @overload
    @classmethod
    async def a_get(
        cls, session: Session, symbols: list[str] | None = None
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    async def a_get(
        cls, session: Session, symbols: str | list[str] | None = None
    ) -> Self | list[Self]:
        """
        Returns a list of Warrant objects from the given symbols, or a single
        Warrant object if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: symbol(s) of the warrants, e.g. 'NKLAW'
        """
        if isinstance(symbols, str):
            data = await session._a_get(f"/instruments/warrants/{symbols}")
            return cls(**data)
        params = {"symbol[]": symbols} if symbols else None
        data = await session._a_get("/instruments/warrants", params=params)
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session, symbols: list[str] | None = None) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, symbols: str) -> Self: ...

    @classmethod
    def get(
        cls, session: Session, symbols: str | list[str] | None = None
    ) -> Self | list[Self]:
        """
        Returns a list of Warrant objects from the given symbols, or a single
        Warrant object if a list is not provided.

        :param session: the session to use for the request.
        :param symbols: symbol(s) of the warrants, e.g. 'NKLAW'
        """
        if isinstance(symbols, str):
            data = session._get(f"/instruments/warrants/{symbols}")
            return cls(**data)
        params = {"symbol[]": symbols} if symbols else None
        data = session._get("/instruments/warrants", params=params)
        return [cls(**i) for i in data["items"]]


# fix pydantic forward references
FutureProduct.model_rebuild()


async def a_get_quantity_decimal_precisions(
    session: Session,
) -> list[QuantityDecimalPrecision]:
    """
    Returns a list of QuantityDecimalPrecision objects for different
    types of instruments.

    :param session: the session to use for the request.
    """
    data = await session._a_get("/instruments/quantity-decimal-precisions")
    return [QuantityDecimalPrecision(**i) for i in data["items"]]


def get_quantity_decimal_precisions(session: Session) -> list[QuantityDecimalPrecision]:
    """
    Returns a list of QuantityDecimalPrecision objects for different
    types of instruments.

    :param session: the session to use for the request.
    """
    data = session._get("/instruments/quantity-decimal-precisions")
    return [QuantityDecimalPrecision(**i) for i in data["items"]]


async def a_get_option_chain(session: Session, symbol: str) -> dict[date, list[Option]]:
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
    symbol = symbol.replace("/", "%2F")
    data = await session._a_get(f"/option-chains/{symbol}")
    chain: dict[date, list[Option]] = defaultdict(list)
    for i in data["items"]:
        option = Option(**i)
        chain[option.expiration_date].append(option)

    return chain


def get_option_chain(session: Session, symbol: str) -> dict[date, list[Option]]:
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
    symbol = symbol.replace("/", "%2F")
    data = session._get(f"/option-chains/{symbol}")
    chain: dict[date, list[Option]] = defaultdict(list)
    for i in data["items"]:
        option = Option(**i)
        chain[option.expiration_date].append(option)

    return chain


async def a_get_future_option_chain(
    session: Session, symbol: str
) -> dict[date, list[FutureOption]]:
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
    symbol = symbol.replace("/", "")
    data = await session._a_get(f"/futures-option-chains/{symbol}")
    chain: dict[date, list[FutureOption]] = defaultdict(list)
    for i in data["items"]:
        option = FutureOption(**i)
        chain[option.expiration_date].append(option)

    return chain


def get_future_option_chain(
    session: Session, symbol: str
) -> dict[date, list[FutureOption]]:
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
    symbol = symbol.replace("/", "")
    data = session._get(f"/futures-option-chains/{symbol}")
    chain: dict[date, list[FutureOption]] = defaultdict(list)
    for i in data["items"]:
        option = FutureOption(**i)
        chain[option.expiration_date].append(option)

    return chain
