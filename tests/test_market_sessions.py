from pytest import fixture

from tastytrade import Session
from tastytrade.market_sessions import (
    ExchangeType,
    a_get_market_sessions,
    a_get_market_holidays,
    get_market_sessions,
    get_market_holidays,
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


def test_get_market_sessions(session: Session, exchanges: list[ExchangeType]):
    get_market_sessions(session, exchanges=exchanges)


def test_get_market_holidays(session: Session):
    get_market_holidays(session)
