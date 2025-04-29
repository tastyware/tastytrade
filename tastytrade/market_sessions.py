from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import Field

from tastytrade.session import Session
from tastytrade.utils import TastytradeData


class ExchangeType(str, Enum):
    """
    Contains the valid exchanges to get futures market sessions for.
    """

    CME = "CME"
    CFE = "CFE"
    NYSE = "Equity"
    SMALL = "Smalls"


class MarketStatus(str, Enum):
    """
    Contains the valid market status values.
    """

    OPEN = "Open"
    CLOSED = "Closed"
    PRE_MARKET = "Pre-market"
    EXTENDED = "Extended"


class MarketSessionSnapshot(TastytradeData):
    """
    Dataclass containing information about the upcoming or previous market session.
    """

    close_at: datetime
    close_at_ext: Optional[datetime] = None
    instrument_collection: str
    open_at: datetime
    session_date: date
    start_at: datetime


class MarketSession(TastytradeData):
    """
    Dataclass representing the current session as well as the next and previous sessions.
    """

    close_at: Optional[datetime] = None
    close_at_ext: Optional[datetime] = None
    instrument_collection: str
    open_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    next_session: Optional[MarketSessionSnapshot] = None
    previous_session: Optional[MarketSessionSnapshot] = None
    status: MarketStatus = Field(alias="state")


class MarketCalendar(TastytradeData):
    """
    Dataclass containing information about market holidays and shortened days.
    """

    half_days: list[date] = Field(alias="market-half-days")
    holidays: list[date] = Field(alias="market-holidays")


async def a_get_market_sessions(
    session: Session, exchanges: list[ExchangeType]
) -> list[MarketSession]:
    """
    Retrieves a list of session timings for the given exchanges.

    :param session: active user session to use
    :param exchanges: the list of exchanges to get market sessions for
    """
    data = await session._a_get(
        "/market-time/sessions/current",
        params={"instrument-collections[]": [e.value for e in exchanges]},
    )
    return [MarketSession(**i) for i in data["items"]]


def get_market_sessions(
    session: Session, exchanges: list[ExchangeType]
) -> list[MarketSession]:
    """
    Retrieves a list of session timings for the given exchanges.

    :param session: active user session to use
    :param exchanges: the list of exchanges to get market sessions for
    """
    data = session._get(
        "/market-time/sessions/current",
        params={"instrument-collections[]": [e.value for e in exchanges]},
    )
    return [MarketSession(**i) for i in data["items"]]


async def a_get_market_holidays(session: Session) -> MarketCalendar:
    """
    Retrieves market calendar for half days and holidays.

    :param session: active user session to use
    """
    data = await session._a_get("/market-time/equities/holidays")
    return MarketCalendar(**data)


def get_market_holidays(session: Session) -> MarketCalendar:
    """
    Retrieves market calendar for half days and holidays.

    :param session: active user session to use
    """
    data = session._get("/market-time/equities/holidays")
    return MarketCalendar(**data)


def get_futures_holidays(session: Session, exchange: ExchangeType) -> MarketCalendar:
    data = session._get(f"/market-time/futures/holidays/{exchange.value}")
    return MarketCalendar(**data)
