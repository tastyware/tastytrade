from tastytrade import Session
from tastytrade.market_sessions import (
    a_get_market_time_sessions,
    a_get_market_time_equity_holidays,
    a_get_market_state,
    get_market_time_sessions,
    get_market_time_equity_holidays,
    get_market_state,
)


async def test_get_market_time_sessions_async(session: Session):
    await a_get_market_time_sessions(session, instrument_collections=['Equity','CME','CFE','Smalls'])


async def test_get_market_time_equity_holidays_async(session: Session):
    await a_get_market_time_equity_holidays(session)


async def test_get_market_state_async(session: Session):
    await a_get_market_state(session, instrument_collections=['Equity','CME','CFE','Smalls'])


def test_get_market_time_sessions(session: Session):
    get_market_time_sessions(session, instrument_collections=['Equity','CME','CFE','Smalls'])


def test_get_market_time_equity_holidays(session: Session):
    get_market_time_equity_holidays(session)


def test_get_market_state(session: Session):
    get_market_state(session, instrument_collections=['Equity','CME','CFE','Smalls'])


