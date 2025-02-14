from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from tastytrade.session import Session
from tastytrade.utils import TastytradeJsonDataclass


class MarketTimeSessionsNext(TastytradeJsonDataclass):
    """Dataclass for data inside the 'next-session' field."""
    close_at: datetime
    close_at_ext: Optional[datetime] = None
    instrument_collection: str
    open_at: datetime
    session_date: date
    start_at: datetime


class MarketTimeSessionsPrevious(TastytradeJsonDataclass):
    """Dataclass for data inside the 'previous-session' field."""
    close_at: datetime
    close_at_ext: Optional[datetime] = None
    instrument_collection: str
    open_at: datetime
    session_date: date
    start_at: datetime


class MarketTimeSessionsCurrent(TastytradeJsonDataclass):
    """
    Dataclass representing the current session and any nested
    'next' or 'previous' session info.

    NOTE: The JSON you showed places `close-at` etc. under
          next-session/previous-session, not at the top level.
          Here, we treat 'close_at', 'open_at', etc. as the
          ones from 'next_session', purely as an example.
    """
    close_at: Optional[datetime] = None
    close_at_ext: Optional[datetime] = None
    instrument_collection: str
    open_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    next_session: Optional[MarketTimeSessionsNext] = None
    previous_session: Optional[MarketTimeSessionsPrevious] = None
    state: str = ""


class MarketTimeSessionsResponse(TastytradeJsonDataclass):
    """
    Top-level container for the API response, which holds
    multiple MarketTimeSessionsCurrent items.
    """
    items: List[MarketTimeSessionsCurrent]


class MarketCalendarData(TastytradeJsonDataclass):
    """
    Represents a data structure holding market half-days and holidays,
    each being a list of ISO-format date strings that get parsed into Python 'date' objects.
    """
    market_half_days: List[date]
    market_holidays: List[date]


class MarketState(str, Enum):
    """
    Represents a data structure holding valid market states.
    """
    open = "Open"
    closed = "Closed"
    pre_market = "Pre-market"
    extended = "Extended"


async def a_get_market_time_sessions(session: Session, exchanges: list[str]) -> list[MarketTimeSessionsCurrent]:
    """
    Retrieves a list of session timings for a date range.

    :param session: active user session to use
    :param instrument_collection: The instrument collection to get market sessions for. Available values : Equity, CME, CFE, Smalls.

    Example:
    import tastytrade.market_sessions as Market
    mt = await Market.a_get_market_time_sessions(session=session, exchanges=['Equity','CME'])
    """
    data = await session._a_get(
        "/market-time/sessions/current", params = "".join(f"&instrument-collections[]={inst}" for inst in exchanges)
    )
    return [MarketTimeSessionsCurrent(**i) for i in data["items"]]


def get_market_time_sessions(session: Session, exchanges: list[str]) -> list[MarketTimeSessionsCurrent]:
    """
    Retrieves market metrics for the given symbols.

    :param session: active user session to use
    :param instrument_collection: The instrument collection to get market sessions for. Available values : Equity, CME, CFE, Smalls.

    Example:
    import tastytrade.market_sessions as Market
    mt = Market.get_market_time_sessions(session=session, exchanges=['Equity','CME])
    """
    data = session._get("/market-time/sessions/current", params = "".join(f"&instrument-collections[]={inst}" for inst in exchanges))
    return [MarketTimeSessionsCurrent(**i) for i in data["items"]]


async def a_get_market_time_equity_holidays(session: Session) -> MarketCalendarData:
    """
    Retrieves market calendar for half days and holidays.

    :param session: active user session to use
    """
    data = await session._a_get("/market-time/equities/holidays")
    return MarketCalendarData(**data)


def get_market_time_equity_holidays(session: Session) -> MarketCalendarData:
    """
    Retrieves market calendar for half days and holidays.

    :param session: active user session to use
    """
    data = session._get("/market-time/equities/holidays")
    return MarketCalendarData(**data)


async def a_get_market_state(session: Session, exchanges: list[str]) -> list:
    """
    Retrieves market state (Open/Closed).

    :param session: active user session to use
    :param instrument_collection: The instrument collection to get market sessions for. Available values : Equity, CME, CFE, Smalls.

    Example:
    s = await Market.a_get_market_state(session=session, instrument_collections=['Equity','CME','CFE','Smalls'])
    Returns ['Closed', 'Closed', 'Closed', 'Closed'] when all markets are closed.
    Other values seen short before market opening: ['Pre-market', 'Open', 'Open', 'Pre-market']
    """
    data = await a_get_market_time_sessions(session=session, exchanges=exchanges)
    enum_states = [MarketState(s.state) for s in data]
    return [st.value for st in enum_states]

def get_market_state(session: Session, exchanges: list[str]) -> list:
    """
    Retrieves market state (Open/Closed).

    :param session: active user session to use
    :param instrument_collection: The instrument collection to get market sessions for. Available values : Equity, CME, CFE, Smalls.

    Example:
    s = Market.get_market_state(session=session, instrument_collections=['Equity','CME','CFE','Smalls'])
    Returns ['Closed', 'Closed', 'Closed', 'Closed'] when all markets are closed.
    Other values seen short before market opening: ['Pre-market', 'Open', 'Open', 'Pre-market']
    Extended market hours: ['Extended', 'Open', 'Open', 'Closed']
    """
    data = get_market_time_sessions(session=session, exchanges=exchanges)
    enum_states = [MarketState(s.state) for s in data]
    return [st.value for st in enum_states]