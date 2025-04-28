from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from tastytrade.order import InstrumentType
from tastytrade.session import Session
from tastytrade.utils import TastytradeData


class ExchangeType(str, Enum):
    """
    Contains the valid exchanges to fetch data for.
    """

    CME = "CME"
    CFE = "CFE"
    NYSE = "Equity"
    SMALL = "Smalls"
    CBOE = "CBOED"
    BOND = "Bond"
    CRYPTO = "Cryptocurrency"
    EQUITY_OFFERING = "Equity Offering"
    UNKNOWN = "Unknown"


class ClosePriceType(str, Enum):
    """
    Contains possible statuses for close prices.
    """

    FINAL = "Final"
    INDICATIVE = "Indicative"
    PRELIMINARY = "Preliminary"
    REGULAR = "Regular"
    UNKNOWN = "Unknown"


class InstrumentKey(TastytradeData):
    """
    Dataclass containing an instrument key.
    """

    symbol: str
    instrument_type: InstrumentType


class Instrument(TastytradeData):
    """
    Dataclass containing information about an instrument.
    """

    symbol: str
    instrument_type: InstrumentType
    instrument_key: InstrumentKey
    underlying_instrument: str
    root_symbol: str
    exchange: ExchangeType


class MarketData(TastytradeData):
    """
    Dataclass containing life market data for a symbol.
    """

    symbol: str
    instrument_type: InstrumentType
    updated_at: datetime
    bid_size: Decimal
    ask_size: Decimal
    mark: Decimal
    close_price_type: ClosePriceType
    prev_close: Decimal
    prev_close_price_type: ClosePriceType
    summary_date: date
    prev_close_date: date
    halt_start_time: int
    halt_end_time: int
    ask: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    bid: Optional[Decimal] = None
    close: Optional[Decimal] = None
    day_open: Optional[Decimal] = None
    day_high: Optional[Decimal] = None
    day_low: Optional[Decimal] = None
    day_close: Optional[Decimal] = None
    day_high_price: Optional[Decimal] = None
    day_low_price: Optional[Decimal] = None
    dividend_amount: Optional[Decimal] = None
    dividend_frequency: Optional[Decimal] = None
    high_limit_price: Optional[Decimal] = None
    instrument: Optional[Instrument] = None
    last: Optional[Decimal] = None
    last_mkt: Optional[Decimal] = None
    last_ext: Optional[Decimal] = None
    last_trade_time: Optional[int] = None
    low_limit_price: Optional[Decimal] = None
    mid: Optional[Decimal] = None
    open: Optional[Decimal] = None
    prev_day_close: Optional[Decimal] = None
    trading_halted: Optional[bool] = None
    trading_halted_reason: Optional[str] = None
    volume: Optional[Decimal] = None
    year_low_price: Optional[Decimal] = None
    year_high_price: Optional[Decimal] = None


def get_market_data(
    session: Session, symbol: str, instrument_type: InstrumentType
) -> MarketData:
    """
    Get market data for the given symbol.

    :param session: active session to use
    :param symbol: symbol to get data for
    :param instrument_type: type of instrument for the symbol
    """
    data = session._get(f"/market-data/{instrument_type.value}/{symbol}")
    return MarketData(**data)


async def a_get_market_data(
    session: Session, symbol: str, instrument_type: InstrumentType
) -> MarketData:
    """
    Get market data for the given symbol.

    :param session: active session to use
    :param symbol: symbol to get data for
    :param instrument_type: type of instrument for the symbol
    """
    data = await session._a_get(f"/market-data/{instrument_type.value}/{symbol}")
    return MarketData(**data)


def get_market_data_by_type(
    session: Session,
    cryptocurrencies: Optional[list[str]] = None,
    equities: Optional[list[str]] = None,
    futures: Optional[list[str]] = None,
    future_options: Optional[list[str]] = None,
    indices: Optional[list[str]] = None,
    options: Optional[list[str]] = None,
) -> list[MarketData]:
    """
    Get market data for the given symbols grouped by instrument type.
    Combined limit across all types is 100.

    :param session: active session to use
    :param cryptocurrencies: list of cryptocurrencies to fetch
    :param equities: list of equities to fetch
    :param futures: list of futures to fetch
    :param future_options: list of future options to fetch
    :param indices: list of indices to fetch
    :param options: list of options to fetch
    """
    params = {
        "index": indices,
        "equity": equities,
        "equity-option": options,
        "future": futures,
        "future-option": future_options,
        "cryptocurrency": cryptocurrencies,
    }
    params = {k: v for k, v in params.items() if v}
    data = session._get("/market-data/by-type", params=params)
    return [MarketData(**i) for i in data["items"]]


async def a_get_market_data_by_type(
    session: Session,
    cryptocurrencies: Optional[list[str]] = None,
    equities: Optional[list[str]] = None,
    futures: Optional[list[str]] = None,
    future_options: Optional[list[str]] = None,
    indices: Optional[list[str]] = None,
    options: Optional[list[str]] = None,
) -> list[MarketData]:
    """
    Get market data for the given symbols grouped by instrument type.
    Combined limit across all types is 100.

    :param session: active session to use
    :param cryptocurrencies: list of cryptocurrencies to fetch
    :param equities: list of equities to fetch
    :param futures: list of futures to fetch
    :param future_options: list of future options to fetch
    :param indices: list of indices to fetch
    :param options: list of options to fetch
    """
    params = {
        "index": indices,
        "equity": equities,
        "equity-option": options,
        "future": futures,
        "future-option": future_options,
        "cryptocurrency": cryptocurrencies,
    }
    params = {k: v for k, v in params.items() if v}
    data = await session._a_get("/market-data/by-type", params=params)
    return [MarketData(**i) for i in data["items"]]
