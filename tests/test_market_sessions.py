import pytest

from tastytrade import Session
from tastytrade.market_sessions import (
    ExchangeType,
    get_futures_holidays,
    get_market_holidays,
    get_market_sessions,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def exchanges() -> list[ExchangeType]:
    return [ExchangeType.NYSE, ExchangeType.CME, ExchangeType.CFE, ExchangeType.SMALL]


async def test_get_market_sessions(session: Session, exchanges: list[ExchangeType]):
    await get_market_sessions(session, exchanges=exchanges)


async def test_get_market_holidays(session: Session):
    await get_market_holidays(session)


async def test_get_future_holidays(session: Session):
    await get_futures_holidays(session, ExchangeType.CME)
