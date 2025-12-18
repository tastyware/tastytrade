from pytest import fixture

from tastytrade import Session
from tastytrade.market_sessions import (
    ExchangeType,
    a_get_futures_holidays,
    a_get_market_holidays,
    a_get_market_sessions,
    get_futures_holidays,
    get_market_holidays,
    get_market_sessions,
)


@fixture
def exchanges() -> list[ExchangeType]:
    return [ExchangeType.NYSE, ExchangeType.CME, ExchangeType.CFE, ExchangeType.SMALL]


async def test_get_market_sessions_async(
    session: Session, exchanges: list[ExchangeType]
):
    await a_get_market_sessions(session, exchanges=exchanges)


async def test_get_market_holidays_async(session: Session):
    await a_get_market_holidays(session)


async def test_get_future_holidays_async(session: Session):
    await a_get_futures_holidays(session, ExchangeType.CME)


def test_get_market_sessions(session: Session, exchanges: list[ExchangeType]):
    get_market_sessions(session, exchanges=exchanges)


def test_get_market_holidays(session: Session):
    get_market_holidays(session)


def test_get_future_holidays(session: Session):
    get_futures_holidays(session, ExchangeType.CME)
